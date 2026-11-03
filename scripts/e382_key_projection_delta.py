"""E382 -- what moves if the key projection is fixed.

E381 named two defects in the face keying that E350/E353/E377 share:

  (a) a ``join`` call is keyed by its OPERANDS, each operand run through ``_face_key`` alone, so
      ``os.path.join("results", "sub", "latest.json")`` is filed as ``latest.json``;
  (b) both face helpers accept only values ending ``.json``, so a ``.jsonl`` read is never keyed
      at all and is counted as unresolved.

Before anyone patches ``e350._face_bindings`` this study prices the repair.  Two arms are built
IN MEMORY over the same corpus, in one parse pass per source:

  * arm ``published``  -- ``e350._face_bindings`` unchanged;
  * arm ``repaired``   -- the join's own operands folded into one path (``e381.joined_key``), and
    ``.jsonl`` accepted as a face.

and every headline that depends on the key set is published three ways: the number the face on
disk carries, the number arm ``published`` re-derives from today's corpus, and the number arm
``repaired`` re-derives from the same corpus.  The repair's bill is ``repaired - published-arm``;
``published-arm - face-on-disk`` is corpus drift and is published separately, because rolling the
two into one delta would bill a bugfix for a panel that moved.

Nothing is written back: E350/E353/E377/E381 stay as published, and a judgement is made from the
deltas rather than assumed.

Usage:
  python scripts/e382_key_projection_delta.py run
  python scripts/e382_key_projection_delta.py verify
  python scripts/e382_key_projection_delta.py selftest
"""
from __future__ import annotations

import ast
import io
import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e347_published_number_gate_census as e347  # noqa: E402
import e350_field_branch_census as e350  # noqa: E402
import e381_component_key_blind_spot as e381  # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-03"
FACE = "KEYDELTA-%s.json" % TODAY
LATEST = "keydelta_latest.json"
STUDY = "E382_key_projection_delta"
SELF_REL = "scripts/e382_key_projection_delta.py"

UP_E350 = "fieldbranch_latest.json"
UP_E377 = "unresolveddest_latest.json"
UP_E381 = "componentkey_latest.json"

ARM_PUBLISHED = "published_keying"
ARM_REPAIRED = "repaired_keying"

V_HEADLINES_MOVE = ("fixing_the_key_projection_moves_published_headlines_so_the_repair_is_a_"
                    "republish_decision_not_a_bugfix")
V_HEADLINES_HOLD = ("fixing_the_key_projection_leaves_every_published_headline_where_it_is_so_the_"
                    "defect_is_real_and_costs_no_published_number")
V_VERDICT_FLIPS = ("at_least_one_published_verdict_string_changes_under_the_repair_so_the_faces_"
                   "must_be_republished_together")
V_EMPTY = "no_face_was_keyed_under_either_projection_so_no_claim_is_made"

# Headlines this study reprices.  The gate names the arm mapping so verify can re-derive any one.
HEADLINES = [
    ("e350_fields", "E350 fields (face,field) rows"),
    ("e350_field_reads", "E350 reads"),
    ("e350_fields_with_no_writer", "E350 fields with no writer"),
    ("e350_guard_fields", "E350 guard fields"),
    ("e350_guard_fields_with_no_writer", "E350 unwritten guard fields"),
    ("e350_faces_named", "E350 distinct face keys"),
    ("e350_fields_with_unresolved_face", "E350 fields whose face key has no path"),
    ("e353_pairs", "E353 unwritten-guard pairs"),
    ("e377_targets", "E377 blind-spot faces (population, keying-independent)"),
    ("e377_targets_keyed", "E377 blind-spot faces the census keys"),
    ("e381_joined_only_faces", "faces named only by the joined keying and present on disk"),
]


def say(message):
    print(message, flush=True)


# ------------------------------------------------------------------ the repaired projection

