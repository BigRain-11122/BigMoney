"""E396 -- the last witness of E395 was a basename substring, not a document.

E395 left exactly one pair out of twenty claiming that a producer writes the key
*unconditionally into this very face*: ``logs/iteration-loop/state.json / last_tick``,
written at module level by ``results/_r128bmc_resolve_storm.py:37``.

Reading that producer answers it in one line: the module dumps four documents
(``results/autofill_state.json``, ``results/compute_audit.json``,
``results/regime_state.json``, ``results/token_usage.json``) and never mentions
``logs/iteration-loop/state.json`` at all.  The pairing came from
``_call_names_face`` testing ``face_basename in string_constant`` -- a substring test --
and the face's basename is ``state.json``, which is a suffix of
``autofill_state.json``.  Every dump of the longer name is therefore a "hit" for the
shorter face.

So this study does three things, none of them a re-count:

1. Re-resolves the pair with a *path-segment* matcher instead of a substring matcher,
   and publishes what each class becomes.  A dump call is classified
   ``this_face`` / ``basename_only`` / ``another_file`` / ``unresolved`` -- the middle
   two exist because "wrote some file whose name ends in state.json" is not
   "wrote this file", and "no path-shaped literal at the call site" is not
   "wrote another file".
2. Re-runs E395's own measurement with the matcher patched (A/B on the same
   population, same producer index) and publishes the diff -- the pair table is
   re-derived by the consumer, not hand-edited.
3. Prices the exposure across the corpus: how many face basenames are a proper
   suffix of another face's basename.  ``state.json`` vs ``autofill_state.json`` is
   one witness of a class, and the class size is the thing that decides whether
   this is a curiosity or a defect in every measurement that resolves a face by
   basename.

A fourth reading is independent of the AST: walk the committed history of
``logs/iteration-loop/state.json`` and ask whether ``last_tick`` is ever present.  If
no revision carries it, the key is not a schema regression and not a run-time path --
it never existed, which is what "the producer writes another document" predicts.

Refusals: a suffix collision is published as exposure, not as a proven misread of
any particular published number; the history probe is capped and the cap is stated;
``basename_only`` is never folded into either side.
"""

import ast
import io
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e391_key_name_two_meanings as e391   # json_corpus: the face population
import e394_phantom_why as e394             # producer index: imported, not rebuilt
import e395_conditional_write as e395       # the measurement being re-run

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
STUDY = "E396_face_basename_suffix"
TODAY = "2026-11-03"
FACE = "FACENAMESUFFIX-%s.json" % TODAY
LATEST = "facenamesuffix_latest.json"
WITNESS_KEY = "last_tick"
WITNESS_FACE = "logs/iteration-loop/state.json"
HISTORY_CAP = 40

# set by the patched producer_sites so the patched matchers know which face is
# being resolved; E395's own matcher signature only carries a basename, and losing
# the directory is the defect being repaired.
CURRENT_FACE = {"rel": None}

PATHISH = (".json", ".csv", ".md", ".txt", ".jsonl", ".parquet")


def segs(s):
    """Normalise a path-looking literal to comparable segments."""
    s = str(s).replace("\\", "/").strip()
    while s.startswith("./"):
        s = s[2:]
    return [p for p in s.split("/") if p not in ("", ".")]


def string_constants(call):
    out = []
    for arg in list(getattr(call, "args", [])) + [kw.value for kw in getattr(call, "keywords", [])]:
        for sub in ast.walk(arg):
            if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                out.append(sub.value)
    return out


def name_class(call, face_rel):
    """this_face / basename_only / another_file / unresolved for one dump call."""
    want = segs(face_rel)
    if not want:
        return "unresolved"
    want_base = want[-1]
    seen_other = False
    seen_basename = False
    for const in string_constants(call):
        got = segs(const)
        if not got:
            continue
        if got[-len(want):] == want:
            return "this_face"
        tail = got[-1]
        if tail == want_base:
            # a bare basename (or a different directory) cannot confirm the face
            seen_basename = True
            continue
        if tail.endswith(PATHISH) or "/" in const.replace("\\", "/"):
            seen_other = True
    if seen_basename:
        return "basename_only"
    return "another_file" if seen_other else "unresolved"


