# -*- coding: utf-8 -*-
"""INNOVATION_QUOTA_W10 runner -- PREMIUM-SENT-P1 premium-sentiment
conditional-mean judged batch (INNOVATION-QUOTA-SLOT-10, zoo #97
etf_premium_sentiment CORRECTED face, prereg research/
INNOVATION_QUOTA_W10_PREREG.md FROZEN bm-c r265; berth probe facts
results/_r264bmc_w10_berth_probe_facts.json + freeze-window facts
results/_r265bmc_w10_freeze_probe_facts.json; seed 20326500
three-step law ALL GREEN results/_r265bmc_w10_seed_law_facts.json).

Laws (construction single source = the berth probe, r456 verbatim-
import paradigm; every face below is either imported from
results/_r264bmc_w10_berth_probe.py or parity-asserted against the
frozen facts at run time -- one-face-off = config mismatch VOID,
fail-closed, reported as face-mismatch not data corruption):

  panel   data/fund_premium/panel/panel.csv via csv.DictReader raw
          direct read (non-engine pool face; four-tuple per prereg
          s2: full-history from 2020-01-02, rolling 252 window /
          min_periods 120 -> first decidable 2020-07-03). The panel
          FACE is frozen at the berth/freeze window (last 2026-09-24,
          NAV disclosure lag structural): rows in (2026-09-24,
          evidence_cutoff] are disclosed as an incremental_segment
          and NOT loaded (G-ANCHOR battery pins the frozen face; W9
          panel-forward-advance precedent); rows beyond the cutoff
          are dropped by the forward lockbox (P-5C).
  signal  cm_t = cross-mean premium_adj over panel members per date
          (the zoo-as-written cross-mean premium_z face is
          mathematically degenerate -- per-date cross-sectional z,
          ddof=0, cross-mean identically 0, empirical 2.58e-16 =
          float roundoff; berth-window erratum, retracted face).
          State = rolling-252 percentile: hot = cm > q90(window),
          cold = cm < q10(window), min_periods 120, author-verbatim
          tail-occupancy gate, zero calibration (pct_rank_state
          verbatim import, defaults asserted via inspect.signature).
  price   data/daily/510300.csv via csv.DictReader raw direct read,
          full history, truncated to evidence cutoff 2026-09-29
          (P-5C frozen binding); fwd_h(d) = close(d+h)/close(d) - 1,
          d+h out-of-range days excluded (usable-count anchors
          frozen). fwd values enter ALL gate arithmetic in PERCENT
          units (pp): unit convention frozen at delivery -- the
          template sec.4 IC-family floor token 0.02 applies on the
          face's own display unit (prereg s5 predictions are quoted
          in the same percent display, COLD h20 +0.737% = 0.737pp;
          a raw-fraction reading, floor = 2%, contradicts the frozen
          s5 [0.4,0.7] V1^V2 pass-probability prediction). Dual-unit
          columns (raw + pp) are disclosed in every cell so the
          judgment is fully re-derivable either way.
  cells   4 cells = {HOT, COLD} x {h20 primary, h5 secondary zero
          family weight} (prereg s0/s4: h20 = main caliber, h5 =
          anti-window-picking disclosure, no family verdict). Cell
          value = mean fwd_h over the tail's state days with valid
          fwd (usable counts frozen: h20 hot 152 / cold 145, h5 hot
          153 / cold 145). N_eff = BATCH_CELLS 2004 = 4 judged
          cells + 2000 null draws (s0 counting law, W9 same).
  nulls   K=2000 occupancy-matched unconditional draws per cell
          (prereg s3): universe = decidable days with valid fwd_h
          (availability matched), draw size = the cell's usable
          count (occupancy matched), rng = np.random.default_rng(
          [SEED, k]) k < 2000 -- one k-stream shared across cells
          (W5/W9 seed law; s3's "seed=SEED_REGISTRY[..]+k" is
          implemented as the family's list-seed substream convention
          exactly as W9's identical text). No npy shards: the whole
          null leg is seconds-scale single-process.
  gates   V1 direction-magnitude (single-sided, preregistered
          direction): HOT spread <= -max(0.02pp, p95|null spread|),
          COLD spread >= +max(0.02pp, p95|null spread|), spread =
          cell mean - mu_null. V2 null-extreme: HOT cell < p5(null
          means), COLD cell > p95(null means). V3 OOS retention:
          fixed calendar split 2023-07-01, both halves' spread vs
          pooled null mu same sign as the full-window spread (empty
          half = honest fail, no retention evidence). Family rule:
          a tail passes = V1^V2^V3 on the h20 cell; any tail passes
          = batch judged-positive (that tail -> T-34 fastline
          candidate pool eligibility, routing-input face, harness
          A/B adoption; REGIME_GUARD T0 brake authority untouched);
          both tails fail = judged-negative family closure + reopen
          note (RANDOM_LARGE_SAMPLE_LAW s5, W1-W9 ten-straight
          negative family, judged-negative = predicted mainline =
          lawful output). 100 random half-splits (k in [3000,3100))
          same-sign-as-each-other rate >= 80% = STABLE flag,
          disclosure not a gate (W9 split face). Starts band k in
          [2000,3000) RESERVED UNUSED per prereg s3 (IC face has no
          path-dependent virtual starts; band position preserved,
          zero collision). No G1'/G2/DSR/PBO in this batch: the IC
          routing-input face judges via V1/V2/V3 per frozen s4 (no
          return-series cells to register; T-34 intake walks the
          harness separately).
  d6      frozen at the r265 freeze-window artifact verbatim (W6/
          W7/W9 paradigm: the admission record = the freeze-window
          facts, no re-computation): batch-internal HOT vs COLD
          -0.1095 structural complement (disjoint tails of one state
          gate, both burn independently); h20/h5 signal face 1.0 by
          construction (cell axis = evaluation horizon); in-register
          five faces max 0.3683; vs T33 four cells max 0.3358; vs
          registered six max 0.3079; merge clause ZERO triggers
          (< 0.7).
  ledger  science_gates.append_ledger("PREMIUM_SENT_P1", 2004,
          file_name="results/innovation_quota/PREMIUM-SENT-P1.json",
          evidence_cutoff="2026-09-29"); return value embedded in
          the product (r217/r434 law); attrition measurement row to
          the EXECUTING machine's lane file (gate_attrition.<id>
          .json, W6 law). prereg_sha256 recorded in the product at
          burn time per the r265 freeze record (delivery-round law).
Products (prereg s6): results/innovation_quota/PREMIUM-SENT-P1.json
(top evidence_cutoff + cutoff_meta + G-ANCHOR faces + degeneracy
identity + 4 cells dual-unit + per-cell null family (mu/sigma/p5/
p95/p95|spread| + values) + V1/V2/V3 verdicts + 100-split STABLE +
V3 calendar halves + frozen d6 + episode trading-face viability
disclosure + year-histogram extreme-segment faces + incremental
segment + funnel + trials_ledger).

Usage: run | verify | selftest   (exit 0 ok; 2 = fail-closed gate
refusal, including the r450 landed-state guard: a judged product
(trials_ledger present, read from CONTENT not existence/timestamps)
refuses re-run unless INNOVATION_QUOTA_W10_REFINALIZE=1). 'verify'
= real-panel G-ANCHOR reconcile only (read-only, no engine, no
product, no ledger -- build-time pre-verification face, the burn
stays with the pool claim). Zero network, zero engine touch, marks
+0, SEED +0.
"""
import argparse
import csv
import hashlib
import json
import math
import os
import shutil
import sys
import tempfile
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "results"))

import science_gates as SG                   # shared gate library (O-2250)

# frozen construction single source (r456 verbatim-import paradigm)
from _r264bmc_w10_berth_probe import (        # berth probe, in-tree
    pct_rank_state, load_csv_series, episodes_confirm2)

