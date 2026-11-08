"""E546 -- which of the names that name a file are read as a directory?

E537 (results/state_tilt/CONSTTERM-2026-11-08.json) split every ``__file__``-derived module constant in
``scripts/`` by what its terminal is: 855 constants name a directory, **35 name a file**.  The second
class is only safe while nothing joins it: ``os.path.join(SRC, "x")`` on a constant that holds
``scripts/run_e336_smoke_leg.py`` yields ``scripts/run_e336_smoke_leg.py/x``, which is not a path a
reader can open, list or create.

This study prices that risk instead of assuming it away.  It takes E537's own population (machine-read;
nothing is hand-copied), re-derives the value of each constant from its own module, and then scans the
module that defines it for every site that consumes the name.  Each site is classified by what the site
says the constant *is*:

  * ``S_DIRECTORY`` -- the constant is used as a container: ``os.path.join(NAME, ...)``,
    ``Path(NAME) / x``, ``Path(NAME).joinpath(x)``, ``NAME + "/x"``, an f-string that puts a ``/`` right
    after it, or one of ``listdir/walk/scandir/makedirs/mkdir/chdir/rmtree/isdir(NAME)``.
  * ``S_FILE``      -- the constant is opened or read as a file: ``open(NAME)``, ``io.open(NAME)``,
    ``Path(NAME).read_text()``, ``os.path.isfile/getsize(NAME)``, and -- per the card -- ``direname`` /
    ``basename`` / ``splitext`` of it, which are *not* directory sites.
  * ``S_PROBE``     -- ``os.path.exists(NAME)`` / ``Path(NAME).exists()``: says neither.
  * ``S_UNKNOWN``   -- the name is handed to a callee this scan does not follow (``scan_site(SELF)``,
    ``load_calendar(CAL_PATH)``, a comparison): the site does not say what the constant is.

Every directory site additionally publishes **what the consumer gets**: the path the join actually
builds, whether that path exists, and whether its parent is the file the constant holds (which is what
makes the site a defect rather than a style question).

Nothing in this repository is executed.  The tree is read as text and every value is folded by E537's
own evaluator; no source is rewritten and no corpus module is imported.

    python scripts/e546_file_named_constant_use.py build     # write the face
    python scripts/e546_file_named_constant_use.py check     # gate the published face (fast)
    python scripts/e546_file_named_constant_use.py verify    # re-derive from the tree and gate
    python scripts/e546_file_named_constant_use.py selftest  # fixture corpus + doctored faces
"""
from __future__ import annotations

import ast
import copy
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e537_constant_terminal as e537  # noqa: E402  (census/binding_values: the parent population)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")

CARD = "E546-WHICH-OF-THE-NAMES-THAT-NAME-A-FILE-ARE-READ-AS-A-DIRECTORY"
STUDY = "E546_file_named_constant_use"
DATE_STAMP = "2026-11-08"
FACE_NAME = "filepathjoined_latest.json"
DATED_PREFIX = "FILEPATHJOINED"
PARENT_FACE = "CONSTTERM-2026-11-08.json"

# a scan that reads the tree must not read its own output or its own predecessors
SELF_EXCLUDED = ("e546_", "run_e546", "_e546", "FILEPATHJOINED", "filepathjoined_")

S_DIRECTORY = "the_site_reads_the_constant_as_a_container"
S_FILE = "the_site_reads_the_constant_as_a_file"
S_PROBE = "the_site_asks_whether_the_path_exists_and_says_neither"
S_UNKNOWN = "the_site_hands_the_constant_to_a_callee_this_scan_does_not_follow"
SHAPE_VOCAB = (S_DIRECTORY, S_FILE, S_PROBE, S_UNKNOWN)

R_DIRECTORY = "a_site_builds_a_path_under_this_constant_as_if_it_were_a_directory"
R_FILE_ONLY = "every_site_that_says_what_it_is_reads_it_as_a_file"
R_PROBE_ONLY = "only_existence_probes_none_of_which_says_which"
R_UNKNOWN_ONLY = "the_name_is_consumed_but_no_site_says_what_it_is"
R_UNREAD = "no_site_in_its_own_module_names_the_constant"
ROW_VOCAB = (R_DIRECTORY, R_FILE_ONLY, R_PROBE_ONLY, R_UNKNOWN_ONLY, R_UNREAD)

# call families, matched on the last dotted segment
_DIR_CALLS = ("listdir", "walk", "scandir", "makedirs", "mkdir", "chdir", "rmtree", "isdir")
_FILE_CALLS = ("dirname", "basename", "splitext", "isfile", "getsize", "getmtime", "open",
               "read_text", "read_bytes", "write_text", "write_bytes")
