"""E537 -- what the module constant that replaces the sentinel *names*.

E532 (results/state_tilt/onehopout_latest.json) published two arms as
``replaced_by_module_constant``: in each, the callee's body does not use the parameter it was
handed but its own ``ROOT`` instead.  That sentence reads as a rescue -- the sentinel is gone,
something concrete took its place -- and it stops exactly where a reader needs it: ``ROOT`` is a
name, and a name is not a population.

This study resolves every published constant chain to its terminal expression, evaluates that
expression with ``__file__`` bound to the module that owns it, and publishes the directory it
actually names:

  * per arm: the chain as the tree reads it (module, name, line, source text), the form of every
    link, the terminal form, the operations that turn ``__file__`` into a directory, and the
    directory itself as a repo-relative path that must exist on disk;
  * per name: every module-level constant in this tree whose value is derived from ``__file__``,
    grouped by the name they carry, with the directories each name reaches.

The question the card asks is whether "the sentinel is replaced by ROOT" is one population.  It is
answered twice: for the two arms (do two arms that look identically rescued read the same
directory?), and for the name itself (does one name reach one directory across the tree?).

    python scripts/e537_constant_terminal.py run        # build + write the face
    python scripts/e537_constant_terminal.py check      # gate the published face (fast)
    python scripts/e537_constant_terminal.py verify     # re-derive from the tree and gate
    python scripts/e537_constant_terminal.py selftest   # fixture corpus + doctored faces
"""
from __future__ import annotations

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

CARD = ("E537-WHICH-SENTINEL-REPLACED-BY-A-MODULE-CONSTANT-ONE-HOP-OUT-LANDS-ON-A-TERMINAL-THAT-"
        "IS-NOT-THE-CALLEE-S-OWN-ROOT")
STUDY = "E537_constant_terminal"
DATE_STAMP = "2026-11-08"
FACE_NAME = "constantterminal_latest.json"
DATED_PREFIX = "CONSTTERM"
PARENT_FACE = "onehopout_latest.json"
PARENT_STUDY = "E532_one_hop_out"

SELF_EXCLUDED = ("e537_", "run_e537", "_e537", "CONSTTERM", "constantterminal_")

HOP_REPLACE_CONST = "replaced_by_module_constant"

# ---------------------------------------------------------------- terminal forms
F_OS_PATH = "an_os_path_dirname_chain_over_the_module_file"
F_PATHLIB = "a_pathlib_parent_chain_over_the_module_file"
F_JOIN = "an_os_path_join_of_the_module_directory_and_a_parent_segment"
F_FILE = "the_module_file_itself_rather_than_a_directory"
F_MODULE_DIR = "the_module_directory_itself"
F_ALIAS = "an_alias_of_another_module_constant"
F_LITERAL = "a_string_literal_that_never_mentions_the_module_file"
F_UNRESOLVED = "a_terminal_the_whitelist_could_not_evaluate"
FORM_VOCAB = (F_OS_PATH, F_PATHLIB, F_JOIN, F_FILE, F_MODULE_DIR, F_ALIAS, F_LITERAL, F_UNRESOLVED)

K_DIR = "names_a_directory"
K_FILE = "names_a_file"
K_UNRESOLVED = "could_not_be_evaluated"
KIND_VOCAB = (K_DIR, K_FILE, K_UNRESOLVED)
UNRESOLVED_BUCKET = "(unresolved)"

# ---------------------------------------------------------------- verdicts
V_ARM_SPLIT = ("the_arms_rescued_by_the_same_constant_name_terminal_on_different_directories")
V_ARM_SAME_NAME_ONE = ("the_arms_terminal_on_one_directory_and_that_name_reaches_one_directory_"
                       "across_the_tree")
V_ARM_SAME_NAME_SPLIT = ("the_arms_terminal_on_one_directory_while_the_name_itself_reaches_"
                         "several_directories_in_this_tree")
V_NAME_SPLIT = ("no_arm_in_the_parent_was_rescued_by_a_module_constant_but_the_rescuing_name_"
                "still_reaches_several_directories")
V_NAME_ONE = ("no_arm_in_the_parent_was_rescued_by_a_module_constant_and_the_corpus_names_one_"
              "directory_per_name")
V_EMPTY = "there_was_no_constant_chain_to_resolve_and_no___file___derived_constant_in_the_tree"
VERDICT_VOCAB = (V_ARM_SPLIT, V_ARM_SAME_NAME_ONE, V_ARM_SAME_NAME_SPLIT, V_NAME_SPLIT, V_NAME_ONE,
                 V_EMPTY)

MAX_HOPS = 12


class _Uneval(Exception):
    def __init__(self, why, what=None):
        Exception.__init__(self, why)
        self.why = why
        self.what = what


def _now():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _is_self(name):
    return any(prefix in name for prefix in SELF_EXCLUDED)


def _rel(path, root):
    out = os.path.relpath(path, root).replace(os.sep, "/")
    return out or "."


# ------------------------------------------------------------------ evaluator
def _dirname(value):
    if not isinstance(value, str):
        raise _Uneval("dirname_of_a_value_that_is_not_a_path")
    return os.path.dirname(value)


def _resolve(value):
    if not isinstance(value, str):
        raise _Uneval("resolve_of_a_value_that_is_not_a_path")
    return os.path.normpath(os.path.abspath(value))


