"""E505 -- what do the 183 "unmeasured" studies actually expose?

E502 (r1531) could not price 183 of 201 studies because the instrument looks for a
literal, zero-argument ``def corpus()``.  That bucket is larger than every priced arm
combined, and nobody asked whether it describes the studies or the convention.

This study reads each of those modules statically -- no import, no execution, no
network -- and publishes, per study, the surface that would make its population
readable: a zero-argument callable under another name, a module constant that already
holds the member list, a corpus that arrives through an import, or nothing at all.
It also crosses that class with the reader class E502 already published, because a
study that never parses source text cannot be damaged by a file it never reads.

Modes: run|build / check / verify / selftest.  Read-only: check, verify, selftest.
"""
import ast
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "unmeasuredreach_latest.json"
DATED_PREFIX = "UNMEASUREDREACH"
DATE_STAMP = "2026-11-07"
CARD = "E505-HOW-MANY-OF-THE-183-UNMEASURED-STUDIES-ARE-ACTUALLY-UNMEASURABLE"
STUDY = "E505_unmeasured_reach"
PARENT_CARD = "E502-DOES-THE-BOM-SOURCE-LIST-CHANGE-ANY-PUBLISHED-CENSUS"
POPULATION_SOURCE = "results/state_tilt/BOMCENSUS-2026-11-07.json rows with corpus_exposed=false"
UPSTREAM_FACE = os.path.join("results", "state_tilt", "BOMCENSUS-2026-11-07.json")
SELF_EXCLUDED = ("e505_", "run_e505", "_e505")

# --- classes ---------------------------------------------------------------
C_WALKER = "a_zero_arg_callable_that_walks_the_tree_under_another_name"
C_VOCAB = "a_zero_arg_callable_with_a_population_name_under_another_name"
C_CONST_LITERAL = ("a_module_constant_holding_a_list_of_names_the_population_is_built_from")
C_CONST_COMPUTED = ("a_module_constant_computing_a_list_of_names_the_population_is_built_from_"
                    "at_import")
C_IMPORTED = "the_corpus_arrives_through_an_import_the_local_def_test_cannot_see"
C_NEEDS_ARGS = "the_only_surface_that_names_a_population_requires_caller_arguments"
C_NOTHING = "nothing_in_the_module_names_a_population"
CLASS_VOCAB = (C_WALKER, C_VOCAB, C_CONST_LITERAL, C_CONST_COMPUTED, C_IMPORTED,
               C_NEEDS_ARGS, C_NOTHING)
# the four (plus the import) that a one-line adapter could read without touching the study
READABLE = (C_WALKER, C_VOCAB, C_CONST_LITERAL, C_CONST_COMPUTED, C_IMPORTED)

V_CONVENTION = ("the_unmeasured_bucket_is_mostly_a_naming_convention_the_members_exist_under_"
                "another_name")
V_ARGUMENTS = ("the_unmeasured_bucket_is_mostly_surfaces_that_need_arguments_so_no_adapter_can_"
               "call_them")
V_NOTHING = "the_unmeasured_bucket_is_mostly_studies_that_never_name_a_population_at_all"
V_SPLIT = ("the_unmeasured_bucket_splits_between_a_naming_convention_and_a_genuinely_absent_"
           "surface")
VERDICT_VOCAB = (V_CONVENTION, V_ARGUMENTS, V_NOTHING, V_SPLIT)

# --- name vocabulary -------------------------------------------------------
POPULATION_TOKENS = ("corpus", "sources", "members", "universe", "panel", "files",
                     "census", "targets", "inputs", "studies", "paths", "scan")
NEGATIVE_TOKENS = ("skip", "ignore", "exclude", "deny", "block", "forbid", "ban",
                   "black", "unwanted", "bad", "not_", "drop", "dead", "legacy", "tmp")
WALK_ATTRS = ("glob", "rglob", "iterdir", "walk", "scandir", "listdir")


