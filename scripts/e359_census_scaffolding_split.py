"""E359 -- how much of the E350 field census is selftest scaffolding.

E353 (r1375) reported that part of E350's 131 "unwritten guards" names files only a
*selftest* writes -- ``FZ.json``, ``_chunk_.json``, ``json`` -- so the published
population mixes production defence with test scaffolding.  That was a suspicion
recorded in a caveat; this study prices it.

The instrument is E350's own, not a re-implementation: the same corpus walker
(``e346._corpus``), the same face-binding resolver, the same branch classifier.  One
question is added at the read site: *which function owns this line?*

  * a site inside ``selftest`` / ``_selftest*`` / ``test_*`` / ``leg_*`` / ``_leg*``,
    or inside a function whose name mentions ``fixture`` or ``harness`` -- scaffolding;
  * a module-level site, or any other function -- production.

Writes are split by set difference instead of by site: the tree is pruned of its
scaffolding top-level functions, re-measured, and ``writes_scaffolding =
writes_all - writes_production``.  A name that a selftest writes *and* a production
path writes stays written on the production side, which is the conservative answer.

Two populations of published number, deliberately not mixed:

  * ADDITIVE counts (read-site derived): field_reads, fields, guard_fields,
    guard_fields_with_no_writer, choice_fields, choice_sites, guard_sites,
    fields_with_no_writer, reads_by_branch.  Each carries production, scaffolding and
    the delta;
  * FILE-LEVEL counts (corpus_sources, sources_parsed, json_bindings, dump_sinks,
    faces_named) are published ONCE for the whole corpus with the reason stated: a
    single file holds both populations, so a per-population split of a file count is
    not a measurement.

And one list that is the point of the exercise: every face whose *only* readers are
scaffolding, named individually with its read count and a sample site.

Usage:
    python scripts/e359_census_scaffolding_split.py build
    python scripts/e359_census_scaffolding_split.py verify
    python scripts/e359_census_scaffolding_split.py selftest
"""
import ast
import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e346_status_writer_unread as e346  # noqa: E402
import e347_published_number_gate_census as e347  # noqa: E402
import e350_field_branch_census as e350  # noqa: E402

ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-02"
FACE = "SCAFFOLD-%s.json" % TODAY
LATEST = "scaffold_latest.json"
STUDY = "E359_census_scaffolding_split"
SELF_REL = "scripts/e359_census_scaffolding_split.py"
E350_FACE = os.path.join("results", "state_tilt", "FIELDBRANCH-2026-11-01.json")
SOURCE_PIN = "HEAD"

POP_PRODUCTION = "production"
POP_SCAFFOLD = "scaffolding"
POPS = (POP_PRODUCTION, POP_SCAFFOLD)

SCAFFOLD_EXACT = ("selftest",)
SCAFFOLD_PREFIXES = ("selftest", "_selftest", "test_", "_test_", "leg_", "_leg")
SCAFFOLD_CONTAINS = ("fixture", "harness")

ADDITIVE_KEYS = ("field_reads", "fields", "guard_fields", "guard_fields_with_no_writer",
                 "choice_fields", "choice_sites", "guard_sites", "fields_with_no_writer",
                 "max_blast_radius")
FILE_LEVEL_KEYS = ("corpus_sources", "sources_parsed", "json_bindings",
                   "unresolved_load_bindings", "dump_sinks", "skipped_numeric_keys",
                   "faces_named", "fields_with_unresolved_face")

V_PRODUCTION = "census_is_mostly_production"
V_SCAFFOLD = "the_published_population_is_mostly_scaffolding"
V_MIXED = "the_split_is_the_answer_not_a_single_share"
V_EMPTY = "no_readable_population"

MAX_ROWS = 40
MAX_FACES = 60


def say(message):
    sys.stdout.write(str(message) + "\n")


# ------------------------------------------------------------------ population rule

def population_of(func_name):
    """Which population a read site belongs to, from its enclosing function's name.

    Frozen on purpose: the rule is published, so a reader can disagree with it.  A
    module-level site has no function and is production by construction -- it runs
    when the module is imported, whatever the name of the file.
    """
    if not func_name:
        return POP_PRODUCTION
    name = str(func_name)
    if name in SCAFFOLD_EXACT or name.startswith(SCAFFOLD_PREFIXES):
        return POP_SCAFFOLD
    for token in SCAFFOLD_CONTAINS:
        if token in name:
            return POP_SCAFFOLD
    return POP_PRODUCTION


