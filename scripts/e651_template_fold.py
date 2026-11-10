"""E651 -- do the 14 expression-built strings E647 left unresolved name a counted read module once
their operands are folded from the bindings of the module they are written in?

E647 matched every string a hit module can be asked to *spell* -- plain literals, all-constant
f-strings, ``"a" + "b"`` folds -- and published the rest as ``unresolved``: an f-string with a
formatted value, ``%`` formatting, ``str.format``.  It named that residual as its own limit (480
strings measured, 14 unresolved), so the residual is a hole, not a disclaimer.

An expression-built string can carry a target name in two disjoint places:

  * in its **template** -- the literal text the expression starts from.  That text is measurable
    for all three forms (the left operand of ``%``, the receiver of ``.format``, and the constant
    fragments of an f-string), and it is measured here *before* any operand is resolved, so a
    template that names a target is published as a template hit rather than hidden inside a fold;
  * in its **operands** -- a value substituted into the template can only be a name if that value
    is knowable.  This study resolves each operand against the scope chain the site sits in
    (literal, the module's own string constant, an alias of one, a string constant assigned in the
    enclosing function) and publishes the binding class for every operand, including the ones it
    cannot resolve (parameter, loop target, comprehension target, call result, other expression,
    unbound name).  Only a site whose operands are all resolved is folded, with the real Python
    operator applied, so a ``%d`` template fed a string constant raises and is published as a fold
    error instead of being read as a folded value.

The two arms are counted apart on purpose: a template hit is a name written in the source, a folded
hit is a name produced by a value, and a residual (a site that cannot be folded) is a limit of the
static arm rather than a zero.

Nothing here re-reads E647's rows: the hits, the counted read lines and the unresolved sites are all
re-derived from the tree, and E647's published counts (7 hits, 14 unresolved) are carried only as
reconciliation figures.  Spellings and match classes are E647's own functions so that a match here
means the same thing it meant there.
"""
import argparse
import ast
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-10"
FACE = "UNRESOLVESTR.json"
LATEST = "unresolvestr_latest.json"
STUDY = "E651_template_fold"
SOURCE_FACE = "results/state_tilt/STRINGREACH.json"
SELF_PARTS = ("e651_", "run_e651_", "_probe_e651", "_r1669")
MAX_OPERANDS = 12
MAX_VALUE = 160
MAX_EXAMPLES = 25

import e640_writeread_collide as e640  # noqa: E402
import e642_module_write_key as e642  # noqa: E402
import e646_crossmodule_key as e646  # noqa: E402
import e647_string_reach as e647  # noqa: E402

SITE_KINDS = ("percent_formatting", "fstring_has_a_formatted_value", "str_format")
BINDING_CLASSES = (
    "literal",
    "module_level_string_constant",
    "module_level_name_alias",
    "assignment_in_scope_string_constant",
    "function_parameter",
    "loop_target",
    "comprehension_target",
    "exception_target",
    "module_level_non_constant",
    "assignment_in_scope_non_constant",
    "call_result",
    "attribute_or_subscript",
    "other_expression",
    "unbound_name",
)
RESOLVED_CLASSES = ("literal", "module_level_string_constant", "module_level_name_alias",
                    "assignment_in_scope_string_constant")
FOLD_REASONS = (
    "all_operands_resolved",
    "residual_operand_binding",
    "operand_expression_unsupported",
    "format_spec_present",
    "conversion_present",
    "operator_raised",
    "no_operand",
)
TEMPLATE_ARMS = ("template_fragment", "folded_value")

V_NO_UNRESOLVED = (
    "the hit modules build no string from an expression, so E647's unresolved arm is empty by "
    "measurement and there is nothing to fold")
V_TEMPLATE_NAMES = (
    "a measurable template fragment already names a counted read module, so the expression-built "
    "string carries the name before any operand is resolved and folding is not needed to see it")
V_FOLD_NAMES = (
    "no template fragment names a counted read module, but folding the operands from their own "
    "bindings does, so the expression arm carries the name through a value rather than the text")
V_FOLDED_NONE_CLOSED = (
    "every expression-built string in the hit modules folds from its own module's bindings and "
    "none names a counted read module, so E647's unresolved arm is closed at operand level too")
V_RESIDUAL_UNFOLDED = (
    "no template fragment and no folded string names a counted read module, but some sites cannot "
    "be folded from module or function bindings, so those stay outside the static arm -- a residual, "
    "not a zero")
V_RESIDUAL_NOT_A_ROUTE = (
    "no template fragment and no folded string names a counted read module, and every site that "
    "cannot be folded is consumed by formatting or by nothing at all rather than by import or file "
    "machinery, so the residual cannot be a route to a module even if a value named one")
SEVERITY = {"template_names": 3, "folded_names": 2, "residual": 1, "closed": 0}


def say(line):
    sys.stdout.write(line + "\n")


def corpus(root=ROOT):
    out = []
    for p in e642.corpus(root):
        if os.path.basename(p).startswith(SELF_PARTS):
            continue
        out.append(p)
    return out


def hid(path, root=ROOT):
    return os.path.relpath(path, root).replace("\\", "/")


def tree_of(path):
    src = io.open(path, encoding="utf-8", errors="replace").read()
    return ast.parse(src), src


# ---------------------------------------------------------------- site census
def _is_percent(node):
    return (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod)
            and isinstance(node.left, ast.Constant) and isinstance(node.left.value, str))


def _is_strformat(node):
    return (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr == "format"
            and isinstance(node.func.value, ast.Constant)
            and isinstance(node.func.value.value, str))


def _collect(node, out):
    """The same walk E647's string census does, so the residual reconciles with its 14."""
    for child in ast.iter_child_nodes(node):
        if isinstance(child, ast.Constant) and isinstance(child.value, str):
            continue
        if isinstance(child, ast.JoinedStr):
            if any(isinstance(v, ast.FormattedValue) for v in child.values):
                out.append((child, "fstring_has_a_formatted_value"))
            continue
        if isinstance(child, ast.BinOp) and isinstance(child.op, ast.Add) \
                and e647._fold_binop(child) is not None:
            continue
        if _is_percent(child):
            out.append((child, "percent_formatting"))
            continue
        if _is_strformat(child):
            out.append((child, "str_format"))
            continue
        _collect(child, out)


def unresolved_sites(tree):
    out = []
    _collect(tree, out)
    out.sort(key=lambda r: (r[0].lineno, r[0].col_offset))
    return out