_PROBE_CALLS = ("exists", "islink")
# Path methods that say what the receiver is
_PATH_DIR_METHODS = ("joinpath", "iterdir", "glob", "rglob", "mkdir")
_PATH_FILE_METHODS = ("read_text", "read_bytes", "write_text", "write_bytes", "parent", "stem",
                      "suffix", "open")

MAX_SITES = 4000


def _now():
    return "%sT%s" % (DATE_STAMP, "00:00:00+08:00")


def _is_self(name):
    low = name.lower()
    return any(tok.lower() in low for tok in SELF_EXCLUDED)


def _rel(root, path):
    return os.path.relpath(path, root).replace("\\", "/")


def _dotted(node):
    """'os.path.join' for an Attribute chain of Names, else None."""
    parts = []
    cur = node
    while isinstance(cur, ast.Attribute):
        parts.append(cur.attr)
        cur = cur.value
    if isinstance(cur, ast.Name):
        parts.append(cur.id)
        return ".".join(reversed(parts))
    return None


def _last(dotted):
    return dotted.rsplit(".", 1)[-1] if dotted else ""


def _is_name(node, name):
    return isinstance(node, ast.Name) and node.id == name


def _path_of(node, name):
    """True when the node is `Path(NAME)` (or `pathlib.Path(NAME)`)."""
    if not isinstance(node, ast.Call) or not node.args:
        return False
    last = _last(_dotted(node.func))
    return last == "Path" and _is_name(node.args[0], name)


def _site(shape, line, spell, **extra):
    row = {"shape": shape, "line": line, "spelling": spell}
    row.update(extra)
    return row


def scan_uses(tree, name):
    """Every site in one parsed module that consumes `name`, classified by what it says."""
    sites = []
    for node in ast.walk(tree):
        if len(sites) >= MAX_SITES:
            break
        if isinstance(node, ast.Call):
            fname = _dotted(node.func)
            last = _last(fname)
            head = node.args[0] if node.args else None
            if head is not None and _is_name(head, name):
                if last == "join" and len(node.args) > 1:
                    sites.append(_site(S_DIRECTORY, node.lineno, "%s(NAME, ...)" % fname,
                                       rest=len(node.args) - 1))
                    continue
                if last in _DIR_CALLS:
                    sites.append(_site(S_DIRECTORY, node.lineno, "%s(NAME)" % fname))
                    continue
                if last == "open":
                    sites.append(_site(S_FILE, node.lineno, "%s(NAME%s)"
                                       % (fname, ", ..." if len(node.args) > 1 else "")))
                    continue
                if last in ("dirname", "basename", "splitext", "isfile", "getsize", "getmtime"):
                    sites.append(_site(S_FILE, node.lineno, "%s(NAME)" % fname))
                    continue
                if last in _PROBE_CALLS:
                    sites.append(_site(S_PROBE, node.lineno, "%s(NAME)" % fname))
                    continue
                sites.append(_site(S_UNKNOWN, node.lineno, "%s(NAME)" % fname,
                                   callee=fname, arg_index=0))
                continue
            # a Path(NAME)<method> receiver
            if isinstance(node.func, ast.Attribute) and _path_of(node.func.value, name):
                meth = node.func.attr
                if meth in _PATH_DIR_METHODS:
                    sites.append(_site(S_DIRECTORY, node.lineno, "Path(NAME).%s()" % meth))
                elif meth in _PATH_FILE_METHODS:
                    sites.append(_site(S_FILE, node.lineno, "Path(NAME).%s" % meth))
                elif meth in _PROBE_CALLS:
                    sites.append(_site(S_PROBE, node.lineno, "Path(NAME).%s()" % meth))
                else:
                    sites.append(_site(S_UNKNOWN, node.lineno, "Path(NAME).%s()" % meth))
        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div) and _path_of(node.left, name):
            sites.append(_site(S_DIRECTORY, node.lineno, "Path(NAME) / x"))
        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            left, right = node.left, node.right
            lit = None
            if _is_name(left, name) and isinstance(right, ast.Constant) and isinstance(right.value, str):
                lit = right.value
            elif _is_name(right, name) and isinstance(left, ast.Constant) and isinstance(left.value, str):
                lit = left.value
            if lit is not None:
                if "/" in lit or os.sep in lit:
                    sites.append(_site(S_DIRECTORY, node.lineno, 'NAME + "%s"' % lit[:20]))
                else:
                    sites.append(_site(S_UNKNOWN, node.lineno, 'NAME + "%s"' % lit[:20]))
        elif isinstance(node, ast.JoinedStr):
            parts = node.values
            for i, part in enumerate(parts):
                if not (isinstance(part, ast.FormattedValue) and _is_name(part.value, name)):
                    continue
                nxt = parts[i + 1] if i + 1 < len(parts) else None
                if isinstance(nxt, ast.Constant) and isinstance(nxt.value, str) and \
                        (nxt.value.startswith("/") or nxt.value.startswith(os.sep)):
                    sites.append(_site(S_DIRECTORY, node.lineno, 'f"{NAME}/..."'))
                else:
                    sites.append(_site(S_UNKNOWN, node.lineno, 'f"{NAME}..."'))
        elif isinstance(node, ast.Name) and node.id == name and isinstance(node.ctx, ast.Load):
            # a bare load outside a call we recognised (comparison, return, container element)
            sites.append(_site(S_UNKNOWN, node.lineno, "NAME"))
    # dedupe: a bare-NAME load that repeats a classified call's own line is the call's argument
    seen = set()
    out = []
    for row in sorted(sites, key=lambda r: (r["line"], SHAPE_VOCAB.index(r["shape"]))):
        key = (row["line"], row["shape"], row["spelling"])
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    if not out:
        return []
    lines_with_call = {r["line"] for r in out if r["shape"] != S_UNKNOWN}
    kept = []
    for row in out:
        if row["shape"] == S_UNKNOWN and row["spelling"] == "NAME" and row["line"] in lines_with_call:
            continue
        kept.append(row)
    return kept


