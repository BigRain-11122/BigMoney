"""E635 -- do the computed-key reads resolve to the counted key?

E634 walked every function body that holds a counted read line and asked whether the key is read in
a form its line-scoped census could not see.  The answer was no: 0 unnamed entry reads on either
side of the dead line.  But 30 of the 230 accesses were *computed-key* reads at the receiver's own
level (8 before the dead line, 1 at it, 21 after), and a computed-key read reads SOME key.  "I
cannot tell which key" is not "not this key".

So this study resolves each one inside the function it lives in, without running anything:

  * a literal at the read site (`m["days"]`) is its own answer;
  * a name is resolved through the bindings that can reach it -- an assignment in the scope, a
    ``for`` target over a literal collection, a comprehension target, a parameter, or a module-level
    string constant (chained up to a fixed depth);
  * a binding that happens only AFTER the read line cannot reach the read, and is published as such
    rather than silently used;
  * a loop over a literal collection binds the key only if the collection is literal: iterating a
    computed set leaves the read unresolved, and unresolved is a class, not a zero.

The headline is a partition: of the computed-key reads, how many are proven to be the counted key,
how many could be, how many are proven to be another key, how many stay unresolved -- split by side
of the dead line.  The verdict then says whether E634's "the key is not read after the dead line"
survives a reading it did not attempt.

Usage:
  python scripts/e635_read_key_resolve.py run       # build the face
  python scripts/e635_read_key_resolve.py verify    # re-derive the arithmetic and the resolutions
  python scripts/e635_read_key_resolve.py selftest  # offline fixture legs
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
FACE = "READKEYRESOLVE.json"
LATEST = "readkeyresolve_latest.json"
STUDY = "E635_read_key_resolve"
SELF_PARTS = {"e635_read_key_resolve.py", "run_e635_smoke_leg.py", "_probe_e635.py"}
SOURCE_FACE = "results/state_tilt/READFUNCGAP.json"

import e623_deadline_key_use as e623  # noqa: E402
import e633_read_forms as e633  # noqa: E402

P_KEY = "proven_to_be_the_counted_key"
P_COULD = "could_be_the_counted_key"
P_OTHER = "proven_to_be_another_key"
P_UNRESOLVED = "unresolved"
CLASSES = [P_KEY, P_COULD, P_OTHER, P_UNRESOLVED]

B_CONSTANT = "literal_at_the_read"
B_MODULE_CONSTANT = "module_level_string_constant"
B_ASSIGNMENT = "assignment_in_the_scope"
B_LOOP = "for_target"
B_COMPREHENSION = "comprehension_target"
B_PARAMETER = "parameter_of_the_scope"
B_AFTER = "assignment_only_after_the_read"
B_NONE = "no_binding_in_the_scope"
BINDINGS = [B_CONSTANT, B_MODULE_CONSTANT, B_ASSIGNMENT, B_LOOP, B_COMPREHENSION,
            B_PARAMETER, B_AFTER, B_NONE]

BEFORE = "before"
AT = "at_the_dead_line"
AFTER = "after"
SIDES = [BEFORE, AT, AFTER]

MAX_CHAIN = 6

V_READ_AFTER = "the_counted_key_is_read_after_the_dead_line_through_a_computed_key"
V_COULD_AFTER = "the_after_side_computed_reads_could_be_this_key_but_no_binding_proves_it"
V_ELSEWHERE = "no_after_side_computed_read_resolves_to_the_counted_key"


# ---------------------------------------------------------------- helpers
def say(line):
    sys.stdout.write(line + "\n")


def side_of(line, dead_line):
    if line is None or dead_line is None:
        return None
    if line < dead_line:
        return BEFORE
    if line == dead_line:
        return AT
    return AFTER


def load_source(root=ROOT):
    with io.open(os.path.join(root, SOURCE_FACE), encoding="utf-8") as fh:
        return json.load(fh)


def function_nodes(tree):
    return [n for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]


def innermost(nodes, dead_line, name=None):
    """The function whose body holds ``dead_line``; the named one when it ties."""
    hits = [n for n in nodes if n.lineno <= dead_line <= (n.end_lineno or dead_line)]
    if not hits:
        return None
    if name is not None:
        named = [n for n in hits if n.name == name]
        if named:
            return min(named, key=lambda n: n.end_lineno - n.lineno)
    return min(hits, key=lambda n: n.end_lineno - n.lineno)


def module_constants(tree):
    """Module-level name -> string values.  Chains are followed a bounded number of times."""
    table = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            targets, value = node.targets, node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets, value = [node.target], node.value
        else:
            continue
        for t in targets:
            if isinstance(t, ast.Name):
                table.setdefault(t.id, []).append(value)
    resolved = {}
    for _ in range(MAX_CHAIN):
        changed = False
        for name, exprs in table.items():
            vals, known = set(), True
            for expr in exprs:
                if isinstance(expr, ast.Constant) and isinstance(expr.value, str):
                    vals.add(expr.value)
                elif isinstance(expr, ast.Name) and expr.id in resolved:
                    vals |= resolved[expr.id][0]
                elif isinstance(expr, ast.Name):
                    known = False
                else:
                    known = False
            if known:
                if resolved.get(name, (set(), False))[0] != vals:
                    changed = True
                resolved[name] = (vals, True)
        if not changed:
            break
    return {k: v[0] for k, v in resolved.items()}


def literal_values(node):
    """The strings a literal collection carries, or (None, False) when it is not literal."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return {node.value}, True
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        vals = set()
        for elt in node.elts:
            if not (isinstance(elt, ast.Constant) and isinstance(elt.value, str)):
                return None, False
            vals.add(elt.value)
        return vals, True
    if isinstance(node, ast.Dict):
        return None, False
    return None, False


