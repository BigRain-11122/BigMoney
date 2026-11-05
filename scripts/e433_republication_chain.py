"""E433: does a republished directory value carry a name one face further?

E423 found 6 read sites that republish a directory-named field into another payload without
joining it, and 44 published fields that hold a FILE path under a directory name. The open
question is the *chain*: when such a value is republished, does the new row also carry a name
field? If it does, a reader of the new face can compose a doubled name exactly as it could in
the face the value came from -- the defect propagates instead of being contained.

Two populations, both machine-derived:

  A. code side -- the republish sites E423 published, parsed with AST. For each site the
     enclosing function is searched for dict literals that carry a directory key, and the
     literal is published with its whole key set. A literal is *bound* when it carries both a
     file-capable directory key (a key E423 observed holding a file path) and a name key.

  B. face side -- the writer faces of those same source files. Each row carrying a file-valued
     directory field is checked for a sibling name field (E423's row-level test) and for a name
     that already equals the value's basename (the doubling condition).

Verdict is recomputed from the summary by ``decide``; ``verify`` re-derives the code side and
re-reads only the writer faces, refusing a stored count that does not come back.

Usage:
    python scripts/e433_republication_chain.py run|verify|selftest
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

import e423_dirfield_join as base  # noqa: E402  (shared vocabulary, not re-implemented)

ST = os.path.join(ROOT, "results", "state_tilt")
DIRFIELD = os.path.join(ST, "dirfield_latest.json")
OUTDIR = ST

V_A_NAME_RIDES_ALONG = (
    "a_republication_row_binds_a_name_beside_a_file_capable_directory_field_and_its_published_rows_"
    "are_still_double_ready")
V_B_NAME_BOUND_NO_ROW = (
    "a_republication_row_binds_a_name_beside_the_directory_field_but_no_row_of_that_face_holds_a_"
    "file_path")
V_C_NO_NAME = "republication_rows_carry_no_name_beside_a_directory_field"
V_D_NO_SITES = "no_republish_site_survives_in_the_published_read_sites"

VERDICT_VOCAB = {V_A_NAME_RIDES_ALONG, V_B_NAME_BOUND_NO_ROW, V_C_NO_NAME, V_D_NO_SITES}


def _rel(path: str) -> str:
    return os.path.relpath(os.path.abspath(path), ROOT).replace("\\", "/")


def _load(path: str) -> dict:
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _enclosing(tree: ast.AST, lineno: int) -> ast.AST:
    """Innermost def/class that contains the line; module when none does."""
    best = tree
    best_size = 10 ** 9
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            start = node.lineno
            end = max((getattr(n, "lineno", start) for n in ast.walk(node)), default=start)
            if start <= lineno <= end:
                size = end - start
                if size < best_size:
                    best, best_size = node, size
    return best


def _dict_literals(scope: ast.AST) -> list[dict]:
    """Every dict literal in the scope with its key set (only str keys are named)."""
    out = []
    for node in ast.walk(scope):
        if not isinstance(node, ast.Dict):
            continue
        keys = [k.value for k in node.keys
                if isinstance(k, ast.Constant) and isinstance(k.value, str)]
        if not keys:
            continue
        out.append({"keys": sorted(set(keys)), "lineno": getattr(node, "lineno", 0)})
    return out


def code_side(file_keys: set[str]) -> list[dict]:
    """The republish sites, each priced by the literals its own function writes."""
    face = _load(DIRFIELD)
    sites = [s for s in face.get("read_sites") or [] if s.get("class") == base.C_REPUBLISH]
    cache: dict[str, ast.AST] = {}
    rows: list[dict] = []
    for site in sites:
        rel = site["file"]
        if os.path.isabs(rel):
            rel = _rel(rel)
        site["file"] = rel
        if rel not in cache:
            path = os.path.join(ROOT, rel)
            try:
                cache[rel] = ast.parse(io.open(path, encoding="utf-8", errors="replace").read())
            except (OSError, SyntaxError):
                cache[rel] = ast.parse("")
        tree = cache[rel]
        scope = _enclosing(tree, int(site["line"]))
        literals = [d for d in _dict_literals(scope)
                    if any(k in base.DIR_KEYS for k in d["keys"])]
        row = {
            "file": rel,
            "line": site["line"],
            "function": site["function"],
            "key": site["key"],
            "scope": getattr(scope, "name", "<module>"),
            "literals": literals,
            "file_capable_keys": sorted({k for d in literals for k in d["keys"]
                                         if k in file_keys}),
            "name_keys": sorted({k for d in literals for k in d["keys"]
                                 if k in base.NAME_KEYS}),
        }
        row["binds_a_name_beside_a_file_capable_key"] = bool(
            row["file_capable_keys"] and row["name_keys"])
        rows.append(row)
    return rows


def _json_literals(node: ast.AST) -> set[str]:
    """Bare *.json file names spelled anywhere inside an expression."""
    out: set[str] = set()
    for sub in ast.walk(node):
        if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
            v = sub.value.strip()
            if v.endswith(".json") and "/" not in v and "\\" not in v and len(v) < 80:
                out.add(v)
    return out


def write_stems(tree: ast.AST) -> set[str]:
    """Face names a module WRITES -- read from the open(..., 'w') call, not from any literal.

    Naming a face is not writing it: e403 names latestfamily_latest.json as its SEED face and
    only reads it. Attributing every *.json literal in the module would have published 32
    'writer faces', most of which the module never opens for writing. A write call usually names
    its file through a loop variable (`for name in (FACE, LATEST)`), so the resolver follows
    module constants and one level of for-loop bindings inside the enclosing function.
    """
    consts: dict[str, ast.AST] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            consts[node.targets[0].id] = node.value
    stems: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = fn.id if isinstance(fn, ast.Name) else (fn.attr if isinstance(fn, ast.Attribute)
                                                       else "")
        if name != "open" or not node.args:
            continue
        modes = [a for a in node.args[1:]
                 if isinstance(a, ast.Constant) and isinstance(a.value, str)]
        if not modes or "w" not in modes[0].value:
            continue
        local: dict[str, ast.AST] = {}
        scope = _enclosing(tree, getattr(node, "lineno", 0))
        for sub in ast.walk(scope):
            if isinstance(sub, ast.For):
                targets = [t.id for t in ast.walk(sub.target) if isinstance(t, ast.Name)]
                for t in targets:
                    local[t] = sub.iter
        arg = node.args[0]
        stems |= _json_literals(arg)
        for sub in ast.walk(arg):
            if not isinstance(sub, ast.Name):
                continue
            for table in (consts, local):
                if sub.id in table:
                    stems |= _json_literals(table[sub.id])
                    for inner in ast.walk(table[sub.id]):
                        if isinstance(inner, ast.Name) and inner.id in consts:
                            stems |= _json_literals(consts[inner.id])
    return stems


def writer_faces(files: set[str]) -> list[str]:
    """Face files the same modules open for writing (only what the write call names)."""
    stems: set[str] = set()
    for rel in files:
        try:
            tree = ast.parse(io.open(os.path.join(ROOT, rel), encoding="utf-8",
                                     errors="replace").read())
        except (OSError, SyntaxError):
            continue
        stems |= write_stems(tree)
    found = []
    for dirpath, dirnames, filenames in os.walk(os.path.join(ROOT, "results")):
        dirnames[:] = [d for d in dirnames if d not in ("_quarantine", "__pycache__")]
        for fn in filenames:
            if fn in stems:
                found.append(_rel(os.path.join(dirpath, fn)))
    return sorted(found)


def face_rows(faces: list[str]) -> tuple[list[dict], int]:
    """File-valued directory fields inside the writer faces, with their sibling names."""
    rows: list[dict] = []
    scanned = 0
    for rel in faces:
        path = os.path.join(ROOT, rel)
        try:
            payload = json.load(io.open(path, encoding="utf-8", errors="replace"))
        except (ValueError, OSError):
            continue
        scanned += 1
        stack = [payload]
        while stack:
            obj = stack.pop()
            if isinstance(obj, dict):
                dir_keys = [k for k in obj if isinstance(k, str) and k in base.DIR_KEYS
                            and isinstance(obj[k], str) and obj[k]]
                names = {k: obj[k] for k in obj if isinstance(k, str) and k in base.NAME_KEYS
                         and isinstance(obj[k], str) and obj[k]}
                for k in dir_keys:
                    v = obj[k]
                    if base.value_class(v) != base.V_FILE:
                        continue
                    bn = base._basename(v)
                    rows.append({
                        "face": rel,
                        "key": k,
                        "value": v if len(v) <= 160 else v[:157] + "...",
                        "name_fields_in_the_same_row": sorted(names),
                        "names_equal_to_the_value_basename": sorted(
                            nk for nk, nv in names.items() if base._basename(nv) == bn),
                    })
                stack.extend(v for v in obj.values() if isinstance(v, (dict, list)))
            elif isinstance(obj, list):
                stack.extend(obj[:200])
    return rows, scanned


def decide(summary: dict) -> str:
    """The verdict is recomputed here, never written by hand."""
    if not summary["republish_sites"]:
        return V_D_NO_SITES
    if summary["sites_binding_a_name_beside_a_file_capable_key"]:
        if summary["double_ready_rows_in_writer_faces"]:
            return V_A_NAME_RIDES_ALONG
        return V_B_NAME_BOUND_NO_ROW
    return V_C_NO_NAME


def build() -> dict:
    e423 = _load(DIRFIELD)
    file_keys = {r["key"] for r in e423.get("published_fields_holding_a_file_path") or []}
    sites = code_side(file_keys)
    src_files = {s["file"] for s in sites}
    faces = writer_faces(src_files)
    rows, scanned = face_rows(faces)
    attributable = {s["file"] for s in sites}
    numbered = set()
    for rel in attributable:
        try:
            tree = ast.parse(io.open(os.path.join(ROOT, rel), encoding="utf-8",
                                     errors="replace").read())
        except (OSError, SyntaxError):
            continue
        numbered |= {(rel, stem) for stem in write_stems(tree)}
    face_basenames = {f.split("/")[-1] for f in faces}
    files_without_a_writer_face = sorted(
        rel for rel in attributable
        if not any(stem in face_basenames for owner, stem in numbered if owner == rel))
    double_ready = [r for r in rows if r["name_fields_in_the_same_row"]]
    same_name = [r for r in rows if r["names_equal_to_the_value_basename"]]
    summary = {
        "republish_sites": len(sites),
        "sites_by_file": dict(collections.Counter(s["file"] for s in sites)),
        "sites_binding_a_name_beside_a_file_capable_key": sum(
            1 for s in sites if s["binds_a_name_beside_a_file_capable_key"]),
        "file_capable_keys": sorted(file_keys),
        "bound_key_pairs": sorted({(s["key"], nk) for s in sites for nk in s["name_keys"]
                                   if s["file_capable_keys"]}),
        "writer_faces": len(faces),
        "writer_faces_scanned": scanned,
        "republish_files_without_a_writer_face": files_without_a_writer_face,
        "file_valued_rows_in_writer_faces": len(rows),
        "rows_carrying_a_name_beside_the_value": len(double_ready),
        "rows_whose_name_already_equals_the_value_basename": len(same_name),
        "double_ready_rows_in_writer_faces": len(double_ready),
        "rows_by_key": dict(collections.Counter(r["key"] for r in rows)),
        "name_keys_by_row": dict(collections.Counter(
            nk for r in rows for nk in r["name_fields_in_the_same_row"])),
    }
    verdict = decide(summary)
    face = {
        "study": "E433_whether_a_republished_directory_value_carries_a_name_one_face_further",
        "card": "E433-WHICH-REPUBLICATION-SITE-CARRIES-A-FILE-VALUED-DIRECTORY-FIELD-INTO-A-NEW-FACE",
        "title": "price whether a republication row binds a name beside a file-capable directory "
                 "field, and whether the new face's rows stay double-ready",
        "generated": date.today().isoformat(),
        "evidence_cutoff": e423.get("evidence_cutoff"),
        "verdict": verdict,
        "summary": summary,
        "republish_sites": sites,
        "writer_faces": faces,
        "rows": rows[:400],
        "method_limits": [
            "a writer is owned only when the module names the face as a bare *.json literal; a "
            "face composed from a stem prefix is not attributed and is published as unattributed",
            "a literal is graded by its own key set; a row assembled from **kwargs or by mutating "
            "a dict after the literal is out of reach and is listed with the keys the AST saw",
            "the name test is E423's row test (a name key holding the value's basename), so it "
            "prices the row, not the key",
        ],
    }
    return face


def verify(face: dict | None = None) -> list[str]:
    """Re-derive the code side and re-read only the writer faces; nothing is trusted."""
    problems: list[str] = []
    face = face or _load(os.path.join(OUTDIR, "republishchain_latest.json"))
    if face.get("verdict") not in VERDICT_VOCAB:
        problems.append(f"verdict outside vocabulary: {face.get('verdict')!r}")
    cut = face.get("evidence_cutoff")
    if not cut:
        problems.append("evidence_cutoff missing")
    live = build()
    mine = face.get("summary") or {}
    for key in ("republish_sites", "sites_binding_a_name_beside_a_file_capable_key",
                "writer_faces", "file_valued_rows_in_writer_faces",
                "double_ready_rows_in_writer_faces"):
        if mine.get(key) != live["summary"].get(key):
            problems.append(f"{key} stored={mine.get(key)!r} live={live['summary'].get(key)!r}")
    if face.get("verdict") != live["verdict"]:
        problems.append(f"verdict stored={face.get('verdict')!r} recomputed={live['verdict']!r}")
    for site in live["republish_sites"]:
        if site["binds_a_name_beside_a_file_capable_key"] and not site["name_keys"]:
            problems.append(f"{site['file']}:{site['line']} bound with no name key")
    for writer in live["writer_faces"]:
        if not os.path.exists(os.path.join(ROOT, writer)):
            problems.append(f"writer face absent: {writer}")
    return problems


def selftest() -> int:
    total = bad = 0

    def check(name: str, ok: bool, detail="") -> None:
        nonlocal total, bad
        total += 1
        if not ok:
            bad += 1
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail else ""))

    fixture = ast.parse(
        "def emit(d):\n"
        "    row = {'dir': d, 'name': 'x'}\n"
        "    return row\n")
    scope = _enclosing(fixture, 3)
    lits = _dict_literals(scope)
    check("scope found and literal keys read", lits and lits[0]["keys"] == ["dir", "name"],
          lits)
    check("a dict literal with only a dir key has no name", not any(
        k in base.NAME_KEYS for k in _dict_literals(ast.parse(
            "def f(d):\n    return {'dir': d}\n"))[0]["keys"]))

    named = ast.parse(
        "LATEST = 'living_latest.json'\n"
        "SEED = os.path.join(OUT, 'seed_latest.json')\n"
        "def _write(face):\n"
        "    for name in (FACE, LATEST):\n"
        "        with open(os.path.join(D, name), 'w', encoding='utf-8') as fh:\n"
        "            json.dump(face, fh)\n")
    got = write_stems(named)
    check("a write call's own name is a writer stem", "living_latest.json" in got, got)
    check("a name the module only reads is NOT a writer stem", "seed_latest.json" not in got, got)

    s = dict(collections.Counter(), **{
        "republish_sites": 2, "sites_binding_a_name_beside_a_file_capable_key": 1,
        "double_ready_rows_in_writer_faces": 0})
    check("bound name with no double-ready row is verdict B", decide(s) == V_B_NAME_BOUND_NO_ROW)
    s["double_ready_rows_in_writer_faces"] = 3
    check("bound name with a double-ready row is verdict A", decide(s) == V_A_NAME_RIDES_ALONG)
    s2 = {"republish_sites": 1, "sites_binding_a_name_beside_a_file_capable_key": 0,
          "double_ready_rows_in_writer_faces": 0}
    check("no bound name is verdict C", decide(s2) == V_C_NO_NAME)
    check("no sites is verdict D", decide(
        {"republish_sites": 0, "sites_binding_a_name_beside_a_file_capable_key": 0,
         "double_ready_rows_in_writer_faces": 0}) == V_D_NO_SITES)

    doctored = {"verdict": sorted(VERDICT_VOCAB)[0], "evidence_cutoff": "2026-01-01",
                "summary": {"republish_sites": 999,
                            "sites_binding_a_name_beside_a_file_capable_key": 0,
                            "writer_faces": 0, "file_valued_rows_in_writer_faces": 0,
                            "double_ready_rows_in_writer_faces": 0}}
    problems = verify(doctored)
    check("verify refuses a stale site count", any("republish_sites" in p for p in problems),
          problems)

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
    out = os.path.join(OUTDIR, f"REPUBLISHCHAIN-{face['evidence_cutoff']}.json")
    for target in (out, os.path.join(OUTDIR, "republishchain_latest.json")):
        with io.open(target, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
    s = face["summary"]
    print(f"sites={s['republish_sites']} bound={s['sites_binding_a_name_beside_a_file_capable_key']} "
          f"writer_faces={s['writer_faces']} file_valued_rows={s['file_valued_rows_in_writer_faces']} "
          f"double_ready={s['double_ready_rows_in_writer_faces']}")
    print(f"by_file={s['sites_by_file']}")
    print(f"pairs={s['bound_key_pairs']}")
    print(f"verdict={face['verdict']}")
    print(f"face={_rel(out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))