def ev(node, env, file_abs):
    """Evaluate a whitelist of path expressions with ``__file__`` bound to file_abs."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        if node.id == "__file__":
            return file_abs
        if node.id in env:
            return env[node.id]
        raise _Uneval("a_name_that_is_not_bound_at_module_level", node.id)
    if isinstance(node, ast.Attribute):
        if node.attr == "parent":
            return _dirname(ev(node.value, env, file_abs))
        if node.attr in ("parents",):
            return _Parents(ev(node.value, env, file_abs))
        raise _Uneval("an_attribute_the_whitelist_does_not_follow", node.attr)
    if isinstance(node, ast.Subscript):
        base = ev(node.value, env, file_abs)
        index = ev(node.slice, env, file_abs)
        if isinstance(base, _Parents):
            if not isinstance(index, int):
                raise _Uneval("a_parents_subscript_that_is_not_an_integer")
            out = base.value
            for _ in range(index + 1):
                out = _dirname(out)
            return out
    if isinstance(node, ast.BinOp):
        if isinstance(node.op, ast.Add):
            left = ev(node.left, env, file_abs)
            right = ev(node.right, env, file_abs)
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            raise _Uneval("a_concatenation_of_values_that_are_not_strings")
        raise _Uneval("a_binary_operator_the_whitelist_does_not_follow")
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Attribute):
            attr = node.func.attr
            if attr == "resolve":
                return _resolve(ev(node.func.value, env, file_abs))
            if attr == "absolute":
                return _resolve(ev(node.func.value, env, file_abs))
            if attr == "joinpath":
                return os.path.join(ev(node.func.value, env, file_abs),
                                   *[ev(a, env, file_abs) for a in node.args])
            # dotted path helpers: os.path.dirname(...), pathlib.Path(...), os.path.join(...)
            dotted = ast.unparse(node.func) if hasattr(ast, "unparse") else attr
            if attr in ("dirname", "abspath", "realpath", "normpath", "expanduser", "join",
                        "Path", "PurePath", "str"):
                return _path_helper(attr, dotted, node, env, file_abs)
            raise _Uneval("a_method_the_whitelist_does_not_follow", attr)
        if not isinstance(node.func, ast.Name):
            raise _Uneval("a_callee_that_is_neither_a_name_nor_a_method")
        return _path_helper(node.func.id.rsplit(".", 1)[-1], node.func.id, node, env, file_abs)
    raise _Uneval("an_expression_kind_the_whitelist_does_not_follow", type(node).__name__)


class _Parents(object):
    def __init__(self, value):
        self.value = value


ONE_ARG_HELPERS = ("dirname", "abspath", "realpath", "normpath", "Path", "PurePath", "str",
                   "expanduser")


def _path_helper(last, spelled, node, env, file_abs):
    """The whitelist of path helpers, shared by dotted and bare spellings."""
    args = [ev(a, env, file_abs) for a in node.args]
    if last in ONE_ARG_HELPERS:
        if len(args) != 1:
            raise _Uneval("a_path_helper_called_with_more_than_one_argument", spelled)
        arg = args[0]
        if last == "dirname":
            return _dirname(arg)
        if last in ("abspath", "realpath"):
            return _resolve(arg)
        if last == "normpath":
            if not isinstance(arg, str):
                raise _Uneval("normpath_of_a_value_that_is_not_a_path")
            return os.path.normpath(arg)
        if last == "expanduser":
            if not isinstance(arg, str):
                raise _Uneval("expanduser_of_a_value_that_is_not_a_path")
            return os.path.expanduser(arg)
        if last == "str":
            return arg if isinstance(arg, str) else str(arg)
        return arg
    if last == "join":
        if not all(isinstance(a, str) for a in args):
            raise _Uneval("a_join_of_values_that_are_not_paths")
        return os.path.join(*args)
    raise _Uneval("a_callee_the_whitelist_does_not_follow", spelled)


def form_of(node, value, module_dir):
    """Which terminal shape produced value."""
    text = ast.unparse(node) if hasattr(ast, "unparse") else ""
    lowered = text.replace("pathlib.", "")
    uses_pathlib = ("Path(" in lowered or ".parents" in lowered or ".parent" in lowered)
    mentions_file = any(isinstance(sub, ast.Name) and sub.id == "__file__"
                        for sub in ast.walk(node))
    if not mentions_file:
        return F_LITERAL if isinstance(value, str) else F_UNRESOLVED
    if isinstance(value, str) and os.path.isfile(value):
        return F_FILE
    if isinstance(value, str) and os.path.normpath(value) == os.path.normpath(module_dir):
        return F_MODULE_DIR
    if "join" in lowered and ".." in lowered:
        return F_JOIN
    if uses_pathlib:
        return F_PATHLIB
    if "dirname" in lowered:
        return F_OS_PATH
    return F_UNRESOLVED


# ------------------------------------------------------------------ chain resolution
def module_file(module, root):
    """Find scripts/<module>.py, or the single scripts/<module>_*.py when the id is abbreviated."""
    scripts = os.path.join(root, "scripts")
    exact = os.path.join(scripts, module + ".py")
    if os.path.isfile(exact):
        return exact
    hits = []
    for base, dirs, files in os.walk(scripts):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for name in files:
            stem = name[:-3] if name.endswith(".py") else None
            if stem and stem.startswith(module + "_"):
                hits.append(os.path.join(base, name))
    if len(hits) == 1:
        return hits[0]
    if len(hits) > 1:
        raise _Uneval("more_than_one_module_in_the_tree_carries_that_abbreviated_id", module)
    return None


def module_assignments(tree):
    """Module-level bindings: last stmt per name, binding counts, first stmt, all stmts.

    A name bound twice (`ROOT = dirname(__file__)` then `ROOT = dirname(ROOT)`) is not a mistake
    and not a split: the module's value is the last binding, and a reader that stops at the first
    one publishes a directory the module never uses.  All four readings are returned so the caller
    can publish both.
    """
    out, counts, first, every = {}, {}, {}, {}
    for stmt in tree.body:
        if isinstance(stmt, ast.Assign):
            targets = [t.id for t in stmt.targets if isinstance(t, ast.Name)]
        elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name) and stmt.value:
            targets = [stmt.target.id]
        else:
            continue
        for name in targets:
            counts[name] = counts.get(name, 0) + 1
            first.setdefault(name, stmt)
            out[name] = stmt
            every.setdefault(name, []).append(stmt)
    return out, counts, first, every


def module_env(tree, file_abs):
    """Bind the module-level names this whitelist can evaluate, in source order."""
    env = {}
    for name, binds in binding_values(tree, file_abs).items():
        if binds and binds[-1][1] is not None:
            env[name] = binds[-1][1]
    return env


def binding_values(tree, file_abs):
    """name -> [(line, value), ...] for every module-level binding, evaluated in order.

    A value is None when the whitelist cannot fold that binding; the binding still counts, so a
    reader can see that the name was re-bound without claiming what the rebinding produced.
    """
    seen = {}
    for stmt in tree.body:
        if isinstance(stmt, ast.Assign):
            targets, value = [t.id for t in stmt.targets if isinstance(t, ast.Name)], stmt.value
        elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name) and stmt.value:
            targets, value = [stmt.target.id], stmt.value
        else:
            continue
        env = {n: v[-1][1] for n, v in seen.items() if v and v[-1][1] is not None}
        try:
            got = ev(value, env, file_abs)
        except _Uneval:
            got = None
        for name in targets:
            seen.setdefault(name, []).append((stmt.lineno, got))
    return seen


def _next_link(node):
    """If the expression is a reference to another module constant, name it."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        return "%s.%s" % (node.value.id, node.attr)
    return None


