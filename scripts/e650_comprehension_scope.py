"""E650 -- do the 383 comprehension-and-lambda sites of E643's residual read a counted row key,
and is the object they subscript bound in a scope of their own?

E643 published the residual of its owner split with three contexts: module body 17,337,
comprehension 342, lambda 41.  The two scoped contexts are the only members of that residual
whose *evaluation scope* is not the module: a comprehension and a lambda each run in a scope of
their own, so a name they subscript can be (a) an iteration variable the construct binds itself,
(b) a parameter of the lambda, or (c) a name that still resolves to the outer row.

Whether that matters for the counted-row read face depends on two facts nobody has measured:

  * does any of those sites subscript a *literal key* that is one of the counted row keys
    (the keys E633's counted read lines use, derived live from the same join E638/E640 share),
  * and when it does, is the object it subscripts a name the comprehension/lambda binds in its
    own scope -- a per-item read -- or a name that has to come from outside -- an outer row read
    that merely happens to sit inside a comprehension?

For every site this study publishes the construct chain, the addressable members with each
member's literal key, its leftmost base name, and whether that base is bound by the enclosing
construct's own scope, plus one class per site: no_counted_key / own_scope_only /
outer_scope_only / both_scopes / unresolved_base.  The per-context residual is reconciled against
E643's published bucket rows (machine-read from its face, never hand-copied) and the difference is
published per context rather than reconciled away.

The population (two-depth site grouping, owner split) is imported from E638/E640 and the context
ruler from E643, so this study cannot drift from the definitions it is pricing.
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
FACE = "COMPREHENSIONSCOPE.json"
LATEST = "comprehensionscope_latest.json"
STUDY = "E650_comprehension_and_lambda_scope"
SELF_PARTS = ("e650_", "run_e650_", "_probe_e650", "_r1671")
SOURCE_FACE = "results/state_tilt/NONFUNCSITE.json"
MAX_BYTES = 1024 * 1024
MAX_EXAMPLES_PER_BUCKET = 8
SCOPED_BUCKETS = ("comprehension", "lambda")
SCOPE_CLASSES = ("no_counted_key", "own_scope_only", "outer_scope_only", "both_scopes",
                 "unresolved_base")

import e391_key_name_two_meanings as e391  # noqa: E402
import e633_read_forms as e633  # noqa: E402
import e638_two_depth_subscripts as e638  # noqa: E402
import e640_writeread_collide as e640  # noqa: E402
import e643_nonfunc_site as e643  # noqa: E402

V_ABSENT = (
    "no_two_depth_site_outside_every_function_sits_in_a_comprehension_or_a_lambda,_so_the_"
    "scoped_slice_of_E643's_residual_is_empty_and_the_scope_question_is_moot_at_this_population")
V_NONE = (
    "none_of_the_comprehension_or_lambda_sites_addresses_a_literal_key_that_is_a_counted_row_key,_"
    "so_those_two_contexts_are_not_part_of_the_counted_row_read_face_at_all_and_the_scope_"
    "question_only_prices_the_bookkeeping_around_the_reads")
V_ALL_OWN = (
    "every_scoped_site_that_addresses_a_counted_row_key_subscripts_a_name_its_own_comprehension_"
    "or_lambda_binds,_so_these_are_per_item_reads_inside_a_scope_and_not_reads_of_an_outer_row")
V_ALL_OUTER = (
    "every_scoped_site_that_addresses_a_counted_row_key_subscripts_a_name_bound_outside_the_"
    "construct,_so_the_read_really_does_reach_the_outer_row_and_the_scope_is_only_where_the_"
    "subscription_is_evaluated")
V_MIXED = (
    "the_scoped_sites_that_address_a_counted_row_key_split_between_names_their_own_construct_"
    "binds_and_names_that_resolve_outside_it,_so_these_two_contexts_are_two_kinds_of_read_and_"
    "the_split_is_published_rather_than_collapsed")
V_UNRESOLVED = (
    "the_scoped_sites_that_address_a_counted_row_key_subscript_something_with_no_leftmost_name,_"
    "so_their_scope_cannot_be_read_off_the_construct_and_they_are_published_as_unresolved_rather_"
    "than_counted_on_either_side")


# ---------------------------------------------------------------- helpers
def say(line):
    sys.stdout.write(line + "\n")


def corpus(root=ROOT):
    """The Python corpus E391 walks, minus this study's own files (exclusion by prefix)."""
    out = []
    for p in e391.py_corpus(root):
        if os.path.basename(p).startswith(SELF_PARTS):
            continue
        out.append(p)
    return out


def rel(module, root=ROOT):
    return os.path.relpath(module, root).replace("\\", "/")


def target_names(node):
    """Names bound by one comprehension generator target (tuple/list/starred aware)."""
    if isinstance(node, ast.Name):
        return {node.id}
    if isinstance(node, (ast.Tuple, ast.List)):
        out = set()
        for elt in node.elts:
            out |= target_names(elt)
        return out
    if isinstance(node, ast.Starred):
        return target_names(node.value)
    return set()


def lambda_params(node):
    """Every name a lambda binds: positional, kwonly, vararg, kwarg."""
    out = set()
    a = node.args
    for arg in list(getattr(a, "posonlyargs", []) or []) + list(a.args or []) + \
            list(a.kwonlyargs or []):
        out.add(arg.arg)
    if a.vararg is not None:
        out.add(a.vararg.arg)
    if a.kwarg is not None:
        out.add(a.kwarg.arg)
    return out


