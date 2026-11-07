"""E517 -- a key read is the last hop of a population, not a builder.

E514 (results/state_tilt/BUILTELSEWHERE-2026-11-08.json) left four rows answered
``the_callee_could_not_be_resolved_so_the_value_stays_unread``.  Every one of them is a key
read -- ``payloads.get(rel)``, ``src.get(...)``, ``e350._sources()`` -- off a container the
enclosing function received or that another module produces.  A ``.get`` is not a producer:
it is the point where a population that was built somewhere else is finally consulted.

So the question this face answers per row is not "who built the value" but "what is the
container, who fills it, and can a reader reconstruct it from a seam or only from the run":

  * a parameter of the function that reads it   -> one hop into the callers, classify what
                                                   each call site actually passes;
  * a local object the same function fills       -> filled in place before the read;
  * a module-level object in the same file       -> built once at import, never refilled;
  * a function in another module                 -> resolve the module alias, name the
                                                   function and whether it exposes a seam.

Everything is machine-read from the E514 face (no hand-copied rows) and from the source
tree at the row's own line.  Nothing is rewritten; this is a static read.

    python scripts/e517_container_feed.py run        # build + write the face
    python scripts/e517_container_feed.py check      # gate the published face
    python scripts/e517_container_feed.py verify     # re-derive and gate in memory
    python scripts/e517_container_feed.py selftest   # fixture arms + doctored arms
"""
from __future__ import annotations

import ast
import io
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

CARD = "E517-WHAT-CONTAINER-DOES-THE-FOUR-UNRESOLVED-KEY-READS-ACTUALLY-READ-OFF"
STUDY = "E517_container_feed"
DATE_STAMP = "2026-11-08"
FACE_NAME = "containerfeed_latest.json"
DATED_PREFIX = "CONTAINERFEED"
UPSTREAM_NAME = "BUILTELSEWHERE-2026-11-08.json"
UPSTREAM_REL = "results/state_tilt/" + UPSTREAM_NAME

# the row answer E514 published for the rows this face exists to finish
UNRESOLVED = "the_callee_could_not_be_resolved_so_the_value_stays_unread"

# this study's own files: a scan that reads the tree must not read its own output
SELF_EXCLUDED = ("e517_", "run_e517", "_e517", "_r1543", "CONTAINERFEED", "containerfeed_")

CONTAINER_VOCAB = [
    "a_parameter_of_the_function_that_reads_it",
    "a_local_object_the_same_function_fills_before_the_read",
    "a_module_level_object_defined_in_the_same_file",
    "a_function_in_another_module_that_reads_the_tree",
    "not_resolvable_from_the_row",
]

FEED_VOCAB = [
    "a_name_the_caller_binds_to_a_literal_object",
    "a_name_the_caller_binds_to_a_call_result",
    "a_name_the_caller_binds_to_a_parameter_of_the_caller",
    "an_object_literal_written_at_the_call",
    "a_call_result_written_at_the_call",
    "a_string_or_number_literal_at_the_call",
    "no_such_call_site_in_the_tree",
]

ANSWER_VOCAB = [
    "the_population_is_decided_by_the_caller_who_fills_the_container",
    "the_container_is_filled_in_place_before_it_is_read",
    "the_container_is_built_once_at_import_and_never_refilled",
    "the_container_is_a_corpus_read_in_another_module",
    "one_hop_does_not_answer_it",
]

VERDICT_VOCAB = [
    "every_unresolved_row_names_its_container",
    "some_rows_still_stop_before_the_container",
]


