"""E647 -- can a name-collision hit reach the counted module through a string rather than an import?

E646 decided its 7 cross-module key-name hits are word collisions using import edges only, and said so
as a limit of its own arm: a module that reaches the read module through ``importlib.import_module("x")``
or through a path string is invisible to an import-statement leg.  This study measures that arm instead
of assuming it is empty.

For every hit module the study

  * collects every string the module can be asked to spell -- plain literals, ``JoinedStr`` nodes whose
    parts are all constants (their concatenation is measurable), and ``"a" + "b"`` folds -- and counts
    the strings that are built from an expression (an f-string with a value, ``str.format``, ``%``),
    because those are the ones no static reader can resolve;
  * builds the target spellings of each counted read module from measurement, not from a hand list:
    its relative path, its basename, its stem, its dotted name, and the face constants it assigns
    itself (``FACE`` / ``LATEST``) where the assigned value is a plain literal;
  * matches every collected string against those spellings in classes (exact path / basename / stem /
    dotted / face, and a weaker whole-token containment class, published apart so that a substring is
    never read as a name);
  * finds the call that consumes each matching string (import machinery, file open, exec/eval,
    ``sys.path`` mutation, path join, other, or no call at all) and publishes the binding name when the
    string only reaches a call through an assignment;
  * publishes one reach class per hit module x read module pair, and the count of dynamic loader calls
    in the hit module whether or not their argument is a literal.

The question answered is whether any of E646's collisions has a non-import route to the same container.
Nothing here re-reads E646's rows: the hits are re-derived from the tree with E642's population and
owner rule, and E646's published count is carried only as a reconciliation figure.
"""
import argparse
import ast
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-10"
FACE = "STRINGREACH.json"
LATEST = "stringreach_latest.json"
STUDY = "E647_string_reach"
SOURCE_FACE = "results/state_tilt/CROSSMODULEKEY.json"
SELF_PARTS = ("e647_", "run_e647_", "_probe_e647", "_r1668")
OUTPUT_NAME_RE = re.compile(r"(FACE|LATEST)")
OUTPUT_CONSTANT_NAMES = ("FACE", "LATEST")
MAX_EXAMPLES = 25
MAX_LITERALS_PER_MODULE = 400
VALUE_TRUNC = 120

import e640_writeread_collide as e640  # noqa: E402
import e642_module_write_key as e642  # noqa: E402
import e646_crossmodule_key as e646  # noqa: E402

MATCH_CLASSES = ("exact_path", "exact_basename", "exact_stem", "exact_dotted", "exact_face",
                 "token_contains_stem")
REACH_CLASSES = ("import_string_reach", "file_text_or_face_read",
                 "loader_machinery_without_a_module_name", "path_string_only",
                 "string_not_consumed", "no_literal_names_the_target")
SEVERITY = {"import_string_reach": 5, "file_text_or_face_read": 4,
            "loader_machinery_without_a_module_name": 3, "path_string_only": 2,
            "string_not_consumed": 1, "no_literal_names_the_target": 0}
LOADER_CLASSES = ("module_import", "file_open", "exec_or_eval", "sys_path")
CONSUMER_CLASSES = ("module_import", "file_open", "exec_or_eval", "sys_path", "path_join",
                    "other_call", "no_call")

V_IMPORT_REACH = (
    "at least one hit module reaches a counted read module through a string that import machinery "
    "consumes, so the collision has a non-import route to a module object that could hold the "
    "counted container")
V_FILE_ONLY_REACH = (
    "hits name a counted module or one of its faces only in strings that a file open consumes, so a "
    "hit can read the module's text or its published face but never the in-memory container the "
    "counted read line reads")
V_MACHINERY_ONLY = (
    "hits spell a counted module only inside loader or path machinery that does not import it by "
    "name (exec, sys.path work, path joins), so no resolved module object is produced by that string")
V_UNCONSUMED = (
    "hit modules do spell a counted module or its face, but no call consumes the string, so the "
    "spelling is inert text")
V_NO_LITERAL = (
    "no hit module spells any counted read module, its stem, or its face in any string it can be "
    "asked to spell, so the importlib/path arm E646 could not see carries no hit either")
V_NO_HITS = (
    "the cross-module arm carries no hits, so there is no string route to price and the question "
    "does not apply")
V_OFF_POPULATION = (
    "hits exist but no counted read line joins to them, so the string question is unsettled rather "
    "than answered")


def say(line):
    sys.stdout.write(line + "\n")


def rel(module, root=ROOT):
    return os.path.relpath(module, root).replace("\\", "/")


def corpus(root=ROOT):
    out = []
    for p in e642.corpus(root):
        if os.path.basename(p).startswith(SELF_PARTS):
            continue
        out.append(p)
    return out


def tree_of(path):
    src = io.open(path, encoding="utf-8", errors="replace").read()
    return ast.parse(src), src


# ---------------------------------------------------------------- string census
def _strip_dot(value):
    out = value
    while out.startswith("./"):
        out = out[2:]
    return out


def _fold_binop(node):
    """``"a" + "b"`` -> "ab" when both sides are plain string literals, else None."""
    if not isinstance(node, ast.BinOp) or not isinstance(node.op, ast.Add):
        return None
    left, right = node.left, node.right
    if isinstance(left, ast.Constant) and isinstance(left.value, str) \
            and isinstance(right, ast.Constant) and isinstance(right.value, str):
        return left.value + right.value
    return None


def _call_text(node):
    if node is None:
        return ""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _call_text(node.value)
        return (base + "." + node.attr) if base else node.attr
    if isinstance(node, ast.Call):
        return _call_text(node.func)
    return ""


def consumer_class_of(text):
    """What a call name does with a string, in whichever class it can be re-derived from."""
    if not text:
        return "no_call"
    last = text.split(".")[-1]
    if last in ("import_module", "__import__", "spec_from_file_location"):
        return "module_import"
    if last == "open":
        return "file_open"
    if last in ("exec", "eval", "compile"):
        return "exec_or_eval"
    if last in ("append", "insert", "extend") and "sys.path" in text:
        return "sys_path"
    if last == "join" and "path" in text:
        return "path_join"
    return "other_call"


