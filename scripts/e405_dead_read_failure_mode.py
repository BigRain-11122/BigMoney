"""E405 -- an absent read target is only a defect if a reader would fail; does it?

E404 published three in-tree files no writer produces (``in_tree_absent_reads: 3``) and stopped at
the join.  That count is a statement about the *path*, not about the *reader*: a join line can be a
write, a module constant, or an existence test, and the file can be absent because a stage has not
run yet.  This study asks the question that decides whether a human should care:

  for each published site -- what is the join line actually doing, who consumes that path, and does
  the consumer raise, refuse, or quietly return nothing?

One vocabulary per evidence, so the classes cannot be re-read as something they are not:

  U1 join_lands_on_a_write_not_a_read          open(path,'w') / json.dump(..., fh)
  U2 module_constant_not_a_read_at_this_line   NAME = os.path.join(...) at module level
  U3 read_site                                 open(path) / json.load(open(path))
  U4 neither_a_read_nor_a_write                anything else (prints, existence tests)

  C1 writer                 feeds _dump / json.dump / open(...,'w')
  C2 existence_gate         os.path.exists(NAME) -- a test, not a read
  C3 status_report          NAME printed in a checklist
  C4 guarded_read           reads NAME inside a function that refuses with a non-zero exit first
  C5 unguarded_read         reads NAME with no existence gate -> FileNotFoundError
  C6 directory_enumeration  glob/listdir over the parent: an absent member is silently omitted
  C7 other_reference        anything else

  M_loud    loud_refuse_nonzero_exit
  M_raise   raises_filenotfounderror
  M_silent  silent_default_or_silent_omission
  M_pending pending_output_of_a_stage_that_has_not_run
  M_notread not_a_read

Population is machine-read from the published E404 face (never hand-copied); every classification is
recomputed from the live source by AST, and no reader is edited.

Usage:
  python scripts/e405_dead_read_failure_mode.py run
  python scripts/e405_dead_read_failure_mode.py verify
  python scripts/e405_dead_read_failure_mode.py selftest
"""
from __future__ import annotations

import ast
import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

EV_CUTOFF = "2026-11-04"
FACE = "DEADREAD-%s.json" % EV_CUTOFF
LATEST = "deadread_latest.json"
PUBLISHED_DIR = os.path.join(ROOT, "results", "state_tilt")
STUDY = "E405_dead_read_failure_mode"
SELF_REL = "scripts/e405_dead_read_failure_mode.py"
POPULATION_SOURCE = "results/state_tilt/CONSTDIRS-%s.json" % EV_CUTOFF

U1 = "join_lands_on_a_write_not_a_read"
U2 = "module_constant_not_a_read_at_this_line"
U3 = "read_site"
U4 = "neither_a_read_nor_a_write"
USE_CLASSES = (U1, U2, U3, U4)

C1 = "writer"
C2 = "existence_gate"
C3 = "status_report"
C4 = "guarded_read"
C5 = "unguarded_read"
C6 = "directory_enumeration"
C7 = "other_reference"
C8 = "passed_to_a_landing_helper"
CONSUMER_CLASSES = (C1, C2, C3, C4, C5, C6, C7, C8)

M_LOUD = "loud_refuse_nonzero_exit"
M_RAISE = "raises_filenotfounderror"
M_SILENT = "silent_default_or_silent_omission"
M_PENDING = "pending_output_of_a_stage_that_has_not_run"
M_NOTREAD = "not_a_read"
M_UNGRADED = "not_graded_this_arm_sees_the_reference_not_its_effect"
FAILURE_MODES = (M_LOUD, M_RAISE, M_SILENT, M_PENDING, M_NOTREAD, M_UNGRADED)

V_MISPREMISE = ("none_of_the_published_sites_reads_its_target_at_the_join_line_so_the_question_was_"
                "mis_premised_two_are_module_constants_and_one_is_a_write")
V_LOUD = ("every_name_based_consumer_refuses_with_a_nonzero_exit_when_the_target_is_absent_so_the_"
          "absence_is_loud")
V_RAISES = ("at_least_one_consumer_reads_the_target_with_no_existence_gate_so_an_absent_file_"
            "raises_filenotfounderror_at_use_time")