# ---------------------------------------------------------------- scopes
def scope_chain(parents, node):
    """Enclosing scopes, innermost first.  Names are resolved here, never globally."""
    chain, cur = [], node
    hops = 0
    while cur in parents and hops < 40:
        p = parents[cur]
        hops += 1
        if isinstance(p, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda,
                          ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp,
                          ast.For, ast.AsyncFor, ast.Module)):
            chain.append(p)
        cur = p
    return chain


def _params(fn):
    names = set()
    args = fn.args if hasattr(fn, "args") else None
    if args is None:
        return names
    for group in (args.posonlyargs, args.args, args.kwonlyargs):
        for a in group:
            names.add(a.arg)
    if args.vararg:
        names.add(args.vararg.arg)
    if args.kwarg:
        names.add(args.kwarg.arg)
    return names


def _targets(node):
    names = set()
    t = getattr(node, "target", None)
    if t is None:
        return names
    for sub in ast.walk(t):
        if isinstance(sub, ast.Name):
            names.add(sub.id)
    return names


def module_level_bindings(tree):
    """name -> (kind, value node) for every name bound at module scope.

    The module body is a block tree, not a flat list (E643): an assignment inside ``try:`` /
    ``if:`` / ``with:`` is still module scope, so the walk descends through compound statements
    while refusing to enter functions, lambdas and classes.  Loop and except targets are recorded
    as their own kinds rather than as assignments, because their value depends on the iteration or
    the exception and not on the source text.
    """
    out = {}

    def walk(body):
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id not in out:
                        out[t.id] = ("assign", node.value)
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                if node.value is not None and node.target.id not in out:
                    out[node.target.id] = ("assign", node.value)
            elif isinstance(node, (ast.For, ast.AsyncFor)):
                for n in _targets(node):
                    out.setdefault(n, ("loop_target", None))
            if isinstance(node, ast.ExceptHandler) and node.name:
                out.setdefault(node.name, ("exception_target", None))
            for field in ("body", "orelse", "finalbody"):
                sub = getattr(node, field, None)
                if isinstance(sub, list):
                    walk(sub)
            for handler in getattr(node, "handlers", []) or []:
                if handler.name:
                    out.setdefault(handler.name, ("exception_target", None))
                walk(handler.body)
            if isinstance(node, (ast.If, ast.While)):
                walk(node.orelse)
            if isinstance(node, ast.Match):
                for case in node.cases:
                    walk(case.body)

    walk(tree.body)
    return out


def _in_scope_assignments(scope_node, name):
    """Assignments to ``name`` inside a function/lambda body, not descending into nested scopes."""
    found = []

    def walk(node):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef,
                                  ast.Lambda)):
                continue
            if isinstance(child, ast.Assign):
                for t in child.targets:
                    if isinstance(t, ast.Name) and t.id == name:
                        found.append(child.value)
            elif isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name) \
                    and child.target.id == name and child.value is not None:
                found.append(child.value)
            walk(child)

    body = getattr(scope_node, "body", None)
    if isinstance(body, list):
        for node in body:
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id == name:
                        found.append(node.value)
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) \
                    and node.target.id == name and node.value is not None:
                found.append(node.value)
            walk(node)
    elif isinstance(body, ast.AST):
        walk(body)
    return found


