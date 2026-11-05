"""E447 -- for each base E446 published as having no writer, is a live reader still launched under it?

E446 (results/state_tilt/frozenwriter_latest.json) split the 51 frozen face-home bases into 28 that
have a writer somewhere in the corpus and 23 that have none. A base with no writer is harmless only
if nobody reads there either: if a published reader still opens a file under an abandoned base, the
absence of a writer is a real gap (the artifact it expects can never be produced), not a retired
directory.

This is the mirror of E446's write scan. For each of the 23 abandoned bases it collects every READ
site in the corpus whose target statically resolves into that base, grades each reader by whether it
is something that actually runs (a chain leg, a smoke leg, a task-referenced script or a plain
script with a __main__ guard) rather than a face-writing census, and publishes the class per base.

Nothing is executed: this is a static AST reading of the tree plus the E446 face.

    python scripts/e447_abandoned_read.py run        # build and publish the face
    python scripts/e447_abandoned_read.py check      # re-derive the tallies from the published rows
    python scripts/e447_abandoned_read.py verify     # re-derive from the live tree
    python scripts/e447_abandoned_read.py selftest   # offline legs
"""

from __future__ import annotations

import ast
import json
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import e446_frozen_writer as e446  # noqa: E402  (the resolver is the measurement; never re-implement)

ROOT = e446.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
DATED_PREFIX = "ABANDONEDREAD"
FACE_NAME = DATED_PREFIX.lower() + "_latest.json"

W_WRITER = e446.W_WRITER
W_NONE = e446.W_NONE

C_UNREAD = "abandoned_and_unread"
C_READ = "abandoned_but_still_read"
C_BACKUP = "abandoned_and_only_a_backup"
CLASSES = (C_UNREAD, C_READ, C_BACKUP)

BACKUP_TOKENS = ("backup", "rollback", "_old", ".bak", "side", "quarantine")

MAX_SITES_PUBLISHED = 25
MAX_FACES_PUBLISHED = 200

# a dataframe reader / binary loader names the path as its first argument
READ_FILE_CALLS = {
    "read_csv", "read_parquet", "read_json", "read_excel", "read_feather", "read_pickle",
    "read_table", "read_html", "read_stata", "read_sas", "read_fwf", "read_orc", "read_hdf",
    "loadtxt", "genfromtxt", "imread", "load_workbook", "read_text",
}
READ_PATH_METHODS = {"read_text", "read_bytes"}
READ_DIR_CALLS = {"listdir", "scandir", "walk", "glob", "iglob", "rglob"}
READ_COPY_SOURCES = {"copy", "copy2", "copyfile", "move"}


def _rel(path: str) -> str:
    return os.path.relpath(path, ROOT).replace("\\", "/")