OUT_DIR = os.path.join(ROOT, "results", "innovation_quota")
OUT_JSON = os.path.join(OUT_DIR, "PREMIUM-SENT-P1.json")
OUT_DIR_RESULTS = os.path.dirname(OUT_DIR)    # results root for lib faces
MACHINE_JSON = os.path.join(ROOT, "fleet", "machine.json")
ATT_JSON_SHARED = os.path.join(ROOT, "results", "gate_attrition.json")
D6_FACTS_PATH = os.path.join(
    ROOT, "results", "_r265bmc_w10_freeze_probe_facts.json")
PREREG_PATH = os.path.join(
    ROOT, "research", "INNOVATION_QUOTA_W10_PREREG.md")

BATCH_NAME = "PREMIUM_SENT_P1"
BATCH_CELLS = 2004                # 4 judged cells + 2000 null draws (s0 law)
EVIDENCE_CUTOFF = "2026-09-29"
PANEL_FROZEN_LAST = "2026-09-24"   # berth/freeze window face (NAV lag)
SEED_KEY = "innovation_quota_w10_premium"
K_NULLS = 2000
K_SPLITS = 100
SPLIT_DATE_FROZEN = "2023-07-01"      # author-verbatim literal (frozen)
SPLIT_DATE = SPLIT_DATE_FROZEN        # working var (selftest reassigns)
HORIZONS = (20, 5)                 # h20 primary / h5 secondary zero weight
TAILS = ("hot", "cold")
CELL_NAME = {("hot", 20): "HOT-H20", ("cold", 20): "COLD-H20",
             ("hot", 5): "HOT-H5", ("cold", 5): "COLD-H5"}
DIRECTION = {"hot": -1, "cold": +1}   # preregistered single-sided direction
V1_FLOOR_PP = 0.02                 # IC-family floor token, percent units
STABLE_RATE = 0.80
DEGEN_TOL = 1e-12
D6_REJECT = 0.7
SEED = None                        # filled from SG.SEED_REGISTRY at run

PANEL_PATH = os.path.join(ROOT, "data", "fund_premium", "panel",
                          "panel.csv")
PRICE_PATH = os.path.join(ROOT, "data", "daily", "510300.csv")

# ---- frozen probe faces (berth r264 + freeze r265 facts verbatim;
# one-face-off = config mismatch VOID per prereg s2 G-ANCHOR-FACE law)
PANEL_ANCHOR = {"n_dates_panel": 1633, "first_date": "2020-01-02",
                "last_date": "2026-09-24", "n_members_first": 37,
                "n_members_last": 48, "cross_mean_min": -0.0741,
                "cross_mean_max": 0.0911, "cross_mean_mean": 0.0023,
                "days_below_par": 675}
STATE_ANCHOR = {"n_state_days": 1514, "first_decidable_date": "2020-07-03",
                "n_hot": 153, "n_cold": 146}
FWD_ANCHOR = {
    "h20": {"hot_mean": 0.00064, "n_hot": 152, "cold_mean": 0.00737,
            "n_cold": 145, "mid_mean": -9e-05, "n_mid": 1199,
            "hot_minus_cold_pp": -0.673},
    "h5": {"hot_mean": 0.0, "n_hot": 153, "cold_mean": 0.00505,
           "n_cold": 145, "mid_mean": -0.00038, "n_mid": 1213,
           "hot_minus_cold_pp": -0.505}}
EPISODES_ANCHOR = {
    "V1_HOT_DEF_2d": {"n_exits_to_cash": 17, "n_reentries": 17,
                      "days_long": 1468, "days_cash": 46,
                      "cash_occupancy": 0.0304, "est_turnover_per_yr": 2.83,
                      "first_flips": ["2020-10-12", "2020-10-14",
                                      "2021-08-24", "2021-08-26",
                                      "2022-03-17", "2022-03-21",
                                      "2022-11-02", "2022-11-08"]},
    "V2_COLD_GATE_2d": {"n_entries": 16, "n_exits": 16, "days_long": 38,
                        "days_cash": 1476, "long_occupancy": 0.0251,
                        "est_turnover_per_yr": 2.66,
                        "first_flips": ["2020-07-16", "2020-07-20",
                                        "2021-03-09", "2021-03-11",
                                        "2021-07-27", "2021-07-29",
                                        "2022-03-08", "2022-03-10"]},
    "window_years": 6.01}
TH_ANCHOR = {"state_window": 252, "state_q_hi": 0.9, "state_q_lo": 0.1,
             "state_min_periods": 120,
             "fwd_horizons_primary_secondary": [20, 5],
             "v3_calendar_split": "2023-07-01", "nulls_K": 2000,
             "batch_cells_N_eff": 2004, "seed_registered": 20326500,
             "v1_floor_pp": 0.02, "stable_rate": 0.8}

_PANEL_OVERRIDE = None             # selftest synthetic-panel injection hook
_PRICE_OVERRIDE = None             # selftest synthetic-price injection hook
_D6_FACTS_OVERRIDE = None          # selftest frozen-d6 stub hook
_ATT_OVERRIDE = None               # selftest attrition-path override


def gate_refuse(msg):
    print(f"GATE-REFUSE(exit2): {msg}")
    return 2


