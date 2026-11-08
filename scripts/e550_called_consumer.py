"""E550 -- what the callee actually does with the constant at the sites that hand it on.

E546 (r1575) published 49 direct sites over 35 file-naming constants and classed
17 of them as ``the_site_hands_the_constant_to_a_callee_this_scan_does_not_follow``.
E549 (r1576) then read four of those rows out of their *enclosing* function and
settled them; the seventeen handed-on sites were never opened at all.

This study takes the parent's own seventeen rows (machine-read from
``filepathjoined_latest.json``, never hand-listed), folds the rows that share a
source line (the parent recorded both a call and its argument as two spellings
of one location), and for each location follows exactly one hop:

  * if the value is handed to a call, the callee is looked up first in the same
    module, then as a ``def <name>(`` in any ``scripts/*.py``;
  * if the value arrives as a default argument, the callee is the function that
    owns the default, and the parameter name is followed through its body;
  * if the value is normalised (``abspath`` and friends) and compared, there is
    no callee reading it -- the value is an identity token.

Each callee's parameter is then classed by what the body does with it: opened,
joined as the container base (the failure mode E546 was looking for, one layer
down), only tested, only compared, taken apart as a path, handed on again, or
never read.

    python scripts/e550_called_consumer.py build      # publish the face
    python scripts/e550_called_consumer.py check      # re-derive from source; problems must be []
    python scripts/e550_called_consumer.py verify     # two builds identical
    python scripts/e550_called_consumer.py selftest   # offline fixtures + defect refusals
"""
from __future__ import annotations

import ast
import io
import json
import os
import sys
import textwrap
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STATE_TILT = os.path.join(ROOT, "results", "state_tilt")
PARENT_LATEST = os.path.join(STATE_TILT, "filepathjoined_latest.json")
LATEST = os.path.join(STATE_TILT, "calledconsumer_latest.json")

STUDY = "E550"
CARD = "E550"
TITLE = "what the callee actually does with the constant at the sites that hand it on"
EVIDENCE_CUTOFF = "2026-11-08"

# The parent's own word for the sites this study consumes.
P_PASSED = "the_site_hands_the_constant_to_a_callee_this_scan_does_not_follow"

# Site classes -- one per thing that happens one hop out.
S_FILE = "one_hop_into_the_callee_the_parameter_is_opened"
S_CONTAINER = "one_hop_into_the_callee_the_parameter_is_the_container_base"
S_PROBE = "one_hop_into_the_callee_the_parameter_is_only_tested_for_existence"
S_COMPARED = "one_hop_into_the_callee_the_parameter_is_only_compared"
S_SPLIT = "one_hop_into_the_callee_the_parameter_is_only_taken_apart_as_a_path"
S_FORWARD = "one_hop_into_the_callee_the_parameter_is_handed_on_again"
S_UNREAD = "one_hop_into_the_callee_the_parameter_is_never_read"
S_MIXED = "the_callee_uses_the_parameter_in_ways_this_scan_does_not_order"
S_RENDER = "the_callee_is_a_builtin_that_only_renders_the_value"
S_IDENTITY = "the_site_compares_a_normalised_own_path_and_no_callee_reads_it"
S_UNDEFINED = "the_callee_is_not_defined_in_this_module_or_in_the_repository"
S_MIXED_SITE = "the_loads_at_this_line_do_not_agree"
SITE_VOCAB = (S_FILE, S_CONTAINER, S_PROBE, S_COMPARED, S_SPLIT, S_FORWARD,
              S_UNREAD, S_MIXED, S_RENDER, S_IDENTITY, S_UNDEFINED, S_MIXED_SITE)

# Use classes -- what the AST does with one load of the callee's parameter.
U_OPENED = "the_load_reaches_open_so_the_parameter_is_read_as_a_file"
U_CONTAINER = "the_load_is_the_first_argument_of_a_join_so_the_parameter_is_a_container"
U_CHILD = "the_load_is_a_later_argument_of_a_join_so_the_parameter_is_a_child_component"
U_PROBED = "the_load_only_asks_whether_the_path_exists"
U_COMPARED = "the_load_is_one_side_of_a_comparison"
U_SPLIT = "the_load_is_only_taken_apart_with_dirname_basename_or_splitext"
U_PASSED = "the_load_is_handed_to_another_callee_this_hop_does_not_follow"
USE_VOCAB = (U_OPENED, U_CONTAINER, U_CHILD, U_PROBED, U_COMPARED, U_SPLIT, U_PASSED)

K_BUILTIN = "a_builtin"
K_MODULE_CALLEE = "a_function_in_the_same_module"
K_REPO_CALLEE = "a_function_defined_in_another_in_repo_module"
K_DEFAULT = "the_function_that_owns_the_default_argument"
K_COMPARISON = "no_callee_because_the_value_is_normalised_and_compared"
K_NOT_FOUND = "no_definition_was_found"