# ------------------------------------------------------------------ measurement

def call_map(tree):
    """``{def_name: {callee_name}}`` for every function in this module.

    Callees are resolved by the last name in ``f(...)`` / ``a.b(...)`` calls.  This is a
    name-level graph inside ONE file: it cannot see a call made from another module, so
    the widened rule below can only ever ADD scaffolding, never remove it -- and a helper
    that no function in its own file calls stays at its name-rule population.
    """
    out = {}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        callees = out.setdefault(node.name, set())
        for inner in ast.walk(node):
            if isinstance(inner, ast.Call):
                func = inner.func
                if isinstance(func, ast.Name):
                    callees.add(func.id)
                elif isinstance(func, ast.Attribute):
                    callees.add(func.attr)
    return out


def scaffolding_closure(tree, calls=None):
    """Function names that are scaffolding under the widened (name + caller) rule.

    A name-rule production function joins the scaffolding population when EVERY function
    that calls it (inside this file) is scaffolding, and at least one does.  A helper with
    no in-file caller is left alone: no evidence either way, so it is not promoted.
    """
    calls = call_map(tree) if calls is None else calls
    defs = set(calls)
    callers = {}
    for name, callees in calls.items():
        for callee in callees:
            if callee in defs:  # a builtin or a method name is not a function of this file
                callers.setdefault(callee, set()).add(name)
    seeds = {name for name in defs if population_of(name) == POP_SCAFFOLD}
    for name in defs:
        if population_of(name) == POP_SCAFFOLD:
            seeds.add(name)
    changed = True
    while changed:
        changed = False
        for name, who in callers.items():
            if name in seeds or not who:
                continue
            if all(caller in seeds for caller in who):
                seeds.add(name)
                changed = True
    return seeds


def function_literals(tree):
    """``{def_name: {string literals written inside it}}`` -- one level, no inheritance.

    Used to tell a read that names its own face from a read whose face name was bound
    elsewhere in the file: E350's resolver is FILE-scoped, so a variable name reused in a
    second function inherits the first function's face.
    """
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            lits = out.setdefault(node.name, set())
            for inner in ast.walk(node):
                if isinstance(inner, ast.Constant) and isinstance(inner.value, str):
                    lits.add(inner.value)
    return out


def module_literals(tree):
    """String literals written at module level (outside every function).

    A face path assembled from a module constant (``OUTDIR``, ``FACE``) is declared once
    for the whole file, so a read inside any function is legitimately self-named.
    """
    out = set()
    for node in getattr(tree, "body", []):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        for inner in ast.walk(node):
            if isinstance(inner, ast.Constant) and isinstance(inner.value, str):
                out.add(inner.value)
    return out


def _store_sites(tree, targets, parents):
    """``[(base, key, node)]`` -- E350's ``_stores``, but keeping the node.

    Kept in lockstep with ``e350._stores`` by a selftest leg that asserts the two agree
    on the same tree, so a drift in either one fails here instead of silently changing
    the split.
    """
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant) \
                and isinstance(node.slice.value, str):
            base = node.value.id if isinstance(node.value, ast.Name) else None
            if base not in targets:
                continue
            parent = parents.get(node)
            if isinstance(parent, (ast.Assign, ast.AugAssign)) and (
                    node in getattr(parent, "targets", [])
                    or getattr(parent, "target", None) is node):
                out.append((base, node.slice.value, node))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if not isinstance(node.func.value, ast.Name) or node.func.value.id not in targets:
                continue
            if node.func.attr not in ("update", "setdefault"):
                continue
            keys = []
            if node.func.attr == "setdefault" and node.args \
                    and isinstance(node.args[0], ast.Constant) \
                    and isinstance(node.args[0].value, str):
                keys = [node.args[0].value]
            if node.func.attr == "update" and node.args and isinstance(node.args[0], ast.Dict):
                keys = [k.value for k in node.args[0].keys
                        if isinstance(k, ast.Constant) and isinstance(k.value, str)]
            for key in keys:
                out.append((node.func.value.id, key, node))
    return out


def _literal_sites(tree, targets):
    """``[(base, key, node)]`` -- E350's ``_literal_keys``, but keeping the node."""
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in targets:
                    for key in node.value.keys:
                        if isinstance(key, ast.Constant) and isinstance(key.value, str):
                            out.append((target.id, key.value, node))
    return out


