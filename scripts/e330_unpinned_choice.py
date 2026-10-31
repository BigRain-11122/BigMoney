"""E330 -- which source decides between two references, and which decision no assertion names?

E329 found one resolver (e242's ``_face_file``) whose order decides which cut a reader gets, and no
selftest leg naming that order.  That is one instance of a wider mechanical shape: a *decision* that
picks between two references to one family, where a two-line edit would quietly change the answer and
nothing in the tree would go red.  Four constructs in this tree make such a decision:

  existence_chain   ``for cand in (ptr, pinned): if os.path.isfile(...): return cand``
                    the order of the container is the decision
  or_fallback       ``read("X-2026-10-05.json") or "X-2026-09-01.json"``
                    an empty/None left side silently selects the right side; similarly
                    ``payload.get(key) or DEFAULT_FACE``
  argparse_default  ``add_argument("--face", default=PINNED)``
                    the default is a second copy of a choice the caller may override silently
  mutable_default   ``def load(rows=[])`` / ``def load(cfg={})``
                    the default object persists across calls, so call N inherits call N-1's state

For each row this study answers the card's two questions mechanically:

  * is the decision *named* by an assertion?  A decision is pinned only by an assertion in the same
    source's selftest region or in the S6 chain file / smoke suite -- the same scope E329 applied,
    because a copy of the resolver's name inside some other study's fixture asserts nothing about
    this source.  A decision whose decider name is generic ("run", "load", "data") counts as
    *nameless*: it has no name an assertion could cite even in principle.
  * would a two-line change to the order *alter the answer today*?  Measured against today's disk:
    for an existence chain, the pinned branch's date versus the vintage the pointer currently holds;
    for an ``or`` between two dated cuts, the two cuts; for a parameterised default, a literal cut
    versus the newest cut of the same family now on disk.  No file is moved and no face is rewritten.

Population: sources in the E326 corpus; a decision must name at least one published face, so a
fallback between two non-face values (``rows or []``) is out of population and stated as such.

Usage:
    python scripts/e330_unpinned_choice.py run|verify|selftest
"""
import io
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import e326_template_parameter_consumers as e326  # noqa: E402  (path set above)
import e329_two_vintage_binding as e329  # noqa: E402

ROOT = e326.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-01"
FACE = "UNPINNEDCHOICE-%s.json" % TODAY
LATEST = "unpinnedchoice_latest.json"
STUDY = "E330_unpinned_choice"

OR_KW = re.compile(r"(?<![\w.])or(?![\w])")
DEFAULT_KW = re.compile(r"\bdefault\s*=")
ADD_ARG = re.compile(r"\badd_argument\s*\(")
DEF_SIG = re.compile(r"^def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\((.*)\)\s*:")
MUTABLE_LIT = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(\{\s*\}|\[\s*\]|set\(\s*\)|dict\(\s*\)|\{\})")
IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
QUOTED_LINE = re.compile(r"^[rbuRBU]{0,2}[\"']")
ARG_FLAG = re.compile(r"[\"'](--?[A-Za-z0-9_\-]+)[\"']")
CONST_ASSIGN = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\S")

C_CHAIN, C_OR, C_DEFAULT, C_MUTABLE = (
    "existence_chain", "or_fallback", "argparse_default", "mutable_default")
CLASSES = (C_CHAIN, C_OR, C_DEFAULT, C_MUTABLE)

V_LIVE = ("an_unpinned_decision_would_return_a_different_cut_if_the_order_were_swapped_today")
V_UNPINNED = "unpinned_decisions_exist_but_every_swap_returns_the_same_cut_today"
V_PINNED = "every_two_reference_decision_is_named_by_an_assertion"
VERDICTS = (V_LIVE, V_UNPINNED, V_PINNED)

# A name that appears in a selftest region proves nothing about a decision when the name is a verb
# every module shares.  Such a row is reported as nameless rather than as pinned (r1234 name-law).
GENERIC = frozenset("""
run main build selftest data path name value json read write load open close print out rows text
line lines file files items item get set add new update calc make do work step call load_json
read_json write_json save load_file read_file row rows_out result results payload doc docs
""".split())

GLOBAL_SOURCES = ("Tools/s6_chain_bmb.py", "smoke_test.py")
OWN_FACES = (FACE, LATEST)
OWN_SOURCES = (os.path.basename(__file__),)
MAX_ROWS = 400
MAX_PIN_SITES = 4


# ---------------------------------------------------------------------------------- primitives

def _clean(text):
    return e329._clean(text)


def _handles(text, lineno):
    return e329.handles_in_line(text, lineno)