def _walk_strings(node, literals, unresolved):
    for child in ast.iter_child_nodes(node):
        if isinstance(child, ast.Constant):
            if isinstance(child.value, str):
                literals.append({"line": getattr(child, "lineno", 0),
                                 "column": getattr(child, "col_offset", 0),
                                 "value": child.value, "built": "constant"})
            continue
        if isinstance(child, ast.JoinedStr):
            parts, named = [], False
            for v in child.values:
                if isinstance(v, ast.Constant) and isinstance(v.value, str):
                    parts.append(v.value)
                elif isinstance(v, ast.FormattedValue):
                    named = True
            if named:
                unresolved.append({"line": getattr(child, "lineno", 0),
                                   "column": getattr(child, "col_offset", 0),
                                   "why": "fstring_has_a_formatted_value"})
            else:
                literals.append({"line": getattr(child, "lineno", 0),
                                 "column": getattr(child, "col_offset", 0),
                                 "value": "".join(parts), "built": "joined_constants"})
            continue
        folded = _fold_binop(child)
        if folded is not None:
            literals.append({"line": getattr(child, "lineno", 0),
                             "column": getattr(child, "col_offset", 0),
                             "value": folded, "built": "constant_concatenation"})
            continue
        if isinstance(child, ast.BinOp) and isinstance(child.op, ast.Mod) \
                and isinstance(child.left, ast.Constant) and isinstance(child.left.value, str):
            unresolved.append({"line": getattr(child, "lineno", 0),
                               "column": getattr(child, "col_offset", 0),
                               "why": "percent_formatting"})
            continue
        if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute) \
                and child.func.attr == "format" \
                and isinstance(child.func.value, ast.Constant) \
                and isinstance(child.func.value.value, str):
            unresolved.append({"line": getattr(child, "lineno", 0),
                               "column": getattr(child, "col_offset", 0),
                               "why": "str_format"})
            continue
        _walk_strings(child, literals, unresolved)


def collect_strings(tree):
    literals, unresolved = [], []
    _walk_strings(tree, literals, unresolved)
    literals.sort(key=lambda r: (r["line"], r["column"], r["value"]))
    unresolved.sort(key=lambda r: (r["line"], r["column"], r["why"]))
    return literals, unresolved


def parents_of(tree):
    parents = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node
    return parents


def consumption(parents, node, max_hops=8):
    """The call that consumes a string, found by walking up, plus what the result was bound to."""
    cur, hops, bound, call = node, 0, None, None
    while cur in parents and hops < max_hops:
        p = parents[cur]
        hops += 1
        if isinstance(p, ast.Assign) and cur is p.value:
            names = [t.id for t in p.targets if isinstance(t, ast.Name)]
            if names and bound is None:
                bound = names[0]
            if call is not None:
                break
        if call is None and isinstance(p, ast.Call):
            args = list(p.args) + [k.value for k in p.keywords]
            if any(cur is a for a in args):
                call = p
        cur = p
    text = _call_text(call.func) if call is not None else ""
    return {"call": text or None,
            "consumer_class": consumer_class_of(text),
            "bound_name": bound,
            "hops": hops}


def dynamic_loader_calls(tree, parents):
    """Every call that can turn a string into a module, a file, or code -- literal argument or not."""
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        text = _call_text(node.func)
        cls = consumer_class_of(text)
        if cls not in LOADER_CLASSES:
            continue
        args = list(node.args) + [k.value for k in node.keywords]
        literal = None
        for a in args:
            if isinstance(a, ast.Constant) and isinstance(a.value, str):
                literal = a.value
                break
            folded = _fold_binop(a)
            if folded is not None:
                literal = folded
                break
        out.append({"line": getattr(node, "lineno", 0),
                    "column": getattr(node, "col_offset", 0),
                    "call": text, "consumer_class": cls,
                    "argument_is_a_measured_literal": bool(literal),
                    "argument": literal})
    out.sort(key=lambda r: (r["line"], r["column"], r["call"]))
    return out


# ---------------------------------------------------------------- targets
def spellings_of(read_module, root=ROOT):
    """Every spelling a module could be named by, plus the faces it assigns itself as literals."""
    path = read_module.replace("\\", "/")
    base = os.path.basename(path)
    stem = base[:-3] if base.endswith(".py") else base
    dotted = path[:-3].replace("/", ".") if path.endswith(".py") else path.replace("/", ".")
    faces, unmeasured = [], []
    try:
        tree, _src = tree_of(os.path.join(root, path))
    except (OSError, SyntaxError, ValueError):
        tree = None
    if tree is not None:
        present = set()
        for node in tree.body:
            if not isinstance(node, ast.Assign):
                continue
            for t in node.targets:
                if not isinstance(t, ast.Name):
                    continue
                if not (t.id.isupper() and OUTPUT_NAME_RE.search(t.id)):
                    continue
                present.add(t.id)
                if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                    faces.append({"constant": t.id,
                                  "value": node.value.value.replace("\\", "/")})
                else:
                    unmeasured.append({"constant": t.id, "kind": "assigned_but_not_a_literal"})
        faces.sort(key=lambda r: (r["constant"], r["value"]))
        unmeasured.sort(key=lambda r: r["constant"])
        absent = sorted(n for n in OUTPUT_CONSTANT_NAMES if n not in present)
    else:
        absent = sorted(OUTPUT_CONSTANT_NAMES)
    return {"path": path, "basename": base, "stem": stem, "dotted": dotted,
            "faces": [f["value"] for f in faces],
            "face_constants": faces,
            "face_constants_unmeasured": unmeasured,
            "face_constants_absent": absent}


def _stem_pattern(stem):
    return re.compile(r"(?<![0-9A-Za-z_])" + re.escape(stem) + r"(?![0-9A-Za-z_])")