def resolve_link(link, root):
    """One link of a published chain: 'module:NAME' or 'module.NAME'."""
    raw = link
    if ":" in link:
        module, name = link.split(":", 1)
    elif "." in link:
        module, name = link.rsplit(".", 1)
    else:
        raise _Uneval("a_chain_link_that_names_no_constant", link)
    path = module_file(module, root)
    if path is None:
        raise _Uneval("the_module_of_this_link_is_not_in_the_tree", module)
    tree = ast.parse(io.open(path, encoding="utf-8").read())
    stmt = module_assignments(tree)[0].get(name)
    if stmt is None:
        raise _Uneval("this_module_does_not_bind_that_name_at_module_level", link)
    module_dir = os.path.dirname(path)
    nxt = _next_link(stmt.value)
    file_abs = os.path.abspath(path)
    binds = (binding_values(tree, file_abs).get(name) or [])
    value = binds[-1][1] if binds else None
    err = None
    if value is None and nxt is None:
        err = _Uneval("the_last_binding_of_this_name_could_not_be_folded")
    form = form_of(stmt.value, value, module_dir)
    if err is not None:
        form = F_UNRESOLVED
    kind = K_UNRESOLVED
    directory = None
    why = None if err is None else err.why
    if nxt is not None:
        # an alias names another module constant: the next link answers this one
        form, value, err = F_ALIAS, None, None
        why = "this_link_names_another_module_constant"
    elif isinstance(value, str):
        if os.path.isdir(value):
            kind, directory = K_DIR, _rel(value, root)
        elif os.path.isfile(value):
            kind, directory = K_FILE, _rel(os.path.dirname(value), root)
    return {
        "link": link,
        "module": module,
        "name": name,
        "source": _rel(path, root),
        "line": stmt.lineno,
        "source_text": ast.unparse(stmt.value) if hasattr(ast, "unparse") else "",
        "form": form,
        "kind": kind,
        "value": value,
        "directory": directory,
        "exists": bool(isinstance(value, str) and os.path.exists(value)),
        "next": nxt,
        "why_unresolved": why,
    }


def resolve_chain(chain, root):
    links = []
    for link in chain:
        if len(links) >= MAX_HOPS:
            raise _Uneval("the_chain_is_longer_than_the_reader_follows")
        got = resolve_link(link, root)
        links.append(got)
        if got["next"] is not None and got["next"] not in chain:
            # a hop the parent face did not publish: record it rather than silently stop
            extra = resolve_link(got["next"], root)
            extra["unpublished_hop"] = True
            links.append(extra)
            break
    return links


def terminal_of(links):
    for link in reversed(links):
        if link.get("value") is not None:
            return link
    return None


# ------------------------------------------------------------------ population
def load_parent(root=None):
    root = root or ROOT
    with io.open(os.path.join(root, "results", "state_tilt", PARENT_FACE), encoding="utf-8") as fh:
        return json.load(fh)


def population(parent):
    """Forwarding rows E532 published as replaced by a module constant."""
    out = []
    for arm in parent.get("arms") or []:
        for fwd in arm.get("forwarding") or []:
            if fwd.get("hop_out_class") != HOP_REPLACE_CONST:
                continue
            out.append({"arm": arm, "forwarding": fwd})
    return out


def analyse_arm(entry, root):
    arm, fwd = entry["arm"], entry["forwarding"]
    chain = list(fwd.get("constant_chain") or [])
    row = {
        "arm_id": arm.get("arm_id"),
        "arm_origin": arm.get("arm_origin"),
        "parameter": arm.get("parameter"),
        "callee": fwd.get("callee"),
        "callee_module": fwd.get("callee_module"),
        "callee_parameter": fwd.get("callee_parameter"),
        "hop_out_line": fwd.get("hop_out_line"),
        "hop_out_source": fwd.get("hop_out_source"),
        "chain_published": chain,
        "chain": [],
        "chain_published_length": len(chain),
        "chain_read_length": None,
        "chain_agrees_with_parent": None,
        "terminal_form": None,
        "terminal_source_text": None,
        "terminal_directory": None,
        "terminal_kind": None,
        "terminal_exists": None,
        "rescue_name": chain[-1].split(":")[-1].split(".")[-1] if chain else None,
        "why_unresolved": None,
    }
    try:
        links = resolve_chain(chain, root)
    except _Uneval as exc:
        row["why_unresolved"] = exc.why
        row["chain_read_length"] = 0
        row["chain_agrees_with_parent"] = False
        row["terminal_form"] = F_UNRESOLVED
        row["terminal_kind"] = K_UNRESOLVED
        return row
    row["chain"] = links
    row["chain_read_length"] = len(links)
    row["chain_agrees_with_parent"] = (len(links) == len(chain) and
                                       all(a["link"] == b for a, b in zip(links, chain)))
    term = terminal_of(links)
    if term is None:
        row["terminal_form"] = F_UNRESOLVED
        row["terminal_kind"] = K_UNRESOLVED
        row["why_unresolved"] = "no_link_in_the_chain_could_be_evaluated"
        return row
    row["terminal_form"] = term["form"]
    row["terminal_source_text"] = term["source_text"]
    row["terminal_directory"] = term["directory"]
    row["terminal_kind"] = term["kind"]
    row["terminal_exists"] = term["exists"]
    return row


# ------------------------------------------------------------------ corpus census
def corpus_files(root=None):
    root = root or ROOT
    out = []
    for base, dirs, files in os.walk(os.path.join(root, "scripts")):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for name in files:
            if name.endswith(".py") and not _is_self(name):
                out.append(os.path.join(base, name))
    return sorted(out)


def _mentions_file(node):
    return any(isinstance(s, ast.Name) and s.id == "__file__" for s in ast.walk(node))


def carries_file(tree):
    """Module-level names whose value derives from __file__, directly or through a sibling."""
    out = set()
    for name, stmt in module_assignments(tree)[0].items():
        if _mentions_file(stmt.value):
            out.add(name)
            continue
        for sub in ast.walk(stmt.value):
            if isinstance(sub, ast.Name) and sub.id in out:
                out.add(name)
                break
    return out