V_SILENT = ("at_least_one_consumer_enumerates_the_parent_directory_so_an_absent_member_is_silently_"
            "omitted_and_nothing_fails")
V_MIXED = ("readers_and_enumeration_disagree_loud_name_based_consumers_and_a_silent_directory_"
           "enumerating_one")


def say(message):
    print(message, flush=True)


def _read(relpath):
    with open(os.path.join(ROOT, relpath), encoding="utf-8", errors="replace") as fh:
        return fh.read()


def _dump(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, indent=1, ensure_ascii=False)
        fh.write("\n")


# --------------------------------------------------------------------------- AST helpers

class Ctx(object):
    """Parent map + source for one file, parsed once."""

    def __init__(self, relpath, text=None):
        self.relpath = relpath
        self.text = text if text is not None else _read(relpath)
        self.tree = ast.parse(self.text)
        self.parent = {}
        for node in ast.walk(self.tree):
            for child in ast.iter_child_nodes(node):
                self.parent[child] = node

    def src(self, node):
        try:
            return ast.get_source_segment(self.text, node) or ""
        except Exception:
            return ""

    def ancestors(self, node):
        out = []
        cur = self.parent.get(node)
        while cur is not None:
            out.append(cur)
            cur = self.parent.get(cur)
        return out

    def enclosing_def(self, node):
        for anc in self.ancestors(node):
            if isinstance(anc, (ast.FunctionDef, ast.AsyncFunctionDef)):
                return anc
        return None


def _consts(node):
    """String constants inside a subtree."""
    out = []
    for sub in ast.walk(node):
        if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
            out.append(sub.value)
    return out


def _call_name(call):
    fn = call.func
    if isinstance(fn, ast.Name):
        return fn.id
    if isinstance(fn, ast.Attribute):
        return fn.attr
    return ""


def _mode_of(call):
    """Literal mode of an open() call, else ''."""
    for arg in call.args[1:]:
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            return arg.value
    for kw in call.keywords:
        if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
            return str(kw.value.value)
    return "r"


def _nodes_on_line(ctx, lineno, fragment):
    """Nodes whose own line is `lineno` and whose subtree mentions `fragment`."""
    hits = []
    for node in ast.walk(ctx.tree):
        if getattr(node, "lineno", None) != lineno:
            continue
        if fragment in _consts(node):
            hits.append(node)
    return hits


def _first_use(ctx, name, after_line):
    """The first later load of `name`; what the assigned path is actually used for."""
    best = None
    for node in ast.walk(ctx.tree):
        if isinstance(node, ast.Name) and node.id == name and isinstance(node.ctx, ast.Load) \
                and node.lineno > after_line:
            if best is None or node.lineno < best.lineno:
                best = node
    if best is None:
        return U4, "the assigned path is never used again"
    for anc in ctx.ancestors(best):
        if isinstance(anc, ast.Call):
            fname = _call_name(anc)
            if fname == "open":
                mode = _mode_of(anc)
                if "w" in mode or "a" in mode:
                    return U1, "open(mode=%r) of the assigned path at line %d" % (mode, anc.lineno)
                return U3, "open(mode=%r) of the assigned path at line %d" % (mode, anc.lineno)
            if fname == "dump":
                return U1, "json.dump of the assigned path at line %d" % anc.lineno
            break
        if isinstance(anc, (ast.FunctionDef, ast.AsyncFunctionDef)):
            break
    return U4, "first later use at line %d is not a file open" % best.lineno


def classify_site(ctx, lineno, fragment):
    """What is the join line doing?  Returns (use_class, name, detail)."""
    hits = _nodes_on_line(ctx, lineno, fragment)
    calls = [n for n in hits if isinstance(n, ast.Call)]
    for call in calls:
        name = _call_name(call)
        if name == "dump":
            return U1, None, "json.dump to an already-open handle"
        if name == "open":
            mode = _mode_of(call)
            if "w" in mode or "a" in mode:
                return U1, None, "open(mode=%r)" % mode
            return U3, None, "open(mode=%r)" % mode
        if name in ("_dump", "dump_json", "write_json"):
            return U1, None, "helper %s(...)" % name
    for node in hits:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    parent = ctx.parent.get(node)
                    if isinstance(parent, ast.Module):
                        return U2, target.id, "module-level constant joining a directory"
                    cls, detail = _first_use(ctx, target.id, node.lineno)
                    return cls, target.id, "function-local path; " + detail
    if hits:
        return U4, None, "literal present but not in a call or a plain assignment"
    return U4, None, "no node on this line mentions the fragment"


