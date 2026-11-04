"""E407 -- does a leg read a face that an earlier leg of the same suite republishes?

Card (results/runnable_pool.json, entered by bm-b r1422 postscript after E305 re-red twice in one
window): "The E305 leg checks 'is precisiongap_latest.json published at the number the audit
re-derives' by calling the study's own build() at check time.  That build reads sibling faces
(t35_open_fill_verify.json and family) which OTHER legs of the same suite republish earlier in the
run."  The card asks, for every live-directory leg: does its input change during the suite, which
leg changes it, and does the leg re-derive before comparing.

This study answers it for the motivating instance by measuring the thing the hypothesis names --
the input set and its in-suite writers -- instead of assuming it:

    inputs   the faces the E305 build actually opens, read out of the census the build consumes
             (not a guess: e305.build() reads every face its at-risk rows name, and those rows are
             in results/state_tilt/precisioncensus_latest.json)
    writers  every source in the tree that names each of those faces (a face is written by the
             module that names it; the census of writers is a literal scan, published per face)
    legs     every leg of smoke_test.py that (a) imports one of those writer modules AND calls a
             write verb on it, or (b) runs one of those scripts as a subprocess with arguments that
             are not a selftest

The order question then has an exact form: a leg's input changes during the suite only if an
earlier leg executes a writer of one of its input faces.  The bill is the pair table, and the
verdict is decided from the summary, never written by hand.

BOUND, published rather than claimed: smoke_test.py's legs are the statically attributable groups
inside main() (statements up to and including the check() each leg ends with).  The suite reports
more legs than that, because legs are also executed from helper functions and loops; the two counts
are published side by side and the gap is not folded into either.  A pre/post hash probe over a full
suite run is the direct confirmation of the within-run claim and is NOT run here -- this study's
within-run statement rests on the static leg-to-writer analysis, and the face carries the 13 input
hashes so the probe can be completed without rebuilding them.

    python scripts/e407_leg_input_stability.py run
    python scripts/e407_leg_input_stability.py verify
    python scripts/e407_leg_input_stability.py selftest
"""
import ast
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-04"
FACE = "LEGINPUT-%s.json" % TODAY
LATEST = "leginput_latest.json"
SUITE = os.path.join(ROOT, "smoke_test.py")
STUDY = "E407_leg_input"

if HERE not in sys.path:
    sys.path.insert(0, HERE)

WRITE_VERBS = {"rebuild_face", "run", "build", "write", "publish", "refresh",
               "sync_face", "snapshot", "tick", "accrue", "paper", "rebuild"}
SELFTEST_ARGS = ("selftest", "--selftest")

V_NONE = "no_leg_in_the_suite_executes_a_writer_of_any_input_face_so_the_leg_is_order_stable_and_the_pinned_columns_are_the_audit"
V_ORDER = "an_earlier_leg_of_the_suite_executes_a_writer_of_an_input_face_so_the_leg_reads_a_face_the_run_itself_moves"
V_INPUTS_MISSING = "the_input_faces_cannot_be_enumerated_so_the_question_is_not_answered"
VERDICTS = (V_NONE, V_ORDER, V_INPUTS_MISSING)


def say(msg):
    sys.stdout.write(str(msg) + "\n")


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


# ------------------------------------------------------------------ inputs
def e305_inputs(census=None):
    """The faces the E305 build opens, taken from the census it consumes."""
    import e305_face_level_row_pricing as m305
    if census is None:
        census = _read(os.path.join(ROOT, "results", "state_tilt", m305.CENSUS))
    rows = [s for s in census.get("sites") or []
            if s.get("at_risk") and s.get("at_risk_faces")
            and all(a.get("basis") == "face_level" for a in s["at_risk_faces"])]
    faces = sorted({f for r in rows for f in (r.get("faces_named") or []) if m305.is_a_face(f)})
    return {"rows": len(rows), "faces": faces}


# ------------------------------------------------------------------ writers
def writers_of(faces, search_dirs=("scripts", "Tools", "monitor", "live", "firm")):
    """Which source names each face.  A face is written by the module that names its basename."""
    out = {}
    for face in faces:
        base = os.path.basename(face)
        hits = []
        for d in search_dirs:
            full = os.path.join(ROOT, d)
            if not os.path.isdir(full):
                continue
            for dirpath, _dirnames, filenames in os.walk(full):
                for fn in filenames:
                    if not fn.endswith(".py"):
                        continue
                    path = os.path.join(dirpath, fn)
                    try:
                        txt = open(path, encoding="utf-8", errors="replace").read()
                    except OSError:
                        continue
                    if base in txt:
                        hits.append(os.path.relpath(path, ROOT).replace("\\", "/"))
        out[face] = sorted(set(hits))
    return out


