"""E628 -- does the object a dead face-key line reads arrive from outside its function?

E625 (r1643) priced the value test, E626 (r1644) followed the one handover into its callee and E627
(r1645) scanned the interval for a second local name bound to the same dict.  All three work inside
the body of the function that holds the dead line, and E627 publishes exactly that bound:

  no alias bound before the function body (a module-level name)
  no rebinding through a container or comprehension

This card prices the bound.  For each live dead face-key line the receiver expression is classified
by *where the object it names is bound*:

  the_receiver_is_a_parameter_of_the_function                  the name is an argument
  the_receiver_is_bound_inside_the_function_body               a local assignment / for / with target
  the_receiver_is_read_out_of_a_container_that_arrives_from_outside
                                                               rows[0] / self.cfg / m["k"] whose
                                                               leftmost name is a parameter or a
                                                               module-level name
  the_receiver_is_read_out_of_a_container_bound_inside_the_function
                                                               d["k"] where d is a local
  the_receiver_is_a_module_level_name                          the name is bound in the module body
  the_receiver_is_an_import_alias                              the name comes from an import
  the_receiver_does_not_resolve_in_this_module                 no binding anywhere in the module

The first, third (when the base arrives from outside), fifth and sixth put the object's origin
*before* the interval E625-E627 scan starts (the function body opening), so a write that happens
where the object began is invisible to all three earlier cards.

For each such row this study also asks the only question it can answer statically: does any other
site in the module -- another function's body or the module body -- write that key on that name?
A name is not an object (E206/E207), so that arm is published as a name-level reading, not a proof.

Deliberately NOT done: no interprocedural descent, no class/attribute resolution (self.cfg is
classified by the base name only), no alias analysis beyond E627's interval scan, no concurrency
model, no fixture write, no runner.

Deterministic, static, no network, no runner, no fixture write.
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
FACE = "RECEIVERORIGIN.json"
LATEST = "receiverorigin_latest.json"
STUDY = "E628_receiver_origin"
SELF_PARTS = {"e628_receiver_origin.py", "run_e628_smoke_leg.py", "_probe_e628.py"}

ORIGIN_CLASSES = [
    "the_receiver_is_a_parameter_of_the_function",
    "the_receiver_is_bound_inside_the_function_body",
    "the_receiver_is_read_out_of_a_container_that_arrives_from_outside",
    "the_receiver_is_read_out_of_a_container_bound_inside_the_function",
    "the_receiver_is_a_module_level_name",
    "the_receiver_is_an_import_alias",
    "the_receiver_does_not_resolve_in_this_module",
]
PARAM, LOCAL, CONTAINER_OUT, CONTAINER_IN, MODULE, IMPORT, UNRESOLVED = ORIGIN_CLASSES

OUTSIDE_ORIGINS = {PARAM, CONTAINER_OUT, MODULE, IMPORT}

FORM_PLAIN = "a_plain_name"
FORM_ATTRIBUTE = "an_attribute_chain"
FORM_SUBSCRIPT = "a_subscript"
FORM_OTHER = "another_expression"
RECEIVER_FORMS = [FORM_PLAIN, FORM_ATTRIBUTE, FORM_SUBSCRIPT, FORM_OTHER]

if HERE not in sys.path:
    sys.path.insert(0, HERE)
import e619_dead_reader_locals as e619                                              # noqa: E402
import e622_deadlocal_reach as e622                                                 # noqa: E402
import e623_deadline_key_use as e623                                                # noqa: E402
import e624_sibling_read_object as e624                                             # noqa: E402
import e625_sibling_read_value as e625                                              # noqa: E402
import e626_handover_write as e626                                                  # noqa: E402
import e627_alias_binding as e627                                                   # noqa: E402

FUNC = (ast.FunctionDef, ast.AsyncFunctionDef)


# ---------------------------------------------------------------- where a name is bound
def params_of(fn):
    """Every argument name the function declares."""
    a = fn.args
    names = [x.arg for x in list(getattr(a, "posonlyargs", [])) + list(a.args)
             + list(a.kwonlyargs)]
    for extra in (a.vararg, a.kwarg):
        if extra is not None:
            names.append(extra.arg)
    return set(names)


def _target_names(node):
    return [n.id for n in ast.walk(node) if isinstance(n, ast.Name)]


def bindings_in(nodes):
    """(name, line) pairs bound by the nodes, in the simple forms this study names."""
    out = []
    for n in nodes:
        line = getattr(n, "lineno", 0)
        if isinstance(n, ast.Assign):
            for t in n.targets:
                for name in _target_names(t):
                    out.append((name, line))
        elif isinstance(n, (ast.AnnAssign, ast.AugAssign)):
            for name in _target_names(n.target):
                out.append((name, line))
        elif isinstance(n, (ast.For, ast.AsyncFor)):
            for name in _target_names(n.target):
                out.append((name, line))
        elif isinstance(n, (ast.With, ast.AsyncWith)):
            for item in n.items:
                if item.optional_vars is not None:
                    for name in _target_names(item.optional_vars):
                        out.append((name, line))
        elif isinstance(n, ast.NamedExpr):
            for name in _target_names(n.target):
                out.append((name, line))
        elif isinstance(n, FUNC):
            out.append((n.name, line))
    return out


def module_bindings(tree):
    """Names bound in the module body, split into plain bindings and import aliases."""
    plain, imported = set(), set()
    body = [n for n in tree.body if not isinstance(n, (ast.ClassDef,))]
    for name, _line in bindings_in(body):
        plain.add(name)
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                imported.add((a.asname or a.name.split(".")[0]))
        elif isinstance(n, ast.ImportFrom):
            for a in n.names:
                if a.name == "*":
                    continue
                imported.add(a.asname or a.name)
    return plain, imported


# Three per-module memos: the module body is walked once, not once per row, and a 14k-line
# function's scope is reduced to its bindings once as well (E442 family: re-slicing a big source
# per node dominated the build).
_CACHE = {}


def _cached(key, build):
    if key not in _CACHE:
        _CACHE[key] = build()
    return _CACHE[key]


# ---------------------------------------------------------------- receiver origin
def receiver_form(node):
    if node is None:
        return FORM_OTHER
    if isinstance(node, ast.Name):
        return FORM_PLAIN
    if isinstance(node, ast.Attribute):
        return FORM_ATTRIBUTE
    if isinstance(node, ast.Subscript):
        return FORM_SUBSCRIPT
    return FORM_OTHER


def base_binding(node, fn, tree, dead_line, scope):
    """(leftmost name, where that name is bound) for a receiver expression."""
    base = e624.base_name(node)
    if base is None:
        return None, "no_nameable_base"
    params = _cached(("params", id(fn)), lambda: params_of(fn))
    if base in params:
        return base, PARAM
    bound = [(n, l) for n, l in _cached(("scope", id(fn)), lambda: bindings_in(scope))
             if n == base and l <= dead_line]
    if bound:
        return base, LOCAL
    plain, imported = _cached(("module", id(tree)), lambda: module_bindings(tree))
    if base in imported:
        return base, IMPORT
    if base in plain:
        return base, MODULE
    return base, UNRESOLVED


def origin_of(node, fn, tree, dead_line, scope):
    """The published origin class of the receiver expression."""
    form = receiver_form(node)
    base, where = base_binding(node, fn, tree, dead_line, scope)
    if where in ("no_nameable_base", UNRESOLVED):
        cls = UNRESOLVED
    elif form == FORM_PLAIN:
        cls = {PARAM: PARAM, LOCAL: LOCAL, MODULE: MODULE, IMPORT: IMPORT}[where]
    else:
        cls = CONTAINER_IN if where == LOCAL else CONTAINER_OUT
    before = None if cls == UNRESOLVED else cls in OUTSIDE_ORIGINS
    return {"receiver_form": form, "receiver_base_name": base,
            "base_binding_origin": where, "receiver_origin": cls,
            "origin_before_the_e627_interval_start": before}


# ---------------------------------------------------------------- writers elsewhere
def writers_elsewhere(tree, fns, fn, base, key, scopes):
    """Write marks at ``key`` on ``base`` outside ``fn`` -- other functions and the module body.

    ``scopes`` caches each function's own scope for the module, so a module with a 14k-line
    function is walked once per (base, key) pair instead of once per row.
    """
    sites = []
    for other in fns:
        if other is fn:
            continue
        if id(other) not in scopes:
            scopes[id(other)] = e623.own_scope(other)
        named, _unnamed, _handed = e625.write_marks(scopes[id(other)], base, key, base)
        for m in named:
            sites.append({"line": m["line"], "function": other.name, "form": m["form"]})
    if "__module_body__" not in scopes:
        scopes["__module_body__"] = [n for n in tree.body if not isinstance(n, FUNC)]
    named, _unnamed, _handed = e625.write_marks(scopes["__module_body__"], base, key, base)
    for m in named:
        sites.append({"line": m["line"], "function": None, "form": m["form"]})
    sites.sort(key=lambda s: (s["line"], s["function"] or ""))
    return sites


# ---------------------------------------------------------------- rows with origin facts
def origin_facts(tree, stem, graph):
    """E627's rows for one module, each extended with where its receiver is bound."""
    rows, inert = e627.alias_facts(tree, stem, graph)
    scopes = {}
    cache = {}
    for r in rows:
        fn = e623.innermost(graph["fns"], r)
        if fn is None:
            continue
        scope = _cached(("own", id(fn)), lambda: e623.own_scope(fn))
        reads = e623.key_reads(scope, r["key"])
        dead_nodes = [n for n in reads if n.lineno == r["line"]]
        if not dead_nodes:
            r.update({"receiver_form": None, "receiver_base_name": None,
                      "base_binding_origin": "no_read_node_at_the_published_line",
                      "receiver_origin": UNRESOLVED,
                      "origin_before_the_e627_interval_start": None,
                      "base_name_written_at_the_key_outside_the_interval": []})
            continue
        recv = e624.receiver_of(dead_nodes[0])
        r.update(origin_of(recv, fn, tree, r["line"], scope))
        sites = []
        if r.get("origin_before_the_e627_interval_start") is True:
            sig = (r["receiver_base_name"], r["key"], id(fn))
            if sig not in cache:
                cache[sig] = writers_elsewhere(tree, graph["fns"], fn,
                                               r["receiver_base_name"], r["key"], scopes)
            sites = cache[sig]
        r["base_name_written_at_the_key_outside_the_interval"] = sites
        r["base_name_is_written_elsewhere"] = bool(sites)
    return rows, inert