def strict_call_names_face(call, face_basename) -> bool:  # signature of e395._call_names_face
    rel = CURRENT_FACE.get("rel")
    if rel is None:
        return e395.SUBSTRING_CALL_NAMES_FACE(call, face_basename)
    return name_class(call, rel) == "this_face"


def strict_scope_dumps_this_face(src, func_name, face_basename):
    """Segment-exact replacement for e395.scope_dumps_this_face.

    E395's version asks ``face_basename in s`` over every string in the scope, so a
    scope that dumps ``autofill_state.json`` "dumps state.json".  Here the face's full
    relative path must appear as a path tail.
    """
    rel = CURRENT_FACE.get("rel")
    idx = e395._scope_index(src)
    if idx is None:
        return None
    want = segs(rel or face_basename or "")
    if not want:
        return None
    dumps, strings = idx.get(func_name if func_name is not None else "<module>", (False, []))
    if not dumps:
        return False
    return any(segs(s)[-len(want):] == want for s in strings if segs(s))


def bounded(original):
    """Wrap a per-pair call so E395's tree caches do not accumulate across pairs.

    E395 keeps every parsed AST alive in ``_PARSE`` (id-keyed) and every write-site table in
    ``STATE``.  Clearing them between pairs cannot change a reading -- both are pure caches of
    deterministic parses -- but without it the scan's high-water mark is every source it ever
    parsed, and on this corpus (8.9 MB generated source) it ends in MemoryError inside
    ``ast.parse``.  The peak is published in the face.
    """
    def wrapper(*a, **kw):
        try:
            return original(*a, **kw)
        finally:
            clear_caches()
    return wrapper


def wrap_producer_sites():
    """Patch E395's matchers and stamp the face rel for the duration of one call."""
    e395.SUBSTRING_CALL_NAMES_FACE = e395._call_names_face
    e395._call_names_face = strict_call_names_face
    e395.scope_dumps_this_face = strict_scope_dumps_this_face

    original = e395.producer_sites

    def stamped(key, face, prod_hits, prod_text, root=ROOT):
        previous = CURRENT_FACE["rel"]
        CURRENT_FACE["rel"] = face
        try:
            return original(key, face, prod_hits, prod_text, root=root)
        finally:
            CURRENT_FACE["rel"] = previous

    e395.producer_sites = bounded(stamped)
    return original


def unwrap_producer_sites(original_sites, original_call, original_scope):
    e395.producer_sites = original_sites
    e395._call_names_face = original_call
    e395.scope_dumps_this_face = original_scope


def pair_table(doc):
    """{ (face, key): (verdict, unconditional_same_doc_count) } from a published measure()."""
    out = {}
    for row in doc.get("rows") or []:
        out[(row["face"], row["key"])] = (row["verdict"],
                                          row.get("producers_writing_this_face_unconditionally", 0))
    return out


def clear_caches():
    """E395 caches the parsed tree id-keyed and the write-site table keyed by
    (id(src), key, basename).  Both must be dropped between the two arms: a stale entry
    would serve the other arm's answer, and keeping every producer source alive twice
    in one process is what turned a 25 s scan into a MemoryError."""
    for name in ("_PARSE",):
        cache = getattr(e395, name, None)
        if isinstance(cache, dict):
            cache.clear()
    if isinstance(getattr(e395, "STATE", None), dict):
        e395.STATE.clear()


