"""E415 -- which bare-path reads are correct only because the process cwd happens to be right?

E414 resolved the one read of a ``*latest.json`` pointer that E398 could not attribute and found
the family supplied by the callee (``load(name, outdir=None) -> join(outdir or OUTDIR, name)``,
OUTDIR derived from ``__file__``).  It also named the shape that would have been an accident: a
read of a bare basename against the process cwd is correct only while the process is started in
the directory that holds the face.  E399/E414 kept narrowing to that shape without naming it.

This study names it.  Population: every read site in the durable corpus whose path expression is
a bare basename -- a plain string constant with no directory separator and a data extension --
and nothing joined onto it at the call.  For each site:

  1. does the immediate callee supply the directory (E414's rule), or does the site rely on the
     process cwd;
  2. for a cwd-relative site, resolve the basename at each surface that actually launches this
     tree (repo root, ``scripts/``, ``Tools/``, ``docs/``, the face directory, and the CLI's own
     home directory) and say for each whether the path exists;
  3. when it exists, is it the same document as the repo's face, or a different file that
     happens to share the basename -- the shadowing case, which is worse than a missing file
     because the leg goes green on someone else's document;
  4. publish class 4 (``cwd_relative_face_missing``) and the shadow class by name.

The readers are not edited: a fix belongs to a separate card.  Bill is
``results/state_tilt/CWDACCIDENT-<cutoff>.json`` + ``cwdaccident_latest.json``.

Subcommands: run | verify | selftest
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "results", "state_tilt")
FACE = "CWDACCIDENT-%s.json"
LATEST = "cwdaccident_latest.json"
STUDY = "E415_cwd_accident"

DATA_EXT = (".json", ".csv", ".md", ".txt", ".parquet")
MODES = {"r", "w", "a", "rb", "wb", "ab", "r+", "w+", "a+", "rt", "wt", "x"}
READ_CALLS = ("open", "load", "read_text", "read_bytes", "read_csv", "read_parquet",
              "exists", "is_file")

# Corpus: the durable code that launches this tree.  Scratch tooling (``_rNNN_*.py``) is
# excluded by name, artefact trees (results/, logs/, data/) are excluded by root, and the two
# legacy trees the iron law names are never walked.
CORPUS_DIRS = ("scripts", "Tools", "firm", "live", "engine")
CORPUS_FILES = ("smoke_test.py",)
SKIP_DIRNAMES = {"__pycache__", "results", "logs", "data", "node_modules", ".git",
                 "Money02", "Money0923", "legacy", ".codely-cli"}

C_RESOLVED = "resolved_by_its_callee"
C_IN_CWD = "cwd_relative_face_in_cwd"
C_SHADOWED = "cwd_relative_face_shadowed"
C_MISSING = "cwd_relative_face_missing"
CLASS_VOCAB = (C_RESOLVED, C_IN_CWD, C_SHADOWED, C_MISSING)

V_ALL_DIRECTED = ("every_bare_path_read_in_the_durable_corpus_is_directed_either_by_its_callee_"
                  "or_by_the_launch_directory_and_no_surface_reads_a_different_document")
V_DIRECTED_WITH_SHADOW = ("every_bare_path_read_is_directed_but_at_least_one_would_read_a_"
                          "different_document_of_the_same_basename_from_another_launch_directory")
V_DIRECTED_WITH_DEAD_LAUNCH = ("every_bare_path_read_is_directed_but_at_least_one_goes_red_from_"
                              "another_launch_directory_because_no_directory_holds_the_basename")
V_UNDIRECTED = ("at_least_one_bare_path_read_is_directed_by_neither_its_callee_nor_a_directory_"
                "the_corpus_supplies")
VERDICT_VOCAB = (V_ALL_DIRECTED, V_DIRECTED_WITH_SHADOW, V_DIRECTED_WITH_DEAD_LAUNCH, V_UNDIRECTED)


# ------------------------------------------------------------------ io
def _rel(path: str, root: str = ROOT) -> str:
    try:
        return os.path.relpath(path, root).replace("\\", "/")
    except ValueError:
        return path.replace("\\", "/")


def _sha(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_face(face: dict, outdir: str | None = None) -> str:
    outdir = outdir or OUT_DIR
    os.makedirs(outdir, exist_ok=True)
    text = json.dumps(face, ensure_ascii=False, indent=1) + "\n"
    paths = []
    for name in (FACE % face["evidence_cutoff"], LATEST):
        p = os.path.join(outdir, name)
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        paths.append(p)
    return paths[0]


# ------------------------------------------------------------------ 1. the population
def is_bare_basename(value) -> bool:
    """A path expression that carries no directory component at all."""
    if not isinstance(value, str) or not value:
        return False
    if "/" in value or "\\" in value:
        return False
    return len(value) > 1 and value.endswith(DATA_EXT)


def _path_arg(node: ast.Call):
    """The path argument of a read call, or None.  ``Path(p).open("r")`` carries its path on
    the receiver, so a mode constant in args[0] means the path is one level out."""
    fn = node.func
    name = getattr(fn, "id", None) or getattr(fn, "attr", None) or ""
    if name not in READ_CALLS:
        return None
    arg = node.args[0] if node.args else None
    if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and arg.value in MODES:
        recv = getattr(fn, "value", None)
        if isinstance(recv, ast.Call) and recv.args:
            return recv.args[0]
        return None
    return arg


def _callee_supplies_a_directory(tree: ast.Module, callee: str) -> dict:
    """Does the named callee join a directory onto the name it was given?"""
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name != callee:
            continue
        for sub in ast.walk(node):
            if isinstance(sub, ast.Call):
                fname = getattr(sub.func, "id", None) or getattr(sub.func, "attr", None) or ""
                if fname in ("join", "Path") and len(sub.args) >= 2:
                    return {"found": True, "joins_a_directory": True,
                            "evidence": "%s() joins %d arguments into the caller's name"
                                        % (fname, len(sub.args))}
            if isinstance(sub, (ast.JoinedStr,)):
                continue
        return {"found": True, "joins_a_directory": False,
                "evidence": "%s() reads the name it was given without joining a directory"
                            % callee}
    return {"found": False, "joins_a_directory": False, "evidence": "no such function in file"}


def _receiver_module(tree: ast.Module, node: ast.Call) -> str:
    """When the reader is called as ``binding.load(name)``, which module is ``binding``?

    The tree binds resolvers by ``importlib.import_module("eNNN_...")`` as often as by a plain
    ``from ... import`` (E414's site does exactly this, which is why a same-file search for
    ``load`` finds nothing and reports a resolver-directed read as cwd-relative).
    """
    fn = node.func
    if not isinstance(fn, ast.Attribute) or not isinstance(fn.value, ast.Name):
        return ""
    binding = fn.value.id
    for sub in ast.walk(tree):
        if isinstance(sub, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == binding for t in sub.targets):
            v = sub.value
            if isinstance(v, ast.Call):
                fname = getattr(v.func, "id", None) or getattr(v.func, "attr", None) or ""
                if fname in ("import_module", "__import__") and v.args \
                        and isinstance(v.args[0], ast.Constant):
                    return str(v.args[0].value)
        if isinstance(sub, ast.Import):
            for a in sub.names:
                if (a.asname or a.name) == binding:
                    return a.name
    return ""


def _module_path(module: str, root: str) -> str:
    if not module:
        return ""
    for d in ("", "scripts", "Tools"):
        p = os.path.join(root, d, module + ".py")
        if os.path.exists(p):
            return p
    return ""


def scan_sites(root: str = ROOT) -> list:
    files = [f for f in CORPUS_FILES]
    for d in CORPUS_DIRS:
        base = os.path.join(root, d)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [x for x in dirnames if x not in SKIP_DIRNAMES]
            for f in sorted(filenames):
                if f.endswith(".py") and not f.startswith("_"):
                    files.append(_rel(os.path.join(dirpath, f), root))
    sites = []
    for rel in files:
        p = os.path.join(root, rel)
        try:
            src = open(p, encoding="utf-8", errors="replace").read()
            tree = ast.parse(src)
        except (OSError, SyntaxError):
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            arg = _path_arg(node)
            if arg is None or not isinstance(arg, ast.Constant) or not is_bare_basename(arg.value):
                continue
            fn = node.func
            callee = getattr(fn, "id", None) or getattr(fn, "attr", None) or ""
            traced = _callee_supplies_a_directory(tree, callee)
            module = ""
            if not traced["joins_a_directory"]:
                module = _receiver_module(tree, node)
                mpath = _module_path(module, root)
                if mpath:
                    try:
                        mtree = ast.parse(open(mpath, encoding="utf-8", errors="replace").read())
                        traced = _callee_supplies_a_directory(mtree, callee)
                        traced["evidence"] = "%s.%s(): %s" % (
                            module, callee, traced["evidence"])
                    except SyntaxError:
                        pass
            sites.append({"file": rel, "line": node.lineno, "callee": callee,
                          "callee_module": module,
                          "basename": arg.value,
                          "callee_supplies_a_directory": traced["joins_a_directory"],
                          "evidence": traced["evidence"]})
    return sites


# ------------------------------------------------------------------ 2. the surfaces
def surface_cwds(root: str = ROOT) -> list:
    """Directories this tree is actually launched from, plus the CLI's own home."""
    out = ["."]
    for d in ("scripts", "Tools", "docs", os.path.join("results", "state_tilt")):
        if os.path.isdir(os.path.join(root, d)):
            out.append(d.replace("\\", "/"))
    home = os.path.join(os.path.expanduser("~"), ".codely-cli")
    if os.path.isdir(home):
        out.append(home)
    return out