def code_mask(text):
    """The line with every quoted span blanked, at unchanged length.

    A handle lives inside quotes by construction, so the *operator* and the *container* are what
    must be code: `for cand in ("%s_latest.json" % stem, ...)` is a resolver, while the same text
    inside one long string (a scanner's own test input) is not.  Blanking keeps every offset, so a
    position found on the mask indexes the raw line.
    """
    out = list(text)
    quote = None
    escape = False
    for index, ch in enumerate(text):
        if quote:
            out[index] = " "
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == quote:
                quote = None
        elif ch in "\"'":
            out[index] = " "
            quote = ch
    return "".join(out)


def _side(handles, op_pos):
    """Handles left and right of an operator position, in source order."""
    return ([h for h in handles if h["pos"] < op_pos],
            [h for h in handles if h["pos"] > op_pos])


def _resolve(handle, cuts, pointers, paths, payloads):
    """The vintage a handle names on today's disk, or None if it names nothing present."""
    if handle["kind"] == e329.K_LATEST:
        stem = (handle["stem"] or handle["var"] or "").lower()
        if stem in pointers:
            return {"kind": r_pointer(), "vintage": e329.pointer_cut(paths.get(stem), payloads)}
        return {"kind": r_pointer(), "vintage": None}
    if handle["kind"] == e329.K_DATED:
        stem = (handle["stem"] or handle["var"] or "").lower()
        date = handle["date"]
        present = date in (cuts.get(stem) or set())
        return {"kind": "dated", "vintage": date if present else None}
    return {"kind": handle["kind"], "vintage": None}


def r_pointer():
    return "pointer"


def _arg_name(body):
    """The argument name of an add_argument call on this line, else None."""
    flag = ARG_FLAG.search(body)
    if not flag:
        return None
    return flag.group(1).lstrip("-").replace("-", "_")


def const_faces(lines, cuts, pointers, paths, payloads):
    """Module-level constants assigned a face handle on one line: NAME -> resolved branch."""
    out = {}
    for _lineno, text in lines:
        body = _clean(text)
        assign = CONST_ASSIGN.match(body)
        if not assign:
            continue
        handles = _handles(text, 0)
        if not handles:
            continue
        name = assign.group(1)
        resolved = _resolve(handles[0], cuts, pointers, paths, payloads)
        out[name] = {"constant": name, "face": {"kind": handles[0]["kind"],
                                                "stem": handles[0]["stem"],
                                                "date": handles[0]["date"]},
                     "vintage": resolved["vintage"], "resolved_kind": resolved["kind"]}
    return out


# ------------------------------------------------------------------------------------ census

def decisions(files, cuts, pointers, paths, payloads):
    """Every two-reference decision in the corpus, with both branches resolved on today's disk."""
    rows = []
    stats = {"candidate_lines": 0, "or_lines_with_faces_on_one_side_only": 0,
             "add_argument_lines": 0, "defs_with_a_mutable_literal": 0}
    for path, src in files:
        rel = e326.relp(path)
        if os.path.basename(rel) in OWN_SOURCES:
            continue
        lines = e329._code_lines(src)
        st = e329.selftest_start(lines)
        consts = const_faces(lines, cuts, pointers, paths, payloads)
        for index, (lineno, text) in enumerate(lines):
            if index >= st:
                continue  # a fixture inside a selftest region is not a decision the tree makes
            body = _clean(text)
            mask = code_mask(body)
            if not mask.strip():
                continue  # a line that is nothing but text is not code
            handles = _handles(text, lineno)
            func, _fidx = e329.enclosing_function(lines, index)

            if ADD_ARG.search(mask):
                stats["add_argument_lines"] += 1
                row = _default_row(rel, lineno, body, handles, cuts, pointers, paths, payloads,
                                   consts, func)
                if row:
                    rows.append(row)
                continue

            if handles:
                match = OR_KW.search(mask)
                if match:
                    stats["candidate_lines"] += 1
                    row = _or_row(rel, lineno, body, handles, match.start(), cuts,
                                  pointers, paths, payloads, func)
                    if row is not None:
                        rows.append(row)
                    else:
                        stats["or_lines_with_faces_on_one_side_only"] += 1
                    continue

            sig = DEF_SIG.match(mask)
            if sig:
                literals = MUTABLE_LIT.findall(sig.group(2))
                stats["defs_with_a_mutable_literal"] += len(literals)
                for param, literal in literals:
                    rows.append({
                        "source": rel, "line": lineno, "class": C_MUTABLE,
                        "decider": sig.group(1), "decider_kind": "function",
                        "branches": [{"side": "default", "expr": "%s=%s" % (param, literal),
                                      "face": None, "vintage": None, "exists": False}],
                        "outcome_today": "the shared object created at import",
                        "alternate_today": "a fresh object per call",
                        "swap_changes_today": False,
                    })
    for row in rows:
        row["pinned"], row["pinned_by"], row["pin_note"] = False, [], ""
        row["nameless"] = row["decider"] is None or row["decider"] in GENERIC
    return rows, stats


