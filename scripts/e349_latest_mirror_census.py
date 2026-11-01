"""E349 -- what a mirror actually decides.

E347 measured the dated faces: 191 published, 15 loaded by name, 12 reach a comparison, and none
of them gates an operational decision.  Its conclusion carried a bound rather than a verdict: the
readers it expects live on *another* channel -- the ``*_latest.json`` mirrors and the live state
files that a round rewrites in place (``state-<id>.json``, ``fleet/machines/<id>.json``,
``results/watermark_red.json``, ``results/idle_trigger.<id>.json``).  A dated face is a citation;
a mirror is a pointer that resolves to whatever is on disk at the moment it is opened.  So the
question a dated face cannot answer is exactly the question a mirror must:

    load    a source names a channel file -- as a basename literal, as a template with a free
            parameter, or through a directory sweep that admits one
    decide  the loaded value reaches a comparison (E347's ``comparison_site``: ``Compare``, an
            ``if``/``while`` test, an ``assert``, a comprehension filter)
    fresh   whether that comparison tests *freshness* (a date/cutoff/ts/age word on the tested or
            bound side) rather than the value.  Freshness is the only check a mirror can carry
            that its dated sibling cannot: "is what I just read current?"

A mirror with no freshness comparison hands whatever is on disk to a branch.  That is not a bug
in any one writer; it is a property of the channel, and it is either measured or assumed.

Three honesty rules are carried from the family, each with a selftest leg:

    (1) E343's store-vs-load: ``node.ctx`` decides, so ``d["k"] = v`` is not a read of ``d``.
    (2) E341/E344's citation: a literal is a load only if it reaches a load primitive.
    (3) E319's self-inclusion: the census cannot count its own face as a target.

Usage:
    python scripts/e349_latest_mirror_census.py run|verify|selftest
"""

import ast
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e347_published_number_gate_census as e347

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-01"
FACE = "MIRROR-%s.json" % TODAY
LATEST = "mirror_latest.json"
STUDY = "E349_latest_mirror_census"
SELF_REL = "scripts/e349_latest_mirror_census.py"
SELF_OUTPUTS = (FACE, LATEST)

MIRROR_RE = re.compile(r"(^|[-_])latest\.json$", re.I)
STATE_RE = re.compile(r"^(state|heartbeat|watermark|idle_trigger|autofill|status)[-_.].*\.json$", re.I)
HEARTBEAT_DIR = "fleet/machines/"

FRESH_WORDS = ("asof", "as_of", "cutoff", "evidence_cutoff", "stale", "fresh", "age", "epoch",
               "timestamp", "updated", "bar_date", "ri_qi", "trade_date", "session_date", "ts")
SWEEP_ROOTS = ("results", "fleet")

# a source that mentions none of these cannot load the channel; the prefilter is published
CHANNEL_TOKENS = ("_latest", "state-", "heartbeat", "watermark", "idle_trigger",
                  "fleet/machines", "fleet\\\\machines")

MAX_ROWS = 60


# ------------------------------------------------------------------------------- plumbing

def say(message):
    sys.stdout.write(str(message) + "\n")
    sys.stdout.flush()


def _run(args, inp=None):
    return subprocess.run(args, cwd=ROOT, input=inp, capture_output=True)


def git(*args):
    p = _run(["git"] + list(args))
    if p.returncode != 0:
        return None
    return p.stdout.decode("utf-8", "replace")


def blob_map(specs):
    """{'<sha>:<path>': blobsha|None} in one batch-check call (E348's reader).

    A missing path comes back as three tokens, not two -- the shape that turns a naive
    ``split()[0]`` into a silent filename.
    """
    if not specs:
        return {}
    inp = ("\n".join(specs) + "\n").encode("utf-8")
    p = _run(["git", "cat-file", "--batch-check=%(objectname) %(objecttype)"], inp)
    out = p.stdout.decode("utf-8", "replace").splitlines()
    res = {}
    for spec, line in zip(specs, out):
        parts = line.split()
        res[spec] = parts[0] if len(parts) == 2 and parts[1] == "blob" else None
    return res


