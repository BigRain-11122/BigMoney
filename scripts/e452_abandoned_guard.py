"""E452 -- of the harness opens E447 found under an abandoned base, which would raise today?

E447 (results/state_tilt/abandonedread_latest.json) published 23 face-home bases with no write site
in the corpus, 7 of which are still read by code a harness launches (smoke_test.py four times, plus
strategy_scorecard and trial_labor_w21).  A harness that opens a file nobody writes is only safe in
one of two worlds: the open is guarded (a try/except, an existence test, or a default), or the
artifact it opens is still on disk.

This face takes exactly those read sites -- the sites under an abandoned base whose reader E447
graded live -- and publishes, per site, the guard shapes found in its own source, whether the
resolved artifact exists on disk today, and the resulting class.

Nothing is executed: this is a static AST reading of the readers plus an os.path.exists on the
resolved targets.

    python scripts/e452_abandoned_guard.py run        # build and publish the face
    python scripts/e452_abandoned_guard.py check      # re-derive every tally from the published rows
    python scripts/e452_abandoned_guard.py verify     # re-derive from the live tree and the disk
    python scripts/e452_abandoned_guard.py selftest   # offline legs
"""

from __future__ import annotations

import ast
import json
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import e446_frozen_writer as e446  # noqa: E402
import e447_abandoned_read as e447  # noqa: E402  (the site scan is the measurement)

ROOT = e447.ROOT
OUTDIR = e447.OUTDIR
DATED_PREFIX = "ABANDONEDGUARD"
FACE_NAME = DATED_PREFIX.lower() + "_latest.json"
SOURCE_FACE = e447.FACE_NAME

C_GONE = "unguarded_and_the_artifact_is_gone"
C_PRESENT = "unguarded_but_the_artifact_is_present"
C_GUARDED = "guarded_so_a_missing_artifact_is_announced"
C_UNRESOLVED = "target_not_statically_resolvable"
CLASSES = (C_GONE, C_PRESENT, C_GUARDED, C_UNRESOLVED)

G_TRY = "try_except"
G_EXISTS = "existence_test_in_the_enclosing_test"
G_EXISTS_FN = "existence_test_earlier_in_the_enclosing_function"
G_DEFAULT = "conditional_default"
GUARD_SHAPES = (G_TRY, G_EXISTS, G_EXISTS_FN, G_DEFAULT)

EXIST_FUNCS = {"exists", "isfile", "isdir", "is_file", "is_dir", "lexists"}


def _rel(path: str) -> str:
    return os.path.relpath(path, ROOT).replace("\\", "/")