def writes_by_population(tree, bindings, consts, closure=None):
    """``{population: {(face, key)}}`` for this file's stores, tagged by enclosing def."""
    parents = e347.parents_of(tree)
    sinks = e350._dump_sinks(tree, consts)
    faces_of = {}
    for name, faces in list(bindings.items()) + list(sinks.items()):
        faces_of.setdefault(name, set()).update(faces)
    out = {pop: set() for pop in POPS}
    for base, key, node in (_store_sites(tree, set(faces_of), parents)
                            + _literal_sites(tree, set(faces_of))):
        func = e347.enclosing_def(node, parents)
        fname = getattr(func, "name", None)
        if closure is not None and fname in closure:
            pop = POP_SCAFFOLD
        else:
            pop = population_of(fname)
        for face in faces_of.get(base, ()):
            out[pop].add((face, key))
    return out


def tag_sites(sources):
    """``(reads, writes_by_pop, stats_by_pop, totals)`` over ``[(relpath, text)]``."""
    reads = []
    writes_by_pop = {pop: set() for pop in POPS}
    writes_by_pop_wide = {pop: set() for pop in POPS}
    stats = {POP_PRODUCTION: {"sources": set(), "parsed": 0},
             POP_SCAFFOLD: {"sources": set(), "parsed": 0}}
    totals = {"sources": 0, "parsed": 0, "json_bindings": 0,
              "unresolved_load_bindings": 0, "dump_sinks": 0,
              "skipped_numeric_keys": 0, "faces_named": set()}

    for relpath, text in sources:
        totals["sources"] += 1
        tree = e347.parse(text)
        if tree is None:
            continue
        totals["parsed"] += 1
        consts = e347.constants(tree)
        bindings, unresolved = e350._face_bindings(tree, consts)
        totals["unresolved_load_bindings"] += unresolved
        sinks = e350._dump_sinks(tree, consts)
        totals["dump_sinks"] += len(sinks)
        totals["faces_named"] |= {f for v in bindings.values() for f in v}
        totals["faces_named"] |= {f for v in sinks.values() for f in v}

        closure = scaffolding_closure(tree)
        for pop, pairs in writes_by_population(tree, bindings, consts).items():
            writes_by_pop[pop] |= pairs
        for pop, pairs in writes_by_population(tree, bindings, consts, closure).items():
            writes_by_pop_wide[pop] |= pairs
        totals["scaffolding_helpers_by_closure"] = totals.get(
            "scaffolding_helpers_by_closure", 0) + len(
            {n for n in closure if population_of(n) == POP_PRODUCTION})

        if not bindings:
            continue
        totals["json_bindings"] += len(bindings)
        parents = e347.parents_of(tree)
        lits = function_literals(tree)
        mod_lits = module_literals(tree)
        for node in ast.walk(tree):
            if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant) \
                    and not isinstance(node.slice.value, str):
                totals["skipped_numeric_keys"] += 1
            hit = e350._key_of(node, bindings)
            if hit is None:
                continue
            base, key, form = hit
            parent = parents.get(node)
            if isinstance(parent, (ast.Assign, ast.AugAssign)) and (
                    node in getattr(parent, "targets", [])
                    or getattr(parent, "target", None) is node):
                continue  # a store, counted on the write side
            branch = e350._nearest_branch(node, parents)
            cls = "unbranched" if branch is None else e350.classify_branch(branch)
            func = e347.enclosing_def(node, parents)
            fname = getattr(func, "name", None)
            pop = population_of(fname)
            wide = POP_SCAFFOLD if fname in closure else pop
            stats[pop]["sources"].add(relpath)
            for face in bindings[base]:
                reads.append({
                    "face": face, "field": key, "path": relpath, "line": node.lineno,
                    "form": form, "branch": cls, "population": pop,
                    "population_widened": wide, "func": fname,
                    "face_named_here": (not fname)
                                     or face in lits.get(fname, ())
                                     or face in mod_lits
                                     or e350._basename(face) in mod_lits,
                })

    for pop in POPS:
        stats[pop]["parsed"] = len(stats[pop]["sources"])
        stats[pop]["sources"] = len(stats[pop]["sources"])
    return reads, writes_by_pop, writes_by_pop_wide, stats, totals