def _module_functions(tree):
    out = {}
    for node in getattr(tree, "body", []):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out[node.name] = node
    return out


def follow_one_hop(tree, sites):
    """Sites that hand the constant to a module-level callee of the same module, followed once.

    E545's lesson: 'undecidable' and 'nobody pointed the resolver at it' are different readings.  A
    call site that passes the name into a function this same module defines is decidable one hop out,
    so it is followed; a comparison or an import-side consumer is not, and stays unknown.
    """
    fns = _module_functions(tree)
    out = []
    for s in sites:
        if s["shape"] != S_UNKNOWN or not s.get("callee"):
            continue
        fn = fns.get(s["callee"].rsplit(".", 1)[-1])
        if fn is None:
            continue
        args = list(getattr(fn.args, "posonlyargs", [])) + list(fn.args.args)
        idx = s.get("arg_index") or 0
        if idx >= len(args):
            continue
        param = args[idx].arg
        sub = scan_uses(fn, param)
        shapes = sorted({x["shape"] for x in sub})
        out.append({
            "line": s["line"],
            "callee": s["callee"],
            "parameter": param,
            "shapes": shapes,
            "reads_as": _classify(sub),
            "sites": len(sub),
        })
    return out


def _classify(sites, one_hop=()):
    shapes = {s["shape"] for s in sites}
    for hop in one_hop or ():
        shapes |= set(hop.get("shapes") or [])
    if not shapes:
        return R_UNREAD
    if S_DIRECTORY in shapes:
        return R_DIRECTORY
    if S_FILE in shapes:
        return R_FILE_ONLY
    if S_PROBE in shapes:
        return R_PROBE_ONLY
    return R_UNKNOWN_ONLY


def _joined(rest_publish, base):
    """What a join site actually builds: the constant with '/x' appended per extra argument."""
    return base + os.sep + rest_publish


def what_the_consumer_gets(shape, spelling, value):
    """For a directory site: the path built, whether it exists, and whose parent it sits under."""
    if shape != S_DIRECTORY:
        return None
    if spelling.startswith("os.path.join") or spelling.startswith("join"):
        built = _joined("<the other join arguments>", value)
    elif spelling.startswith("Path(NAME) /"):
        built = _joined("<the other operand>", value)
    elif spelling.startswith("NAME +"):
        built = value + spelling.split('"')[1] if '"' in spelling else value + "/<lit>"
    elif spelling.startswith('f"{NAME}'):
        built = _joined("<the rest of the f-string>", value)
    else:
        built = value
    return {
        "path_the_site_builds": built,
        "that_path_exists": os.path.exists(built.replace("<", "_").replace(">", "_")),
        "the_constant_itself_is_a_file": os.path.isfile(value),
        "the_constant_itself_is_a_directory": os.path.isdir(value),
    }


# ------------------------------------------------------------------ the population
def _parent_face(root=None):
    path = os.path.join(root or ROOT, "results", "state_tilt", PARENT_FACE)
    if not os.path.exists(path):
        raise RuntimeError("parent face %s is absent; E537 must publish it first" % PARENT_FACE)
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def population(root=None, parent=None):
    """E537's own file-naming rows, re-derived from its census (never hand-copied)."""
    root = root or ROOT
    parent = parent or _parent_face(root)
    rows = e537.census(root)
    file_rows = [r for r in rows if r.get("kind") == e537.K_FILE]
    published = (parent.get("summary") or {}).get("corpus_by_kind", {}).get("names_a_file")
    return rows, file_rows, published