def _load(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def is_own_output(rel: str) -> bool:
    name = os.path.basename(rel)
    if name == FACE_NAME:
        return True
    return name.startswith(DATED_PREFIX + "-") and name.endswith(".json")


# ----------------------------------------------------------------------------- call location


def _call_kind(call: ast.Call) -> str | None:
    """The kind label E447 published for this call shape (same vocabulary, never re-invented)."""
    func = call.func
    name = func.attr if isinstance(func, ast.Attribute) else (
        func.id if isinstance(func, ast.Name) else None)
    if name == "open":
        return "open"
    if isinstance(func, ast.Attribute) and func.attr in e447.READ_PATH_METHODS:
        return func.attr
    if isinstance(func, ast.Attribute) and func.attr in e447.READ_FILE_CALLS:
        return func.attr
    if isinstance(func, ast.Attribute) and func.attr in e447.READ_DIR_CALLS:
        return func.attr
    if isinstance(func, ast.Attribute) and func.attr in e447.READ_COPY_SOURCES:
        return "copy_source"
    return None


def _path_expr(call: ast.Call):
    """The node E447's read_sites used as the path argument for this shape."""
    func = call.func
    name = func.attr if isinstance(func, ast.Attribute) else (
        func.id if isinstance(func, ast.Name) else None)
    if name == "open" and call.args:
        return call.args[0]
    if isinstance(func, ast.Attribute) and func.attr in e447.READ_PATH_METHODS:
        return func.value
    if isinstance(func, ast.Attribute) and func.attr in e447.READ_FILE_CALLS:
        if call.args:
            return call.args[0]
        for kw in call.keywords:
            if kw.arg in ("filepath_or_buffer", "path", "io", "fname", "filename"):
                return kw.value
        return None
    if isinstance(func, ast.Attribute) and func.attr in e447.READ_DIR_CALLS:
        if call.args:
            return call.args[0]
        if isinstance(func.value, (ast.Constant, ast.Name, ast.Call)):
            return func.value
        return None
    if isinstance(func, ast.Attribute) and func.attr in e447.READ_COPY_SOURCES:
        if call.args:
            return call.args[0]
        for kw in call.keywords:
            if kw.arg in ("src", "source"):
                return kw.value
    return None


def _parents(tree: ast.AST) -> dict:
    parents: dict = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node
    return parents


def _contains(node: ast.AST, target: ast.AST) -> bool:
    for n in ast.walk(node):
        if n is target:
            return True
    return False


def _is_exists_call(node: ast.AST) -> bool:
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    if isinstance(func, ast.Attribute):
        return func.attr in EXIST_FUNCS
    if isinstance(func, ast.Name):
        return func.id in EXIST_FUNCS
    return False


def _norm(text: str | None) -> str:
    return None if text is None else "".join(str(text).split())


def _existence_targets(test: ast.AST, src: str) -> list[tuple[str, bool]]:
    """(normalised expression text, whether the test is a NEGATIVE existence test)."""
    out: list[tuple[str, bool]] = []
    for node in ast.walk(test):
        if not _is_exists_call(node) or not node.args:
            continue
        text = _norm(ast.get_source_segment(src, node.args[0]))
        if not text:
            continue
        negative = False
        cur = node
        while cur is not test:
            parent = None
            for cand in ast.walk(test):
                if any(child is cur for child in ast.iter_child_nodes(cand)):
                    parent = cand
                    break
            if parent is None:
                break
            if isinstance(parent, ast.UnaryOp) and isinstance(parent.op, ast.Not):
                negative = True
                break
            if isinstance(parent, ast.Compare) and any(
                    isinstance(c, ast.Constant) and c.value is False for c in parent.comparators):
                negative = True
                break
            cur = parent
        out.append((text, negative))
    return out


def _module_source(rel: str, cache: dict) -> tuple[str | None, ast.AST | None, dict | None]:
    if rel in cache:
        return cache[rel]
    path = os.path.join(ROOT, rel)
    try:
        with open(path, encoding="utf-8") as fh:
            src = fh.read()
        tree = ast.parse(src)
    except (OSError, SyntaxError, UnicodeDecodeError):
        cache[rel] = (None, None, None)
        return cache[rel]
    cache[rel] = (src, tree, _parents(tree))
    return cache[rel]


# A shared-resolver reading that stopped early is NOT a path (E448 family: a truncated f-string
# head reported as a target reads as a missing file).  Those sites are re-resolved here with the
# f-string completed when every part of it names a module constant, and the provenance is
# published so a completed reading is never mistaken for a shared-resolver one.
PARTIAL_HOW_MARKERS = ("fstring_head", "unresolved", "too_deep", "bare_name")


def how_is_partial(how: str | None) -> bool:
    h = str(how or "")
    return any(m in h for m in PARTIAL_HOW_MARKERS)


def complete_resolve(node, consts: dict, depth: int = 0, rel: str = ""):
    """The value of the expression only if EVERY part of it resolves (None otherwise)."""
    if depth > 12:
        return None
    if isinstance(node, ast.Constant):
        return e446._norm_repo_path(node.value) if isinstance(node.value, str) else None
    if isinstance(node, ast.Name):
        if node.id == "__file__":
            return rel or None
        if node.id in consts:
            return e446._norm_repo_path(consts[node.id])
        if node.id in ("ROOT", "REPO", "REPO_ROOT", "BASE_DIR"):
            return ""
        return None
    if isinstance(node, ast.JoinedStr):
        parts: list[str] = []
        for part in node.values:
            if isinstance(part, ast.Constant) and isinstance(part.value, str):
                parts.append(str(part.value))
            elif isinstance(part, ast.FormattedValue):
                val = complete_resolve(part.value, consts, depth + 1, rel)
                if val is None:
                    return None
                parts.append(val)
            else:
                return None
        return e446._norm_repo_path("".join(parts))
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = complete_resolve(node.left, consts, depth + 1, rel)
        right = complete_resolve(node.right, consts, depth + 1, rel)
        if left is None or right is None:
            return None
        return e446._norm_repo_path(left + "/" + right)
    if isinstance(node, ast.Call):
        fname = node.func.attr if isinstance(node.func, ast.Attribute) else (
            node.func.id if isinstance(node.func, ast.Name) else None)
        if fname in ("abspath", "realpath", "normpath", "resolve", "str") and len(node.args) == 1:
            return complete_resolve(node.args[0], consts, depth + 1, rel)
        if e446._is_joinish(node.func):
            vals = [complete_resolve(a, consts, depth + 1, rel) for a in node.args]
            if not vals or any(v is None for v in vals):
                return None
            joined = vals[0]
            for piece in vals[1:]:
                joined = joined + "/" + piece if joined else piece
            return e446._norm_repo_path(joined)
    return None


def strict_consts(tree: ast.AST, rel: str = "", passes: int = 2) -> dict[str, str]:
    """Module-scope constants resolved WITHOUT truncation (an f-string with literal parts completes).

    The shared consts map stores a truncated value for a constant written as
    ``os.path.join(ROOT, "d", f"CENSUS-{PIN}.json")``; comparing the two maps is what tells a
    completed reading from the shared one.
    """
    consts: dict[str, str] = {}
    for _ in range(max(1, passes)):
        pairs = []

        def walk_block(body):
            for node in body:
                if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                        and isinstance(node.targets[0], ast.Name):
                    pairs.append((node.targets[0].id, node.value))
                elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) \
                        and node.value is not None:
                    pairs.append((node.target.id, node.value))
                for attr in ("body", "orelse", "finalbody"):
                    inner = getattr(node, attr, None)
                    if isinstance(inner, list) and inner and isinstance(inner[0], ast.stmt):
                        walk_block(inner)
                for handler in getattr(node, "handlers", []) or []:
                    walk_block(handler.body)

        walk_block(getattr(tree, "body", []))
        for name, expr in pairs:
            val = complete_resolve(expr, consts, 0, rel)
            if val is not None:
                consts[name] = val
    return consts


