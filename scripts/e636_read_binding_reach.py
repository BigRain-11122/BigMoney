"""E636 -- does a computed-key read resolve once binding REACHABILITY is decided?

E635 resolved the 12 computed-key reads E634 found and left 6 unresolved.  All six sit in one
function, all six are bound by a ``for`` target, and all six were unresolved for the same reason:
E635 UNIONED every binding of the name in the scope, so a second, non-literal loop over the same
name poisoned the first, literal one.  Unioning is a property of the instrument, not of the code.

This study replaces the union with reachability and adds the arm E635 did not have:

  * a ``for``/comprehension binding reaches the read only when the loop's own line span contains the
    read line -- a sibling loop over the same name does not;
  * an assignment reaches the read only when it sits before it (E635 already split that side);
  * a parameter reaches the read and proves nothing, which is published as its own class;
  * and, for a loop whose iterable is a fully literal sequence of tuples, the binding is enumerated
    per iteration, so ``for mult, key in ((1, "x1"), (2, "x2"))`` proves the key on exactly the
    iterations that carry it instead of landing on "could be".

Two readings are published for every row because they answer different questions: the UNION class
(what the read could be across all reaching bindings) and the ITERATION class (what it is along the
iteration that binds the counted key).  A verdict that promoted an iteration reading to an
unconditional one would be a much stronger claim than the code supports, so both are counted and
the gate is stated in terms of which one fired.

Usage:
  python scripts/e636_read_binding_reach.py run       # build the face
  python scripts/e636_read_binding_reach.py verify    # re-derive the classes from the tree
  python scripts/e636_read_binding_reach.py selftest  # offline fixture legs
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
TODAY = "2026-11-10"
FACE = "READBINDINGREACH.json"
LATEST = "readbindingreach_latest.json"
STUDY = "E636_read_binding_reach"
SELF_PARTS = {"e636_read_binding_reach.py", "run_e636_smoke_leg.py", "_probe_e636.py"}
SOURCE_FACE = "results/state_tilt/READKEYRESOLVE.json"

import e635_read_key_resolve as e635  # noqa: E402

P_KEY = e635.P_KEY
P_COULD = e635.P_COULD
P_OTHER = e635.P_OTHER
P_UNRESOLVED = e635.P_UNRESOLVED
CLASSES = [P_KEY, P_COULD, P_OTHER, P_UNRESOLVED]

R_ENCLOSES = "loop_span_contains_the_read"
R_BEFORE = "assignment_before_the_read"
R_PARAMETER = "the_key_arrives_as_a_parameter"
R_AFTER = "assignment_after_the_read"
R_ELSEWHERE = "the_binding_does_not_reach_the_read"
REACHES = [R_ENCLOSES, R_BEFORE, R_PARAMETER, R_AFTER, R_ELSEWHERE]

W_ENCLOSING_LITERAL = "the_reaching_loop_binds_a_literal"
W_ENCLOSING_NOT_LITERAL = "the_reaching_loop_binds_a_non_literal"
W_SEVERAL = "more_than_one_binding_reaches_the_read"
W_PARAMETER = "the_key_arrives_as_a_parameter"
W_NONE = "no_binding_reaches_the_read"
W_NOT_A_NAME = "the_key_expression_is_not_a_bare_name"
WHYS = [W_ENCLOSING_LITERAL, W_ENCLOSING_NOT_LITERAL, W_SEVERAL, W_PARAMETER, W_NONE,
        W_NOT_A_NAME]

V_READ_ALONG_A_PATH = ("the_counted_key_is_read_after_the_dead_line_along_the_iteration_of_the_"
                       "enclosing_loop_that_binds_it_so_the_after_side_zero_is_unconditional_only")
V_COULD_ALONG_A_PATH = ("the_after_side_reads_could_be_the_counted_key_on_some_path_but_no_literal_"
                        "loop_enumerates_it")
V_FOLDED_OUT = ("every_after_side_unresolved_read_names_a_member_id_and_the_read_that_does_name_the_"
                "counted_key_at_that_location_sits_one_level_below_the_receiver_and_was_never_"
                "censused_so_the_after_side_zero_is_about_the_population")
V_STILL_UNRESOLVED = ("the_after_side_stays_unresolved_and_at_least_one_of_those_locations_carries_"
                      "no_read_of_the_counted_key_below_the_receiver")
V_OTHER_ON_EVERY_PATH = ("every_after_side_read_resolves_to_another_key_on_every_path_so_the_"
                         "after_side_zero_stands")


# ---------------------------------------------------------------- helpers
def say(line):
    sys.stdout.write(line + "\n")


# ---------------------------------------------------------------- bindings and reach
def candidate_bindings(scope, name):
    """Every binding of ``name`` in the scope with its span, in document order.

    ``e635.bindings_for`` answers the same question but drops the node, so it cannot say whether a
    loop contains the read.  The kinds are kept identical so the two faces are comparable.
    """
    out = []
    for node in ast.walk(scope):
        kind, expr, literal = None, None, None
        if isinstance(node, ast.Assign):
            if any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
                kind, expr = e635.B_ASSIGNMENT, node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            if isinstance(node.target, ast.Name) and node.target.id == name:
                kind, expr = e635.B_ASSIGNMENT, node.value
        elif isinstance(node, ast.AugAssign):
            if isinstance(node.target, ast.Name) and node.target.id == name:
                kind, expr = e635.B_ASSIGNMENT, None
        elif isinstance(node, ast.withitem) and node.optional_vars is not None:
            if isinstance(node.optional_vars, ast.Name) and node.optional_vars.id == name:
                kind, expr = e635.B_ASSIGNMENT, node.context_expr
        elif isinstance(node, (ast.For, ast.AsyncFor, ast.comprehension)):
            if isinstance(node.target, ast.Name) and node.target.id == name:
                kind, expr = e635.B_LOOP, node.iter
                literal, _ = e635.literal_values(node.iter)
            elif isinstance(node.target, (ast.Tuple, ast.List)):
                vals, known = e635.unpacked_values(node.target, node.iter, name)
                if known:
                    kind, expr, literal = e635.B_LOOP, node.iter, vals
        if kind is None:
            continue
        out.append({"kind": kind, "expr": expr, "literal_values": literal,
                    "lineno": getattr(node, "lineno", None),
                    "end_lineno": getattr(node, "end_lineno", getattr(node, "lineno", None))})
    args = getattr(scope, "args", None)
    if args is not None:
        names = [a.arg for a in (list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs))]
        names += [a.arg for a in (args.vararg, args.kwarg) if a is not None]
        if name in names:
            out.append({"kind": e635.B_PARAMETER, "expr": None, "literal_values": None,
                        "lineno": getattr(scope, "lineno", None),
                        "end_lineno": getattr(scope, "lineno", None)})
    out.sort(key=lambda b: (b["lineno"] or 0))
    return out


def reach_of(binding, read_line):
    if binding["kind"] == e635.B_PARAMETER:
        return R_PARAMETER
    line = binding["lineno"]
    end = binding["end_lineno"] or line
    if line is None or read_line is None:
        return R_ELSEWHERE
    if binding["kind"] == e635.B_LOOP:
        return R_ENCLOSES if line <= read_line <= end else R_ELSEWHERE
    if line < read_line:
        return R_BEFORE
    if line == read_line:
        return R_BEFORE
    return R_AFTER


def union_class(bindings, module_consts, key):
    """What the read could be across every binding that reaches it."""
    reaching = [b for b in bindings if b["reach"] != R_ELSEWHERE and b["reach"] != R_AFTER]
    if not reaching:
        return P_UNRESOLVED, W_NONE, [], []
    if any(b["reach"] == R_PARAMETER for b in reaching):
        return P_UNRESOLVED, W_PARAMETER, [], []
    vals, unknown = set(), False
    for b in reaching:
        bvals, known = e635.values_of(b["expr"], module_consts)
        if b["literal_values"]:
            bvals, known = set(b["literal_values"]), True
        vals |= bvals
        if not known:
            unknown = True
    if unknown:
        return P_UNRESOLVED, W_ENCLOSING_NOT_LITERAL, [], sorted(vals)
    if vals == {key}:
        return P_KEY, W_ENCLOSING_LITERAL, reaching, sorted(vals)
    if key in vals:
        cls, why = P_COULD, W_SEVERAL if len(reaching) > 1 else W_ENCLOSING_LITERAL
        return cls, why, reaching, sorted(vals)
    return P_OTHER, W_ENCLOSING_LITERAL if len(reaching) == 1 else W_SEVERAL, reaching, sorted(vals)


def iteration_class(bindings, module_consts, key):
    """What the read IS along the iteration of the enclosing literal loop that binds the key.

    ``(class, iterations_binding_the_key, iterations_enumerated)``.  A loop whose iterable is not
    fully literal cannot be enumerated and answers (unresolved, 0, 0) -- it is not a zero, it is an
    instrument limit, which is exactly the distinction this study exists to publish.
    """
    loops = [b for b in bindings if b["reach"] == R_ENCLOSES]
    if not loops:
        return P_UNRESOLVED, 0, 0
    best = (P_UNRESOLVED, 0, 0)
    for b in loops:
        vals, known = e635.values_of(b["expr"], module_consts)
        if b["literal_values"]:
            vals, known = set(b["literal_values"]), True
        if not known:
            # a loop over a computed set is not an enumeration: it can only say the key is among
            # the values it already knows, which is 'could be' and never 'is'
            if vals and key in vals and best[0] == P_UNRESOLVED:
                best = (P_COULD, 1, len(vals))
            continue
        if not vals:
            continue
        hits = sum(1 for v in vals if v == key)
        if hits:
            # along the iteration that binds the counted key the read IS that key; how many
            # iterations carry it is published beside the class, not folded into it
            return (P_KEY, hits, len(vals))
        if best[0] != P_KEY and best[0] != P_COULD:
            best = (P_OTHER, 0, len(vals))
    return best


def resolve_row(expr, scope, module_consts, key, read_line):
    """One computed-key read under the reachability instrument."""
    if expr is None:
        return {"union_class": P_UNRESOLVED, "why": W_NONE, "bindings": [],
                "union_values": [], "iteration_class": P_UNRESOLVED,
                "iterations_binding_the_key": 0, "iterations_enumerated": 0}
    if not isinstance(expr, ast.Name):
        vals, known = e635.values_of(expr, module_consts)
        if not known:
            return {"union_class": P_UNRESOLVED, "why": W_NOT_A_NAME, "bindings": [],
                    "union_values": [], "iteration_class": P_UNRESOLVED,
                    "iterations_binding_the_key": 0, "iterations_enumerated": 0}
        cls = P_KEY if vals == {key} else (P_COULD if key in vals else P_OTHER)
        return {"union_class": cls, "why": W_ENCLOSING_LITERAL, "bindings": [],
                "union_values": sorted(vals), "iteration_class": cls,
                "iterations_binding_the_key": 1 if key in vals else 0,
                "iterations_enumerated": len(vals)}
    name = expr.id
    if name in module_consts:
        vals = set(module_consts[name])
        cls = P_KEY if vals == {key} else (P_COULD if key in vals else P_OTHER)
        return {"union_class": cls, "why": W_ENCLOSING_LITERAL, "bindings": [],
                "union_values": sorted(vals), "iteration_class": cls,
                "iterations_binding_the_key": 1 if key in vals else 0,
                "iterations_enumerated": len(vals)}
    bindings = candidate_bindings(scope, name)
    for b in bindings:
        b["reach"] = reach_of(b, read_line)
    ucls, why, reaching, vals = union_class(bindings, module_consts, key)
    icls, hits, total = iteration_class(bindings, module_consts, key)
    return {"union_class": ucls, "why": why,
            "bindings": [{"kind": b["kind"], "reach": b["reach"], "line": b["lineno"],
                          "values": (sorted(b["literal_values"]) if b["literal_values"] else [])}
                         for b in bindings],
            "union_values": vals,
            "iteration_class": icls,
            "iterations_binding_the_key": hits,
            "iterations_enumerated": total}


# ---------------------------------------------------------------- measure
def measure(root=ROOT):
    source = json.load(io.open(os.path.join(root, SOURCE_FACE), encoding="utf-8"))
    cache, rows, unparsed = {}, [], 0
    for r in source.get("rows") or []:
        module = r.get("module")
        key = r.get("key")
        dead = r.get("dead_line")
        read_line = r.get("read_line")
        if module not in cache:
            try:
                with io.open(os.path.join(root, module), encoding="utf-8") as fh:
                    cache[module] = ast.parse(fh.read(), filename=module)
            except Exception:
                cache[module] = None
        tree = cache[module]
        if tree is None:
            unparsed += 1
            continue
        scope = e635.innermost(e635.function_nodes(tree), dead, r.get("function"))
        if scope is None:
            unparsed += 1
            continue
        consts = e635.module_constants(tree)
        roots = e635.receiver_roots(scope, key, read_line)
        sites = [s for s in e635.computed_reads_in(scope, roots)
                 if getattr(s["node"], "lineno", None) == r.get("line")
                 and getattr(s["node"], "col_offset", None) == r.get("column")]
        # a chained subscript (``d[k1][k2]``) puts two read sites on ONE (line, column) and neither
        # E634 nor E635 could tell them apart by that signature.  Both are examined here and the
        # strongest class wins, with the number of sites and each key expression published so the
        # tie-break is visible instead of implied.
        read_line = r.get("line")
        cands = []
        for site in sites:
            sexpr = e635.key_expression_of(site, site["node"])
            res = resolve_row(sexpr, scope, consts, key, read_line)
            res["key_expression"] = (sexpr.id if isinstance(sexpr, ast.Name)
                                     else ast.dump(sexpr)[:60] if sexpr is not None else None)
            cands.append(res)
        if not cands:
            res = resolve_row(None, scope, consts, key, read_line)
            res["key_expression"] = None
            cands = [res]
        order = {P_KEY: 0, P_COULD: 1, P_OTHER: 2, P_UNRESOLVED: 3}
        res = sorted(cands, key=lambda x: order.get(x["iteration_class"], 4))[0]
        # the same (line, column) can also carry a read the classifier shelves as "below the
        # receiver": a chained subscript reads one container inside the one the row is about, and
        # E633 folds it out of the census.  It is published here because "this location does not
        # read the key" and "the read of the key at this location was folded out" are different
        # claims and only one of them is about the code.
        below = []
        import e633_read_forms as e633  # noqa: E402  (local: only this arm needs it)
        for s in e633.access_sites(list(ast.walk(scope)), r.get("line"), roots):
            if getattr(s["node"], "col_offset", None) != r.get("column"):
                continue
            if e633.classify(s, None, set()) != e633.R_BELOW:
                continue
            sl = s["node"].slice if isinstance(s["node"], ast.Subscript) else None
            if isinstance(sl, ast.Name):
                below.append(sl.id)
            elif isinstance(sl, ast.Constant) and isinstance(sl.value, str):
                below.append(sl.value)
            elif sl is not None:
                below.append(ast.dump(sl)[:60])
        rows.append({
            "module": module, "function": r.get("function"), "key": key,
            "dead_line": dead, "read_line": read_line,
            "line": r.get("line"), "column": r.get("column"),
            "side": r.get("side"),
            "form": r.get("form"),
            "e635_class": r.get("class"),
            "e635_binding_kind": r.get("binding_kind"),
            "union_class": res["union_class"],
            "iteration_class": res["iteration_class"],
            "why": res["why"],
            "bindings": res["bindings"],
            "union_values": res["union_values"],
            "iterations_binding_the_key": res["iterations_binding_the_key"],
            "iterations_enumerated": res["iterations_enumerated"],
            "key_expression": res.get("key_expression"),
            "sites_at_this_location": len(cands),
            "key_expressions_at_this_location": sorted(
                {c.get("key_expression") for c in cands if c.get("key_expression")}),
            "below_the_receiver_at_this_location": below,
        })
    return {"rows": rows, "unparsed": unparsed,
            "source_verdict": source.get("verdict"),
            "source_rows": len(source.get("rows") or [])}


def counts_of(rows):
    by_union = {c: 0 for c in CLASSES}
    by_iter = {c: 0 for c in CLASSES}
    by_why = {w: 0 for w in WHYS}
    by_side = {s: {c: 0 for c in CLASSES} for s in ("before", "at_the_dead_line", "after")}
    moved = []
    for r in rows:
        by_union[r["union_class"]] = by_union.get(r["union_class"], 0) + 1
        by_iter[r["iteration_class"]] = by_iter.get(r["iteration_class"], 0) + 1
        by_why[r["why"]] = by_why.get(r["why"], 0) + 1
        side = r.get("side")
        if side in by_side:
            by_side[side][r["iteration_class"]] = by_side[side].get(r["iteration_class"], 0) + 1
        if r.get("e635_class") != r["iteration_class"]:
            moved.append({"module": r.get("module"), "line": r.get("line"), "key": r.get("key"),
                          "side": side, "from": r.get("e635_class"),
                          "to": r["iteration_class"], "union": r["union_class"],
                          "why": r["why"]})
    after_rows = [r for r in rows if r.get("side") == "after"]
    after_unresolved = [r for r in after_rows if r["iteration_class"] == P_UNRESOLVED]
    after_folded = [r for r in after_unresolved
                    if r.get("key") and r.get("key") in
                    (r.get("below_the_receiver_at_this_location") or [])]
    return {
        "rows": len(rows),
        "by_union_class": by_union,
        "by_iteration_class": by_iter,
        "by_why": by_why,
        "by_side_iteration": by_side,
        "after_the_dead_line": sum(by_side["after"].values()),
        "after_the_dead_line_proven_along_a_path": by_side["after"].get(P_KEY, 0),
        "after_the_dead_line_could_be_along_a_path": by_side["after"].get(P_COULD, 0),
        "after_the_dead_line_other_along_every_path": by_side["after"].get(P_OTHER, 0),
        "after_the_dead_line_still_unresolved": by_side["after"].get(P_UNRESOLVED, 0),
        "after_the_dead_line_unresolved_whose_location_reads_the_key_below_the_receiver":
            len(after_folded),
        "rows_whose_location_reads_the_counted_key_below_the_receiver":
            sum(1 for r in rows
                if r.get("key") and r.get("key") in
                (r.get("below_the_receiver_at_this_location") or [])),
        "below_the_receiver_key_expressions": sorted(
            {e for r in rows for e in (r.get("below_the_receiver_at_this_location") or [])
             if isinstance(e, str)}),
        "rows_moved_against_e635": len(moved),
        "moved": moved,
        "iterations_binding_the_key": sum(r["iterations_binding_the_key"] for r in rows),
        "iterations_enumerated": sum(r["iterations_enumerated"] for r in rows),
    }


def decide(c):
    if c["after_the_dead_line_proven_along_a_path"] > 0:
        return V_READ_ALONG_A_PATH
    if c["after_the_dead_line_could_be_along_a_path"] > 0:
        return V_COULD_ALONG_A_PATH
    if c["after_the_dead_line_still_unresolved"] > 0:
        if (c["after_the_dead_line_unresolved_whose_location_reads_the_key_below_the_receiver"]
                == c["after_the_dead_line_still_unresolved"]):
            return V_FOLDED_OUT
        return V_STILL_UNRESOLVED
    return V_OTHER_ON_EVERY_PATH


def answer_of(c):
    return ("Of E635's %d row(s), %d change class once binding reachability replaces the union of "
            "every same-named binding in the scope.  Along the iteration of the enclosing literal "
            "loop that binds the counted key: %d are proven to be that key, %d could be, %d are "
            "another key and %d stay unresolved.  On the after side of the dead line that is %d "
            "proven / %d could-be / %d other / %d unresolved, over %d enumerated iteration(s) of "
            "which %d carry the key.  %d of the %d after-side unresolved location(s) do read the "
            "counted key -- one level below the receiver (%s), where E633's classifier folds the "
            "read out of the census instead of counting it."
            % (c["rows"], c["rows_moved_against_e635"],
               c["by_iteration_class"][P_KEY], c["by_iteration_class"][P_COULD],
               c["by_iteration_class"][P_OTHER], c["by_iteration_class"][P_UNRESOLVED],
               c["after_the_dead_line_proven_along_a_path"],
               c["after_the_dead_line_could_be_along_a_path"],
               c["after_the_dead_line_other_along_every_path"],
               c["after_the_dead_line_still_unresolved"],
               c["iterations_enumerated"], c["iterations_binding_the_key"],
               c["after_the_dead_line_unresolved_whose_location_reads_the_key_below_the_receiver"],
               c["after_the_dead_line_still_unresolved"],
               ", ".join(c["below_the_receiver_key_expressions"]) or "-"))


# ---------------------------------------------------------------- face
def face_from(m):
    c = counts_of(m["rows"])
    return {
        "study": STUDY,
        "script": "scripts/e636_read_binding_reach.py",
        "card": "E636",
        "evidence_cutoff": TODAY,
        "dept": "研究",
        "method": ("each computed-key read of %s is re-decided under two readings: the UNION class "
                   "over every binding that reaches the read (a for/comprehension binding reaches "
                   "only if its own line span contains the read line; an assignment reaches only if "
                   "it sits before it), and the ITERATION class, which enumerates the enclosing loop "
                   "when its iterable is a fully literal sequence and answers what the key is on the "
                   "iteration that binds it" % SOURCE_FACE),
        "population_source": ("the %d published row(s) of %s (E635), one per distinct computed-key "
                              "read site" % (m["source_rows"], SOURCE_FACE)),
        "source_face": SOURCE_FACE,
        "source_verdict": m["source_verdict"],
        "counts": c,
        "rows": m["rows"],
        "limits": [
            "reachability is intra-procedural and syntactic: a loop that reassigns the name inside "
            "its body, or a binding reached through a helper, is not modelled",
            "the iteration class enumerates only a fully literal iterable; anything else answers "
            "unresolved, and unresolved is published as an instrument limit, never as a zero",
            "the iteration class is a per-path statement: a row proven there is NOT proven "
            "unconditionally, and the two counts are published separately for that reason",
            "no runner and no fixture write: this study reads source and E635's published rows",
        ],
        "verdict": decide(c),
        "answer": answer_of(c),
    }


def face_problems(face):
    """Everything the smoke leg refuses, derived from the face's own rows."""
    problems = []
    if not face:
        return ["face is absent or empty"]
    rows = face.get("rows") or []
    c = face.get("counts") or {}
    live = counts_of(rows)
    for key in ("rows", "by_union_class", "by_iteration_class", "by_why",
                "after_the_dead_line", "after_the_dead_line_proven_along_a_path",
                "after_the_dead_line_unresolved_whose_location_reads_the_key_below_the_receiver",
                "rows_moved_against_e635", "iterations_binding_the_key"):
        if c.get(key) != live.get(key):
            problems.append("counts.%s does not re-add from the rows" % key)
    for r in rows:
        if r.get("union_class") not in CLASSES:
            problems.append("row %s:%s carries union class %r"
                            % (r.get("module"), r.get("line"), r.get("union_class")))
            break
        if r.get("iteration_class") not in CLASSES:
            problems.append("row %s:%s carries iteration class %r"
                            % (r.get("module"), r.get("line"), r.get("iteration_class")))
            break
        if r.get("why") not in WHYS:
            problems.append("row %s:%s carries reason %r"
                            % (r.get("module"), r.get("line"), r.get("why")))
            break
        if r.get("iteration_class") == P_KEY and not r.get("iterations_binding_the_key"):
            problems.append("row %s:%s is proven along a path but enumerates no such iteration"
                            % (r.get("module"), r.get("line")))
            break
        if r.get("side") == "after" and r.get("iteration_class") == P_KEY and \
                r.get("union_class") == P_UNRESOLVED and r.get("why") != W_SEVERAL:
            problems.append("row %s:%s is proven per path while its union is unresolved for a "
                            "reason that is not 'several bindings reach it'"
                            % (r.get("module"), r.get("line")))
            break
    if decide(c) != face.get("verdict"):
        problems.append("the published verdict is not the one the counts force")
    if rows and c.get("iterations_enumerated", 0) == 0 and \
            c.get("by_iteration_class", {}).get(P_UNRESOLVED, 0) != len(rows):
        problems.append("the census enumerated no iteration yet does not report every row unresolved")
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
    say("run: rows=%d moved=%d proven=%d could=%d other=%d unresolved=%d"
        % (c["rows"], c["rows_moved_against_e635"], c["by_iteration_class"][P_KEY],
           c["by_iteration_class"][P_COULD], c["by_iteration_class"][P_OTHER],
           c["by_iteration_class"][P_UNRESOLVED]))
    say("run: after_side proven=%d could=%d other=%d unresolved=%d"
        % (c["after_the_dead_line_proven_along_a_path"],
           c["after_the_dead_line_could_be_along_a_path"],
           c["after_the_dead_line_other_along_every_path"],
           c["after_the_dead_line_still_unresolved"]))
    say("run: verdict=%s" % doc["verdict"])
    return doc


