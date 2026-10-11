#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""E16 roster probe - alphagen slice-2 random-grammar census input face (catalog #17).

Purpose (E16 leg-1, r877 bm-b):
  Mechanical facts face for the planned random-grammar cheap census on the
  rebuilt astock_daily stock panel (T23 r840 slice-2 prescription: sample K
  formulas from the vendored A158 substrate grammar, per-formula rank-IC
  distribution vs A158-known-negative face + same-machinery permutation nulls;
  verdict licenses or kills the RL build BEFORE any training spend).

Laws honored:
  - Zero judgment, zero thresholds invented here: descriptive facts only.
    K membership, trial accounting, nulls count are PINNED PROPOSALS for the
    prereg (next leg) to freeze, not decisions made here.
  - L1 deterministic, zero network, read-only inputs, append-safe output.
  - A158 lineage negative prior disclosed verbatim (157/158 |ICIR|<0.09 on
    ETF/fund corpus; A9 0/9, A10 0/16 gate sub-lines) -- this census differs on
    search engine (random sampling vs fixed list), corpus (broad stock
    cross-section vs 48 ETF/fund), objective (distribution face vs registration).

Usage:
  python scripts/alphagen_rg_roster.py run       # emit results/alphagen_rg/e16_roster.json
  python scripts/alphagen_rg_roster.py selftest # hermetic offline self-check
