"""E395 -- a writer that names the key is not a writer that always writes it.

E394 classified 218 reads that resolve to a real face which does not store their key.  131 of
them landed in one class: some source that *mentions* the face also builds the key structurally
(dict literal / subscript store / ``setdefault``).  E394 named that class
``producer_names_the_key_but_the_face_lacks_it`` and was careful to say it is evidence that the
producer *can* write the key, not proof that it did on that run.

This study takes the honest follow-up: for every one of those reads, does the producer write the
key on every path, on a branch, or behind a condition -- and is that conditionality written down
anywhere a reader of the face can find it?

The measurement is a *path position*, not a call graph.  For every write site the runner walks the
ancestor chain and asks which compound statements sit between the write and the module body:

  * ``if`` / ``try`` / ``for`` / ``while`` / ``with``  -> the write is on a branch;
  * a conditional expression guarding the *value*        -> the key is written either way, with a
    branch inside its value, which is a different thing and is published separately;
  * a function body                                      -> the write happens when the function is
    called, which is a condition no static reading of one file can discharge.

Refusals that keep the answer from flattering itself:

  * an unconditional module-level write is published as ``not_that_producers_output`` rather than
    as "conditional": a producer that always writes the key cannot be the producer of a face that
    lacks it, so that triple is an attribution failure, not conditionality;
  * a write inside a function is *not* called conditional -- it is called ``inside_a_callable``
    and the study publishes whether that callable is referenced anywhere else in the module,
    because "called on some paths" is not decidable from the write site alone;
  * ``setdefault`` is a write that only fires when the key is absent and is classified apart;
  * a producer that cannot be parsed is published as ``unattributed``, never guessed;
  * a key mentioned only in a *string* is not a declaration -- the declaration test looks for the
    key literal in a docstring line that also carries an optionality marker, and the matching line
    is published verbatim so a reader can disagree with it;
  * the study does not scan itself, its face, its mirror or its smoke leg.

    python scripts/e395_conditional_write.py run
    python scripts/e395_conditional_write.py verify
    python scripts/e395_conditional_write.py selftest
"""
import ast
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e394_phantom_why as e394      # producer index + write forms: imported, not rebuilt

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
STUDY = "E395_conditional_write"
TODAY = "2026-11-03"
FACE = "CONDITIONALWRITE-%s.json" % TODAY
LATEST = "conditionalwrite_latest.json"
SOURCE_FACE = os.path.join(OUTDIR, "PHANTOMWHY-%s.json" % TODAY)

OWN_FILES = tuple(e394.OWN_FILES) + ("scripts/e395_conditional_write.py",
                                     "scripts/run_e395_smoke_leg.py")

# path classes for a single write site
W_UNCONDITIONAL = "unconditional_at_module_level"
W_BRANCH = "inside_if_try_loop_or_with"
W_CALLABLE = "inside_a_callable"
W_UNPARSED = "producer_unparsed"

COND_STMTS = (ast.If, ast.Try, ast.For, ast.AsyncFor, ast.While, ast.With, ast.AsyncWith)

MARKERS = ("optional", "may be", "might", "if present", "if any", "conditional", "nullable",
           "when available", "only when", "only if", "absent", "missing", "not always", "omitted")

V_UNCONDITIONAL_SAME_DOC = "producer_writes_the_key_unconditionally_into_this_very_face"
V_UNCONDITIONAL_ELSEWHERE = ("producer_writes_the_key_unconditionally_but_into_another_"
                             "document_so_it_is_not_this_faces_writer")
V_BRANCH = "every_write_site_is_on_a_branch"
V_CALLABLE = "every_write_site_is_inside_a_callable_and_no_module_level_write_exists"
V_MIXED = "write_sites_disagree_some_branch_some_callable"
V_NONE = "no_write_site_found_for_this_producer"

STATE = {}


# ---------------------------------------------------------------- AST helpers
def _walk_with_stack(tree):
    """Yield (node, ancestor tuple) for every node, ancestors outermost first."""
    stack = []

    def rec(node):
        yield node, tuple(stack)
        stack.append(node)
        for child in ast.iter_child_nodes(node):
            yield from rec(child)
        stack.pop()

    yield from rec(tree)


