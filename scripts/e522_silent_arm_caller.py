"""E522 -- which of the silent literal arms is actually read by a production caller that cannot test it?

E518 (results/state_tilt/LITERALGUARD-2026-11-08.json) published 475 literal arms whose
builder returns both a literal and a read and where nothing in the arm declares the empty
case; 402 of them sit outside entry points.  But E518 never asked whether anybody calls those
builders.  An arm that no production caller reads is a dormant hazard; an arm whose callers all
test the result before touching it is not a hazard at all, whatever the arm looks like.

So the measurement is per arm, at the call sites:

  * who calls this builder from production code, and how many sites
  * at each site: is the result bound to a name, and is that name tested by a *terminating*
    guard before the first read (the same guard rule E515 applies to empty arms)
  * if no guard: what is the first read (subscript / attribute / method / truth / handed on)
  * and can any shape test tell this arm apart from the builder's read arm at all
    (E518's distinguishability: is-None / truthiness / type / same-arity unpack / nothing)

An arm is only *readable-and-untestable* when a production caller reads it with no guard AND
the arm shares the read arm's shape, i.e. ``nothing_short_of_reading_the_values_tells_the_two_arms_apart``.

Attribution limit, published in the face: a call site cannot say which arm it will hit, so every
arm of a builder inherits that builder's production sites.  The study therefore speaks about
builders' exposure per arm, not about observed executions.

    python scripts/e522_silent_arm_caller.py run        # build + write the face
    python scripts/e522_silent_arm_caller.py check      # gate the published face (fast)
    python scripts/e522_silent_arm_caller.py verify     # re-derive from the tree and gate
    python scripts/e522_silent_arm_caller.py selftest   # fixture corpus + doctored faces
"""
from __future__ import annotations

import ast
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e515_empty_arm_cover as e515          # noqa: E402  corpus, call resolution, guards, reads
import e518_literal_guard as e518            # noqa: E402  arm risks and distinguishability

CARD = "E522-WHICH-OF-THE-402-SILENT-LITERAL-ARMS-IS-READ-BY-A-PRODUCTION-CALLER-THAT-CANNOT-TEST-IT"
STUDY = "E522_silent_arm_caller"
DATE_STAMP = "2026-11-08"
FACE_NAME = "silentarmread_latest.json"
DATED_PREFIX = "SILENTARMREAD"

# a scan that reads the tree must not read its own output
SELF_EXCLUDED = ("e522_", "run_e522", "_e522", "_r1549", "SILENTARMREAD", "silentarmread_")

UPSTREAM_FACE = "results/state_tilt/LITERALGUARD-2026-11-08.json"
UPSTREAM_STUDY = e518.STUDY

# per-site verdicts
CT_GUARDED = "a_terminating_guard_names_the_result_before_the_first_read"
CT_TESTED_IN_PLACE = "the_result_is_the_test_or_a_comparison_operand_at_the_site_itself"
CT_UNGUARDED = "the_result_is_read_in_production_with_no_terminating_guard"
CT_UNPACKED = "the_result_is_unpacked_at_the_site_so_only_its_arity_is_checked"
CT_NEVER_READ = "the_result_is_bound_to_a_name_and_never_read_again_at_this_site"
CT_HANDED = "the_result_is_handed_onward_without_being_read_here"
CT_DISCARDED = "the_result_is_dropped_without_being_used"
CT_TEST_ONLY = "the_result_is_read_only_from_a_test"
CT_UNREACHABLE = "no_corpus_caller_reaches_this_site"
SITE_VOCAB = (CT_GUARDED, CT_TESTED_IN_PLACE, CT_UNGUARDED, CT_UNPACKED, CT_NEVER_READ,
              CT_HANDED, CT_DISCARDED, CT_TEST_ONLY, CT_UNREACHABLE)

# per-arm verdicts
A_NO_CALLER = "no_production_caller_reads_this_builder_so_the_arm_is_never_exposed"
A_GUARDED = "every_production_caller_tests_the_result_before_reading_it"
A_HANDED_ON = "every_production_caller_hands_the_result_onward_without_reading_it_here"
A_RESULT_DROPPED = "every_production_caller_drops_the_result_without_reading_it"
A_UNGUARDED_TESTABLE = "a_production_caller_reads_the_result_without_a_test_but_the_shapes_would_have_told"
A_UNGUARDED_INDISTINGUISHABLE = "a_production_caller_reads_the_result_without_a_test_and_no_shape_test_could_tell_the_arms_apart"
ARM_VOCAB = (A_NO_CALLER, A_GUARDED, A_HANDED_ON, A_RESULT_DROPPED,
             A_UNGUARDED_TESTABLE, A_UNGUARDED_INDISTINGUISHABLE)

