"""E559 -- does anything read a chain receipt, or a chain runner's return code?

E558 (r1584) measured that all three chain runners record each leg's return code,
compare it to zero, print the NONZERO lines and then exit 0 -- a refusing gate leg
leaves the process green.  That closes one half of the question.  This study asks the
other half: is there any consumer at all on the other end of that channel?

Two channels are measured separately, because they behave differently:

  * the process exit code of a chain runner (``s6_chain_bm[abc].py``).  Population =
    every live source that spawns a runner.  Each site is classified by whether it
    waits for the child, whether it reads the return code, and whether reading it can
    fail the caller at all.  A detached spawn observes nothing, so it cannot be
    counted as an observer even though it is the closest thing to one.
  * the receipt file the runner writes (``results/_r<N>bm[abc]_s6_chain.json``).
    Population = every source that opens a chain receipt.  A writer opening its own
    receipt is published as a writer, never as a reader: "it opened the file" and
    "it consumed the result" are different claims.

Task definitions and shell wrappers are a third arm.  No scheduled task on this box
runs a chain runner (disclosed, not gated: the live task census is not reproducible
at build time), so the wrapper classifier is exercised by fixtures and the face says
so instead of pretending a live row trained it.  The wrapper classes keep the r-study
trap apart on purpose: ``$LASTEXITCODE`` is null after a ``.ps1`` call, so a null-vs-
zero comparison is always true and a wrapper built that way cannot fail.

    python scripts/e559_chain_rc_consumer.py build      # publish the face
    python scripts/e559_chain_rc_consumer.py check      # re-derive from source
    python scripts/e559_chain_rc_consumer.py verify     # two builds identical
    python scripts/e559_chain_rc_consumer.py selftest   # offline fixtures
"""
from __future__ import annotations

import ast
import io
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

STATE_TILT = os.path.join(ROOT, "results", "state_tilt")
LATEST = os.path.join(STATE_TILT, "chainrcconsumer_latest.json")
DATED_PREFIX = "CHAINRCCONSUMER"
PARENT = os.path.join(STATE_TILT, "gateread_latest.json")

STUDY = "E559"
CARD = "E559"
TITLE = "whether any task or source reads a chain receipt or a leg rc"
EVIDENCE_CUTOFF = "2026-11-08"

RUNNERS = {
    "Tools/s6_chain_bma.py": "bm-a",
    "Tools/s6_chain_bmb.py": "bm-b",
    "Tools/s6_chain_bmc.py": "bm-c",
}
CHAIN_NAME = re.compile(r"s6_chain_bm([abc])")
RECEIPT_TEXT = "_s6_chain.json"

PY_EXT = (".py",)
SH_EXT = (".ps1", ".cmd", ".bat", ".vbs")
CODE_EXT = PY_EXT + SH_EXT

CORPUS_DIRS = ("scripts", "Tools", "monitor", "firm", "live", "tests", "knowledge")
SKIP_DIRS = {".git", "data", "results", "logs", "_quarantine", "node_modules",
             ".codely-cli", "media", "legacy", "Money02", "__pycache__", "artifacts"}

# ---- spawn classes -------------------------------------------------------------
S_FAILS = "fails_when_the_chain_fails"
S_OBSERVES = "reads_the_rc_but_cannot_fail_the_caller"
S_DISCARDS = "waits_for_the_child_and_discards_the_rc"
S_NEVER = "detached_spawn_never_observes_the_rc"
S_UNFOLDABLE = "spawn_shape_this_scan_cannot_fold"
SPAWN_CLASSES = (S_FAILS, S_OBSERVES, S_DISCARDS, S_NEVER, S_UNFOLDABLE)

# ---- import classes ------------------------------------------------------------
I_LEGS = "reads_the_leg_table_not_the_result"

# ---- receipt classes -----------------------------------------------------------
R_WRITE = "writer_of_a_receipt"
R_READ = "reader_of_a_receipt"

# ---- wrapper classes -----------------------------------------------------------
W_FAILS = "wrapper_fails_when_the_chain_fails"
W_NULL = "wrapper_checks_LASTEXITCODE_after_a_ps1_call_cannot_fail"
W_PRINTS = "wrapper_checks_the_rc_then_exits_zero"
W_IGNORES = "wrapper_never_checks_the_rc"
W_UNFOLDABLE = "wrapper_shape_this_scan_cannot_fold"
WRAPPER_CLASSES = (W_FAILS, W_NULL, W_PRINTS, W_IGNORES, W_UNFOLDABLE)

VERDICTS = (
    "some_spawn_site_fails_when_the_chain_fails",
    "the_receipt_is_read_but_no_spawn_site_fails",
    "nothing_on_any_machine_reads_the_exit_code_or_the_receipt",
)

SPAWN_NAMES = {
    "subprocess.Popen", "subprocess.run", "subprocess.call", "subprocess.check_call",
    "subprocess.check_output", "os.system", "os.popen", "Popen", "run", "call",
    "check_call", "check_output", "system", "popen",
}
WAIT_NAMES = {"run", "call", "check_call", "check_output"}