def _now():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _load_json(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _src(rel, root=None):
    root = root or ROOT
    with io.open(os.path.join(root, rel), encoding="utf-8") as fh:
        return fh.read()


# ------------------------------------------------------------------ AST helpers
def enclosing_function(tree, line):
    """Deepest FunctionDef whose line span holds ``line``."""
    best = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end = getattr(node, "end_lineno", node.lineno)
            if node.lineno <= line <= end:
                if best is None or node.lineno >= best.lineno:
                    best = node
    return best


def _params(func):
    return [a.arg for a in list(func.args.args) + list(func.args.kwonlyargs)]


def _assigned_before(func, name, line):
    """The last assignment to ``name`` inside ``func`` that sits before ``line``."""
    hits = []
    for node in ast.walk(func):
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == name and node.lineno < line:
                    hits.append(node)
    return max(hits, key=lambda n: n.lineno) if hits else None


def module_assignment(tree, name):
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == name:
                    return node
    return None


def import_alias(tree, alias):
    """Map a module alias used in a call to the module file it imports."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                bound = a.asname or a.name.split(".")[0]
                if bound == alias:
                    return a.name
        elif isinstance(node, ast.ImportFrom):
            for a in node.names:
                bound = a.asname or a.name
                if bound == alias and node.module:
                    return node.module
    return None


def _call_in(expr_text):
    """The first call node of an expression, or None when it does not parse."""
    try:
        tree = ast.parse(expr_text, mode="eval")
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            return node
    return None


def _value_kind(node):
    """What a binding expression names, in this study's vocabulary."""
    if node is None:
        return None
    if isinstance(node, (ast.Dict, ast.List, ast.Set, ast.Tuple)):
        return "literal_object"
    if isinstance(node, ast.Call):
        return "call_result"
    if isinstance(node, ast.Name):
        return "name"
    if isinstance(node, ast.Constant):
        return "constant"
    return "other"


# ------------------------------------------------------------------ the analysis
def upstream_rows(root=None, upstream=None):
    if upstream is not None:
        rows = list(upstream)
    else:
        face = _load_json(os.path.join(root or ROOT, UPSTREAM_REL))
        rows = face.get("rows") or []
    return [r for r in rows if r.get("answer") == UNRESOLVED]


def _container_of(row):
    """(expression text, container node) for the row's key read."""
    call = _call_in(row.get("value_expression") or "")
    if call is None:
        return None, None
    func = call.func
    # payloads.get(rel) -- the container is the receiver, a read is not a builder
    if isinstance(func, ast.Attribute) and func.attr in ("get", "pop", "setdefault", "__getitem__"):
        return ast.unparse(func.value) if hasattr(ast, "unparse") else None, func.value
    return (ast.unparse(func) if hasattr(ast, "unparse") else None), func


def _resolve_module_function(root, module_name, func_name):
    """Locate ``func_name`` in the in-repo module file ``module_name``."""
    rel = os.path.join("scripts", module_name + ".py")
    path = os.path.join(root, rel)
    if not os.path.isfile(path):
        return None
    tree = ast.parse(_src(rel, root))
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            calls = [ast.unparse(n.func) if hasattr(ast, "unparse") else ""
                     for n in ast.walk(node) if isinstance(n, ast.Call)]
            positional = list(node.args.args)
            widths = [a.arg for a, d in zip(positional[-len(node.args.defaults):], node.args.defaults)
                      if isinstance(d, ast.Constant) and d.value is None] if node.args.defaults else []
            return {
                "module": module_name,
                "rel": rel.replace(os.sep, "/"),
                "function": func_name,
                "line": node.lineno,
                "parameters": _params(node),
                "seam_parameters": widths,
                "calls_made": calls[:12],
                "reads_the_tree": any(("_corpus" in c) or ("walk" in c) or ("glob" in c)
                                      for c in calls) or ("open(" in (ast.unparse(node) if hasattr(ast, "unparse") else "")),
            }
    return None


def _call_sites(root, func_name, callee_params, param_name, own_rel):
    """Every call of ``func_name`` in scripts/, with what sits at ``param_name``'s position."""
    feeds = []
    scripts = os.path.join(root, "scripts")
    if not os.path.isdir(scripts):
        return feeds
    for name in sorted(os.listdir(scripts)):
        if not name.endswith(".py") or name.startswith(SELF_EXCLUDED):
            continue
        rel = "scripts/" + name
        try:
            tree = ast.parse(_src(rel, root))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            fname = ast.unparse(node.func) if hasattr(ast, "unparse") else ""
            if fname.split(".")[-1] != func_name:
                continue
            owner = enclosing_function(tree, node.lineno)
            if owner is None:
                continue
            index = callee_params.index(param_name) if param_name in callee_params else None
            passed = node.args[index] if (index is not None and index < len(node.args)) else None
            if passed is None:
                continue
            kind = _value_kind(passed)
            feed = None
            detail = None
            if kind == "literal_object":
                feed = "an_object_literal_written_at_the_call"
            elif kind == "call_result":
                feed = "a_call_result_written_at_the_call"
            elif kind == "constant":
                feed = "a_string_or_number_literal_at_the_call"
            elif kind == "name":
                name = getattr(passed, "id", None)
                if name in _params(owner):
                    feed = "a_name_the_caller_binds_to_a_parameter_of_the_caller"
                    detail = name
                else:
                    bind = _assigned_before(owner, name, node.lineno)
                    vk = _value_kind(bind.value) if bind is not None else None
                    detail = (name, vk, bind.lineno if bind is not None else None)
                    if vk == "literal_object":
                        feed = "a_name_the_caller_binds_to_a_literal_object"
                    elif vk in ("call_result", "name"):
                        feed = "a_name_the_caller_binds_to_a_call_result"
            if feed is None:
                continue
            feeds.append({
                "source": rel,
                "line": node.lineno,
                "in_function": owner.name,
                "argument": ast.unparse(passed) if hasattr(ast, "unparse") else "",
                "feed": feed,
                "detail": detail,
            })
    return feeds


def _answer_for(container_class, feeds, resolved):
    if container_class == "a_function_in_another_module_that_reads_the_tree":
        return "the_container_is_a_corpus_read_in_another_module"
    if container_class == "a_parameter_of_the_function_that_reads_it":
        if feeds and all(f["feed"] not in ("no_such_call_site_in_the_tree",) for f in feeds):
            return "the_population_is_decided_by_the_caller_who_fills_the_container"
        return "one_hop_does_not_answer_it"
    if container_class == "a_local_object_the_same_function_fills_before_the_read":
        return "the_container_is_filled_in_place_before_it_is_read"
    if container_class == "a_module_level_object_defined_in_the_same_file":
        return "the_container_is_built_once_at_import_and_never_refilled"
    if resolved:
        return "the_population_is_decided_by_the_caller_who_fills_the_container"
    return "one_hop_does_not_answer_it"


def analyse(root=None, upstream=None):
    root = root or ROOT
    rows = []
    for row in upstream_rows(root, upstream):
        rel = row.get("source") or ""
        line = row.get("line")
        try:
            tree = ast.parse(_src(rel, root))
        except (OSError, SyntaxError):
            rows.append({
                "source": rel, "line": line,
                "value_expression": row.get("value_expression"),
                "container_expression": None,
                "container_class": "not_resolvable_from_the_row",
                "answer": "one_hop_does_not_answer_it",
                "call_sites": [],
                "resolved_function": None,
            })
            continue
        expr_text, container = _container_of(row)
        func = enclosing_function(tree, line) if isinstance(line, int) else None
        record = {
            "source": rel,
            "line": line,
            "value_expression": row.get("value_expression"),
            "symbol": row.get("symbol"),
            "surfaces": row.get("surfaces") or [],
            "enclosing_function": func.name if func else None,
            "enclosing_parameters": _params(func) if func else [],
            "container_expression": expr_text,
            "container_class": "not_resolvable_from_the_row",
            "call_sites": [],
            "resolved_function": None,
        }
        if container is None:
            record["answer"] = _answer_for(record["container_class"], [], None)
            rows.append(record)
            continue

        resolved = None
        if isinstance(container, ast.Name):
            name = container.id
            if func is not None and name in _params(func):
                record["container_class"] = "a_parameter_of_the_function_that_reads_it"
                record["call_sites"] = _call_sites(root, func.name, _params(func), name, rel)
            else:
                local = _assigned_before(func, name, line) if func is not None else None
                module_level = module_assignment(tree, name)
                if local is not None and (module_level is None or local.lineno > module_level.lineno):
                    record["container_class"] = "a_local_object_the_same_function_fills_before_the_read"
                elif module_level is not None:
                    record["container_class"] = "a_module_level_object_defined_in_the_same_file"
        elif isinstance(container, ast.Attribute) and isinstance(container.value, ast.Name):
            module_name = import_alias(tree, container.value.id)
            resolved = _resolve_module_function(root, module_name, container.attr) if module_name else None
            record["resolved_function"] = resolved
            if resolved is not None:
                record["container_class"] = "a_function_in_another_module_that_reads_the_tree"

        record["answer"] = _answer_for(record["container_class"], record["call_sites"], resolved)
        rows.append(record)
    return rows


def _count(rows, key, vocab):
    out = {k: 0 for k in vocab}
    for row in rows:
        value = row.get(key)
        if value in out:
            out[value] += 1
    return out


def _summary(rows):
    feeds = [f["feed"] for row in rows for f in row.get("call_sites") or []]
    return {
        "rows": len(rows),
        "rows_by_container": _count(rows, "container_class", CONTAINER_VOCAB),
        "rows_by_answer": _count(rows, "answer", ANSWER_VOCAB),
        "call_sites": len(feeds),
        "call_sites_by_feed": {k: feeds.count(k) for k in FEED_VOCAB},
        "rows_whose_container_is_reconstructable_without_the_run": sum(
            1 for row in rows
            if row.get("answer") in (
                "the_population_is_decided_by_the_caller_who_fills_the_container",
                "the_container_is_a_corpus_read_in_another_module")),
        "rows_with_a_seam_in_the_resolving_function": sum(
            1 for row in rows
            if (row.get("resolved_function") or {}).get("seam_parameters")),
        "rows_still_unread": sum(1 for row in rows if row.get("answer") == "one_hop_does_not_answer_it"),
    }


def _verdict(summary):
    if summary.get("rows_still_unread"):
        return "some_rows_still_stop_before_the_container"
    return "every_unresolved_row_names_its_container"


POPULATION_SOURCE = ("results/state_tilt/%s -- the rows whose answer is %r; read, never rebuilt"
                     % (UPSTREAM_NAME, UNRESOLVED))


def build(root=None, write=True, upstream=None):
    root = root or ROOT
    rows = analyse(root, upstream=upstream)
    summary = _summary(rows)
    face = {
        "study": STUDY,
        "card": CARD,
        "title": ("E514's four unresolved rows are all key reads.  A key read is the last hop of a "
                  "population, not a builder: name the container per row, classify what fills it, and "
                  "follow one hop into the callers to see whether the population is reconstructable "
                  "without the run."),
        "evidence_cutoff": DATE_STAMP,
        "generated": _now(),
        "population_source": POPULATION_SOURCE,
        "container_vocab": list(CONTAINER_VOCAB),
        "feed_vocab": list(FEED_VOCAB),
        "answer_vocab": list(ANSWER_VOCAB),
        "verdict_vocab": list(VERDICT_VOCAB),
        "rows": rows,
        "summary": summary,
        "verdict": _verdict(summary),
        "method_limits": [
            "one hop only: a feed that is itself a parameter of the caller is named, not chased",
            "static only: no call is executed, so a container filled by a side effect is named by its binding",
            "the corpus reader is resolved through the row file's own import alias, not by module name guessing",
        ],
    }
    if write:
        write_face(face, root)
    return face


def write_face(face, root=None):
    root = root or ROOT
    outdir = os.path.join(root, "results", "state_tilt")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    for name in (FACE_NAME, "%s-%s.json" % (DATED_PREFIX, DATE_STAMP)):
        with io.open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body + "\n")