def _guards_before(ctx, fundef, node, name):
    """Existence gate in `fundef` before `node`.  Returns (gate_line, exit_code) or (None, None)."""
    if fundef is None:
        return None, None
    best = (None, None)
    for sub in ast.walk(fundef):
        if not isinstance(sub, ast.If):
            continue
        if sub.lineno >= node.lineno:
            continue
        test_src = ctx.src(sub.test)
        if "exists(" not in test_src:
            continue
        if name not in test_src:
            continue
        code = None
        for stmt in sub.body:
            if isinstance(stmt, ast.Return) and isinstance(stmt.value, ast.Constant) \
                    and isinstance(stmt.value.value, int):
                code = stmt.value.value
                break
        if code is None:
            body_src = " ".join(ctx.src(s) for s in sub.body)
            if "SystemExit" in body_src or "raise" in body_src:
                code = -1
            elif "return 0" in body_src:
                code = 0
        best = (sub.lineno, code)
    return best


def classify_consumer(ctx, node):
    """Classify one ast.Name Load of the constant."""
    fundef = ctx.enclosing_def(node)
    fname_def = getattr(fundef, "name", "") or ""
    for anc in ctx.ancestors(node):
        if isinstance(anc, ast.Call):
            name = _call_name(anc)
            fn_path = ctx.src(anc.func)
            if "exists" in fn_path or "isfile" in fn_path or "isdir" in fn_path:
                return C2, anc
            if name in ("dump",):
                return C1, anc
            if name == "open":
                mode = _mode_of(anc)
                if "w" in mode or "a" in mode:
                    return C1, anc
                return C4, anc  # tentative; graded by the guard check below
            if name in ("_dump", "dump_json", "write_json"):
                return C1, anc
            if name in ("glob", "listdir", "scandir", "iterdir", "iglob"):
                return C6, anc
            if "landed" in name or "already" in name:
                return C8, anc
            if name in ("print", "format"):
                return C3, anc
        if isinstance(anc, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Module)):
            break
    if "status" in fname_def.lower():
        return C3, None
    return C7, None


def consumers_of(ctx, name, def_line):
    rows = []
    for node in ast.walk(ctx.tree):
        if not isinstance(node, ast.Name):
            continue
        if node.id != name or not isinstance(node.ctx, ast.Load):
            continue
        if node.lineno == def_line:
            continue
        cls, call = classify_consumer(ctx, node)
        row = {"line": node.lineno, "class": cls}
        if cls == C4:
            fundef = ctx.enclosing_def(node)
            gate_line, code = _guards_before(ctx, fundef, node, name)
            if gate_line is None:
                row["class"] = C5
                row["failure_mode"] = M_RAISE
            else:
                row["failure_mode"] = M_LOUD if code not in (None, 0) else M_SILENT
                row["gate_line"] = gate_line
                row["gate_exit_code"] = code
            row["function"] = getattr(fundef, "name", None)
        elif cls == C1:
            row["failure_mode"] = M_NOTREAD
        elif cls == C2:
            row["failure_mode"] = M_LOUD
        elif cls == C3:
            row["failure_mode"] = M_SILENT
        elif cls == C6:
            row["failure_mode"] = M_SILENT
        elif cls == C8:
            row["failure_mode"] = M_UNGRADED
        else:
            row["failure_mode"] = M_UNGRADED
        if call is not None:
            row["call"] = _call_name(call)
            row["source"] = ctx.src(call)[:160]
        rows.append(row)
    rows.sort(key=lambda r: r["line"])
    return rows


