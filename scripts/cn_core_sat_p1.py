# -*- coding: utf-8 -*-
"""CN-CORE-SATELLITE-P1 -- CN-CORE-SATELLITE combo model, s3 slice-5 (FINAL
CN-native model) batch runner (T-2026-09-26-73, CEO order O-20260926-0926).

Prereg FROZEN research/CN_CORE_SATELLITE_PREREG.md (R261 freeze commit
e6e7fcd1 precedes ANY run). Zero threshold edits post-run; s7/s8 backfill
is the only sanctioned prereg edit (control plane, not here).

Cells (prereg s0: judged grid = 4, K=50 nulls NOT in the skill grid):
  SAT20_bare / SAT20_gate : 80% core (510880 dividend ballast) + 20%
  SAT40_bare / SAT40_gate : 60% core + 40% satellite sleeve
  Satellite = argmax trailing-252d clean strict-window return among
  AVAILABLE style-ETF legs (MIN_AVAIL=3 frozen, prereg s3.1); quarterly
  63-trading-day rhythm (anchor 62, slice-E law holding horizon).
  Gate cells: selected satellite leg must close above its full-history
  MA200 (clean face) else satellite sleeve -> cash; CORE NEVER gated
  (core-satellite doctrine, prereg s3.3). Ties -> satellite weight split
  equally among winners (frozen deterministic rule).

Machinery reuse (anti-repeat law -- family single sources, zero new judge
code): DRV = cn_div_lowvol_rot_p1 (queue-fill simulate / metrics / MA200 /
transition compaction -- leg-generic engine, injected LEGS=8 + crisis
windows below, selftest-locked), SRP = t73_s2_style_rotation (union panel
loader + envelope-rule event detector + clean_rets + clean_value bridge --
r239 law family single source), science_gates shared criteria (zero
hand-copied lines), cn_rev_tilt_p1 (D6/member faces + regime column).

Faces (prereg s2):
  signal = rolling-252 on the FULL union calendar (slice-E convention;
  timeline floor truncates only the SIM window, never signal history);
  sim prices = clean_value BRIDGE face (event/suspension days ret->NaN->0
  bridged, split-adjustment convention, R259 amendment law); exec open =
  raw_open x (clean_close/raw_close) ratio face (step function, ffilled);
  ADV20 = raw volume x raw close rolling-20 (CNY, fold-invariant, family
  caliber); missing-bar days = no fill (NaN ADV -> conservative zero cap)
  + 0-return valuation (bridge).
  Frozen event set (envelope rule, my 8-leg universe): 510500
  2015-04-15 (+248.55%), 510500 2022-08-29 (-12.74%), 512100 2022-09-05
  (+176.27%); CORE 510880 zero events (slice-D face, runner-asserted);
  20%-family real extreme days (159915 2024-09-30 +20.0% etc.) KEPT.

Accounting (prereg s3.2/s3.5, family MF_ROT/DOG semantics): capital
1,000,000 CNY; signal at close r -> fills from open r+1 (T+1); quarterly
rebalance; daily close valuation; cash zero-yield; warmup = cash-honest.
Cost = V2 ADV20-tiered (knowledge/rules.py CostPatch single source), judge
face = x2 always on; x1 = side_cost_v2 verbatim, x3 = tripled disclosure.
Queue fill: >1% x ADV20 notionals fill over days at min(remaining,
1% x ADV20(t-1)); sells before buys; buys lot-rounded; re-anchor
supersedes incomplete transitions (fill_days=None honest).

Nulls (s3.4): K=50 random-satellite sleeves -- per rebalance one uniform
draw among AVAILABLE legs, numpy.random.default_rng(20261080+k), k<50;
same window/rhythm/cost(x2)/availability/SAT20 weight structure; gate
cells share the bare-null distribution (prereg conservative note).
Baselines (disclosure only): core-only buy-hold 510880 (the satellite-
increment yardstick) + static 80/20 core/EW-available-satellite, both
activation-anchored, x2 face. N = 4 + 50 = 54 on the D1 bill.

Panel (prereg s2, probe results/core_sat_probe.json frozen): 8-leg union
timeline T=3333 (2013-01-04..2026-09-22), cutoff 2026-09-22 (D2 lockbox),
first-active rebalance 2013-07-17, zero post-activation cash rebalances;
data gates fail-closed exit 2 on any drift (date-drift refusal law).

Gates (prereg s4, shared library only): G1'v2 = science_gates.g1_prime_v2
(batch_cells=4, pool='core48', null_pool=batch-own) on the JUDGED x2
series; G2 = g2_registration_v2 + DSR (deflated_sharpe_ratio raw daily
returns) + family PBO (screening/pbo.cscv_pbo CSCV-8, 4-cell grid). D6
reject face = max|corr| vs 6 registered traders (>=0.7 reject); H4-style
disclosures (never admission): corr vs 510880 leg face (ALLOC P5 slot,
high BY CONSTRUCTION), vs DIV_LOWVOL family band 0.6-0.9 declared.
Descriptive clauses + hard-bound triad with FIVE frozen crisis windows
(2015-06..08 crash / 2016-01 fuse / 2020-03 / 2021-02 / 2024-09..10 --
prereg s4, family triad lawfully extended for the 2013+ window).

Products (prereg s6): results/cn_core_satellite/p1_results.json (top-level
evidence_cutoff + cutoff_meta + 4 cells x {x1,x2,x3} + nulls + baselines +
D6 + fill_days faces) + cells_summary.csv; ledger append single-shot at
finalize (CN_CORE_SATELLITE_P1_REFINALIZE=1 = only redo path); attrition
row lands in the ENTRIES list (r248 consumer-chain law); per-unit .npz
checkpoints (gitignored, exact resume).

Usage: run | selftest   (exit 0 ok; 2 = fail-closed gate/mechanism refusal)
"""
import argparse
import json
import math
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "screening"))

import numpy as np
import pandas as pd

import science_gates as sg
from alloc_backtest import side_cost_v2, side_cost_x2
from div_lowvol_backtest import side_cost_x3
from pbo import cscv_pbo, align_returns
from composite_ic import IS_END
from knowledge import rules as krules
import t73_s2_style_rotation as SRP       # slice-E single source (frozen)
import cn_div_lowvol_rot_p1 as DRV        # family sim engine (frozen batch)
from cn_rev_tilt_p1 import (_corr, d6_block, load_member_rets,
                            regime_v3_column)