V_SOME_INDISTINGUISHABLE = "some_silent_arms_are_read_unguarded_by_a_production_caller_that_could_not_tell_them_apart"
V_ONLY_TESTABLE = "every_unguarded_silent_arm_could_have_been_told_apart_by_a_shape_test"
V_ALL_GUARDED = "every_silent_arm_with_a_production_caller_is_tested_before_it_is_read"
V_NO_CALLER = "no_silent_literal_arm_has_a_production_caller"
V_EMPTY = "the_upstream_face_carries_no_silent_arm_outside_an_entry_point"
VERDICT_VOCAB = (V_SOME_INDISTINGUISHABLE, V_ONLY_TESTABLE, V_ALL_GUARDED, V_NO_CALLER, V_EMPTY)

SHAPE_TESTABLE = (e518.D_IS_NONE, e518.D_TRUTHINESS, e518.D_TYPE, e518.D_ARITY)

READ_UNPACKED = "unpacked_into_several_names"


def _now():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _excerpt(node):
    return e515._excerpt(node)


# ------------------------------------------------------------------ upstream population
def load_upstream(root=None):
    path = os.path.join(root or ROOT, UPSTREAM_FACE)
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh), _sha256_file(path)


def population(face):
    """One row per silent literal arm of a builder that is not an entry point."""
    rows = []
    for builder in face.get("builders") or []:
        if builder.get("entry_point"):
            continue
        for arm in builder.get("literal_rows") or []:
            if arm.get("risk") != e518.R_SILENT_INDISTINGUISHABLE:
                continue
            rows.append({
                "module": builder.get("module"),
                "builder": builder.get("builder"),
                "builder_line": builder.get("line"),
                "line": arm.get("line"),
                "expr": arm.get("expr"),
                "class": arm.get("class"),
                "shape": arm.get("shape"),
                "distinguishable_by": arm.get("distinguishable_by"),
                "read_shapes": builder.get("read_shapes") or [],
                "builder_reach": builder.get("reach"),
            })
    rows.sort(key=lambda r: (r["module"] or "", r["builder"] or "", r["line"] or 0))
    return rows


def callee_map(arms):
    """(module, builder) -> what the scan needs to know about that builder."""
    out = {}
    for arm in arms:
        key = (arm["module"], arm["builder"])
        row = out.setdefault(key, {"module": arm["module"], "name": arm["builder"],
                                   "line": arm["builder_line"], "arms": 0,
                                   "shapes_testable": 0, "shapes_untestable": 0})
        row["arms"] += 1
        if arm["distinguishable_by"] in SHAPE_TESTABLE:
            row["shapes_testable"] += 1
        else:
            row["shapes_untestable"] += 1
    for row in out.values():
        # e515.resolve_call keys on (rel, name); keep the same three fields it reads
        row["rel"] = row["module"]
        row["name"] = row["name"]
        row["return_paths"] = 0
        row["returns_nothing"] = 0
        row["returns_a_value"] = 0
    return out


# ------------------------------------------------------------------ call-site scan
def corpus_rels(root=None):
    return [rel for rel in e515.corpus(root) if not rel.startswith(SELF_EXCLUDED)]


def parse(rels, root=None):
    trees, failed = [], []
    for rel in rels:
        try:
            trees.append((rel, ast.parse(e515._src(rel, root or ROOT))))
        except (SyntaxError, OSError, UnicodeDecodeError, ValueError):
            failed.append(rel)
    return trees, failed


