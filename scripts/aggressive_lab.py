"""AGGRESSIVE_LAB runner (CEO order O-20260925-1126; ticket T-2026-09-25-56;
claim R157 bm-a; prereg research/AGGRESSIVE_LAB.md FROZEN pre-run -- freeze
commit precedes any run; sha256 of every weight vector frozen in prereg s3;
no tuning after seeing results, iron rule 3).

Dual-track (order s1): this lab = aggressive candidate SUPPLY face; the SPM
stability bench (0.70 / J2 frozen lines) stays the ONLY selector. ZERO
adoption, ZERO canon/paper wiring in this batch; month-boundary entry into
the T-27 tournament pool per ticket (e).

Five aggressive blend variants over the T-27 frozen 28-member roster
(zero new signal functions, zero search, zero nulls -> SEED_REGISTRY +0):
  AGGR-CONC-TOP2   top-2 OOS-Sharpe concentration 0.50/0.50
  AGGR-OFFENSE     corps budgets 70/15/15; air-defense corps EMPTY in
                   roster v1 (honest fact) -> pro-rata renorm 70/85 offense
                   + 15/85 oscillation, equal weight within corps
  AGGR-MOM         T-27 registered loser C revived verbatim
  AGGR-NOCASH      B_MAXDIV frozen weights verbatim + paper risk-budget
                   face (cap 95%, cash leg off) -- blend face = canon
                   verification leg, execution-layer delta declared
  AGGR-REGIME      T-27 registered loser D revived, v3 states: GREEN/
                   YELLOW -> offense-corps full weights, ORANGE/RED ->
                   A_IV defensive (v3 raw states, causal shift(1))

Judgment bench = T-28 J-line verbatim (frozen): W-CUR 2026-01-05..09-23
{x1,x2} -> J1 (ret>0, |dd|<=5%) / J2 (x2 ret>0); W-SEG v3 segment classes
-> J3 (per-class cum >= -5%); W-GRID {legacy,deep}x{6m,12m,24m}x{base,x2}
-> J5 D7 four disclosures + beat rates; KPI = return ceiling + bull-segment
delta vs canon B_MAXDIV, NOT promotion count. Expected failures reported
honestly (aggressive faces are EXPECTED to breach J2/J3 -- order s3).

Sleeves: 56 = 28 members x {x1,x2} = T-27 machinery reproduction at the
live paper panel truncated 2026-09-23 (o1600 caliber, T-28 precedent),
ledger +0. Judgment cells = 5 variants x 20 = 100 aggregate cells ->
append_ledger('T56-AGGRESSIVE-LAB', 100, ...).

Slice-2 (ticket (d), prereg s6 frozen): `paper` subcommand -- 5 paper
accounts AGGR-* in results/aggr_paper/ (each CNY 1,000,000 initial,
shadow guard, experimental risk-budget fields, marks = daily blend
accrual from the first bar after evidence_cutoff 2026-09-23, sleeve
domain advancing with new bars; PROS-* whitelist lane paradigm -- NOT
in t35/scorecard CEO faces; marks are not trials -> ledger +0).

Pool-ready per O-2100/O-2130: --shard/--shards over the sleeve job set,
workers_plan in the pool entry; first judgment run executed in-round per
R41 <5min exemption (T-28 caliber 5.4s empirical).

CLI: run [--shard S --shards N] | paper | family | selftest
"""
import argparse
import hashlib
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

from config import PATHS
from live.paper import load_core, v3_state_series
from parallel_runner import run_cells_parallel, worker_cap
from science_gates import append_ledger, cutoff_meta, ledger_head
from t27_blend_tournament import (FROZEN_ROSTER, _frame_returns,
                                  daily_ret_matrix)
from t28_stable_profit import (TOURN_JSON, W_CUR_END, W_CUR_START, WINDOWS,
                               _blend_daily_ret, _grid_unit,
                               _load_deep_grid, _load_legacy_grid,
                               _seg_classes, _sleeve_worker, _window_face)

PREREG = os.path.join(PATHS.root, "research", "AGGRESSIVE_LAB.md")
OUT_JSON = os.path.join(PATHS.results_dir, "aggressive_lab.json")
GA_PATH = os.path.join(PATHS.results_dir, "gate_attrition.json")
AGGR_DIR = os.path.join(PATHS.results_dir, "aggr_paper")   # T-56 slice-2 lane
N_CELLS = 100                     # prereg s0 (5 variants x 20 T-28 cells)
SLEEVE_CUTOFF = W_CUR_END          # prereg s2 (bench comparability w/ T-28)
# slice-2 paper lane (prereg s6 frozen): marks accrue on the first bar
# STRICTLY AFTER the frozen judgment domain (evidence_cutoff 2026-09-23)
PAPER_START = pd.Timestamp("2026-09-24")
INITIAL_CNY = 1_000_000.0
RISK_BUDGET = {                    # prereg s6: experimental, per-account
    "AGGR-NOCASH": {"position_cap": 0.95, "cash_parking_leg": "disabled"},
}
CE6 = ("COMPOSITE-CE-01", "COMPOSITE-CE-02", "DROUGHT-CE-01", "ENGULF-CE-01",
       "NEEDLE-DE-01", "VOLATILITY-CE-01")
OFFENSE_CORPS = ("COMPOSITE-CE-01", "PROS-DUCK-01", "PROS-DUCK-CE-01",
                 "PROS-IBB-01", "PROS-IBB-CE-01", "PROS-VOB-CE-01")
OSCILLATION_CORPS = ("COMPOSITE-CE-02", "DROUGHT-CE-01", "ENGULF-CE-01",
                     "NEEDLE-DE-01", "PROS-BBS-01", "PROS-BBS-CE-01",
                     "PROS-DOJI-01", "PROS-DOJI-CE-01", "PROS-HAM-01",
                     "PROS-HAM-CE-01", "PROS-OVB-01", "PROS-OVB-CE-01",
                     "PROS-TMU-01", "PROS-TMU-CE-01", "VOLATILITY-CE-01")
# corps partition gate (prereg s2): 6 + 15 + 7 pending == 28, disjoint
PENDING_CORPS = tuple(sorted(set(FROZEN_ROSTER)
                             - set(OFFENSE_CORPS) - set(OSCILLATION_CORPS)))
ROSTER = tuple(sorted(FROZEN_ROSTER))
VARIANTS = ("AGGR-CONC-TOP2", "AGGR-OFFENSE", "AGGR-MOM", "AGGR-NOCASH",
            "AGGR-REGIME")
FROZEN_SHA = {                    # prereg s3 (frozen pre-run)
    "AGGR-CONC-TOP2": "9a9579482cc1851b",
    "AGGR-OFFENSE": "eac2b583586e8bb3",
    "AGGR-MOM": "5655696a60300bf4",
    "AGGR-NOCASH": "9b112d51583aeeb7",
    "AGGR-REGIME-offensive": "b95dab70673f5941",
    "AGGR-REGIME-defensive": "3868f2f55bae825e",
}
OFFENSE_BUDGET, AIRDEFENSE_BUDGET, OSC_BUDGET = 0.70, 0.15, 0.15

# ---------------------------------------------------------------------------
# T-58 s2 broad aggressive family (CEO order O-20260925-1138; ticket
# T-2026-09-25-58; prereg research/AGGR_FAMILY_PREREG.md FROZEN pre-run).
# 15 NEW variants on six axes + the five T-56 variants = 20-member family,
# zero rebuild of T-56 faces. Selection basis for TOP-N faces = registered
# OOS Sharpe (member registry firm/traders/*.json -- cherry face honestly
# acknowledged, T-56 s3 precedent; purpose = ceiling test).
# ---------------------------------------------------------------------------
FAM_VARIANTS = ("AGGR-TOP3", "AGGR-FULLCE", "AGGR-OFFENSE-FULL",
                "AGGR-TOP2-80", "AGGR-TOP2-60", "AGGR-GREEN-MAX",
                "AGGR-REG3", "AGGR-TOP2-C80", "AGGR-TOP2-C95",
                "AGGR-BARBELL", "AGGR-TOP2-MON", "AGGR-TOP2-WK",
                "AGGR-GREEN-TOP2", "AGGR-TOP3-GRAD", "AGGR-FULLCE-C80")
