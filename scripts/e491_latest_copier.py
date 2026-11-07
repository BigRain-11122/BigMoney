"""E491 -- who composes a ``*_latest.json`` face, when the dated face is the only thing written?

E489 (r1514) found exactly one same-directory row whose write call composes the reader
directory under ANOTHER basename: ``bandthreshguard``.  Its traced write call is
``open(path, ...)`` where ``path = os.path.join(OUTDIR, FACE)`` and ``FACE`` is a dated
name, while the reader opens ``bandthreshguard_latest.json``.  E489 recorded that as
"another basename, composed elsewhere" -- a guess, because its trace only knows calls
that TAKE a path and write into it.

This face replaces the guess with a measurement.  A ``_latest`` copy is very often made by
a COPY call -- ``shutil.copyfile(path, latest)`` -- which carries its destination as the
SECOND argument.  E489's write-call tracer reads only first arguments, so it cannot see
that call at all, and reports the row as if no producer existed.

Measured, whole-repo, statically, no draws and no engine:

  1. every call to a copier (``shutil.copyfile/copy/copy2/move``, ``os.replace/rename``)
     whose folded DESTINATION basename ends ``_latest.json``;
  2. every direct write (``open``/``write_text``/``write_json``) to the same name shape;
  3. fold BOTH arguments of each copier, so the row says which dated face is copied into
     which latest name, and whether the two paths share a directory;
  4. re-read ``bandthreshguard_latest.json``'s producer from scratch and publish the call
     that makes it, so E489's row stops being an inference.

Reads scripts/ and Tools/ Python sources; writes
results/state_tilt/LATESTCOPIER-<cutoff>.json plus latestcopier_latest.json.
"""
import argparse
import ast
import io
import json
import os
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if os.path.join(ROOT, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "scripts"))

import e451_prereg_digest as e451  # noqa: E402
import e489_write_wire as e489  # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "latestcopier_latest.json"
DATED_PREFIX = "LATESTCOPIER"
CARD = ("E491-WHO-COMPOSES-THE-LATEST-COPY-OF-THE-ONE-WRITER-E489-FOUND-IN-THE-READERS-"
        "DIRECTORY-UNDER-ANOTHER-BASENAME")
LATEST_SUFFIX = "_latest.json"
MAX_READ_BYTES = 2 * 1024 * 1024
MAX_HOPS = 24
MAX_PATHS = 6
SCAN_DIRS = ("scripts", "Tools", "firm")
SELF_EXCLUDED = ("e491_", "run_e491", "e489_", "run_e489", "smoke_test")

COPY_FUNCS = ("copyfile", "copy", "copy2", "move", "replace", "rename")
COPY_ATTRS = COPY_FUNCS
DIRECT_FUNCS = ("write_json", "write_text", "dump_json", "write_json_face")
DIRECT_ATTRS = ("open", "write_text", "write_bytes", "dump")
DIRECT_NAMES = DIRECT_FUNCS + ("open",)

C_COPY_SAME_DIR = "the_latest_copy_is_a_copy_call_inside_the_source_directory"
C_COPY_OTHER_DIR = "the_latest_copy_is_a_copy_call_out_of_the_source_directory"
C_DIRECT = "the_latest_copy_is_written_directly"
C_SEVERAL = "the_latest_copy_has_several_static_composers"
C_NONE = "no_static_composer_is_found"
CLASSES = (C_COPY_SAME_DIR, C_COPY_OTHER_DIR, C_DIRECT, C_SEVERAL, C_NONE)

K_COPY = "copy"
K_DIRECT = "direct"

V_EMPTY = "no_latest_face_has_a_static_composer"
V_COPY = "most_latest_copies_are_copy_calls_inside_the_source_directory"
V_COPY_MINORITY = "a_minority_of_latest_copies_are_copy_calls_inside_the_source_directory"
V_DIRECT = "most_latest_copies_are_written_directly"
VERDICT_VOCAB = (V_EMPTY, V_COPY, V_COPY_MINORITY, V_DIRECT)

ANSWER_FACE = "bandthreshguard_latest.json"


def _norm(text):
    return e489._norm(text)


def _clean(path):
    return e489._clean(path)


# ------------------------------------------------------------------ call discovery


def _call_kind(node):
    if not isinstance(node, ast.Call):
        return None
    func = node.func
    name = None
    if isinstance(func, ast.Name):
        name = func.id
        if name in COPY_FUNCS:
            return K_COPY
        if name in DIRECT_NAMES:
            return K_DIRECT
        return None
    if isinstance(func, ast.Attribute):
        if func.attr in COPY_ATTRS:
            return K_COPY
        if func.attr in DIRECT_ATTRS:
            return K_DIRECT
        return None
    return None