def measure(root=ROOT):
    _CACHE.clear()
    mods, skipped = e619.population(root)
    skip = (set(e622.SELF_PARTS) | set(e623.SELF_PARTS) | set(e624.SELF_PARTS)
            | set(e625.SELF_PARTS) | set(e626.SELF_PARTS) | set(e627.SELF_PARTS)
            | set(SELF_PARTS))
    keep = [(rel, tree) for rel, tree in mods if os.path.basename(rel) not in skip]
    lines, inert = [], 0
    for rel, tree in keep:
        stem = os.path.basename(rel)[:-3]
        graph = e622.call_graph(tree, stem)
        rows, inert_here = origin_facts(tree, stem, graph)
        for r in rows:
            r["module"] = rel
        lines.extend(rows)
        inert += inert_here
    lines.sort(key=lambda r: (r["module"], r["line"]))
    return {"population_modules": len(keep), "skipped": skipped, "lines": lines,
            "inert_dead_facekey_lines": inert,
            "cross_check": e627_cross_check(root, lines)}


def e627_cross_check(root, lines):
    """Diff the re-derived rows against the face E627 published (row for row)."""
    out = {"published": False, "agrees": None}
    path = os.path.join(root, "results", "state_tilt", e627.LATEST)
    if not os.path.exists(path):
        out["note"] = "no published E627 face on disk"
        return out
    pub = json.load(io.open(path, encoding="utf-8"))
    key = lambda r: (r.get("module"), r.get("function"), r.get("def_line"), r.get("line"))
    published = {key(r): r for r in (pub.get("lines") or [])}
    mine = {key(r): r for r in lines}
    moved = sorted(k for k in set(mine) & set(published)
                   if mine[k].get("duplicate_class_after_the_alias_scan")
                   != published[k].get("duplicate_class_after_the_alias_scan"))
    out.update({
        "published": True,
        "published_lines": len(published),
        "rederived_lines": len(mine),
        "lines_whose_duplicate_class_differs_n": len(moved),
        "lines_whose_duplicate_class_differs": [list(k) for k in moved[:10]],
        "lines_only_here": [list(k) for k in sorted(set(mine) - set(published))][:10],
        "lines_only_in_the_published_face":
            [list(k) for k in sorted(set(published) - set(mine))][:10],
        "published_split": {k: (pub.get("counts") or {}).get(k) for k in
                            ("duplicates_surviving_after_the_alias_scan",
                             "duplicates_stored_over_after_the_alias_scan",
                             "duplicates_still_undecided_after_the_alias_scan")},
        "agrees": not moved and not (set(published) - set(mine)),
    })
    return out