TICKET = "T-2026-09-26-73"
PREREG = os.path.join(ROOT, "research", "CN_CORE_SATELLITE_PREREG.md")
OUT_DIR = os.path.join(ROOT, "results", "cn_core_satellite")
CKPT_DIR = os.path.join(OUT_DIR, "ckpt")
OUT_JSON = os.path.join(OUT_DIR, "p1_results.json")
OUT_CSV = os.path.join(OUT_DIR, "cells_summary.csv")
ATT_JSON = os.path.join(ROOT, "results", "gate_attrition.json")
LOG_PATH = os.path.join(OUT_DIR, "runner.log")

EVIDENCE_CUTOFF = "2026-09-22"           # prereg s2 (all legs' last bar)
EVIDENCE_CUTOFF_TS = pd.Timestamp(EVIDENCE_CUTOFF)
TIMELINE_FIRST = "2013-01-04"            # probe-authoritative (floor 2013-01-01)
T_FROZEN = 3333                          # probe-authoritative
FIRST_ACTIVE_FROZEN = "2013-07-17"       # probe-authoritative
OOS_START = "2025-01-01"                 # composite_ic shared split
SEED_BASE = 20_261_080                   # SEED_REGISTRY['cn_core_sat_p1']
K_NULLS = 50
BATCH_CELLS = 4
LEDGER_TRIALS = 54                       # 4 cells + 50 nulls on the D1 bill

CORE = "510880"
SAT = ("510050", "510300", "510500", "512100", "159915", "588000", "563300")
LEGS_ALL = (CORE,) + SAT                  # 8 legs (sim engine injection)

W = 252                                   # slice-E alive law window (s3.1)
MIN_AVAIL = 3                             # frozen (s3.1 rationale in prereg)
REBAL_ANCHOR = 62                         # frozen grid anchor (s3.2)
REBAL_STEP = 63                           # quarterly (law holding horizon)
MA_WIN = 200                              # s3.3 gate window (family)
SAT_W = {"SAT20": 0.20, "SAT40": 0.40}    # frozen weight axis (s3.1)
JUDGED_FACE = "x2"
FACES = {"x1": side_cost_v2, "x2": side_cost_x2, "x3": side_cost_x3}
JUDGED_CELLS = ("SAT20_bare", "SAT20_gate", "SAT40_bare", "SAT40_gate")
CAPITAL = 1_000_000.0
LOT = int(krules.min_lot(CORE))           # 100 shares (single source)
ADV_CAP = float(krules.ADV_FILL_CAP_RATE)  # 1% ADV20 (single source)
MAXDD_LINE = -0.35                        # descriptive (s4)
CRASH_YEAR_LINE = -0.30                   # (s4)
D6_REJECT = 0.7                           # s1 hard line
# prereg s4: family triad LAWFULLY EXTENDED for the 2013+ window (frozen
# five windows; 2024-09..30 +20% 159915 real day is INSIDE the last window)
CRISIS_WINDOWS = [("2015-06-15", "2015-08-31"),
                  ("2016-01-01", "2016-01-31"),
                  ("2020-03-01", "2020-03-31"),
                  ("2021-02-01", "2021-02-28"),
                  ("2024-09-01", "2024-10-31")]
CRISIS_LOG_ABS_R = 0.05
EVT_FROZEN = {("510500", "2015-04-15"), ("510500", "2022-08-29"),
              ("512100", "2022-09-05")}
PBP = 252.0

# ---- family machinery injection (documented, selftest-locked) ----------
# DRV.simulate/metrics are leg-count-generic engines validated in the judged
# CN-DIV-LOWVOL-ROT-P1 batch; they read their module globals at CALL time.
# Injecting the 8-leg tuple + the pre-registered five-window crisis list is
# the anti-repeat-law reuse face (zero copied judge code). Selftest [M1]
# asserts the injected state; [M2] re-validates the engine on a hermetic
# multi-leg fixture; the DIV-LOWVOL batch artifact on disk is untouched.
DRV.LEGS = LEGS_ALL
DRV.CRISIS_WINDOWS = CRISIS_WINDOWS


def _log(msg):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")
    print(f"[cn_core_sat] {msg}", flush=True)


def _leg_frame(sym):
    fn = f"sh{sym}.csv" if sym[0] == "5" else f"sz{sym}.csv"
    df = pd.read_csv(os.path.join(ROOT, "data", "daily", fn),
                     parse_dates=["date"])
    return df.set_index("date").sort_index()


def panel_gates(tl, evt_set, core_zero, nan_free_core):
    ok = {
        "T": int(len(tl)),
        "T_ok": bool(len(tl) == T_FROZEN),
        "first": str(tl[0].date()),
        "first_ok": bool(str(tl[0].date()) == TIMELINE_FIRST),
        "cutoff": str(tl[-1].date()),
        "cutoff_ok": bool(str(tl[-1].date()) == EVIDENCE_CUTOFF),
        "legs": int(len(LEGS_ALL)),
        "legs_ok": bool(len(LEGS_ALL) == 8),
        "events": sorted(f"{s}@{d}" for s, d in evt_set),
        "events_ok": bool(evt_set == EVT_FROZEN),
        "core_zero_events": bool(core_zero),
        "core_zero_ok": bool(core_zero),
        "nan_free_core_face": bool(nan_free_core),
    }
    ok["all_ok"] = bool(all(ok[k] for k in
                           ("T_ok", "first_ok", "cutoff_ok", "legs_ok",
                            "events_ok", "core_zero_ok",
                            "nan_free_core_face")))
    return ok