def blob_contents(shas):
    """{blobsha: bytes} in one batch call."""
    uniq = sorted({s for s in shas if s})
    if not uniq:
        return {}
    p = _run(["git", "cat-file", "--batch"], ("\n".join(uniq) + "\n").encode("utf-8"))
    data, res, pos = p.stdout, {}, 0
    while pos < len(data):
        nl = data.find(b"\n", pos)
        if nl < 0:
            break
        header = data[pos:nl].decode("utf-8", "replace").split()
        if len(header) < 3:
            break
        size = int(header[2])
        res[header[0]] = data[nl + 1:nl + 1 + size]
        pos = nl + 1 + size + 1
    return res


def repo_corpus(pin):
    """``(corpus{path: text}, all_paths, counts)`` read at one commit, in two batch calls.

    The corpus is the *source* tree: ``results/`` holds artifacts this census would be reading
    the output of, and the vendored dirs are not this firm's decisions.  A source that never
    mentions the channel by any of its spellings cannot load it, so it is skipped by a cheap
    text prefilter and the count is published rather than dropped (E332: an invisible filter
    is a silent population).
    """
    listing = git("ls-tree", "-r", "--name-only", pin) or ""
    paths = [p for p in listing.splitlines() if p]
    pys = [p for p in paths
           if p.endswith(".py")
           and not p.startswith(("legacy/", "Money02/", "Money0923/", "results/"))
           and "__pycache__" not in p]
    blobs = blob_map(["%s:%s" % (pin, p) for p in pys])
    contents = blob_contents(list(blobs.values()))
    corpus, prefilted = {}, 0
    for path in pys:
        sha = blobs.get("%s:%s" % (pin, path))
        if not sha or sha not in contents:
            continue
        text = contents[sha].decode("utf-8", "replace")
        if not any(tok in text for tok in CHANNEL_TOKENS):
            prefilted += 1
            continue
        corpus[path] = text
    counts = {"source_files": len(pys), "prefiltered_out": prefilted,
              "scanned": len(corpus)}
    return corpus, paths, counts


# --------------------------------------------------------------------------- the channel

def channel_paths(paths):
    """``(mirrors, state)`` -- the live-pointer population under a commit's tree."""
    mirrors, state = [], []
    for path in paths:
        norm = path.replace("\\", "/")
        base = norm.rsplit("/", 1)[-1]
        if base in SELF_OUTPUTS:
            continue  # E319: the census is not its own target
        at_root = "/" not in norm
        if not at_root and not norm.startswith(("results/", "docs/", "fleet/")):
            continue
        if MIRROR_RE.search(base):
            mirrors.append(norm)
        elif STATE_RE.match(base):
            state.append(norm)
        elif norm.startswith(HEARTBEAT_DIR) and base.endswith(".json"):
            state.append(norm)
    return sorted(set(mirrors)), sorted(set(state))


def channel_kind(base, mirrors_by_name, state_by_name):
    if base in mirrors_by_name:
        return "mirror"
    if base in state_by_name:
        return "state"
    return ""


def sweep_scopes(tree, consts):
    """Directory sweeps that could admit a channel file (results/ and fleet/ roots)."""
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or e347._fname(node.func) not in e347.ENUM_FNS:
            continue
        tails = []
        for value in e347.values_in(node, consts):
            norm = value.replace("\\", "/")
            for root in SWEEP_ROOTS:
                idx = norm.find(root)
                if idx >= 0:
                    tails.append(norm[idx:])
                    break
        pats = [t for t in tails if any(c in t for c in "*?") or t.endswith(".json")]
        dirs = [t for t in tails if t not in pats]
        patterns = []
        for pat in pats:
            if pat.startswith(SWEEP_ROOTS):
                patterns.append(pat)
            else:
                for base in dirs or ["results"]:
                    patterns.append(base.rstrip("/") + "/" + pat)
        if not pats:
            for base in dirs:
                patterns.append(base.rstrip("/") + "/*.json")
        for pattern in patterns:
            out.append({"pattern": pattern, "line": node.lineno})
    return out


def _memo_parents():
    """E347 recomputes ``parents_of(tree)`` once per load binding; memoise it per tree.

    Same function, same answer -- only the walk count changes (697 load sites over 1109 sources
    took 212s before this and about a tenth of that after).
    """
    cache = {}
    original = e347.parents_of

    def wrapped(tree):
        key = id(tree)
        got = cache.get(key)
        if got is None:
            got = original(tree)
            cache[key] = got
        return got

    e347.parents_of = wrapped
    return cache


_MEMO = _memo_parents()


