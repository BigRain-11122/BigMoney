"""E404 -- which module constant supplies an "untraceable" fragment directory, and would that join land?

E402 traced 52 bare-basename fragments to their producer sites and stopped at 19 sites with the
class ``directory_expression_not_traceable_statically``.  That class is a statement about the
reader, not about the code: the expression was not followed through its first name.  This study
follows that name to its binding -- and then asks the only question a reader can act on, whether the
composed path is a directory the tree holds.

The trace is deliberately mechanical, one vocabulary per evidence:

  F1 fixture directory created by a runtime helper     (fx = _mkfixture(tmp))
  F2 module constant rebound inside a function         (MACHINES_DIR rebound under `global`)
  F3 directory supplied by a parameter or loop value   (d, cd)
  F4 imported constant whose module is absent          (from config import PATHS, no config.py)
  F5 constant directory inside the tree, path exists
  F6 constant directory inside the tree, path absent
  F7 directory outside the tree or git-ignored runtime cache
  F8 still unresolved by this arm

The distinction that matters: F1/F2/F3 mean the *name was never a constant in the first place* (a
fixture rebinding a module global is not a constant, it is a local written through `global`), and F4
means the script cannot import its own constant at all.  Only F5/F6 are real directory claims.

Population is read from the published E402 face; the resolution and the existence test are measured
live against the tree.

Usage:
  python scripts/e404_constant_directory_resolution.py run
  python scripts/e404_constant_directory_resolution.py verify
  python scripts/e404_constant_directory_resolution.py selftest
"""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

TODAY = "2026-11-04"
FACE = "CONSTDIRS-%s.json" % TODAY
LATEST = "constdirs_latest.json"
PUBLISHED_DIR = os.path.join(ROOT, "results", "state_tilt")
STUDY = "E404_constant_directory_resolution"
SELF_REL = "scripts/e404_constant_directory_resolution.py"
POPULATION_SOURCE = "results/state_tilt/FRAGMENTPRODUCERS-2026-11-04.json"
POPULATION_CLASS = "directory_expression_not_traceable_statically"

F1 = "fixture_directory_created_by_a_runtime_helper"
F2 = "module_constant_rebound_inside_a_function"
F3 = "directory_supplied_by_a_function_parameter_or_loop_value"
F4 = "imported_constant_module_absent_from_the_tree"
F5 = "resolved_directory_inside_the_tree_and_the_path_exists"
F6 = "resolved_directory_inside_the_tree_and_the_path_is_absent"
F7 = "resolved_directory_outside_the_tree_or_gitignored_runtime_cache"
F8 = "still_unresolved_by_this_arm"
CLASSES = (F1, F2, F3, F4, F5, F6, F7, F8)
DESIGN_FREE = (F1, F2, F3)

V_DANGLING = ("the_reader_stopped_where_a_script_cannot_start_some_untraceable_directories_come_from_"
              "an_import_whose_module_does_not_exist_in_the_tree")
V_DEAD_JOIN = ("a_module_constant_does_name_an_in_tree_directory_and_the_joined_file_is_not_there")
V_LANDS = ("every_traced_constant_names_a_directory_the_tree_holds_and_the_join_lands")
V_ALL_RUNTIME = ("every_untraceable_directory_is_supplied_at_runtime_by_a_fixture_or_a_parameter_so_"
                 "the_trace_limit_was_the_readers_not_the_codes")
V_PARTIAL = ("the_untraceable_set_splits_between_runtime_supplied_directories_and_directories_the_"
             "tree_does_not_hold_so_neither_reading_covers_it")
V_NOT_YET_PRODUCED = ("the_in_tree_directories_are_write_targets_the_corpus_has_not_produced_yet_so_"
                      "an_absent_file_is_a_pending_output_not_a_broken_path")
V_MISSING_READ_TARGET = ("an_in_tree_directory_holds_no_writer_for_the_fragment_so_the_read_can_only_"
                         "ever_fail")

TEMP_FUNCS = {"mkdtemp", "TemporaryDirectory", "mkstemp", "NamedTemporaryFile", "TemporaryFile",
              "gettempdir", "tempdir"}

EXISTS = os.path.exists


def say(message):
    print(message, flush=True)


def _read(relpath):
    with open(os.path.join(ROOT, relpath), encoding="utf-8", errors="replace") as fh:
        return fh.read()


# --------------------------------------------------------------------------- per-file context