def verify(root=ROOT):
    problems = []
    path = os.path.join(OUTDIR, FACE)
    if not os.path.exists(path):
        say("verify problems=['face is absent']")
        return ["face is absent"]
    with io.open(path, encoding="utf-8") as fh:
        face = json.load(fh)
    if face.get("evidence_cutoff") != TODAY:
        problems.append("evidence_cutoff moved")
    problems.extend(face_problems(face))
    live = measure(root)
    live_rows = {(r["module"], r["line"], r["column"], r["key"]): r for r in live["rows"]}
    for r in face.get("rows") or []:
        sig = (r.get("module"), r.get("line"), r.get("column"), r.get("key"))
        if sig not in live_rows:
            problems.append("row %s:%s is no longer a computed-key read in the tree" % sig[:2])
            break
        if live_rows[sig]["iteration_class"] != r.get("iteration_class"):
            problems.append("row %s:%s reads %s in the face, the tree now reads %s"
                            % (sig[0], sig[1], r.get("iteration_class"),
                               live_rows[sig]["iteration_class"]))
            break
    say("verify problems=%s" % (problems or "[]"))
    return problems


# ---------------------------------------------------------------- selftest
FIXTURE = '''\
KEYS = ("x1", "x2")


def two_loops(m):
    out = []
    for mult, k in ((1, "x1"), (2, "x2")):
        pass
    dead = m["x1"]
    for mult, k in ((1, "x1"), (2, "x2")):
        out.append(m[k])
    return dead, out


def sibling_non_literal(m, names):
    for k in names:
        pass
    dead = m["x1"]
    out = []
    for k in names:
        out.append(m[k])
    return dead, out


def only_one_iteration(m):
    dead = m["x1"]
    out = []
    for k in ("x1", "x2", "x3"):
        out.append(m[k])
    return dead, out


def not_the_key(m):
    dead = m["x1"]
    out = []
    for k in ("x2", "x3"):
        out.append(m[k])
    return dead, out


def parameter(m, k):
    dead = m["x1"]
    return dead, m[k]
'''