def wired_sources(pin, candidates):
    """Source files named inside the S6 chain -- the readers that actually run every round.

    A historical closeout script (``Tools/_r1029bmc_close.py``) asserts on a heartbeat too, but
    it ran once and will never run again.  Counting it beside a chain leg would repeat E347's
    population/decision confusion, so the chain file's own text decides the cut.
    """
    chain = "Tools/s6_chain_bmb.py"
    blobs = blob_map(["%s:%s" % (pin, chain)])
    sha = blobs.get("%s:%s" % (pin, chain))
    if not sha:
        return set()
    text = blob_contents([sha]).get(sha, b"").decode("utf-8", "replace")
    return {path for path in candidates if path in text}


TEXT_EXT = (".ps1", ".cmd", ".bat", ".txt", ".js")


def non_python_refs(pin, paths, names):
    """Which channel files an *operational* non-Python file names (a citation, not a load).

    The loop's own prompt, the scheduled-task wrappers and the dashboard live here.  They cannot
    be parsed by this census, so they are counted and published as the bound: a channel file
    with no Python reader may still have a PowerShell reader, and saying "nobody reads it" would
    be the same mistake as E347's empty window.
    """
    targets = [p for p in paths
               if p.lower().endswith(TEXT_EXT) and not p.startswith(("results/", "legacy/"))]
    blobs = blob_map(["%s:%s" % (pin, p) for p in targets])
    contents = blob_contents(list(blobs.values()))
    hits = {}
    for path in targets:
        sha = blobs.get("%s:%s" % (pin, path))
        if not sha or sha not in contents:
            continue
        text = contents[sha].decode("utf-8", "replace")
        for name in names:
            if name in text:
                hits.setdefault(name, []).append(path)
    return {"files_scanned": len(targets), "hits": hits}


def measure(corpus, mirrors, state):
    """The whole measurement, pure, over ``{path: text}`` and the channel listing."""
    mirrors_by_name = {p.rsplit("/", 1)[-1]: p for p in mirrors}
    state_by_name = {p.rsplit("/", 1)[-1]: p for p in state}
    stems = {}
    for path, kind in [(p, "mirror") for p in mirrors] + [(p, "state") for p in state]:
        stem = path.rsplit("/", 1)[-1][:-5]  # strip ".json"
        stems.setdefault(stem, (path.rsplit("/", 1)[-1], kind))
    all_paths = mirrors + state

    loads, gates = [], []
    for path in sorted(corpus):
        if path == SELF_REL:
            continue
        text = corpus[path]
        tree = e347.parse(text)
        if tree is None:
            continue
        consts = e347.constants(tree)
        handles = e347.file_handles(tree, consts)
        scopes = sweep_scopes(tree, consts)
        admitted = []
        for scope in scopes:
            regex = e347._glob_re(scope["pattern"])
            for cand in all_paths:
                if regex.fullmatch(cand):
                    admitted.append(cand)
        admitted = sorted(set(admitted))
        for binding in e347.load_bindings(tree, consts):
            hits = []
            for value in binding["values"]:
                base = value.replace("\\", "/").rsplit("/", 1)[-1]
                kind = channel_kind(base, mirrors_by_name, state_by_name)
                if kind:
                    hits.append({"face": base, "matched_by": "exact_filename", "kind": kind,
                                 "literal": value})
                    continue
                for stem, (name, kind2) in stems.items():
                    if stem and stem in value and ("%" in value or "{" in value):
                        hits.append({"face": name, "matched_by": "stem_in_template",
                                     "kind": kind2, "literal": value})
                        break
                else:
                    # a template whose parameter IS the mirror identity: "results/x/%s_latest.json"
                    # resolves to *some* mirror, so the hit is the channel, not one file
                    probe = re.sub(r"%[sdri]|\{[^}]*\}", "X", base)
                    if ("%" in base or "{" in base) and MIRROR_RE.search(probe):
                        hits.append({"face": "<any mirror (template)>",
                                     "matched_by": "template_with_a_free_parameter",
                                     "kind": "mirror", "literal": value})
            if hits:
                channel = "named"
            elif binding["enumerates"] and admitted:
                # A sweep is not 179 readers: one ``for p in glob(results/*.json)`` reaches
                # every mirror at once, so the row belongs to the sweep, not to each file it
                # happens to admit.  Attributing it per file multiplied one comparison into 147
                # (measured on Tools/_r698bmc_s3_probe.py) and is exactly the population/decision
                # confusion this study is about.
                channel = "enumeration"
                pattern = scopes[0]["pattern"] if scopes else "results"
                hits = [{"face": "<sweep %s>" % pattern, "matched_by": "directory_sweep",
                         "kind": "sweep", "literal": pattern}]
            else:
                continue
            loads.append({"source": path, "binding": binding["binding"], "line": binding["line"],
                          "load_name": binding["load_name"], "channel": channel,
                          "files": sorted({h["face"] for h in hits}),
                          "admits": sorted({a.rsplit("/", 1)[-1] for a in admitted})
                          if channel == "enumeration" else [],
                          "kinds": sorted({h["kind"] for h in hits})})
            gates.extend(e347.gate_rows(path, text, tree, consts, handles, binding, hits, channel))

    deduped, seen = [], set()
    for row in gates:
        key = (row["source"], row["line"], row["kind"], row["face"], row["tested"])
        if key in seen:
            continue
        seen.add(key)
        row["freshness"] = _freshness(row)
        deduped.append(row)
    return loads, deduped