def directory_enumerators(fragment):
    """Corpus-wide: who enumerates the parent directory of `fragment` instead of naming the file?"""
    hits = []
    skip_dirs = {".git", ".codely-cli", "__pycache__", "results", "data", "legacy", "Money02"}
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for fn in files:
            if not fn.endswith(".py"):
                continue
            rel = os.path.relpath(os.path.join(base, fn), ROOT).replace("\\", "/")
            if rel == SELF_REL or rel.startswith("scripts/_r14") or rel.startswith("_tmp"):
                continue
            try:
                text = _read(rel)
            except Exception:
                continue
            try:
                tree = ast.parse(text)
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and _call_name(node) in ("glob", "iglob"):
                    src = ast.get_source_segment(text, node) or ""
                    if "traders" in src or "listdir" in src:
                        hits.append({"site": "%s:%d" % (rel, node.lineno),
                                     "class": C6, "source": src.replace("\n", " ")[:160]})
                    break
    return hits


# --------------------------------------------------------------------------- study

def population():
    """Machine-read E404's published dead joins; nothing hand-copied."""
    path = os.path.join(ROOT, POPULATION_SOURCE)
    with open(path, encoding="utf-8") as fh:
        face = json.load(fh)
    rows = []
    for row in face["summary"]["dead_joins"]:
        site = row["site"]
        rel, _, line = site.rpartition(":")
        rows.append({"site": site, "source_file": rel, "line": int(line),
                     "fragment": row["fragment"], "composed_path": row["composed"]})
    return rows, face.get("summary", {}).get("in_tree_absent_reads")


def price(row):
    ctx = Ctx(row["source_file"])
    cls, name, detail = classify_site(ctx, row["line"], row["fragment"])
    target_exists = os.path.exists(os.path.join(ROOT, row["composed_path"].replace("/", os.sep)))
    out = {
        "site": row["site"],
        "fragment": row["fragment"],
        "composed_path": row["composed_path"],
        "target_exists_on_disk": target_exists,
        "use_class": cls,
        "use_detail": detail,
        "constant_name": name,
        "consumers": [],
        "directory_enumerators": [],
        "failure_mode": M_NOTREAD if cls in (U1, U2, U4) else None,
    }
    if cls == U2 and name:
        out["consumers"] = consumers_of(ctx, name, row["line"])
        modes = [c["failure_mode"] for c in out["consumers"]]
        if M_RAISE in modes:
            out["failure_mode"] = M_RAISE
        elif M_LOUD in modes:
            out["failure_mode"] = M_LOUD
        elif M_SILENT in modes:
            out["failure_mode"] = M_SILENT
        elif modes:
            out["failure_mode"] = M_UNGRADED
        # a writer inside the same file means the target is a pending output, not a broken path
        if C1 in [c["class"] for c in out["consumers"]]:
            out["produced_by"] = [c["line"] for c in out["consumers"] if c["class"] == C1]
            out["pending_output"] = True
    if cls == U1:
        out["directory_enumerators"] = directory_enumerators(row["fragment"])
        if out["directory_enumerators"]:
            out["failure_mode"] = M_SILENT
            out["pending_output"] = True
        else:
            out["failure_mode"] = M_PENDING
            out["pending_output"] = True
    return out


def decide(rows):
    uses = [r["use_class"] for r in rows]
    modes = [r["failure_mode"] for r in rows]
    reads = uses.count(U3)
    silent = modes.count(M_SILENT)
    raises = modes.count(M_RAISE)
    loud = modes.count(M_LOUD)
    if reads == 0:
        if silent and (raises or loud):
            return V_MIXED
        if silent:
            return V_SILENT
        if raises:
            return V_RAISES
        if loud:
            return V_LOUD
        return V_MISPREMISE
    if raises:
        return V_RAISES
    if silent:
        return V_SILENT
    if loud:
        return V_LOUD
    return V_MISPREMISE