def scoped_containers(ctx, line, column):
    """The comprehension/lambda containers holding the position, innermost first."""
    out = []
    for node, kind in ctx["containers"]:
        if kind not in ("comprehension", "lambda"):
            continue
        if not e643.holds(node, line, column):
            continue
        end = e643._endpos(node) or e643._pos(node)
        out.append((end[0] - e643._pos(node)[0], node, kind))
    out.sort(key=lambda item: item[0])
    return [(node, kind) for _, node, kind in out]


def own_scope_names(containers):
    """Every name the enclosing constructs bind themselves (all of them, union)."""
    names = set()
    for node, kind in containers:
        if kind == "lambda":
            names |= lambda_params(node)
        else:
            for gen in node.generators:
                names |= target_names(gen.target)
    return names


def container_chain(containers):
    out = []
    for node, kind in containers:
        out.append(kind)
    out.reverse()
    return out


def subscript_members(tree, line, column, own):
    """One entry per Subscript that starts at (line, column): key, base, ctx, own-scope flag."""
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Subscript):
            continue
        if node.lineno != line or node.col_offset != column:
            continue
        key = e633.const_str(node.slice)
        base, _depth = e633.base_of(node.value)
        out.append({
            "key": key,
            "base": base,
            "ctx": ("store" if isinstance(node.ctx, ast.Store)
                    else "del" if isinstance(node.ctx, ast.Del) else "load"),
            "base_bound_in_own_scope": bool(base and base in own),
        })
    out.sort(key=lambda m: (m["ctx"], m["key"] or "", m["base"] or ""))
    return out


def classify_scope(members, own, counted):
    """The one class per site that the gate re-derives from the members."""
    matched = [m for m in members if m["key"] is not None and m["key"] in counted]
    if not matched:
        return "no_counted_key", []
    if any(m["base"] is None for m in matched):
        return "unresolved_base", sorted({m["key"] for m in matched})
    in_own = any(m["base"] in own for m in matched)
    outside = any(m["base"] not in own for m in matched)
    if in_own and outside:
        return "both_scopes", sorted({m["key"] for m in matched})
    if in_own:
        return "own_scope_only", sorted({m["key"] for m in matched})
    return "outer_scope_only", sorted({m["key"] for m in matched})


def counted_keys(root=ROOT):
    """The row keys E633's counted read lines use, derived live from the join E638/E640 share."""
    keys = set()
    for row in e638.join_counted_lines(root):
        key = row.get("key")
        if key:
            keys.add(key)
    return sorted(keys)


# ---------------------------------------------------------------- measure
def _source_contexts(root=ROOT):
    """E643's published per-context residual, read from its face -- never hand-copied."""
    try:
        face = json.load(io.open(os.path.join(root, SOURCE_FACE), encoding="utf-8"))
    except (OSError, ValueError):
        return None
    rows = face.get("bucket_rows") or []
    sites = {}
    for row in rows:
        if row.get("bucket") in SCOPED_BUCKETS:
            sites[row["bucket"]] = int(row.get("sites") or 0)
    if not sites:
        return None
    return {"sites_by_context": sites, "face": SOURCE_FACE, "study": face.get("study")}