def census(root=None, files=None):
    """Every module-level constant whose value is derived from __file__."""
    root = root or ROOT
    rows = []
    for path in (files if files is not None else corpus_files(root)):
        try:
            tree = ast.parse(io.open(path, encoding="utf-8").read())
        except Exception:
            continue
        module_dir = os.path.dirname(path)
        file_abs = os.path.abspath(path)
        binds = binding_values(tree, file_abs)
        last, counts, first, every = module_assignments(tree)
        for name, stmt in last.items():
            file_stmts = [s for s in every.get(name, []) if _mentions_file(s.value)]
            if not file_stmts:
                continue
            form_src = file_stmts[0]
            vals = binds.get(name) or []
            value = vals[-1][1] if vals else None
            by_line = {line: got for line, got in vals}
            form = form_of(form_src.value, value, module_dir) if value is not None else F_UNRESOLVED
            kind, directory = K_UNRESOLVED, None
            why = None
            if _next_link(form_src.value) is not None:
                form, why = F_ALIAS, "this_constant_names_another_module_constant"
            elif value is None:
                why = "the_last_binding_of_this_name_could_not_be_folded"
            elif isinstance(value, str):
                if os.path.isdir(value):
                    kind, directory = K_DIR, _rel(value, root)
                elif os.path.isfile(value):
                    kind, directory = K_FILE, _rel(os.path.dirname(value), root)
            row = {
                "source": _rel(path, root),
                "name": name,
                "line": stmt.lineno,
                "source_text": ast.unparse(stmt.value) if hasattr(ast, "unparse") else "",
                "form": form,
                "kind": kind,
                "directory": directory,
                "exists": bool(isinstance(value, str) and os.path.exists(value)),
                "bindings": counts.get(name, 1),
                "first_line": form_src.lineno,
                "first_directory": None,
                "why_unresolved": why,
            }
            if row["bindings"] > 1:
                first_value = by_line.get(form_src.lineno)
                if isinstance(first_value, str):
                    if os.path.isdir(first_value):
                        row["first_directory"] = _rel(first_value, root)
                    elif os.path.isfile(first_value):
                        row["first_directory"] = _rel(os.path.dirname(first_value), root)
            rows.append(row)
    return rows


def name_groups(rows):
    groups = {}
    for row in rows:
        got = groups.setdefault(row["name"], {"count": 0, "directories": {}, "forms": {},
                                              "kinds": {}})
        got["count"] += 1
        key = row["directory"] if row["directory"] is not None else UNRESOLVED_BUCKET
        got["directories"][key] = got["directories"].get(key, 0) + 1
        got["forms"][row["form"]] = got["forms"].get(row["form"], 0) + 1
        got["kinds"][row["kind"]] = got["kinds"].get(row["kind"], 0) + 1
    out = {}
    for name in sorted(groups):
        got = groups[name]
        out[name] = {
            "count": got["count"],
            "directories": got["directories"],
            "distinct_directories": len([d for d in got["directories"]
                                        if d != UNRESOLVED_BUCKET]),
            "forms": got["forms"],
            "kinds": got["kinds"],
        }
    return out


def outliers(rows, groups):
    """Rows belonging to a name that reaches more than one directory."""
    out = []
    for row in rows:
        meta = groups.get(row["name"]) or {}
        if (meta.get("distinct_directories") or 0) > 1:
            out.append(row)
    return out


# ------------------------------------------------------------------ summary
def _count(rows, key):
    out = {}
    for row in rows:
        out[row.get(key)] = out.get(row.get(key), 0) + 1
    return dict(sorted(out.items(), key=lambda kv: str(kv[0])))


def _summary(arms, rows, groups, files_read):
    terminal_dirs = [a.get("terminal_directory") for a in arms if a.get("terminal_directory")]
    names = sorted(groups)
    split_names = [n for n in names if groups[n]["distinct_directories"] > 1]
    rescue_names = sorted({a.get("rescue_name") for a in arms if a.get("rescue_name")})
    split_rescue_names = [n for n in rescue_names if groups.get(n, {}).get("distinct_directories", 0) > 1]
    return {
        "sources_read": files_read,
        "corpus_constants": len(rows),
        "corpus_modules": len({r["source"] for r in rows}),
        "corpus_names": len(names),
        "corpus_names_reaching_more_than_one_directory": len(split_names),
        "corpus_names_that_name_is_not_a_directory": len(
            [n for n in names if groups[n]["kinds"].get(K_FILE)]),
        "corpus_names_that_could_not_be_evaluated": len(
            [n for n in names if groups[n]["kinds"].get(K_UNRESOLVED)]),
        "corpus_constants_outside_the_home_directory": len(
            [r for r in rows if r["directory"] not in (None, ".")]),
        "arms": len(arms),
        "arms_resolved": len(terminal_dirs),
        "arms_with_a_terminal_directory": len(terminal_dirs),
        "distinct_arm_terminal_directories": len(set(terminal_dirs)),
        "arm_terminal_directories": sorted(set(terminal_dirs)),
        "arms_where_the_published_chain_is_what_the_tree_reads": len(
            [a for a in arms if a.get("chain_agrees_with_parent")]),
        "arms_by_terminal_form": _count(arms, "terminal_form"),
        "arms_by_rescue_name": _count(arms, "rescue_name"),
        "rescue_names": rescue_names,
        "rescue_names_that_reach_more_than_one_directory": split_rescue_names,
        "names_reaching_more_than_one_directory": split_names,
        "corpus_by_form": _count(rows, "form"),
        "corpus_by_kind": _count(rows, "kind"),
        "corpus_constants_bound_more_than_once": len(
            [r for r in rows if (r.get("bindings") or 1) > 1]),
        "corpus_rows_whose_first_binding_names_a_different_directory": len(
            [r for r in rows if r.get("first_directory") not in (None, r.get("directory"))]),
        "corpus_rows_whose_first_binding_names_a_different_directory_examples": [
            {"source": r["source"], "name": r["name"], "line": r["line"],
             "first_line": r["first_line"], "first_directory": r["first_directory"],
             "directory": r["directory"]}
            for r in rows if r.get("first_directory") not in (None, r.get("directory"))][:12],
    }


