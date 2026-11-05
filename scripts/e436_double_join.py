"""E436: does any consumer join a double-ready directory value with its own name?

E433 published rows whose directory-named field holds a FILE path while a sibling name field
already equals that file's basename -- the composition ``dir + name`` is armed, and nobody had
asked whether a read site actually performs it.

Population (imported, not re-derived): ``results/state_tilt/constdirs_latest.json`` rows that
carry a ``fragment``. Rows are deduplicated to *targets* = (fragment, resolved_directory) so that
five rows of the same module are not counted as five findings.

Measurement: every ``.py`` source in E423's corpus is parsed with AST and every IO/path call whose
argument subtree spells the fragment literally is a *fragment site*. Each site is graded by the
base it composes onto:

  * ``joins_the_published_directory`` -- the base resolves to the very directory value the row
    published. This is the doubling read E433 implied.
  * ``composes_from_the_parent_directory`` -- the base resolves to the parent of that value, so
    the site rebuilds the same path correctly from a fresh root. It names the file; it does not
    consume the published value.
  * ``composes_from_an_unrelated_base`` / ``base_unresolved`` -- published, never folded.

For every composing site the concrete path is rebuilt and tested with ``os.path.exists``, so the
face answers E436's second half: compositions that would land on a file that is not there.

Verdict is recomputed from the summary by ``decide``; ``verify`` re-derives the whole census and
refuses a stored count that does not come back.

Usage:
    python scripts/e436_double_join.py run|verify|selftest
"""
from __future__ import annotations

import ast
import collections
import io
import json
import os
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import e423_dirfield_join as base  # noqa: E402  (corpus + fragment vocabulary, not re-implemented)

ST = os.path.join(ROOT, "results", "state_tilt")
CONSTDIRS = os.path.join(ST, "constdirs_latest.json")
OUTDIR = ST

# --- site classes (frozen vocabulary; verify refuses anything else) -------------------------
S_JOINS_PUBLISHED = "joins_the_published_directory"
S_FROM_PARENT = "composes_from_the_parent_directory"
S_FROM_OTHER = "composes_from_an_unrelated_base"
S_UNRESOLVED = "base_unresolved"
SITE_CLASSES = {S_JOINS_PUBLISHED, S_FROM_PARENT, S_FROM_OTHER, S_UNRESOLVED}

# --- call families -------------------------------------------------------------------------
READ_CALLS = {"open", "read_text", "read_bytes", "read_csv", "read_json", "read_parquet",
              "load", "loads", "read", "iterdir"}
WRITE_CALLS = {"write_text", "write_bytes", "to_csv", "to_parquet", "to_json", "dump"}
PATH_CALLS = {"join", "exists", "isfile", "isdir", "mkdir", "makedirs", "Path", "glob", "rglob",
              "unlink", "replace", "rename", "is_file", "is_dir"}

V_A_NO_DOUBLING_READ = (
    "no_reader_joins_a_double_ready_directory_value_and_the_readers_naming_the_same_file_"
    "recompose_it_from_the_parent")
V_B_NO_READER_NAMES = "no_reader_names_a_double_ready_fragment_at_all"
V_C_DOUBLED_ABSENT = (
    "a_reader_joins_a_double_ready_directory_value_with_its_own_name_and_the_doubled_path_is_absent")
V_D_DOUBLED_EXISTS = (
    "a_reader_joins_a_double_ready_directory_value_with_its_own_name_and_the_doubled_path_exists")
VERDICT_VOCAB = {V_A_NO_DOUBLING_READ, V_B_NO_READER_NAMES, V_C_DOUBLED_ABSENT, V_D_DOUBLED_EXISTS}


def _rel(path: str) -> str:
    return os.path.relpath(os.path.abspath(path), ROOT).replace("\\", "/")


def _load(path: str) -> dict:
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _src(rel: str) -> str:
    return io.open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace").read()


def _callee(node: ast.Call) -> str:
    f = node.func
    parts = []
    while isinstance(f, ast.Attribute):
        parts.append(f.attr)
        f = f.value
    if isinstance(f, ast.Name):
        parts.append(f.id)
    return ".".join(reversed(parts))