def measure(root=ROOT):
    files = corpus(root)
    holes = {"over_the_size_cap": 0, "unreadable": 0, "does_not_parse": 0}
    counted = set(counted_keys(root))
    rows = []
    examples = {b: [] for b in SCOPED_BUCKETS}
    bucket_sites = {}
    total_sites = 0
    nonfunc_total = 0
    for p in files:
        got, why = e638.file_sites(p)
        if got is None:
            holes[why] = holes.get(why, 0) + 1
            continue
        total_sites += len(got["sites"])
        if not got["sites"]:
            continue
        spans = e640.function_spans(p)
        ctx = e643.context_of_file(p)
        if spans is None or ctx is None:
            holes["does_not_parse"] = holes.get("does_not_parse", 0) + 1
            continue
        module = rel(p, root)
        for site in got["sites"]:
            if e640.innermost_owner(spans, site["line"]) is not None:
                continue
            nonfunc_total += 1
            cls = e643.classify(ctx, site["line"], site["column"])
            bucket_sites[cls["bucket"]] = bucket_sites.get(cls["bucket"], 0) + 1
            if cls["bucket"] not in SCOPED_BUCKETS:
                continue
            containers = scoped_containers(ctx, site["line"], site["column"])
            own = own_scope_names(containers)
            members = subscript_members(ctx["tree"], site["line"], site["column"], own)
            scope_class, matched = classify_scope(members, own, counted)
            lines = ctx["lines"]
            text = ""
            if 0 < site["line"] <= len(lines):
                text = lines[site["line"] - 1].strip()[:160]
            row = {
                "module": module,
                "line": site["line"],
                "column": site["column"],
                "bucket": cls["bucket"],
                "tag": cls["tag"],
                "chain": container_chain(containers),
                "depth_pair": site["depth_pair"],
                "constructor_chain": ">".join(container_chain(containers)),
                "own_scope_names": sorted(own),
                "members": members,
                "member_ctx": sorted({m["ctx"] for m in members}),
                "literal_keys": sorted({m["key"] for m in members if m["key"] is not None}),
                "base_names": sorted({m["base"] for m in members if m["base"]}),
                "matched_keys": matched,
                "names_a_counted_key": bool(matched),
                "scope_class": scope_class,
                "any_member_is_write": any(m["ctx"] in e640.WRITE_CTX for m in members),
                "source": text,
            }
            rows.append(row)
            block = examples[cls["bucket"]]
            if len(block) < MAX_EXAMPLES_PER_BUCKET:
                block.append({
                    "module": module, "line": site["line"], "column": site["column"],
                    "tag": cls["tag"], "chain": row["chain"], "scope_class": scope_class,
                    "members": [{"key": m["key"], "base": m["base"], "ctx": m["ctx"],
                                 "base_bound_in_own_scope": m["base_bound_in_own_scope"]}
                                for m in members],
                    "source": text,
                })
    rows.sort(key=lambda r: (r["bucket"], r["module"], r["line"], r["column"]))
    counts = counts_of(rows, len(files), holes, total_sites, nonfunc_total,
                       bucket_sites, sorted(counted))
    doc = {
        "study": STUDY,
        "date": TODAY,
        "source_face": SOURCE_FACE,
        "method": ("re-parse every .py in the corpus E391 walks, import E638's two-depth site "
                   "grouping, E640's innermost-owner split and E643's context ruler, and for every "
                   "site with no enclosing function that sits in a comprehension or a lambda "
                   "publish the construct chain, the own-scope names the construct binds, every "
                   "subscript at the site with its literal key and leftmost base, whether that "
                   "base is one of the construct's own names, and whether any key is one of the "
                   "counted row keys E633's counted read lines use"),
        "population_source": ("%d Python files of the tree corpus; the population is every "
                             "two-depth site E640's owner split leaves without a function that "
                             "E643 classifies into a comprehension or a lambda"
                             % len(files)),
        "counts": counts,
        "rows": rows,
        "examples": {b: v for b, v in examples.items() if v},
        "limits": [
            "'own scope' is the union of the names the enclosing constructs bind (comprehension "
            "generator targets and lambda parameters, all constructs on the chain); a site whose "
            "construct is the second one of a nested pair is not told apart from the first",
            "a name can be bound in the own scope and still hold an outer row (the caller can pass "
            "the row in, or the generator can iterate over rows); the published class says where "
            "the name is bound, not what object it carries at run time",
            "classic loops over a row set are module-body sites with a for-guard (E649's loop "
            "bucket), not comprehension sites, so the same per-item read pattern is priced in "
            "another bucket and is not part of these 383",
            "a subscript addressed through a call or an attribute chain publishes the leftmost "
            "name (E633's own rule) or no base at all; no base means the scope cannot be read off "
            "the construct and the site is published as unresolved_base, not guessed",
            "the key is a literal string here; a computed key (a variable, a join, an f-string) "
            "has no literal key and therefore never matches a counted key in this face (E645 and "
            "E651 price computed keys in their own arms)",
            "the exclusion list drops only this study's own files, so the sibling studies' scripts "
            "stay inside the population and the site totals are slightly larger than E643's own",
            "files over 1MB are skipped rather than parsed (E391's cap) and are counted apart",
        ],
    }
    doc["verdict"] = decide(counts)
    doc["answer"] = answer_of(counts)
    return doc


def live_counts(rows):
    """Every headline re-derived from the rows alone, so the gate cannot drift from the face."""
    by_context = {}
    by_scope = {}
    matched_hist = {}
    base_kind = {}
    sites = keyed = wrote = all_own = none_own = 0
    for row in rows:
        bucket = row.get("bucket")
        by_context[bucket] = by_context.get(bucket, 0) + 1
        scope_class = row.get("scope_class")
        by_scope[scope_class] = by_scope.get(scope_class, 0) + 1
        sites += 1
        if row.get("names_a_counted_key"):
            keyed += 1
            for key in row.get("matched_keys") or []:
                matched_hist[key] = matched_hist.get(key, 0) + 1
        if row.get("any_member_is_write"):
            wrote += 1
        binds = [m.get("base_bound_in_own_scope") for m in (row.get("members") or [])
                 if m.get("base") is not None]
        if binds and all(binds):
            all_own += 1
        if binds and not any(binds):
            none_own += 1
        for member in row.get("members") or []:
            kind = "no_leftmost_name" if member.get("base") is None else "named"
            base_kind[kind] = base_kind.get(kind, 0) + 1
    return {
        "scoped_sites": sites,
        "scoped_sites_by_context": dict(sorted(by_context.items())),
        "scoped_sites_by_scope_class": dict(sorted(by_scope.items())),
        "scoped_sites_naming_a_counted_key": keyed,
        "scoped_sites_naming_a_counted_key_histogram": dict(sorted(matched_hist.items())),
        "scoped_sites_naming_a_counted_key_in_their_own_scope": by_scope.get("own_scope_only", 0),
        "scoped_sites_naming_a_counted_key_in_an_outer_scope": by_scope.get(
            "outer_scope_only", 0),
        "scoped_sites_naming_a_counted_key_in_both_scopes": by_scope.get("both_scopes", 0),
        "scoped_sites_naming_a_counted_key_through_no_leftmost_name": by_scope.get(
            "unresolved_base", 0),
        "scoped_sites_whose_subscripted_names_are_all_bound_in_the_construct": all_own,
        "scoped_sites_whose_subscripted_names_are_all_bound_outside_the_construct": none_own,
        "scoped_write_sites": wrote,
        "member_base_kind_histogram": dict(sorted(base_kind.items())),
        "scope_classes_measured_with_no_site": [c for c in SCOPE_CLASSES if c not in by_scope],
    }