def match_class(value, sp):
    """Which spelling class a string is, exact classes first so a substring is never read as a name."""
    v = _strip_dot(str(value).replace("\\", "/").strip())
    if v in (sp["path"], _strip_dot(sp["path"])):
        return "exact_path"
    if v == sp["basename"]:
        return "exact_basename"
    if v == sp["stem"]:
        return "exact_stem"
    if v == sp["dotted"]:
        return "exact_dotted"
    if v in sp["faces"]:
        return "exact_face"
    if sp["stem"] and _stem_pattern(sp["stem"]).search(v):
        return "token_contains_stem"
    return None


def reach_class_of(matches):
    """The strongest route the matching strings give, or none at all."""
    if not matches:
        return "no_literal_names_the_target"
    classes = {m["consumer_class"] for m in matches}
    if "module_import" in classes:
        return "import_string_reach"
    if "file_open" in classes:
        return "file_text_or_face_read"
    if classes & {"exec_or_eval", "sys_path"}:
        return "loader_machinery_without_a_module_name"
    if "path_join" in classes:
        return "path_string_only"
    return "string_not_consumed"


# ---------------------------------------------------------------- population
def read_population(root=ROOT):
    return e646.read_population(root)


def count_published_hits(root=ROOT):
    """E646's published hit count -- a reconciliation figure, never an input."""
    path = os.path.join(root, SOURCE_FACE)
    try:
        doc = json.load(io.open(path, encoding="utf-8"))
    except (OSError, ValueError):
        return None
    rows = doc.get("rows")
    return len(rows) if isinstance(rows, list) else None


# ---------------------------------------------------------------- measure
def measure(root=ROOT):
    files = corpus(root)
    reads = read_population(root)
    keys = {r["key"] for r in reads if r["key"]}
    hits = e646.re_derive_hits(root, files, keys)

    read_rows = [r for r in reads]
    by_module = {}
    for h in hits:
        by_module.setdefault(h["module"], []).append(h)

    rows = []
    pairs = []
    for module in sorted(by_module):
        hit_list = by_module[module]
        path = os.path.join(root, module)
        tree, _src = tree_of(path)
        parents = parents_of(tree)
        literals, unresolved = collect_strings(tree)
        loaders = dynamic_loader_calls(tree, parents)

        # joins use E646's own rule: the keys this hit names select the counted read lines
        named_keys = {k for h in hit_list for k in h["row_keys_named"]}
        targets_read = sorted({r["module"] for r in read_rows if r["key"] in named_keys})

        literal_rows = []
        for lit in literals[:MAX_LITERALS_PER_MODULE]:
            literal_rows.append({"line": lit["line"], "column": lit["column"],
                                 "value": lit["value"][:VALUE_TRUNC], "built": lit["built"]})
        elided = max(0, len(literals) - len(literal_rows))

        target_rows = []
        for rm in targets_read:
            sp = spellings_of(rm, root)
            naming = []
            for lit in literals:
                cls = match_class(lit["value"], sp)
                if cls is None:
                    continue
                node = _node_at(tree, lit["line"], lit["column"])
                cons = consumption(parents, node) if node is not None else {
                    "call": None, "consumer_class": "no_call", "bound_name": None, "hops": 0}
                naming.append({"line": lit["line"], "column": lit["column"],
                               "value": lit["value"][:VALUE_TRUNC],
                               "built": lit["built"], "match": cls,
                               "consumer": cons["call"],
                               "consumer_class": cons["consumer_class"],
                               "bound_name": cons["bound_name"],
                               "hops": cons["hops"]})
            naming.sort(key=lambda r: (r["line"], r["column"], r["match"]))
            reach = reach_class_of(naming)
            target_rows.append({"read_module": rm, "spellings": sp,
                                "literals_naming": naming[:MAX_EXAMPLES],
                                "literals_naming_count": len(naming),
                                "reach": reach})
            pairs.append({"hit_module": module, "read_module": rm,
                          "keys": sorted({k for h in hit_list for k in h["row_keys_named"]
                                          if any(r["module"] == rm and r["key"] == k
                                                 for r in read_rows)}),
                          "naming_literals": len(naming),
                          "reach": reach,
                          "match_classes": sorted({n["match"] for n in naming}),
                          "consumer_classes": sorted({n["consumer_class"] for n in naming})})

        rows.append({
            "module": module,
            "module_class": e646.module_class(module),
            "hit_lines": [{"line": h["line"], "column": h["column"], "keys": h["keys"],
                           "row_keys_named": h["row_keys_named"]} for h in hit_list],
            "literals_examined": len(literals),
            "literals": literal_rows,
            "literals_elided": elided,
            "unresolved_strings": unresolved,
            "dynamic_loader_calls": loaders,
            "targets": target_rows,
            "reach_classes": sorted({t["reach"] for t in target_rows}),
        })

    counts = counts_of(rows, pairs, len(files), len(hits), reads, count_published_hits(root))
    m = {
        "study": STUDY,
        "source_face": SOURCE_FACE,
        "method": ("re-derive E646's cross-module hits from the tree, then for every hit module "
                   "collect every string it can be asked to spell (literals, all-constant f-strings, "
                   "constant concatenations) and count the ones built from an expression; build each "
                   "counted read module's spellings from measurement (path, basename, stem, dotted "
                   "name, its own FACE/LATEST literals); match in exact classes first and whole-token "
                   "containment apart; publish the call that consumes each naming string and one "
                   "reach class per hit module x read module pair"),
        "population_source": ("%d Python files of E642's corpus, %d counted read line(s) over %d "
                              "key(s), %d cross-module hit(s) in %d module(s)"
                              % (len(files), len(reads), len(keys), len(hits), len(rows))),
        "counts": counts,
        "rows": rows,
        "pairs": pairs,
        "limits": [
            "reach is static and one-directional: a string names a module, never proves the module "
            "object it resolves to is the container the counted read line reads, so an import-string "
            "route is a route and not a demonstration",
            "strings built from an expression (f-string with a value, str.format, percent formatting) "
            "are counted and published as unresolved rather than matched, so a computed route is "
            "outside this arm by construction",
            "a string can reach a call through more assignments than the walk follows (8 hops); "
            "beyond that the consumer is published as no_call, which is a limit not a zero",
            "face names are read from module-level assignments whose name is upper case and contains "
            "FACE or LATEST (FACE_NAME and UPSTREAM_FACE included, each published with its own "
            "constant name so an upstream face is never silently read as the module's own); a face "
            "assigned through a non-literal is published as face_constants_unmeasured, and a module "
            "that assigns none of the frozen names at all is published as face_constants_absent "
            "rather than as a zero spelling set",
            "spellings are whole tokens of the measured name, so a literal that names only a family "
            "prefix ('e382' for 'e382_key_projection_delta') is not a match and is not counted",
            "the read population is E638's join (one definition); a change to that join moves this "
            "study's pairs without touching its hits",
            "files over 1MB are skipped rather than parsed (E391's cap) and are counted separately "
            "by the population this study re-derives",
        ],
    }
    m["verdict"] = decide(counts)
    m["answer"] = answer_of(counts)
    return m