def _or_row(rel, lineno, body, handles, op_pos, cuts, pointers, paths, payloads, func):
    left, right = _side(handles, op_pos)
    if not (left and right):
        return None  # a fallback to a null literal or a bare name is not a choice between two faces
    branches = []
    for side, group, span in (("left", left, body[:op_pos]), ("right", right, body[op_pos + 2:])):
        handle = group[0] if group else None
        face = None
        vintage = None
        if handle is not None:
            face = {"kind": handle["kind"], "stem": handle["stem"], "date": handle["date"]}
            vintage = _resolve(handle, cuts, pointers, paths, payloads)["vintage"]
        branches.append({"side": side, "expr": span.strip()[:60], "face": face,
                         "vintage": vintage, "exists": vintage is not None})
    decider = None
    assign = CONST_ASSIGN.match(body)
    if assign:
        decider, kind = assign.group(1), "constant"
    elif func:
        decider, kind = func, "function"
    else:
        kind = "none"
    outcome = branches[0]["vintage"] if branches[0]["exists"] else branches[1]["vintage"]
    alternate = branches[1]["vintage"] if branches[0]["exists"] else branches[0]["vintage"]
    return {
        "source": rel, "line": lineno, "class": C_OR, "decider": decider, "decider_kind": kind,
        "branches": branches, "outcome_today": outcome, "alternate_today": alternate,
        "swap_changes_today": bool(branches[0]["exists"] and branches[1]["exists"]
                                   and branches[0]["vintage"] != branches[1]["vintage"]),
    }


def _default_row(rel, lineno, body, handles, cuts, pointers, paths, payloads, consts, func):
    """An argparse default that names a face directly, or through a module constant."""
    if not DEFAULT_KW.search(body):
        return None
    branch = None
    if handles:
        handle = handles[0]
        branch = {"side": "default", "expr": body.strip()[:60],
                  "face": {"kind": handle["kind"], "stem": handle["stem"],
                           "date": handle["date"]},
                  "vintage": _resolve(handle, cuts, pointers, paths, payloads)["vintage"],
                  "exists": True}
    else:
        tail = body[DEFAULT_KW.search(body).end():].strip()
        name = IDENT.match(tail)
        if name and name.group(0) in consts:
            const = consts[name.group(0)]
            branch = {"side": "default", "expr": "%s (module constant)" % const["constant"],
                      "face": const["face"], "vintage": const["vintage"],
                      "exists": True}
    if branch is None:
        return None
    stem = ((branch.get("face") or {}).get("stem") or "").lower()
    newest = e329.newest_cut(cuts, stem) if stem else None
    fresh = bool(branch["vintage"] and newest and branch["vintage"] < newest)
    branch["exists"] = branch["vintage"] is not None
    return {
        "source": rel, "line": lineno, "class": C_DEFAULT,
        "decider": _arg_name(body) or func, "decider_kind": "argument" if _arg_name(body) else "none",
        "branches": [branch],
        "outcome_today": branch["vintage"],
        "alternate_today": "caller_supplied" if branch["vintage"] else None,
        "swap_changes_today": False,
        "default_is_already_stale": fresh,
    }