def counts_of(rows, files_scanned=0, holes=None, total_sites=None,
              sites_without_an_owner_function=0, bucket_sites=None, keys=None):
    holes = holes or {}
    c = live_counts(rows)
    c["python_files_scanned"] = files_scanned
    c["python_files_over_the_size_cap"] = int(holes.get("over_the_size_cap") or 0)
    c["python_files_unreadable"] = int(holes.get("unreadable") or 0)
    c["python_files_that_do_not_parse"] = int(holes.get("does_not_parse") or 0)
    c["two_depth_sites"] = total_sites
    c["sites_without_an_owner_function"] = sites_without_an_owner_function
    c["non_function_sites_by_context"] = dict(sorted((bucket_sites or {}).items()))
    c["counted_keys"] = list(keys or [])
    source = _source_contexts()
    if source:
        c["source_face_sites_by_context"] = source["sites_by_context"]
        c["delta_vs_source_face_by_context"] = {
            b: c["scoped_sites_by_context"].get(b, 0) - n
            for b, n in source["sites_by_context"].items()
        }
        c["delta_vs_source_face"] = sum(c["delta_vs_source_face_by_context"].values())
        c["source_face_study"] = source["study"]
    return c


def decide(c):
    total = c.get("scoped_sites") or 0
    if not total:
        return V_ABSENT
    keyed = c.get("scoped_sites_naming_a_counted_key") or 0
    if not keyed:
        return V_NONE
    own = c.get("scoped_sites_naming_a_counted_key_in_their_own_scope") or 0
    outer = c.get("scoped_sites_naming_a_counted_key_in_an_outer_scope") or 0
    both = c.get("scoped_sites_naming_a_counted_key_in_both_scopes") or 0
    unresolved = c.get("scoped_sites_naming_a_counted_key_through_no_leftmost_name") or 0
    if unresolved == keyed:
        return V_UNRESOLVED
    if own == keyed:
        return V_ALL_OWN
    if outer == keyed:
        return V_ALL_OUTER
    if own or outer or both:
        return V_MIXED
    return V_UNRESOLVED


def answer_of(c):
    def n(key):
        return int(c.get(key) or 0)
    return ("%d files, %d scoped site(s) (contexts %s; %d of the %d no-owner sites); %d name a "
            "counted key %s of keys %s; scope classes %s; %d own-scope / %d outer-scope / %d "
            "both / %d unresolved; %d scoped site(s) write; member bases %s; delta vs E643's "
            "published per-context residual: %s"
            % (n("python_files_scanned"), n("scoped_sites"),
               json.dumps(c.get("scoped_sites_by_context") or {}, sort_keys=True),
               n("scoped_sites"), n("sites_without_an_owner_function"),
               n("scoped_sites_naming_a_counted_key"),
               json.dumps(c.get("scoped_sites_naming_a_counted_key_histogram") or {},
                          sort_keys=True),
               json.dumps(c.get("counted_keys") or []),
               json.dumps(c.get("scoped_sites_by_scope_class") or {}, sort_keys=True),
               n("scoped_sites_naming_a_counted_key_in_their_own_scope"),
               n("scoped_sites_naming_a_counted_key_in_an_outer_scope"),
               n("scoped_sites_naming_a_counted_key_in_both_scopes"),
               n("scoped_sites_naming_a_counted_key_through_no_leftmost_name"),
               n("scoped_write_sites"),
               json.dumps(c.get("member_base_kind_histogram") or {}, sort_keys=True),
               json.dumps(c.get("delta_vs_source_face_by_context") or {}, sort_keys=True)))


COUNT_KEYS = (
    "scoped_sites", "scoped_sites_by_context", "scoped_sites_by_scope_class",
    "scoped_sites_naming_a_counted_key", "scoped_sites_naming_a_counted_key_histogram",
    "scoped_sites_naming_a_counted_key_in_their_own_scope",
    "scoped_sites_naming_a_counted_key_in_an_outer_scope",
    "scoped_sites_naming_a_counted_key_in_both_scopes",
    "scoped_sites_naming_a_counted_key_through_no_leftmost_name",
    "scoped_sites_whose_subscripted_names_are_all_bound_in_the_construct",
    "scoped_sites_whose_subscripted_names_are_all_bound_outside_the_construct",
    "scoped_write_sites", "member_base_kind_histogram", "scope_classes_measured_with_no_site",
)