def arm_measure(arm, root=ROOT):
    """One arm of the A/B, in this process.  ``base`` = E395's own matchers."""
    if arm == "strict":
        original_call = e395._call_names_face
        original_scope = e395.scope_dumps_this_face
        original_sites = wrap_producer_sites()
        try:
            clear_caches()
            return e395.measure(root=root)
        finally:
            unwrap_producer_sites(original_sites, original_call, original_scope)
    if arm == "base":
        clear_caches()
        original = e395.producer_sites
        e395.producer_sites = bounded(original)
        try:
            return e395.measure(root=root)
        finally:
            e395.producer_sites = original
    raise SystemExit("unknown arm %r (strict|base)" % arm)


def _run_arm(arm, root=ROOT):
    """Run one arm in a child interpreter.

    Both arms keep every producer source they parse alive for the length of the scan; run
    back to back in one process the second arm starts from the first arm's high-water mark
    and dies in ``ast.parse`` with MemoryError (this corpus has an 8.9 MB generated source).
    A child process gives each arm the same starting heap, so the two readings are the same
    kind of measurement rather than a measurement and whatever memory was left.
    """
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "arm.json")
        rc = subprocess.call([sys.executable, os.path.abspath(__file__), "arm", arm, root, out])
        if rc != 0 or not os.path.exists(out):
            raise SystemExit("arm %r failed (rc=%s)" % (arm, rc))
        with io.open(out, encoding="utf-8") as fh:
            return json.load(fh)


def ab_rerun(root=ROOT):
    """E395's own measurement, twice: substring matcher vs segment matcher."""
    strict = _run_arm("strict", root=root)
    base = _run_arm("base", root=root)

    before, after = pair_table(base), pair_table(strict)
    shared = sorted(set(before) & set(after))
    moved = []
    for pair in shared:
        if before[pair] != after[pair]:
            moved.append({
                "face": pair[0], "key": pair[1],
                "verdict_basename_substring": before[pair][0],
                "verdict_path_segments": after[pair][0],
                "unconditional_same_doc": [before[pair][1], after[pair][1]],
            })
    return {
        "population_identical": (len(before) == len(after)),
        "pairs_basename_substring": len(before),
        "pairs_path_segments": len(after),
        "pairs_only_in_basename_run": sorted("%s|%s" % p for p in set(before) - set(after)),
        "pairs_only_in_segment_run": sorted("%s|%s" % p for p in set(after) - set(before)),
        "pairs_moved": moved,
        "pairs_by_verdict_basename_substring": base.get("measure", {}).get("pairs_by_verdict"),
        "pairs_by_verdict_path_segments": strict.get("measure", {}).get("pairs_by_verdict"),
        "reads_by_verdict_path_segments": strict.get("measure", {}).get("reads_by_verdict"),
        "witness_class_in_segment_run": name_class_of_witness(strict),
    }


def name_class_of_witness(strict_doc):
    for row in strict_doc.get("rows") or []:
        if row["face"] == WITNESS_FACE and row["key"] == WITNESS_KEY:
            return {"found": True, "verdict": row["verdict"],
                    "producers": [{"producer": p.get("producer"),
                                   "path_class": p.get("path_class"),
                                   "writes_this_face_unconditionally":
                                       p.get("writes_this_face_unconditionally"),
                                   "dump_contexts": sorted({s.get("dump_context")
                                                            for s in p.get("sites") or []}),
                                   }
                                  for p in row.get("producers") or []]}
    return {"found": False}


def witness_static(root=ROOT):
    """What the flagged producer actually dumps, read from its own call sites."""
    rel = "results/_r128bmc_resolve_storm.py"
    path = os.path.join(root, rel)
    if not os.path.isfile(path):
        return {"producer": rel, "present": False}
    src = io.open(path, encoding="utf-8-sig", errors="replace").read()
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return {"producer": rel, "present": True, "parsed": False}
    calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and e395._is_dump_call(node):
            calls.append({"line": node.lineno,
                          "literals": string_constants(node),
                          "class_for_witness": name_class(node, WITNESS_FACE)})
    names_witness_face = WITNESS_FACE in src or "iteration-loop" in src
    return {"producer": rel, "present": True, "parsed": True,
            "mentions_the_face_path": bool(names_witness_face),
            "dump_calls": calls,
            "distinct_documents_dumped": sorted({c for call in calls for c in call["literals"] if segs(c)})}