# ---------------------------------------------------------------- counts / verdict
def _duplicates(lines):
    return [r for r in lines
            if r.get("corrected_class") == e624.CORRECTED[0]
            and r.get("sibling_read_reads_the_same_object_after_the_dead_line")]


def counts_of(m):
    lines = m["lines"]
    oc = {k: 0 for k in ORIGIN_CLASSES}
    fc = {k: 0 for k in RECEIVER_FORMS}
    for r in lines:
        origin = r.get("receiver_origin")
        oc[origin] = oc.get(origin, 0) + 1
        form = r.get("receiver_form")
        if form in fc:
            fc[form] += 1
    dup = _duplicates(lines)
    dup_open = [r for r in dup if r.get("origin_before_the_e627_interval_start") is True]
    dup_unresolved = [r for r in dup if r.get("origin_before_the_e627_interval_start") is None]
    dup_written = [r for r in dup_open if r.get("base_name_is_written_elsewhere")]
    c = {
        "population_modules": m["population_modules"],
        "skipped_modules": len(m["skipped"]),
        "live_dead_facekey_lines": len(lines),
        "inert_dead_facekey_lines": m["inert_dead_facekey_lines"],
        "same_object_duplicate_rows": len(dup),
        "duplicates_whose_origin_lies_before_the_interval": len(dup_open),
        "duplicates_whose_origin_cannot_be_resolved": len(dup_unresolved),
        "duplicates_whose_receiver_name_is_written_elsewhere": len(dup_written),
        "lines_whose_receiver_name_is_written_elsewhere": sum(
            1 for r in lines if r.get("base_name_is_written_elsewhere")),
        "rows_read_through_a_container": fc[FORM_SUBSCRIPT] + fc[FORM_ATTRIBUTE],
        "rows_with_no_resolvable_origin": oc[UNRESOLVED],
    }
    for k in ORIGIN_CLASSES:
        c["origin_" + k] = oc[k]
    for k in RECEIVER_FORMS:
        c["form_" + k] = fc[k]
    return c