def site_verdict(record):
    """What actually happens to the call's result at this site.

    The binding decides more than the read: ``return f()`` and ``g(f())`` hand the result on
    (the reader may be elsewhere), ``f()`` as a statement drops it, ``f()`` as a test is a test
    at the site itself, and an unpacked target checks only the arity.
    """
    if record["guard_terminates_before_the_first_read"]:
        return CT_GUARDED
    if record["reach"] == e515.REACH_TEST_ONLY:
        return CT_TEST_ONLY
    if record["reach"] == e515.REACH_ORPHAN:
        return CT_UNREACHABLE
    binding = record["binding"]
    if binding == "an_unpacked_or_tuple_target":
        return CT_UNPACKED
    if binding in ("the_test", "a_comparison_operand", "a_boolean_operand"):
        return CT_TESTED_IN_PLACE
    if binding == "discarded":
        return CT_DISCARDED
    if binding == "read_in_place":
        return CT_UNGUARDED
    if binding == "a_single_name":
        if record["read_kind"] == e515.READ_NONE:
            return CT_NEVER_READ
        if record["read_kind"] == e515.READ_HANDON:
            return CT_HANDED
        return CT_UNGUARDED
    return CT_HANDED


def scan(trees, callees):
    """Every corpus call that resolves to one of the silent-arm builders."""
    index = e515.module_index(trees)
    production_calls, test_calls = e515.call_index(trees)
    sites = []
    for rel, tree in trees:
        spans = e515.function_spans(tree)
        parents = e515.parent_map(tree)
        imports = e515.import_maps(tree)
        loads, ifs = {}, {}
        for call in [n for n in ast.walk(tree) if isinstance(n, ast.Call)]:
            resolved = e515.resolve_call(imports, call, rel, index, callees)
            if resolved is None:
                continue
            row = callees[resolved]
            func = e515.enclosing_def(spans, call.lineno)
            key = id(func)
            if key not in loads:
                loads[key] = [n for n in ast.walk(func)
                              if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)] \
                    if func is not None else []
                ifs[key] = sorted([n for n in ast.walk(func) if isinstance(n, ast.If)],
                                  key=lambda n: n.lineno) if func is not None else []
            binding, symbol, bind_node = e515.call_bindings(func, call, parents)
            reads = e515.first_reads(func, call.lineno, symbol, loads[key]) if symbol else []
            if reads:
                first = reads[0]
                read_line = first.lineno
                kind = e515.read_kind(first, parents)
                read_expression = _excerpt(parents.get(first, first))
            elif binding == "read_in_place":
                # ``f()[0]`` / ``f().items()`` -- the read is at the call itself, so there is no
                # bound name for first_reads to find; ask the parent instead of publishing "never"
                read_line = call.lineno
                kind = e515.read_kind(call, parents)
                read_expression = _excerpt(parents.get(call, call))
            elif binding == "an_unpacked_or_tuple_target":
                # the targets are unpacked, so the only thing checked is the arity
                read_line = call.lineno
                kind = READ_UNPACKED
                read_expression = _excerpt(bind_node) if bind_node is not None else ""
            else:
                read_line = call.lineno
                kind = e515.READ_NONE
                read_expression = ""
            guards = e515.terminating_guards(func, call.lineno, read_line, symbol, ifs[key])
            covering = [g for g in guards if g["terminates"]]
            record = {
                "source": rel,
                "line": call.lineno,
                "call_expression": _excerpt(call),
                "callee_module": row["module"],
                "callee": row["name"],
                "callee_line": row["line"],
                "callee_silent_arms": row["arms"],
                "enclosing_function": func.name if func is not None else None,
                "reach": e515.reach_of(func, production_calls, test_calls),
                "binding": binding,
                "bound_name": symbol,
                "read_kind": kind,
                "first_read_line": read_line,
                "first_read_expression": read_expression,
                "guards_between": guards,
                "guard_terminates_before_the_first_read": bool(covering),
                "verdict": None,
            }
            record["verdict"] = site_verdict(record)
            sites.append(record)
    sites.sort(key=lambda r: (r["callee"], r["source"], r["line"]))
    return sites


PRODUCTION_REACH = (e515.REACH_PRODUCTION, e515.REACH_MODULE)