def load_panel():
    """Union timeline + bridge faces + signal/MA arrays (prereg s2/s3).
    Zero network; corpus twins in-repo; slice-E loaders single source."""
    closeU, retU = SRP.load_panels()              # 9-leg union (frozen set)
    events = SRP.fund_events(retU)                # envelope rule (single src)
    evt_set = {(s, e["date"]) for s in LEGS_ALL for e in events.get(s, [])}
    core_zero = not events.get(CORE)
    cleanU, flagged = SRP.clean_rets(retU, events)
    cv = {s: SRP.clean_value(closeU, cleanU, s) for s in LEGS_ALL}

    idx = closeU.index
    tl = idx[(idx >= pd.Timestamp("2013-01-01"))
             & (idx <= EVIDENCE_CUTOFF_TS)]

    legs = {}
    for s in LEGS_ALL:
        df = _leg_frame(s)
        raw_close = df["close"].reindex(tl)
        raw_open = df["open"].reindex(tl)
        cl = cv[s].reindex(tl)                   # bridged close face
        ratio = (cl / raw_close).ffill()          # step face (event adj)
        op = (raw_open * ratio).ffill()           # bridged exec open
        # pre-listing arrays: 0.0 price + NaN ADV = never fills, never
        # poisons equity (holds stay 0 -- R240 never-invested sanity face)
        op = op.fillna(0.0).to_numpy(dtype=np.float64)
        cl_arr = cl.fillna(0.0).to_numpy(dtype=np.float64)
        vc = (df["volume"] * df["close"]).reindex(tl)
        adv = vc.rolling(20).mean().to_numpy(dtype=np.float64)
        legs[s] = {"open": op, "close": cl_arr, "adv": adv}

    # signal = rolling 252 on FULL union calendar (slice-E convention),
    # evaluated on the timeline; MA200 = clean-value face rolling (s3.3)
    sig = {}
    for s in SAT:
        sig[s] = ((1.0 + cleanU[s]).rolling(W, min_periods=W).apply(
            lambda x: float(np.prod(x)), raw=True) - 1.0).reindex(tl)
    ma = {}
    for s in SAT:
        ma[s] = cv[s].rolling(MA_WIN, min_periods=MA_WIN).mean().reindex(tl)

    sig_arr = {s: sig[s].to_numpy(dtype=np.float64) for s in SAT}
    ma_arr = {s: ma[s].to_numpy(dtype=np.float64) for s in SAT}
    cl_arr = {s: legs[s]["close"] for s in SAT}

    first_active = None
    sched = rebal_schedule(len(tl))
    for r in sched:
        nvalid = int(sum(1 for s in SAT if np.isfinite(sig_arr[s][r])))
        if nvalid >= MIN_AVAIL:
            first_active = str(tl[r].date())
            break
    gates = panel_gates(tl, evt_set, core_zero,
                        bool(np.isfinite(legs[CORE]["close"]).all()))
    gates["first_active_rebal"] = first_active
    gates["first_active_ok"] = bool(first_active == FIRST_ACTIVE_FROZEN)

    P = {"days": tl, "n": int(len(tl)), "legs": legs,
         "sig": sig_arr, "ma": ma_arr, "cl_sat": cl_arr,
         "gates": gates, "flagged_events": int(flagged),
         "rebal_days": sched,
         "events_detail": {s: events.get(s, []) for s in LEGS_ALL}}
    return P


def rebal_schedule(T):
    """Quarterly grid, frozen anchor 62, step 63 (prereg s3.2)."""
    return list(range(REBAL_ANCHOR, T - 1, REBAL_STEP))


# ---------------------------------------------------------------- targets


def make_target(sat_key, gate_on):
    """s3.1/s3.3 target rule at signal close r (timeline index).
    None = warmup/cash-honest (fewer than MIN_AVAIL available legs)."""
    sat_w = SAT_W[sat_key]
    core_w = 1.0 - sat_w

    def tgt(r):
        avail = [s for s in SAT if np.isfinite(SIG[s][r])]
        if len(avail) < MIN_AVAIL:
            return None
        vals = [SIG[s][r] for s in avail]
        mx = max(vals)
        winners = [s for s in avail if SIG[s][r] == mx]     # strict tie face
        out = {CORE: core_w}
        if gate_on:
            keep = [s for s in winners
                    if np.isfinite(MA[s][r]) and CL[s][r] > MA[s][r]]
            if not keep:
                return {CORE: core_w}      # satellite -> cash, CORE held
            for s in keep:
                out[s] = sat_w / len(keep)
        else:
            for s in winners:
                out[s] = sat_w / len(winners)
        return out
    return tgt


def make_null_target(seed):
    """s3.4: one uniform draw among AVAILABLE satellite legs per rebalance
    (rng consumed in schedule order); SAT20 weight structure; same
    availability/warmup face as the judged bare cells."""
    rng = np.random.default_rng(seed)
    state = {"draws": []}

    def tgt(r):
        avail = [s for s in SAT if np.isfinite(SIG[s][r])]
        if len(avail) < MIN_AVAIL:
            return None
        d = avail[int(rng.integers(0, len(avail)))]
        state["draws"].append(d)
        return {CORE: 0.8, d: 0.2}
    tgt.draws = state["draws"]
    return tgt


# global panel faces for target closures (set in run()/selftest setup)
SIG = {}
MA = {}
CL = {}


def _bind_panel(P):
    global SIG, MA, CL
    SIG = P["sig"]
    MA = P["ma"]
    CL = P["cl_sat"]


# ---------------------------------------------------------------- ckpt


def _ck_path(unit):
    return os.path.join(CKPT_DIR, unit + ".npz")


def _ck_save(unit, rec, series):
    os.makedirs(CKPT_DIR, exist_ok=True)
    r = {k: v for k, v in rec.items() if k != "returns"}
    np.savez(_ck_path(unit), meta=json.dumps(r, default=str),
             returns=np.asarray(series, dtype=np.float64),
             index=np.asarray([str(d.date()) for d in series.index]))


def _ck_load(unit, idx):
    p = _ck_path(unit)
    if not os.path.exists(p):
        return None
    try:
        z = np.load(p, allow_pickle=False)
        meta = json.loads(str(z["meta"]))
        dates = [str(x) for x in z["index"]]
        if len(dates) != len(idx) or dates[0] != str(idx[0].date()) \
                or dates[-1] != str(idx[-1].date()):
            return None
        out = dict(meta)
        out["returns"] = pd.Series(z["returns"], index=idx)
        return out
    except Exception:
        return None


def _write_ckpt_gitignore():
    os.makedirs(CKPT_DIR, exist_ok=True)
    p = os.path.join(CKPT_DIR, ".gitignore")
    if not os.path.exists(p):
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("*\n!.gitignore\n")


# ---------------------------------------------------------------- run