def _family(callee: str, node: ast.Call | None = None) -> str | None:
    """Grade a call by what it does; `open` is a reader only when its mode does not write."""
    last = callee.split(".")[-1]
    if last == "open" and node is not None and len(node.args) > 1:
        mode = node.args[1]
        if isinstance(mode, ast.Constant) and isinstance(mode.value, str) \
                and any(ch in mode.value for ch in "wax+"):
            return "write"
    if last in READ_CALLS:
        return "read"
    if last in WRITE_CALLS:
        return "write"
    if last in PATH_CALLS:
        return "path"
    return None


def _family_of(node: ast.Call) -> str | None:
    return _family(_callee(node), node)


def _chain(node: ast.AST) -> list[ast.AST] | None:
    """Flatten a join/division chain into its elements (left to right)."""
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        left = _chain(node.left)
        right = _chain(node.right)
        return (left or [node.left]) + (right or [node.right])
    if isinstance(node, ast.Call):
        last = _callee(node).split(".")[-1]
        if last in ("join", "Path") and node.args:
            out: list[ast.AST] = []
            for arg in node.args:
                out.extend(_chain(arg) or [arg])
            return out
    return None


def _fragment_node(node: ast.AST, fragment: str) -> ast.AST | None:
    """The outermost composing chain in `node` whose last element is the fragment."""
    best = None
    best_lines = -1
    for sub in ast.walk(node):
        chain = _chain(sub)
        if not chain:
            continue
        tail = chain[-1]
        if not (isinstance(tail, ast.Constant) and tail.value == fragment):
            continue
        span = (getattr(sub, "end_lineno", 0) or 0) - (getattr(sub, "lineno", 0) or 0)
        if span >= best_lines:
            best, best_lines = sub, span
    return best


def _enclosing_name(tree: ast.AST, lineno: int) -> str:
    best = (10 ** 9, "<module>")
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end = getattr(node, "end_lineno", 10 ** 9)
            if node.lineno <= lineno <= end:
                span = end - node.lineno
                if span < best[0]:
                    best = (span, node.name)
    return best[1]


def _module_assignments(tree: ast.AST) -> dict[str, ast.AST]:
    out: dict[str, ast.AST] = {}
    for node in tree.body if isinstance(tree, ast.Module) else []:
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name):
                    out[tgt.id] = node.value
    return out


def _resolve_name(rel: str, tree: ast.AST, name: str) -> str | None:
    """One-hop module constant resolution: string literal, __file__ shape, or another name."""
    assigns = _module_assignments(tree)
    value = assigns.get(name)
    seen = {name}
    for _ in range(3):
        if value is None:
            return None
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            return value.value
        if isinstance(value, ast.Name):
            if value.id in seen:
                return None
            seen.add(value.id)
            value = assigns.get(value.id)
            continue
        text = ast.unparse(value) if hasattr(ast, "unparse") else ""
        if "__file__" in text:
            here = os.path.join(ROOT, rel)
            hops = text.count("dirname")
            if "parents[" in text:
                try:
                    hops = int(text.split("parents[")[1].split("]")[0]) + 1
                except (IndexError, ValueError):
                    return None
            for _h in range(hops):
                here = os.path.dirname(here)
            return here
        return None
    return None


def _base_path(rel: str, tree: ast.AST, node: ast.AST) -> str | None:
    """Resolve the directory part of a composing expression (everything before the fragment)."""
    chain = _chain(node) or [node]
    head = chain[0]
    if isinstance(head, ast.Constant) and isinstance(head.value, str):
        parts = [head.value]
    elif isinstance(head, ast.Name):
        root = _resolve_name(rel, tree, head.id)
        if not root:
            return None
        parts = [root]
    else:
        return None
    for node in chain[1:-1]:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            parts.append(node.value)
        elif isinstance(node, ast.Name):
            seed = _resolve_name(rel, tree, node.id)
            if seed is None:
                # A name with no module binding is a runtime value; the base stays unknown
                # rather than being guessed from its spelling.
                return None
            parts.append(seed)
        else:
            return None
    return os.path.normpath(os.path.join(*parts))


def _inside(path: str) -> bool:
    try:
        rel = os.path.relpath(os.path.abspath(path), ROOT)
    except ValueError:
        return False
    return not rel.startswith("..")


def _shown(path: str | None) -> str | None:
    if not path:
        return None
    return _rel(path) if _inside(path) else os.path.abspath(path).replace("\\", "/")