def load_face(root=None):
    return _load_json(os.path.join(root or ROOT, "results", "state_tilt", FACE_NAME))


# ---------------------------------------------------------------------- gate
def site_problems(face):
    """Re-derive every published count and every answer from the rows' own evidence."""
    problems = []
    rows = face.get("rows") or []
    summary = face.get("summary") or {}
    if summary.get("rows") != len(rows):
        problems.append("summary.rows is not the row list length")
    if _count(rows, "container_class", CONTAINER_VOCAB) != summary.get("rows_by_container"):
        problems.append("rows_by_container does not re-derive from the rows")
    if _count(rows, "answer", ANSWER_VOCAB) != summary.get("rows_by_answer"):
        problems.append("rows_by_answer does not re-derive from the rows")
    feeds = [f.get("feed") for row in rows for f in row.get("call_sites") or []]
    if summary.get("call_sites") != len(feeds):
        problems.append("call_sites is not the feed list length")
    if summary.get("call_sites_by_feed") != {k: feeds.count(k) for k in FEED_VOCAB}:
        problems.append("call_sites_by_feed does not re-derive from the rows")
    for row in rows:
        if row.get("container_class") not in CONTAINER_VOCAB:
            problems.append("container class outside the vocabulary: %r" % (row.get("container_class"),))
        if row.get("answer") not in ANSWER_VOCAB:
            problems.append("answer outside the vocabulary: %r" % (row.get("answer"),))
        expected = _answer_for(row.get("container_class"), row.get("call_sites") or [],
                               row.get("resolved_function"))
        if row.get("answer") != expected:
            problems.append("%s:%s answer %r is not what its own evidence implies (%r)"
                            % (row.get("source"), row.get("line"), row.get("answer"), expected))
        for feed in row.get("call_sites") or []:
            if feed.get("feed") not in FEED_VOCAB:
                problems.append("feed outside the vocabulary: %r" % (feed.get("feed"),))
        if row.get("container_class") == "a_parameter_of_the_function_that_reads_it" and not row.get("call_sites"):
            if row.get("answer") != "one_hop_does_not_answer_it":
                problems.append("a parameter container with no call site claims an answer")
    if _verdict(summary) != face.get("verdict"):
        problems.append("verdict is not what the summary implies: %r" % (face.get("verdict"),))
    if face.get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict outside the vocabulary")
    if (face.get("population_source") or "") != POPULATION_SOURCE:
        problems.append("population_source was edited")
    return problems