def _enclosing_callable(stack):
    for node in reversed(stack):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return node
    return None


def _conditional_ancestors(node, stack):
    """Compound statements between the write and its enclosing callable (or the module)."""
    func = _enclosing_callable(stack)
    out = []
    for anc in stack:
        if func is not None and anc is func:
            continue
        if isinstance(anc, COND_STMTS) or isinstance(anc, ast.IfExp):
            out.append(anc)
    return out


def _describe(node):
    kind = type(node).__name__
    if isinstance(node, ast.IfExp):
        kind = "if_expression"
    test = None
    if isinstance(node, ast.If):
        test = _unparse(node.test)
    elif isinstance(node, ast.While):
        test = _unparse(node.test)
    return {"kind": kind, "line": getattr(node, "lineno", None), "test": test}


def _unparse(node):
    try:
        return ast.unparse(node)
    except Exception:      # pragma: no cover - ast.unparse is available on 3.9+
        return None


def _is_dump_call(node):
    if not isinstance(node, ast.Call):
        return False
    fn = node.func
    return ((isinstance(fn, ast.Attribute) and fn.attr in ("dump", "dumps"))
            or (isinstance(fn, ast.Name) and fn.id in ("dump", "dumps")))


def _call_names_face(call, face_basename):
    for arg in list(call.args) + [kw.value for kw in call.keywords]:
        for sub in ast.walk(arg):
            if (isinstance(sub, ast.Constant) and isinstance(sub.value, str)
                    and face_basename in sub.value):
                return True
    return False


def _dump_context(src, node, stack, face_basename):
    """Does this write reach a dump of *this* face?  Direct argument, or one name hop.

    "the same function dumps a file called <face>" is not the same claim as "this dict is what
    gets dumped into <face>": a closeout writes several documents from one function, so the
    weaker test attributes every key in the function to every file it touches.  This one follows
    the object one hop (``json.dump(facts, ...)`` or ``facts = {...}; json.dump(facts, ...)``).
    """
    if face_basename is None:
        return "unknown_face"
    parent = stack[-1] if stack else None
    if _is_dump_call(parent) and node in parent.args:
        return "direct_to_this_face" if _call_names_face(parent, face_basename) else \
            "direct_to_another_file"
    if isinstance(parent, ast.Assign) and node is parent.value:
        names = [t.id for t in parent.targets if isinstance(t, ast.Name)]
        if names:
            scope = _enclosing_callable(stack)
            scope_node = scope if scope is not None else _parsed(src)
            if scope_node is not None:
                for sub in ast.walk(scope_node):
                    if not _is_dump_call(sub) or not sub.args:
                        continue
                    first = sub.args[0]
                    if isinstance(first, ast.Name) and first.id in names:
                        if _call_names_face(sub, face_basename):
                            return "via_name_to_this_face"
                        return "via_name_to_another_file"
            return "assigned_and_never_dumped"
    if isinstance(parent, (ast.Dict, ast.List, ast.Tuple)):
        return "inside_another_literal"
    return "not_part_of_a_dump"


def write_sites(src, key, face_basename=None):
    """Every place a source can put ``key`` into an object, with its path position."""
    cache_key = (id(src), key, face_basename)
    if cache_key in STATE.setdefault("site_cache", {}):
        return STATE["site_cache"][cache_key]
    tree = _parsed(src)
    if tree is None:
        STATE["site_cache"][cache_key] = None
        return None
    sites = []
    for node, stack in _walk_with_stack(tree):
        forms = []
        if isinstance(node, ast.Dict):
            for name in node.keys:
                if isinstance(name, ast.Constant) and name.value == key:
                    forms.append("dict_literal_key")
        elif isinstance(node, ast.Subscript) and isinstance(node.ctx, ast.Store):
            sl = node.slice
            if isinstance(sl, ast.Constant) and sl.value == key:
                forms.append("subscript_write")
        elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
              and node.func.attr == "setdefault" and node.args
              and isinstance(node.args[0], ast.Constant) and node.args[0].value == key):
            forms.append("setdefault")
        if not forms:
            continue
        conds = _conditional_ancestors(node, stack)
        func = _enclosing_callable(stack)
        if conds:
            cls = W_BRANCH
        elif func is not None:
            cls = W_CALLABLE
        else:
            cls = W_UNCONDITIONAL
        value_form = None
        if isinstance(node, ast.Dict):
            for k, v in zip(node.keys, node.values):
                if isinstance(k, ast.Constant) and k.value == key:
                    value_form = type(v).__name__
                    if isinstance(v, ast.IfExp):
                        value_form = "IfExp"
        sites.append({
            "form": forms[0],
            "line": getattr(node, "lineno", None),
            "path_class": cls,
            "conditional_ancestors": [_describe(c) for c in conds],
            "enclosing_function": (func.name if func is not None else None),
            "value_form": value_form,
            "dump_context": _dump_context(src, node, stack, face_basename),
        })
    STATE["site_cache"][cache_key] = sites
    return sites