V_NO_CONTAINER = "no_site_that_hands_the_constant_on_reads_it_as_a_container_one_hop_out"
V_CONTAINER = "some_sites_that_hand_the_constant_on_read_it_as_a_container_one_hop_out"
V_UNDEFINED = "some_callees_at_these_sites_are_defined_nowhere_in_the_repository"
VERDICT_VOCAB = (V_NO_CONTAINER, V_CONTAINER, V_UNDEFINED)

# Callables that only render a value into a message; they never read the path.
RENDER_BUILTINS = ("print", "str", "repr", "format")
# Frames that only normalise a path -- climbing through them lands on the real use.
PATH_FRAMES = ("abspath", "normpath", "realpath", "expanduser")
# Path operations that take a file path apart rather than read it.
SPLIT_FUNCS = ("dirname", "basename", "splitext")


# ---------------------------------------------------------------- source reads
def _read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def _rel(path):
    return os.path.relpath(path, ROOT).replace("\\", "/")


def _fname(func):
    try:
        return ast.unparse(func)
    except Exception:
        return "?"


def _short(text, n=120):
    text = " ".join(str(text).split())
    return text if len(text) <= n else text[: n - 1] + "\u2026"


def _parent_map(tree):
    parents = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node
    return parents


def _innermost_function(tree, line):
    best = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end = getattr(node, "end_lineno", node.lineno)
            if node.lineno <= line <= end:
                if best is None or node.lineno >= best.lineno:
                    best = node
    return best


def _module_functions(tree):
    return {n.name: n for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}


def _names_in(body, name):
    """Every Name load of ``name`` inside the given statement list."""
    out = []
    for node in body:
        for sub in ast.walk(node):
            if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Load) and sub.id == name:
                out.append(sub)
    return sorted(out, key=lambda n: (n.lineno, n.col_offset))


def _loads_at_line(tree, name, line):
    return sorted([n for n in ast.walk(tree)
                   if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)
                   and n.id == name and n.lineno == line],
                  key=lambda n: n.col_offset)


def _climb_frames(node, parents):
    """Climb out of path-normalising wrappers; return the outermost such node."""
    cur = node
    while True:
        par = parents.get(cur)
        if isinstance(par, ast.Call) and par.args and par.args[0] is cur and \
                _fname(par.func).split(".")[-1] in PATH_FRAMES:
            cur = par
            continue
        return cur


def _classify_use(node, parents):
    """-> (use_class, detail) for one load of a bound name."""
    cur = _climb_frames(node, parents)
    wrapped = cur is not node
    par = parents.get(cur)
    detail = {"line": node.lineno}
    if wrapped:
        detail["climbed_through"] = _short(_fname(cur.func) if isinstance(cur, ast.Call) else "?")
    if isinstance(par, ast.Compare):
        detail["the_other_side"] = _short(
            par.left if cur in par.comparators else par.comparators[0])
        detail["operator"] = " ".join(ast.unparse(o) for o in par.ops)
        detail["statement"] = _short(ast.unparse(par))
        return U_COMPARED, detail
    if isinstance(par, ast.Call):
        callee = _fname(par.func)
        base = callee.split(".")[-1]
        detail["callee"] = callee
        detail["argument_position"] = par.args.index(cur) if cur in par.args else None
        if base == "open":
            return U_OPENED, detail
        if base == "join":
            return (U_CONTAINER if par.args and par.args[0] is cur else U_CHILD), detail
        if base in ("exists", "isfile", "isdir"):
            return U_PROBED, detail
        if base in SPLIT_FUNCS:
            return U_SPLIT, detail
        return U_PASSED, detail
    detail["parent_node"] = type(par).__name__ if par is not None else "none"
    return U_PASSED, detail


def _callee_uses(fn, param, parents):
    out = []
    for node in _names_in(fn.body, param):
        cls, detail = _classify_use(node, parents)
        out.append({"use_class": cls, "detail": detail})
    out.sort(key=lambda u: (u["detail"]["line"], u["use_class"]))
    return out


def _callee_class(uses):
    """What the callee does with the parameter, with the container arm winning.

    A callee that both joins the parameter and opens it is reported as a
    container: the card is asking for the failure mode, so the defect outranks
    the benign arm rather than the other way round.
    """
    classes = {u["use_class"] for u in uses}
    if not classes:
        return S_UNREAD
    if U_CONTAINER in classes:
        return S_CONTAINER
    if U_OPENED in classes:
        return S_FILE
    if U_PASSED in classes:
        return S_FORWARD
    if classes <= {U_PROBED, U_COMPARED}:
        return S_PROBE
    if classes <= {U_COMPARED}:
        return S_COMPARED
    if classes <= {U_SPLIT, U_COMPARED, U_PROBED}:
        return S_SPLIT
    return S_MIXED