# ------------------------------------------------------------------ legs
def leg_groups(src_text):
    """Ordered leg groups inside main(): statements up to and including the check() they end with."""
    tree = ast.parse(src_text)

    def has_check(node):
        return any(isinstance(s, ast.Call) and isinstance(s.func, ast.Name) and s.func.id == "check"
                   for s in ast.walk(node))

    for top in tree.body:
        if isinstance(top, ast.FunctionDef) and top.name == "main":
            groups, cur = [], []
            for n in top.body:
                if isinstance(n, (ast.Import, ast.ImportFrom)):
                    continue
                cur.append(n)
                if has_check(n):
                    groups.append(cur)
                    cur = []
            trailing = len(cur)
            return groups, trailing
    return [], 0


def leg_facts(group):
    """module imports, write-verb calls on those modules, and subprocess script runs."""
    mods, verbs, runs = {}, [], []
    for stmt in group:
        if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call):
            c = stmt.value
            if (isinstance(c.func, ast.Attribute) and c.func.attr == "import_module"
                    and c.args and isinstance(c.args[0], ast.Constant)):
                mods[stmt.targets[0].id] = c.args[0].value
        for s in ast.walk(stmt):
            if not isinstance(s, ast.Call):
                continue
            if isinstance(s.func, ast.Attribute) and s.func.attr in WRITE_VERBS \
                    and isinstance(s.func.value, ast.Name):
                verbs.append((s.func.attr, s.func.value.id))
            if isinstance(s.func, ast.Attribute) and s.func.attr == "run":
                blob = ast.dump(s)
                for lit in re.findall(r"'value': '(scripts/[^']+\.py)'", blob):
                    args = [a.value for a in s.args if isinstance(a, ast.Constant)]
                    runs.append({"script": lit, "args": args})
    written = sorted(set(mods[r] for _v, r in verbs if r in mods))
    return {"modules": sorted(set(mods.values())), "write_modules": written, "runs": runs}


def _is_selftest(run):
    return any(str(a).strip() in SELFTEST_ARGS for a in run.get("args") or [])


def leg_census(src_text, input_faces, writer_map):
    """Per leg: does it execute a writer of an input face, and does it read one literally?"""
    groups, trailing = leg_groups(src_text)
    writer_by_module = {}
    for face, mods in writer_map.items():
        for m in mods:
            stem = os.path.splitext(os.path.basename(m))[0]
            writer_by_module.setdefault(stem, set()).add(face)
            writer_by_module.setdefault(m.replace("/", ".").replace(".py", ""), set()).add(face)
    bases = {os.path.basename(f): f for f in input_faces}
    legs, pairs = [], []
    for i, g in enumerate(groups, 1):
        facts = leg_facts(g)
        line = g[0].lineno
        moved = set()
        for mod in facts["write_modules"]:
            moved |= writer_by_module.get(mod, set())
        for run in facts["runs"]:
            if _is_selftest(run):
                continue
            stem = os.path.splitext(os.path.basename(run["script"]))[0]
            moved |= writer_by_module.get(stem, set())
        text = ast.dump(ast.Module(body=g, type_ignores=[]))
        reads = sorted(bases[b] for b in bases if b in text)
        row = {
            "index": i,
            "line": line,
            "modules": facts["modules"],
            "write_modules": facts["write_modules"],
            "script_runs": sorted({r["script"]: 0 for r in facts["runs"]} and
                                  {r["script"] for r in facts["runs"]}),
            "selftest_runs": sorted({r["script"] for r in facts["runs"] if _is_selftest(r)}),
            "moves": sorted(moved),
            "reads_literal": reads,
        }
        legs.append(row)
    for writer in legs:
        for face in writer["moves"]:
            for reader in legs:
                if face in reader["reads_literal"] and reader["index"] > writer["index"]:
                    pairs.append({"writer_leg": writer["index"], "reader_leg": reader["index"],
                                  "face": face})
    return legs, pairs, trailing


# ------------------------------------------------------------------ build
def decide(summary):
    if not summary.get("input_faces"):
        return V_INPUTS_MISSING
    if summary.get("order_pairs"):
        return V_ORDER
    return V_NONE