def _node_at(tree, line, column):
    best = None
    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
            if not isinstance(node, ast.JoinedStr) and not isinstance(node, ast.BinOp):
                continue
        if getattr(node, "lineno", -1) != line or getattr(node, "col_offset", -1) != column:
            continue
        if best is None or type(node) is ast.Constant:
            best = node
    return best


def counts_of(rows, pairs, files_scanned, hits, reads, published_hits):
    def hist(values):
        out = {}
        for v in values:
            out[v] = out.get(v, 0) + 1
        return out

    by_match = {k: 0 for k in MATCH_CLASSES}
    by_consumer = {k: 0 for k in CONSUMER_CLASSES}
    for row in rows:
        for t in row["targets"]:
            for n in t["literals_naming"]:
                by_match[n["match"]] = by_match.get(n["match"], 0) + 1
                by_consumer[n["consumer_class"]] = by_consumer.get(n["consumer_class"], 0) + 1
    loader_hist = {}
    for row in rows:
        for c in row["dynamic_loader_calls"]:
            loader_hist[c["consumer_class"]] = loader_hist.get(c["consumer_class"], 0) + 1
    face_measured = sum(len(t["spellings"]["faces"]) for row in rows for t in row["targets"])
    face_unmeasured = sum(len(t["spellings"]["face_constants_unmeasured"])
                          for row in rows for t in row["targets"])
    face_absent = sum(len(t["spellings"].get("face_constants_absent") or [])
                      for row in rows for t in row["targets"])
    counts = {
        "python_files_scanned": files_scanned,
        "counted_read_lines": len(reads),
        "counted_row_keys": len({r["key"] for r in reads if r["key"]}),
        "hits_re_derived": hits,
        "hits_published_by_e646": published_hits,
        "distinct_hit_modules": len(rows),
        "read_modules_involved": len({p["read_module"] for p in pairs}),
        "hit_modules_with_a_naming_literal": sum(
            1 for r in rows if any(t["literals_naming_count"] for t in r["targets"])),
        "string_literals_examined": sum(r["literals_examined"] for r in rows),
        "string_literals_published": sum(len(r["literals"]) for r in rows),
        "string_literals_elided": sum(r["literals_elided"] for r in rows),
        "unresolved_strings": sum(len(r["unresolved_strings"]) for r in rows),
        "literals_naming_a_target": sum(by_match.values()),
        "literals_by_match_class": by_match,
        "literals_by_consumer_class": by_consumer,
        "dynamic_loader_calls": sum(loader_hist.values()),
        "dynamic_loader_calls_by_class": loader_hist,
        "dynamic_loader_calls_with_a_measured_literal": sum(
            1 for r in rows for c in r["dynamic_loader_calls"]
            if c["argument_is_a_measured_literal"]),
        "face_constants_measured": face_measured,
        "face_constants_unmeasured": face_unmeasured,
        "face_constants_absent": face_absent,
        "pairs": len(pairs),
        "pairs_by_reach": hist([p["reach"] for p in pairs]),
        "hit_module_class_histogram": hist([r["module_class"] for r in rows]),
    }
    counts["pairs"] = counts.get("pairs", 0)
    return counts


def decide(c):
    if not c.get("hits_re_derived"):
        return V_NO_HITS
    if not c.get("pairs"):
        return V_OFF_POPULATION
    reaches = c.get("pairs_by_reach") or {}
    best = max([SEVERITY.get(k, 0) * v for k, v in reaches.items()] or [0])
    if best >= SEVERITY["import_string_reach"]:
        return V_IMPORT_REACH
    if best == SEVERITY["file_text_or_face_read"]:
        return V_FILE_ONLY_REACH
    if best in (SEVERITY["loader_machinery_without_a_module_name"],
                SEVERITY["path_string_only"]):
        return V_MACHINERY_ONLY
    if best == SEVERITY["string_not_consumed"]:
        return V_UNCONSUMED
    return V_NO_LITERAL


def answer_of(c):
    reaches = c.get("pairs_by_reach") or {}
    return ("%d file(s), %d counted read line(s) over %d key(s); %d cross-module hit(s) re-derived "
            "(E646 published %s) in %d module(s) against %d read module(s); %d string(s) examined of "
            "which %d are published and %d elided, %d built from an expression; %d literal(s) name a "
            "target, by class %s, consumed by %s; %d dynamic loader call(s) in the hit modules of "
            "which %d carry a measured literal; the %d hit x read pair(s) split %s"
            % (c["python_files_scanned"], c["counted_read_lines"], c["counted_row_keys"],
               c["hits_re_derived"], c["hits_published_by_e646"], c["distinct_hit_modules"],
               c["read_modules_involved"], c["string_literals_examined"],
               c["string_literals_published"], c["string_literals_elided"],
               c["unresolved_strings"], c["literals_naming_a_target"],
               json.dumps(c["literals_by_match_class"], sort_keys=True),
               json.dumps(c["literals_by_consumer_class"], sort_keys=True),
               c["dynamic_loader_calls"],
               c["dynamic_loader_calls_with_a_measured_literal"], c["pairs"],
               json.dumps(reaches, sort_keys=True)))