def _freshness(row):
    """A comparison tests freshness if the tested or a bound operand names a time."""
    blob = (str(row.get("tested") or "") + " " + " ".join(row.get("bound") or [])).lower()
    for word in FRESH_WORDS:
        if re.search(r"(^|[^a-z_])" + re.escape(word) + r"($|[^a-z_])", blob):
            return "freshness"
    return "value"


# ------------------------------------------------------------------------------ summary

def summarize(mirrors, state, loads, gates, corpus_size, wired=None):
    wired = wired or set()
    mirror_names = {p.rsplit("/", 1)[-1] for p in mirrors}
    state_names = {p.rsplit("/", 1)[-1] for p in state}
    population = mirror_names | state_names

    def touched(rows, kind):
        names = set()
        for row in rows:
            for name in row["files"]:
                if (name in mirror_names) if kind == "mirror" else (name in state_names):
                    names.add(name)
        return names

    named = touched([r for r in loads if r["channel"] == "named"], "mirror") | \
        touched([r for r in loads if r["channel"] == "named"], "state")
    swept = set()
    for row in loads:
        if row["channel"] == "enumeration":
            swept |= {a for a in row.get("admits") or [] if a in population}
    sweep_rows = [row for row in gates if row.get("kind") and row["face"] not in population]
    gated = {row["face"] for row in gates if row["face"] in population}
    real = [row for row in gates if row["face"] in population
            and row["decision_class"] != "selftest_fixture" and row["kind"] != "null_guard"]
    sweep_real = [row for row in sweep_rows if row["decision_class"] != "selftest_fixture"
                  and row["kind"] != "null_guard"]
    sweep_ops = [row for row in sweep_real if row["decision_class"] == "operational"]
    wired_real = [row for row in real if row["source"] in wired]
    wired_ops = [row for row in wired_real if row["decision_class"] == "operational"]
    gated_real = {row["face"] for row in real if row["face"] in population}
    fresh = [row for row in real if row["freshness"] == "freshness"]
    operational = [row for row in real if row["decision_class"] == "operational"]
    operational_fresh = [row for row in operational if row["freshness"] == "freshness"]

    by_class, by_kind = {}, {}
    for row in gates:
        by_class[row["decision_class"]] = by_class.get(row["decision_class"], 0) + 1
        by_kind[row["kind"]] = by_kind.get(row["kind"], 0) + 1
    by_kind["freshness"] = len(fresh)

    def share(num, den):
        return round(100.0 * num / den, 2) if den else None

    summary = {
        "scan_domain": {
            "sources_scanned": corpus_size,
            "mirror_files": len(mirror_names),
            "live_state_files": len(state_names),
            "load_sites": len(loads),
            "files_reached": len(named | swept),
            "comparison_sites": len(gates),
            "verdict": "contains_targets",
        },
        "mirror_files": len(mirror_names),
        "live_state_files": len(state_names),
        "loaded_by_name": len(named),
        "loaded_only_by_enumeration": len(swept - named),
        "never_loaded": len(population - named - swept),
        "with_a_gate": len(gated),
        "with_a_non_fixture_gate": len(gated_real),
        "with_a_freshness_check": len({row["face"] for row in fresh if row["face"] in population}),
        "gates_total": len(gates),
        "gates_outside_fixtures": len(real),
        "sweep_load_sites": len([r for r in loads if r["channel"] == "enumeration"]),
        "sweep_non_fixture_gates": len(sweep_real),
        "sweep_operational_gates": len(sweep_ops),
        "sweep_operational_freshness_gates": len([r for r in sweep_ops
                                                  if r["freshness"] == "freshness"]),
        "wired_sources_total": len(wired),
        "wired_sources_reading_the_channel": len({r["source"] for r in wired_real}),
        "wired_non_fixture_gates": len(wired_real),
        "wired_operational_gates": len(wired_ops),
        "wired_operational_freshness_gates": len([r for r in wired_ops
                                                  if r["freshness"] == "freshness"]),
        "operational_gates": len(operational),
        "operational_gates_that_test_freshness": len(operational_fresh),
        "gates_by_class": by_class,
        "gates_by_kind": by_kind,
        "freshness_gates": len(fresh),
        "share_of_channel_loaded": share(len(named | swept), len(population)),
        "share_of_channel_that_decides": share(len(gated_real), len(population)),
        "share_of_deciding_gates_that_test_freshness": share(len(fresh), len(real)),
    }
    if not population or not loads:
        summary["scan_domain"]["verdict"] = "empty_scan_domain"
    return summary