def resolve_for_site(rel: str, expr, tree, consts: dict, strict: dict) -> tuple[str | None, str, str]:
    """(value, resolution, shared_how) for one read site.

    resolution = shared_resolver (the shared reading is confirmed by an untruncated resolution),
    completed_fstring (the shared reading was truncated and the completion differs), or
    unresolved (nothing complete can be produced).
    """
    shared, how = e446.resolve_path(expr, consts, 0, rel) if expr is not None else (None, "no_expression")
    done = complete_resolve(expr, strict, 0, rel) if expr is not None else None
    if done is not None:
        return done, ("shared_resolver" if done == shared else "completed_fstring"), how
    if shared is not None and not how_is_partial(how):
        # the shared resolver follows shapes the strict one does not (dirname/parent chains)
        return shared, "shared_resolver", how
    return None, "unresolved", how


def guard_shapes(rel: str, line: int, kind: str, cache: dict | None = None) -> tuple[list[str], str, int]:
    """Guard shapes visible around the read call at `line`; plus the path expression text."""
    cache = cache if cache is not None else {}
    src, tree, parents = _module_source(rel, cache)
    if tree is None:
        return [], "", 0
    calls = [n for n in ast.walk(tree)
             if isinstance(n, ast.Call) and getattr(n, "lineno", 0) == line
             and _call_kind(n) is not None]
    if not calls:
        return [], "", 0
    same_kind = [c for c in calls if _call_kind(c) == kind] or calls
    call = same_kind[0]
    expr = _path_expr(call)
    want = _norm(ast.get_source_segment(src, expr)) if expr is not None else ""
    shapes: set[str] = set()

    cur: ast.AST = call
    while cur in parents:
        anc = parents[cur]
        if isinstance(anc, ast.Try):
            for stmt in anc.body:
                if _contains(stmt, call):
                    shapes.add(G_TRY)
                    break
        if isinstance(anc, (ast.If, ast.IfExp)):
            in_body = any(_contains(s, call) for s in anc.body) if isinstance(
                anc.body, list) else _contains(anc.body, call)
            in_else = False
            if isinstance(anc, ast.If):
                in_else = any(_contains(s, call) for s in anc.orelse)
            else:
                in_else = _contains(anc.orelse, call) if anc.orelse is not None else False
            if in_body or in_else:
                for text, negative in _existence_targets(anc.test, src):
                    if text != want:
                        continue
                    if in_body and not negative:
                        shapes.add(G_EXISTS)
                    if in_else and negative:
                        shapes.add(G_EXISTS)
            if isinstance(anc, ast.IfExp) and in_body and anc.orelse is not None:
                shapes.add(G_DEFAULT)
        cur = anc

    # an enclosing function that tests the same path before this line (lexical, not a CFG proof)
    fn = None
    cur = call
    while cur in parents:
        cur = parents[cur]
        if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef)):
            fn = cur
            break
    if fn is not None:
        for stmt in fn.body:
            if getattr(stmt, "lineno", 0) >= line:
                continue
            for node in ast.walk(stmt):
                if isinstance(node, (ast.If, ast.IfExp, ast.BoolOp, ast.While)):
                    for text, negative in _existence_targets(node, src):
                        if text == want and negative:
                            shapes.add(G_EXISTS_FN)
    return [s for s in GUARD_SHAPES if s in shapes], want, len(calls)