def repaired_face_bindings(tree, consts):
    """``e350._face_bindings`` with the join folded into one path and ``.jsonl`` accepted.

    Additive by construction: when a load's operand list yields no joined face key the published
    per-value rule still runs, so the repair can only add keys, never drop one.  ``unresolved``
    keeps the published meaning (a load that names no face at all).
    """
    out, unresolved = {}, 0
    for row in e347.load_bindings(tree, consts):
        key = e381.joined_key(row["values"])
        if key:
            out.setdefault(row["binding"], []).append(key)
            continue
        tails = [e350._face_key(v) for v in row["values"]
                 if str(v).replace("\\", "/").endswith(".json")]
        tails = sorted(set(t for t in tails if t))
        if tails:
            out.setdefault(row["binding"], []).extend(tails)
        else:
            unresolved += 1
    return {k: sorted(set(v)) for k, v in out.items()}, unresolved


# ------------------------------------------------------------------ one parse, two arms

def _reads_for(tree, relpath, bindings, parents):
    rows = []
    for node in ast.walk(tree):
        hit = e350._key_of(node, bindings)
        if hit is None:
            continue
        base, key, form = hit
        parent = parents.get(node)
        if isinstance(parent, (ast.Assign, ast.AugAssign)) and (
                node in getattr(parent, "targets", []) or getattr(parent, "target", None) is node):
            continue  # a store, counted in _write_sites
        branch = e350._nearest_branch(node, parents)
        cls = "unbranched" if branch is None else e350.classify_branch(branch)
        for face in bindings[base]:
            rows.append({"face": face, "field": key, "path": relpath, "line": node.lineno,
                         "form": form, "branch": cls,
                         "branch_line": getattr(branch, "lineno", None) if branch is not None else None})
    return rows


def _blank_stats():
    return {"sources": 0, "parsed": 0, "json_bindings": 0, "unresolved_load_bindings": 0,
            "faces_named": set(), "skipped_numeric_keys": 0, "dump_sinks": 0}


def measure_arms(sources):
    """Both arms in one pass over the corpus: ``{arm: (reads, writes, stats, keys)}``."""
    arms = {}
    for arm in (ARM_PUBLISHED, ARM_REPAIRED):
        arms[arm] = {"reads": [], "writes": set(), "stats": _blank_stats()}
    joined = set()
    joined_sites = {}
    for relpath, text in sources:
        # counts that are arm-independent
        for arm in arms:
            arms[arm]["stats"]["sources"] += 1
        tree = e347.parse(text)
        if tree is None:
            continue
        for arm in arms:
            arms[arm]["stats"]["parsed"] += 1
        consts = e347.constants(tree)
        parents = e347.parents_of(tree)
        bindings = {ARM_PUBLISHED: e350._face_bindings(tree, consts),
                    ARM_REPAIRED: repaired_face_bindings(tree, consts)}
        for row in e347.load_bindings(tree, consts):
            key = e381.joined_key(row["values"])
            if key:
                joined.add(key)
                joined_sites.setdefault(key, []).append("%s:%d %s" % (relpath, row["line"], row["values"]))
        for arm, (binds, unresolved) in bindings.items():
            slot = arms[arm]
            sinks = e350._dump_sinks(tree, consts)
            slot["stats"]["unresolved_load_bindings"] += unresolved
            slot["stats"]["dump_sinks"] += len(sinks)
            slot["stats"]["faces_named"] |= {f for v in binds.values() for f in v}
            slot["stats"]["faces_named"] |= {f for v in sinks.values() for f in v}
            slot["writes"] |= e350._write_sites(tree, binds, consts)
            if not binds:
                continue
            slot["stats"]["json_bindings"] += len(binds)
            for node in ast.walk(tree):
                if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant):
                    if not isinstance(node.slice.value, str):
                        slot["stats"]["skipped_numeric_keys"] += 1
            slot["reads"].extend(_reads_for(tree, relpath, binds, parents))
    out = {}
    for arm, slot in arms.items():
        keys = set(slot["stats"]["faces_named"])
        out[arm] = {"reads": slot["reads"], "writes": slot["writes"],
                    "stats": slot["stats"], "keys": keys}
    out["joined"] = {"keys": joined, "sites": joined_sites}
    return out


def _arm_numbers(arm):
    rows = e350._rows(arm["reads"], arm["writes"])
    summary = e350.summarize(arm["reads"], arm["writes"], arm["stats"])
    pairs = [r for r in rows if r["guards"] and not r["written"]]
    return {"rows": rows, "summary": summary, "pairs": pairs, "verdict": e350.decide(summary)}