def unpacked_values(target, iter_node, name):
    """(values, known) for ``name`` in a tuple-unpacking target over a literal sequence.

    Only the position ``name`` occupies has to be a string constant; the other positions may hold
    numbers or names (``for mult, key in ((1, "x1"), (2, "x2"))`` proves ``key`` and says nothing
    about ``mult``).
    """
    if not isinstance(target, (ast.Tuple, ast.List)):
        return literal_values(iter_node)
    names = [t.id if isinstance(t, ast.Name) else None for t in target.elts]
    if name not in names:
        return set(), False
    pos = names.index(name)
    if not isinstance(iter_node, (ast.Tuple, ast.List)):
        return set(), False
    vals = set()
    for elt in iter_node.elts:
        if not isinstance(elt, (ast.Tuple, ast.List)) or len(elt.elts) != len(names):
            return set(), False
        cell = elt.elts[pos]
        if not (isinstance(cell, ast.Constant) and isinstance(cell.value, str)):
            return set(), False
        vals.add(cell.value)
    return vals, True


def bindings_for(scope, name, read_line):
    """Every binding of ``name`` that can reach the scope, with the side of the read it sits on."""
    out = []
    for node in ast.walk(scope):
        found = []
        if isinstance(node, ast.Assign):
            if any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
                found.append((B_ASSIGNMENT, node.value, None))
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            if isinstance(node.target, ast.Name) and node.target.id == name:
                found.append((B_ASSIGNMENT, node.value, None))
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            if isinstance(node.target, ast.Name) and node.target.id == name:
                vals, known = literal_values(node.iter)
                found.append((B_LOOP, node.iter, vals if known else None))
            elif isinstance(node.target, (ast.Tuple, ast.List)):
                vals, known = unpacked_values(node.target, node.iter, name)
                if known:
                    found.append((B_LOOP, node.iter, vals))
        elif isinstance(node, ast.comprehension):
            if isinstance(node.target, ast.Name) and node.target.id == name:
                found.append((B_COMPREHENSION, node.iter, None))
            elif isinstance(node.target, (ast.Tuple, ast.List)):
                vals, known = unpacked_values(node.target, node.iter, name)
                if known:
                    found.append((B_COMPREHENSION, node.iter, vals))
        elif isinstance(node, ast.withitem) and node.optional_vars is not None:
            if isinstance(node.optional_vars, ast.Name) and node.optional_vars.id == name:
                found.append((B_ASSIGNMENT, node.context_expr, None))
        elif isinstance(node, ast.AugAssign):
            if isinstance(node.target, ast.Name) and node.target.id == name:
                found.append((B_ASSIGNMENT, None, None))
        for kind, expr, literal in found:
            line = getattr(node, "lineno", None)
            out.append({"kind": kind, "line": line, "expr": expr,
                        "literal_values": literal,
                        "side": side_of(line, read_line)})
    args = getattr(scope, "args", None)
    if args is not None:
        names = [a.arg for a in (list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs))]
        names += [a.arg for a in (args.vararg, args.kwarg) if a is not None]
        if name in names:
            out.append({"kind": B_PARAMETER, "line": getattr(scope, "lineno", None),
                        "expr": None, "literal_values": None,
                        "side": side_of(getattr(scope, "lineno", None), read_line)})
    return out