def derive_verdict(m):
    c = counts_of(m)
    if c["population_modules"] == 0:
        return "no_face_publishers_in_the_population"
    if c["live_dead_facekey_lines"] == 0:
        return "no_live_dead_facekey_line_in_the_population"
    n = c["same_object_duplicate_rows"]
    if n == 0:
        return "no_same_object_duplicate_row_whose_origin_to_place"
    if c["duplicates_whose_origin_lies_before_the_interval"] == 0:
        return ("every_one_of_the_%d_duplicate_receivers_is_bound_inside_the_function_so_the_"
                "interval_covers_its_origin" % n)
    k = c["duplicates_whose_origin_lies_before_the_interval"]
    if c["duplicates_whose_receiver_name_is_written_elsewhere"] == 0:
        return ("%d_of_the_%d_duplicate_receivers_arrive_from_outside_the_interval_but_no_other_"
                "site_in_the_module_writes_that_name_at_that_key" % (k, n))
    j = c["duplicates_whose_receiver_name_is_written_elsewhere"]
    return ("%d_of_the_%d_duplicate_receivers_arrive_from_outside_the_interval_and_%d_of_those_"
            "names_are_written_at_the_key_elsewhere_in_the_module" % (k, n, j))


def answer_of(m):
    c = counts_of(m)
    if c["same_object_duplicate_rows"] == 0:
        return "E627 left no same-object duplicate row, so there is no receiver origin to place"
    return ("Over %d live dead face-key line(s) the receiver is a parameter of the function in %d, "
            "bound inside its body in %d, read out of a container that arrives from outside in %d "
            "and out of a container bound inside in %d, a module-level name in %d, an import alias "
            "in %d and unresolvable in %d.  %d of the %d same-object duplicate row(s) read an "
            "object whose origin lies before the interval E625-E627 scan (the other %d are bound "
            "inside it, %d unresolved), and %d of those %d names is written at that key by another "
            "site in the module"
            % (c["live_dead_facekey_lines"], c["origin_" + PARAM], c["origin_" + LOCAL],
               c["origin_" + CONTAINER_OUT], c["origin_" + CONTAINER_IN],
               c["origin_" + MODULE], c["origin_" + IMPORT], c["origin_" + UNRESOLVED],
               c["duplicates_whose_origin_lies_before_the_interval"],
               c["same_object_duplicate_rows"],
               c["same_object_duplicate_rows"]
               - c["duplicates_whose_origin_lies_before_the_interval"]
               - c["duplicates_whose_origin_cannot_be_resolved"],
               c["duplicates_whose_origin_cannot_be_resolved"],
               c["duplicates_whose_receiver_name_is_written_elsewhere"],
               c["duplicates_whose_origin_lies_before_the_interval"]))


