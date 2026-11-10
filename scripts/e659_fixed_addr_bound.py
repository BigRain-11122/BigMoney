"""E659 -- what the 149 fixed-address loop writes collapse to, and whether each loop bound
is countable.

E653 split the 845 loop-guarded residual module-level write sites by address shape: 696 compute
their address from the loop target (an accumulator), 149 repeat one address every pass
(last-write-wins).  That split answers *what the body writes*; it does not answer *how many times
it writes it*.  A fixed-address site inside ``for x in range(3): P['k'] = x`` performs three writes
of one key -- the first two are dead stores.  A fixed-address site inside ``for x in rows: P['k'] = x``
does the same but nobody can say how many.

So for every one of E653's fixed-address sites this study publishes the innermost loop's iteration
bound as a machine-checkable reading:

  * ``exact``   -- the bound is statically computable, and the value is published: a literal
                   container (its length), a string (its length), ``range`` over resolvable
                   integers, ``enumerate`` of a resolvable sequence, ``zip`` of resolvable
                   sequences (min), or a module-level name whose binding chain bottoms out in one
                   of those.
  * ``unknown`` -- the iterable is a bare name, a call other than range/enumerate/zip, a
                   comprehension, an attribute/subscript, or an operator: the write count cannot
                   be read off the source.
  * ``while``   -- the loop has no iteration bound at all by construction.

The collapse is published per site (``redundant_writes = max(n - 1, 0)``) and in total, so a
reader can price how much of the residual is dead stores rather than live writes.

Population and ruler are imported, not re-implemented: E638/E640 give the two-depth site grouping
and owner split, E643 the module-context parser and bucket, E649 the containment test and the
module-level guard chain, and E653 the innermost-loop lookup, iterable/key form rulers and the
address-varies decision.  The population is reconciled against E653's published face row by row;
a site that disappears is a hard red, a site the tree grew since that face is disclosed.
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
FACE = "FIXEDADDRBOUND.json"
LATEST = "fixedaddrbound_latest.json"
STUDY = "E659_fixed_address_loop_write_bound"
SOURCE_FACE = "results/state_tilt/LOOPWRITEKEY.json"
DELIVERABLE = "results/state_tilt/FIXEDADDRBOUND.json"
SELF_PARTS = ("e659_", "run_e659_", "_probe_e659", "_r1677")
MAX_DEPTH = 6
MAX_EXAMPLES = 8

import e638_two_depth_subscripts as e638  # noqa: E402
import e640_writeread_collide as e640  # noqa: E402
import e643_nonfunc_site as e643  # noqa: E402
import e649_guarded_write as e649  # noqa: E402
import e653_loop_write_key as e653  # noqa: E402

BOUND_CLASSES = ("exact", "unknown", "while")

V_ABSENT = (
    "no_fixed_address_loop_write_exists,_so_there_is_no_repeated_write_to_price")
V_ALL_EXACT = (
    "every_fixed_address_loop_write_has_a_statically_computable_iteration_bound,_so_each_such_loop_"
    "collapses_to_one_live_write_and_the_rest_are_dead_stores")
V_NONE_EXACT = (
    "no_fixed_address_loop_write_has_a_statically_computable_bound,_so_the_repeated_write_is_real_"
    "but_the_number_of_repeats_is_not_readable_from_the_source")
V_SPLIT = (
    "fixed_address_loop_writes_split_by_whether_the_bound_is_readable,_and_the_split_is_published_"
    "rather_than_assuming_a_loop_around_a_write_means_many_writes")


def say(line):
    sys.stdout.write(str(line) + "\n")


def rel(module, root=ROOT):
    return e653.rel(module, root)


# ---------------------------------------------------------------- bound ruler
def _scalar(node, bindings, depth, seen):
    """Resolve a node to an int, or None when the source does not say."""
    if depth > MAX_DEPTH:
        return None
    if isinstance(node, ast.Constant):
        return node.value if isinstance(node.value, int) else None
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        inner = _scalar(node.operand, bindings, depth + 1, seen)
        if inner is None:
            return None
        return -inner if isinstance(node.op, ast.USub) else inner
    if isinstance(node, ast.Name):
        bound = bindings.get(node.id)
        if bound is None or node.id in seen:
            return None
        return _scalar(bound, bindings, depth + 1, seen | {node.id})
    if isinstance(node, ast.BinOp):
        left = _scalar(node.left, bindings, depth + 1, seen)
        right = _scalar(node.right, bindings, depth + 1, seen)
        if left is None or right is None:
            return None
        try:
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.FloorDiv) and right:
                return left // right
        except ZeroDivisionError:
            return None
    return None


def _length(node, bindings, depth, seen):
    """Resolve a node to a static length, or None."""
    if depth > MAX_DEPTH:
        return None
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return len(node.elts)
    if isinstance(node, ast.Dict):
        return len(node.keys)
    if isinstance(node, ast.Constant) and isinstance(node.value, (str, bytes)):
        return len(node.value)
    if isinstance(node, ast.Name):
        bound = bindings.get(node.id)
        if bound is None or node.id in seen:
            return None
        return _length(bound, bindings, depth + 1, seen | {node.id})
    if isinstance(node, ast.Call):
        name = _call_name(node)
        if name == "range":
            n = _range_len(node, bindings, depth, seen)
            return n
        if name == "enumerate":
            if not node.args:
                return None
            return _length(node.args[0], bindings, depth + 1, seen)
        if name == "zip":
            if not node.args:
                return None
            got = [_length(a, bindings, depth + 1, seen) for a in node.args]
            if any(g is None for g in got):
                return None
            return min(got)
    return None


def _range_len(node, bindings, depth, seen):
    args = [_scalar(a, bindings, depth + 1, seen) for a in node.args]
    if not args or any(a is None for a in args):
        return None
    if len(args) == 1:
        start, stop, step = 0, args[0], 1
    elif len(args) == 2:
        start, stop, step = args[0], args[1], 1
    elif len(args) == 3:
        start, stop, step = args
    else:
        return None
    if step == 0:
        return None
    span = stop - start
    if span <= 0:
        return 0 if step > 0 else None
    if step < 0:
        return 0
    return (span + step - 1) // step


def _call_name(node):
    func = node.func if isinstance(node, ast.Call) else None
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return ""


def resolve_iterable(node, bindings, depth=0, seen=None, source=""):
    """(bound_class, value, source, reason) for a ``for`` iterable expression."""
    seen = seen or frozenset()
    depth = depth or 0
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return "exact", len(node.elts), source or "literal_container", ""
    if isinstance(node, ast.Dict):
        return "exact", len(node.keys), source or "literal_dict_keys", ""
    if isinstance(node, ast.Constant) and isinstance(node.value, (str, bytes)):
        return "exact", len(node.value), source or "string_literal", ""
    if isinstance(node, ast.Constant):
        return "unknown", None, source or "constant", "a_non_string_constant_is_not_iterable"
    if isinstance(node, ast.Name):
        if node.id in seen:
            return "unknown", None, source or ("name:" + node.id), "binding_cycle"
        bound = bindings.get(node.id)
        if bound is None:
            return "unknown", None, source or ("bare_name:" + node.id), \
                "bare_name_bound_not_statically_known"
        cls, value, src, why = resolve_iterable(
            bound, bindings, depth + 1, seen | {node.id},
            source=(source + ">" if source else "module_constant:") + node.id)
        return cls, value, src, why
    if isinstance(node, ast.Call):
        name = _call_name(node)
        if name == "range":
            n = _range_len(node, bindings, depth, seen)
            if n is None:
                return "unknown", None, source or "range_call", \
                    "range_arguments_are_not_resolvable_integers"
            return "exact", n, source or "range_call", ""
        if name == "enumerate":
            if not node.args:
                return "unknown", None, source or "enumerate_call", "enumerate_without_argument"
            cls, value, src, why = resolve_iterable(
                node.args[0], bindings, depth + 1, seen,
                source=(source + ">" if source else "enumerate_of:") + "arg")
            if cls != "exact":
                return "unknown", None, src, why
            return "exact", value, src, ""
        if name == "zip":
            if not node.args:
                return "unknown", None, source or "zip_call", "zip_without_arguments"
            got = []
            for arg in node.args:
                cls, value, src, why = resolve_iterable(
                    arg, bindings, depth + 1, seen, source=(source or "zip_of"))
                if cls != "exact":
                    return "unknown", None, src, why
                got.append(value)
            return "exact", min(got), source or "zip_call", ""
        return "unknown", None, source or ("call:" + (name or "anon")), \
            "call_bound_not_statically_known"
    if isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
        return "unknown", None, source or "comprehension", \
            "comprehension_bound_depends_on_its_generator"
    if isinstance(node, (ast.Attribute, ast.Subscript)):
        return "unknown", None, source or "attribute_or_subscript", \
            "member_read_bound_not_statically_known"
    if isinstance(node, ast.BinOp):
        return "unknown", None, source or "operator", "operator_bound_not_statically_known"
    return "unknown", None, source or "other", "form_not_recognised_as_a_static_bound"


def bound_of(loop, bindings):
    """The bound reading for the innermost loop holding a site."""
    if isinstance(loop, ast.While):
        return {"bound_class": "while", "bound_value": None,
                "bound_source": "while:" + (e653.unparse(loop.test) or "")[:60],
                "bound_reason": "a_while_loop_has_no_static_iteration_bound"}
    cls, value, src, why = resolve_iterable(loop.iter, bindings)
    return {"bound_class": cls, "bound_value": value,
            "bound_source": src[:120], "bound_reason": why}


def redundant_writes(bound_class, bound_value):
    """Dead stores removed by collapsing N repeated writes of one address to one live write."""
    if bound_class != "exact" or bound_value is None:
        return None
    return max(int(bound_value) - 1, 0)


# ---------------------------------------------------------------- measure
def measure(root=ROOT):
    files = [p for p in e649.corpus(root)
             if not os.path.basename(p).startswith(SELF_PARTS)]
    holes = {"over_the_size_cap": 0, "unreadable": 0, "does_not_parse": 0}
    rows = []
    for path in files:
        got, why = e638.file_sites(path)
        if got is None:
            holes[why] = holes.get(why, 0) + 1
            continue
        if not got["sites"]:
            continue
        spans = e640.function_spans(path)
        ctx = e643.context_of_file(path)
        if spans is None or ctx is None:
            holes["does_not_parse"] = holes.get("does_not_parse", 0) + 1
            continue
        tree = ctx["tree"]
        lines = ctx["lines"]
        bindings = e653.module_bindings(tree)
        for site in got["sites"]:
            if e640.innermost_owner(spans, site["line"]) is not None:
                continue
            row = e640.site_row(site)
            if not row["any_member_is_write"]:
                continue
            bucket = e643.classify(ctx, site["line"], site["column"])["bucket"]
            chain = e649.block_chain(tree, site["line"], site["column"]) \
                if bucket == "module_body" else []
            if "loop" not in chain:
                continue
            loop = e653.innermost_loop(tree, site["line"], site["column"])
            if loop is None:
                continue
            names, unpack = ([], False)
            if isinstance(loop, ast.While):
                loop_kind = "while"
                iter_form = e653.condition_form(loop.test)
                binding = e653.unparse(loop.test)
            else:
                loop_kind = "async_for" if isinstance(loop, ast.AsyncFor) else "for"
                iter_form = e653.iterable_form(loop.iter, bindings)
                binding = e653.unparse(loop.iter)
                names, unpack = e653.target_names(loop.target)
            addr = e653.classify_site(tree, site["line"], site["column"], names, unpack)
            if addr["address_can_vary"]:
                continue
            bound = bound_of(loop, bindings)
            rows.append({
                "module": rel(path, root),
                "line": site["line"],
                "column": site["column"],
                "chain": chain,
                "loop_kind": loop_kind,
                "iterable_form": iter_form,
                "iterable_binding": binding[:120],
                "bound_class": bound["bound_class"],
                "bound_value": bound["bound_value"],
                "bound_source": bound["bound_source"],
                "bound_reason": bound["bound_reason"],
                "redundant_writes": redundant_writes(bound["bound_class"],
                                                     bound["bound_value"]),
                "key_form": addr["key_form"],
                "key_text": addr["key_text"],
                "container_key_form": addr["container_key_form"],
                "source": lines[site["line"] - 1].strip()[:160]
                if 0 < site["line"] <= len(lines) else "",
            })
    rows.sort(key=lambda r: (r["module"], r["line"], r["column"]))
    counts = counts_of(rows, len(files), holes)
    counts["reconciliation"] = reconcile(rows, root)
    return {
        "study": STUDY,
        "date": TODAY,
        "evidence_cutoff": TODAY,
        "source_face": SOURCE_FACE,
        "deliverable": DELIVERABLE,
        "method": (
            "take E653's population (loop-guarded residual module-level write sites whose address "
            "does not mention the loop target), then publish for each the innermost loop's "
            "iteration bound as exact/unknown/while with the resolved integer where the source "
            "states it; literal containers, strings, range over resolvable integers, enumerate "
            "and zip of resolvable sequences, and module-level binding chains that bottom out in "
            "those are exact; bare names, other calls, comprehensions, member reads and operators "
            "are unknown"),
        "population_source": (
            "%d Python files of the E391 corpus minus this study's own prefixes; the population is "
            "every E653 fixed-address site, which is every two-depth module-level write site "
            "behind a loop guard whose row key and container key both ignore the loop target"
            % len(files)),
        "counts": counts,
        "rows": rows,
        "examples": examples_of(rows),
        "limits": [
            "an exact bound is a syntactic promise about the iterable expression, not a proof "
            "that the loop runs that many times: a ``break``, a ``return`` or a raising guard "
            "inside the body shortens the run and this ruler does not look for them",
            "``zip`` is published as the minimum of its resolvable arms; a zip with one "
            "unresolvable arm is unknown rather than the minimum of the rest",
            "``range`` step must be a resolvable integer; a negative step is published as zero "
            "because the ruler does not model decreasing ranges",
            "module-level binding chains are followed to ``MAX_DEPTH`` (6) and a cycle is cut as "
            "unknown with reason ``binding_cycle``; the first assignment wins, as in E653",
            "``enumerate`` and ``zip`` bounds are read from their arguments, so a generator "
            "argument inherits ``comprehension_bound_depends_on_its_generator``",
            "``redundant_writes`` counts dead stores in a last-write-wins loop, not savings in "
            "runtime: the loop still iterates, only the address is written repeatedly",
            "a site E653 published but this build cannot find is a hard red (the population "
            "shrank); a site the tree grew since E653's face is disclosed and not counted against "
            "the face",
            "files over 1MB are skipped rather than parsed (E391's cap) and counted apart",
        ],
        "verdict": decide(counts),
        "answer": answer_of(counts),
    }


def counts_of(rows, files_scanned=0, holes=None):
    c = {
        "python_files_scanned": files_scanned,
        "fixed_address_sites": len(rows),
        "dead_stores_collapsed": 0,
        "sites_with_exact_bound": 0,
        "sites_with_unknown_bound": 0,
        "sites_inside_a_while": 0,
        "sites_whose_bound_came_through_a_module_constant": 0,
        "holes": holes or {},
    }
    by_class, by_iter, by_bound_form, by_reason = {}, {}, {}, {}
    histogram = {}
    dead_total = 0
    for r in rows:
        by_class[r["bound_class"]] = by_class.get(r["bound_class"], 0) + 1
        by_iter[r["iterable_form"]] = by_iter.get(r["iterable_form"], 0) + 1
        by_bound_form[r["bound_source"].split(">")[0].split(":")[0]] = \
            by_bound_form.get(r["bound_source"].split(">")[0].split(":")[0], 0) + 1
        if r["bound_reason"]:
            by_reason[r["bound_reason"]] = by_reason.get(r["bound_reason"], 0) + 1
        if r["bound_class"] == "exact":
            c["sites_with_exact_bound"] += 1
            value = r["bound_value"]
            histogram[str(value)] = histogram.get(str(value), 0) + 1
            dead_total += r["redundant_writes"] or 0
        elif r["bound_class"] == "unknown":
            c["sites_with_unknown_bound"] += 1
        elif r["bound_class"] == "while":
            c["sites_inside_a_while"] += 1
        if "module_constant" in r["bound_source"]:
            c["sites_whose_bound_came_through_a_module_constant"] += 1
    c["dead_stores_collapsed"] = dead_total
    c["by_bound_class"] = by_class
    c["by_iterable_form"] = by_iter
    c["by_bound_source_root"] = by_bound_form
    c["by_unknown_reason"] = by_reason
    c["exact_bound_histogram"] = dict(
        sorted(histogram.items(), key=lambda kv: (len(kv[0]), kv[0])))
    exact_values = sorted(r["bound_value"] for r in rows if r["bound_class"] == "exact")
    c["exact_bound_median"] = median(exact_values)
    c["exact_bound_max"] = exact_values[-1] if exact_values else None
    c["cross_bound_class_by_iterable_form"] = cross(rows, "iterable_form")
    return c


def median(values):
    if not values:
        return None
    mid = len(values) // 2
    if len(values) % 2:
        return values[mid]
    return (values[mid - 1] + values[mid]) / 2.0


def cross(rows, key):
    out = {}
    for r in rows:
        bucket = out.setdefault(r[key], {})
        bucket[r["bound_class"]] = bucket.get(r["bound_class"], 0) + 1
    return dict(sorted(out.items()))


def source_fixed_sites(root=ROOT):
    """E653's published fixed-address rows, machine-read from its face."""
    path = os.path.join(root, SOURCE_FACE)
    try:
        with io.open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
    except (OSError, ValueError):
        return None
    rows = doc.get("rows") or []
    fixed = [r for r in rows if r.get("write_mode") == "last_write_wins"]
    return {
        "count": len(fixed),
        "counts_key": (doc.get("counts") or {}).get("write_sites_that_repeat_one_address"),
        "sites": sorted((r.get("module"), r.get("line"), r.get("column")) for r in fixed),
    }


