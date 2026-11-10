"""E653 -- what the loop-guarded module-level write sites iterate over, and whether every
iteration writes the same address.

E649 published 1,012 residual write sites "behind a guard" and labelled 548 of them `loop`, with the
execution line ``runs_at_import_zero_or_more_times``.  Two things are missing from that label:

  * "loop" in that histogram is the INNERMOST guard region, so a site inside ``for ...: if ...:
    P['k'] = v`` is published as ``conditional`` while it still executes once per iteration.  The
    real population of sites that run inside a loop is the union over every chain that mentions
    one, and the difference is not small.
  * "runs zero or more times" is not the same as "accumulates".  A loop body that writes the same
    address N times is one write repeated (last-write-wins); a body whose key or container comes
    from the loop target writes a distinct address each pass (an accumulator).  The guard label
    cannot tell those apart, and no published face prices the difference.

For every residual module-level write site whose guard chain contains a loop, this study publishes
the innermost loop that holds it (``for``/``async for``/``while``), what that loop iterates over
(literal container / module constant / call -- with zip, enumerate and range named apart /
comprehension / attribute / operator / bare name), the loop target names and whether they are an
unpack, the row key form and the container key form of the two-depth address, and whether the
address can differ between iterations.

Population and ruler are imported, not re-implemented: the two-depth site grouping and owner split
come from E638/E640, the module-context parser and bucket ruler from E643, the containment test and
the module-level guard chain from E649.  The counted row keys come from the same join E649 uses.
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
FACE = "LOOPWRITEKEY.json"
LATEST = "loopwritekey_latest.json"
STUDY = "E653_loop_guarded_write_key"
SOURCE_FACE = "results/state_tilt/GUARDEDWRITE.json"
SELF_PARTS = ("e653_", "run_e653_", "_probe_e653", "_r1676")
MAX_EXAMPLES = 8

import e638_two_depth_subscripts as e638  # noqa: E402
import e640_writeread_collide as e640  # noqa: E402
import e643_nonfunc_site as e643  # noqa: E402
import e649_guarded_write as e649  # noqa: E402

V_ABSENT = (
    "no_residual_module_level_write_site_executes_inside_a_loop,_so_the_zero_or_more_times_"
    "execution_line_has_no_members_to_price")
V_ALL_FIXED = (
    "every_loop_guarded_residual_write_repeats_one_address_per_iteration,_so_a_loop_around_a_"
    "module_level_write_is_one_write_repeated_and_never_an_accumulator")
V_ALL_VARY = (
    "every_loop_guarded_residual_write_computes_its_address_from_the_loop_target,_so_every_loop_"
    "guarded_module_level_write_accumulates_distinct_addresses_rather_than_repeating_one")
V_MIXED = (
    "the_loop_guarded_residual_is_two_write_shapes,_last_write_wins_sites_that_repeat_an_address_"
    "and_accumulators_that_write_a_distinct_address_per_iteration,_and_the_split_is_published_"
    "rather_than_absorbed_by_the_loop_label")

KEY_FORMS = ("literal", "literal_nonstring", "loop_target", "unpack_member", "computed_name",
             "computed_constant", "computed", "computed_call", "computed_member", "slice",
             "other")
ITER_FORMS = ("literal_container", "literal_constant", "module_constant", "bare_name",
              "zip_call", "enumerate_call", "range_call", "call", "comprehension",
              "attribute_or_subscript", "operator", "condition_compare", "condition_call",
              "condition_name", "other")


def say(line):
    sys.stdout.write(str(line) + "\n")


def rel(module, root=ROOT):
    return os.path.relpath(module, root).replace("\\", "/")


def holds(node, line, column):
    return e643.holds(node, line, column)


def module_bindings(tree):
    """Module-level ``NAME = <expr>`` bindings, first assignment wins (import order)."""
    out = {}
    for st in tree.body:
        targets = []
        if isinstance(st, ast.Assign):
            targets = st.targets
            value = st.value
        elif isinstance(st, ast.AnnAssign) and st.value is not None:
            targets, value = [st.target], st.value
        else:
            continue
        for t in targets:
            if isinstance(t, ast.Name):
                out.setdefault(t.id, value)
    return out


def innermost_loop(tree, line, column):
    """The innermost loop statement holding (line, column), searched module-level bodies only.

    A site inside a function is out of this population by construction (E640's owner split ran
    first), so descending into function bodies here could only produce a false attribution.
    """
    found = []

    def visit(stmts):
        for st in stmts:
            if not isinstance(st, (ast.stmt, ast.ExceptHandler)):
                continue
            if not holds(st, line, column):
                continue
            if isinstance(st, (ast.For, ast.AsyncFor, ast.While)):
                found.append(st)
            for field in ("body", "orelse", "finalbody"):
                child = getattr(st, field, None)
                if isinstance(child, list):
                    visit(child)
            if isinstance(st, ast.Try):
                visit(st.handlers)

    visit(tree.body)
    return found[-1] if found else None


def target_names(node):
    """Names a ``for`` target binds, plus whether the target is a tuple/list unpack."""
    names, unpack = [], False
    if isinstance(node, ast.Name):
        names.append(node.id)
    elif isinstance(node, (ast.Tuple, ast.List)):
        unpack = True
        for elt in node.elts:
            sub, _ = target_names(elt)
            names.extend(sub)
    elif isinstance(node, ast.Starred):
        sub, _ = target_names(node.value)
        names.extend(sub)
    return names, unpack


def iterable_form(node, bindings):
    """What a ``for`` iterates over, as a form the reader can act on."""
    if isinstance(node, (ast.List, ast.Tuple, ast.Set, ast.Dict)):
        return "literal_container"
    if isinstance(node, ast.Constant):
        return "literal_constant"
    if isinstance(node, ast.Name):
        return "module_constant" if node.id in bindings else "bare_name"
    if isinstance(node, ast.Call):
        func = node.func
        name = func.id if isinstance(func, ast.Name) else (
            func.attr if isinstance(func, ast.Attribute) else "")
        return {"zip": "zip_call", "enumerate": "enumerate_call",
                "range": "range_call"}.get(name, "call" if name else "other")
    if isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
        return "comprehension"
    if isinstance(node, (ast.Attribute, ast.Subscript)):
        return "attribute_or_subscript"
    if isinstance(node, ast.BinOp):
        return "operator"
    return "other"


def condition_form(node):
    """A ``while`` test's form -- a while loop binds no target, and the reader should see that."""
    if isinstance(node, ast.Compare):
        return "condition_compare"
    if isinstance(node, ast.Call):
        return "condition_call"
    if isinstance(node, ast.Name):
        return "condition_name"
    if isinstance(node, ast.Constant):
        return "literal_constant"
    if isinstance(node, ast.UnaryOp):
        return "condition_compare"
    return "other"