# ---------------------------------------------------------------- face problems
def face_problems(face):
    p = []
    if not isinstance(face, dict) or "counts" not in face:
        return ["the face carries no counts block"]
    counts = face["counts"]
    lines = face.get("lines") or []
    if counts.get("live_dead_facekey_lines") != len(lines):
        p.append("counts.live_dead_facekey_lines says %r but the face publishes %d lines"
                 % (counts.get("live_dead_facekey_lines"), len(lines)))
    oc = {k: 0 for k in ORIGIN_CLASSES}
    fc = {k: 0 for k in RECEIVER_FORMS}
    for r in lines:
        origin = r.get("receiver_origin")
        if origin not in ORIGIN_CLASSES:
            p.append("line %r in %r carries receiver_origin=%r"
                     % (r.get("line"), r.get("function"), origin))
        else:
            oc[origin] += 1
        form = r.get("receiver_form")
        if form in fc:
            fc[form] += 1
        elif form is not None:
            p.append("line %r in %r carries receiver_form=%r"
                     % (r.get("line"), r.get("function"), form))
        before = r.get("origin_before_the_e627_interval_start")
        if origin in ORIGIN_CLASSES:
            want = None if origin == UNRESOLVED else origin in OUTSIDE_ORIGINS
            if before is not want:
                p.append("line %r in %r says origin_before_the_e627_interval_start=%r against "
                         "receiver_origin=%r" % (r.get("line"), r.get("function"), before, origin))
        sites = r.get("base_name_written_at_the_key_outside_the_interval") or []
        if bool(sites) != bool(r.get("base_name_is_written_elsewhere")):
            p.append("line %r in %r publishes %d writer site(s) but "
                     "base_name_is_written_elsewhere=%r"
                     % (r.get("line"), r.get("function"), len(sites),
                        r.get("base_name_is_written_elsewhere")))
        base = r.get("receiver_base_name")
        for s in sites:
            if not base:
                p.append("line %r in %r publishes a writer site for a receiver with no base name"
                         % (r.get("line"), r.get("function")))
    for k in ORIGIN_CLASSES:
        if counts.get("origin_" + k) != oc[k]:
            p.append("counts.origin_%s does not re-derive from the lines" % k)
    if sum(oc.values()) != len(lines):
        p.append("the origin classes do not add up to the published line count")
    for k in RECEIVER_FORMS:
        if counts.get("form_" + k) != fc[k]:
            p.append("counts.form_%s does not re-derive from the lines" % k)
    if sum(fc.values()) > len(lines):
        p.append("the receiver forms add up to more lines than the face publishes")
    dup = _duplicates(lines)
    if counts.get("same_object_duplicate_rows") != len(dup):
        p.append("counts.same_object_duplicate_rows does not re-derive")
    open_rows = [r for r in dup if r.get("origin_before_the_e627_interval_start") is True]
    if counts.get("duplicates_whose_origin_lies_before_the_interval") != len(open_rows):
        p.append("counts.duplicates_whose_origin_lies_before_the_interval does not re-derive")
    unres = [r for r in dup if r.get("origin_before_the_e627_interval_start") is None]
    if counts.get("duplicates_whose_origin_cannot_be_resolved") != len(unres):
        p.append("counts.duplicates_whose_origin_cannot_be_resolved does not re-derive")
    written = [r for r in open_rows if r.get("base_name_is_written_elsewhere")]
    if counts.get("duplicates_whose_receiver_name_is_written_elsewhere") != len(written):
        p.append("counts.duplicates_whose_receiver_name_is_written_elsewhere does not re-derive")
    if counts.get("lines_whose_receiver_name_is_written_elsewhere") != sum(
            1 for r in lines if r.get("base_name_is_written_elsewhere")):
        p.append("counts.lines_whose_receiver_name_is_written_elsewhere does not re-derive")
    if counts.get("rows_read_through_a_container") != fc[FORM_SUBSCRIPT] + fc[FORM_ATTRIBUTE]:
        p.append("counts.rows_read_through_a_container does not re-derive")
    if counts.get("rows_with_no_resolvable_origin") != oc[UNRESOLVED]:
        p.append("counts.rows_with_no_resolvable_origin does not re-derive")
    cc = face.get("e627_cross_check") or {}
    if cc.get("published"):
        if cc.get("agrees") is False:
            p.append("the re-derived E627 population no longer matches the published face "
                     "(%r rows differ)" % cc.get("lines_whose_duplicate_class_differs_n"))
        if cc.get("rederived_lines") != counts.get("live_dead_facekey_lines"):
            p.append("the E627 cross-check re-derived %r lines but the counts say %r"
                     % (cc.get("rederived_lines"), counts.get("live_dead_facekey_lines")))
    derived = derive_verdict({"population_modules": counts.get("population_modules"),
                              "lines": lines,
                              "inert_dead_facekey_lines": counts.get("inert_dead_facekey_lines"),
                              "skipped": [None] * (counts.get("skipped_modules") or 0)})
    if face.get("verdict") != derived:
        p.append("the published verdict %r is not what the line rows force (%r)"
                 % (face.get("verdict"), derived))
    return p