class FileCtx(object):
    """Module bindings, imports, parent map for one source file."""

    def __init__(self, relpath, text=None):
        self.relpath = relpath
        self.text = text if text is not None else _read(relpath)
        self.tree = ast.parse(self.text)
        self.parent = {}
        for node in ast.walk(self.tree):
            for child in ast.iter_child_nodes(node):
                self.parent[child] = node
        self.module_assign = {}
        self.defs = {}
        self.imports = {}
        self.classes = {}
        self._collect()

    def src(self, node):
        try:
            return ast.get_source_segment(self.text, node) or ""
        except Exception:
            return ""

    def _collect(self):
        stack = list(self.tree.body)
        while stack:
            node = stack.pop(0)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.defs[node.name] = node
                continue
            if isinstance(node, ast.ClassDef):
                self.classes[node.name] = node
                continue
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.module_assign[target.id] = node.value
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                if node.value is not None:
                    self.module_assign[node.target.id] = node.value
            elif isinstance(node, ast.ImportFrom):
                module_name = ("." * (node.level or 0)) + (node.module or "")
                for alias in node.names:
                    self.imports[(alias.asname or alias.name)] = ("from", module_name, alias.name)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    self.imports[alias.asname or alias.name.split(".")[0]] = ("import", alias.name,
                                                                              None)
            elif isinstance(node, (ast.If, ast.Try)):
                stack.extend(getattr(node, "body", []) or [])
                stack.extend(getattr(node, "orelse", []) or [])
                stack.extend(getattr(node, "finalbody", []) or [])
                for handler in getattr(node, "handlers", []) or []:
                    stack.extend(handler.body)

    def _site_node(self, node):
        """A node from a separate parse has no parent link; anchor it on this file's tree."""
        try:
            line = getattr(node, "lineno", None)
            text = self.src(node).strip()
        except Exception:
            return None
        best = None
        for sub in ast.walk(self.tree):
            if not isinstance(sub, ast.expr):
                continue
            if text and (self.src(sub) or "").strip() == text:
                best = sub
                break
        if best is None and line:
            stmts = [sub for sub in ast.walk(self.tree)
                     if isinstance(sub, ast.stmt) and getattr(sub, "lineno", 0) <= line
                     and (getattr(sub, "end_lineno", 0) or 0) >= line]
            if stmts:
                best = sorted(stmts, key=lambda n: -(getattr(n, "end_lineno", 0)
                                                     - getattr(n, "lineno", 0)))[0]
        return best

    def enclosing_functions(self, node):
        chain = []
        cur = self.parent.get(node)
        while cur is not None:
            if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef)):
                chain.append(cur)
            cur = self.parent.get(cur)
        return chain

    def scope_binding(self, node, name):
        """Where does `name` come from at `node`?  Returns a dict describing the binding."""
        if node is not None and node not in self.parent:
            node = self._site_node(node)
        for fn in self.enclosing_functions(node):
            declared_global = any(name in g.names for g in ast.walk(fn) if isinstance(g, ast.Global))
            args = [a.arg for a in list(fn.args.args) + list(fn.args.kwonlyargs)]
            if name in args:
                return {"scope": "function_parameter", "function": fn.name, "value": None}
            bound = None
            for sub in ast.walk(fn):
                if isinstance(sub, (ast.For, ast.AsyncFor)):
                    if isinstance(sub.target, ast.Name) and sub.target.id == name:
                        bound = sub.iter
                elif isinstance(sub, (ast.With, ast.AsyncWith)):
                    for item in sub.items:
                        if isinstance(item.optional_vars, ast.Name) and item.optional_vars.id == name:
                            bound = item.context_expr
                elif isinstance(sub, (ast.Assign, ast.AnnAssign)):
                    targets = sub.targets if isinstance(sub, ast.Assign) else [sub.target]
                    for target in targets:
                        if isinstance(target, ast.Name) and target.id == name:
                            bound = sub.value
            if bound is not None:
                return {"scope": "global_rebound_in_function" if declared_global else "function_local",
                        "function": fn.name, "value": bound}
            if declared_global:
                return {"scope": "global_declared_not_assigned_here", "function": fn.name,
                        "value": None}
        if name in self.module_assign:
            return {"scope": "module", "function": None, "value": self.module_assign[name]}
        if name in self.imports:
            return {"scope": "import", "function": None, "value": self.imports[name]}
        return {"scope": "unbound", "function": None, "value": None}


# The corpus runs its scripts with scripts/ (and Tools/) on sys.path, so a bare `import settings`
# inside config/__init__.py or `import p1c_bigpanel_ops` inside scripts/ is a real module.
IMPORT_ROOTS = ("", "scripts", "Tools", "config")


def _module_file(module_name, origin_relpath=None):
    """Repo-relative path of the module a `from X import Y` would load."""
    if not module_name:
        return None
    origin_dir = os.path.dirname((origin_relpath or "").replace("\\", "/"))
    if module_name.startswith("."):
        tail = module_name.lstrip(".").replace(".", os.sep)
        bases = [origin_dir]
    else:
        tail = module_name.replace(".", os.sep)
        bases = [origin_dir] + list(IMPORT_ROOTS)
    for base in bases:
        for candidate in ((os.path.join(base, tail) + ".py") if base else (tail + ".py"),
                          os.path.join(base, tail, "__init__.py") if base else
                          os.path.join(tail, "__init__.py")):
            if candidate and os.path.exists(os.path.join(ROOT, candidate)):
                return candidate.replace("\\", "/")
    return None