def face_problems(face):
    """Everything the smoke leg refuses, re-derived from the face's own rows."""
    problems = []
    if not face:
        return ["face is absent or empty"]
    rows = face.get("rows") or []
    c = face.get("counts") or {}
    keys = set(c.get("counted_keys") or [])
    live = live_counts(rows)
    for key in COUNT_KEYS:
        if c.get(key) != live.get(key):
            problems.append("counts.%s does not re-add from the rows" % key)
    if decide(live) != face.get("verdict"):
        problems.append("the published verdict is not the one the rows force")
    for row in rows:
        where = "%s:%s" % (row.get("module"), row.get("line"))
        if row.get("bucket") not in SCOPED_BUCKETS:
            problems.append("row %s carries a bucket outside the two scoped kinds" % where)
            break
        members = row.get("members") or []
        own = set(row.get("own_scope_names") or [])
        if not members:
            problems.append("row %s carries no subscript member" % where)
            break
        for member in members:
            want = bool(member.get("base") and member.get("base") in own)
            if bool(member.get("base_bound_in_own_scope")) != want:
                problems.append("row %s publishes an own-scope flag that its own names refute"
                                % where)
                break
        matched = sorted({m.get("key") for m in members
                          if m.get("key") is not None and m.get("key") in keys})
        if matched != sorted(row.get("matched_keys") or []):
            problems.append("row %s publishes matched keys that are not its counted-key members"
                            % where)
            break
        if bool(row.get("matched_keys")) != bool(row.get("names_a_counted_key")):
            problems.append("row %s has a key-match flag that disagrees with its keys" % where)
            break
        label, _matched = classify_scope(members, own, keys)
        if row.get("scope_class") != label:
            problems.append("row %s publishes a scope class its members do not force" % where)
            break
        if row.get("scope_class") not in SCOPE_CLASSES:
            problems.append("row %s publishes an unknown scope class" % where)
            break
        if set(row.get("literal_keys") or []) != {
                m.get("key") for m in members if m.get("key") is not None}:
            problems.append("row %s publishes literal keys that are not its members' keys" % where)
            break
        if set(row.get("base_names") or []) != {m.get("base") for m in members if m.get("base")}:
            problems.append("row %s publishes base names that are not its members' bases" % where)
            break
        if row.get("constructor_chain") and row.get("constructor_chain") != ">".join(
                row.get("chain") or []):
            problems.append("row %s publishes a chain that is not its construct chain" % where)
            break
        if row.get("any_member_is_write") != any(
                m.get("ctx") in e640.WRITE_CTX for m in members):
            problems.append("row %s publishes a write flag its members do not force" % where)
            break
    sums = sum((live.get("scoped_sites_by_context") or {}).values())
    if sums != (live.get("scoped_sites") or 0):
        problems.append("the per-context counts do not add up to the scoped total")
    if sum((live.get("scoped_sites_by_scope_class") or {}).values()) != (
            live.get("scoped_sites") or 0):
        problems.append("the scope-class histogram does not add up to the scoped total")
    keyed = live.get("scoped_sites_naming_a_counted_key") or 0
    parts = (live.get("scoped_sites_naming_a_counted_key_in_their_own_scope") or 0) + \
            (live.get("scoped_sites_naming_a_counted_key_in_an_outer_scope") or 0) + \
            (live.get("scoped_sites_naming_a_counted_key_in_both_scopes") or 0) + \
            (live.get("scoped_sites_naming_a_counted_key_through_no_leftmost_name") or 0)
    if parts != keyed:
        problems.append("the counted-key scope classes do not add up to the counted-key sites")
    if "delta_vs_source_face_by_context" in c:
        want = 0
        for bucket, n in (c.get("source_face_sites_by_context") or {}).items():
            want += (live.get("scoped_sites_by_context") or {}).get(bucket, 0) - n
        if (c.get("delta_vs_source_face") or 0) != want:
            problems.append("the delta against the source face is not the per-context difference")
    for bucket, block in (face.get("examples") or {}).items():
        if bucket not in SCOPED_BUCKETS:
            problems.append("examples publish an unknown bucket %s" % bucket)
            break
        for row in block:
            if row.get("scope_class") not in SCOPE_CLASSES:
                problems.append("an example publishes an unknown scope class")
                break
    if face.get("verdict") == V_ABSENT and rows:
        problems.append("the absent verdict is published while rows carry scoped sites")
    if face.get("verdict") == V_NONE and keyed:
        problems.append("the none verdict is published with a counted-key site")
    if face.get("verdict") == V_ALL_OWN and (
            (live.get("scoped_sites_naming_a_counted_key_in_an_outer_scope") or 0) or
            (live.get("scoped_sites_naming_a_counted_key_in_both_scopes") or 0)):
        problems.append("the all-own verdict is published with an outer-scope site")
    if face.get("verdict") == V_ALL_OUTER and (
            (live.get("scoped_sites_naming_a_counted_key_in_their_own_scope") or 0) or
            (live.get("scoped_sites_naming_a_counted_key_in_both_scopes") or 0)):
        problems.append("the all-outer verdict is published with an own-scope site")
    if face.get("verdict") == V_MIXED and not (
            ((live.get("scoped_sites_naming_a_counted_key_in_their_own_scope") or 0) and
             (live.get("scoped_sites_naming_a_counted_key_in_an_outer_scope") or 0)) or
            (live.get("scoped_sites_naming_a_counted_key_in_both_scopes") or 0)):
        problems.append("the mixed verdict is published while only one scope class is populated")
    return problems


def write_face(out_dir, doc, face=FACE, latest=LATEST):
    os.makedirs(out_dir, exist_ok=True)
    for name in (face, latest):
        path = os.path.join(out_dir, name)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
        say("run: %s" % os.path.relpath(path, ROOT))


def build(root=ROOT, out_dir=None):
    doc = measure(root)
    write_face(out_dir or OUTDIR, doc)
    c = doc["counts"]
    say("run: files=%d scoped=%d keyed=%d own=%d outer=%d both=%d unresolved=%d"
        % (c["python_files_scanned"], c["scoped_sites"],
           c["scoped_sites_naming_a_counted_key"],
           c["scoped_sites_naming_a_counted_key_in_their_own_scope"],
           c["scoped_sites_naming_a_counted_key_in_an_outer_scope"],
           c["scoped_sites_naming_a_counted_key_in_both_scopes"],
           c["scoped_sites_naming_a_counted_key_through_no_leftmost_name"]))
    say("run: verdict=" + doc["verdict"])
    say("run: answer=" + doc["answer"])
    return doc, []