FAM_N_CELLS = 300                  # prereg s0 (15 variants x 20 cells)
FAM_OUT_JSON = os.path.join(PATHS.results_dir, "aggressive_family.json")
PREREG_FAMILY = os.path.join(PATHS.root, "research",
                             "AGGR_FAMILY_PREREG.md")
RULE_MON = ("boundary=first trading day of each calendar month in the x1 "
            "sleeve inner-join index; at boundary b rank members by trailing "
            "compounded x1 daily return over the last 63 trading days with "
            "index strictly < b; top-2 equal 0.5/0.5; ties broken by "
            "registered OOS Sharpe descending then member id ascending; "
            "warmup (fewer than 63 rows before b) -> frozen static "
            "TOP2-OOS-Sharpe face (VOLATILITY-CE-01 0.5 + COMPOSITE-CE-01 "
            "0.5); x2 cost face reuses x1-selected weights")
RULE_WK = ("boundary=first trading day of each ISO week in the x1 sleeve "
           "inner-join index; at boundary b rank members by trailing "
           "compounded x1 daily return over the last 21 trading days with "
           "index strictly < b; top-2 equal 0.5/0.5; ties broken by "
           "registered OOS Sharpe descending then member id ascending; "
           "warmup (fewer than 21 rows before b) -> frozen static "
           "TOP2-OOS-Sharpe face (VOLATILITY-CE-01 0.5 + COMPOSITE-CE-01 "
           "0.5); x2 cost face reuses x1-selected weights")
FAM_FROZEN_SHA = {                 # probe-printed at freeze (R162)
    "AGGR-TOP3": "364f9b0b9f0236e7",
    "AGGR-FULLCE": "b5868fe1e26690a8",
    "AGGR-OFFENSE-FULL": "b95dab70673f5941",
    "AGGR-TOP2-80": "12ec4a3a90bb3dfa",
    "AGGR-TOP2-60": "465c3ea667a6b1d5",
    "AGGR-TOP2-C80": "0481dc98d379748c",
    "AGGR-TOP2-C95": "c7f512ab59c66da2",
    "AGGR-BARBELL": "93deb766fe8bc552",
    "AGGR-TOP3-GRAD": "fa598198d684514f",
    "AGGR-FULLCE-C80": "1c74f4d052d19b86",
    "AGGR-GREEN-MAX-off": "b95dab70673f5941",
    "AGGR-GREEN-MAX-def": "3868f2f55bae825e",
    "AGGR-REG3-off": "b95dab70673f5941",
    "AGGR-REG3-osc": "b20b9b26dd5629e3",
    "AGGR-REG3-def": "3868f2f55bae825e",
    "AGGR-GREEN-TOP2-off": "9a9579482cc1851b",
    "AGGR-GREEN-TOP2-def": "3868f2f55bae825e",
    "AGGR-TOP2-MON-rule": "3317402382e496e0",
    "AGGR-TOP2-WK-rule": "80a6f61c235aed7b",
}


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def w_sha(w: dict) -> str:
    return hashlib.sha256(
        json.dumps(w, sort_keys=True).encode()).hexdigest()[:16]


def build_weights() -> dict:
    """Five frozen weight faces (prereg s3) + sha gate vs prereg freeze."""
    with open(TOURN_JSON, encoding="utf-8") as fh:
        tour = json.load(fh)
    w_mom = dict(tour["weights"]["C_IVMOM"]["weights"])
    w_nocash = dict(tour["weights"]["B_MAXDIV"]["weights"])
    w_def = dict(tour["weights"]["A_IV"]["weights"])

    w_conc = {t: 0.0 for t in ROSTER}
    w_conc["VOLATILITY-CE-01"] = 0.5
    w_conc["COMPOSITE-CE-01"] = 0.5

    # air-defense corps EMPTY (roster v1 fact) -> pro-rata renorm (prereg s3)
    denom = OFFENSE_BUDGET + OSC_BUDGET      # 0.85
    w_off = {t: 0.0 for t in ROSTER}
    for t in OFFENSE_CORPS:
        w_off[t] = round(OFFENSE_BUDGET / denom / len(OFFENSE_CORPS), 6)
    for t in OSCILLATION_CORPS:
        w_off[t] = round(OSC_BUDGET / denom / len(OSCILLATION_CORPS), 6)

    w_reg_off = {t: 0.0 for t in ROSTER}
    for t in OFFENSE_CORPS:
        w_reg_off[t] = round(1.0 / len(OFFENSE_CORPS), 6)

    faces = {"AGGR-CONC-TOP2": {"static": w_conc},
             "AGGR-OFFENSE": {"static": w_off},
             "AGGR-MOM": {"static": w_mom},
             "AGGR-NOCASH": {"static": w_nocash},
             "AGGR-REGIME": {"regime": {"offensive": w_reg_off,
                                        "defensive": w_def}}}
    checks = {"AGGR-CONC-TOP2": w_sha(w_conc),
              "AGGR-OFFENSE": w_sha(w_off),
              "AGGR-MOM": w_sha(w_mom),
              "AGGR-NOCASH": w_sha(w_nocash),
              "AGGR-REGIME-offensive": w_sha(w_reg_off),
              "AGGR-REGIME-defensive": w_sha(w_def)}
    for key, got in checks.items():
        want = FROZEN_SHA[key]
        if got != want:
            raise SystemExit(f"WEIGHT-SHA GATE FAIL: {key} got {got} "
                             f"want {want} (prereg s3 frozen)")
    for name, w in (("MOM", w_mom), ("NOCASH", w_nocash),
                    ("REGIME-defensive", w_def)):
        if set(w) != set(ROSTER):
            raise SystemExit(f"ROSTER GATE FAIL: {name} weight keys "
                             f"!= frozen roster")
    return faces, checks, tour


def _regime_blend(sleeves: dict, off: dict, defw: dict,
                  states: pd.Series):
    """AGGR-REGIME frame: v3 raw states, causal; GREEN/YELLOW -> offensive,
    ORANGE/RED -> defensive; state(t-1) drives day t (shift(1)); first day
    defaults offensive (T-27 D precedent). Returns (port_ret, w_mean)."""
    R = daily_ret_matrix(sleeves, "x1")
    if set(off) != set(R.columns) or set(defw) != set(R.columns):
        raise SystemExit("REGIME GATE FAIL: weight/column mismatch")
    s_prev = (states.reindex(R.index, method="ffill")
              .shift(1).fillna("GREEN"))
    offensive = s_prev.isin(["GREEN", "YELLOW"])
    W = pd.DataFrame([off if b else defw for b in offensive],
                     index=R.index, columns=list(R.columns))
    port = (R * W).sum(axis=1)
    return port, {t: round(float(x), 6) for t, x in W.mean().items()}


def _ce6_restrict(w: dict) -> dict:
    """Restrict a 28-key weight vector to the grid's CE-6 domain, renorm
    (T-28 honest sub-portfolio disclosure, prereg s4)."""
    sub_sum = sum(w[t] for t in CE6)
    if sub_sum <= 0:
        raise SystemExit("CE6-RESTRICT GATE FAIL: zero CE-6 mass")
    return {t: round(w[t] / sub_sum, 8) for t in CE6}


def _oos_sharpe_map() -> dict:
    """Registered OOS Sharpe per roster member (firm/traders registry --
    the same registry T-56 s3 verified against; frozen selection basis)."""
    import glob
    out = {}
    for p in glob.glob(os.path.join(PATHS.root, "firm", "traders",
                                    "*.json")):
        with open(p, encoding="utf-8-sig") as fh:
            d = json.load(fh)
        tid = d.get("id")
        if tid in ROSTER:
            out[tid] = float(d["backtest"]["out_sample"]["sharpe"])
    if set(out) != set(ROSTER):
        raise SystemExit(f"SHARPE-MAP GATE FAIL: {sorted(set(ROSTER) ^ set(out))}")
    return out