_PARSE = {}


def _parsed(src):
    """Parse each producer source once per run (id-keyed, the object is kept alive)."""
    key = id(src)
    if key in _PARSE:
        return _PARSE[key][1]
    try:
        tree = ast.parse(src)
    except SyntaxError:
        tree = None
    _PARSE[key] = (src, tree)
    return tree


def _scope_index(src):
    """Per-scope facts: does this scope dump a document, and which strings does it name."""
    tree = _parsed(src)
    if tree is None:
        return None
    idx = {}
    scopes = [("<module>", tree)] + [(n.name, n) for n, _ in _walk_with_stack(tree)
                                     if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    for name, node in scopes:
        dumps = False
        strings = []
        for sub in ast.walk(node):
            if isinstance(sub, ast.Call):
                fn = sub.func
                if isinstance(fn, ast.Attribute) and fn.attr in ("dump", "dumps", "write"):
                    dumps = True
                elif isinstance(fn, ast.Name) and fn.id in ("dump", "dumps"):
                    dumps = True
            elif isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                strings.append(sub.value)
        idx[name] = (dumps, strings)
    return idx


def scope_dumps_this_face(src, func_name, face_basename):
    """Whether the enclosing scope both dumps a document and names this face's file.

    A module-level dict literal carrying the key is only evidence about *this* face if the same
    scope writes a file whose name is the face's.  Otherwise the key was written into some other
    document that merely lives in the same source file.
    """
    idx = _scope_index(src)
    if idx is None:
        return None
    dumps, strings = idx.get(func_name if func_name is not None else "<module>", (False, []))
    return bool(dumps) and any(face_basename in s for s in strings)


def callable_referenced(src, name):
    """Whether a function name is referenced anywhere in the module (call or attribute)."""
    if not name:
        return None
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None
    hits = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == name:
            hits += 1
        elif isinstance(node, ast.Attribute) and node.attr == name:
            hits += 1
    return hits


def docstring_declarations(src, key, func_name=None):
    """Docstring lines that name the key beside an optionality marker, published verbatim."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    texts = []
    mod = ast.get_docstring(tree)
    if mod:
        texts.append(("module", mod))
    for node, _stack in _walk_with_stack(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if func_name is not None and getattr(node, "name", None) != func_name:
                continue
            doc = ast.get_docstring(node)
            if doc:
                texts.append((getattr(node, "name", "?"), doc))
    out = []
    for where, doc in texts:
        for line in doc.splitlines():
            low = line.lower()
            if key.lower() not in low:
                continue
            if any(m in low for m in MARKERS):
                out.append({"where": where, "line": line.strip()[:200]})
    return out


def face_prose_names_the_key(face_rel, key, root=ROOT):
    """Whether the face's own prose (any string value) names the key. JSON faces carry no doc."""
    path = os.path.join(root, face_rel)
    try:
        with io.open(path, encoding="utf-8", errors="replace") as fh:
            doc = json.load(fh)
    except (OSError, ValueError):
        return None
    hits = []

    def rec(value, trail):
        if isinstance(value, dict):
            for k, v in value.items():
                if isinstance(v, str) and key in v:
                    hits.append({"at": trail + "/" + str(k), "text": v[:160]})
                rec(v, trail + "/" + str(k))
        elif isinstance(value, list):
            for i, v in enumerate(value[:200]):
                rec(v, trail + "[%d]" % i)
        elif isinstance(value, str) and key in value:
            hits.append({"at": trail or "/", "text": value[:160]})

    rec(doc, "")
    return hits[:5]


# ---------------------------------------------------------------- measurement
def producer_sites(key, face, prod_hits, prod_text, root=ROOT):
    """Every (producer, write sites) for one (key, face) pair."""
    out = []
    for rel in sorted(prod_hits.get(face, ())):
        if rel in OWN_FILES:
            continue
        src = prod_text.get(rel)
        if src is None:
            try:
                with io.open(os.path.join(root, rel), encoding="utf-8",
                             errors="replace") as fh:
                    src = fh.read()
            except OSError:
                out.append({"producer": rel, "path_class": W_UNPARSED, "sites": [],
                            "writes_this_face_unconditionally": False,
                            "declared": [], "declared_in_function": []})
                continue
        sites = write_sites(src, key, os.path.basename(face))
        if sites is None:
            out.append({"producer": rel, "path_class": W_UNPARSED, "sites": [],
                        "writes_this_face_unconditionally": False,
                        "declared": [], "declared_in_function": []})
            continue
        if not sites:
            continue
        base = os.path.basename(face)
        STRICT = ("direct_to_this_face", "via_name_to_this_face")
        for s in sites:
            s["callable_refs"] = callable_referenced(src, s["enclosing_function"])
            s["scope_dumps_this_face"] = scope_dumps_this_face(src, s["enclosing_function"],
                                                               base)
        same_doc = any(s["path_class"] == W_UNCONDITIONAL
                       and s.get("dump_context") in STRICT for s in sites)
        classes = sorted({s["path_class"] for s in sites})
        if classes == [W_UNCONDITIONAL]:
            cls = W_UNCONDITIONAL
        elif len(classes) > 1:
            cls = "mixed"
        else:
            cls = classes[0]
        out.append({
            "producer": rel,
            "path_class": cls,
            "sites": sites,
            "writes_this_face_unconditionally": bool(same_doc),
            "declared": docstring_declarations(src, key),
            "declared_in_function": docstring_declarations(
                src, key, sites[0]["enclosing_function"] if sites else None),
        })
    return out


def pair_verdict(producers):
    if not producers:
        return V_NONE
    classes = {p["path_class"] for p in producers}
    if any(p.get("writes_this_face_unconditionally") for p in producers):
        return V_UNCONDITIONAL_SAME_DOC
    if W_UNCONDITIONAL in classes:
        return V_UNCONDITIONAL_ELSEWHERE
    if classes == {W_BRANCH}:
        return V_BRANCH
    if classes == {W_CALLABLE}:
        return V_CALLABLE
    if classes == {W_UNPARSED} and len(classes) == 1:
        return V_NONE
    return V_MIXED


def _count(items):
    out = {}
    for it in items:
        out[it] = out.get(it, 0) + 1
    return out


def measure(root=ROOT):
    with io.open(SOURCE_FACE, encoding="utf-8") as fh:
        source = json.load(fh)
    residual = source.get("residual") or {}
    rows = [i for i in (residual.get("classified") or [])
            if i.get("class") == e394.C_PRODUCER]
    faces = sorted({r["face"] for r in rows})
    prod_hits, prod_text = e394.producer_index(faces, root=root)

    pairs = {}
    for row in rows:
        k = (row["key"], row["face"])
        pairs.setdefault(k, []).append(row)

    out_rows = []
    for (key, face) in sorted(pairs):
        read_rows = pairs[(key, face)]
        producers = producer_sites(key, face, prod_hits, prod_text, root=root)
        verdict = pair_verdict(producers)
        declared = [{"producer": p["producer"], "line": d["line"], "where": d["where"]}
                    for p in producers for d in p["declared"]]
        site_classes = {}
        for p in producers:
            for s in p["sites"]:
                site_classes[s["path_class"]] = site_classes.get(s["path_class"], 0) + 1
        out_rows.append({
            "key": key,
            "face": face,
            "reads": len(read_rows),
            "read_sites": sorted({r["site"] for r in read_rows}),
            "producers": [{"producer": p["producer"], "path_class": p["path_class"],
                           "writes_this_face_unconditionally":
                               p["writes_this_face_unconditionally"],
                           "sites": p["sites"]}
                          for p in producers],
            "producer_count": len(producers),
            "producers_writing_this_face_unconditionally": sum(
                1 for p in producers if p["writes_this_face_unconditionally"]),
            "write_site_classes": dict(sorted(site_classes.items())),
            "producer_path_classes": dict(sorted(
                _count(p["path_class"] for p in producers).items())),
            "verdict": verdict,
            "declared_in_producer_docstring": declared,
            "face_prose_names_the_key": face_prose_names_the_key(face, key, root=root),
        })

    by_verdict = {}
    for r in out_rows:
        by_verdict[r["verdict"]] = by_verdict.get(r["verdict"], 0) + 1
    reads_by_verdict = {}
    for r in out_rows:
        reads_by_verdict[r["verdict"]] = reads_by_verdict.get(r["verdict"], 0) + r["reads"]
    declared_pairs = [r for r in out_rows if r["declared_in_producer_docstring"]]
    face_prose = [r for r in out_rows if r["face_prose_names_the_key"]]

    branch_pairs = [r for r in out_rows if r["verdict"] == V_BRANCH]
    same_doc = [r for r in out_rows if r["verdict"] == V_UNCONDITIONAL_SAME_DOC]
    elsewhere = [r for r in out_rows if r["verdict"] == V_UNCONDITIONAL_ELSEWHERE]

    if not out_rows:
        verdict = "no_producer_named_read_remains_to_ask_about"
    elif same_doc:
        verdict = ("some_producers_write_the_key_unconditionally_into_this_exact_face_so_the_"
                   "face_lacks_a_key_its_own_writer_always_sets")
    elif elsewhere:
        verdict = ("most_of_the_producer_class_is_an_attribution_failure_the_key_is_written_"
                   "unconditionally_into_some_other_document")
    elif branch_pairs and not declared_pairs:
        verdict = ("the_writes_are_on_branches_and_no_producer_docstring_says_the_key_is_"
                   "optional")
    elif branch_pairs:
        verdict = ("the_writes_are_on_branches_and_some_producers_declare_the_key_optional_"
                   "but_the_face_itself_does_not")
    else:
        verdict = "no_write_site_is_a_plain_module_level_write_so_the_condition_is_the_call"

    return {
        "source_face": os.path.relpath(SOURCE_FACE, root).replace("\\", "/"),
        "measure": {
            "producer_named_reads": len(rows),
            "distinct_pairs": len(out_rows),
            "distinct_keys": len({r["key"] for r in out_rows}),
            "distinct_faces": len({r["face"] for r in out_rows}),
            "pairs_by_verdict": dict(sorted(by_verdict.items())),
            "reads_by_verdict": dict(sorted(reads_by_verdict.items())),
            "pairs_with_a_declaration": len(declared_pairs),
            "pairs_where_the_face_prose_names_the_key": len(face_prose),
        },
        "rows": out_rows,
        "verdict": verdict,
    }


# ---------------------------------------------------------------- io
def write_face(out_dir, doc, face=FACE, latest=LATEST):
    os.makedirs(out_dir, exist_ok=True)
    for name in (face, latest):
        path = os.path.join(out_dir, name)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=1, sort_keys=False)
            fh.write("\n")
    return os.path.join(out_dir, face)


