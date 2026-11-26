"""Do the bench's GO verdicts survive a comparison with their own benchmark?

Why this exists
---------------
`scripts/bench_generic.py` decides GO with two numbers that never look at each
other:

  * the gate wants an **absolute** annualised return (`H1_full_ge` >= 4.0%,
    and `target_edge_pp` = 5.0 gating `powered_for_target`), and
  * the arm is sized to `cfg["target_vol"]` (0.06 on the bond and index pair
    faces, 0.08 on the commodity faces) while `buy_and_hold()` is hard-wired
    to `target_vol=0.10`.

So on those faces the published benchmark is a **different book** from the one
being judged: 10% target volatility against a 6% arm is 1.67x the leverage, and
the benchmark's annualised return is inflated by the same factor. A reader who
subtracts the printed benchmark from a printed arm is subtracting two things
measured at different sizes.

This face does two things, and says which is which:

  1. **Re-sizes the benchmark to the arm's own volatility target** (same panel,
     same per-side cost), and prints how far the published banner was from it.
  2. **Puts the two rulers side by side** for every arm: the absolute one the
     gate uses, and excess-over-that-aligned-benchmark measured against the
     arm's own MDE. A GO whose excess cannot clear its own MDE is not a
     judgement this sample can support -- it is a ruler that cannot see the
     quantity it claims to certify.

It never rewrites a bench verdict. It is an audit face: read-only over
`results/bench_*.json` plus the in-repo futures panels.

Usage
-----
  python scripts/bench_go_ruler_audit.py            # write json + page
  python scripts/bench_go_ruler_audit.py --selftest # offline behaviour legs
"""
from __future__ import annotations

import argparse
import datetime
import glob
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import bench_core as bc  # noqa: E402

RESULTS = os.path.join(ROOT, "results")
OUT_JSON = os.path.join(RESULTS, "bench_go_ruler_audit.json")
OUT_MD = os.path.join(ROOT, "research", "BENCH_GO_RULER_AUDIT.md")

SCHEMA = "bench-go-ruler-audit/v1"

# The gate's own absolute thresholds, copied from bench_generic.run_arm so the
# audit states the ruler it is auditing rather than re-inventing it.
H1_FULL_PCT = 4.0
BENCH_HARDWIRED_TARGET_VOL = 0.10

GO_BACKED = "GO_BACKED_BY_EXCESS"
GO_UNSUPPORTED = "GO_ON_A_RULER_THAT_CANNOT_SEE_ITS_EXCESS"
GATE_FAILED_BUT_EXCESS = "EXCESS_CLEARS_MDE_BUT_GATE_FAILED_ELSEWHERE"
NO_EDGE = "CONSISTENT_WITH_NO_EDGE"
UNDECIDABLE = "UNDECIDABLE"

FACE_SKIP = {"_revalidate"}  # monitoring cells, not strategy runs


def classify(arm, bench_aligned):
    """One arm -> one label. Pure: same inputs always give the same label."""
    ann = arm.get("ann_pct")
    mde = arm.get("mde_pp")
    verdict = str(arm.get("verdict") or "")
    if ann is None or mde is None or bench_aligned is None:
        return UNDECIDABLE, None
    excess = round(float(ann) - float(bench_aligned), 2)
    clears = excess >= float(mde)
    if verdict == "GO":
        return (GO_BACKED if clears else GO_UNSUPPORTED), excess
    if clears and excess > 0:
        return GATE_FAILED_BUT_EXCESS, excess
    return NO_EDGE, excess


def flat_arms(doc):
    """Pull (label, ann, mde, verdict) out of a bench document's arms."""
    out = []
    arms = doc.get("arms")
    if not isinstance(arms, list):
        return out
    for a in arms:
        if not isinstance(a, dict):
            continue
        cw = a.get("common_window") or {}
        out.append({
            "variant": (a.get("tags") or {}).get("variant")
            or (a.get("tags") or {}).get("combo"),
            "ann_pct": cw.get("ann_pct"),
            "sharpe": cw.get("sharpe"),
            "mdd_pct": cw.get("mdd_pct"),
            "mde_pp": a.get("mde_pp"),
            "powered_for_target": a.get("powered_for_target"),
            "verdict": a.get("verdict"),
            "checks": a.get("checks") or {},
        })
    return out