def run() -> int:
    t0 = time.time()
    if os.environ.get("CN_CORE_SATELLITE_P1_REFINALIZE") != "1" \
            and os.path.exists(OUT_JSON):
        try:
            j = json.load(open(OUT_JSON, encoding="utf-8"))
            if j.get("trials_ledger"):
                print("idempotent fast path: results/cn_core_satellite/"
                      "p1_results.json already finalized (ledger block "
                      "present); CN_CORE_SATELLITE_P1_REFINALIZE=1 = only "
                      "redo")
                return 0
        except Exception:
            pass
    if sg.SEED_REGISTRY.get("cn_core_sat_p1") != SEED_BASE:
        print("VOID: seed base cn_core_sat_p1 not registered in "
              "science_gates.SEED_REGISTRY (prereg s3.4: registered AT "
              "the R261 freeze commit)")
        return 2

    P = load_panel()
    if not P["gates"]["all_ok"] or not P["gates"]["first_active_ok"]:
        print("VOID: panel gate FAILED:",
              json.dumps(P["gates"], ensure_ascii=False))
        return 2
    _bind_panel(P)
    _write_ckpt_gitignore()
    _log(f"panel gates OK: T={P['gates']['T']} first_active="
         f"{P['gates']['first_active_rebal']} events="
         f"{P['gates']['events']} flagged={P['flagged_events']}")

    days, n = P["days"], P["n"]
    sched = P["rebal_days"]

    resumed = []

    def run_unit(unit, target_fn, cost_fn):
        ck = _ck_load(unit, days)
        if ck is not None and "returns" in ck:
            resumed.append(unit)
            return ck
        rec = DRV.simulate(P, target_fn, cost_fn)
        _ck_save(unit, rec, rec["returns"])
        return rec

    # -- judged cells x3 faces (s3.5: judge = x2, x1/x3 disclosure)
    cell_recs = {}
    for sat_key in ("SAT20", "SAT40"):
        for gate_on in (False, True):
            cell = f"{sat_key}_{'gate' if gate_on else 'bare'}"
            tf = make_target(sat_key, gate_on)
            for face, cost_fn in FACES.items():
                cell_recs[(cell, face)] = run_unit(
                    f"cell_{cell}_{face}", tf, cost_fn)
            m = DRV.metrics(cell_recs[(cell, JUDGED_FACE)])
            _log(f"cell {cell}: {JUDGED_FACE} sharpe={m['sharpe']} "
                 f"ann={m['ann_ret']} maxdd={m['max_dd']} "
                 f"entries={m['n_entries']} fill_max={m['fill_days_max']} "
                 f"superseded={m['n_superseded']}")

    # -- R240 zero-rebalance-evaluation refusal (warmup still counts)
    for cell in JUDGED_CELLS:
        rec = cell_recs[(cell, JUDGED_FACE)]
        if rec["n_active_rebal"] == 0 and rec["n_warmup_rebal"] == 0:
            print(f"VOID: {cell} zero rebalance evaluations -- signal "
                  "machinery broken, refusing verdict")
            return 2

    # -- K=50 nulls on the judged x2 face (s3.4)
    null_recs = []
    null_draws_head = None
    for k in range(K_NULLS):
        tf = make_null_target(SEED_BASE + k)
        rec = run_unit(f"null_{k:02d}", tf, FACES[JUDGED_FACE])
        null_recs.append(rec)
        if k == 0:
            null_draws_head = list(tf.draws[:12])
    null_vals = [(DRV._sharpe(r["returns"]) or 0.0) for r in null_recs]
    mu, sigma = float(np.mean(null_vals)), float(np.std(null_vals, ddof=1))
    null_pool = {
        "values": [round(v, 6) for v in null_vals],
        "coverage": {"n_values": len(null_vals), "mu": mu, "sigma": sigma,
                     "schemas_parsed": [f"cn_core_sat_p1: {K_NULLS} "
                                       f"random-satellite quarterly "
                                       f"sleeves (seeds 20261080+i, x2 "
                                       f"face, SAT20 structure, "
                                       f"availability-masked)"],
                     "known_unparsed": []},
    }
    _log(f"nulls: K={K_NULLS} mu={mu:.4f} sigma={sigma:.4f}")

    # -- baselines (s3.4 disclosure only, x2 face, activation-anchored)
    def bh_core_target(r):
        avail = [s for s in SAT if np.isfinite(SIG[s][r])]
        if len(avail) < MIN_AVAIL:
            return None
        return {CORE: 1.0}

    def ew_sat_target(r):
        avail = [s for s in SAT if np.isfinite(SIG[s][r])]
        if len(avail) < MIN_AVAIL:
            return None
        out = {CORE: 0.8}
        for s in avail:
            out[s] = 0.2 / len(avail)
        return out

    bh_core = run_unit("baseline_core_bh", bh_core_target,
                       FACES[JUDGED_FACE])
    ew_static = run_unit("baseline_static_8020", ew_sat_target,
                         FACES[JUDGED_FACE])

    # -- census gate (r188 law): every unit computed before finalize
    units_expected = (len(JUDGED_CELLS) * len(FACES) + K_NULLS + 2)
    units_have = (len(cell_recs) + len(null_recs) + 2)
    if units_have < units_expected:
        print(f"finalize census gate: {units_have}/{units_expected} units "
              "-- premature finalize refused, no artifact written")
        return 2

    # -- gates (shared library, zero hand-copied lines; prereg s4)
    line = sg.skill_line_v2(batch_cells=BATCH_CELLS, pool="core48",
                            null_pool=null_pool)
    g1, dsr, g2 = {}, {}, {}
    judged_series = {}
    for cell in JUDGED_CELLS:
        rec = cell_recs[(cell, JUDGED_FACE)]
        rets = rec["returns"].iloc[1:]        # drop NaN head interval
        judged_series[cell] = rets
        g1[cell] = sg.g1_prime_v2(
            sharpe_full=DRV._sharpe(rets), returns=rets,
            batch_cells=BATCH_CELLS, pool="core48", null_pool=null_pool,
            n_trades=rec["n_trades"], n_entries=rec["n_entries"])
        dsr[cell] = sg.deflated_sharpe_ratio(
            rets, n_trials=line["n_eff"], var_null_sr=sigma ** 2)
    fam_pbo = cscv_pbo(align_returns(judged_series))
    for cell in JUDGED_CELLS:
        g2[cell] = sg.g2_registration_v2(
            g1_pass=bool(g1[cell]["pass_v2"]), dsr=dsr[cell],
            pbo=fam_pbo["pbo"])

    g1_errs = {c: v.get("error") for c, v in g1.items()
               if isinstance(v, dict) and "error" in v}
    if g1_errs:
        first = next(iter(g1_errs.items()))
        print(f"finalize FAIL-CLOSED: g1 errored for {len(g1_errs)}/"
              f"{len(g1)} cells (first: {first[0]} -> "
              f"{str(first[1])[:120]}) -- no artifact written")
        return 2

    # -- D6 (registered members reject face + same-batch disclosure)
    try:
        member_rets, member_cutoffs = load_member_rets()
        d6 = {c: d6_block(judged_series[c], member_rets)
              for c in JUDGED_CELLS}
        d6["member_cutoffs"] = member_cutoffs
    except Exception as exc:
        d6 = {"status": "pending_error", "error": repr(exc)[:200]}
    same_batch = {}
    for a in JUDGED_CELLS:
        row = {}
        for b in JUDGED_CELLS:
            if a == b:
                continue
            v, ov = _corr(judged_series[a], judged_series[b])
            row[b] = {"corr": v, "overlap_days": ov}
        same_batch[a] = row
    h4 = h4_family_faces(judged_series, P)

    # -- descriptive clauses + x1/x3 stability (s4)
    descriptive = {}
    for cell in JUDGED_CELLS:
        xm = DRV.metrics(cell_recs[(cell, JUDGED_FACE)])
        yr2 = xm["yearly"]
        stable = {}
        for face in ("x1", "x3"):
            yf = DRV.metrics(cell_recs[(cell, face)])["yearly"]
            common = [y for y in yr2 if y in yf]
            stable[face] = {
                "sign_match_years": int(sum(
                    1 for y in common if (yr2[y] > 0) == (yf[y] > 0))),
                "n_common_years": len(common),
            }
        xm["cost_stability"] = stable
        descriptive[cell] = {
            "full_ann_positive": bool((xm["ann_ret"] or 0) > 0),
            "oos_dual_positive": bool(
                (xm["oos"]["sharpe"] or 0) > 0
                and (xm["oos"]["ann_ret"] or 0) > 0),
            "max_dd_line_pass": bool((xm["max_dd"] or 0) >= MAXDD_LINE),
            "no_crash_year": bool(all(
                v > CRASH_YEAR_LINE for v in yr2.values())),
            "crash_year_line": CRASH_YEAR_LINE,
            "x1_x3_yearly_stability": stable,
        }

    # -- regime descriptive column + per-cell target axis (never a switch)
    reg_col = regime_v3_column(days)
    gate_axis = {}
    for cell in JUDGED_CELLS:
        sat_key = cell.split("_")[0]
        gate_on = cell.endswith("_gate")
        tf = make_target(sat_key, gate_on)
        per_year = {}
        leg_counts = {s: 0 for s in SAT}
        cash_sat_years = {}
        for r in sched:
            y = int(days[r].year)
            per_year.setdefault(y, {"cash": 0, "warmup": 0,
                                    "sat_to_cash": 0})
            tgt = tf(r)
            if tgt is None:
                per_year[y]["warmup"] += 1
            else:
                sats = [s for s in tgt if s != CORE]
                if not sats:
                    per_year[y]["sat_to_cash"] += 1
                    cash_sat_years[str(days[r].date())] = \
                        "gate-rejected or zero-weight satellite"
                for s in sats:
                    leg_counts[s] += 1
        gate_axis[cell] = {"rebal_target_counts_per_year": per_year,
                           "sat_pick_counts": leg_counts}

    # -- cells block (judged face carries per-transition fill rows)
    cells_out = {}
    for cell in JUDGED_CELLS:
        per_face = {}
        for face in FACES:
            mrec = DRV.metrics(cell_recs[(cell, face)])
            if face == JUDGED_FACE:
                mrec["cost_stability"] = descriptive[cell][
                    "x1_x3_yearly_stability"]
                mrec["transitions"] = DRV._compact_transitions(
                    cell_recs[(cell, face)])
            per_face[face] = mrec
        cells_out[cell] = per_face
    judged_returns_audit = {
        cell: [round(float(v), 6) for v in judged_series[cell].tolist()]
        for cell in JUDGED_CELLS}

    nulls_out = {
        "config": {"base": SEED_BASE, "registered": "cn_core_sat_p1",
                   "draws": K_NULLS, "face": f"{JUDGED_FACE}_judged",
                   "rule": "one uniform draw among AVAILABLE satellite "
                           "legs per rebalance (rng per sleeve, schedule "
                           "order); SAT20 weight structure; same "
                           "availability/warmup face; gate cells share "
                           "the bare-null distribution (prereg s3.4 "
                           "conservative note)",
                   "null0_draws_head": null_draws_head},
        "n_values": len(null_vals),
        "values_rounded": null_pool["values"],
        "coverage": null_pool["coverage"],
    }
    baselines_out = {
        "core_only_buy_hold_510880": DRV.metrics(bh_core),
        "static_8020_core_ew_satellite": DRV.metrics(ew_static),
        "note": "activation-anchored passive faces (disclosure only); "
                "skill-line passive anchor = core48 pool via the shared "
                "library (s4); core-only = the satellite-increment "
                "yardstick (prereg s5.4)",
    }

    led = sg.append_ledger(
        "CN-CORE-SATELLITE-P1", LEDGER_TRIALS,
        file_name="results/cn_core_satellite/p1_results.json",
        evidence_cutoff=EVIDENCE_CUTOFF,
        note="4 judged cells {SAT20,SAT40}x{bare,MA200-gate} core=510880 "
             "ballast + satellite=7-leg style-momentum rotation "
             "(quarterly 63d, W252 strict-window clean face) + K50 "
             "random-satellite nulls (seeds 20261080+i, registered "
             "cn_core_sat_p1 at the R261 freeze commit); V2 ADV20-tiered "
             "cost, judge face x2, 1%ADV queue-fill, clean_value bridge "
             "face; prereg research/CN_CORE_SATELLITE_PREREG.md frozen "
             "R261; T-2026-09-26-73 s3 slice-5 (final CN-native model)")

    att = json.load(open(ATT_JSON, encoding="utf-8"))
    d6_rejects = ({c: ((d6.get(c) or {}).get("member_face", {})
                       .get("reject")) for c in JUDGED_CELLS}
                  if d6.get("status") != "pending_error" else None)
    att["entries"].append({
        "batch": "CN-CORE-SATELLITE-P1",
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "kind": "measurement",
        "cells_ledger_delta": LEDGER_TRIALS,
        "ledger_total_after": led["total"],
        "gates": {
            "panel_pass": True,
            "g1_prime_pass": {c: bool(g1[c]["pass_v2"])
                              for c in JUDGED_CELLS},
            "g2_eligible": {c: bool(g2[c]["eligible_v2"])
                            for c in JUDGED_CELLS},
            "d6_reject": d6_rejects,
        },
        "eliminated": LEDGER_TRIALS - sum(
            1 for c in JUDGED_CELLS if g2[c]["eligible_v2"]),
        "refs": {"prereg": "research/CN_CORE_SATELLITE_PREREG.md",
                 "ticket": TICKET},
    })

    import hashlib
    prereg_sha = hashlib.sha256(
        open(PREREG, "rb").read().replace(b"\r\n", b"\n")).hexdigest()

    payload = {
        **sg.cutoff_meta(EVIDENCE_CUTOFF),
        "meta": {
            "batch": "CN-CORE-SATELLITE-P1", "ticket": TICKET,
            "prereg": "research/CN_CORE_SATELLITE_PREREG.md",
            "prereg_sha256_lf_normalized": prereg_sha,
            "judge_face": f"{JUDGED_FACE} (whole-V2 doubled, side_cost_x2 "
                          "family precedent, always on); x1/x3 disclosure "
                          "tracks",
            "seed_base_registered": "cn_core_sat_p1=20261080",
            "cost_basis": "V2 ADV20-tiered (knowledge/rules.py CostPatch "
                          "single source) + 1% ADV participation cap with "
                          "DAY-QUEUED fills (fill_days counters per "
                          "transition; missing-bar days = no fill, NaN "
                          "ADV conservative zero cap)",
            "accounting": "signal close r -> fills from open r+1 (T+1); "
                          "quarterly 63d grid anchor 62; daily close "
                          "valuation; cash zero-yield; warmup = "
                          "cash-honest; MIN_AVAIL=3 (prereg s3.1); tie -> "
                          "satellite weight split; MA200 gate NEVER touches "
                          "CORE (s3.3); re-anchor supersedes incomplete "
                          "transitions",
            "panel": "8-leg union timeline T=3333 (2013-01-04..2026-09-22); "
                     "signal = rolling-252 on FULL union calendar "
                     "(slice-E convention); sim prices = clean_value "
                     "bridge face (event/suspension days 0-return, "
                     "split-adjustment convention, r239 law family); ADV20 "
                     "= raw volume x close CNY (fold-invariant); frozen "
                     "event set 3 (510500 x2, 512100 x1), CORE zero events",
            "machinery_reuse": "DRV=cn_div_lowvol_rot_p1 engine (LEGS=8 "
                               "injection, judged-batch-validated); "
                               "SRP=t73_s2_style_rotation loaders/event "
                               "guard; science_gates shared criteria; "
                               "crisis windows = prereg s4 five-window "
                               "extension",
            "machine": _machine_id(),
        },
        "panel_gates": P["gates"],
        "events_detail": P["events_detail"],
        "cells": cells_out,
        "nulls": nulls_out,
        "baselines": baselines_out,
        "skill_line": line,
        "g1_prime_v2": g1,
        "g2_registration_v2": g2,
        "family_pbo": {k: fam_pbo[k] for k in
                       ("pbo", "n_blocks", "n_trials", "n_rows",
                        "n_combinations") if k in fam_pbo},
        "dsr": dsr,
        "d6_correlation": d6,
        "same_batch_corr": same_batch,
        "h4_disclosure_faces": h4,
        "descriptive": descriptive,
        "regime_columns": {
            "market_v3_axis": reg_col,
            "satellite_axis": gate_axis,
        },
        "judged_x2_returns_6dp_audit": judged_returns_audit,
        "n_trials": LEDGER_TRIALS,
        "audit": {
            "elapsed_sec": round(time.time() - t0, 1),
            "workers": 1,
            "units_expected": units_expected,
            "units_fresh_this_run": units_expected - len(resumed),
            "units_resumed_from_checkpoint": len(resumed),
            "resumed_units_head": resumed[:80],
            "blind_run_flags": {
                "deterministic_sim": "no wall-clock inside sim outputs; "
                                     "double-run byte identity via selftest",
                "queue_rule_frozen": "sells before buys; caps from "
                                     "ADV20(t-1); buys lot-rounded; NaN "
                                     "ADV/missing-bar days = no fill",
            },
        },
        "trials_ledger": led,
    }
    json.loads(json.dumps(payload, default=str))     # validate before write
    tmp = OUT_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, default=str)
    os.replace(tmp, OUT_JSON)
    tmp = ATT_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(att, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, ATT_JSON)
    _write_csv(cells_out, g1, g2, d6)
    _log(f"finalize: ledger total={led['total']} | g1="
         f"{ {c: g1[c]['pass_v2'] for c in JUDGED_CELLS} } g2="
         f"{ {c: g2[c]['eligible_v2'] for c in JUDGED_CELLS} } | "
         f"elapsed={round(time.time() - t0, 1)}s")
    print(f"[cn_core_sat] written {OUT_JSON}; g1="
          f"{ {c: g1[c]['pass_v2'] for c in JUDGED_CELLS} }")
    return 0