# -------------------------------------------------------------------------------------------
# population
# -------------------------------------------------------------------------------------------

def population() -> tuple[list[dict], list[dict]]:
    """E433's rows carrying a fragment, plus the deduplicated targets they describe."""
    face = _load(CONSTDIRS)
    rows = [r for r in face.get("rows") or [] if r.get("fragment")]
    targets: dict[tuple[str, str | None], dict] = {}
    for r in rows:
        key = (r["fragment"], r.get("resolved_directory"))
        t = targets.setdefault(key, {
            "fragment": r["fragment"],
            "resolved_directory": r.get("resolved_directory"),
            "directory_expression": r.get("directory_expression"),
            "rows": 0,
            "classes": set(),
            "sites": [],
            "published_path_exists": r.get("path_exists"),
            "resolved_inside_tree": bool(r.get("resolved_inside_tree")),
        })
        t["rows"] += 1
        t["classes"].add(r.get("class"))
        t["sites"].append(r.get("site"))
    out = []
    for t in targets.values():
        t["classes"] = sorted(c for c in t["classes"] if c)
        t["sites"] = sorted({s for s in t["sites"] if s})
        if t["resolved_directory"]:
            t["published_path_exists"] = os.path.exists(t["resolved_directory"])
        out.append(t)
    out.sort(key=lambda t: (t["fragment"], str(t["resolved_directory"])))
    return rows, out


# -------------------------------------------------------------------------------------------
# fragment-site census
# -------------------------------------------------------------------------------------------

def fragment_sites(fragments: set[str]) -> list[dict]:
    sites: list[dict] = []
    for rel in base.corpus():
        try:
            src = _src(rel)
            tree = ast.parse(src)
        except (OSError, SyntaxError, ValueError):
            continue
        calls = [n for n in ast.walk(tree)
                 if isinstance(n, ast.Call) and _family_of(n) in ("read", "write", "path")]
        for call in calls:
            hit = [f for f in fragments
                   if any(isinstance(s, ast.Constant) and s.value == f for s in ast.walk(call))]
            if not hit:
                continue
            # One row per (file, line, same name): the innermost call holding the literal is the
            # composing act; the outer open()/json.load() wrapping it is the same act.
            line = getattr(call, "lineno", 0)
            for name in hit:
                sites.append({
                    "file": rel,
                    "line": line,
                    "function": _enclosing_name(tree, line),
                    "callee": _callee(call),
                    "family": _family_of(call),
                    "fragment": name,
                    "_chain": _fragment_node(call, name),
                    "_tree": tree,
                })
        # A name that only ever appears inside a payload literal is a republication surface, not
        # a read; those are counted separately so "named" never reads as "consumed".
    # keep the earliest site per (file, line, fragment); a chain inside it is the composing act
    dedup: dict[tuple[str, int, str], dict] = {}
    for s in sites:
        dedup.setdefault((s["file"], s["line"], s["fragment"]), s)
    out = []
    for s in dedup.values():
        chain = s.pop("_chain")
        tree = s.pop("_tree")
        if chain is None:
            s["class"] = S_UNRESOLVED
            s["base_text"] = None
            s["base_path"] = None
            s["composed_path"] = None
            s["composed_exists"] = None
        else:
            elems = _chain(chain) or [chain]
            parts = [ast.unparse(n) if hasattr(ast, "unparse") else "" for n in elems[:-1]]
            s["base_text"] = " | ".join(parts)
            base_path = _base_path(s["file"], tree, chain)
            s["base_path"] = _shown(base_path)
            if base_path is None:
                s["class"] = S_UNRESOLVED
                s["composed_path"] = None
                s["composed_exists"] = None
            else:
                composed = os.path.join(base_path, s["fragment"])
                s["composed_path"] = _shown(composed)
                s["composed_exists"] = os.path.exists(composed)
                s["class"] = S_FROM_OTHER  # re-graded against each target below
        out.append(s)
    out.sort(key=lambda s: (s["file"], s["line"]))
    return out