def _load(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def is_own_output(rel: str) -> bool:
    """A face this study publishes must not be counted as a reader of anything."""
    name = os.path.basename(rel)
    if name == FACE_NAME:
        return True
    return name.startswith(DATED_PREFIX + "-") and name.endswith(".json")


# ----------------------------------------------------------------------------- read-site scan


def _mode_is_reading(call: ast.Call) -> tuple[bool, str]:
    writing, how = e446._mode_is_writing(call)
    if writing:
        return False, how
    if how == "default_read":
        return True, how
    if how.startswith("read_mode:"):
        return True, how
    return False, how


def read_sites(tree: ast.AST, rel: str, consts: dict[str, str]) -> list[dict]:
    """Every call in one module that takes bytes (or a listing) FROM a path."""
    sites: list[dict] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = func.attr if isinstance(func, ast.Attribute) else (
            func.id if isinstance(func, ast.Name) else None)
        kind = None
        path_node = None
        extra = ""
        if name == "open" and node.args:
            reading, mhow = _mode_is_reading(node)
            if not reading:
                continue
            kind, path_node, extra = "open", node.args[0], mhow
        elif isinstance(func, ast.Attribute) and func.attr in READ_PATH_METHODS:
            kind, path_node = func.attr, func.value
        elif isinstance(func, ast.Attribute) and func.attr in READ_FILE_CALLS:
            if node.args:
                path_node = node.args[0]
            else:
                for kw in node.keywords:
                    if kw.arg in ("filepath_or_buffer", "path", "io", "fname", "filename"):
                        path_node = kw.value
            if path_node is None:
                continue
            kind = func.attr
        elif isinstance(func, ast.Attribute) and func.attr in READ_DIR_CALLS:
            if node.args:
                path_node = node.args[0]
            elif isinstance(func.value, (ast.Constant, ast.Name, ast.Call)):
                path_node = func.value  # Path(dir).rglob() carries the path in the receiver
            if path_node is None:
                continue
            kind = func.attr
        elif isinstance(func, ast.Attribute) and func.attr in READ_COPY_SOURCES:
            if node.args:
                path_node = node.args[0]
            else:
                for kw in node.keywords:
                    if kw.arg in ("src", "source"):
                        path_node = kw.value
            if path_node is None:
                continue
            kind = "copy_source"
        else:
            continue
        resolved, how = e446.resolve_path(path_node, consts, 0, rel)
        sites.append({"face": rel, "line": getattr(node, "lineno", 0), "kind": kind,
                      "mode": extra, "resolved_path": resolved, "how": how})
    return sites


def scan_corpus(root: str = ROOT) -> dict:
    files, walk = e446.py_corpus(root)
    sites: list[dict] = []
    parse_errors: list[dict] = []
    has_main: dict[str, bool] = {}
    writes_faces: dict[str, bool] = {}
    for path in files:
        rel = _rel(path) if os.path.isabs(path) else path
        if is_own_output(rel):
            continue
        try:
            if os.path.getsize(os.path.join(root, rel)) > e446.MAX_BYTES:
                continue
            src = open(os.path.join(root, rel), encoding="utf-8", errors="replace").read()
        except OSError as exc:
            parse_errors.append({"face": rel, "error": "read:%s" % exc})
            continue
        try:
            tree = ast.parse(src)
        except SyntaxError as exc:
            parse_errors.append({"face": rel, "error": "parse:%s" % exc})
            continue
        consts = e446.module_constants(tree, rel)
        sites.extend(read_sites(tree, rel, consts))
        writes_faces[rel] = any(
            e446.is_under(s.get("resolved_path"), "results")
            and str(s.get("resolved_path")).endswith(".json")
            for s in e446.write_sites(tree, rel, consts))
        has_main[rel] = any(
            isinstance(n, ast.If) and "__main__" in ast.dump(n.test) for n in ast.walk(tree))
    return {"files": files, "walk": walk, "sites": sites, "parse_errors": parse_errors,
            "has_main": has_main, "writes_faces": writes_faces}


# ----------------------------------------------------------------------------- reader grading


def _harness_text(rel: str) -> str:
    path = os.path.join(ROOT, rel)
    try:
        return open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


def harness_readers() -> dict:
    """The set of modules something actually launches, read from the harnesses themselves."""
    smoke = _harness_text("smoke_test.py")
    chain = _harness_text("Tools/s6_chain_bmb.py")
    tasks = []
    tools = os.path.join(ROOT, "Tools")
    if os.path.isdir(tools):
        for name in sorted(os.listdir(tools)):
            if name.lower().endswith((".ps1", ".cmd", ".bat")):
                tasks.append(_harness_text(os.path.join("Tools", name)))
    return {"smoke": smoke, "chain": chain, "tasks": "\n".join(tasks)}


def harvest_named(rel: str, text: str, stem_path: str, dotted: str) -> bool:
    """A harness names a module by its repo-relative path or its dotted module path.

    A bare basename is NOT evidence: `run.py` appears in every harness by accident, and counting
    those made 65 of 133 readers look like smoke legs in the first draft of this face.
    """
    if not text:
        return False
    # a Windows wrapper spells the same module with a backslash
    return stem_path in text or dotted in text or stem_path.replace("/", "\\") in text


def reader_class(rel: str, harness: dict, scan: dict, writes_faces: bool) -> str:
    stem = os.path.splitext(os.path.basename(rel))[0]
    stem_path = rel[:-3] if rel.endswith(".py") else rel
    dotted = stem_path.replace("/", ".")
    if rel == "smoke_test.py" or (harness["smoke"] and harvest_named(
            rel, harness["smoke"], stem_path, dotted)):
        return "smoke_leg"
    if harvest_named(rel, harness["chain"], stem_path, dotted):
        return "chain_leg"
    if harvest_named(rel, harness["tasks"], stem_path, dotted):
        return "task_referenced"
    # A module that publishes faces is a CENSUS of the directory it reads: it runs, but what it
    # does is measure its subject, so it is not a consumer of the abandoned base's artifacts.
    if writes_faces:
        return "face_writing_census"
    if scan["has_main"].get(rel):
        return "runnable_script"
    return "library_module"


LIVE_CLASSES = ("smoke_leg", "chain_leg", "task_referenced", "runnable_script")


def grade_base(base: str, sites: list[dict], readers: dict, max_sites: int = MAX_SITES_PUBLISHED) -> dict:
    """One row per abandoned base: the read sites under it and what kind of code they sit in."""
    exact = [s for s in sites if e446.is_under(s["resolved_path"], base)]
    suffix = [s for s in sites if e446.suffix_is_under(s["resolved_path"], base)] \
        if not exact else []
    rows = []
    for s in exact:
        r = dict(s)
        r["match"] = "resolved_under_the_base"
        rows.append(r)
    for s in suffix:
        r = dict(s)
        r["match"] = "literal_tail_only"
        rows.append(r)
    faces = {}
    for r in rows:
        face = r["face"]
        faces.setdefault(face, {"face": face, "sites": 0, "classes": set(), "writes_faces": False})
        faces[face]["sites"] += 1
        info = readers.get(face) or {"class": "library_module", "writes_faces": False}
        faces[face]["classes"].add(info["class"])
        faces[face]["writes_faces"] = info["writes_faces"]
    face_rows = []
    for k in sorted(faces):
        f = faces[k]
        face_rows.append({"face": k, "sites": f["sites"],
                          "reader_class": f["classes"].pop() if len(f["classes"]) == 1 else
                          "|".join(sorted(f["classes"])),
                          "writes_faces": f["writes_faces"],
                          "live": any(c in LIVE_CLASSES for c in readers.get(k, {}).get("classes")
                                      or {readers.get(k, {}).get("class")})})
    live = [f for f in face_rows if f["live"]]
    is_backup = any(tok in base.rsplit("/", 1)[-1].lower() for tok in BACKUP_TOKENS)
    if not rows:
        cls = C_BACKUP if is_backup else C_UNREAD
    else:
        cls = C_READ
    return {"base": base, "class": cls, "is_backup_or_rollback": is_backup,
            "read_site_count": len(rows), "exact_read_site_count": len(exact),
            "read_only_through_a_literal_tail": bool(rows) and not exact,
            "read_sites": rows[:max_sites],
            "read_sites_truncated": max(0, len(rows) - max_sites),
            "suffix_only_read_sites": len(suffix),
            "reader_class_counts": {c: sum(1 for f in face_rows if f["reader_class"] == c)
                              for c in sorted({f["reader_class"] for f in face_rows})},
            "reader_faces": len(face_rows),
            "reader_faces_with_a_live_consumer": len(live),
            "readers": face_rows[:max_sites],
            "reader_face_names": [f["face"] for f in face_rows][:MAX_FACES_PUBLISHED],
            "reader_face_names_truncated": max(0, len(face_rows) - MAX_FACES_PUBLISHED),
            "reader_classes": sorted({f["reader_class"] for f in face_rows}),
            "live_readers": [f["face"] for f in live]}


def verdict_for(rows: list[dict]) -> str:
    if not rows:
        return "empty_population"
    live = [r["base"] for r in rows if r["reader_faces_with_a_live_consumer"]]
    read = [r["base"] for r in rows if r["read_site_count"]]
    if live:
        return "at_least_one_abandoned_base_is_still_read_by_code_a_harness_launches"
    if read:
        return "abandoned_bases_are_read_only_by_censuses_and_libraries"
    return "no_abandoned_base_is_read_at_all"


# ----------------------------------------------------------------------------- build


def build(cutoff: str | None = None, root: str | None = None,
          writer_face: dict | None = None, scan: dict | None = None,
          harness: dict | None = None) -> dict:
    root = root or ROOT
    face = writer_face if writer_face is not None else _load(
        os.path.join(root, "results", "state_tilt", e446.FACE_NAME))
    population = [r for r in face["rows"] if r["writer_class"] == W_NONE]
    scan = scan if scan is not None else scan_corpus(root)
    harness = harness if harness is not None else harness_readers()

    # A reader is graded by what the module does with the bytes: a face writer is a census, an
    # unlaunched library is neither.
    readers: dict[str, dict] = {}
    for s in scan["sites"]:
        if s["face"] not in readers:
            wf = bool((scan.get("writes_faces") or {}).get(s["face"]))
            readers[s["face"]] = {"writes_faces": wf, "classes": set()}
        readers[s["face"]]["classes"].add(
            reader_class(s["face"], harness, scan, readers[s["face"]]["writes_faces"]))
    for k, v in readers.items():
        v["class"] = sorted(v["classes"])[0]

    rows = [grade_base(r["base"], scan["sites"], readers) for r in population]
    for row, src in zip(rows, population):
        row["carriers"] = src.get("carriers")
        row["members_in_the_base"] = src.get("members_in_the_base")
        row["newest_member"] = src.get("newest_member")
        row["newest_member_ts"] = src.get("newest_member_ts")

    classes = {c: sum(1 for r in rows if r["class"] == c) for c in CLASSES}
    kinds: dict[str, int] = {}
    for r in rows:
        for s in r["read_sites"]:
            kinds[s["kind"]] = kinds.get(s["kind"], 0) + 1

    summary = {
        "abandoned_bases": len(rows),
        "class_counts": classes,
        "bases_read_by_a_live_consumer": sum(1 for r in rows if r["reader_faces_with_a_live_consumer"]),
        "bases_read_at_all": sum(1 for r in rows if r["read_site_count"]),
        "read_sites_under_abandoned_bases": sum(r["read_site_count"] for r in rows),
        "read_sites_by_kind": kinds,
        "distinct_reader_faces": len({n for r in rows for n in r["reader_face_names"]}),
        "reader_class_counts": {
            c: sum(1 for n in {n for r in rows for n in r["reader_face_names"]}
                   if readers.get(n, {}).get("class") == c)
            for c in ("smoke_leg", "chain_leg", "task_referenced", "runnable_script",
                      "face_writing_census", "library_module")},
        "backup_or_rollback_bases": sum(1 for r in rows if r["is_backup_or_rollback"]),
        "bases_read_only_through_a_literal_tail": sum(
            1 for r in rows if r["read_only_through_a_literal_tail"]),
        "exact_read_sites_under_abandoned_bases": sum(r["exact_read_site_count"] for r in rows),
        "corpus": {
            "python_files_walked": len(scan["files"]),
            "parse_errors": len(scan["parse_errors"]),
            "skipped_over_max_bytes": len(scan["walk"].get("skipped_over_max_bytes") or []),
            "skipped_dir_names": sorted(e446.SKIP_DIRS),
            "max_bytes_per_file": e446.MAX_BYTES,
            "total_read_sites": len(scan["sites"]),
            "read_sites_with_a_resolved_path": sum(
                1 for s in scan["sites"] if s.get("resolved_path") is not None),
        },
        "population_check": {
            "e446_frozen_bases": face["summary"]["frozen_bases"],
            "e446_bases_without_a_writer": face["summary"]["bases_without_a_writer"],
            "recomputed_abandoned_population": len(rows),
            "agrees": face["summary"]["bases_without_a_writer"] == len(rows),
        },
    }

    return {
        "study": "E447_which_abandoned_base_is_still_named_by_a_live_reader",
        "card": "E447-WHICH-ABANDONED-BASE-IS-STILL-NAMED-BY-A-LIVE-READER",
        "title": "for each face-home base E446 published as having no writer, find every read site "
                 "whose path resolves into that base and publish whether a harness-launched reader, "
                 "a face-writing census, or nobody at all still opens a file there",
        "generated": date.today().isoformat(),
        "evidence_cutoff": cutoff or date.today().isoformat(),
        "verdict": verdict_for(rows),
        "class_vocab": list(CLASSES),
        "summary": summary,
        "rows": rows,
        "method_limits": [
            "a reader is a CALL that takes bytes or a listing FROM a path (open in a reading mode, "
            "read_text/read_bytes, read_csv/read_parquet/read_json and the other pandas loaders, "
            "np.loadtxt/genfromtxt, os.listdir/scandir/walk, glob/rglob, and the SOURCE argument of "
            "copy/move). A call that merely names the directory is neither a reader nor a writer and "
            "is out of this population",
            "resolution is E446's resolver verbatim (literals, module-scope constants, os.path.join "
            "chains, f-string heads, constant concatenation). A join whose head cannot be followed "
            "publishes only its literal tail and is classed match=literal_tail_only, never as a "
            "resolved hit",
            "liveness is read from the harnesses, not guessed from filenames: smoke_leg = named in "
            "smoke_test.py, chain_leg = named in Tools/s6_chain_bmb.py, task_referenced = named in a "
            "Tools/*.ps1|cmd|bat wrapper, runnable_script = the module has a __main__ guard, "
            "face_writing_census = the module writes a face (E446's write vocabulary), library_module "
            "= none of the above. A runnable_script with a __main__ guard counts as live even if "
            "nothing schedules it today: this face answers 'would a launch read there'",
            "the population is E446's published 23 no_writer_in_the_corpus rows, read from its "
            "summary; a base whose class changed since E446 shows up in population_check.agrees "
            "instead of being silently re-graded",
            "the corpus is every .py under the repo root minus %s and this study's own faces; files "
            "over %d bytes are skipped" % (sorted(e446.SKIP_DIRS), e446.MAX_BYTES),
            "no file outside results/state_tilt is written and nothing in the repository is executed",
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


def tally_problems(face: dict) -> list[str]:
    problems: list[str] = []
    rows = face["rows"]
    s = face["summary"]
    if len(rows) != s["abandoned_bases"]:
        problems.append("row count %d != summary %d" % (len(rows), s["abandoned_bases"]))
    recomputed = {c: sum(1 for r in rows if r["class"] == c) for c in CLASSES}
    if recomputed != s["class_counts"]:
        problems.append("class_counts %s != recomputed %s" % (s["class_counts"], recomputed))
    live = sum(1 for r in rows if r["reader_faces_with_a_live_consumer"])
    if live != s["bases_read_by_a_live_consumer"]:
        problems.append("live readers %d != summary %d" % (live, s["bases_read_by_a_live_consumer"]))
    read = sum(1 for r in rows if r["read_site_count"])
    if read != s["bases_read_at_all"]:
        problems.append("read bases %d != summary %d" % (read, s["bases_read_at_all"]))
    sites = sum(r["read_site_count"] for r in rows)
    if sites != s["read_sites_under_abandoned_bases"]:
        problems.append("site count %d != summary %d" % (sites, s["read_sites_under_abandoned_bases"]))
    for r in rows:
        if r["class"] not in CLASSES:
            problems.append("row %s carries unknown class %r" % (r["base"], r["class"]))
        if len(r["read_sites"]) != min(r["read_site_count"], MAX_SITES_PUBLISHED):
            problems.append("row %s publishes %d of %d sites"
                            % (r["base"], len(r["read_sites"]), r["read_site_count"]))
        if r["read_site_count"] and r["class"] == C_UNREAD:
            problems.append("row %s has a read site but is classed unread" % r["base"])
        if not r["read_site_count"] and r["class"] == C_READ:
            problems.append("row %s has no read site but is classed read" % r["base"])
        if r["reader_faces_with_a_live_consumer"] and r["class"] != C_READ:
            problems.append("row %s has a live reader but is not classed read" % r["base"])
        if r["reader_faces"] != len(r["reader_face_names"]) + r["reader_face_names_truncated"]:
            problems.append("row %s publishes %d of %d reader faces"
                            % (r["base"], len(r["reader_face_names"]), r["reader_faces"]))
    if face["verdict"] != verdict_for(rows):
        problems.append("verdict %r does not re-derive (%r)" % (face["verdict"], verdict_for(rows)))
    return problems


def verify(face: dict | None = None, root: str | None = None) -> list[str]:
    face = face if face is not None else _load(os.path.join(OUTDIR, FACE_NAME))
    fresh = build(cutoff=face["evidence_cutoff"], root=root)
    problems = tally_problems(fresh)
    old = {r["base"]: r for r in face["rows"]}
    new = {r["base"]: r for r in fresh["rows"]}
    if set(old) != set(new):
        problems.append("population moved: %s" % sorted(set(old) ^ set(new)))
    for base in sorted(set(old) & set(new)):
        a, b = old[base], new[base]
        if a["class"] != b["class"]:
            problems.append("%s class %s -> %s" % (base, a["class"], b["class"]))
        if a["read_site_count"] != b["read_site_count"]:
            problems.append("%s read sites %d -> %d"
                            % (base, a["read_site_count"], b["read_site_count"]))
        if a["reader_faces_with_a_live_consumer"] != b["reader_faces_with_a_live_consumer"]:
            problems.append("%s live readers %d -> %d"
                            % (base, a["reader_faces_with_a_live_consumer"],
                               b["reader_faces_with_a_live_consumer"]))
    if face["verdict"] != fresh["verdict"]:
        problems.append("verdict moved %r -> %r" % (face["verdict"], fresh["verdict"]))
    return problems


# ----------------------------------------------------------------------------- selftest


def _sites_of(src: str) -> tuple[list[dict], dict]:
    tree = ast.parse(src)
    consts = e446.module_constants(tree, "scripts/x.py")
    return read_sites(tree, "scripts/x.py", consts), consts


def _harness_for(src: str, rel: str = "scripts/x.py") -> dict:
    return {"smoke": src, "chain": "", "tasks": ""}


def selftest() -> int:
    bad: list[str] = []

    def check(name: str, ok: bool) -> None:
        if not ok:
            bad.append(name)

    # 1 a read-mode open is a reader, a write-mode open is not
    sites, _ = _sites_of('open("results/fx/a.json")\nopen("results/fx/b.json", "rb")\n')
    check("default and rb opens are readers", len(sites) == 2)
    sites, _ = _sites_of('open("results/fx/a.json", "w")\n')
    check("a write open is not a reader", sites == [])
    sites, _ = _sites_of('with open("results/fx/a.json", encoding="utf-8") as fh:\n    pass\n')
    check("a keyword-only open is a reader", len(sites) == 1)

    # 2 pandas loaders name the path in the first argument
    sites, _ = _sites_of('pd.read_csv("results/fx/p.csv")\n'
                         'pd.read_parquet(os.path.join("results", "fx", "q.parquet"))\n')
    check("pandas loaders are readers", len(sites) == 2)
    check("a loader join resolves", sites[1]["resolved_path"] == "results/fx/q.parquet")

    # 3 a path constant carries the base
    src = 'BASE = "results/fx"\njson.load(open(os.path.join(BASE, "a.json")))\n'
    sites, consts = _sites_of(src)
    check("a constant-driven open resolves", consts.get("BASE") == "results/fx")
    check("the constant lands under the base",
          len(sites) == 1 and sites[0]["resolved_path"] == "results/fx/a.json")

    # 4 Path receivers and directory listings
    sites, _ = _sites_of('from pathlib import Path\nPath("results/fx/a.json").read_text()\n'
                         'os.listdir("results/fx")\n')
    check("read_text and listdir are readers", len(sites) == 2)
    check("read_text resolves through the receiver", sites[0]["resolved_path"] == "results/fx/a.json")

    # 5 a copy source is a reader, its destination is not
    sites, _ = _sites_of('shutil.copy("results/fx/a.json", "results/other/a.json")\n')
    check("only the copy source is a reader",
          len(sites) == 1 and sites[0]["resolved_path"] == "results/fx/a.json")

    # 6 an unfollowable head degrades to a literal tail
    sites, _ = _sites_of('def r(folder):\n    return open(os.path.join(folder, "a.json")).read()\n')
    check("an unresolved head keeps a suffix reading",
          len(sites) == 1 and str(sites[0]["resolved_path"]).startswith("?"))
    check("and never matches the base by full path",
          not e446.is_under(sites[0]["resolved_path"], "results/fx"))

    # 7 reader classes come from the harness text and the __main__ guard
    scan = {"has_main": {"scripts/x.py": False}, "sites": []}
    check("a module named in smoke_test is a smoke leg",
          reader_class("scripts/x.py", _harness_for("import scripts.x"), scan, False) == "smoke_leg")
    check("a module named in the chain is a chain leg",
          reader_class("scripts/x.py", {"smoke": "", "chain": "scripts/x.py", "tasks": ""},
                       scan, False) == "chain_leg")
    check("a module named in a task wrapper is task referenced",
          reader_class("scripts/x.py", {"smoke": "", "chain": "", "tasks": "scripts\\x.py"},
                       scan, False) == "task_referenced")
    check("a __main__ module is a runnable script",
          reader_class("scripts/x.py", _harness_for(""), {"has_main": {"scripts/x.py": True},
                                                          "sites": []}, False) == "runnable_script")
    check("a face writer is a census",
          reader_class("scripts/y.py", _harness_for(""), {"has_main": {}, "sites": []},
                       True) == "face_writing_census")
    check("everything else is a library",
          reader_class("scripts/z.py", _harness_for(""), {"has_main": {}, "sites": []},
                       False) == "library_module")

    # 8 grading: a read makes the base still-read, and liveness separates the classes
    readers = {"scripts/x.py": {"class": "smoke_leg", "writes_faces": False}}
    s = [{"face": "scripts/x.py", "line": 3, "kind": "open", "mode": "default_read",
          "resolved_path": "results/fx/a.json", "how": "literal"}]
    row = grade_base("results/fx", s, readers)
    check("a read site makes the base still read", row["class"] == C_READ)
    check("a harness-launched reader is counted live", row["reader_faces_with_a_live_consumer"] == 1)
    readers2 = {"scripts/x.py": {"class": "face_writing_census", "writes_faces": True}}
    row2 = grade_base("results/fx", s, readers2)
    check("a census consumer is read but not live",
          row2["class"] == C_READ and row2["reader_faces_with_a_live_consumer"] == 0)
    check("no read site at all is unread", grade_base("results/fx", [], {})["class"] == C_UNREAD)
    check("a backup directory with no reader is classed backup",
          grade_base("results/_r9_backup", [], {})["class"] == C_BACKUP)
    check("a sibling read is not a hit",
          grade_base("results/fx", [dict(s[0], resolved_path="results/fx2/a.json")],
                     readers)["class"] == C_UNREAD)

    # 9 the verdict re-derives from the rows
    check("verdict: a live reader decides",
          verdict_for([{"base": "b", "read_site_count": 1,
                        "reader_faces_with_a_live_consumer": 1}]).startswith("at_least_one"))
    check("verdict: census-only reads",
          verdict_for([{"base": "b", "read_site_count": 1,
                        "reader_faces_with_a_live_consumer": 0}]).startswith("abandoned_bases_are_read_only"))
    check("verdict: nothing reads",
          verdict_for([{"base": "b", "read_site_count": 0,
                        "reader_faces_with_a_live_consumer": 0}]).startswith("no_abandoned_base"))
    check("verdict: empty population is not 'nothing reads'",
          verdict_for([]) == "empty_population")

    # 10 the study's own faces are never readers
    check("own latest face is excluded", is_own_output("results/state_tilt/" + FACE_NAME))
    check("own dated face is excluded",
          is_own_output("results/state_tilt/%s-2026-11-06.json" % DATED_PREFIX))
    check("a sibling face is not excluded",
          not is_own_output("results/state_tilt/frozenwriter_latest.json"))

    total = 30
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
        print("abandoned bases %d | class %s | read at all %d | read by a live consumer %d"
              % (s["abandoned_bases"], json.dumps(s["class_counts"]),
                 s["bases_read_at_all"], s["bases_read_by_a_live_consumer"]))
        print("read sites %d | distinct reader faces %d | reader classes %s"
              % (s["read_sites_under_abandoned_bases"], s["distinct_reader_faces"],
                 json.dumps(s["reader_class_counts"])))
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