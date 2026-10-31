"""E329 -- which source names two vintages of one family, and does the stale one win?

E328 measured numbers that sit on a stale cut.  It assumed a source names one file.  A source can
name two: a `_latest` pointer plus a pinned dated fallback, or two dated cuts side by side.  When
it does, *something* has to pick, and there are only three ways the tree actually decides:

  fallback_chain      an ordered container where the first existing file is returned
                      (``for cand in (ptr, pinned): if os.path.isfile(...): return cand``)
  same_target_rebound the same variable is assigned twice; the last assignment wins
  separate_targets    both cuts are bound to different names, so no order decides anything and
                      the consumer decides -- which is a role, not a race

The question the card asks is the middle column: *where both are bound, does the stale file win?*
A statically bound pair cannot answer that on its own, so for a fallback chain this study also
evaluates what the chain would return **on today's disk** for the stems its own call sites name:
pointer present -> the pointer's vintage, pointer absent -> the pinned vintage, even though a newer
cut of the same family may sit beside it.  That branch is the exposure.  Presence is measured, not
simulated: no file is moved and no face is rewritten.

Population:
  source  = a python file in the E326 corpus
  handle  = a face reference on one line, one of
              dated    NAME-YYYY-MM-DD.json (also "%s-YYYY-MM-DD.json" % var)
              latest   NAME_latest.json   (also "%s_latest.json" % var)
              template NAME-%s.json       (an unpinned form, not a vintage)
  family  = lit:STEM for a literal stem, var:VAR for a %-formatted stem.  A bare literal carries
            no directory, so a source-level family is keyed by stem alone -- the deviation from
            E328's (directory, stem) is deliberate and stated in ``limits``.
  vintage = a dated cut, or the pointer (which resolves to whatever cut it holds today)

Static tree analysis plus one read-only pass over the published faces for on-disk presence.

Usage:
    python scripts/e329_two_vintage_binding.py run|verify|selftest
"""
import datetime
import io
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import e326_template_parameter_consumers as e326  # noqa: E402  (path set above)
import e328_quoted_number_staleness as e328  # noqa: E402

ROOT = e326.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-01"
FACE = "TWOVINTAGE-%s.json" % TODAY
LATEST = "twovintage_latest.json"
STUDY = "E329_two_vintage_binding"

TYPED = re.compile(r"(?P<tpl>%s)?(?P<stem>[A-Za-z0-9_+\-]*)-(?P<date>\d{4}-\d{2}-\d{2})\.json")
LATEST_RE = re.compile(r"(?P<tpl>%s)?(?P<stem>[A-Za-z0-9_+\-]*)_latest\.json")
TEMPLATE_FORM = re.compile(r"(?P<stem>[A-Za-z0-9_+\-]+)-%s\.json")
PERCENT = re.compile(r"%\s*([A-Za-z_][A-Za-z0-9_]*)")
DEF = re.compile(r"^def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")
SELFTEST_REGION = re.compile(r"^def\s+(selftest|_selftest|cmd_selftest)\s*\(")
ORDERED = re.compile(r"for\s+[A-Za-z_][A-Za-z0-9_]*\s+in\s*\(")
EXISTENCE = re.compile(r"(isfile|exists)\s*\(")
ASSIGN = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*")
CUTOFF_KEYS = ("evidence_cutoff", "cutoff", "as_of", "asof")
CALL_LITERAL = re.compile(r"%s\(\s*[\"']([A-Za-z0-9_+\-]+)[\"']")

K_DATED, K_LATEST, K_TEMPLATE = "dated", "latest", "template"
O_CHAIN, O_REBOUND, O_SEPARATE, O_MENTION, O_LIST = (
    "fallback_chain", "same_target_rebound", "separate_targets", "mention_only", "ordered_list")

V_SERVES_STALE = "a_source_serves_the_stale_cut_on_today_s_disk"
V_FALLBACK_EXPOSED = ("the_stale_cut_loses_while_the_pointer_exists_and_no_fallback_rechecks_for_"
                     "a_newer_cut")