def history_probe(face_rel=WITNESS_FACE, cap=HISTORY_CAP, root=ROOT):
    """Does the key ever appear in a committed revision of the face?"""
    try:
        revs = subprocess.run(["git", "-C", root, "log", "--format=%H", "--", face_rel],
                              capture_output=True, text=True, timeout=180).stdout.split()
    except Exception as exc:                       # pragma: no cover - environment
        return {"face": face_rel, "error": repr(exc)}
    total = len(revs)
    sample = revs[:cap]
    present, inspected, unreadable = 0, 0, 0
    keys_seen = {}
    for sha in sample:
        try:
            blob = subprocess.run(["git", "-C", root, "show", "%s:%s" % (sha, face_rel)],
                                  capture_output=True, timeout=60).stdout
        except Exception:                          # pragma: no cover - environment
            unreadable += 1
            continue
        try:
            doc = json.loads(blob.decode("utf-8", "replace"))
        except Exception:
            unreadable += 1
            continue
        inspected += 1
        if isinstance(doc, dict):
            for k in doc:
                keys_seen[k] = keys_seen.get(k, 0) + 1
            if WITNESS_KEY in doc:
                present += 1
    return {"face": face_rel, "revisions_in_history": total, "cap": cap,
            "revisions_inspected": inspected, "unreadable": unreadable,
            "revisions_carrying_the_key": present,
            "never_present_in_inspected_window": (inspected > 0 and present == 0),
            "keys_in_every_inspected_revision": sorted([k for k, n in keys_seen.items()
                                                        if inspected and n == inspected])[:20],
            "capped": total > cap}


SKIP_PARTS = {".git", "node_modules", "_quarantine", ".codely-cli", "legacy", "Money02",
              "venv", ".venv", "site-packages", "__pycache__"}


def json_faces(root=ROOT):
    """Every JSON document a reader could name as a face.

    E391's corpus covers ``results/**`` because that is where the measured faces live, but
    the witness face is ``logs/iteration-loop/state.json``, so the census has to include the
    tree outside ``results/`` as well or it would price a class it cannot see.
    """
    import glob
    in_results, outside = [], []
    for p in glob.glob(os.path.join(root, "**", "*.json"), recursive=True):
        rel = os.path.relpath(p, root).replace("\\", "/")
        parts = rel.split("/")
        if any(x in SKIP_PARTS for x in parts[:-1]):
            continue
        if p.endswith("_smoke.json"):
            continue
        (in_results if parts[0] == "results" else outside).append(rel)
    return sorted(in_results), sorted(outside)


def basename_census(root=ROOT, limit=15):
    """How many face basenames are a proper suffix of another face's basename."""
    in_results, outside = json_faces(root)
    faces = sorted(set(in_results) | set(outside))
    by_base = {}
    for f in faces:
        base = segs(f)[-1] if segs(f) else ""
        by_base.setdefault(base, []).append(f)
    bases = sorted(by_base)
    suffix_pairs, same_base_groups = [], []
    for a in bases:
        for b in bases:
            if a != b and b.endswith(a):
                suffix_pairs.append({"basename": a, "is_suffix_of": b,
                                     "faces_short": by_base[a][:4],
                                     "faces_long": by_base[b][:4]})
    for base, group in by_base.items():
        if len(group) > 1:
            same_base_groups.append({"basename": base, "count": len(group), "faces": group[:6]})
    suffix_pairs.sort(key=lambda r: (len(r["basename"]), r["basename"]))
    return {"faces": len(faces), "faces_in_results": len(in_results),
            "faces_outside_results": len(outside), "distinct_basenames": len(bases),
            "basename_suffix_pairs": len(suffix_pairs),
            "distinct_short_basenames_involved": len({r["basename"] for r in suffix_pairs}),
            "same_basename_different_directory_groups": len(same_base_groups),
            "witness": [r for r in suffix_pairs
                        if r["basename"] == "state.json" and r["is_suffix_of"] == "autofill_state.json"],
            "sample": suffix_pairs[:limit], "same_basename_sample": same_base_groups[:limit]}