# ---------------------------------------------------------------- faces
def load_panel_rows(path):
    """Berth-probe verbatim panel semantics: mem[date] -> list of
    (premium_adj, premium_z); ValueError rows skipped, premium_adj
    None skipped, premium_z may be None (excluded from z-mean only)."""
    mem = {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                pz = float(r["premium_z"]) if r["premium_z"] not in (
                    "", None) else None
                pa = float(r["premium_adj"]) if r["premium_adj"] not in (
                    "", None) else None
            except ValueError:
                continue
            if pa is None:
                continue
            mem.setdefault(r["date"], []).append((pa, pz))
    return mem


def derive_faces(mem, price_rows):
    """G-PANEL + G-ANCHOR derivation (cross-mean state + degeneracy
    identity + fwd conditional faces + 2d-confirm episodes + segment
    histograms). All comparisons rounded exactly like the frozen probe
    facts (4dp cross-mean stats, 5dp fwd means, 3dp pp spreads)."""
    pd_dates = sorted(mem)
    # ---- degeneracy identity (berth-probe verbatim)
    max_abs_zmean = 0.0
    for d in pd_dates:
        pzs = [x[1] for x in mem[d] if x[1] is not None]
        if pzs:
            max_abs_zmean = max(max_abs_zmean, abs(sum(pzs) / len(pzs)))
    # ---- corrected face: cross-mean premium_adj state
    cross = {d: sum(x[0] for x in mem[d]) / len(mem[d]) for d in pd_dates}
    cmd = sorted(cross)
    cmv = [cross[d] for d in cmd]
    cstate = pct_rank_state(cmd, cmv)
    hot_ind = {d: (1 if v[0] else 0) for d, v in cstate.items()}
    cold_ind = {d: (1 if v[1] else 0) for d, v in cstate.items()}
    panel_face = {
        "n_dates_panel": len(pd_dates), "first_date": pd_dates[0],
        "last_date": pd_dates[-1],
        "n_members_first": len(mem[pd_dates[0]]),
        "n_members_last": len(mem[pd_dates[-1]]),
        "cross_mean_min": round(min(cmv), 4),
        "cross_mean_max": round(max(cmv), 4),
        "cross_mean_mean": round(sum(cmv) / len(cmv), 4),
        "days_below_par": sum(1 for v in cmv if v < 0),
    }
    state_face = {
        "n_state_days": len(cstate),
        "first_decidable_date": min(cstate.keys()) if cstate else None,
        "n_hot": sum(hot_ind.values()), "n_cold": sum(cold_ind.values()),
    }
    # ---- price face + fwd (berth-probe closure semantics)
    pxd = sorted(price_rows)
    pxv = [price_rows[x] for x in pxd]
    pxi = {d: i for i, d in enumerate(pxd)}

    def fwd(d, h):
        i = pxi.get(d)
        if i is None or i + h >= len(pxd):
            return None
        return pxv[i + h] / pxv[i] - 1.0

    fwd_face = {}
    usable = {}
    for h in HORIZONS:
        hot_f = [fwd(d, h) for d in sorted(cstate) if hot_ind[d]]
        cold_f = [fwd(d, h) for d in sorted(cstate) if cold_ind[d]]
        mid_f = [fwd(d, h) for d in sorted(cstate)
                 if not hot_ind[d] and not cold_ind[d]]
        hot_f = [x for x in hot_f if x is not None]
        cold_f = [x for x in cold_f if x is not None]
        mid_f = [x for x in mid_f if x is not None]

        def _mean(xs):
            return round(sum(xs) / len(xs), 5) if xs else None

        fwd_face["h%d" % h] = {
            "hot_mean": _mean(hot_f), "n_hot": len(hot_f),
            "cold_mean": _mean(cold_f), "n_cold": len(cold_f),
            "mid_mean": _mean(mid_f), "n_mid": len(mid_f),
            "hot_minus_cold_pp": (round(
                (sum(hot_f) / len(hot_f) - sum(cold_f) / len(cold_f))
                * 100, 3) if hot_f and cold_f else None),
        }
        for tail, ind in (("hot", hot_ind), ("cold", cold_ind)):
            vals = [(d, fwd(d, h)) for d in sorted(cstate) if ind[d]]
            usable[(tail, h)] = [(d, v) for (d, v) in vals
                                 if v is not None]
    # ---- confirmed-state episodes (berth-probe verbatim machine)
    cdates = sorted(cstate)
    hot_raw = {d: bool(hot_ind[d]) for d in cdates}
    cold_raw = {d: bool(cold_ind[d]) for d in cdates}
    v1_off, v1_on, v1_days_on, v1_days_off, v1_flips = \
        episodes_confirm2(cdates, hot_raw, start_on=True)
    v2_off, v2_on, v2_days_on, v2_days_off, v2_flips = \
        episodes_confirm2(cdates, {d: not cold_raw[d] for d in cdates},
                          start_on=False)
    years = len(cdates) / 252.0
    episodes_face = {
        "V1_HOT_DEF_2d": {
            "n_exits_to_cash": v1_off, "n_reentries": v1_on,
            "days_long": v1_days_on, "days_cash": v1_days_off,
            "cash_occupancy": round(v1_days_off / max(1, len(cdates)), 4),
            "est_turnover_per_yr": round(v1_off / years, 2),
            "first_flips": v1_flips},
        "V2_COLD_GATE_2d": {
            "n_entries": v2_on, "n_exits": v2_off,
            "days_long": v2_days_on, "days_cash": v2_days_off,
            "long_occupancy": round(v2_days_on / max(1, len(cdates)), 4),
            "est_turnover_per_yr": round(v2_on / years, 2),
            "first_flips": v2_flips},
        "window_years": round(years, 2)}
    # ---- extreme-segment faces (prereg s5.5 (c) clause: hot-side
    # 2024 cross-border hype segment sensitivity; year histogram +
    # max consecutive-run share per tail, harvest disclosure face)
    seg = {}
    for tail, ind in (("hot", hot_ind), ("cold", cold_ind)):
        days = [d for d in cdates if ind[d]]
        hist = {}
        for d in days:
            hist[d[:4]] = hist.get(d[:4], 0) + 1
        max_run = run = 0
        prev = None
        for d in days:
            run = run + 1 if (prev is not None and _next_bd(prev) == d) \
                else 1
            max_run = max(max_run, run)
            prev = d
        seg[tail] = {"n_days": len(days),
                     "year_histogram": dict(sorted(hist.items())),
                     "max_consecutive_run": max_run,
                     "max_run_share": round(
                         max_run / max(1, len(days)), 4)}
    return {"panel": panel_face, "state": state_face, "fwd": fwd_face,
            "episodes": episodes_face, "degeneracy": max_abs_zmean,
            "usable": usable, "segments": seg}


def _next_bd(d):
    """Next calendar day string (approx consecutive-run face; trading
    gaps break runs conservatively -- honest lower bound on runs)."""
    import datetime
    t = datetime.date(int(d[:4]), int(d[5:7]), int(d[8:10]))
    return (t + datetime.timedelta(days=1)).isoformat()


def threshold_face():
    """Author-verbatim constants, zero calibration: code defaults
    asserted via inspect.signature on the single-source pct_rank_state
    (freeze step-4 law) + module literals + registry seed."""
    import inspect
    sig = inspect.signature(pct_rank_state)
    d = {k: v.default for k, v in sig.parameters.items()
         if v.default is not inspect.Parameter.empty}
    return {"state_window": d.get("window"), "state_q_hi": d.get("q_hi"),
            "state_q_lo": d.get("q_lo"),
            "state_min_periods": d.get("min_periods"),
            "fwd_horizons_primary_secondary": list(HORIZONS),
            "v3_calendar_split": SPLIT_DATE, "nulls_K": K_NULLS,
            "batch_cells_N_eff": BATCH_CELLS,
            "seed_registered": SG.SEED_REGISTRY.get(SEED_KEY),
            "v1_floor_pp": V1_FLOOR_PP, "stable_rate": STABLE_RATE}


def anchor_drift(P):
    """Fail-closed reconcile vs the frozen probe facts (one-face-off =
    config mismatch VOID, not data corruption)."""
    bad = []

    def _cmp(family, got, exp):
        for k, v in exp.items():
            g = got.get(k)
            if g != v:
                bad.append(f"{family}.{k}: {g!r} != frozen {v!r}")

    _cmp("panel", P["panel"], PANEL_ANCHOR)
    _cmp("state", P["state"], STATE_ANCHOR)
    for h in HORIZONS:
        _cmp(f"fwd.h{h}", P["fwd"]["h%d" % h], FWD_ANCHOR["h%d" % h])
    _cmp("episodes.V1", P["episodes"]["V1_HOT_DEF_2d"],
         EPISODES_ANCHOR["V1_HOT_DEF_2d"])
    _cmp("episodes.V2", P["episodes"]["V2_COLD_GATE_2d"],
         EPISODES_ANCHOR["V2_COLD_GATE_2d"])
    _cmp("episodes", P["episodes"],
         {"window_years": EPISODES_ANCHOR["window_years"]})
    _cmp("thresholds", threshold_face(), TH_ANCHOR)
    if not (P["degeneracy"] < DEGEN_TOL):
        bad.append(f"degeneracy_identity: {P['degeneracy']!r} >= "
                   f"{DEGEN_TOL} (cross-mean premium_z must be "
                   f"identically 0 up to float roundoff)")
    return bad


# ------------------------------------------------------------- cell legs
def null_family(universe_vals_pp, n_draw, k_nulls):
    """K occupancy-matched unconditional draws for one cell: universe
    = decidable days with valid fwd (availability matched), draw size
    = the cell's usable count (occupancy matched), one shared k-stream
    rng([SEED, k]) per the W5/W9 seed law."""
    U = np.asarray(universe_vals_pp, dtype=float)
    vals = np.empty(k_nulls, dtype=float)
    for k in range(k_nulls):
        rng = np.random.default_rng([SEED, k])
        idx = rng.choice(len(U), size=n_draw, replace=False)
        vals[k] = float(U[idx].mean())
    v = vals
    mu = float(v.mean())
    return {
        "values": [round(float(x), 6) for x in v],
        "coverage": {"mu": round(mu, 6),
                     "sigma": round(float(v.std(ddof=1)), 6),
                     "p5": round(float(np.percentile(v, 5)), 6),
                     "p95": round(float(np.percentile(v, 95)), 6),
                     "p95_abs_spread": round(float(np.percentile(
                         np.abs(v - mu), 95)), 6),
                     "n_values": int(len(v))},
    }


def v1_pass(tail, cell_mean_pp, mu_null, p95_abs_spread):
    """V1 direction-magnitude, preregistered single side: HOT needs
    spread <= -max(floor, p95|null spread|); COLD needs >= +."""
    thr = max(V1_FLOOR_PP, p95_abs_spread)
    spread = cell_mean_pp - mu_null
    if DIRECTION[tail] < 0:
        return bool(spread <= -thr), round(spread, 6), round(thr, 6)
    return bool(spread >= thr), round(spread, 6), round(thr, 6)


def v2_pass(tail, cell_mean_pp, p5_null, p95_null):
    """V2 null-extreme, single side: HOT cell < p5(null means);
    COLD cell > p95(null means)."""
    if DIRECTION[tail] < 0:
        return bool(cell_mean_pp < p5_null)
    return bool(cell_mean_pp > p95_null)


def v3_halves(tail, usable, mu_null):
    """V3 OOS retention, fixed calendar split: both halves' spread vs
    pooled null mu same sign as the full-window spread; an empty half
    = honest fail (no retention evidence)."""
    h1 = [(d, v) for (d, v) in usable if d < SPLIT_DATE]
    h2 = [(d, v) for (d, v) in usable if d >= SPLIT_DATE]
    full = (sum(v for (_d, v) in usable) / len(usable)) if usable else None
    if full is None:
        return {"pass": False, "reason": "empty cell",
                "half1_mean": None, "half2_mean": None,
                "half1_spread": None, "half2_spread": None,
                "full_spread": None}
    s_full = full - mu_null
    out = {"full_spread": round(s_full, 6),
           "half1_n": len(h1), "half2_n": len(h2)}
    if not h1 or not h2:
        out["pass"] = False
        out["reason"] = "empty half (%s)" % (
            "half1" if not h1 else "half2")
        out["half1_mean"] = (round(sum(v for (_d, v) in h1) / len(h1), 6)
                             if h1 else None)
        out["half2_mean"] = (round(sum(v for (_d, v) in h2) / len(h2), 6)
                             if h2 else None)
        out["half1_spread"] = (out["half1_mean"] - mu_null
                               if h1 else None)
        out["half2_spread"] = (out["half2_mean"] - mu_null
                               if h2 else None)
        return out
    m1 = sum(v for (_d, v) in h1) / len(h1)
    m2 = sum(v for (_d, v) in h2) / len(h2)
    s1, s2 = m1 - mu_null, m2 - mu_null
    sf = (1.0 if s_full > 0 else -1.0) if s_full != 0 else 0.0
    out["half1_mean"] = round(m1, 6)
    out["half2_mean"] = round(m2, 6)
    out["half1_spread"] = round(s1, 6)
    out["half2_spread"] = round(s2, 6)
    out["pass"] = bool(sf != 0 and (s1 > 0) == (sf > 0)
                       and (s2 > 0) == (sf > 0))
    return out


def stable_splits(usable_vals_pp, mu_null, k_splits):
    """100 random half-splits (k in [3000,3100)): same-sign-as-each-
    other rate >= 80% = STABLE flag (disclosure, not a gate; W9 split
    face)."""
    vals = np.asarray(usable_vals_pp, dtype=float)
    n = len(vals)
    agree = 0
    for j in range(k_splits):
        rng = np.random.default_rng([SEED, 3000 + j])
        perm = rng.permutation(n)
        half = n // 2
        a = float(vals[perm[:half]].mean()) - mu_null
        b = float(vals[perm[half:]].mean()) - mu_null
        agree += int((a > 0) == (b > 0))
    rate = agree / k_splits
    return {"same_sign_rate": round(rate, 4),
            "segment_stable": bool(rate >= STABLE_RATE),
            "n_splits": k_splits}


# ------------------------------------------------------------------ d6
def frozen_d6_block():
    """Verbatim copy of the freeze-window D6 record (W6/W7/W9
    paradigm: the admission record = the freeze-window artifact, no
    re-computation)."""
    path = _D6_FACTS_OVERRIDE or D6_FACTS_PATH
    with open(path, encoding="utf-8") as fh:
        facts = json.load(fh)
    d6 = dict(facts["d6_cells_face"])
    d6["freeze_artifact"] = ("results/_r265bmc_w10_freeze_probe_facts"
                             ".json (frozen r265 bm-c, no "
                             "re-computation, W6 admission-record "
                             "paradigm)")
    d6["reject_line"] = D6_REJECT
    return d6


# --------------------------------------------------------------- attrition
def _att_json_path():
    """prereg s6: the EXECUTING machine's lane file (gate_attrition
    .<id>.json); shared-file fallback when machine.json unreadable."""
    try:
        with open(MACHINE_JSON, encoding="utf-8") as fh:
            mid = json.load(fh).get("machine_id")
        if mid:
            return os.path.join(ROOT, "results",
                                f"gate_attrition.{mid}.json")
    except Exception:
        pass
    return ATT_JSON_SHARED


def _attr_row(batch, delta, total, gates, entries):
    path = _ATT_OVERRIDE or _att_json_path()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
    else:
        d = {"entries": []}
    row = {"batch": batch, "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
           "kind": "measurement", "cells_ledger_delta": delta,
           "ledger_total_after": total, "gates": gates,
           "entries": entries}
    own = [i for i, e in enumerate(d["entries"])
           if e.get("batch") == batch and e.get("kind") == "measurement"]
    if own:
        d["entries"][own[-1]] = row
    else:
        d["entries"].append(row)
    with open(path + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
    os.replace(path + ".tmp", path)


# ------------------------------------------------------------------ product
def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 16), b""):
            h.update(blk)
    return h.hexdigest()