# ---------------------------------------------------------------- gate
def face_from(m):
    return {
        "study": STUDY,
        "date": TODAY,
        "evidence_cutoff": TODAY,
        "source_face": SOURCE_FACE,
        "method": m["method"],
        "population_source": m["population_source"],
        "counts": m["counts"],
        "rows": m["rows"],
        "pairs": m["pairs"],
        "limits": m["limits"],
        "verdict": m["verdict"],
        "answer": m["answer"],
    }


COUNT_KEYS = (
    "counted_read_lines", "counted_row_keys", "hits_re_derived", "distinct_hit_modules",
    "read_modules_involved", "hit_modules_with_a_naming_literal", "string_literals_examined",
    "string_literals_published", "string_literals_elided", "unresolved_strings",
    "literals_naming_a_target", "dynamic_loader_calls",
    "dynamic_loader_calls_with_a_measured_literal", "face_constants_measured",
    "face_constants_unmeasured", "face_constants_absent", "pairs",
)


def live_counts(rows, pairs):
    by_match = {k: 0 for k in MATCH_CLASSES}
    by_consumer = {k: 0 for k in CONSUMER_CLASSES}
    for row in rows:
        for t in row.get("targets") or []:
            for n in t.get("literals_naming") or []:
                by_match[n.get("match")] = by_match.get(n.get("match"), 0) + 1
                by_consumer[n.get("consumer_class")] = by_consumer.get(n.get("consumer_class"), 0) + 1
    loader_hist = {}
    for row in rows:
        for c in row.get("dynamic_loader_calls") or []:
            loader_hist[c.get("consumer_class")] = loader_hist.get(c.get("consumer_class"), 0) + 1
    live = {
        "hits_re_derived": sum(len(r.get("hit_lines") or []) for r in rows),
        "distinct_hit_modules": len({r.get("module") for r in rows}),
        "read_modules_involved": len({p.get("read_module") for p in pairs}),
        "hit_modules_with_a_naming_literal": sum(
            1 for r in rows if any((t.get("literals_naming_count") or 0) for t in r.get("targets") or [])),
        "string_literals_examined": sum(r.get("literals_examined") or 0 for r in rows),
        "string_literals_published": sum(len(r.get("literals") or []) for r in rows),
        "string_literals_elided": sum(r.get("literals_elided") or 0 for r in rows),
        "unresolved_strings": sum(len(r.get("unresolved_strings") or []) for r in rows),
        "literals_naming_a_target": sum(by_match.values()),
        "dynamic_loader_calls": sum(loader_hist.values()),
        "dynamic_loader_calls_with_a_measured_literal": sum(
            1 for r in rows for c in r.get("dynamic_loader_calls") or []
            if c.get("argument_is_a_measured_literal")),
        "face_constants_measured": sum(len((t.get("spellings") or {}).get("faces") or [])
                                       for r in rows for t in r.get("targets") or []),
        "face_constants_unmeasured": sum(
            len((t.get("spellings") or {}).get("face_constants_unmeasured") or [])
            for r in rows for t in r.get("targets") or []),
        "face_constants_absent": sum(
            len((t.get("spellings") or {}).get("face_constants_absent") or [])
            for r in rows for t in r.get("targets") or []),
        "pairs": len(pairs),
        "literals_by_match_class": by_match,
        "literals_by_consumer_class": by_consumer,
        "dynamic_loader_calls_by_class": loader_hist,
        "pairs_by_reach": {},
    }
    for p in pairs:
        live["pairs_by_reach"][p.get("reach")] = live["pairs_by_reach"].get(p.get("reach"), 0) + 1
    live["hit_module_class_histogram"] = {}
    for r in rows:
        k = r.get("module_class")
        live["hit_module_class_histogram"][k] = live["hit_module_class_histogram"].get(k, 0) + 1
    return live


def face_problems(face):
    """Everything the smoke leg refuses, re-derived from the face's own rows and pairs."""
    problems = []
    if not face:
        return ["face is absent or empty"]
    rows = face.get("rows") or []
    pairs = face.get("pairs") or []
    c = face.get("counts") or {}
    live = live_counts(rows, pairs)
    for key in COUNT_KEYS:
        if key in ("counted_read_lines", "counted_row_keys"):
            continue
        if c.get(key) != live.get(key):
            problems.append("counts.%s does not re-add from the rows" % key)
    for key in ("literals_by_match_class", "literals_by_consumer_class",
                "dynamic_loader_calls_by_class", "pairs_by_reach", "hit_module_class_histogram"):
        if (c.get(key) or {}) != (live.get(key) or {}):
            problems.append("counts.%s is not the histogram the rows give" % key)
    if sum((c.get("literals_by_match_class") or {}).values()) != (c.get("literals_naming_a_target") or 0):
        problems.append("the match-class histogram is not the naming-literal count")
    if sum((c.get("pairs_by_reach") or {}).values()) != len(pairs):
        problems.append("the reach buckets do not add up to the pairs")
    if set(c.get("pairs_by_reach") or {}) - set(REACH_CLASSES):
        problems.append("a reach class outside the published set is reported")
    if sum((c.get("hit_module_class_histogram") or {}).values()) != len(rows):
        problems.append("the module-class histogram is not the per-module count")
    # every pair's reach must be the one its own naming literals force
    for p in pairs:
        row = next((r for r in rows if r.get("module") == p.get("hit_module")), None)
        if row is None:
            problems.append("pair names a module with no row: %s" % p.get("hit_module"))
            break
        target = next((t for t in row.get("targets") or []
                       if t.get("read_module") == p.get("read_module")), None)
        if target is None:
            problems.append("pair names a target its module row does not carry")
            break
        want = reach_class_of(target.get("literals_naming") or [])
        if p.get("reach") != want or target.get("reach") != want:
            problems.append("pair %s x %s is classified %r but its own literals force %r"
                            % (p.get("hit_module"), p.get("read_module"), p.get("reach"), want))
            break
        if (p.get("naming_literals") or 0) != (target.get("literals_naming_count") or 0):
            problems.append("pair %s x %s publishes a naming count its target does not carry"
                            % (p.get("hit_module"), p.get("read_module")))
            break
        for n in target.get("literals_naming") or []:
            if n.get("match") not in MATCH_CLASSES:
                problems.append("a naming literal carries an unpublished match class")
                break
            if n.get("consumer_class") not in CONSUMER_CLASSES:
                problems.append("a naming literal carries an unpublished consumer class")
                break
    for r in rows:
        if (r.get("literals_examined") or 0) != ((len(r.get("literals") or []))
                                                + (r.get("literals_elided") or 0)):
            problems.append("module %s publishes an examined count its literal list does not add to"
                            % r.get("module"))
            break
        if (r.get("literals_elided") or 0) and len(r.get("literals") or []) < MAX_LITERALS_PER_MODULE:
            problems.append("module %s elides literals it could have published" % r.get("module"))
            break
        if not r.get("targets"):
            problems.append("module %s carries no target row" % r.get("module"))
            break
    if c.get("hits_published_by_e646") is not None \
            and c.get("hits_published_by_e646") != c.get("hits_re_derived"):
        problems.append("the re-derived hit count is not the one E646 published")
    if decide(live) != face.get("verdict"):
        problems.append("the published verdict is not the one the counts force")
    if face.get("verdict") == V_NO_LITERAL and (live.get("literals_naming_a_target") or 0):
        problems.append("the no-literal verdict is published with naming literals")
    if face.get("verdict") == V_IMPORT_REACH and not any(
            p.get("reach") == "import_string_reach" for p in pairs):
        problems.append("the import-reach verdict is published with no import-reaching pair")
    if face.get("verdict") == V_FILE_ONLY_REACH and any(
            p.get("reach") == "import_string_reach" for p in pairs):
        problems.append("the file-only verdict is published with an import-reaching pair")
    return problems