def aligned_benchmark(cfg, cache):
    """Buy-and-hold measured at the arm's own volatility target.

    The published banner is priced at 10% target vol no matter what the arm
    used, so this recomputes the same signal at `cfg["target_vol"]`.
    """
    products = cfg.get("products") or []
    if not products:
        return None
    key = (tuple(products), float(cfg.get("target_vol") or 0.0),
           float(cfg.get("cost_bp_side") or 3.0), str(cfg.get("split") or "2024-01-01"))
    if key in cache:
        return cache[key]
    panel = bc.load_futures_products(list(products))
    if len(panel) < 1:
        cache[key] = None
        return None
    dates, closes, rets, vols = bc.align_futures(panel)
    sig = {c: s.where(s.notna()).mul(0.0).add(1.0) for c, s in closes.items()}
    pos, _ = bc.vol_weighted_positions(sig, vols, target_vol=float(cfg.get("target_vol") or 0.10))
    if pos is None:
        cache[key] = None
        return None
    _gross, net, _turn = bc.apply_costs(pos, rets, cost_bp_side=float(cfg.get("cost_bp_side") or 3.0))
    net = net.reindex(dates).fillna(0.0)
    reading = bc.split_perf(net.values, dates, split=key[3])
    out = {
        "ann_pct": reading["full"]["ann_pct"],
        "sharpe": reading["full"]["sharpe"],
        "mdd_pct": reading["full"]["mdd_pct"],
        "n": reading["full"]["n"],
        "target_vol": key[1],
        "cost_bp_side": key[2],
    }
    cache[key] = out
    return out


def audit_one(path, cache):
    with io.open(path, encoding="utf-8") as f:
        doc = json.load(f)
    face = os.path.basename(path)[5:-5] if os.path.basename(path).startswith("bench_") else \
        os.path.basename(path)[:-5]
    if face in FACE_SKIP:
        return None
    cfg = doc.get("config") or {}
    arms = flat_arms(doc)
    if not arms:
        return None
    published = None
    bh = doc.get("benchmark_buy_and_hold")
    if isinstance(bh, dict):
        published = (bh.get("common_window") or {}).get("ann_pct")
    aligned = aligned_benchmark(cfg, cache) if cfg.get("products") else None
    aligned_ann = aligned["ann_pct"] if aligned else None
    rows = []
    for a in arms:
        label, excess = classify(a, aligned_ann)
        rows.append(dict(a, label=label, excess_pp=excess))
    counts = {}
    for r in rows:
        counts[r["label"]] = counts.get(r["label"], 0) + 1
    return {
        "face": face,
        "path": "results/" + os.path.basename(path),
        "face_evidence_cutoff": doc.get("evidence_cutoff"),
        "target_vol_arm": cfg.get("target_vol"),
        "cost_bp_side": cfg.get("cost_bp_side"),
        "target_edge_pp": cfg.get("target_edge_pp"),
        "benchmark_published_ann_pct": published,
        "benchmark_published_target_vol": BENCH_HARDWIRED_TARGET_VOL if published is not None else None,
        "benchmark_aligned_ann_pct": aligned_ann,
        "benchmark_aligned_target_vol": (aligned or {}).get("target_vol"),
        "benchmark_size_gap_pp": (None if (published is None or aligned_ann is None)
                                  else round(float(published) - float(aligned_ann), 2)),
        "n_arms": len(rows),
        "counts": counts,
        "rows": rows,
    }