def write_product(product):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_JSON + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(product, fh, ensure_ascii=False, indent=1)
    os.replace(OUT_JSON + ".tmp", OUT_JSON)
    return product


def _refuse_if_judged():
    """r450 landed-state guard: read CONTENT (trials_ledger block), not
    existence/timestamps. Judged product refuses re-run (rc=2) unless
    INNOVATION_QUOTA_W10_REFINALIZE=1; unreadable/partial = resume."""
    if not os.path.exists(OUT_JSON):
        return 0
    try:
        with open(OUT_JSON, encoding="utf-8") as fh:
            old = json.load(fh)
    except Exception:
        return 0
    if (old.get("trials_ledger") or {}).get("total") is not None and \
            os.environ.get("INNOVATION_QUOTA_W10_REFINALIZE") != "1":
        print("GATE-REFUSE(exit2): PREMIUM-SENT-P1.json already "
              "judged (trials_ledger present, content-read per r450); "
              "INNOVATION_QUOTA_W10_REFINALIZE=1 = only redo")
        return 2
    return 0


# ------------------------------------------------------------------ legs
def _load_data():
    """Panel (frozen face + incremental disclosure + lockbox) and
    price (cutoff lockbox) loads."""
    mem_raw = load_panel_rows(_PANEL_OVERRIDE or PANEL_PATH)
    frozen_dates = sorted(d for d in mem_raw if d <= PANEL_FROZEN_LAST)
    incremental = [d for d in sorted(mem_raw)
                   if PANEL_FROZEN_LAST < d <= EVIDENCE_CUTOFF]
    dropped = [d for d in sorted(mem_raw) if d > EVIDENCE_CUTOFF]
    mem = {d: mem_raw[d] for d in frozen_dates}
    price_raw = load_csv_series(_PRICE_OVERRIDE or PRICE_PATH,
                                "date", "close")
    price_rows = {d: v for d, v in price_raw.items()
                  if d <= EVIDENCE_CUTOFF}
    seg = {"n_incremental_rows_in_cutoff_window": len(incremental),
           "incremental_dates_head": incremental[:5],
           "n_rows_beyond_cutoff_dropped_lockbox": len(dropped),
           "law": ("panel face frozen at berth/freeze window (last "
                   f"{PANEL_FROZEN_LAST}, NAV disclosure lag "
                   "structural); rows in (frozen_last, evidence_"
                   "cutoff] disclosed here and NOT loaded (G-ANCHOR "
                   "battery pins the frozen face, W9 panel-forward-"
                   "advance precedent); rows beyond the cutoff "
                   "dropped by the P-5C forward lockbox")}
    return mem, price_rows, seg