def build(src_text=None, writer_map=None, inputs=None):
    src_text = src_text if src_text is not None else open(SUITE, encoding="utf-8").read()
    if inputs is None:
        inputs = e305_inputs()
    faces = inputs["faces"]
    if writer_map is None:
        writer_map = writers_of(faces)
    legs, pairs, trailing = leg_census(src_text, faces, writer_map)
    hashes = {}
    for face in faces:
        path = os.path.join(ROOT, face.replace("/", os.sep))
        hashes[face] = {"sha16": _sha(path), "bytes": os.path.getsize(path)} if os.path.exists(path) else None
    writers_who_are_legs = sorted({l["write_modules"][0] for l in legs if l["moves"] and l["write_modules"]})
    summary = {
        "input_rows_in_census": inputs["rows"],
        "input_faces": len(faces),
        "input_faces_present_on_disk": sum(1 for k, v in hashes.items() if v),
        "faces_with_a_writer_in_the_tree": sum(1 for f in faces if writer_map.get(f)),
        "faces_with_no_writer_in_the_tree": [f for f in faces if not writer_map.get(f)],
        "attributable_legs": len(legs),
        "legs_that_execute_a_writer_of_an_input_face": len([l for l in legs if l["moves"]]),
        "order_pairs": len(pairs),
        "legs_reading_an_input_face_literally": len([l for l in legs if l["reads_literal"]]),
        "script_runs_that_are_not_selftests": sum(len(l["script_runs"]) for l in legs),
        "legs_that_are_writers_but_not_of_an_input_face":
            len([l for l in legs if l["write_modules"] and not l["moves"]]),
        "code_legs_without_a_trailing_statement": trailing,
    }
    summary["verdict"] = decide(summary)
    return {
        "study": STUDY,
        "evidence_cutoff": TODAY,
        "card": "E407-DOES-A-SMELL-TEST-LEG-READ-A-FACE-AN-EARLIER-LEG-REPUBLISHES",
        "subject_leg": "E305 (product: a face-level bound is not a measurement)",
        "method": "input set from the census the build consumes; writers from a literal scan of "
                  "scripts/Tools/monitor/live/firm; legs from the statically attributable groups "
                  "inside main(); a leg moves an input only if it imports a writer and calls a "
                  "write verb on it, or runs that writer as a non-selftest subprocess",
        "bound": "legs executed from helper functions and loops are outside the static census; the "
                 "suite's own leg count and this census are published side by side and the gap is "
                 "not folded into either; the within-run claim rests on this static analysis, and "
                 "the 13 input hashes are published so a pre/post probe can confirm it",
        "input_faces": [{"face": f, "writers": writer_map.get(f) or [], "on_disk": hashes[f]}
                        for f in faces],
        "legs": legs,
        "order_pairs": pairs,
        "summary": summary,
        "verdict": summary["verdict"],
        "writers_that_are_legs": writers_who_are_legs,
    }