def _is_own_face(name: str) -> bool:
    return name == LATEST or (name.startswith("CWDACCIDENT-") and name.endswith(".json"))


def resolve_at_surfaces(site: dict, root: str = ROOT) -> list:
    """Where the basename lands from each surface, and is it the same document."""
    rows = []
    own = os.path.join(root, site["basename"])
    own_sha = _sha(own) if os.path.exists(own) else None
    for cwd in surface_cwds(root):
        base = root if cwd == "." else (cwd if os.path.isabs(cwd) else os.path.join(root, cwd))
        p = os.path.join(base, site["basename"])
        exists = os.path.exists(p) and not os.path.isdir(p)
        # "a different document" is only a measurement when this tree's own copy exists to
        # compare against: otherwise the surface simply holds the one copy that exists.
        differs = bool(exists and own_sha is not None and _sha(p) != own_sha)
        rows.append({
            "cwd": cwd if cwd == "." else _rel(base, root),
            "exists": exists,
            "this_tree_holds_the_name": own_sha is not None,
            "different_document": differs,
            "bytes": os.path.getsize(p) if exists else None,
            "own_face": _is_own_face(site["basename"]),
        })
    return rows


def classify(site: dict, rows: list) -> str:
    """The callee decides first; then the launch directories do.

    ``C_SHADOWED`` is the dangerous shape: some surface holds a file with the same basename
    that is not this tree's document, so the read goes green measuring someone else's file.
    ``C_MISSING`` fails loudly everywhere because not even the first surface holds the name.
    ``C_IN_CWD`` is the card's fourth class -- correct only because the process was started in
    the directory that holds the face; the surfaces that lack it are published per site.
    """
    if site["callee_supplies_a_directory"]:
        return C_RESOLVED
    if not rows[0]["exists"]:
        return C_MISSING
    if any(r["different_document"] for r in rows[1:]):
        return C_SHADOWED
    return C_IN_CWD