def build(root=ROOT):
    picked = measure(root=root)
    from datetime import datetime
    return {
        "study": STUDY,
        "script": "scripts/e395_conditional_write.py",
        "generated": datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": TODAY,
        "dept": "research+engineering",
        "method": ("static AST path position over E394's producer-named class; the ancestor chain "
                   "decides whether the write sits on a branch, inside a callable, or at module "
                   "level, and the producer docstring is searched for the key beside an "
                   "optionality marker"),
        "refusals": [
            "an unconditional module-level write is published as an attribution failure, not as "
            "conditionality",
            "a write inside a function is published as inside_a_callable, never as conditional: "
            "whether the callable is reached on a given path is not decidable from one file",
            "setdefault is classified apart from a plain store",
            "a declaration needs the key literal AND an optionality marker on the same docstring "
            "line, and the line is published verbatim",
            "a producer that cannot be parsed is published as producer_unparsed, never guessed",
            "the study excludes its own source, face, mirror and smoke leg",
        ],
        "verify_covers": [
            "every published pair re-derived from the published rows and the write-site table",
            "the verdict strings re-derived from the published per-pair verdicts",
            "the read totals re-added from the pairs",
        ],
        "verify_does_not_cover": [
            "the AST re-parse of each producer (verify reads the published sites)",
            "whether a callable that contains a write is reached at run time",
        ],
        **picked,
    }