def scan_sources(root=None):
    """Every Python source under SCAN_DIRS that mentions a latest name, self excluded."""
    root = root or ROOT
    found = []
    for sub in SCAN_DIRS:
        base = os.path.join(root, sub)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = sorted(d for d in dirnames
                                 if d not in (".git", "__pycache__", "node_modules",
                                              "legacy", "Money02"))
            for name in sorted(filenames):
                if not name.endswith(".py"):
                    continue
                if name.startswith(SELF_EXCLUDED):
                    continue
                full = os.path.join(dirpath, name)
                try:
                    if os.path.getsize(full) > MAX_READ_BYTES:
                        continue
                    text = e451.read_text(full)
                except (OSError, UnicodeError):
                    continue
                if LATEST_SUFFIX not in text:
                    continue
                rel = os.path.relpath(full, root).replace(os.sep, "/")
                found.append((rel, text))
    return found


def composers_in(rel, text, root=None):
    """Every call in ``rel`` whose folded destination is a latest name."""
    root = root or ROOT
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return [], "the_source_cannot_be_parsed"
    folder = e489.FolderEx(rel, tree, root)
    sites = []
    for node in ast.walk(tree):
        kind = _call_kind(node)
        if kind is None or len(node.args) < 2:
            continue
        dst_arg = node.args[1] if kind == K_COPY else node.args[0]
        names = dict(folder.module_bindings)
        line = getattr(node, "lineno", 0)
        names.update(folder.function_bindings(line))
        names.update(folder.for_bindings(line))
        dst, dst_open = folder.fold(dst_arg, names, 0)
        dst = [_clean(p) for p in dst if _clean(p)]
        if not any(os.path.basename(p).endswith(LATEST_SUFFIX) for p in dst):
            continue
        src = []
        if kind == K_COPY:
            srcs, _ = folder.fold(node.args[0], names, 0)
            src = [_clean(p) for p in srcs if _clean(p)]
        sites.append({
            "source": rel,
            "line": line,
            "kind": kind,
            "callee": (node.func.id if isinstance(node.func, ast.Name) else node.func.attr),
            "destination_paths": dst[:MAX_PATHS],
            "source_paths": src[:MAX_PATHS],
            "destination_unfolded": bool(dst_open) or not dst,
            "source_unfolded": bool(src) is False and kind == K_COPY,
        })
    return sites, None


def _dated_sibling(dst_basename, src_paths):
    stem = dst_basename[: -len(LATEST_SUFFIX)]
    if not stem:
        return False
    for src in src_paths:
        base = os.path.basename(src)
        if base == dst_basename:
            continue
        if base.upper().startswith(stem.upper()):
            return True
    return False


def compose_class(composers):
    if not composers:
        return C_NONE
    if len(composers) > 1:
        return C_SEVERAL
    site = composers[0]
    if site.get("kind") == K_DIRECT:
        return C_DIRECT
    dst_dirs = {os.path.dirname(p) for p in site.get("destination_paths") or []}
    src_dirs = {os.path.dirname(p) for p in site.get("source_paths") or []}
    if dst_dirs and src_dirs and dst_dirs == src_dirs:
        return C_COPY_SAME_DIR
    return C_COPY_OTHER_DIR


# ------------------------------------------------------------------ population


def population(root=None):
    root = root or ROOT
    sites = []
    unparsed = []
    sources = scan_sources(root)
    for rel, text in sources:
        found, note = composers_in(rel, text, root)
        if note:
            unparsed.append(rel)
            continue
        sites.extend(found)
    rows = {}
    for site in sites:
        for dst in site.get("destination_paths") or []:
            base = os.path.basename(dst)
            if not base.endswith(LATEST_SUFFIX):
                continue
            row = rows.setdefault(base, {"latest_basename": base, "composers": [],
                                         "destination_paths": []})
            if dst not in row["destination_paths"]:
                row["destination_paths"].append(dst)
            key = (site["source"], site["line"])
            if key not in [(c["source"], c["line"]) for c in row["composers"]]:
                row["composers"].append(dict(site))
    out = []
    for base in sorted(rows):
        row = rows[base]
        row["composers"].sort(key=lambda c: (c["source"], c["line"]))
        row["destination_paths"] = sorted(row["destination_paths"])
        row["compose_class"] = compose_class(row["composers"])
        row["copy_source_is_a_dated_sibling"] = _dated_sibling(
            base, [p for c in row["composers"] for p in (c.get("source_paths") or [])])
        row["destination_exists"] = any(
            os.path.exists(os.path.join(root, p)) for p in row["destination_paths"])
        out.append(row)
    meta = {
        "scan_directories": list(SCAN_DIRS),
        "sources_mentioning_a_latest_name": len(sources),
        "sources_unparsed": sorted(unparsed),
        "excluded_source_prefixes": list(SELF_EXCLUDED),
        "population_definition": "every call whose folded destination basename ends "
                                 "'%s', grouped by that basename" % LATEST_SUFFIX,
    }
    return out, meta