def subscript_pair(tree, line, column):
    """The outer (row-key) and inner (container-key) Subscript at exactly (line, column).

    In ``P['a']['b'] = v`` both subscripts start at the same column; E638's own depth rule tells
    them apart, so the row key is the deepest node's slice and the container key is the shallowest
    node's slice.  Returning them by depth rather than by ast.walk order keeps this the same ruler
    E638/E640 use to build the site.
    """
    nodes = [n for n in ast.walk(tree) if isinstance(n, ast.Subscript)
             and getattr(n, "lineno", None) == line
             and getattr(n, "col_offset", None) == column]
    if not nodes:
        return None, None
    outer = max(nodes, key=e638.subscript_depth)
    inner = min(nodes, key=e638.subscript_depth)
    return outer, (inner if inner is not outer else None)


def mentions(node, names):
    if node is None or not names:
        return False
    return any(isinstance(n, ast.Name) and n.id in names for n in ast.walk(node))


def key_form(sl, names, unpack):
    """The form of a subscript's slice, and whether it can differ across iterations."""
    if sl is None:
        return "other", False
    can_vary = mentions(sl, names)
    if isinstance(sl, ast.Constant):
        form = "literal" if isinstance(sl.value, str) else "literal_nonstring"
    elif isinstance(sl, ast.Name):
        if sl.id in names:
            form = "unpack_member" if unpack else "loop_target"
        else:
            form = "computed_name"
    elif isinstance(sl, (ast.BinOp, ast.JoinedStr)):
        form = "computed" if can_vary else "computed_constant"
    elif isinstance(sl, ast.Call):
        form = "computed_call"
    elif isinstance(sl, (ast.Attribute, ast.Subscript)):
        form = "computed_member" if can_vary else "computed_constant"
    elif isinstance(sl, ast.Slice):
        # a slice is an address RANGE, not a key: named apart so a range assignment is never
        # read as a key write whose form went unrecognised
        form = "slice"
    else:
        form = "other"
    return form, bool(can_vary)