def _fixture_rows(text=FIXTURE):
    tree = ast.parse(text)
    consts = e635.module_constants(tree)
    funcs = {n.name: n for n in e635.function_nodes(tree)}
    out = []
    for name, fn in funcs.items():
        dead = None
        for node in ast.walk(fn):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Subscript):
                sl = node.value.slice
                if isinstance(sl, ast.Constant) and sl.value == "x1":
                    dead = node.lineno
                    break
        if dead is None:
            dead = fn.lineno
        for site in e635.computed_reads_in(fn, {"m"}):
            node = site["node"]
            expr = e635.key_expression_of(site, node)
            res = resolve_row(expr, fn, consts, "x1", node.lineno)
            res["function"] = name
            res["line"] = node.lineno
            res["side"] = e635.side_of(node.lineno, dead)
            out.append(res)
    return out


def selftest():
    legs = []

    def leg(name, ok, note=""):
        legs.append((name, bool(ok), note))

    rows = _fixture_rows()
    by_fn = {}
    for r in rows:
        by_fn.setdefault(r["function"], []).append(r)

    two = by_fn["two_loops"][0]
    leg("a_sibling_loop_before_the_read_does_not_reach_it", len(two["bindings"]) == 2,
        str(len(two["bindings"])))
    leg("the_enclosing_loop_is_the_binding_that_reaches",
        [b["reach"] for b in two["bindings"]].count(R_ENCLOSES) == 1,
        str([b["reach"] for b in two["bindings"]]))
    leg("the_other_loop_is_published_as_not_reaching",
        [b["reach"] for b in two["bindings"]].count(R_ELSEWHERE) == 1,
        str([b["reach"] for b in two["bindings"]]))
    leg("a_literal_loop_enumerates_the_iteration_that_binds_the_key",
        two["iteration_class"] == P_KEY and two["iterations_binding_the_key"] == 1
        and two["iterations_enumerated"] == 2,
        "%s %d/%d" % (two["iteration_class"], two["iterations_binding_the_key"],
                      two["iterations_enumerated"]))
    leg("the_union_of_two_iterations_is_only_could_be", two["union_class"] == P_COULD,
        two["union_class"])

    sib = by_fn["sibling_non_literal"][0]
    leg("a_non_literal_sibling_loop_no_longer_poisons_the_read",
        sib["why"] == W_ENCLOSING_NOT_LITERAL,
        "%s %s" % (sib["iteration_class"], sib["why"]))
    leg("the_poisoning_sibling_is_published_as_not_reaching",
        [b["reach"] for b in sib["bindings"]].count(R_ELSEWHERE) == 1,
        str([b["reach"] for b in sib["bindings"]]))

    one = by_fn["only_one_iteration"][0]
    leg("a_partial_literal_loop_proves_the_iteration_that_binds_it",
        one["iteration_class"] == P_KEY, one["iteration_class"])
    leg("a_partial_literal_loop_publishes_its_one_hit_of_three",
        one["iterations_binding_the_key"] == 1 and one["iterations_enumerated"] == 3,
        "%d/%d" % (one["iterations_binding_the_key"], one["iterations_enumerated"]))

    other = by_fn["not_the_key"][0]
    leg("a_loop_that_never_binds_the_key_is_proven_other", other["iteration_class"] == P_OTHER,
        other["iteration_class"])

    par = by_fn["parameter"][0]
    leg("a_parameter_is_not_a_loop_and_stays_unresolved",
        par["iteration_class"] == P_UNRESOLVED and par["why"] == W_PARAMETER,
        "%s %s" % (par["iteration_class"], par["why"]))

    # by_side / gate
    c = counts_of([{"union_class": P_COULD, "iteration_class": P_KEY, "why": W_ENCLOSING_LITERAL,
                    "side": "after", "iterations_binding_the_key": 1,
                    "iterations_enumerated": 2, "e635_class": P_UNRESOLVED},
                   {"union_class": P_UNRESOLVED, "iteration_class": P_UNRESOLVED,
                    "why": W_NONE, "side": "after", "iterations_binding_the_key": 0,
                    "iterations_enumerated": 0, "e635_class": P_UNRESOLVED}])
    leg("the_side_table_splits_the_iteration_class", c["by_side_iteration"]["after"][P_KEY] == 1
        and c["by_side_iteration"]["after"][P_UNRESOLVED] == 1, str(c["by_side_iteration"]))
    leg("gate_prefers_a_proven_path", decide(c) == V_READ_ALONG_A_PATH, decide(c))
    leg("moved_rows_are_published", c["rows_moved_against_e635"] == 1,
        str(c["rows_moved_against_e635"]))
    c2 = counts_of([{"union_class": P_COULD, "iteration_class": P_COULD, "why": W_SEVERAL,
                     "side": "after", "iterations_binding_the_key": 1,
                     "iterations_enumerated": 3, "e635_class": P_UNRESOLVED}])
    leg("gate_does_not_promote_could_be", decide(c2) == V_COULD_ALONG_A_PATH, decide(c2))
    c3 = counts_of([{"union_class": P_OTHER, "iteration_class": P_OTHER,
                     "why": W_ENCLOSING_LITERAL, "side": "after",
                     "iterations_binding_the_key": 0, "iterations_enumerated": 2,
                     "e635_class": P_OTHER}])
    leg("gate_elsewhere_when_every_path_is_another_key", decide(c3) == V_OTHER_ON_EVERY_PATH,
        decide(c3))

    # an unresolved after side is not "another key": it is either a population story (the key is read
    # one level below the receiver) or an honest instrument limit, and the two are different verdicts
    c4 = counts_of([{"union_class": P_UNRESOLVED, "iteration_class": P_UNRESOLVED, "why": W_NONE,
                     "side": "after", "key": "x1", "iterations_binding_the_key": 0,
                     "iterations_enumerated": 0, "e635_class": P_UNRESOLVED,
                     "below_the_receiver_at_this_location": ["x1"]}])
    leg("an_unresolved_after_side_is_not_promoted_to_another_key",
        decide(c4) != V_OTHER_ON_EVERY_PATH, decide(c4))
    leg("a_below_the_receiver_read_of_the_key_makes_it_a_population_story",
        decide(c4) == V_FOLDED_OUT, decide(c4))
    c5 = counts_of([{"union_class": P_UNRESOLVED, "iteration_class": P_UNRESOLVED, "why": W_NONE,
                     "side": "after", "key": "x1", "iterations_binding_the_key": 0,
                     "iterations_enumerated": 0, "e635_class": P_UNRESOLVED,
                     "below_the_receiver_at_this_location": []}])
    leg("without_that_read_the_after_side_is_honestly_unresolved",
        decide(c5) == V_STILL_UNRESOLVED, decide(c5))

    # a zero census may not be published as a measurement
    leg("a_census_that_enumerates_nothing_reports_every_row_unresolved",
        counts_of([{"union_class": P_UNRESOLVED, "iteration_class": P_UNRESOLVED,
                    "why": W_NONE, "side": "after", "iterations_binding_the_key": 0,
                    "iterations_enumerated": 0, "e635_class": P_UNRESOLVED}])
        ["by_iteration_class"][P_UNRESOLVED] == 1)

    passed = sum(1 for _, ok, _ in legs if ok)
    for name, ok, note in legs:
        say("  %-58s %s%s" % (name, "PASS" if ok else "FAIL", ("  " + note) if note and not ok else ""))
    say("selftest %d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "selftest"
    if cmd == "run":
        build()
        return 0
    if cmd == "verify":
        return 0 if not verify() else 1
    if cmd == "selftest":
        return selftest()
    say("usage: %s [run|verify|selftest]" % os.path.basename(argv[0]))
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))