def _verdict(summary):
    if not summary.get("arms") and not summary.get("corpus_constants"):
        return V_EMPTY
    if summary.get("distinct_arm_terminal_directories", 0) > 1:
        return V_ARM_SPLIT
    if summary.get("arms"):
        if summary.get("rescue_names_that_reach_more_than_one_directory"):
            return V_ARM_SAME_NAME_SPLIT
        return V_ARM_SAME_NAME_ONE
    if summary.get("corpus_names_reaching_more_than_one_directory"):
        return V_NAME_SPLIT
    return V_NAME_ONE


# ------------------------------------------------------------------ face
def build(root=None, write=True, arms=None, rows=None, parent=None):
    root = root or ROOT
    if arms is None:
        parent = parent or load_parent(root)
        arms = [analyse_arm(entry, root) for entry in population(parent)]
    files = corpus_files(root)
    if rows is None:
        rows = census(root, files)
    groups = name_groups(rows)
    summary = _summary(arms, rows, groups, len(files))
    face = {
        "study": STUDY,
        "card": CARD,
        "title": ("what the module constant that replaces a sentinel in its callee's body "
                  "actually names, and whether one name is one population"),
        "generated": _now(),
        "evidence_cutoff": DATE_STAMP,
        "population_source": ("%s::population() -- every forwarding row E532 published as %r, plus "
                              "every module-level constant in scripts/ whose value is derived from "
                              "__file__" % (os.path.basename(__file__), HOP_REPLACE_CONST)),
        "parent_face": PARENT_FACE,
        "method_limits": [
            "nothing in this repository is executed: every expression is evaluated by a whitelist "
            "interpreter with __file__ bound to the owning module's own path",
            "the whitelist covers os.path.dirname/abspath/realpath/normpath/join, pathlib "
            "Path/PurePath construction with .resolve/.absolute/.parent/.parents[n]/.joinpath, "
            "str concatenation and expanduser; anything else is published as unresolved with the "
            "kind it named, never folded into a directory",
            "a directory is only published when the evaluation exists on disk; a value that names "
            "a file publishes that file's directory and is counted separately as kind=%r" % K_FILE,
            "the corpus is scripts/ only -- a constant with the same name inside a test fixture, "
            "a Tools/ script or a legacy tree is outside this reading",
            "the chain is followed to the deepest link the parent face published; a hop the "
            "parent did not publish is recorded with unpublished_hop and stops the chain rather "
            "than being guessed",
            "sources_read and the corpus counts are a snapshot of a live tree other lanes write "
            "to; every class, every directory and the verdict are re-derived by verify",
        ],
        "summary": summary,
        "verdict": _verdict(summary),
        "verdict_vocab": list(VERDICT_VOCAB),
        "form_vocab": list(FORM_VOCAB),
        "kind_vocab": list(KIND_VOCAB),
        "arms": arms,
        "rescue_names": {n: groups[n] for n in sorted({a.get("rescue_name") for a in arms
                                                      if a.get("rescue_name")}) if n in groups},
        "names": groups,
        "outliers": outliers(rows, groups),
        "rebindings": [r for r in rows if (r.get("bindings") or 1) > 1],
    }
    if write:
        write_face(face, root)
    return face


def write_face(face, root=None):
    root = root or ROOT
    outdir = os.path.join(root, "results", "state_tilt")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    text = json.dumps(face, ensure_ascii=False, indent=1) + "\n"
    for path in (os.path.join(outdir, "%s-%s.json" % (DATED_PREFIX, DATE_STAMP)),
                 os.path.join(outdir, FACE_NAME)):
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    return text


def load_face(root=None):
    root = root or ROOT
    with io.open(os.path.join(root, "results", "state_tilt", FACE_NAME), encoding="utf-8") as fh:
        return json.load(fh)


