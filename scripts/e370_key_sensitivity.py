"""E370 -- which published numbers move when the population does?

E368 compared four keys and found one stable and one that moved 20%.  That is a result about four
keys, not a rule a reader can apply.  This study takes the **whole summary** of both studies over
the same four arms and classifies every key by how it answers a corpus that has grown:

  published    -- the summary as the face on disk states it (no compute)
  live         -- a fresh walk of the tree now
  pinned_list  -- the pin's members, bytes read from disk now
  pinned_bytes -- the pin's members, bytes resolved from the pin's commit when the disk alone no
                  longer hashes to the pin

The classification is measured, never declared: a key is ``ratio`` when it is bit-identical in
every arm whose population moved (a share or an average over the population absorbs the growth);
``count`` when it moves and the movement equals the population's own growth applied to the
published value (a count of members satisfies a predicate that the new members satisfy too);
``filtered`` when it moves but not proportionally (the new members hit the predicate unevenly);
``flag`` for booleans and ``other`` for non-numeric leaves.

Each key also publishes the drift it actually tolerated: the largest relative population change
at which the key still read exactly the published number.  That number is the whole point -- it
says how much corpus growth a reader may ignore before the number they are quoting is a different
number.

Deviation disclosed: E353's population is E350's unwritten-guard rows, so ``e353.build()`` re-pays
E350's scan.  This study computes E350's rows once per arm and derives E353's summary from those
same rows (the same ``classify`` / ``reconcile`` / ``summarize`` calls, no re-implementation), and
the live arm's ``pairs`` is cross-checked against E353's published face (131).

Usage:
  python scripts/e370_key_sensitivity.py run       # build the four arms + write the face
  python scripts/e370_key_sensitivity.py verify    # re-derive what needs no scan
  python scripts/e370_key_sensitivity.py selftest  # offline fixture legs
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e350_field_branch_census as e350  # noqa: E402
import e353_unwritten_guard_presence as e353  # noqa: E402
import e368_seam_replay as e368  # noqa: E402  (pin loading + member resolution, reused)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-03"
FACE = "KEYSENS-%s.json" % TODAY
LATEST = "keysens_latest.json"
STUDY = "E370_which_numbers_move_with_the_population"
SELF_REL = "scripts/e370_key_sensitivity.py"

E350_FACE = os.path.join(OUTDIR, "fieldbranch_latest.json")
E353_FACE = os.path.join(OUTDIR, "guardpresence_latest.json")
CACHE_PATH = os.path.join(ROOT, "logs", "_e370_partial.json")

# frozen before any number is read
POP_TOL = 0.02          # a "count" must move with the population to within 2% of the prediction
ARMS = ("live", "pinned_list", "pinned_bytes")

C_RATIO = "ratio"
C_COUNT = "count"
C_FILTERED = "filtered"
C_FLAG = "flag"
C_OTHER = "other"
# a study whose population is identical in every arm cannot be classified at all: its keys are not
# "stable under growth", they were never asked the question (E370: E353's population is the
# guard-pair count, and every arm reproduces it, so no arm grew it)
C_UNMOVED = "unmoved"
CLASSES = (C_RATIO, C_COUNT, C_FILTERED, C_FLAG, C_OTHER, C_UNMOVED)

V_RULE = ("published_keys_split_into_%d_ratio_%d_count_%d_filtered_and_the_rule_is_that_a_share_"
          "absorbs_a_%s_pct_corpus_growth_while_a_predicate_count_does_not_%d_keys_are_unmoved_"
          "because_their_studys_population_never_changed_in_any_arm")
V_ONE = "one_class_only_so_the_table_states_a_property_of_the_summary_not_a_rule"
V_EMPTY = "no_summary_replayed_so_no_claim_is_made"


def say(message):
    print(message, flush=True)


# ------------------------------------------------------------------ summaries

def flatten(prefix, value, out):
    """Leaf-level view of a summary -- nested dicts become dotted keys, never a lost key."""
    if isinstance(value, dict):
        for key in sorted(value):
            flatten((prefix + "." if prefix else "") + key, value[key], out)
    else:
        out[prefix] = value
    return out


def summarize_arm(files, index):
    """Both studies' summaries from ONE scan of ``files`` (E353's population is E350's rows)."""
    reads, writes, stats = e350.measure(e350._sources(files))
    rows = e350._rows(reads, writes)
    summary_350 = e350.summarize(reads, writes, stats)
    population = [r for r in rows if r["guards"] and not r["written"]]
    e353_rows = [e353.classify(r["face"], r["field"], index) for r in population]
    block = e353.reconcile(population, rows)
    summary_353 = e353.summarize(e353_rows, len(population), block)
    return {"population_source": e350._population_source(files),
            "E350": summary_350, "E353": summary_353}


