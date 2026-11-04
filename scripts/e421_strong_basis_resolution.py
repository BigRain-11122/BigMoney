"""E421 - a face name that resolves to no file: is it a face the tree lacks, or a temp-dir fixture?

E406 named 58 faces from blob readers; 32 of those names resolved to no file and one resolved
to no file *at HEAD*. E412 then priced the 25 it could measure and disclosed that every one of
them carries the WEAK attribution basis (`module_face_literal`: the module's whole face list is
repeated on every call site, so a site arrives carrying a face it never touches), which left the
implication that the strong-basis names might behave differently.

This study answers the resolution question directly instead of by basis: for each unresolved
name, find the literal sites that spell it and ask **what directory the literal is joined
against**. A selftest that builds a fixture tree under `tempfile.mkdtemp()` spells
`results/A/B-2026-01-01.json` verbatim -- repo-shaped, and a temp path. The name shape is not the
resolution; the join is.

Read-only: no reader, leg or face is edited.

Usage:
    python scripts/e421_strong_basis_resolution.py run|verify|selftest
"""
from __future__ import annotations

import ast
import io
import json
import os
import re
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ST = os.path.join(ROOT, "results", "state_tilt")
E406 = os.path.join(ST, "blobread_latest.json")
CAL = os.path.join(ROOT, "data", "exchange_calendar.csv")
OUTDIR = ST

# The verdict vocabulary is frozen: the smoke leg refuses a published value outside it.
V_FIXTURE = "resolves_inside_a_selftest_temp_dir"
V_REPO_MISSING = "joined_into_the_repo_and_the_file_is_not_there"
V_REPO_PRESENT = "joined_into_the_repo_and_the_file_is_there"
V_ABSENT_AT_HEAD = "on_disk_but_absent_at_HEAD"
V_SPELLED = "the_reader_spells_a_repo_path_the_file_exists_at"
V_ELSEWHERE = "the_basename_exists_in_another_directory_than_the_census_recorded"
V_LITERAL_ONLY = "literal_with_no_join_resolved"
V_CENSUS_SELF = "named_only_by_the_census_own_selftest"
VERDICT_VOCAB = {V_FIXTURE, V_REPO_MISSING, V_REPO_PRESENT, V_ABSENT_AT_HEAD, V_SPELLED,
                 V_ELSEWHERE, V_LITERAL_ONLY, V_CENSUS_SELF}
# The census that produced the population. A name whose only sites are inside this file is not a
# face: it is a string the census's own selftest parses (E180/E207/E330 self-inclusion family).
CENSUS_MODULE = "scripts/e406_blob_vs_tree_readers.py"
# This study's own selftest spells the names it is resolving, so it must be outside its own
# candidate set -- otherwise the first burn makes three census-self names look like repo reads
# (E180/E207/E330 family, fourth recurrence; published as a count, not silently dropped).
SELF_MODULE = "scripts/e421_strong_basis_resolution.py"

TEMP_CALLS = {"mkdtemp", "mkstemp", "TemporaryDirectory", "gettempdir", "mkdtemp_", "tempdir"}
JOIN_CALLS = {"join", "joinpath", "Path", "PurePath"}
WRITE_CALLS = {"open", "write_text", "write_bytes", "dump", "makedirs", "mkdir"}
MUTATORS = {"append", "extend", "add", "insert", "setdefault", "update"}
REPO_PREFIX = ("results/", "docs/", "data/", "research/", "knowledge/", "fleet/", "state/")


def _rel(path: str) -> str:
    return os.path.relpath(os.path.abspath(path), ROOT).replace("\\", "/")