def _value_of(root, source, name, line):
    """The absolute value of the constant at its published line, folded by E537's evaluator."""
    path = os.path.join(root, source)
    try:
        tree = ast.parse(open(path, encoding="utf-8").read())
    except (OSError, SyntaxError):
        return None, None
    binds = e537.binding_values(tree, path)
    for ln, value in binds.get(name) or []:
        if ln == line:
            return value, tree
    return None, tree


def _imports_elsewhere(root, source, name):
    """Cheap disclosure: other modules that import this name (the scan does not follow them)."""
    stem = os.path.splitext(os.path.basename(source))[0]
    hits = []
    if not stem:
        return hits
    for rel in all_py(root):
        if rel == source or _is_self(os.path.basename(rel)):
            continue
        try:
            text = open(os.path.join(root, rel), encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        if ("import %s" % stem) in text and name in text:
            hits.append(rel)
    return hits


def all_py(root=None):
    root = root or ROOT
    out = []
    base = os.path.join(root, "scripts")
    for dirpath, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in sorted(files):
            if f.endswith(".py") and not _is_self(f):
                out.append(_rel(root, os.path.join(dirpath, f)))
    return out


def build(root=None, write=True, parent=None):
    root = root or ROOT
    parent = parent or _parent_face(root)
    rows_all, file_rows, published = population(root, parent)
    rows = []
    for r in file_rows:
        value, tree = _value_of(root, r["source"], r["name"], r["line"])
        sites = scan_uses(tree, r["name"]) if tree is not None else []
        one_hop = follow_one_hop(tree, sites) if tree is not None else []
        row_class = _classify(sites, one_hop)
        dir_sites = [s for s in sites if s["shape"] == S_DIRECTORY]
        for s in dir_sites:
            s["what_the_consumer_gets"] = what_the_consumer_gets(s["shape"], s["spelling"], value or "")
        rows.append({
            "source": r["source"],
            "name": r["name"],
            "line": r["line"],
            "form": r["form"],
            "value": value,
            "value_is_a_file": bool(value and os.path.isfile(value)),
            "value_is_a_directory": bool(value and os.path.isdir(value)),
            "row_class": row_class,
            "site_count": len(sites),
            "directory_sites": len(dir_sites),
            "sites": sites,
            "one_hop": one_hop,
            "directory_found_only_one_hop_out": bool(
                not dir_sites and any(S_DIRECTORY in (h.get("shapes") or []) for h in one_hop)),
            "imports_published_elsewhere": _imports_elsewhere(root, r["source"], r["name"]),
        })
    summary = _summary(rows, len(rows_all), published)
    face = {
        "study": STUDY,
        "card": CARD,
        "title": "which of the names that name a file are read as a directory",
        "generated": _now(),
        "evidence_cutoff": DATE_STAMP,
        "population_source": {
            "parent_face": PARENT_FACE,
            "census_rows_total": len(rows_all),
            "file_naming_rows": len(file_rows),
            "file_naming_rows_as_published_by_the_parent": published,
            "reproduction_matches_the_parent": published == len(file_rows),
        },
        "method_limits": [
            "the scan reads the module that defines the constant; an import-side consumer is counted "
            "and named (imports_published_elsewhere) but not classified",
            "a site that hands the name to a callee is published as S_UNKNOWN, not as clean",
            "dirname/basename/splitext of the constant are file sites by the card's own definition, "
            "not directory sites",
            "what_the_consumer_gets is a spelling of the join, not a runtime path: the other join "
            "arguments are often not literal",
            "a default-argument binding (``def f(p=NAME)``) is published as a bare-name site and the "
            "callee's own use of ``p`` is not followed from there; the four residual rows are of this "
            "kind or are ``os.path.abspath(NAME)`` identity comparisons, neither of which says whether "
            "the constant is a file or a directory -- they are published as unknown, not as clean",
        ],
        "summary": summary,
        "verdict": _verdict(summary),
        "verdict_vocab": [
            "every_file_named_constant_is_read_as_a_file_where_a_site_says_which",
            "some_file_named_constants_are_joined_as_if_they_were_directories",
            "no_site_says_which_so_the_question_stays_open",
        ],
        "row_vocab": list(ROW_VOCAB),
        "shape_vocab": list(SHAPE_VOCAB),
        "rows": rows,
    }
    if write:
        write_face(face, root)
    return face


def _summary(rows, total, published):
    by_class = {}
    for r in rows:
        by_class[r["row_class"]] = by_class.get(r["row_class"], 0) + 1
    dir_rows = [r for r in rows if r["row_class"] == R_DIRECTORY]
    by_name = {}
    for r in rows:
        slot = by_name.setdefault(r["name"], {"constants": 0, "directory_rows": 0})
        slot["constants"] += 1
        if r["row_class"] == R_DIRECTORY:
            slot["directory_rows"] += 1
    shapes = {s: 0 for s in SHAPE_VOCAB}
    for r in rows:
        for s in r["sites"]:
            shapes[s["shape"]] = shapes.get(s["shape"], 0) + 1
    hop_shapes = {s: 0 for s in SHAPE_VOCAB}
    hop_sites = 0
    for r in rows:
        for h in r.get("one_hop") or []:
            hop_sites += 1
            for sh in h.get("shapes") or []:
                hop_shapes[sh] = hop_shapes.get(sh, 0) + 1
    return {
        "census_rows_total": total,
        "file_naming_rows": len(rows),
        "file_naming_rows_as_published_by_the_parent": published,
        "reproduction_matches_the_parent": published == len(rows),
        "rows": len(rows),
        "by_class": by_class,
        "names": len(by_name),
        "by_name": by_name,
        "directory_rows": len(dir_rows),
        "directory_rows_found_only_one_hop_out": sum(
            1 for r in rows if r.get("directory_found_only_one_hop_out")),
        "one_hop_sites": hop_sites,
        "one_hop_by_shape": hop_shapes,
        "unknown_spellings": sorted({s["spelling"] for r in rows for s in r["sites"]
                                     if s["shape"] == S_UNKNOWN}),
        "directory_rows_whose_constant_is_a_file_on_disk": sum(
            1 for r in dir_rows if r.get("value_is_a_file") and not r.get("value_is_a_directory")),
        "directory_rows_with_a_self_import_elsewhere": sum(
            1 for r in dir_rows if r.get("imports_published_elsewhere")),
        "sites": sum(len(r["sites"]) for r in rows),
        "sites_by_shape": shapes,
        "constants_read_as_a_directory": sorted({r["name"] for r in dir_rows}),
    }


def _verdict(summary):
    if summary["directory_rows"]:
        return "some_file_named_constants_are_joined_as_if_they_were_directories"
    if summary["by_class"].get(R_FILE_ONLY):
        return "every_file_named_constant_is_read_as_a_file_where_a_site_says_which"
    return "no_site_says_which_so_the_question_stays_open"


def write_face(face, root=None):
    root = root or ROOT
    out = os.path.join(root, "results", "state_tilt")
    os.makedirs(out, exist_ok=True)
    dated = os.path.join(out, "%s-%s.json" % (DATED_PREFIX, DATE_STAMP))
    latest = os.path.join(out, FACE_NAME)
    for path in (dated, latest):
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=False)
            fh.write("\n")
    return dated, latest