# ------------------------------------------------------------------ build
def build(root: str = ROOT, now: datetime | None = None, write: bool = True) -> dict:
    now = now or datetime.now().astimezone()
    cutoff = now.date().isoformat()
    sites = scan_sites(root)
    rows = []
    for s in sites:
        if _is_own_face(s["basename"]):
            continue
        surfaces = resolve_at_surfaces(s, root)
        cls = classify(s, surfaces)
        rows.append({
            "file": s["file"], "line": s["line"], "callee": s["callee"],
            "callee_module": s.get("callee_module") or "",
            "basename": s["basename"], "class": cls,
            "callee_supplies_a_directory": s["callee_supplies_a_directory"],
            "callee_evidence": s["evidence"],
            "surfaces": surfaces,
            "surfaces_missing_the_name": [r["cwd"] for r in surfaces if not r["exists"]],
            "surfaces_with_a_different_document":
                [r["cwd"] for r in surfaces if r["different_document"]],
        })
    by_class = {c: sum(1 for r in rows if r["class"] == c) for c in CLASS_VOCAB}
    shadowed = [r for r in rows if r["class"] == C_SHADOWED]
    missing = [r for r in rows if r["class"] == C_MISSING]
    undirected = [r for r in rows if r["class"] in (C_SHADOWED, C_MISSING)]

    if undirected and all(r["class"] == C_MISSING for r in undirected):
        verdict = V_DIRECTED_WITH_DEAD_LAUNCH
    elif shadowed:
        verdict = V_DIRECTED_WITH_SHADOW
    elif undirected:
        verdict = V_UNDIRECTED
    else:
        verdict = V_ALL_DIRECTED

    face = {
        "study": STUDY,
        "card": "E415-DO-BARE-BASENAME-READS-WORK-ONLY-BECAUSE-THE-CWD-HOLDS-THE-FACE",
        "evidence_cutoff": cutoff,
        "generated": now.isoformat(timespec="seconds"),
        "verdict": verdict,
        "summary": {
            "bare_path_read_sites": len(rows),
            "surfaces": surface_cwds(root),
            "by_class": by_class,
            "directed_by_callee": by_class[C_RESOLVED],
            "directed_by_launch_directory": by_class[C_IN_CWD],
            "would_read_a_different_document": by_class[C_SHADOWED],
            "would_fail_because_the_directory_lacks_the_name": by_class[C_MISSING],
            "sites_that_only_work_from_the_launch_directory":
                sum(1 for r in rows if r["class"] == C_IN_CWD
                    and r["surfaces_missing_the_name"]),
            "corpus_files_with_a_bare_path_read": len({r["file"] for r in rows}) or None,
            "own_faces_excluded": sum(1 for s in sites if _is_own_face(s["basename"])),
            "bound": ("the census sees a read whose path argument is a literal basename at the "
                      "call.  A basename held in a variable first, built by an f-string, or "
                      "passed through a wrapper that does not join a directory is outside it; "
                      "that population is E398's (families supplied nowhere) and E403's "
                      "(parameter pass-through), and neither is claimed here."),
        },
        "sites": rows,
        "shadowing_sites": [{"file": r["file"], "line": r["line"], "basename": r["basename"],
                             "surfaces_holding_a_different_document":
                                 r["surfaces_with_a_different_document"]}
                            for r in shadowed],
        "why": ("a bare basename read is directed by the callee when the callee joins a "
                "directory onto the name it is given (E414's rule); when it does not, the "
                "read lands in whatever directory the process was started in, and the leg "
                "then measures that directory's copy of the document rather than this "
                "tree's.  The shadowed class is the one that goes green on a foreign "
                "document; the missing class at least fails loudly."),
        "law_ref": "E414 (resolver rule) + E398 (family supplied nowhere) + O-20261002-2100",
        "not_run": ["the readers were not edited", "no surface was launched to prove the "
                    "shadow empirically: the resolution is a static join against the cwd"],
    }
    if write:
        face["_path"] = write_face(face)
    return face