def _contains_temp_helper(ctx, fn_node, depth=0):
    if depth > 2:
        return False
    for sub in ast.walk(fn_node):
        if isinstance(sub, ast.Call):
            name = sub.func.attr if isinstance(sub.func, ast.Attribute) else getattr(sub.func, "id", "")
            if name in TEMP_FUNCS:
                return True
            if isinstance(sub.func, ast.Name) and sub.func.id in ctx.defs:
                if _contains_temp_helper(ctx, ctx.defs[sub.func.id], depth + 1):
                    return True
    return False


def _join_constants(node):
    """The literal path segments carried by the expression, in source order."""
    constants = [sub for sub in ast.walk(node)
                 if isinstance(sub, ast.Constant) and isinstance(sub.value, str)]
    constants.sort(key=lambda n: (getattr(n, "lineno", 0), getattr(n, "col_offset", 0)))
    return [c.value for c in constants]


class Trace(object):
    """Resolve one directory expression one hop at a time, recording every hop."""

    def __init__(self):
        self.hops = []

    def hop(self, text):
        self.hops.append(text)


def resolve_value(ctx, node, trace, depth=0, scope=None):
    """Return (kind, base_or_None, detail).  kind is 'dir' | 'file' | one of CLASSES."""
    if depth > 14 or node is None:
        return (F8, None, "depth/None")
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return ("dir", node.value, "literal %r" % node.value)
    if isinstance(node, ast.Call):
        func = node.func
        name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
        if name in ("join", "joinpath"):
            if not node.args:
                return (F8, None, "join with no args")
            kind, base, detail = resolve_value(ctx, node.args[0], trace, depth + 1, scope)
            trace.hop("%s() base -> %s (%s)" % (name, kind, detail))
            if kind in ("dir", "file"):
                rest = [a.value for a in node.args[1:]
                        if isinstance(a, ast.Constant) and isinstance(a.value, str)]
                if rest:
                    base = os.path.join(base, *rest)
                return (kind, base, detail)
            return (kind, None, detail)
        if name == "Path":
            if node.args:
                return resolve_value(ctx, node.args[0], trace, depth + 1, scope)
            return (F8, None, "Path() with no args")
        if name == "dirname" and node.args:
            kind, base, detail = resolve_value(ctx, node.args[0], trace, depth + 1, scope)
            if kind in ("dir", "file") and base:
                return ("dir", os.path.dirname(base), detail)
            return (kind, None, detail)
        if name in ("resolve", "absolute"):
            inner = func.value if isinstance(func, ast.Attribute) else None
            return resolve_value(ctx, inner, trace, depth + 1, scope)
        if name == "abspath" and node.args:
            kind, base, detail = resolve_value(ctx, node.args[0], trace, depth + 1, scope)
            if kind in ("dir", "file") and base and not os.path.isabs(base):
                return (kind, os.path.join(ROOT, base), detail)
            return (kind, base, detail)
        if name == "cwd":
            return ("dir", os.getcwd(), "cwd()")
        if isinstance(func, ast.Name) and func.id in ctx.classes:
            return ("instance", func.id, "instance of %s" % func.id)
        if isinstance(func, ast.Name) and func.id in ctx.defs:
            helper = ctx.defs[func.id]
            if _contains_temp_helper(ctx, helper):
                trace.hop("%s() creates a temporary directory" % func.id)
                return (F1, None, "helper %s builds a tempdir" % func.id)
            for sub in ast.walk(helper):
                if isinstance(sub, ast.Return) and sub.value is not None:
                    return resolve_value(ctx, sub.value, trace, depth + 1, scope)
            trace.hop("%s() is a call this arm does not evaluate" % func.id)
            return (F8, None, "call to %s" % func.id)
        trace.hop("call %s() is not evaluated by this arm" % (name or "?"))
        return (F8, None, "call %s" % name)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        kind, base, detail = resolve_value(ctx, node.left, trace, depth + 1, scope)
        if kind in ("dir", "file") and isinstance(node.right, ast.Constant) \
                and isinstance(node.right.value, str):
            return ("dir", os.path.join(base, node.right.value), detail)
        return (kind, base, detail)
    if isinstance(node, ast.Subscript):
        inner = node.value
        if isinstance(inner, ast.Attribute) and inner.attr == "parents":
            kind, base, detail = resolve_value(ctx, inner.value, trace, depth + 1, scope)
            if kind in ("dir", "file") and isinstance(node.slice, ast.Constant):
                levels = int(node.slice.value) + (1 if kind == "file" else 0)
                for _ in range(levels):
                    base = os.path.dirname(base)
                return ("dir", base, "parents[%s] of %s" % (levels, detail))
            return (kind, None, detail)
        return (F8, None, "subscript")
    if isinstance(node, ast.Attribute):
        return resolve_chain(ctx, node, trace, depth, scope)
    if isinstance(node, ast.Name):
        if node.id == "__file__":
            return ("file", os.path.join(ROOT, ctx.relpath), "__file__ of %s" % ctx.relpath)
        binding = ctx.scope_binding(scope or node, node.id)
        which = binding["scope"]
        trace.hop("%s is %s" % (node.id, which))
        if which == "function_parameter":
            return (F3, None, "parameter of %s" % binding["function"])
        if which == "function_local":
            value = binding["value"]
            if isinstance(value, ast.Call):
                fn_name = getattr(value.func, "id", "") or getattr(value.func, "attr", "")
                if fn_name in ctx.defs and _contains_temp_helper(ctx, ctx.defs[fn_name]):
                    return (F1, None, "local %s = %s()" % (node.id, fn_name))
            kind, base, detail = resolve_value(ctx, value, trace, depth + 1, scope)
            if kind in ("dir", "file"):
                return (kind, base, "local %s -> %s" % (node.id, detail))
            if kind in (F1, F3, F4):
                return (kind, None, detail)
            return (F3, None, "local %s" % node.id)
        if which == "global_rebound_in_function":
            return (F2, None, "rebound in %s under a global statement" % binding["function"])
        if which == "module":
            return resolve_value(ctx, binding["value"], trace, depth + 1, scope)
        if which == "import":
            kind, module, attr = binding["value"]
            module_name = module if kind == "from" else node.id
            target = _module_file(module_name, ctx.relpath)
            if target is None:
                return (F4, None, "module %s absent" % module_name)
            if kind == "from" and attr:
                sub = FileCtx(target)
                return resolve_attr(sub, attr, trace, depth + 1)
            return (F8, None, "module %s used as a directory" % module_name)
        return (F8, None, "unbound %s" % node.id)
    if isinstance(node, ast.Constant):
        return (F8, None, "number")
    return (F8, None, type(node).__name__)