def _param_for_position(fn, pos):
    args = list(getattr(fn.args, "posonlyargs", [])) + list(fn.args.args)
    if pos is not None and 0 <= pos < len(args):
        return args[pos].arg
    return None


def _param_for_keyword(fn, kw):
    args = list(getattr(fn.args, "posonlyargs", [])) + list(fn.args.args)
    names = [a.arg for a in args] + [a.arg for a in fn.args.kwonlyargs]
    return kw if kw in names else None


def _owner_function(parents, arguments):
    cur = arguments
    while cur is not None and not isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef)):
        cur = parents.get(cur)
    return cur


def _default_param(fn, node):
    """The parameter whose default expression contains ``node``."""
    if fn is None:
        return None
    args = list(getattr(fn.args, "posonlyargs", [])) + list(fn.args.args)
    pairs = list(zip(args[len(args) - len(fn.args.defaults):], fn.args.defaults))
    pairs += [(a, d) for a, d in zip(fn.args.kwonlyargs, fn.args.kw_defaults) if d is not None]
    for arg, default in pairs:
        if any(sub is node for sub in ast.walk(default)):
            return arg.arg
    return None


# ---------------------------------------------------------------- repo lookup
_REPO_INDEX = None


def _repo_index():
    """callee name -> source path, from a `def <name>(` scan over scripts/*.py."""
    global _REPO_INDEX
    if _REPO_INDEX is not None:
        return _REPO_INDEX
    index = {}
    here = os.path.abspath(__file__)
    for name in sorted(os.listdir(HERE)):
        if not name.endswith(".py"):
            continue
        path = os.path.join(HERE, name)
        if os.path.abspath(path) == here:
            continue
        try:
            tree = ast.parse(_read(path))
        except SyntaxError:
            continue
        for fn in ast.walk(tree):
            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                index.setdefault(fn.name, _rel(path))
    _REPO_INDEX = index
    return index


# ---------------------------------------------------------------- one site
def classify_site(text, name, line, source=None):
    """Follow one hop from a single site.  Pure: text in, one site's guts out."""
    tree = ast.parse(text)
    parents = _parent_map(tree)
    loads = _loads_at_line(tree, name, line)
    site = {
        "line": line,
        "loads_at_this_line": len(loads),
        "hop": None,
        "site_class": S_MIXED_SITE,
        "what_the_callee_does": None,
    }
    if not loads:
        site["why"] = "no load of the name on this line"
        return site
    seen = []
    first_hop = None
    for node in loads:
        hop = _classify_one(text, name, node, tree, parents, source)
        if first_hop is None:
            first_hop = hop
        seen.append(hop.get("site_class"))
    site["hop"] = first_hop
    site["site_class"] = first_hop["site_class"] if len(set(seen)) == 1 else S_MIXED_SITE
    site["what_the_callee_does"] = _what_it_does(site["site_class"])
    return site


def _classify_one(text, name, node, tree, parents, source):
    hop = {"kind": None, "callee": None, "callee_source": None, "parameter": None,
           "use_classes": [], "uses": []}
    par = parents.get(node)
    # a default argument: the callee is the function the default belongs to
    if isinstance(par, ast.arguments):
        fn = _owner_function(parents, par)
        param = _default_param(fn, node)
        hop["kind"] = K_DEFAULT
        hop["callee"] = fn.name if fn is not None else None
        hop["callee_source"] = source
        hop["parameter"] = param
        if fn is not None and param is not None:
            hop["uses"] = _callee_uses(fn, param, parents)
            hop["use_classes"] = [u["use_class"] for u in hop["uses"]]
        hop["site_class"] = _callee_class(hop["uses"])
        return hop
    # handed to a call (possibly through a path-normalising frame)
    cur = _climb_frames(node, parents)
    par = parents.get(cur)
    if isinstance(par, ast.Compare):
        hop["kind"] = K_COMPARISON
        hop["site_class"] = S_IDENTITY
        hop["detail"] = {
            "climbed_through": _short(_fname(cur.func)) if cur is not node and isinstance(cur, ast.Call) else None,
            "statement": _short(ast.unparse(par)),
        }
        return hop
    pos, kw = None, None
    if isinstance(par, ast.Call):
        if cur in par.args:
            pos = par.args.index(cur)
        elif cur in par.keywords:
            kw = par.keywords[par.keywords.index(cur)].arg
    if pos is None and kw is None:
        hop["site_class"] = S_UNREAD
        hop["why"] = "the load is neither a call argument nor a default"
        return hop
    callee_expr = _fname(par.func)
    base = callee_expr.split(".")[-1]
    hop["callee"] = callee_expr
    if base in RENDER_BUILTINS:
        hop["kind"] = K_BUILTIN
        hop["use_classes"] = ["renders_only"]
        hop["site_class"] = S_RENDER
        hop["detail"] = {"statement": _short(ast.unparse(par))}
        return hop
    fn = _module_functions(tree).get(base)
    hop_parents = parents
    hop_source = source
    if fn is not None:
        hop["kind"] = K_MODULE_CALLEE
    else:
        hit = _repo_index().get(base)
        if hit is None:
            hop["kind"] = K_NOT_FOUND
            hop["site_class"] = S_UNDEFINED
            return hop
        hop_source = hit
        hop_text = _read(os.path.join(ROOT, hit))
        hop_tree = ast.parse(hop_text)
        hop_parents = _parent_map(hop_tree)
        fn = _module_functions(hop_tree).get(base)
        hop["kind"] = K_REPO_CALLEE
        if fn is None:
            hop["kind"] = K_NOT_FOUND
            hop["site_class"] = S_UNDEFINED
            return hop
    hop["callee_source"] = hop_source
    hop["parameter"] = _param_for_position(fn, pos) if kw is None else _param_for_keyword(fn, kw)
    if hop["parameter"] is None:
        hop["site_class"] = S_UNREAD
        hop["why"] = "the argument position does not map to a parameter"
        return hop
    hop["uses"] = _callee_uses(fn, hop["parameter"], hop_parents)
    hop["use_classes"] = [u["use_class"] for u in hop["uses"]]
    hop["site_class"] = _callee_class(hop["uses"])
    return hop