def relate(sites: list[dict], targets: list[dict]) -> list[dict]:
    """Grade each site against the rows that publish the same fragment."""
    by_fragment: dict[str, list[dict]] = collections.defaultdict(list)
    for t in targets:
        by_fragment[t["fragment"]].append(t)
    for s in sites:
        rel = []
        for t in by_fragment.get(s["fragment"], []):
            published = t["resolved_directory"]
            if published and s.get("base_path"):
                base_abs = os.path.join(ROOT, s["base_path"]) if not os.path.isabs(s["base_path"]) \
                    else s["base_path"]
                if os.path.normcase(os.path.normpath(base_abs)) == os.path.normcase(
                        os.path.normpath(published)):
                    rel.append((t, S_JOINS_PUBLISHED))
                    continue
                if os.path.normcase(os.path.normpath(base_abs)) == os.path.normcase(
                        os.path.normpath(os.path.dirname(published))):
                    rel.append((t, S_FROM_PARENT))
                    continue
            rel.append((t, S_FROM_OTHER if s.get("base_path") else S_UNRESOLVED))
        classes = [c for _t, c in rel]
        if S_JOINS_PUBLISHED in classes:
            s["class"] = S_JOINS_PUBLISHED
        elif S_FROM_PARENT in classes:
            s["class"] = S_FROM_PARENT
        elif classes:
            s["class"] = S_FROM_OTHER if s.get("base_path") else S_UNRESOLVED
        s["targets"] = [{"fragment": t["fragment"],
                         "resolved_directory": _shown(t["resolved_directory"]),
                         "class": c} for t, c in rel]
        if s["class"] == S_JOINS_PUBLISHED:
            published = next(t["resolved_directory"] for t, c in rel if c == S_JOINS_PUBLISHED)
            doubled = os.path.join(published, s["fragment"])
            s["doubled_path"] = _shown(doubled)
            s["doubled_exists"] = os.path.exists(doubled)
    return sites


# -------------------------------------------------------------------------------------------
# build / verify / selftest
# -------------------------------------------------------------------------------------------

def decide(summary: dict) -> str:
    """The verdict is recomputed here and never written by hand."""
    if summary["fragment_naming_read_sites"] == 0:
        return V_B_NO_READER_NAMES
    if summary["read_sites_joining_the_published_directory"]:
        if summary["doubled_paths_that_exist"]:
            return V_D_DOUBLED_EXISTS
        return V_C_DOUBLED_ABSENT
    return V_A_NO_DOUBLING_READ


def build() -> dict:
    rows, targets = population()
    fragments = {t["fragment"] for t in targets}
    sites = relate(fragment_sites(fragments), targets)
    reads = [s for s in sites if s["family"] == "read"]
    writes = [s for s in sites if s["family"] == "write"]
    joins = [s for s in reads if s["class"] == S_JOINS_PUBLISHED]
    parents = [s for s in reads if s["class"] == S_FROM_PARENT]
    in_tree = [t for t in targets if t["resolved_inside_tree"] and t["resolved_directory"]]
    summary = {
        "double_ready_rows": len(rows),
        "double_ready_targets": len(targets),
        "targets_by_fragment": dict(collections.Counter(t["fragment"] for t in targets)),
        "targets_with_a_resolved_in_tree_directory": len(in_tree),
        "published_paths_that_exist": sum(1 for t in targets if t["published_path_exists"]),
        "fragment_naming_sites": len(sites),
        "fragment_naming_read_sites": len(reads),
        "fragment_naming_write_sites": len(writes),
        "sites_by_class": dict(collections.Counter(s["class"] for s in sites)),
        "sites_by_family": dict(collections.Counter(s["family"] for s in sites)),
        "read_sites_that_rebuild_the_published_path": sum(
            1 for s in reads
            if s.get("composed_path") and any(
                t["resolved_directory"] and os.path.normcase(os.path.normpath(
                    os.path.join(ROOT, s["composed_path"]))) == os.path.normcase(
                    os.path.normpath(t["resolved_directory"]))
                for t in targets if t["fragment"] == s["fragment"] and t["resolved_directory"])),
        "read_sites_joining_the_published_directory": len(joins),
        "read_sites_composing_from_the_parent_directory": len(parents),
        "doubled_paths_that_exist": sum(1 for s in joins if s.get("doubled_exists")),
        "read_compositions_that_exist": sum(1 for s in reads if s.get("composed_exists")),
        "read_compositions_that_land_on_an_absent_file": sum(
            1 for s in reads if s.get("composed_exists") is False),
        "read_compositions_unresolved": sum(
            1 for s in reads if s.get("composed_exists") is None),
        "sites_by_file": dict(collections.Counter(s["file"] for s in sites)),
        "targets_without_any_read_site": sorted(
            t["fragment"] for t in targets
            if not any(s["fragment"] == t["fragment"] and s["family"] == "read" for s in sites)),
    }
    verdict = decide(summary)
    face = {
        "study": "E436_whether_any_consumer_joins_a_double_ready_directory_row_with_its_name",
        "card": "E436-WHICH-CONSUMER-JOINS-THE-DOUBLE-READY-ROWS-THAT-E433-FOUND",
        "title": "grade every site that names a double-ready fragment by the base it composes onto "
                 "and test the composed path",
        "generated": date.today().isoformat(),
        "evidence_cutoff": _load(CONSTDIRS).get("evidence_cutoff"),
        "verdict": verdict,
        "summary": summary,
        "targets": [{**t, "classes": t["classes"]} for t in targets],
        "read_sites": reads,
        "write_sites": writes,
        "method_limits": [
            "the population is E433's published rows (constdirs_latest.json) carrying a fragment; "
            "rows are deduplicated to (fragment, resolved_directory) targets, so row counts and "
            "target counts are different units and are published side by side",
            "a site is attributed only when its composing chain ends in the fragment literal: a "
            "site that builds the name from a variable, an f-string, or a loop is outside this "
            "scan and is not counted as absent",
            "the base is resolved one hop through module-level constants (string literal, "
            "__file__/dirname shape, another name); a base bound inside a function stays "
            "base_unresolved rather than being guessed from its spelling",
            "existence is tested on the current work tree, so a gitignored runtime cache that this "
            "machine never wrote reads as absent exactly like a mis-composed in-tree path",
        ],
    }
    return face