def attribute(arms, sites):
    """Give every arm its builder's production exposure and a verdict."""
    by_callee = {}
    for site in sites:
        by_callee.setdefault((site["callee_module"], site["callee"]), []).append(site)
    rows = []
    for arm in arms:
        mine = by_callee.get((arm["module"], arm["builder"]), [])
        prod = [s for s in mine if s["reach"] in PRODUCTION_REACH]
        guarded = [s for s in prod if s["verdict"] in (CT_GUARDED, CT_TESTED_IN_PLACE)]
        unguarded = [s for s in prod if s["verdict"] in (CT_UNGUARDED, CT_UNPACKED)]
        never = [s for s in prod if s["verdict"] == CT_NEVER_READ]
        dropped = [s for s in prod if s["verdict"] in (CT_DISCARDED, CT_NEVER_READ)]
        handed = [s for s in prod if s["verdict"] == CT_HANDED]
        testable = arm["distinguishable_by"] in SHAPE_TESTABLE
        if not prod:
            verdict = A_NO_CALLER
        elif unguarded:
            verdict = A_UNGUARDED_TESTABLE if testable else A_UNGUARDED_INDISTINGUISHABLE
        elif guarded:
            verdict = A_GUARDED
        elif handed:
            verdict = A_HANDED_ON
        else:
            verdict = A_RESULT_DROPPED
        row = dict(arm)
        row.update({
            "shape_testable": testable,
            "sites_total": len(mine),
            "production_sites": len(prod),
            "guarded_sites": len(guarded),
            "unguarded_read_sites": len(unguarded),
            "never_read_sites": len(never),
            "dropped_sites": len(dropped),
            "handed_on_sites": len(handed),
            "production_callers": sorted({(s["source"] or "", s["enclosing_function"] or "")
                                          for s in prod})[:6],
            "first_unguarded_site": ({"source": unguarded[0]["source"],
                                      "line": unguarded[0]["line"],
                                      "read": unguarded[0]["first_read_expression"],
                                      "read_kind": unguarded[0]["read_kind"]}
                                     if unguarded else None),
            "verdict": verdict,
        })
        rows.append(row)
    return rows


# ------------------------------------------------------------------ face
def _count(records, key, vocab):
    got = {k: 0 for k in vocab}
    for rec in records:
        value = rec.get(key)
        if value in got:
            got[value] += 1
    return got


def _summary(arms, sites, sources, failures):
    by_arm = _count(arms, "verdict", ARM_VOCAB)
    by_site = _count(sites, "verdict", SITE_VOCAB)
    by_dist = {}
    for arm in arms:
        by_dist[arm["distinguishable_by"]] = by_dist.get(arm["distinguishable_by"], 0) + 1
    prod = [s for s in sites if s["reach"] in PRODUCTION_REACH]
    by_prod = _count(prod, "verdict", SITE_VOCAB)
    return {
        "sources_read": sources,
        "parse_failures": len(failures),
        "silent_arms_outside_entry_points": len(arms),
        "builders_carrying_them": len({(a["module"], a["builder"]) for a in arms}),
        "arms_by_verdict": by_arm,
        "arms_by_distinguishability": by_dist,
        "arms_with_a_production_caller": sum(v for k, v in by_arm.items() if k != A_NO_CALLER),
        "arms_read_unguarded_by_a_production_caller":
            by_arm[A_UNGUARDED_TESTABLE] + by_arm[A_UNGUARDED_INDISTINGUISHABLE],
        "arms_read_unguarded_and_indistinguishable": by_arm[A_UNGUARDED_INDISTINGUISHABLE],
        "arms_guarded_at_every_production_site": by_arm[A_GUARDED],
        "arms_only_handed_onward": by_arm[A_HANDED_ON],
        "arms_whose_result_is_always_dropped": by_arm[A_RESULT_DROPPED],
        "sites": len(sites),
        "production_sites": len(prod),
        "sites_by_verdict": by_site,
        "production_sites_by_verdict": by_prod,
        "production_sites_that_read_the_result_unguarded":
            by_prod[CT_UNGUARDED] + by_prod[CT_UNPACKED],
        "production_sites_that_read_the_result_unguarded_with_a_subscript_or_attribute":
            by_prod[CT_UNGUARDED],
        "production_sites_that_unpack_the_result": by_prod[CT_UNPACKED],
        "production_sites_that_have_the_result_handed_onward": by_prod[CT_HANDED],
        "production_sites_that_drop_the_result": by_prod[CT_DISCARDED] + by_prod[CT_NEVER_READ],
        "production_sites_where_a_guard_filters_the_arm":
            by_prod[CT_GUARDED] + by_prod[CT_TESTED_IN_PLACE],
    }