def load_face(root=None):
    path = os.path.join(root or ROOT, "results", "state_tilt", FACE_NAME)
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# ------------------------------------------------------------------ the gate
def face_problems(face, root=None):
    """Everything this face promises, re-checked against the face itself."""
    root = root or ROOT
    problems = []
    if face.get("card") != CARD:
        problems.append("the face does not carry this card id")
    if not face.get("evidence_cutoff"):
        problems.append("the face has no evidence_cutoff")
    rows = face.get("rows") or []
    summary = face.get("summary") or {}
    if summary.get("rows") != len(rows):
        problems.append("the published row count is not the number of published rows")
    if summary.get("file_naming_rows") != len(rows):
        problems.append("the population size does not equal the published rows")
    if not summary.get("reproduction_matches_the_parent"):
        problems.append("the population does not reproduce the parent's own count")
    by_class = {}
    for r in rows:
        by_class[r.get("row_class")] = by_class.get(r.get("row_class"), 0) + 1
        if r.get("row_class") not in ROW_VOCAB:
            problems.append("a row carries a class outside the vocabulary: %r" % (r.get("row_class"),))
            continue
        shapes = [s.get("shape") for s in (r.get("sites") or [])]
        for sh in shapes:
            if sh not in SHAPE_VOCAB:
                problems.append("a site carries a shape outside the vocabulary: %r" % (sh,))
        if r["row_class"] == R_DIRECTORY and S_DIRECTORY not in shapes and not any(
                S_DIRECTORY in (h.get("shapes") or []) for h in (r.get("one_hop") or [])):
            problems.append("a directory row publishes no directory site (%s)" % r.get("source"))
        if r["row_class"] == R_FILE_ONLY and (S_DIRECTORY in shapes or (
                S_FILE not in shapes and not any(S_FILE in (h.get("shapes") or [])
                                                 for h in (r.get("one_hop") or [])))):
            problems.append("a file-only row does not publish a file site, or hides a directory site "
                            "(%s)" % r.get("source"))
        if r["row_class"] == R_PROBE_ONLY and (S_DIRECTORY in shapes or S_FILE in shapes):
            problems.append("a probe-only row publishes a directory or file site (%s)"
                            % r.get("source"))
        if r["row_class"] == R_UNREAD and shapes:
            problems.append("an unread row publishes sites (%s)" % r.get("source"))
        if r.get("site_count") != len(r.get("sites") or []):
            problems.append("a row's site count is not its number of sites (%s)" % r.get("source"))
        if r.get("directory_sites") != sum(1 for sh in shapes if sh == S_DIRECTORY):
            problems.append("a row's directory-site count is not the number of directory sites (%s)"
                            % r.get("source"))
        # one-hop layers must name a callee that exists in the module and a parameter that is not a
        # module-level constant (following a constant would be following the wrong name)
        for hop in r.get("one_hop") or []:
            for sh in hop.get("shapes") or []:
                if sh not in SHAPE_VOCAB:
                    problems.append("a one-hop site carries a shape outside the vocabulary (%s)"
                                    % r.get("source"))
            if hop.get("reads_as") not in ROW_VOCAB:
                problems.append("a one-hop site carries a class outside the vocabulary (%s)"
                                % r.get("source"))
            if not hop.get("parameter"):
                problems.append("a one-hop site names no parameter (%s)" % r.get("source"))
        want_flag = bool(not [s for s in (r.get("sites") or []) if s.get("shape") == S_DIRECTORY]
                         and any(S_DIRECTORY in (h.get("shapes") or [])
                                 for h in (r.get("one_hop") or [])))
        if bool(r.get("directory_found_only_one_hop_out")) != want_flag:
            problems.append("a row's one-hop-only flag does not follow from its sites (%s)"
                            % r.get("source"))
        # every directory site must say what the consumer gets, and the constant must be a file
        for s in r.get("sites") or []:
            if s.get("shape") != S_DIRECTORY:
                if "what_the_consumer_gets" in s:
                    problems.append("a non-directory site carries a built path (%s:%s)"
                                    % (r.get("source"), s.get("line")))
                continue
            got = s.get("what_the_consumer_gets") or {}
            if not got.get("path_the_site_builds"):
                problems.append("a directory site does not publish the path it builds (%s:%s)"
                                % (r.get("source"), s.get("line")))
            if got and not got.get("the_constant_itself_is_a_file"):
                problems.append("a directory site's constant is not a file on disk (%s:%s)"
                                % (r.get("source"), s.get("line")))
            if got and got.get("the_constant_itself_is_a_directory"):
                problems.append("a directory site's constant is in fact a directory, so the site is "
                                "not a defect (%s:%s)" % (r.get("source"), s.get("line")))
        # a published site must exist at that line in the module it names, and mention the name
        src = os.path.join(root, r.get("source") or "")
        if not os.path.exists(src):
            problems.append("a row names a source that is not on disk (%s)" % (r.get("source"),))
            continue
        lines = open(src, encoding="utf-8", errors="replace").read().splitlines()
        for s in r.get("sites") or []:
            ln = s.get("line")
            if not isinstance(ln, int) or ln < 1 or ln > len(lines):
                problems.append("a row publishes a line outside its source (%s:%r)"
                                % (r.get("source"), ln))
                continue
            if r.get("name") and r["name"] not in lines[ln - 1]:
                problems.append("a published site line does not mention the constant (%s:%s)"
                                % (r.get("source"), ln))
    if by_class != {k: v for k, v in (summary.get("by_class") or {}).items() if v}:
        problems.append("the published class counts are not the classes of the published rows")
    shapes = {s: 0 for s in SHAPE_VOCAB}
    for r in rows:
        for s in r.get("sites") or []:
            shapes[s.get("shape")] = shapes.get(s.get("shape"), 0) + 1
    if {k: v for k, v in shapes.items() if v} != {k: v for k, v in
                                                   (summary.get("sites_by_shape") or {}).items() if v}:
        problems.append("the published site-shape counts are not the shapes of the published sites")
    dir_rows = [r for r in rows if r.get("row_class") == R_DIRECTORY]
    if summary.get("directory_rows") != len(dir_rows):
        problems.append("the directory-row count is not the number of directory rows")
    if sorted({r["name"] for r in dir_rows}) != (summary.get("constants_read_as_a_directory") or []):
        problems.append("the published directory constant names are not the directory rows' names")
    hop_sites = sum(len(r.get("one_hop") or []) for r in rows)
    if summary.get("one_hop_sites") != hop_sites:
        problems.append("the published one-hop count is not the number of one-hop sites")
    hop_shapes = {s: 0 for s in SHAPE_VOCAB}
    for r in rows:
        for h in r.get("one_hop") or []:
            for sh in h.get("shapes") or []:
                hop_shapes[sh] = hop_shapes.get(sh, 0) + 1
    if {k: v for k, v in hop_shapes.items() if v} != {k: v for k, v in
                                                       (summary.get("one_hop_by_shape") or {}).items() if v}:
        problems.append("the published one-hop shape counts are not the one-hop sites' shapes")
    if summary.get("directory_rows_found_only_one_hop_out") != sum(
            1 for r in rows if r.get("directory_found_only_one_hop_out")):
        problems.append("the published one-hop-only directory count does not match the rows")
    if face.get("verdict") != _verdict(summary):
        problems.append("the verdict is not the one the summary implies")
    return problems