# ------------------------------------------------------------------ verify
COMPARE = ("evidence_cutoff", "verdict", "summary", "sites", "shadowing_sites")


def _comparable(payload: dict) -> dict:
    out = {}
    for k in COMPARE:
        v = payload.get(k)
        if k == "sites" and isinstance(v, list):
            v = [{kk: r.get(kk) for kk in ("file", "line", "callee", "callee_module",
                                           "basename", "class",
                                           "callee_supplies_a_directory",
                                           "surfaces_missing_the_name",
                                           "surfaces_with_a_different_document")}
                 for r in v]
        out[k] = v
    return out


def verify(root: str = ROOT) -> list:
    p = os.path.join(root, "results", "state_tilt", LATEST)
    if not os.path.exists(p):
        return ["no published face at results/state_tilt/%s" % LATEST]
    stored = json.load(open(p, encoding="utf-8"))
    fresh = build(root=root, write=False)
    problems = []
    a, b = _comparable(stored), _comparable(fresh)
    for k in COMPARE:
        if a.get(k) != b.get(k):
            problems.append("%s does not re-derive" % k)
    if stored.get("verdict") not in VERDICT_VOCAB:
        problems.append("stored verdict is outside the vocabulary")
    if fresh.get("verdict") not in VERDICT_VOCAB:
        problems.append("live verdict is outside the vocabulary")
    s = fresh.get("summary") or {}
    bc = s.get("by_class") or {}
    if sum(bc.values()) != s.get("bare_path_read_sites"):
        problems.append("by_class does not re-add to the site count")
    if s.get("would_read_a_different_document") != bc.get(C_SHADOWED):
        problems.append("the shadow count and its class disagree")
    if s.get("would_fail_because_the_directory_lacks_the_name") != bc.get(C_MISSING):
        problems.append("the missing count and its class disagree")
    for r in fresh.get("sites") or []:
        if r.get("class") not in CLASS_VOCAB:
            problems.append("a site class is outside the vocabulary")
            break
        if r.get("callee_supplies_a_directory") and r.get("class") != C_RESOLVED:
            problems.append("a resolver-directed site is not published as resolved")
            break
        if r.get("class") == C_RESOLVED and not r.get("callee_supplies_a_directory"):
            problems.append("a site published as resolved has no resolver")
            break
    if fresh["verdict"] == V_ALL_DIRECTED and s.get("would_read_a_different_document"):
        problems.append("published as all-directed while a site would read another document")
    return problems