def _verdict(summary):
    if not summary["silent_arms_outside_entry_points"]:
        return V_EMPTY
    if not summary["arms_with_a_production_caller"]:
        return V_NO_CALLER
    if summary["arms_read_unguarded_and_indistinguishable"]:
        return V_SOME_INDISTINGUISHABLE
    if summary["arms_read_unguarded_by_a_production_caller"]:
        return V_ONLY_TESTABLE
    return V_ALL_GUARDED


def build(root=None, write=True, arms=None, sites=None, sources=None, failures=None,
          upstream_sha=None):
    root = root or ROOT
    if arms is None:
        face, sha = load_upstream(root)
        arms = population(face)
        upstream_sha = upstream_sha or sha
    callees = callee_map(arms)
    if sites is None:
        trees, failed = parse(corpus_rels(root), root)
        sites = scan(trees, callees)
        sources = len(trees) if sources is None else sources
        failures = failed if failures is None else failures
    rows = attribute(arms, sites)
    summary = _summary(rows, sites, sources or 0, failures or [])
    face = {
        "study": STUDY,
        "card": CARD,
        "title": ("which silent literal arms is read by a production caller that cannot tell them "
                  "apart from the builder's read arm"),
        "generated": _now(),
        "evidence_cutoff": DATE_STAMP,
        "population_source": ("%s::population() -- the silent literal arms of non-entry-point "
                              "builders, read from the published E518 face" % os.path.basename(__file__)),
        "upstream_face": UPSTREAM_FACE,
        "upstream_study": UPSTREAM_STUDY,
        "upstream_face_sha256": upstream_sha,
        "method_limits": [
            "a call site cannot say which arm of the builder it will hit, so every arm of a "
            "builder inherits that builder's production sites -- this is exposure per builder, "
            "not observed execution",
            "a call is attributed to a builder only when the name resolves through the same "
            "module-import rules E515 uses (a bare imported name, a module alias, or the "
            "defining module); a dynamically dispatched call is not seen",
            "guards are counted the way E515 counts them: an if-statement between the call and "
            "the first read of the bound name that ends the enclosing function on one arm",
            "an arm is 'testable' only when the published E518 distinguishability is is-None, "
            "truthiness, type or same-arity unpack; sentinel arms whose shape equals the read "
            "arm's shape are untestable by construction",
            "nothing is executed and no source is rewritten",
        ],
        "summary": summary,
        "verdict": _verdict(summary),
        "verdict_vocab": list(VERDICT_VOCAB),
        "arm_vocab": list(ARM_VOCAB),
        "site_vocab": list(SITE_VOCAB),
        "arms": rows,
        "sites": sites,
        "parse_failures": failures or [],
    }
    if write:
        write_face(face, root)
    return face


def write_face(face, root=None):
    root = root or ROOT
    outdir = os.path.join(root, "results", "state_tilt")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    dated = os.path.join(outdir, "%s-%s.json" % (DATED_PREFIX, DATE_STAMP))
    latest = os.path.join(outdir, FACE_NAME)
    text = json.dumps(face, indent=1, sort_keys=True)
    for path in (dated, latest):
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text + "\n")
    return dated