def build_family_vectors() -> dict:
    """T-58 s2 family construction (deterministic, zero search): 10 static
    vectors + 3 leg-map faces + 2 rotation rules. Returns (faces, checks);
    gate vs FAM_FROZEN_SHA happens in build_family_weights()."""
    with open(TOURN_JSON, encoding="utf-8") as fh:
        tour = json.load(fh)
    w_def = dict(tour["weights"]["A_IV"]["weights"])

    top2 = ("VOLATILITY-CE-01", "COMPOSITE-CE-01")       # OOS Sharpe #1/#2
    top3 = top2 + ("COMPOSITE-CE-02",)                   # OOS Sharpe #3
    fullce = ("COMPOSITE-CE-01", "COMPOSITE-CE-02", "DROUGHT-CE-01",
              "ENGULF-CE-01", "NEEDLE-DE-01", "VOLATILITY-CE-01")

    def filled(pairs) -> dict:
        w = {t: 0.0 for t in ROSTER}
        for t, v in pairs:
            w[t] = v
        return w

    w_top3 = filled([(t, round(1.0 / 3, 6)) for t in top3])
    w_fullce = filled([(t, round(1.0 / 6, 6)) for t in fullce])
    w_offfull = filled([(t, round(1.0 / 6, 6)) for t in OFFENSE_CORPS])
    w_t2_80 = filled([(top2[0], 0.8), (top2[1], 0.2)])
    w_t2_60 = filled([(top2[0], 0.6), (top2[1], 0.4)])
    w_t2_c80 = filled([(top2[0], 0.4), (top2[1], 0.4)])       # cash 0.2
    w_t2_c95 = filled([(top2[0], 0.475), (top2[1], 0.475)])   # cash 0.05
    w_t3_grad = filled([(top3[0], 0.5), (top3[1], 0.3), (top3[2], 0.2)])
    w_fc_c80 = filled([(t, round(0.8 / 6, 6)) for t in fullce])
    w_barbell = filled([(t, round(0.4 / 6, 6)) for t in OFFENSE_CORPS])
    for t in ROSTER:
        w_barbell[t] = round(w_barbell[t] + round(w_def[t] * 0.6, 6), 6)

    w_osc15 = filled([(t, round(1.0 / 15, 6)) for t in OSCILLATION_CORPS])
    w_top2 = filled([(top2[0], 0.5), (top2[1], 0.5)])

    faces = {
        "AGGR-TOP3": {"static": w_top3},
        "AGGR-FULLCE": {"static": w_fullce},
        "AGGR-OFFENSE-FULL": {"static": w_offfull},
        "AGGR-TOP2-80": {"static": w_t2_80},
        "AGGR-TOP2-60": {"static": w_t2_60},
        "AGGR-TOP2-C80": {"static": w_t2_c80},
        "AGGR-TOP2-C95": {"static": w_t2_c95},
        "AGGR-BARBELL": {"static": w_barbell},
        "AGGR-TOP3-GRAD": {"static": w_t3_grad},
        "AGGR-FULLCE-C80": {"static": w_fc_c80},
        "AGGR-GREEN-MAX": {"legs": {"off": w_offfull, "def": w_def},
                           "gate": {"GREEN": "off", "YELLOW": "def",
                                    "ORANGE": "def", "RED": "def"}},
        "AGGR-REG3": {"legs": {"off": w_offfull, "osc": w_osc15,
                               "def": w_def},
                      "gate": {"GREEN": "off", "YELLOW": "off",
                               "ORANGE": "osc", "RED": "def"}},
        "AGGR-GREEN-TOP2": {"legs": {"off": w_top2, "def": w_def},
                            "gate": {"GREEN": "off", "YELLOW": "def",
                                     "ORANGE": "def", "RED": "def"}},
        "AGGR-TOP2-MON": {"rotation": {"kind": "month", "lookback": 63}},
        "AGGR-TOP2-WK": {"rotation": {"kind": "week", "lookback": 21}},
    }
    checks = {
        "AGGR-TOP3": w_sha(w_top3), "AGGR-FULLCE": w_sha(w_fullce),
        "AGGR-OFFENSE-FULL": w_sha(w_offfull),
        "AGGR-TOP2-80": w_sha(w_t2_80), "AGGR-TOP2-60": w_sha(w_t2_60),
        "AGGR-TOP2-C80": w_sha(w_t2_c80), "AGGR-TOP2-C95": w_sha(w_t2_c95),
        "AGGR-BARBELL": w_sha(w_barbell),
        "AGGR-TOP3-GRAD": w_sha(w_t3_grad),
        "AGGR-FULLCE-C80": w_sha(w_fc_c80),
        "AGGR-GREEN-MAX-off": w_sha(w_offfull),
        "AGGR-GREEN-MAX-def": w_sha(w_def),
        "AGGR-REG3-off": w_sha(w_offfull), "AGGR-REG3-osc": w_sha(w_osc15),
        "AGGR-REG3-def": w_sha(w_def),
        "AGGR-GREEN-TOP2-off": w_sha(w_top2),
        "AGGR-GREEN-TOP2-def": w_sha(w_def),
        "AGGR-TOP2-MON-rule": hashlib.sha256(
            RULE_MON.encode()).hexdigest()[:16],
        "AGGR-TOP2-WK-rule": hashlib.sha256(
            RULE_WK.encode()).hexdigest()[:16],
    }
    return faces, checks


def build_family_weights() -> dict:
    """Family construction + sha gate vs prereg freeze (FAM_FROZEN_SHA)."""
    faces, checks = build_family_vectors()
    if not FAM_FROZEN_SHA:
        raise SystemExit("FAM sha table empty -- freeze incomplete")
    for key, got in checks.items():
        want = FAM_FROZEN_SHA.get(key)
        if want is None:
            raise SystemExit(f"FAM-SHA GATE FAIL: unknown key {key}")
        if got != want:
            raise SystemExit(f"FAM-SHA GATE FAIL: {key} got {got} "
                             f"want {want} (prereg frozen)")
    return faces, checks


def _legs_blend(sleeves: dict, legs: dict, gate: dict, states: pd.Series):
    """Leg-map frame (2- or 3-leg generalization of _regime_blend):
    state(t-1) -> leg via frozen gate map; first day defaults GREEN
    (T-27 D precedent). Returns (port_ret, w_mean, W)."""
    R = daily_ret_matrix(sleeves, "x1")
    for leg, w in legs.items():
        if set(w) != set(R.columns):
            raise SystemExit(f"LEGS GATE FAIL: {leg} weight/column mismatch")
    s_prev = (states.reindex(R.index, method="ffill")
              .shift(1).fillna("GREEN"))
    leg_of = s_prev.map(gate)
    if leg_of.isna().any():
        raise SystemExit("LEGS GATE FAIL: unmapped v3 state")
    W = pd.DataFrame([legs[l] for l in leg_of],
                     index=R.index, columns=list(R.columns))
    port = (R * W).sum(axis=1)
    w_mean = {t: round(float(x), 6) for t, x in W.mean().items()}
    return port, w_mean, W


def _rotation_blend(sleeves: dict, kind: str, lookback: int,
                    sharpe_map: dict):
    """Rotation frame (T-58 rotation-speed axis, rules frozen in prereg
    s3): at each boundary re-rank members by trailing compounded x1
    return over `lookback` rows strictly before the boundary day
    (forward-locked), top-2 equal 0.5/0.5; warmup -> frozen static
    TOP2-OOS-Sharpe face; ties by OOS Sharpe desc then id asc.
    Returns (port_ret, w_mean, W)."""
    R = daily_ret_matrix(sleeves, "x1")
    if kind == "month":
        keys = [str(p) for p in R.index.to_period("M")]
    else:
        iso = R.index.isocalendar()
        keys = [f"{y}W{str(int(w)).zfill(2)}"
                for y, w in zip(iso["year"], iso["week"])]
    fallback = {t: 0.0 for t in ROSTER}
    fallback["VOLATILITY-CE-01"] = 0.5
    fallback["COMPOSITE-CE-01"] = 0.5
    W = pd.DataFrame(0.0, index=R.index, columns=list(R.columns))
    prev_key, cur = None, None
    for i, d in enumerate(R.index):
        if keys[i] != prev_key:
            if i >= lookback:
                hist = R.iloc[i - lookback:i]     # rows strictly < d
                metric = (1.0 + hist).prod() - 1.0
                top = sorted(
                    R.columns,
                    key=lambda t: (-float(metric[t]),
                                   -sharpe_map.get(t, 0.0), t))[:2]
                cur = {t: (0.5 if t in top else 0.0) for t in ROSTER}
            else:
                cur = dict(fallback)
            prev_key = keys[i]
        W.loc[d] = [cur[t] for t in W.columns]
    port = (R * W).sum(axis=1)
    w_mean = {t: round(float(x), 6) for t, x in W.mean().items()}
    return port, w_mean, W