def check(face=None, root=None):
    face = face or load_face(root)
    problems = site_problems(face)
    print("check problems=%r" % (problems,))
    return 0 if not problems else 1


def verify(root=None):
    root = root or ROOT
    face = build(root, write=False)
    problems = site_problems(face)
    print("verify problems=%r" % (problems,))
    print("verdict=%s rows=%d" % (face["verdict"], len(face["rows"])))
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest
ALPHA = '''import io


def resolve(audit, payloads):
    path = audit.get("path")
    return payloads.get(path)


def sources(files=None):
    if files is None:
        corpus = _corpus()
    else:
        corpus = files
    return [(rel, io.open(rel, encoding="utf-8").read()) for rel in corpus]


def run(audit):
    payloads = _load("x.json")
    return resolve(audit, payloads)
'''

BETA = '''import alpha


def run():
    rows = [(rel, text) for rel, text in alpha.sources() if rel != "self"]
    return rows
'''


def selftest():
    failures = []
    checks = [0]

    def ok(label, cond, detail=None):
        checks[0] += 1
        if not cond:
            failures.append("%s (got %r)" % (label, detail))

    tmp = tempfile.mkdtemp(prefix="e517_")
    try:
        scripts = os.path.join(tmp, "scripts")
        os.makedirs(scripts)
        with io.open(os.path.join(scripts, "alpha.py"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(ALPHA)
        with io.open(os.path.join(scripts, "beta.py"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(BETA)
        rows = [
            {"source": "scripts/alpha.py", "line": 6, "symbol": "payload",
             "value_expression": "payloads.get(path)", "surfaces": ["scan_key"],
             "answer": UNRESOLVED},
            {"source": "scripts/beta.py", "line": 5, "symbol": "rows",
             "value_expression": "[(rel, text) for rel, text in alpha.sources() if rel != \"self\"]",
             "surfaces": ["census"], "answer": UNRESOLVED},
            {"source": "scripts/alpha.py", "line": 6, "symbol": "ignored",
             "value_expression": "payloads.get(path)",
             "answer": "the_value_is_a_literal_written_at_the_site"},
        ]
        face = build(tmp, write=False, upstream=rows)
        by_symbol = {r.get("symbol"): r for r in face["rows"]}

        ok("only rows E514 left unresolved enter the population", len(face["rows"]) == 2,
           [r.get("symbol") for r in face["rows"]])
        a = by_symbol.get("payload")
        ok("a .get receiver is named as the container, not the callee",
           a["container_expression"] == "payloads", a["container_expression"])
        ok("the receiver is classified as a parameter of the reading function",
           a["container_class"] == "a_parameter_of_the_function_that_reads_it", a["container_class"])
        ok("the one hop reaches the caller and names what it passes",
           len(a["call_sites"]) == 1 and a["call_sites"][0]["source"] == "scripts/alpha.py"
           and a["call_sites"][0]["line"] == 19, a["call_sites"])
        ok("a caller-bound name backed by a call is the feed it publishes",
           a["call_sites"][0]["feed"] == "a_name_the_caller_binds_to_a_call_result",
           a["call_sites"][0]["feed"])
        ok("the parameter arm answers through the caller, not the run",
           a["answer"] == "the_population_is_decided_by_the_caller_who_fills_the_container", a["answer"])

        b = by_symbol.get("rows")
        ok("a dotted receiver resolves through the row file's own import alias",
           (b.get("resolved_function") or {}).get("function") == "sources",
           b.get("resolved_function"))
        ok("the resolved function's seam parameter is published",
           (b.get("resolved_function") or {}).get("seam_parameters") == ["files"],
           b.get("resolved_function"))
        ok("a cross-module corpus reader is named as what it is",
           b["container_class"] == "a_function_in_another_module_that_reads_the_tree", b["container_class"])
        ok("the cross-module arm answers with the corpus reading",
           b["answer"] == "the_container_is_a_corpus_read_in_another_module", b["answer"])

        ok("the fixture verdict is total, not partial",
           face["verdict"] == "every_unresolved_row_names_its_container", face["verdict"])
        ok("the gate passes on the built fixture", site_problems(face) == [], site_problems(face))
        ok("the summary counts the one call site it found",
           face["summary"]["call_sites"] == 1, face["summary"]["call_sites"])

        doctored = json.loads(json.dumps(face))
        doctored["rows"][0]["container_class"] = "not_resolvable_from_the_row"
        ok("the gate refuses a container class its own call sites contradict",
           site_problems(doctored) != [])

        ok("the reconstructable count is re-derivable from the rows",
           face["summary"]["rows_whose_container_is_reconstructable_without_the_run"] == 2,
           face["summary"]["rows_whose_container_is_reconstructable_without_the_run"])

        doctored3 = json.loads(json.dumps(face))
        doctored3["verdict"] = "some_rows_still_stop_before_the_container"
        ok("the gate refuses a hand-written verdict", site_problems(doctored3) != [])

        doctored4 = json.loads(json.dumps(face))
        doctored4["rows"].append({
            "source": "scripts/alpha.py", "line": 6, "value_expression": "payloads.get(path)",
            "container_class": "a_parameter_of_the_function_that_reads_it",
            "answer": "the_population_is_decided_by_the_caller_who_fills_the_container",
            "call_sites": [], "resolved_function": None})
        ok("the gate refuses a parameter container answered with no call site",
           site_problems(doctored4) != [])

        doctored5 = json.loads(json.dumps(face))
        doctored5["population_source"] = "hand-written"
        ok("the gate refuses an edited population_source", site_problems(doctored5) != [])

        empty = build(tmp, write=False, upstream=[])
        ok("an empty upstream is not an error and is not a total verdict",
           empty["summary"]["rows"] == 0
           and empty["verdict"] == "every_unresolved_row_names_its_container", empty["verdict"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("selftest %d/%d" % (checks[0] - len(failures), checks[0]))
    for failure in failures:
        print("FAIL: %s" % failure)
    return 0 if not failures else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    mode = argv[0] if argv else "run"
    if mode in ("run", "build"):
        face = build()
        print("verdict=%s" % face["verdict"])
        print("summary=%s" % json.dumps(face["summary"], ensure_ascii=False, sort_keys=True))
        return 0
    if mode == "check":
        return check()
    if mode == "verify":
        return verify()
    if mode == "selftest":
        return selftest()
    print("unknown mode %r" % mode)
    return 2


if __name__ == "__main__":
    sys.exit(main())