def unparse(node):
    try:
        return ast.unparse(node)[:120]
    except Exception:  # noqa: BLE001 -- a form we cannot print must not stop the walk
        return ""


def counted_keys(root=ROOT):
    return e649.counted_keys(root)


def classify_site(tree, line, column, names, unpack):
    """Everything the study publishes about one write address at (line, column)."""
    outer, inner = subscript_pair(tree, line, column)
    if outer is None:
        return {"key_form": "other", "key_text": "", "container_key_form": "other",
                "container_key_text": "", "address_can_vary": False}
    kform, kvary = key_form(outer.slice, names, unpack)
    cform, cvary = key_form(inner.slice if inner is not None else None, names, unpack)
    return {"key_form": kform, "key_text": unparse(outer.slice),
            "container_key_form": cform if inner is not None else "no_inner_subscript",
            "container_key_text": unparse(inner.slice) if inner is not None else "",
            "address_can_vary": bool(kvary or cvary)}


# ---------------------------------------------------------------- measure
def measure(root=ROOT):
    files = e649.corpus(root)
    keys = counted_keys(root)
    holes = {"over_the_size_cap": 0, "unreadable": 0, "does_not_parse": 0}
    rows = []
    innermost_loop_sites = 0
    guarded_total = 0
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
        bindings = module_bindings(tree)
        for site in got["sites"]:
            if e640.innermost_owner(spans, site["line"]) is not None:
                continue
            row = e640.site_row(site)
            if not row["any_member_is_write"]:
                continue
            bucket = e643.classify(ctx, site["line"], site["column"])["bucket"]
            chain = e649.block_chain(tree, site["line"], site["column"]) \
                if bucket == "module_body" else []
            if chain and chain[-1] == "loop":
                innermost_loop_sites += 1
            if "loop" not in chain:
                continue
            guarded_total += 1
            loop = innermost_loop(tree, site["line"], site["column"])
            if loop is None:
                # a chain that says loop while no loop node holds the position would be an
                # instrument defect; the row is kept and published as such rather than dropped
                rows.append({
                    "module": rel(path, root), "line": site["line"],
                    "column": site["column"], "chain": chain,
                    "loop_kind": "unfound", "iterable_form": "other",
                    "iterable_binding": "", "target_names": [], "target_is_unpack": False,
                    "key_form": "other", "key_text": "",
                    "container_key_form": "other", "container_key_text": "",
                    "address_can_vary_across_iterations": None,
                    "write_mode": "unknown", "write_keys": e649.write_keys(row),
                    "matched_keys": [], "source": "",
                })
                continue
            if isinstance(loop, ast.While):
                loop_kind = "while"
                iter_form = condition_form(loop.test)
                binding = unparse(loop.test)
                names, unpack = [], False
            else:
                loop_kind = "async_for" if isinstance(loop, ast.AsyncFor) else "for"
                iter_form = iterable_form(loop.iter, bindings)
                binding = unparse(loop.iter)
                names, unpack = target_names(loop.target)
            addr = classify_site(tree, site["line"], site["column"], names, unpack)
            matched = sorted(set(e649.write_keys(row)) & set(keys))
            rows.append({
                "module": rel(path, root),
                "line": site["line"],
                "column": site["column"],
                "chain": chain,
                "loop_kind": loop_kind,
                "iterable_form": iter_form,
                "iterable_binding": binding,
                "target_names": names,
                "target_is_unpack": unpack,
                "key_form": addr["key_form"],
                "key_text": addr["key_text"],
                "container_key_form": addr["container_key_form"],
                "container_key_text": addr["container_key_text"],
                "address_can_vary_across_iterations": addr["address_can_vary"],
                "write_mode": ("accumulation" if addr["address_can_vary"]
                               else "last_write_wins"),
                "write_keys": e649.write_keys(row),
                "matched_keys": matched,
                "source": lines[site["line"] - 1].strip()[:160]
                if 0 < site["line"] <= len(lines) else "",
            })
    rows.sort(key=lambda r: (r["module"], r["line"], r["column"]))
    counts = counts_of(rows, len(files), holes, guarded_total, innermost_loop_sites)
    counts["source_face_loop_bucket"] = source_loop_bucket(root)
    counts["source_face_write_sites_naming_a_counted_key"] = source_counted_key_sites(root)
    counts["write_sites_the_guard_label_hid"] = guarded_total - innermost_loop_sites
    return {
        "study": STUDY,
        "date": TODAY,
        "evidence_cutoff": TODAY,
        "source_face": SOURCE_FACE,
        "deliverable": "results/state_tilt/LOOPWRITEKEY.json",
        "method": (
            "re-parse every .py in the corpus E391 walks; import E638's two-depth site grouping, "
            "E640's owner split, E643's bucket ruler and E649's module-level guard chain; keep the "
            "residual write sites whose chain mentions a loop; for each, publish the innermost "
            "loop AST node's kind, what it iterates over and its target names, plus the row-key "
            "and container-key forms of the two-depth address and whether that address can differ "
            "between iterations"),
        "population_source": (
            "%d Python files of the tree corpus; the population is every two-depth write site "
            "E640's owner split leaves without a function AND whose E649 guard chain mentions a "
            "loop" % len(files)),
        "counted_keys": keys,
        "counts": counts,
        "rows": rows,
        "examples": examples_of(rows),
        "limits": [
            "the population is E649's chain, so 'loop' means a loop region on the chain, not "
            "E649's innermost-loop histogram bucket: both numbers are published "
            "(write_sites_executing_inside_a_loop vs "
            "write_sites_whose_innermost_region_is_a_loop) and the difference is what the guard "
            "label hides",
            "'can differ across iterations' is decided syntactically: the row key or the container "
            "key mentions a name the loop target binds. A key computed from a mutable counter that "
            "is not the target (``i += 1; P[i]['k'] = v``) is published as computed_name/"
            "last_write_wins even though it also varies -- the column is a claim about the target, "
            "not about dataflow",
            "a while loop binds no target, so every address inside it is last_write_wins under "
            "this ruler even when the body mutates the key's source; the while rows are published "
            "with their test form so the reader can see the ruler's edge",
            "'accumulation' states that the ADDRESS differs, not that the values accumulate: a "
            "body writing a distinct (container,key) pair each pass overwrites nothing, which is "
            "what makes the statement an accumulator rather than a repeated write",
            "an augmented assignment and a delete count as writes exactly as they do in E640",
            "the address is read from the two Subscripts at the site position by E638's depth "
            "ruler: the deepest node's slice is the row key, the shallowest node's slice is the "
            "container key; a site with only one subscript has no container key and says so",
            "files over 1MB are skipped rather than parsed (E391's cap) and counted apart",
            "this study's own files are excluded by prefix, so a re-run cannot count itself",
        ],
        "verdict": decide(counts),
        "answer": answer_of(counts),
    }