V_UNCHECKED = ("the_mirror_channel_is_opened_by_operational_branches_and_almost_never_asks_whether_"
               "what_it_opened_is_current")
V_CHECKED = ("the_mirror_channel_is_read_through_freshness_comparisons_so_a_stale_pointer_is_"
             "refused_before_it_decides")
V_POPULATION = ("the_mirror_channel_is_opened_but_never_compared_so_a_mirror_describes_a_population"
                "_rather_than_decides")
V_EMPTY = "the_scan_domain_did_not_contain_the_targets_so_no_clean_claim_is_made"


def decide(summary):
    if summary["scan_domain"]["verdict"] == "empty_scan_domain":
        return V_EMPTY
    real = summary["gates_outside_fixtures"]
    fresh = summary.get("freshness_gates", summary["gates_by_kind"].get("freshness", 0))
    wired_ops = summary.get("wired_operational_gates") or 0
    wired_fresh = summary.get("wired_operational_freshness_gates") or 0
    if wired_ops and wired_fresh * 2 < wired_ops:
        return V_UNCHECKED  # the readers that run every round decide without asking freshness
    if summary["operational_gates"] and fresh == 0:
        return V_UNCHECKED
    if real and fresh * 2 >= real:
        return V_CHECKED
    if summary["operational_gates"] and fresh * 2 < real:
        return V_UNCHECKED
    return V_POPULATION


# -------------------------------------------------------------------------------- build

def build(pin=None):
    pin = (pin or (git("rev-parse", "HEAD") or "")).strip()
    if not pin:
        raise SystemExit("no git HEAD")
    corpus, paths, counts = repo_corpus(pin)
    mirrors, state = channel_paths(paths)
    loads, gates = measure(corpus, mirrors, state)
    wired = wired_sources(pin, list(corpus))
    summary = summarize(mirrors, state, loads, gates, len(corpus), wired)
    pop_names = {p.rsplit("/", 1)[-1] for p in mirrors + state}
    outside = non_python_refs(pin, paths, sorted(pop_names))
    state_names = {p.rsplit("/", 1)[-1] for p in state}
    mentioned = set(outside["hits"])
    summary["outside_python"] = {
        "files_scanned": outside["files_scanned"],
        "channel_files_mentioned": len(mentioned),
        "state_files_mentioned": len(mentioned & state_names),
        "mirror_files_mentioned": len(mentioned - state_names),
    }
    summary["scan_domain"].update(counts)
    population = sorted({p.rsplit("/", 1)[-1] for p in mirrors + state})
    touch = {}
    for row in gates:
        touch.setdefault(row["face"], []).append(row)
    rows = []
    for name in population:
        got = touch.get(name, [])
        real = [r for r in got if r["decision_class"] != "selftest_fixture"
                and r["kind"] != "null_guard"]
        fresh = [r for r in real if r["freshness"] == "freshness"]
        rows.append({
            "file": name,
            "kind": "mirror" if name in {p.rsplit("/", 1)[-1] for p in mirrors} else "state",
            "gates": len(got),
            "non_fixture_gates": len(real),
            "freshness_gates": len(fresh),
            "decisions": sorted({r["decision_class"] for r in real}),
            "sources": sorted({r["source"] for r in real})[:6],
        })
    rows.sort(key=lambda r: (-r["freshness_gates"], -r["non_fixture_gates"], r["file"]))
    faces_read = set()
    for row in loads:
        faces_read |= set(row["files"]) | set(row.get("admits") or [])
    write_only = [{"file": name,
                   "mentioned_by": outside["hits"].get(name, [])[:4],
                   "kind": "state" if name in state_names else "mirror"}
                  for name in sorted(set(pop_names) - faces_read)]
    summary["write_only_to_python"] = len(write_only)
    summary["never_named_by_any_in_repo_file"] = len(
        [r for r in write_only if not r["mentioned_by"]])
    return {
        "study": STUDY,
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "today": TODAY,
        "pin": pin,
        "source": SELF_REL,
        "evidence_cutoff": TODAY,
        "summary": summary,
        "verdict": decide(summary),
        "rows": rows[:MAX_ROWS],
        "write_only": write_only[:MAX_ROWS],
        "rows_truncated": max(0, len(rows) - MAX_ROWS),
        "loads": loads[:MAX_ROWS],
        "gates": [g for g in gates if g["decision_class"] != "selftest_fixture"][:MAX_ROWS],
        "bound": ("the corpus is the in-repo .py sources at %s; a consumer outside this tree "
                  "(a scheduled task's own script, the dashboard's browser code) is not in it"
                  % pin[:8]),
    }