# ----------------------------------------------------------------------------- build


def artifact_present(resolved: str | None, root: str = ROOT) -> bool | None:
    """None when the target is not statically resolvable (a literal tail is not a path)."""
    if not resolved or str(resolved).startswith("?"):
        return None
    return os.path.exists(os.path.join(root, str(resolved).replace("/", os.sep)))


def classify(shapes: list[str], present: bool | None) -> str:
    if present is None:
        return C_UNRESOLVED
    if shapes:
        return C_GUARDED
    return C_PRESENT if present else C_GONE


def verdict_for(sites: list[dict]) -> str:
    if not sites:
        return "empty_population"
    if any(s["class"] == C_GONE for s in sites):
        return "at_least_one_harness_open_would_raise_today"
    if any(s["class"] == C_PRESENT for s in sites):
        return "every_unguarded_harness_open_still_finds_its_artifact"
    if any(s["class"] == C_UNRESOLVED for s in sites):
        return "no_unguarded_open_is_statically_resolvable"
    return "every_harness_open_of_an_abandoned_base_is_guarded"


def module_consts(rel: str, cache: dict) -> tuple[dict, dict]:
    key = ("consts", rel)
    if key in cache:
        return cache[key]
    _src, tree, _parents_map = _module_source(rel, cache)
    consts = e446.module_constants(tree, rel) if tree is not None else {}
    strict = strict_consts(tree, rel) if tree is not None else {}
    cache[key] = (consts, strict)
    return cache[key]


def locate_expr(rel: str, line: int, kind: str, cache: dict):
    """The path-expression node of the read call E447 published at this line."""
    _src, tree, _parents_map = _module_source(rel, cache)
    if tree is None:
        return None
    calls = [n for n in ast.walk(tree)
             if isinstance(n, ast.Call) and getattr(n, "lineno", 0) == line
             and _call_kind(n) is not None]
    if not calls:
        return None
    same_kind = [c for c in calls if _call_kind(c) == kind] or calls
    return _path_expr(same_kind[0])