def verify(out_dir=OUTDIR, face=FACE):
    problems = []
    path = os.path.join(out_dir, face)
    with io.open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    rows = doc.get("rows") or []
    m = doc.get("measure") or {}
    if len(rows) != m.get("distinct_pairs"):
        problems.append("distinct_pairs %r != rows %d" % (m.get("distinct_pairs"), len(rows)))
    if sum(r["reads"] for r in rows) != m.get("producer_named_reads"):
        problems.append("producer_named_reads does not re-add from the pairs")
    by_v, reads_v = {}, {}
    for r in rows:
        by_v[r["verdict"]] = by_v.get(r["verdict"], 0) + 1
        reads_v[r["verdict"]] = reads_v.get(r["verdict"], 0) + r["reads"]
    if dict(sorted(by_v.items())) != (m.get("pairs_by_verdict") or {}):
        problems.append("pairs_by_verdict does not re-derive")
    if dict(sorted(reads_v.items())) != (m.get("reads_by_verdict") or {}):
        problems.append("reads_by_verdict does not re-derive")
    if len({r["key"] for r in rows}) != m.get("distinct_keys"):
        problems.append("distinct_keys does not re-derive")
    if len({r["face"] for r in rows}) != m.get("distinct_faces"):
        problems.append("distinct_faces does not re-derive")
    for r in rows:
        got = pair_verdict(r["producers"])
        if got != r["verdict"]:
            problems.append("pair %s/%s verdict %r != re-derived %r"
                            % (r["face"], r["key"], r["verdict"], got))
        n_same = sum(1 for p in r["producers"] if p.get("writes_this_face_unconditionally"))
        if n_same != r["producers_writing_this_face_unconditionally"]:
            problems.append("pair %s/%s same-doc counter does not re-add" % (r["face"], r["key"]))
        if r["verdict"] == V_UNCONDITIONAL_SAME_DOC and not n_same:
            problems.append("pair %s/%s claims a same-document write with none published"
                            % (r["face"], r["key"]))
    return problems