def _load(path: str) -> dict:
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _median(values):
    vals = sorted(values)
    if not vals:
        return None
    n = len(vals)
    return float(vals[n // 2]) if n % 2 else (vals[n // 2 - 1] + vals[n // 2]) / 2.0


# ---------------------------------------------------------------- module corpus


def module_texts() -> dict[str, str]:
    out = {}
    for base in ("scripts", "Tools"):
        for dirpath, dirnames, filenames in os.walk(os.path.join(ROOT, base)):
            dirnames[:] = [d for d in dirnames if d != "__pycache__"]
            for name in filenames:
                if not name.endswith(".py"):
                    continue
                full = os.path.join(dirpath, name)
                rel = _rel(full)
                if rel == SELF_MODULE:
                    continue
                try:
                    with io.open(full, encoding="utf-8", errors="replace") as fh:
                        out[rel] = fh.read()
                except OSError:
                    continue
    return out


# ---------------------------------------------------------------- taint machinery


def _const_strings(node) -> list[str]:
    return [s.value for s in ast.walk(node)
            if isinstance(s, ast.Constant) and isinstance(s.value, str)]


def _spells(node, base: str) -> bool:
    """A literal that IS the name, or a path ending in `/name`. Never a suffix of a longer name.

    `endswith(base)` is not this test: it reads `delta_latest.json` out of `keydelta_latest.json`
    and then reports a face the tree never had (E330 family, quote-adjacency not substring).
    """
    for s in _const_strings(node):
        if s == base or s.endswith("/" + base):
            return True
    return False


def _mentions(node, base: str) -> bool:
    return _spells(node, base)


def _names(node) -> set[str]:
    return {s.id for s in ast.walk(node) if isinstance(s, ast.Name)}


def _target_names(node) -> set[str]:
    out = set()
    for sub in ast.walk(node):
        if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Store):
            out.add(sub.id)
    return out


def _call_name(node) -> str:
    if not isinstance(node, ast.Call):
        return ""
    return getattr(node.func, "id", None) or getattr(node.func, "attr", None) or ""


def _is_temp_call(node) -> bool:
    if not isinstance(node, ast.Call):
        return False
    name = _call_name(node)
    if name in TEMP_CALLS:
        return True
    # pathlib.Path(tempfile.gettempdir()) / ... and friends
    return any(_call_name(sub) in TEMP_CALLS for sub in ast.walk(node) if isinstance(sub, ast.Call))


def _taint(nodes, base: str, face_seed: dict, temp_seed: dict):
    """Two fixpoints over one scope: names carrying the face, names carrying a temp root."""
    face = dict(face_seed)
    temp = dict(temp_seed)
    changed = True
    while changed:
        changed = False
        for node in nodes:
            if isinstance(node, (ast.Assign, ast.AnnAssign)) and node.value is not None:
                value = node.value
                has_face = _mentions(value, base) or (_names(value) & set(face))
                has_temp = _is_temp_call(value) or (_is_temp_call_in_args(value)) \
                    or (_names(value) & set(temp))
                for target in _target_names(node):
                    if has_face and target not in face:
                        face[target] = node.lineno
                        changed = True
                    if has_temp and target not in temp:
                        temp[target] = node.lineno
                        changed = True
            elif isinstance(node, ast.For):
                it = node.iter
                has_face = _mentions(it, base) or (_names(it) & set(face))
                has_temp = _names(it) & set(temp)
                for target in _target_names(node):
                    if has_face and target not in face:
                        face[target] = node.lineno
                        changed = True
                    if has_temp and target not in temp:
                        temp[target] = node.lineno
                        changed = True
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                    and node.func.attr in MUTATORS:
                recv = getattr(node.func.value, "id", None)
                if recv and (_mentions(node, base) or (_names(node) & set(face))) \
                        and recv not in face:
                    face[recv] = node.lineno
                    changed = True
    return face, temp


def _is_temp_call_in_args(node) -> bool:
    return any(_is_temp_call(sub) for sub in ast.walk(node) if isinstance(sub, ast.Call))


def _join_sites(nodes, base: str, face: dict, temp: dict) -> list[dict]:
    """Every call in this scope that either joins the face or opens/writes it."""
    out = []
    for node in nodes:
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node)
        if name not in JOIN_CALLS and name not in WRITE_CALLS:
            continue
        args = list(node.args) + [k.value for k in node.keywords]
        carries_face = any(_mentions(a, base) or (_names(a) & set(face)) for a in args)
        if not carries_face:
            continue
        carries_temp = any(_names(a) & set(temp) for a in args)
        if name in JOIN_CALLS and carries_temp:
            kind = "temp_join"
        elif name in JOIN_CALLS:
            kind = "join"
        elif carries_temp:
            kind = "temp_join"
        else:
            kind = "open"
        out.append({"line": node.lineno, "kind": kind, "callee": name})
    return out


def _scopes(tree):
    yield "module", list(ast.walk(tree))
    for fn in ast.walk(tree):
        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield fn.name, list(ast.walk(fn))