def resolve_object(ctx, name, scope, trace, depth=0):
    """Resolve a bare name to ('module'|'instance'|'value'|'absent', ctx, payload)."""
    if depth > 6:
        return ("unresolved", ctx, "depth")
    if name == "__file__":
        return ("file", ctx, os.path.join(ROOT, ctx.relpath))
    binding = ctx.scope_binding(scope, name)
    which = binding["scope"]
    if which == "import":
        kind, module, attr = binding["value"]
        module_name = module if module else name
        target = _module_file(module_name, ctx.relpath)
        if target is None:
            trace.hop("import %s has no module file in the tree" % module_name)
            return ("absent", ctx, module_name)
        sub = FileCtx(target)
        if kind == "from" and attr:
            return resolve_object(sub, attr, None, trace, depth + 1)
        return ("module", sub, module_name)
    if which == "module":
        node = ctx.module_assign[name]
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id in ctx.classes:
            return ("instance", ctx, node.func.id)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id in ctx.defs:
            helper = ctx.defs[node.func.id]
            if _contains_temp_helper(ctx, helper):
                return ("temp", ctx, node.func.id)
        return ("value", ctx, node)
    if which == "global_rebound_in_function":
        return ("rebound", ctx, binding["function"])
    if which == "function_local":
        value = binding["value"]
        if isinstance(value, ast.Call) and isinstance(value.func, ast.Name) \
                and value.func.id in ctx.defs and _contains_temp_helper(ctx, ctx.defs[value.func.id]):
            return ("temp", ctx, value.func.id)
        return ("local", ctx, value)
    if which == "function_parameter":
        return ("parameter", ctx, binding["function"])
    return ("unresolved", ctx, name)


def _class_field(ctx, class_name, attr, trace):
    klass = ctx.classes.get(class_name)
    if klass is None:
        return None
    for stmt in klass.body:
        targets = []
        if isinstance(stmt, ast.Assign):
            targets = [t for t in stmt.targets if isinstance(t, ast.Name)]
        elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            targets = [stmt.target]
        for target in targets:
            if target.id == attr and stmt.value is not None:
                trace.hop("%s.%s from the class body" % (class_name, attr))
                return stmt.value
    return None


def _class_value(ctx, class_name, value, trace, depth=0):
    """A dataclass field may name a sibling field; follow that one hop before evaluating."""
    if depth > 6:
        return (F8, None, "class field depth")
    if isinstance(value, ast.Call) and getattr(value.func, "attr", "") == "join" and value.args:
        first = value.args[0]
        if isinstance(first, ast.Name) and first.id != "self":
            sibling = _class_field(ctx, class_name, first.id, trace)
            if sibling is not None:
                kind, base, detail = _class_value(ctx, class_name, sibling, trace, depth + 1)
                if kind in ("dir", "file"):
                    rest = [a.value for a in value.args[1:]
                            if isinstance(a, ast.Constant) and isinstance(a.value, str)]
                    return (kind, os.path.join(base, *rest) if rest else base, detail)
                return (kind, None, detail)
    return resolve_value(ctx, value, trace, depth + 1, None)