def _build_cells(P):
    """4 cells + null families + V1/V2/V3 + STABLE splits."""
    cells = {}
    for tail in TAILS:
        for h in HORIZONS:
            usable = P["usable"][(tail, h)]
            raw_vals = [v for (_d, v) in usable]
            pp_vals = [v * 100.0 for v in raw_vals]
            cell_raw = sum(raw_vals) / len(raw_vals)
            cell_pp = sum(pp_vals) / len(pp_vals)
            # null universe = ALL decidable days with valid fwd_h
            # (occupancy-matched unconditional draw, availability
            # matched by construction: same usable-count draw size)
            universe = P["universe"][h]
            nulls = null_family(universe, len(usable), K_NULLS)
            cov = nulls["coverage"]
            v1, spread, thr = v1_pass(tail, cell_pp, cov["mu"],
                                      cov["p95_abs_spread"])
            v2 = v2_pass(tail, cell_pp, cov["p5"], cov["p95"])
            v3 = v3_halves(tail, usable, cov["mu"])
            stab = stable_splits(pp_vals, cov["mu"], K_SPLITS)
            cells[(tail, h)] = {
                "cell_name": CELL_NAME[(tail, h)], "tail": tail,
                "horizon": h, "role": ("primary" if h == 20
                                       else "secondary-zero-weight"),
                "direction": DIRECTION[tail],
                "n_state_days": (P["state"]["n_hot"] if tail == "hot"
                                 else P["state"]["n_cold"]),
                "n_usable": len(usable),
                "cell_mean_raw": round(cell_raw, 8),
                "cell_mean_pp": round(cell_pp, 6),
                "nulls": nulls,
                "gates": {"V1_direction_magnitude": {
                              "pass": v1, "spread_pp": spread,
                              "threshold_pp": thr,
                              "inputs": {"mu_null_pp": cov["mu"],
                                         "p95_abs_spread_pp":
                                             cov["p95_abs_spread"],
                                         "floor_pp": V1_FLOOR_PP}},
                          "V2_null_extreme": {
                              "pass": v2,
                              "inputs": {"p5_null_pp": cov["p5"],
                                         "p95_null_pp": cov["p95"]}},
                          "V3_oos_retention": v3},
                "splits_stable": stab,
            }
    return cells


def cmd_run():
    global SEED
    if SEED_KEY not in SG.SEED_REGISTRY:
        return gate_refuse(f"SEED_REGISTRY key {SEED_KEY} missing "
                           f"(freeze-window registration absent)")
    SEED = SG.SEED_REGISTRY[SEED_KEY]
    t0 = time.time()
    mem, price_rows, seg = _load_data()
    P = derive_faces(mem, price_rows)
    # null universe per horizon: all decidable days with valid fwd
    P["universe"] = _universe_from_faces(P, mem, price_rows)
    bad = anchor_drift(P)
    if bad:
        for b in bad[:12]:
            print(f"  drift: {b}")
        return gate_refuse(f"G-ANCHOR drift {len(bad)} face(s) vs "
                          f"frozen probe facts -- config mismatch "
                          f"VOID (one-face-off law)")
    print(f"G-ANCHOR reconcile: bit-exact ({time.time() - t0:.0f}s)",
          flush=True)
    cells = _build_cells(P)
    for key in cells:
        c = cells[key]
        print(f"  cell {c['cell_name']}: mean={c['cell_mean_pp']}pp "
              f"n={c['n_usable']} V1={c['gates']['V1_direction_magnitude']['pass']} "
              f"V2={c['gates']['V2_null_extreme']['pass']} "
              f"V3={c['gates']['V3_oos_retention']['pass']} "
              f"({time.time() - t0:.0f}s)", flush=True)
    # ---- family verdict (h20 primary, per-tail independent)
    verdicts = {}
    for tail in TAILS:
        c = cells[(tail, 20)]
        v = c["gates"]
        verdicts[tail] = {
            "tail": tail, "primary_cell": c["cell_name"],
            "V1": v["V1_direction_magnitude"]["pass"],
            "V2": v["V2_null_extreme"]["pass"],
            "V3": v["V3_oos_retention"]["pass"],
            "tail_pass": bool(v["V1_direction_magnitude"]["pass"]
                              and v["V2_null_extreme"]["pass"]
                              and v["V3_oos_retention"]["pass"])}
    passing_tails = [t for t in TAILS if verdicts[t]["tail_pass"]]
    judged_positive = bool(passing_tails)
    d6 = frozen_d6_block()
    prev_total = None
    if os.path.exists(OUT_JSON):
        try:
            with open(OUT_JSON, encoding="utf-8") as fh:
                old = json.load(fh)
            prev_total = (old.get("trials_ledger")
                          or {}).get("prev_total")
        except Exception:
            prev_total = None
    ledger = SG.append_ledger(
        BATCH_NAME, BATCH_CELLS,
        file_name="results/innovation_quota/PREMIUM-SENT-P1.json",
        evidence_cutoff=EVIDENCE_CUTOFF, prev_total=prev_total)
    product = {
        "batch": BATCH_NAME,
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "cutoff_meta": SG.cutoff_meta(EVIDENCE_CUTOFF),
        "prereg": "research/INNOVATION_QUOTA_W10_PREREG.md (berth r264 "
                  "bm-c + freeze r265 bm-c, drafting-machine self-freeze "
                  "per W5/W6/W7/W9 mirror)",
        "prereg_sha256_16": _sha256_file(PREREG_PATH)[:16],
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "seed": {"base": SEED, "k_nulls": K_NULLS, "k_splits": K_SPLITS,
                 "k_substreams": ("nulls k<2000; splits k in "
                                  "[3000,3100); starts band k in "
                                  "[2000,3000) RESERVED UNUSED (IC "
                                  "face, no path-dependent starts); "
                                  "rng([SEED, k]) one k-stream shared "
                                  "across cells (W5/W9 law)")},
        "unit_convention": {
            "fwd_unit": "percent (pp); cell means/spreads/null stats "
                        "all in pp",
            "v1_floor": f"{V1_FLOOR_PP} pp (= 2bp on the h-day forward "
                        "return); template sec.4 IC-family floor token "
                        "0.02 applied on the face's own display unit",
            "coherence_note": ("prereg s5 predictions are quoted in "
                               "the same percent display (COLD h20 "
                               "+0.737% = 0.737pp); a raw-fraction "
                               "reading (floor = 2%) contradicts the "
                               "frozen s5 [0.4,0.7] V1^V2 pass-"
                               "probability prediction; dual-unit "
                               "columns disclosed per cell so the "
                               "judgment is re-derivable either way"),
        },
        "panel": P["panel"], "state_face": P["state"],
        "fwd_conditional_means": P["fwd"],
        "degeneracy_identity": {
            "max_abs_cross_mean_premium_z": P["degeneracy"],
            "identity_holds": bool(P["degeneracy"] < DEGEN_TOL),
            "note": "construction-erratum mechanical self-proof "
                    "(per-date cross-sectional z ddof=0 -> cross-mean "
                    "identically 0); berth r264 + freeze r265 repro"},
        "confirmed_state_episodes_2d": P["episodes"],
        "trading_face_viability_note": (
            "exposure-gate form structurally killed by F6 (2d-confirm "
            "episodes 17/16 < 30, berth probe facts); episode readings "
            "carried as consumer-face viability disclosure, NOT a "
            "judgment face; cost/turnover clauses inapplicable to the "
            "IC routing-input face per prereg s3 honest note"),
        "incremental_segment": seg,
        "extreme_segment_faces": P["segments"],
        "threshold_constants": threshold_face(),
        "construction": "verbatim-import results/_r264bmc_w10_berth_"
                        "probe.py (pct_rank_state + load_csv_series + "
                        "episodes_confirm2 + panel/fwd semantics "
                        "mirrored; parity-anchored every run vs the "
                        "frozen berth/freeze facts) -- r456 "
                        "single-source zero-drift paradigm",
        "cells": {cells[k]["cell_name"]: cells[k]
                  for k in cells},
        "family_verdict": {
            "primary_caliber": "h20 (prereg s4); h5 cells disclosed "
                               "per-cell with the same gates, zero "
                               "family weight (anti-window-picking)",
            "tails": verdicts,
            "judged_positive": judged_positive,
            "passing_tails": passing_tails,
            "judged_negative_note": (
                "both tails fail = judged-negative family closure + "
                "reopen note (RANDOM_LARGE_SAMPLE_LAW s5; W1-W9 ten-"
                "straight negative family, negative verdict = "
                "predicted mainline = lawful output saving future "
                "premium-sentiment-family burns)") if not
            judged_positive else None,
            "positive_note": (
                "passing tail -> T-34 fastline candidate pool "
                "eligibility (routing-input face, zoo #97 consumption "
                "line; harness A/B adoption face; REGIME_GUARD T0 "
                "brake authority untouched)") if judged_positive
            else None},
        "d6": d6,
        "virtual_starts": {"used": False,
                           "law": "IC face has no path-dependent "
                                  "virtual starts; k-band [2000,3000) "
                                  "reserved unused per prereg s3 "
                                  "(band position preserved, zero "
                                  "collision with splits)"},
        "negative_prior_burden": [
            "innovation-quota line W1-W9 nine-straight judged "
            "negative (null-judgment dominant family law)",
            "#84/#87 sentiment/crowding neighborhood 10-burn burden "
            "(corrected-face signal corr max 0.3683 disclosed)",
            "descriptive evidence = single berth reading (overlapping "
            "windows inflate, no cost, no null calibration until this "
            "burn); hot tail flat / cold tail only",
            "thin history 6.7y (2020-01-02 NAV backfill boundary; "
            "three-window grid ~6-7 segments)",
            "2024 cross-border ETF hype segment = hot-side segment "
            "sensitivity must-check (extreme_segment_faces)"],
        "funnel": {
            "harvest_column": 1,
            "gate_column": "; ".join(
                f"{t}: {'PASS' if verdicts[t]['tail_pass'] else 'FAIL'}"
                f" (V1={verdicts[t]['V1']}/V2={verdicts[t]['V2']}/"
                f"V3={verdicts[t]['V3']})" for t in TAILS)},
        "judgment_note": (
            "judged per frozen prereg s4 via V1/V2/V3 on the h20 "
            "primary cells (IC routing-input face: no G1'/G2/DSR/PBO "
            "-- no return-series cells to register; T-34 intake walks "
            "the CE admission harness separately); null family = "
            "batch-own occupancy-matched unconditional draws per "
            "s3 (availability-matched universe, occupancy-matched "
            "draw size, one shared k-stream); BATCH_CELLS=2004 = "
            "4 judged cells + 2000 null draws (s0 counting law, W9 "
            "same); h5 secondary zero family weight"),
    }
    product["trials_ledger"] = ledger          # r434 law: value carried
    write_product(product)
    _attr_row(BATCH_NAME, BATCH_CELLS, int(ledger["total"]),
              {"family_verdict": {t: verdicts[t]["tail_pass"]
                                 for t in TAILS},
               "v_gates": {cells[k]["cell_name"]:
                           {g: cells[k]["gates"][g]["pass"]
                            if isinstance(cells[k]["gates"][g], dict)
                            else cells[k]["gates"][g].get("pass")
                            for g in cells[k]["gates"]}
                           for k in cells}},
              {"episodes": P["episodes"],
               "occupancy": {"hot": P["state"]["n_hot"],
                              "cold": P["state"]["n_cold"],
                              "state_days": P["state"]["n_state_days"]}})
    print(f"finalize ok: verdict="
          f"{'judged-positive ' + str(passing_tails) if judged_positive else 'judged-negative (family closure)'} "
          f"ledger={product['trials_ledger']['total']} "
          f"elapsed={time.time() - t0:.0f}s")
    return 0