def write(face):
    os.makedirs(OUTDIR, exist_ok=True)
    dated = os.path.join(OUTDIR, FACE)
    latest = os.path.join(OUTDIR, LATEST)
    for target in (dated, latest):
        with open(target, "w", encoding="utf-8") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
    return dated, latest


def _same(published, fresh):
    """Deep comparison of the scalar summary only; row tables may carry timestamps."""
    return json.dumps(published, sort_keys=True) == json.dumps(fresh, sort_keys=True)


def verify():
    dated = os.path.join(OUTDIR, FACE)
    if not os.path.exists(dated):
        latest = os.path.join(OUTDIR, LATEST)
        if not os.path.exists(latest):
            say("no published face")
            return 2
        dated = latest
    face = json.load(open(dated, encoding="utf-8"))
    pin = face.get("pin") or ""
    if blob_map(["%s:%s" % (pin, SELF_REL)]).get("%s:%s" % (pin, SELF_REL)) is None:
        say("pin %s does not carry this study -- the face is its own evidence" % pin[:8])
        return 2
    fresh = build(pin)
    problems = []
    if not _same(face.get("summary"), fresh.get("summary")):
        problems.append("summary does not re-derive from the pinned corpus")
    if face.get("verdict") != fresh.get("verdict"):
        problems.append("verdict does not re-derive (%s vs %s)"
                        % (face.get("verdict"), fresh.get("verdict")))
    for key in ("rows",):
        if len(face.get(key) or []) != len(fresh.get(key) or []):
            problems.append("%s length differs (%s vs %s)"
                            % (key, len(face.get(key) or []), len(fresh.get(key) or [])))
    say(json.dumps({"problems": problems}, ensure_ascii=False))
    return 0 if not problems else 1


# ------------------------------------------------------------------------------ selftest

def _fixture(src, mirrors, state, path="scripts/fixture.py"):
    corpus = {path: src}
    return measure(corpus, mirrors, state)