def write_face(out_dir, doc, face=FACE, latest=LATEST):
    os.makedirs(out_dir, exist_ok=True)
    for name in (face, latest):
        path = os.path.join(out_dir, name)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
        say("run: %s" % os.path.relpath(path, ROOT))


def build(root=ROOT, out_dir=None):
    doc = face_from(measure(root))
    write_face(out_dir or OUTDIR, doc)
    c = doc["counts"]
    say("run: files=%d reads=%d hits=%d(e646 %s) modules=%d targets=%d pairs=%d by_reach=%s"
        % (c["python_files_scanned"], c["counted_read_lines"], c["hits_re_derived"],
           c["hits_published_by_e646"], c["distinct_hit_modules"], c["read_modules_involved"],
           c["pairs"], json.dumps(c["pairs_by_reach"], sort_keys=True)))
    say("run: literals=%d naming=%d unresolved=%d loaders=%d"
        % (c["string_literals_examined"], c["literals_naming_a_target"],
           c["unresolved_strings"], c["dynamic_loader_calls"]))
    say("run: verdict=" + doc["verdict"])
    say("run: answer=" + doc["answer"])
    return doc, []


# ---------------------------------------------------------------- selftest
def _row(module="a.py", cls="production_module", literals=None, targets=None, loaders=None):
    literals = literals if literals is not None else []
    targets = targets if targets is not None else []
    return {"module": module, "module_class": cls,
            "hit_lines": [{"line": 3, "column": 0, "keys": ["k"], "row_keys_named": ["k"]}],
            "literals_examined": len(literals), "literals": literals,
            "literals_elided": 0, "unresolved_strings": [],
            "dynamic_loader_calls": loaders or [], "targets": targets,
            "reach_classes": sorted({t["reach"] for t in targets})}


def _target(read_module="b.py", naming=None):
    naming = naming if naming is not None else []
    return {"read_module": read_module,
            "spellings": {"path": read_module, "basename": os.path.basename(read_module),
                          "stem": os.path.basename(read_module)[:-3], "dotted": "b",
                          "faces": [], "face_constants_unmeasured": []},
            "literals_naming": naming, "literals_naming_count": len(naming),
            "reach": reach_class_of(naming)}


def _pair(row, target):
    return {"hit_module": row["module"], "read_module": target["read_module"], "keys": ["k"],
            "naming_literals": target["literals_naming_count"], "reach": target["reach"],
            "match_classes": sorted({n["match"] for n in target["literals_naming"]}),
            "consumer_classes": sorted({n["consumer_class"] for n in target["literals_naming"]})}


def _lit(match="exact_stem", consumer_class="no_call", value="b"):
    return {"line": 1, "column": 0, "value": value, "built": "constant", "match": match,
            "consumer": None if consumer_class == "no_call" else consumer_class,
            "consumer_class": consumer_class, "bound_name": None, "hops": 1}


def _counts(rows, pairs, published=None):
    return counts_of(rows, pairs, 10, sum(len(r["hit_lines"]) for r in rows),
                     [{"key": "k"}], published)