def build(cutoff: str | None = None, root: str | None = None,
          source_face: dict | None = None, scan: dict | None = None,
          harness: dict | None = None) -> dict:
    root = root or ROOT
    face = source_face if source_face is not None else _load(os.path.join(root, OUTDIR, SOURCE_FACE))
    scan = scan if scan is not None else e447.scan_corpus(root)
    harness = harness if harness is not None else e447.harness_readers()

    readers: dict[str, set] = {}
    for s in scan["sites"]:
        if s["face"] not in readers:
            readers[s["face"]] = set()
        readers[s["face"]].add(e447.reader_class(
            s["face"], harness, scan, bool((scan.get("writes_faces") or {}).get(s["face"]))))

    live = {k for k, v in readers.items() if v & set(e447.LIVE_CLASSES)}
    population = [r for r in face["rows"] if r["class"] == e447.C_READ
                  and r["reader_faces_with_a_live_consumer"]]

    cache: dict = {}
    rows: list[dict] = []
    all_sites: list[dict] = []
    shared_mismatch: list[str] = []
    for base_row in population:
        base = base_row["base"]
        sites = []
        for s in scan["sites"]:
            if s["face"] not in live:
                continue
            if not e446.is_under(s["resolved_path"], base):
                continue
            shapes, expr, calls_on_line = guard_shapes(s["face"], s["line"], s["kind"], cache)
            consts, strict = module_consts(s["face"], cache)
            expr_node = locate_expr(s["face"], s["line"], s["kind"], cache)
            value, resolution, shared_how = resolve_for_site(s["face"], expr_node, None, consts, strict)
            if resolution == "shared_resolver" and value != s["resolved_path"]:
                shared_mismatch.append("%s:%d" % (s["face"], s["line"]))
            present = artifact_present(value, root)
            site = {
                "face": s["face"], "line": s["line"], "kind": s["kind"],
                "resolved_path": value,
                "shared_resolver_path": s["resolved_path"],
                "resolution": resolution,
                "resolver_how": shared_how,
                "path_expression": expr,
                "calls_on_line": calls_on_line,
                "guard_shapes": shapes, "guarded": bool(shapes),
                "artifact_present": present,
                "class": classify(shapes, present),
            }
            sites.append(site)
        sites.sort(key=lambda x: (x["face"], x["line"]))
        all_sites.extend(sites)
        rows.append({
            "base": base,
            "e447_class": base_row["class"],
            "live_readers": sorted({s["face"] for s in sites}),
            "site_count": len(sites),
            "class_counts": {c: sum(1 for s in sites if s["class"] == c) for c in CLASSES},
            "sites": sites,
        })

    def counts(key: str) -> dict:
        out: dict = {}
        for s in all_sites:
            v = s[key]
            if isinstance(v, list):
                v = json.dumps(v, ensure_ascii=False)
            out[str(v).lower() if isinstance(v, bool) else v] = \
                out.get(str(v).lower() if isinstance(v, bool) else v, 0) + 1
        return out

    cross = {
        "guarded": {str(p): sum(1 for s in all_sites
                                if s["guarded"] and s["artifact_present"] is p) for p in (True, False, None)},
        "unguarded": {str(p): sum(1 for s in all_sites
                                  if not s["guarded"] and s["artifact_present"] is p) for p in (True, False, None)},
    }
    summary = {
        "bases_with_a_live_reader": len(rows),
        "sites_graded": len(all_sites),
        "class_counts": {c: sum(1 for s in all_sites if s["class"] == c) for c in CLASSES},
        "guarded_sites": sum(1 for s in all_sites if s["guarded"]),
        "unguarded_sites": sum(1 for s in all_sites if not s["guarded"]),
        "guard_shape_counts": {g: sum(1 for s in all_sites if g in s["guard_shapes"])
                               for g in GUARD_SHAPES},
        "sites_with_no_guard": sum(1 for s in all_sites if not s["guard_shapes"]),
        "artifact_present_counts": {"present": sum(1 for s in all_sites if s["artifact_present"] is True),
                                    "gone": sum(1 for s in all_sites if s["artifact_present"] is False),
                                    "unresolved": sum(1 for s in all_sites
                                                      if s["artifact_present"] is None)},
        "guard_by_presence": cross,
        "distinct_reader_faces": len({s["face"] for s in all_sites}),
        "distinct_targets": len({s["resolved_path"] for s in all_sites}),
        "resolution_counts": {r: sum(1 for s in all_sites if s["resolution"] == r)
                              for r in ("shared_resolver", "completed_fstring", "unresolved")},
        "shared_resolver_mismatches": shared_mismatch,
        "bases_where_e447_live_reader_is_not_live_now": [
            r["base"] for r in rows if not r["sites"]],
        "unguarded_and_gone_sites": ["%s:%d" % (s["face"], s["line"])
                                     for s in all_sites if s["class"] == C_GONE],
        "population_check": {
            "e447_bases_read_by_a_live_consumer": face["summary"]["bases_read_by_a_live_consumer"],
            "recomputed_bases_with_a_live_reader": len(rows),
            "agrees": face["summary"]["bases_read_by_a_live_consumer"] == len(rows),
        },
        "corpus": {
            "python_files_walked": len(scan["files"]),
            "total_read_sites": len(scan["sites"]),
            "live_reader_faces": len(live),
            "skipped_dir_names": sorted(e446.SKIP_DIRS),
            "max_bytes_per_file": e446.MAX_BYTES,
        },
    }

    return {
        "study": "E452_which_harness_open_of_an_abandoned_base_is_unguarded",
        "card": "E452-WHICH-HARNESS-OPEN-OF-AN-ABANDONED-BASE-IS-UNGUARDED",
        "title": "of the reads E447 found under an abandoned base whose reader a harness launches, "
                 "which open is guarded and which artifact is gone today",
        "evidence_cutoff": cutoff or date.today().isoformat(),
        "generated": date.today().isoformat(),
        "source_face": "results/state_tilt/" + SOURCE_FACE,
        "class_vocab": list(CLASSES),
        "guard_vocab": list(GUARD_SHAPES),
        "verdict": verdict_for(all_sites),
        "summary": summary,
        "rows": rows,
        "method_limits": [
            "the population is E447's abandoned_but_still_read bases that have at least one live "
            "reader, re-walked from the live corpus with E447's own scan so the site set is not "
            "limited by E447's 25-sites-per-base publication cap",
            "a site is graded live exactly as E447 grades liveness (smoke leg / chain leg / task "
            "referenced / __main__ runnable); face-writing censuses and unlaunched libraries are "
            "out of this population",
            "guard shapes counted: try_except (the call sits in a try body), "
            "existence_test_in_the_enclosing_test (an if/if-exp/boolean test names an exists() of "
            "the same expression, with polarity matched to the branch the call sits in), "
            "conditional_default (the call is the body of an if-exp with an else), and "
            "existence_test_earlier_in_the_enclosing_function (a negative existence test on the "
            "same expression appears lexically earlier in the same function)",
            "guard detection is lexical, not a control-flow proof: a guard one call away (in a "
            "caller or a wrapper helper) is not credited, and a negative test earlier in the "
            "function is credited whether or not every path reaches it",
            "the path expression is compared by source text (whitespace stripped), so an exists() "
            "that tests a differently spelled alias of the same value is not credited",
            "artifact_present is os.path.exists on the resolved repo-relative target today; a site "
            "whose target is only a literal tail (unresolved head) is classed "
            "target_not_statically_resolvable and never counted as gone",
            "a shared-resolver reading that stopped early (fstring_head / unresolved / bare_name) is "
            "not a path: those sites are re-resolved locally with the f-string completed when every "
            "part names a module constant, and the site publishes resolution=completed_fstring plus "
            "the shared reading it replaces; sites where the completion fails keep "
            "resolution=unresolved and are never counted as gone",
        ],
    }