def _source_counts(root=ROOT):
    path = os.path.join(root, SOURCE_FACE)
    try:
        with io.open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
    except (OSError, ValueError):
        return {}
    return doc.get("counts") or {}


def source_loop_bucket(root=ROOT):
    """E649's published innermost-loop bucket, machine-read from its face."""
    return (_source_counts(root).get("guard_histogram") or {}).get("loop")


def source_counted_key_sites(root=ROOT):
    """How many residual write sites E649 found naming a counted row key, read from its face."""
    return _source_counts(root).get("write_sites_naming_a_counted_key")


def counts_of(rows, files_scanned=0, holes=None, guarded_total=0, innermost=0):
    c = {
        "python_files_scanned": files_scanned,
        "write_sites_executing_inside_a_loop": guarded_total,
        "write_sites_whose_innermost_region_is_a_loop": innermost,
        "rows_published": len(rows),
        "holes": holes or {},
    }
    by_loop, by_iter, by_key, by_cont, by_mode = {}, {}, {}, {}, {}
    vary = fixed = unknown = 0
    unpack_sites = 0
    counted = 0
    for r in rows:
        by_loop[r["loop_kind"]] = by_loop.get(r["loop_kind"], 0) + 1
        by_iter[r["iterable_form"]] = by_iter.get(r["iterable_form"], 0) + 1
        by_key[r["key_form"]] = by_key.get(r["key_form"], 0) + 1
        by_cont[r["container_key_form"]] = by_cont.get(r["container_key_form"], 0) + 1
        by_mode[r["write_mode"]] = by_mode.get(r["write_mode"], 0) + 1
        if r["address_can_vary_across_iterations"] is True:
            vary += 1
        elif r["address_can_vary_across_iterations"] is False:
            fixed += 1
        else:
            unknown += 1
        if r["target_is_unpack"]:
            unpack_sites += 1
        if r["matched_keys"]:
            counted += 1
    c["write_sites_that_vary_the_address_across_iterations"] = vary
    c["write_sites_that_repeat_one_address"] = fixed
    c["write_sites_whose_address_could_not_be_read"] = unknown
    c["write_sites_the_guard_label_hid"] = (guarded_total or 0) - (innermost or 0)
    c["write_sites_with_an_unpacking_target"] = unpack_sites
    c["write_sites_naming_a_counted_row_key"] = counted
    c["loop_kind_histogram"] = dict(sorted(by_loop.items()))
    c["iterable_form_histogram"] = dict(sorted(by_iter.items()))
    c["key_form_histogram"] = dict(sorted(by_key.items()))
    c["container_key_form_histogram"] = dict(sorted(by_cont.items()))
    c["write_mode_histogram"] = dict(sorted(by_mode.items()))
    return c