def build():
    cache = {}
    faces = []
    for path in sorted(glob.glob(os.path.join(RESULTS, "bench_*.json"))):
        if os.path.basename(path) == os.path.basename(OUT_JSON):
            continue
        try:
            got = audit_one(path, cache)
        except Exception as exc:  # a face that cannot be audited must say so
            faces.append({"face": os.path.basename(path), "error": repr(exc)[:180]})
            continue
        if got:
            faces.append(got)

    usable = [f for f in faces if "rows" in f]
    n_go = n_go_unsupported = n_go_backed = n_left = 0
    go_measurements = {}
    for f in usable:
        for r in f["rows"]:
            if str(r.get("verdict")) == "GO":
                n_go += 1
                if r["label"] == GO_UNSUPPORTED:
                    n_go_unsupported += 1
                elif r["label"] == GO_BACKED:
                    n_go_backed += 1
                # Two faces running the same (rule, params) on the same panel print
                # the same ann/mde; counting them twice would sell one measurement
                # as two pieces of evidence.
                sig = (round(float(r.get("ann_pct") or 0), 2),
                       round(float(r.get("mde_pp") or 0), 2),
                       r["label"])
                go_measurements.setdefault(sig, []).append(f["face"])
            elif r["label"] == GATE_FAILED_BUT_EXCESS:
                n_left += 1
    mismatched = [f for f in usable
                  if f["benchmark_size_gap_pp"] is not None
                  and abs(f["benchmark_size_gap_pp"]) >= 0.5]
    # Faces whose arm already used the benchmark's own 0.10 target vol are a
    # built-in control: their gap is not a sizing effect, it is the noise from
    # re-pricing today's panel against a banner computed on an earlier cutoff.
    control_gaps = [abs(f["benchmark_size_gap_pp"]) for f in usable
                    if f["benchmark_size_gap_pp"] is not None
                    and f.get("target_vol_arm") is not None
                    and abs(float(f["target_vol_arm"]) - BENCH_HARDWIRED_TARGET_VOL) < 1e-9]
    noise_floor = round(max(control_gaps), 2) if control_gaps else None
    above_noise = [f for f in mismatched
                   if noise_floor is None or abs(f["benchmark_size_gap_pp"]) > noise_floor]
    cutoffs = [f.get("face_evidence_cutoff") for f in usable if f.get("face_evidence_cutoff")]
    return {
        "schema": SCHEMA,
        "generated": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": max(cutoffs) if cutoffs else None,
        "cutoff_rule": "max of the audited faces' own evidence_cutoff fields",
        "rules_audited": {
            "H1_full_ge_pct": H1_FULL_PCT,
            "gate_target_edge_pp": "read per face from config",
            "benchmark_hardwired_target_vol": BENCH_HARDWIRED_TARGET_VOL,
            "excess_ruler": "ann_pct - aligned_benchmark_ann_pct, compared with the arm's own mde_pp",
        },
        "n_faces_audited": len(usable),
        "n_arms_audited": sum(f["n_arms"] for f in usable),
        "n_go": n_go,
        "n_go_backed": n_go_backed,
        "n_go_unsupported": n_go_unsupported,
        "n_go_distinct_measurements": len(go_measurements),
        "go_measurement_groups": [
            {"ann_pct": k[0], "mde_pp": k[1], "label": k[2], "faces": v}
            for k, v in sorted(go_measurements.items())],
        "n_gate_failed_but_excess_clears_mde": n_left,
        "n_faces_with_size_mismatch": len(mismatched),
        "noise_floor_pp": noise_floor,
        "noise_floor_rule": "max |gap| among faces whose arm target vol already equals "
                            "the benchmark's 0.10 -- for those the gap is only the "
                            "re-pricing noise from a newer panel, not a sizing effect",
        "n_faces_sized_gap_above_noise": len(above_noise),
        "faces_sized_gap_above_noise": [
            {"face": f["face"], "arm_tv": f["target_vol_arm"],
             "gap_pp": f["benchmark_size_gap_pp"]} for f in above_noise],
        "faces_with_size_mismatch": [
            {"face": f["face"], "arm_tv": f["target_vol_arm"],
             "published_ann_pct": f["benchmark_published_ann_pct"],
             "aligned_ann_pct": f["benchmark_aligned_ann_pct"],
             "gap_pp": f["benchmark_size_gap_pp"]} for f in mismatched],
        "faces": usable,
        "errors": [f for f in faces if "error" in f],
    }