def write_face(face: dict) -> str:
    os.makedirs(OUTDIR, exist_ok=True)
    dated = os.path.join(OUTDIR, "%s-%s.json" % (DATED_PREFIX, face["evidence_cutoff"]))
    latest = os.path.join(OUTDIR, FACE_NAME)
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    for path in (dated, latest):
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body + "\n")
    return dated


# ----------------------------------------------------------------------------- check / verify


def _sites_of(face: dict) -> list[dict]:
    return [s for r in face["rows"] for s in r["sites"]]


def tally_problems(face: dict) -> list[str]:
    problems: list[str] = []
    sites = _sites_of(face)
    s = face["summary"]
    if len(sites) != s["sites_graded"]:
        problems.append("site rows %d != summary %d" % (len(sites), s["sites_graded"]))
    recomputed = {c: sum(1 for x in sites if x["class"] == c) for c in CLASSES}
    if recomputed != s["class_counts"]:
        problems.append("class_counts %s != recomputed %s" % (s["class_counts"], recomputed))
    for x in sites:
        want = classify(x["guard_shapes"], x["artifact_present"])
        if x["class"] != want:
            problems.append("%s:%s class %r does not re-derive (%r)"
                            % (x["face"], x["line"], x["class"], want))
        if bool(x["guard_shapes"]) != bool(x["guarded"]):
            problems.append("%s:%s guarded flag disagrees with its shapes"
                            % (x["face"], x["line"]))
        if x["resolution"] == "unresolved" and x["class"] != C_UNRESOLVED:
            problems.append("%s:%s unresolved target graded %r"
                            % (x["face"], x["line"], x["class"]))
        if x["resolution"] != "unresolved" and not x["resolved_path"]:
            problems.append("%s:%s %s resolution carries no path"
                            % (x["face"], x["line"], x["resolution"]))
        if x["resolution"] == "shared_resolver" and x["resolved_path"] != x["shared_resolver_path"]:
            problems.append("%s:%s shared reading was rewritten" % (x["face"], x["line"]))
    for r, n in s["resolution_counts"].items():
        if sum(1 for x in sites if x["resolution"] == r) != n:
            problems.append("resolution_counts[%s] does not re-add" % r)
    mism = ["%s:%d" % (x["face"], x["line"]) for x in sites
            if x["resolution"] == "shared_resolver" and x["resolved_path"] != x["shared_resolver_path"]]
    if mism != s["shared_resolver_mismatches"]:
        problems.append("shared_resolver_mismatches does not re-add")
    if sum(1 for x in sites if x["guarded"]) != s["guarded_sites"]:
        problems.append("guarded_sites does not re-add")
    if sum(1 for x in sites if x["artifact_present"] is True) != s["artifact_present_counts"]["present"]:
        problems.append("present count does not re-add")
    if sum(1 for x in sites if x["artifact_present"] is False) != s["artifact_present_counts"]["gone"]:
        problems.append("gone count does not re-add")
    if len({x["face"] for x in sites}) != s["distinct_reader_faces"]:
        problems.append("distinct_reader_faces does not re-add")
    for row in face["rows"]:
        rc = {c: sum(1 for x in row["sites"] if x["class"] == c) for c in CLASSES}
        if rc != row["class_counts"]:
            problems.append("row %s class_counts does not re-add" % row["base"])
        if row["site_count"] != len(row["sites"]):
            problems.append("row %s site_count %d != %d"
                            % (row["base"], row["site_count"], len(row["sites"])))
    if face["verdict"] != verdict_for(sites):
        problems.append("verdict %r does not re-derive (%r)"
                        % (face["verdict"], verdict_for(sites)))
    return problems