def decide(c):
    if not c.get("write_sites_executing_inside_a_loop"):
        return V_ABSENT
    if not c.get("write_sites_that_vary_the_address_across_iterations"):
        return V_ALL_FIXED
    if not c.get("write_sites_that_repeat_one_address"):
        return V_ALL_VARY
    return V_MIXED


def answer_of(c):
    if not c.get("write_sites_executing_inside_a_loop"):
        return "no residual module-level write site executes inside a loop, so nothing is priced"
    total = c["write_sites_executing_inside_a_loop"]
    vary = c.get("write_sites_that_vary_the_address_across_iterations") or 0
    fixed = c.get("write_sites_that_repeat_one_address") or 0
    text = (
        "%d residual module-level write sites execute inside a loop, which is %d more than the %d "
        "E649 published under its innermost-region `loop` bucket; of those, %d (%.1f%%) compute "
        "their address from the loop target and are accumulators while %d (%.1f%%) repeat one "
        "address and are last-write-wins, so `zero or more times` is one statement and two write "
        "shapes."
        % (total, c.get("write_sites_the_guard_label_hid") or 0,
           c.get("write_sites_whose_innermost_region_is_a_loop") or 0,
           vary, 100.0 * vary / max(1, total), fixed, 100.0 * fixed / max(1, total)))
    iters = c.get("iterable_form_histogram") or {}
    if iters:
        text += " Iterables: " + ", ".join(
            "%s=%d" % (k, iters[k]) for k in sorted(iters)) + "."
    keys = c.get("key_form_histogram") or {}
    if keys:
        text += " Row-key forms: " + ", ".join(
            "%s=%d" % (k, keys[k]) for k in sorted(keys)) + "."
    return text


def examples_of(rows):
    out = {}
    for r in rows:
        got = out.setdefault(r["iterable_form"], [])
        if len(got) < MAX_EXAMPLES:
            got.append({
                "module": r["module"], "line": r["line"], "loop_kind": r["loop_kind"],
                "iterable_binding": r["iterable_binding"], "key_form": r["key_form"],
                "key_text": r["key_text"],
                "container_key_form": r["container_key_form"],
                "container_key_text": r["container_key_text"],
                "write_mode": r["write_mode"], "source": r["source"],
            })
    return {k: v for k, v in sorted(out.items()) if v}


# ---------------------------------------------------------------- gates
def live_counts(rows):
    """Every headline re-derived from the rows alone (the gate never trusts the stored counts).

    The population is the row list itself -- every row is a residual write site whose chain
    mentions a loop -- so the two population keys are read off the rows rather than carried in
    from the walk, or a stale stored count would have nothing to disagree with.
    """
    inner = sum(1 for r in rows if (r.get("chain") or []) and r["chain"][-1] == "loop")
    return counts_of(rows, files_scanned=0, guarded_total=len(rows), innermost=inner)