# ---------------------------------------------------------------- selftest
FIXTURE_SRC = '''\
ROWS = {"a": {"b": 1}, "c": {"d": 2}}
OUTER = {"days": {"x": 1}, "verdict": {"y": 2}}

BY_ITEM = {k: v["days"]["x"] for k, v in OUTER.items()}
BY_OUTER = {k: OUTER["days"]["x"] for k in ("1", "2")}
NESTED = [[v["verdict"]["y"] for v in OUTER.values()] for k in ("3",)]
LAM_ITEM = lambda r: r["days"]["x"]
LAM_OUTER = lambda r: OUTER["days"]["x"]
LAM_DEEP = lambda r: OUTER["verdict"]["y"]
COMPUTED = {k: v[KEYNAME]["x"] for k, v in OUTER.items()}
STORE = [(OUTER["days"].__setitem__("x", 1) or k) for k in ("4",)]
'''


def _fixture(source=FIXTURE_SRC):
    import tempfile
    fd, path = tempfile.mkstemp(suffix=".py")
    os.close(fd)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(source)
    try:
        payload, why = e638.file_sites(path)
        assert why is None, why
        return e643.context_of_file(path), payload, e640.function_spans(path)
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


def _scoped_at(source, needle, nth=0, counted=("days", "verdict")):
    """Facts for the nth scoped site whose source line contains ``needle`` (fixtures by text)."""
    ctx, got, spans = _fixture(source)
    hits = [s for s in got["sites"]
            if needle in (ctx["lines"][s["line"] - 1] if s["line"] <= len(ctx["lines"]) else "")]
    site = hits[nth]
    cls = e643.classify(ctx, site["line"], site["column"])
    containers = scoped_containers(ctx, site["line"], site["column"])
    own = own_scope_names(containers)
    members = subscript_members(ctx["tree"], site["line"], site["column"], own)
    scope_class, matched = classify_scope(members, own, set(counted))
    owner = e640.innermost_owner(spans, site["line"])
    return {"bucket": cls["bucket"], "chain": container_chain(containers), "own": own,
            "members": members, "scope_class": scope_class, "matched": matched,
            "owner": owner, "site": site, "tag": cls["tag"]}


def _row(bucket="comprehension", scope_class="no_counted_key", matched=(), members=None,
         own=(), write=False, chain=None):
    members = members if members is not None else []
    return {
        "module": "a.py", "line": 1, "column": 0, "bucket": bucket,
        "tag": bucket, "chain": list(chain if chain is not None else [bucket]),
        "constructor_chain": ">".join(chain if chain is not None else [bucket]),
        "depth_pair": "2->3", "own_scope_names": sorted(own), "members": members,
        "member_ctx": sorted({m.get("ctx") for m in members}),
        "literal_keys": sorted({m.get("key") for m in members if m.get("key") is not None}),
        "base_names": sorted({m.get("base") for m in members if m.get("base")}),
        "matched_keys": list(matched), "names_a_counted_key": bool(matched),
        "scope_class": scope_class, "any_member_is_write": bool(write), "source": "",
    }


def _member(key="days", base="v", own=True, ctx="load"):
    return {"key": key, "base": base, "ctx": ctx, "base_bound_in_own_scope": bool(own)}