def resolve_chain(ctx, node, trace, depth, scope):
    """Follow `a.b.c` from its root name, one hop per attribute."""
    attrs = []
    cur = node
    while isinstance(cur, ast.Attribute):
        attrs.append(cur.attr)
        cur = cur.value
    if not isinstance(cur, ast.Name):
        trace.hop("chain does not start at a name: %s" % ctx.src(node))
        return (F8, None, "chain without a name")
    attrs.reverse()
    kind, holder, payload = resolve_object(ctx, cur.id, scope, trace, depth)
    trace.hop("%s resolves to %s (%s)" % (cur.id, kind, payload if isinstance(payload, str) else ""))
    if kind == "absent":
        return (F4, None, "module %s absent" % payload)
    if kind == "temp":
        return (F1, None, "helper %s builds a tempdir" % payload)
    if kind == "rebound":
        return (F2, None, "rebound in %s under a global statement" % payload)
    if kind == "parameter":
        return (F3, None, "parameter of %s" % payload)
    if kind == "unresolved":
        return (F8, None, "unbound %s" % cur.id)
    if kind == "file":
        return ("file", payload, "__file__")
    if kind in ("value", "local"):
        sub_kind, base, detail = resolve_value(ctx, payload, trace, depth + 1, scope)
        if sub_kind == "instance":
            kind, holder, payload = "instance", ctx, base
        elif sub_kind in ("dir", "file"):
            return (sub_kind, base, detail)
        else:
            return (sub_kind, None, detail)
    # walk the attributes
    for attr in attrs:
        if kind == "module":
            sub = holder
            if attr in sub.module_assign or attr in sub.imports:
                kind, holder, payload = resolve_object(sub, attr, None, trace, depth + 1)
            else:
                trace.hop("module %s has no binding for %s" % (payload, attr))
                return (F8, None, "attribute %s unbound" % attr)
        elif kind == "instance":
            value = _class_field(holder, payload, attr, trace)
            if value is None:
                trace.hop("class %s has no field %s" % (payload, attr))
                return (F8, None, "attribute %s unbound" % attr)
            sub_kind, base, detail = _class_value(holder, payload, value, trace, depth + 1)
            if sub_kind in ("dir", "file"):
                return (sub_kind, base, detail)
            if sub_kind in (F1, F3, F4):
                return (sub_kind, None, detail)
            return (F8, None, detail)
        elif kind in ("value", "local"):
            sub_kind, base, detail = resolve_value(holder, payload, trace, depth + 1, None)
            if sub_kind in ("dir", "file"):
                return (sub_kind, base, detail)
            if sub_kind in (F1, F3, F4):
                return (sub_kind, None, detail)
            if sub_kind == "instance":
                kind, holder, payload = "instance", holder, base
            else:
                return (F8, None, detail)
        else:
            return (F8, None, "cannot take %s off %s" % (attr, kind))
    if kind in ("value", "local"):
        sub_kind, base, detail = resolve_value(holder, payload, trace, depth + 1, None)
        if sub_kind in ("dir", "file"):
            return (sub_kind, base, detail)
        if sub_kind in (F1, F3, F4):
            return (sub_kind, None, detail)
        return (F8, None, detail)
    if kind == "module":
        return (F8, None, "module %s used as a directory" % payload)
    if kind == "instance":
        return (F8, None, "instance %s used as a directory" % payload)
    return (F8, None, "chain ended at %s" % kind)


# --------------------------------------------------------------------------- population

def load_population(face_path=None):
    path = face_path or os.path.join(ROOT, POPULATION_SOURCE)
    with open(path, encoding="utf-8") as fh:
        face = json.load(fh)
    sites = []
    for row in face.get("rows", []):
        for site in row.get("sites", []):
            if site.get("class") == POPULATION_CLASS:
                sites.append({"fragment": row["fragment"], "site": site["site"],
                              "directory_expression": site.get("directory_expression") or "",
                              "fragment_write_sites": int(row.get("n_write_sites") or 0),
                              "exists_at_e402": bool(site.get("exists"))})
    return face, sites


def _git_ignored(relpath):
    try:
        proc = subprocess.run(["git", "check-ignore", "-q", relpath], cwd=ROOT,
                              capture_output=True)
        return proc.returncode == 0
    except Exception:
        return False


def _split_site(site):
    path, _, line = site.partition(":")
    return path.replace("\\", "/"), int(line or 0)


def find_scope_node(ctx, expr_text, line=0):
    """The expression node inside the file's own tree, so scope lookup can walk parents."""
    target = (expr_text or "").strip()
    if target:
        for sub in ast.walk(ctx.tree):
            if isinstance(sub, ast.expr) and (ctx.src(sub) or "").strip() == target:
                return sub
    if line:
        stmts = [sub for sub in ast.walk(ctx.tree)
                 if isinstance(sub, ast.stmt) and getattr(sub, "lineno", 0) <= line
                 and (getattr(sub, "end_lineno", 0) or 0) >= line]
        if stmts:
            return sorted(stmts, key=lambda n: (getattr(n, "end_lineno", 0)
                                                - getattr(n, "lineno", 0)))[0]
    return None


def classify(ctx, expr_text, scope_node):
    """Resolve one directory expression into (class, resolved_dir, trace, constants, detail)."""
    trace = Trace()
    try:
        expr = ast.parse(expr_text, mode="eval").body
    except SyntaxError:
        return (F8, None, ["expression does not parse"], [], "does not parse")
    kind, base, detail = resolve_value(ctx, expr, trace, 0, scope_node)
    constants = _join_constants(expr)
    return (kind, base, trace.hops, constants, detail)