def run_batch(shard: int = 0, shards: int = 1) -> int:
    t0 = time.time()
    log("=== T56-AGGRESSIVE-LAB (prereg R157 frozen) ===")
    faces, sha_checks, tour = build_weights()
    log(f"weight sha gates PASS ({len(sha_checks)} vectors)")

    # -- sleeves: 28 members x {x1,x2} at live panel, T-28 caliber (ledger +0)
    prices_full = load_core()
    cutoff = max(df.index.max() for df in prices_full.values())
    if cutoff < SLEEVE_CUTOFF:
        raise SystemExit(f"PANEL GATE FAIL: cutoff {cutoff.date()} < "
                         f"{SLEEVE_CUTOFF.date()}")
    prices = {s: df[df.index <= SLEEVE_CUTOFF]
              for s, df in prices_full.items()}
    jobs = [(tid, mult, prices, SLEEVE_CUTOFF) for tid in ROSTER
            for mult in (None, 2.0)]
    if shards > 1:                       # pool shard protocol (O-2100)
        jobs = [j for i, j in enumerate(jobs) if i % shards == shard]
        log(f"shard {shard}/{shards}: {len(jobs)} sleeve jobs")
    res = run_cells_parallel(
        [(f"{a[0]}|{a[1] or 'x1'}", _sleeve_worker, a) for a in jobs],
        workers=min(worker_cap(), 25), desc="aggr-sleeves")
    sleeves = {}
    for tid in ROSTER:
        r1, r2 = res[f"{tid}|x1"], res[f"{tid}|2.0"]
        for r in (r1, r2):
            r["eq_s"] = pd.Series(r["eq"], index=pd.to_datetime(r["dates"]))
        sleeves[tid] = {"x1": r1, "x2": r2}
    log(f"sleeves: {len(sleeves)} members x 2 faces ({time.time()-t0:.0f}s)")

    states = v3_state_series()
    lt, lp = _load_legacy_grid()
    dt, dp = _load_deep_grid()

    out_variants, corr_inputs = {}, {"CANON-B_MAXDIV": None}
    canon = None
    for name in VARIANTS:
        face = faces[name]
        if "static" in face:
            w = face["static"]
            pr1 = _blend_daily_ret({t: sleeves[t]["x1"] for t in ROSTER}, w)
            pr2 = _blend_daily_ret({t: sleeves[t]["x2"] for t in ROSTER}, w)
            rep_w = dict(w)
            w_src = "static"
        else:
            off, defw = face["regime"]["offensive"], face["regime"]["defensive"]
            pr1, w_mean = _regime_blend(sleeves, off, defw, states)
            # x2 face reuses x1-frozen regime weights (prereg s3)
            sl2 = {t: sleeves[t]["x2"] for t in ROSTER}
            R2 = pd.concat({tid: sl2[tid]["eq_s"] for tid in sl2},
                           axis=1, join="inner").dropna().pct_change().dropna()
            s_prev = (states.reindex(R2.index, method="ffill")
                      .shift(1).fillna("GREEN"))
            offensive = s_prev.isin(["GREEN", "YELLOW"])
            W2 = pd.DataFrame([off if b else defw for b in offensive],
                              index=R2.index, columns=list(R2.columns))
            pr2 = (R2 * W2).sum(axis=1)
            rep_w = w_mean                     # time-avg (T-27 D precedent)
            w_src = "regime_v3"

        wcur = {"x1": _window_face(pr1, W_CUR_START, W_CUR_END),
                "x2": _window_face(pr2, W_CUR_START, W_CUR_END)}
        wseg = {f: _seg_classes(pr, states) for f, pr in
                (("x1", pr1), ("x2", pr2))}
        j1 = bool(wcur["x1"]["ret"] > 0 and abs(wcur["x1"]["dd"]) <= 0.05)
        j2 = bool(wcur["x2"]["ret"] > 0)
        j3 = all((wseg[f][c]["cum_ret"] is not None
                  and wseg[f][c]["cum_ret"] >= -0.05)
                 for f in ("x1", "x2") for c in ("bull", "chop", "bear"))

        w_ce = _ce6_restrict(rep_w)
        grid = {}
        for axis, tret, passive in (("legacy", lt, lp), ("deep", dt, dp)):
            for window in WINDOWS:
                for fce in ("x1", "x2"):
                    grid[f"{axis}|{window}|{fce}"] = _grid_unit(
                        tret, passive, w_ce, CE6, window, fce)
        n12 = grid["legacy|12m|x1"]["n"] + grid["deep|12m|x1"]["n"]
        k12 = (grid["legacy|12m|x1"]["beats"]
               + grid["deep|12m|x1"]["beats"])

        # descriptive faces (prereg s4 hard-bound trio: median / p99.9)
        dr = {"median": round(float(pr1.median()), 6),
              "p999": round(float(pr1.quantile(0.999)), 6)}

        out_variants[name] = {
            "weights_src": w_src, "weights_sha": sha_checks.get(
                name, sha_checks.get(f"{name}-offensive")),
            "regime_legs_sha": ({"offensive": FROZEN_SHA[
                "AGGR-REGIME-offensive"], "defensive": FROZEN_SHA[
                    "AGGR-REGIME-defensive"]} if name == "AGGR-REGIME"
                else None),
            "weights_representative": {k: v for k, v in rep_w.items()
                                       if v > 0},
            "grid_ce6_restricted": w_ce,
            "w_cur": wcur, "w_seg": wseg,
            "judgments": {"J1_current_window_profit": j1,
                          "J2_x2_survival": j2,
                          "J3_regime_segment_stability": j3},
            "daily_ret_faces_x1": dr,
            "w_grid": grid,
            "grid_12m_pooled": {"n": n12, "beats": k12,
                                "rate": round(k12 / n12, 4) if n12 else None},
        }
        corr_inputs[name] = pr1
        if name == "AGGR-NOCASH":
            canon = out_variants[name]        # blend face == canon B_MAXDIV
        log(f"{name}: J1={j1} J2={j2} J3={j3} "
            f"W-CUR x1 ret={wcur['x1']['ret']} dd={wcur['x1']['dd']} "
            f"12m pooled={k12}/{n12}")

    # -- KPI faces: ceiling + bull delta vs canon (prereg s4)
    canon_bull = canon["w_seg"]["x1"]["bull"]["cum_ret"]
    for name in VARIANTS:
        v = out_variants[name]
        v["kpi"] = {
            "return_ceiling_w_cur_x1": v["w_cur"]["x1"]["ret"],
            "bull_delta_vs_canon": round(
                v["w_seg"]["x1"]["bull"]["cum_ret"] - canon_bull, 6),
            "note": "KPI = ceiling + bull delta (ticket); promotion count "
                    "is NOT the lab KPI; expected J2/J3 breaches are honest "
                    "lab outcomes (order s3)",
        }
    # variant daily-return correlation (descriptive, prereg s1)
    cdf = pd.DataFrame({k: v for k, v in corr_inputs.items()
                        if v is not None}).dropna()
    corr = {a: {b: round(float(cdf[a].corr(cdf[b])), 4)
               for b in cdf.columns} for a in cdf.columns}

    # -- ledger (100 aggregate judgment cells; sleeves +0 reproduction)
    head = ledger_head()
    led = append_ledger("T56-AGGRESSIVE-LAB", N_CELLS,
                        os.path.basename(OUT_JSON),
                        note="100 aggregate judgment cells (5 aggressive "
                             "variants x 20 T-28-caliber cells: W-CUR 2 + "
                             "W-SEG 6 + W-GRID 12); W-GRID per-cell N "
                             "follows P5C/t22 already-counted ledgers, no "
                             "recount; 56 sleeves = T-27-machinery "
                             "reproductions o1600 caliber, ledger +0; zero "
                             "adoption zero wiring (dual-track, order s1)",
                        evidence_cutoff=str(SLEEVE_CUTOFF.date()),
                        prev_total=head["total"])
    log(f"ledger: prev={head['total']} +{N_CELLS} -> {led['total']}")

    with open(PREREG, "rb") as fh:
        prereg_sha = hashlib.sha256(fh.read().replace(
            b"\r\n", b"\n")).hexdigest()[:16]
    out = cutoff_meta(str(SLEEVE_CUTOFF.date()))
    out.update({
        "batch": "T56-AGGRESSIVE-LAB",
        "order": "O-20260925-1126", "ticket": "T-2026-09-25-56",
        "prereg": "research/AGGRESSIVE_LAB.md",
        "prereg_sha256_lf": prereg_sha,
        "roster": list(ROSTER),
        "corps": {"offense": list(OFFENSE_CORPS),
                  "oscillation": list(OSCILLATION_CORPS),
                  "air_defense": [], "pending_zero_weight":
                      list(PENDING_CORPS)},
        "variants": out_variants,
        "canon_verification_face": "AGGR-NOCASH blend face == B_MAXDIV "
            "canon (weights sha 9b112d51583aeeb7 verbatim; execution-layer "
            "delta = paper risk-budget fields only)",
        "variant_daily_ret_corr": corr,
        "trials_ledger": led,
        "adoption": "ZERO wiring this batch (dual-track supply face; "
                    "month-boundary tournament entry per ticket (e))",
        "paper_wiring_slice2_design": {
            "accounts": list(VARIANTS), "initial_cash_cny": 1_000_000,
            "guard": "shadow",
            "risk_budget_fields": {"position_cap": {"AGGR-NOCASH": 0.95,
                                                    "default": 0.80},
                                   "cash_parking_leg": {"AGGR-NOCASH":
                                                        "disabled",
                                                        "default": "paper "
                                                        "plane structurally "
                                                        "no parking leg "
                                                        "(T-09 note)"},
                                   "experimental": True},
            "marks": "daily blend accrual, sleeve domain advances with "
                     "new bars", "s6_whitelist_pattern": "PROS-* precedent"},
        "audit": {"runtime_sec": round(time.time() - t0, 1),
                  "machine": "bm-a",
                  "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
                  "sleeve_cutoff": str(SLEEVE_CUTOFF.date()),
                  "workers": min(worker_cap(), 25),
                  "shard": f"{shard}/{shards}"},
    })
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, default=float)
    log(f"outputs: {OUT_JSON}")

    # -- gate_attrition row
    try:
        ga = json.load(open(GA_PATH, encoding="utf-8"))
        ga["entries"].append({
            "batch": "T56-AGGRESSIVE-LAB",
            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "kind": "aggressive-lab (candidate supply, dual-track)",
            "cells_ledger_delta": N_CELLS,
            "ledger_total_after": led["total"],
            "gates": {v: out_variants[v]["judgments"] for v in VARIANTS},
            "eliminated": None,
            "refs": {"results": OUT_JSON, "prereg": PREREG}})
        with open(GA_PATH, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(ga, fh, ensure_ascii=False, indent=1)
    except FileNotFoundError:
        log("gate_attrition.json absent -- skipped (disclosed)")
    return 0


# ------------------------------------------------- slice-2: paper marks
def _accrue_marks(pr: pd.Series, start: pd.Timestamp, initial: float):
    """Deterministic daily blend accrual from `start` (inclusive) over the
    blend daily-return series. Internal equity stays unrounded; outputs
    round for display only (r163 rounding-face law). Returns (marks, eq)."""
    seg = pr[pr.index >= start]
    eq, marks = initial, []
    for d, r in seg.items():
        eq *= 1.0 + float(r)
        marks.append({"date": str(pd.Timestamp(d).date()),
                     "daily_ret": round(float(r), 8),
                     "equity_cny": round(eq, 2)})
    return marks, eq


def _marks_dd(marks: list, initial: float) -> float:
    """Peak-to-trough drawdown over the marked equity path (initial point
    included). 0.0 when no marks yet (honest zero, not None)."""
    peak, eq = initial, initial
    dd = 0.0
    for m in marks:
        eq = m["equity_cny"]
        peak = max(peak, eq)
        dd = min(dd, eq / peak - 1.0)
    return round(dd, 6)


def _variant_daily_rets(faces, sleeves, states):
    """Blend daily-return series per variant over the ADVANCING sleeve
    domain (slice-2: no truncation -- sleeve domain advances with new
    bars, prereg s6). Static faces via _blend_daily_ret; REGIME via
    _regime_blend (v3 raw states, causal shift(1))."""
    rets = {}
    for name in VARIANTS:
        face = faces[name]
        if "static" in face:
            rets[name] = _blend_daily_ret(
                {t: sleeves[t]["x1"] for t in ROSTER}, face["static"])
        else:
            rets[name], _ = _regime_blend(
                sleeves, face["regime"]["offensive"],
                face["regime"]["defensive"], states)
    return rets


def _paper_state_path(variant: str) -> str:
    return os.path.join(AGGR_DIR, f"{variant}_paper.json")


def run_family_batch() -> int:
    """T-58 s2/s4 family judgment bench: 15 variants x 20 T-28-caliber
    cells (W-CUR 2 + W-SEG 6 + W-GRID 12) = 300 aggregate cells -> ledger.
    Sleeve block duplicated from run_batch deliberately (keeps the frozen
    T-56 path byte-stable for month-boundary reruns)."""
    t0 = time.time()
    log("=== T58-AGGR-FAMILY (prereg frozen pre-run, R162) ===")
    faces, sha_checks = build_family_weights()
    log(f"family weight sha gates PASS ({len(sha_checks)} entries)")

    with open(TOURN_JSON, encoding="utf-8") as fh:
        tour = json.load(fh)
    w_canon = dict(tour["weights"]["B_MAXDIV"]["weights"])
    if w_sha(w_canon) != FROZEN_SHA["AGGR-NOCASH"]:
        raise SystemExit("CANON GATE FAIL: B_MAXDIV vector sha drift")

    # -- sleeves: 28 members x {x1,x2} (T-56 caliber, ledger +0)
    prices_full = load_core()
    cutoff = max(df.index.max() for df in prices_full.values())
    if cutoff < SLEEVE_CUTOFF:
        raise SystemExit(f"PANEL GATE FAIL: cutoff {cutoff.date()} < "
                         f"{SLEEVE_CUTOFF.date()}")
    prices = {s: df[df.index <= SLEEVE_CUTOFF]
              for s, df in prices_full.items()}
    jobs = [(tid, mult, prices, SLEEVE_CUTOFF) for tid in ROSTER
            for mult in (None, 2.0)]
    res = run_cells_parallel(
        [(f"{a[0]}|{a[1] or 'x1'}", _sleeve_worker, a) for a in jobs],
        workers=min(worker_cap(), 25), desc="fam-sleeves")
    sleeves = {}
    for tid in ROSTER:
        r1, r2 = res[f"{tid}|x1"], res[f"{tid}|2.0"]
        for r in (r1, r2):
            r["eq_s"] = pd.Series(r["eq"], index=pd.to_datetime(r["dates"]))
        sleeves[tid] = {"x1": r1, "x2": r2}
    log(f"sleeves: {len(sleeves)} members x 2 faces ({time.time()-t0:.0f}s)")

    states = v3_state_series()
    lt, lp = _load_legacy_grid()
    dt, dp = _load_deep_grid()
    sharpe_map = _oos_sharpe_map()

    # canon B_MAXDIV re-derive verification leg (ledger +0, T-56 precedent)
    canon_pr1 = _blend_daily_ret(
        {t: sleeves[t]["x1"] for t in ROSTER}, w_canon)
    canon_bull = _seg_classes(canon_pr1, states)["bull"]["cum_ret"]

    out_variants, corr_inputs = {}, {"CANON-B_MAXDIV": canon_pr1}
    for name in FAM_VARIANTS:
        face = faces[name]
        sl1 = {t: sleeves[t]["x1"] for t in ROSTER}
        sl2 = {t: sleeves[t]["x2"] for t in ROSTER}
        if "static" in face:
            w = face["static"]
            pr1 = _blend_daily_ret(sl1, w)
            pr2 = _blend_daily_ret(sl2, w)
            rep_w = dict(w)
            w_src, legs_sha, w_sha_rec = "static", None, sha_checks[name]
        elif "legs" in face:
            pr1, rep_w, W = _legs_blend(sleeves, face["legs"],
                                        face["gate"], states)
            R2 = daily_ret_matrix(sleeves, "x2")
            if not R2.index.equals(W.index):
                raise SystemExit("LEGS GATE FAIL: x2 index drift")
            pr2 = (R2 * W).sum(axis=1)
            w_src = "legs_v3"
            legs_sha = {k: sha_checks[f"{name}-{k}"]
                        for k in face["legs"]}
            w_sha_rec = legs_sha["off"]
        else:
            pr1, rep_w, W = _rotation_blend(sleeves, face["rotation"]["kind"],
                                            face["rotation"]["lookback"],
                                            sharpe_map)
            R2 = daily_ret_matrix(sleeves, "x2")
            if not R2.index.equals(W.index):
                raise SystemExit("ROTATION GATE FAIL: x2 index drift")
            pr2 = (R2 * W).sum(axis=1)
            w_src = f"rotation_{face['rotation']['kind']}"
            legs_sha = None
            w_sha_rec = sha_checks[f"{name}-rule"]

        wcur = {"x1": _window_face(pr1, W_CUR_START, W_CUR_END),
                "x2": _window_face(pr2, W_CUR_START, W_CUR_END)}
        wseg = {f: _seg_classes(pr, states) for f, pr in
                (("x1", pr1), ("x2", pr2))}
        j1 = bool(wcur["x1"]["ret"] > 0 and abs(wcur["x1"]["dd"]) <= 0.05)
        j2 = bool(wcur["x2"]["ret"] > 0)
        j3 = all((wseg[f][c]["cum_ret"] is not None
                  and wseg[f][c]["cum_ret"] >= -0.05)
                 for f in ("x1", "x2") for c in ("bull", "chop", "bear"))

        w_ce = _ce6_restrict(rep_w)
        grid = {}
        for axis, tret, passive in (("legacy", lt, lp), ("deep", dt, dp)):
            for window in WINDOWS:
                for fce in ("x1", "x2"):
                    grid[f"{axis}|{window}|{fce}"] = _grid_unit(
                        tret, passive, w_ce, CE6, window, fce)
        n12 = grid["legacy|12m|x1"]["n"] + grid["deep|12m|x1"]["n"]
        k12 = grid["legacy|12m|x1"]["beats"] + grid["deep|12m|x1"]["beats"]

        dr = {"median": round(float(pr1.median()), 6),
              "p999": round(float(pr1.quantile(0.999)), 6)}
        out_variants[name] = {
            "weights_src": w_src, "weights_sha": w_sha_rec,
            "legs_or_rule_sha": legs_sha,
            "weights_representative": {k: v for k, v in rep_w.items()
                                       if v > 0},
            "grid_ce6_restricted": w_ce, "w_cur": wcur, "w_seg": wseg,
            "judgments": {"J1_current_window_profit": j1,
                          "J2_x2_survival": j2,
                          "J3_regime_segment_stability": j3},
            "daily_ret_faces_x1": dr, "w_grid": grid,
            "grid_12m_pooled": {"n": n12, "beats": k12,
                                "rate": round(k12 / n12, 4) if n12 else None},
            "kpi": {"return_ceiling_w_cur_x1": wcur["x1"]["ret"],
                    "bull_delta_vs_canon": round(
                        wseg["x1"]["bull"]["cum_ret"] - canon_bull, 6),
                    "note": "KPI = ceiling + bull delta vs canon B_MAXDIV "
                            "(ticket s4); promotion count NOT the KPI; "
                            "expected J2/J3 breaches = honest outcomes"},
        }
        corr_inputs[name] = pr1
        log(f"{name}: J1={j1} J2={j2} J3={j3} "
            f"W-CUR x1 ret={wcur['x1']['ret']} dd={wcur['x1']['dd']} "
            f"12m pooled={k12}/{n12}")

    cdf = pd.DataFrame(corr_inputs).dropna()
    corr = {a: {b: round(float(cdf[a].corr(cdf[b])), 4)
               for b in cdf.columns} for a in cdf.columns}

    head = ledger_head()
    led = append_ledger("T58-AGGR-FAMILY", FAM_N_CELLS,
                        os.path.basename(FAM_OUT_JSON),
                        note="300 aggregate judgment cells (15 aggressive "
                             "family variants x 20 T-28-caliber cells: "
                             "W-CUR 2 + W-SEG 6 + W-GRID 12); W-GRID per-cell "
                             "N follows P5C/t22 already-counted ledgers, no "
                             "recount; 56 sleeves = T-27-machinery "
                             "reproductions o1600 caliber, ledger +0; canon "
                             "B_MAXDIV re-derive = verification leg +0; "
                             "zero adoption zero wiring (dual-track)",
                        evidence_cutoff=str(SLEEVE_CUTOFF.date()),
                        prev_total=head["total"])
    log(f"ledger: prev={head['total']} +{FAM_N_CELLS} -> {led['total']}")

    with open(PREREG_FAMILY, "rb") as fh:
        prereg_sha = hashlib.sha256(fh.read().replace(
            b"\r\n", b"\n")).hexdigest()[:16]
    out = cutoff_meta(str(SLEEVE_CUTOFF.date()))
    out.update({
        "batch": "T58-AGGR-FAMILY",
        "order": "O-20260925-1138", "ticket": "T-2026-09-25-58",
        "prereg": "research/AGGR_FAMILY_PREREG.md",
        "prereg_sha256_lf": prereg_sha,
        "roster": list(ROSTER),
        "corps": {"offense": list(OFFENSE_CORPS),
                  "oscillation": list(OSCILLATION_CORPS),
                  "air_defense": [], "pending_zero_weight":
                      list(PENDING_CORPS)},
        "selection_basis": "registered OOS Sharpe (firm/traders registry), "
                           "cherry face honestly acknowledged (T-56 s3 "
                           "precedent; purpose = ceiling test)",
        "variants": out_variants,
        "canon_verification_face": "B_MAXDIV blend re-derived "
            "(weights sha 9b112d51583aeeb7 verbatim; ledger +0)",
        "variant_daily_ret_corr": corr,
        "trials_ledger": led,
        "adoption": "ZERO wiring this batch (dual-track supply face; "
                    "month-boundary T-27 tournament entry per ticket s4)",
        "audit": {"runtime_sec": round(time.time() - t0, 1),
                  "machine": "bm-a",
                  "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
                  "sleeve_cutoff": str(SLEEVE_CUTOFF.date()),
                  "workers": min(worker_cap(), 25)},
    })
    with open(FAM_OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, default=float)
    log(f"outputs: {FAM_OUT_JSON}")

    try:
        ga = json.load(open(GA_PATH, encoding="utf-8"))
        ga["entries"].append({
            "batch": "T58-AGGR-FAMILY",
            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "kind": "aggressive-family (candidate supply, dual-track)",
            "cells_ledger_delta": FAM_N_CELLS,
            "ledger_total_after": led["total"],
            "gates": {v: o["judgments"] for v, o in out_variants.items()},
        })
        with open(GA_PATH, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(ga, fh, ensure_ascii=False, indent=1)
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        log(f"gate_attrition append skipped: {exc}")
    return 0


def cmd_paper() -> int:
    """T-56 slice-2 (ticket deliverable (d), prereg s6 frozen): 5 paper
    accounts AGGR-* -- initial CNY 1,000,000 each, shadow guard (record
    only, zero interference, zero canon touch), experimental risk budget
    fields declared per account, marks = daily blend accrual with the
    sleeve domain advancing on new bars. PROS-* whitelist paradigm: own
    lane results/aggr_paper/, NOT consumed by t35/scorecard CEO faces.
    Marks are not trials -> ledger +0, SEED_REGISTRY +0."""
    try:
        faces, sha_checks, _ = build_weights()      # sha gates re-verified
        prices_full = load_core()
        cutoff = max(df.index.max() for df in prices_full.values())
        if cutoff < PAPER_START:
            print(f"aggr paper: no markable bar yet (panel cutoff "
                  f"{cutoff.date()} < paper_start {PAPER_START.date()}) "
                  f"-- no-op")
            return 0
        state_path = _paper_state_path(VARIANTS[0])
        if os.path.exists(state_path):
            prev = json.load(open(state_path, encoding="utf-8-sig"))
            if prev.get("panel_cutoff") == str(cutoff.date()):
                print(f"aggr paper: marks already at panel cutoff "
                      f"{cutoff.date()} -- no-op (idempotent)")
                return 0

        jobs = [(tid, None, prices_full, cutoff) for tid in ROSTER]
        res = run_cells_parallel(
            [(f"{a[0]}|x1", _sleeve_worker, a) for a in jobs],
            workers=min(worker_cap(), 25), desc="aggr-paper-sleeves")
        sleeves = {}
        for tid in ROSTER:
            r = res[f"{tid}|x1"]
            r["eq_s"] = pd.Series(r["eq"], index=pd.to_datetime(r["dates"]))
            sleeves[tid] = {"x1": r}
        states = v3_state_series()
        rets = _variant_daily_rets(faces, sleeves, states)

        os.makedirs(AGGR_DIR, exist_ok=True)
        summary = {}
        for name in VARIANTS:
            marks, eq = _accrue_marks(rets[name], PAPER_START, INITIAL_CNY)
            bud = RISK_BUDGET.get(name, {})
            st = {
                "schema": "t56_aggr_paper_v1",
                "account": name, "variant": name,
                "lane": "experimental-aggressive (T-56 slice-2, ticket "
                        "(d), order O-20260925-1126)",
                "whitelist_paradigm": "PROS-* precedent: own lane dir; "
                    "excluded from t35 paper_export and daily_scorecard "
                    "CEO faces by construction",
                "guard": "shadow (record-only; zero interference; zero "
                         "canon/production-account touch)",
                "experimental": True,
                "initial_cash_cny": INITIAL_CNY,
                "denomination": "CNY",
                "paper_start": str(PAPER_START.date()),
                "paper_start_rationale": "first bar strictly after the "
                    "frozen judgment domain evidence_cutoff 2026-09-23 "
                    "(blind forward; prereg s2/s6)",
                "evidence_cutoff": str(SLEEVE_CUTOFF.date()),
                "weights_sha": (sha_checks.get(name) if name
                                != "AGGR-REGIME" else {
                                    "offensive": FROZEN_SHA[
                                        "AGGR-REGIME-offensive"],
                                    "defensive": FROZEN_SHA[
                                        "AGGR-REGIME-defensive"]}),
                "risk_budget": {
                    "position_cap": bud.get("position_cap", 0.80),
                    "position_cap_note": "0.80 production-aligned default;"
                        " AGGR-NOCASH 0.95 per prereg s6",
                    "cash_parking_leg": bud.get(
                        "cash_parking_leg",
                        "paper plane structurally no parking leg "
                        "(T-09 unwired disclosure, live-side watch item)"),
                    "experimental": True,
                    "execution_layer_note": "marks are the blend-face "
                        "measurement; cap/cash fields are declared budget "
                        "parameters, not modeled in blend marks",
                },
                "cost_face": "x1 (13bp production-aligned; x2 is a "
                             "judgment-batch stress face only)",
                "marks": marks,
                "marks_summary": {
                    "bars": len(marks),
                    "first_date": marks[0]["date"] if marks else None,
                    "last_date": marks[-1]["date"] if marks else None,
                    "cumulative_ret": round(
                        eq / INITIAL_CNY - 1.0, 8),
                    "current_dd": _marks_dd(marks, INITIAL_CNY),
                },
                "equity_cny": round(eq, 2),
                "panel_cutoff": str(cutoff.date()),
                "updated": time.strftime("%Y-%m-%d %H:%M:%S"),
                "audit": {"network": "zero", "ledger_trials_added": 0,
                          "seed_registry_added": 0,
                          "engine_runs": len(ROSTER),
                          "adoption": "ZERO (dual-track supply face)"},
            }
            tmp = _paper_state_path(name) + ".tmp"
            with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(st, fh, ensure_ascii=False, indent=1)
            os.replace(tmp, _paper_state_path(name))
            s = st["marks_summary"]
            summary[name] = s
            print(f"aggr paper {name}: bars={s['bars']} "
                  f"last={s['last_date']} cum={s['cumulative_ret']} "
                  f"dd={s['current_dd']} equity={st['equity_cny']}")
        print(f"aggr paper: {len(VARIANTS)} accounts marked through "
              f"{cutoff.date()} -> {AGGR_DIR}")
        return 0
    except SystemExit as e:
        print(f"aggr paper mechanism fault (gate): {e}")
        return 2
    except Exception as e:                       # noqa: BLE001
        print(f"aggr paper mechanism fault: {e}")
        return 2


# ------------------------------------------------------------- selftest
def cmd_selftest() -> int:
    ok = []

    def check(name, cond):
        ok.append((name, bool(cond)))
        print(("PASS " if cond else "FAIL ") + name)

    # F1 constructed-vector sha gates vs prereg freeze (no data needed)
    try:
        faces, checks, _ = build_weights()
        check("F1 weight sha gates (6 vectors)", True)
    except SystemExit as e:
        check(f"F1 weight sha gates -> {e}", False)
        return 1
    check("F1b corps partition 6+15+7=28 disjoint",
          len(OFFENSE_CORPS) == 6 and len(OSCILLATION_CORPS) == 15
          and len(PENDING_CORPS) == 7
          and set(OFFENSE_CORPS).isdisjoint(OSCILLATION_CORPS)
          and set(OFFENSE_CORPS) | set(OSCILLATION_CORPS)
          | set(PENDING_CORPS) == set(ROSTER))
    w_off = faces["AGGR-OFFENSE"]["static"]
    check("F1c offense budget 70/85 mass on offense corps",
          abs(sum(w_off[t] for t in OFFENSE_CORPS) - 0.823529) < 1e-3)
    check("F1d pending members zero weight",
          all(w_off[t] == 0.0 for t in PENDING_CORPS))

    # F2 static blend math: EW blend == mean of member daily returns
    idx = pd.bdate_range("2026-01-05", periods=40)
    sleeves = {}
    rng = pd.Series([0.001 * (i % 5 - 2) for i in range(40)], index=idx)
    for i, t in enumerate(ROSTER[:4]):
        eq = (1.0 + rng * (1 + 0.01 * i)).cumprod()
        sleeves[t] = {"x1": {"eq_s": eq}, "x2": {"eq_s": eq}}
    w_ew = {t: 0.25 for t in ROSTER[:4]}
    face1 = {t: sleeves[t]["x1"] for t in ROSTER[:4]}
    pr = _blend_daily_ret(face1, w_ew)
    manual = pd.concat([sleeves[t]["x1"]["eq_s"]
                        / sleeves[t]["x1"]["eq_s"].iloc[0]
                        for t in ROSTER[:4]], axis=1).pct_change().mean(axis=1)
    check("F2 static blend == mean(EW)", float(
        (pr - manual).abs().max()) < 1e-12)

    # F3 window face math: constant ret -> compound, zero dd
    wf = _window_face(pd.Series(0.01, index=idx), idx[0], idx[-1])
    check("F3 window face compound math",
          abs(wf["ret"] - (1.01 ** 40 - 1)) < 1e-5 and abs(wf["dd"]) < 1e-12)

    # F4 regime causality: state(t-1) drives day t; first R row offensive

    states = pd.Series(["ORANGE"] * 40, index=idx)

    states.iloc[10] = "GREEN"                 # day 10 GREEN

    off = {t: (1.0 if t == ROSTER[0] else 0.0) for t in ROSTER[:4]}

    defw = {t: 0.25 for t in ROSTER[:4]}

    pr, w_mean = _regime_blend(sleeves, off, defw, states)

    manual = pd.concat({t: sleeves[t]["x1"]["eq_s"]

                        / sleeves[t]["x1"]["eq_s"].iloc[0]

                        for t in ROSTER[:4]}, axis=1).pct_change().dropna()

    off_day = manual[ROSTER[0]]               # concentrated offense leg

    def_day = manual.mean(axis=1)             # EW defensive leg

    # daily_ret_matrix drops the first NaN row: R rows = idx[1:]

    check("F4 first-day offensive default",

          abs(pr.iloc[0] - off_day.iloc[0]) < 1e-12)

    check("F4 ORANGE->defensive with 1-day lag",

          abs(pr.loc[idx[5]] - def_day.loc[idx[5]]) < 1e-12)

    check("F4 GREEN(t-1)->offensive(t)",

          abs(pr.loc[idx[11]] - off_day.loc[idx[11]]) < 1e-12)

    # F5 CE-6 restriction renormalizes to 1
    w_ce = _ce6_restrict(w_off)
    check("F5 CE6 restriction sums to 1", abs(sum(w_ce.values()) - 1) < 1e-6
          and set(w_ce) == set(CE6))

    # F6 sha mismatch -> gate fires (negative test)
    global FROZEN_SHA
    saved = dict(FROZEN_SHA)
    try:
        FROZEN_SHA["AGGR-CONC-TOP2"] = "deadbeefdeadbeef"
        build_weights()
        check("F6 sha gate fires on mismatch", False)
    except SystemExit:
        check("F6 sha gate fires on mismatch", True)
    finally:
        FROZEN_SHA = saved

    # F7 slice-2 accrual math: equity product over synthetic returns
    # (fixture values built at construction -- r139 CoW law)
    idx7 = pd.bdate_range("2026-09-24", periods=3)
    pr7 = pd.Series([0.01, -0.02, 0.03], index=idx7)
    marks7, eq7 = _accrue_marks(pr7, PAPER_START, INITIAL_CNY)
    want_eq = INITIAL_CNY * 1.01 * 0.98 * 1.03
    check("F7 accrual equity product + unrounded chain",
          abs(eq7 - want_eq) < 1e-6 and len(marks7) == 3
          and abs(marks7[0]["equity_cny"]
                  - round(INITIAL_CNY * 1.01, 2)) < 0.01)

    # F8 accrual start gate: pre-paper_start rows never marked
    idx8 = pd.bdate_range("2026-09-20", periods=6)
    pr8 = pd.Series([0.01] * 6, index=idx8)
    marks8, _ = _accrue_marks(pr8, PAPER_START, INITIAL_CNY)
    check("F8 marks start strictly after evidence cutoff",
          all(m["date"] >= str(PAPER_START.date()) for m in marks8)
          and len(marks8) == len([d for d in idx8
                                  if d >= PAPER_START]))

    # F9 marks dd math: peak-to-trough over marked path
    marks9 = [{"equity_cny": 1_010_000.0},
              {"equity_cny": 980_000.0},
              {"equity_cny": 1_005_000.0}]
    check("F9 marks dd peak-to-trough",
          abs(_marks_dd(marks9, INITIAL_CNY) - (980_000.0
                                                 / 1_010_000.0 - 1.0))
          < 1e-6 and _marks_dd([], INITIAL_CNY) == 0.0)

    # F10 risk-budget fields per frozen design (NOCASH 0.95/disabled,
    # others 0.80 production-aligned default)
    check("F10 risk budget frozen fields",
          RISK_BUDGET["AGGR-NOCASH"]["position_cap"] == 0.95
          and RISK_BUDGET["AGGR-NOCASH"]["cash_parking_leg"] == "disabled"
          and all(v not in RISK_BUDGET for v in VARIANTS
                  if v != "AGGR-NOCASH"))

    # F11 paper lane path + start-date gate constants
    check("F11 paper lane constants",
          AGGR_DIR.endswith("aggr_paper")
          and PAPER_START == pd.Timestamp("2026-09-23") + pd.Timedelta(
              days=1) and INITIAL_CNY == 1_000_000.0)

    # F12 family vector sha gates vs prereg freeze (no data needed)
    try:
        fam_faces, fam_checks = build_family_weights()
        check("F12 family sha gates (19 entries)", True)
    except SystemExit as e:
        check(f"F12 family sha gates -> {e}", False)
        return 1
    check("F12b family count 15 + six-axis coverage",
          len(FAM_VARIANTS) == 15
          and len(fam_faces) == 15 and len(fam_checks) == 19)

    # F13 cash-leg no-renorm: sum<1 weights -> cash remainder stays
    w_c80 = fam_faces["AGGR-TOP2-C80"]["static"]
    r13 = pd.Series([0.01, -0.02, 0.03], index=pd.bdate_range(
        "2026-01-05", periods=3))
    sl13 = {t: {"x1": {"eq_s": (1.0 + r13 * (1 + 0.01 * i)).cumprod()},
                "x2": {"eq_s": (1.0 + r13 * (1 + 0.01 * i)).cumprod()}}
            for i, t in enumerate(ROSTER[:2])}
    check("F13 cash-leg vector sums to 0.8",
          abs(sum(w_c80.values()) - 0.8) < 1e-9)
    pr13 = _blend_daily_ret({t: sl13[t]["x1"] for t in ROSTER[:2]},
                            {t: w_c80[t] for t in ROSTER[:2]})
    manual13 = sum(w_c80[t] * (sl13[t]["x1"]["eq_s"].pct_change()
                               - 0.0) for t in ROSTER[:2])
    check("F13b blend keeps cash remainder (no renorm)",
          float((pr13 - manual13).abs().max()) < 1e-12)

    # F14 legs-frame causality: 3-leg gate, state(t-1) drives day t
    states14 = pd.Series(["ORANGE"] * 40, index=idx)
    states14.iloc[10] = "GREEN"
    legs14 = {"off": {t: (1.0 if t == ROSTER[0] else 0.0)
                      for t in ROSTER[:4]},
              "osc": {t: (0.5 if t == ROSTER[1] else 0.0)
                      for t in ROSTER[:4]},
              "def": {t: 0.25 for t in ROSTER[:4]}}
    gate14 = {"GREEN": "off", "YELLOW": "off", "ORANGE": "osc", "RED": "def"}
    pr14, w14m, _ = _legs_blend(sleeves, legs14, gate14, states14)
    m14 = pd.concat({t: sleeves[t]["x1"]["eq_s"]
                     / sleeves[t]["x1"]["eq_s"].iloc[0]
                     for t in ROSTER[:4]}, axis=1).pct_change().dropna()
    off14 = m14[ROSTER[0]]
    osc14 = m14[ROSTER[1]] * 0.5
    def14 = m14.mean(axis=1)
    check("F14 3-leg gate: first-day GREEN default -> off leg",
          abs(pr14.iloc[0] - off14.iloc[0]) < 1e-12)
    check("F14b ORANGE(t-1)->osc leg(t)", abs(
        pr14.loc[idx[5]] - osc14.loc[idx[5]]) < 1e-12)
    check("F14c GREEN(t-1)->off leg(t)", abs(
        pr14.loc[idx[11]] - off14.loc[idx[11]]) < 1e-12)

    # F15 rotation warmup + forward lock (synthetic flat panel)
    idx15 = pd.bdate_range("2026-01-05", periods=140)
    flat = pd.Series(0.001, index=idx15)
    fam3 = ("COMPOSITE-CE-01", "VOLATILITY-CE-01", "DROUGHT-CE-01")
    sl15 = {}
    for i, t in enumerate(fam3):
        eq = (1.0 + flat * (1 + 0.05 * i)).cumprod()   # member 3 best
        sl15[t] = {"x1": {"eq_s": eq}, "x2": {"eq_s": eq}}
    pr15, w15m, W15 = _rotation_blend(sl15, "month", 63,
                                      {t: 1.0 for t in fam3})
    # warmup: first 63 rows -> frozen fallback names (both in fixture)
    check("F15 warmup uses frozen fallback (0.5/0.5 top2-of-roster)",
          abs(W15.iloc[0]["COMPOSITE-CE-01"] - 0.5) < 1e-12
          and abs(W15.iloc[0]["VOLATILITY-CE-01"] - 0.5) < 1e-12)
    # forward lock: after boundary >63 rows, top-by-trailing = members 2/3
    late = W15.iloc[-1]
    check("F15b post-warmup selection = best trailing member",
          abs(late["DROUGHT-CE-01"] - 0.5) < 1e-12
          and abs(late["VOLATILITY-CE-01"] - 0.5) < 1e-12
          and late["COMPOSITE-CE-01"] < 1e-12)

    n_fail = sum(1 for _, c in ok if not c)
    print(f"selftest: {len(ok) - n_fail}/{len(ok)} PASS")
    return 0 if n_fail == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", choices=("run", "paper", "family", "selftest"))
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--shards", type=int, default=1)
    a = ap.parse_args()
    if a.cmd == "selftest":
        return cmd_selftest()
    if a.cmd == "paper":
        return cmd_paper()
    if a.cmd == "family":
        return run_family_batch()
    return run_batch(shard=a.shard, shards=a.shards)


if __name__ == "__main__":
    raise SystemExit(main())