def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    # 1. the channel is recognised by name, and a dated face is not in it
    m, s = channel_paths([
        "results/state_tilt/call_latest.json",
        "results/idle_trigger.bm-b.json",
        "state-bm-b.json",
        "fleet/machines/bm-b.json",
        "results/state_tilt/DECIDEGATE-2026-11-01.json",
        "docs/readme.md",
    ])
    leg("mirror names are recognised", m == ["results/state_tilt/call_latest.json"], m)
    leg("live state names are recognised",
        set(s) == {"results/idle_trigger.bm-b.json", "state-bm-b.json",
                   "fleet/machines/bm-b.json"}, s)
    leg("a dated face is not a channel file",
        not any("DECIDEGATE" in p for p in m + s))

    # 2. E319: the census is not its own target
    m2, s2 = channel_paths(["results/state_tilt/%s" % FACE,
                            "results/state_tilt/%s" % LATEST])
    leg("the census does not scan its own output", m2 == [] and s2 == [], (m2, s2))

    # 3. a printed literal is a citation, not a load
    loads, gates = _fixture('print("call_latest.json")\n', ["results/x/call_latest.json"], [])
    leg("a printed literal is not a load", loads == [] and gates == [], (loads, gates))

    # 4. a load by basename literal is
    loads, _ = _fixture('d = json.load(open("results/x/call_latest.json"))\n',
                        ["results/x/call_latest.json"], [])
    leg("a literal that reaches a load is a load",
        len(loads) == 1 and loads[0]["files"] == ["call_latest.json"], loads)

    # 5. a template with a free parameter resolves by stem
    loads, _ = _fixture('d = json.load(open("results/x/%s_latest.json" % kind))\n',
                        ["results/x/call_latest.json"], [])
    leg("a template resolves to its mirror", len(loads) == 1, loads)

    # 6. freshness is the mirror's own question
    src = ('d = json.load(open("results/x/call_latest.json"))\n'
           'if d["asof"] != today:\n    pass\n')
    _, gates = _fixture(src, ["results/x/call_latest.json"], [])
    leg("a freshness comparison is flagged as freshness",
        len(gates) == 1 and gates[0]["freshness"] == "freshness", gates)

    # 7. and a value comparison is not
    src = ('d = json.load(open("results/x/call_latest.json"))\n'
           'if d["score"] > 0:\n    pass\n')
    _, gates = _fixture(src, ["results/x/call_latest.json"], [])
    leg("a value comparison is not freshness",
        len(gates) == 1 and gates[0]["freshness"] == "value", gates)

    # 8. E343: a store is not a read
    src = ('d = json.load(open("results/x/call_latest.json"))\n'
           'd["k"] = 1\n')
    _, gates = _fixture(src, ["results/x/call_latest.json"], [])
    leg("a store is not a read", gates == [], gates)

    # 9. a selftest fixture is not a firm decision
    src = ('def selftest_fixture():\n'
           '    d = json.load(open("results/x/call_latest.json"))\n'
           '    if d["asof"] != today:\n        return 1\n    return 0\n')
    _, gates = _fixture(src, ["results/x/call_latest.json"], [])
    leg("a fixture comparison is published as a fixture",
        len(gates) == 1 and gates[0]["decision_class"] == "selftest_fixture", gates)

    # 10. an enumeration admits channel files, and only those in its scope
    src = ('for p in sorted(glob.glob("results/*/*_latest.json")):\n'
           '    d = json.load(open(p))\n    if d["asof"] != today:\n        skip()\n')
    _, gates = _fixture(src, ["results/x/call_latest.json"], [])
    leg("an enumeration admits a channel file",
        any(g["channel"] == "enumeration" for g in gates), gates)

    # 11. an empty domain must not read as an all-clear
    summary = summarize([], [], [], [], 0)
    leg("an empty domain publishes its own verdict",
        summary["scan_domain"]["verdict"] == "empty_scan_domain")

    # 12. a summary that does not re-derive is refused
    summary = summarize(["results/x/call_latest.json"], [], [], [], 10)
    tampered = json.loads(json.dumps(summary))
    tampered["gates_total"] = summary["gates_total"] + 1
    leg("a summary that does not re-derive is refused", not _same(summary, tampered))

    # 13. a file that is opened and never compared is a population, not a decision
    summary = summarize(["results/x/call_latest.json"], [], [
        {"source": "s.py", "binding": "d", "line": 1, "load_name": "load", "channel": "named",
         "files": ["call_latest.json"], "kinds": ["mirror"]}], [], 10)
    leg("an uncompared mirror is a population",
        summary["with_a_non_fixture_gate"] == 0
        and summary["loaded_by_name"] == 1, summary)

    failed = [row for row in legs if not row[1]]
    for name, ok, detail in legs:
        say("[%s] %s%s" % ("PASS" if ok else "FAIL", name,
                           "" if ok else " :: %s" % (detail,)))
    say("selftest %d/%d" % (len(legs) - len(failed), len(legs)))
    return 0 if not failed else 1


# ---------------------------------------------------------------------------------- main

def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "run":
        face = build()
        dated, latest = write(face)
        say(json.dumps({"study": STUDY, "verdict": face["verdict"],
                        "summary": face["summary"], "dated": dated.replace(ROOT + os.sep, ""),
                        "latest": latest.replace(ROOT + os.sep, "")}, ensure_ascii=False,
                       indent=1))
        return 0
    if cmd == "verify":
        return verify()
    say("usage: run|verify|selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))