def verify(face: dict | None = None) -> list[str]:
    problems: list[str] = []
    face = face or _load(os.path.join(OUTDIR, "doublejoin_latest.json"))
    if face.get("verdict") not in VERDICT_VOCAB:
        problems.append(f"verdict outside vocabulary: {face.get('verdict')!r}")
    if not face.get("evidence_cutoff"):
        problems.append("evidence_cutoff missing")
    live = build()
    mine = face.get("summary") or {}
    for key in ("double_ready_rows", "double_ready_targets", "fragment_naming_sites",
                "fragment_naming_read_sites", "read_sites_joining_the_published_directory",
                "read_sites_composing_from_the_parent_directory",
                "read_compositions_that_land_on_an_absent_file",
                "published_paths_that_exist", "doubled_paths_that_exist"):
        if mine.get(key) != live["summary"].get(key):
            problems.append(f"{key} stored={mine.get(key)!r} live={live['summary'].get(key)!r}")
    if face.get("verdict") != live["verdict"]:
        problems.append(f"verdict stored={face.get('verdict')!r} recomputed={live['verdict']!r}")
    for s in live["read_sites"]:
        if s["class"] not in SITE_CLASSES:
            problems.append(f"site class outside vocabulary: {s['file']}:{s['line']} {s['class']!r}")
        if s["class"] == S_FROM_PARENT and s.get("composed_exists") is None:
            problems.append(f"parent composition with no path: {s['file']}:{s['line']}")
    return problems