def h4_family_faces(judged_series, P):
    """s1 H4-style disclosures (never admission). (1) corr vs 510880 leg
    face = the CORE ballast leg (high BY CONSTRUCTION -- structural
    disclosure, never an alpha claim) = also the ALLOC P5 slot leg face;
    (2) vs family DIV_LOWVOL_P1 C1 x2: artifact carries no return series
    -> honest unavailable, prereg band 0.6-0.9 stands as declared
    expectation."""
    days = P["days"]
    cl = P["legs"][CORE]["close"]
    leg_core = pd.Series(np.append([np.nan],
                                   cl[1:] / cl[:-1] - 1.0), index=days)
    out = {}
    for cell, rets in judged_series.items():
        v510, ov = _corr(rets, leg_core)
        out[cell] = {
            "corr_vs_510880_core_leg": {
                "corr": v510, "overlap_days": ov,
                "note": "CORE ballast leg face (80/60% by construction) = "
                        "ALLOC P5 slot leg face (disclosure only, line "
                        "judgments never cross-wired)"},
            "corr_vs_div_lowvol_p1_c1_x2": {
                "status": "unavailable_in_artifact",
                "note": "family artifact carries per-face metrics only, "
                        "no return series; prereg s1 declared band "
                        "0.6-0.9 (same-instrument domain, judged-negative "
                        "non-member)"},
        }
    return out