def sites_for(base: str, texts: dict[str, str], cache: dict) -> list[dict]:
    """Every literal site that spells this basename, with the join shape it sits in."""
    out = []
    for rel in sorted(texts):
        text = texts[rel]
        if base not in text:
            continue
        if ("tree", rel) not in cache:
            try:
                cache[("tree", rel)] = ast.parse(text)
            except SyntaxError:
                cache[("tree", rel)] = None
        tree = cache[("tree", rel)]
        if tree is None:
            continue
        if not _spells(tree, base):
            continue
        module_face: dict = {}
        module_temp: dict = {}
        # module scope first, so constants defined at module level reach the functions
        module_face, module_temp = _taint(list(ast.walk(tree)), base, {}, {})
        for scope, nodes in _scopes(tree):
            face, temp = _taint(nodes, base, module_face, module_temp)
            literal_lines = sorted({n.lineno for n in ast.walk(tree)
                                    if isinstance(n, ast.Constant) and isinstance(n.value, str)
                                    and (n.value == base or n.value.endswith("/" + base))})
            joins = _join_sites(nodes, base, face, temp)
            if not literal_lines and not joins:
                continue
            # A site is the literal line plus every join/open in that scope that carries it;
            # the scope is the attribution unit because a fixture path crosses several lines.
            out.append({
                "module": rel,
                "scope": scope,
                "lines": literal_lines[:6],
                "joins": sorted({(j["line"], j["kind"]) for j in joins}),
                "kinds": sorted({j["kind"] for j in joins}),
                "repo_shaped": any((s == base or s.endswith("/" + base)) and s.startswith(REPO_PREFIX)
                                   for s in _const_strings(tree)),
                "literal_paths": sorted({s for s in _const_strings(tree)
                                         if (s == base or s.endswith("/" + base))
                                         and s.startswith(REPO_PREFIX)}),
                "temp_names": sorted(temp)[:6],
            })
    return out


def repo_shaped(base: str, sites: list[dict]) -> bool:
    """Does any site spell the name as a repo-relative path rather than a bare basename?"""
    return any(s.get("repo_shaped") for s in sites)


def stem_of(base: str) -> str:
    stem = base.rsplit(".", 1)[0]
    m = re.match(r"([A-Za-z][A-Za-z0-9]*)", stem)
    return m.group(1) if m else stem


def stem_siblings(base: str, limit: int = 4000) -> list[str]:
    """Files on disk whose name starts with the same alphabetic stem. NOT a resolution."""
    want = stem_of(base)
    hits = []
    for dirpath, dirnames, filenames in os.walk(os.path.join(ROOT, "results")):
        dirnames[:] = [d for d in dirnames if d not in ("_quarantine", "__pycache__")]
        for name in filenames:
            if name.startswith(want + "-") or name.startswith(want + "_"):
                hits.append(_rel(os.path.join(dirpath, name)))
                if len(hits) >= limit:
                    return sorted(hits)
    return sorted(hits)


# ---------------------------------------------------------------- classification


def classify(site_kinds: set[str], on_disk: bool, at_head: bool, shaped: bool,
             spelled: list[str] | None = None, elsewhere: list[str] | None = None,
             census_only: bool = False) -> str:
    """Frozen rule, ordered by evidence strength.

    A file at the path the census recorded is a fact about that path, so it outranks every
    reading taken from some *other* site that happens to spell the same basename -- a later
    round's script or a selftest fixture reusing a real face's name is not evidence about the
    face. Below that, a literal the reader itself spells and the file exists at is the strongest
    resolution; a basename that exists in another directory is next (the census path was
    wrong, not the file); a temp-directory join means only a selftest ever writes it.
    """
    spelled = spelled or []
    elsewhere = elsewhere or []
    if on_disk:
        return V_REPO_PRESENT if at_head else V_ABSENT_AT_HEAD
    if spelled:
        return V_SPELLED
    if elsewhere:
        return V_ELSEWHERE
    if census_only:
        return V_CENSUS_SELF
    if "temp_join" in site_kinds:
        return V_FIXTURE
    if site_kinds & {"join", "open"}:
        return V_REPO_MISSING
    if shaped:
        return V_REPO_MISSING
    return V_LITERAL_ONLY


def _repo_files_named(base: str, limit: int = 40) -> list[str]:
    """Every tracked-or-on-disk repo file whose basename is exactly this name."""
    hits = []
    for top in ("results", "docs", "data", "research", "knowledge", "fleet", "state", "scripts"):
        root = os.path.join(ROOT, top)
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in ("_quarantine", "__pycache__")]
            if base in filenames:
                hits.append(_rel(os.path.join(dirpath, base)))
                if len(hits) >= limit:
                    return sorted(hits)
    return sorted(hits)