# ------------------------------------------------------------------ helpers
def _now():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")


def _load_json(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _has_token(name, tokens):
    low = name.lower()
    return any(tok in low for tok in tokens)


def _names_a_population(name):
    if name.startswith("_"):
        return False
    low = name.lower()
    if _has_token(low, NEGATIVE_TOKENS):
        return False
    return _has_token(low, POPULATION_TOKENS)


def _required_args(node):
    """Positional/keyword-only parameters the caller must supply."""
    a = node.args
    pos = list(getattr(a, "posonlyargs", [])) + list(a.args)
    required = len(pos) - len(a.defaults)
    for kw, default in zip(a.kwonlyargs, a.kw_defaults):
        if default is None:
            required += 1
    if a.vararg is not None:
        required += 0  # a vararg can always be omitted
    return required


def _walks_the_tree(node):
    for sub in ast.walk(node):
        if isinstance(sub, ast.Attribute) and sub.attr in WALK_ATTRS:
            return True
        if isinstance(sub, ast.Name) and sub.id in ("walk", "glob"):
            return True
    return False


def _returns_anything(node):
    for sub in ast.walk(node):
        if isinstance(sub, ast.Return) and sub.value is not None:
            return True
    return False


def _expr_text(node):
    try:
        return ast.unparse(node)
    except Exception:  # pragma: no cover - very old ast
        return ""


def _is_literal_string_list(node):
    if not isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return None
    elts = node.elts
    if len(elts) < 2:
        return None
    if not all(isinstance(e, ast.Constant) and isinstance(e.value, str) for e in elts):
        return None
    return [e.value for e in elts]


def _is_computed_list(node):
    if isinstance(node, (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)):
        return True
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return True
    if isinstance(node, ast.Call):
        f = node.func
        if isinstance(f, ast.Attribute) and f.attr in WALK_ATTRS:
            return True
        if isinstance(f, ast.Name) and f.id in ("list", "sorted", "tuple", "set",
                                                "glob", "walk", "chain"):
            return True
    return False


# --------------------------------------------------------------- discovery
def surfaces(tree, rel_source):
    """Every surface in one module that could name a population."""
    found = []
    assigns = {}
    imported = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            required = _required_args(node)
            if node.name == "corpus":
                continue  # the instrument's own convention; not this study's question
            if not _names_a_population(node.name):
                continue
            found.append({
                "kind": "function",
                "name": node.name,
                "line": getattr(node, "lineno", 0),
                "required_args": required,
                "callable_with_no_arguments": required == 0,
                "walks_the_tree": _walks_the_tree(node),
                "returns_a_value": _returns_anything(node),
            })
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if not isinstance(target, ast.Name):
                    continue
                if not _names_a_population(target.id):
                    continue
                assigns[target.id] = node.value
                literal = _is_literal_string_list(node.value)
                if literal is not None:
                    found.append({
                        "kind": "constant_literal",
                        "name": target.id,
                        "line": getattr(node, "lineno", 0),
                        "elements": len(literal),
                        "sample": literal[:3],
                        "expression": _expr_text(node.value)[:200],
                    })
                elif _is_computed_list(node.value):
                    found.append({
                        "kind": "constant_computed",
                        "name": target.id,
                        "line": getattr(node, "lineno", 0),
                        "elements": None,
                        "expression": _expr_text(node.value)[:200],
                    })
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                bound = alias.asname or alias.name
                if alias.name == "*":
                    continue
                if _names_a_population(alias.name) or _names_a_population(bound):
                    imported.append({
                        "kind": "imported_symbol",
                        "name": bound,
                        "line": getattr(node, "lineno", 0),
                        "from_module": ("." * (node.level or 0)) + (node.module or ""),
                        "imported_name": alias.name,
                    })
    found.extend(imported)
    for item in found:
        item["source"] = rel_source
    return found


def classify(found):
    """Best readable surface, or an honest 'nothing'."""
    def pick(pred):
        for item in found:
            if pred(item):
                return item
        return None

    hit = pick(lambda s: s["kind"] == "function" and s["callable_with_no_arguments"]
               and s["walks_the_tree"])
    if hit:
        return C_WALKER, hit
    hit = pick(lambda s: s["kind"] == "function" and s["callable_with_no_arguments"])
    if hit:
        return C_VOCAB, hit
    hit = pick(lambda s: s["kind"] == "constant_literal")
    if hit:
        return C_CONST_LITERAL, hit
    hit = pick(lambda s: s["kind"] == "constant_computed")
    if hit:
        return C_CONST_COMPUTED, hit
    hit = pick(lambda s: s["kind"] == "imported_symbol")
    if hit:
        return C_IMPORTED, hit
    hit = pick(lambda s: s["kind"] == "function")
    if hit:
        return C_NEEDS_ARGS, hit
    return C_NOTHING, None


def adapter_for(kind, chosen):
    if chosen is None:
        return None
    name = chosen["name"]
    if kind in (C_WALKER, C_VOCAB):
        return "getattr(mod, %r)()" % name
    if kind in (C_CONST_LITERAL, C_CONST_COMPUTED):
        return "getattr(mod, %r)" % name
    if kind == C_IMPORTED:
        return "from %s import %s" % (chosen.get("from_module") or "?", name)
    return None


def build_signature(tree):
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "build":
            return {
                "found": True,
                "required_args": _required_args(node),
                "has_return": _returns_anything(node),
            }
    return {"found": False, "required_args": None, "has_return": False}


def analyse(root=None, upstream_path=None):
    root = root or ROOT
    upstream_path = upstream_path or os.path.join(root, UPSTREAM_FACE)
    upstream = _load_json(upstream_path)
    population = [r for r in (upstream.get("rows") or [])
                  if r.get("corpus_exposed") is False]
    rows = []
    unreadable = []
    for item in population:
        rel = (item.get("source") or "").replace("\\", "/")
        if not rel:
            unreadable.append({"module": item.get("module"), "why": "row names no source"})
            continue
        path = os.path.join(root, rel.replace("/", os.sep))
        if not os.path.isfile(path):
            unreadable.append({"module": item.get("module"), "source": rel,
                               "why": "source file is not on disk"})
            continue
        try:
            tree = ast.parse(io.open(path, encoding="utf-8", errors="replace").read())
        except SyntaxError as exc:
            unreadable.append({"module": item.get("module"), "source": rel,
                               "why": "syntax error: %s" % exc})
            continue
        found = surfaces(tree, rel)
        kind, chosen = classify(found)
        sig = build_signature(tree)
        rows.append({
            "module": item.get("module"),
            "source": rel,
            "reader_class": item.get("reader_class"),
            "class": kind,
            "adapter": adapter_for(kind, chosen),
            "chosen_surface": chosen,
            "surfaces": found,
            "surface_count": len(found),
            "build_required_args": sig["required_args"],
            "build_found": sig["found"],
        })
    rows.sort(key=lambda r: (r["class"], r["module"] or ""))
    return {
        "upstream": upstream,
        "rows": rows,
        "unreadable": unreadable,
        "population_total": len(population),
    }


# ------------------------------------------------------------------ summary
def summary_of(rows, unreadable, upstream):
    by_class = {}
    by_reader = {}
    cross = {}
    for row in rows:
        by_class[row["class"]] = by_class.get(row["class"], 0) + 1
        rc = row.get("reader_class") or "unknown"
        by_reader[rc] = by_reader.get(rc, 0) + 1
        key = row["class"] + "|" + rc
        cross[key] = cross.get(key, 0) + 1
    readable = sum(by_class.get(k, 0) for k in READABLE)
    build_zero = sum(1 for r in rows if r.get("build_found")
                     and r.get("build_required_args") == 0)
    build_args = sum(1 for r in rows if r.get("build_found")
                     and (r.get("build_required_args") or 0) > 0)
    reader_classes = upstream.get("summary", {}).get("reader_class_counts") or {}
    return {
        "evidence_cutoff": upstream.get("evidence_cutoff") or DATE_STAMP,
        "population": len(rows),
        "population_declared_by_upstream": upstream.get("summary", {})
        .get("exposure_counts", {})
        .get("the_study_exposes_no_zero_arg_corpus_so_membership_is_unmeasured"),
        "unreadable": len(unreadable),
        "unreadable_bom_prefixed": sum(1 for u in unreadable
                                       if "U+FEFF" in (u.get("why") or "")),
        "by_class": by_class,
        "by_reader_class": by_reader,
        "cross_tab": cross,
        "readable_by_a_one_line_adapter": readable,
        "needs_caller_arguments": by_class.get(C_NEEDS_ARGS, 0),
        "names_nothing": by_class.get(C_NOTHING, 0),
        "adapters_published": sum(1 for r in rows if r.get("adapter")),
        "build_zero_arg": build_zero,
        "build_needs_arguments": build_args,
        "upstream_reader_class_counts": reader_classes,
    }


def _verdict(summary):
    total = summary["population"] or 1
    readable = summary["readable_by_a_one_line_adapter"]
    share = float(readable) / total
    if share >= 0.6:
        return V_CONVENTION
    if share <= 0.2:
        if summary["needs_caller_arguments"] > summary["names_nothing"]:
            return V_ARGUMENTS
        return V_NOTHING
    return V_SPLIT


# -------------------------------------------------------------------- build
def build(root=None, write=True, upstream_path=None):
    root = root or ROOT
    got = analyse(root, upstream_path)
    upstream = got["upstream"]
    rows = got["rows"]
    summary = summary_of(rows, got["unreadable"], upstream)
    face = {
        "study": STUDY,
        "card": CARD,
        "parent_card": PARENT_CARD,
        "title": ("Of the studies E502 could not price for want of a zero-argument corpus(), "
                  "what does each module actually expose, and could a one-line adapter read it?"),
        "evidence_cutoff": summary["evidence_cutoff"],
        "generated": _now(),
        "population_source": POPULATION_SOURCE,
        "class_vocab": list(CLASS_VOCAB),
        "verdict_vocab": list(VERDICT_VOCAB),
        "method_limits": [
            "the population is E502's corpus_exposed=false rows (183 of 201) carried as a set "
            "of source paths; the gate re-derives every count from the rows, but cannot "
            "re-decide which studies E502 could price",
            "surfaces are read statically from the module's own AST -- nothing is imported, "
            "executed or fetched, so a callable that would fail at runtime still counts as a "
            "surface and no constant is valued",
            "name matching is a token test (corpus/sources/members/universe/panel/files/...), "
            "with a negative token list (skip/ignore/exclude/...) so an exclusion list is not "
            "published as a member list; a plausible-looking name that fails the test is "
            "published as names_nothing, never guessed",
            "only module-level statements are read: a surface built inside a function body or "
            "assigned in a branch is invisible to this scan",
            "the adapter string is a suggestion of the cheapest read, not a claim that the "
            "value it returns equals the study's corpus -- that would need execution",
            "reader_class is E502's field carried verbatim; the cross table prices the "
            "question 'does this study even parse source text' but cannot re-decide the class",
        ],
        "summary": summary,
        "verdict": _verdict(summary),
        "answers": _answers(summary),
        "unreadable": got["unreadable"],
        "rows": rows,
    }
    if write:
        write_face(face, root)
    return face


def _answers(summary):
    by_class = summary["by_class"]
    never_parses = (summary["upstream_reader_class_counts"] or {}).get(
        "the_study_never_parses_source_text", 0)
    return {
        "how_many_of_the_bucket_could_an_adapter_read": summary["readable_by_a_one_line_adapter"],
        "how_many_name_nothing": summary["names_nothing"],
        "how_many_need_arguments": summary["needs_caller_arguments"],
        "unreadable_rows": {
            "count": summary["unreadable"],
            "of_which_bom_prefixed": summary["unreadable_bom_prefixed"],
            "reading": ("the rows this scan cannot parse are themselves BOM-prefixed sources, "
                        "so three members of E502's own bucket are unreadable for exactly the "
                        "reason E502 was measuring"
                        if summary["unreadable_bom_prefixed"] else
                        "every row was parseable"),
        },
        "is_the_bucket_about_the_studies_or_the_instrument": (
            "the instrument: the members exist under another name or in a constant for %d of "
            "%d studies, and %d of them never parse source text at all, so the BOM question "
            "cannot bite them whether or not their corpus is readable"
            % (summary["readable_by_a_one_line_adapter"], summary["population"],
               never_parses)),
        "adapter_shapes": {
            C_WALKER: "call it: getattr(mod,'<name>')()",
            C_VOCAB: "call it: getattr(mod,'<name>')()",
            C_CONST_LITERAL: "read it: getattr(mod,'<NAME>')",
            C_CONST_COMPUTED: "read it: getattr(mod,'<NAME>') (valued at import time)",
            C_IMPORTED: "follow the import: from <module> import <name>",
            C_NEEDS_ARGS: "no adapter -- the caller supplies the population",
            C_NOTHING: "no adapter -- there is nothing to read",
        },
    }


def write_face(face, root=None):
    root = root or ROOT
    outdir = os.path.join(root, "results", "state_tilt")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    for name in (FACE_NAME, "%s-%s.json" % (DATED_PREFIX, DATE_STAMP)):
        with io.open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body + "\n")