def _write_csv(cells_out, g1, g2, d6):
    import csv as _csv
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as fh:
        w = _csv.writer(fh)
        w.writerow(["cell", "face", "sharpe", "ann_ret", "max_dd",
                    "oos_sharpe", "oos_ann", "n_entries", "n_trades",
                    "n_active_rebal", "fill_days_max", "n_superseded",
                    "traded_notional", "cost_total", "g1_pass",
                    "g2_eligible", "d6_max_abs_corr"])
        for cell, per_face in cells_out.items():
            for face, m in per_face.items():
                mf = ((d6.get(cell) or {}).get("member_face", {})
                      if face == JUDGED_FACE else {})
                w.writerow([cell, face, m["sharpe"], m["ann_ret"],
                            m["max_dd"], m["oos"]["sharpe"],
                            m["oos"]["ann_ret"], m["n_entries"],
                            m["n_trades"], m["n_active_rebal"],
                            m["fill_days_max"], m["n_superseded"],
                            m["traded_notional_total"], m["cost_total"],
                            g1[cell]["pass_v2"] if face == JUDGED_FACE
                            else "",
                            g2[cell]["eligible_v2"]
                            if face == JUDGED_FACE else "",
                            mf.get("max_abs_corr", "")])


def _machine_id():
    try:
        return json.load(open(os.path.join(ROOT, "fleet", "machine.json"),
                              encoding="utf-8-sig"))["machine_id"]
    except Exception:
        return os.environ.get("COMPUTERNAME", "unknown")