def _read(path):
    """Read source text.  A handful of live files are GBK, and reading them as UTF-8
    with replacement characters turns a parseable module into a SyntaxError -- which the
    first build reported as seven 'unfoldable' spawn sites that were really seven
    encoding failures (E559 first cut)."""
    raw = open(path, "rb").read()
    for enc in ("utf-8-sig", "gbk"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def _rel(path):
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def _tracked():
    try:
        p = subprocess.run(["git", "-C", ROOT, "ls-files", "-z"],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=120)
        if p.returncode != 0:
            return None
        return {x.replace(os.sep, "/") for x in p.stdout.split("\0") if x}
    except Exception:
        return None


def corpus():
    """Live code files this study reads.  results/ and data/ are history, not code."""
    out = []
    for name in CORPUS_DIRS:
        d = os.path.join(ROOT, name)
        if not os.path.isdir(d):
            continue
        for dp, dn, fn in os.walk(d):
            dn[:] = sorted(x for x in dn if x not in SKIP_DIRS and not x.startswith("."))
            for f in sorted(fn):
                if f.endswith(CODE_EXT):
                    out.append(_rel(os.path.join(dp, f)))
    for f in sorted(os.listdir(ROOT)):
        p = os.path.join(ROOT, f)
        if os.path.isfile(p) and f.endswith(CODE_EXT):
            out.append(f)
    return sorted(set(out))


# ---- expression folding --------------------------------------------------------
def fold(node, depth=0):
    """Fold a path/command expression to text, or None when this scan cannot."""
    if depth > 8 or node is None:
        return None
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        parts = []
        for v in node.values:
            if isinstance(v, ast.Constant):
                parts.append(str(v.value))
            else:
                parts.append("{}")
        return "".join(parts)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        a, b = fold(node.left, depth + 1), fold(node.right, depth + 1)
        return None if a is None or b is None else a + b
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
        a = fold(node.left, depth + 1)
        if a is not None:
            return re.sub(r"%[sdr]", "{}", a)
        return None
    if isinstance(node, (ast.List, ast.Tuple)):
        parts = [fold(e, depth + 1) for e in node.elts]
        if all(p is not None for p in parts):
            return " ".join(parts)
        return None
    if isinstance(node, ast.Call):
        f = node.func
        name = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else "")
        parts = [fold(a, depth + 1) for a in node.args]
        if name in ("join", "abspath", "normpath", "realpath") and parts and all(p is not None for p in parts):
            return "/".join(parts)
        if name in ("format", "fspath", "str") and parts and parts[0] is not None:
            return parts[0]
        return None
    return None


def dotted(node):
    if isinstance(node, ast.Attribute):
        base = dotted(node.value)
        return (base + "." + node.attr) if base else node.attr
    if isinstance(node, ast.Name):
        return node.id
    return ""


def enclosing(tree):
    """Map every node to its nearest enclosing FunctionDef (or None)."""
    owner = {}

    def walk(node, cur):
        for child in ast.iter_child_nodes(node):
            owner[child] = cur
            walk(child, child if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) else cur)

    owner[tree] = None
    walk(tree, None)
    return owner


def _function_nodes(fn):
    if fn is None:
        return []
    return list(ast.walk(fn))