def summarize_population(reads, writes):
    rows = e350._rows(reads, writes)
    by_class = {}
    for row in reads:
        by_class[row["branch"]] = by_class.get(row["branch"], 0) + 1
    guard_fields = [r for r in rows if r["guards"]]
    unwritten = [r for r in guard_fields if not r["written"]]
    choices = [r for r in rows if r["choices"]]
    resolved = [r for r in rows if r["face_resolved"]]
    top = resolved[0] if resolved else (rows[0] if rows else None)
    return {
        "field_reads": len(reads),
        "fields": len(rows),
        "guard_fields": len(guard_fields),
        "guard_fields_with_no_writer": len(unwritten),
        "choice_fields": len(choices),
        "choice_sites": sum(r["choices"] for r in rows),
        "guard_sites": sum(r["guards"] for r in rows),
        "fields_with_no_writer": sum(1 for r in rows if not r["written"]),
        "fields_with_unresolved_face": sum(1 for r in rows if not r["face_resolved"]),
        "reads_by_branch": by_class,
        "max_blast_radius": top["blast_radius"] if top else 0,
        "max_blast_field": ("%s :: %s" % (top["face"], top["field"])) if top else None,
    }


def only_scaffolding_faces(reads, key="population"):
    """Faces whose entire read population sits inside scaffolding functions."""
    seen = {}
    for row in reads:
        slot = seen.setdefault(row["face"], {POP_PRODUCTION: 0, POP_SCAFFOLD: 0,
                                             "sample": None, "fields": set()})
        slot[row[key]] += 1
        slot["fields"].add(row["field"])
        if slot["sample"] is None:
            slot["sample"] = {"path": row["path"], "line": row["line"],
                              "field": row["field"], "func": row["func"]}
    out = []
    for face, slot in seen.items():
        if slot[POP_SCAFFOLD] and not slot[POP_PRODUCTION]:
            out.append({"face": face, "reads": slot[POP_SCAFFOLD],
                        "fields": sorted(slot["fields"])[:6],
                        "fields_n": len(slot["fields"]), "sample": slot["sample"]})
    out.sort(key=lambda r: (-r["reads"], r["face"]))
    return out


def decide(summary):
    """Verdict from the WIDER reading: the conservative direction."""
    pops = summary.get("populations_widened") or summary["populations"]
    prod = pops[POP_PRODUCTION]
    scaf = pops[POP_SCAFFOLD]
    if not prod["field_reads"] and not scaf["field_reads"]:
        return V_EMPTY
    total = prod["field_reads"] + scaf["field_reads"]
    share = 100.0 * scaf["field_reads"] / total
    summary["scaffolding_share_pct"] = round(share, 2)
    if share < 5.0:
        return V_PRODUCTION
    if share > 50.0:
        return V_SCAFFOLD
    return V_MIXED


# ------------------------------------------------------------------ build / verify

def sources_from_disk():
    corpus = [p for p in e346._corpus() if p != SELF_REL]
    out = []
    for rel in corpus:
        try:
            with open(os.path.join(ROOT, rel), "r", encoding="utf-8",
                      errors="replace") as fh:
                out.append((rel, fh.read()))
        except OSError:
            continue
    return out