def build():
    rows, published_count = population()
    priced = [price(row) for row in rows]
    verdict = decide(priced)
    by_use = {}
    by_mode = {}
    for row in priced:
        by_use[row["use_class"]] = by_use.get(row["use_class"], 0) + 1
        by_mode[row["failure_mode"]] = by_mode.get(row["failure_mode"], 0) + 1
    payload = {
        "study": STUDY,
        "evidence_cutoff": EV_CUTOFF,
        "generated": datetime.now().astimezone().isoformat(timespec="seconds"),
        "population_source": POPULATION_SOURCE,
        "population_note": ("the three sites E404 published as in_tree_absent_reads; this study "
                            "re-derives what each join line does and who consumes the path"),
        "published_absent_read_count": published_count,
        "summary": {
            "sites": len(priced),
            "by_use_class": by_use,
            "by_failure_mode": by_mode,
            "sites_that_are_reads_at_the_join_line": by_use.get(U3, 0),
            "sites_that_are_writes_at_the_join_line": by_use.get(U1, 0),
            "sites_that_are_module_constants_at_the_join_line": by_use.get(U2, 0),
            "sites_with_a_pending_output": sum(1 for r in priced if r.get("pending_output")),
        },
        "rows": priced,
        "bounds": {
            "no_rewrites": "no published face, pointer, constant or consumer is edited here",
            "static_only": ("failure modes are read from the AST and from os.path.exists on the "
                            "target; no consumer is executed"),
        },
        "verdict": verdict,
        "source": SELF_REL,
    }
    face = os.path.join(PUBLISHED_DIR, FACE)
    _dump(face, payload)
    _dump(os.path.join(PUBLISHED_DIR, LATEST), payload)
    say("published %s (%d sites, verdict=%s)" % (face, len(priced), verdict))
    for row in priced:
        say("  %s use=%s failure_mode=%s consumers=%d enum=%d"
            % (row["site"], row["use_class"], row["failure_mode"],
               len(row["consumers"]), len(row["directory_enumerators"])))
    return payload


def verify():
    problems = []
    face = os.path.join(PUBLISHED_DIR, FACE)
    if not os.path.exists(face):
        return ["face missing: %s" % FACE]
    with open(face, encoding="utf-8") as fh:
        payload = json.load(fh)
    if payload.get("evidence_cutoff") != EV_CUTOFF:
        problems.append("evidence_cutoff mismatch")
    rows = payload.get("rows") or []
    if len(rows) != 3:
        problems.append("expected 3 priced sites, got %d" % len(rows))
    for row in rows:
        if row["use_class"] not in USE_CLASSES:
            problems.append("%s: unknown use class %s" % (row["site"], row["use_class"]))
        if row["failure_mode"] not in FAILURE_MODES:
            problems.append("%s: unknown failure mode %s" % (row["site"], row["failure_mode"]))
        for c in row["consumers"]:
            if c["class"] not in CONSUMER_CLASSES:
                problems.append("%s: unknown consumer class line %s" % (row["site"], c["line"]))
        if row["use_class"] == U2 and not row["consumers"]:
            problems.append("%s: constant with no consumer rows" % row["site"])
    if payload.get("verdict") != decide(rows):
        problems.append("verdict does not re-derive from rows")
    # the live tree must still agree with what was published
    for row in rows:
        live_use, _, _ = classify_site(Ctx(row["site"].rpartition(":")[0]),
                                       int(row["site"].rpartition(":")[2]),
                                       row["fragment"])
        if live_use != row["use_class"]:
            problems.append("%s: live use class %s != published %s"
                            % (row["site"], live_use, row["use_class"]))
    return problems


# --------------------------------------------------------------------------- selftest

WRITE_FIX = """import json, os
ROOT = os.path.dirname(os.path.abspath(__file__))
def register():
    path = os.path.join(ROOT, "firm", "traders", "NEW-001.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"id": "NEW-001"}, fh)
"""

CONST_FIX = """import json, os
RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
SCREEN_FILE = os.path.join(RES, "w99_screen.json")
def cmd_screen():
    prod = {"n": 1}
    _dump(SCREEN_FILE, prod)
def cmd_judge():
    if not os.path.exists(SCREEN_FILE):
        print("GATE: absent")
        return 2
    screen = json.load(open(SCREEN_FILE, encoding="utf-8"))
    return 0
def cmd_loose():
    screen = json.load(open(SCREEN_FILE, encoding="utf-8"))
    return 0
def cmd_status():
    print(SCREEN_FILE)
"""