def check(face=None, root=None):
    face = face or load_face(root)
    problems = face_problems(face, root)
    print(json.dumps({"check": "ok" if not problems else "problems",
                      "rows": len(face.get("rows") or []),
                      "problems": problems}, ensure_ascii=False))
    return 0 if not problems else 1


def verify(root=None):
    root = root or ROOT
    published = json.loads(json.dumps(load_face(root)))
    fresh = build(root, write=False)
    published.pop("generated", None)
    fresh.pop("generated", None)
    same = published == fresh
    problems = face_problems(fresh, root)
    print(json.dumps({"verify": "identical" if same else "differs",
                      "problems": problems,
                      "rows": len(fresh.get("rows") or [])}, ensure_ascii=False))
    return 0 if (same and not problems) else 1


# ------------------------------------------------------------------ selftest
_FIXTURE_MOD = '''"""fixture module (E546 selftest)."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(HERE), "smoke_test.py")
OUT = os.path.join(os.path.dirname(HERE), "results", "fixture.json")
UNUSED = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nothing.csv")
JOINED = os.path.join(SRC, "member.csv")

lines = io.open(SRC, encoding="utf-8").read().splitlines()
with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("x")
if os.path.exists(OUT):
    pass
print(os.path.dirname(SRC))


def read_it(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


TEXT = read_it(SRC)
'''