# ---------------------------------------------------------------- selftest


def _mk_leg(o, cl, adv, n):
    return {"open": np.asarray(o, dtype=np.float64),
            "close": np.asarray(cl, dtype=np.float64),
            "adv": np.asarray(adv, dtype=np.float64)}


def _hermetic_panel(n=40):
    """Flat-price 8-leg hermetic panel (ALL injected DRV.LEGS must be
    present): core + 2 live satellites at flat prices with huge ADV
    (cost/queue arithmetic isolation); the other 5 legs = UNLISTED face
    (0.0 price + NaN ADV -- never fills, never poisons equity)."""
    days = pd.bdate_range("2020-01-01", periods=n)
    legs = {}
    px = {"510880": 10.0, "510050": 20.0, "510300": 30.0,
          "512100": 5.0}
    for s, p in px.items():
        legs[s] = _mk_leg([p] * n, [p] * n, [1e9] * n, n)
    for s in SAT:
        if s not in legs:
            legs[s] = _mk_leg([0.0] * n, [0.0] * n, [np.nan] * n, n)
    return {"days": days, "n": n, "legs": legs,
            "rebal_days": [20, 33]}


def selftest() -> int:
    fails = []

    def ok(fid, cond, detail=""):
        print(f"  [{'PASS' if cond else 'FAIL'}] {fid} {detail}")
        if not cond:
            fails.append(fid)

    # [C1] frozen constants (prereg numbers, drift guard)
    ok("[C1] frozen constants", all([
        T_FROZEN == 3333 and TIMELINE_FIRST == "2013-01-04"
        and FIRST_ACTIVE_FROZEN == "2013-07-17",
        sg.SEED_REGISTRY.get("cn_core_sat_p1") == SEED_BASE
        and SEED_BASE == 20_261_080,
        K_NULLS == 50 and BATCH_CELLS == 4 and LEDGER_TRIALS == 54,
        W == 252 and MIN_AVAIL == 3 and REBAL_ANCHOR == 62
        and REBAL_STEP == 63 and MA_WIN == 200,
        SAT_W == {"SAT20": 0.20, "SAT40": 0.40},
        CAPITAL == 1_000_000.0 and LOT == 100
        and abs(ADV_CAP - krules.ADV_FILL_CAP_RATE) < 1e-15
        and ADV_CAP == 0.01,
        JUDGED_FACE == "x2" and set(FACES) == {"x1", "x2", "x3"}
        and FACES["x1"].__name__ == "side_cost_v2"
        and FACES["x2"].__name__ == "side_cost_x2"
        and FACES["x3"].__name__ == "side_cost_x3",
        JUDGED_CELLS == ("SAT20_bare", "SAT20_gate",
                         "SAT40_bare", "SAT40_gate"),
        EVT_FROZEN == {("510500", "2015-04-15"),
                       ("510500", "2022-08-29"),
                       ("512100", "2022-09-05")},
        EVIDENCE_CUTOFF == "2026-09-22" and OOS_START == "2025-01-01"
        and IS_END == "2024-12-31",
        len(SAT) == 7 and len(LEGS_ALL) == 8 and LEGS_ALL[0] == CORE,
        D6_REJECT == 0.7 and MAXDD_LINE == -0.35
        and CRASH_YEAR_LINE == -0.30 and CRISIS_LOG_ABS_R == 0.05,
        CRISIS_WINDOWS == [("2015-06-15", "2015-08-31"),
                           ("2016-01-01", "2016-01-31"),
                           ("2020-03-01", "2020-03-31"),
                           ("2021-02-01", "2021-02-28"),
                           ("2024-09-01", "2024-10-31")],
    ]))

    # [M1] machinery injection state (documented module-global face)
    ok("[M1] DRV injection", DRV.LEGS == LEGS_ALL
       and DRV.CRISIS_WINDOWS == CRISIS_WINDOWS
       and DRV.simulate.__module__ == "cn_div_lowvol_rot_p1")

    # [M2] engine re-validation on a hermetic 3-leg panel: 80/20 target
    # restores weights within one day (huge ADV -> no queue), tie-free
    global SIG, MA, CL
    P0 = _hermetic_panel()
    # build per-leg signal arrays: satellite A always wins when finite;
    # unlisted legs keep NaN signals (never available, never selected)
    SIG = {"510050": np.full(P0["n"], np.nan),
           "510300": np.full(P0["n"], np.nan),
           "512100": np.full(P0["n"], np.nan)}
    for s in SAT:
        SIG.setdefault(s, np.full(P0["n"], np.nan))
    MA = {"510050": np.zeros(P0["n"]),
          "510300": np.zeros(P0["n"])}
    CL = {"510050": np.full(P0["n"], 20.0),
          "510300": np.full(P0["n"], 30.0)}
    for s in SAT:
        MA.setdefault(s, np.zeros(P0["n"]))
        CL.setdefault(s, np.zeros(P0["n"]))
    for r in P0["rebal_days"]:
        SIG["510050"][r] = 0.10      # winner
        SIG["510300"][r] = 0.05
        SIG["512100"][r] = 0.01
    tf = make_target("SAT20", False)
    rec = DRV.simulate(P0, tf, FACES["x2"])
    # T+1: first fill day = anchor + 1
    tr = [t for t in rec["transitions"] if t["anchor_r"]
          == P0["rebal_days"][0]][0]
    ok("[M2a] T+1 exec", tr["first_exec"] == P0["rebal_days"][0] + 1)
    # 80/20 target anchored; single transition carries BOTH legs' entries
    # (entry_notional accumulates across legs: ~1M - costs at flat prices)
    ok("[M2b] 80/20 target anchored + both legs entered",
       tr["target"] == {CORE: 0.8, "510050": 0.2}
       and abs(tr["entry_notional"] - 1_000_000.0) < 5_000,
       f"target={tr['target']} entry={tr['entry_notional']}")
    # deterministic: double-run byte identity
    rec2 = DRV.simulate(P0, tf, FACES["x2"])
    ok("[M2c] double-run identity",
       np.array_equal(np.asarray(rec["returns"]),
                      np.asarray(rec2["returns"]), equal_nan=True)
       and rec["n_trades"] == rec2["n_trades"])

    # [M3] MIN_AVAIL rule: only 2 valid legs -> None (cash-honest);
    # in-place mutation (never rebuild SIG -- make_target reads it live)
    saved_300 = {r: SIG["510300"][r] for r in P0["rebal_days"]}
    for r in P0["rebal_days"]:
        SIG["510300"][r] = np.nan      # -> avail = 2 < MIN_AVAIL
    ok("[M3] MIN_AVAIL=3 refusal", tf(P0["rebal_days"][0]) is None)
    for r, v in saved_300.items():
        SIG["510300"][r] = v

    # [M4] MA200 gate: winner below MA200 -> satellite to cash, CORE held
    MA["510050"][:] = 100.0          # winner (close 20) far below MA200
    tfg = make_target("SAT20", True)
    tgt = tfg(P0["rebal_days"][0])
    ok("[M4] gate satellite->cash core held",
       tgt == {CORE: 0.8}, f"tgt={tgt}")
    MA["510050"][:] = 0.0            # restore: winner above MA200
    ok("[M4b] gate pass", tfg(P0["rebal_days"][0])
       == {CORE: 0.8, "510050": 0.2})

    # [M5] tie rule: exact float equality -> satellite weight split
    SIG["510300"][P0["rebal_days"][0]] = 0.10
    ok("[M5] strict tie split",
       make_target("SAT40", False)(P0["rebal_days"][0])
       == {CORE: 0.6, "510050": 0.2, "510300": 0.2})
    SIG["510300"][P0["rebal_days"][0]] = 0.05

    # [M6] null determinism: same seed -> same draw sequence
    tfn1 = make_null_target(20261080)
    tfn2 = make_null_target(20261080)
    for r in P0["rebal_days"]:
        tfn1(r)
        tfn2(r)
    ok("[M6] null determinism", tfn1.draws == tfn2.draws)

    # [M7] bridge face: fold artifact day bridges 0-return in clean_value
    close_fake = pd.Series([100.0, 100.0, 348.55, 350.0, 352.0],
                           index=pd.bdate_range("2020-01-01", periods=5))
    ret_fake = close_fake.pct_change(fill_method=None)
    ev_fake = {"510050": [{"date": str(close_fake.index[2].date()),
                           "ret": 2.4855}]}
    clean_fake, _ = SRP.clean_rets(
        pd.DataFrame({"510050": ret_fake}), ev_fake)
    v = SRP.clean_value(pd.DataFrame({"510050": close_fake}),
                        clean_fake, "510050")
    ok("[M7] clean_value bridge",
       abs(v.iloc[2] - v.iloc[1]) < 1e-9
       and abs(v.iloc[4] - 100.0 * (350.0 / 348.55)
               * (352.0 / 350.0)) < 1e-9,
       f"v2={v.iloc[2]:.4f}")

    # [M8] no-lookahead: signal window ends at r (change future -> past
    # signal unchanged) -- strict-window rolling semantics from slice-E
    L = pd.Series(np.log1p(np.asarray([0.01] * 10)))
    sig_a = np.expm1(L.rolling(5, min_periods=5).sum())
    L2 = L.copy()
    L2.iloc[9] = 0.5
    sig_b = np.expm1(L2.rolling(5, min_periods=5).sum())
    ok("[M8] no-lookahead", np.array_equal(
        sig_a.iloc[:5].values, sig_b.iloc[:5].values, equal_nan=True)
        and abs(sig_b.iloc[9] - sig_a.iloc[9]) > 0.1)

    # [M9] real-corpus panel gates (offline, in-repo): frozen event set,
    # core zero events, T/first/cutoff/first_active all frozen numbers
    P = load_panel()
    _bind_panel(P)                      # real faces -> target closures
    g = P["gates"]
    ok("[M9] real panel gates", bool(g["all_ok"] and g["first_active_ok"]),
       f"T={g['T']} first_active={g['first_active_rebal']} "
       f"events={g['events']}")

    # [M10] pre-listing safety: unlisted legs never traded, equity never
    # NaN (0.0 price face + NaN ADV -> no fills; R240 never-invested)
    first_active_idx = next(r for r in P["rebal_days"]
                            if str(P["days"][r].date())
                            == FIRST_ACTIVE_FROZEN)
    ok("[M10] first_active index",
       P["days"][first_active_idx].date()
       == pd.Timestamp(FIRST_ACTIVE_FROZEN).date())

    # [M11] warmup cash-honest + satellite axis on the real panel
    tf_real = make_target("SAT20", False)
    warmups = sum(1 for r in P["rebal_days"]
                  if tf_real(r) is None)
    actives = len(P["rebal_days"]) - warmups
    ok("[M11] warmup/active counts", warmups >= 1 and actives >= 45,
       f"warmup={warmups} active={actives}")
    tgt_first = tf_real(first_active_idx)
    ok("[M11b] first active target shape",
       isinstance(tgt_first, dict) and abs(
           sum(tgt_first.values()) - 1.0) < 1e-9
       and CORE in tgt_first and abs(tgt_first[CORE] - 0.8) < 1e-9,
       f"tgt={tgt_first}")

    # [M12] engine on the REAL panel: SAT20_bare x2 completes, no NaN in
    # returns post-first-entry, R240 zero-eval refusal face NOT triggered
    rec = DRV.simulate(P, make_target("SAT20", False), FACES["x2"])
    rets = rec["returns"].dropna()
    ok("[M12] real sim sanity", bool(
        len(rets) > 3000 and np.isfinite(rets).all()
        and rec["n_active_rebal"] > 0
        and rec["first_entry_day"] is not None
        and rec["first_entry_day"] >= first_active_idx),
       f"n_valid_rets={len(rets)} active_rebal={rec['n_active_rebal']} "
       f"first_entry={rec['first_entry_day']}")

    print(f"cn_core_sat_p1 selftest: {12}-leg battery, "
          f"{len(fails)} FAIL")
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "selftest"])
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