def load_face(root=None, name=None):
    path = os.path.join(root or ROOT, "results", "state_tilt", name or FACE_NAME)
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def face_problems(face, root=None):
    """Everything a consumer can check without re-walking the tree."""
    bad = []
    for key in ("study", "card", "generated", "evidence_cutoff", "population_source",
                "upstream_face", "upstream_face_sha256", "summary", "verdict", "arms", "sites",
                "method_limits", "parse_failures"):
        if key not in face:
            bad.append("the face does not publish %s" % key)
    if face.get("study") != STUDY:
        bad.append("the face is not this study")
    if not str(face.get("population_source") or "").startswith(
            "e522_silent_arm_caller.py::population()"):
        bad.append("the population_source is not this study's population function")
    if face.get("verdict") not in VERDICT_VOCAB:
        bad.append("the verdict %r is not in the vocabulary" % face.get("verdict"))
    summary = face.get("summary") or {}
    arms = face.get("arms") or []
    sites = face.get("sites") or []
    if face.get("verdict") != _verdict(summary):
        bad.append("the published verdict does not re-derive from the summary")
    if summary.get("silent_arms_outside_entry_points") != len(arms):
        bad.append("the arm population does not add up")
    if summary.get("sites") != len(sites):
        bad.append("the site population does not add up")
    by_arm = _count(arms, "verdict", ARM_VOCAB)
    if by_arm != (summary.get("arms_by_verdict") or {}):
        bad.append("the per-arm verdict counts do not re-derive")
    if sum(by_arm.values()) != len(arms):
        bad.append("the per-arm verdicts do not cover every arm")
    by_site = _count(sites, "verdict", SITE_VOCAB)
    if by_site != (summary.get("sites_by_verdict") or {}):
        bad.append("the per-site verdict counts do not re-derive")
    for arm in arms:
        for key in ("module", "builder", "line", "shape", "distinguishable_by", "verdict",
                    "production_sites", "unguarded_read_sites", "shape_testable"):
            if key not in arm:
                bad.append("arm %s:%s line %s does not publish %s"
                           % (arm.get("module"), arm.get("builder"), arm.get("line"), key))
                break
        if arm.get("verdict") == A_UNGUARDED_INDISTINGUISHABLE and arm.get("shape_testable"):
            bad.append("an arm is called untestable while its shape is testable")
        if arm.get("verdict") != A_NO_CALLER and not arm.get("production_sites"):
            bad.append("arm %s:%s claims a production caller it does not count"
                       % (arm.get("module"), arm.get("builder")))
        if arm.get("unguarded_read_sites", 0) > arm.get("production_sites", 0):
            bad.append("arm %s:%s has more unguarded reads than production sites"
                       % (arm.get("module"), arm.get("builder")))
    for site in sites:
        if site.get("verdict") != site_verdict(site):
            bad.append("site %s:%s has a verdict that does not re-derive"
                       % (site.get("source"), site.get("line")))
            break
    for site in sites:
        if site.get("verdict") == CT_UNGUARDED and site.get("read_kind") == e515.READ_NONE:
            bad.append("site %s:%s calls a result read unguarded and names no read kind"
                       % (site.get("source"), site.get("line")))
            break
    for site in sites:
        if site.get("verdict") == CT_UNPACKED and site.get("read_kind") != READ_UNPACKED:
            bad.append("site %s:%s unpacks a result without saying so"
                       % (site.get("source"), site.get("line")))
            break
    for site in sites:
        if site.get("verdict") == CT_GUARDED and not site.get("guard_terminates_before_the_first_read"):
            bad.append("a site claims a guard it does not carry")
            break
    upstream = face.get("upstream_face")
    if upstream:
        path = os.path.join(root or ROOT, upstream)
        if not os.path.isfile(path):
            bad.append("the upstream face is not on disk at %s" % upstream)
        elif _sha256_file(path) != face.get("upstream_face_sha256"):
            bad.append("the upstream face changed since this face was built -- rebuild")
    return bad


def check(face=None, root=None):
    face = face or load_face(root)
    bad = face_problems(face, root)
    print("E522 check: %d problem(s)" % len(bad))
    for line in bad[:20]:
        print("  - %s" % line)
    return 1 if bad else 0


def verify(root=None):
    published = load_face(root)
    fresh = build(root=root, write=False)
    bad = face_problems(published, root)
    for key in ("verdict", "summary"):
        if fresh["verdict"] != published["verdict"]:
            bad.append("the verdict drifts when re-derived")
            break
        if json.dumps(fresh["summary"], sort_keys=True) != json.dumps(published["summary"], sort_keys=True):
            bad.append("the summary drifts when re-derived")
            break
    print("E522 verify: %d problem(s)" % len(bad))
    for line in bad[:20]:
        print("  - %s" % line)
    return 1 if bad else 0


# ------------------------------------------------------------------ selftest
FIXTURE_BUILDER = '''
def _read_something(path):
    return open(path).read()


def sentinel_builder(path):
    if not path:
        return ""
    return _read_something(path)


def guarded_caller(path):
    value = sentinel_builder(path)
    if not value:
        return None
    return value.splitlines()


def blind_caller(path):
    value = sentinel_builder(path)
    return value.splitlines()


def test_sentinel():
    return sentinel_builder("x")


def inline_caller(path):
    return len(sentinel_builder(path).splitlines())


def main():
    guarded_caller("a")
    blind_caller("b")
    inline_caller("c")
    return 0
'''