# ------------------------------------------------------------------ summary / verdict


def _recompute(face):
    rows = face.get("rows") or []
    counts = {k: 0 for k in CLASSES}
    for row in rows:
        if row.get("compose_class") in counts:
            counts[row["compose_class"]] += 1
    return {
        "latest_faces": len(rows),
        "composer_sites": len({(c.get("source"), c.get("line")) for r in rows
                               for c in (r.get("composers") or [])}),
        "compose_class_counts": counts,
        "faces_whose_copy_is_a_copy_call": (
            counts[C_COPY_SAME_DIR] + counts[C_COPY_OTHER_DIR]),
        "faces_whose_copy_is_a_copy_call_in_the_source_directory": counts[C_COPY_SAME_DIR],
        "faces_written_directly": counts[C_DIRECT],
        "faces_with_several_composers": counts[C_SEVERAL],
        "faces_with_no_static_composer": counts[C_NONE],
        "faces_whose_copy_source_is_a_dated_sibling": sum(
            1 for r in rows if r.get("copy_source_is_a_dated_sibling")),
        "faces_whose_destination_exists_on_disk": sum(
            1 for r in rows if r.get("destination_exists")),
        "copy_faces_whose_destination_exists_on_disk": sum(
            1 for r in rows if r.get("destination_exists")
            and r.get("compose_class") in (C_COPY_SAME_DIR, C_COPY_OTHER_DIR)),
    }


def _verdict(summary):
    total = int(summary.get("latest_faces") or 0)
    if not total:
        return V_EMPTY
    same_dir = int(summary.get("faces_whose_copy_is_a_copy_call_in_the_source_directory") or 0)
    direct = int(summary.get("faces_written_directly") or 0)
    if same_dir * 2 >= total:
        return V_COPY
    if direct * 2 >= total:
        return V_DIRECT
    return V_COPY_MINORITY


def answer(rows, name=ANSWER_FACE):
    """E491's own question, answered from the rows -- never from prose."""
    row = next((r for r in rows if r["latest_basename"] == name), None)
    if row is None:
        return {"latest_basename": name,
                "found": False,
                "note": "no static composer of this name was found in the scanned sources"}
    site = row["composers"][0] if row["composers"] else None
    return {
        "latest_basename": name,
        "found": True,
        "compose_class": row["compose_class"],
        "composer_count": len(row["composers"]),
        "composer": site,
        "goes_through_the_same_directory_constant": (
            row["compose_class"] == C_COPY_SAME_DIR),
        "copy_source_is_a_dated_sibling": row["copy_source_is_a_dated_sibling"],
    }


# ------------------------------------------------------------------ build / write


def build(root=None, write=True):
    root = root or ROOT
    rows, meta = population(root)
    summary = _recompute({"rows": rows})
    ans = answer(rows)
    face = {
        "card": CARD,
        "study": "E491_who_composes_the_latest_copy_when_the_dated_face_is_the_only_written_file",
        "title": "who composes a *_latest.json face when the writer only opens a dated file?",
        "evidence_cutoff": time.strftime("%Y-%m-%d"),
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "population_source": meta,
        "call_rule": {
            "copy": "shutil.copyfile/copy/copy2/move and os.replace/rename carry the "
                    "destination as the SECOND positional argument",
            "direct": "open/write_text/write_json/dump_json carry the destination as the "
                      "FIRST positional argument",
            "fold": "arguments fold through module, same-function and loop-target constants "
                    "up to %d hops (E488/E489 folder)" % MAX_HOPS,
            "why_e489_missed_it": "E489's tracer reads first arguments only, so a copy call "
                                  "looks like no producer at all",
        },
        "class_definition": {
            C_COPY_SAME_DIR: "one copy call, destination and source fold into the same "
                             "directory",
            C_COPY_OTHER_DIR: "one copy call, destination and source fold into different "
                              "directories",
            C_DIRECT: "one direct write to the latest name",
            C_SEVERAL: "two or more static composers within the scanned sources",
            C_NONE: "no composer folds to this name (out of static reach)",
        },
        "summary": summary,
        "verdict": _verdict(summary),
        "verdict_vocab": list(VERDICT_VOCAB),
        "card_answer": ans,
        "rows": rows,
        "method_limits": [
            "static only: the population is calls whose destination string folds; a name "
            "built from argv/env/a dict key is invisible here and is not counted as absent",
            "a glob-driven copier (e.g. a loop over dated files) folds to the directory, not "
            "to the copied basenames, so those faces are published as no-static-composer "
            "rather than as copies",
            "scan_directories is declared; a producer living outside scripts/Tools/firm is "
            "out of population, not proven missing",
            "C_COPY_SAME_DIR says the two folded paths share a directory; it does not claim "
            "the run executed or that the file exists",
        ],
    }
    if write:
        _write(face, root)
    return face