# ---------------------------------------------------------------- selftest
UNCOND = '''
import json
doc = {"alpha": 1, "beta": 2}
json.dump(doc, open("face.json", "w"))
'''
BRANCHY = '''
import json
doc = {"alpha": 1}
if flag:
    doc["beta"] = 2
try:
    doc.setdefault("beta", 3)
except Exception:
    pass
json.dump(doc, open("face.json", "w"))
'''
IN_CALL = '''
import json
def emit(state):
    """Writes the face.

    beta: optional, present only when the branch fired.
    """
    out = {"alpha": 1, "beta": state}
    json.dump(out, open("face.json", "w"))
    return out
'''


def _fixture(tmp):
    os.makedirs(os.path.join(tmp, "scripts"), exist_ok=True)
    for name, src in (("uncond.py", UNCOND), ("branchy.py", BRANCHY), ("incall.py", IN_CALL)):
        with io.open(os.path.join(tmp, "scripts", name), "w", encoding="utf-8",
                     newline="\n") as fh:
            fh.write(src)
    return tmp


def selftest():
    import tempfile
    legs = []

    sites = write_sites(UNCOND, "beta")
    legs.append(("an unconditional module-level dict literal is classified unconditional",
                 sites and sites[0]["path_class"] == W_UNCONDITIONAL))

    sites = write_sites(BRANCHY, "beta")
    classes = sorted({s["path_class"] for s in sites})
    legs.append(("an if/subscript write and a try/setdefault are both branches",
                 classes == [W_BRANCH] and len(sites) == 2))
    legs.append(("the if write records its test",
                 any(s["conditional_ancestors"] and s["conditional_ancestors"][0]["kind"] == "If"
                     for s in sites)))
    legs.append(("setdefault is classified apart from a plain store",
                 any(s["form"] == "setdefault" for s in sites)
                 and any(s["form"] == "subscript_write" for s in sites)))

    sites = write_sites(IN_CALL, "beta")
    legs.append(("a write inside a function is inside_a_callable, not conditional",
                 sites and sites[0]["path_class"] == W_CALLABLE
                 and sites[0]["enclosing_function"] == "emit"))
    legs.append(("a callable defined but never referenced anywhere reads as 0",
                 callable_referenced(IN_CALL, "emit") == 0))
    legs.append(("a callable that is called reads as a positive reference count",
                 callable_referenced(IN_CALL + "\nRESULT = emit(None)\n", "emit") >= 1))

    decl = docstring_declarations(IN_CALL, "beta")
    legs.append(("a docstring line naming the key beside a marker is a declaration",
                 len(decl) == 1 and "optional" in decl[0]["line"].lower()))
    legs.append(("a docstring line naming the key without a marker is not a declaration",
                 not docstring_declarations(IN_CALL, "alpha")))

    legs.append(("pair verdict: an unconditional write into the same face wins",
                 pair_verdict([{"path_class": W_UNCONDITIONAL,
                                "writes_this_face_unconditionally": True}])
                 == V_UNCONDITIONAL_SAME_DOC))
    legs.append(("pair verdict: an unconditional write elsewhere is an attribution failure",
                 pair_verdict([{"path_class": W_UNCONDITIONAL,
                                "writes_this_face_unconditionally": False}])
                 == V_UNCONDITIONAL_ELSEWHERE))
    legs.append(("pair verdict: all-branch",
                 pair_verdict([{"path_class": W_BRANCH}]) == V_BRANCH))
    legs.append(("pair verdict: all-callable",
                 pair_verdict([{"path_class": W_CALLABLE}]) == V_CALLABLE))
    legs.append(("pair verdict: unmixed classes disagree -> mixed",
                 pair_verdict([{"path_class": W_BRANCH}, {"path_class": W_CALLABLE}]) == V_MIXED))
    legs.append(("pair verdict: nothing found",
                 pair_verdict([]) == V_NONE))

    legs.append(("a key that only appears in a string value is not a write site",
                 write_sites('doc = {"note": "beta"}', "beta") == []))
    legs.append(("an unparseable producer returns None rather than an empty list",
                 write_sites("def f(:\n", "beta") is None))
    legs.append(("a conditional expression in the value is recorded as IfExp, not as a branch",
                 (write_sites('doc = {"beta": 1 if flag else 2}', "beta")[0]["value_form"]
                  == "IfExp")))

    with tempfile.TemporaryDirectory() as tmp:
        _fixture(tmp)
        with io.open(os.path.join(tmp, "face.json"), "w", encoding="utf-8") as fh:
            json.dump({"note": "carries beta only on some runs"}, fh)
        prose = face_prose_names_the_key("face.json", "beta", root=tmp)
        legs.append(("the face's own prose is searched for the key", bool(prose)))
        legs.append(("a face that does not name the key in prose reports empty",
                     face_prose_names_the_key("face.json", "alpha", root=tmp) == []))

    bad = [name for name, ok in legs if not ok]
    print("selftest %d/%d" % (len(legs) - len(bad), len(legs)))
    for name in bad:
        print("  FAIL", name)
    return 0 if not bad else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        doc = build()
        path = write_face(OUTDIR, doc)
        m = doc["measure"]
        print("verdict:", doc["verdict"])
        print("pairs %d / reads %d / keys %d / faces %d"
              % (m["distinct_pairs"], m["producer_named_reads"], m["distinct_keys"],
                 m["distinct_faces"]))
        print("by verdict:", json.dumps(m["pairs_by_verdict"], ensure_ascii=False))
        print("declared pairs:", m["pairs_with_a_declaration"],
              "| face prose names the key:", m["pairs_where_the_face_prose_names_the_key"])
        print("face:", path)
        return 0
    if cmd == "verify":
        problems = verify()
        print("verify problems:", problems)
        return 0 if not problems else 1
    if cmd == "selftest":
        return selftest()
    print("unknown command %r (run|verify|selftest)" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))