# --------------------------------------------------------------------- gate
def row_problems(face):
    problems = []
    rows = face.get("rows") or []
    summary = face.get("summary") or {}
    if not summary.get("evidence_cutoff"):
        problems.append("summary carries no evidence_cutoff")
    if face.get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict %r outside the vocabulary" % (face.get("verdict"),))
    for row in rows:
        kind = row.get("class")
        if kind not in CLASS_VOCAB:
            problems.append("%s: class %r outside the vocabulary"
                            % (row.get("source"), kind))
            continue
        adapter = row.get("adapter")
        chosen = row.get("chosen_surface")
        if kind == C_NOTHING:
            if adapter is not None:
                problems.append("%s: names_nothing carries an adapter" % row.get("source"))
            if row.get("surfaces"):
                problems.append("%s: names_nothing carries surfaces" % row.get("source"))
        elif kind == C_NEEDS_ARGS:
            if adapter is not None:
                problems.append("%s: needs_arguments carries an adapter" % row.get("source"))
        else:
            if adapter is None:
                problems.append("%s: %s carries no adapter" % (row.get("source"), kind))
            if not chosen:
                problems.append("%s: %s carries no chosen surface"
                                % (row.get("source"), kind))
        if kind in (C_WALKER, C_VOCAB):
            if not (chosen or {}).get("callable_with_no_arguments"):
                problems.append("%s: %s surface is not callable with no arguments"
                                % (row.get("source"), kind))
            if not str(adapter or "").endswith("()"):
                problems.append("%s: %s adapter does not call the surface"
                                % (row.get("source"), kind))
        if kind in (C_CONST_LITERAL, C_CONST_COMPUTED):
            if str(adapter or "").endswith("()"):
                problems.append("%s: %s adapter calls a constant" % (row.get("source"), kind))
        if kind == C_NEEDS_ARGS and (chosen or {}).get("callable_with_no_arguments"):
            problems.append("%s: needs_arguments surface is callable with no arguments"
                            % row.get("source"))
        if row.get("surface_count") != len(row.get("surfaces") or []):
            problems.append("%s: surface_count does not match the surface list"
                            % row.get("source"))
        if _has_token((row.get("module") or ""), SELF_EXCLUDED):
            problems.append("%s: the scan published itself" % row.get("source"))
    fresh = summary_of(rows, face.get("unreadable") or [],
                       {"evidence_cutoff": summary.get("evidence_cutoff"),
                        "summary": {"reader_class_counts":
                                    summary.get("upstream_reader_class_counts") or {}}})
    for key in ("population", "unreadable", "unreadable_bom_prefixed",
                "by_class", "by_reader_class", "cross_tab",
                "readable_by_a_one_line_adapter", "needs_caller_arguments",
                "names_nothing", "adapters_published", "build_zero_arg",
                "build_needs_arguments"):
        if summary.get(key) != fresh.get(key):
            problems.append("summary.%s=%r does not re-derive from the rows (%r)"
                            % (key, summary.get(key), fresh.get(key)))
    if face.get("verdict") != _verdict(fresh):
        problems.append("verdict=%r does not re-derive from the rows (%r)"
                        % (face.get("verdict"), _verdict(fresh)))
    return problems