def chains(files, root=None):
    """The existence chains among the corpus, reusing E329's classification and disk exposure."""
    root = root or ROOT
    cuts, pointers, paths, spellings = e329.disk_index(root)
    payloads = {}
    text_at = {}
    for path, src in files:
        text_at[e326.relp(path)] = {n: t for n, t in e329._code_lines(src)}
    out = []
    for _key, row in e329.collect(files).items():
        if e329.classify(row)["order_class"] != e329.O_CHAIN:
            continue
        line_text = text_at.get(row["source"], {}).get(row["ordered_line"], "")
        if not e329.ORDERED.search(code_mask(_clean(line_text))):
            continue  # the container sits inside a quoted string: text, not a resolver in this tree
        order = e329.chain_order(row)
        stems = e329.call_site_stems(files, row["function"])
        exposures = e329.exposure_for(root, cuts, pointers, stems, order, payloads, paths,
                                      spellings)
        record = {
            "source": row["source"], "line": row["ordered_line"], "class": C_CHAIN,
            "decider": row["function"], "decider_kind": "function",
            "branches": [{"side": i and "fallback" or "primary",
                          "expr": h["kind"], "face": {"kind": h["kind"], "stem": h["stem"],
                                                      "date": h["date"]},
                          "vintage": (h["date"] if h["kind"] == e329.K_DATED
                                      else e329.pointer_cut(paths.get((h["stem"] or "").lower()),
                                                            payloads)),
                          "exists": (h["date"] in (cuts.get((h["stem"] or "").lower()) or set())
                                     if h["kind"] == e329.K_DATED
                                     else (h["stem"] or "").lower() in pointers)}
                         for i, h in enumerate(order)],
            "call_site_stems": stems,
            "outcome_today": None,
            "alternate_today": None,
            "swap_changes_today": False,
            "fallback_lags_newest_cut": False,
            "serves_stale_today": sum(1 for e in exposures if e["serves_stale_today"]),
            "fallback_shadowed_on": [e["stem"] for e in exposures if e["fallback_shadowed"]],
        }
        per_stem = []
        for exposure in exposures:
            pinned_date = None
            for h in order:
                if h["kind"] == e329.K_DATED and h["date"] in exposure["cuts_on_disk"]:
                    pinned_date = h["date"]
                    break
            served = exposure["served_today"]
            newest = exposure["newest_cut"]
            per_stem.append({
                "stem": exposure["stem"],
                "pointer_present": exposure["pointer_present"],
                "pointer_vintage": served,
                "pinned_fallback": pinned_date,
                "newest_cut_on_disk": newest,
                "swap_changes_today": bool(served and pinned_date and served != pinned_date),
                "fallback_lags_newest_cut": bool(pinned_date and newest and pinned_date < newest),
            })
        record["per_stem"] = per_stem
        # The row-level reading is taken from the first stem where the branches actually disagree,
        # never from an aggregate: a chain is one decision but many stems, and reporting the first
        # stem's vintage beside another stem's flag is the same-name-different-quantity mistake.
        disagreeing = [p for p in per_stem
                       if p["swap_changes_today"] or p["fallback_lags_newest_cut"]]
        head = disagreeing[0] if disagreeing else (per_stem[0] if per_stem else None)
        if head is not None:
            record["outcome_today"] = head["pointer_vintage"]
            record["alternate_today"] = head["pinned_fallback"]
            record["stem_where_the_branches_disagree"] = head["stem"]
            record["swap_changes_today"] = any(p["swap_changes_today"] for p in per_stem)
            record["fallback_lags_newest_cut"] = any(p["fallback_lags_newest_cut"] for p in per_stem)
        out.append(record)
    return out


def _global_pin_index(root):
    index = {}
    for rel in GLOBAL_SOURCES:
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            continue
        try:
            with io.open(path, encoding="utf-8", errors="replace") as fh:
                src = fh.read()
        except Exception:
            continue
        for lineno, text in e329._code_lines(src):
            body = _clean(text)
            if not body.strip():
                continue  # a mention inside a comment asserts nothing
            for ident in IDENT.findall(body):
                index.setdefault(ident, []).append("%s:%s" % (rel, lineno))
    return index


def _own_pin_index(files):
    """source -> name -> sites inside that source's own selftest region."""
    index = {}
    for path, src in files:
        rel = e326.relp(path)
        lines = e329._code_lines(src)
        st = e329.selftest_start(lines)
        if st >= len(lines):
            continue
        bucket = index.setdefault(rel, {})
        for lineno, text in lines[st:]:
            body = _clean(text)
            if not body.strip():
                continue
            for ident in IDENT.findall(body):
                bucket.setdefault(ident, []).append("%s:%s" % (rel, lineno))
    return index


def pin(rows, files, root=None):
    root = root or ROOT
    own = _own_pin_index(files)
    glob = _global_pin_index(root)
    for row in rows:
        name = row.get("decider")
        if not name or name in GENERIC:
            row["pinned"] = False
            row["pinned_by"] = []
            row["pin_note"] = ("the decision has no name an assertion could cite" if not name
                               else "%r is a shared verb, so a mention of it pins nothing" % name)
            continue
        sites = (own.get(row["source"], {}).get(name) or []) + (glob.get(name) or [])
        row["pinned"] = bool(sites)
        row["pinned_by"] = sites[:MAX_PIN_SITES]
        row["pin_note"] = "" if sites else "no assertion in this source or in the chain/smoke files"
    return rows


# ------------------------------------------------------------------------------------ build