def face_problems(face):
    problems = []
    rows = face.get("rows") or []
    c = face.get("counts") or {}
    live = live_counts(rows)
    for key in ("write_sites_executing_inside_a_loop",
                "write_sites_that_vary_the_address_across_iterations",
                "write_sites_that_repeat_one_address",
                "write_sites_whose_address_could_not_be_read",
                "write_sites_with_an_unpacking_target",
                "write_sites_naming_a_counted_row_key",
                "write_sites_the_guard_label_hid",
                "loop_kind_histogram", "iterable_form_histogram",
                "key_form_histogram", "container_key_form_histogram",
                "write_mode_histogram"):
        if c.get(key) != live.get(key):
            problems.append("%s does not re-derive from the rows (%s vs %s)"
                            % (key, c.get(key), live.get(key)))
    if c.get("rows_published") != len(rows):
        problems.append("rows_published does not equal the row list")
    total = (live.get("write_sites_that_vary_the_address_across_iterations") or 0) + \
            (live.get("write_sites_that_repeat_one_address") or 0) + \
            (live.get("write_sites_whose_address_could_not_be_read") or 0)
    if total != len(rows):
        problems.append("the three address-variance classes do not cover the rows (%d vs %d)"
                        % (total, len(rows)))
    mode_total = sum((live.get("write_mode_histogram") or {}).values())
    if mode_total != len(rows):
        problems.append("the write-mode histogram does not cover the rows")
    if decide(live) != face.get("verdict"):
        problems.append("the verdict does not re-derive from the rows")
    if not face.get("answer"):
        problems.append("no answer published")
    for r in rows:
        if "loop" not in (r.get("chain") or []):
            problems.append("a published row's chain carries no loop: %s:%s"
                            % (r.get("module"), r.get("line")))
            break
        if r.get("address_can_vary_across_iterations") is None:
            continue
        if r["address_can_vary_across_iterations"] and r["write_mode"] != "accumulation":
            problems.append("a varying address is not published as accumulation")
            break
        if not r["address_can_vary_across_iterations"] \
                and r["write_mode"] != "last_write_wins":
            problems.append("a fixed address is not published as last-write-wins")
            break
    for r in rows:
        base = os.path.basename(str(r.get("module") or ""))
        if any(base.startswith(p) for p in SELF_PARTS):
            problems.append("a self file is inside the population")
            break
        if "\\" in str(r.get("module") or ""):
            problems.append("a row carries a backslash path")
            break
    for bucket, items in (face.get("examples") or {}).items():
        if len(items) > MAX_EXAMPLES:
            problems.append("examples for %s exceed the cap" % bucket)
            break
    if any(str(k).startswith("_") for k in c):
        problems.append("a private key leaked into the published counts")
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
    path = write_face(out_dir or OUTDIR, doc)
    say("wrote " + rel(path, root))
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
    """The part of ``counts`` a rebuild must reproduce exactly.

    ``python_files_scanned`` and ``holes`` are tree-vintage readings: this repo grows a file every
    round, so comparing them would re-red this leg for growth alone (E420/E421 family).  They are
    published and never silently dropped -- the row-derived readings below are what the gate holds
    the face to.
    """
    vintage = ("python_files_scanned", "holes")
    return {k: v for k, v in (counts or {}).items() if k not in vintage}


def verify(root=ROOT):
    """Rebuild in memory and compare the published face against it field by field."""
    face = load_face(root=root)
    fresh = measure(root)
    problems = face_problems(face)
    for key in ("rows", "examples", "verdict", "answer", "counted_keys"):
        if face.get(key) != fresh.get(key):
            problems.append("rebuild differs on %s" % key)
    if compared_counts(face.get("counts")) != compared_counts(fresh.get("counts")):
        moved = sorted(k for k in set(compared_counts(face.get("counts")))
                       | set(compared_counts(fresh.get("counts")))
                       if compared_counts(face.get("counts")).get(k)
                       != compared_counts(fresh.get("counts")).get(k))
        problems.append("rebuild differs on counts (%s)" % ", ".join(moved[:6]))
    say("verify problems=%s" % json.dumps(problems[:8], ensure_ascii=False))
    return 0 if not problems else 3


# ---------------------------------------------------------------- selftest
FIXTURE = '''\
P = {}
NAMES = ["a", "b"]

for name in NAMES:
    P[name]["rows"] = 1

for i, name in enumerate(NAMES):
    P[name]["payload"] = {"i": i}

for k, v in zip(NAMES, NAMES):
    P["shared"][k] = v

for n in range(3):
    P["fixed"]["constant"] = n

for row in [{"k": 1}]:
    P["dyn"]["%s" % row["k"]] = 2

for key in NAMES:
    if key:
        P["nest"][key] = 3

for extra in NAMES:
    P[extra.upper()]["leaf"] = 4

while NAMES:
    P["loop"]["guard"] = 5
    break

for inside in NAMES:
    Q = {}
    Q[inside]["x"] = 1


def writer():
    P["a"]["not_population"] = 1
'''