def face_problems(face, root=None):
    root = root or ROOT
    problems = []
    arms = face.get("arms") or []
    names = face.get("names") or {}
    summary = face.get("summary") or {}
    if face.get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict %r is not in its own vocabulary" % (face.get("verdict"),))
    if summary.get("arms") != len(arms):
        problems.append("summary arms %r does not equal the published arms %d"
                        % (summary.get("arms"), len(arms)))
    total = sum((n.get("count") or 0) for n in names.values())
    if summary.get("corpus_constants") != total:
        problems.append("corpus_constants %r does not equal the per-name counts %d"
                        % (summary.get("corpus_constants"), total))
    if summary.get("corpus_names") != len(names):
        problems.append("corpus_names %r does not equal the published names %d"
                        % (summary.get("corpus_names"), len(names)))
    for name, meta in names.items():
        if sum((meta.get("directories") or {}).values()) != meta.get("count"):
            problems.append("name %r: its directories do not add up to its own count" % (name,))
        if meta.get("distinct_directories") != len(
                [d for d in (meta.get("directories") or {}) if d != UNRESOLVED_BUCKET]):
            problems.append("name %r: distinct_directories does not re-derive" % (name,))
        for form in (meta.get("forms") or {}):
            if form not in FORM_VOCAB:
                problems.append("name %r: form %r is not in the vocabulary" % (name, form))
        for kind in (meta.get("kinds") or {}):
            if kind not in KIND_VOCAB:
                problems.append("name %r: kind %r is not in the vocabulary" % (name, kind))
    split = sorted(n for n in names if (names[n].get("distinct_directories") or 0) > 1)
    if summary.get("names_reaching_more_than_one_directory") != split:
        problems.append("names_reaching_more_than_one_directory does not re-derive")
    for name in split:
        if not any(o.get("name") == name for o in (face.get("outliers") or [])):
            problems.append("name %r reaches several directories but no outlier row is published"
                            % (name,))
    for row in face.get("outliers") or []:
        meta = names.get(row.get("name")) or {}
        if (meta.get("directories") or {}).get(
                row.get("directory") if row.get("directory") is not None
                else UNRESOLVED_BUCKET) is None:
            problems.append("outlier %s:%s names a directory its own name's table does not carry"
                            % (row.get("source"), row.get("line")))
        if row.get("form") not in FORM_VOCAB or row.get("kind") not in KIND_VOCAB:
            problems.append("outlier %s:%s carries a form or kind outside the vocabulary"
                            % (row.get("source"), row.get("line")))
        if (row.get("bindings") or 1) < 1 or row.get("first_line") is None:
            problems.append("outlier %s:%s carries no binding count" % (row.get("source"),
                                                                       row.get("line")))
    if summary.get("corpus_constants_bound_more_than_once") != len(face.get("rebindings") or []):
        problems.append("corpus_constants_bound_more_than_once does not re-derive from the "
                        "published rebound rows")
    first_diff = [r for r in (face.get("rebindings") or [])
                  if r.get("first_directory") not in (None, r.get("directory"))]
    if summary.get("corpus_rows_whose_first_binding_names_a_different_directory") != len(first_diff):
        problems.append("corpus_rows_whose_first_binding_names_a_different_directory does not "
                        "re-derive from the published rebound rows")
    if summary.get("corpus_rows_whose_first_binding_names_a_different_directory_examples") != [
            {"source": r["source"], "name": r["name"], "line": r["line"],
             "first_line": r["first_line"], "first_directory": r["first_directory"],
             "directory": r["directory"]} for r in first_diff][:12]:
        problems.append("the first-binding examples do not re-derive from the rebound rows")
    for row in face.get("rebindings") or []:
        if (row.get("bindings") or 1) < 2:
            problems.append("a rebound row carries fewer than two bindings")
        if row.get("first_directory") is None and row.get("form") != F_ALIAS:
            problems.append("%s:%s is rebound but publishes no first-binding directory"
                            % (row.get("source"), row.get("line")))
    rescue = sorted(summary.get("rescue_names") or [])
    split_rescue = [n for n in rescue if (names.get(n) or {}).get("distinct_directories", 0) > 1]
    if summary.get("rescue_names_that_reach_more_than_one_directory") != split_rescue:
        problems.append("rescue_names_that_reach_more_than_one_directory does not re-derive")
    for name in rescue:
        if name not in names:
            problems.append("the rescuing name %r is not in the corpus table" % (name,))
        if name not in (face.get("rescue_names") or {}):
            problems.append("the rescuing name %r has no published group" % (name,))
    for arm in arms:
        where = "%s -> %s" % (arm.get("arm_id"), arm.get("hop_out_source"))
        if arm.get("terminal_form") not in FORM_VOCAB:
            problems.append("%s: terminal form %r is not in the vocabulary"
                            % (where, arm.get("terminal_form")))
        if arm.get("terminal_kind") not in KIND_VOCAB:
            problems.append("%s: terminal kind %r is not in the vocabulary"
                            % (where, arm.get("terminal_kind")))
        links = arm.get("chain") or []
        if arm.get("chain_read_length") != len(links):
            problems.append("%s: chain_read_length does not equal its own links" % where)
        if arm.get("chain_published_length") != len(arm.get("chain_published") or []):
            problems.append("%s: chain_published_length does not equal the parent's chain" % where)
        for link in links:
            if link.get("form") not in FORM_VOCAB:
                problems.append("%s: link %r carries a form outside the vocabulary"
                                % (where, link.get("link")))
            if link.get("form") == F_UNRESOLVED and not link.get("why_unresolved"):
                problems.append("%s: link %r is unresolved with no reason"
                                % (where, link.get("link")))
            if link.get("kind") == K_DIR and not link.get("exists"):
                problems.append("%s: link %r names a directory that is not on disk"
                                % (where, link.get("link")))
        term = None
        for link in reversed(links):
            if link.get("value") is not None:
                term = link
                break
        if term is not None:
            if arm.get("terminal_directory") != term.get("directory"):
                problems.append("%s: the terminal directory is not its terminal link's directory"
                                % where)
            if arm.get("terminal_form") != term.get("form"):
                problems.append("%s: the terminal form is not its terminal link's form" % where)
            if arm.get("terminal_source_text") != term.get("source_text"):
                problems.append("%s: the terminal source text is not its terminal link's" % where)
            if arm.get("terminal_kind") == K_DIR and not os.path.isdir(
                    os.path.join(root, arm.get("terminal_directory") or "")):
                problems.append("%s: the published directory %r is not on disk"
                                % (where, arm.get("terminal_directory")))
        elif arm.get("terminal_directory") is not None:
            problems.append("%s: a directory is published for a chain with no evaluable link"
                            % where)
        if not links and not arm.get("why_unresolved"):
            problems.append("%s: an empty chain carries no reason" % where)
    arm_dirs = sorted({a.get("terminal_directory") for a in arms if a.get("terminal_directory")})
    if summary.get("arm_terminal_directories") != arm_dirs:
        problems.append("arm_terminal_directories does not re-derive")
    if summary.get("distinct_arm_terminal_directories") != len(arm_dirs):
        problems.append("distinct_arm_terminal_directories does not re-derive")
    if _verdict(summary) != face.get("verdict"):
        problems.append("the verdict does not re-derive from the summary")
    return problems


def check(face=None, root=None):
    face = face if face is not None else load_face(root)
    problems = face_problems(face, root)
    print(json.dumps({"study": STUDY, "face": FACE_NAME, "problems": problems,
                      "verdict": face.get("verdict"), "arms": len(face.get("arms") or []),
                      "names": len(face.get("names") or {})}, ensure_ascii=False, indent=1))
    return 0 if not problems else 1


def verify(root=None):
    root = root or ROOT
    live = build(root, write=False)
    published = load_face(root)
    problems = face_problems(live, root)
    if live.get("arms") != published.get("arms"):
        problems.append("the published arms do not re-derive from the tree")
    if live.get("names") != published.get("names"):
        problems.append("the published name table does not re-derive from the tree")
    if live.get("outliers") != published.get("outliers"):
        problems.append("the published outliers do not re-derive from the tree")
    if live.get("rebindings") != published.get("rebindings"):
        problems.append("the published rebound rows do not re-derive from the tree")
    if live.get("verdict") != published.get("verdict"):
        problems.append("the verdict re-derives to %r, the face publishes %r"
                        % (live.get("verdict"), published.get("verdict")))
    print(json.dumps({"study": STUDY, "problems": problems, "verdict": live.get("verdict"),
                      "arms_live": len(live.get("arms") or []),
                      "arms_published": len(published.get("arms") or []),
                      "names_live": len(live.get("names") or {}),
                      "names_published": len(published.get("names") or {})},
                     ensure_ascii=False, indent=1))
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest
FIXTURE_A = '''\
"""fixture module: os.path form, the repo-root shape."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLES = os.path.join(ROOT, "results")
'''