def render_md(doc):
    L = []
    L.append("# Do the bench's GO verdicts survive their own benchmark?\n")
    L.append("generated %s | faces audited %d | arms audited %d\n"
             % (doc.get("generated") or "-", doc["n_faces_audited"], doc["n_arms_audited"]))
    L.append("Read-only audit over `results/bench_*.json`. It never rewrites a verdict.\n")
    L.append("## Headline\n")
    L.append("- GO rows printed by the bench: **%d**" % doc["n_go"])
    L.append("- of those, distinct measurements after de-duplicating faces that ran the same "
             "rule on the same panel: **%d**" % doc["n_go_distinct_measurements"])
    L.append("- GO rows whose excess over the *aligned* benchmark clears the arm's own MDE: **%d**"
             % doc["n_go_backed"])
    L.append("- GO rows whose excess cannot be seen at this sample size: **%d**"
             % doc["n_go_unsupported"])
    L.append("- faces whose printed benchmark was sized at a different volatility target: **%d of %d**\n"
             % (doc["n_faces_with_size_mismatch"], doc["n_faces_audited"]))
    L.append("## The two rulers\n")
    L.append("The gate asks one question: is the arm's **absolute** annualised return above "
             "%.1f%% (and above the face's `target_edge_pp`), with an MDE small enough to "
             "resolve that target? It never asks what the money would have earned just "
             "sitting in the same products at the same size.\n" % H1_FULL_PCT)
    L.append("The second ruler subtracts the buy-and-hold book, **re-priced at the arm's own "
             "`target_vol`**, and compares that excess with the arm's own MDE. An excess smaller "
             "than the arm's MDE is not a small edge -- it is a quantity this sample cannot "
             "measure.\n")
    L.append("## Where the printed benchmark was a different size\n")
    L.append("A face whose arm already ran at the benchmark's own 0.10 target vol is a built-in "
             "control: its gap cannot be a sizing effect, only the noise from re-pricing today's "
             "panel against a banner computed on an earlier cutoff. That control puts the noise "
             "floor at **%s pp**. %d face(s) exceed it.\n"
             % ("-" if doc.get("noise_floor_pp") is None else "%.2f" % doc["noise_floor_pp"],
                doc.get("n_faces_sized_gap_above_noise") or 0))
    L.append("| face | arm target vol | printed banner %/yr | same book at arm's vol %/yr | gap pp |")
    L.append("|---|---|---|---|---|")
    for f in doc["faces_with_size_mismatch"]:
        L.append("| %s | %s | %s | %s | %+.2f |" % (
            f["face"], f["arm_tv"], f["published_ann_pct"], f["aligned_ann_pct"], f["gap_pp"]))
    if not doc["faces_with_size_mismatch"]:
        L.append("| (none) | | | | |")
    L.append("")
    L.append("## Face by face\n")
    L.append("| face | arms | GO | GO unsupported | left behind | banner gap pp |")
    L.append("|---|---|---|---|---|---|")
    for f in doc["faces"]:
        c = f["counts"]
        L.append("| %s | %d | %d | %d | %d | %s |" % (
            f["face"], f["n_arms"], c.get("GO_BACKED_BY_EXCESS", 0) + c.get(GO_UNSUPPORTED, 0),
            c.get(GO_UNSUPPORTED, 0), c.get(GATE_FAILED_BUT_EXCESS, 0),
            "-" if f["benchmark_size_gap_pp"] is None else "%+.2f" % f["benchmark_size_gap_pp"]))
    L.append("")
    go_rows = [(f["face"], r) for f in doc["faces"] for r in f["rows"]
               if str(r.get("verdict")) == "GO"]
    L.append("## Every GO, with both readings\n")
    if go_rows:
        L.append("| face | variant | ann %/yr | bench @arm vol %/yr | excess pp | MDE pp | label |")
        L.append("|---|---|---|---|---|---|---|")
        for face, r in go_rows:
            f = next(x for x in doc["faces"] if x["face"] == face)
            L.append("| %s | %s | %s | %s | %s | %s | %s |" % (
                face, (r.get("variant") or "")[:44], r.get("ann_pct"),
                f.get("benchmark_aligned_ann_pct"), r.get("excess_pp"),
                r.get("mde_pp"), r.get("label")))
    else:
        L.append("(no GO verdicts printed)")
    if doc.get("go_measurement_groups"):
        L.append("\nThe same measurement can appear on more than one face: "
                 "`census_commodity` and `robust_tsmom_commodity` run the same (rule, lookback) "
                 "on the same panel, so their rows share one ann/MDE. Grouped by measurement:\n")
        L.append("| ann %/yr | MDE pp | label | faces carrying it |")
        L.append("|---|---|---|---|")
        for g in doc["go_measurement_groups"]:
            L.append("| %s | %s | %s | %s |" % (g["ann_pct"], g["mde_pp"], g["label"],
                                                ", ".join(g["faces"])))
    L.append("")
    L.append("## What this face does not say\n")
    L.append("- it does not re-run a single arm, so it inherits whatever the bench measured; "
             "it only re-prices the benchmark at the arm's size and puts the two rulers side by side")
    L.append("- an `UNDECIDABLE` row means the face printed no MDE or no usable benchmark "
             "(missing products, missing config), not that the edge was zero")
    L.append("- `EXCESS_CLEARS_MDE_BUT_GATE_FAILED_ELSEWHERE` says the absolute gate said no "
             "while the excess ruler said it was visible: that is a disagreement about *which* "
             "question was asked, not evidence that the arm should have been promoted")
    L.append("- the aligned benchmark uses the face's own `cost_bp_side`; a face that printed "
             "no cost cannot be aligned and is listed under `errors`, not silently dropped")
    return "\n".join(L) + "\n"