def build(root=None, outdir=None, files=None):
    root = root or ROOT
    files = files if files is not None else e326.corpus()
    cuts, pointers, paths, _spellings = e329.disk_index(root)
    payloads = {}
    rows, stats = decisions(files, cuts, pointers, paths, payloads)
    rows.extend(chains(files, root))
    pin(rows, files, root)
    for row in rows:
        row.setdefault("nameless", row["decider"] is None or row["decider"] in GENERIC)

    by_class = {cls: [r for r in rows if r["class"] == cls] for cls in CLASSES}
    unpinned = [r for r in rows if not r["pinned"]]
    live = [r for r in unpinned
            if r["swap_changes_today"] or r.get("fallback_lags_newest_cut")]
    if live:
        verdict = V_LIVE
    elif unpinned:
        verdict = V_UNPINNED
    else:
        verdict = V_PINNED

    summary = {
        "sources_scanned": len({e326.relp(p) for p, _s in files}),
        "decisions": len(rows),
        "decisions_by_class": {cls: len(by_class[cls]) for cls in CLASSES},
        "decisions_pinned": sum(1 for r in rows if r["pinned"]),
        "decisions_unpinned": len(unpinned),
        "decisions_nameless": sum(1 for r in rows if r["nameless"]),
        "decisions_whose_swap_changes_today": sum(
            1 for r in rows if r["swap_changes_today"]),
        "decisions_whose_fallback_lags_the_newest_cut": sum(
            1 for r in rows if r.get("fallback_lags_newest_cut")),
        "unpinned_decisions_whose_branches_disagree_today": len(live),
        "chains": len(by_class[C_CHAIN]),
        "chains_serving_a_stale_cut_today": sum(
            1 for r in by_class[C_CHAIN] if r.get("serves_stale_today")),
        "defaults_already_stale_on_disk": sum(
            1 for r in by_class[C_DEFAULT] if r.get("default_is_already_stale")),
        "mutable_defaults": len(by_class[C_MUTABLE]),
        "or_lines_offered_and_rejected_as_one_sided": stats["or_lines_with_faces_on_one_side_only"],
        "add_argument_lines_seen": stats["add_argument_lines"],
        "defs_with_a_mutable_literal_seen": stats["defs_with_a_mutable_literal"],
        "rows_published": min(len(rows), MAX_ROWS),
        "rows_truncated": max(0, len(rows) - MAX_ROWS),
    }
    doc = {
        "study": STUDY,
        "evidence_cutoff": TODAY,
        "verdict": verdict,
        "summary": summary,
        "rules": {
            "decision": "a construct that picks between two references to one family, where a "
                        "two-line edit would change the answer",
            "pinned": "an assertion names the decider inside the same source's selftest region, or "
                      "inside Tools/s6_chain_bmb.py / smoke_test.py",
            "nameless": "the decider is absent or is a shared verb ('run', 'load', 'data'), so no "
                        "assertion could name the decision specifically",
            "swap_changes_today": "the two branches resolve to different vintages on today's disk",
            "declaration_scope": "a construct inside a selftest region is a fixture, not a "
                                 "decision the tree makes",
        },
        "limits": {
            "faces_on_both_sides": "an `or` row needs a face on each side; a fallback to a null literal or to "
                                   "a bare name is an acceptable default, not a choice between two "
                                   "vintages, and the count of rejected one-sided lines is published "
                                   "rather than dropped silently",
            "single_line": "an argument default or a function signature split across lines is not "
                           "read; an `or` whose two faces sit on different lines (e260's "
                           "_try_load(...) or _try_load(...)) is out of population for the same "
                           "reason, and the order of a multi-line chain stays E329's mention_only",
            "quoted_text": "a container or an operator that sits inside a quoted string is text "
                           "being written, not a decision the tree makes -- a scanner's own test "
                           "input is the case that proves the rule",
            "pin_scope": "a copy of the decider's name inside some other study's fixture asserts "
                         "nothing about this source and is not counted",
            "presence_not_behaviour": "swap_changes_today compares what each branch names on disk; "
                                      "the tool never deletes a pointer to watch a fallback fire",
        },
        "rows": rows[:MAX_ROWS],
    }
    target = outdir or OUTDIR
    os.makedirs(target, exist_ok=True)
    for name in (FACE, LATEST):
        with io.open(os.path.join(target, name), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(doc, fh, indent=1, sort_keys=False)
            fh.write("\n")
    return doc


# ------------------------------------------------------------------------------------ verify

def verify(root=None, files=None):
    root = root or ROOT
    fresh = build(root=root, outdir=tempfile.mkdtemp(prefix="e330_verify_"), files=files)
    disk_path = os.path.join(root, "results", "state_tilt", FACE)
    problems = []
    try:
        with io.open(disk_path, encoding="utf-8") as fh:
            disk = json.load(fh)
    except Exception as exc:
        return ["the face does not read: %r" % (exc,)]
    if disk.get("verdict") != fresh.get("verdict"):
        problems.append("the verdict does not re-derive")
    if disk.get("verdict") not in VERDICTS:
        problems.append("verdict %r is outside the frozen set" % (disk.get("verdict"),))
    for key, value in (fresh.get("summary") or {}).items():
        if (disk.get("summary") or {}).get(key) != value:
            problems.append("summary.%s does not re-derive" % key)
    published = [(r["source"], r["line"], r["class"], r["decider"], r["pinned"],
                  r["swap_changes_today"]) for r in disk.get("rows") or []]
    recomputed = [(r["source"], r["line"], r["class"], r["decider"], r["pinned"],
                   r["swap_changes_today"]) for r in fresh["rows"]]
    if published != recomputed:
        problems.append("a published decision does not re-derive")
    for row in disk.get("rows") or []:
        if row["pinned"] and not row["pinned_by"]:
            problems.append("a pinned row carries no assertion site")
            break
        if not row["pinned"] and row["pinned_by"]:
            problems.append("an unpinned row carries assertion sites")
            break
        if row["class"] == C_OR and len(row["branches"]) != 2:
            problems.append("an or-decision without two branches")
            break
    return problems


# ------------------------------------------------------------------------------------ selftest

def _fixture():
    """A tree with one pinned chain, one unpinned chain, and one decision of each other class."""
    root = tempfile.mkdtemp(prefix="e330_fx_")
    st = os.path.join(root, "results", "state_tilt")
    os.makedirs(st, exist_ok=True)

    def write(name, payload):
        with io.open(os.path.join(st, name), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(payload, fh)

    write("AAA-2026-10-01.json", {"evidence_cutoff": "2026-10-01"})
    write("AAA-2026-10-05.json", {"evidence_cutoff": "2026-10-05"})
    write("AAA_latest.json", {"evidence_cutoff": "2026-10-05"})
    write("BBB-2026-09-01.json", {"evidence_cutoff": "2026-09-01"})
    write("BBB-2026-09-09.json", {"evidence_cutoff": "2026-09-09"})
    # CCC's pointer holds the SAME cut as the pinned fallback while a newer cut sits on disk:
    # swapping the order changes nothing today, yet the fallback is already one cut behind.
    write("CCC-2026-09-01.json", {"evidence_cutoff": "2026-09-01"})
    write("CCC-2026-09-09.json", {"evidence_cutoff": "2026-09-09"})
    write("CCC_latest.json", {"evidence_cutoff": "2026-09-01"})

    src = os.path.join(root, "scripts")
    os.makedirs(src, exist_ok=True)
    bodies = {
        "chain_loud.py": (
            'import os\n'
            'def _face(stem):\n'
            '    for cand in ("%s_latest.json" % stem, "%s-2026-10-01.json" % stem):\n'
            '        p = os.path.join("results/state_tilt", cand)\n'
            '        if os.path.isfile(p):\n'
            '            return cand\n'
            '    return None\n'
            'def run():\n'
            '    return _face("AAA")\n'
            'def selftest():\n'
            '    return _face("AAA") is not None\n'),
        "chain_silent.py": (
            'import os\n'
            'def _pick(stem):\n'
            '    for cand in ("%s_latest.json" % stem, "%s-2026-10-01.json" % stem):\n'
            '        p = os.path.join("results/state_tilt", cand)\n'
            '        if os.path.isfile(p):\n'
            '            return cand\n'
            '    return None\n'
            'def run():\n'
            '    return _pick("AAA")\n'
            'def selftest():\n'
            '    return True\n'),
        "orcase.py": (
            'OUT = "results/state_tilt"\n'
            'def pick():\n'
            '    return read("BBB-2026-09-01.json") or "BBB-2026-09-09.json"\n'
            'def read(n):\n'
            '    return n\n'),
        "argcase.py": (
            'CONST = "BBB-2026-09-01.json"\n'
            'def build(parser):\n'
            '    parser.add_argument("--face", default=CONST)\n'
            '    parser.add_argument("--other", default="BBB-2026-09-09.json")\n'
            '    parser.add_argument("--n", default=3)\n'
            '    return parser\n'),
        "chain_lagging.py": (
            'import os\n'
            'def _lag(stem):\n'
            '    for cand in ("%s_latest.json" % stem, "%s-2026-09-01.json" % stem):\n'
            '        p = os.path.join("results/state_tilt", cand)\n'
            '        if os.path.isfile(p):\n'
            '            return cand\n'
            '    return None\n'
            'def run():\n'
            '    return _lag("CCC")\n'
            'def selftest():\n'
            '    return True\n'),
        "bogus.py": (
            'import os\n'
            'def pick(outdir):\n'
            '    return os.path.join(outdir or "results", "AAA_latest.json")\n'
            'TEXT = (\n'
            "'    for cand in (\"%s_latest.json\" % stem, \"%s-2026-10-01.json\" % stem):\\n'\n"
            ')\n'),
        "mutable.py": (
            'def load(rows=[]):\n'
            '    return rows\n'
            'def load2(cfg={}):\n'
            '    return cfg\n'
            'def fine(x=None):\n'
            '    return x\n'),
    }
    files = []
    for name, body in bodies.items():
        path = os.path.join(src, name)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
        files.append((path, body))
    tools = os.path.join(root, "Tools")
    os.makedirs(tools, exist_ok=True)
    chain = 'LEGS = [("x", ["python", "scripts/x.py", "verify"])]  # _pick named here\n'
    with io.open(os.path.join(tools, "s6_chain_bmb.py"), "w", encoding="utf-8",
                 newline="\n") as fh:
        fh.write(chain)
    return root, files


def cmd_selftest():
    checks = []

    def check(name, ok, detail=""):
        checks.append((name, bool(ok), detail))
        print("%-6s %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else "  <- " + detail))
        sys.stdout.flush()

    root, files = _fixture()
    cuts, pointers, paths, spellings = e329.disk_index(root)
    doc = build(root=root, outdir=tempfile.mkdtemp(prefix="e330_fx_out_"), files=files)
    rows = doc["rows"]
    by = {}
    for row in rows:
        by.setdefault(row["class"], []).append(row)

    check("L1 the fixture yields all four decision classes",
          set(by) == set(CLASSES), str(sorted(by)))
    check("L2 an or-decision carries exactly two resolved branches",
          len(by[C_OR][0]["branches"]) == 2
          and [b["vintage"] for b in by[C_OR][0]["branches"]] == ["2026-09-01", "2026-09-09"])
    check("L3 an or-decision between two dated cuts changes the answer when swapped",
          by[C_OR][0]["swap_changes_today"] is True)
    check("L4 the or-decision's decider is the enclosing function",
          by[C_OR][0]["decider"] == "pick")

    chain_silent = [r for r in by[C_CHAIN] if r["source"].endswith("chain_silent.py")][0]
    check("L5 a chain is a decision with its resolver as decider",
          chain_silent["decider"] == "_pick" and chain_silent["class"] == C_CHAIN)
    check("L6 a chain whose pointer holds the newest cut is still a swap that would bite",
          chain_silent["swap_changes_today"] is True
          and chain_silent["outcome_today"] == "2026-10-05"
          and chain_silent["alternate_today"] == "2026-10-01",
          str((chain_silent["outcome_today"], chain_silent["alternate_today"])))
    check("L7 its call-site stems are read from the tree",
          chain_silent["call_site_stems"] == ["AAA"], str(chain_silent["call_site_stems"]))
    check("L8 a chain named only in another source's selftest is unpinned",
          chain_silent["pinned"] is False and chain_silent["pin_note"])
    chain_loud = [r for r in by[C_CHAIN] if r["source"].endswith("chain_loud.py")][0]
    check("L9 a chain named inside its own selftest region is pinned",
          chain_loud["pinned"] is True and any("chain_loud.py" in s for s in chain_loud["pinned_by"]))

    defaults = by[C_DEFAULT]
    check("L10 a default naming a module constant is a decision",
          any("CONST" in r["branches"][0]["expr"] for r in defaults),
          str([r["branches"][0]["expr"] for r in defaults]))
    const_row = [r for r in defaults if "CONST" in r["branches"][0]["expr"]][0]
    check("L11 the constant's face is resolved, not guessed",
          const_row["branches"][0]["vintage"] == "2026-09-01")
    check("L12 the argument name is the decider",
          const_row["decider"] == "face", const_row["decider"])
    check("L13 a default of a plain integer is not a decision",
          all(r["branches"][0]["face"] for r in defaults))
    check("L14 only the default older than the newest cut is flagged",
          [r["default_is_already_stale"] for r in defaults] == [True, False],
          str([(r["outcome_today"], r["default_is_already_stale"]) for r in defaults]))

    mutable = {r["decider"] for r in by[C_MUTABLE]}
    check("L15 both mutable defaults are rows and a None default is not",
          mutable == {"load", "load2"}, str(sorted(mutable)))
    check("L16 a mutable default is not a swap between two vintages",
          all(r["swap_changes_today"] is False for r in by[C_MUTABLE]))
    check("L17 a shared verb as decider is reported nameless, not pinned",
          all(r["nameless"] for r in by[C_MUTABLE]) == all(
              r["decider"] in GENERIC for r in by[C_MUTABLE]))

    check("L18 the fixture verdict is an unpinned swap", doc["verdict"] == V_LIVE,
          doc["verdict"])
    check("L19 the summary counts each class exactly",
          doc["summary"]["decisions_by_class"] == {c: len(by[c]) for c in CLASSES},
          str(doc["summary"]["decisions_by_class"]))
    check("L20 a decision inside a selftest region is not a row",
          not any(r["source"].endswith("chain_loud.py") and r["line"] == 12 for r in rows))

    out = tempfile.mkdtemp(prefix="e330_fx_pub_")
    build(root=root, outdir=out, files=files)
    st_dir = os.path.join(root, "results", "state_tilt")
    import shutil
    for name in os.listdir(out):
        shutil.copy(os.path.join(out, name), os.path.join(st_dir, name))
    check("L21 verify reproduces the face it wrote", verify(root=root, files=files) == [],
          "; ".join(verify(root=root, files=files))[:140])
    disk_path = os.path.join(st_dir, FACE)
    fresh = json.load(io.open(disk_path, encoding="utf-8"))
    fresh["summary"]["decisions"] = 999
    with io.open(disk_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(fresh, fh)
    problems = verify(root=root, files=files)
    check("L22 verify refuses a doctored summary",
          any("decisions" in p for p in problems), "; ".join(problems)[:140])
    check("L23 the frozen vocabulary is closed", set(VERDICTS) == {V_LIVE, V_UNPINNED, V_PINNED})
    check("L24 the limits state the population bound",
          "faces_on_both_sides" in doc["limits"] and "presence_not_behaviour" in doc["limits"]
          and "quoted_text" in doc["limits"])
    check("L25 the pointer's vintage is read from its stated cutoff",
          e329.pointer_cut(paths["aaa"]) == "2026-10-05")

    lagging = [r for r in by[C_CHAIN] if r["source"].endswith("chain_lagging.py")][0]
    check("L26 a chain whose pointer holds the pinned cut does not claim a swap",
          lagging["swap_changes_today"] is False
          and lagging["outcome_today"] == "2026-09-01",
          str((lagging["swap_changes_today"], lagging["outcome_today"])))
    check("L27 but its fallback is already one cut behind the newest on disk",
          lagging["fallback_lags_newest_cut"] is True)
    check("L28 a fallback to a null literal is not a choice between two faces",
          not any(r["source"].endswith("bogus.py") and r["class"] == C_OR for r in rows))
    check("L29 a chain written into a fixture string is not a resolver in this tree",
          not any(r["source"].endswith("bogus.py") and r["class"] == C_CHAIN for r in rows))
    check("L30 an unpinned lagging chain still reaches the live verdict",
          any(r.get("fallback_lags_newest_cut") and not r["pinned"] for r in rows))

    bad = [c for c in checks if not c[1]]
    print("\n%d/%d passed" % (len(checks) - len(bad), len(checks)))
    return 0 if not bad else 1


# --------------------------------------------------------------------------------------- cli

def cmd_run():
    doc = build()
    s = doc["summary"]
    print("%s | %s" % (doc["verdict"], STUDY))
    print("sources %(sources_scanned)s / decisions %(decisions)s %(decisions_by_class)s" % s)
    print("pinned %(decisions_pinned)s / unpinned %(decisions_unpinned)s / nameless "
          "%(decisions_nameless)s" % s)
    print("swaps that change today's answer %(decisions_whose_swap_changes_today)s / fallbacks lagging "
          "the newest cut %(decisions_whose_fallback_lags_the_newest_cut)s / unpinned decisions whose "
          "branches disagree %(unpinned_decisions_whose_branches_disagree_today)s" % s)
    print("chains %(chains)s (serving stale %(chains_serving_a_stale_cut_today)s) / stale defaults "
          "%(defaults_already_stale_on_disk)s / mutable defaults %(mutable_defaults)s" % s)
    return 0


def cmd_verify():
    problems = verify()
    if problems:
        print("PROBLEMS: " + "; ".join(problems[:8]))
        return 1
    print("verify: 0 problems")
    return 0


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "run":
        return cmd_run()
    if cmd == "verify":
        return cmd_verify()
    if cmd == "selftest":
        return cmd_selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))