def build(cutoff: str | None = None) -> dict:
    if not os.path.exists(E406):
        raise SystemExit("E406's population face is missing: %s" % _rel(E406))
    source = _load(E406)
    if source.get("study") != "E406_blob_vs_tree_readers":
        raise SystemExit("the population face is not E406's: %r" % source.get("study"))
    cutoff = cutoff or min(_last_bar(), date.today().isoformat())
    texts = module_texts()
    cache: dict = {}
    head_files = _head_paths()

    rows = []
    for face in source.get("faces") or []:
        base = face.get("face_name") or os.path.basename(face.get("face") or "")
        if not base:
            continue
        rel = face.get("face") or ""
        on_disk = bool(rel) and os.path.exists(os.path.join(ROOT, rel)) and "%s" not in rel
        at_head = rel in head_files if rel else False
        sites = sites_for(base, texts, cache)
        kinds = {k for s in sites for k in s["kinds"]}
        shaped = repo_shaped(base, sites)
        literal_paths = sorted({p for s in sites for p in s.get("literal_paths") or []})
        spelled = [p for p in literal_paths if os.path.exists(os.path.join(ROOT, p))]
        elsewhere = [] if (on_disk or spelled) else _repo_files_named(base)
        modules = sorted({s["module"] for s in sites})
        census_only = bool(modules) and modules == [CENSUS_MODULE]
        verdict = classify(kinds, on_disk, at_head, shaped, spelled, elsewhere, census_only)
        siblings = [] if verdict == V_FIXTURE else stem_siblings(base)[:5]
        rows.append({
            "face": rel,
            "face_name": base,
            "source_state": face.get("state"),
            "source_basis": face.get("basis"),
            "read_by": face.get("read_by") or [],
            "on_disk": on_disk,
            "at_head": at_head,
            "repo_shaped_literal": shaped,
            "literal_paths": literal_paths,
            "literal_paths_on_disk": spelled,
            "same_basename_elsewhere": elsewhere[:6],
            "site_count": len(sites),
            "site_modules": sorted({s["module"] for s in sites}),
            "site_scope": sorted({s["module"] + "::" + s["scope"] for s in sites})[:4],
            "join_kinds": sorted(kinds),
            "sites": sites[:4],
            "stem_siblings": siblings,
            "verdict": verdict,
        })

    unresolved = [r for r in rows if r["source_state"] != "compared"]
    control = [r for r in rows if r["source_state"] == "compared"]

    def tally(rs):
        out: dict[str, int] = {}
        for r in rs:
            out[r["verdict"]] = out.get(r["verdict"], 0) + 1
        return out

    by_verdict = tally(rows)
    weak = [r for r in unresolved if r["source_basis"] == "module_face_literal"]
    strong = [r for r in unresolved if r["source_basis"] != "module_face_literal"]
    control_fixture = [r for r in control if r["verdict"] == V_FIXTURE]

    summary = {
        "faces_in_population": len(rows),
        "faces_unresolved_in_e406": len(unresolved),
        "faces_in_the_control_arm": len(control),
        "unresolved_by_source_state": _count(unresolved, "source_state"),
        "unresolved_by_basis": _count(unresolved, "source_basis"),
        "weak_basis_unresolved": len(weak),
        "strong_basis_unresolved": len(strong),
        "strong_basis_names": [r["face_name"] for r in strong],
        "strong_basis_resolving_to_a_fixture": sum(1 for r in strong if r["verdict"] == V_FIXTURE),
        "strong_basis_resolving_to_a_file": sum(1 for r in strong if r["verdict"] in
                                                (V_REPO_PRESENT, V_ABSENT_AT_HEAD)),
        "weak_basis_resolving_to_a_fixture": sum(1 for r in weak if r["verdict"] == V_FIXTURE),
        "weak_basis_resolving_to_a_file": sum(1 for r in weak if r["verdict"] in
                                              (V_REPO_PRESENT, V_ABSENT_AT_HEAD)),
        "by_verdict": by_verdict,
        "by_verdict_unresolved": tally(unresolved),
        "by_verdict_control": tally(control),
        "unresolved_joined_into_a_temp_dir": sum(1 for r in unresolved if r["verdict"] == V_FIXTURE),
        "unresolved_joined_into_the_repo_and_missing": sum(
            1 for r in unresolved if r["verdict"] == V_REPO_MISSING),
        "unresolved_resolving_at_the_spelled_path": sum(
            1 for r in unresolved if r["verdict"] == V_SPELLED),
        "unresolved_resolving_under_another_directory": sum(
            1 for r in unresolved if r["verdict"] == V_ELSEWHERE),
        "unresolved_with_no_join_at_all": sum(1 for r in unresolved if r["verdict"] == V_LITERAL_ONLY),
        "unresolved_named_only_by_the_census_own_selftest": sum(
            1 for r in unresolved if r["verdict"] == V_CENSUS_SELF),
        "unresolved_resolving_to_a_file_somewhere": sum(
            1 for r in unresolved if r["verdict"] in (V_SPELLED, V_ELSEWHERE, V_ABSENT_AT_HEAD)),
        "unresolved_directories_the_readers_actually_spell": _dirs(
            [p for r in unresolved for p in r["literal_paths_on_disk"]]),
        "unresolved_census_directory": _dirs([r["face"] for r in unresolved]),
        "unresolved_whose_literal_is_repo_shaped": sum(
            1 for r in unresolved if r["repo_shaped_literal"]),
        "unresolved_with_a_site_in_the_tree": sum(1 for r in unresolved if r["site_count"]),
        "unresolved_with_no_site_in_the_tree": sum(1 for r in unresolved if not r["site_count"]),
        "unresolved_carrying_a_stem_sibling": sum(
            1 for r in unresolved if r["stem_siblings"]),
        "control_resolving_to_a_temp_dir": len(control_fixture),
        "control_resolving_to_a_file": sum(
            1 for r in control if r["verdict"] in (V_REPO_PRESENT, V_ABSENT_AT_HEAD)),
        "classifier_discriminates": len(control_fixture) == 0
                                    and all(r["verdict"] in (V_REPO_PRESENT, V_ABSENT_AT_HEAD)
                                            for r in control),
        "census_module": CENSUS_MODULE,
        "self_excluded": SELF_MODULE,
        "self_excluded_in_corpus": SELF_MODULE not in texts,
    }
    verdict = _verdict(summary)
    return {
        "study": "E421_a_name_that_resolves_to_no_file_is_a_join_not_a_basis",
        "card": "E413-DOES-THE-STRONG-BASIS-FACE-NAME-RESOLVE-TO-A-FILE",
        "title": "the 33 names E406 could not resolve, resolved by the directory their literal is joined against",
        "evidence_cutoff": cutoff,
        "source_face": "results/state_tilt/blobread_latest.json",
        "source_study": source.get("study"),
        "source_rev": source.get("rev"),
        "rule": {
            "population": "every face E406 named from a blob reader (58): 33 unresolved + 25 compared as a control arm",
            "resolution": "a name resolves when the literal at its site is joined against a repo root; a name "
                          "that is only ever joined against a tempfile.mkdtemp() root is a selftest fixture",
            "temp_taint": "a name carries a temp root when it is assigned from tempfile.mkdtemp / "
                          "TemporaryDirectory / mkstemp, or from a join one of whose arguments carries one",
            "face_taint": "a name carries the face when it is assigned from, loop-bound over, or built out of a "
                          "literal that spells the basename",
            "verdict_order": "temp_join > on_disk > repo join > repo-shaped literal > literal only",
            "stem_arm": "a sibling with the same alphabetic stem is published and is NOT counted as resolution: "
                        "a fixture name and the family it copies share a stem",
            "no_rewrite": "no reader, leg or face is edited by this study",
            "self_exclusion": SELF_MODULE + " is removed from the candidate corpus: this study's own "
                                           "selftest spells the names it resolves",
        },
        "summary": summary,
        # A corpus size is a fact about the tree, not a measurement of it: it grows by construction
        # every round a script is added, so it lives outside the summary that the smoke leg pins by
        # equality (E420's law, met again in this very study's first publish).
        "corpus": {"modules_read": len(texts), "self_excluded": SELF_MODULE not in texts,
                   "census_module": CENSUS_MODULE},
        "rows": sorted(rows, key=lambda r: (r["source_state"] == "compared", r["face_name"])),
        "verdict": verdict,
    }