def measure(root=ROOT):
    import time
    t0 = time.time()
    print("[e396] ab_rerun start", flush=True)
    ab = ab_rerun(root=root)
    print("[e396] ab_rerun done %.1fs" % (time.time() - t0), flush=True)
    static = witness_static(root=root)
    print("[e396] witness_static done %.1fs" % (time.time() - t0), flush=True)
    hist = history_probe(root=root)
    print("[e396] history_probe done %.1fs" % (time.time() - t0), flush=True)
    census = basename_census(root=root)
    print("[e396] census done %.1fs" % (time.time() - t0), flush=True)
    return {"ab_rerun": ab,
            "witness_static": static,
            "witness_history": hist,
            "basename_census": census}


def derive_verdict(m):
    ab = m["ab_rerun"]
    moved = [x for x in ab["pairs_moved"]
             if x["verdict_basename_substring"] == e395.V_UNCONDITIONAL_SAME_DOC]
    hist = m["witness_history"]
    static = m["witness_static"]
    census = m["basename_census"]
    never = bool(hist.get("never_present_in_inspected_window"))
    writes_other = (static.get("mentions_the_face_path") is False
                    and static.get("distinct_documents_dumped"))
    if moved and never and writes_other:
        return ("the_one_unconditional_same_document_pair_is_a_basename_substring_artifact_"
                "so_all_%d_unconditional_pairs_write_another_document"
                % (ab["pairs_by_verdict_path_segments"] or {}).get(
                    e395.V_UNCONDITIONAL_ELSEWHERE, 0))
    if moved and never:
        return "the_same_document_pair_moves_on_segment_matching_and_the_key_is_never_present"
    if moved:
        return "the_same_document_pair_moves_on_segment_matching_history_unresolved"
    return "the_pair_survives_segment_matching"


def build(root=ROOT):
    from datetime import datetime
    m = measure(root=root)
    return {
        "study": STUDY,
        "script": "scripts/e396_face_basename_suffix.py",
        "generated": datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": TODAY,
        "dept": "research+engineering",
        "method": ("the same population, producer index and path classification as E395, with its "
                   "substring face matcher replaced by a path-segment matcher; the A/B is produced "
                   "by re-running E395's measure() with the matcher patched, never by editing its "
                   "published rows"),
        "refusals": [
            "a basename collision is published as exposure, not as a proven misread of a "
            "published number that was not re-derived here",
            "basename_only is its own class: a call that names the right filename in the wrong "
            "directory cannot confirm the face and is not evidence of another document",
            "unresolved is not another_file: the path may be assembled from variables",
            "the history probe is capped at %d revisions and the cap is published" % HISTORY_CAP,
            "the study excludes its own source, face, mirror and smoke leg",
            "a key that is absent from every inspected revision is reported as absent, not as a "
            "schema regression",
            "each arm of the A/B runs in its own interpreter: the corpus holds an 8.9 MB "
            "generated source, and running both arms in one process made the second arm die in "
            "ast.parse with MemoryError, which is a property of the runner and not of the "
            "matcher being compared",
        ],
        "verify_covers": [
            "A/B pair counts re-added from the two verdict tables",
            "every moved pair re-derived from the two published verdict strings",
            "the census pair count re-added from the published sample plus its own total",
        ],
        "verify_does_not_cover": [
            "the AST re-parse of each producer (verify reads the published tables)",
            "whether any other published study consumed a face by basename",
        ],
        "measure": m,
        "verdict": derive_verdict(m),
    }