def _universe_from_faces(P, mem, price_rows):
    """Null universe per horizon: every decidable state day (hot/cold/
    mid alike) with valid fwd_h, value in pp. Mirrors the fwd closure
    of derive_faces exactly (same price index)."""
    pxd = sorted(price_rows)
    pxv = [price_rows[x] for x in pxd]
    pxi = {d: i for i, d in enumerate(pxd)}
    # rebuild state membership over all decidable days
    # derive_faces computed cstate internally; recover membership via
    # the fwd face counts: cheaper to recompute the state face here
    # from the same inputs (verbatim semantics, deterministic).
    pd_dates = sorted(mem)
    cross = {d: sum(x[0] for x in mem[d]) / len(mem[d])
             for d in pd_dates}
    cmd = sorted(cross)
    cmv = [cross[d] for d in cmd]
    cstate = pct_rank_state(cmd, cmv)
    out = {}
    for h in HORIZONS:
        vals = []
        for d in sorted(cstate):
            i = pxi.get(d)
            if i is None or i + h >= len(pxd):
                continue
            vals.append((pxv[i + h] / pxv[i] - 1.0) * 100.0)
        out[h] = vals
    return out


def cmd_verify():
    """Real-panel G-ANCHOR reconcile (read-only; no engine, no
    product, no ledger). Build-time pre-verification face."""
    mem, price_rows, _seg = _load_data()
    P = derive_faces(mem, price_rows)
    P["universe"] = _universe_from_faces(P, mem, price_rows)
    bad = anchor_drift(P)
    if bad:
        for b in bad[:12]:
            print(f"  drift: {b}")
        print(f"GATE-REFUSE(exit2): G-ANCHOR drift {len(bad)} face(s) "
              f"vs frozen probe facts -- config mismatch VOID "
              f"(one-face-off law)")
        return 2
    f = P["fwd"]
    print("G-ANCHOR verify: ALL faces bit-exact vs frozen berth/freeze "
          f"facts (panel {P['panel']['first_date']}.."
          f"{P['panel']['last_date']}, {P['panel']['n_dates_panel']} "
          f"dates, members {P['panel']['n_members_first']}->"
          f"{P['panel']['n_members_last']}; state "
          f"{P['state']['n_state_days']} decidable from "
          f"{P['state']['first_decidable_date']}, hot "
          f"{P['state']['n_hot']}/cold {P['state']['n_cold']}; "
          f"fwd20 hot {f['h20']['hot_mean']}/cold {f['h20']['cold_mean']}"
          f"/mid {f['h20']['mid_mean']} (n {f['h20']['n_hot']}/"
          f"{f['h20']['n_cold']}/{f['h20']['n_mid']}); fwd5 hot "
          f"{f['h5']['hot_mean']}/cold {f['h5']['cold_mean']}/mid "
          f"{f['h5']['mid_mean']} (n {f['h5']['n_hot']}/"
          f"{f['h5']['n_cold']}/{f['h5']['n_mid']}); degeneracy "
          f"{P['degeneracy']:.2e} < {DEGEN_TOL}; episodes V1 "
          f"{P['episodes']['V1_HOT_DEF_2d']['n_exits_to_cash']}/V2 "
          f"{P['episodes']['V2_COLD_GATE_2d']['n_entries']}; "
          f"thresholds zero-drift incl. seed "
          f"{SG.SEED_REGISTRY.get(SEED_KEY)})")
    return 0


# ------------------------------------------------------------------ selftest
def _mk_fixture(tmp):
    """Synthetic premium panel + 510300 price with planted tails:
    480 panel dates (bdays from 2020-01-02), 3 members/date (offsets
    -0.3/0/+0.3 so premium_z cross-mean exercises the identity), 520
    price dates but only 495 populated -> fwd20 lacks on the last 5
    panel days (availability face exercised). Cold clusters t=150-179
    (cross-mean -5.00..-5.29 descending) and t=300-329 (-8.00..-8.29,
    deeper so it clears the q10 left by cluster 1); hot cluster
    t=200-219 (+5.00..+5.19). Price dips to 80 through cold clusters
    (recovers right after) and spikes to 120 through the hot cluster
    -> fwd20 from late-cold days +25%, from hot days -16.67%."""
    import datetime
    import pandas as pd
    dates = list(pd.bdate_range("2020-01-02", periods=520)
                 .strftime("%Y-%m-%d"))
    panel_dates = dates[:480]
    price_dates = dates[:495]

    def cm(t):
        if 150 <= t <= 179:
            return -5.0 - 0.01 * (t - 150)
        if 200 <= t <= 219:
            return 5.0 + 0.01 * (t - 200)
        if 300 <= t <= 329:
            return -8.0 - 0.01 * (t - 300)
        return 0.1 * math.sin(t / 13.0)

    def close(t):
        if 150 <= t <= 179 or 300 <= t <= 329:
            return 80.0
        if 200 <= t <= 219:
            return 120.0
        return 100.0

    pd_dir = os.path.join(tmp, "panel")
    os.makedirs(pd_dir)
    with open(os.path.join(pd_dir, "panel.csv"), "w",
              encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "code", "premium_adj", "premium_z"])
        for t, d in enumerate(panel_dates):
            v = cm(t)
            members = [v - 0.3, v, v + 0.3]
            mu = sum(members) / 3.0
            var = sum((x - mu) ** 2 for x in members) / 3.0
            sd = math.sqrt(var)
            for j, x in enumerate(members):
                z = (x - mu) / sd if sd > 0 else 0.0
                w.writerow([d, f"M{j:02d}", round(x, 6),
                            round(z, 6)])
    daily = os.path.join(tmp, "daily")
    os.makedirs(daily)
    with open(os.path.join(daily, "510300.csv"), "w",
              encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "open", "high", "low", "close", "volume"])
        for t, d in enumerate(price_dates):
            c = close(t) if t < 480 else 100.0
            w.writerow([d, c, c * 1.01, c * 0.99, c, 1000000])
    return os.path.join(pd_dir, "panel.csv"), \
        os.path.join(daily, "510300.csv")