def _what_it_does(site_class):
    return {
        S_FILE: "a_file_read_one_hop_out",
        S_CONTAINER: "a_container_one_hop_out_the_failure_mode_this_card_was_asked_about",
        S_PROBE: "a_path_only_tested_for_existence",
        S_COMPARED: "a_value_only_compared",
        S_SPLIT: "a_path_only_taken_apart",
        S_FORWARD: "handed_on_again_and_not_read_at_this_hop",
        S_UNREAD: "built_and_never_read_one_hop_out",
        S_MIXED: "used_in_ways_this_scan_does_not_order",
        S_RENDER: "rendered_into_a_message_and_never_read_as_data",
        S_IDENTITY: "an_identity_token_never_read",
        S_UNDEFINED: "not_settled_because_the_callee_is_not_defined_here",
        S_MIXED_SITE: "not_settled_because_the_loads_disagree",
    }[site_class]


# ---------------------------------------------------------------- the face
def _parent_population():
    parent = json.load(io.open(PARENT_LATEST, encoding="utf-8"))
    hits = []
    for row in parent.get("rows") or []:
        for site in row.get("sites") or []:
            if site.get("shape") == P_PASSED:
                hits.append((row, site))
    return parent, hits


def build(write=True):
    parent, pop = _parent_population()
    grouped = {}
    for row, site in pop:
        key = (row["source"], site["line"])
        g = grouped.setdefault(key, {"row": row, "lines": [], "spellings": []})
        g["spellings"].append(site.get("spelling"))
    rows = []
    for (source, line), g in sorted(grouped.items()):
        prow = g["row"]
        site = classify_site(_read(os.path.join(ROOT, source)), prow["name"], line, source)
        row = {
            "source": source,
            "name": prow["name"],
            "line": line,
            "declaration_line": prow.get("line"),
            "the_value_the_parent_published": prow.get("value"),
            "parent_site_count": len(g["spellings"]),
            "parent_spellings": g["spellings"],
            "hop": site["hop"],
            "site_class": site["site_class"],
            "loads_at_this_line": site["loads_at_this_line"],
            "what_the_callee_does": site["what_the_callee_does"],
        }
        if site.get("why"):
            row["why"] = site["why"]
        rows.append(row)

    def units(field, value):
        return sum(1 for r in rows if r.get(field) == value)

    by_class = {c: 0 for c in SITE_VOCAB}
    for r in rows:
        by_class[r["site_class"]] += 1
    hops = [r["hop"] for r in rows if r.get("hop")]
    uses = [u for h in hops for u in h.get("uses") or []]
    uses_by_class = {c: 0 for c in USE_VOCAB}
    for u in uses:
        if u["use_class"] in uses_by_class:
            uses_by_class[u["use_class"]] += 1

    summary = {
        "parent_sites_published_as_passed_to_a_callee": len(pop),
        "distinct_locations": len(rows),
        "locations_the_parent_published_twice": sum(1 for r in rows if r["parent_site_count"] > 1),
        "loads_analysed": sum(r.get("loads_at_this_line", 0) for r in rows),
        "by_class": by_class,
        "rows_whose_callee_is_a_builtin": units("site_class", S_RENDER),
        "rows_whose_callee_is_a_repository_function": sum(
            1 for h in hops if h.get("kind") in (K_MODULE_CALLEE, K_REPO_CALLEE)),
        "rows_whose_value_is_a_default_argument": sum(
            1 for h in hops if h.get("kind") == K_DEFAULT),
        "use_classes_over_callee_parameters": uses_by_class,
        "callee_use_loads_published": len(uses),
        "rows_read_as_a_file_one_hop_out": by_class[S_FILE],
        "rows_read_as_a_container_one_hop_out": by_class[S_CONTAINER],
        "rows_the_caller_builds_and_no_callee_reads_as_data":
            by_class[S_RENDER] + by_class[S_IDENTITY] + by_class[S_UNREAD],
        "rows_not_settled": by_class[S_UNDEFINED] + by_class[S_MIXED] + by_class[S_MIXED_SITE],
        "distinct_callees": sorted({h["callee"] for h in hops if h.get("callee")}),
        "callees_followed_into_a_definition": sorted(
            {h["callee"] for h in hops if h.get("kind") in (K_MODULE_CALLEE, K_REPO_CALLEE)}),
        "reproduction_matches_the_parent":
            len(pop) == (parent.get("summary") or {}).get("sites_by_shape", {}).get(P_PASSED),
    }

    if by_class[S_CONTAINER]:
        verdict = V_CONTAINER
    elif by_class[S_UNDEFINED]:
        verdict = V_UNDEFINED
    else:
        verdict = V_NO_CONTAINER

    face = {
        "study": STUDY,
        "card": CARD,
        "title": TITLE,
        "generated": datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": parent.get("evidence_cutoff") or EVIDENCE_CUTOFF,
        "population_source": {
            "parent_face": "results/state_tilt/filepathjoined_latest.json",
            "parent_study": parent.get("study"),
            "parent_evidence_cutoff": parent.get("evidence_cutoff"),
            "parent_site_shape_consumed": P_PASSED,
            "parent_sites_published_as_passed_to_a_callee": len(pop),
            "how_the_population_was_taken":
                "the parent's own site rows with its own shape word -- machine-read, never hand-listed; "
                "rows sharing one source line are folded into one location",
        },
        "method_limits": [
            "exactly one hop: a parameter handed on again is published as forwarded, not followed",
            "the repository fallback looks for `def <name>(` in scripts/*.py only -- packages and "
            "Tools/*.py are outside this index, so a miss there is 'not found by this scan', not 'absent'",
            "the container class wins when a callee both joins and opens the parameter, so the defect "
            "cannot be hidden behind a benign arm",
            "no execution: classes are static, and 'opened' means a load reaches open(), not that the file exists",
            "a parent row pair such as scan_site(NAME) plus NAME is one location with two spellings, "
            "so the seventeen parent sites are reported beside their distinct-location count",
        ],
        "summary": summary,
        "verdict": verdict,
        "verdict_vocab": list(VERDICT_VOCAB),
        "site_vocab": list(SITE_VOCAB),
        "use_vocab": list(USE_VOCAB),
        "hop_kind_vocab": [K_BUILTIN, K_MODULE_CALLEE, K_REPO_CALLEE, K_DEFAULT,
                           K_COMPARISON, K_NOT_FOUND],
        "rows": rows,
    }
    if write:
        out = os.path.join(STATE_TILT, "CALLEDCONSUMER-%s.json" % face["evidence_cutoff"])
        text = json.dumps(face, ensure_ascii=False, indent=1)
        for path in (out, LATEST):
            io.open(path, "w", encoding="utf-8", newline="\n").write(text + "\n")
    return face