def _sound_face(rows, counted=("days", "verdict")):
    c = live_counts(rows)
    c["counted_keys"] = list(counted)
    return {"rows": rows, "counts": c, "verdict": decide(c), "examples": {}}


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

    def a_comprehension_body_site_is_a_comprehension_site():
        got = _scoped_at(FIXTURE_SRC, 'v["days"]["x"] for k, v')
        assert got["owner"] is None, got["owner"]
        assert got["bucket"] == "comprehension", got

    def a_comprehension_binds_its_own_generator_targets():
        got = _scoped_at(FIXTURE_SRC, 'v["days"]["x"] for k, v')
        assert got["own"] == {"k", "v"}, got["own"]
        assert got["chain"] == ["comprehension"], got["chain"]

    def an_own_scope_read_is_published_as_own_scope():
        got = _scoped_at(FIXTURE_SRC, 'v["days"]["x"] for k, v')
        assert got["scope_class"] == "own_scope_only", got["scope_class"]
        assert got["matched"] == ["days"], got["matched"]

    def an_outer_scope_read_is_published_as_outer_scope():
        got = _scoped_at(FIXTURE_SRC, 'OUTER["days"]["x"] for k in')
        assert got["own"] == {"k"}, got["own"]
        assert got["scope_class"] == "outer_scope_only", got["scope_class"]
        assert got["matched"] == ["days"], got["matched"]

    def a_lambda_parameter_is_an_own_scope_name():
        got = _scoped_at(FIXTURE_SRC, "LAM_ITEM")
        assert got["bucket"] == "lambda" and got["own"] == {"r"}, got
        assert got["scope_class"] == "own_scope_only", got["scope_class"]

    def a_lambda_over_an_outer_name_is_outer_scope():
        got = _scoped_at(FIXTURE_SRC, "LAM_OUTER")
        assert got["bucket"] == "lambda", got
        assert got["scope_class"] == "outer_scope_only", got["scope_class"]
        assert got["matched"] == ["days"], got["matched"]

    def a_nested_site_publishes_the_whole_construct_chain():
        got = _scoped_at(FIXTURE_SRC, 'v["verdict"]["y"] for v')
        assert got["chain"] == ["comprehension", "comprehension"], got["chain"]
        assert got["own"] == {"k", "v"}, got["own"]
        assert got["scope_class"] == "own_scope_only", got

    def a_fixture_site_with_two_distinct_depths_is_a_site():
        got = _scoped_at(FIXTURE_SRC, "LAM_DEEP")
        assert got["bucket"] == "lambda", got
        assert [m["key"] for m in got["members"]] == ["verdict", "y"], got["members"]
        assert got["scope_class"] == "outer_scope_only", got["scope_class"]

    def a_key_outside_the_counted_set_is_not_a_match():
        got = _scoped_at(FIXTURE_SRC, 'v["days"]["x"] for k, v', counted=("verdict",))
        assert got["matched"] == [] and got["scope_class"] == "no_counted_key", got

    def a_computed_key_has_no_literal_and_so_no_match():
        got = _scoped_at(FIXTURE_SRC, 'v[KEYNAME]["x"]')
        assert any(m["key"] is None for m in got["members"]), got["members"]
        assert got["scope_class"] == "no_counted_key", got["scope_class"]

    def a_base_with_no_leftmost_name_is_unresolved_not_guessed():
        members = [_member(key="days", base=None, own=False)]
        label, matched = classify_scope(members, {"v"}, {"days"})
        assert label == "unresolved_base", (label, matched)
        assert matched == ["days"], matched

    def two_members_in_two_scopes_are_both_scopes():
        members = [_member(key="days", base="v", own=True),
                   _member(key="verdict", base="OUTER", own=False)]
        label, matched = classify_scope(members, {"v"}, {"days", "verdict"})
        assert label == "both_scopes", label
        assert matched == ["days", "verdict"], matched

    def a_write_member_is_flagged_but_scoped_sites_are_still_sites():
        members = [_member(key="days", base="v", own=True, ctx="store")]
        row = _row(scope_class="own_scope_only", matched=["days"], members=members,
                   own=["v"], write=True)
        c = live_counts([row])
        assert c["scoped_write_sites"] == 1, c["scoped_write_sites"]

    def target_names_handles_tuples_and_stars():
        tree = ast.parse("for (a, *b) in x:\n    pass\n")
        target = tree.body[0].target
        assert target_names(target) == {"a", "b"}, target_names(target)

    def lambda_params_cover_vararg_and_kwarg():
        node = ast.parse("f = lambda a, *b, c=1, **d: 0\n").body[0].value
        assert lambda_params(node) == {"a", "b", "c", "d"}, lambda_params(node)

    def the_absent_verdict_needs_an_empty_population():
        c = live_counts([])
        assert decide(c) == V_ABSENT, decide(c)

    def the_none_verdict_needs_zero_counted_key_sites():
        c = live_counts([_row(scope_class="no_counted_key",
                              members=[_member(key="other", base="v")], own=["v"])])
        assert decide(c) == V_NONE, decide(c)

    def the_all_own_verdict_needs_every_keyed_site_in_own_scope():
        c = live_counts([_row(scope_class="own_scope_only", matched=["days"],
                              members=[_member(key="days", base="v")], own=["v"])])
        assert decide(c) == V_ALL_OWN, decide(c)

    def the_all_outer_verdict_needs_every_keyed_site_outside():
        c = live_counts([_row(scope_class="outer_scope_only", matched=["days"],
                              members=[_member(key="days", base="OUTER", own=False)])])
        assert decide(c) == V_ALL_OUTER, decide(c)

    def the_mixed_verdict_needs_two_populated_scope_classes():
        rows = [_row(scope_class="own_scope_only", matched=["days"],
                     members=[_member(key="days", base="v")], own=["v"]),
                _row(scope_class="outer_scope_only", matched=["days"],
                     members=[_member(key="days", base="OUTER", own=False)])]
        assert decide(live_counts(rows)) == V_MIXED, decide(live_counts(rows))

    def the_unresolved_verdict_needs_every_keyed_site_without_a_base():
        rows = [_row(scope_class="unresolved_base", matched=["days"],
                     members=[_member(key="days", base=None, own=False)])]
        assert decide(live_counts(rows)) == V_UNRESOLVED, decide(live_counts(rows))

    def a_sound_face_passes_its_own_gate():
        rows = [_row(scope_class="own_scope_only", matched=["days"],
                     members=[_member(key="days", base="v")], own=["v"])]
        face = _sound_face(rows)
        assert face_problems(face) == [], face_problems(face)

    def face_problems_catches_a_count_that_does_not_re_add():
        rows = [_row(scope_class="no_counted_key", members=[_member(key="other", base="v")],
                     own=["v"])]
        face = _sound_face(rows)
        face["counts"]["scoped_sites"] = 5
        assert any("does not re-add" in p for p in face_problems(face)), face_problems(face)

    def face_problems_catches_a_matched_key_outside_the_counted_set():
        rows = [_row(scope_class="own_scope_only", matched=["other"],
                     members=[_member(key="other", base="v")], own=["v"])]
        face = _sound_face(rows)
        assert any("counted-key members" in p for p in face_problems(face)), face_problems(face)

    def face_problems_catches_a_scope_class_the_members_refute():
        rows = [_row(scope_class="outer_scope_only", matched=["days"],
                     members=[_member(key="days", base="v", own=True)], own=["v"])]
        face = _sound_face(rows)
        assert any("scope class its members do not force" in p for p in face_problems(face)), \
            face_problems(face)

    def face_problems_catches_an_own_scope_flag_the_names_refute():
        rows = [_row(scope_class="own_scope_only", matched=["days"],
                     members=[_member(key="days", base="v", own=False)], own=["v"])]
        face = _sound_face(rows)
        assert any("own-scope flag" in p for p in face_problems(face)), face_problems(face)

    def face_problems_catches_a_verdict_the_rows_do_not_force():
        rows = [_row(scope_class="no_counted_key", members=[_member(key="other", base="v")],
                     own=["v"])]
        face = _sound_face(rows)
        face["verdict"] = V_ALL_OWN
        assert any("not the one the rows force" in p for p in face_problems(face)), \
            face_problems(face)

    def face_problems_catches_a_bucket_outside_the_two_kinds():
        rows = [_row(bucket="module_body", scope_class="no_counted_key",
                     members=[_member(key="other", base="v")], own=["v"], chain=[])]
        face = _sound_face(rows)
        face["counts"] = live_counts(rows)
        assert any("bucket outside" in p for p in face_problems(face)), face_problems(face)

    def face_problems_catches_scope_class_sums_that_do_not_add_up():
        rows = [_row(scope_class="own_scope_only", matched=["days"],
                     members=[_member(key="days", base="v")], own=["v"])]
        face = _sound_face(rows)
        face["counts"]["scoped_sites_by_scope_class"] = {"own_scope_only": 2}
        assert any("scoped_sites_by_scope_class" in p for p in face_problems(face)), \
            face_problems(face)

    def answer_names_the_numbers():
        c = live_counts([_row(scope_class="own_scope_only", matched=["days"],
                              members=[_member(key="days", base="v")], own=["v"])])
        c["counted_keys"] = ["days"]
        text = answer_of(c)
        assert "1 scoped site" in text and "own_scope_only" in text, text

    for name, fn in [
        ("a_comprehension_body_site_is_a_comprehension_site",
         a_comprehension_body_site_is_a_comprehension_site),
        ("a_comprehension_binds_its_own_generator_targets",
         a_comprehension_binds_its_own_generator_targets),
        ("an_own_scope_read_is_published_as_own_scope",
         an_own_scope_read_is_published_as_own_scope),
        ("an_outer_scope_read_is_published_as_outer_scope",
         an_outer_scope_read_is_published_as_outer_scope),
        ("a_lambda_parameter_is_an_own_scope_name", a_lambda_parameter_is_an_own_scope_name),
        ("a_lambda_over_an_outer_name_is_outer_scope", a_lambda_over_an_outer_name_is_outer_scope),
        ("a_nested_site_publishes_the_whole_construct_chain",
         a_nested_site_publishes_the_whole_construct_chain),
        ("a_fixture_site_with_two_distinct_depths_is_a_site",
         a_fixture_site_with_two_distinct_depths_is_a_site),
        ("a_key_outside_the_counted_set_is_not_a_match", a_key_outside_the_counted_set_is_not_a_match),
        ("a_computed_key_has_no_literal_and_so_no_match",
         a_computed_key_has_no_literal_and_so_no_match),
        ("a_base_with_no_leftmost_name_is_unresolved_not_guessed",
         a_base_with_no_leftmost_name_is_unresolved_not_guessed),
        ("two_members_in_two_scopes_are_both_scopes", two_members_in_two_scopes_are_both_scopes),
        ("a_write_member_is_flagged_but_scoped_sites_are_still_sites",
         a_write_member_is_flagged_but_scoped_sites_are_still_sites),
        ("target_names_handles_tuples_and_stars", target_names_handles_tuples_and_stars),
        ("lambda_params_cover_vararg_and_kwarg", lambda_params_cover_vararg_and_kwarg),
        ("the_absent_verdict_needs_an_empty_population", the_absent_verdict_needs_an_empty_population),
        ("the_none_verdict_needs_zero_counted_key_sites", the_none_verdict_needs_zero_counted_key_sites),
        ("the_all_own_verdict_needs_every_keyed_site_in_own_scope",
         the_all_own_verdict_needs_every_keyed_site_in_own_scope),
        ("the_all_outer_verdict_needs_every_keyed_site_outside",
         the_all_outer_verdict_needs_every_keyed_site_outside),
        ("the_mixed_verdict_needs_two_populated_scope_classes",
         the_mixed_verdict_needs_two_populated_scope_classes),
        ("the_unresolved_verdict_needs_every_keyed_site_without_a_base",
         the_unresolved_verdict_needs_every_keyed_site_without_a_base),
        ("a_sound_face_passes_its_own_gate", a_sound_face_passes_its_own_gate),
        ("face_problems_catches_a_count_that_does_not_re_add",
         face_problems_catches_a_count_that_does_not_re_add),
        ("face_problems_catches_a_matched_key_outside_the_counted_set",
         face_problems_catches_a_matched_key_outside_the_counted_set),
        ("face_problems_catches_a_scope_class_the_members_refute",
         face_problems_catches_a_scope_class_the_members_refute),
        ("face_problems_catches_an_own_scope_flag_the_names_refute",
         face_problems_catches_an_own_scope_flag_the_names_refute),
        ("face_problems_catches_a_verdict_the_rows_do_not_force",
         face_problems_catches_a_verdict_the_rows_do_not_force),
        ("face_problems_catches_a_bucket_outside_the_two_kinds",
         face_problems_catches_a_bucket_outside_the_two_kinds),
        ("face_problems_catches_scope_class_sums_that_do_not_add_up",
         face_problems_catches_scope_class_sums_that_do_not_add_up),
        ("answer_names_the_numbers", answer_names_the_numbers),
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