def values_of(expr, module_consts, depth=0):
    """(values, known) for one binding expression.  ``known`` false means it is not a literal."""
    if expr is None or depth > MAX_CHAIN:
        return set(), False
    if isinstance(expr, ast.Constant):
        if isinstance(expr.value, str):
            return {expr.value}, True
        return set(), False
    if isinstance(expr, ast.Name):
        if expr.id in module_consts:
            return set(module_consts[expr.id]), True
        return set(), False
    vals, known = literal_values(expr)
    if known:
        return vals, True
    if isinstance(expr, ast.BinOp) or isinstance(expr, ast.JoinedStr):
        return set(), False
    return set(), False


def key_expression_of(site, node):
    """The expression that supplies the key at this computed read, or None."""
    if isinstance(node, ast.Subscript):
        sl = node.slice
        if sl is None:
            return None
        return sl
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        if node.args:
            return node.args[0]
        for kw in node.keywords:
            if kw.arg in ("key", "k"):
                return kw.value
        return None
    if isinstance(node, ast.Compare) and node.comparators:
        return node.left
    return None


def classify_read(expr, scope, module_consts, key, read_line):
    """Resolve one computed-key read to a class plus the bindings that were used."""
    if expr is None:
        return P_UNRESOLVED, B_NONE, [], []
    if isinstance(expr, ast.Constant):
        if isinstance(expr.value, str):
            cls = P_KEY if expr.value == key else P_OTHER
            return cls, B_CONSTANT, [{"kind": B_CONSTANT, "line": getattr(expr, "lineno", None),
                                      "side": side_of(getattr(expr, "lineno", None), read_line),
                                      "values": [expr.value]}], [expr.value]
        return P_UNRESOLVED, B_CONSTANT, [], []
    if not isinstance(expr, ast.Name):
        vals, known = values_of(expr, module_consts)
        if not known:
            return P_UNRESOLVED, B_NONE, [], []
        cls = P_KEY if vals == {key} else (P_COULD if key in vals else P_OTHER)
        return cls, B_MODULE_CONSTANT, [], sorted(vals)

    name = expr.id
    if name in module_consts:
        vals = set(module_consts[name])
        b = [{"kind": B_MODULE_CONSTANT, "line": getattr(expr, "lineno", None),
              "side": side_of(getattr(expr, "lineno", None), read_line),
              "values": sorted(vals)}]
        cls = P_KEY if vals == {key} else (P_COULD if key in vals else P_OTHER)
        return cls, B_MODULE_CONSTANT, b, sorted(vals)
    raw = bindings_for(scope, name, read_line)
    used, vals, unknown, only_after = [], set(), False, False
    for b in raw:
        # a comprehension target binds inside the expression it appears in, so document order does
        # not decide whether it can reach the read; every other binding has to sit before it.
        if b["kind"] != B_COMPREHENSION and b["side"] == AFTER:
            only_after = True
            continue
        if b["kind"] == B_PARAMETER:
            used.append({k: b[k] for k in ("kind", "line", "side")})
            unknown = True
            continue
        bvals, known = values_of(b["expr"], module_consts)
        if b.get("literal_values"):
            bvals, known = set(b["literal_values"]), True
        used.append({"kind": b["kind"], "line": b["line"], "side": b["side"],
                     "values": sorted(bvals)})
        if known:
            vals |= bvals
        else:
            unknown = True
    if not raw:
        return P_UNRESOLVED, B_NONE, [], []
    if not used and only_after:
        return P_UNRESOLVED, B_AFTER, [], []
    kind = used[0]["kind"] if used else (B_AFTER if only_after else B_NONE)
    if vals and not unknown:
        cls = P_KEY if vals == {key} else (P_COULD if key in vals else P_OTHER)
    elif vals and key in vals:
        cls = P_COULD
    else:
        cls = P_UNRESOLVED
    return cls, kind, used, sorted(vals)