def face_from(m):
    face = {
        "study": STUDY,
        "script": "scripts/e628_receiver_origin.py",
        "evidence_cutoff": TODAY,
        "dept": "research+engineering",
        "method": ("for every live dead face-key line, classify where the receiver expression's "
                   "leftmost name is bound (parameter / local / container / module level / import "
                   "/ unresolvable), mark the classes whose origin precedes the interval E625-E627 "
                   "scan, and then ask whether any other site in the module writes that key on that "
                   "name"),
        "population_source": ("scripts/*.py (AST) via e619.population, E627's alias rows over "
                              "E626/E625/E624, less the "
                              "E619/E622/E623/E624/E625/E626/E627/this study self-exclusion sets"),
        "counts": counts_of(m),
        "e627_cross_check": m.get("cross_check") or {"published": False},
        "lines": m["lines"],
        "skipped": m["skipped"],
        "limits": [
            "a name is not an object: the writer arm reports sites that write the same key on the "
            "same spelled name elsewhere in the module, which can be a different object entirely",
            "the receiver is classified by its leftmost name only: self.cfg is read as a container "
            "off a parameter, not as the attribute of a resolved class",
            "no interprocedural descent: a called function in the interval is not followed here "
            "(E626 followed handovers one hop for the value test only)",
            "no concurrency model: a writer outside the module, or between the two reads through "
            "another path, is out of reach",
            "no rebinding-through-a-call analysis: a name assigned from a call result is a local "
            "binding, and where that object comes from is not traced",
            "the population is the one E627 published; this study excludes itself, its smoke leg "
            "and its probe, and keeps every earlier study's self-exclusion set",
        ],
        "verdict": derive_verdict(m),
        "answer": answer_of(m),
    }
    return face, face_problems(face)


def build(root=ROOT):
    return face_from(measure(root=root))


def write_face(out_dir, doc, face=FACE, latest=LATEST):
    os.makedirs(out_dir, exist_ok=True)
    for name in (face, latest):
        with io.open(os.path.join(out_dir, name), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=1, sort_keys=False)
            fh.write("\n")
    return os.path.join(out_dir, face)