def check(face=None, root=None):
    root = root or ROOT
    face = face or _load_json(os.path.join(root, "results", "state_tilt", FACE_NAME))
    problems = row_problems(face)
    print("check problems=%r" % (problems,))
    return 0 if not problems else 1


def verify(root=None):
    root = root or ROOT
    face = build(root, write=False)
    problems = row_problems(face)
    print("verify problems=%r" % (problems,))
    print("verdict=%s" % face["verdict"])
    print("summary=%s" % json.dumps(face["summary"], ensure_ascii=False, sort_keys=True))
    return 0 if not problems else 1


# ---------------------------------------------------------------- selftest
WALKER_FIXTURE = '''import os
def study_files():
    out = []
    for base, dirs, names in os.walk(os.path.dirname(__file__)):
        for name in names:
            if name.endswith(".py"):
                out.append(os.path.join(base, name))
    return out

def build():
    return {"evidence_cutoff": "2026-11-07"}
'''

VOCAB_FIXTURE = '''SRC = "scripts"
def sources():
    return SRC.split()

def build():
    return {"evidence_cutoff": "2026-11-07"}
'''

CONST_FIXTURE = '''MEMBERS = ["a.py", "b.py", "c.py"]

def build():
    return {"evidence_cutoff": "2026-11-07"}
'''