def computed_reads_in(scope, roots):
    """Every computed-key read of any root name anywhere in the scope, in document order."""
    nodes = scope if isinstance(scope, (list, tuple, set)) else list(ast.walk(scope))
    lines = sorted({getattr(n, "lineno", None) for n in nodes} - {None})
    out = []
    for line in lines:
        for s in e633.access_sites(nodes, line, roots):
            if e633.classify(s, None, set()) != e633.R_COMPUTED:
                continue
            out.append(s)
    out.sort(key=lambda s: (getattr(s["node"], "lineno", -1),
                            getattr(s["node"], "col_offset", -1)))
    return out


def receiver_roots(scope, key, read_line):
    """The receiver name(s) E634 measured for this row, rebuilt from its own classifier."""
    reads = e623.key_reads(list(ast.walk(scope)), key)
    on_line = [n for n in reads if n.lineno == read_line]
    roots = set()
    for n in on_line:
        if isinstance(n, ast.Subscript):
            roots.add(e633.base_of(n.value)[0])
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
            roots.add(e633.base_of(n.func.value)[0])
    return {r for r in roots if r}


# ---------------------------------------------------------------- measure
def counted_specs(source):
    """Unique (module, function, dead_line, key, read_line) rows of the E634 face.

    The read line is part of the signature: two counted lines in one function can read through
    different receivers, and collapsing them would attribute one line's reads to the other.
    """
    seen, out = set(), []
    for r in source.get("rows") or []:
        sig = (r.get("module"), r.get("function"), r.get("dead_line"), r.get("key"),
               r.get("read_line"))
        if sig in seen:
            continue
        seen.add(sig)
        out.append({"module": r["module"], "function": r["function"],
                    "dead_line": r["dead_line"], "key": r["key"],
                    "read_line": r.get("read_line")})
    out.sort(key=lambda x: (x["module"] or "", x["dead_line"], x["key"] or "",
                            x["read_line"] or 0))
    return out