FIXTURE_B = '''\
"""fixture module: pathlib form, same directory as ROOT above."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALT = pathlib.Path(__file__).resolve().parent.parent
'''


def _fixture(root):
    mods = {"fx_os": FIXTURE_A, "fx_pathlib": FIXTURE_B}
    files = []
    if not os.path.isdir(os.path.join(root, "scripts")):
        os.makedirs(os.path.join(root, "scripts"))
    if not os.path.isdir(os.path.join(root, "results")):
        os.makedirs(os.path.join(root, "results"))
    for name, text in mods.items():
        path = os.path.join(root, "scripts", name + ".py")
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        files.append(path)
    # a nested module: the same two-dirname chain lands one level higher
    nested = os.path.join(root, "scripts", "nested", "fx_nested.py")
    if not os.path.isdir(os.path.dirname(nested)):
        os.makedirs(os.path.dirname(nested))
    with io.open(nested, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(FIXTURE_A.replace("fixture module", "fixture module, one level down"))
    files.append(nested)
    return files


def selftest():
    import shutil
    import tempfile
    base = tempfile.mkdtemp(prefix="e537_")
    legs = []

    def leg(name, ok, detail=""):
        legs.append({"leg": name, "ok": bool(ok), "detail": detail})

    try:
        files = _fixture(base)
        rows = census(base, files)
        groups = name_groups(rows)
        by_src = {(r["source"], r["name"]): r for r in rows}

        os_root = by_src.get(("scripts/fx_os.py", "ROOT"))
        leg("os.path form is read", os_root is not None and os_root["form"] == F_OS_PATH)
        leg("the os.path chain lands on the fixture root",
            os_root is not None and os_root["directory"] == ".", os_root and os_root["directory"])
        pl_root = by_src.get(("scripts/fx_pathlib.py", "ROOT"))
        leg("pathlib parents[1] lands on the same directory as the os.path chain",
            pl_root is not None and pl_root["directory"] == ".", pl_root and pl_root["directory"])
        pl_alt = by_src.get(("scripts/fx_pathlib.py", "ALT"))
        leg("pathlib .parent.parent lands on the same directory too",
            pl_alt is not None and pl_alt["directory"] == ".",
            pl_alt and pl_alt["directory"])
        leg("the two forms are published as different forms",
            os_root is not None and pl_root is not None and
            os_root["form"] != pl_root["form"])
        here = by_src.get(("scripts/fx_os.py", "HERE"))
        leg("a module-directory constant is published as the module directory",
            here is not None and here["directory"] == "scripts" and here["kind"] == K_DIR,
            here and here["directory"])
        tables = by_src.get(("scripts/fx_os.py", "TABLES"))
        leg("a constant that inherits the file only through a sibling is outside the population",
            tables is None)
        _tree = ast.parse(FIXTURE_A)
        _env = module_env(_tree, os.path.join(base, "scripts", "fx_os.py"))
        leg("the evaluator still folds such a constant through the module environment",
            _env.get("TABLES") is not None and
            os.path.normpath(_env["TABLES"]) == os.path.normpath(os.path.join(base, "results")),
            _env.get("TABLES"))
        nested = by_src.get(("scripts/nested/fx_nested.py", "ROOT"))
        leg("the same expression one level down names a different directory",
            nested is not None and nested["directory"] == "scripts",
            nested and nested["directory"])
        grp = groups.get("ROOT") or {}
        leg("the name table counts every row of that name",
            grp.get("count") == 3, grp.get("count"))
        leg("one name reaching two directories is published as two",
            grp.get("distinct_directories") == 2, grp.get("distinct_directories"))
        leg("a name read through two forms publishes both",
            len(grp.get("forms") or {}) == 2, grp.get("forms"))
        out = outliers(rows, groups)
        leg("every row of a split name is published as an outlier", len(out) == 5, len(out))

        # a name that DOES split: the nested module named its own directory ROOT
        nested_path = os.path.join(base, "scripts", "nested", "fx_nested.py")
        with io.open(nested_path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(FIXTURE_A.replace('ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))',
                                       'ROOT = os.path.dirname(os.path.abspath(__file__))'))
        rows2 = census(base, files)
        groups2 = name_groups(rows2)
        nested2 = [r for r in rows2
                   if r["source"] == "scripts/nested/fx_nested.py" and r["name"] == "ROOT"]
        leg("a module that names its own directory moves that name's directory",
            nested2 and nested2[0]["directory"] == "scripts/nested",
            nested2 and nested2[0]["directory"])
        leg("the split survives the deeper module",
            (groups2.get("ROOT") or {}).get("distinct_directories") == 2,
            (groups2.get("ROOT") or {}).get("distinct_directories"))
        out2 = outliers(rows2, groups2)
        leg("every row of the split name is published as an outlier",
            len(out2) == 5, len(out2))

        # the two-line idiom: ROOT = dirname(file); ROOT = dirname(ROOT)
        rebound_path = os.path.join(base, "scripts", "fx_rebound.py")
        with io.open(rebound_path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("import os\n"
                     "ROOT = os.path.dirname(os.path.abspath(__file__))\n"
                     "ROOT = os.path.dirname(ROOT)\n")
        rows3 = census(base, files + [rebound_path])
        rb = [r for r in rows3 if r["source"] == "scripts/fx_rebound.py" and r["name"] == "ROOT"]
        leg("a name rebound twice publishes the binding the module actually holds",
            rb and rb[0]["directory"] == ".", rb and rb[0]["directory"])
        leg("the same row publishes the binding a first-reader would have stopped at",
            rb and rb[0]["first_directory"] == "scripts", rb and rb[0]["first_directory"])
        leg("the rebinding is counted on the row", rb and rb[0]["bindings"] == 2,
            rb and rb[0]["bindings"])

        # chains: alias -> alias -> terminal
        chain_files = {
            "fx_c": "ROOT = %s\n" % "os.path.dirname(os.path.dirname(os.path.abspath(__file__)))",
            "fx_b": "import fx_c\nROOT = fx_c.ROOT\n",
            "fx_a": "import fx_b\nROOT = fx_b.ROOT\n",
        }
        for name, text in chain_files.items():
            path = os.path.join(base, "scripts", name + ".py")
            with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write("import os\n" + text)
        links = resolve_chain(["fx_a:ROOT", "fx_b.ROOT", "fx_c.ROOT"], base)
        leg("a chain of three links is read end to end", len(links) == 3, len(links))
        leg("the first link is published as an alias of the next",
            links[0]["form"] == F_ALIAS and links[0]["next"] == "fx_b.ROOT", links[0]["form"])
        term = terminal_of(links)
        leg("the terminal of the chain names the fixture root",
            term is not None and term["directory"] == ".", term and term["directory"])
        leg("the chain agrees with the published order",
            [l["link"] for l in links] == ["fx_a:ROOT", "fx_b.ROOT", "fx_c.ROOT"])

        bad_links = resolve_chain(["fx_a:NOT_A_NAME"], base) if False else None
        try:
            resolve_chain(["fx_a:NOT_A_NAME"], base)
            leg("a name the module does not bind is refused", False)
        except _Uneval as exc:
            leg("a name the module does not bind is refused", exc.why ==
                "this_module_does_not_bind_that_name_at_module_level", exc.why)
        try:
            resolve_chain(["fx_missing:ROOT"], base)
            leg("a module that is not in the tree is refused", False)
        except _Uneval as exc:
            leg("a module that is not in the tree is refused",
                exc.why == "the_module_of_this_link_is_not_in_the_tree", exc.why)

        unresolvable = os.path.join(base, "scripts", "fx_odd.py")
        with io.open(unresolvable, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("import os\nOUT = os.path.dirname(sorted([__file__])[0])\n")
        odd = [r for r in census(base, [unresolvable]) if r["name"] == "OUT"]
        leg("a computation outside the whitelist is unresolved, not folded",
            odd and odd[0]["form"] == F_UNRESOLVED and odd[0]["directory"] is None,
            odd and odd[0]["why_unresolved"])

        # a hand-built face, so the gates are exercised without the repo
        parent = {"arms": [{"arm_id": "fx_a::run(p)", "arm_origin": "fixture",
                            "parameter": "p", "forwarding": [
                                {"callee": "build", "callee_module": "fx_c",
                                 "callee_parameter": "p", "hop_out_class": HOP_REPLACE_CONST,
                                 "hop_out_line": 1, "hop_out_source": "ROOT",
                                 "constant_chain": ["fx_a:ROOT", "fx_b.ROOT", "fx_c.ROOT"]}]}]}
        face = build(base, write=False, parent=parent, rows=rows3, arms=None)
        leg("the fixture face gates clean", not face_problems(face, base),
            face_problems(face, base)[:2])
        leg("the fixture publishes the rebound row in its own block",
            len(face.get("rebindings") or []) == 1 and
            face["summary"]["corpus_rows_whose_first_binding_names_a_different_directory"] == 1,
            face["summary"]["corpus_rows_whose_first_binding_names_a_different_directory"])
        doc = json.loads(json.dumps(face))
        doc["rebindings"] = []
        leg("an erased rebinding block is refused", bool(face_problems(doc, base)))
        doc = json.loads(json.dumps(face))
        doc["rebindings"][0]["first_directory"] = "."
        leg("a first binding reported as the final one is refused", bool(face_problems(doc, base)))
        leg("the fixture verdict is the name-split arm",
            face["verdict"] == V_ARM_SAME_NAME_SPLIT, face["verdict"])
        leg("the fixture arm's directory is the fixture root",
            face["arms"][0]["terminal_directory"] == ".", face["arms"][0]["terminal_directory"])

        doc = json.loads(json.dumps(face))
        doc["verdict"] = "a_verdict_this_study_never_publishes"
        leg("a hand-written verdict is refused", bool(face_problems(doc, base)))
        doc = json.loads(json.dumps(face))
        doc["summary"]["corpus_constants"] += 7
        leg("an inflated constant count is refused", bool(face_problems(doc, base)))
        doc = json.loads(json.dumps(face))
        doc["names"]["ROOT"]["distinct_directories"] = 1
        leg("a name flattened to one directory is refused", bool(face_problems(doc, base)))
        doc = json.loads(json.dumps(face))
        doc["arms"][0]["terminal_directory"] = "scripts"
        leg("a terminal directory that disagrees with its own chain is refused",
            bool(face_problems(doc, base)))
        doc = json.loads(json.dumps(face))
        doc["arms"][0]["chain_read_length"] += 2
        leg("a chain length that disagrees with its own links is refused",
            bool(face_problems(doc, base)))
        doc = json.loads(json.dumps(face))
        for link in doc["arms"][0]["chain"]:
            link["form"] = F_UNRESOLVED
            link["value"] = None
            link["directory"] = None
            link["kind"] = K_UNRESOLVED
            link["why_unresolved"] = None
            link["exists"] = False
        doc["arms"][0]["terminal_directory"] = "."
        leg("an unresolved link with no reason is refused", bool(face_problems(doc, base)))
        doc = json.loads(json.dumps(face))
        doc["summary"]["names_reaching_more_than_one_directory"] = []
        leg("an emptied split list is refused", bool(face_problems(doc, base)))
        doc = json.loads(json.dumps(face))
        doc["outliers"] = []
        leg("a split name with no outlier row is refused", bool(face_problems(doc, base)))
        doc = json.loads(json.dumps(face))
        doc["summary"]["rescue_names_that_reach_more_than_one_directory"] = []
        leg("a rescuing name's split erased from the summary is refused",
            bool(face_problems(doc, base)))
        doc = json.loads(json.dumps(face))
        _dirs = doc["names"]["ROOT"]["directories"]
        _dirs[sorted(_dirs)[0]] = _dirs[sorted(_dirs)[0]] + 4
        leg("a name whose directories do not add up to its count is refused",
            bool(face_problems(doc, base)))
    finally:
        shutil.rmtree(base, ignore_errors=True)

    failed = [l for l in legs if not l["ok"]]
    print(json.dumps({"study": STUDY, "legs": len(legs), "passed": len(legs) - len(failed),
                      "failed": failed}, ensure_ascii=False, indent=1))
    return 0 if not failed else 1


# ------------------------------------------------------------------ cli
def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    if cmd == "run":
        face = build()
        print(json.dumps({"study": STUDY, "face": FACE_NAME, "verdict": face["verdict"],
                          "summary": face["summary"]}, ensure_ascii=False, indent=1))
        return 0
    if cmd == "check":
        return check()
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    print("usage: python scripts/e537_constant_terminal.py [run|check|verify|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main())