def _rederive_class(row):
    """What the row's own hop says its class must be."""
    hop = row.get("hop") or {}
    kind = hop.get("kind")
    if kind == K_BUILTIN:
        return S_RENDER
    if kind == K_COMPARISON:
        return S_IDENTITY
    if kind == K_NOT_FOUND:
        return S_UNDEFINED
    if kind in (K_MODULE_CALLEE, K_REPO_CALLEE, K_DEFAULT):
        return _callee_class(hop.get("uses") or [])
    return S_MIXED_SITE


def face_problems(face):
    """Re-derive everything the face claims, from its own rows.  -> [problem]."""
    probs = []
    rows = face.get("rows") or []
    s = face.get("summary") or {}
    if not rows:
        probs.append("the population is empty")
        return probs

    by_class = {c: 0 for c in SITE_VOCAB}
    hops = []
    uses = []
    for r in rows:
        if r.get("site_class") not in SITE_VOCAB:
            probs.append("site class outside the vocabulary: %s" % (r.get("site_class"),))
        else:
            by_class[r["site_class"]] += 1
        hop = r.get("hop") or {}
        hops.append(hop)
        for u in hop.get("uses") or []:
            if u.get("use_class") not in USE_VOCAB:
                probs.append("use class outside the vocabulary: %s" % (u.get("use_class"),))
            uses.append(u)
        laid = _rederive_class(r)
        if laid != r["site_class"]:
            probs.append("a row's class is not what its own hop says (%s:%s -- %s vs %s)"
                         % (r.get("source"), r.get("line"), r.get("site_class"), laid))
        if r.get("what_the_callee_does") != _what_it_does(laid):
            probs.append("a row's word is not what its class says (%s:%s)" % (r.get("source"), r.get("line")))
        if laid == S_CONTAINER and U_CONTAINER not in (hop.get("use_classes") or []):
            probs.append("a row is called a container with no join-as-base load (%s:%s)"
                         % (r.get("source"), r.get("line")))
        if laid == S_FILE and U_OPENED not in (hop.get("use_classes") or []):
            probs.append("a row is called an opened file with no load that reaches open() (%s:%s)"
                         % (r.get("source"), r.get("line")))
        if laid == S_RENDER and (hop.get("use_classes") or []) != ["renders_only"]:
            probs.append("a row is called a render with a hop that does more than render (%s:%s)"
                         % (r.get("source"), r.get("line")))
        if laid in (S_FILE, S_CONTAINER, S_PROBE, S_COMPARED, S_SPLIT, S_FORWARD, S_UNREAD, S_MIXED) \
                and not hop.get("parameter"):
            probs.append("a followed row publishes no parameter name (%s:%s)"
                         % (r.get("source"), r.get("line")))
        if r.get("parent_site_count", 0) < 1 or r.get("parent_site_count") != len(r.get("parent_spellings") or []):
            probs.append("a row's parent-spelling count is not its own list (%s:%s)"
                         % (r.get("source"), r.get("line")))

    if s.get("by_class") != by_class:
        probs.append("the summary's class counts are not the rows' (%s vs %s)" % (s.get("by_class"), by_class))
    expected = {
        "rows_read_as_a_file_one_hop_out": by_class[S_FILE],
        "rows_read_as_a_container_one_hop_out": by_class[S_CONTAINER],
        "rows_whose_callee_is_a_builtin": by_class[S_RENDER],
        "rows_not_settled": by_class[S_UNDEFINED] + by_class[S_MIXED] + by_class[S_MIXED_SITE],
        "rows_the_caller_builds_and_no_callee_reads_as_data":
            by_class[S_RENDER] + by_class[S_IDENTITY] + by_class[S_UNREAD],
        "rows_whose_value_is_a_default_argument": sum(
            1 for h in hops if h.get("kind") == K_DEFAULT),
        "rows_whose_callee_is_a_repository_function": sum(
            1 for h in hops if h.get("kind") in (K_MODULE_CALLEE, K_REPO_CALLEE)),
        "distinct_locations": len(rows),
        "locations_the_parent_published_twice": sum(
            1 for r in rows if r.get("parent_site_count", 0) > 1),
        "parent_sites_published_as_passed_to_a_callee": sum(
            r.get("parent_site_count", 0) for r in rows),
        "callee_use_loads_published": len(uses),
    }
    for key, val in expected.items():
        if s.get(key) != val:
            probs.append("summary %s=%r but the rows say %r" % (key, s.get(key), val))
    uses_by_class = {c: 0 for c in USE_VOCAB}
    for u in uses:
        uses_by_class[u["use_class"]] += 1
    if s.get("use_classes_over_callee_parameters") != uses_by_class:
        probs.append("the summary's callee-use counts are not the rows'")
    if s.get("reproduction_matches_the_parent") is not True:
        probs.append("the population is not published as reproducing the parent")
    if (face.get("population_source") or {}).get("parent_sites_published_as_passed_to_a_callee") \
            != sum(r.get("parent_site_count", 0) for r in rows):
        probs.append("the population source does not agree with the rows' parent-site count")

    if by_class[S_CONTAINER]:
        want = V_CONTAINER
    elif by_class[S_UNDEFINED]:
        want = V_UNDEFINED
    else:
        want = V_NO_CONTAINER
    if face.get("verdict") != want:
        probs.append("the verdict is not what the rows derive (%r vs %r)" % (face.get("verdict"), want))
    if face.get("verdict") not in VERDICT_VOCAB:
        probs.append("verdict outside the vocabulary")
    return probs