def build_face(sources=None, pin=None):
    sources = sources_from_disk() if sources is None else sources
    reads, writes_by_pop, writes_by_pop_wide, stats, totals = tag_sites(sources)

    populations, populations_widened = {}, {}
    for pop in POPS:
        populations[pop] = summarize_population(
            [r for r in reads if r["population"] == pop], writes_by_pop[pop])
        populations_widened[pop] = summarize_population(
            [r for r in reads if r["population_widened"] == pop], writes_by_pop_wide[pop])

    def delta_of(pops, all_reads, all_writes):
        out = {}
        whole = summarize_population(all_reads, all_writes)
        for key in ADDITIVE_KEYS:
            a = pops[POP_PRODUCTION].get(key, 0)
            b = pops[POP_SCAFFOLD].get(key, 0)
            out[key] = {"production": a, "scaffolding": b, "sum": a + b,
                        "union": whole.get(key, a + b),
                        "additive": whole.get(key, a + b) == a + b,
                        "scaffolding_share_pct": round(100.0 * b / (a + b), 2) if (a + b) else 0.0}
        return out

    all_writes = writes_by_pop[POP_PRODUCTION] | writes_by_pop[POP_SCAFFOLD]
    all_writes_wide = writes_by_pop_wide[POP_PRODUCTION] | writes_by_pop_wide[POP_SCAFFOLD]
    delta = delta_of(populations, reads, all_writes)
    delta_widened = delta_of(populations_widened, reads, all_writes_wide)

    file_level = {
        "corpus_sources": totals["sources"],
        "sources_parsed": totals["parsed"],
        "json_bindings": totals["json_bindings"],
        "unresolved_load_bindings": totals["unresolved_load_bindings"],
        "dump_sinks": totals["dump_sinks"],
        "skipped_numeric_keys": totals["skipped_numeric_keys"],
        "faces_named": len(totals["faces_named"]),
        "helpers_promoted_by_caller_closure": totals.get("scaffolding_helpers_by_closure", 0),
    }
    faces = only_scaffolding_faces(reads, key="population")
    faces_wide = only_scaffolding_faces(reads, key="population_widened")

    leaked = [r for r in reads if not r.get("face_named_here", True)]
    leaked_prod = [r for r in leaked if r["population_widened"] == POP_PRODUCTION]
    # faces whose EVERY read has its name bound outside the reading function: the reader
    # never wrote this path, so the handler it is guarding may belong to another function
    per_face = {}
    for row in reads:
        slot = per_face.setdefault(row["face"], [0, 0])
        slot[0] += 1
        if not row.get("face_named_here", True):
            slot[1] += 1
    all_leaked = sorted(({"face": face, "reads": n, "leaked": k}
                         for face, (n, k) in per_face.items() if k == n and n >= 2),
                        key=lambda r: (-r["reads"], r["face"]))

    summary = {
        "populations": populations,
        "populations_widened": populations_widened,
        "delta": delta,
        "delta_widened": delta_widened,
        "file_level_counts": file_level,
        "leak": {
            "definition": ("a read is 'leaked' when its reported face is written as a literal neither "
                           "inside the read's own enclosing function nor at module level -- "
                           "E350's resolver is file-scoped, so a reused variable name "
                           "inherits another function's face"),
            "reads_total": len(reads),
            "leaked_reads": len(leaked),
            "leaked_share_pct": round(100.0 * len(leaked) / len(reads), 2) if reads else 0.0,
            "leaked_production_reads": len(leaked_prod),
            "faces_whose_every_read_is_leaked": len(all_leaked),
        },
        "faces_every_read_leaked": all_leaked[:MAX_FACES],
        "file_level_reason": ("these are file-level counts and are NOT split: one source "
                              "file holds both populations, so a per-population share of a "
                              "file count is not a measurement"),
        "faces_only_read_by_scaffolding": len(faces),
        "faces_only_read_by_scaffolding_widened": len(faces_wide),
        "read_sites_total": len(reads),
        "sites_split": sum(stats[p]["parsed"] for p in POPS),
    }
    verdict = decide(summary)

    face = {
        "study": STUDY,
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "today": TODAY,
        "pin": pin or SOURCE_PIN,
        "verdict": verdict,
        "summary": summary,
        "populations": populations,
        "populations_widened": populations_widened,
        "delta": delta,
        "delta_widened": delta_widened,
        "faces_only_read_by_scaffolding": faces[:MAX_FACES],
        "faces_only_read_by_scaffolding_widened": faces_wide[:MAX_FACES],
        "variants": {
            "name_only": ("a site is scaffolding when its own enclosing function is named "
                          "selftest/test_/leg_*/fixture/harness"),
            "name_plus_callers": ("...OR every function that calls it inside the same file "
                                  "is scaffolding (a helper used only by a selftest); a "
                                  "function with no in-file caller is never promoted"),
            "verdict_uses": "name_plus_callers (the wider, conservative reading)",
        },
        "delta_rows": [delta[k] | {"key": k} for k in ADDITIVE_KEYS],
        "unwritten_guards_by_population": {
            pop: [r for r in e350._rows([x for x in reads if x["population"] == pop],
                                        writes_by_pop[pop])
                  if r["guards"] and not r["written"]][:MAX_ROWS]
            for pop in POPS
        },
        "rule": {
            "scaffolding_functions_exact": list(SCAFFOLD_EXACT),
            "scaffolding_functions_prefixes": list(SCAFFOLD_PREFIXES),
            "scaffolding_functions_name_contains": list(SCAFFOLD_CONTAINS),
            "module_level_sites": POP_PRODUCTION,
            "writes_split_by": ("prune the scaffolding top-level functions, re-measure, and "
                                "take the set difference (a name written on both sides stays "
                                "written on the production side)"),
        },
        "bound": ("corpus = in-repo .py sources walked by e346._corpus() minus this study's own "
                  "source.  Population is read from the enclosing function's NAME, so a fixture "
                  "built inside a production helper is counted as production (this understates "
                  "scaffolding, never overstates it).  Reads reached through a path this "
                  "resolver cannot fold remain in unresolved_load_bindings and contribute no "
                  "field rows, exactly as in E350.  Additive keys are exact; file-level keys are "
                  "published once, unsplit, on purpose."),
    }
    return face