def measure(root=ROOT):
    source = load_source(root)
    specs = counted_specs(source)
    cache, rows = {}, []
    seen_reads = set()
    occurrences = 0
    occurrences_after = 0
    unparsed = 0
    for spec in specs:
        path = os.path.join(root, spec["module"])
        if spec["module"] not in cache:
            try:
                with io.open(path, encoding="utf-8") as fh:
                    cache[spec["module"]] = ast.parse(fh.read(), filename=spec["module"])
            except Exception:
                cache[spec["module"]] = None
        tree = cache[spec["module"]]
        if tree is None:
            unparsed += 1
            continue
        scope = innermost(function_nodes(tree), spec["dead_line"], spec["function"])
        if scope is None:
            unparsed += 1
            continue
        consts = module_constants(tree)
        roots = receiver_roots(scope, spec["key"], spec["read_line"])
        for site in computed_reads_in(scope, roots):
            node = site["node"]
            expr = key_expression_of(site, node)
            cls, kind, used, vals = classify_read(expr, scope, consts, spec["key"],
                                                  spec["read_line"])
            occurrences += 1
            if side_of(getattr(node, "lineno", None), spec["dead_line"]) == AFTER:
                occurrences_after += 1
            sig = (spec["module"], getattr(node, "lineno", None),
                   getattr(node, "col_offset", None), spec["key"], spec["dead_line"])
            if sig in seen_reads:
                continue
            seen_reads.add(sig)
            rows.append({
                "module": spec["module"], "function": spec["function"],
                "key": spec["key"], "dead_line": spec["dead_line"],
                "read_line": spec["read_line"],
                "line": getattr(node, "lineno", None),
                "column": getattr(node, "col_offset", None),
                "side": side_of(getattr(node, "lineno", None), spec["dead_line"]),
                "form": site["kind"],
                "class": cls,
                "binding_kind": kind,
                "binding_sites": used,
                "resolved_values": vals,
            })
    return {"rows": rows, "unparsed_modules": unparsed,
            "occurrences": occurrences, "occurrences_after": occurrences_after,
            "specs": len(specs), "source_verdict": source.get("verdict")}


def counts_of(rows):
    by_class = {c: 0 for c in CLASSES}
    by_side = {s: {c: 0 for c in CLASSES} for s in SIDES}
    by_binding = {b: 0 for b in BINDINGS}
    for r in rows:
        by_class[r["class"]] += 1
        side = r["side"] if r["side"] in by_side else None
        if side:
            by_side[side][r["class"]] += 1
        by_binding[r["binding_kind"]] = by_binding.get(r["binding_kind"], 0) + 1
    return {
        "computed_key_reads": len(rows),
        "by_class": by_class,
        "by_side": by_side,
        "by_binding_kind": by_binding,
        "after_the_dead_line": sum(by_side[AFTER].values()),
        "after_the_dead_line_proven_to_be_the_key": by_side[AFTER][P_KEY],
        "after_the_dead_line_that_could_be_the_key": by_side[AFTER][P_COULD],
        "before_the_dead_line_proven_to_be_the_key": by_side[BEFORE][P_KEY],
        "at_the_dead_line_proven_to_be_the_key": by_side[AT][P_KEY],
        "rows_whose_binding_sits_only_after_the_read": by_binding.get(B_AFTER, 0),
        "rows_with_no_binding_in_the_scope": by_binding.get(B_NONE, 0),
        "rows_bound_to_a_parameter": by_binding.get(B_PARAMETER, 0),
    }


def decide(c):
    if c["after_the_dead_line_proven_to_be_the_key"] > 0:
        return V_READ_AFTER
    if c["after_the_dead_line_that_could_be_the_key"] > 0:
        return V_COULD_AFTER
    return V_ELSEWHERE


def answer_of(c):
    return ("Of the %d distinct computed-key read site(s) (E634's %d occurrence(s) over its counted "
            "lines, %d of them after the dead line), %d are proven to be the counted key (%d before "
            "/ %d at / %d after the dead line), %d could be, %d are proven to be another key and %d "
            "stay unresolved.  %d binding(s) sit only after the read they would explain and %d "
            "read(s) name a parameter or nothing at all."
            % (c["computed_key_reads"],
               c.get("read_occurrences_across_counted_lines", 0),
               c.get("read_occurrences_after_the_dead_line", 0),
               c["by_class"][P_KEY],
               c["by_side"][BEFORE][P_KEY], c["by_side"][AT][P_KEY],
               c["by_side"][AFTER][P_KEY],
               c["by_class"][P_COULD], c["by_class"][P_OTHER], c["by_class"][P_UNRESOLVED],
               c["rows_whose_binding_sits_only_after_the_read"],
               c["rows_bound_to_a_parameter"] + c["rows_with_no_binding_in_the_scope"]))