"""
import glob
import importlib.util
import json
import os
import random
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PER_DIR = os.path.join(ROOT, "data", "astock_daily", "per")
ELIG = os.path.join(ROOT, "data", "fundamental", "eligibility.csv")
BMASK = os.path.join(ROOT, "data", "fundamental", "b_layer_mask.csv")
A158 = os.path.join(ROOT, "scripts", "alpha158_compare.py")
OUT_DIR = os.path.join(ROOT, "results", "alphagen_rg")
OUT_PATH = os.path.join(OUT_DIR, "e16_roster.json")

EXPECTED_CUTOFF = "2026-10-09"          # last complete bar day (Fri) per S6 faces
CENSUS_WINDOW_START = "2018-01-01"      # pinned proposal for prereg (disclosed)
K_DEPTH1 = 120                          # pinned proposal
K_DEPTH2 = 80                           # pinned proposal (2 op passes each)
K_NULLS = 200                           # per-date cross-sectional rank permutation
FWD = "1d_close_to_close"                # pinned proposal
SAMPLER_SEED = 20261011                 # pinned proposal (deterministic sample)


def import_a158_inventory():
    """Import scripts/alpha158_compare.py verbatim; run its parse gate."""
    spec = importlib.util.spec_from_file_location("alpha158_compare", A158)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    kbar_names, ops, expr, price_names, gate = mod.build_inventory()
    return kbar_names, ops, expr, price_names, gate


def classify_ops(expr_templates):
    """Split ops into single-input vs cross-input by distinct $field tokens."""
    import re
    single, cross = [], []
    for op, tmpl in expr_templates.items():
        if isinstance(tmpl, (list, tuple)):
            tmpl = tmpl[0] if tmpl else "n/a"
        if not isinstance(tmpl, str) or tmpl == "n/a":
            single.append(op)  # conservative: treat unparseable as single
            continue
        fields = set(re.findall(r"\$([A-Za-z0-9_]+)", tmpl))
        (cross if len(fields) >= 2 else single).append(op)
    return sorted(single), sorted(cross)


def panel_disk_truth(sample_n=40, seed=7):
    """Per-file disk count + sampled last-date check (r840 disk-truth law)."""
    files = sorted(glob.glob(os.path.join(PER_DIR, "*.csv")))
    rnd = random.Random(seed)
    sample = rnd.sample(files, min(sample_n, len(files)))
    import pandas as pd
    tails = []
    for f in sample:
        with open(f, "r", encoding="utf-8") as fh:
            tail = fh.readlines()[-1]
        tails.append(tail.split(",")[0])
    return {
        "per_files_on_disk": len(files),
        "sampled_n": len(sample),
        "sampled_last_dates_min": min(tails),
        "sampled_last_dates_max": max(tails),
        "all_sampled_at_expected_cutoff": all(t == EXPECTED_CUTOFF for t in tails),
    }


def universe_faces():
    import pandas as pd
    e = pd.read_csv(ELIG)
    b = pd.read_csv(BMASK)
    elig_codes = set(e.loc[e["eligible"] == True, "code"].astype(str))
    ok_static = set(b.loc[b["ok_static"] == True, "code"].astype(str))
    joined = elig_codes & ok_static
    return {
        "eligibility_rows": int(len(e)),
        "eligibility_eligible": int(len(elig_codes)),
        "bmask_rows": int(len(b)),
        "bmask_ok_static": int(len(ok_static)),
        "universe_join_n": int(len(joined)),
        "pit_disclosure": (
            "eligibility.csv is a <24h as-collected snapshot (ST/loss face); "
            "applying it backward over history is a measurement-face universe "
            "caveat, disclosed -- survivors face strict-PIT rules only in a "
            "later judged prereg; b_layer_mask first/last board ranges are "
            "historical and used as the per-code validity window"
        ),
    }


def mini_timing_pass(n_stocks=50, seed=11):
    """Time one rolling-op pass over a stock sample to extrapolate burn cost."""
    import pandas as pd
    files = sorted(glob.glob(os.path.join(PER_DIR, "*.csv")))
    rnd = random.Random(seed)
    sample = rnd.sample(files, min(n_stocks, len(files)))
    t0 = time.time()
    rows = 0
    for f in sample:
        d = pd.read_csv(f, usecols=["date", "close"])
        d = d[d["date"] >= CENSUS_WINDOW_START]
        v = d["close"]
        r = v / v.shift(20) - 1.0          # ROC(close, 20) depth-1 stand-in
        s = r.rolling(20).std()            # depth-2 stand-in pass
        rows += len(d)
    dt = time.time() - t0
    est_full_passes = K_DEPTH1 + 2 * K_DEPTH2  # depth-2 costs two passes
    return {
        "sampled_stocks": len(sample),
        "sampled_rows_window_2018plus": int(rows),
        "elapsed_sec_2_passes": round(dt, 3),
        "est_full_panel_rows_2018plus": int(rows * len(files) / max(len(sample), 1)),
        "est_passes_total": est_full_passes,
        "naive_singlethread_est_min": round(
            dt / 2 * est_full_passes * len(files) / max(len(sample), 1) / 60.0, 1
        ),
        "shard_note": "pool batch 12 shards x workers>=4 pattern (R31 lane law); "
                      "estimate is naive singlethread, pool burn multiplies down",
    }


def grammar_space(single_ops, cross_ops, kbar_n=9, price0_n=4):
    base_inputs = ["open", "high", "low", "close", "volume", "amount",
                   "vwap", "turnover"]
    n_base = len(base_inputs)
    windows = [5, 10, 20, 30, 60]
    d1_space = len(single_ops) * n_base * len(windows) + len(cross_ops) * (n_base ** 2) * len(windows)
    return {
        "base_inputs": base_inputs,
        "windows": windows,
        "single_input_ops": single_ops,
        "cross_input_ops": cross_ops,
        "depth1_expression_space_size": int(d1_space),
        "depth2_note": "depth-2 sampled as op(depth-1 result, window) -- space "
                       "is d1_space x ops x windows; sampled, not enumerated",
    }


def design_pin():
    return {
        "sampler_seed": SAMPLER_SEED,
        "K_depth1": K_DEPTH1,
        "K_depth2": K_DEPTH2,
        "K_total": K_DEPTH1 + K_DEPTH2,
        "nulls": {
            "design": "per-date cross-sectional rank permutation "
                      "(factor ranks shuffled within each date, same computed "
                      "factor matrix reused -- same-machinery null face)",
            "K_nulls": K_NULLS,
        },
        "forward_return": FWD,
        "census_window_start": CENSUS_WINDOW_START,
        "trial_budget_law": "BACKTEST_PLAN <=500 trials/30d; census counted as "
                            "K_total trials on the batch ledger face (proposal "
                            "for prereg to freeze; nulls are calibration, not trials)",
        "a158_negative_prior": "157/158 |ICIR|<0.09 ETF/fund corpus; A9 0/9 "
                                "single-gate; A10 0/16 combo (lineage disclosure)",
        "exit_axis": "measurement census -- no position/exit machinery; "
                     "survivor consumption route = time-series gate / input "
                     "feature on core48 (A158-TSGATE-P1 + A10 precedents), "
                     "long-only T+1 cost model; judged faces later need their "
                     "own exit-axis explicit 3-choose-1 declaration",
        "d6_law": "same-family max|corr|>=0.7 reject at registration; census "
                  "output is distribution face only -- D6 enforced on any "
                  "survivor registration, not here",
        "consumer_plan": "verdict licenses or kills the RL build before "
                         "training spend (T23 slice-2 gate); if licensed, next "
                         "step = N2 U3 channel-1 drafting window via "
                         "PREREG_TEMPLATE (alpha-mechanism 4-choose-1 + D6 + "
                         "exit-axis + seed gate + collision probe)",
    }


def run():
    kbar_names, ops, expr, price_names, gate = import_a158_inventory()
    single_ops, cross_ops = classify_ops(expr)
    roster = {
        "probe": "E16 alphagen slice-2 random-grammar census roster (leg-1)",
        "queue_row": "state/queue/explore.md E16",
        "machine": os.environ.get("COMPUTERNAME", "bm-b"),
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "substrate_gate": gate,
        "kbar_names": kbar_names,
        "price0_names": price_names,
        "grammar_space": grammar_space(single_ops, cross_ops, len(kbar_names), len(price_names)),
        "panel_disk_truth": panel_disk_truth(),
        "universe_faces": universe_faces(),
        "mini_timing": mini_timing_pass(),
        "design_pin": design_pin(),
        "l1_zero_network": True,
        "zero_judgment": True,
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(roster, fh, ensure_ascii=False, indent=1, sort_keys=True)
    print(json.dumps({
        "out": OUT_PATH,
        "per_files": roster["panel_disk_truth"]["per_files_on_disk"],
        "cutoff_ok": roster["panel_disk_truth"]["all_sampled_at_expected_cutoff"],
        "gate_158": gate["total_is_158"],
        "universe_join_n": roster["universe_faces"]["universe_join_n"],
        "naive_burn_est_min": roster["mini_timing"]["naive_singlethread_est_min"],
    }, ensure_ascii=False))


def selftest():
    """Hermetic: no panel/disk reads; pure functions only."""
    ok = 0

    def chk(name, cond):
        nonlocal ok
        assert cond, "SELFTEST FAIL: " + name
        ok += 1

    # classify_ops on canned templates
    single, cross = classify_ops({"ROC": ["Ref($close,%d)/Ref($close,%d)-1"],
                                  "CORR": ["Corr($close,$volume,%d)"],
                                  "OPAQUE": ["n/a"]})
    chk("corr_is_cross", "CORR" in cross)
    chk("roc_is_single", "ROC" in single)
    chk("opaque_fallback_single", "OPAQUE" in single)

    # grammar space arithmetic
    g = grammar_space(["ROC", "STD"], ["CORR"])
    chk("base_inputs_8", len(g["base_inputs"]) == 8)
    expected_d1 = 2 * 8 * 5 + 1 * 64 * 5
    chk("depth1_space_arith", g["depth1_expression_space_size"] == expected_d1)

    # design pin invariants
    d = design_pin()
    chk("k_total", d["K_total"] == 200)
    chk("budget_law_cited", "500" in d["trial_budget_law"])
    chk("exit_axis_present", "exit" in d["exit_axis"].lower())
    chk("d6_present", "0.7" in d["d6_law"])
    chk("seed_deterministic", d["sampler_seed"] == SAMPLER_SEED)
    chk("nulls_count", d["nulls"]["K_nulls"] == K_NULLS)

    # substrate gate on the real vendored file (read-only parse, no network)
    kbar_names, ops, expr, price_names, gate = import_a158_inventory()
    chk("gate_158", gate["total_is_158"])
    chk("gate_kbar9", gate["kbar_count"] == 9)
    chk("gate_ops29", gate["rolling_ops"] == 29)
    chk("price0_4", gate["price0_count"] == 4 if "price0_count" in gate else len(price_names) == 4)

    print(json.dumps({"selftest": "PASS", "checks": ok}))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "run":
        run()
    elif cmd == "selftest":
        selftest()
    else:
        print("usage: alphagen_rg_roster.py run|selftest")
        sys.exit(2)