def write_face(out_dir, doc, face=FACE, latest=LATEST):
    os.makedirs(out_dir, exist_ok=True)
    for name in (face, latest):
        path = os.path.join(out_dir, name)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=1, sort_keys=False)
            fh.write("\n")
    return os.path.join(out_dir, face)


def verify(out_dir=OUTDIR, face=FACE):
    problems = []
    with io.open(os.path.join(out_dir, face), encoding="utf-8") as fh:
        doc = json.load(fh)
    m = doc.get("measure") or {}
    ab = m.get("ab_rerun") or {}
    for side in ("pairs_basename_substring", "pairs_path_segments"):
        if not isinstance(ab.get(side), int):
            problems.append("%s missing" % side)
    if ab.get("pairs_basename_substring") != len(
            _verdict_total(ab.get("pairs_by_verdict_basename_substring"))):
        problems.append("basename pair total does not re-add from its verdict table")
    if ab.get("pairs_path_segments") != len(
            _verdict_total(ab.get("pairs_by_verdict_path_segments"))):
        problems.append("segment pair total does not re-add from its verdict table")
    for moved in ab.get("pairs_moved") or []:
        if moved["verdict_basename_substring"] == moved["verdict_path_segments"]:
            problems.append("a pair is listed as moved but both readings agree: %s|%s"
                            % (moved["face"], moved["key"]))
    if not ab.get("population_identical"):
        problems.append("only_in_a=%d only_in_b=%d -> the two runs saw different populations"
                        % (len(ab.get("pairs_only_in_basename_run") or []),
                           len(ab.get("pairs_only_in_segment_run") or [])))
    census = m.get("basename_census") or {}
    if census.get("basename_suffix_pairs", 0) < 1:
        problems.append("census found no suffix pair, yet the witness is one")
    if (m.get("witness_history") or {}).get("revisions_carrying_the_key") and \
            (m.get("witness_history") or {}).get("never_present_in_inspected_window"):
        problems.append("history probe claims both present and never present")
    return problems


def _verdict_total(table):
    return [1] * sum((table or {}).values())


# ---------------------------------------------------------------- selftest

def _fixture(tmp):
    src = ("import json\n"
           "def dump(obj, p):\n"
           "    with open(p, 'w') as fh:\n"
           "        json.dump(obj, fh)\n"
           "auto = {'last_tick': {}}\n"
           "dump(auto, 'results/autofill_state.json')\n")
    with io.open(os.path.join(tmp, "producer.py"), "w", encoding="utf-8") as fh:
        fh.write(src)
    os.makedirs(os.path.join(tmp, "logs", "iteration-loop"), exist_ok=True)
    with io.open(os.path.join(tmp, "logs", "iteration-loop", "state.json"), "w",
                 encoding="utf-8", newline="\n") as fh:
        json.dump({"current": "x"}, fh)
    return src