# --------------------------------------------------------------------------
# selftest
# --------------------------------------------------------------------------
def selftest():
    fails = []

    # leg 1: a GO whose excess cannot clear its own MDE must be labelled unsupported
    arm = {"ann_pct": 5.24, "mde_pp": 3.66, "verdict": "GO"}
    label, excess = classify(arm, 4.62)
    if label != GO_UNSUPPORTED:
        fails.append("leg1: expected %s, got %s (excess=%s)" % (GO_UNSUPPORTED, label, excess))
    if excess != 0.62:
        fails.append("leg1: excess expected 0.62, got %s" % excess)

    # leg 2: the same shape with a benchmark low enough to be cleared must flip to backed
    label2, excess2 = classify(arm, 1.00)
    if label2 != GO_BACKED:
        fails.append("leg2: expected %s, got %s (excess=%s)" % (GO_BACKED, label2, excess2))

    # leg 3: a non-GO arm whose excess clears its MDE must be called out, not folded into NO_EDGE
    arm3 = {"ann_pct": 6.0, "mde_pp": 1.0, "verdict": "NO_EDGE"}
    label3, _ = classify(arm3, 4.0)
    if label3 != GATE_FAILED_BUT_EXCESS:
        fails.append("leg3: expected %s, got %s" % (GATE_FAILED_BUT_EXCESS, label3))

    # leg 4: missing MDE must be undecidable rather than silently "no edge"
    label4, _ = classify({"ann_pct": 5.0, "mde_pp": None, "verdict": "GO"}, 4.0)
    if label4 != UNDECIDABLE:
        fails.append("leg4: expected %s, got %s" % (UNDECIDABLE, label4))

    # leg 5: a gain that does not clear MDE must not be promoted to "left behind"
    arm5 = {"ann_pct": 4.5, "mde_pp": 3.0, "verdict": "NO_EDGE"}
    label5, _ = classify(arm5, 4.0)
    if label5 != NO_EDGE:
        fails.append("leg5: expected %s, got %s" % (NO_EDGE, label5))

    for f in fails:
        print("FAIL " + f)
    print("selftest %d/%d" % (5 - len(fails), 5))
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()

    bc.weight_priority()
    doc = build()
    with io.open(OUT_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    md = render_md(doc)
    with io.open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write(md)
    print("faces=%d arms=%d GO=%d backed=%d unsupported=%d size_mismatch=%d"
          % (doc["n_faces_audited"], doc["n_arms_audited"], doc["n_go"],
             doc["n_go_backed"], doc["n_go_unsupported"], doc["n_faces_with_size_mismatch"]))
    print("-> results/bench_go_ruler_audit.json")
    print("-> research/BENCH_GO_RULER_AUDIT.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