V_ALL_FRESH = "every_two_vintage_source_resolves_to_the_newest_cut_on_disk"
VERDICTS = (V_SERVES_STALE, V_FALLBACK_EXPOSED, V_ALL_FRESH)

OWN_FACES = (FACE, LATEST)
OWN_SOURCES = (os.path.basename(__file__),)
LOOKAHEAD = 6
MAX_BYTES = 4 << 20


# ---------------------------------------------------------------------------------- primitives

def _clean(text):
    """Drop a trailing comment so `# ` asides do not add handles."""
    cut = text.find("#")
    return text if cut < 0 else text[:cut]


def handles_in_line(text, lineno):
    """Every face reference on one line, in left-to-right order."""
    body = _clean(text)
    operand = None
    percents = PERCENT.findall(body)
    if percents:
        operand = percents[-1]
    out = []
    seen = []

    def add(kind, stem, date, pos, tpl):
        var = operand if tpl else None
        key = (kind, stem, date, pos)
        if key in seen:
            return
        seen.append(key)
        out.append({"kind": kind, "stem": stem or None, "var": var,
                    "date": date, "line": lineno, "pos": pos})
        del var

    for match in TYPED.finditer(body):
        stem = match.group("stem") or ""
        tpl = bool(match.group("tpl")) or not stem
        if not stem and not match.group("tpl"):
            continue
        try:
            date = datetime.date.fromisoformat(match.group("date")).isoformat()
        except ValueError:
            continue
        add(K_DATED, stem, date, match.start(), tpl)
    for match in LATEST_RE.finditer(body):
        stem = match.group("stem") or ""
        if not stem and not match.group("tpl"):
            continue
        add(K_LATEST, stem, None, match.start(), bool(match.group("tpl")) or not stem)
    for match in TEMPLATE_FORM.finditer(body):
        add(K_TEMPLATE, match.group("stem"), None, match.start(), False)
    out.sort(key=lambda h: h["pos"])
    return out


def family_of(handle):
    if handle["stem"]:
        return "lit:%s" % handle["stem"]
    if handle["var"]:
        return "var:%s" % handle["var"]
    return None