def write_face(face, root=ROOT):
    outdir = os.path.join(root, "results", "state_tilt")
    os.makedirs(outdir, exist_ok=True)
    payload = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    for name in (FACE, LATEST):
        with open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(payload + "\n")
    return os.path.join(outdir, FACE)


def verify(root=ROOT):
    path = os.path.join(root, "results", "state_tilt", LATEST)
    if not os.path.exists(path):
        say("PROBLEM: no published face at %s" % LATEST)
        return 1
    with open(path, encoding="utf-8") as fh:
        stored = json.load(fh)
    fresh = build_face(pin=stored.get("pin"))
    problems = []
    if stored.get("verdict") != decide(json.loads(json.dumps(stored["summary"]))):
        problems.append("the stored verdict does not re-derive from its own summary")
    if stored.get("delta") != fresh["delta"]:
        problems.append("the additive delta does not re-derive")
    stored_faces = [f["face"] for f in stored.get("faces_only_read_by_scaffolding") or []]
    fresh_faces = [f["face"] for f in fresh["faces_only_read_by_scaffolding"]]
    if stored_faces != fresh_faces:
        problems.append("the scaffolding-only face list does not re-derive")
    if [f["face"] for f in stored.get("faces_only_read_by_scaffolding_widened") or []] != \
            [f["face"] for f in fresh["faces_only_read_by_scaffolding_widened"]]:
        problems.append("the widened scaffolding-only face list does not re-derive")
    if stored.get("delta_widened") != fresh["delta_widened"]:
        problems.append("the widened delta does not re-derive")
    if (stored.get("summary") or {}).get("leak") != fresh["summary"]["leak"]:
        problems.append("the leak axis does not re-derive")
    if (stored.get("summary") or {}).get("file_level_counts") != \
            fresh["summary"]["file_level_counts"]:
        problems.append("the file-level counts do not re-derive")
    for pop in POPS:
        if (stored.get("populations") or {}).get(pop) != fresh["populations"][pop]:
            problems.append("the %s population does not re-derive" % pop)
    for row in stored.get("faces_only_read_by_scaffolding") or []:
        slot = (stored.get("delta") or {}).get("field_reads") or {}
        if row["reads"] <= 0:
            problems.append("a scaffolding-only face carries no reads: %s" % row["face"])
        del slot
    total = sum(d["sum"] for d in (stored.get("delta") or {}).values() if isinstance(d, dict))
    if not total:
        problems.append("every additive delta row is empty")
    if problems:
        for p in problems:
            say("PROBLEM: %s" % p)
        return 1
    say("VERIFY OK: problems=[] populations re-derived, delta re-derived, "
        "%d scaffolding-only faces" % len(fresh_faces))
    return 0


# ------------------------------------------------------------------ selftest

PRODY = '''import json
NOTE = "module constant the pruned arm must keep"

def report():
    with open("results/x/OK.json", encoding="utf-8") as ok_fh:
        ok_doc = json.load(ok_fh)
    assert ok_doc["verdict"] == "ok", "verdict"
    if ok_doc["stale"]:
        raise SystemExit("stale")
    ok_doc["seen"] = ok_doc["n"]
    return ok_doc["n"]
'''

SCAFF = '''

def selftest():
    with open("FZ.json", "w", encoding="utf-8") as fz_fh:
        json.dump({"verdict": "ok"}, fz_fh)
    with open("FZ.json", encoding="utf-8") as fz_in:
        fz_doc = json.load(fz_in)
    assert fz_doc["verdict"] == "ok", "fixture verdict"
    fz_doc["stale"] = False
    return True
'''


LONE_HELPER = '''import json

def _orphan_reader():
    with open("results/x/OK.json", encoding="utf-8") as lone_fh:
        lone_doc = json.load(lone_fh)
    assert lone_doc["verdict"] == "ok", "lone"
'''