def selftest() -> int:
    total = bad = 0

    def check(name: str, ok: bool, detail="") -> None:
        nonlocal total, bad
        total += 1
        if not ok:
            bad += 1
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail else ""))

    tree = ast.parse(
        "ROOT = os.path.dirname(os.path.abspath(__file__))\n"
        "def emit(tmp):\n"
        "    a = os.path.join(ROOT, 'results', 'x.json')\n"
        "    b = ROOT / 'results' / 'y.json'\n"
        "    c = os.path.join(tmp, 'results', 'z.json')\n"
        "    return a, b, c\n")
    join_call = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and _callee(node) == "os.path.join" \
                and any(isinstance(s, ast.Constant) and s.value == "x.json"
                        for s in ast.walk(node)):
            join_call = node
            break
    check("a join call is found", join_call is not None)
    chain = _fragment_node(join_call, "x.json")
    check("the composing chain ends on the fragment", chain is not None)
    resolved = _base_path("<selftest>", tree, chain) if chain else None
    check("__file__ shape resolves to a directory", bool(resolved) and not resolved.endswith(".py"),
          resolved)

    tree2 = ast.parse(
        "ROOT = os.path.dirname(os.path.abspath(__file__))\n"
        "v = ROOT / 'results' / 'y.json'\n")
    chain2 = _fragment_node(tree2.body[1].value, "y.json")
    check("a pathlib division chain flattens", chain2 is not None
          and len(_chain(chain2) or []) == 3, _chain(chain2))
    check("a chain without the fragment is not attributed",
          _fragment_node(tree2.body[1].value, "nope.json") is None)

    tree3 = ast.parse("def f(p):\n    return os.path.join(p, 'q.json')\n")
    call3 = [n for n in ast.walk(tree3) if isinstance(n, ast.Call) and _callee(n) == "os.path.join"][0]
    chain3 = _fragment_node(call3, "q.json")
    check("a runtime parameter base stays unresolved",
          _base_path("<selftest>", tree3, chain3) is None)

    fam = _family("json.loads") == "read" and _family("Path.write_text") == "write" \
        and _family("os.path.join") == "path"
    check("call families are graded by name", fam)
    mode_tree = ast.parse("open(a, 'w')") if False else ast.parse(
        "with open(p, 'w', encoding='utf-8') as fh:\n    pass\n"
        "with open(q, encoding='utf-8') as fh:\n    pass\n")
    calls = [n for n in ast.walk(mode_tree) if isinstance(n, ast.Call)]
    check("open in 'w' mode is a write, open with no mode is a read",
          _family_of(calls[0]) == "write" and _family_of(calls[1]) == "read",
          (_family_of(calls[0]), _family_of(calls[1])))

    s = {"fragment_naming_read_sites": 0, "read_sites_joining_the_published_directory": 0,
         "doubled_paths_that_exist": 0}
    check("no reader is verdict B", decide(s) == V_B_NO_READER_NAMES)
    s["fragment_naming_read_sites"] = 4
    check("readers that recompose from the parent are verdict A", decide(s) == V_A_NO_DOUBLING_READ)
    s["read_sites_joining_the_published_directory"] = 1
    check("a doubling read with an absent path is verdict C", decide(s) == V_C_DOUBLED_ABSENT)
    s["doubled_paths_that_exist"] = 1
    check("a doubling read that lands is verdict D", decide(s) == V_D_DOUBLED_EXISTS)

    doctored = {"verdict": sorted(VERDICT_VOCAB)[0], "evidence_cutoff": "2026-01-01",
                "summary": {"double_ready_rows": -1, "double_ready_targets": -1,
                            "fragment_naming_sites": -1, "fragment_naming_read_sites": -1,
                            "read_sites_joining_the_published_directory": -1,
                            "read_sites_composing_from_the_parent_directory": -1,
                            "read_compositions_that_land_on_an_absent_file": -1,
                            "published_paths_that_exist": -1, "doubled_paths_that_exist": -1}}
    problems = verify(doctored)
    check("verify refuses a stale row count", any("double_ready_rows" in p for p in problems),
          problems[:2])

    print(f"selftest {'PASS' if not bad else 'FAIL'} {total - bad}/{total}")
    return 0 if not bad else 1


def main(argv: list[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "verify":
        problems = verify()
        for p in problems:
            print("PROBLEM:", p)
        print(f"verify problems={len(problems)}")
        return 0 if not problems else 1
    face = build()
    os.makedirs(OUTDIR, exist_ok=True)
    if not face.get("evidence_cutoff"):
        print("evidence_cutoff missing on the population face; refusing to publish a dated name")
        return 2
    out = os.path.join(OUTDIR, f"DOUBLEJOIN-{face['evidence_cutoff']}.json")
    for target in (out, os.path.join(OUTDIR, "doublejoin_latest.json")):
        with io.open(target, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
    s = face["summary"]
    print(f"rows={s['double_ready_rows']} targets={s['double_ready_targets']} "
          f"sites={s['fragment_naming_sites']} reads={s['fragment_naming_read_sites']} "
          f"joins={s['read_sites_joining_the_published_directory']} "
          f"parent={s['read_sites_composing_from_the_parent_directory']} "
          f"absent={s['read_compositions_that_land_on_an_absent_file']}")
    print(f"by_class={s['sites_by_class']}")
    print(f"verdict={face['verdict']}")
    print(f"face={_rel(out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))