def check():
    pub = json.load(io.open(LATEST, encoding="utf-8"))
    problems = list(face_problems(pub))
    fresh = build(write=False)
    if [(r["source"], r["line"]) for r in fresh["rows"]] != \
            [(r["source"], r["line"]) for r in pub["rows"]]:
        problems.append("the published population is not the one the parent has now")
    else:
        for a, b in zip(fresh["rows"], pub["rows"]):
            if json.dumps(a, sort_keys=True) != json.dumps(b, sort_keys=True):
                problems.append("a published row is not what the source says now (%s:%s)"
                                % (a["source"], a["line"]))
    if fresh["verdict"] != pub["verdict"]:
        problems.append("the published verdict is not the one the sources derive now")
    print(json.dumps({"problems": problems, "verdict": pub.get("verdict"),
                      "rows": len(pub.get("rows") or [])}, ensure_ascii=False))
    return 1 if problems else 0


def verify():
    a, b = build(write=False), build(write=False)
    pa = {k: v for k, v in a.items() if k != "generated"}
    pb = {k: v for k, v in b.items() if k != "generated"}
    problems = [] if json.dumps(pa, sort_keys=True) == json.dumps(pb, sort_keys=True) else \
        ["two builds of the same sources differ"]
    print(json.dumps({"problems": problems}, ensure_ascii=False))
    return 1 if problems else 0


