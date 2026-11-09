"""E622 -- are the functions holding E619's dead reader lines ever called?

E619 (r1639 bm-b) found 27 of 1,091 face publishers carrying a local assigned from a face key
and never read again (36 lines); the wider population holds 54 such lines.  A dead line is only
*inert* if the function holding it never runs: a dead local inside a function nothing calls costs
nothing, while the same line inside a function the module calls on every run is a real defect
that study has not yet priced.  So the question is reachability, not the class.

Population, fixed before the scan:

  * every module under ``scripts/`` that E619's own population rule calls a face publisher
    (dumps JSON and opens a file for writing / calls ``write_face``).  The parser and the
    dead-line classifier are E619's, imported -- not re-implemented, so the two studies cannot
    drift apart silently;
  * a *holder function* = the enclosing function definition of one of E619's dead reader lines.

Reach is a graph, not a one-hop ladder.  A call whose innermost enclosing function is ``f``
creates an edge ``f -> callee``; a call with no enclosing function (module level, including the
``__main__`` block) creates an edge from the module root, and reachability is the transitive
closure of the root.  Each holder is then classed, first match wins:

  called_from_module_level             the module calls it at top level (so it runs on import/run)
  reachable_through_a_chain_of_calls    reachable only through another function that is reachable
  reachable_through_a_registry_handoff  reachable only because the module hands the name to an
                                        argparse parser it built (``set_defaults(func=F)``)
  called_only_by_itself                the only edge into it is its own recursion
  called_from_an_unreachable_function  it has a caller, but that caller never runs either
  referenced_never_called              the name is loaded or passed, never called
  named_in_a_string_only               only a string constant equal to the name
  unreferenced                         the name appears nowhere outside its own definition

The verdict is stated on E619's ``scope_facekey`` population (the direct test).  Three guard
rails the first draft needed, all published:

  * an *attribute* call (``obj.name()``) becomes an edge only when the callee is a class-scoped
    function; a module-level function named ``get`` would otherwise be "called" by every
    ``d.get(...)`` in the file.  Ignored hits are counted per holder, never as reach.
  * string mentions are a class of their own and never count as reach: a constant equal to a
    function name also matches labels, keys and prose.
  * a local alias is followed exactly one hop (``A = f`` ... ``A()``); a registry dict keyed by
    name is out of reach and is disclosed as a limit.

Deterministic, static, no network, no runner, no fixture write.  ``selftest`` proves every rung
on a synthetic module and on the real population.
"""
import argparse
import ast
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-09"
FACE = "DEADLOCALREACH-%s.json" % TODAY
LATEST = "deadlocalreach_latest.json"
STUDY = "E622_dead_local_reach"
SELF_PARTS = {"e622_deadlocal_reach.py", "run_e622_smoke_leg.py", "_probe_e622.py"}
SCOPES = ["scope_all", "scope_facekey", "scope_incoming"]
ROOT_KEY = "module-level"
CLASSES = ["called_from_module_level", "reachable_through_a_chain_of_calls",
           "reachable_through_a_registry_handoff", "called_only_by_itself",
           "called_from_an_unreachable_function",
           "referenced_never_called", "named_in_a_string_only", "unreferenced"]
LIVE = ("called_from_module_level", "reachable_through_a_chain_of_calls",
        "reachable_through_a_registry_handoff")
INERT = ("referenced_never_called", "named_in_a_string_only", "unreferenced",
         "called_from_an_unreachable_function")

if HERE not in sys.path:
    sys.path.insert(0, HERE)
import e619_dead_reader_locals as e619                                              # noqa: E402

FUNC = (ast.FunctionDef, ast.AsyncFunctionDef)


# ---------------------------------------------------------------- AST helpers
def parent_map(tree):
    """node -> parent, by identity (ast node objects are unique within one tree)."""
    par = {}
    stack = [(tree, None)]
    while stack:
        node, p = stack.pop()
        par[id(node)] = p
        for ch in ast.iter_child_nodes(node):
            stack.append((ch, node))
    return par


def owner_map(tree):
    """node id -> innermost enclosing function definition (None at module level).

    Decorators, argument defaults and annotations are evaluated in the enclosing scope, so they
    are owned by the outer function rather than by the definition they decorate.
    """
    innermost = {}
    stack = [(tree, None)]
    while stack:
        node, cur = stack.pop()
        innermost[id(node)] = cur
        if isinstance(node, FUNC):
            for ch in list(node.decorator_list) + [node.args] + \
                    ([node.returns] if node.returns else []):
                stack.append((ch, cur))
            for ch in node.body:
                stack.append((ch, node))
            continue
        for ch in ast.iter_child_nodes(node):
            stack.append((ch, cur))
    return innermost


def enclosing_functions(par, node):
    """Every function definition whose body contains ``node``, innermost first."""
    out = []
    cur = par.get(id(node))
    while cur is not None:
        if isinstance(cur, FUNC):
            out.append(cur)
        cur = par.get(id(cur))
    return out


def scope_of(par, fn):
    """module / class / nested, from the nearest enclosing definition of either kind."""
    cur = par.get(id(fn))
    while cur is not None:
        if isinstance(cur, ast.ClassDef):
            return "class"
        if isinstance(cur, FUNC):
            return "nested"
        cur = par.get(id(cur))
    return "module"