def build_site_row(ctx, item):
    relpath, line = _split_site(item["site"])
    trace = Trace()
    row = {"fragment": item["fragment"], "site": item["site"], "source": relpath,
           "directory_expression": item["directory_expression"],
           "fragment_write_sites": int(item.get("fragment_write_sites") or 0), "constants": []}
    try:
        expr = ast.parse(item["directory_expression"], mode="eval").body
    except SyntaxError:
        row.update({"class": F8, "resolved_directory": None, "composed_path": None,
                    "path_exists": None, "detail": "expression does not parse", "trace": []})
        return row
    scope_node = find_scope_node(ctx, item["directory_expression"], line)
    kind, base, hops, constants, detail = classify(ctx, item["directory_expression"], scope_node)
    row["trace"] = hops
    row["constants"] = [c for c in constants]
    if kind in (F1, F2, F3, F4):
        row.update({"class": kind, "resolved_directory": None, "composed_path": None,
                    "path_exists": None, "detail": detail})
        return row
    if kind != "dir" or not base:
        row.update({"class": F8, "resolved_directory": None, "composed_path": None,
                    "path_exists": None, "detail": detail})
        return row
    base_abs = base if os.path.isabs(base) else os.path.join(ROOT, base)
    tail = [c for c in constants]
    if tail and os.path.normcase(base_abs).endswith(os.path.normcase(os.path.join(*tail))):
        tail = []
    composed = os.path.join(base_abs, *tail) if tail else base_abs
    inside = os.path.normcase(os.path.abspath(composed)).startswith(
        os.path.normcase(os.path.abspath(ROOT) + os.sep))
    exists = bool(EXISTS(composed))
    rel = os.path.relpath(composed, ROOT).replace("\\", "/")
    if not inside:
        klass = F7
    elif exists:
        klass = F5
    elif _git_ignored(rel) or _git_ignored(rel.rsplit("/", 1)[0] if "/" in rel else rel):
        klass = F7
    else:
        klass = F6
    row.update({"class": klass, "resolved_directory": base_abs, "resolved_inside_tree": inside,
                "composed_path": rel, "path_exists": exists, "detail": detail})
    return row


def decide(summary):
    by_class = summary["by_class"]
    if by_class.get(F4):
        return V_DANGLING
    if summary.get("in_tree_absent_reads"):
        return V_DEAD_JOIN
    if by_class.get(F6) and not summary.get("in_tree_absent_writes"):
        return V_DEAD_JOIN
    if by_class.get(F6):
        return V_NOT_YET_PRODUCED
    if by_class.get(F5):
        return V_LANDS
    design = sum(by_class.get(k, 0) for k in DESIGN_FREE)
    if design and design == sum(by_class.values()):
        return V_ALL_RUNTIME
    return V_PARTIAL


def build(write_face=True):
    face_in, items = load_population()
    rows = []
    cache = {}
    for item in items:
        relpath, _line = _split_site(item["site"])
        if relpath not in cache:
            if not os.path.exists(os.path.join(ROOT, relpath)):
                rows.append({"fragment": item["fragment"], "site": item["site"], "source": relpath,
                             "directory_expression": item["directory_expression"],
                             "class": F8, "detail": "source file absent", "trace": [],
                             "constants": []})
                continue
            cache[relpath] = FileCtx(relpath)
        rows.append(build_site_row(cache[relpath], item))
    by_class = {}
    for row in rows:
        by_class[row["class"]] = by_class.get(row["class"], 0) + 1
    fragments = sorted({row["fragment"] for row in rows})
    per_fragment = {}
    for frag in fragments:
        classes = sorted({row["class"] for row in rows if row["fragment"] == frag})
        per_fragment[frag] = classes
    summary = {
        "population_source": POPULATION_SOURCE,
        "population_class": POPULATION_CLASS,
        "sites": len(rows),
        "fragments": len(fragments),
        "distinct_source_files": len({row["source"] for row in rows}),
        "by_class": by_class,
        "by_fragment": per_fragment,
        "sites_still_unresolved": by_class.get(F8, 0),
        "sites_naming_a_directory_the_reader_cannot_act_on": sum(
            by_class.get(k, 0) for k in DESIGN_FREE + (F4, F7)),
        "sites_where_the_join_lands": by_class.get(F5, 0),
        "sites_where_the_directory_is_in_tree_and_the_file_is_absent": by_class.get(F6, 0),
        "in_tree_absent_writes": sum(1 for r in rows if r["class"] == F6
                                     and r.get("fragment_write_sites")),
        "in_tree_absent_reads": sum(1 for r in rows if r["class"] == F6
                                    and not r.get("fragment_write_sites")),
        "classes_sum_to_sites": sum(by_class.values()) == len(rows),
        "dead_joins": [{"fragment": r["fragment"], "site": r["site"],
                        "composed": r["composed_path"]} for r in rows if r["class"] == F6],
        "dangling_imports": sorted({r["detail"] for r in rows if r["class"] == F4}),
    }
    summary["verdict"] = decide(summary)
    face = {
        "study": STUDY,
        "evidence_cutoff": TODAY,
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "source": SELF_REL,
        "seeded_by": POPULATION_SOURCE,
        "arms": {
            "A0_population": {"kind": "%s rows whose site class == %s" % (POPULATION_SOURCE,
                                                                         POPULATION_CLASS),
                              "rows_read": len(face_in.get("rows", []))},
            "A1_name_trace": {"kind": "first name of the directory expression followed to its "
                                      "binding: function scope (parameter / local / `global` "
                                      "rebind) then module assignment then import",
                              "classes": list(CLASSES)},
            "A2_module_hop": {"kind": "attribute on an imported module resolved one hop into that "
                                      "module's file; absent module file -> F4"},
            "A3_landing_test": {"kind": "compose the literal tail onto the resolved directory and "
                                        "test existence; in-tree but absent and not git-ignored -> F6"},
        },
        "summary": summary,
        "verdict": summary["verdict"],
        "rows": rows,
        "bounds": {
            "measured": ("every %d site E402 classed %s, its directory expression followed to the "
                         "first name's binding, and whether the composed path exists"
                         % (len(rows), POPULATION_CLASS)),
            "not_measured": ("expressions whose base is only known at call time stay F8; attribute "
                             "chains deeper than module.attr.attr are not followed; the existence "
                             "test is a point-in-time read of a machine-local tree"),
            "no_rewrites": "no published face, pointer, caller or key is edited here",
        },
    }
    say("by_class: %s" % json.dumps(by_class, sort_keys=True))
    say("verdict: %s" % summary["verdict"])
    for row in rows:
        say("  %-26s %-58s %s" % (row["fragment"], row["class"], row.get("composed_path") or ""))
    if write_face:
        _write(face)
    return face


