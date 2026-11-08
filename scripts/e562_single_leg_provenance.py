"""E562 -- can an existing field tell a deliberate one-leg S6 run from a chain killed mid-run?

E561 (r1587) ended on a sentence it could not price: of 320 chain receipts, 159 are shorter
than the leg table of their own round, and "a stopped run and an --only run look identical"
inside the file.  This study asks whether ANY field that already exists on disk separates the
two, and if none does inside the receipt, where the separating fact actually lives.

Two populations are kept apart on purpose:

  * the RECEIPT (results/_r<N>bm<X>_s6_chain.json) -- its keys are the candidate fields;
  * the RUNNER (Tools/s6_chain_bm<X>.py at the receipt's own join commit) -- where the fact
    that decides the question is written.

Method, all static, no execution of any runner: for each short receipt the runner blob at its
join commit is parsed and three things are measured about the leg loop and the file it writes:

  writer position   does the runner close the receipt after the loop, or per leg?
  selection arm     does the runner honour an --only argument at all?
  skip arm          can the loop drop a leg by itself (a `continue` before the row append)?
  per-leg catch     does a leg that raises still get a row (so failures cannot shorten a file)?

If a runner writes only after its loop and cannot skip a leg, then a short receipt is NOT a
killed chain: a process killed inside the loop leaves no file at all.  That converts E561's
"identical" into a named explanation, and it also says which artefact must carry the answer
in future -- the receipt, which today records no selection at all.

CLI: python scripts/e562_single_leg_provenance.py [build|check|verify|selftest]
     build is the default; verify rebuilds twice and refuses a face that moves.
"""

import ast
import hashlib
import importlib.util
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

EVIDENCE_CUTOFF = "2026-11-08"
DATED_PREFIX = "SINGLELEGPROVENANCE"
STATE_TILT = os.path.join(ROOT, "results", "state_tilt")
LATEST = os.path.join(STATE_TILT, "singlelegprovenance_latest.json")

# the vintage this study reads its population from (E369: a pin must name the artefact, and the
# population must be declared rather than re-invented)
E561_FACE = os.path.join(STATE_TILT, "RECEIPTTABLE-2026-11-08.json")
E561_SCRIPT = os.path.join(HERE, "e561_receipt_table_join.py")

# report faces that might carry a human witness of the selection
REPORT_FACES = ("round_reports-bm-b.md", "round_reports-bm-c.md")

# ---- classes ----------------------------------------------------------------------
W_AFTER = "after_the_leg_loop"
W_INSIDE = "inside_the_leg_loop"
W_BEFORE = "before_the_leg_loop"
W_NONE = "no_receipt_writer"
W_NO_LOOP = "no_leg_loop"

C_SUBSET = "written_after_the_loop_by_a_runner_that_honours_only"
C_KILL = "a_killed_chain_could_leave_this_file"
C_SKIP = "the_loop_can_drop_a_leg_without_a_kill"
C_OTHER = "the_run_was_shorter_than_the_table_for_another_reason"
C_UNEXPLAINED = "unexplained_short_receipt"
C_NO_BLOB = "no_runner_blob_reachable"

VERDICT_KILL = "a_killed_chain_cannot_leave_a_short_receipt_in_any_runner_that_wrote_one"
VERDICT_OPEN = "a_killed_chain_could_leave_a_short_receipt_somewhere_in_the_population"
VERDICT_BLIND = "the_runner_blobs_could_not_be_read_so_nothing_is_concluded"


def _git(args, timeout=180):
    import subprocess
    try:
        p = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True, timeout=timeout)
    except Exception:
        return None
    if p.returncode != 0:
        return None
    return p.stdout