def _line_of(ctx, fragment):
    """The line where a literal equal to `fragment` appears."""
    lines = [n.lineno for n in ast.walk(ctx.tree)
             if isinstance(n, ast.Constant) and n.value == fragment]
    return min(lines) if lines else -1


def selftest():
    results = []

    def leg(name, good, detail=""):
        results.append((name, bool(good), detail))

    ctxw = Ctx("fixture_write.py", WRITE_FIX)
    cls, name, _ = classify_site(ctxw, _line_of(ctxw, "NEW-001.json"), "NEW-001.json")
    leg("a path assigned then opened for writing is a write, not a read (U1)", cls == U1, cls)
    leg("a function-local path is not published as a constant", name is None or name == "path", name)

    ctxc = Ctx("fixture_const.py", CONST_FIX)
    cls, name, _ = classify_site(ctxc, _line_of(ctxc, "w99_screen.json"), "w99_screen.json")
    leg("a module-level join is a constant, not a read (U2)", cls == U2, cls)
    leg("the constant name is recovered from the assignment", name == "SCREEN_FILE", name)

    const_line = _line_of(ctxc, "w99_screen.json")
    rows = consumers_of(ctxc, "SCREEN_FILE", const_line)
    classes = [r["class"] for r in rows]
    leg("a writer consumer is classified C1", C1 in classes, classes)
    leg("an existence test is classified C2, not a read", C2 in classes, classes)
    leg("a checklist print is classified C3", C3 in classes, classes)
    leg("a gated read is C4 and a bare read is C5", C4 in classes and C5 in classes, classes)
    leg("a reference this arm cannot grade is not charged as a failure",
        all(r["failure_mode"] != M_SILENT for r in rows if r["class"] == C7),
        [r["failure_mode"] for r in rows if r["class"] == C7])

    gated = [r for r in rows if r["class"] == C4]
    bare = [r for r in rows if r["class"] == C5]
    leg("the gated read reports a loud non-zero refusal",
        gated and gated[0]["failure_mode"] == M_LOUD and gated[0]["gate_exit_code"] == 2,
        gated[0] if gated else None)
    leg("the bare read reports FileNotFoundError",
        bare and bare[0]["failure_mode"] == M_RAISE, bare[0] if bare else None)
    leg("a write consumer is not a read at all", any(r["failure_mode"] == M_NOTREAD for r in rows))

    leg("decide: no read at the join line and only loud modes -> loud",
        decide([{"use_class": U1, "failure_mode": M_PENDING},
                {"use_class": U2, "failure_mode": M_LOUD}]) == V_LOUD)
    leg("decide: a silent enumeration outranks a loud reader",
        decide([{"use_class": U1, "failure_mode": M_SILENT},
                {"use_class": U2, "failure_mode": M_LOUD}]) == V_MIXED)
    leg("decide: only silent modes -> silent",
        decide([{"use_class": U1, "failure_mode": M_SILENT}]) == V_SILENT)
    leg("decide: an ungated read outranks everything",
        decide([{"use_class": U3, "failure_mode": M_RAISE},
                {"use_class": U1, "failure_mode": M_SILENT}]) == V_RAISES)
    leg("class sets are closed",
        set(USE_CLASSES) == {U1, U2, U3, U4} and
        set(CONSUMER_CLASSES) == {C1, C2, C3, C4, C5, C6, C7, C8} and
        set(FAILURE_MODES) == {M_LOUD, M_RAISE, M_SILENT, M_PENDING, M_NOTREAD, M_UNGRADED})

    ok = all(r[1] for r in results)
    for name, good, detail in results:
        say("%s %s%s" % ("PASS" if good else "FAIL", name, (" (%s)" % detail) if detail else ""))
    say("%d/%d" % (sum(1 for r in results if r[1]), len(results)))
    return 0 if ok else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        build()
        return 0
    if cmd == "verify":
        problems = verify()
        if problems:
            for problem in problems:
                say("PROBLEM %s" % problem)
            return 1
        say("verify: problems=[]")
        return 0
    if cmd == "selftest":
        return selftest()
    say("usage: run | verify | selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))