def _write(face, root=None):
    root = root or ROOT
    outdir = os.path.join(root, "results", "state_tilt")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    dated = os.path.join(outdir, "%s-%s.json" % (DATED_PREFIX, face["evidence_cutoff"]))
    latest = os.path.join(outdir, FACE_NAME)
    body = json.dumps(face, indent=1, ensure_ascii=False)
    for path in (dated, latest):
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
    return dated, latest


# ------------------------------------------------------------------ check / verify


def row_problems(face):
    problems = []
    summary = face.get("summary") or {}
    derived = _recompute(face)
    for key, value in derived.items():
        if summary.get(key) != value:
            problems.append("%s: published %r, re-derives %r" % (key, summary.get(key), value))
    seen = set()
    for row in face.get("rows") or []:
        base = row.get("latest_basename")
        if not base or not base.endswith(LATEST_SUFFIX):
            problems.append("%r: not a latest name" % (base,))
            continue
        if base in seen:
            problems.append("%s: duplicated row" % (base,))
        seen.add(base)
        klass = row.get("compose_class")
        if klass not in CLASSES:
            problems.append("%s: unknown class %r" % (base, klass))
        recount = compose_class(row.get("composers") or [])
        if klass != recount:
            problems.append("%s: class %r does not re-derive as %r" % (base, klass, recount))
        for site in row.get("composers") or []:
            if site.get("kind") not in (K_COPY, K_DIRECT):
                problems.append("%s: unknown composer kind %r" % (base, site.get("kind")))
            if not site.get("destination_paths"):
                problems.append("%s: composer %s:%s publishes no destination"
                                % (base, site.get("source"), site.get("line")))
    ans = face.get("card_answer") or {}
    if face.get("verdict") != _verdict({k: summary.get(k) for k in derived}):
        problems.append("verdict: published %r, re-derives %r"
                        % (face.get("verdict"),
                           _verdict({k: summary.get(k) for k in derived})))
    re_ans = answer(face.get("rows") or [],
                    ans.get("latest_basename") or ANSWER_FACE)
    if (ans.get("found") != re_ans.get("found")
            or ans.get("compose_class") != re_ans.get("compose_class")
            or ans.get("goes_through_the_same_directory_constant")
            != re_ans.get("goes_through_the_same_directory_constant")):
        problems.append("card_answer does not re-derive from the rows")
    if ans.get("found") and ans.get("compose_class") != C_COPY_SAME_DIR \
            and ans.get("goes_through_the_same_directory_constant"):
        problems.append("card_answer claims the same directory constant under another class")
    return problems


def check(face=None):
    face = face or json.load(io.open(os.path.join(OUTDIR, FACE_NAME), "r", encoding="utf-8"))
    problems = row_problems(face)
    print("e491 check %s" % ("problems=[]" if not problems else "problems=%r" % problems))
    print("verdict: %s" % face.get("verdict"))
    s = face.get("summary") or {}
    print("latest_faces=%d copy_same_dir=%d direct=%d several=%d none=%d dated_sibling=%d"
          % (s.get("latest_faces") or 0,
             s.get("faces_whose_copy_is_a_copy_call_in_the_source_directory") or 0,
             s.get("faces_written_directly") or 0,
             s.get("faces_with_several_composers") or 0,
             s.get("faces_with_no_static_composer") or 0,
             s.get("faces_whose_copy_source_is_a_dated_sibling") or 0))
    return 0 if not problems else 1