def _count(rows, key) -> dict:
    out: dict[str, int] = {}
    for r in rows:
        out[str(r.get(key))] = out.get(str(r.get(key)), 0) + 1
    return out


def _dirs(paths) -> dict:
    out: dict[str, int] = {}
    for p in paths:
        if not p:
            continue
        d = os.path.dirname(p.replace("\\", "/")) or "."
        out[d] = out.get(d, 0) + 1
    return out


def _verdict(s: dict) -> str:
    g = lambda k: s.get(k) or 0  # noqa: E731
    if not g("unresolved_with_a_site_in_the_tree"):
        return "the_unresolved_names_have_no_site_the_census_can_find_so_resolution_is_unanswerable"
    n = g("faces_unresolved_in_e406")
    at_temp = g("unresolved_joined_into_a_temp_dir")
    by_u = s.get("by_verdict_unresolved") or {}
    under_repo = g("unresolved_resolving_at_the_spelled_path") \
        + g("unresolved_resolving_under_another_directory") \
        + g("unresolved_with_no_join_at_all") \
        + g("unresolved_named_only_by_the_census_own_selftest") \
        + (1 if by_u.get(V_REPO_PRESENT) else 0) \
        + (1 if by_u.get(V_ABSENT_AT_HEAD) else 0)
    missing = g("unresolved_joined_into_the_repo_and_missing")
    if missing == 0 and under_repo + at_temp == n:
        return ("no unresolved name is a face the tree reads and lacks: %d resolve to a file the "
                "reader itself spells, %d exist under another directory than the census recorded, "
                "%d are on disk, %d are written only into a selftest temp dir, and %d are named only "
                "by the census's own selftest" % (
                    g("unresolved_resolving_at_the_spelled_path"),
                    g("unresolved_resolving_under_another_directory"),
                    (1 if by_u.get(V_REPO_PRESENT) else 0) + (1 if by_u.get(V_ABSENT_AT_HEAD) else 0),
                    at_temp,
                    g("unresolved_named_only_by_the_census_own_selftest")))
    if missing:
        return ("%d of %d unresolved names are joined into the repo and the tree does not hold them"
                % (missing, n))
    return "the_unresolved_names_resolve_outside_the_recorded_path_and_basis_does_not_predict_which"