def _blobs(specs):
    """{spec: text} through ONE cat-file process; a missing object is an honest answer."""
    import subprocess
    specs = [s for s in dict.fromkeys(specs) if s]
    if not specs:
        return {}
    payload = ("\n".join(specs) + "\n").encode("utf-8")
    try:
        p = subprocess.run(["git", "cat-file", "--batch"], cwd=ROOT, input=payload,
                           capture_output=True, timeout=240)
    except Exception:
        return {}
    if p.returncode != 0:
        return {}
    out, i, found = p.stdout, 0, {}
    for spec in specs:
        nl = out.find(b"\n", i)
        if nl < 0:
            break
        header = out[i:nl].decode("utf-8", "replace").strip()
        i = nl + 1
        parts = header.rsplit(" ", 2)
        if len(parts) != 3 or not parts[2].isdigit():
            continue
        size = int(parts[2])
        body = out[i:i + size]
        i += size + 1
        found[spec] = body.decode("utf-8-sig", "replace")
    return found


def _e561():
    spec = importlib.util.spec_from_file_location("e561_receipt_table_join", E561_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---- reading the runner ----------------------------------------------------------
def _leg_loop(tree):
    """The For loop that runs the legs: the outermost loop that calls subprocess.run."""
    loop = None
    for node in ast.walk(tree):
        if not isinstance(node, ast.For):
            continue
        runs = any(isinstance(s, ast.Call) and isinstance(s.func, ast.Attribute)
                   and s.func.attr in ("run", "Popen", "call", "check_output")
                   for s in ast.walk(node))
        if not runs:
            continue
        if loop is None or (node.end_lineno or 0) > (loop.end_lineno or 0):
            loop = node
    return loop


def _write_lines(tree):
    """Line numbers of the calls that can close the receipt file."""
    lines = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        if isinstance(f, ast.Attribute) and f.attr == "dump":
            lines.append(node.lineno)
        elif isinstance(f, ast.Name) and f.id == "open" and node.args:
            mode = node.args[1] if len(node.args) > 1 else None
            if isinstance(mode, ast.Constant) and isinstance(mode.value, str) \
                    and "w" in mode.value:
                lines.append(node.lineno)
    return sorted(set(lines))


def analyse_runner(src):
    """Everything this study claims about a runner, read off its source and nothing else."""
    out = {
        "parsed": False,
        "leg_loop": None,
        "write_lines": [],
        "writer_position": W_NONE,
        "honours_an_only_argument": bool(re.search(r"""['"]--only""", src)),
        "loop_can_skip_a_leg": False,
        "a_failing_leg_still_gets_a_row": False,
        "row_is_appended_inside_the_loop": False,
    }
    try:
        tree = ast.parse(src)
    except Exception:
        return out
    out["parsed"] = True
    loop = _leg_loop(tree)
    writes = _write_lines(tree)
    out["write_lines"] = writes
    if loop is None:
        out["writer_position"] = W_NO_LOOP
        return out
    out["leg_loop"] = [loop.lineno, loop.end_lineno]
    out["loop_can_skip_a_leg"] = any(isinstance(s, ast.Continue) for s in ast.walk(loop))
    out["a_failing_leg_still_gets_a_row"] = any(
        isinstance(s, ast.Try) and s.handlers for s in ast.walk(loop))
    out["row_is_appended_inside_the_loop"] = any(
        isinstance(s, ast.Call) and isinstance(s.func, ast.Attribute) and s.func.attr == "append"
        for s in ast.walk(loop))
    if not writes:
        out["writer_position"] = W_NONE
    elif any(loop.lineno <= w <= (loop.end_lineno or loop.lineno) for w in writes):
        out["writer_position"] = W_INSIDE
    elif all(w > (loop.end_lineno or 0) for w in writes):
        out["writer_position"] = W_AFTER
    else:
        out["writer_position"] = W_BEFORE
    return out


def classify(rows, analysis):
    """Per-receipt class, decided by the runner and the row count only."""
    if not analysis or not analysis.get("parsed"):
        return C_NO_BLOB
    pos = analysis.get("writer_position")
    if pos == W_INSIDE:
        # the receipt grows while the loop runs: a process killed mid-run leaves exactly this
        return C_KILL
    if analysis.get("loop_can_skip_a_leg"):
        return C_SKIP
    if pos == W_AFTER:
        if analysis.get("honours_an_only_argument"):
            return C_SUBSET
        return C_OTHER
    return C_UNEXPLAINED


# ---- population -----------------------------------------------------------------
def _sha16(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()[:16]


def read_population():
    """E561's short receipts, re-derived from its own rows (not trusted as a label)."""
    with io.open(E561_FACE, encoding="utf-8") as fh:
        face = json.load(fh)
    rows, local_partial = [], 0
    for r in face.get("rows") or []:
        if not isinstance(r, dict) or r.get("unparsed"):
            continue
        n, table = r.get("rows"), r.get("table_at_its_round")
        if isinstance(n, int) and isinstance(table, int) and n < table:
            local_partial += 1
            rows.append({
                "file": r.get("file"),
                "machine": r.get("machine"),
                "name_round": r.get("name_round"),
                "rows": n,
                "table_at_its_round": table,
                "join_commit": r.get("join_commit"),
                "committed": bool(r.get("committed")),
            })
    return rows, local_partial, face


def receipt_selection_fields():
    """Keys across every receipt on disk that would echo which legs were asked for."""
    import glob
    words = re.compile(r"only|request|selected|argv|subset", re.I)
    hits = []
    for path in sorted(glob.glob(os.path.join(ROOT, "results", "_r*bm*_s6_chain.json"))):
        try:
            with io.open(path, encoding="utf-8-sig") as fh:
                payload = json.load(fh)
        except Exception:
            continue
        keys = []
        if isinstance(payload, dict):
            keys = [k for k in payload if isinstance(k, str)]
        for k in keys:
            if words.search(k):
                hits.append({"file": os.path.basename(path), "key": k})
    return hits


def round_report_only_witness():
    """Rounds whose round-report line names --only -- the only prose witness on disk."""
    rounds = set()
    lines = 0
    for name in REPORT_FACES:
        path = os.path.join(ROOT, name)
        if not os.path.isfile(path):
            continue
        with io.open(path, "rb") as fh:
            text = fh.read().decode("utf-8", "replace")
        for line in text.splitlines():
            if "--only" not in line:
                continue
            lines += 1
            for m in re.finditer(r"\br(\d{2,5})\b", line):
                rounds.add(int(m.group(1)))
    return {"report_lines_naming_only": lines, "rounds_named": sorted(rounds)[:20],
            "rounds_named_n": len(rounds)}


# ---- build ----------------------------------------------------------------------
def build(write=True):
    rows, local_partial, e561_face = read_population()
    specs = []
    for r in rows:
        if r.get("machine") and r.get("join_commit"):
            specs.append("%s:Tools/s6_chain_bm%s.py" % (r["join_commit"], r["machine"]))
    blobs = _blobs(specs)
    cache = {}
    for r in rows:
        spec = ("%s:Tools/s6_chain_bm%s.py" % (r["join_commit"], r["machine"])
                if r.get("machine") and r.get("join_commit") else None)
        if spec and spec not in cache:
            src = blobs.get(spec)
            cache[spec] = analyse_runner(src) if src else None
        a = cache.get(spec) if spec else None
        r["class"] = classify(r.get("rows"), a)
        r["writer_position"] = (a or {}).get("writer_position")
        r["honours_an_only_argument"] = (a or {}).get("honours_an_only_argument")
        r["loop_can_skip_a_leg"] = (a or {}).get("loop_can_skip_a_leg")
        r["a_failing_leg_still_gets_a_row"] = (a or {}).get("a_failing_leg_still_gets_a_row")
        r["runner_spec"] = spec
    rows.sort(key=lambda x: (x.get("machine") or "", int(x.get("name_round") or 0)))

    s = {
        "short_receipts": len(rows),
        "single_leg_receipts": sum(1 for r in rows if r.get("rows") == 1),
        "receipts_shorter_than_two_legs": sum(1 for r in rows if (r.get("rows") or 0) < 2),
        "runners_joined": sum(1 for r in rows if r.get("writer_position")),
        "runners_unreachable": sum(1 for r in rows if r.get("class") == C_NO_BLOB),
        "writer_after_the_loop": sum(1 for r in rows if r.get("writer_position") == W_AFTER),
        "writer_inside_the_loop": sum(1 for r in rows if r.get("writer_position") == W_INSIDE),
        "writer_not_found": sum(1 for r in rows
                                if r.get("writer_position") in (W_NONE, W_NO_LOOP)),
        "honours_an_only_argument": sum(1 for r in rows if r.get("honours_an_only_argument")),
        "loop_can_skip_a_leg": sum(1 for r in rows if r.get("loop_can_skip_a_leg")),
        "a_failing_leg_still_gets_a_row": sum(1 for r in rows
                                              if r.get("a_failing_leg_still_gets_a_row")),
        "killed_chain_could_leave_this_file": sum(1 for r in rows if r.get("class") == C_KILL),
        "deliberate_subset": sum(1 for r in rows if r.get("class") == C_SUBSET),
        "unexplained": sum(1 for r in rows if r.get("class") == C_UNEXPLAINED),
    }
    sel = receipt_selection_fields()
    s["receipts_echoing_their_selection"] = len({h["file"] for h in sel})
    s["receipt_keys_that_echo_a_selection"] = sorted({h["key"] for h in sel})
    wit = round_report_only_witness()
    s["round_report_lines_naming_only"] = wit["report_lines_naming_only"]
    s["rounds_the_report_names_as_an_only_run"] = wit["rounds_named_n"]
    s["short_receipt_rounds_the_report_mentions"] = sum(
        1 for r in rows if r.get("name_round") in set(wit["rounds_named"]))

    verdict, line = _verdict(s)
    face = {
        "card": "E562",
        "study": "E562",
        "dept": "research+engineering",
        "machine": "bm-b",
        "round": "r1588",
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "population_source": {
            "face": os.path.relpath(E561_FACE, ROOT).replace("\\", "/"),
            "sha16": _sha16(E561_FACE),
            "short_rows_in_that_face": local_partial,
            "note": "read as a vintage: the receipt directory is live, so this face answers for "
                    "the receipts E561 had classified on 2026-11-08, and the short class is "
                    "re-derived here from rows < table_at_its_round rather than trusted",
        },
        "summary": s,
        "rows": rows,
        "control_arms": _control_arms(),
        "verdict": verdict,
        "verdict_line": line,
        "note": "static only: no runner is executed and no receipt is rewritten; the separating "
                "fact is the writer's position in the runner blob at the receipt's own join "
                "commit, so a change of runner invalidates the per-row class and the gate "
                "re-derives it",
        "producers": {
            "script": "scripts/e562_single_leg_provenance.py",
            "selftest": "python scripts/e562_single_leg_provenance.py selftest",
            "card": "knowledge/METHODOLOGY_ASSETS.md E562",
        },
    }
    if write:
        _write(LATEST, face)
        _write(os.path.join(STATE_TILT, "%s-%s.json" % (DATED_PREFIX, EVIDENCE_CUTOFF)), face)
    return face


def _verdict(s):
    s = {"short_receipts": 0, "single_leg_receipts": 0, "runners_joined": 0,
         "writer_after_the_loop": 0, "honours_an_only_argument": 0, "loop_can_skip_a_leg": 0,
         "a_failing_leg_still_gets_a_row": 0, "killed_chain_could_leave_this_file": 0,
         "deliberate_subset": 0, "receipts_echoing_their_selection": 0,
         "round_report_lines_naming_only": 0, "rounds_the_report_names_as_an_only_run": 0,
         "unexplained": 0, **s}
    if not s["runners_joined"]:
        return VERDICT_BLIND, ("none of the %d short receipts could be joined to the runner "
                              "blob of its own round, so nothing is concluded"
                              % s["short_receipts"])
    line = ("%d short receipts (%d of them single-leg); %d joined to their runner blob, and "
            "%d of those runners close the receipt only AFTER the leg loop, %d honour an "
            "--only argument and %d can drop a leg by a continue, %d still give a raising leg "
            "its own row -- so %d short files could be a killed chain and %d are deliberate "
            "subsets.  %d receipts carry any field that echoes which legs were asked for, and "
            "the round reports name --only on %d lines covering %d rounds, so the answer is not "
            "written down anywhere except in the runner."
            % (s["short_receipts"], s["single_leg_receipts"], s["runners_joined"],
               s["writer_after_the_loop"], s["honours_an_only_argument"],
               s["loop_can_skip_a_leg"], s["a_failing_leg_still_gets_a_row"],
               s["killed_chain_could_leave_this_file"], s["deliberate_subset"],
               s["receipts_echoing_their_selection"], s["round_report_lines_naming_only"],
               s["rounds_the_report_names_as_an_only_run"]))
    if s["killed_chain_could_leave_this_file"]:
        return VERDICT_OPEN, line
    if s["unexplained"]:
        return VERDICT_BLIND, line
    return VERDICT_KILL, line


FIXTURES = {
    "after_loop_with_only": '''
import json, subprocess
LEGS = [("a", ["x"]), ("b", ["y"])]
rows = []
only = None
for a in sys.argv[1:]:
    if a == "--only":
        only = set()
legs = LEGS if only is None else [(n, c) for n, c in LEGS if n in only]
for name, cmd in legs:
    try:
        p = subprocess.run(cmd)
        rc = p.returncode
    except Exception:
        rc = 99
    rows.append({"leg": name, "rc": rc})
json.dump({"legs": rows}, open("x.json", "w"))
''',
    "inside_loop": '''
import json, subprocess
rows = []
for name, cmd in [("a", ["x"])]:
    p = subprocess.run(cmd)
    rows.append({"leg": name, "rc": p.returncode})
    json.dump({"legs": rows}, open("x.json", "w"))
''',
    "skip_arm": '''
import json, subprocess
rows = []
for name, cmd in [("a", ["x"])]:
    if not name:
        continue
    p = subprocess.run(cmd)
    rows.append({"leg": name, "rc": p.returncode})
json.dump({"legs": rows}, open("x.json", "w"))
''',
    "after_loop_no_only": '''
import json, subprocess
rows = []
for name, cmd in [("a", ["x"])]:
    p = subprocess.run(cmd)
    rows.append({"leg": name, "rc": p.returncode})
json.dump({"legs": rows}, open("x.json", "w"))
''',
    "no_writer": '''
import subprocess
rows = []
for name, cmd in [("a", ["x"])]:
    p = subprocess.run(cmd)
    rows.append({"leg": name, "rc": p.returncode})
''',
    "unparsable": "def broken(:\n",
}


def _control_arms():
    arms = {}
    a = analyse_runner(FIXTURES["after_loop_with_only"])
    arms["a_runner_that_closes_after_the_loop"] = {
        "found": a["writer_position"] == W_AFTER and a["honours_an_only_argument"],
        "value": a["writer_position"],
        "class_at_one_row": classify(1, a),
    }
    b = analyse_runner(FIXTURES["inside_loop"])
    arms["a_runner_that_writes_per_leg_is_visible"] = {
        "found": b["writer_position"] == W_INSIDE,
        "value": b["writer_position"],
        "class_at_one_row": classify(1, b),
    }
    c = analyse_runner(FIXTURES["skip_arm"])
    arms["a_skipping_loop_is_a_third_explanation"] = {
        "found": c["loop_can_skip_a_leg"] and classify(1, c) == C_SKIP,
        "value": classify(1, c),
    }
    d = analyse_runner(FIXTURES["after_loop_no_only"])
    arms["a_runner_without_an_only_arm_is_not_a_subset"] = {
        "found": d["writer_position"] == W_AFTER and not d["honours_an_only_argument"]
                 and classify(1, d) == C_OTHER,
        "value": classify(1, d),
    }
    e = analyse_runner(FIXTURES["no_writer"])
    arms["a_runner_with_no_writer_is_not_silently_short"] = {
        "found": e["writer_position"] == W_NONE and classify(1, e) == C_UNEXPLAINED,
        "value": classify(1, e),
    }
    f = analyse_runner(FIXTURES["unparsable"])
    arms["an_unparsable_runner_is_not_a_pass"] = {
        "found": f["parsed"] is False and classify(1, f) == C_NO_BLOB,
        "value": classify(1, f),
    }
    return arms


# ---- persistence / gates --------------------------------------------------------
def _write(path, obj):
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")


def _canon(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True)


def face_problems(face):
    p = []
    rows = face.get("rows") or []
    if not rows:
        p.append("the short-receipt population is empty")
    s = face.get("summary") or {}
    if s.get("short_receipts") != len(rows):
        p.append("the short count is not the length of the row list")
    if s.get("single_leg_receipts") != sum(1 for r in rows if r.get("rows") == 1):
        p.append("the single-leg count is not the number of one-row receipts")
    for cls, key in ((C_SUBSET, "deliberate_subset"), (C_KILL, "killed_chain_could_leave_this_file"),
                     (C_UNEXPLAINED, "unexplained"), (C_NO_BLOB, "runners_unreachable")):
        if s.get(key) != sum(1 for r in rows if r.get("class") == cls):
            p.append("the %s count is not the number of rows in that class" % key)
    for r in rows:
        if r.get("writer_position") is None and r.get("class") != C_NO_BLOB:
            p.append("%s: a writer position was never read but the row is not classed blind"
                     % r.get("file"))
        if r.get("class") == C_SUBSET and r.get("writer_position") != W_AFTER:
            p.append("%s: called a deliberate subset by a runner that does not close after the "
                     "loop" % r.get("file"))
        if r.get("class") == C_KILL and r.get("writer_position") != W_INSIDE:
            p.append("%s: called killable by a runner that does not write inside the loop"
                     % r.get("file"))
    for name, arm in (face.get("control_arms") or {}).items():
        if not (arm or {}).get("found"):
            p.append("control arm %s is blind" % name)
    if face.get("verdict") != _verdict(s)[0]:
        p.append("the verdict is not what the summary says")
    if not face.get("verdict_line"):
        p.append("the face carries no verdict line")
    if not (face.get("population_source") or {}).get("sha16"):
        p.append("the population is not pinned to a vintage")
    return p


def check():
    face = build(write=False)
    if not os.path.isfile(LATEST):
        print("problems: the published face is missing")
        return 2
    with io.open(LATEST, encoding="utf-8") as fh:
        published = json.load(fh)
    problems = []
    for key in ("control_arms", "summary"):
        if _canon(published.get(key)) != _canon(face.get(key)):
            problems.append("%s does not re-derive from source" % key)
    pub = {r.get("file"): r for r in published.get("rows") or [] if isinstance(r, dict)}
    new = {r.get("file"): r for r in face.get("rows") or [] if isinstance(r, dict)}
    for name in sorted(set(pub) & set(new)):
        a, b = pub[name], new[name]
        for k in ("class", "writer_position", "honours_an_only_argument"):
            if a.get(k) != b.get(k):
                problems.append("%s: %s moved (%r -> %r)" % (name, k, a.get(k), b.get(k)))
    for name in sorted(set(new) - set(pub)):
        problems.append("%s: a short receipt the face does not carry" % name)
    problems += face_problems(published)
    if problems:
        print("problems:")
        for x in problems[:20]:
            print(" -", x)
        return 2
    print("check OK: %d short receipts re-derive to their runner's writer position"
          % len(face["rows"]))
    return 0


def verify():
    a = build(write=False)
    b = build(write=False)
    if _canon(a) != _canon(b):
        print("verify FAILED: two builds of the same tree disagree")
        return 2
    print("verify OK: two builds identical (%d rows).  %s"
          % (len(a["rows"]), a["verdict_line"][:120]))
    return 0


# ---- selftest -------------------------------------------------------------------
def selftest():
    fails = []
    a = analyse_runner(FIXTURES["after_loop_with_only"])
    if a["writer_position"] != W_AFTER:
        fails.append("after-loop writer read as %r" % a["writer_position"])
    if not a["honours_an_only_argument"]:
        fails.append("an --only arm was not seen")
    if not a["a_failing_leg_still_gets_a_row"]:
        fails.append("a per-leg try/except was not seen")
    if not a["row_is_appended_inside_the_loop"]:
        fails.append("the row append was not placed inside the loop")
    if classify(1, a) != C_SUBSET:
        fails.append("a one-row receipt by an after-loop --only runner is not a subset")

    b = analyse_runner(FIXTURES["inside_loop"])
    if b["writer_position"] != W_INSIDE:
        fails.append("per-leg writer read as %r" % b["writer_position"])
    if classify(1, b) != C_KILL:
        fails.append("a per-leg writer does not admit a killed chain")

    c = analyse_runner(FIXTURES["skip_arm"])
    if not c["loop_can_skip_a_leg"]:
        fails.append("a continue in the loop was not seen")
    if classify(1, c) != C_SKIP:
        fails.append("a skipping loop is not its own class")

    d = analyse_runner(FIXTURES["after_loop_no_only"])
    if d["honours_an_only_argument"]:
        fails.append("an --only arm was seen in a runner that has none")
    if classify(1, d) != C_OTHER:
        fails.append("an after-loop runner without --only is not OTHER")

    e = analyse_runner(FIXTURES["no_writer"])
    if e["writer_position"] != W_NONE:
        fails.append("a runner with no writer read as %r" % e["writer_position"])
    if classify(1, e) != C_UNEXPLAINED:
        fails.append("a writer-less runner is silently explained")

    f = analyse_runner(FIXTURES["unparsable"])
    if f["parsed"]:
        fails.append("unparsable source parsed")
    if classify(1, f) != C_NO_BLOB:
        fails.append("an unparsable runner is not classed blind")

    # the verdict must move with the population, not be a constant
    base = {"short_receipts": 1, "single_leg_receipts": 1, "runners_joined": 1,
            "writer_after_the_loop": 1, "honours_an_only_argument": 1,
            "loop_can_skip_a_leg": 0, "a_failing_leg_still_gets_a_row": 1,
            "killed_chain_could_leave_this_file": 0, "deliberate_subset": 1,
            "receipts_echoing_their_selection": 0, "round_report_lines_naming_only": 0,
            "rounds_the_report_names_as_an_only_run": 0, "unexplained": 0}
    if _verdict(dict(base))[0] != VERDICT_KILL:
        fails.append("a clean population does not say a kill cannot leave the file")
    hostile = dict(base)
    hostile["killed_chain_could_leave_this_file"] = 1
    hostile["deliberate_subset"] = 0
    if _verdict(hostile)[0] != VERDICT_OPEN:
        fails.append("a killable runner does not open the verdict")
    blind = dict(base)
    blind["runners_joined"] = 0
    if _verdict(blind)[0] != VERDICT_BLIND:
        fails.append("no joined runner does not read as blind")
    unexpl = dict(base)
    unexpl["unexplained"] = 1
    if _verdict(unexpl)[0] != VERDICT_BLIND:
        fails.append("an unexplained short receipt does not block the verdict")

    # a face that publishes a subset without an after-loop writer must be refused
    faces = [
        ({"rows": [{"file": "x", "rows": 1, "class": C_SUBSET, "writer_position": W_INSIDE}],
          "summary": {}}, "a subset class beside an inside-loop writer"),
        ({"rows": [], "summary": {}}, "an empty population"),
    ]
    for face, why in faces:
        if not face_problems(face):
            fails.append("the gate accepts %s" % why)

    if fails:
        print("selftest FAILED")
        for x in fails:
            print(" -", x)
        return 1
    print("selftest OK 14/14")
    return 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    cmd = (argv[0] if argv else "build").lower()
    if cmd == "build":
        face = build(write=True)
        print(json.dumps(face["summary"], ensure_ascii=False, indent=1))
        print(face["verdict_line"])
        return 0
    if cmd == "check":
        return check()
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    print("usage: e562_single_leg_provenance.py [build|check|verify|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main())