def _write(face):
    os.makedirs(PUBLISHED_DIR, exist_ok=True)
    for name in (FACE, LATEST):
        with open(os.path.join(PUBLISHED_DIR, name), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
    say("wrote %s and %s" % (FACE, LATEST))


def verify():
    """Re-derive every published row from the tree as it stands."""
    problems = []
    with open(os.path.join(PUBLISHED_DIR, FACE), encoding="utf-8") as fh:
        face = json.load(fh)
    _in, items = load_population()
    if len(items) != len(face["rows"]):
        problems.append("population moved: %d sites now, %d published"
                        % (len(items), len(face["rows"])))
    published = {(r["site"], r["fragment"]): r for r in face["rows"]}
    cache = {}
    for item in items:
        row = published.get((item["site"], item["fragment"]))
        if row is None:
            problems.append("site %s / %s is not in the face" % (item["site"], item["fragment"]))
            continue
        relpath, _line = _split_site(item["site"])
        if not os.path.exists(os.path.join(ROOT, relpath)):
            if row["class"] != F8:
                problems.append("%s: source gone but class is %s" % (item["site"], row["class"]))
            continue
        if relpath not in cache:
            cache[relpath] = FileCtx(relpath)
        now = build_site_row(cache[relpath], item)
        if now["class"] != row["class"]:
            problems.append("%s: class %s -> %s" % (item["site"], row["class"], now["class"]))
        if bool(now.get("path_exists")) != bool(row.get("path_exists")):
            problems.append("%s: existence changed" % item["site"])
        if (now.get("composed_path") or None) != (row.get("composed_path") or None):
            problems.append("%s: composed path moved" % item["site"])
    by_class = {}
    for row in face["rows"]:
        by_class[row["class"]] = by_class.get(row["class"], 0) + 1
    if by_class != face["summary"]["by_class"]:
        problems.append("by_class does not re-derive")
    if sum(by_class.values()) != face["summary"]["sites"]:
        problems.append("by_class does not sum to the published site total")
    if set(by_class) - set(CLASSES):
        problems.append("a class outside the published set is in the face")
    if not face["summary"].get("classes_sum_to_sites"):
        problems.append("classes_sum_to_sites is false in the published summary")
    if decide(face["summary"]) != face["verdict"]:
        problems.append("verdict does not re-derive")
    return problems


# --------------------------------------------------------------------------- selftest

def selftest():
    results = []

    def leg(name, ok, detail=""):
        results.append((name, bool(ok), detail))

    def row(text, expr, line_hint="p"):
        ctx = FileCtx("fixture_%d.py" % len(results), text=text)
        return build_site_row(ctx, {"fragment": "frag.json", "site": "fixture:1",
                                    "directory_expression": expr})

    temp_helper = ("import os, tempfile\n"
                   "def _mkfixture(tmp):\n"
                   "    d = tempfile.mkdtemp()\n"
                   "    return d\n"
                   "def f(tmp):\n"
                   "    fx = _mkfixture(tmp)\n"
                   "    return os.path.join(fx, 'results', 'frag.json')\n")
    leg("fixture helper -> F1", row(temp_helper, "os.path.join(fx, 'results', 'frag.json')")["class"]
        == F1, row(temp_helper, "os.path.join(fx, 'results', 'frag.json')")["class"])

    rebound = ("import os\n"
               "MACHINES_DIR = os.path.join('fleet', 'machines')\n"
               "def f():\n"
               "    global MACHINES_DIR\n"
               "    MACHINES_DIR = os.path.join('tmp', 'machines')\n"
               "    return os.path.join(MACHINES_DIR, 'bm-x.json')\n")
    leg("`global` rebind in a function -> F2",
        row(rebound, "os.path.join(MACHINES_DIR, 'bm-x.json')")["class"] == F2,
        row(rebound, "os.path.join(MACHINES_DIR, 'bm-x.json')")["class"])

    param = "import os\ndef f(d):\n    return os.path.join(d, 'train_log.jsonl')\n"
    leg("parameter -> F3", row(param, "os.path.join(d, 'train_log.jsonl')")["class"] == F3,
        row(param, "os.path.join(d, 'train_log.jsonl')")["class"])

    dangling = ("import os\nfrom no_such_module_xyz import PATHS\ndef f():\n"
                "    return os.path.join(PATHS.root, 'firm', 'x.json')\n")
    leg("import whose module has no file in the tree -> F4",
        row(dangling, "os.path.join(PATHS.root, 'firm', 'x.json')")["class"] == F4,
        row(dangling, "os.path.join(PATHS.root, 'firm', 'x.json')")["class"])
    # the installed config package is a package (relative re-export into a dataclass field): a real
    # in-tree directory must not be reported as a dangling import
    real_ctx = FileCtx("scripts/p2_deepening.py")
    real_expr = 'os.path.join(PATHS.root, "firm", "traders", "COMPOSITE-001.json")'
    real_kind = classify(real_ctx, real_expr, find_scope_node(real_ctx, real_expr, 420))[0]
    leg("the installed config package supplies PATHS.root as a real directory",
        real_kind == "dir", real_kind)

    real = ("import os\nROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\n"
            "def f():\n    return os.path.join(ROOT, 'results', 'state_tilt')\n")
    leg("os.path.dirname(os.path.abspath(__file__)) resolves to a directory, not F8",
        row(real, "os.path.join(ROOT, 'results', 'state_tilt')")["class"] not in (F8,),
        row(real, "os.path.join(ROOT, 'results', 'state_tilt')")["class"])

    global EXISTS
    real_exists = EXISTS
    try:
        EXISTS = lambda path: True
        rowland = row(temp_helper.replace("fx = _mkfixture(tmp)", "fx = 'scripts'"),
                      "os.path.join(fx, 'results', 'frag.json')")
        EXISTS = lambda path: False
    finally:
        EXISTS = real_exists
    leg("in-tree constant + existing file -> F5", rowland["class"] == F5, rowland["class"])
    leg("a landed join publishes the composed path",
        (rowland.get("composed_path") or "").endswith("scripts/results/frag.json"),
        rowland.get("composed_path"))

    missing = ("import os\nROOT = os.path.abspath(os.path.dirname(__file__))\n"
               "def f():\n    return os.path.join(ROOT, 'results', 'no_such_dir_xyz')\n")
    leg("in-tree constant + absent file -> F6 (not silently dropped)",
        row(missing, "os.path.join(ROOT, 'results', 'no_such_dir_xyz')")["class"] in (F6, F7),
        row(missing, "os.path.join(ROOT, 'results', 'no_such_dir_xyz')")["class"])

    leg("verdict: a dangling import outranks a dead join",
        decide({"by_class": {F4: 1, F6: 3}}) == V_DANGLING)
    leg("verdict: in-tree absent directories -> dead join",
        decide({"by_class": {F6: 2, F1: 4}}) == V_DEAD_JOIN)
    leg("verdict: every join lands -> lands",
        decide({"by_class": {F5: 3}}) == V_LANDS)
    leg("verdict: all runtime-supplied -> the reader was the limit",
        decide({"by_class": {F1: 5, F2: 2, F3: 3}}) == V_ALL_RUNTIME)
    leg("verdict: a mix that fits none of the above -> partial",
        decide({"by_class": {F1: 2, F7: 2}}) == V_PARTIAL)
    leg("class set is closed", set(CLASSES) == {F1, F2, F3, F4, F5, F6, F7, F8})

    ok = all(r[1] for r in results)
    for name, good, detail in results:
        say("%s %s%s" % ("PASS" if good else "FAIL", name, (" (%s)" % detail) if detail else ""))
    say("%d/%d" % (sum(1 for r in results if r[1]), len(results)))
    return 0 if ok else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        build()
        return 0
    if cmd == "verify":
        problems = verify()
        if problems:
            for problem in problems:
                say("PROBLEM %s" % problem)
            return 1
        say("verify: problems=[]")
        return 0
    if cmd == "selftest":
        return selftest()
    say("usage: run | verify | selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))