def published_summaries():
    out = {}
    for study, path in (("E350", E350_FACE), ("E353", E353_FACE)):
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as fh:
            face = json.load(fh)
        out[study] = {"face": os.path.relpath(path, ROOT).replace("\\", "/"),
                      "pin": face.get("pin"),
                      "evidence_cutoff": face.get("evidence_cutoff"),
                      "summary": face.get("summary") or {}}
    return out


def population_of(study, summary):
    """What the study's population is -- E350 walks sources, E353 counts guard pairs."""
    if study == "E350":
        return summary.get("corpus_sources")
    return summary.get("upstream_pairs", summary.get("pairs"))


# ------------------------------------------------------------------ classification

def _numeric(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def classify_key(published_value, arm_values, arm_pop_ratios):
    """Classify one leaf by the response it shows across the arms (rules frozen above)."""
    moving = [a for a in ARMS if arm_values.get(a) is not None
              and arm_pop_ratios.get(a) not in (None, 1.0)]
    stable = [a for a in moving if arm_values.get(a) == published_value]
    tolerated = 0.0
    for arm in stable:
        tolerated = max(tolerated, abs(arm_pop_ratios[arm] - 1.0) * 100.0)

    if isinstance(published_value, bool):
        return {"class": C_FLAG, "tolerated_drift_pct": round(tolerated, 2),
                "equal_in": stable, "evidence": "boolean leaf"}
    if not _numeric(published_value):
        return {"class": C_OTHER, "tolerated_drift_pct": None,
                "equal_in": stable, "evidence": "non-numeric leaf"}

    mine = [a for a in moving if arm_values.get(a) is not None]
    if not mine:
        return {"class": C_UNMOVED, "tolerated_drift_pct": None, "equal_in": stable,
                "evidence": "no arm moved the population, so nothing is claimed"}
    if len(stable) == len(mine):
        return {"class": C_RATIO, "tolerated_drift_pct": round(tolerated, 2), "equal_in": stable,
                "evidence": "held exactly at %d moving arm(s): %.2f%% population drift absorbed"
                            % (len(stable), tolerated)}

    proportional, residuals = [], {}
    for arm in mine:
        if arm in stable:
            continue
        predicted = published_value * arm_pop_ratios[arm]
        gap = arm_values[arm] - predicted
        residuals[arm] = round(gap, 6)
        proportional.append(abs(gap) <= POP_TOL * max(abs(arm_values[arm]), 1.0))
    klass = C_COUNT if all(proportional) else C_FILTERED
    return {"class": klass, "tolerated_drift_pct": round(tolerated, 2), "equal_in": stable,
            "evidence": ("moved with the population within %.0f%% at %d/%d moving arm(s)"
                         % (POP_TOL * 100, sum(1 for p in proportional if p), len(proportional))),
            "residual_vs_proportional": residuals}


def _summary_of(block):
    """A summary, whether the caller hands the raw summary or a face block that carries one."""
    if isinstance(block, dict) and isinstance(block.get("summary"), dict):
        return block["summary"]
    return block or {}


def table(published, arms):
    published_summary = published
    arm_pop, rows = {}, []
    for study in ("E350", "E353"):
        pub_flat = flatten("", published_summary[study]["summary"], {})
        pop0 = population_of(study, published_summary[study]["summary"])
        per_study = {}
        for arm in ARMS:
            summary = _summary_of((arms.get(arm) or {}).get(study))
            per_study[arm] = flatten("", summary, {})
            pop = population_of(study, summary)
            arm_pop[(study, arm)] = (pop / pop0) if (pop is not None and pop0) else None
        for key in sorted(pub_flat):
            values = {arm: per_study[arm].get(key) for arm in ARMS}
            klass = classify_key(pub_flat[key], values,
                                 {arm: arm_pop[(study, arm)] for arm in ARMS})
            rows.append({"study": study, "key": key, "published": pub_flat[key],
                         "live": values["live"], "pinned_list": values["pinned_list"],
                         "pinned_bytes": values["pinned_bytes"],
                         "population_pct_change": {arm: (None if arm_pop[(study, arm)] is None
                                                         else round((arm_pop[(study, arm)] - 1) * 100, 3))
                                                   for arm in ARMS},
                         **klass})
    return rows, arm_pop


def decide(rows, arms):
    if not rows:
        return V_EMPTY
    counts = {c: sum(1 for r in rows if r["class"] == c) for c in CLASSES}
    named = counts[C_RATIO] + counts[C_COUNT] + counts[C_FILTERED]
    if not named:
        return V_EMPTY
    if counts[C_COUNT] == 0 and counts[C_FILTERED] == 0:
        return V_ONE
    biggest = 0.0
    for arm in ARMS:
        block = (arms.get(arm) or {}).get("drift_pct") or {}
        if block.get("E350") is not None:
            biggest = max(biggest, abs(block["E350"]))
    return V_RULE % (counts[C_RATIO], counts[C_COUNT], counts[C_FILTERED], "%.2f" % biggest,
                     counts[C_UNMOVED])


# ------------------------------------------------------------------ build

def load_cache(pin_id):
    if not os.path.exists(CACHE_PATH):
        return {}
    try:
        with open(CACHE_PATH, "r", encoding="utf-8") as fh:
            done = json.load(fh)
    except (OSError, ValueError):
        return {}
    return done if done.get("pin_id") == pin_id else {}


def run(write_face=True):
    pin = e368.load_pin()
    members, prov = e368.resolve_members(pin)
    pin_paths = [p for p, _ in members]
    say("pin %s: %d members (%s)" % (pin.get("pin_id"), len(members),
                                     {k: v for k, v in prov.items() if not k.endswith("_paths")}))

    published = published_summaries()
    if published is None:
        raise SystemExit("published summaries missing")

    done = load_cache(pin.get("pin_id"))
    arms = {}
    index = e353.build_index()
    say("face index built")
    plans = {"live": None, "pinned_list": pin_paths, "pinned_bytes": members}
    for arm in ARMS:
        if arm in (done.get("arms") or {}):
            say("%s: cached" % arm)
            arms[arm] = done["arms"][arm]
            continue
        say("%s: scanning" % arm)
        arms[arm] = summarize_arm(plans[arm], index)
        done.setdefault("arms", {})[arm] = arms[arm]
        done["pin_id"] = pin.get("pin_id")
        with open(CACHE_PATH, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(done, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")

    rows, arm_pop = table(published, arms)
    drift = {}
    for arm in ARMS:
        drift[arm] = {study: (None if arm_pop.get((study, arm)) is None
                              else round((arm_pop[(study, arm)] - 1) * 100, 3))
                      for study in ("E350", "E353")}
    arms_block = {arm: {"population_source": arms[arm].get("population_source"),
                        "drift_pct": drift[arm],
                        "E350": arms[arm].get("E350"), "E353": arms[arm].get("E353")}
                  for arm in ARMS}

    cross = {"e353_published_pairs": published["E353"]["summary"].get("pairs"),
             "e353_live_pairs": (arms["live"].get("E353") or {}).get("pairs"),
             "agrees": (arms["live"].get("E353") or {}).get("pairs")
                       == published["E353"]["summary"].get("pairs")}

    # Membership, not vibes: the pinned arms read the SAME disk bytes as live for every shared
    # member, so a gap between the two arms that the member lists do not explain is a fact about
    # the members, not about the population.  Path sets only (no reads), before each study's own
    # file exclusion, so the arithmetic is reproducible from the tree.
    live_paths = set(e350.e346._corpus())
    pin_set = set(pin_paths)
    overlap = {"common": len(live_paths & pin_set), "only_live": len(live_paths - pin_set),
               "only_pin": len(pin_set - live_paths),
               "only_live_paths": sorted(live_paths - pin_set)[:40],
               "basis": ("path sets from the walker and the pin, before any study's own-source "
                         "exclusion; the bytes behind a shared member are the same disk bytes in "
                         "both arms, so only the exclusive members can move a count by membership")}

    decide_input = dict(arms_block)
    decide_input["published_E350_pop"] = published["E350"]["summary"].get("corpus_sources")
    verdict = decide(rows, decide_input)

    counts = {c: sum(1 for r in rows if r["class"] == c) for c in CLASSES}
    face = {
        "study": STUDY,
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "today": TODAY,
        "evidence_cutoff": TODAY,
        "source": SELF_REL,
        "pin": pin.get("git_commit"),
        "pin_id": pin.get("pin_id"),
        "pin_file": os.path.relpath(e368.PIN_PATH, ROOT).replace("\\", "/"),
        "pin_members": len(members),
        "bytes_provenance": {k: v for k, v in prov.items() if not k.endswith("_paths")},
        "store_needed_paths": prov["store_needed_paths"],
        "rules": {
            "arms": list(ARMS),
            "ratio": "bit-identical in every arm whose population moved",
            "count": ("moves everywhere it moved and matches published * population growth "
                      "within %.0f%%" % (POP_TOL * 100)),
            "filtered": "moves, but not proportionally (the new members hit the predicate unevenly)",
            "flag": "boolean leaf", "other": "non-numeric leaf",
            "unmoved": "the study's population did not change in any arm, so nothing is claimed",
            "tolerated_drift_pct": ("largest relative population change at which the key still "
                                    "read exactly the published number"),
        },
        "cross_check": cross,
        "population_overlap": overlap,
        "arm_populations": {arm: {study: population_of(study, _summary_of((arms[arm] or {}).get(study)))
                                  for study in ("E350", "E353")} for arm in ARMS},
        "published_populations": {study: population_of(study, published[study]["summary"])
                                 for study in ("E350", "E353")},
        "class_counts": counts,
        "keys": rows,
        "arms": arms_block,
        "verdict": verdict,
        "bound": (
            "the arm set is three scans plus the face on disk; 'published' is therefore the same "
            "study at whatever vintage its face was written, so a key that moves between published "
            "and a pinned arm may be a vintage difference as well as a population difference -- "
            "the pinned arms are the controlled pair and live vs pinned is the population pair; "
            "classification is measured from the arms, not from the key's name, so a key whose "
            "published value is zero can only ever read 'ratio' (documented per row); E353's "
            "summary is derived from E350's rows in the same scan instead of a second walk, and "
            "the live arm's pairs is cross-checked against E353's published face rather than "
            "assumed equal"),
    }
    if write_face:
        os.makedirs(OUTDIR, exist_ok=True)
        for target in (os.path.join(OUTDIR, FACE), os.path.join(OUTDIR, LATEST)):
            with open(target, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
                fh.write("\n")
    return face


# ------------------------------------------------------------------ verify / selftest

def verify():
    dated = os.path.join(OUTDIR, FACE)
    if not os.path.exists(dated):
        say("no published face")
        return 2
    with open(dated, "r", encoding="utf-8") as fh:
        face = json.load(fh)
    problems = []
    published = published_summaries()
    if published is None:
        problems.append("upstream summaries missing")
    else:
        for study in ("E350", "E353"):
            if published[study]["summary"] != {} and face["published_populations"][study] is None:
                problems.append("%s: published population not recorded" % study)
    rows, _arm_pop = table(published, {arm: {study: face["arms"][arm][study]
                                             for study in ("E350", "E353")}
                                       for arm in ARMS})
    if rows != face["keys"]:
        drift = [r["key"] for r, k in zip(rows, face["keys"]) if r != k][:5]
        problems.append("key table does not re-derive from the published arms: %s" % drift)
    recount = {c: sum(1 for r in face["keys"] if r["class"] == c) for c in CLASSES}
    if recount != face["class_counts"]:
        problems.append("class_counts %r != recount %r" % (face["class_counts"], recount))
    decide_input = dict(face["arms"])
    decide_input["published_E350_pop"] = face["published_populations"]["E350"]
    if decide(face["keys"], decide_input) != face["verdict"]:
        problems.append("verdict does not re-derive")
    for row in face["keys"]:
        if row["class"] == C_RATIO and row["published"] not in (0, None) and not _numeric(row["published"]):
            problems.append("%s/%s classified ratio on a non-numeric value" % (row["study"], row["key"]))
            break
    say("verify problems=%s" % problems)
    return 0 if not problems else 1


def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    # (1) flattening loses no key and keeps nesting legible
    flat = flatten("", {"a": 1, "b": {"c": 2, "d": {"e": 3}}, "f": True}, {})
    leg("nested summaries flatten to dotted keys without loss",
        flat == {"a": 1, "b.c": 2, "b.d.e": 3, "f": True}, str(flat))

    # (2) a key that holds while the population grows is a ratio
    c = classify_key(100, {"live": 100, "pinned_list": 100, "pinned_bytes": 100},
                     {"live": 1.02, "pinned_list": 1.0, "pinned_bytes": 1.0})
    leg("a bit-identical key under a bigger population is a ratio", c["class"] == C_RATIO, str(c))
    leg("and it publishes the drift it tolerated", c["tolerated_drift_pct"] == 2.0, str(c))

    # (3) a count that grows with the population is a count
    c = classify_key(131, {"live": 134, "pinned_list": 131, "pinned_bytes": 131},
                     {"live": 1.02, "pinned_list": 1.0, "pinned_bytes": 1.0})
    leg("131 * 1.02 = 133.6 is inside 2% of 134 -> count", c["class"] == C_COUNT, str(c))

    # (4) a predicate that the new members do not satisfy is filtered
    c = classify_key(131, {"live": 150, "pinned_list": 90, "pinned_bytes": 80},
                     {"live": 1.2, "pinned_list": 0.9, "pinned_bytes": 0.8})
    leg("a moving key far from the proportional prediction is filtered",
        c["class"] == C_FILTERED, str(c))
    leg("a filtered key that never held reports zero tolerated drift",
        c["tolerated_drift_pct"] == 0.0, str(c))

    # (5) an arm that did not move the population cannot be cited as evidence
    c = classify_key(5, {"live": 5, "pinned_list": 5, "pinned_bytes": 5},
                     {"live": 1.0, "pinned_list": 1.0, "pinned_bytes": 1.0})
    leg("no arm moved the population -> unmoved, nothing claimed, tolerated drift null",
        c["class"] == C_UNMOVED and c["tolerated_drift_pct"] is None, str(c))

    # (6) booleans and strings are not silently classified as ratios
    leg("a boolean is a flag", classify_key(True, {"live": True}, {"live": 1.1})["class"] == C_FLAG)
    leg("a string leaf is other", classify_key("x", {"live": "x"}, {"live": 1.1})["class"] == C_OTHER)

    # (7) the two studies' populations are read from different fields
    leg("E350's population is its source count",
        population_of("E350", {"corpus_sources": 2343}) == 2343)
    leg("E353's population is its upstream pair count",
        population_of("E353", {"upstream_pairs": 131, "pairs": 131}) == 131)

    # (8) the derivation reuses E353's own functions, so an empty population claims nothing
    leg("an empty population yields E353's own empty verdict",
        e353.decide(e353.summarize([], 0, {})) == e353.V_EMPTY)

    # (9) the live arm's cross-check is a published comparison, not an assertion of equality
    path = os.path.join(OUTDIR, LATEST)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            face = json.load(fh)
        cross = face.get("cross_check") or {}
        leg("the face publishes whether its live arm agrees with E353's own face",
            "agrees" in cross and "e353_live_pairs" in cross, str(cross))
    else:
        leg("no face yet, cross-check leg is not claimed", True, "skipped")

    failed = [n for n, ok, _ in legs if not ok]
    for name, ok, detail in legs:
        say(("PASS " if ok else "FAIL ") + name + (("  [" + detail + "]") if not ok and detail else ""))
    say("selftest %d/%d" % (len(legs) - len(failed), len(legs)))
    return 0 if not failed else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "verify").lower()
    if cmd == "run":
        face = run()
        say("verdict: %s" % face["verdict"])
        say("classes: %s" % face["class_counts"])
        for row in face["keys"]:
            say("  %-6s %-46s class=%-8s tolerated=%s%%"
                % (row["study"], row["key"], row["class"], row["tolerated_drift_pct"]))
        return 0
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    say("usage: run | verify | selftest")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))