# ---------------------------------------------------------------- selftest
FIXTURE = '''
import io, json


def parameter_receiver(m):
    face = {"counts": 1, "x": None}
    seen = []
    first = m["counts"]
    seen.append(m["counts"])
    json.dump(face, io.open("x", "w"))
    return seen


def local_receiver():
    face = {"counts": 1, "x": None}
    m = {"counts": 1}
    seen = []
    first = m["counts"]
    seen.append(m["counts"])
    json.dump(face, io.open("x", "w"))
    return seen


def module_receiver():
    face = {"counts": 1, "x": None}
    seen = []
    first = MOD["counts"]
    seen.append(MOD["counts"])
    json.dump(face, io.open("x", "w"))
    return seen


def container_from_a_parameter(rows):
    face = {"counts": 1, "x": None}
    seen = []
    first = rows[0]["counts"]
    seen.append(rows[0]["counts"])
    json.dump(face, io.open("x", "w"))
    return seen


def container_bound_inside():
    face = {"counts": 1, "x": None}
    rows = [{"counts": 1}]
    seen = []
    first = rows[0]["counts"]
    seen.append(rows[0]["counts"])
    json.dump(face, io.open("x", "w"))
    return seen


def attribute_of_a_parameter(self):
    face = {"counts": 1, "x": None}
    seen = []
    first = self.cfg["counts"]
    seen.append(self.cfg["counts"])
    json.dump(face, io.open("x", "w"))
    return seen


def import_receiver():
    face = {"counts": 1, "x": None}
    seen = []
    first = json.FACE["counts"]
    seen.append(json.FACE["counts"])
    json.dump(face, io.open("x", "w"))
    return seen


def import_plain_receiver():
    face = {"counts": 1, "x": None}
    seen = []
    first = json["counts"]
    seen.append(json["counts"])
    json.dump(face, io.open("x", "w"))
    return seen


def unbound_receiver():
    face = {"counts": 1, "x": None}
    seen = []
    first = unknown_panel["counts"]
    seen.append(unknown_panel["counts"])
    json.dump(face, io.open("x", "w"))
    return seen


MOD = {"counts": 1}


def writes_the_module_object():
    MOD["counts"] = 9


parameter_receiver({"counts": 1})
local_receiver()
module_receiver()
container_from_a_parameter([{"counts": 1}])
container_bound_inside()
attribute_of_a_parameter(None)
import_receiver()
import_plain_receiver()
unbound_receiver()
'''