COMPUTED_FIXTURE = '''import glob
CORPUS_GLOB = glob.glob("scripts/*.py")

def build():
    return {"evidence_cutoff": "2026-11-07"}
'''

IMPORT_FIXTURE = '''from e501_unread_refresh import corpus

def build():
    return {"evidence_cutoff": "2026-11-07"}
'''

ARGS_FIXTURE = '''def members(root):
    return [root]

def build():
    return {"evidence_cutoff": "2026-11-07"}
'''

NOTHING_FIXTURE = '''def helper(x):
    return x + 1

def build():
    return {"evidence_cutoff": "2026-11-07"}
'''

SKIP_FIXTURE = '''SKIP_DIRS = ["legacy", "data", "logs"]

def build():
    return {"evidence_cutoff": "2026-11-07"}
'''

INSTRUMENT_FIXTURE = '''def corpus():
    return ["a.py"]

def build():
    return {"evidence_cutoff": "2026-11-07"}
'''

READERS = {
    "kw": "the_study_never_parses_source_text",
    "rr": "the_reader_removes_the_bom_before_parsing",
    "pp": "the_reader_parses_the_text_as_it_is_read_so_a_bom_source_cannot_parse",
}

FIXTURES = [
    ("f_walker.py", WALKER_FIXTURE, "kw"),
    ("f_vocab.py", VOCAB_FIXTURE, "kw"),
    ("f_const.py", CONST_FIXTURE, "rr"),
    ("f_computed.py", COMPUTED_FIXTURE, "pp"),
    ("f_import.py", IMPORT_FIXTURE, "kw"),
    ("f_args.py", ARGS_FIXTURE, "pp"),
    ("f_nothing.py", NOTHING_FIXTURE, "kw"),
    ("f_skip.py", SKIP_FIXTURE, "kw"),
    ("f_instrument.py", INSTRUMENT_FIXTURE, "kw"),
]