def binding_mode(text, handle):
    """How the handle is bound on its own line: assigned, called, ordered, or merely mentioned."""
    body = _clean(text)
    assign = ASSIGN.match(body)
    if assign:
        eq = body.find("=")
        if eq >= 0 and eq < handle["pos"]:
            name = assign.group(1)
            return {"mode": "assign", "target": name, "module_level": not text[:1].isspace(),
                    "upper": name.isupper()}
    calls = re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*\(", body[:handle["pos"]])
    if calls:
        return {"mode": "call", "target": calls[-1], "module_level": False, "upper": False}
    return {"mode": "mention", "target": None, "module_level": False, "upper": False}


def enclosing_function(lines, index):
    for back in range(min(index, len(lines) - 1), -1, -1):
        match = DEF.match(lines[back][1])
        if match:
            return match.group(1), back
    return None, -1


def selftest_start(lines):
    for index, (_n, text) in enumerate(lines):
        if SELFTEST_REGION.match(text):
            return index
    return len(lines)


# ------------------------------------------------------------------------------- disk facts

def disk_index(root):
    """Case-insensitive stem view of the published faces.

    Stems disagree in case on this disk (``OWNCROSS-2026-10-29.json`` beside ``owncross_latest.json``),
    so a caller that names ``owncross`` would miss its own family's cuts if the index were exact.
    Returns (cuts, pointers, pointer_paths, spellings) keyed by the lowercased stem.
    """
    cuts, pointers, paths, spellings = {}, set(), {}, {}
    base = os.path.join(root, "results")
    for dirpath, _dirnames, filenames in os.walk(base):
        for name in filenames:
            if not name.endswith(".json"):
                continue
            if name.endswith("_latest.json"):
                stem = name[:-len("_latest.json")]
                key = stem.lower()
                pointers.add(key)
                paths.setdefault(key, os.path.join(dirpath, name))
                spellings.setdefault(key, set()).add(stem)
                continue
            parsed = e328.face_name(name)
            if parsed:
                key = parsed[0].lower()
                cuts.setdefault(key, set()).add(parsed[1].isoformat())
                spellings.setdefault(key, set()).add(parsed[0])
    return cuts, pointers, paths, spellings


def pointer_cut(path, payloads=None):
    """The vintage a _latest pointer holds today: its stated cutoff, else None."""
    if path is None:
        return None
    if payloads is not None and path in payloads:
        doc = payloads[path]
    else:
        try:
            if os.path.getsize(path) > MAX_BYTES:
                return None
            with io.open(path, encoding="utf-8") as fh:
                doc = json.load(fh)
        except Exception:
            return None
    if isinstance(doc, dict):
        for key in CUTOFF_KEYS:
            value = doc.get(key)
            if isinstance(value, str):
                match = e328.DATE.search(value)
                if match:
                    return match.group(0)
    return None


def newest_cut(cuts, stem):
    dates = cuts.get(stem) or set()
    return max(dates) if dates else None


# ------------------------------------------------------------------------------------ build

def collect(files):
    """(source, family) -> handles, with the enclosing function and binding mode of each."""
    rows = {}
    for path, src in files:
        rel = e326.relp(path)
        lines = _code_lines(src)
        st = selftest_start(lines)
        for index, (lineno, text) in enumerate(lines):
            found = handles_in_line(text, lineno)
            if not found:
                continue
            func, func_index = enclosing_function(lines, index)
            for handle in found:
                family = family_of(handle)
                if not family:
                    continue
                bind = binding_mode(text, handle)
                key = (rel, family)
                row = rows.setdefault(key, {"source": rel, "family": family, "handles": [],
                                            "function": func, "function_line": func_index,
                                            "source_lines": len(lines), "selftest_start": st,
                                            "selftest_text": "\n".join(t for _n, t in lines[st:]),
                                            "ordered_line": None, "has_existence_test": False})
                handle.update(bind)
                handle["text"] = text.strip()[:140]
                if handle not in row["handles"]:
                    row["handles"].append(handle)
                if ORDERED.search(_clean(text)) and len(found) > 1:
                    row["ordered_line"] = lineno
                    ahead = [t for _n, t in lines[index + 1:index + 1 + LOOKAHEAD]]
                    if any(EXISTENCE.search(t) for t in ahead):
                        row["has_existence_test"] = True
    return rows


def _code_lines(src):
    return e326.code_lines(src)


def classify(row):
    """Verdict-bearing shape of one (source, family) pair."""
    handles = row["handles"]
    dated = sorted({h["date"] for h in handles if h["kind"] == K_DATED and h["date"]})
    latest = any(h["kind"] == K_LATEST for h in handles)
    template = any(h["kind"] == K_TEMPLATE for h in handles)
    targets = [h["target"] for h in handles if h["mode"] == "assign" and h["target"]]
    multi = len(dated) >= 2 or bool(dated and latest)

    if row["ordered_line"] is not None and (len(dated) >= 2 or (dated and latest)):
        order = O_CHAIN if row["has_existence_test"] else O_LIST
    elif len(set(targets)) < len(targets) and len({h["line"] for h in handles if h["target"]}) >= 2:
        order = O_REBOUND
    elif len(set(targets)) >= 2:
        order = O_SEPARATE
    else:
        order = O_MENTION

    return {"dated_cuts": dated, "has_latest": latest, "has_template": template,
            "multi_vintage": multi, "order_class": order,
            "roles_named": order == O_SEPARATE and len(set(targets)) == len(targets),
            "targets": sorted(set(targets))}


def chain_order(row):
    """Handles of the ordered container, in source order."""
    line = row["ordered_line"]
    picked = [h for h in row["handles"] if h["line"] == line]
    return sorted(picked, key=lambda h: h["pos"])


def call_site_stems(files, function):
    """Literal stems a resolver helper is called with anywhere in the corpus."""
    if not function:
        return []
    stems = set()
    pattern = re.compile(r"\b%s\(\s*[\"']([A-Za-z0-9_+\-]+)[\"']" % re.escape(function))
    for _path, src in files:
        for _n, text in e326.code_lines(src):
            for stem in pattern.findall(text):
                stems.add(stem)
    return sorted(stems)


def exposure_for(root, cuts, pointers, stems, order=None, payloads=None, paths=None,
                 spellings=None):
    """What a pointer-first chain returns today, and whether the fallback it holds is already stale.

    ``order`` is the chain's handles in source order; the first handle whose file exists is what the
    chain returns.  Without an order the chain has no statically known winner and nothing is served.
    """
    order = order or []
    paths = paths or {}
    spellings = spellings or {}
    out = []
    for stem in stems:
        key = stem.lower()
        dated = sorted(cuts.get(key) or [])
        newest = dated[-1] if dated else None
        served, served_handle = None, None
        fallback_dates = [h["date"] for h in order if h["kind"] == K_DATED and h["date"]]
        for handle in order:
            if handle["kind"] == K_LATEST:
                if key in pointers:
                    served = pointer_cut(paths.get(key), payloads)
                    served_handle = K_LATEST
                    break
            elif handle["kind"] == K_DATED and handle["date"]:
                if handle["date"] in dated:
                    served, served_handle = handle["date"], K_DATED
                    break
        stale = bool(served and newest and served < newest)
        shadowed = bool(served_handle == K_LATEST and newest
                        and any(d < newest for d in fallback_dates))
        out.append({
            "stem": stem,
            "disk_spelling": sorted(spellings.get(key) or []),
            "spellings_differing": [s for s in sorted(spellings.get(key) or []) if s != stem],
            "pointer_present": key in pointers,
            "cuts_on_disk": dated,
            "newest_cut": newest,
            "served_today": served,
            "served_handle": served_handle,
            "pinned_fallback_dates": fallback_dates,
            "serves_stale_today": stale,
            "fallback_shadowed": shadowed,
        })
    return out


def build(root=None, outdir=None, files=None, payloads=None):
    root = root or ROOT
    files = files if files is not None else e326.corpus()
    cuts, pointers, paths, spellings = disk_index(root)
    raw = collect([f for f in files if os.path.basename(f[0]) not in OWN_SOURCES])

    rows = []
    pairs = 0
    multi = 0
    for (rel, family), row in sorted(raw.items()):
        pairs += 1
        shape = classify(row)
        if not shape["multi_vintage"]:
            continue
        multi += 1
        on_disk = sorted({h["date"] for h in row["handles"]
                          if h["kind"] == K_DATED and h["date"] and
                          h["date"] in (cuts.get((h["stem"] or "").lower(), set()))})
        record = {
            "source": rel,
            "family": family,
            "dated_cuts": shape["dated_cuts"],
            "has_latest": shape["has_latest"],
            "order_class": shape["order_class"],
            "roles_named": shape["roles_named"],
            "named_targets": shape["targets"],
            "cuts_present_on_disk": on_disk,
            "both_cuts_on_disk": len(on_disk) >= 2,
            "handles": [{"kind": h["kind"], "stem": h["stem"], "var": h["var"],
                         "date": h["date"], "mode": h["mode"], "target": h["target"],
                         "line": h["line"], "text": h["text"]} for h in row["handles"]],
            "exposures": [],
        }
        if shape["order_class"] == O_CHAIN:
            record["chain"] = {
                "line": row["ordered_line"],
                "order": [{"kind": h["kind"], "stem": h["stem"], "date": h["date"]}
                          for h in chain_order(row)],
                "has_existence_test": row["has_existence_test"],
                "resolver": row["function"],
                "order_covered_by_a_leg": _covered(row),
            }
            stems = call_site_stems(files, row["function"])
            record["call_site_stems"] = stems
            record["exposures"] = exposure_for(root, cuts, pointers, stems,
                                               chain_order(row), payloads, paths, spellings)
        rows.append(record)

    served_stale = sum(1 for r in rows for e in r["exposures"] if e["serves_stale_today"])
    shadowed = sum(1 for r in rows for e in r["exposures"] if e["fallback_shadowed"])
    chains = sum(1 for r in rows if r["order_class"] == O_CHAIN)
    if served_stale:
        verdict = V_SERVES_STALE
    elif shadowed:
        verdict = V_FALLBACK_EXPOSED
    else:
        verdict = V_ALL_FRESH

    summary = {
        "sources_scanned": len({r[0] for r in raw}),
        "source_family_pairs": pairs,
        "pairs_naming_two_vintages": multi,
        "pairs_with_two_dated_cuts": sum(1 for r in rows if len(r["dated_cuts"]) >= 2),
        "pairs_with_a_pointer_pair": sum(1 for r in rows if r["has_latest"]),
        "pairs_both_cuts_on_disk": sum(1 for r in rows if r["both_cuts_on_disk"]),
        "pairs_order_decided": chains,
        "pairs_roles_named": sum(1 for r in rows if r["roles_named"]),
        "pairs_no_static_winner": sum(1 for r in rows if r["order_class"] == O_MENTION),
        "chains_with_an_existence_test": sum(
            1 for r in rows if r.get("chain", {}).get("has_existence_test")),
        "ordered_lists_with_no_test": sum(1 for r in rows if r["order_class"] == O_LIST),
        "chains_whose_order_a_leg_covers": sum(
            1 for r in rows if r.get("chain", {}).get("order_covered_by_a_leg")),
        "call_site_stems": sum(len(r["exposures"]) for r in rows),
        "stems_served_from_a_pointer_today": sum(
            1 for r in rows for e in r["exposures"] if e["pointer_present"]),
        "stems_serving_a_stale_cut_today": served_stale,
        "stems_where_the_pinned_fallback_is_already_stale": shadowed,
        "stems_whose_disk_spelling_differs": sum(
            1 for r in rows for e in r["exposures"] if e["spellings_differing"]),
    }
    doc = {
        "study": STUDY,
        "evidence_cutoff": TODAY,
        "verdict": verdict,
        "summary": summary,
        "rules": {
            "handle": "a dated literal, a _latest pointer, or a %%s template for one stem",
            "family": "lit:STEM for literal stems, var:VAR for %%-formatted stems",
            "vintage": "a dated cut, or the pointer (which holds whatever cut is on disk today)",
            "order_class": [O_CHAIN, O_REBOUND, O_SEPARATE, O_MENTION, O_LIST],
            "serves_stale_today": "the chain's first existing handle is older than the newest cut "
                                  "of the same stem already on disk",
            "fallback_shadowed": "the pointer exists today (so nothing is served stale) while a "
                                 "newer cut than the pinned fallback sits on disk",
        },
        "limits": {
            "family_by_stem": "a bare literal carries no directory, so a source-level family is "
                              "the stem alone; E328 keys families by (directory, stem) because it "
                              "measures files, not sources",
            "static_binding_only": "a chain is read on the line its container sits on; a resolver "
                                   "that builds its order over several lines is classified "
                                   "mention_only rather than guessed",
            "presence_not_behaviour": "serves_stale_today evaluates presence on disk, not a run: "
                                      "the tool never moves a file to see the fallback fire",
            "template_is_not_a_vintage": "NAME-%%s.json names a form, not a cut, and is not counted "
                                         "toward two vintages",
        },
        "rows": rows,
    }
    target = outdir or OUTDIR
    os.makedirs(target, exist_ok=True)
    for name in (FACE, LATEST):
        with io.open(os.path.join(target, name), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(doc, fh, indent=1, sort_keys=False)
            fh.write("\n")
    return doc


def _covered(row):
    """Does a selftest leg name the resolver whose order decides the row?"""
    name = row.get("function")
    if not name:
        return False
    return name in (row.get("selftest_text") or "")


# ------------------------------------------------------------------------------------ verify

def verify(root=None, files=None):
    root = root or ROOT
    fresh = build(root=root, outdir=tempfile.mkdtemp(prefix="e329_verify_"), files=files)
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
    on_disk = {(r["source"], r["family"]): (r["order_class"], tuple(r["dated_cuts"]))
               for r in disk.get("rows") or []}
    computed = {(r["source"], r["family"]): (r["order_class"], tuple(r["dated_cuts"]))
                for r in fresh["rows"]}
    if on_disk != computed:
        problems.append("a two-vintage pair does not re-derive")
    for row in disk.get("rows") or []:
        if row["order_class"] == O_CHAIN and "chain" not in row:
            problems.append("an order-decided row carries no chain record")
            break
        if row["has_latest"] and not row["dated_cuts"]:
            problems.append("a pointer pair carries no dated cut")
            break
    for row in disk.get("rows") or []:
        for exposure in row.get("exposures") or []:
            if exposure["serves_stale_today"] and exposure["served_today"] is None:
                problems.append("a stale verdict without a served cut")
                break
    return problems


# ---------------------------------------------------------------------------------- selftest

def _fixture():
    """A tree with one real family, a pointer, and three sources in the three binding shapes."""
    root = tempfile.mkdtemp(prefix="e329_fx_")
    st = os.path.join(root, "results", "state_tilt")
    os.makedirs(st, exist_ok=True)

    def write(name, payload):
        with io.open(os.path.join(st, name), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(payload, fh)

    write("AAA-2026-10-01.json", {"evidence_cutoff": "2026-10-01", "n": 1})
    write("AAA-2026-10-05.json", {"evidence_cutoff": "2026-10-05", "n": 2})
    write("AAA_latest.json", {"evidence_cutoff": "2026-10-05", "n": 2})
    write("BBB-2026-09-01.json", {"evidence_cutoff": "2026-09-01", "n": 3})
    write("BBB-2026-09-09.json", {"evidence_cutoff": "2026-09-09", "n": 4})

    src = os.path.join(root, "scripts")
    os.makedirs(src, exist_ok=True)
    chain = (
        'import json, os\n'
        'OUT = "results/state_tilt"\n'
        '\n'
        'def _face(stem):\n'
        '    for cand in ("%s_latest.json" % stem, "%s-2026-10-01.json" % stem):\n'
        '        p = os.path.join(OUT, cand)\n'
        '        if os.path.isfile(p):\n'
        '            return cand\n'
        '    return None\n'
        '\n'
        'def run():\n'
        '    return _face("AAA")\n'
        '    return _face("BBB")\n'
        '\n'
        'def selftest():\n'
        '    return _face  # named, so the order is covered\n')
    roles = (
        'ASOF = "results/state_tilt/BBB-2026-09-01.json"\n'
        'FRESH = "results/state_tilt/BBB-2026-09-09.json"\n'
        'def run():\n'
        '    return ASOF, FRESH\n'
        '\n'
        'def selftest():\n'
        '    return True\n')
    mention = (
        'NAMES = ("AAA-2026-10-01.json", "AAA-2026-10-05.json")\n'
        'def selftest():\n'
        '    return NAMES\n')
    files = []
    for name, body in (("chain.py", chain), ("roles.py", roles), ("mention.py", mention)):
        path = os.path.join(src, name)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
        files.append((path, body))
    return root, files


def cmd_selftest():
    checks = []

    def check(name, ok, detail=""):
        checks.append((name, bool(ok), detail))
        print("%-6s %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else "  <- " + detail))
        sys.stdout.flush()

    hits = handles_in_line('for cand in ("%s_latest.json" % stem, "%s-2026-10-01.json" % stem):', 1)
    check("L1 a %%s pointer and a %%s dated cut resolve to one var family",
          [h["kind"] for h in hits] == [K_LATEST, K_DATED]
          and {h["var"] for h in hits} == {"stem"})
    check("L2 the dated %%s handle carries its date", hits[1]["date"] == "2026-10-01")
    lit = handles_in_line('FACE = "OUT-2026-10-05.json"  # the newest cut', 2)
    check("L3 a comment after the literal adds nothing", len(lit) == 1 and lit[0]["stem"] == "OUT")
    tpl = handles_in_line('FACE = "BANDFIELDS-%s.json" % CUTOFF', 3)
    check("L4 a template is a form, not a vintage", [h["kind"] for h in tpl] == [K_TEMPLATE])
    check("L5 family keys separate literal and formatted stems",
          family_of({"stem": "AAA", "var": None}) == "lit:AAA"
          and family_of({"stem": None, "var": "stem"}) == "var:stem")
    modes = binding_mode('DEFAULT_ASOF = os.path.join(D, "R-2026-09-30.json")',
                         {"pos": 40})
    check("L6 a module constant is bound by assignment", modes["mode"] == "assign"
          and modes["target"] == "DEFAULT_ASOF" and modes["upper"] and modes["module_level"])
    called = binding_mode('n, p = _read_face(_face_file("owncross") or "", out)', {"pos": 20})
    check("L7 a call-bound handle names its callee", called["mode"] == "call"
          and called["target"] == "_read_face")

    root, files = _fixture()
    cuts, pointers, paths, spellings = disk_index(root)
    check("L8 the disk index splits cuts from pointers",
          cuts["aaa"] == {"2026-10-01", "2026-10-05"} and "aaa" in pointers)
    check("L9 a compact family is indexed by stem", cuts["bbb"] == {"2026-09-01", "2026-09-09"})
    check("L10 the pointer's vintage comes from its stated cutoff",
          pointer_cut(paths["aaa"]) == "2026-10-05")

    for path, body in files:
        if e326.relp(path).endswith("chain.py"):
            rows = collect([(path, body)])
        if e326.relp(path).endswith("roles.py"):
            roles_rows = collect([(path, body)])
    row = list(rows.values())[0]
    shape = classify(row)
    check("L11 an ordered container of two vintages is a fallback chain",
          shape["order_class"] == O_CHAIN and shape["multi_vintage"])
    check("L12 the chain records that it tests existence", row["has_existence_test"])
    chain_handles = chain_order(row)
    check("L13 the chain order is pointer first, pinned second",
          [h["kind"] for h in chain_handles] == [K_LATEST, K_DATED])
    role_row = list(roles_rows.values())[0]
    role_shape = classify(role_row)
    check("L14 two assigned constants are separate targets, not an order",
          role_shape["order_class"] == O_SEPARATE and role_shape["roles_named"])
    check("L15 the roles are named by their own variables",
          role_shape["targets"] == ["ASOF", "FRESH"])

    stems = call_site_stems(files, row["function"])
    check("L16 call sites are found from the set of literal stems",
          stems == ["AAA", "BBB"], str(stems))
    exp = exposure_for(root, cuts, pointers, stems, chain_order(row), None, paths, spellings)
    by_stem = {e["stem"]: e for e in exp}
    check("L17 a stem with a pointer is served from the pointer",
          by_stem["AAA"]["served_today"] == "2026-10-05"
          and by_stem["AAA"]["served_handle"] == K_LATEST
          and not by_stem["AAA"]["serves_stale_today"])
    check("L18 the pinned fallback is stale but shadowed by the pointer",
          by_stem["AAA"]["fallback_shadowed"] is True)
    stale_exp = exposure_for(root, cuts, pointers, ["BBB"],
                             [{"kind": K_DATED, "date": "2026-09-01"}])
    check("L19 with the pointer gone the pinned fallback serves a stale cut",
          stale_exp[0]["served_today"] == "2026-09-01"
          and stale_exp[0]["serves_stale_today"] is True)

    out = tempfile.mkdtemp(prefix="e329_fx_out_")
    doc = build(root=root, outdir=out, files=files)
    summary = doc["summary"]
    check("L20 only the two-vintage pairs are rows", summary["pairs_naming_two_vintages"] == 3,
          str(summary["pairs_naming_two_vintages"]))
    check("L21 the chain, roles and container rows are all published",
          {r["order_class"] for r in doc["rows"]} == {O_CHAIN, O_SEPARATE, O_MENTION},
          str(sorted({r["order_class"] for r in doc["rows"]})))
    check("L21b an ordered container with no existence test is a list, not a chain",
          classify({"handles": [{"kind": K_DATED, "date": "2026-01-01", "line": 1, "mode": "mention",
                                 "target": None, "stem": "X"},
                                {"kind": K_DATED, "date": "2026-01-02", "line": 1, "mode": "mention",
                                 "target": None, "stem": "X"}],
                    "ordered_line": 1, "has_existence_test": False})["order_class"] == O_LIST)
    check("L21b one assignment of a tuple of cuts is not a rebound",
          all(r["order_class"] != O_REBOUND for r in doc["rows"]))
    check("L22 the verdict names the shadowed fallback",
          doc["verdict"] == V_FALLBACK_EXPOSED, doc["verdict"])
    check("L23 on-disk presence is measured per cut",
          sorted(r["cuts_present_on_disk"] for r in doc["rows"] if r["family"] == "lit:BBB")[0]
          == ["2026-09-01", "2026-09-09"])

    import shutil
    st_dir = os.path.join(root, "results", "state_tilt")
    os.makedirs(st_dir, exist_ok=True)
    for name in os.listdir(out):
        shutil.copy(os.path.join(out, name), os.path.join(st_dir, name))
    check("L24 verify reproduces the face it wrote", verify(root=root, files=files) == [],
          "; ".join(verify(root=root, files=files))[:140])
    disk_path = os.path.join(root, "results", "state_tilt", FACE)
    fresh = json.load(io.open(disk_path, encoding="utf-8"))
    fresh["summary"]["pairs_naming_two_vintages"] = 99
    with io.open(disk_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(fresh, fh)
    problems = verify(root=root, files=files)
    check("L25 verify refuses a doctored summary",
          any("pairs_naming_two_vintages" in p for p in problems), "; ".join(problems)[:140])
    check("L26 the frozen vocabulary is closed", set(VERDICTS) == {
        V_SERVES_STALE, V_FALLBACK_EXPOSED, V_ALL_FRESH})

    bad = [c for c in checks if not c[1]]
    print("\n%d/%d passed" % (len(checks) - len(bad), len(checks)))
    return 0 if not bad else 1


# --------------------------------------------------------------------------------------- cli

def cmd_run():
    doc = build()
    s = doc["summary"]
    print("%s | %s" % (doc["verdict"], STUDY))
    print("sources with a face reference %(sources_scanned)s / source-family pairs "
          "%(source_family_pairs)s / pairs naming two vintages %(pairs_naming_two_vintages)s" % s)
    print("two dated cuts %(pairs_with_two_dated_cuts)s / a pointer pair %(pairs_with_a_pointer_pair)s"
          " / both cuts on disk %(pairs_both_cuts_on_disk)s" % s)
    print("order decided %(pairs_order_decided)s (existence test %(chains_with_an_existence_test)s, "
          "covered by a leg %(chains_whose_order_a_leg_covers)s) / roles named "
          "%(pairs_roles_named)s / no static winner %(pairs_no_static_winner)s" % s)
    print("call-site stems %(call_site_stems)s: served from a pointer %(stems_served_from_a_pointer_today)s"
          ", serving stale %(stems_serving_a_stale_cut_today)s, pinned fallback already stale "
          "%(stems_where_the_pinned_fallback_is_already_stale)s" % s)
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