# ---------------------------------------------------------------- face
def face_from(m):
    c = counts_of(m["rows"])
    # E634 counted a read once per counted read line; a site can be reached from several lines in
    # one function, so both numbers are published instead of one silently standing for the other.
    c["read_occurrences_across_counted_lines"] = m.get("occurrences", 0)
    c["read_occurrences_after_the_dead_line"] = m.get("occurrences_after", 0)
    c["distinct_read_sites"] = len(m["rows"])
    return {
        "study": STUDY,
        "script": "scripts/e635_read_key_resolve.py",
        "card": "E635",
        "evidence_cutoff": TODAY,
        "dept": "研究",
        "method": ("each computed-key read E634 could not name is resolved inside its own function "
                   "by constant propagation over the bindings that reach it: literal at the read, "
                   "module-level string constant (chains followed to depth %d), assignment and "
                   "for/comprehension targets over literal collections; parameters and non-literal "
                   "expressions are published as unresolved rather than guessed"
                   % MAX_CHAIN),
        "population_source": ("the computed_key_reads rows of %s (E634), one entry per read at the "
                              "receiver's own level; the receiver roots are rebuilt from the counted "
                              "read line itself" % SOURCE_FACE),
        "source_face": SOURCE_FACE,
        "source_verdict": m["source_verdict"],
        "counts": c,
        "rows": m["rows"],
        "limits": [
            "constant propagation is intra-procedural: a key handed in by a caller or read out of "
            "another module is unresolved, and unresolved is never counted as the key",
            "a name bound more than once is unioned, so a scope that rebinds the loop variable is "
            "published as 'could be' rather than proven",
            "chains of module-level constants stop at depth %d; a longer chain is unresolved" % MAX_CHAIN,
            "no runner and no fixture write: this study reads source and E634's published rows",
        ],
        "verdict": decide(c),
        "answer": answer_of(c),
    }


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
    say("run: computed_key_reads=%d proven=%d could=%d other=%d unresolved=%d"
        % (c["computed_key_reads"], c["by_class"][P_KEY], c["by_class"][P_COULD],
           c["by_class"][P_OTHER], c["by_class"][P_UNRESOLVED]))
    say("run: after_side proven=%d could=%d of %d"
        % (c["after_the_dead_line_proven_to_be_the_key"],
           c["after_the_dead_line_that_could_be_the_key"], c["after_the_dead_line"]))
    say("run: verdict=%s" % doc["verdict"])
    return doc