def reconcile(rows, root=ROOT):
    src = source_fixed_sites(root)
    mine = sorted((r["module"], r["line"], r["column"]) for r in rows)
    if src is None:
        return {"source_face_present": False, "population_diff": None}
    theirs = src["sites"]
    only_mine = [s for s in mine if s not in set(theirs)]
    only_theirs = [s for s in theirs if s not in set(mine)]
    return {
        "source_face_present": True,
        "source_face_count": src["count"],
        "source_face_counts_key": src["counts_key"],
        "this_build_count": len(mine),
        "only_in_this_build": [list(s) for s in only_mine],
        "only_in_source_face": [list(s) for s in only_theirs],
        "population_grew_since_source_face": bool(only_mine) and not only_theirs,
        "population_shrank_since_source_face": bool(only_theirs),
    }


def examples_of(rows):
    out = {}
    for cls in BOUND_CLASSES:
        out[cls] = [{"module": r["module"], "line": r["line"],
                     "iterable": r["iterable_binding"][:70],
                     "bound_value": r["bound_value"],
                     "bound_source": r["bound_source"],
                     "bound_reason": r["bound_reason"],
                     "redundant_writes": r["redundant_writes"],
                     "source": r["source"][:90]}
                    for r in rows if r["bound_class"] == cls][:MAX_EXAMPLES // 2]
    return out


def decide(c):
    fixed = c.get("fixed_address_sites") or 0
    if not fixed:
        return V_ABSENT
    exact = c.get("sites_with_exact_bound") or 0
    if exact == fixed:
        return V_ALL_EXACT
    if exact == 0:
        return V_NONE_EXACT
    return V_SPLIT


def answer_of(c):
    fixed = c.get("fixed_address_sites") or 0
    if not fixed:
        return "no fixed-address loop write exists in the corpus"
    exact = c.get("sites_with_exact_bound") or 0
    unknown = c.get("sites_with_unknown_bound") or 0
    whiles = c.get("sites_inside_a_while") or 0
    dead = c.get("dead_stores_collapsed") or 0
    pct = 100.0 * exact / fixed
    med = c.get("exact_bound_median")
    return (
        "%d fixed-address loop writes; %d (%.1f%%) have a bound the source states (median %s "
        "iterations, max %s), %d do not, %d sit inside a while; collapsing the exact ones removes "
        "%d dead stores"
        % (fixed, exact, pct, med, c.get("exact_bound_max"), unknown, whiles, dead))


# ---------------------------------------------------------------- face gate
def face_problems(doc):
    problems = []
    c = doc.get("counts") or {}
    rows = doc.get("rows") or []
    if c.get("fixed_address_sites") != len(rows):
        problems.append("fixed_address_sites does not equal the published row count")
    if (c.get("sites_with_exact_bound", 0) + c.get("sites_with_unknown_bound", 0)
            + c.get("sites_inside_a_while", 0)) != len(rows):
        problems.append("the three bound classes do not partition the rows")
    by_class = c.get("by_bound_class") or {}
    for cls in BOUND_CLASSES:
        mine = sum(1 for r in rows if r.get("bound_class") == cls)
        if by_class.get(cls, 0) != mine:
            problems.append("by_bound_class[%s] does not re-derive from the rows" % cls)
    dead = sum(r.get("redundant_writes") or 0 for r in rows
               if r.get("bound_class") == "exact")
    if c.get("dead_stores_collapsed") != dead:
        problems.append("dead_stores_collapsed does not re-derive from the rows")
    for r in rows:
        if r.get("bound_class") == "exact" and r.get("bound_value") is None:
            problems.append("an exact row carries no bound value (%s:%s)"
                            % (r.get("module"), r.get("line")))
            break
        if r.get("bound_class") in ("unknown", "while") and r.get("redundant_writes") is not None:
            problems.append("a non-exact row carries a redundant_writes count (%s:%s)"
                            % (r.get("module"), r.get("line")))
            break
    rec = c.get("reconciliation") or {}
    if rec.get("population_shrank_since_source_face"):
        problems.append("the population shrank since E653's face: %s"
                        % (rec.get("only_in_source_face") or [])[:4])
    if c.get("fixed_address_sites") and not rec.get("source_face_present", False):
        problems.append("E653's source face is absent, so the population cannot be reconciled")
    if doc.get("verdict") != decide(c):
        problems.append("the verdict does not re-derive from the published counts")
    if not str(doc.get("answer") or "").strip():
        problems.append("the answer line is empty")
    return problems


def write_face(out_dir, doc, face=FACE, latest=LATEST):
    os.makedirs(out_dir, exist_ok=True)
    blob = json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=False)
    for name in (face, latest):
        with io.open(os.path.join(out_dir, name), "w", encoding="utf-8",
                     newline="\n") as fh:
            fh.write(blob)
            fh.write("\n")
    return os.path.join(out_dir, face)