# ---------------------------------------------------------------- selftest
FIXTURES = {
    "file": textwrap.dedent('''
        def scan_site(path, dropped):
            with open(path, encoding="utf-8") as fh:
                return fh.read()
        def caller():
            return scan_site(SELF, {})
    ''').split("\n"),
    "container": textwrap.dedent('''
        import os
        def walk(base):
            return os.path.join(base, "child.csv")
        def caller():
            return walk(OUT_PATH)
    ''').split("\n"),
    "render": textwrap.dedent('''
        def caller():
            print("wrote", OUT_PATH, "(done)")
    ''').split("\n"),
    "identity": textwrap.dedent('''
        import os
        def caller(paths):
            for p in paths:
                if os.path.abspath(p) == SELF:
                    continue
    ''').split("\n"),
    "default": textwrap.dedent('''
        import os
        def load_calendar(path=CAL_PATH):
            if not os.path.exists(path):
                return []
            with open(path, encoding="utf-8") as fh:
                return [l.strip() for l in fh]
    ''').split("\n"),
    "undefined": textwrap.dedent('''
        def caller():
            return not_a_repo_function(OUT_PATH)
    ''').split("\n"),
    "unread": textwrap.dedent('''
        def take(path):
            return 1
        def caller():
            return take(OUT_PATH)
    ''').split("\n"),
}


def _line_of(lines, needle):
    for i, l in enumerate(lines, 1):
        if needle in l:
            return i
    raise AssertionError("fixture line not found: %s" % needle)