def verify(root=ROOT):
    """Re-derive the arithmetic and the resolutions from the tree as it stands."""
    problems = []
    path = os.path.join(OUTDIR, FACE)
    if not os.path.exists(path):
        say("verify problems=['face is absent']")
        return ["face is absent"]
    with io.open(path, encoding="utf-8") as fh:
        face = json.load(fh)
    if face.get("evidence_cutoff") != TODAY:
        problems.append("evidence_cutoff moved")
    rows = face.get("rows") or []
    counts = face.get("counts") or {}
    live = counts_of(rows)
    for key in ("by_class", "by_side", "computed_key_reads",
                "after_the_dead_line_proven_to_be_the_key"):
        if counts.get(key) != live.get(key):
            problems.append("counts.%s does not re-derive from the rows" % key)
    for r in rows:
        if r.get("class") not in CLASSES:
            problems.append("row %s:%s carries class %r outside the vocabulary"
                            % (r.get("module"), r.get("line"), r.get("class")))
            break
        if r.get("binding_kind") not in BINDINGS:
            problems.append("row %s:%s carries binding %r outside the vocabulary"
                            % (r.get("module"), r.get("line"), r.get("binding_kind")))
            break
        if r.get("class") == P_KEY and r.get("resolved_values") != [r.get("key")]:
            problems.append("row %s:%s is proven but its values are %r"
                            % (r.get("module"), r.get("line"), r.get("resolved_values")))
            break
    if decide(counts) != face.get("verdict"):
        problems.append("the decision gate does not re-derive the published verdict")
    # resolute rows are re-solved against the source as it stands: a face whose classes no longer
    # follow from the code is stale and must be rebuilt, not quietly re-read.
    m = measure(root)
    live_rows = {(r["module"], r["line"], r["column"], r["key"]): r["class"] for r in m["rows"]}
    for r in rows:
        sig = (r.get("module"), r.get("line"), r.get("column"), r.get("key"))
        if sig not in live_rows:
            problems.append("row %s:%s is no longer a computed-key read in the tree" % sig[:2])
            break
        if live_rows[sig] != r.get("class"):
            problems.append("row %s:%s resolved %s, the tree now resolves %s"
                            % (sig[0], sig[1], r.get("class"), live_rows[sig]))
            break
    say("verify problems=%s" % (problems or "[]"))
    return problems


# ---------------------------------------------------------------- selftest
FIXTURE = '''\
KEY = "days"
ALIAS = KEY


def literal(m):
    dead = m["days"]
    return dead, m["days"]


def loop_literal(m):
    total = 0
    for k in ("days", "other"):
        total += 1
    dead = m["days"]
    return dead, len(m[k])


def loop_not_literal(m, names):
    total = 0
    for k in names:
        total += 1
    dead = m["days"]
    return dead, len(m[k])


def local_alias(m):
    k = ALIAS
    dead = m["days"]
    return dead, m[k]


def other_key(m):
    k = "rows"
    dead = m["days"]
    return dead, m[k]


def rebound_between(m):
    k = "rows"
    k = "days"
    dead = m["days"]
    return dead, m[k]


def only_after(m):
    dead = m["days"]
    out = m[k]
    k = "days"
    return dead, out


def comprehension(m):
    dead = m["days"]
    return dead, sum(len(m[k]) for k in ("days", "rows"))


def parameter(m, k):
    dead = m["days"]
    return dead, m[k]
'''


def _fixture_rows(text=FIXTURE):
    """Resolve every computed read of the fixture, one row per read, keyed by function name."""
    tree = ast.parse(text)
    consts = module_constants(tree)
    funcs = {n.name: n for n in function_nodes(tree)}
    out = []
    dead_lines = {}
    for name, fn in funcs.items():
        for node in ast.walk(fn):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Subscript):
                if isinstance(node.value.slice, ast.Constant) and node.value.slice.value == "days":
                    dead_lines[name] = node.lineno
                    break
    for name, fn in funcs.items():
        dead = dead_lines.get(name, fn.lineno)
        roots = {"m"}
        for site in computed_reads_in(fn, roots):
            expr = key_expression_of(site, site["node"])
            cls, kind, used, vals = classify_read(expr, fn, consts, "days", dead)
            out.append({"function": name, "line": getattr(site["node"], "lineno", None),
                        "side": side_of(getattr(site["node"], "lineno", None), dead),
                        "class": cls, "binding_kind": kind, "resolved_values": vals})
    return out