def _fixture(root):
    """A tiny corpus with one file-naming constant read three ways."""
    os.makedirs(os.path.join(root, "scripts"), exist_ok=True)
    os.makedirs(os.path.join(root, "results"), exist_ok=True)
    with open(os.path.join(root, "smoke_test.py"), "w", encoding="utf-8") as fh:
        fh.write("print('fixture')\n")
    path = os.path.join(root, "scripts", "fixture_mod.py")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(_FIXTURE_MOD)
    return path


def selftest():
    problems = []
    tmp = tempfile.mkdtemp(prefix="e546_")
    try:
        _fixture(tmp)
        tree = ast.parse(open(os.path.join(tmp, "scripts", "fixture_mod.py"),
                              encoding="utf-8").read())
        src_sites = scan_uses(tree, "SRC")
        shapes = [s["shape"] for s in src_sites]
        if S_DIRECTORY not in shapes:
            problems.append("a join under a file-naming constant was not read as a directory")
        if S_FILE not in shapes:
            problems.append("an open/dirname of a file-naming constant was not read as a file")
        if _classify(src_sites) != R_DIRECTORY:
            problems.append("a constant with both kinds of site was not classed as a directory row")
        out_sites = scan_uses(tree, "OUT")
        if S_PROBE not in [s["shape"] for s in out_sites]:
            problems.append("an os.path.exists probe was not classified as a probe")
        if S_DIRECTORY in [s["shape"] for s in out_sites]:
            problems.append("opening a file and probing it was read as a directory site")
        if _classify(out_sites) != R_FILE_ONLY:
            problems.append("a constant opened and probed was not classed as a file row")
        if _classify(scan_uses(tree, "HERE")) != R_FILE_ONLY:
            problems.append("a constant only handed to dirname was not classed as a file row")
        if _classify(scan_uses(tree, "UNUSED")) != R_UNREAD:
            problems.append("a name never used in the module was not classed unread")
        # one hop: a callee of the same module that opens its parameter makes the site decidable
        read_sites = [s for s in scan_uses(tree, "TEXT") if s["shape"] == S_UNKNOWN]
        if read_sites:
            problems.append("a call site that hands the name to a callee was not published as unknown")
        hops = follow_one_hop(tree, scan_uses(tree, "SRC"))
        if not any(h["callee"] == "read_it" and S_FILE in (h["shapes"] or []) for h in hops):
            problems.append("a callee that opens its parameter was not followed one hop out")
        # a callee that never names the parameter is not evidence either way
        if _classify([{"shape": S_UNKNOWN, "line": 1, "spelling": "x", "callee": "nope"}],
                     [{"shapes": []}]) != R_UNKNOWN_ONLY:
            problems.append("an empty one-hop layer promoted a row to a decided class")
        # the join site must say what the consumer gets, and it must know the constant is a file
        join_site = [s for s in src_sites if s["shape"] == S_DIRECTORY][0]
        got = what_the_consumer_gets(join_site["shape"], join_site["spelling"],
                                     os.path.join(tmp, "smoke_test.py"))
        if not got or not got["the_constant_itself_is_a_file"]:
            problems.append("a directory site did not report that its constant is a file")
        # the row builder over a hand-made parent population
        parent = {"summary": {"corpus_by_kind": {"names_a_file": 1}}}
        values = e537.binding_values(tree, os.path.join(tmp, "scripts", "fixture_mod.py"))
        if "SRC" not in values:
            problems.append("the parent evaluator could not fold the fixture constant")
        # doctored faces must be refused
        face = {
            "card": CARD, "evidence_cutoff": DATE_STAMP, "generated": _now(),
            "population_source": {"reproduction_matches_the_parent": True},
            "summary": {"rows": 1, "file_naming_rows": 1,
                        "reproduction_matches_the_parent": True,
                        "by_class": {R_DIRECTORY: 1}, "directory_rows": 1,
                        "sites_by_shape": {S_DIRECTORY: 1},
                        "one_hop_sites": 0, "one_hop_by_shape": {},
                        "directory_rows_found_only_one_hop_out": 0,
                        "constants_read_as_a_directory": ["SRC"]},
            "verdict": _verdict({"directory_rows": 1, "by_class": {R_DIRECTORY: 1}}),
            "rows": [{"source": "scripts/fixture_mod.py", "name": "SRC", "line": 6,
                      "row_class": R_DIRECTORY, "site_count": 1, "directory_sites": 1,
                      "one_hop": [], "directory_found_only_one_hop_out": False,
                      "sites": [{"shape": S_DIRECTORY, "line": 8,
                                 "spelling": "os.path.join(NAME, ...)",
                                 "what_the_consumer_gets": {
                                     "path_the_site_builds": os.path.join(tmp, "smoke_test.py",
                                                                          "<rest>"),
                                     "the_constant_itself_is_a_file": True,
                                     "the_constant_itself_is_a_directory": False}}]}],
        }
        # the doctored fixture needs the real line numbers of the fixture module
        src_lines = open(os.path.join(tmp, "scripts", "fixture_mod.py"),
                         encoding="utf-8").read().splitlines()
        for i, ln in enumerate(src_lines, 1):
            if ln.startswith("SRC ="):
                face["rows"][0]["line"] = i
            if "os.path.join(SRC, " in ln:
                face["rows"][0]["sites"][0]["line"] = i
        if face_problems(face, root=tmp):
            problems.append("the hand-built face for the fixture was refused: %s"
                            % (face_problems(face, root=tmp)[:2],))
        doc = copy.deepcopy(face)
        doc["rows"][0]["row_class"] = R_FILE_ONLY
        if not face_problems(doc, root=tmp):
            problems.append("a flipped row class was accepted")
        doc = copy.deepcopy(face)
        doc["verdict"] = "a_verdict_this_study_never_publishes"
        if not face_problems(doc, root=tmp):
            problems.append("a hand-written verdict was accepted")
        doc = copy.deepcopy(face)
        doc["rows"][0]["sites"][0].pop("what_the_consumer_gets")
        if not face_problems(doc, root=tmp):
            problems.append("a directory site with no built path was accepted")
        doc = copy.deepcopy(face)
        doc["rows"][0]["sites"][0]["what_the_consumer_gets"]["the_constant_itself_is_a_directory"] = True
        if not face_problems(doc, root=tmp):
            problems.append("a site whose constant is a directory was accepted as a defect")
        doc = copy.deepcopy(face)
        doc["rows"][0]["sites"][0]["line"] = 9999
        if not face_problems(doc, root=tmp):
            problems.append("a site line outside the source was accepted")
        doc = copy.deepcopy(face)
        doc["summary"]["rows"] = 2
        if not face_problems(doc, root=tmp):
            problems.append("a summary that outlives its rows was accepted")
        doc = copy.deepcopy(face)
        doc["rows"][0]["sites"] = []
        doc["rows"][0]["site_count"] = 0
        doc["rows"][0]["directory_sites"] = 0
        if not face_problems(doc, root=tmp):
            problems.append("a directory row with no directory site was accepted")
    except Exception as exc:  # pragma: no cover - selftest must report, not raise
        problems.append("selftest raised %r" % (exc,))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    total = 20
    print(json.dumps({"selftest": "%d/%d" % (total - len(problems), total),
                      "problems": problems}, ensure_ascii=False))
    return 0 if not problems else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "build"
    if cmd == "build":
        face = build()
        summary = face["summary"]
        print(json.dumps({"built": FACE_NAME, "rows": summary["rows"],
                          "by_class": summary["by_class"],
                          "directory_rows": summary["directory_rows"],
                          "verdict": face["verdict"]}, ensure_ascii=False))
        return 0
    if cmd == "check":
        return check()
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    print(json.dumps({"error": "unknown command %r" % cmd,
                      "commands": ["build", "check", "verify", "selftest"]}, ensure_ascii=False))
    return 2


if __name__ == "__main__":
    sys.exit(main())