def _last_bar() -> str:
    try:
        with io.open(CAL, encoding="utf-8") as fh:
            bars = [ln.strip() for ln in fh if ln.strip()]
        return bars[-1] if bars else date.today().isoformat()
    except OSError:
        return date.today().isoformat()


def _head_paths() -> set[str]:
    import subprocess
    try:
        out = subprocess.run(["git", "ls-tree", "-r", "--name-only", "-z", "HEAD"],
                             cwd=ROOT, capture_output=True, check=False)
        if out.returncode != 0:
            return set()
        return {p for p in out.stdout.decode("utf-8", "replace").split("\0") if p}
    except OSError:
        return set()


# ---------------------------------------------------------------- verify / publish


def verify() -> list[str]:
    problems = []
    path = os.path.join(OUTDIR, "nameresolve_latest.json")
    if not os.path.exists(path):
        return ["face missing: %s" % _rel(path)]
    face = _load(path)
    rows = face["rows"]
    s = face["summary"]
    if s["faces_in_population"] != len(rows):
        problems.append("population count does not re-derive from rows")
    unresolved = [r for r in rows if r["source_state"] != "compared"]
    control = [r for r in rows if r["source_state"] == "compared"]
    if s["faces_unresolved_in_e406"] != len(unresolved):
        problems.append("unresolved count does not re-derive")
    if s["faces_in_the_control_arm"] != len(control):
        problems.append("control count does not re-derive")
    recomputed: dict[str, int] = {}
    for r in rows:
        recomputed[r["verdict"]] = recomputed.get(r["verdict"], 0) + 1
    if recomputed != s["by_verdict"]:
        problems.append("by_verdict does not re-derive: %s" % recomputed)
    for name, subset in (("by_verdict_unresolved", unresolved), ("by_verdict_control", control)):
        got: dict[str, int] = {}
        for r in subset:
            got[r["verdict"]] = got.get(r["verdict"], 0) + 1
        if got != s[name]:
            problems.append("%s does not re-derive: %s" % (name, got))
    if s["weak_basis_unresolved"] + s["strong_basis_unresolved"] != len(unresolved):
        problems.append("basis split does not add up to the unresolved population")
    if s["unresolved_joined_into_a_temp_dir"] + s["unresolved_joined_into_the_repo_and_missing"] \
            + s["unresolved_with_no_join_at_all"] > len(unresolved):
        problems.append("unresolved verdict counts exceed the population")
    if s["classifier_discriminates"] != (s["control_resolving_to_a_temp_dir"] == 0
                                         and s["control_resolving_to_a_file"] == len(control)):
        problems.append("classifier_discriminates does not follow from the control arm")
    for r in rows:
        if r["verdict"] not in VERDICT_VOCAB:
            problems.append("%s: verdict outside the frozen vocabulary" % r["face_name"])
        if r["verdict"] == V_REPO_PRESENT and not r["on_disk"]:
            problems.append("%s: published as present but not on disk" % r["face_name"])
        if r["verdict"] == V_FIXTURE and r["on_disk"]:
            problems.append("%s: published as a fixture but the file is on disk" % r["face_name"])
    stated = face["verdict"] == _verdict(s)
    if not stated:
        problems.append("published verdict does not follow from the recomputed one")
    return problems