def verify(face: dict | None = None, root: str | None = None) -> list[str]:
    face = face if face is not None else _load(os.path.join(OUTDIR, FACE_NAME))
    fresh = build(cutoff=face["evidence_cutoff"], root=root)
    problems = tally_problems(fresh)
    old = {(s["face"], s["line"]): s for s in _sites_of(face)}
    new = {(s["face"], s["line"]): s for s in _sites_of(fresh)}
    if set(old) != set(new):
        gone = sorted(set(old) - set(new))[:5]
        added = sorted(set(new) - set(old))[:5]
        problems.append("site population moved: -%s +%s" % (gone, added))
    for key in sorted(set(old) & set(new)):
        a, b = old[key], new[key]
        if a["class"] != b["class"]:
            problems.append("%s:%s class %s -> %s" % (key[0], key[1], a["class"], b["class"]))
        if a["resolved_path"] != b["resolved_path"]:
            problems.append("%s:%s target %s -> %s"
                            % (key[0], key[1], a["resolved_path"], b["resolved_path"]))
        if a["resolution"] != b["resolution"]:
            problems.append("%s:%s resolution %s -> %s"
                            % (key[0], key[1], a["resolution"], b["resolution"]))
        if a["artifact_present"] != b["artifact_present"]:
            problems.append("%s:%s artifact_present %s -> %s"
                            % (key[0], key[1], a["artifact_present"], b["artifact_present"]))
        if a["guard_shapes"] != b["guard_shapes"]:
            problems.append("%s:%s guard shapes %s -> %s"
                            % (key[0], key[1], a["guard_shapes"], b["guard_shapes"]))
    if face["verdict"] != fresh["verdict"]:
        problems.append("verdict moved %r -> %r" % (face["verdict"], fresh["verdict"]))
    return problems


# ----------------------------------------------------------------------------- selftest


def _guards_of(src: str, line: int, kind: str = "open") -> list[str]:
    tree = ast.parse(src)
    cache = {"scripts/x.py": (src, tree, _parents(tree))}
    shapes, _, _ = guard_shapes("scripts/x.py", line, kind, cache)
    return shapes