def sites_from_source(src):
    """Parse a fixture into the same row shape measure() builds, without the file corpus."""
    import tempfile

    tmp = tempfile.mkdtemp(prefix="e653_")
    path = os.path.join(tmp, "fixture_loops.py")
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(src)
    got, why = e638.file_sites(path)
    assert got is not None, why
    spans = e640.function_spans(path)
    ctx = e643.context_of_file(path)
    tree, lines = ctx["tree"], ctx["lines"]
    bindings = module_bindings(tree)
    rows = []
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
        loop = innermost_loop(tree, site["line"], site["column"])
        if loop is None:
            continue
        if isinstance(loop, ast.While):
            loop_kind, iter_form = "while", condition_form(loop.test)
            binding, names, unpack = unparse(loop.test), [], False
        else:
            loop_kind = "for"
            iter_form = iterable_form(loop.iter, bindings)
            binding = unparse(loop.iter)
            names, unpack = target_names(loop.target)
        addr = classify_site(tree, site["line"], site["column"], names, unpack)
        rows.append({
            "module": "fixture_loops.py", "line": site["line"], "column": site["column"],
            "chain": chain, "loop_kind": loop_kind, "iterable_form": iter_form,
            "iterable_binding": binding, "target_names": names,
            "target_is_unpack": unpack, "key_form": addr["key_form"],
            "key_text": addr["key_text"],
            "container_key_form": addr["container_key_form"],
            "container_key_text": addr["container_key_text"],
            "address_can_vary_across_iterations": addr["address_can_vary"],
            "write_mode": "accumulation" if addr["address_can_vary"] else "last_write_wins",
            "write_keys": e649.write_keys(row), "matched_keys": [],
            "source": lines[site["line"] - 1].strip()[:160],
        })
    rows.sort(key=lambda r: (r["line"], r["column"]))
    return rows