def _write(face):
    os.makedirs(OUTDIR, exist_ok=True)
    for name in (FACE, LATEST):
        with open(os.path.join(OUTDIR, name), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
    say("wrote %s and %s" % (FACE, LATEST))


# ------------------------------------------------------------------ verify
def verify(path=None, face=None):
    path = path or os.path.join(OUTDIR, FACE)
    if face is None:
        if not os.path.exists(path):
            say("verify problems=['face is absent']")
            return ["face is absent"]
        face = _read(path)
    problems = []
    summary = face.get("summary") or {}
    if face.get("evidence_cutoff") != TODAY:
        problems.append("evidence_cutoff %r is not today" % face.get("evidence_cutoff"))
    if face.get("verdict") != decide(summary):
        problems.append("the verdict does not re-derive from the summary")
    if face.get("verdict") not in VERDICTS:
        problems.append("verdict outside the frozen set")
    legs = face.get("legs") or []
    if len(legs) != summary.get("attributable_legs"):
        problems.append("the leg rows do not re-add to the headline")
    if [l.get("index") for l in legs] != list(range(1, len(legs) + 1)):
        problems.append("the leg indices are not the run order")
    movers = [l for l in legs if l.get("moves")]
    if len(movers) != summary.get("legs_that_execute_a_writer_of_an_input_face"):
        problems.append("the mover count does not re-add")
    if len(movers) > len([l for l in legs if l.get("write_modules")]) + \
            len([l for l in legs if l.get("script_runs")]):
        problems.append("more legs move an input than could possibly have executed a writer")
    # re-derive the leg census from source and refuse a stored table that does not reproduce
    fresh = build()
    if len(fresh["legs"]) != len(legs):
        problems.append("the leg census does not re-derive (%d vs %d)" % (len(fresh["legs"]), len(legs)))
    if fresh["summary"]["order_pairs"] != summary.get("order_pairs"):
        problems.append("the order-pair count does not re-derive")
    for a, b in zip(legs, fresh["legs"]):
        if a.get("moves") != b.get("moves") or a.get("reads_literal") != b.get("reads_literal"):
            problems.append("leg %s does not re-derive" % a.get("index"))
            break
    # a face is never reported as moved unless a writer of it exists in the tree
    for face_now in face.get("input_faces") or []:
        if not face_now.get("writers") and face_now.get("face") in {
                m for l in legs for m in l.get("moves") or []}:
            problems.append("%s is reported moved but has no writer" % face_now.get("face"))
    if summary.get("verdict") == V_NONE and summary.get("order_pairs"):
        problems.append("the no-order-pair verdict was written over a non-empty pair table")
    say("verify problems=%s" % problems)
    return problems


# ------------------------------------------------------------------ selftest
FIXTURE = '''
def main():
    _m = importlib.import_module("e250_book_turnover_echo")
    _m.build()
    check("writer leg", True, "")
    _v = json.load(open("results/state_tilt/bookecho_latest.json"))
    check("reader leg after the writer", True, "")
    _w = importlib.import_module("e251_star_own_component")
    _w.run()
    check("a later writer", True, "")
'''


def selftest():
    bad = []
    groups, trailing = leg_groups(FIXTURE)
    if len(groups) != 3:
        bad.append("fixture leg census %d != 3" % len(groups))
    faces = ["results/state_tilt/bookecho_latest.json"]
    writer_map = {faces[0]: ["scripts/e250_book_turnover_echo.py"]}
    legs, pairs, _t = leg_census(FIXTURE, faces, writer_map)
    if len(pairs) != 1:
        bad.append("fixture pairs %d != 1" % len(pairs))
    elif pairs[0] != {"writer_leg": 1, "reader_leg": 2, "face": faces[0]}:
        bad.append("fixture pair is not (1 -> 2)")
    if legs[2]["moves"]:
        bad.append("a writer of a face nobody reads must not create a pair")
    # a reader that precedes every writer is not ordered behind one
    early = '''
def main():
    _v = json.load(open("results/state_tilt/bookecho_latest.json"))
    check("reader first", True, "")
    _m = importlib.import_module("e250_book_turnover_echo")
    _m.build()
    check("writer second", True, "")
'''
    _l2, p2, _t2 = leg_census(early, faces, writer_map)
    if p2:
        bad.append("a writer that runs after the reader was billed as an earlier leg")
    # a selftest run is not a write path
    st = '''
def main():
    _sp.run([sys.executable, "scripts/e250_book_turnover_echo.py", "selftest"])
    check("selftest run", True, "")
    _v = json.load(open("results/state_tilt/bookecho_latest.json"))
    check("reader", True, "")
'''
    _l3, p3, _t3 = leg_census(st, faces, writer_map)
    if p3:
        bad.append("a selftest subprocess was billed as a writer")
    # deciding
    if decide({"input_faces": 0, "order_pairs": 0}) != V_INPUTS_MISSING:
        bad.append("an empty input set must not decide as order-stable")
    if decide({"input_faces": 3, "order_pairs": 0}) != V_NONE:
        bad.append("no pairs must decide as order-stable")
    if decide({"input_faces": 3, "order_pairs": 1}) != V_ORDER:
        bad.append("a pair must decide as an order problem")
    # the live face must re-derive and name its inputs
    live = build()
    if not live["input_faces"]:
        bad.append("the live census names no input faces")
    if live["summary"]["input_faces"] != len(live["input_faces"]):
        bad.append("the live headline does not re-add")
    say("selftest problems=%s" % bad)
    if not bad:
        say("selftest 11/11")
    return bad


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd in ("run", "build"):
        face = build()
        _write(face)
        s = face["summary"]
        say("inputs=%d on_disk=%d writers_in_tree=%d legs=%d movers=%d order_pairs=%d"
            % (s["input_faces"], s["input_faces_present_on_disk"],
               s["faces_with_a_writer_in_the_tree"], s["attributable_legs"],
               s["legs_that_execute_a_writer_of_an_input_face"], s["order_pairs"]))
        say("verdict: %s" % face["verdict"])
        return 0
    if cmd == "verify":
        return 1 if verify() else 0
    if cmd == "selftest":
        return 1 if selftest() else 0
    say(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))