def selftest() -> int:
    import tempfile
    bad = 0

    def leg(label, got, want):
        nonlocal bad
        if got != want:
            bad += 1
            print("FAIL: %s: %r != %r" % (label, got, want))

    def analyse(code: str, base: str) -> dict:
        tree = ast.parse(code)
        face, temp = _taint(list(ast.walk(tree)), base, {}, {})
        kinds = sorted({j["kind"] for j in _join_sites(list(ast.walk(tree)), base, face, temp)})
        return {"kinds": kinds, "face": sorted(face), "temp": sorted(temp)}

    base = "X-2026-01-01.json"

    leg("a literal joined onto a temp root is a fixture join",
        analyse("import os, tempfile\n"
                "def main():\n"
                "    tmp = tempfile.mkdtemp()\n"
                "    p = os.path.join(tmp, '%s')\n" % base, base)["kinds"], ["temp_join"])

    leg("a literal joined onto ROOT is a repo join",
        analyse("import os\nROOT='/r'\n"
                "def main():\n"
                "    p = os.path.join(ROOT, 'results/%s')\n" % base, base)["kinds"], ["join"])

    leg("a literal that is only opened has no join",
        analyse("def main():\n    p = 'results/%s'\n    open(p,'w')\n" % base, base)["kinds"], ["open"])

    leg("temp taint crosses an intermediate join and owns the whole chain",
        analyse("import os, tempfile\n"
                "def main():\n"
                "    tmp = tempfile.mkdtemp()\n"
                "    root = os.path.join(tmp, 'fake')\n"
                "    p = os.path.join(root, 'results/%s')\n" % base, base)["kinds"], ["temp_join"])

    leg("temp taint reaches a loop binding over a fixture list",
        analyse("import os, tempfile\n"
                "def main():\n"
                "    tmp = tempfile.mkdtemp()\n"
                "    fixture = [('results/%s', b'{}')]\n"
                "    for rel, body in fixture:\n"
                "        open(os.path.join(tmp, rel), 'w')\n" % base, base)["kinds"],
        ["temp_join"])

    leg("a module-level constant reaches a function scope",
        analyse("P = 'results/%s'\n"
                "def main():\n    open(P)\n" % base, base)["face"], ["P"])

    leg("temp_join wins over a plain join in the verdict order",
        classify({"temp_join", "join"}, on_disk=False, at_head=False, shaped=True), V_FIXTURE)
    leg("a repo join with no file is a missing repo file",
        classify({"join"}, on_disk=False, at_head=False, shaped=True), V_REPO_MISSING)
    leg("on disk and at HEAD is present",
        classify(set(), on_disk=True, at_head=True, shaped=False), V_REPO_PRESENT)
    leg("on disk but absent at HEAD is its own verdict",
        classify(set(), on_disk=True, at_head=False, shaped=False), V_ABSENT_AT_HEAD)
    leg("a repo-shaped literal alone still grades as a missing repo file",
        classify(set(), on_disk=False, at_head=False, shaped=True), V_REPO_MISSING)
    leg("a bare literal with no join is unresolved",
        classify(set(), on_disk=False, at_head=False, shaped=False), V_LITERAL_ONLY)

    tmpdir = tempfile.mkdtemp(prefix="e421_")
    try:
        os.makedirs(os.path.join(tmpdir, "results"))
        with io.open(os.path.join(tmpdir, "results", base), "w", encoding="utf-8") as fh:
            fh.write("{}")
        got = os.path.exists(os.path.join(tmpdir, "results", base))
        leg("a fixture path really does exist inside the temp dir", got, True)
        leg("and it does not exist in the repo", os.path.exists(os.path.join(ROOT, "results", base)), False)
    finally:
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)

    leg("stem of a name is its alphabetic prefix", stem_of("ALLOWANCE-2099-01-01.json"), "ALLOWANCE")
    leg("stem of a one-letter name is that letter", stem_of("B-2026-01-01.json"), "B")

    summary = {"unresolved_with_a_site_in_the_tree": 0, "unresolved_joined_into_the_repo_and_missing": 0,
               "unresolved_whose_literal_is_repo_shaped": 3}
    leg("no site means unanswerable", _verdict(summary),
        "the_unresolved_names_have_no_site_the_census_can_find_so_resolution_is_unanswerable")
    summary = {"faces_unresolved_in_e406": 4, "unresolved_with_a_site_in_the_tree": 4,
               "unresolved_joined_into_the_repo_and_missing": 0,
               "unresolved_resolving_at_the_spelled_path": 2,
               "unresolved_joined_into_a_temp_dir": 1,
               "unresolved_named_only_by_the_census_own_selftest": 1,
               "by_verdict_unresolved": {V_SPELLED: 2, V_FIXTURE: 1, V_CENSUS_SELF: 1}}
    leg("all four accounted for and none missing means no face is lacked",
        _verdict(summary).startswith("no unresolved name is a face the tree reads and lacks"), True)
    summary["unresolved_joined_into_the_repo_and_missing"] = 1
    leg("one genuinely missing repo file flips the verdict", _verdict(summary),
        "1 of 4 unresolved names are joined into the repo and the tree does not hold them")
    summary["unresolved_joined_into_the_repo_and_missing"] = 0
    summary["by_verdict_unresolved"] = {V_SPELLED: 2, V_REPO_PRESENT: 1, V_CENSUS_SELF: 1}
    summary["unresolved_joined_into_a_temp_dir"] = 0
    leg("an on-disk face counts as accounted for in the verdict arithmetic",
        _verdict(summary).startswith("no unresolved name"), True)

    # exact-name matching: a suffix of a longer name is not this name (E330 family)
    leg("a bare literal names the face", _spells(ast.parse("x = 'gamma_latest.json'"), base="gamma_latest.json"), True)
    leg("a path ending in the name names it",
        _spells(ast.parse("x = 'results/state_tilt/gamma_latest.json'"), base="gamma_latest.json"), True)
    leg("keydelta_latest.json does not name delta_latest.json",
        _spells(ast.parse("x = 'keydelta_latest.json'"), base="delta_latest.json"), False)
    leg("slopematrix_latest.json does not name x_latest.json",
        _spells(ast.parse("x = 'slopematrix_latest.json'"), base="x_latest.json"), False)

    leg("a census-only site outranks a temp join",
        classify({"temp_join"}, on_disk=False, at_head=False, shaped=True, census_only=True), V_CENSUS_SELF)
    leg("a spelled existing path outranks a temp join",
        classify({"temp_join"}, on_disk=False, at_head=False, shaped=True,
                 spelled=["results/state_tilt/A-2026-01-01.json"]), V_SPELLED)
    leg("a file at the recorded path outranks a temp join elsewhere",
        classify({"temp_join"}, on_disk=True, at_head=True, shaped=False), V_REPO_PRESENT)

    corpus = module_texts()
    leg("the study excludes itself from the corpus it scans", SELF_MODULE not in corpus, True)
    leg("but it does scan the census that produced the population", CENSUS_MODULE in corpus, True)

    print("selftest %d/%d" % (27 - bad, 27))
    return 0 if bad == 0 else 1


def main(argv: list[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "verify":
        problems = verify()
        for p in problems:
            print("PROBLEM:", p)
        print("verify problems=%d" % len(problems))
        return 0 if not problems else 1
    face = build()
    os.makedirs(OUTDIR, exist_ok=True)
    out = os.path.join(OUTDIR, "NAMERESOLVE-%s.json" % face["evidence_cutoff"])
    for target in (out, os.path.join(OUTDIR, "nameresolve_latest.json")):
        with io.open(target, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
    s = face["summary"]
    print("population=%d unresolved=%d control=%d"
          % (s["faces_in_population"], s["faces_unresolved_in_e406"], s["faces_in_the_control_arm"]))
    print("unresolved by verdict=%s" % s["by_verdict_unresolved"])
    print("control by verdict=%s" % s["by_verdict_control"])
    print("strong_basis=%s -> fixture=%d file=%d"
          % (s["strong_basis_names"], s["strong_basis_resolving_to_a_fixture"],
             s["strong_basis_resolving_to_a_file"]))
    print("classifier_discriminates=%s" % s["classifier_discriminates"])
    print("verdict=%s" % face["verdict"])
    print("face=%s" % _rel(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))