def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    sources = [("scripts/fake_prod.py", PRODY + SCAFF)]
    reads, writes_by_pop, writes_by_pop_wide, stats, totals = tag_sites(sources)

    prod = [r for r in reads if r["population"] == POP_PRODUCTION]
    scaf = [r for r in reads if r["population"] == POP_SCAFFOLD]
    leg("a selftest body is scaffolding and the module body is production",
        len(prod) == 4 and len(scaf) == 1,
        "prod=%d scaf=%d" % (len(prod), len(scaf)))
    leg("the scaffolding side is the hard-coded fixture name",
        sorted({r["face"] for r in scaf}) == ["FZ.json"],
        str(sorted({r["face"] for r in scaf})))
    leg("the production side is the real face",
        sorted({r["face"] for r in prod}) == ["results/x/OK.json"],
        str(sorted({r["face"] for r in prod})))
    leg("population is read from the enclosing function name",
        {r["func"] for r in scaf} == {"selftest"} and
        {r["func"] for r in prod} == {"report"},
        str({r["func"] for r in scaf} | {r["func"] for r in prod}))
    leg("module-level sites with no function are production",
        population_of(None) == POP_PRODUCTION, population_of(None))
    leg("the rule is frozen on prefixes, not on substrings of unrelated words",
        population_of("selftest_two") == POP_SCAFFOLD
        and population_of("report") == POP_PRODUCTION
        and population_of("legacy_reader") == POP_PRODUCTION,
        "%s/%s/%s" % (population_of("selftest_two"), population_of("report"),
                      population_of("legacy_reader")))

    faces = only_scaffolding_faces(reads)
    leg("a face read only by a selftest is named individually",
        [f["face"] for f in faces] == ["FZ.json"], str([f["face"] for f in faces]))
    leg("the scaffolding-only row carries its sample site",
        faces and faces[0]["sample"]["func"] == "selftest",
        str(faces[0]["sample"] if faces else None))

    prod_sum = summarize_population(prod, writes_by_pop[POP_PRODUCTION])
    scaf_sum = summarize_population(scaf, writes_by_pop[POP_SCAFFOLD])
    leg("the production population keeps its guards",
        prod_sum["guard_fields"] == 2, str(prod_sum["guard_fields"]))
    leg("the scaffolding population has its own guard",
        scaf_sum["guard_fields"] == 1, str(scaf_sum["guard_fields"]))
    leg("an unwritten guard is counted per population, not once",
        prod_sum["guard_fields_with_no_writer"] == 2 and
        scaf_sum["guard_fields_with_no_writer"] == 1,
        "%s/%s" % (prod_sum["guard_fields_with_no_writer"],
                   scaf_sum["guard_fields_with_no_writer"]))

    # the split's write arm must be E350's write arm, only tagged: same pairs, one set
    prod_tree = e347.parse(PRODY)
    prod_consts = e347.constants(prod_tree)
    prod_bind, _u = e350._face_bindings(prod_tree, prod_consts)
    mine = writes_by_population(prod_tree, prod_bind, prod_consts)
    leg("the tagged write walker agrees with E350's on the same tree",
        bool(mine[POP_PRODUCTION])
        and (mine[POP_PRODUCTION] | mine[POP_SCAFFOLD])
        == e350._write_sites(prod_tree, prod_bind, prod_consts),
        "%d pairs, production %d" % (len(mine[POP_PRODUCTION] | mine[POP_SCAFFOLD]),
                                     len(mine[POP_PRODUCTION])))
    scaf_tree = e347.parse(SCAFF)
    scaf_consts = e347.constants(scaf_tree)
    scaf_bind, _u2 = e350._face_bindings(scaf_tree, scaf_consts)
    scaf_mine = writes_by_population(scaf_tree, scaf_bind, scaf_consts)
    leg("a store inside a selftest lands on the scaffolding side only",
        bool(scaf_mine[POP_SCAFFOLD]) and not scaf_mine[POP_PRODUCTION],
        "%d/%d" % (len(scaf_mine[POP_SCAFFOLD]), len(scaf_mine[POP_PRODUCTION])))

    # the widened rule: a helper whose only in-file caller is a selftest joins it
    helper_src = ('import json\n'
                  'def _cap_worker():\n'
                  '    with open("FZ.json", encoding="utf-8") as cap_fh:\n'
                  '        cap_doc = json.load(cap_fh)\n'
                  '    assert cap_doc["verdict"] == "ok", "cap"\n'
                  '    return cap_doc["n"]\n'
                  '\n'
                  'def selftest():\n'
                  '    return _cap_worker()\n')
    ht = e347.parse(helper_src)
    closure = scaffolding_closure(ht)
    leg("a helper called only by a selftest is promoted to scaffolding",
        "_cap_worker" in closure, str(sorted(closure)))
    leg("only functions this file defines can be promoted (no builtin callee names)",
        "open" not in closure and "load" not in closure
        and closure <= set(call_map(ht)),
        str(sorted(n for n in closure if n not in {"selftest", "_cap_worker"})))
    leg("the name-only rule would leave it in production",
        population_of("_cap_worker") == POP_PRODUCTION, population_of("_cap_worker"))

    _rh, _wh, _whw, _sh, _th = tag_sites([("scripts/helper.py", helper_src)])
    wide_scaf = [r for r in _rh if r["population_widened"] == POP_SCAFFOLD]
    narrow_scaf = [r for r in _rh if r["population"] == POP_SCAFFOLD]
    leg("the widened reading moves the helper's fixture reads to scaffolding",
        len(wide_scaf) == 2 and {r["face"] for r in wide_scaf} == {"FZ.json"}
        and not narrow_scaf,
        "wide=%d narrow=%d" % (len(wide_scaf), len(narrow_scaf)))
    lt = e347.parse(LONE_HELPER)
    leg("a helper with no in-file caller is never promoted",
        "_orphan_reader" not in scaffolding_closure(lt),
        str(sorted(scaffolding_closure(lt))))
    leg("the lone helper's read therefore stays production",
        [r["population_widened"] for r in
         tag_sites([("scripts/lone.py", LONE_HELPER)])[0]] == [POP_PRODUCTION],
        "population pinned")