def build(root=ROOT, out_dir=None):
    doc = measure(root)
    problems = face_problems(doc)
    if problems:
        say("FACE-PROBLEMS: " + "; ".join(problems))
        return 3, doc
    path = write_face(out_dir if out_dir is not None else OUTDIR, doc)
    say("wrote " + rel(path, root))
    say("answer: " + doc["answer"])
    return 0, doc


def load_face(path=None, root=ROOT):
    path = path or os.path.join(root, OUTDIR, FACE)
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def check(path=None, root=ROOT):
    problems = face_problems(load_face(path, root))
    say("check problems=%s" % json.dumps(problems, ensure_ascii=False))
    return 0 if not problems else 3


def compared_counts(counts):
    vintage = ("python_files_scanned", "holes")
    return {k: v for k, v in (counts or {}).items()
            if k not in vintage and k != "reconciliation"}


def verify(root=ROOT):
    """Re-read each published row's own module and re-derive its bound; compare field by field.

    A full re-measure would re-walk 13k files for a reading this study already publishes per row,
    so the cheap proof is the one that matters: every row names a file and a position, and the
    bound must come back the same when that file is parsed again.
    """
    face = load_face(root=root)
    problems = face_problems(face)
    rows = face.get("rows") or []
    cache = {}
    for r in rows:
        path = os.path.join(root, r["module"])
        if path not in cache:
            cache[path] = e643.context_of_file(path)
        ctx = cache[path]
        if ctx is None:
            problems.append("row module does not parse: %s" % r["module"])
            continue
        tree = ctx["tree"]
        bindings = e653.module_bindings(tree)
        loop = e653.innermost_loop(tree, r["line"], r["column"])
        if loop is None:
            problems.append("no loop holds %s:%s" % (r["module"], r["line"]))
            continue
        bound = bound_of(loop, bindings)
        if bound["bound_class"] != r["bound_class"]:
            problems.append("bound class moved at %s:%s (%s -> %s)"
                            % (r["module"], r["line"], r["bound_class"],
                               bound["bound_class"]))
        elif bound["bound_value"] != r["bound_value"]:
            problems.append("bound value moved at %s:%s (%s -> %s)"
                            % (r["module"], r["line"], r["bound_value"],
                               bound["bound_value"]))
        if len(problems) > 12:
            break
    say("verify rows=%d problems=%s" % (len(rows), json.dumps(problems[:8], ensure_ascii=False)))
    return 0 if not problems else 3