def verify(root=None):
    root = root or ROOT
    published = json.load(io.open(os.path.join(OUTDIR, FACE_NAME), "r", encoding="utf-8"))
    fresh = build(root, write=False)
    problems = []
    if published.get("verdict") != fresh.get("verdict"):
        problems.append("verdict moved %r -> %r" % (published.get("verdict"),
                                                    fresh.get("verdict")))
    a = {r["latest_basename"]: r for r in published.get("rows") or []}
    b = {r["latest_basename"]: r for r in fresh.get("rows") or []}
    if set(a) != set(b):
        problems.append("population moved: +%d -%d"
                        % (len(set(b) - set(a)), len(set(a) - set(b))))
    for base in sorted(set(a) & set(b)):
        if a[base].get("compose_class") != b[base].get("compose_class"):
            problems.append("%s: class moved %r -> %r"
                            % (base, a[base].get("compose_class"),
                               b[base].get("compose_class")))
    problems.extend(row_problems(fresh))
    print("e491 verify %s" % ("problems=[]" if not problems else "problems=%r" % problems))
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest


def _fixture(root):
    os.makedirs(os.path.join(root, "scripts"))
    os.makedirs(os.path.join(root, "results", "state_tilt"))
    os.makedirs(os.path.join(root, "results", "quarantine"))

    def w(name, body):
        io.open(os.path.join(root, "scripts", name), "w", encoding="utf-8",
                newline="\n").write(body)

    head = ("import os\nimport shutil\n"
            "ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\n"
            "OUTDIR = os.path.join(ROOT, 'results', 'state_tilt')\n")
    w("w_copy.py", head +
      "FACE = 'ANSWER-2026-11-07.json'\n"
      "LATEST = 'answer_latest.json'\n"
      "path = os.path.join(OUTDIR, FACE)\n"
      "with open(path, 'w') as fh:\n"
      "    fh.write('{}')\n"
      "latest = os.path.join(OUTDIR, LATEST)\n"
      "shutil.copyfile(path, latest)\n")
    w("w_copy_other.py", head +
      "OTHER = os.path.join(ROOT, 'results', 'quarantine')\n"
      "shutil.copyfile(os.path.join(OTHER, 'FAR-2026-11-07.json'),\n"
      "                os.path.join(OUTDIR, 'far_latest.json'))\n")
    w("w_direct.py", head +
      "open(os.path.join(OUTDIR, 'direct_latest.json'), 'w').write('{}')\n")
    w("w_both.py", head +
      "shutil.copyfile(os.path.join(OUTDIR, 'BOTH-2026-11-07.json'),\n"
      "                os.path.join(OUTDIR, 'both_latest.json'))\n"
      "open(os.path.join(OUTDIR, 'both_latest.json'), 'w').write('{}')\n")
    w("w_argv.py", "import sys\nsys.argv[1]\n")
    io.open(os.path.join(root, "results", "state_tilt", "direct_latest.json"), "w",
            encoding="utf-8", newline="\n").write("{}")
    return root


def selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    tmp = tempfile.mkdtemp(prefix="e491_")
    root = _fixture(tmp)
    rows, meta = population(root)
    by = {r["latest_basename"]: r for r in rows}

    leg("the fixtures are scanned", len(rows) == 4)
    leg("only sources that mention a latest name are scanned",
        meta["sources_mentioning_a_latest_name"] == 4)
    leg("a copy inside the source directory is C_COPY_SAME_DIR",
        by.get("answer_latest.json", {}).get("compose_class") == C_COPY_SAME_DIR)
    leg("the copy's source is the dated sibling of the name",
        by["answer_latest.json"]["copy_source_is_a_dated_sibling"])
    leg("both arguments of the copy fold",
        by["answer_latest.json"]["composers"][0]["source_paths"]
        == ["results/state_tilt/ANSWER-2026-11-07.json"]
        and by["answer_latest.json"]["composers"][0]["destination_paths"]
        == ["results/state_tilt/answer_latest.json"])
    leg("a copy out of the source directory is C_COPY_OTHER_DIR",
        by.get("far_latest.json", {}).get("compose_class") == C_COPY_OTHER_DIR)
    leg("a direct write is C_DIRECT",
        by.get("direct_latest.json", {}).get("compose_class") == C_DIRECT)
    leg("two composers is C_SEVERAL",
        by.get("both_latest.json", {}).get("compose_class") == C_SEVERAL)
    leg("a name nobody writes is C_NONE",
        compose_class([]) == C_NONE)
    leg("a direct write publishes no source path",
        all(not (c.get("source_paths") or []) for c in
            by["direct_latest.json"]["composers"]))
    leg("a destination that exists on disk is marked present",
        by["direct_latest.json"]["destination_exists"] is True)
    leg("a destination that exists nowhere is marked absent",
        by["answer_latest.json"]["destination_exists"] is False)
    leg("the E489 blind spot is reproducible: the destination is the second argument",
        by["answer_latest.json"]["composers"][0]["callee"] == "copyfile")
    ans = answer(rows, "answer_latest.json")
    leg("card_answer is answered from rows, not prose",
        ans["found"] and ans["compose_class"] == C_COPY_SAME_DIR
        and ans["goes_through_the_same_directory_constant"] is True)
    face = {"rows": rows, "evidence_cutoff": "2026-11-07"}
    summary = _recompute(face)
    face["summary"] = summary
    face["verdict"] = _verdict(summary)
    face["card_answer"] = ans
    leg("the tallies re-derive", summary["latest_faces"] == len(rows))
    leg("every row lands in exactly one class",
        sum(summary["compose_class_counts"].values()) == len(rows))
    leg("the copy-same-directory count is the headline",
        summary["faces_whose_copy_is_a_copy_call_in_the_source_directory"] == 1)
    leg("the dated-sibling count is three (two in-directory copies and one out-of-directory copy)",
        summary["faces_whose_copy_source_is_a_dated_sibling"] == 3)
    leg("the fixture has no row problems", row_problems(face) == [])
    broken = json.loads(json.dumps(face))
    next(r for r in broken["rows"]
         if r["compose_class"] == C_COPY_SAME_DIR)["compose_class"] = C_NONE
    leg("a class that does not re-derive is refused", row_problems(broken))
    broken2 = json.loads(json.dumps(face))
    broken2["verdict"] = V_DIRECT
    leg("a verdict that does not re-derive is refused", row_problems(broken2))
    broken3 = json.loads(json.dumps(face))
    broken3["card_answer"] = {"latest_basename": "absent_latest.json", "found": False}
    broken3["card_answer"] = answer(broken3["rows"])
    broken3["card_answer"]["compose_class"] = C_DIRECT
    leg("a card answer that disagrees with its rows is refused", row_problems(broken3))
    broken4 = json.loads(json.dumps(face))
    broken4["rows"].append({"latest_basename": "x_latest.json", "compose_class": C_NONE,
                            "composers": []})
    leg("a row added without its tally is refused", row_problems(broken4))
    broken5 = json.loads(json.dumps(face))
    broken5["rows"][0]["composers"] = [
        {"source": "scripts/x.py", "line": 1, "kind": "weird",
         "destination_paths": ["results/state_tilt/x_latest.json"]}]
    leg("an unknown composer kind is refused", row_problems(broken5))
    leg("write leaves both faces on disk",
        all(os.path.exists(p) for p in _write(face, root)))
    passed = sum(1 for _, ok in legs if ok)
    for name, ok in legs:
        print("%s %s" % ("PASS" if ok else "FAIL", name))
    print("selftest %d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


# ------------------------------------------------------------------ run


def run(root=None):
    root = root or ROOT
    face = build(root, write=True)
    s = face["summary"]
    ans = face["card_answer"]
    print("e491 run verdict=%s" % face["verdict"])
    print("latest_faces=%d copy_same_dir=%d copy_other_dir=%d direct=%d several=%d none=%d"
          % (s["latest_faces"],
             s["faces_whose_copy_is_a_copy_call_in_the_source_directory"],
             (s["compose_class_counts"] or {}).get(C_COPY_OTHER_DIR, 0),
             s["faces_written_directly"], s["faces_with_several_composers"],
             s["faces_with_no_static_composer"]))
    print("card_answer: %s found=%s class=%s composer=%s"
          % (ans.get("latest_basename"), ans.get("found"), ans.get("compose_class"),
             ((ans.get("composer") or {}).get("callee"),
              (ans.get("composer") or {}).get("source"),
              (ans.get("composer") or {}).get("line"))))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="E491 who composes a latest copy")
    ap.add_argument("mode", nargs="?", default="run",
                    choices=("run", "check", "verify", "selftest"))
    args = ap.parse_args(argv)
    if args.mode == "check":
        return check()
    if args.mode == "verify":
        return verify()
    if args.mode == "selftest":
        return selftest()
    return run()


if __name__ == "__main__":
    sys.exit(main())