# ------------------------------------------------------------------ selftest
def selftest() -> int:
    import tempfile
    fails = []

    def ok(name, cond, detail=""):
        if not cond:
            fails.append(name)
            print("FAIL:", name, detail)

    # --- bare-expression detection
    ok("a bare json basename is a bare path", is_bare_basename("CODELY.md"))
    ok("a joined path is not", not is_bare_basename("results/x.json"))
    ok("a windows-separated path is not", not is_bare_basename("results\\x.json"))
    ok("a mode string is not a path", not is_bare_basename("w"))
    ok("a bare non-data name is not a read path", not is_bare_basename("turnover"))

    # --- the classifier: resolver wins over cwd
    ok("a callee that joins a directory classifies as resolved",
       classify({"callee_supplies_a_directory": True}, [{"exists": True, "different_document": False}])
       == C_RESOLVED)
    ok("a cwd read that exists everywhere identically classifies as in-cwd",
       classify({"callee_supplies_a_directory": False},
                [{"exists": True, "different_document": False}] * 3) == C_IN_CWD)
    ok("a cwd read that is missing in its own directory classifies as missing",
       classify({"callee_supplies_a_directory": False},
                [{"exists": False, "different_document": False}] * 3) == C_MISSING)
    ok("a cwd read that finds a different document elsewhere classifies as shadowed",
       classify({"callee_supplies_a_directory": False},
                [{"exists": True, "different_document": False},
                 {"exists": True, "different_document": True}]) == C_SHADOWED)

    with tempfile.TemporaryDirectory() as tmp:
        # --- fixture: one shadowed read and one resolver-directed read
        os.makedirs(os.path.join(tmp, "scripts"), exist_ok=True)
        os.makedirs(os.path.join(tmp, "docs"), exist_ok=True)
        with open(os.path.join(tmp, "CODELY.md"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("- [a] this tree's memory\n" * 60)
        with open(os.path.join(tmp, "docs", "CODELY.md"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("- [b] another document with the same name\n" * 3)
        with open(os.path.join(tmp, "smoke_test.py"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join([
                "import json, os",
                "def load(name, outdir=None):",
                "    return json.load(open(os.path.join(outdir or 'results', name)))",
                "def a():",
                "    return open('CODELY.md', encoding='utf-8').read()",
                "def b():",
                "    return load('face_latest.json')",
            ]) + "\n")
        sites = scan_sites(tmp)
        ok("fixture: both read sites are found", len(sites) == 2, sites)
        by_name = {s["basename"]: s for s in sites}
        ok("fixture: the plain open is not resolver-directed",
           by_name.get("CODELY.md") and by_name["CODELY.md"]["callee_supplies_a_directory"] is False)
        ok("fixture: the load() callee joins a directory",
           by_name.get("face_latest.json")
           and by_name["face_latest.json"]["callee_supplies_a_directory"] is True,
           by_name.get("face_latest.json"))
        rows = resolve_at_surfaces(by_name["CODELY.md"], tmp)
        ok("fixture: the docs surface holds a different document",
           any(r["different_document"] for r in rows), rows)
        ok("fixture: the shadow is classified as shadowed, not in-cwd",
           classify(by_name["CODELY.md"], rows) == C_SHADOWED)
        ok("fixture: own faces are excluded from the population",
           _is_own_face(LATEST) and _is_own_face("CWDACCIDENT-2026-11-04.json")
           and not _is_own_face("CODELY.md"))

        # --- the false positive this study hit first: a resolver bound through importlib
        with open(os.path.join(tmp, "scripts", "e298_census.py"), "w", encoding="utf-8",
                  newline="\n") as fh:
            fh.write("\n".join([
                "import json, os",
                "HERE = os.path.dirname(os.path.abspath(__file__))",
                "OUTDIR = os.path.join(HERE, '..', 'results', 'state_tilt')",
                "def load(name, outdir=None):",
                "    return json.load(open(os.path.join(outdir or OUTDIR, name)))",
            ]) + "\n")
        with open(os.path.join(tmp, "smoke_test.py"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join([
                "import json, os",
                "def c():",
                "    m = __import__('importlib').import_module('e298_census')",
                "    return m.load('replaycensus_latest.json')",
            ]) + "\n")
        sites = scan_sites(tmp)
        ok("fixture: a resolver bound by import_module is traced into its own module",
           sites and sites[0]["callee_supplies_a_directory"] is True
           and sites[0]["callee_module"] == "e298_census", sites)
        ok("fixture: that site is published as resolved, not as a cwd read",
           classify(sites[0], [{"exists": True, "different_document": False}]) == C_RESOLVED)

        # --- absence goes red, never silent: a face with no sites still publishes a verdict
        empty = os.path.join(tmp, "empty")
        os.makedirs(empty, exist_ok=True)
        face = build(root=empty, write=False)
        ok("fixture: an empty corpus publishes zero sites and an all-directed verdict",
           face["summary"]["bare_path_read_sites"] == 0 and face["verdict"] == V_ALL_DIRECTED,
           face["verdict"])
        # a published face whose stored verdict is outside the vocabulary must be refused
        p = os.path.join(empty, "results", "state_tilt")
        os.makedirs(p, exist_ok=True)
        bad = dict(face)
        bad["verdict"] = "looks_fine_to_me"
        with open(os.path.join(p, LATEST), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(bad, ensure_ascii=False))
        problems = verify(root=empty)
        ok("fixture: a verdict outside the vocabulary is refused", bool(problems), problems)

    if fails:
        print("selftest %d/%d legs green" % (0, 11 + 8))
        return 1
    print("selftest 19/19 legs green")
    return 0


def main(argv: list) -> int:
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "run":
        face = build()
        print(json.dumps({"evidence_cutoff": face["evidence_cutoff"], "verdict": face["verdict"],
                          "summary": face["summary"]}, ensure_ascii=False, indent=1))
        print("written:", face.get("_path"))
        for r in face["sites"]:
            print("  %-28s:%-6s %-24s class=%s dirs_with_a_different_document=%s"
                  % (r["file"], r["line"], r["basename"], r["class"],
                     r["surfaces_with_a_different_document"]))
        return 0
    if cmd == "verify":
        problems = verify()
        print(json.dumps({"problems": problems}, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "selftest":
        return selftest()
    print("usage: e415_cwd_accident.py run|verify|selftest", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))