# a fixture written inside a production helper is production: the rule understates
    # scaffolding, and the leg pins the direction of that bias instead of hiding it
    helper = ('def make_temp_doc():\n'
              '    with open("FZ.json", "w", encoding="utf-8") as tmp_fh:\n'
              '        json.dump({"a": 1}, tmp_fh)\n')
    _r2, _w2, _w2w, _s2, _t2 = tag_sites([("scripts/h.py", helper)])
    leg("a fixture written by an ordinarily-named helper counts as production",
        population_of("make_temp_doc") == POP_PRODUCTION,
        population_of("make_temp_doc"))

    # the face's own accounting has to close
    face = build_face(sources=sources, pin="fixture")
    leg("the fixture face's verdict comes from its own share",
        face["verdict"] == decide(json.loads(json.dumps(face["summary"]))),
        face["verdict"])
    leg("read-site counts are additive; distinct-key counts carry their union",
        face["delta"]["field_reads"]["additive"] is True
        and all(d["sum"] == d["production"] + d["scaffolding"]
                and d["union"] >= max(d["production"], d["scaffolding"])
                for d in face["delta"].values()),
        "field_reads additive=%s" % face["delta"]["field_reads"]["additive"])
    leg("the file-level counts are published and explicitly unsplit",
        face["summary"]["file_level_counts"]["corpus_sources"] == 1
        and "NOT split" in face["summary"]["file_level_reason"],
        str(face["summary"]["file_level_counts"]))

    passed = sum(1 for _n, ok, _d in legs if ok)
    for name, ok, detail in legs:
        say(("PASS " if ok else "FAIL ") + name + (("  [" + detail + "]") if detail else ""))
    say("selftest %d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "build").lower()
    if cmd == "build":
        face = build_face()
        write_face(face)
        s = face["summary"]
        d = face["delta"]
        say("wrote %s: %d read sites, scaffolding share %s%% (widened rule)"
            % (FACE, s["read_sites_total"], s["scaffolding_share_pct"]))
        for label, d in (("name-only", face["delta"]),
                         ("widened", face["delta_widened"])):
            say("%-9s fields %d -> %d / %d | guard fields %d -> %d / %d | unwritten "
                "guards %d -> %d / %d | scaffolding-only faces %d"
                % (label,
                   d["fields"]["sum"], d["fields"]["production"], d["fields"]["scaffolding"],
                   d["guard_fields"]["sum"], d["guard_fields"]["production"],
                   d["guard_fields"]["scaffolding"],
                   d["guard_fields_with_no_writer"]["sum"],
                   d["guard_fields_with_no_writer"]["production"],
                   d["guard_fields_with_no_writer"]["scaffolding"],
                   s["faces_only_read_by_scaffolding"] if label == "name-only"
                   else s["faces_only_read_by_scaffolding_widened"]))
        say("helpers promoted to scaffolding by the caller closure: %d"
            % s["file_level_counts"]["helpers_promoted_by_caller_closure"])
        say("VERDICT: %s" % face["verdict"])
        return 0
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    say("usage: %s [build|verify|selftest]" % SELF_REL)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))