def selftest():
    legs = []

    def leg(name, ok, note=""):
        legs.append((name, bool(ok), note))
        say("%s %s%s" % ("PASS" if ok else "FAIL", name,
                         (" -- " + note) if note and not ok else ""))

    rows = sites_from_source(FIXTURE)

    def row_of(fragment):
        for r in rows:
            if fragment in r["source"]:
                return r
        return None

    r_plain = row_of('P[name]["rows"] = 1')
    leg("loop_target_container_is_accumulation",
        r_plain and r_plain["container_key_form"] == "loop_target"
        and r_plain["key_form"] == "literal"
        and r_plain["write_mode"] == "accumulation"
        and r_plain["loop_kind"] == "for",
        json.dumps(r_plain, ensure_ascii=False)[:240] if r_plain else "no row")
    leg("module_constant_iterable_is_named",
        r_plain and r_plain["iterable_form"] == "module_constant",
        (r_plain or {}).get("iterable_form"))
    r_enum = next((r for r in rows if "enumerate(NAMES)" in r["iterable_binding"]), None)
    leg("enumerate_call_is_named_and_unpacked",
        r_enum and r_enum["iterable_form"] == "enumerate_call"
        and r_enum["target_is_unpack"] is True
        and r_enum["container_key_form"] == "unpack_member",
        json.dumps(r_enum, ensure_ascii=False)[:240] if r_enum else "no row")
    r_zip = next((r for r in rows if "zip(NAMES, NAMES)" in r["iterable_binding"]), None)
    leg("zip_iterable_is_named_and_its_key_varies",
        r_zip and r_zip["iterable_form"] == "zip_call"
        and r_zip["key_form"] == "unpack_member"
        and r_zip["write_mode"] == "accumulation",
        json.dumps(r_zip, ensure_ascii=False)[:240] if r_zip else "no row")
    r_range = row_of('P["fixed"]["constant"] = n')
    leg("range_call_and_a_fully_literal_address_repeats",
        r_range and r_range["iterable_form"] == "range_call"
        and r_range["write_mode"] == "last_write_wins"
        and r_range["key_form"] == "literal"
        and r_range["container_key_form"] == "literal",
        json.dumps(r_range, ensure_ascii=False)[:240] if r_range else "no row")
    r_fmt = row_of('P["dyn"]["%s" % row["k"]] = 2')
    leg("percent_formatted_key_is_computed_and_varying",
        r_fmt and r_fmt["key_form"] == "computed"
        and r_fmt["write_mode"] == "accumulation",
        json.dumps(r_fmt, ensure_ascii=False)[:240] if r_fmt else "no row")
    leg("literal_container_iterable_is_named",
        r_fmt and r_fmt["iterable_form"] == "literal_container",
        (r_fmt or {}).get("iterable_form"))
    r_nested = row_of('P["nest"][key] = 3')
    leg("nested_conditional_chain_still_counts_as_loop_guarded",
        r_nested and "loop" in r_nested["chain"]
        and r_nested["chain"][-1] != "loop"
        and r_nested["write_mode"] == "accumulation",
        str((r_nested or {}).get("chain")))
    r_attr = row_of('P[extra.upper()]["leaf"] = 4')
    leg("computed_call_container_varies",
        r_attr and r_attr["container_key_form"] == "computed_call"
        and r_attr["write_mode"] == "accumulation",
        json.dumps(r_attr, ensure_ascii=False)[:240] if r_attr else "no row")
    r_while = row_of('P["loop"]["guard"] = 5')
    leg("while_loop_binds_no_target_so_its_address_is_fixed",
        r_while and r_while["loop_kind"] == "while"
        and r_while["write_mode"] == "last_write_wins",
        json.dumps(r_while, ensure_ascii=False)[:240] if r_while else "no row")
    r_inner = row_of('Q[inside]["x"] = 1')
    leg("an_inner_dict_defined_in_the_loop_is_still_a_module_level_write",
        r_inner and r_inner["write_mode"] == "accumulation",
        json.dumps(r_inner, ensure_ascii=False)[:240] if r_inner else "no row")
    leg("a_function_body_is_out_of_the_population",
        not any("not_population" in r["source"] for r in rows))

    c = counts_of(rows, files_scanned=1, guarded_total=len(rows),
                  innermost=sum(1 for r in rows if r["chain"][-1] == "loop"))
    leg("counts_readd_by_class",
        (c["write_sites_that_vary_the_address_across_iterations"]
         + c["write_sites_that_repeat_one_address"]
         + c["write_sites_whose_address_could_not_be_read"]) == len(rows))
    leg("histograms_cover_the_rows",
        all(sum(h.values()) == len(rows) for h in (
            c["write_mode_histogram"], c["loop_kind_histogram"], c["key_form_histogram"],
            c["container_key_form_histogram"], c["iterable_form_histogram"])))
    leg("verdict_is_mixed_on_a_two_shape_fixture", decide(c) == V_MIXED, decide(c))

    leg("empty_population_is_not_assessed",
        decide(counts_of([], files_scanned=1)) == V_ABSENT)
    leg("fixed_only_population_reads_as_last_write_wins",
        decide(counts_of([r for r in rows if r["write_mode"] == "last_write_wins"],
                         files_scanned=1,
                         guarded_total=sum(1 for r in rows
                                           if r["write_mode"] == "last_write_wins")))
        == V_ALL_FIXED)
    leg("varying_only_population_reads_as_accumulation",
        decide(counts_of([r for r in rows if r["write_mode"] == "accumulation"],
                         files_scanned=1,
                         guarded_total=sum(1 for r in rows
                                           if r["write_mode"] == "accumulation")))
        == V_ALL_VARY)

    inner = sum(1 for r in rows if r["chain"] and r["chain"][-1] == "loop")
    leg("innermost_loop_is_a_strict_subset_of_loop_chained_sites", inner < len(rows),
        "%d vs %d" % (inner, len(rows)))
    leg("self_exclusion_predicate",
        any(os.path.basename(__file__).startswith(p) for p in SELF_PARTS))

    # a tree that grew a file must not re-red the leg: the vintage fields are published but not
    # compared, while every row-derived reading still is
    grown = dict(c)
    grown["python_files_scanned"] = (c.get("python_files_scanned") or 0) + 1
    grown["holes"] = {"does_not_parse": 305}
    leg("a_grown_tree_is_not_a_rebuild_difference",
        compared_counts(grown) == compared_counts(c)
        and compared_counts(c).get("write_sites_the_guard_label_hid")
        == c.get("write_sites_the_guard_label_hid"))
    moved = dict(c)
    moved["write_sites_that_repeat_one_address"] = (c["write_sites_that_repeat_one_address"]
                                                    + 1)
    leg("a_moved_reading_is_a_rebuild_difference",
        compared_counts(moved) != compared_counts(c))

    ok = all(l[1] for l in legs)
    say("selftest %d/%d" % (sum(1 for l in legs if l[1]), len(legs)))
    return 0 if ok else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("build")
    sub.add_parser("check")
    sub.add_parser("verify")
    sub.add_parser("selftest")
    args = parser.parse_args(argv)
    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "check":
        return check()
    if args.cmd == "verify":
        return verify()
    if args.cmd == "build":
        rc, doc = build()
        say("verdict=%s" % doc.get("verdict"))
        say(doc.get("answer"))
        return rc
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