def selftest() -> int:
    bad: list[str] = []

    def check(name: str, ok: bool) -> None:
        if not ok:
            bad.append(name)

    # 1 try/except around the open
    src = ('try:\n    fh = open("results/fx/a.json")\nexcept OSError:\n    fh = None\n')
    check("a try body is a try_except guard", G_TRY in _guards_of(src, 2))

    # 2 positive existence test on the same expression, call inside the if body
    src = ('import os\nif os.path.exists("results/fx/a.json"):\n'
           '    open("results/fx/a.json")\n')
    check("an existence test guards the then-branch", G_EXISTS in _guards_of(src, 3))

    # 3 a negated test guards the else-branch
    src = ('import os\nif not os.path.exists("results/fx/a.json"):\n    pass\n'
           'else:\n    open("results/fx/a.json")\n')
    check("a negated test guards the else-branch", G_EXISTS in _guards_of(src, 5))

    # 4 polarity matters: a positive test must not guard the else-branch
    src = ('import os\nif os.path.exists("results/fx/a.json"):\n    pass\n'
           'else:\n    open("results/fx/a.json")\n')
    check("a positive test does not guard the else-branch", G_EXISTS not in _guards_of(src, 5))

    # 5 the test must name the same expression
    src = ('import os\nif os.path.exists("results/other.json"):\n'
           '    open("results/fx/a.json")\n')
    check("an unrelated existence test is not a guard", _guards_of(src, 3) == [])

    # 6 conditional default
    src = ('data = open("results/fx/a.json").read() if True else ""\n')
    check("an if-exp with an else is a conditional_default", G_DEFAULT in _guards_of(src, 1))

    # 7 negative test earlier in the enclosing function
    src = ('import os\ndef load():\n    if not os.path.isfile("results/fx/a.json"):\n'
           '        return {}\n    return open("results/fx/a.json")\n')
    check("an earlier negative test is credited lexically",
          G_EXISTS_FN in _guards_of(src, 5))

    # 8 nothing guards a bare open
    src = 'open("results/fx/a.json")\n'
    check("a bare open has no guard", _guards_of(src, 1) == [])

    # 9 classification and precedence
    check("unguarded + gone is the raising class",
          classify([], False) == C_GONE)
    check("unguarded + present is the present class",
          classify([], True) == C_PRESENT)
    check("guarded wins over presence", classify([G_TRY], False) == C_GUARDED)
    check("an unresolvable target is its own class",
          classify([], None) == C_UNRESOLVED)
    check("artifact_present: a literal tail is not a path", artifact_present("?reports/x.md") is None)
    check("artifact_present: a real file is present",
          artifact_present("scripts/e452_abandoned_guard.py") is True)
    check("artifact_present: a missing file is gone",
          artifact_present("results/__no_such_face__.json") is False)

    # 10 verdict precedence
    gone = {"class": C_GONE}
    present = {"class": C_PRESENT}
    guarded = {"class": C_GUARDED}
    unresolved = {"class": C_UNRESOLVED}
    check("verdict: a gone unguarded site wins",
          verdict_for([guarded, present, gone]) == "at_least_one_harness_open_would_raise_today")
    check("verdict: present unguarded is its own reading",
          verdict_for([guarded, present]) == "every_unguarded_harness_open_still_finds_its_artifact")
    check("verdict: all guarded",
          verdict_for([guarded]) == "every_harness_open_of_an_abandoned_base_is_guarded")
    check("verdict: unresolved is not called guarded",
          verdict_for([unresolved]) == "no_unguarded_open_is_statically_resolvable")
    check("verdict: empty population",
          verdict_for([]) == "empty_population")

    # 11 a truncated shared reading is completed, and says so
    src = ('import os\nROOT = "."\nPIN = "2026-10-09"\n'
           'P = os.path.join(ROOT, "results", "t23", f"CENSUS-{PIN}.json")\nopen(P)\n')
    tree = ast.parse(src)
    shared = e446.module_constants(tree, "scripts/x.py")
    strict = strict_consts(tree, "scripts/x.py")
    check("the shared constant reading is truncated",
          str(shared.get("P", "")).endswith("CENSUS-"))
    check("the strict reading completes the f-string",
          str(strict.get("P", "")).endswith("CENSUS-2026-10-09.json"))
    call = [n for n in ast.walk(tree)
            if isinstance(n, ast.Call) and _call_kind(n) == "open"][0]
    value, resolution, _how = resolve_for_site(
        "scripts/x.py", _path_expr(call), tree, shared, strict)
    check("a completed reading is published as completed_fstring",
          resolution == "completed_fstring" and str(value).endswith("CENSUS-2026-10-09.json"))
    check("a partial how is recognised", how_is_partial("fstring_head") is True
          and how_is_partial("constant:P") is False)

    # 12 the study's own faces are never population
    check("own latest face is excluded", is_own_output("results/state_tilt/" + FACE_NAME))
    check("own dated face is excluded",
          is_own_output("results/state_tilt/%s-2026-11-06.json" % DATED_PREFIX))
    check("a sibling face is not excluded",
          not is_own_output("results/state_tilt/abandonedread_latest.json"))

    total = 27
    if bad:
        print("selftest FAIL %d/%d" % (len(bad), total))
        for b in bad:
            print("  -", b)
        return 1
    print("selftest %d/%d PASS" % (total, total))
    return 0


# ----------------------------------------------------------------------------- cli


def main(argv: list[str]) -> int:
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        face = build()
        path = write_face(face)
        s = face["summary"]
        print("wrote %s" % _rel(path))
        print("bases %d | sites %d | class %s"
              % (s["bases_with_a_live_reader"], s["sites_graded"],
                 json.dumps(s["class_counts"])))
        print("guarded %d | unguarded %d | guard shapes %s | presence %s"
              % (s["guarded_sites"], s["unguarded_sites"],
                 json.dumps(s["guard_shape_counts"]),
                 json.dumps(s["artifact_present_counts"])))
        print("verdict: %s" % face["verdict"])
        return 0
    if cmd == "check":
        face = _load(os.path.join(OUTDIR, FACE_NAME))
        problems = tally_problems(face)
        print("problems=%s" % json.dumps(problems, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "verify":
        problems = verify()
        print("problems=%s" % json.dumps(problems, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "selftest":
        return selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))