def selftest():
    bad = []
    tmp = tempfile.mkdtemp(prefix="e522_")
    try:
        os.makedirs(os.path.join(tmp, "scripts"))
        with io.open(os.path.join(tmp, "scripts", "fixture_mod.py"), "w",
                     encoding="utf-8", newline="\n") as fh:
            fh.write(FIXTURE_BUILDER)
        face = {"builders": [
            {"module": "scripts/fixture_mod.py", "builder": "sentinel_builder", "line": 8,
             "entry_point": False, "reach": e515.REACH_PRODUCTION,
             "read_shapes": [{"shape": ["a_string", 0]}],
             "literal_rows": [
                 {"line": 10, "expr": "''", "class": e518.A_LITERAL,
                  "shape": ["a_string", 0],
                  "distinguishable_by": e518.D_NOTHING,
                  "risk": e518.R_SILENT_INDISTINGUISHABLE},
                 {"line": 9, "expr": "None", "class": e518.A_LITERAL,
                  "shape": ["none", 0],
                  "distinguishable_by": e518.D_IS_NONE,
                  "risk": e518.R_SILENT_INDISTINGUISHABLE},
                 {"line": 11, "expr": "[]", "class": e518.A_LITERAL,
                  "shape": ["a_list", 0],
                  "distinguishable_by": e518.D_TRUTHINESS,
                  "risk": e518.R_DECLARED}]},
            {"module": "scripts/fixture_mod.py", "builder": "lonely_builder", "line": 99,
             "entry_point": False, "reach": e515.REACH_ORPHAN, "read_shapes": [],
             "literal_rows": [
                 {"line": 100, "expr": "None", "class": e518.A_LITERAL,
                  "shape": ["none", 0],
                  "distinguishable_by": e518.D_NOTHING,
                  "risk": e518.R_SILENT_INDISTINGUISHABLE}]},
            {"module": "scripts/fixture_mod.py", "builder": "main", "line": 1,
             "entry_point": True, "reach": e515.REACH_PRODUCTION, "read_shapes": [],
             "literal_rows": [
                 {"line": 2, "expr": "2", "class": e518.A_LITERAL,
                  "shape": ["an_integer", 2],
                  "distinguishable_by": e518.D_TYPE,
                  "risk": e518.R_SILENT_INDISTINGUISHABLE}]},
        ]}
        arms = population(face)
        if len(arms) != 3:
            bad.append("population kept %r arms; the entry-point arm should be excluded "
                       "and the declared arm is not silent" % len(arms))
        if any(a.get("builder") == "main" for a in arms):
            bad.append("an entry-point arm survived the population filter")
        trees, failed = parse(["scripts/fixture_mod.py"], tmp)
        if failed or not trees:
            bad.append("the fixture corpus did not parse: %r" % failed)
        sites = scan(trees, callee_map(arms))
        prod = [s for s in sites if s["reach"] in PRODUCTION_REACH]
        if len(prod) != 3:
            bad.append("expected three production sites of the fixture builder, saw %r" % len(prod))
        guarded = [s for s in prod if s["verdict"] == CT_GUARDED]
        unguarded = [s for s in prod if s["verdict"] == CT_UNGUARDED]
        if len(guarded) != 1:
            bad.append("the guarded fixture caller was not seen as guarded (%r)" % len(guarded))
        if len(unguarded) != 2:
            bad.append("the blind and inline fixture callers were not seen as unguarded (%r)"
                       % len(unguarded))
        inline = [s for s in prod if s["enclosing_function"] == "inline_caller"]
        if not inline:
            bad.append("the inline caller is missing from the fixture sites")
        elif inline[0]["read_kind"] == e515.READ_NONE:
            bad.append("a read in place was published with no read kind")
        test_site = [s for s in sites if s["verdict"] == CT_TEST_ONLY]
        if len(test_site) != 1:
            bad.append("the test-only fixture caller was not separated (%r)" % len(test_site))
        rows = attribute(arms, sites)
        by = {r["expr"]: r["verdict"] for r in rows}
        if by.get("''") != A_UNGUARDED_INDISTINGUISHABLE:
            bad.append("a sentinel whose shape equals the read arm's should be untestable, saw %r"
                       % by.get("''"))
        if by.get("None") != A_UNGUARDED_TESTABLE:
            bad.append("an is-None arm read unguarded should stay testable, saw %r" % by.get("None"))
        lonely = [r for r in rows if r["builder"] == "lonely_builder"]
        if not lonely or lonely[0]["verdict"] != A_NO_CALLER:
            bad.append("a builder nobody calls should be reported as unexposed")
        # a guarded-only builder must come out guarded everywhere
        only_guarded = [dict(a, builder="sentinel_builder") for a in arms[:1]]
        only_guarded_sites = [s for s in sites if s["verdict"] == CT_GUARDED]
        if attribute(only_guarded, only_guarded_sites)[0]["verdict"] != A_GUARDED:
            bad.append("a builder with only a guarded site should be guarded everywhere")

        face2 = build(root=tmp, write=False, arms=arms, sites=sites, sources=1,
                      failures=[],
                      upstream_sha=_sha256_file(os.path.join(ROOT, UPSTREAM_FACE)))
        os.makedirs(os.path.join(tmp, "results", "state_tilt"))
        shutil.copyfile(os.path.join(ROOT, UPSTREAM_FACE),
                        os.path.join(tmp, "results", "state_tilt", os.path.basename(UPSTREAM_FACE)))
        if face2["verdict"] != V_SOME_INDISTINGUISHABLE:
            bad.append("the fixture verdict should be the indistinguishable one, saw %r"
                       % face2["verdict"])
        if face_problems(face2, tmp):
            bad.append("the fixture face is refused by its own gate: %r"
                       % face_problems(face2, tmp)[:2])
        for doctor, why in (
            (lambda f: f.__setitem__("verdict", V_ALL_GUARDED),
             "a hand-written verdict"),
            (lambda f: f["summary"].__setitem__("silent_arms_outside_entry_points", 99),
             "an edited arm count"),
            (lambda f: f["summary"]["arms_by_verdict"].__setitem__(A_UNGUARDED_TESTABLE, 0),
             "an edited arm histogram"),
            (lambda f: f["arms"][0].__setitem__("verdict", A_GUARDED),
             "an arm relabelled as guarded"),
            (lambda f: [s.__setitem__("verdict", CT_GUARDED) for s in f["sites"]
                        if s["verdict"] != CT_GUARDED][:1],
             "a site relabelled as guarded"),
            (lambda f: f.__setitem__("population_source", "hand-written"),
             "an edited population_source"),
        ):
            import copy
            hurt = copy.deepcopy(face2)
            doctor(hurt)
            if not face_problems(hurt, tmp):
                bad.append("%s survived the gate" % why)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if bad:
        print("E522 selftest: %d problem(s)" % len(bad))
        for line in bad[:20]:
            print("  - %s" % line)
        return 1
    print("E522 selftest: clean")
    return 0