def cmd_selftest():
    global OUT_JSON, OUT_DIR, ATT_JSON_SHARED, SEED, K_NULLS, \
        K_SPLITS, PANEL_ANCHOR, STATE_ANCHOR, FWD_ANCHOR, \
        EPISODES_ANCHOR, _PANEL_OVERRIDE, _PRICE_OVERRIDE, \
        _D6_FACTS_OVERRIDE, _ATT_OVERRIDE, SPLIT_DATE
    tmp = tempfile.mkdtemp(prefix="innovation_quota_w10_selftest_")
    K_NULLS, K_SPLITS = 40, 12
    SPLIT_DATE = "2020-12-01"          # fixture mid (between clusters)
    SEED = SG.SEED_REGISTRY[SEED_KEY]  # frozen registry value (public)
    OUT_DIR = os.path.join(tmp, "results", "innovation_quota")
    OUT_JSON = os.path.join(OUT_DIR, "PREMIUM-SENT-P1.json")
    os.makedirs(OUT_DIR, exist_ok=True)
    _ATT_OVERRIDE = os.path.join(tmp, "gate_attrition.lane.json")
    json.dump({"entries": []}, open(_ATT_OVERRIDE, "w"))
    panel_csv, price_csv = _mk_fixture(tmp)
    _PANEL_OVERRIDE, _PRICE_OVERRIDE = panel_csv, price_csv
    d6_tmp = os.path.join(tmp, "d6_facts.json")
    json.dump({"d6_cells_face": {
        "batch_internal_hot_vs_cold": -0.1095,
        "in_register_max_abs_corr": 0.3683,
        "merge_clause_applied": [],
        "vs_registered_six": {"max_abs_corr": 0.3079,
                              "argmax": "ENGULF-CE-01"}}},
        open(d6_tmp, "w"))
    _D6_FACTS_OVERRIDE = d6_tmp
    ok = []
    try:
        # ---- data loads through the real loader chain
        mem, price_rows, seg = _load_data()
        ok.append(("fixture loads via real loaders",
                   len(mem) == 480 and len(price_rows) == 495
                   and seg["n_incremental_rows_in_cutoff_window"] == 0
                   and seg["n_rows_beyond_cutoff_dropped_lockbox"] == 0))
        P = derive_faces(mem, price_rows)
        P["universe"] = _universe_from_faces(P, mem, price_rows)
        dates = sorted(mem)
        # ---- degeneracy identity on fixture (planted z face)
        ok.append(("degeneracy identity < 1e-12",
                   0.0 <= P["degeneracy"] < 1e-12))
        # ---- state faces: warmup law (append-before-check -> decidable
        # at t=119) + planted-cluster coverage + mechanical tail
        # occupancy law (q90/q10 classify ~10% of ANY series -> 31 hot
        # = 20 planted + 11 mechanical, 70 cold = 60 + 10, both
        # deterministic fixture constants)
        di = {d: i for i, d in enumerate(dates)}
        hot_idx = {di[d] for d, _v in P["usable"][("hot", 20)]}
        cold_idx = {di[d] for d, _v in P["usable"][("cold", 20)]}
        ok.append(("state warmup + planted coverage + occupancy",
                   P["state"]["n_state_days"] == 361
                   and P["state"]["first_decidable_date"] == dates[119]
                   and P["state"]["n_hot"] == 31
                   and P["state"]["n_cold"] == 70
                   and {i for i in range(200, 220)} <= hot_idx
                   and {i for i in range(150, 180)}
                   | {i for i in range(300, 330)} <= cold_idx))
        # ---- fwd availability: only the last 5 panel days lack fwd20
        # (all of them mid; h5 fully available)
        ok.append(("fwd20 availability exercised (mid loses 5)",
                   P["fwd"]["h20"]["n_mid"] == 255
                   and P["fwd"]["h5"]["n_mid"] == 260
                   and P["fwd"]["h20"]["n_cold"] == 70
                   and P["fwd"]["h20"]["n_hot"] == 31))
        # ---- percent-unit law: planted arithmetic -- cold cell =
        # 40 recovery days @+25% + 10 mechanical (sin-trough) days whose
        # fwd20 lands inside the dip @-20% + 20 in-dip days @0
        # -> sum 8.0 over 70 days
        cold_raw = sum(v for (_d, v) in P["usable"][("cold", 20)]) / 70
        ok.append(("percent-unit law (planted mean 8/70, pp = raw x100)",
                   abs(cold_raw - 8.0 / 70.0) < 1e-12
                   and abs(cold_raw * 100.0
                           - 100.0 * cold_raw) < 1e-9))

        # ---- author-verbatim constants spot check (real registry +
        # single-source code defaults), then derive-then-freeze the
        # full anchor set (W5/W7/W9 pattern; K rescaled for selftest)
        tf = threshold_face()
        ok.append(("threshold constants author-verbatim",
                   tf["state_window"] == 252
                   and tf["state_q_hi"] == 0.9
                   and tf["state_min_periods"] == 120
                   and tf["seed_registered"] == 20326500
                   and SPLIT_DATE_FROZEN == "2023-07-01"))
        PANEL_ANCHOR = dict(P["panel"])
        STATE_ANCHOR = dict(P["state"])
        FWD_ANCHOR = {"h20": dict(P["fwd"]["h20"]),
                      "h5": dict(P["fwd"]["h5"])}
        EPISODES_ANCHOR = {"V1_HOT_DEF_2d": dict(
                               P["episodes"]["V1_HOT_DEF_2d"]),
                           "V2_COLD_GATE_2d": dict(
                               P["episodes"]["V2_COLD_GATE_2d"]),
                           "window_years":
                               P["episodes"]["window_years"]}
        _saved_th = dict(TH_ANCHOR)
        TH_ANCHOR.clear()
        TH_ANCHOR.update(tf)      # nulls_K/splits follow the selftest K
        bad = anchor_drift(P)
        ok.append(("derive-then-freeze anchors pass", bad == []))
        ok.append(("fixture episodes fire both machines",
                   P["episodes"]["V1_HOT_DEF_2d"]["n_exits_to_cash"]
                   >= 1
                   and P["episodes"]["V2_COLD_GATE_2d"]["n_entries"]
                   >= 2))

        # ---- null machinery properties
        universe = P["universe"][20]
        n_cold_usable = len(P["usable"][("cold", 20)])
        nf1 = null_family(universe, n_cold_usable, K_NULLS)
        nf2 = null_family(universe, n_cold_usable, K_NULLS)
        ok.append(("nulls deterministic + K-sized + occupancy law",
                   nf1["values"] == nf2["values"]
                   and len(nf1["values"]) == K_NULLS
                   and n_cold_usable == 70
                   and len(universe) == 356))
        ok.append(("null coverage stats sane",
                   nf1["coverage"]["mu"] < nf1["coverage"]["p95"]
                   and nf1["coverage"]["p5"]
                   < nf1["coverage"]["p95_abs_spread"]))

        # ---- V-gate pure-function hand-checks
        ok.append(("V1 COLD pass/fail + floor",
                   v1_pass("cold", 1.0, 0.1, 0.5)[0]
                   and not v1_pass("cold", 0.5, 0.1, 0.5)[0]
                   and v1_pass("cold", 0.05, 0.02, 0.005)[0]
                   and not v1_pass("cold", 0.03, 0.02, 0.005)[0]))
        ok.append(("V1 HOT single-sided",
                   v1_pass("hot", -1.0, 0.1, 0.5)[0]
                   and not v1_pass("hot", 1.5, 0.1, 0.5)[0]))
        ok.append(("V2 single-sided extremes",
                   v2_pass("cold", 1.0, -0.3, 0.4)
                   and not v2_pass("cold", 0.3, -0.3, 0.4)
                   and v2_pass("hot", -1.0, -0.3, 0.4)
                   and not v2_pass("hot", 0.0, -0.3, 0.4)))
        # synthetic V3 faces (hand-checkable; SPLIT_DATE is the
        # selftest fixture value 2020-12-01)
        d11, d12, d21, d22 = ("2020-06-01", "2020-06-02",
                              "2021-06-01", "2021-06-02")
        case_pass = [(d11, 1.0), (d12, 1.0), (d21, 2.0), (d22, 2.0)]
        case_empty = [(d11, 1.0), (d12, 1.0)]
        case_flip = [(d11, 1.0), (d12, 1.0), (d21, -2.0), (d22, -2.0)]
        ok.append(("V3 retention: pass / empty-half / sign-flip",
                   v3_halves("cold", case_pass, 0.5)["pass"] is True
                   and v3_halves("cold", case_empty, 0.5)["pass"]
                   is False
                   and v3_halves("cold", case_empty, 0.5)["reason"]
                   == "empty half (half2)"
                   and v3_halves("cold", case_flip, 0.5)["pass"]
                   is False))
        ok.append(("fixture V3: planted COLD both-halves pass",
                   v3_halves("cold", P["usable"][("cold", 20)],
                             nf1["coverage"]["mu"])["pass"] is True))
        stab = stable_splits(
            [v * 100.0 for (_d, v) in P["usable"][("cold", 20)]],
            nf1["coverage"]["mu"], K_SPLITS)
        ok.append(("STABLE flag on planted tail",
                   stab["segment_stable"] is True
                   and stab["n_splits"] == K_SPLITS))

        # ---- full pipeline cells on fixture
        cells = _build_cells(P)
        cold20 = cells[("cold", 20)]
        ok.append(("4 cells built, COLD-H20 planted-pass (V1^V2^V3)",
                   set(cells) == {(t, h) for t in TAILS
                                  for h in HORIZONS}
                   and cold20["gates"]["V1_direction_magnitude"]["pass"]
                   and cold20["gates"]["V2_null_extreme"]["pass"]
                   and cold20["gates"]["V3_oos_retention"]["pass"]))
        ok.append(("all gate verdicts are bools (deterministic faces)",
                   all(isinstance(c["gates"][g]["pass"], bool)
                       for c in cells.values()
                       for g in c["gates"])))
        ok.append(("dual-unit columns disclosed per cell",
                   all("cell_mean_raw" in c and "cell_mean_pp" in c
                       for c in cells.values())))

        # ---- product assembly + r450 guard
        product = {
            "batch": BATCH_NAME, "evidence_cutoff": EVIDENCE_CUTOFF,
            "cutoff_meta": SG.cutoff_meta(EVIDENCE_CUTOFF),
            "cells": {cells[k]["cell_name"]: cells[k] for k in cells},
            "funnel": {"harvest_column": 1,
                       "gate_column": "fixture"},
        }
        write_product(product)
        ok.append(("phase-1 product written",
                   os.path.exists(OUT_JSON)
                   and product["cutoff_meta"]["evidence_cutoff"]
                   == EVIDENCE_CUTOFF))
        with open(OUT_JSON + ".tmp2", "w", encoding="utf-8") as fh:
            json.dump({"trials_ledger": {"prev_total": 1,
                                         "total": 2}}, fh)
        os.replace(OUT_JSON + ".tmp2", OUT_JSON)
        ok.append(("r450 guard: judged product refuses (rc=2 face)",
                   _refuse_if_judged() == 2))
        write_product(product)
        ok.append(("r450 guard: phase-1-only product resumes",
                   _refuse_if_judged() == 0))

        # ---- finalize face with stubbed shared-library state
        _al = SG.append_ledger
        SG.append_ledger = lambda *a, **k: {"prev_total": 0,
                                            "total": 100,
                                            "batch": BATCH_NAME}
        try:
            product["trials_ledger"] = SG.append_ledger(
                BATCH_NAME, BATCH_CELLS)
            _attr_row(BATCH_NAME, BATCH_CELLS,
                      int(product["trials_ledger"]["total"]),
                      {"family_verdict": {"fixture": True}},
                      {"episodes": P["episodes"]})
            write_product(product)
            att = json.load(open(_ATT_OVERRIDE, encoding="utf-8"))
            ok.append(("finalize: ledger embedded + attrition lane row",
                       product["trials_ledger"]["total"] == 100
                       and att["entries"][-1]["batch"] == BATCH_NAME
                       and att["entries"][-1]
                       ["cells_ledger_delta"] == BATCH_CELLS))
        finally:
            SG.append_ledger = _al

        # ---- drift refusal battery (each family one-face-off)
        real = PANEL_ANCHOR["n_dates_panel"]
        PANEL_ANCHOR = dict(PANEL_ANCHOR, n_dates_panel=real + 1)
        ok.append(("G-PANEL drift refusal", anchor_drift(P) != []))
        PANEL_ANCHOR = dict(PANEL_ANCHOR, n_dates_panel=real)
        real_c = STATE_ANCHOR["n_cold"]
        STATE_ANCHOR = dict(STATE_ANCHOR, n_cold=real_c + 1)
        ok.append(("state drift refusal", anchor_drift(P) != []))
        STATE_ANCHOR = dict(STATE_ANCHOR, n_cold=real_c)
        FWD_ANCHOR["h20"] = dict(FWD_ANCHOR["h20"], n_cold=999)
        ok.append(("fwd availability drift refusal",
                   anchor_drift(P) != []))
        FWD_ANCHOR["h20"] = dict(P["fwd"]["h20"])
        real_e = EPISODES_ANCHOR["V1_HOT_DEF_2d"]["n_exits_to_cash"]
        EPISODES_ANCHOR["V1_HOT_DEF_2d"] = dict(
            EPISODES_ANCHOR["V1_HOT_DEF_2d"],
            n_exits_to_cash=real_e + 1)
        ok.append(("episode drift refusal", anchor_drift(P) != []))
        EPISODES_ANCHOR["V1_HOT_DEF_2d"] = dict(
            EPISODES_ANCHOR["V1_HOT_DEF_2d"],
            n_exits_to_cash=real_e)
        TH_ANCHOR["state_window"] = 253
        ok.append(("threshold drift refusal", anchor_drift(P) != []))
        TH_ANCHOR["state_window"] = 252
        ok.append(("anchors restored -> all pass again",
                   anchor_drift(P) == []))
        TH_ANCHOR.clear()
        TH_ANCHOR.update(_saved_th)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    n_ok = sum(1 for _, v in ok if v)
    print(f"innovation_quota_w10 selftest: {n_ok}/{len(ok)} PASS")
    for name, v in ok:
        if not v:
            print(f"  FAIL: {name}")
    return 0 if n_ok == len(ok) else 1


# ------------------------------------------------------------------ driver
def main():
    try:
        # r236 GBK-console law: reconfigure at entry (idempotent)
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "verify", "selftest"])
    a = ap.parse_args()
    if a.cmd == "selftest":
        return cmd_selftest()
    if a.cmd == "verify":
        return cmd_verify()
    guard = _refuse_if_judged()
    if guard:
        return guard
    return cmd_run()


if __name__ == "__main__":
    sys.exit(main())