def selftest():
    fails = []
    n = 0

    def ok(name, cond, detail=""):
        nonlocal n
        n += 1
        if not cond:
            fails.append(name + ((" -- " + detail) if detail else ""))
        print(("PASS " if cond else "FAIL ") + name + ((" -- " + detail) if detail else ""))

    def run(fixture, name, needle, source="fixture.py"):
        lines = FIXTURES[fixture]
        return classify_site("\n".join(lines), name, _line_of(lines, needle), source)

    # 1 -- same-module callee that opens its parameter
    s = run("file", "SELF", "scan_site(SELF", source="fixture_file.py")
    ok("file: the callee is a function in the same module",
       (s["hop"] or {}).get("kind") == K_MODULE_CALLEE, json.dumps(s)[:200])
    ok("file: one hop in, the parameter is opened",
       s["site_class"] == S_FILE and (s["hop"] or {}).get("parameter") == "path", json.dumps(s)[:200])

    # 2 -- the failure mode: the callee joins the parameter as the container base
    s = run("container", "OUT_PATH", "walk(OUT_PATH)", source="fixture_container.py")
    ok("container: a joined parameter is classed as the container base",
       s["site_class"] == S_CONTAINER and
       U_CONTAINER in (s["hop"] or {}).get("use_classes", []), json.dumps(s)[:200])

    # 3 -- a builtin that only renders
    s = run("render", "OUT_PATH", "print(\"wrote\"", source="fixture_render.py")
    ok("render: print is a callee that only renders the value",
       s["site_class"] == S_RENDER and (s["hop"] or {}).get("kind") == K_BUILTIN)

    # 4 -- normalised and compared: no callee reads it
    s = run("identity", "SELF", "== SELF", source="fixture_identity.py")
    ok("identity: a comparison through abspath has no callee reading the value",
       s["site_class"] == S_IDENTITY and (s["hop"] or {}).get("kind") == K_COMPARISON)

    # 5 -- a default argument is one hop, not an unfollowed edge
    s = run("default", "CAL_PATH", "def load_calendar(path=CAL_PATH)",
            source="fixture_default.py")
    ok("default: the function owning the default is the callee",
       (s["hop"] or {}).get("kind") == K_DEFAULT)
    ok("default: the parameter is opened one hop out",
       s["site_class"] == S_FILE and (s["hop"] or {}).get("parameter") == "path",
       json.dumps(s)[:200])

    # 6 -- a callee that is defined nowhere
    s = run("undefined", "OUT_PATH", "not_a_repo_function(OUT_PATH)",
            source="fixture_undefined.py")
    ok("undefined: a callee the scan cannot find is published as not settled",
       s["site_class"] == S_UNDEFINED and (s["hop"] or {}).get("kind") == K_NOT_FOUND)

    # 7 -- a callee that only rebinds nothing: built and never read
    s = run("unread", "OUT_PATH", "take(OUT_PATH)", source="fixture_unread.py")
    ok("unread: a parameter never read is its own class, not 'unknown'",
       s["site_class"] == S_UNREAD, json.dumps(s)[:200])

    # 8 -- the published face
    face = build(write=False)
    rows = face["rows"]
    s = face["summary"]
    ok("face: the population is the parent's own seventeen passed sites",
       s["parent_sites_published_as_passed_to_a_callee"] == 17, str(s["parent_sites_published_as_passed_to_a_callee"]))
    ok("face: the seventeen parent sites are fewer distinct locations",
       s["distinct_locations"] < s["parent_sites_published_as_passed_to_a_callee"] and
       s["locations_the_parent_published_twice"] >= 1,
       "%s / %s" % (s["distinct_locations"], s["locations_the_parent_published_twice"]))
    ok("face: every parent row is represented",
       sum(r["parent_site_count"] for r in rows) ==
       s["parent_sites_published_as_passed_to_a_callee"])
    ok("face: nothing is left not settled",
       s["rows_not_settled"] == 0, str(s["by_class"]))
    ok("face: the container count is what the verdict uses",
       s["rows_read_as_a_container_one_hop_out"] == s["by_class"][S_CONTAINER])
    ok("face: face_problems is clean", face_problems(face) == [], str(face_problems(face))[:300])
    ok("face: the verdict follows the container count",
       face["verdict"] == (V_CONTAINER if s["rows_read_as_a_container_one_hop_out"] else V_NO_CONTAINER))
    ok("face: every followed row publishes a parameter name",
       all((r["hop"] or {}).get("parameter") for r in rows
           if r["site_class"] in (S_FILE, S_CONTAINER, S_PROBE, S_COMPARED, S_FORWARD, S_UNREAD)))

    # 9 -- doctored copies must be refused
    doc = json.loads(json.dumps(face))
    doc["verdict"] = "a_verdict_this_study_never_publishes"
    ok("defect: a hand-written verdict is refused", bool(face_problems(doc)))
    doc = json.loads(json.dumps(face))
    doc["rows"] = doc["rows"][:-1]
    ok("defect: a summary that outlives its rows is refused", bool(face_problems(doc)))
    doc = json.loads(json.dumps(face))
    for r in doc["rows"]:
        if r["site_class"] == S_RENDER:
            r["site_class"] = S_UNDEFINED
            break
    ok("defect: a flipped site class is refused", bool(face_problems(doc)))
    doc = json.loads(json.dumps(face))
    for r in doc["rows"]:
        if r["site_class"] == S_IDENTITY:
            r["site_class"] = S_CONTAINER
            break
    ok("defect: a row called a container with no join-as-base load is refused", bool(face_problems(doc)))
    doc = json.loads(json.dumps(face))
    doc["summary"]["rows_read_as_a_container_one_hop_out"] = 3
    ok("defect: a container count that is not the rows' is refused", bool(face_problems(doc)))
    doc = json.loads(json.dumps(face))
    for r in doc["rows"]:
        if r["site_class"] == S_FILE:
            r["hop"]["use_classes"] = [U_COMPARED]
            r["hop"]["uses"] = [{"use_class": U_COMPARED, "detail": {"line": 1}}]
            break
    ok("defect: an opened row whose hop only compares is refused", bool(face_problems(doc)))

    print("%d/%d legs green" % (n - len(fails), n))
    return 1 if fails else 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "build"
    if cmd == "build":
        face = build()
        s = face["summary"]
        print(json.dumps({"rows": len(face["rows"]),
                          "parent_sites": s["parent_sites_published_as_passed_to_a_callee"],
                          "file": s["rows_read_as_a_file_one_hop_out"],
                          "container": s["rows_read_as_a_container_one_hop_out"],
                          "render": s["rows_whose_callee_is_a_builtin"],
                          "verdict": face["verdict"]}, ensure_ascii=False))
        return 0
    if cmd == "check":
        return check()
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    raise SystemExit("unknown command: %s (build|check|verify|selftest)" % cmd)


if __name__ == "__main__":
    sys.exit(main())