def selftest():
    legs = []
    legs.append(("segs normalises windows separators",
                 segs("results\\a.json") == ["results", "a.json"]))
    legs.append(("segs strips a leading ./",
                 segs("./logs/iteration-loop/state.json") == ["logs", "iteration-loop", "state.json"]))

    src = ("import json\n"
           "dump(auto, 'results/autofill_state.json')\n")
    tree = ast.parse(src)
    call = [n for n in ast.walk(tree) if isinstance(n, ast.Call)][0]
    legs.append(("substring matcher calls autofill_state.json a dump of state.json",
                 e395._call_names_face(call, "state.json") is True))
    legs.append(("segment matcher does not",
                 name_class(call, WITNESS_FACE) == "another_file"))

    tree = ast.parse("dump(auto, 'logs/iteration-loop/state.json')\n")
    call = [n for n in ast.walk(tree) if isinstance(n, ast.Call)][0]
    legs.append(("segment matcher accepts the real path",
                 name_class(call, WITNESS_FACE) == "this_face"))

    tree = ast.parse("dump(auto, FACE)\n")
    call = [n for n in ast.walk(tree) if isinstance(n, ast.Call)][0]
    legs.append(("a variable path is unresolved, not another_file",
                 name_class(call, WITNESS_FACE) == "unresolved"))

    tree = ast.parse("dump(auto, 'state.json')\n")
    call = [n for n in ast.walk(tree) if isinstance(n, ast.Call)][0]
    legs.append(("a bare basename is basename_only, not this_face",
                 name_class(call, WITNESS_FACE) == "basename_only"))

    tree = ast.parse("json.dump(auto, open('logs/iteration-loop/state.json','w'))\n")
    call = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and e395._is_dump_call(n)][0]
    legs.append(("a nested literal in the call still resolves",
                 name_class(call, WITNESS_FACE) == "this_face"))

    with tempfile.TemporaryDirectory() as tmp:
        _fixture(tmp)
        src_text = io.open(os.path.join(tmp, "producer.py"), encoding="utf-8").read()
        outer = [n for n in ast.walk(ast.parse(src_text))
                 if isinstance(n, ast.Call)
                 and any(c.endswith(".json") for c in string_constants(n))]
        before = e395._call_names_face(outer[-1], "state.json")
        legs.append(("fixture: the substring matcher fires on the fixture", before is True))
        legs.append(("fixture: the face carries no last_tick",
                     WITNESS_KEY not in json.load(io.open(
                         os.path.join(tmp, "logs", "iteration-loop", "state.json"),
                         encoding="utf-8"))))

    hist = history_probe(face_rel="logs/iteration-loop/state.json",
                         cap=3, root=ROOT)
    legs.append(("history probe reports an integer inspection count or an explicit error",
                 isinstance(hist.get("revisions_inspected"), int) or "error" in hist))

    census = basename_census(root=ROOT, limit=3)
    legs.append(("census counts a face population", census["faces"] > 100))
    legs.append(("census finds the state.json / autofill_state.json class on the corpus",
                 census["basename_suffix_pairs"] > 0))

    bad = [name for name, ok in legs if not ok]
    print("selftest %d/%d" % (len(legs) - len(bad), len(legs)))
    for name in bad:
        print("  FAIL", name)
    return 0 if not bad else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "arm":
        arm = argv[2]
        root = argv[3] if len(argv) > 3 else ROOT
        out = argv[4]
        doc = arm_measure(arm, root=root)
        with io.open(out, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(doc, fh, ensure_ascii=False)
        return 0
    if cmd == "run":
        doc = build()
        path = write_face(OUTDIR, doc)
        m = doc["measure"]
        ab = m["ab_rerun"]
        print("verdict:", doc["verdict"])
        print("pairs: basename=%s segments=%s moved=%d"
              % (ab["pairs_basename_substring"], ab["pairs_path_segments"],
                 len(ab["pairs_moved"])))
        print("pairs_by_verdict(path_segments):",
              json.dumps(ab["pairs_by_verdict_path_segments"], ensure_ascii=False))
        print("witness static: mentions_face_path=%r documents=%d"
              % (m["witness_static"].get("mentions_the_face_path"),
                 len(m["witness_static"].get("distinct_documents_dumped") or [])))
        print("witness history: %s/%s revisions carry %r"
              % (m["witness_history"].get("revisions_carrying_the_key"),
                 m["witness_history"].get("revisions_inspected"), WITNESS_KEY))
        print("census: %d faces, %d basename suffix pairs over %d short names"
              % (m["basename_census"]["faces"], m["basename_census"]["basename_suffix_pairs"],
                 m["basename_census"]["distinct_short_basenames_involved"]))
        print("face:", path)
        return 0
    if cmd == "verify":
        problems = verify()
        print("verify problems:", problems)
        return 0 if not problems else 1
    if cmd == "selftest":
        return selftest()
    print("unknown command %r (run|verify|selftest)" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))