# ---------------------------------------------------------------- selftest
def selftest():
    legs = []

    def leg(name, ok, note=""):
        legs.append((name, bool(ok), note))
        say("%s %s%s" % ("PASS" if ok else "FAIL", name,
                         (" -- " + note) if note and not ok else ""))

    def bound(src, name="x"):
        import tempfile
        tmp = tempfile.mkdtemp(prefix="e659_")
        path = os.path.join(tmp, "fixture_bound.py")
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(src)
        ctx = e643.context_of_file(path)
        assert ctx is not None, "fixture does not parse"
        tree = ctx["tree"]
        bindings = e653.module_bindings(tree)
        for st in tree.body:
            if isinstance(st, (ast.For, ast.AsyncFor, ast.While)):
                return bound_of(st, bindings)
        raise AssertionError("fixture has no loop")

    b = bound("for x in [1, 2, 3]:\n    P = x\n")
    leg("literal list bound is its length", b["bound_class"] == "exact" and b["bound_value"] == 3, str(b))
    b = bound("for x in (1, 2):\n    P = x\n")
    leg("literal tuple bound is its length", b["bound_class"] == "exact" and b["bound_value"] == 2, str(b))
    b = bound("for x in {'a': 1, 'b': 2, 'c': 3, 'd': 4}:\n    P = x\n")
    leg("literal dict bound counts keys", b["bound_class"] == "exact" and b["bound_value"] == 4, str(b))
    b = bound("for x in 'abcd':\n    P = x\n")
    leg("string bound is its length", b["bound_class"] == "exact" and b["bound_value"] == 4, str(b))
    b = bound("for x in range(3):\n    P = x\n")
    leg("range(3) is exactly three", b["bound_class"] == "exact" and b["bound_value"] == 3, str(b))
    b = bound("for x in range(2, 7):\n    P = x\n")
    leg("range(2,7) is five", b["bound_class"] == "exact" and b["bound_value"] == 5, str(b))
    b = bound("for x in range(1, 10, 3):\n    P = x\n")
    leg("range with step rounds up", b["bound_class"] == "exact" and b["bound_value"] == 3, str(b))
    b = bound("NAMES = ['a', 'b']\nfor x in NAMES:\n    P = x\n")
    leg("module literal constant is exact", b["bound_class"] == "exact" and b["bound_value"] == 2, str(b))
    b = bound("N = 4\nfor x in range(N):\n    P = x\n")
    leg("module integer constant feeds range", b["bound_class"] == "exact" and b["bound_value"] == 4, str(b))
    b = bound("A = B\nB = [1, 2, 3]\nfor x in A:\n    P = x\n")
    leg("module binding chain is followed", b["bound_class"] == "exact" and b["bound_value"] == 3, str(b))
    b = bound("ROWS = ['a', 'b', 'c']\nfor i, x in enumerate(ROWS):\n    P = x\n")
    leg("enumerate bound comes from its argument", b["bound_class"] == "exact" and b["bound_value"] == 3, str(b))
    b = bound("for x in zip([1, 2, 3], [1, 2]):\n    P = x\n")
    leg("zip bound is the shortest arm", b["bound_class"] == "exact" and b["bound_value"] == 2, str(b))
    b = bound("for x in rows:\n    P = x\n")
    leg("bare name is unknown", b["bound_class"] == "unknown" and b["bound_value"] is None, str(b))
    b = bound("for x in load():\n    P = x\n")
    leg("other call is unknown", b["bound_class"] == "unknown", str(b))
    b = bound("for x in [y for y in (1, 2)]:\n    P = x\n")
    leg("comprehension is unknown", b["bound_class"] == "unknown", str(b))
    b = bound("while True:\n    P = 1\n    break\n")
    leg("while has no static bound", b["bound_class"] == "while" and b["bound_value"] is None, str(b))
    b = bound("A = B\nB = A\nfor x in A:\n    P = x\n")
    leg("binding cycle is cut as unknown",
        b["bound_class"] == "unknown" and b["bound_reason"] == "binding_cycle", str(b))
    b = bound("C = 2\nfor x in range(C * 3):\n    P = x\n")
    leg("range over arithmetic constants resolves", b["bound_class"] == "exact" and b["bound_value"] == 6, str(b))
    leg("redundant_writes removes only the repeats",
        redundant_writes("exact", 3) == 2 and redundant_writes("exact", 1) == 0
        and redundant_writes("unknown", None) is None
        and redundant_writes("while", None) is None, "")
    leg("an empty bound is zero, not negative",
        redundant_writes("exact", 0) == 0 and _range_len(ast.parse("range(0)", mode="eval").body, {}, 0, frozenset()) == 0, "")
    leg("median of an even list averages the middle",
        median([1, 2, 3, 4]) == 2.5 and median([5]) == 5 and median([]) is None, "")
    leg("zip with an unresolvable arm is unknown",
        bound("for x in zip([1, 2], load()):\n    P = x\n")["bound_class"] == "unknown", "")

    passed = sum(1 for _, ok, _ in legs if ok)
    say("selftest %d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="E659 fixed-address loop write bound")
    ap.add_argument("mode", nargs="?", default="build",
                    choices=("build", "check", "verify", "selftest", "answer"))
    args = ap.parse_args(argv)
    if args.mode == "selftest":
        return selftest()
    if args.mode == "check":
        return check()
    if args.mode == "verify":
        return verify()
    if args.mode == "answer":
        doc = load_face()
        say(doc.get("answer") or "")
        return 0
    rc, _doc = build()
    return rc


if __name__ == "__main__":
    sys.exit(main())