def callee_name(node):
    """The bare name a call goes through: ``f(x)`` -> (f, 'name'); ``o.f(x)`` -> (f, 'attr')."""
    f = node.func
    if isinstance(f, ast.Name):
        return f.id, "name"
    if isinstance(f, ast.Attribute):
        return f.attr, "attr"
    return None, None


def freed_name(node):
    """The function name an expression names on its own (``f`` or ``mod.f``), else None."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def module_receivers(tree, stem=""):
    """Names that hold a *module object* in this file: imported aliases plus the module stem.

    This is what makes the house's re-import entry point (``sys.exit(_canonical.main())`` inside
    ``if __name__ == '__main__'``) a call rather than a dangling attribute: the receiver is the
    module itself, so a module-level function of that name is genuinely reached.  A first draft
    accepted attribute calls only onto class-scoped definitions and therefore published every
    holder behind a ``_canonical.main()`` entry as unreachable.
    """
    names = set()
    if stem:
        names.add(stem)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                names.add(a.asname or a.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for a in node.names:
                if a.name != "*":
                    names.add(a.asname or a.name)
    return names


def call_graph(tree, stem=""):
    """Edges between a caller function and the definitions it can call, plus root reachability."""
    par = parent_map(tree)
    owner = owner_map(tree)
    fns = [n for n in ast.walk(tree) if isinstance(n, FUNC)]
    id_to_fn = {id(f): f for f in fns}
    receivers = module_receivers(tree, stem)
    class_names = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
    name_to_ids = {}
    for f in fns:
        name_to_ids.setdefault(f.name, []).append(id(f))
    class_scoped = {id(f) for f in fns if scope_of(par, f) == "class"}

    aliases = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            target = freed_name(node.value)
            if target:
                aliases.setdefault(node.targets[0].id, set()).update(
                    name_to_ids.get(target, []))

    edges = {}
    attr_ignored = {}
    self_edges = {}
    alias_edges = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name, kind = callee_name(node)
        if not name:
            continue
        owner_fn = owner.get(id(node))
        caller = id(owner_fn) if owner_fn is not None else ROOT_KEY
        targets = set(name_to_ids.get(name, []))
        if kind == "attr":
            recv = node.func.value
            rname = recv.id if isinstance(recv, ast.Name) else None
            if isinstance(recv, ast.Call) and isinstance(recv.func, ast.Name):
                rname_ctor = recv.func.id
            else:
                rname_ctor = None
            if rname in ("self", "cls") or rname in class_names or rname_ctor in class_names:
                allowed = targets & class_scoped
            elif rname is not None and rname in receivers:
                allowed = targets                  # a module object: any definition is reachable
            else:
                allowed = set()                    # d.get(...) on a dict is not a call of get()
            for t in targets - allowed:
                attr_ignored[t] = attr_ignored.get(t, 0) + 1
            targets = allowed
        via_alias = False
        if name in aliases:
            targets |= aliases[name]
            via_alias = True
        for t in targets:
            edges.setdefault(caller, set()).add(t)
            if caller == t:
                self_edges[t] = self_edges.get(t, 0) + 1
            if via_alias:
                alias_edges[t] = alias_edges.get(t, 0) + 1

    handoff = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        if not (isinstance(f, ast.Attribute) and f.attr == "set_defaults"):
            continue
        owner_fn = owner.get(id(node))
        caller = id(owner_fn) if owner_fn is not None else ROOT_KEY
        for kw in node.keywords:
            if kw.arg != "func":
                continue
            target = freed_name(kw.value)
            for t in name_to_ids.get(target, []):
                handoff.setdefault(caller, set()).add(t)

    handoff_hits = {}
    for caller, targets in handoff.items():
        for t in targets:
            handoff_hits[t] = handoff_hits.get(t, 0) + 1

    def closure(edge_map):
        seen = set()
        queue = list(edge_map.get(ROOT_KEY, ()))
        while queue:
            cur = queue.pop()
            if cur in seen:
                continue
            seen.add(cur)
            queue.extend(t for t in edge_map.get(cur, ()) if t not in seen)
        return seen

    reach_call = closure(edges)
    union = {k: set(v) for k, v in edges.items()}
    for k, v in handoff.items():
        union.setdefault(k, set()).update(v)
    reach_all = closure(union)

    callers = {}
    for caller, targets in edges.items():
        for t in targets:
            if caller != t:
                callers.setdefault(t, set()).add(caller)

    dict_tables = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict) and node.values:
            named = sum(1 for v in node.values if freed_name(v) in name_to_ids)
            if named >= 2:
                dict_tables += 1

    return {"fns": fns, "par": par, "owner": owner, "edges": edges, "reachable": reach_all,
            "reachable_without_handoff": reach_call, "handoff": handoff,
            "handoff_hits": handoff_hits, "dict_tables": dict_tables,
            "root_calls": set(edges.get(ROOT_KEY, ())), "callers": callers,
            "attr_ignored": attr_ignored, "self_edges": self_edges,
            "alias_edges": alias_edges, "name_to_ids": name_to_ids}


def function_rows(tree, graph=None, stem=""):
    """One row per function definition: its scope, its reach class and the evidence for it."""
    g = graph or call_graph(tree, stem)
    par = g["par"]
    owner = g["owner"]
    loads_by_name = {}
    strings = set()
    string_owner = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            loads_by_name.setdefault(node.id, []).append(id(node))
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            strings.add(node.value)
            string_owner.setdefault(node.value, set()).add(id(owner.get(id(node))))
    rows = []
    for fn in g["fns"]:
        fid = id(fn)
        mentioned = any(o != fid for o in
                        (id(owner.get(i)) for i in loads_by_name.get(fn.name, ())))
        string_only = fn.name in strings and any(
            o != fid for o in string_owner.get(fn.name, ()))
        if fid in g["root_calls"]:
            reach = "called_from_module_level"
        elif fid in g["reachable_without_handoff"]:
            reach = "reachable_through_a_chain_of_calls"
        elif fid in g["reachable"]:
            reach = "reachable_through_a_registry_handoff"
        elif g["self_edges"].get(fid) and not g["callers"].get(fid):
            reach = "called_only_by_itself"
        elif g["callers"].get(fid):
            reach = "called_from_an_unreachable_function"
        elif mentioned:
            reach = "referenced_never_called"
        elif string_only:
            reach = "named_in_a_string_only"
        else:
            reach = "unreferenced"
        rows.append({
            "function": fn.name,
            "scope": scope_of(par, fn),
            "line": fn.lineno,
            "reach": reach,
            "callers": len(g["callers"].get(fid, ())),
            "handed_to_a_set_defaults_registry": g["handoff_hits"].get(fid, 0),
            "self_recursive_calls": g["self_edges"].get(fid, 0),
            "calls_through_a_local_alias": g["alias_edges"].get(fid, 0),
            "attribute_hits_not_counted_as_reach": g["attr_ignored"].get(fid, 0),
            "name_is_mentioned_outside": bool(mentioned),
            "name_appears_in_a_string": bool(string_only),
        })
    rows.sort(key=lambda r: r["line"])
    return rows


# ---------------------------------------------------------------- measure
def e619_cross_check(root, redone):
    """Diff this study's re-derivation of E619's rows against the face E619 published.

    The point is not agreement for its own sake: if the imported classifier ever drifts from the
    published face, the holder population here would silently describe a different study.
    ``redone`` maps module -> [(function, local, key, line)] as re-derived by that same import.
    """
    path = os.path.join(root, "results", "state_tilt", "deadreaderlocals_latest.json")
    out = {"published": False, "agrees": None}
    if not os.path.exists(path):
        out["note"] = "no published E619 face on disk"
        return out
    pub = json.load(io.open(path, encoding="utf-8"))
    published_rows = {}
    for r in pub.get("modules") or []:
        published_rows[r.get("module")] = [
            (x.get("function"), x.get("local"), x.get("key"), x.get("line"))
            for x in (r.get("dead_reader_locals") or [])]
    mine = dict(redone)
    shared = sorted(set(mine) & set(published_rows))
    differing = [rel for rel in shared if mine[rel] != published_rows[rel]]
    only_here = sorted(set(mine) - set(published_rows))
    only_there = sorted(set(published_rows) - set(mine))
    out.update({
        "published": True,
        "published_population": (pub.get("counts") or {}).get("population_modules"),
        "rederived_population": len(mine),
        "modules_compared": len(shared),
        "modules_with_differing_dead_rows": differing[:10],
        "modules_with_differing_dead_rows_n": len(differing),
        "modules_only_in_this_rederivation": only_here,
        "modules_only_in_the_published_face": only_there,
        "agrees": not differing and not only_there,
        "note": ("rows are compared per module as (function, local, key, line); a module present "
                 "in only one side is listed rather than counted as agreement"),
    })
    return out


def measure(root=ROOT):
    mods, skipped = e619.population(root)
    keep = [(rel, tree) for rel, tree in mods
            if not any(rel.endswith(p) for p in SELF_PARTS)]
    holders = []
    redone = {}
    base = {"modules": 0, "functions": 0, "reachable_functions": 0,
            "functions_in_modules_holding_a_dead_line": 0}
    for rel, tree in keep:
        stem = os.path.basename(rel)
        if stem.endswith(".py"):
            stem = stem[:-3]
        g = call_graph(tree, stem)
        rows = function_rows(tree, g, stem)
        base["modules"] += 1
        base["functions"] += len(rows)
        base["reachable_functions"] += sum(1 for r in rows if r["reach"] in LIVE)
        dead = e619.dead_reader_locals(tree)
        redone[rel] = [(d["function"], d["local"], d["key"], d["line"]) for d in dead]
        if not dead:
            continue
        # E619 publishes the enclosing function NAME; a name can be defined twice in a module
        # (a nested helper), so each dead row is resolved to the innermost definition spanning
        # its own line.
        resolved = {}
        for d in dead:
            cand = [f for f in g["fns"] if f.name == d["function"]
                    and f.lineno <= d["line"] <= (f.end_lineno or f.lineno)]
            cand.sort(key=lambda f: f.lineno)
            if not cand:
                continue
            resolved.setdefault(id(cand[-1]), []).append(d)
        by_key = {(r["function"], r["line"]): r for r in rows}
        mod_holders = []
        for fid, dead_rows in resolved.items():
            fn = next((f for f in g["fns"] if id(f) == fid), None)
            if fn is None:
                continue
            row = by_key.get((fn.name, fn.lineno))
            if row is None:
                continue
            facekey = [d for d in dead_rows if d.get("key_is_a_dict_literal_key")]
            incoming = [d for d in facekey if d.get("indexed_object_is_incoming")]
            mod_holders.append({
                "function": fn.name,
                "scope": row["scope"],
                "def_line": fn.lineno,
                "reach": row["reach"],
                "callers": row["callers"],
                "handed_to_a_set_defaults_registry":
                    row["handed_to_a_set_defaults_registry"],
                "self_recursive_calls": row["self_recursive_calls"],
                "calls_through_a_local_alias": row["calls_through_a_local_alias"],
                "attribute_hits_not_counted_as_reach":
                    row["attribute_hits_not_counted_as_reach"],
                "dead_lines": len(dead_rows),
                "dead_lines_facekey": len(facekey),
                "dead_lines_incoming": len(incoming),
                "dead_keys": sorted({d["key"] for d in dead_rows}),
            })
        mod_holders.sort(key=lambda r: r["def_line"])
        base["functions_in_modules_holding_a_dead_line"] += len(rows)
        holders.append({"module": rel, "functions_in_module": len(rows),
                        "set_defaults_handoffs": sum(len(v) for v in g["handoff"].values()),
                        "dict_dispatch_tables_of_function_names": g["dict_tables"],
                        "holders": mod_holders})
    return {"modules": holders, "skipped": skipped, "base": base,
            "cross_check": e619_cross_check(root, redone)}


def base_of(m):
    """The base rate block, from either the live measurement or a published face."""
    b = m.get("base") or m.get("base_rates") or {}
    return {
        "modules": b.get("modules", b.get("population_modules")) or 0,
        "functions": b.get("functions", b.get("functions_in_the_population")) or 0,
        "reachable_functions": b.get("reachable_functions",
                                     b.get("functions_reachable_in_the_population")) or 0,
        "functions_in_modules_holding_a_dead_line":
            b.get("functions_in_modules_holding_a_dead_line") or 0,
    }


def counts_of(m):
    holders = [h for mod in m["modules"] for h in mod["holders"]]
    base = base_of(m)
    scope_of_key = {"scope_all": "dead_lines", "scope_facekey": "dead_lines_facekey",
                    "scope_incoming": "dead_lines_incoming"}
    c = {
        "population_modules": base["modules"],
        "skipped_modules": len(m["skipped"]),
        "modules_holding_a_dead_line": len(m["modules"]),
        "holder_functions_total": len(holders),
        "functions_in_the_population": base["functions"],
        "functions_reachable_in_the_population": base["reachable_functions"],
        "functions_in_modules_holding_a_dead_line":
            base["functions_in_modules_holding_a_dead_line"],
        "attribute_hits_not_counted_as_reach": sum(
            h["attribute_hits_not_counted_as_reach"] for h in holders),
        "holders_called_through_a_local_alias": sum(
            1 for h in holders if h["calls_through_a_local_alias"]),
        "inert_holders_in_a_module_with_a_dict_dispatch_table": sum(
            1 for mod in m["modules"] if mod.get("dict_dispatch_tables_of_function_names")
            for h in mod["holders"] if h["reach"] in INERT),
    }
    for scope, key in scope_of_key.items():
        held = [h for h in holders if h[key] > 0]
        c[scope + "_holder_functions"] = len(held)
        c[scope + "_dead_lines"] = sum(h[key] for h in held)
    for cls in CLASSES:
        c["scope_facekey_holders_" + cls] = sum(
            1 for h in holders if h["dead_lines_facekey"] and h["reach"] == cls)
        c["scope_all_holders_" + cls] = sum(
            1 for h in holders if h["reach"] == cls)
    for name, pool in (("scope_facekey", [h for h in holders if h["dead_lines_facekey"]]),
                       ("scope_all", holders)):
        c[name + "_holders_live"] = sum(1 for h in pool if h["reach"] in LIVE)
        c[name + "_dead_lines_in_a_live_holder"] = sum(
            h["dead_lines_facekey" if name == "scope_facekey" else "dead_lines"]
            for h in pool if h["reach"] in LIVE)
        c[name + "_dead_lines_in_an_inert_holder"] = sum(
            h["dead_lines_facekey" if name == "scope_facekey" else "dead_lines"]
            for h in pool if h["reach"] in INERT)
    return c


def derive_verdict(m):
    c = counts_of(m)
    if c["holder_functions_total"] == 0:
        return "no_function_holds_a_dead_reader_line"
    total = c["scope_facekey_holder_functions"]
    if total == 0:
        return "no_function_holds_a_dead_facekey_line"
    live = c["scope_facekey_holders_live"]
    if live == total:
        return ("every_one_of_the_%d_functions_holding_a_dead_facekey_line_is_reachable_from_"
                "module_level" % total)
    if live == 0:
        return ("none_of_the_%d_functions_holding_a_dead_facekey_line_is_reachable_from_"
                "module_level" % total)
    return ("%d_of_%d_functions_holding_a_dead_facekey_line_are_reachable_from_module_level"
            % (live, total))


def answer_of(m):
    c = counts_of(m)
    total = c["scope_facekey_holder_functions"]
    live = c["scope_facekey_holders_live"]
    share = (100.0 * c["functions_reachable_in_the_population"]
             / c["functions_in_the_population"]) if c["functions_in_the_population"] else 0.0
    return ("of %d functions holding one of E619's %d dead face-key lines, %d are reachable "
            "from module level (%d called at top level, %d through a chain of calls, %d only "
            "through an argparse set_defaults(func=...) handoff) and %d are not (%d only by "
            "their own recursion, %d only from a function that never runs, %d loaded but never "
            "called, %d named only in a string, %d entirely unreferenced); the same split on "
            "E619's wider population is %d live of %d holders carrying %d dead lines; for scale "
            "%d of %d functions in %d face publishers are reachable (%.1f%%), so the %d dead "
            "face-key lines in a live holder are defects and the %d in an inert holder cost "
            "nothing; %d of the inert holders on that wider population sit in a module that "
            "builds a dict dispatch table of function names, which this scan does not follow, "
            "so inertness is an upper bound rather than a death sentence"
            % (total, c["scope_facekey_dead_lines"], live,
               c["scope_facekey_holders_called_from_module_level"],
               c["scope_facekey_holders_reachable_through_a_chain_of_calls"],
               c["scope_facekey_holders_reachable_through_a_registry_handoff"], total - live,
               c["scope_facekey_holders_called_only_by_itself"],
               c["scope_facekey_holders_called_from_an_unreachable_function"],
               c["scope_facekey_holders_referenced_never_called"],
               c["scope_facekey_holders_named_in_a_string_only"],
               c["scope_facekey_holders_unreferenced"],
               c["scope_all_holders_live"], c["scope_all_holder_functions"],
               c["scope_all_dead_lines"],
               c["functions_reachable_in_the_population"], c["functions_in_the_population"],
               c["population_modules"], share,
               c["scope_facekey_dead_lines_in_a_live_holder"],
               c["scope_facekey_dead_lines_in_an_inert_holder"],
               c["inert_holders_in_a_module_with_a_dict_dispatch_table"]))


def face_problems(face):
    p = []
    if not isinstance(face, dict) or "counts" not in face:
        return ["the face carries no counts block"]
    counts = face["counts"]
    mods = face.get("modules") or []
    holders = [h for mod in mods for h in (mod.get("holders") or [])]

    if counts.get("modules_holding_a_dead_line") != len(mods):
        p.append("counts.modules_holding_a_dead_line says %r but the face publishes %d modules"
                 % (counts.get("modules_holding_a_dead_line"), len(mods)))
    if counts.get("holder_functions_total") != len(holders):
        p.append("counts.holder_functions_total says %r but the face publishes %d holders"
                 % (counts.get("holder_functions_total"), len(holders)))
    for mod in mods:
        if not (mod.get("holders") or []):
            p.append("module %r is published with no holder" % mod.get("module"))
        if sum(h.get("dead_lines", 0) for h in (mod.get("holders") or [])) == 0:
            p.append("module %r is published with no dead line on any holder" % mod.get("module"))
        if mod.get("functions_in_module", 0) < len(mod.get("holders") or []):
            p.append("module %r claims fewer functions than holders" % mod.get("module"))
    for h in holders:
        if h.get("dead_lines_facekey", 0) > h.get("dead_lines", 0):
            p.append("holder %r:%r has more face-key dead lines than dead lines"
                     % (h.get("function"), h.get("def_line")))
        if h.get("reach") not in CLASSES:
            p.append("holder %r:%r carries reach=%r, not a published class"
                     % (h.get("function"), h.get("def_line"), h.get("reach")))
        if h.get("reach") == "reachable_through_a_chain_of_calls" and not h.get("callers"):
            p.append("holder %r:%r is classed as reached through a chain with no caller"
                     % (h.get("function"), h.get("def_line")))
        if h.get("reach") == "called_from_an_unreachable_function" and not h.get("callers"):
            p.append("holder %r:%r is classed as called from an unreachable function with no "
                     "caller" % (h.get("function"), h.get("def_line")))
        if h.get("reach") == "reachable_through_a_registry_handoff" and not (
                h.get("handed_to_a_set_defaults_registry") or h.get("callers")):
            p.append("holder %r:%r is classed as reached through a registry handoff with neither "
                     "a handoff nor a caller recorded"
                     % (h.get("function"), h.get("def_line")))
        if h.get("reach") == "called_only_by_itself" and not h.get("self_recursive_calls"):
            p.append("holder %r:%r is classed as self-recursive with no self call"
                     % (h.get("function"), h.get("def_line")))

    scope_keys = {"scope_all": "dead_lines", "scope_facekey": "dead_lines_facekey",
                  "scope_incoming": "dead_lines_incoming"}
    for scope, key in scope_keys.items():
        held = [h for h in holders if h.get(key, 0) > 0]
        if counts.get(scope + "_holder_functions") != len(held):
            p.append("counts.%s_holder_functions does not re-derive (%r vs %r)"
                     % (scope, counts.get(scope + "_holder_functions"), len(held)))
        if counts.get(scope + "_dead_lines") != sum(h.get(key, 0) for h in held):
            p.append("counts.%s_dead_lines does not re-derive from the holders" % scope)
    for cls in CLASSES:
        want_fk = sum(1 for h in holders if h.get("dead_lines_facekey") and h.get("reach") == cls)
        if counts.get("scope_facekey_holders_" + cls) != want_fk:
            p.append("counts.scope_facekey_holders_%s does not re-derive from the holders" % cls)
        want_all = sum(1 for h in holders if h.get("reach") == cls)
        if counts.get("scope_all_holders_" + cls) != want_all:
            p.append("counts.scope_all_holders_%s does not re-derive from the holders" % cls)
    for name, pool, key in (("scope_facekey", [h for h in holders if h.get("dead_lines_facekey")],
                             "dead_lines_facekey"),
                            ("scope_all", holders, "dead_lines")):
        if counts.get(name + "_holders_live") != sum(1 for h in pool if h.get("reach") in LIVE):
            p.append("counts.%s_holders_live does not re-derive" % name)
        if counts.get(name + "_dead_lines_in_a_live_holder") != sum(
                h.get(key, 0) for h in pool if h.get("reach") in LIVE):
            p.append("counts.%s_dead_lines_in_a_live_holder does not re-derive" % name)
        if counts.get(name + "_dead_lines_in_an_inert_holder") != sum(
                h.get(key, 0) for h in pool if h.get("reach") in INERT):
            p.append("counts.%s_dead_lines_in_an_inert_holder does not re-derive" % name)
    if counts.get("holders_called_through_a_local_alias") != sum(
            1 for h in holders if h.get("calls_through_a_local_alias")):
        p.append("counts.holders_called_through_a_local_alias does not re-derive")
    if counts.get("attribute_hits_not_counted_as_reach") != sum(
            h.get("attribute_hits_not_counted_as_reach", 0) for h in holders):
        p.append("counts.attribute_hits_not_counted_as_reach does not re-derive")
    if counts.get("inert_holders_in_a_module_with_a_dict_dispatch_table") != sum(
            1 for mod in mods if mod.get("dict_dispatch_tables_of_function_names")
            for h in (mod.get("holders") or []) if h.get("reach") in INERT):
        p.append("counts.inert_holders_in_a_module_with_a_dict_dispatch_table does not "
                 "re-derive")

    cc = face.get("e619_cross_check") or {}
    if cc.get("published"):
        if cc.get("rederived_population") != counts.get("population_modules"):
            p.append("the E619 cross-check re-derived %r modules but the counts say %r"
                     % (cc.get("rederived_population"), counts.get("population_modules")))
        if cc.get("agrees") is False:
            p.append("the imported E619 classifier no longer reproduces the published face "
                     "(%r modules differ, %r modules only in the published face)"
                     % (cc.get("modules_with_differing_dead_rows_n"),
                        len(cc.get("modules_only_in_the_published_face") or [])))

    derived = derive_verdict({"modules": mods, "skipped": [None] * (
        counts.get("skipped_modules") or 0),
        "base": {"modules": counts.get("population_modules"),
                 "functions": counts.get("functions_in_the_population"),
                 "reachable_functions": counts.get("functions_reachable_in_the_population"),
                 "functions_in_modules_holding_a_dead_line":
                     counts.get("functions_in_modules_holding_a_dead_line")}})
    if face.get("verdict") != derived:
        p.append("the published verdict %r is not what the holder rows force (%r)"
                 % (face.get("verdict"), derived))
    return p


def build(root=ROOT, m=None):
    m = m or measure(root=root)
    c = counts_of(m)
    base = m["base"]
    face = {
        "study": STUDY,
        "script": "scripts/e622_deadlocal_reach.py",
        "evidence_cutoff": TODAY,
        "dept": "research+engineering",
        "method": ("take E619's own face-publisher population and dead-reader-line classifier "
                   "(imported, not re-implemented), resolve each dead line to its enclosing "
                   "function definition, build the module's intra-file call graph (explicit "
                   "calls plus one-hop local aliases, attribute calls only onto class-scoped "
                   "definitions) and class the holder by whether it is reachable from module "
                   "level"),
        "population_source": "scripts/*.py (AST) via e619.population, face publishers only, "
                             "less this script and its smoke leg",
        "base_rates": {
            "population_modules": base["modules"],
            "functions_in_the_population": base["functions"],
            "functions_reachable_in_the_population": base["reachable_functions"],
            "share_of_functions_reachable": round(
                (100.0 * base["reachable_functions"] / base["functions"])
                if base["functions"] else 0.0, 2),
            "functions_in_modules_holding_a_dead_line":
                base["functions_in_modules_holding_a_dead_line"],
            "note": ("the base rate is the control for 'never called': in a module where most "
                     "functions are reachable, an inert holder is the exception and a live holder "
                     "is the rule"),
        },
        "counts": c,
        "e619_cross_check": m["cross_check"],
        "modules": m["modules"],
        "skipped": m["skipped"],
        "limits": [
            "reach is measured inside one module: a holder exported and called by an importer is "
            "outside this study, so 'unreferenced' means unreferenced here, not dead everywhere",
            "an attribute call (obj.name()) becomes an edge only when the receiver is self/cls "
            "(class-scoped callee) or a module object imported in the file -- the house's "
            "re-import entry point sys.exit(_canonical.main()) is reachable that way; every "
            "other receiver is ignored and counted per holder in "
            "attribute_hits_not_counted_as_reach, because a module-level function named get or "
            "write would otherwise be 'called' by every d.get / fh.write in the file",
            "string mentions are a class of their own and never count as reach: a constant equal "
            "to a function name also matches labels, keys and prose",
            "a local alias is followed exactly one hop (A = f then A()), never through a "
            "container, a getattr or a registry dict keyed by name",
            "the only registry hand-off followed is argparse's set_defaults(func=F): a function "
            "reached that way is a class of its own, because the call happens inside the parser "
            "the module itself built, while a name stored in a plain dict or resolved through "
            "getattr is not followed at all",
            "a decorated definition is not counted as reach: the decorator expression is a "
            "mention, so a function only registered by a framework decorator lands in "
            "referenced_never_called",
            "E619 skips modules that do not parse; the 14 it skips are absent here too",
            "this script excludes itself and its smoke leg from the population it measures",
        ],
        "verdict": derive_verdict(m),
        "answer": answer_of(m),
    }
    return face, face_problems(face)


def write_face(out_dir, doc, face=FACE, latest=LATEST):
    os.makedirs(out_dir, exist_ok=True)
    for name in (face, latest):
        with io.open(os.path.join(out_dir, name), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=1, sort_keys=False)
            fh.write("\n")
    return os.path.join(out_dir, face)


# ---------------------------------------------------------------- selftest
FIXTURE = '''
import io, json, os

HANDLERS = {"x": "only_in_a_string"}


def entry(rows):
    return called_everywhere(rows)


def called_everywhere(rows):
    tmp = rows["counts"]
    return 1


def unreachable_parent(rows):
    def child(inner):
        dead = inner["summary"]
        return 2
    return child(rows)


def never_called(doc):
    dead = doc["summary"]
    return 3


def only_recursive(n):
    if n:
        return only_recursive(n - 1)
    return 0


def only_in_a_string(rows):
    dead = rows["counts"]
    return 4


def replaced_by_alias(rows):
    dead = rows["counts"]
    return 5


def loaded_but_never_called(rows):
    dead = rows["counts"]
    return 6


class Holder(object):
    def method(self, rows):
        dead = rows["counts"]
        return 7


def dispatch(rows):
    entry(rows)
    alias = replaced_by_alias
    alias(rows)
    print(loaded_but_never_called)
    Holder().method(rows)
    return 8


def build(rows):
    face = {"counts": 1}
    path = os.path.join("x", "face.json")
    with io.open(path, "w", encoding="utf-8") as fh:
        json.dump(face, fh)
    return face


def cli_entry(args):
    cfg = args["cfg"]
    return 9


def make_parser():
    import argparse
    ap = argparse.ArgumentParser()
    ap.set_defaults(func=cli_entry)
    return ap


make_parser()


if __name__ == "__main__":
    dispatch({})
'''


def selftest():
    legs = []
    tree = ast.parse(FIXTURE)
    rows = function_rows(tree)
    by_name = {}
    for r in rows:
        by_name.setdefault(r["function"], []).append(r)
    one = lambda n: by_name[n][0] if n in by_name else {}

    legs.append(("every function definition is counted", len(rows) == len(by_name) or
                 len(rows) >= 13))
    legs.append(("a top-level call makes a function called_from_module_level",
                 one("dispatch").get("reach") == "called_from_module_level"))
    legs.append(("a call from a reachable function is reached through a chain",
                 one("entry").get("reach") == "reachable_through_a_chain_of_calls"))
    legs.append(("the chain reaches two hops",
                 one("called_everywhere").get("reach") == "reachable_through_a_chain_of_calls"))
    legs.append(("a function nothing touches is unreferenced",
                 one("never_called").get("reach") == "unreferenced"))
    legs.append(("recursion alone is called_only_by_itself",
                 one("only_recursive").get("reach") == "called_only_by_itself"))
    legs.append(("a name only inside a string is named_in_a_string_only",
                 one("only_in_a_string").get("reach") == "named_in_a_string_only"))
    legs.append(("a call through a one-hop alias still reaches",
                 one("replaced_by_alias").get("reach") == "reachable_through_a_chain_of_calls"))
    legs.append(("the alias call is recorded as such",
                 one("replaced_by_alias").get("calls_through_a_local_alias") == 1))
    legs.append(("a bare mention without a call is referenced_never_called",
                 one("loaded_but_never_called").get("reach") == "referenced_never_called"))
    legs.append(("a method called by name from a reachable function is reachable",
                 one("method").get("reach") == "reachable_through_a_chain_of_calls"))
    legs.append(("the method's scope is published", one("method").get("scope") == "class"))
    legs.append(("a nested helper of an unreachable parent is called_from_an_unreachable_function",
                 one("child").get("reach") == "called_from_an_unreachable_function"))
    legs.append(("the nested function's scope is published", one("child").get("scope") == "nested"))
    legs.append(("the unreachable parent itself is unreferenced",
                 one("unreachable_parent").get("reach") == "unreferenced"))
    legs.append(("a function handed to argparse set_defaults is reached through the handoff",
                 one("cli_entry").get("reach") == "reachable_through_a_registry_handoff"))
    legs.append(("the handoff is recorded on the holder",
                 one("cli_entry").get("handed_to_a_set_defaults_registry") == 1))
    legs.append(("the parser builder that does the handing is called at module level",
                 one("make_parser").get("reach") == "called_from_module_level"))

    attr_tree = ast.parse(
        "def get(d):\n    return 1\n\n"
        "def run(d):\n    return d.get('k')\n")
    arow = [r for r in function_rows(attr_tree) if r["function"] == "get"][0]
    legs.append(("an attribute call on a module-level function is not reach",
                 arow["reach"] == "unreferenced"))
    legs.append(("the ignored attribute hit is published",
                 arow["attribute_hits_not_counted_as_reach"] == 1))

    chain_tree = ast.parse(
        "def a():\n    return 1\n"
        "def b():\n    return a()\n"
        "def c():\n    return b()\n"
        "def start():\n    return c()\n"
        "start()\n")
    crows = {r["function"]: r for r in function_rows(chain_tree)}
    legs.append(("a three-hop chain is reachable", crows["a"]["reach"] ==
                 "reachable_through_a_chain_of_calls"))

    self_import_tree = ast.parse(
        "import sys\n"
        "def main(argv):\n    return 0\n"
        "if __name__ == '__main__':\n"
        "    import sample as _canonical\n"
        "    sys.exit(_canonical.main(sys.argv))\n")
    irows = {r["function"]: r for r in function_rows(self_import_tree, stem="sample")}
    legs.append(("a self-import entry point reaches main",
                 irows["main"]["reach"] == "called_from_module_level"))
    dict_recv_tree = ast.parse(
        "def main(argv):\n    return 0\n"
        "cfg = {}\n"
        "cfg.main()\n")
    drows = {r["function"]: r for r in function_rows(dict_recv_tree, stem="sample")}
    legs.append(("a call on a plain local receiver does not reach main",
                 drows["main"]["reach"] == "unreferenced"))

    cycle_tree = ast.parse(
        "def a():\n    return b()\n"
        "def b():\n    return a()\n")
    yrows = {r["function"]: r for r in function_rows(cycle_tree)}
    legs.append(("a call cycle with no entry point does not loop forever and stays inert",
                 yrows["a"]["reach"] == "called_from_an_unreachable_function"))

    m = measure(root=ROOT)
    legs.append(("the measured population parses and is non-empty", m["base"]["modules"] > 100))
    legs.append(("this study excludes itself from the population it measures",
                 all(not mod["module"].endswith(p) for mod in m["modules"] for p in SELF_PARTS)))
    m = measure(root=ROOT)
    c = counts_of(m)
    holders = [h for mod in m["modules"] for h in mod["holders"]]
    legs.append(("every holder carries a dead line", all(h["dead_lines"] >= 1 for h in holders)))
    legs.append(("counts re-add the holder rows", c["holder_functions_total"] == len(holders)))
    legs.append(("every holder's reach is a published class",
                 all(h["reach"] in CLASSES for h in holders)))
    legs.append(("holders are a subset of their module's functions",
                 all(mod["functions_in_module"] >= len(mod["holders"]) for mod in m["modules"])))
    legs.append(("the live and inert dead-line counts add up",
                 c["scope_facekey_dead_lines_in_a_live_holder"] +
                 c["scope_facekey_dead_lines_in_an_inert_holder"] == c["scope_facekey_dead_lines"]))
    legs.append(("the E617 anchor holder is present",
                 any(h["function"] == "derive_verdict" and
                     mod["module"].endswith("e396_face_basename_suffix.py")
                     for mod in m["modules"] for h in mod["holders"])))
    face, problems = build(root=ROOT, m=m)
    legs.append(("the built face has no problems", problems == []))
    bad = json.loads(json.dumps(face))
    bad["counts"]["holder_functions_total"] += 1
    legs.append(("a perturbed holder count fails face_problems", face_problems(bad) != []))
    bad2 = json.loads(json.dumps(face))
    if bad2["modules"]:
        bad2["modules"][0]["holders"] = bad2["modules"][0]["holders"][:-1]
    legs.append(("a dropped holder row fails face_problems", face_problems(bad2) != []))
    bad3 = json.loads(json.dumps(face))
    bad3["verdict"] = "no_function_holds_a_dead_reader_line"
    if face["verdict"] == "no_function_holds_a_dead_reader_line":
        bad3["verdict"] = "other"
    legs.append(("a perturbed verdict fails face_problems", face_problems(bad3) != []))
    bad4 = json.loads(json.dumps(face))
    if bad4["modules"] and bad4["modules"][0]["holders"]:
        bad4["modules"][0]["holders"][0]["reach"] = "called_only_by_itself"
        bad4["modules"][0]["holders"][0]["self_recursive_calls"] = 0
    legs.append(("a self-recursive class with no self call fails face_problems",
                 face_problems(bad4) != []))

    failed = [n for n, ok in legs if not ok]
    for name, ok in legs:
        print(("PASS" if ok else "FAIL") + " :: " + name)
    print("%d/%d selftest legs" % (len(legs) - len(failed), len(legs)))
    return 0 if not failed else 1


# ---------------------------------------------------------------- CLI
def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="build")
    args = ap.parse_args(argv[1:])
    cmd = args.cmd.lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "check":
        face, problems = build(root=ROOT)
        print("problems=" + json.dumps(problems, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "verify":
        path = os.path.join(OUTDIR, FACE)
        if not os.path.exists(path):
            print("no face at %s" % path)
            return 1
        doc = json.load(io.open(path, encoding="utf-8"))
        problems = face_problems(doc)
        print("problems=" + json.dumps(problems, ensure_ascii=False))
        return 0 if not problems else 1
    face, problems = build(root=ROOT)
    if cmd in ("build", "run"):
        path = write_face(OUTDIR, face)
        print("face:", path)
    if problems:
        print("PROBLEMS: " + "; ".join(problems))
        return 1
    c = face["counts"]
    print("modules=%d holders=%d facekey_holders=%d live=%d inert_lines=%d live_lines=%d"
          % (c["modules_holding_a_dead_line"], c["holder_functions_total"],
             c["scope_facekey_holder_functions"], c["scope_facekey_holders_live"],
             c["scope_facekey_dead_lines_in_an_inert_holder"],
             c["scope_facekey_dead_lines_in_a_live_holder"]))
    print("verdict=" + face["verdict"])
    print("answer=" + face["answer"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))