def selftest():
    legs = []

    def leg(name, fn):
        try:
            fn()
            legs.append((name, True))
            say("PASS :: " + name)
        except AssertionError as exc:
            legs.append((name, False))
            say("FAIL :: %s :: %s" % (name, exc))

    def literals_include_plain_and_folded_strings():
        tree = ast.parse('A = "x"\nB = "y" + "z"\nC = f"p{1}"\nD = "q"\n')
        lits, unresolved = collect_strings(tree)
        values = sorted(l["value"] for l in lits)
        assert "x" in values and "yz" in values, values
        assert len(unresolved) == 1, unresolved

    def an_all_constant_fstring_is_measured():
        tree = ast.parse('F = f"ab"\n')
        lits, unresolved = collect_strings(tree)
        assert [l["value"] for l in lits] == ["ab"], lits
        assert unresolved == [], unresolved

    def percent_formatting_is_unresolved_not_matched():
        tree = ast.parse('F = "a%s" % name\n')
        lits, unresolved = collect_strings(tree)
        assert lits == [], lits
        assert unresolved and unresolved[0]["why"] == "percent_formatting", unresolved

    def spellings_come_from_measurement():
        path = e640._fixture_path('FACE = "cost_latest.json"\n'
                                  'FACE_NAME = "named_latest.json"\n'
                                  'LATEST = 3\n'
                                  'UPSTREAM_FACE = os.path.join("results", "x.json")\n')
        try:
            sp = spellings_of(path)
            assert sp["basename"].endswith(".py"), sp
            assert sp["stem"] == os.path.basename(path)[:-3], sp
            assert sp["faces"] == ["cost_latest.json", "named_latest.json"], sp
            assert [u["constant"] for u in sp["face_constants_unmeasured"]] == \
                ["LATEST", "UPSTREAM_FACE"], sp
            assert sp["face_constants_absent"] == [], sp
        finally:
            try:
                os.remove(path)
            except OSError:
                pass

    def a_module_without_the_frozen_names_is_published_as_absent():
        path = e640._fixture_path('X = 1\n')
        try:
            sp = spellings_of(path)
            assert sp["face_constants_absent"] == ["FACE", "LATEST"], sp
            assert sp["faces"] == [] and sp["face_constants_unmeasured"] == [], sp
        finally:
            try:
                os.remove(path)
            except OSError:
                pass

    def exact_classes_beat_containment():
        sp = {"path": "scripts/e382_x.py", "basename": "e382_x.py", "stem": "e382_x",
              "dotted": "scripts.e382_x", "faces": ["key_latest.json"], "face_constants_unmeasured": []}
        assert match_class("scripts/e382_x.py", sp) == "exact_path"
        assert match_class("./scripts/e382_x.py", sp) == "exact_path"
        assert match_class("e382_x.py", sp) == "exact_basename"
        assert match_class("e382_x", sp) == "exact_stem"
        assert match_class("scripts.e382_x", sp) == "exact_dotted"
        assert match_class("key_latest.json", sp) == "exact_face"

    def containment_needs_a_whole_token():
        sp = {"path": "scripts/e382_x.py", "basename": "e382_x.py", "stem": "e382_x",
              "dotted": "scripts.e382_x", "faces": [], "face_constants_unmeasured": []}
        assert match_class("see e382_x for detail", sp) == "token_contains_stem"
        assert match_class("e382_xy", sp) is None, match_class("e382_xy", sp)

    def a_consumer_is_the_call_that_takes_the_string():
        tree = ast.parse('import importlib\nm = importlib.import_module("e382_x")\n')
        parents = parents_of(tree)
        node = next(n for n in ast.walk(tree)
                    if isinstance(n, ast.Constant) and n.value == "e382_x")
        cons = consumption(parents, node)
        assert cons["consumer_class"] == "module_import", cons
        assert cons["bound_name"] == "m", cons

    def open_is_a_file_consumer_and_an_unused_string_is_none():
        tree = ast.parse('f = open("a.py")\nU = "a.py"\n')
        parents = parents_of(tree)
        first = next(n for n in ast.walk(tree)
                     if isinstance(n, ast.Constant) and n.value == "a.py"
                     and n.lineno == 1)
        assert consumption(parents, first)["consumer_class"] == "file_open"
        second = next(n for n in ast.walk(tree)
                      if isinstance(n, ast.Constant) and n.value == "a.py"
                      and n.lineno == 2)
        assert consumption(parents, second)["consumer_class"] == "no_call"

    def sys_path_and_join_are_their_own_classes():
        assert consumer_class_of("sys.path.append") == "sys_path"
        assert consumer_class_of("os.path.join") == "path_join"
        assert consumer_class_of("importlib.import_module") == "module_import"
        assert consumer_class_of("exec") == "exec_or_eval"
        assert consumer_class_of("print") == "other_call"

    def loader_calls_are_counted_with_or_without_a_literal():
        tree = ast.parse('import importlib\n'
                         'importlib.import_module("x")\n'
                         'importlib.import_module(name)\n'
                         'open(some_path)\n')
        got = dynamic_loader_calls(tree, parents_of(tree))
        classes = sorted(c["consumer_class"] for c in got)
        assert classes == ["file_open", "module_import", "module_import"], classes
        assert sum(1 for c in got if c["argument_is_a_measured_literal"]) == 1, got

    def import_reach_is_reachable():
        t = _target(naming=[_lit("exact_stem", "module_import", "b")])
        assert t["reach"] == "import_string_reach", t
        assert decide(_counts([_row(targets=[t])], [_pair(_row(targets=[t]), t)])) == V_IMPORT_REACH

    def file_only_reach_is_reachable():
        t = _target(naming=[_lit("exact_path", "file_open", "b.py")])
        r = _row(targets=[t])
        assert t["reach"] == "file_text_or_face_read", t
        assert decide(_counts([r], [_pair(r, t)])) == V_FILE_ONLY_REACH

    def machinery_only_reach_is_reachable():
        t = _target(naming=[_lit("token_contains_stem", "sys_path", "x/b")])
        r = _row(targets=[t])
        assert t["reach"] == "loader_machinery_without_a_module_name", t
        assert decide(_counts([r], [_pair(r, t)])) == V_MACHINERY_ONLY

    def unconsumed_reach_is_reachable():
        t = _target(naming=[_lit("exact_stem", "no_call", "b")])
        r = _row(targets=[t])
        assert t["reach"] == "string_not_consumed", t
        assert decide(_counts([r], [_pair(r, t)])) == V_UNCONSUMED

    def no_literal_reach_is_reachable():
        t = _target(naming=[])
        r = _row(targets=[t])
        assert t["reach"] == "no_literal_names_the_target", t
        assert decide(_counts([r], [_pair(r, t)])) == V_NO_LITERAL

    def no_hits_and_off_population_are_reachable():
        assert decide({"hits_re_derived": 0, "pairs": 0}) == V_NO_HITS
        assert decide({"hits_re_derived": 3, "pairs": 0}) == V_OFF_POPULATION

    def face_problems_accepts_a_sound_face():
        t = _target(naming=[_lit("exact_stem", "open" if False else "other_call", "b")])
        r = _row(literals=[{"line": 1, "column": 0, "value": "b", "built": "constant"}],
                 targets=[t])
        p = _pair(r, t)
        face = {"rows": [r], "pairs": [p], "counts": _counts([r], [p])}
        face["verdict"] = decide(face["counts"])
        assert face_problems(face) == [], face_problems(face)

    def face_problems_catches_a_drifted_count():
        t = _target(naming=[_lit()])
        r = _row(targets=[t])
        p = _pair(r, t)
        face = {"rows": [r], "pairs": [p], "counts": _counts([r], [p])}
        face["counts"]["literals_naming_a_target"] += 1
        assert any("does not re-add" in x for x in face_problems(face)), face_problems(face)

    def face_problems_catches_a_verdict_its_counts_do_not_force():
        t = _target(naming=[])
        r = _row(targets=[t])
        p = _pair(r, t)
        face = {"rows": [r], "pairs": [p], "counts": _counts([r], [p])}
        face["verdict"] = V_IMPORT_REACH
        assert any("verdict" in x for x in face_problems(face)), face_problems(face)

    def face_problems_catches_a_pair_whose_literals_force_another_reach():
        t = _target(naming=[_lit("exact_stem", "module_import", "b")])
        r = _row(targets=[t])
        p = _pair(r, t)
        p["reach"] = "string_not_consumed"
        face = {"rows": [r], "pairs": [p], "counts": _counts([r], [p])}
        assert any("classified" in x for x in face_problems(face)), face_problems(face)

    def face_problems_catches_an_examined_count_the_literal_list_does_not_add_to():
        t = _target(naming=[])
        r = _row(targets=[t])
        r["literals_examined"] = 5
        p = _pair(r, t)
        face = {"rows": [r], "pairs": [p], "counts": _counts([r], [p])}
        assert any("examined count" in x for x in face_problems(face)), face_problems(face)

    def face_problems_catches_a_reach_class_outside_the_set():
        t = _target(naming=[_lit()])
        r = _row(targets=[t])
        p = _pair(r, t)
        face = {"rows": [r], "pairs": [p], "counts": _counts([r], [p])}
        face["counts"]["pairs_by_reach"] = {"made_up": 1}
        assert any("outside the published set" in x for x in face_problems(face)), face_problems(face)

    def face_problems_catches_a_reconciliation_that_moves():
        t = _target(naming=[_lit()])
        r = _row(targets=[t])
        p = _pair(r, t)
        face = {"rows": [r], "pairs": [p], "counts": _counts([r], [p], published=9)}
        face["verdict"] = decide(face["counts"])
        assert any("E646" in x for x in face_problems(face)), face_problems(face)

    def answer_names_the_numbers():
        t = _target(naming=[_lit("exact_stem", "module_import", "b")])
        r = _row(targets=[t])
        p = _pair(r, t)
        a = answer_of(_counts([r], [p]))
        for token in ("1 counted read line", "1 literal(s) name a target", "split"):
            assert token in a, (token, a)

    for name, fn in [
        ("literals_include_plain_and_folded_strings", literals_include_plain_and_folded_strings),
        ("an_all_constant_fstring_is_measured", an_all_constant_fstring_is_measured),
        ("percent_formatting_is_unresolved_not_matched",
         percent_formatting_is_unresolved_not_matched),
        ("spellings_come_from_measurement", spellings_come_from_measurement),
        ("a_module_without_the_frozen_names_is_published_as_absent",
         a_module_without_the_frozen_names_is_published_as_absent),
        ("exact_classes_beat_containment", exact_classes_beat_containment),
        ("containment_needs_a_whole_token", containment_needs_a_whole_token),
        ("a_consumer_is_the_call_that_takes_the_string", a_consumer_is_the_call_that_takes_the_string),
        ("open_is_a_file_consumer_and_an_unused_string_is_none",
         open_is_a_file_consumer_and_an_unused_string_is_none),
        ("sys_path_and_join_are_their_own_classes", sys_path_and_join_are_their_own_classes),
        ("loader_calls_are_counted_with_or_without_a_literal",
         loader_calls_are_counted_with_or_without_a_literal),
        ("import_reach_is_reachable", import_reach_is_reachable),
        ("file_only_reach_is_reachable", file_only_reach_is_reachable),
        ("machinery_only_reach_is_reachable", machinery_only_reach_is_reachable),
        ("unconsumed_reach_is_reachable", unconsumed_reach_is_reachable),
        ("no_literal_reach_is_reachable", no_literal_reach_is_reachable),
        ("no_hits_and_off_population_are_reachable", no_hits_and_off_population_are_reachable),
        ("face_problems_accepts_a_sound_face", face_problems_accepts_a_sound_face),
        ("face_problems_catches_a_drifted_count", face_problems_catches_a_drifted_count),
        ("face_problems_catches_a_verdict_its_counts_do_not_force",
         face_problems_catches_a_verdict_its_counts_do_not_force),
        ("face_problems_catches_a_pair_whose_literals_force_another_reach",
         face_problems_catches_a_pair_whose_literals_force_another_reach),
        ("face_problems_catches_an_examined_count_the_literal_list_does_not_add_to",
         face_problems_catches_an_examined_count_the_literal_list_does_not_add_to),
        ("face_problems_catches_a_reach_class_outside_the_set",
         face_problems_catches_a_reach_class_outside_the_set),
        ("face_problems_catches_a_reconciliation_that_moves",
         face_problems_catches_a_reconciliation_that_moves),
        ("answer_names_the_numbers", answer_names_the_numbers),
    ]:
        leg(name, fn)
    ok = sum(1 for _, good in legs if good)
    say("selftest: %d/%d legs green" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


# ---------------------------------------------------------------- CLI
def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run")
    args = ap.parse_args(argv[1:])
    cmd = args.cmd.lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "check":
        doc, problems = build(root=ROOT)
        problems = problems + face_problems(doc)
        say("problems=" + json.dumps(problems, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "verify":
        path = os.path.join(OUTDIR, FACE)
        if not os.path.exists(path):
            say("no face at %s" % path)
            return 1
        doc = json.load(io.open(path, encoding="utf-8"))
        problems = face_problems(doc)
        say("problems=" + json.dumps(problems, ensure_ascii=False))
        return 0 if not problems else 1
    doc, problems = build(root=ROOT)
    problems = problems + face_problems(doc)
    if problems:
        say("PROBLEMS: " + "; ".join(problems))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))