def selftest():
    legs = []
    tree = ast.parse(FIXTURE)
    graph = e622.call_graph(tree, "fixture")
    rows, inert = origin_facts(tree, "fixture", graph)

    def row_of(fn_name):
        got = [r for r in rows if r["function"] == fn_name]
        return got[0] if got else None

    def origin(fn_name):
        r = row_of(fn_name)
        return r.get("receiver_origin") if r else None

    def before(fn_name):
        r = row_of(fn_name)
        return r.get("origin_before_the_e627_interval_start") if r else None

    legs.append(("the fixture yields live dead face-key lines", len(rows) >= 8 and inert == 0))
    legs.append(("a parameter is an origin before the interval",
                 origin("parameter_receiver") == PARAM and before("parameter_receiver") is True))
    legs.append(("a local binding is an origin inside the interval",
                 origin("local_receiver") == LOCAL and before("local_receiver") is False))
    legs.append(("a module-level name is an origin before the interval",
                 origin("module_receiver") == MODULE and before("module_receiver") is True))
    legs.append(("a container off a parameter arrives from outside",
                 origin("container_from_a_parameter") == CONTAINER_OUT
                 and before("container_from_a_parameter") is True))
    legs.append(("a container bound inside the function does not",
                 origin("container_bound_inside") == CONTAINER_IN
                 and before("container_bound_inside") is False))
    legs.append(("an attribute chain off a parameter arrives from outside",
                 origin("attribute_of_a_parameter") == CONTAINER_OUT
                 and row_of("attribute_of_a_parameter").get("receiver_form") == FORM_ATTRIBUTE))
    legs.append(("an attribute chain off an import arrives from outside",
                 origin("import_receiver") == CONTAINER_OUT and before("import_receiver") is True))
    legs.append(("a plain imported name is an origin before the interval",
                 origin("import_plain_receiver") == IMPORT
                 and before("import_plain_receiver") is True))
    legs.append(("a name bound nowhere in the module does not resolve",
                 origin("unbound_receiver") == UNRESOLVED and before("unbound_receiver") is None))
    legs.append(("the receiver forms are published per row",
                 row_of("parameter_receiver").get("receiver_form") == FORM_PLAIN
                 and row_of("container_from_a_parameter").get("receiver_form") == FORM_SUBSCRIPT))
    legs.append(("a writer elsewhere in the module is found for the module object",
                 bool(row_of("module_receiver").get("base_name_written_at_the_key_outside_the_"
                                                    "interval"))))
    legs.append(("a parameter receiver has no writer in this fixture",
                 row_of("parameter_receiver").get("base_name_is_written_elsewhere") is False))

    for r in rows:
        r["module"] = "scripts/fixture.py"
    m = {"population_modules": 1, "skipped": [], "lines": rows,
         "inert_dead_facekey_lines": inert}
    c = counts_of(m)
    legs.append(("counts re-add the line rows", c["live_dead_facekey_lines"] == len(rows)))
    legs.append(("the origin classes add up to the line count",
                 sum(c["origin_" + k] for k in ORIGIN_CLASSES) == len(rows)))
    legs.append(("the open duplicates are exactly the outside-origin duplicates",
                 c["duplicates_whose_origin_lies_before_the_interval"]
                 == sum(1 for r in _duplicates(rows)
                        if r.get("origin_before_the_e627_interval_start") is True)
                 and c["duplicates_whose_origin_lies_before_the_interval"] >= 4))
    legs.append(("the container counter adds the two container forms",
                 c["rows_read_through_a_container"]
                 == c["form_" + FORM_SUBSCRIPT] + c["form_" + FORM_ATTRIBUTE]))
    face, problems = face_from(m)
    legs.append(("the fixture face has no problems", problems == []))
    bad = {"counts": dict(face["counts"]), "lines": [dict(r) for r in face["lines"]],
           "verdict": face["verdict"], "e627_cross_check": face["e627_cross_check"]}
    bad["counts"]["origin_" + PARAM] = int(bad["counts"]["origin_" + PARAM]) + 1
    legs.append(("a perturbed origin count fails face_problems", face_problems(bad) != []))
    bad2 = {"counts": dict(face["counts"]), "lines": [dict(r) for r in face["lines"]],
            "verdict": "other", "e627_cross_check": face["e627_cross_check"]}
    legs.append(("a perturbed verdict fails face_problems", face_problems(bad2) != []))
    bad3 = {"counts": dict(face["counts"]), "lines": [dict(r) for r in face["lines"]][:-1],
            "verdict": face["verdict"], "e627_cross_check": face["e627_cross_check"]}
    legs.append(("a dropped line row fails face_problems", face_problems(bad3) != []))
    flipped = [dict(r) for r in face["lines"]]
    done = False
    for r in flipped:
        if r.get("receiver_origin") == PARAM:
            r["receiver_origin"] = LOCAL
            done = True
            break
    bad4 = {"counts": dict(face["counts"]), "lines": flipped, "verdict": face["verdict"],
            "e627_cross_check": face["e627_cross_check"]}
    legs.append(("an origin silently changed without its flag fails face_problems",
                 done and face_problems(bad4) != []))

    mods, _skipped = e619.population(ROOT)
    kept = [os.path.basename(rel) for rel, _ in mods
            if os.path.basename(rel) not in (set(e622.SELF_PARTS) | set(e623.SELF_PARTS)
                                             | set(e624.SELF_PARTS) | set(e625.SELF_PARTS)
                                             | set(e626.SELF_PARTS) | set(e627.SELF_PARTS)
                                             | set(SELF_PARTS))]
    legs.append(("the real population parses and is non-empty", len(mods) > 100))
    legs.append(("this script excludes itself", "e628_receiver_origin.py" not in kept))
    real = measure(root=ROOT)
    cc = real["cross_check"]
    legs.append(("the E627 cross-check read a published face", cc.get("published") is True))
    legs.append(("the re-derived duplicate classes are the ones E627 published",
                 cc.get("agrees") is True))
    face2, problems2 = face_from(real)
    legs.append(("the built face has no problems", problems2 == []))

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
    print("population=%d lines=%d duplicates=%d open_origin=%d unresolved=%d written_elsewhere=%d"
          % (c["population_modules"], c["live_dead_facekey_lines"],
             c["same_object_duplicate_rows"],
             c["duplicates_whose_origin_lies_before_the_interval"],
             c["duplicates_whose_origin_cannot_be_resolved"],
             c["duplicates_whose_receiver_name_is_written_elsewhere"]))
    for k in ORIGIN_CLASSES:
        print("  %s=%d" % (k, c["origin_" + k]))
    print("verdict=" + face["verdict"])
    print("answer=" + face["answer"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))