# ------------------------------------------------------------------ entry
def run():
    face = build()
    s = face["summary"]
    print("E522 run: %r silent arms outside entry points in %r builders / %r sources (%r parse "
          "failures)" % (s["silent_arms_outside_entry_points"], s["builders_carrying_them"],
                         s["sources_read"], s["parse_failures"]))
    print("  arms with a production caller %r | unguarded read %r (indistinguishable %r) | "
          "guarded everywhere %r | handed onward only %r | always dropped %r | no caller %r"
          % (s["arms_with_a_production_caller"],
             s["arms_read_unguarded_by_a_production_caller"],
             s["arms_read_unguarded_and_indistinguishable"],
             s["arms_guarded_at_every_production_site"],
             s["arms_only_handed_onward"],
             s["arms_whose_result_is_always_dropped"],
             s["arms_by_verdict"][A_NO_CALLER]))
    print("  production sites %r (guarded %r, unguarded read %r, handed onward %r)"
          % (s["production_sites"], s["production_sites_where_a_guard_filters_the_arm"],
             s["production_sites_that_read_the_result_unguarded"],
             s["production_sites_that_have_the_result_handed_onward"]))
    print("  verdict %r" % face["verdict"])
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    table = {"run": run, "check": check, "verify": verify, "selftest": selftest}
    if cmd not in table:
        print(__doc__)
        return 2
    return table[cmd]()


if __name__ == "__main__":
    sys.exit(main())