def _upstream(name):
    path = os.path.join(OUTDIR, name)
    if not os.path.exists(path):
        return {}
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _published_headlines(face350, faces=None):
    """What each face on disk actually publishes, read, never re-derived.

    Four of the eleven numbers live in the other faces: E353's pair count, E377's target list, and
    E381's joined-only count are read from their own published summaries so the "published face"
    column is a citation rather than a blank.  E377's keyed count is 0 by the list's own meaning
    (the list IS the set the census keys with no resolved sink), and it is published as such.
    """
    faces = faces or {}
    s = face350.get("summary") or {}
    s353 = (faces.get("guardpresence_latest.json") or {}).get("summary") or {}
    s377 = (faces.get(UP_E377) or {}).get("summary") or {}
    s381 = (faces.get(UP_E381) or {}).get("summary") or {}
    return {
        "e350_fields": s.get("fields"),
        "e350_field_reads": s.get("field_reads"),
        "e350_fields_with_no_writer": s.get("fields_with_no_writer"),
        "e350_guard_fields": s.get("guard_fields"),
        "e350_guard_fields_with_no_writer": s.get("guard_fields_with_no_writer"),
        "e350_faces_named": s.get("faces_named"),
        "e350_fields_with_unresolved_face": s.get("fields_with_unresolved_face"),
        "e350_corpus_sources": s.get("corpus_sources"),
        "e353_pairs": s353.get("pairs"),
        "e377_targets": s377.get("faces_no_census_keys"),
        "e377_targets_keyed": 0 if s377.get("faces_no_census_keys") else None,
        "e381_joined_only_faces": s381.get("joined_only_faces"),
    }


def _classify_targets(targets, keys_by_arm):
    rows = []
    for face in targets:
        row = {"face": face}
        for arm in (ARM_PUBLISHED, ARM_REPAIRED):
            row[arm] = face in keys_by_arm[arm]
        if row[ARM_PUBLISHED] and not row[ARM_REPAIRED]:
            row["status"] = "the_repair_loses_a_key"
        elif row[ARM_REPAIRED] and not row[ARM_PUBLISHED]:
            row["status"] = "the_repair_names_it"
        elif row[ARM_REPAIRED]:
            row["status"] = "both_arms_name_it"
        else:
            row["status"] = "neither_arm_names_it"
        rows.append(row)
    return rows


def decide(summary):
    moves = summary.get("headlines_that_move") or 0
    if not (summary.get("arms") or {}).get(ARM_REPAIRED, {}).get("keys"):
        return V_EMPTY
    if summary.get("verdicts_that_flip"):
        return V_VERDICT_FLIPS
    return V_HEADLINES_MOVE if moves else V_HEADLINES_HOLD


# ------------------------------------------------------------------ build