def _const_string(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def resolve_name(name, chain, bindings, depth=0, seen=()):
    """What a bare name is, in the innermost scope that binds it (or a module-level alias)."""
    if depth > 4 or name in seen:
        return {"binding": "unbound_name", "value": None, "resolved_by": None}
    seen = seen + (name,)
    for scope in chain:
        if isinstance(scope, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            hit = any(name in _targets(g) for g in scope.generators)
            if hit:
                return {"binding": "comprehension_target", "value": None,
                        "resolved_by": "comprehension_generator_target"}
        elif isinstance(scope, (ast.For, ast.AsyncFor)):
            if name in _targets(scope):
                return {"binding": "loop_target", "value": None,
                        "resolved_by": "loop_target"}
        elif isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            if name in _params(scope):
                return {"binding": "function_parameter", "value": None,
                        "resolved_by": "parameter_list"}
            assigns = _in_scope_assignments(scope, name)
            if assigns:
                # the last assignment before the site would be exact; the first is published
                # instead, together with the count, so a shadowed name is visible
                value = _const_string(assigns[0])
                if value is None:
                    return {"binding": "assignment_in_scope_non_constant", "value": None,
                            "resolved_by": "function_assignment",
                            "assignments_in_scope": len(assigns)}
                return {"binding": "assignment_in_scope_string_constant", "value": value,
                        "resolved_by": "function_assignment",
                        "assignments_in_scope": len(assigns)}
        elif isinstance(scope, ast.Module):
            if name not in bindings:
                continue
            kind, node = bindings[name]
            if kind == "loop_target":
                return {"binding": "loop_target", "value": None,
                        "resolved_by": "module_loop_target"}
            if kind == "exception_target":
                return {"binding": "exception_target", "value": None,
                        "resolved_by": "module_except_arm"}
            value = _const_string(node)
            if value is not None:
                return {"binding": "module_level_string_constant", "value": value,
                        "resolved_by": "module_assignment"}
            if isinstance(node, ast.Name):
                inner = resolve_name(node.id, chain, bindings, depth + 1, seen)
                return {"binding": "module_level_name_alias",
                        "value": inner["value"],
                        "resolved_by": "module_alias_of:" + inner["binding"],
                        "alias_target": node.id}
            if isinstance(node, ast.Call):
                return {"binding": "call_result", "value": None,
                        "resolved_by": "module_call"}
            return {"binding": "module_level_non_constant", "value": None,
                    "resolved_by": "module_assignment"}
    return {"binding": "unbound_name", "value": None, "resolved_by": None}


def operand_of(expr, chain, bindings):
    """One substituted value: its text, its binding class, and its value when knowable."""
    try:
        text = ast.unparse(expr)
    except Exception:  # noqa: BLE001 - unparse is best effort, the class does not depend on it
        text = type(expr).__name__
    if isinstance(expr, ast.Constant) and isinstance(expr.value, (str, int, float)):
        return {"text": text[:MAX_VALUE], "binding": "literal", "value": expr.value,
                "resolved": True, "resolved_by": "literal"}
    if isinstance(expr, ast.Name):
        got = resolve_name(expr.id, chain, bindings)
        resolved = got["binding"] in RESOLVED_CLASSES and got["value"] is not None
        row = {"text": text[:MAX_VALUE], "binding": got["binding"],
               "value": got["value"] if resolved else None,
               "resolved": resolved, "resolved_by": got["resolved_by"]}
        for k in ("alias_target", "assignments_in_scope"):
            if k in got:
                row[k] = got[k]
        return row
    if isinstance(expr, (ast.Attribute, ast.Subscript)):
        return {"text": text[:MAX_VALUE], "binding": "attribute_or_subscript", "value": None,
                "resolved": False, "resolved_by": None}
    return {"text": text[:MAX_VALUE], "binding": "other_expression", "value": None,
            "resolved": False, "resolved_by": None}


# ---------------------------------------------------------------- fold
def fold_site(kind, template, fragments, operands, has_conversion, has_format_spec,
              ordered=None):
    """Apply the real operator when every operand is known; publish why not otherwise."""
    if kind == "fstring_has_a_formatted_value":
        if has_conversion:
            return {"status": "not_foldable", "reason": "conversion_present", "value": None}
        if has_format_spec:
            return {"status": "not_foldable", "reason": "format_spec_present", "value": None}
        if not operands:
            return {"status": "not_foldable", "reason": "no_operand", "value": None}
        if not all(o["resolved"] for o in operands):
            return {"status": "not_foldable", "reason": "residual_operand_binding", "value": None}
        return {"status": "folded", "reason": "all_operands_resolved",
                "value": fstring_fold(ordered or [], operands)}
    if not operands:
        return {"status": "not_foldable", "reason": "no_operand", "value": None}
    if not all(o["resolved"] for o in operands):
        return {"status": "not_foldable", "reason": "residual_operand_binding", "value": None}
    values = [o["value"] for o in operands]
    values = [o["value"] for o in operands]
    if any(o.get("keyword") == "**" for o in operands):
        return {"status": "not_foldable", "reason": "operand_expression_unsupported",
                "value": None}
    try:
        if kind == "percent_formatting":
            if len(values) == 1 and "%" not in template.replace("%%", "")[1:]:
                built = template % values[0]
            else:
                built = template % tuple(values)
        elif kind == "str_format":
            positional = [o["value"] for o in operands if not o.get("keyword")]
            keywords = {o["keyword"]: o["value"] for o in operands if o.get("keyword")
                        and o["keyword"] != "**"}
            built = template.format(*positional, **keywords)
        else:
            built = "".join(str(v) for v in values)
    except Exception as exc:  # noqa: BLE001 - the operator's own refusal is a measurement
        return {"status": "not_foldable", "reason": "operator_raised",
                "value": None, "error": type(exc).__name__}
    if not isinstance(built, str):
        built = str(built)
    return {"status": "folded", "reason": "all_operands_resolved", "value": built}


def fstring_fold(ordered, operands):
    """An f-string's value is its constant fragments interleaved with its values, in order."""
    parts = []
    for marker, payload in ordered:
        parts.append(payload if marker == "c" else str(operands[payload]["value"]))
    return "".join(parts)


def describe_site(tree, parents, node, kind):
    bindings = module_level_bindings(tree)
    chain = scope_chain(parents, node)
    templates, fragments, operands = [], [], []
    has_conversion = has_format_spec = False
    if kind == "percent_formatting":
        template = node.left.value
        templates = [template]
        right = node.right
        exprs = list(right.elts) if isinstance(right, ast.Tuple) else [right]
        operands = [operand_of(e, chain, bindings) for e in exprs]
    elif kind == "str_format":
        template = node.func.value.value
        templates = [template]
        exprs = list(node.args) + [k.value for k in node.keywords]
        kw_names = [None] * len(node.args) + [k.arg for k in node.keywords]
        operands = []
        for e, kw in zip(exprs, kw_names):
            row = operand_of(e, chain, bindings)
            row["keyword"] = kw if kw else ("**" if kw is None and e in
                                            [k.value for k in node.keywords] else None)
            if kw is None and any(e is k.value for k in node.keywords):
                row["keyword"] = "**"
            operands.append(row)
    else:
        template = ""
        ordered = []
        for v in node.values:
            if isinstance(v, ast.Constant) and isinstance(v.value, str):
                fragments.append(v.value)
                ordered.append(("c", v.value))
            elif isinstance(v, ast.FormattedValue):
                if v.conversion not in (-1, None):
                    has_conversion = True
                if v.format_spec is not None:
                    has_format_spec = True
                ordered.append(("v", len(operands)))
                operands.append(operand_of(v.value, chain, bindings))
        template = "\x00".join(fragments)
        templates = [template]
    fold = fold_site(kind, template if kind != "fstring_has_a_formatted_value" else template,
                     fragments, operands, has_conversion, has_format_spec,
                     ordered if kind == "fstring_has_a_formatted_value" else None)
    cons = e647.consumption(parents, node)
    return {
        "line": node.lineno,
        "column": node.col_offset,
        "kind": kind,
        "template": template[:MAX_VALUE],
        "template_fragments": [f[:MAX_VALUE] for f in fragments] if fragments else [template[:MAX_VALUE]],
        "operands_total": len(operands),
        "operands": operands[:MAX_OPERANDS],
        "operands_elided": max(0, len(operands) - MAX_OPERANDS),
        "fold": fold,
        "consumer": cons["call"],
        "consumer_class": cons["consumer_class"],
        "bound_name": cons["bound_name"],
        "hops": cons["hops"],
        "naming": [],
        "naming_count": 0,
        "folded_naming": [],
        "folded_naming_count": 0,
        "reach": "no_literal_names_the_target",
    }


def site_rows(tree, parents=None):
    parents = parents or e647.parents_of(tree)
    return [describe_site(tree, parents, node, kind) for node, kind in unresolved_sites(tree)]


# ---------------------------------------------------------------- targets
def attach_targets(row, spelling_map):
    """Match the site's template fragments, and its folded value when it has one, in two arms."""
    naming = []
    for cls_name, values in (("template_fragment", row["template_fragments"]),):
        for value in values:
            for rm, sp in sorted(spelling_map.items()):
                m = e647.match_class(value, sp)
                if m is None:
                    continue
                naming.append({"arm": cls_name, "read_module": rm, "value": value[:MAX_VALUE],
                               "match": m})
    folded = row["fold"].get("value")
    folded_naming = []
    if row["fold"]["status"] == "folded" and folded is not None:
        for rm, sp in sorted(spelling_map.items()):
            m = e647.match_class(folded, sp)
            if m is None:
                continue
            folded_naming.append({"arm": "folded_value", "read_module": rm,
                                  "value": folded[:MAX_VALUE], "match": m})
    row["naming"] = naming[:MAX_EXAMPLES]
    row["naming_count"] = len(naming)
    row["folded_naming"] = folded_naming[:MAX_EXAMPLES]
    row["folded_naming_count"] = len(folded_naming)
    row["reach"] = site_reach_of(row)
    return row


def site_reach_of(row):
    """The strongest route the site's own naming entries give, in E647's reach vocabulary."""
    entries = ([{"consumer_class": row["consumer_class"]} for _ in row.get("naming") or []]
               + [{"consumer_class": row["consumer_class"]} for _ in row.get("folded_naming") or []])
    return e647.reach_class_of(entries)


# ---------------------------------------------------------------- population
def read_population(root=ROOT):
    return e646.read_population(root)


def published_counts(root=ROOT):
    """E647's published counts -- reconciliation figures, never inputs."""
    path = os.path.join(root, SOURCE_FACE)
    try:
        doc = json.load(io.open(path, encoding="utf-8"))
    except (OSError, ValueError):
        return {"hits": None, "unresolved_strings": None}
    c = doc.get("counts") or {}
    return {"hits": c.get("hits_re_derived"), "unresolved_strings": c.get("unresolved_strings")}


# ---------------------------------------------------------------- measure
def measure(root=ROOT):
    files = corpus(root)
    reads = read_population(root)
    keys = {r["key"] for r in reads if r["key"]}
    hits = e646.re_derive_hits(root, files, keys)
    pub = published_counts(root)

    by_module = {}
    for h in hits:
        by_module.setdefault(h["module"], []).append(h)

    read_rows = [r for r in reads]
    rows, pairs = [], []
    for module in sorted(by_module):
        hit_list = by_module[module]
        tree, _src = tree_of(os.path.join(root, module))
        named_keys = {k for h in hit_list for k in h["row_keys_named"]}
        targets_read = sorted({r["module"] for r in read_rows if r["key"] in named_keys})
        spelling_map = {rm: e647.spellings_of(rm, root) for rm in targets_read}
        sites = [attach_targets(s, spelling_map) for s in site_rows(tree)]
        rows.append({
            "module": module,
            "module_class": e646.module_class(module),
            "hit_lines": [{"line": h["line"], "column": h["column"], "keys": h["keys"],
                           "row_keys_named": h["row_keys_named"]} for h in hit_list],
            "read_modules_involved": targets_read,
            "sites": sites,
        })
        for s in sites:
            for n in (s["naming"] or []) + (s["folded_naming"] or []):
                pairs.append({"hit_module": module, "read_module": n["read_module"],
                              "line": s["line"], "column": s["column"], "kind": s["kind"],
                              "arm": n["arm"], "match": n["match"],
                              "consumer_class": s["consumer_class"],
                              "reach": s["reach"]})

    counts = counts_of(rows, pairs, len(files), len(hits), len(reads), len(keys), pub)
    m = {
        "study": STUDY,
        "source_face": SOURCE_FACE,
        "method": ("re-derive E646's cross-module hits and E647's unresolved sites from the tree; "
                   "for every expression-built string publish the measurable template (the left "
                   "operand of %, the receiver of .format, the constant fragments of an f-string) "
                   "and match it before resolving anything; then resolve every substituted operand "
                   "against the scope chain the site sits in (literal / the module's own string "
                   "constant / an alias of one / a string constant assigned in the enclosing "
                   "function) and publish the binding class of every operand, including the ones "
                   "that are not knowable; fold only sites whose operands are all resolved, by "
                   "applying the real Python operator, and match the folded value as a second arm"),
        "population_source": ("%d Python files of E642's corpus, %d counted read line(s) over %d "
                              "key(s), %d cross-module hit(s) in %d module(s)"
                              % (len(files), len(reads), len(keys), len(hits), len(rows))),
        "counts": counts,
        "rows": rows,
        "pairs": pairs,
        "limits": [
            "a folded value proves the string the source would build at that point; it does not "
            "prove the call that consumes it resolves a module object, so a folded import-string "
            "route is a route and not a demonstration",
            "operands are resolved from module-scope assignments and from assignments inside the "
            "enclosing function, taking the first assignment in source order; a name reassigned "
            "before the site is published with its assignment count but not ordered, which is a "
            "limit of the resolver rather than a claim about the value",
            "a name bound by a loop or comprehension target is not resolved even when the iterable "
            "is a literal list of strings, because the value depends on the iteration the string is "
            "built in; those sites are published as residual with their binding class",
            "conversion (!r / !s) and a format spec inside an f-string are not folded; the site is "
            "published with that reason so the evasion is visible",
            "templates are matched as whole tokens with E647's match classes, so a fragment that "
            "names only a family prefix is not a hit",
            "the read population is E638's join (one definition), so a change to that join moves "
            "this study's pairs without touching its sites",
            "files over 1MB are skipped rather than parsed (E391's cap) and are counted by the "
            "population this study re-derives",
        ],
    }
    m["verdict"] = decide(counts)
    m["answer"] = answer_of(counts)
    return m


def counts_of(rows, pairs, files_scanned, hits, reads, keys, published):
    def hist(values):
        out = {}
        for v in values:
            out[v] = out.get(v, 0) + 1
        return out

    sites = [s for r in rows for s in r["sites"]]
    operands = [o for s in sites for o in s["operands"]]
    by_kind = hist([s["kind"] for s in sites])
    by_binding = {k: 0 for k in BINDING_CLASSES}
    for o in operands:
        by_binding[o["binding"]] = by_binding.get(o["binding"], 0) + 1
    reasons = {k: 0 for k in FOLD_REASONS}
    for s in sites:
        reasons[s["fold"]["reason"]] = reasons.get(s["fold"]["reason"], 0) + 1
    by_reach = hist([s["reach"] for s in sites])
    counts = {
        "python_files_scanned": files_scanned,
        "counted_read_lines": reads,
        "counted_row_keys": keys,
        "hits_re_derived": hits,
        "hits_published_by_e647": published.get("hits"),
        "distinct_hit_modules": len(rows),
        "expression_built_strings": len(sites),
        "expression_built_strings_published_by_e647": published.get("unresolved_strings"),
        "sites_by_kind": by_kind,
        "sites_by_consumer_class": hist([s["consumer_class"] for s in sites]),
        "sites_consumed_by_loader_machinery": sum(
            1 for s in sites if s["consumer_class"] in e647.LOADER_CLASSES),
        "sites_folded": sum(1 for s in sites if s["fold"]["status"] == "folded"),
        "sites_not_foldable": sum(1 for s in sites if s["fold"]["status"] == "not_foldable"),
        "sites_by_fold_reason": reasons,
        "operands_total": len(operands),
        "operands_resolved": sum(1 for o in operands if o["resolved"]),
        "operands_by_binding": by_binding,
        "template_fragments_naming_a_target": sum(s["naming_count"] for s in sites),
        "folded_strings_naming_a_target": sum(s["folded_naming_count"] for s in sites),
        "sites_by_reach": by_reach,
        "sites_reaching_a_target": sum(1 for s in sites if s["naming_count"] or s["folded_naming_count"]),
        "pairs": len(pairs),
        "pairs_by_arm": hist([p["arm"] for p in pairs]),
        "pairs_by_match_class": hist([p["match"] for p in pairs]),
        "pairs_by_reach": hist([p["reach"] for p in pairs]),
        "read_modules_involved": len({p["read_module"] for p in pairs}),
        "hit_module_class_histogram": hist([r["module_class"] for r in rows]),
    }
    return counts


def decide(c):
    if not c.get("expression_built_strings"):
        return V_NO_UNRESOLVED
    if c.get("template_fragments_naming_a_target"):
        return V_TEMPLATE_NAMES
    if c.get("folded_strings_naming_a_target"):
        return V_FOLD_NAMES
    if c.get("sites_not_foldable"):
        if not c.get("sites_consumed_by_loader_machinery"):
            return V_RESIDUAL_NOT_A_ROUTE
        return V_RESIDUAL_UNFOLDED
    return V_FOLDED_NONE_CLOSED


def answer_of(c):
    return ("%d file(s), %d cross-module hit(s) in %d module(s), %d expression-built string(s) "
            "re-derived (E647 published %s) split %s; %d folded / %d not foldable, reasons %s; "
            "%d operand(s) of which %d resolved, bindings %s; %d template fragment(s) and %d "
            "folded string(s) name a target, pair matches %s; the %d site(s) consumed by %s split "
            "by reach %s"
            % (c["python_files_scanned"], c["hits_re_derived"], c["distinct_hit_modules"],
               c["expression_built_strings"], c["expression_built_strings_published_by_e647"],
               json.dumps(c["sites_by_kind"], sort_keys=True), c["sites_folded"],
               c["sites_not_foldable"], json.dumps(c["sites_by_fold_reason"], sort_keys=True),
               c["operands_total"], c["operands_resolved"],
               json.dumps(c["operands_by_binding"], sort_keys=True),
               c["template_fragments_naming_a_target"], c["folded_strings_naming_a_target"],
               json.dumps(c["pairs_by_match_class"], sort_keys=True),
               c["expression_built_strings"],
               json.dumps(c["sites_by_consumer_class"], sort_keys=True),
               json.dumps(c["sites_by_reach"], sort_keys=True)))


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
    "hits_re_derived", "distinct_hit_modules", "expression_built_strings", "sites_folded",
    "sites_not_foldable", "operands_total", "operands_resolved",
    "sites_consumed_by_loader_machinery",
    "template_fragments_naming_a_target", "folded_strings_naming_a_target",
    "sites_reaching_a_target", "pairs", "read_modules_involved",
)


def live_counts(rows, pairs):
    sites = [s for r in rows for s in r.get("sites") or []]
    operands = [o for s in sites for o in s.get("operands") or []]
    by_binding = {k: 0 for k in BINDING_CLASSES}
    for o in operands:
        by_binding[o.get("binding")] = by_binding.get(o.get("binding"), 0) + 1
    reasons = {k: 0 for k in FOLD_REASONS}
    for s in sites:
        reasons[s.get("fold", {}).get("reason")] = reasons.get(
            s.get("fold", {}).get("reason"), 0) + 1
    live = {
        "hits_re_derived": sum(len(r.get("hit_lines") or []) for r in rows),
        "distinct_hit_modules": len({r.get("module") for r in rows}),
        "expression_built_strings": len(sites),
        "sites_by_kind": _hist([s.get("kind") for s in sites]),
        "sites_by_consumer_class": _hist([s.get("consumer_class") for s in sites]),
        "sites_consumed_by_loader_machinery": sum(
            1 for s in sites if s.get("consumer_class") in e647.LOADER_CLASSES),
        "sites_folded": sum(1 for s in sites if s.get("fold", {}).get("status") == "folded"),
        "sites_not_foldable": sum(1 for s in sites
                                  if s.get("fold", {}).get("status") == "not_foldable"),
        "sites_by_fold_reason": reasons,
        "operands_total": len(operands),
        "operands_resolved": sum(1 for o in operands if o.get("resolved")),
        "operands_by_binding": by_binding,
        "template_fragments_naming_a_target": sum(s.get("naming_count") or 0 for s in sites),
        "folded_strings_naming_a_target": sum(s.get("folded_naming_count") or 0 for s in sites),
        "sites_by_reach": _hist([s.get("reach") for s in sites]),
        "sites_reaching_a_target": sum(1 for s in sites
                                       if (s.get("naming_count") or 0)
                                       or (s.get("folded_naming_count") or 0)),
        "pairs": len(pairs),
        "pairs_by_arm": _hist([p.get("arm") for p in pairs]),
        "pairs_by_match_class": _hist([p.get("match") for p in pairs]),
        "pairs_by_reach": _hist([p.get("reach") for p in pairs]),
        "read_modules_involved": len({p.get("read_module") for p in pairs}),
        "hit_module_class_histogram": _hist([r.get("module_class") for r in rows]),
    }
    return live


def _hist(values):
    out = {}
    for v in values:
        out[v] = out.get(v, 0) + 1
    return out


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
    for key in ("sites_by_kind", "sites_by_consumer_class", "sites_by_fold_reason",
                "operands_by_binding", "sites_by_reach", "pairs_by_arm",
                "pairs_by_match_class", "pairs_by_reach", "hit_module_class_histogram"):
        if (c.get(key) or {}) != (live.get(key) or {}):
            problems.append("counts.%s is not the histogram the rows give" % key)
    if (c.get("sites_folded") or 0) + (c.get("sites_not_foldable") or 0) != live.get(
            "expression_built_strings"):
        problems.append("the fold status buckets do not add up to the sites")
    if sum((c.get("sites_by_fold_reason") or {}).values()) != live.get("expression_built_strings"):
        problems.append("the fold-reason histogram is not the site count")
    if sum((c.get("sites_by_reach") or {}).values()) != live.get("expression_built_strings"):
        problems.append("the reach buckets do not add up to the sites")
    if (c.get("operands_resolved") or 0) > (c.get("operands_total") or 0):
        problems.append("more operands are resolved than exist")
    if sum((c.get("operands_by_binding") or {}).values()) != live.get("operands_total"):
        problems.append("the binding histogram is not the operand count")
    if set(c.get("operands_by_binding") or {}) - set(BINDING_CLASSES):
        problems.append("an operand binding class outside the published set is reported")
    if set(c.get("sites_by_fold_reason") or {}) - set(FOLD_REASONS):
        problems.append("a fold reason outside the published set is reported")
    if set(c.get("pairs_by_arm") or {}) - set(TEMPLATE_ARMS):
        problems.append("a pair arm outside the published set is reported")
    if sum((c.get("pairs_by_arm") or {}).values()) != len(pairs):
        problems.append("the arm buckets do not add up to the pairs")
    if (c.get("template_fragments_naming_a_target") or 0) != 0:
        if not any(p.get("arm") == "template_fragment" for p in pairs):
            problems.append("the template arm count is published with no template pair")
    if (c.get("folded_strings_naming_a_target") or 0) != 0:
        if not any(p.get("arm") == "folded_value" for p in pairs):
            problems.append("the folded arm count is published with no folded pair")
    # every site's reach must be the one its own naming entries force, and its fold must agree
    # with its own operands
    for r in rows:
        for s in r.get("sites") or []:
            want = site_reach_of(s)
            if s.get("reach") != want:
                problems.append("site %s:%s is classified %r but its own entries force %r"
                                % (r.get("module"), s.get("line"), s.get("reach"), want))
                break
            if (s.get("naming_count") or 0) != len(s.get("naming") or []):
                problems.append("site %s:%s publishes a naming count its list does not carry"
                                % (r.get("module"), s.get("line")))
                break
            if (s.get("folded_naming_count") or 0) != len(s.get("folded_naming") or []):
                problems.append("site %s:%s publishes a folded count its list does not carry"
                                % (r.get("module"), s.get("line")))
                break
            fold = s.get("fold") or {}
            if fold.get("status") == "folded":
                if not all(o.get("resolved") for o in s.get("operands") or []):
                    problems.append("site %s:%s is folded with an unresolved operand"
                                    % (r.get("module"), s.get("line")))
                    break
                if fold.get("reason") != "all_operands_resolved":
                    problems.append("site %s:%s is folded for a reason other than full resolution"
                                    % (r.get("module"), s.get("line")))
                    break
                if not fold.get("value"):
                    problems.append("site %s:%s is folded to no value"
                                    % (r.get("module"), s.get("line")))
                    break
            else:
                if fold.get("value") is not None:
                    problems.append("site %s:%s is not folded but publishes a value"
                                    % (r.get("module"), s.get("line")))
                    break
            if fold.get("status") == "not_foldable" and fold.get("reason") == \
                    "all_operands_resolved":
                problems.append("site %s:%s publishes a residual under a folded reason"
                                % (r.get("module"), s.get("line")))
                break
            if (s.get("operands_total") or 0) != ((len(s.get("operands") or []))
                                                 + (s.get("operands_elided") or 0)):
                problems.append("site %s:%s publishes an operand count its list does not add to"
                                % (r.get("module"), s.get("line")))
                break
    for p in pairs:
        row = next((r for r in rows if r.get("module") == p.get("hit_module")), None)
        if row is None:
            problems.append("pair names a module with no row: %s" % p.get("hit_module"))
            break
        site = next((s for s in row.get("sites") or []
                     if s.get("line") == p.get("line") and s.get("column") == p.get("column")), None)
        if site is None:
            problems.append("pair names a site its module row does not carry")
            break
        if p.get("arm") == "template_fragment" and not (site.get("naming_count") or 0):
            problems.append("a template pair points at a site with no naming fragment")
            break
        if p.get("arm") == "folded_value" and not (site.get("folded_naming_count") or 0):
            problems.append("a folded pair points at a site with no folded name")
            break
        if p.get("reach") != site.get("reach"):
            problems.append("a pair reach is not the one its own site forces")
            break
    for key, pub in (("hits_published_by_e647", "hits_re_derived"),
                     ("expression_built_strings_published_by_e647", "expression_built_strings")):
        if c.get(key) is not None and c.get(key) != c.get(pub):
            problems.append("the re-derived %s is not the one E647 published" % pub)
    if decide(live) != face.get("verdict"):
        problems.append("the published verdict is not the one the counts force")
    if face.get("verdict") == V_FOLDED_NONE_CLOSED and (live.get("sites_not_foldable") or 0):
        problems.append("the closed verdict is published with sites that could not be folded")
    if face.get("verdict") == V_RESIDUAL_UNFOLDED and not live.get("sites_not_foldable"):
        problems.append("the residual verdict is published with every site folded")
    if face.get("verdict") == V_RESIDUAL_NOT_A_ROUTE:
        if not live.get("sites_not_foldable"):
            problems.append("the not-a-route verdict is published with every site folded")
        if live.get("sites_consumed_by_loader_machinery"):
            problems.append("the not-a-route verdict is published with a loader-consumed site")
    if face.get("verdict") == V_TEMPLATE_NAMES and not live.get(
            "template_fragments_naming_a_target"):
        problems.append("the template verdict is published with no naming template fragment")
    if face.get("verdict") == V_FOLD_NAMES and live.get("template_fragments_naming_a_target"):
        problems.append("the folded verdict is published with a naming template")
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
    say("run: files=%d hits=%d(e647 %s) modules=%d sites=%d(e647 %s) by_kind=%s"
        % (c["python_files_scanned"], c["hits_re_derived"], c["hits_published_by_e647"],
           c["distinct_hit_modules"], c["expression_built_strings"],
           c["expression_built_strings_published_by_e647"],
           json.dumps(c["sites_by_kind"], sort_keys=True)))
    say("run: folded=%d not_foldable=%d reasons=%s operands=%d resolved=%d"
        % (c["sites_folded"], c["sites_not_foldable"],
           json.dumps(c["sites_by_fold_reason"], sort_keys=True),
           c["operands_total"], c["operands_resolved"]))
    say("run: template_naming=%d folded_naming=%d pairs=%d by_reach=%s"
        % (c["template_fragments_naming_a_target"], c["folded_strings_naming_a_target"],
           c["pairs"], json.dumps(c["pairs_by_reach"], sort_keys=True)))
    say("run: verdict=" + doc["verdict"])
    say("run: answer=" + doc["answer"])
    return doc, []


# ---------------------------------------------------------------- selftest
def _spellings(path="scripts/e382_x.py", faces=None):
    base = os.path.basename(path)
    return {"path": path, "basename": base, "stem": base[:-3],
            "dotted": path[:-3].replace("/", "."), "faces": faces or [],
            "face_constants_unmeasured": [], "face_constants_absent": []}


def _site(src, targets=None, index=0):
    tree = ast.parse(src)
    rows = site_rows(tree)
    if targets is None:
        return rows[index]
    return attach_targets(rows[index], targets)


def _counts(rows, pairs, published=None):
    published = published or {}
    return counts_of(rows, pairs, 10, sum(len(r["hit_lines"]) for r in rows),
                     [{"key": "k"}], 1,
                     {"hits": published.get("hits"), "unresolved_strings":
                      published.get("unresolved_strings")})


def _row(module="a.py", sites=None, cls="production_module"):
    sites = sites or []
    return {"module": module, "module_class": cls,
            "hit_lines": [{"line": 3, "column": 0, "keys": ["k"], "row_keys_named": ["k"]}],
            "read_modules_involved": [], "sites": sites}


def _pair(row, site, arm="template_fragment", reach=None):
    return {"hit_module": row["module"], "read_module": "scripts/e382_x.py",
            "line": site["line"], "column": site["column"], "kind": site["kind"],
            "arm": arm, "match": "exact_stem", "consumer_class": site["consumer_class"],
            "reach": reach or site["reach"]}


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

    def sites_reconcile_with_e647_census():
        src = ('A = "x"\n'
               'B = f"p{q}"\n' if False else '')
        src = 'q = "z"\nB = f"p{q}"\nC = "%s-%d" % (q, 1)\nD = "{a}".format(a=q)\n'
        got = [(n.lineno, kind) for n, kind in unresolved_sites(ast.parse(src))]
        assert got == [(2, "fstring_has_a_formatted_value"), (3, "percent_formatting"),
                       (4, "str_format")], got

    def all_constant_fstring_is_still_a_literal():
        got = unresolved_sites(ast.parse('F = f"ab"\n'))
        assert got == [], got

    def a_module_string_constant_is_resolved():
        s = _site('X = "e382_x"\nB = f"{X}"\n')
        assert s["operands"][0]["binding"] == "module_level_string_constant", s["operands"]
        assert s["operands"][0]["resolved"] is True, s["operands"]
        assert s["fold"]["status"] == "folded", s["fold"]
        assert s["fold"]["value"] == "e382_x", s["fold"]

    def a_module_alias_resolves_through_its_target():
        s = _site('T = "e382_x"\nX = T\nB = f"{X}"\n')
        o = s["operands"][0]
        assert o["binding"] == "module_level_name_alias", o
        assert o["resolved"] and o["value"] == "e382_x", o
        assert o["resolved_by"] == "module_alias_of:module_level_string_constant", o

    def a_function_parameter_is_a_residual_not_a_zero():
        s = _site('def f(q):\n    return f"{q}"\n')
        o = s["operands"][0]
        assert o["binding"] == "function_parameter", o
        assert o["resolved"] is False, o
        assert s["fold"]["status"] == "not_foldable", s["fold"]
        assert s["fold"]["reason"] == "residual_operand_binding", s["fold"]

    def a_loop_target_is_not_folded_even_over_a_literal_list():
        s = _site('F = ["a", "b"]\n'
                  'for q in F:\n'
                  '    print(f"{q}")\n')
        o = s["operands"][0]
        assert o["binding"] == "loop_target", o
        assert s["fold"]["status"] == "not_foldable", s["fold"]

    def a_comprehension_target_is_its_own_class():
        s = _site('print(f"{q}" for q in "ab")\n' if False else
                  '[f"{q}" for q in "ab"]\n')
        o = s["operands"][0]
        assert o["binding"] in ("comprehension_target",), o

    def a_string_constant_assigned_in_the_function_is_resolved():
        s = _site('def f():\n'
                  '    name = "e382_x"\n'
                  '    return f"{name}"\n')
        o = s["operands"][0]
        assert o["binding"] == "assignment_in_scope_string_constant", o
        assert o["resolved"] and o["value"] == "e382_x", o
        assert s["fold"]["status"] == "folded", s["fold"]

    def a_percent_template_is_applied_with_its_real_operator():
        s = _site('N = "e382_x"\nB = "%s.py" % N\n')
        assert s["fold"]["status"] == "folded", s["fold"]
        assert s["fold"]["value"] == "e382_x.py", s["fold"]
        s2 = _site('B = "%d/x" % "abc"\n')
        assert s2["fold"]["status"] == "not_foldable", s2["fold"]
        assert s2["fold"]["reason"] == "operator_raised", s2["fold"]

    def a_str_format_receiver_is_applied():
        s = _site('N = "e382_x"\nB = "{n}.py".format(n=N)\n')
        assert s["fold"]["status"] == "folded", s["fold"]
        assert s["fold"]["value"] == "e382_x.py", s["fold"]

    def conversion_and_format_spec_are_named_reasons():
        s = _site('N = "x"\nB = f"{N!r}"\n')
        assert s["fold"]["reason"] == "conversion_present", s["fold"]
        s2 = _site('N = 3\nB = f"{N:>3}"\n')
        assert s2["fold"]["reason"] == "format_spec_present", s2["fold"]

    def a_template_fragment_names_before_any_fold():
        s = _site('q = None\nB = f"{q}scripts/e382_x.py"\n')
        s = attach_targets(s, {"scripts/e382_x.py": _spellings()})
        assert s["naming_count"] == 1, s["naming"]
        assert s["naming"][0]["arm"] == "template_fragment", s["naming"]
        assert s["naming"][0]["match"] == "exact_path", s["naming"]

    def a_folded_value_names_only_after_the_fold():
        s = _site('N = "e382_x"\nB = f"{N}.py"\n')
        s = attach_targets(s, {"scripts/e382_x.py": _spellings()})
        assert s["naming_count"] == 0, s["naming"]
        assert s["folded_naming_count"] == 1, s["folded_naming"]
        assert s["folded_naming"][0]["arm"] == "folded_value", s["folded_naming"]

    def reach_classes_are_reachable():
        s = _site('import importlib\nN = "e382_x"\nimportlib.import_module(f"{N}")\n')
        s = attach_targets(s, {"scripts/e382_x.py": _spellings()})
        assert s["reach"] == "import_string_reach", s

    def no_sites_is_its_own_verdict():
        assert decide({"expression_built_strings": 0}) == V_NO_UNRESOLVED

    def closed_and_residual_are_separated():
        assert decide({"expression_built_strings": 2, "sites_not_foldable": 0}) == \
            V_FOLDED_NONE_CLOSED
        assert decide({"expression_built_strings": 2, "sites_not_foldable": 1}) == \
            V_RESIDUAL_NOT_A_ROUTE
        assert decide({"expression_built_strings": 2, "sites_not_foldable": 1,
                       "sites_consumed_by_loader_machinery": 1}) == V_RESIDUAL_UNFOLDED
        assert decide({"expression_built_strings": 2, "sites_not_foldable": 1,
                       "folded_strings_naming_a_target": 1}) == V_FOLD_NAMES
        assert decide({"expression_built_strings": 2, "sites_not_foldable": 1,
                       "folded_strings_naming_a_target": 1,
                       "template_fragments_naming_a_target": 1}) == V_TEMPLATE_NAMES

    def face_problems_accepts_a_sound_face():
        s = _site('N = "e382_x"\nB = f"{N}.py"\n')
        s = attach_targets(s, {"scripts/e382_x.py": _spellings()})
        r = _row(sites=[s])
        p = _pair(r, s, "folded_value")
        face = {"rows": [r], "pairs": [p], "counts": _counts([r], [p])}
        face["verdict"] = decide(face["counts"])
        assert face_problems(face) == [], face_problems(face)

    def face_problems_catches_a_folded_site_with_an_unresolved_operand():
        s = _site('def f(q):\n    return f"{q}"\n')
        s["fold"] = {"status": "folded", "reason": "all_operands_resolved", "value": "q"}
        r = _row(sites=[s])
        face = {"rows": [r], "pairs": [], "counts": _counts([r], [])}
        face["verdict"] = V_FOLDED_NONE_CLOSED
        assert any("unresolved operand" in x for x in face_problems(face)), face_problems(face)

    def face_problems_catches_a_reason_outside_the_set():
        s = _site('N = "x"\nB = f"{N}"\n')
        s["fold"]["reason"] = "made_up"
        r = _row(sites=[s])
        face = {"rows": [r], "pairs": [], "counts": _counts([r], [])}
        face["verdict"] = V_FOLDED_NONE_CLOSED
        assert any("outside the published set" in x for x in face_problems(face)), \
            face_problems(face)

    def face_problems_catches_a_drifted_count():
        s = _site('N = "x"\nB = f"{N}"\n')
        r = _row(sites=[s])
        face = {"rows": [r], "pairs": [], "counts": _counts([r], [])}
        face["counts"]["expression_built_strings"] += 1
        face["verdict"] = decide(face["counts"])
        assert any("does not re-add" in x for x in face_problems(face)), face_problems(face)

    def face_problems_catches_a_residual_under_a_closed_verdict():
        s = _site('def f(q):\n    return f"{q}"\n')
        r = _row(sites=[s])
        face = {"rows": [r], "pairs": [], "counts": _counts([r], [])}
        face["verdict"] = V_FOLDED_NONE_CLOSED
        assert any("closed verdict" in x for x in face_problems(face)), face_problems(face)

    def face_problems_catches_a_reconciliation_that_moves():
        s = _site('N = "x"\nB = f"{N}"\n')
        r = _row(sites=[s])
        face = {"rows": [r], "pairs": [], "counts": _counts([r], [], {"unresolved_strings": 9})}
        face["verdict"] = decide(face["counts"])
        assert any("E647" in x for x in face_problems(face)), face_problems(face)

    def a_module_constant_inside_a_compound_statement_is_resolved():
        s = _site('try:\n'
                  '    NAME = "e382_x"\n'
                  'except Exception:\n'
                  '    NAME = "other"\n'
                  'B = f"{NAME}.py"\n')
        o = s["operands"][0]
        assert o["binding"] == "module_level_string_constant", o
        assert s["fold"]["status"] == "folded", s
        assert s["fold"]["value"] == "e382_x.py", s["fold"]

    def an_except_arm_name_is_its_own_class():
        s = _site('try:\n'
                  '    pass\n'
                  'except Exception as ex:\n'
                  '    msg = "boom: %r" % ex\n')
        o = s["operands"][0]
        assert o["binding"] == "exception_target", o
        assert s["fold"]["status"] == "not_foldable", s["fold"]

    def a_module_loop_target_is_not_folded():
        s = _site('F = ["a", "b"]\n'
                  'for q in F:\n'
                  '    P = "v=%s" % q\n')
        o = s["operands"][0]
        assert o["binding"] == "loop_target", o
        assert s["fold"]["status"] == "not_foldable", s["fold"]

    def answer_names_the_numbers():
        s = _site('N = "x"\nB = f"{N}"\n')
        r = _row(sites=[s])
        a = answer_of(_counts([r], []))
        for token in ("expression-built string", "folded", "operand", "split by reach"):
            assert token in a, (token, a)

    for name, fn in [
        ("sites_reconcile_with_e647_census", sites_reconcile_with_e647_census),
        ("all_constant_fstring_is_still_a_literal", all_constant_fstring_is_still_a_literal),
        ("a_module_string_constant_is_resolved", a_module_string_constant_is_resolved),
        ("a_module_alias_resolves_through_its_target", a_module_alias_resolves_through_its_target),
        ("a_function_parameter_is_a_residual_not_a_zero",
         a_function_parameter_is_a_residual_not_a_zero),
        ("a_loop_target_is_not_folded_even_over_a_literal_list",
         a_loop_target_is_not_folded_even_over_a_literal_list),
        ("a_comprehension_target_is_its_own_class", a_comprehension_target_is_its_own_class),
        ("a_string_constant_assigned_in_the_function_is_resolved",
         a_string_constant_assigned_in_the_function_is_resolved),
        ("a_percent_template_is_applied_with_its_real_operator",
         a_percent_template_is_applied_with_its_real_operator),
        ("a_str_format_receiver_is_applied", a_str_format_receiver_is_applied),
        ("conversion_and_format_spec_are_named_reasons",
         conversion_and_format_spec_are_named_reasons),
        ("a_template_fragment_names_before_any_fold", a_template_fragment_names_before_any_fold),
        ("a_folded_value_names_only_after_the_fold", a_folded_value_names_only_after_the_fold),
        ("reach_classes_are_reachable", reach_classes_are_reachable),
        ("no_sites_is_its_own_verdict", no_sites_is_its_own_verdict),
        ("closed_and_residual_are_separated", closed_and_residual_are_separated),
        ("face_problems_accepts_a_sound_face", face_problems_accepts_a_sound_face),
        ("face_problems_catches_a_folded_site_with_an_unresolved_operand",
         face_problems_catches_a_folded_site_with_an_unresolved_operand),
        ("face_problems_catches_a_reason_outside_the_set",
         face_problems_catches_a_reason_outside_the_set),
        ("face_problems_catches_a_drifted_count", face_problems_catches_a_drifted_count),
        ("face_problems_catches_a_residual_under_a_closed_verdict",
         face_problems_catches_a_residual_under_a_closed_verdict),
        ("face_problems_catches_a_reconciliation_that_moves",
         face_problems_catches_a_reconciliation_that_moves),
        ("answer_names_the_numbers", answer_names_the_numbers),
        ("a_module_constant_inside_a_compound_statement_is_resolved",
         a_module_constant_inside_a_compound_statement_is_resolved),
        ("an_except_arm_name_is_its_own_class", an_except_arm_name_is_its_own_class),
        ("a_module_loop_target_is_not_folded", a_module_loop_target_is_not_folded),
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