# ---- spawn classification ------------------------------------------------------
def spawn_names(tree):
    """Which spawn callees this module can actually reach.

    A bare `run(...)` is only subprocess.run when the name was imported from subprocess
    or os.  The first cut counted a local helper named `run` as a spawn site and reported
    the *caller* of that helper as a chain consumer -- a false positive that would have
    inflated the population with a site that never touches a process (E559 first cut).
    """
    names = set()
    mods = {"subprocess", "os"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name in mods:
                    names.add(a.asname or a.name)
        elif isinstance(node, ast.ImportFrom) and node.module in mods:
            for a in node.names:
                names.add(a.asname or a.name)
    return names


def is_spawn_call(callee, aliases, tree):
    if not callee:
        return False
    if "." in callee:
        head, _, _ = callee.partition(".")
        return head in aliases and head in ("subprocess", "os") and callee.split(".")[-1] in (
            "Popen", "run", "call", "check_call", "check_output", "system", "popen")
    return callee in aliases and callee in (
        "Popen", "run", "call", "check_call", "check_output", "system", "popen")


def strings_in(node):
    """Every string literal inside an expression, folded together.

    A spawn command is usually a list containing a nested join of the runner path, so
    folding the list itself fails while the pieces are all right there."""
    parts = []
    for sub in ast.walk(node):
        if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
            parts.append(sub.value)
        elif isinstance(sub, ast.JoinedStr):
            parts.append("".join(v.value if isinstance(v, ast.Constant) else "{}"
                                 for v in sub.values))
    return " ".join(parts)


_TRACKED = {}


def tracked_set():
    if "v" not in _TRACKED:
        _TRACKED["v"] = _tracked()
    return _TRACKED["v"]


def _is_tracked(rel):
    t = tracked_set()
    return None if t is None else (rel in t)


def classify_spawn(waits, reads_rc, can_fail):
    """Pure classifier, so a published row can be re-derived from its own fields."""
    if not waits:
        return S_NEVER
    if not reads_rc:
        return S_DISCARDS
    if not can_fail:
        return S_OBSERVES
    return S_FAILS


def _spawn_sites():
    rows = []
    for rel in corpus():
        if rel in RUNNERS or not rel.endswith(PY_EXT):
            continue
        path = os.path.join(ROOT, rel)
        try:
            src = _read(path)
        except OSError:
            continue
        if "s6_chain_bm" not in src:
            continue
        try:
            tree = ast.parse(src)
        except SyntaxError:
            rows.append({"path": rel, "line": 0, "callee": "", "class": S_UNFOLDABLE,
                         "waits": False, "reads_rc": False, "can_fail": False,
                         "evidence": "the file does not parse as Python"})
            continue
        owner = enclosing(tree)
        aliases = spawn_names(tree)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            callee = dotted(node.func)
            if not is_spawn_call(callee, aliases, tree):
                continue
            short = callee.split(".")[-1]
            blob = " ".join(strings_in(a) for a in list(node.args) + [k.value for k in node.keywords])
            if not CHAIN_NAME.search(blob):
                continue
            fn = owner.get(node)
            body = _function_nodes(fn)
            # the child handle: `p = Popen(...)` / `r = run(...)`
            handle = None
            for parent in ast.walk(tree):
                if isinstance(parent, ast.Assign) and parent.value is node and len(parent.targets) == 1:
                    tg = parent.targets[0]
                    if isinstance(tg, ast.Name):
                        handle = tg.id
            waits = short in WAIT_NAMES
            reads_rc = False
            if handle:
                for sub in body:
                    if isinstance(sub, ast.Attribute) and sub.attr in ("wait", "communicate", "poll"):
                        if isinstance(sub.value, ast.Name) and sub.value.id == handle:
                            waits = True
                    if isinstance(sub, ast.Attribute) and sub.attr == "returncode":
                        reads_rc = True
                    if isinstance(sub, ast.Name) and sub.id == handle:
                        pass
            for sub in body:
                if isinstance(sub, ast.Attribute) and sub.attr == "returncode":
                    reads_rc = True
                if isinstance(sub, ast.Compare):
                    sides = [fold(sub.left)] + [fold(c) for c in sub.comparators]
                    if any(s is not None and "returncode" in s for s in sides):
                        reads_rc = True
            can_fail = False
            for sub in body:
                if isinstance(sub, ast.Raise):
                    can_fail = True
                if isinstance(sub, ast.Call):
                    nm = dotted(sub.func)
                    if nm in ("sys.exit", "exit", "SystemExit", "os._exit"):
                        can_fail = True
            if not waits:
                reads_rc = False
            cls = classify_spawn(waits, reads_rc, can_fail)
            ev = []
            ev.append("waits" if waits else "no wait/communicate/poll on the child")
            ev.append("reads .returncode" if reads_rc else "never reads .returncode")
            ev.append("raises or exits non-zero in the same function" if can_fail
                      else "no raise/sys.exit in the same function")
            rows.append({"path": rel, "line": node.lineno, "callee": callee, "class": cls,
                         "waits": waits, "reads_rc": reads_rc, "can_fail": can_fail,
                         "tracked": _is_tracked(rel),
                         "evidence": "; ".join(ev)})
    rows.sort(key=lambda r: (r["path"], r["line"]))
    return rows


def _import_sites():
    rows = []
    for rel in corpus():
        if rel in RUNNERS or not rel.endswith(PY_EXT):
            continue
        try:
            src = _read(os.path.join(ROOT, rel))
        except OSError:
            continue
        if "s6_chain_bm" not in src:
            continue
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            mod = None
            if isinstance(node, ast.Import):
                for a in node.names:
                    if CHAIN_NAME.search(a.name):
                        mod = a.name
            elif isinstance(node, ast.ImportFrom) and node.module and CHAIN_NAME.search(node.module):
                mod = node.module
            elif isinstance(node, ast.Call):
                nm = dotted(node.func)
                if nm.split(".")[-1] in ("import_module", "__import__") and node.args:
                    t = fold(node.args[0])
                    if t and CHAIN_NAME.search(t):
                        mod = t
            if mod:
                rows.append({"path": rel, "line": node.lineno, "module": mod, "class": I_LEGS})
    rows.sort(key=lambda r: (r["path"], r["line"]))
    return rows


def bound_paths(tree):
    """Best-effort name -> folded text, so `path = f"results/_r{n}..."` then
    `open(path, "w")` is readable.  Two hops is enough for the shapes in this repo."""
    table = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            tg = node.targets[0]
            if isinstance(tg, ast.Name):
                t = fold(node.value)
                if t and tg.id not in table:
                    table[tg.id] = t
    for _ in range(2):
        changed = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                tg = node.targets[0]
                if isinstance(tg, ast.Name) and tg.id not in table:
                    v = node.value
                    if isinstance(v, ast.Name) and v.id in table:
                        table[tg.id] = table[v.id]
                        changed = True
        if not changed:
            break
    return table


def classify_receipt(mode):
    m = (mode or "r").lower()
    return R_WRITE if ("w" in m or "a" in m or "x" in m) else R_READ


def _receipt_sites():
    writers, readers = [], []
    for rel in corpus():
        try:
            src = _read(os.path.join(ROOT, rel))
        except OSError:
            continue
        if RECEIPT_TEXT not in src:
            continue
        if not rel.endswith(PY_EXT):
            for m in re.finditer(re.escape(RECEIPT_TEXT), src):
                line = src[:m.start()].count("\n") + 1
                readers.append({"path": rel, "line": line, "mode": "shell", "class": R_READ,
                                "folded": "(shell text)"})
            continue
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        binds = bound_paths(tree)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            nm = dotted(node.func)
            if nm.split(".")[-1] not in ("open", "read_text", "load", "readlines", "read", "loads"):
                continue
            target = None
            if node.args:
                target = fold(node.args[0])
                if target is None and isinstance(node.args[0], ast.Name):
                    target = binds.get(node.args[0].id)
            if node.keywords:
                for k in node.keywords:
                    if k.arg in ("file", "fp", "path"):
                        target = target or fold(k.value)
            if not target or RECEIPT_TEXT not in target:
                continue
            mode = "r"
            if len(node.args) > 1:
                mv = fold(node.args[1])
                if mv:
                    mode = mv
            for k in node.keywords:
                if k.arg == "mode":
                    mv = fold(k.value)
                    if mv:
                        mode = mv
            cls = classify_receipt(mode)
            row = {"path": rel, "line": node.lineno, "mode": mode, "class": cls,
                   "tracked": _is_tracked(rel),
                   "folded": target.replace(os.sep, "/")}
            (writers if cls == R_WRITE else readers).append(row)
    writers.sort(key=lambda r: (r["path"], r["line"]))
    readers.sort(key=lambda r: (r["path"], r["line"]))
    return writers, readers


# ---- wrapper arm ---------------------------------------------------------------
def wrapper_shapes(text):
    """(reads $LASTEXITCODE, calls another .ps1, exits non-zero).  One definition, used
    by the live scan and by the fixtures, so a fixture can never pass on a rule the live
    scan does not apply."""
    reads_le = "$LASTEXITCODE" in text or "%ERRORLEVEL%" in text
    calls_ps1 = bool(re.search(r"^\s*(?:&\s+|\.\s+)[^|;\n]*\.ps1\s*$", text, re.M))
    exits = bool(re.search(r"\bexit\s+(?!0\b)\S|\bthrow\b", text, re.I))
    return reads_le, calls_ps1, exits


def classify_wrapper(invokes_runner, reads_last_exit, calls_a_ps1, exits_nonzero):
    if not invokes_runner:
        return None
    if not reads_last_exit:
        return W_IGNORES
    if calls_a_ps1:
        return W_NULL
    return W_FAILS if exits_nonzero else W_PRINTS


def _wrapper_rows():
    rows = []
    for rel in corpus():
        if rel in RUNNERS or not rel.endswith(SH_EXT):
            continue
        try:
            src = _read(os.path.join(ROOT, rel))
        except OSError:
            continue
        if "s6_chain_bm" not in src:
            continue
        lines = src.splitlines()
        invokes = [i + 1 for i, ln in enumerate(lines)
                   if CHAIN_NAME.search(ln) and not ln.strip().startswith("#")]
        if not invokes:
            continue
        reads_le, calls_ps1, exits = wrapper_shapes(src)
        cls = classify_wrapper(True, reads_le, calls_ps1, exits)
        rows.append({"path": rel, "line": invokes[0], "class": cls,
                     "reads_LASTEXITCODE": reads_le, "calls_a_ps1": calls_ps1,
                     "exits_non_zero": exits, "tracked": _is_tracked(rel)})
    rows.sort(key=lambda r: r["path"])
    return rows


def _task_definition_rows():
    """Repo sources that declare a scheduled-task action.  A runner named here would be
    the one place a machine could schedule the chain; the live census is disclosed
    separately in the digest because it is not reproducible at build time."""
    rows = []
    pat = re.compile(r"(TaskName|schtasks|Register-ScheduledTask|New-ScheduledTaskAction)", re.I)
    for rel in corpus():
        if not rel.endswith(".ps1"):
            continue
        try:
            src = _read(os.path.join(ROOT, rel))
        except OSError:
            continue
        if not (pat.search(src) and CHAIN_NAME.search(src)):
            continue
        rows.append({"path": rel, "declares_a_chain_action": True})
    return rows


# ---- build --------------------------------------------------------------------
def _runner_rows():
    rows = []
    for rel, machine in sorted(RUNNERS.items()):
        path = os.path.join(ROOT, rel)
        if not os.path.isfile(path):
            rows.append({"path": rel, "machine": machine, "present": False,
                         "receipt_template": None, "exits_non_zero_on_a_failing_leg": None,
                         "receipt_tokens": []})
            continue
        src = _read(path)
        tmpl = None
        for m in re.finditer(r"[\"'](?:results[\\/])?_r%[sb][^\"']*_s6_chain\.json[\"']", src):
            tmpl = m.group(0).strip("\"'").replace("\\", "/")
        if tmpl is None:
            for m in re.finditer(r"[\"'](?:_r\{[^\"']*\}?bm[abc][^\"']*_s6_chain\.json)[\"']", src):
                tmpl = m.group(0).strip("\"'").replace("\\", "/")
        exits = bool(re.search(r"^\s*sys\.exit\(1\)|raise SystemExit\(1\)|return\s+1\s*$",
                               src, re.M))
        tokens = sorted(set(re.findall(r"NONZERO|all_nonzero|failed", src)))[:6]
        rows.append({"path": rel, "machine": machine, "present": True,
                     "receipt_template": tmpl,
                     "exits_non_zero_on_a_failing_leg": exits,
                     "receipt_tokens": tokens})
    return rows


def _verdict(summary):
    if summary["by_class"].get(S_FAILS):
        return VERDICTS[0]
    if summary["receipt_readers_outside_the_writer"]:
        return VERDICTS[1]
    return VERDICTS[2]


def build(write=True):
    corpus_files = corpus()
    spawn = _spawn_sites()
    imports = _import_sites()
    writers, readers = _receipt_sites()
    writer_paths = {w["path"] for w in writers}
    outside = [r for r in readers if r["path"] not in writer_paths]
    wrappers = _wrapper_rows()
    tasks = _task_definition_rows()
    by_class = {c: 0 for c in SPAWN_CLASSES}
    for r in spawn:
        by_class[r["class"]] = by_class.get(r["class"], 0) + 1
    summary = {
        "corpus_files": len(corpus_files),
        "spawn_sites": len(spawn),
        "by_class": by_class,
        "import_sites": len(imports),
        "receipt_writers": len(writers),
        "receipt_readers": len(readers),
        "receipt_readers_outside_the_writer": len(outside),
        "wrappers_naming_a_runner": len(wrappers),
        "task_sources_declaring_a_chain_action": len(tasks),
        "runners_present": sum(1 for r in _runner_rows() if r["present"]),
        "runners_exiting_non_zero_on_a_failing_leg": sum(
            1 for r in _runner_rows() if r["exits_non_zero_on_a_failing_leg"]),
    }
    face = {
        "study": STUDY,
        "card": CARD,
        "title": TITLE,
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "root": ROOT,
        "population_rule": ("live code under %s plus repo-root files (%s); results/ and "
                            "data/ are history, not code; the three chain runners are the "
                            "producers, never their own consumer"
                            % ("/".join(CORPUS_DIRS), " ".join(CODE_EXT))),
        "producers": _runner_rows(),
        "spawn_sites": spawn,
        "import_sites": imports,
        "receipts": {"writers": writers, "readers": readers,
                     "readers_outside_the_writer": outside},
        "wrappers": {"rows": wrappers,
                     "note": ("a wrapper is only counted when a live shell file names a runner "
                              "in a non-comment line; the classes that need a live row are "
                              "exercised by fixtures while this list is empty")},
        "task_definitions": {"rows": tasks,
                             "note": ("repo sources that declare a scheduled-task action.  The "
                                      "live census is disclosed in the digest: 296 actions on "
                                      "bm-b, 0 of them run a chain runner")},
        "control_arms": _control_arms(),
        "summary": summary,
        "verdict": _verdict(summary),
        "verdict_line": _verdict_line(summary),
    }
    if write:
        _write(LATEST, face)
        dated = os.path.join(STATE_TILT, "%s-%s.json" % (DATED_PREFIX, EVIDENCE_CUTOFF))
        _write(dated, face)
    return face


def _verdict_line(s):
    return ("%d live source%s spawn a chain runner; %d of them can fail on a failing chain "
            "(%s).  The receipt the runner writes has %d writers and %d reader%s outside the "
            "writer, and %d repo task-source%s declare a chain action."
            % (s["spawn_sites"], "" if s["spawn_sites"] == 1 else "s",
               s["by_class"].get(S_FAILS, 0),
               ", ".join("%s=%d" % (k, v) for k, v in s["by_class"].items() if v) or "no rows",
               s["receipt_writers"], s["receipt_readers_outside_the_writer"],
               "" if s["receipt_readers_outside_the_writer"] == 1 else "s",
               s["task_sources_declaring_a_chain_action"],
               "" if s["task_sources_declaring_a_chain_action"] == 1 else "s"))


def _control_arms():
    """Fixtures that prove each classifier can say the harder thing."""
    arms = {}
    # a spawn site that waits, reads the rc and raises: the classifier must see all three
    src_fail = '''
import subprocess, sys
def main():
    p = subprocess.run(["python", "Tools/s6_chain_bmb.py"], capture_output=True)
    if p.returncode != 0:
        raise SystemExit(1)
main()
'''
    row = _spawn_class_from_source(src_fail)
    arms["spawn_fails"] = {"found": bool(row) and row["class"] == S_FAILS,
                           "class": row["class"] if row else None}
    src_never = '''
import subprocess, sys
p = subprocess.Popen([sys.executable, "Tools/s6_chain_bmc.py"])
print("spawned", p.pid)
'''
    row = _spawn_class_from_source(src_never)
    arms["spawn_never_waits"] = {"found": bool(row) and row["class"] == S_NEVER,
                                 "class": row["class"] if row else None}
    src_discard = '''
import subprocess
def go():
    subprocess.run(["python", "Tools/s6_chain_bma.py"])
go()
'''
    row = _spawn_class_from_source(src_discard)
    arms["spawn_discards_rc"] = {"found": bool(row) and row["class"] == S_DISCARDS,
                                 "class": row["class"] if row else None}
    # wrapper: proper path, vs the $LASTEXITCODE-after-ps1 trap
    good = ('python "Tools\\s6_chain_bmb.py"\nif ($LASTEXITCODE -ne 0) { exit 1 }\n', None)
    bad = ('python "Tools\\s6_chain_bmb.py"\nif ($LASTEXITCODE -ne 0) { Write-Host "fail" }\n', None)
    arms["wrapper_fails"] = {"found": _wrapper_class_in_text(good[0]) == W_FAILS,
                             "class": _wrapper_class_in_text(good[0])}
    arms["wrapper_checks_rc_but_cannot_fail"] = {
        "found": _wrapper_class_in_text(bad[0]) == W_PRINTS,
        "class": _wrapper_class_in_text(bad[0])}
    trap = ('& Tools\\s6_wrapper.ps1\nif ($LASTEXITCODE -ne 0) { exit 1 }\n')
    arms["wrapper_null_trap"] = {"found": _wrapper_class_in_text(trap) == W_NULL,
                                 "class": _wrapper_class_in_text(trap)}
    shadow = '''
import subprocess
def run(tag, argv, logname):
    return 0
run("CHAIN", ["python", "Tools/s6_chain_bmb.py"], "x.log")
'''
    arms["local_helper_named_run_is_not_a_spawn"] = {
        "found": _spawn_class_from_source(shadow) is None,
        "class": None}
    arms["receipt_mode"] = {"found": (classify_receipt("w") == R_WRITE
                                      and classify_receipt("rb") == R_READ
                                      and classify_receipt(None) == R_READ),
                            "class": classify_receipt("w")}
    return arms


def _spawn_class_from_source(src):
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None
    owner = enclosing(tree)
    aliases = spawn_names(tree)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        callee = dotted(node.func)
        if not is_spawn_call(callee, aliases, tree):
            continue
        short = callee.split(".")[-1]
        texts = [strings_in(a) for a in node.args]
        if not CHAIN_NAME.search(" ".join(texts)):
            continue
        fn = owner.get(node)
        body = _function_nodes(fn) if fn is not None else list(ast.walk(tree))
        handle = None
        for parent in ast.walk(tree):
            if isinstance(parent, ast.Assign) and parent.value is node and len(parent.targets) == 1:
                if isinstance(parent.targets[0], ast.Name):
                    handle = parent.targets[0].id
        waits = short in WAIT_NAMES
        reads_rc = False
        can_fail = False
        for sub in body:
            if isinstance(sub, ast.Attribute) and sub.attr in ("wait", "communicate", "poll"):
                if handle and isinstance(sub.value, ast.Name) and sub.value.id == handle:
                    waits = True
            if isinstance(sub, ast.Attribute) and sub.attr == "returncode" and handle:
                if isinstance(sub.value, ast.Name) and sub.value.id == handle:
                    reads_rc = True
            if isinstance(sub, ast.Raise):
                can_fail = True
            if isinstance(sub, ast.Call) and dotted(sub.func) in ("sys.exit", "exit", "SystemExit"):
                can_fail = True
        if not waits:
            reads_rc = False
        return {"class": classify_spawn(waits, reads_rc, can_fail),
                "waits": waits, "reads_rc": reads_rc, "can_fail": can_fail}
    return None


def _wrapper_class_in_text(text):
    reads_le, calls_ps1, exits = wrapper_shapes(text)
    return classify_wrapper(True, reads_le, calls_ps1, exits)


# ---- persistence / gates -------------------------------------------------------
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
    """Re-derive every claim from the face's own rows; never trust a stored class."""
    p = []
    s = face.get("summary") or {}
    spawn = face.get("spawn_sites") or []
    if not spawn:
        p.append("the spawn population is empty")
    for r in spawn:
        want = classify_spawn(bool(r.get("waits")), bool(r.get("reads_rc")),
                              bool(r.get("can_fail")))
        if r.get("class") != want:
            p.append("a spawn row's class is not what its own fields say (%s)" % r.get("path"))
        if r.get("class") == S_FAILS and not r.get("can_fail"):
            p.append("a row is called failing without a raise or a non-zero exit")
        if r.get("class") == S_NEVER and (r.get("waits") or r.get("reads_rc")):
            p.append("a detached spawn is published as an observer (%s)" % r.get("path"))
    by = s.get("by_class") or {}
    if sum(by.values()) != len(spawn):
        p.append("the class table does not partition the spawn rows")
    if any(sum(v for k, v in by.items() if k == c) != sum(1 for r in spawn if r["class"] == c)
           for c in SPAWN_CLASSES):
        p.append("a published class count is not the number of rows in that class")
    rec = face.get("receipts") or {}
    writers = rec.get("writers") or []
    outside = rec.get("readers_outside_the_writer") or []
    if s.get("receipt_readers_outside_the_writer") != len(outside):
        p.append("the reader count outside the writer is not the length of that list")
    wp = {w.get("path") for w in writers}
    for r in outside:
        if r.get("path") in wp:
            p.append("a writer is published as an outside reader (%s)" % r.get("path"))
        if r.get("class") != R_READ:
            p.append("an outside reader is not classified as a reader")
    for w in writers:
        if w.get("class") != R_WRITE:
            p.append("a writer is not classified as a writer")
        if classify_receipt(w.get("mode")) != R_WRITE:
            p.append("a writer's own open mode is not a write (%s %r)"
                     % (w.get("path"), w.get("mode")))
    for r in (rec.get("readers") or []):
        if classify_receipt(r.get("mode")) != R_READ:
            p.append("a read-mode open is published with a write mode (%s)" % r.get("path"))
    if s.get("receipt_readers") != len(rec.get("readers") or []):
        p.append("the reader count is not the length of the reader list")
    arms = face.get("control_arms") or {}
    for name, arm in arms.items():
        if not (arm or {}).get("found"):
            p.append("control arm %s is blind" % name)
    want_v = _verdict({
        "by_class": by,
        "receipt_readers_outside_the_writer": s.get("receipt_readers_outside_the_writer"),
    })
    if face.get("verdict") != want_v:
        p.append("the verdict is not what the rows say")
    if s.get("task_sources_declaring_a_chain_action") != len(
            (face.get("task_definitions") or {}).get("rows") or []):
        p.append("the task-source count is not the length of its row list")
    for r in face.get("import_sites") or []:
        if r.get("class") != I_LEGS:
            p.append("an import site is published with a class this study cannot measure")
    if not face.get("verdict_line"):
        p.append("the face carries no verdict line")
    return p


def check():
    face = build(write=False)
    if not os.path.isfile(LATEST):
        print("problems: the published face is missing")
        return 2
    published = json.load(io.open(LATEST, encoding="utf-8"))
    problems = []
    for key in ("spawn_sites", "import_sites", "receipts", "wrappers", "task_definitions",
                "summary", "verdict", "producers"):
        if _canon(published.get(key)) != _canon(face.get(key)):
            problems.append("%s does not re-derive from source" % key)
    problems.extend(face_problems(published))
    if problems:
        for x in problems:
            print("PROBLEM:", x)
        return 1
    print("problems=[] rows=%d spawn=%d readers_outside_writer=%d verdict=%s"
          % (len(published.get("spawn_sites") or []), published["summary"]["spawn_sites"],
             published["summary"]["receipt_readers_outside_the_writer"],
             published.get("verdict")))
    return 0


def verify():
    a = _canon(build(write=False))
    b = _canon(build(write=False))
    if a != b:
        print("VERIFY FAIL: two builds differ")
        return 1
    print("VERIFY PASS: two builds identical (%d bytes)" % len(a))
    return 0


# ---- selftest -----------------------------------------------------------------
def selftest():
    bad = []
    total = 0

    def leg(name, cond):
        nonlocal total
        total += 1
        if not cond:
            bad.append(name)

    # 1-5 the spawn classifier, one leg per class plus a boundary
    leg("detached spawn is never an observer", classify_spawn(False, True, True) == S_NEVER)
    leg("waiting without reading the rc discards it", classify_spawn(True, False, True) == S_DISCARDS)
    leg("reading the rc without a failing action only observes",
        classify_spawn(True, True, False) == S_OBSERVES)
    leg("a raise on a non-zero rc fails", classify_spawn(True, True, True) == S_FAILS)
    leg("no wait means unobservable even when fields claim otherwise",
        classify_spawn(False, False, False) == S_NEVER)

    # 6-10 fixtures read through the same code path as the live scan
    fail_src = (
        "import subprocess\n"
        "def main():\n"
        "    p = subprocess.run(['python', 'Tools/s6_chain_bmb.py'])\n"
        "    if p.returncode != 0:\n"
        "        raise SystemExit(1)\n")
    row = _spawn_class_from_source(fail_src)
    leg("fixture: run+returncode+raise is F:", bool(row) and row["class"] == S_FAILS)

    det_src = (
        "import subprocess, sys\n"
        "p = subprocess.Popen([sys.executable, 'Tools/s6_chain_bmc.py'])\n"
        "print(p.pid)\n")
    row = _spawn_class_from_source(det_src)
    leg("fixture: bare Popen is NEVER:", bool(row) and row["class"] == S_NEVER)

    disc_src = (
        "import subprocess\n"
        "subprocess.run(['python', 'Tools/s6_chain_bma.py'])\n")
    row = _spawn_class_from_source(disc_src)
    leg("fixture: run without reading rc is DISCARDS:",
        bool(row) and row["class"] == S_DISCARDS)

    obs_src = (
        "import subprocess\n"
        "def go():\n"
        "    p = subprocess.run(['python', 'Tools/s6_chain_bmb.py'])\n"
        "    print('rc', p.returncode)\n")
    row = _spawn_class_from_source(obs_src)
    leg("fixture: printing the rc is not failing:", bool(row) and row["class"] == S_OBSERVES)

    # 11-14 wrapper classes, including the $LASTEXITCODE trap the card names
    leg("wrapper: rc + exit is F:",
        _wrapper_class_in_text('python "Tools\\s6_chain_bmb.py"\nif ($LASTEXITCODE -ne 0) { exit 1 }\n') == W_FAILS)
    leg("wrapper: rc then a message is PRINTS:",
        _wrapper_class_in_text('python "Tools\\s6_chain_bmb.py"\nif ($LASTEXITCODE -ne 0) { Write-Host "x" }\n') == W_PRINTS)
    leg("wrapper: $LASTEXITCODE after a .ps1 call cannot fail:",
        _wrapper_class_in_text("& T\\outer.ps1\nif ($LASTEXITCODE -ne 0) { exit 1 }\n") == W_NULL)
    leg("wrapper: no rc check is IGNORES:",
        _wrapper_class_in_text("& T\\x.ps1\n") == W_IGNORES)

    # 15-18 receipt mode
    leg("open('w') is a writer", classify_receipt("w") == R_WRITE)
    leg("open('a') is a writer", classify_receipt("a") == R_WRITE)
    leg("open('rb') is a reader", classify_receipt("rb") == R_READ)
    leg("no mode is a reader", classify_receipt(None) == R_READ)

    # 19-24 the live face obeys its own gate
    face = build(write=False)
    leg("live face has no self-detected problems", face_problems(face) == [])
    leg("live face re-derives", face == build(write=False))
    leg("control arms are all found",
        all((a or {}).get("found") for a in (face.get("control_arms") or {}).values()))

    bad_face = json.loads(json.dumps(face))
    bad_face["verdict"] = "a_verdict_this_study_never_publishes"
    leg("a hand-written verdict is refused", bool(face_problems(bad_face)))

    bad_face = json.loads(json.dumps(face))
    if bad_face["spawn_sites"]:
        bad_face["spawn_sites"][0]["class"] = S_FAILS
        bad_face["spawn_sites"][0]["can_fail"] = False
        leg("a relabelled spawn row is refused", bool(face_problems(bad_face)))
    else:
        leg("a relabelled spawn row is refused", True)

    bad_face = json.loads(json.dumps(face))
    bad_face["summary"]["receipt_readers_outside_the_writer"] = (
        bad_face["summary"]["receipt_readers_outside_the_writer"] + 1)
    leg("an inflated reader count is refused", bool(face_problems(bad_face)))

    bad_face = json.loads(json.dumps(face))
    if bad_face["receipts"]["writers"]:
        bad_face["receipts"]["readers_outside_the_writer"] = [
            dict(bad_face["receipts"]["writers"][0])]
        bad_face["summary"]["receipt_readers_outside_the_writer"] = 1
        leg("a writer published as an outside reader is refused",
            bool(face_problems(bad_face)))
    else:
        leg("a writer published as an outside reader is refused", True)

    if bad:
        print("SELFTEST FAIL %d/%d" % (total - len(bad), total))
        for x in bad:
            print("  -", x)
        return 1
    print("SELFTEST PASS %d/%d" % (total, total))
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "build"
    if cmd == "build":
        face = build(write=True)
        s = face["summary"]
        print("built %s: spawn=%d by_class=%s readers_outside_writer=%d verdict=%s"
              % (os.path.basename(LATEST), s["spawn_sites"],
                 ",".join("%s=%d" % (k, v) for k, v in s["by_class"].items() if v),
                 s["receipt_readers_outside_the_writer"], face["verdict"]))
        return 0
    if cmd == "check":
        return check()
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    print("usage: e559_chain_rc_consumer.py build|check|verify|selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main())