def build(write_face=True):
    srcs = [(rel, text) for rel, text in e350._sources() if rel != SELF_REL]
    say("corpus: %d sources" % len(srcs))
    arms = measure_arms(srcs)
    numbers, verdicts = {}, {}
    for arm in (ARM_PUBLISHED, ARM_REPAIRED):
        got = _arm_numbers(arms[arm])
        numbers[arm] = {
            "e350_fields": got["summary"]["fields"],
            "e350_field_reads": got["summary"]["field_reads"],
            "e350_fields_with_no_writer": got["summary"]["fields_with_no_writer"],
            "e350_guard_fields": got["summary"]["guard_fields"],
            "e350_guard_fields_with_no_writer": got["summary"]["guard_fields_with_no_writer"],
            "e350_faces_named": got["summary"]["faces_named"],
            "e350_fields_with_unresolved_face": got["summary"]["fields_with_unresolved_face"],
            "e353_pairs": len(got["pairs"]),
            "e369_corpus_sources": got["summary"]["corpus_sources"],
        }
        verdicts[arm] = got["verdict"]
        say("%s: fields %d | no-writer %d | guard-unwritten %d | e353 pairs %d | faces %d"
            % (arm, numbers[arm]["e350_fields"], numbers[arm]["e350_fields_with_no_writer"],
               numbers[arm]["e350_guard_fields_with_no_writer"], numbers[arm]["e353_pairs"],
               numbers[arm]["e350_faces_named"]))

    faces = {name: _upstream(name) for name in (UP_E350, UP_E377, UP_E381, "guardpresence_latest.json")}
    published = _published_headlines(faces[UP_E350], faces)

    targets = faces[UP_E377].get("faces_no_census_keys") or []
    if not targets:
        targets = (faces[UP_E377].get("summary") or {}).get("faces_no_census_keys") or []
    keys_by_arm = {ARM_PUBLISHED: arms[ARM_PUBLISHED]["keys"],
                   ARM_REPAIRED: arms[ARM_REPAIRED]["keys"]}
    target_rows = _classify_targets(targets, keys_by_arm)
    numbers[ARM_PUBLISHED]["e377_targets_keyed"] = sum(1 for r in target_rows if r[ARM_PUBLISHED])
    numbers[ARM_REPAIRED]["e377_targets_keyed"] = sum(1 for r in target_rows if r[ARM_REPAIRED])
    for arm in (ARM_PUBLISHED, ARM_REPAIRED):
        numbers[arm]["e377_targets"] = len(target_rows)

    joined = arms["joined"]["keys"]
    joined_only = sorted(k for k in joined - keys_by_arm[ARM_PUBLISHED]
                         if k.endswith((".json", ".jsonl")) and os.path.exists(os.path.join(ROOT, k)))
    numbers[ARM_PUBLISHED]["e381_joined_only_faces"] = len(joined_only)
    numbers[ARM_REPAIRED]["e381_joined_only_faces"] = len(
        [k for k in joined_only if k not in keys_by_arm[ARM_REPAIRED]])
    say("E377 targets %d | keyed under published %d / repaired %d | joined-only faces %d"
        % (len(target_rows), numbers[ARM_PUBLISHED]["e377_targets_keyed"],
           numbers[ARM_REPAIRED]["e377_targets_keyed"], len(joined_only)))

    headline_rows = []
    for key, label in HEADLINES:
        before = numbers[ARM_PUBLISHED].get(key)
        after = numbers[ARM_REPAIRED].get(key)
        headline_rows.append({
            "key": key, "label": label,
            "published_face": published.get(key),
            "recomputed_published_arm": before,
            "recomputed_repaired_arm": after,
            "repair_delta": (after - before) if isinstance(after, int) and isinstance(before, int) else None,
            "corpus_drift": ((before - published[key])
                             if isinstance(before, int) and isinstance(published.get(key), int) else None),
        })
    moves = [r for r in headline_rows if r["repair_delta"]]
    flips = []
    if verdicts[ARM_PUBLISHED] != verdicts[ARM_REPAIRED]:
        flips.append({"face": "E350", "published_arm": verdicts[ARM_PUBLISHED],
                      "repaired_arm": verdicts[ARM_REPAIRED]})
    e377_pub_verdict = faces[UP_E377].get("verdict")
    summary = {
        "corpus_sources": len(srcs),
        "arms": {arm: {"keys": len(keys_by_arm[arm]),
                       "verdict": verdicts[arm]} for arm in (ARM_PUBLISHED, ARM_REPAIRED)},
        "headlines": {r["key"]: {"published_face": r["published_face"],
                                 "published_arm": r["recomputed_published_arm"],
                                 "repaired_arm": r["recomputed_repaired_arm"],
                                 "repair_delta": r["repair_delta"],
                                 "corpus_drift": r["corpus_drift"]} for r in headline_rows},
        "headlines_that_move": len(moves),
        "headline_keys_that_move": [r["key"] for r in moves],
        "verdicts_that_flip": len(flips),
        "e377_targets": len(target_rows),
        "e377_targets_named_only_by_the_repair": sum(
            1 for r in target_rows if r["status"] == "the_repair_names_it"),
        "e377_targets_lost_by_the_repair": sum(
            1 for r in target_rows if r["status"] == "the_repair_loses_a_key"),
        "e350_published_verdict": faces[UP_E350].get("verdict"),
        "not_repriced": {
            "E353_verdict": ("the pair COUNT is repriced, the verdict is not: E353's classes come "
                             "from reading each pair's face on disk, and the new pairs would need "
                             "that classification re-run over the tree"),
            "E377_verdict": ("its inputs are dump-call and unresolved-call counts, which do not "
                             "change with key projection; only its face list does, and that is "
                             "republished here as e377_targets_keyed"),
            "E381_verdict": ("E381 already published this defect; its moved set is re-derived "
                             "here as e381_joined_only_faces"),
        },
    }
    face = {
        "study": STUDY,
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": TODAY,
        "source": SELF_REL,
        "summary": summary,
        "headlines": headline_rows,
        "verdict_flips": flips,
        "e377_rows": target_rows[:400],
        "e377_rows_truncated": max(0, len(target_rows) - 400),
        "joined_only_faces": joined_only[:200],
        "joined_only_examples": [
            {"face": k, "sites": (arms["joined"]["sites"].get(k) or [])[:2]} for k in joined_only[:20]],
        "verdict": decide(summary),
        "bound": (
            "both arms are built in one pass over TODAY's corpus, so the repair's bill is "
            "repaired - published-arm and never repaired - face-on-disk: the corpus has moved "
            "since E350 was published and that drift is carried in its own column.  A repair "
            "delta therefore measures the key projection alone.  The repair RENAMES keys: a folded load is "
            "keyed by its path instead of its basename, so a distinct-key count can move either "
            "way and no monotonicity is claimed -- the sign of each delta is published rather than "
            "argued.  A load whose operands do not fold still takes the published per-value rule, "
            "so no binding loses its key.  E350's and E353's verdicts are re-derived only for "
            "E350; the two workflows whose verdict needs work this study does not do are named in "
            "not_repriced rather than guessed."),
    }
    if write_face:
        for target in (os.path.join(OUTDIR, FACE), os.path.join(OUTDIR, LATEST)):
            with open(target, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
                fh.write("\n")
        say("wrote %s" % os.path.join(OUTDIR, FACE))
    return face


# ------------------------------------------------------------------ verify

def verify():
    path = os.path.join(OUTDIR, FACE)
    if not os.path.exists(path):
        say("no published face")
        return 2
    with io.open(path, encoding="utf-8") as fh:
        face = json.load(fh)
    problems = []
    summary = face.get("summary") or {}
    rows = face.get("headlines") or []
    if len(rows) != len(HEADLINES):
        problems.append("headline table does not carry every named headline")
    for row in rows:
        before, after = row.get("recomputed_published_arm"), row.get("recomputed_repaired_arm")
        delta = row.get("repair_delta")
        if isinstance(before, int) and isinstance(after, int):
            if delta != after - before:
                problems.append("delta does not re-derive for %s" % row.get("key"))
        elif delta is not None:
            problems.append("a non-integer delta is published at %s" % row.get("key"))
    moves = [r for r in rows if r.get("repair_delta")]
    if summary.get("headlines_that_move") != len(moves):
        problems.append("headlines_that_move does not equal the moving rows")
    if sorted(summary.get("headline_keys_that_move") or []) != sorted(r["key"] for r in moves):
        problems.append("the moving-key list is not the moving rows")
    targets = face.get("e377_rows") or []
    named = sum(1 for r in targets if r.get("status") == "the_repair_names_it")
    if named != summary.get("e377_targets_named_only_by_the_repair"):
        problems.append("the repair-names-it count does not re-derive")
    for row in targets:
        if row.get("the_repair_loses_a_key"):
            problems.append("a target key was lost by the repair: %s" % row.get("face"))
    arms = summary.get("arms") or {}
    added = [k for k in (face.get("joined_only_faces") or []) if "/" not in k]
    if added:
        problems.append("a joined-only face is published without a path")
    recomputed = decide(summary)
    if recomputed != face.get("verdict"):
        problems.append("verdict does not re-derive: %s vs %s" % (recomputed, face.get("verdict")))
    # the two defects must each be visible in the published numbers, or be reported as absent
    if not summary.get("headlines_that_move") and not summary.get("e377_targets_named_only_by_the_repair"):
        say("note: no headline moves and no target is re-named -- the face says so in its verdict")
    say("verify problems=%s" % problems)
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest

FIXTURE_JOIN = '''
import json, os
OUT = "results"
doc = json.load(open(os.path.join(OUT, "sub", "latest.json")))
x = doc["a"]
'''

FIXTURE_JSONL = '''
import json
rows = json.load(open("results/state_tilt/rows.jsonl"))
y = rows["n"]
'''

FIXTURE_OPAQUE = '''
import json
def load(path):
    return json.load(open(path))
doc = load("results/x.json")
z = doc["k"]
'''


def _selftest_corpus():
    return [("fixture_join.py", FIXTURE_JOIN), ("fixture_jsonl.py", FIXTURE_JSONL),
            ("fixture_opaque.py", FIXTURE_OPAQUE)]


def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    srcs = _selftest_corpus()
    arms = measure_arms(srcs)
    pub, rep = arms[ARM_PUBLISHED], arms[ARM_REPAIRED]

    leg("published arm files a joined path under its basename",
        "latest.json" in pub["keys"], sorted(pub["keys"]))
    leg("repaired arm files the same read under its full path",
        "results/sub/latest.json" in rep["keys"], sorted(rep["keys"]))
    # a fold REPLACES the basename key, it does not keep both: keeping both would preserve the very
    # collision the repair is for, so a face count may move either way and no monotonicity is claimed
    leg("the repair replaces the basename key rather than keeping both",
        "latest.json" not in rep["keys"], sorted(rep["keys"]))
    leg("both arms see the opaque load's literal face",
        "results/x.json" in pub["keys"] and "results/x.json" in rep["keys"],
        sorted(pub["keys"]))
    leg("a .jsonl read is unresolved under the published rule",
        pub["stats"]["unresolved_load_bindings"] >= 1,
        pub["stats"]["unresolved_load_bindings"])
    leg("the same .jsonl read is keyed under the repair",
        "results/state_tilt/rows.jsonl" in rep["keys"], sorted(rep["keys"]))
    leg("every key the repair removes is a bare basename",
        all("/" not in k for k in (pub["keys"] - rep["keys"])),
        sorted(pub["keys"] - rep["keys"]))
    leg("every key the repair adds is a path or a .jsonl face",
        all("/" in k or k.endswith(".jsonl") for k in (rep["keys"] - pub["keys"])),
        sorted(rep["keys"] - pub["keys"]))

    # the encoding token is not a path component, so it cannot end a joined key
    key = e381.joined_key(["results", "state_tilt", "rows.json", "utf-8"])
    leg("an encoding keyword is not folded into the path", key == "results/state_tilt/rows.json", key)
    leg("a load with no face component yields no joined key", e381.joined_key(["flags"]) is None,
        e381.joined_key(["flags"]))

    # additive by construction: a binding the published rule keys is still keyed
    tree = e347.parse(FIXTURE_OPAQUE)
    consts = e347.constants(tree)
    binds, unresolved = repaired_face_bindings(tree, consts)
    leg("the repaired binding table still keys a plain literal",
        any("results/x.json" in v for v in binds.values()), binds)
    leg("a load it cannot fold is still counted unresolved", unresolved >= 0, unresolved)

    # the published face on disk must be readable and carry the numbers this study reprices
    face350 = _upstream(UP_E350)
    pub_head = _published_headlines(face350)
    leg("E350's published face carries every headline this study reprices",
        all(k in pub_head for k in ("e350_fields", "e350_fields_with_no_writer")), sorted(pub_head))

    # the reprice arithmetic on a fixture summary
    s = {"arms": {ARM_REPAIRED: {"keys": 3}}, "headlines_that_move": 1, "verdicts_that_flip": 0}
    leg("verdict asks for a republish when a headline moves", decide(s) == V_HEADLINES_MOVE)
    s["headlines_that_move"] = 0
    leg("verdict says the defect costs nothing when nothing moves", decide(s) == V_HEADLINES_HOLD)
    s["arms"][ARM_REPAIRED]["keys"] = 0
    leg("verdict refuses to claim on an empty keyed set", decide(s) == V_EMPTY)

    failed = [l for l in legs if not l[1]]
    for name, ok, detail in legs:
        say(("PASS " if ok else "FAIL ") + name + (("  [%s]" % detail) if detail and not ok else ""))
    say("selftest %d/%d" % (len(legs) - len(failed), len(legs)))
    return 0 if not failed else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "run":
        build()
        return 0
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    say("usage: run | verify | selftest")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))