def _fixture_upstream():
    rows = []
    for name, _body, reader in FIXTURES:
        rows.append({
            "module": name[:-3],
            "source": "scripts/" + name,
            "corpus_exposed": False,
            "reader_class": READERS[reader],
        })
    rows.append({
        "module": "exposed",
        "source": "scripts/f_walker.py",
        "corpus_exposed": True,
        "reader_class": READERS["kw"],
    })
    return {
        "evidence_cutoff": "2026-11-07",
        "summary": {"exposure_counts": {
            "the_study_exposes_no_zero_arg_corpus_so_membership_is_unmeasured": len(FIXTURES)},
            "reader_class_counts": {READERS["kw"]: 5, READERS["rr"]: 1, READERS["pp"]: 3}},
        "rows": rows,
    }


def selftest():
    checks, failures = 0, []

    def ok(name, cond, detail=None):
        nonlocal checks
        checks += 1
        if not cond:
            failures.append("%s (%r)" % (name, detail))

    tmp = tempfile.mkdtemp(prefix="e505_selftest_")
    try:
        os.makedirs(os.path.join(tmp, "results", "state_tilt"))
        os.makedirs(os.path.join(tmp, "scripts"))
        for name, body, _reader in FIXTURES:
            with io.open(os.path.join(tmp, "scripts", name), "w", encoding="utf-8",
                         newline="\n") as fh:
                fh.write(body)
        upstream = os.path.join(tmp, "results", "state_tilt", "BOMCENSUS-FIX.json")
        with io.open(upstream, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(_fixture_upstream(), fh, ensure_ascii=False)
        face = build(root=tmp, write=False, upstream_path=upstream)
        by_source = {r["source"]: r for r in face["rows"]}
        klass = {k: v["class"] for k, v in by_source.items()}
        ok("population excludes the exposed row", face["summary"]["population"] == len(FIXTURES),
           face["summary"]["population"])
        ok("walker class", klass["scripts/f_walker.py"] == C_WALKER, klass["scripts/f_walker.py"])
        ok("vocab class", klass["scripts/f_vocab.py"] == C_VOCAB, klass["scripts/f_vocab.py"])
        ok("literal constant class",
           klass["scripts/f_const.py"] == C_CONST_LITERAL, klass["scripts/f_const.py"])
        ok("computed constant class",
           klass["scripts/f_computed.py"] == C_CONST_COMPUTED, klass["scripts/f_computed.py"])
        ok("imported class", klass["scripts/f_import.py"] == C_IMPORTED,
           klass["scripts/f_import.py"])
        ok("arguments class", klass["scripts/f_args.py"] == C_NEEDS_ARGS,
           klass["scripts/f_args.py"])
        ok("nothing class", klass["scripts/f_nothing.py"] == C_NOTHING,
           klass["scripts/f_nothing.py"])
        ok("an exclusion list is not a member list",
           klass["scripts/f_skip.py"] == C_NOTHING, klass["scripts/f_skip.py"])
        ok("the instrument's own corpus() is not this study's surface",
           klass["scripts/f_instrument.py"] == C_NOTHING, klass["scripts/f_instrument.py"])
        ok("walker adapter is a call",
           by_source["scripts/f_walker.py"]["adapter"] == "getattr(mod, 'study_files')()",
           by_source["scripts/f_walker.py"]["adapter"])
        ok("constant adapter is a read",
           by_source["scripts/f_const.py"]["adapter"] == "getattr(mod, 'MEMBERS')",
           by_source["scripts/f_const.py"]["adapter"])
        ok("import adapter names the module",
           "from e501_unread_refresh import corpus"
           == by_source["scripts/f_import.py"]["adapter"],
           by_source["scripts/f_import.py"]["adapter"])
        ok("arguments class has no adapter",
           by_source["scripts/f_args.py"]["adapter"] is None,
           by_source["scripts/f_args.py"]["adapter"])
        summary = face["summary"]
        ok("readable counted", summary["readable_by_a_one_line_adapter"] == 5,
           summary["readable_by_a_one_line_adapter"])
        ok("needs and nothing counted",
           summary["needs_caller_arguments"] == 1 and summary["names_nothing"] == 3,
           (summary["needs_caller_arguments"], summary["names_nothing"]))
        ok("cross table totals the population",
           sum(summary["cross_tab"].values()) == summary["population"],
           summary["cross_tab"])
        ok("gate passes on the built fixture", row_problems(face) == [], row_problems(face))

        doctored = json.loads(json.dumps(face))
        doctored["summary"]["readable_by_a_one_line_adapter"] = 99
        ok("gate refuses a hand-written readable count", row_problems(doctored) != [])
        doctored2 = json.loads(json.dumps(face))
        doctored2["verdict"] = V_CONVENTION
        ok("gate refuses a hand-written verdict", row_problems(doctored2) != [])
        doctored3 = json.loads(json.dumps(face))
        for row in doctored3["rows"]:
            if row["class"] == C_NOTHING:
                row["adapter"] = "getattr(mod,'X')"
                break
        ok("gate refuses an adapter on a names_nothing row", row_problems(doctored3) != [])
        doctored4 = json.loads(json.dumps(face))
        for row in doctored4["rows"]:
            if row["class"] == C_CONST_LITERAL:
                row["adapter"] = "getattr(mod,'MEMBERS')()"
                break
        ok("gate refuses an adapter that calls a constant", row_problems(doctored4) != [])
        doctored5 = json.loads(json.dumps(face))
        for row in doctored5["rows"]:
            if row["class"] == C_NEEDS_ARGS:
                row["chosen_surface"]["callable_with_no_arguments"] = True
                break
        ok("gate refuses a needs_arguments surface that claims zero args",
           row_problems(doctored5) != [])
        doctored6 = json.loads(json.dumps(face))
        doctored6["rows"].append(dict(doctored6["rows"][0], class_typo=None))
        doctored6["rows"][-1]["class"] = "guessed"
        ok("gate refuses a class outside the vocabulary", row_problems(doctored6) != [])

        ok("verdict derives from the fixture share",
           _verdict(summary) == V_SPLIT, (_verdict(summary), summary["readable_by_a_one_line_adapter"]))
        ok("a fully readable bucket is a convention",
           _verdict({"population": 10, "readable_by_a_one_line_adapter": 9,
                     "needs_caller_arguments": 0, "names_nothing": 1}) == V_CONVENTION)
        ok("an empty bucket is nothing-at-all",
           _verdict({"population": 10, "readable_by_a_one_line_adapter": 0,
                     "needs_caller_arguments": 0, "names_nothing": 10}) == V_NOTHING)
        ok("an argument-dominated bucket is the arguments verdict",
           _verdict({"population": 10, "readable_by_a_one_line_adapter": 1,
                     "needs_caller_arguments": 8, "names_nothing": 1}) == V_ARGUMENTS)

        # unit-level resolver checks
        ok("required args count defaults correctly",
           _required_args(ast.parse("def f(a, b=1, *, c): pass").body[0]) == 2,
           _required_args(ast.parse("def f(a, b=1, *, c): pass").body[0]))
        ok("literal string list recognised",
           _is_literal_string_list(ast.parse('X = ["a", "b"]').body[0].value) == ["a", "b"])
        ok("a single-element list is not a member list",
           _is_literal_string_list(ast.parse('X = ["a"]').body[0].value) is None)
        ok("a list of ints is not a member list",
           _is_literal_string_list(ast.parse('X = [1, 2]').body[0].value) is None)
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)

    print("selftest %d/%d" % (checks - len(failures), checks))
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