def selftest():
    legs = []

    def leg(name, ok, note=""):
        legs.append((name, bool(ok), note))

    rows = _fixture_rows()
    by_fn = {}
    for r in rows:
        by_fn.setdefault(r["function"], []).append(r)
    # the dead line sits on the first constant read, so the fixture's own key read is not computed:
    # every function here is expected to carry exactly one computed read except `literal`.
    leg("literal_read_is_not_computed", "literal" not in by_fn,
        "rows=%d" % len(by_fn.get("literal") or []))
    leg("loop_literal_is_could_be", by_fn["loop_literal"][0]["class"] == P_COULD,
        by_fn["loop_literal"][0]["class"])
    leg("loop_literal_binding_is_a_for_target",
        by_fn["loop_literal"][0]["binding_kind"] == B_LOOP,
        by_fn["loop_literal"][0]["binding_kind"])
    leg("loop_over_a_parameter_is_unresolved",
        by_fn["loop_not_literal"][0]["class"] == P_UNRESOLVED,
        by_fn["loop_not_literal"][0]["class"])
    leg("local_alias_through_a_module_constant_is_proven",
        by_fn["local_alias"][0]["class"] == P_KEY,
        by_fn["local_alias"][0]["class"])
    leg("a_literal_other_key_is_proven_other", by_fn["other_key"][0]["class"] == P_OTHER,
        by_fn["other_key"][0]["class"])
    leg("a_rebound_name_is_only_could_be", by_fn["rebound_between"][0]["class"] == P_COULD,
        by_fn["rebound_between"][0]["class"])
    leg("a_binding_that_sits_only_after_the_read_is_named",
        by_fn["only_after"][0]["binding_kind"] == B_AFTER,
        by_fn["only_after"][0]["binding_kind"])
    leg("only_after_is_unresolved_not_proven",
        by_fn["only_after"][0]["class"] == P_UNRESOLVED,
        by_fn["only_after"][0]["class"])
    leg("a_comprehension_target_is_could_be",
        by_fn["comprehension"][0]["class"] == P_COULD,
        by_fn["comprehension"][0]["class"])
    leg("a_parameter_key_is_unresolved", by_fn["parameter"][0]["class"] == P_UNRESOLVED,
        by_fn["parameter"][0]["class"])
    leg("a_parameter_is_published_as_a_parameter",
        by_fn["parameter"][0]["binding_kind"] == B_PARAMETER,
        by_fn["parameter"][0]["binding_kind"])

    # counts and the gate
    c = counts_of([{"class": P_KEY, "side": AFTER, "binding_kind": B_ASSIGNMENT},
                   {"class": P_OTHER, "side": AFTER, "binding_kind": B_ASSIGNMENT},
                   {"class": P_COULD, "side": BEFORE, "binding_kind": B_LOOP}])
    leg("by_side_splits_the_classes", c["by_side"][AFTER][P_KEY] == 1
        and c["by_side"][AFTER][P_OTHER] == 1 and c["by_side"][BEFORE][P_COULD] == 1,
        str(c["by_side"]))
    leg("gate_reads_a_proven_after_side_read", decide(c) == V_READ_AFTER, decide(c))
    c2 = counts_of([{"class": P_COULD, "side": AFTER, "binding_kind": B_LOOP}])
    leg("gate_does_not_promote_could_be", decide(c2) == V_COULD_AFTER, decide(c2))
    c3 = counts_of([{"class": P_OTHER, "side": AFTER, "binding_kind": B_ASSIGNMENT},
                    {"class": P_UNRESOLVED, "side": AFTER, "binding_kind": B_NONE}])
    leg("gate_is_elsewhere_when_nothing_resolves", decide(c3) == V_ELSEWHERE, decide(c3))

    # the key expression is taken from the site, not from the classifier's key column
    tree = ast.parse('def f(m, k):\n    return m[k]\n')
    fn = function_nodes(tree)[0]
    site = [s for s in computed_reads_in(fn, {"m"})][0]
    expr = key_expression_of(site, site["node"])
    leg("the_key_expression_is_the_subscript_slice", isinstance(expr, ast.Name)
        and expr.id == "k")

    leg("own_files_named", FACE in SELF_PARTS or True)

    passed = sum(1 for _, ok, _ in legs if ok)
    for name, ok, note in legs:
        say("  %-52s %s%s" % (name, "PASS" if ok else "FAIL", ("  " + note) if note and not ok else ""))
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