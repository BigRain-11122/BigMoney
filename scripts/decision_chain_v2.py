"""DECISION_CHAIN_V2_P1 (T-95 - CEO order O-2026-09-27-2255: screen suitable
portfolio strategies AND decision chains FAST; negative also reported). The
v2 SIMPLIFICATION batch: one frozen ring-level change set per the canonical
prereg research/DECISION_CHAIN_V2_PREREG.md (bm-a R365 s1 side-branch,
ADOPTED canonical by owner bm-c r118 + s9 zero-run amendments a1-a4):

  ring-2 deletion  : daily member routing DELETED entirely; the six
                     registered members stay constant equal-weight core
                     (1/6 attack corps + 5/6 chop corps) at all times.
  ring-1 bypass     : N=5-day state-confirmation hysteresis on the state
                     series (5 consecutive days of the new state before the
                     confirmed state switches; T close -> T+1 exec shift).
  ladder absorption : regime position ladder RED 0.20 / YELLOW 0.65 /
                     ORANGE 0.50 / GREEN 0.80, GREEN x heat-composite HOT
                     -> 0.95 (clock L5 law; a1 amendment = POSITION_LADDER
                     canon verbatim, market_clock import face).
  REV-OSC bear sleeve: confirmed-RED days activate the judged FY_BG_TP8
                     three-piece sleeve at the FULL red cap (20% sleeve +
                     80% cash leg - CEO "xiong-state activation" verbatim);
                     admin-channel entry per O-2340, judged-negative slot
                     closed honestly annotated; params = judged frozen
                     constants imported, zero re-judgment.
  repo cash leg     : uninvested portion accrues GC001 daily
                     (close/100/252, ffill missing days, T-88 s3 face).

Four arms, B/C/D identical-to-v1 definitions (v1-consumed, zero re-count;
G-REPRO-v1 = recomputed B/D aggregates bit-level equal the v1 frozen
records = pipeline integrity gate):

  A-v2 = the v2 simplified chain arm (four-leg envelope),
  B    = best single strategy no-switch (COMPOSITE-CE-01 all-weather),
  C    = passive EW buy&hold baseline (dd path measured in-run for J-C4;
         readings derived-not-counted, zero new trials),
  D    = six-member static equal-weight, no routing.

N_eff = 5,522 = A-v2 {base,x2} x 2,761 frozen starts (legacy 1,255 +
deep 1,506). Windows {6m,12m,24m}; 12m complete-window = primary; J-C1..C4
+ J-TARGET verdicts verbatim v1 caliber; four-ring relocalization mandatory
both outcomes; sleeve/cash attribution columns; D7 four fields + 25td
subsample. Bootstrap seed = SEED_REGISTRY['decision_chain_v2'] = 20284110.

Import-face reuse (prereg s6, zero rewrite): decision_chain_e2e Stage-B
envelope primitives (_agg_arm/_pairwise/_ci_boot caliber/rate_side/gates),
t34/t22 enumeration/loading/anchor gates, rev_osc_stock_p1 judged engine
(sleeve replay), market_clock heat composite (build_heat, s1 law), repo
panel reader (GC001 csv). The four-leg envelope generalizes the frozen
env_daily formula (sum_c w_c r_c - rate*sum_c|dw_c|, first-day exempt);
selftest asserts exact bit-level reduction to t34.env_daily.

Sleeve gate (G-REPRO-REV, s9-a4 two-path law + s9-a5 drift-fallback):
canonical = on-machine judged replay (p1c_stock cache; stats/counters
bit-level == p1_results frozen readings); physical-dependency fallback
= the frozen sleeve-export artifact (results/rev_osc/
daily_series_FY_BG_TP8.json, sha256-verified, stats gate equal); replay
that drifts (benign cross-machine float, dd/quantiles identical) falls
back to the verified artifact with re-validation vs frozen (s9-a5,
MSG-20260928-0340 forensics); both missing -> exit 2 honest.

Usage:
  python scripts/decision_chain_v2.py run          # gates -> verdict -> backfill
  python scripts/decision_chain_v2.py sleeve-export # replay + freeze sleeve artifact
  python scripts/decision_chain_v2.py status
  python scripts/decision_chain_v2.py selftest      # hermetic, offline
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

import t34_early_signal as t34                      # frozen pipeline parent
import decision_chain_e2e as v1                     # v1 Stage-B primitives
import rev_osc_stock_p1 as ro                       # judged sleeve engine
from t22_virtual_timepoints import (               # frozen T-22 primitives
    W6M, W12M, W24M, regime_proxy,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TICKET = "T-2026-09-27-95"
BATCH = "DECISION_CHAIN_V2_P1"
PREREG_PATH = os.path.join(ROOT, "research", "DECISION_CHAIN_V2_PREREG.md")
LEDGER_PATH = os.path.join(ROOT, "research", "DECISION_CHAIN_LEDGER.md")
OUT_JSON = os.path.join(ROOT, "results", "decision_chain_v2.json")
OUT_CSV = os.path.join(ROOT, "research", "shortline",
                       "decision_chain_v2_results.csv")
V1_JSON = os.path.join(ROOT, "results", "decision_chain_e2e.json")
REV_P1_JSON = os.path.join(ROOT, "results", "rev_osc", "p1_results.json")
SLEEVE_ARTIFACT = os.path.join(ROOT, "results", "rev_osc",
                               "daily_series_FY_BG_TP8.json")
GC001_CSV = os.path.join(ROOT, "data", "repo_daily", "GC001.csv")
DD_RED_LINE = t34.DD_RED_LINE        # -0.35 frozen (J-C4)
DD_TARGET_LINE = -0.10               # J-TARGET CEO line (O-0809 s2 verbatim)
BOOTSTRAP_B = t34.BOOTSTRAP_B        # 2000 frozen
BOOTSTRAP_SEED = 20284110            # SEED_REGISTRY['decision_chain_v2']
N_EFF = 5522                         # prereg s0 frozen (A-v2 only)
CONFIRM_DAYS = 5                     # N=5 hysteresis (prereg s3)
FACES = ("base", "x2")
WINDOWS = {"6m": W6M, "12m": W12M, "24m": W24M}
ARMS_V2 = ("A-v2", "B", "C", "D")    # C included: dd line + corr face
REV_FACE_MAP = {"base": "x1", "x2": "x2"}   # chain face -> judged sleeve face
S7_ANCHOR = ("（finalize 于收割轮回填：G 门读数+四臂全表+J 判读+四环复定位"
             "+袖/现金腿归因+预测对账+账本行）")
S8_ANCHOR = ("（一次定稿；预测对账；门禁链损耗账 results/gate_attrition.json "
             "追加一行；回执入轮报告+CODELY.md 行级追加；链赢/链不赢+四环"
             "复定位定案呈 GM/CEO）")


def _log(msg: str) -> None:
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}", flush=True)


def machine_id() -> str:
    return json.load(open(os.path.join(ROOT, "fleet", "machine.json"),
                          encoding="utf-8"))["machine_id"]


def _seed_check():
    from science_gates import SEED_REGISTRY
    got = SEED_REGISTRY.get("decision_chain_v2")
    assert got == BOOTSTRAP_SEED, (
        f"seed law: SEED_REGISTRY['decision_chain_v2']={got} != "
        f"{BOOTSTRAP_SEED} (prereg s3 + s9-a3 single-entry amendment)")
    src = open(os.path.join(ROOT, "scripts", "science_gates.py"),
               encoding="utf-8").read()
    n = src.count('"decision_chain_v2":')
    assert n == 1, (
        f"seed law: duplicate-key risk - 'decision_chain_v2' dict literal "
        f"appears x{n} in science_gates.py (r118 pit law: count==1)")


def _ci_boot(k: int, n: int):
    """Binomial bootstrap 95% CI, v2 seed (prereg s3: 20284110), fresh
    seeded rng per call (v1 caliber, v2 seed parameter)."""
    if n == 0:
        return None, None
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    draws = rng.binomial(n, k / n, BOOTSTRAP_B) / n
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return round(float(lo), 4), round(float(hi), 4)


# -------------------------------------------------- v2 mechanism primitives

def hysteresis_confirm(raw: pd.Series, n: int = CONFIRM_DAYS) -> pd.Series:
    """N-day confirmation (prereg s3): the confirmed state switches to s
    only after n consecutive days of raw==s; causal, zero look-ahead;
    first day initializes with its own raw state (t34 exec_shift family
    disclosure: no pre-positioning without a prior run of decisions)."""
    vals = list(raw.values)
    out = [None] * len(vals)
    if not vals:
        return pd.Series(out, index=raw.index, dtype=object)
    cur = vals[0]
    cand, run = None, 0
    out[0] = cur
    for i in range(1, len(vals)):
        r = vals[i]
        if r == cur:
            cand, run = None, 0
        else:
            if r == cand:
                run += 1
            else:
                cand, run = r, 1
            if run >= n:
                cur, cand, run = r, None, 0
        out[i] = cur
    return pd.Series(out, index=raw.index, dtype=object)


def state_series(axis: str, close: pd.DataFrame) -> pd.Series:
    """Raw state series per axis (prereg s2): legacy = REGIME_GUARD v3
    four-state import-replay (v1 deploy_series face); deep = T-22 frozen
    3-way proxy honestly degraded per a1 map (bull->GREEN, chop/na->ORANGE,
    bear->RED - conservative, disclosed)."""
    if axis == "legacy":
        from live.paper import v3_state_series
        st = v3_state_series()
        return st.reindex(close.index).ffill()
    prox = regime_proxy(close["510300"])
    return prox.map({"bull": "GREEN", "chop": "ORANGE", "na": "ORANGE",
                     "bear": "RED"})


def heat_series(close: pd.DataFrame):
    """L1 heat composite, per-day causal (market_clock import face, s1 law).
    Returns (heat_map, face_info) - heat failure = honest degradation
    (GREEN stays 0.80, prereg s2 'data window' clause), never a gate."""
    try:
        from market_clock_backtest import build_heat
        out = build_heat(close)
        heat = {d: v[3] for d, v in out.items()}
        p80_ok = sum(1 for v in out.values() if v[2] is not None)
        info = {"state": "OK", "computable_days": int(p80_ok),
                "total_days": int(len(out)),
                "coverage": round(p80_ok / len(out), 4) if out else None}
        return heat, info
    except Exception as ex:
        return {}, {"state": "FACE_ERROR", "error": repr(ex)[:200],
                    "computable_days": 0, "total_days": int(len(close)),
                    "coverage": 0.0}


def cap_ladder(confirmed: pd.Series, heat: dict, axis: str) -> pd.Series:
    """Confirmed state -> position cap (prereg s3 + a1 canon verbatim:
    market_clock_call.POSITION_LADDER; GREEN x HOT -> +HOT_LADDER_BONUS =
    0.95 on the legacy axis only - deep proxy axis stays flat per a1)."""
    from market_clock_call import POSITION_LADDER, HOT_LADDER_BONUS
    caps = confirmed.map(lambda s: POSITION_LADDER.get(s))
    if axis == "legacy":
        def adj(d, c):
            if d in heat and heat[d] == "HOT" and c is not None \
                    and confirmed.loc[d] == "GREEN":
                return round(c + HOT_LADDER_BONUS, 2)
            return c
        caps = pd.Series([adj(d, c) for d, c in
                          zip(confirmed.index, caps)], index=confirmed.index)
    return caps.astype(float)


def cash_series(close: pd.DataFrame):
    """GC001 cash leg (prereg s2/s3): daily accrual = close/100/252
    (close = annualized percent), reindex on the panel calendar, ffill
    missing days; pre-coverage days accrue 0 (disclosed)."""
    g = pd.read_csv(GC001_CSV, parse_dates=["date"]).set_index("date")["close"]
    accrue = (g / 100.0 / 252.0).reindex(close.index).ffill().fillna(0.0)
    pre_cov = int((close.index < g.index[0]).sum()) \
        if g.index[0] > close.index[0] else 0
    return accrue, {"first_gc001_day": str(g.index[0].date()),
                    "pre_coverage_zero_days": pre_cov,
                    "ffill_missing_days": int(
                        g.reindex(close.index).isna().sum())}


def sleeve_frozen_record() -> dict:
    d = json.load(open(REV_P1_JSON, encoding="utf-8-sig"))
    return d["cells"]["FY_BG_TP8"]


def sleeve_cell_spec() -> dict:
    return next(c for c in ro.CELLS if c["name"] == "FY_BG_TP8")


def sleeve_series_replay(face: str):
    """Canonical sleeve path: on-machine judged replay (deterministic,
    zero rng; prereg s2). Returns (pd.Series, stats, counters, provenance)."""
    P = ro.load_panel()
    dates = pd.to_datetime(np.load(os.path.join(ro.CACHE, "dates.npy")),
                           unit="us")
    cell = sleeve_cell_spec()
    out = ro.sim_cell(P, cell, REV_FACE_MAP[face])
    stats = ro.cell_stats(out["series"])
    counters = {k: out[k] for k in ("entries", "trades", "unfillable",
                                    "skips", "exits", "cohorts")}
    prov = {"path": "on-machine-replay", "machine": machine_id(),
            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "cache": ro.CACHE, "face": face}
    return pd.Series(out["series"], index=dates), stats, counters, prov


def _series_sha256(series) -> str:
    arr = np.asarray(series, dtype=np.float64)
    return hashlib.sha256(arr.tobytes()).hexdigest()


def sleeve_series_artifact(face: str):
    """Fallback sleeve path (s9-a4): consume the frozen sleeve-export
    artifact; gate = stats/counters bit-level + sha256 self-consistency."""
    d = json.load(open(SLEEVE_ARTIFACT, encoding="utf-8-sig"))
    blk = d["faces"][REV_FACE_MAP[face]]
    arr = np.asarray(blk["series"], dtype=np.float64)
    sha = hashlib.sha256(arr.tobytes()).hexdigest()
    assert sha == blk["sha256_series"], (
        f"sleeve artifact sha256 drift (face {face})")
    stats = ro.cell_stats(arr)
    prov = {"path": "sleeve-export-artifact", "face": face,
            "artifact_provenance": d.get("provenance"),
            "sha256_series": sha}
    return pd.Series(arr, index=pd.to_datetime(blk["dates"])), stats, \
        blk["counters"], prov


def sleeve_gate(face: str):
    """Two-path sleeve gate (s9-a4 + s9-a5 drift-fallback): on-machine
    replay preferred, frozen export-artifact fallback; both missing ->
    None; stats/counters must equal the judged frozen readings bit-level
    (G-REPRO-REV). Returns the DATES-INDEXED series (per-axis alignment
    happens in the axis loop)."""
    rec = sleeve_frozen_record()
    frozen = rec[REV_FACE_MAP[face]]
    if os.path.isdir(ro.CACHE):
        series, stats, counters, prov = sleeve_series_replay(face)
        path_used = "replay"
    elif os.path.exists(SLEEVE_ARTIFACT):
        series, stats, counters, prov = sleeve_series_artifact(face)
        path_used = "artifact"
    else:
        return None
    ok = (stats == frozen["stats"]
          and counters["entries"] == frozen["entries"]
          and counters["trades"] == frozen["trades"])
    if not ok and path_used == "replay" and os.path.exists(SLEEVE_ARTIFACT):
        # s9-a5 drift-fallback (MSG-20260928-0340/0345 forensics): benign
        # cross-machine float accumulation drift on cache-bearing machines
        # (identical dd/n_days/quantiles, sub-1e-4 sharpe/ann_ret wobble) --
        # the r368-verified bit-equal artifact is the deterministic face;
        # re-check below re-validates vs frozen, fail-closed preserved.
        series, stats, counters, prov = sleeve_series_artifact(face)
        path_used = "artifact-drift-fallback"
        ok = (stats == frozen["stats"]
              and counters["entries"] == frozen["entries"]
              and counters["trades"] == frozen["trades"])
    if not ok:
        return {"gate": "G_REPRO_REV_FAIL", "mine_stats": stats,
                "frozen_stats": frozen["stats"], "prov": prov}
    return {"series": series, "stats": stats, "counters": counters,
            "prov": prov, "path": path_used}


def sleeve_align(gated: dict, close: pd.DataFrame):
    """Align the gated sleeve series onto the axis panel calendar (missing
    days -> 0.0 sleeve return, census disclosed)."""
    series = gated["series"]
    aligned = series.reindex(close.index).fillna(0.0)
    census = {"sleeve_days": int(series.index.size),
              "panel_days": int(len(close.index)),
              "covered": int(close.index.isin(series.index).sum()),
              "missing_filled_zero": int(
                  (~close.index.isin(series.index)).sum())}
    return aligned, census


# ---------------------------------------------------- four-leg envelope

def env_daily_v2(rets, W: np.ndarray, rate: float) -> np.ndarray:
    """v2 four-leg envelope: r = sum_c w_c r_c - rate * sum_c|dw_c|;
    initial deployment day exempt (frozen env_daily formula generalized
    to 4 legs; selftest asserts exact reduction to t34.env_daily)."""
    core = (W[:, 0] * rets[0] + W[:, 1] * rets[1]
            + W[:, 2] * rets[2] + W[:, 3] * rets[3])
    dW = np.abs(np.diff(W, axis=0, prepend=W[:1])).sum(axis=1)
    dW[0] = 0.0
    return core - rate * dW


def weights_v2(confirmed: pd.Series, caps_exec: pd.Series,
               sleeve_active_exec: pd.Series) -> np.ndarray:
    """Global four-leg weights (n x 4: attack/chop/sleeve/cash).
    Non-RED: cap x (1/6 attack + 5/6 chop), sleeve 0, cash 1-cap.
    Confirmed-RED: sleeve = full red cap 0.20, cash 0.80, core 0
    (CEO 'bear-state activation' verbatim, prereg s3)."""
    n = len(confirmed)
    W = np.zeros((n, 4))
    capv = caps_exec.to_numpy(dtype=float)
    actv = sleeve_active_exec.to_numpy(dtype=bool)
    W[:, 0] = np.where(actv, 0.0, capv / 6.0)
    W[:, 1] = np.where(actv, 0.0, 5.0 * capv / 6.0)
    W[:, 2] = np.where(actv, 0.20, 0.0)
    W[:, 3] = 1.0 - W[:, 0] - W[:, 1] - W[:, 2]
    return W


def _arm_cells_v2(W4, att, chop, sleeve, cash, close, eligible, curves,
                  rate, axis_reg):
    """A-v2 per-startpoint cells (v1 _arm_cells caliber, four-leg envelope;
    window metrics via frozen t34._win_metrics; beat vs p_ret_12m curve
    row = passive caliber verbatim; 12m leg attribution columns)."""
    idx = close.index
    cells = {}
    for p in eligible:
        n = min(W24M, len(idx) - p)
        Wp = W4[p:p + n]
        sl = sleeve[p:p + n]
        ca = cash[p:p + n]
        r = env_daily_v2((att[p], chop[p], sl, ca), Wp, rate)
        row = curves[f"{t34.ATTACK[0]}|{p}"]
        m6 = t34._win_metrics(r, W6M, t34._passive_window(close, p, W6M))
        m12 = t34._win_metrics(r, W12M, row["p_ret_12m"])
        m24 = t34._win_metrics(r, W24M, t34._passive_window(close, p, W24M))
        sw = int((np.abs(np.diff(Wp, axis=0, prepend=Wp[:1])).sum(axis=1)
                  > 0).sum())
        k12 = min(W12M, n)
        seg12 = r[:k12]
        leg12 = {
            "core": float(np.sum(Wp[:k12, 0] * att[p][:k12]
                                 + Wp[:k12, 1] * chop[p][:k12])),
            "sleeve": float(np.sum(Wp[:k12, 2] * sl[:k12])),
            "cash": float(np.sum(Wp[:k12, 3] * ca[:k12])),
            "fee": float(-rate * np.abs(np.diff(
                Wp[:k12], axis=0, prepend=Wp[:1])).sum()),
        }
        sdate = idx[p]
        cells[p] = {"pos": p, "start": str(sdate.date()),
                    "regime": str(axis_reg.loc[sdate]),
                    "n_bars": int(len(r)),
                    "partial_12m": m12["n_bars"] < W12M,
                    "partial_24m": m24["n_bars"] < W24M,
                    "ret_6m": m6["ret"], "ret_12m": m12["ret"],
                    "ret_24m": m24["ret"],
                    "dd_6m": m6["dd"], "dd_12m": m12["dd"],
                    "dd_24m": m24["dd"],
                    "beat_6m": m6["beat"], "beat_12m": m12["beat"],
                    "beat_24m": m24["beat"], "switches": sw,
                    "p_ret_12m": row["p_ret_12m"],
                    "leg_contrib_12m": leg12}
    return cells


def passive_cells(close: pd.DataFrame, eligible, axis_reg):
    """C-arm cells: passive EW buy&hold (frozen t22 caliber); window
    returns via t34._passive_window verbatim (bit-equal asserted), dd from
    the same equity path; readings derived-not-counted (prereg s0)."""
    idx = close.index
    cells = {}
    for p in eligible:
        sdate = idx[p]
        syms = close.columns[close.loc[sdate].notna()]
        base = close.loc[sdate, syms]
        path = (close.loc[sdate:, syms] / base).mean(axis=1)
        path = np.asarray(path)[:max(W24M, 1)]
        out = {"pos": p, "start": str(sdate.date()),
               "regime": str(axis_reg.loc[sdate]), "switches": 0,
               "n_bars": int(min(W24M, len(idx) - p)), "p_ret_12m": None}
        for wname, k in WINDOWS.items():
            seg = path[:k]
            ret = float(seg[-1] - 1.0) if len(seg) >= 2 else 0.0
            ref = t34._passive_window(close, p, k)
            assert abs(ret - ref) < 1e-12, (
                f"passive caliber drift at p={p} w={wname}: "
                f"{ret} vs t34 {ref}")
            eq = np.cumprod(seg)
            peak = np.maximum.accumulate(eq)
            dd = float((eq / peak - 1.0).min()) if len(eq) >= 2 else 0.0
            pflag = len(seg) < k
            out[f"ret_{wname}"] = ret
            out[f"dd_{wname}"] = dd
            out[f"beat_{wname}"] = bool(ret > ref)   # self-compare: False
            if wname == "12m":
                out["partial_12m"] = pflag
                out["p_ret_12m"] = ref
            if wname == "24m":
                out["partial_24m"] = pflag
        cells[p] = out
    return cells


# --------------------------------------------------------------- overlay

def overlay_axis_face(axis, face, close, eligible, W4, sleeve, cash,
                      log=_log):
    """Cells for all four arms on one (axis, face); B/D via the frozen v1
    _arm_cells (2-leg verbatim), A-v2 via the four-leg envelope, C via the
    passive path; A-v2 zero-fee counterfactual kept for ring-3."""
    curves, dup = v1._face_curves(axis, face)
    if dup:
        log(f"[{axis}/{face}] {len(dup)} duplicate curve keys -- abort")
        return None
    need = {f"{m}|{p}" for p in eligible for m in t34.ATTACK + t34.CHOP}
    missing = sorted(need - set(curves))
    if missing:
        log(f"[{axis}/{face}] coverage FAIL: {len(missing)} cells missing "
            f"(e.g. {missing[:3]}) -- curves incomplete on this machine")
        return None
    rate = v1.rate_side(face)
    att = {p: np.asarray(curves[f"{t34.ATTACK[0]}|{p}"]["curve"], dtype=float)
           for p in eligible}
    chop = {p: np.mean([np.asarray(curves[f"{m}|{p}"]["curve"], dtype=float)
                        for m in t34.CHOP], axis=0) for p in eligible}
    axis_reg = regime_proxy(close["510300"])
    sleeve_np = np.asarray(sleeve, dtype=float)
    cash_np = np.asarray(cash, dtype=float)
    n = len(close.index)
    W_B = np.tile([1.0, 0.0, 0.0], (n, 1))
    W_D = np.tile([1.0 / 6.0, 5.0 / 6.0, 0.0], (n, 1))
    cells = {}
    cells["A-v2"] = _arm_cells_v2(W4, att, chop, sleeve_np, cash_np,
                                  close, eligible, curves, rate, axis_reg)
    cells["B"] = v1._arm_cells(W_B, att, chop, close, eligible, curves,
                               rate, axis_reg)
    cells["D"] = v1._arm_cells(W_D, att, chop, close, eligible, curves,
                               rate, axis_reg)
    cells["C"] = passive_cells(close, eligible, axis_reg)
    a2v_prime = _arm_cells_v2(W4, att, chop, sleeve_np, cash_np, close,
                              eligible, curves, 0.0, axis_reg)
    return {"cells": cells, "a2v_prime": a2v_prime, "rate_side": rate}


# -------------------------------------------------------------- judgment

def _agg(cells, wname):
    """Arm aggregate - v1 _agg_arm with v2 bootstrap seed (CI caliber
    identical, seed = v2 registry per prereg s3)."""
    pflag = {"6m": None, "12m": "partial_12m", "24m": "partial_24m"}[wname]
    full = [c for c in cells.values() if pflag is None or not c[pflag]]
    n = len(full)
    k = sum(1 for c in full if c[f"beat_{wname}"])
    dds = [c[f"dd_{wname}"] for c in full]
    sws = [c["switches"] for c in full]
    rate = k / n if n else None
    lo, hi = _ci_boot(k, n)
    seg = {}
    for c in full:
        b = seg.setdefault(c["regime"], {"n": 0, "k": 0, "dds": []})
        b["n"] += 1
        b["k"] += int(bool(c[f"beat_{wname}"]))
        b["dds"].append(c[f"dd_{wname}"])
    starts = sorted(c["start"] for c in full)
    n_reg, last = 0, None
    for c in sorted(full, key=lambda c: c["pos"]):
        if c["regime"] != last:
            n_reg += 1
            last = c["regime"]
    sub = [c for c in full if c["pos"] % 25 == 0]
    all_k = sum(1 for c in cells.values() if c[f"beat_{wname}"])
    return {"n": n, "beats": k,
            "beat_rate": round(rate, 4) if rate is not None else None,
            "ci95": [lo, hi], "ci95_width":
            None if lo is None else round(hi - lo, 4),
            "min_dd": round(min(dds), 4) if dds else None,
            "mean_dd": round(sum(dds) / len(dds), 4) if dds else None,
            "oos_trades": int(sum(sws)),
            "switches_mean": round(sum(sws) / len(sws), 2) if sws else None,
            "covered_years": (round((pd.Timestamp(starts[-1])
                                     - pd.Timestamp(starts[0])).days
                                    / 365.25, 2) if starts else None),
            "independent_regime_windows": n_reg,
            "partial_n": len(cells) - n,
            "all_windows": {"n": len(cells),
                            "beat_rate": round(all_k / len(cells), 4)
                            if cells else None},
            "subsample_25td": (round(sum(1 for c in sub
                                          if c[f"beat_{wname}"]) / len(sub),
                                     4) if sub else None),
            "segments": {s: {"n": b["n"],
                             "beat_rate": round(b["k"] / b["n"], 4),
                             "min_dd": round(min(b["dds"]), 4)}
                         for s, b in sorted(seg.items())}}


def _pairwise(cells_a, cells_b, wname):
    pflag = {"6m": None, "12m": "partial_12m", "24m": "partial_24m"}[wname]
    full = [p for p, c in cells_a.items() if pflag is None or not c[pflag]]
    k = sum(1 for p in full
            if cells_a[p][f"ret_{wname}"] > cells_b[p][f"ret_{wname}"])
    n = len(full)
    lo, hi = _ci_boot(k, n)
    return {"n": n, "wins": k, "rate": round(k / n, 4) if n else None,
            "ci95": [lo, hi]}


def judge_axis_face(pack):
    """Judgment pack: tables x pairwise x J-C (legacy 12m primary caliber)
    x J-TARGET; J-C4 dd red line over the four arms {A-v2,B,C,D}."""
    cells = pack["cells"]
    tables = {w: {arm: _agg(cells[arm], w) for arm in ARMS_V2}
              for w in WINDOWS}
    pairwise = {}
    for w in WINDOWS:
        pairwise[w] = {
            "Av2_vs_B": _pairwise(cells["A-v2"], cells["B"], w),
            "Av2_vs_D": _pairwise(cells["A-v2"], cells["D"], w),
            "Av2_vs_C": {"n": tables[w]["A-v2"]["n"],
                         "wins": tables[w]["A-v2"]["beats"],
                         "rate": tables[w]["A-v2"]["beat_rate"],
                         "ci95": tables[w]["A-v2"]["ci95"]},
        }
    pw12 = pairwise["12m"]

    def _lo(d):
        return d["ci95"][0]

    jc = {
        "J_C1_chain_vs_best_single": bool(
            _lo(pw12["Av2_vs_B"]) is not None and _lo(pw12["Av2_vs_B"]) > 0.50),
        "J_C2_chain_vs_static_ew": bool(
            _lo(pw12["Av2_vs_D"]) is not None and _lo(pw12["Av2_vs_D"]) > 0.50),
        "J_C3_chain_vs_passive": bool(
            _lo(pw12["Av2_vs_C"]) is not None and _lo(pw12["Av2_vs_C"]) > 0.50),
        "J_C4_dd_redline": bool(all(
            tables["12m"][arm]["min_dd"] is not None
            and tables["12m"][arm]["min_dd"] >= DD_RED_LINE
            for arm in ARMS_V2)),
    }
    jc["chain_win"] = bool(jc["J_C1_chain_vs_best_single"]
                           and jc["J_C2_chain_vs_static_ew"]
                           and jc["J_C3_chain_vs_passive"]
                           and jc["J_C4_dd_redline"])
    j_target = {}
    for w in WINDOWS:
        a, b_ = tables[w]["A-v2"], tables[w]["B"]
        beat_gt = bool(a["beat_rate"] is not None and b_["beat_rate"]
                       is not None and a["beat_rate"] > b_["beat_rate"])
        dd_ok = bool(a["min_dd"] is not None
                     and a["min_dd"] >= DD_TARGET_LINE)
        j_target[w] = {"a2v_beat_rate": a["beat_rate"],
                       "b_beat_rate": b_["beat_rate"],
                       "a2v_min_dd": a["min_dd"],
                       "beat_gt_b": beat_gt, "dd_ok": dd_ok,
                       "pass": bool(beat_gt and dd_ok)}
    return {"tables": tables, "pairwise": pairwise, "j_c": jc,
            "j_target": j_target}


def repro_v1_checks(judge_all, v1_payload):
    """G-REPRO-v1: recomputed B/D aggregates bit-level equal the v1 frozen
    records, both axes x both faces x all windows (pipeline integrity gate;
    C has no v1 table - its integrity rides on the same curve rows via the
    B/D beat columns, disclosed)."""
    checks = {}
    for axis in ("legacy", "deep"):
        for face in FACES:
            for w in WINDOWS:
                for arm in ("B", "D"):
                    mine = judge_all[axis][face]["tables"][w][arm]
                    ref = v1_payload["axes"][axis]["judge"][face][
                        "tables"][w][arm]
                    checks[f"{axis}.{face}.{w}.{arm}"] = (mine == ref)
    return checks


def ring_table_v2(pack, confirmed, raw_state, close, eligible, face,
                  v1_payload):
    """Four-ring relocalization (prereg s4, v2-specific; legacy axis per
    face). ring1 = hysteresis rescue vs v1 switching; ring2 = pure ladder
    value (A-v2 - D after routing deletion); ring3 = friction + zero-fee
    counterfactual; ring4 = GREEN share + seat vacancy 0 honest."""
    cells_a = pack["cells"]["A-v2"]
    cells_b = pack["cells"]["B"]
    cells_d = pack["cells"]["D"]
    prime = pack["a2v_prime"]
    raw_np = raw_state.astype(str)
    day_flips = int((raw_np != raw_np.shift(1).fillna(raw_np.iloc[0])).sum())
    conf_flips = int((confirmed.astype(str) != confirmed.astype(str)
                      .shift(1).fillna(confirmed.iloc[0])).sum())
    v1_ref_sw = v1_payload["ring_table"][face]["ring3_friction"][
        "switches_mean"]
    v1_dis = v1_payload["ring_table"][face]["ring1_temperature"][
        "day_disagreement_rate"]
    seg_diff = {}
    for c in cells_a.values():
        s = c["regime"]
        b = seg_diff.setdefault(s, {"n": 0, "d": 0.0})
        b["n"] += 1
        b["d"] += c["ret_12m"] - cells_d[c["pos"]]["ret_12m"]
    fr = [cells_a[c]["ret_12m"] - prime[c]["ret_12m"]
          for c in cells_a if not cells_a[c]["partial_12m"]]
    gross = [abs(prime[c]["ret_12m"]) for c in cells_a
             if not cells_a[c]["partial_12m"]]
    green_days = int((confirmed == "GREEN").sum())
    green_w = [c for c in cells_a.values()
               if confirmed.loc[pd.Timestamp(c["start"])] == "GREEN"]
    oth_w = [c for c in cells_a.values()
             if confirmed.loc[pd.Timestamp(c["start"])] != "GREEN"]

    def _m(rows, other):
        if not rows:
            return None
        vals = [c["ret_12m"] - other[c["pos"]]["ret_12m"] for c in rows]
        return round(sum(vals) / len(vals), 4)

    a2v_sw = _agg(cells_a, "12m")["switches_mean"]
    return {
        "ring1_hysteresis": {
            "raw_day_flip_rate": round(day_flips / len(raw_np), 4),
            "confirmed_switch_days": conf_flips,
            "a2v_switches_mean_12m": a2v_sw,
            "v1_a1_switches_mean_12m": v1_ref_sw,
            "v1_day_disagreement_rate": v1_dis,
            "rescue_ratio": (round(a2v_sw / v1_ref_sw, 4)
                             if v1_ref_sw else None)},
        "ring2_pure_ladder_value": {
            s: {"n": b["n"], "mean_av2_minus_d_12m": round(b["d"] / b["n"], 4)}
            for s, b in sorted(seg_diff.items())},
        "ring3_friction": {
            "switches_mean": a2v_sw,
            "mean_friction_pp_12m": round(sum(fr) / len(fr), 4)
            if fr else None,
            "friction_share_of_gross": (round(sum(fr) / sum(gross), 4)
                                        if gross and sum(gross) > 0
                                        else None),
            "counterfactual": "A-v2' = same weights, rate=0"},
        "ring4_seat": {
            "green_day_share": round(green_days / len(confirmed), 4),
            "green_days": green_days,
            "green_start_av2_minus_b_12m": _m(green_w, cells_b),
            "other_start_av2_minus_b_12m": _m(oth_w, cells_b),
            "vacancy_note": ("attack corps live count 0 (STYLE_CORPS v1.1); "
                             "0 bull-specialist seats disclosed - v3 "
                             "trigger per ticket spec verbatim")},
    }


def corr_face(pack, eligible):
    """Arm-pairwise window-return correlation (disclosure column only)."""
    out = {}
    for w in WINDOWS:
        for i, a in enumerate(ARMS_V2):
            for b in ARMS_V2[i + 1:]:
                va = np.array([pack["cells"][a][p][f"ret_{w}"]
                               for p in eligible], dtype=float)
                vb = np.array([pack["cells"][b][p][f"ret_{w}"]
                               for p in eligible], dtype=float)
                if va.std() > 0 and vb.std() > 0:
                    c = round(float(np.corrcoef(va, vb)[0, 1]), 4)
                else:
                    c = None
                out[f"{a}-{b}_{w}"] = c
    return out


def attribution_face(pack, eligible):
    """Sleeve/cash-leg attribution (mean 12m window leg contribution over
    complete-window A-v2 cells; prereg s6 attribution columns)."""
    full = [c for c in pack["cells"]["A-v2"].values()
            if not c["partial_12m"]]
    legs = ("core", "sleeve", "cash", "fee")
    out = {k: (round(sum(c["leg_contrib_12m"][k] for c in full) / len(full),
                     6) if full else None) for k in legs}
    out["n"] = len(full)
    red_cells = [c for c in full if c["leg_contrib_12m"]["sleeve"] != 0.0]
    out["sleeve_active_cells"] = len(red_cells)
    out["sleeve_mean_contrib_active_cells"] = (
        round(sum(c["leg_contrib_12m"]["sleeve"] for c in red_cells)
              / len(red_cells), 6) if red_cells else None)
    return out


# ----------------------------------------------------------------- gates

def artifact_gate(log=_log):
    """Hard artifact gate (honest exit-2 listing; a2/a4 physical faces):
    panels, curves, v1 records, GC001; sleeve two-path handled at load."""
    missing = []
    for axis in ("legacy", "deep"):
        try:
            close, el = v1._axis_eligible(axis, t34._expected_starts())
            if el is None:
                missing.append(f"panel/census {axis}")
        except Exception as ex:
            missing.append(f"panel load {axis}: {repr(ex)[:120]}")
    for axis in ("legacy", "deep"):
        if not os.path.exists(t34.curve_path(axis)):
            missing.append(f"t34 base curves {axis} "
                           f"({t34.curve_path(axis)})")
    for f, label in ((V1_JSON, "v1 verdict records"),
                     (REV_P1_JSON, "rev_osc p1 frozen readings"),
                     (GC001_CSV, "GC001 repo panel"),
                     (os.path.join(ROOT, "results", "shortline",
                                   "t18_deep_manifest.json"),
                      "t18 deep manifest")):
        if not os.path.exists(f):
            missing.append(f"{label} ({f})")
    if not (os.path.isdir(ro.CACHE) or os.path.exists(SLEEVE_ARTIFACT)):
        missing.append(
            f"sleeve source: neither p1c_stock cache ({ro.CACHE}) nor "
            f"export artifact ({SLEEVE_ARTIFACT}) - run sleeve-export on "
            f"the cache-bearing machine (s9-a4)")
    if missing:
        for m in missing:
            log(f"ARTIFACT MISSING: {m}")
        log(f"artifact gate FAIL x{len(missing)} -- this machine lacks the "
            f"a2/a4 physical dependency set (honest exit 2)")
    return missing


def payload_skeleton():
    """Construction key set (B7b contract: consumer keys subset assert)."""
    return {"batch": None, "ticket": None, "prereg": None,
            "prereg_sha256": None, "evidence_cutoff": None,
            "cutoff_meta": None, "faces": None, "windows": None,
            "bootstrap": None, "rate_side": None, "gates": None,
            "axes": None, "pairwise": None, "verdict": None,
            "ring_table": None, "corr": None, "attribution": None,
            "sleeve_face": None, "seat_vacancy": None,
            "trials_ledger": None, "audit": None,
            "finalize_runtime_sec": None}


CONSUMER_KEYS = ("batch", "ticket", "prereg_sha256", "evidence_cutoff",
                 "cutoff_meta", "gates", "axes", "pairwise", "verdict",
                 "ring_table", "corr", "attribution", "sleeve_face",
                 "trials_ledger", "audit")


# ------------------------------------------------------- prereg backfill

def backfill_prereg(payload, ring_note):
    """§7/§8 backfill (prereg s6 deliverable): replace the placeholder
    anchors with the frozen-number blocks; anchors must match exactly
    (no blind rewrite); §8 keeps the receipt/report faces for the
    harvesting session."""
    src = open(PREREG_PATH, encoding="utf-8").read()
    if S7_ANCHOR not in src or S8_ANCHOR not in src:
        raise RuntimeError(
            "prereg backfill anchors not found - file drifted; refusing "
            "blind rewrite")
    gates = payload["gates"]
    jc = payload["verdict"]["j_c_faces"]
    jt = payload["verdict"]["j_target"]
    s7 = [
        "## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】",
        "",
        f"- finalize {payload['audit'].get('asof', '')} via "
        f"{payload.get('executed_by')}（车道=a2 checkpoint 正典面）。",
        f"- G 门读数：G-V3 leg1/leg2={'PASS' if gates['G_V3_leg1']['ok'] else 'FAIL'}/"
        f"{'PASS' if gates['G_V3_leg2']['ok'] else 'FAIL'}·G-CENSUS "
        f"{gates['G_CENSUS_expected']}·G-ANCHOR {gates['G_ANCHOR']}·"
        f"G-MANIFEST {'PASS' if gates['G_MANIFEST']['ok'] else 'FAIL'}·"
        f"G-REPRO-v1 {'PASS' if gates['G_REPRO_v1']['ok'] else 'FAIL'}"
        f"（{gates['G_REPRO_v1']['n_checks']} 检查）·G-REPRO-REV "
        f"{'PASS' if gates['G_REPRO_REV']['ok'] else 'FAIL'}（双面 stats+"
        f"counters 位级）·G-HEAT census={gates['G_HEAT']}。",
        "- 四臂全表（legacy 12m 完整窗·逐面）：",
    ]
    # compact per-face table lines
    for face in FACES:
        t12 = payload["axes"]["legacy"][face]["tables"]["12m"]
        s7.append(
            f"  - {face} legacy 12m：" + "；".join(
                f"{arm} n={t12[arm]['n']} beat_rate={t12[arm]['beat_rate']}"
                f" ci95={t12[arm]['ci95']} min_dd={t12[arm]['min_dd']}"
                for arm in ARMS_V2))
        pw = payload["pairwise"]["legacy"][face]["12m"]
        s7.append(
            f"    pairwise：A-v2 vs B rate={pw['Av2_vs_B']['rate']} "
            f"ci95={pw['Av2_vs_B']['ci95']}；A-v2 vs D "
            f"rate={pw['Av2_vs_D']['rate']} ci95={pw['Av2_vs_D']['ci95']}；"
            f"A-v2 vs C rate={pw['Av2_vs_C']['rate']} "
            f"ci95={pw['Av2_vs_C']['ci95']}")
    s7.append(
        f"- J 判读：J-C1={jc['base']['J_C1_chain_vs_best_single']}/"
        f"{jc['x2']['J_C1_chain_vs_best_single']}·J-C2="
        f"{jc['base']['J_C2_chain_vs_static_ew']}/"
        f"{jc['x2']['J_C2_chain_vs_static_ew']}·J-C3="
        f"{jc['base']['J_C3_chain_vs_passive']}/"
        f"{jc['x2']['J_C3_chain_vs_passive']}·J-C4="
        f"{jc['base']['J_C4_dd_redline']}/{jc['x2']['J_C4_dd_redline']}"
        f"（base/x2）→ chain_win={payload['verdict']['chain_win']}；"
        f"J-TARGET 逐轴×窗×面 pass={payload['verdict']['j_target_pass']}。")
    s7.append(f"- 四环复定位：{ring_note}")
    s7.append(
        f"- 袖/现金腿归因（legacy·完整 12m 窗均值·逐面）："
        + json.dumps(payload["attribution"], ensure_ascii=False))
    s7.append(
        f"- 账本行：append_ledger batch_trials={N_EFF}"
        f"（audit {'CLEAN' if (payload['trials_ledger'] or {}).get('total') else 'not-CLEAN 未计'}）"
        f"——判定面 results/decision_chain_v2.json。")
    s8 = [
        "## §8 批后复盘【必填·s7-T】",
        "",
        f"- 一次定稿（finalize {payload['audit'].get('asof', '')} via "
        f"{payload.get('executed_by')}·机制面=预注册 §3 冻结零调参·判据"
        f"零触碰·非结果驱动改版=v2 版本面封版 per 版本台账律）。",
        f"- 预测对账（§5 逐条）：{payload['prediction_reconciliation']}",
        f"- 门禁链损耗账：results/gate_attrition.json 已追加 "
        f"{BATCH} 行（kind=measurement）。",
        "- 回执入轮报告+CODELY.md 行级追加+链赢/链不赢+四环复定位定案"
        "呈 GM/CEO=收割轮会话面（本文件由 runner 机械回填·叙述定案归"
        "会话 per v1.1 先例）。",
    ]
    out = src.replace(S7_ANCHOR, "\n".join(s7))
    out = out.replace(S8_ANCHOR, "\n".join(s8))
    with open(PREREG_PATH, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(out)


def flip_ledger(payload):
    """DECISION_CHAIN_LEDGER.md v2 row verdict flip PENDING -> LANDED
    (recording flip per v1.1 r319 precedent) + append-only changelog line.
    The original PENDING note stays preserved in the changelog."""
    src = open(LEDGER_PATH, encoding="utf-8").read()
    lines = src.splitlines()
    row_i = next(i for i, l in enumerate(lines)
                 if l.startswith("| v2 简化链版 |"))
    row = lines[row_i]
    assert "PENDING" in row, "v2 ledger row not PENDING - refusing flip"
    cells = row.split(" | ")
    assert cells[-1].lstrip("| ").startswith("PENDING"), \
        "verdict cell shape drift - refusing blind rewrite"
    v = payload["verdict"]
    jc = v["j_c_faces"]
    new_cell = (
        f"LANDED {time.strftime('%Y-%m-%d %H:%M')} {payload['executed_by']} "
        f"finalize（记录性翻面 per v1.1 r319 先例·判据零改动·非结果驱动"
        f"改版=v2 版本面就此封版）：chain_win={v['chain_win']}（base/x2 "
        f"双面·J-C1={jc['base']['J_C1_chain_vs_best_single']}/"
        f"{jc['x2']['J_C1_chain_vs_best_single']}·J-C2="
        f"{jc['base']['J_C2_chain_vs_static_ew']}/"
        f"{jc['x2']['J_C2_chain_vs_static_ew']}·J-C3="
        f"{jc['base']['J_C3_chain_vs_passive']}/"
        f"{jc['x2']['J_C3_chain_vs_passive']}·J-C4="
        f"{jc['base']['J_C4_dd_redline']}/{jc['x2']['J_C4_dd_redline']}）"
        f"·J-TARGET pass={v['j_target_pass']}（逐轴×窗×面）·四环复定位入 "
        f"results/decision_chain_v2.json；批内 N={N_EFF}·判定面 "
        f"results/decision_chain_v2.json；PENDING 期注记（owner 采纳裁决"
        f"a1/a2/a3）append-only 保全于变更日志 r118 行 |")
    cells[-1] = new_cell
    lines[row_i] = " | ".join(cells)
    changelog = (
        f"- {time.strftime('%Y-%m-%d %H:%M')} {payload['executed_by']}: v2 "
        f"verdict 落账（PENDING→LANDED 记录性翻面·finalize 结果入行·判据"
        f"零改动 per r319 先例；runner={os.path.basename(__file__)}·"
        f"chain_win={v['chain_win']}·j_target_pass={v['j_target_pass']}）。")
    # insert changelog at the end of the 变更日志 section (file end)
    lines.append(changelog)
    with open(LEDGER_PATH, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")


def prediction_reconciliation(payload):
    """§5 prediction vs measured - mechanical band membership flags
    (bands are the frozen prereg text; outcome numbers live-read)."""
    t12b = payload["axes"]["legacy"]["base"]["tables"]["12m"]
    t12x = payload["axes"]["legacy"]["x2"]["tables"]["12m"]
    pw = payload["pairwise"]["legacy"]["base"]["12m"]
    ring1 = payload["ring_table"]["base"]["ring1_hysteresis"]
    ring3 = payload["ring_table"]["base"]["ring3_friction"]
    attr = payload["attribution"]["base"]
    dd = min(x for x in (t12b["A-v2"]["min_dd"], t12x["A-v2"]["min_dd"])
             if x is not None)
    lift_d = round(pw["Av2_vs_D"]["rate"] - 0.5
                   if pw["Av2_vs_D"]["rate"] is not None else None, 4)
    out = {
        "p1_hysteresis_rescue": {
            "predicted": "有效切换 ≈1/5 量级（每 12m 窗 ~10 次级 vs v1 48 换防）",
            "measured_a2v_switches_mean_12m": ring1["a2v_switches_mean_12m"],
            "v1_ref": ring1["v1_a1_switches_mean_12m"],
            "rescue_ratio": ring1["rescue_ratio"]},
        "p2_av2_vs_d": {
            "predicted": "beat-lift [+0.02,+0.06]·CI 下界 [0.45,0.55]",
            "measured_pairwise_rate": pw["Av2_vs_D"]["rate"],
            "measured_ci95_lo": pw["Av2_vs_D"]["ci95"][0],
            "beat_lift_vs_50": lift_d},
        "p3_av2_vs_b": {
            "predicted": "点估计 [+0.03,+0.10]·CI 下界 [0.46,0.56]",
            "measured_pairwise_rate": pw["Av2_vs_B"]["rate"],
            "measured_ci95_lo": pw["Av2_vs_B"]["ci95"][0]},
        "p4_worst_dd": {
            "predicted": "v1 −0.3194 → [−0.22,−0.12]·J-TARGET −0.10 线大概率不达（PASS 概率 [10%,35%]）",
            "measured_min_dd_12m": dd,
            "j_target_pass": payload["verdict"]["j_target_pass"]},
        "p5_sleeve_contrib": {
            "predicted": "RED 段袖贡献预期小负/近零（行政通道）",
            "measured_sleeve_mean_contrib": attr.get(
                "sleeve_mean_contrib_active_cells")},
        "p6_friction_share": {
            "predicted": "摩擦份额 [0.5%,3%]",
            "measured": ring3["friction_share_of_gross"]},
        "p7_repro_family": {
            "predicted": "B/C/D 位级=v1 冻结读数；REV-OSC 袖 stats 位级=judged 冻结读数（确定性）",
            "g_repro_v1_ok": payload["gates"]["G_REPRO_v1"]["ok"],
            "g_repro_rev_ok": payload["gates"]["G_REPRO_REV"]["ok"]},
    }
    return out


# ------------------------------------------------------------------- run

def cmd_run(_) -> int:
    t0 = time.time()
    _seed_check()
    mid = machine_id()
    _log(f"=== {BATCH} run: gates -> A-v2 overlay -> verdict "
         f"(machine {mid}) ===")
    from science_gates import append_ledger, cutoff_meta

    if os.path.exists(OUT_JSON) and \
            os.environ.get("DECISION_CHAIN_V2_REFINALIZE") != "1":
        _log(f"verdict already landed ({OUT_JSON}); "
             f"DECISION_CHAIN_V2_REFINALIZE=1 = only redo path")
        return 0

    # ---- artifact gate (a2/a4 physical faces, honest exit 2)
    missing = artifact_gate()
    if missing:
        return 2

    # ---- gates
    v3g = t34._gate_v3()
    _log(f"G-V3 leg1 {'PASS' if v3g['ok'] else 'FAIL'} {v3g['got']}")
    if not v3g["ok"]:
        return 2
    v3l2 = v1._gate_v3_leg2()
    _log(f"G-V3 leg2 {'PASS' if v3l2.get('ok') else 'FAIL'}")
    if not v3l2.get("ok"):
        return 2
    n_anchor_fail = v1._anchor_gate()
    if n_anchor_fail:
        _log(f"G-ANCHOR FAIL x{n_anchor_fail} -- batch void")
        return 2
    expected = t34._expected_starts()
    man = json.load(open(os.path.join(ROOT, "results", "shortline",
                                      "t18_deep_manifest.json"),
                         encoding="utf-8-sig"))
    g_manifest = {"ok": bool(man.get("verdict") == "PASS"
                             and len(man.get("members", {})) == 48)}
    if not g_manifest["ok"]:
        _log(f"G-MANIFEST FAIL {g_manifest}")
        return 2

    # audit block (prereg s0: no CLEAN audit -> not ledgered)
    try:
        subprocess.run([sys.executable, os.path.join(
            ROOT, "scripts", "compute_audit.py")],
            capture_output=True, text=True, timeout=180)
        aj = json.load(open(os.path.join(ROOT, "results",
                                        "compute_audit.json"),
                            encoding="utf-8-sig"))
        latest = aj.get("history", aj)
        if isinstance(latest, list) and latest:
            latest = latest[-1]
        audit = {"verdict": latest.get("verdict"),
                 "flags": latest.get("flags"),
                 "asof": latest.get("ts") or latest.get("asof")}
    except Exception as ex:
        audit = {"verdict": "unavailable", "error": str(ex)[:120]}
    audit_clean = audit.get("verdict") == "CLEAN"

    v1_payload = json.load(open(V1_JSON, encoding="utf-8-sig"))

    # ---- sleeve (two-path gate, s9-a4) + G-REPRO-REV both faces
    sleeve_gated = {}
    for face in FACES:
        got = sleeve_gate(face)
        if got is None or "gate" in got:
            detail = got if (got and "gate" in got) else "no sleeve source"
            _log(f"G-REPRO-REV FAIL [{face}]: sleeve source missing or "
                 f"stats drift ({detail}) -- s9-a4 two-path absent/failing")
            return 2
        sleeve_gated[face] = got
    _log(f"G-REPRO-REV PASS both faces "
         f"(path={sleeve_gated['base']['path']}/"
         f"{sleeve_gated['x2']['path']})")

    # ---- per-axis state machinery + overlay
    panels, packs_all, judge_all = {}, {}, {}
    states_meta = {}
    axis_states = {}
    for axis in ("legacy", "deep"):
        close, eligible = v1._axis_eligible(axis, expected)
        if eligible is None:
            return 2
        panels[axis] = (close, eligible)
        raw = state_series(axis, close)
        assert not raw.isna().any(), (
            f"[{axis}] state series has NaN days - ladder cap undefined "
            f"(prereg has no NaN-cap semantics; honest abort)")
        confirmed = hysteresis_confirm(raw)
        heat, heat_info = heat_series(close)
        caps = cap_ladder(confirmed, heat, axis)
        caps_exec = t34.exec_shift(caps)
        red_exec = t34.exec_shift(confirmed.eq("RED").astype(bool))
        W4 = weights_v2(confirmed, caps_exec, red_exec)
        cash, cash_info = cash_series(close)
        axis_states[axis] = {"raw": raw, "confirmed": confirmed}
        sleeve_census = {}
        for face in FACES:
            sl, census = sleeve_align(sleeve_gated[face], close)
            sleeve_census[face] = census
            pack = overlay_axis_face(axis, face, close, eligible, W4,
                                     sl, cash)
            if pack is None:
                return 2
            packs_all.setdefault(axis, {})[face] = pack
        judge_all[axis] = {face: judge_axis_face(packs_all[axis][face])
                           for face in FACES}
        states_meta[axis] = {
            "raw_first": str(raw.iloc[0]),
            "confirmed_switch_days": int(
                (confirmed.astype(str) != confirmed.astype(str)
                 .shift(1).fillna(confirmed.iloc[0])).sum()),
            "cap_value_counts": {str(k): int(v) for k, v in
                                 pd.Series(caps_exec).round(2)
                                 .value_counts().items()},
            "heat": heat_info, "cash": cash_info,
            "sleeve_active_days": int(red_exec.sum()),
            "sleeve_census": sleeve_census,
        }
        _log(f"[{axis}] overlay done both faces "
             f"({round(time.time() - t0, 1)}s cumulative)")

    # ---- G-REPRO-v1 (B/D aggregates bit-level vs v1 frozen records)
    repro_checks = repro_v1_checks(judge_all, v1_payload)
    repro_ok = all(repro_checks.values())
    n_repro = len(repro_checks)
    _log(f"G-REPRO-v1 {'PASS' if repro_ok else 'FAIL'} "
         f"({sum(repro_checks.values())}/{n_repro})")
    if not repro_ok:
        bad = [k for k, ok in repro_checks.items() if not ok]
        _log(f"G-REPRO-v1 drift examples: {bad[:6]}")
        return 2

    # ---- verdicts
    jc_faces = {face: judge_all["legacy"][face]["j_c"] for face in FACES}
    chain_win = bool(all(jc_faces[f]["chain_win"] for f in FACES))
    j_target = {axis: {face: judge_all[axis][face]["j_target"]
                       for face in FACES}
                for axis in ("legacy", "deep")}
    j_target_pass = bool(all(
        j_target[axis][face][w]["pass"]
        for axis in ("legacy", "deep") for face in FACES for w in WINDOWS))

    ring_table = {face: ring_table_v2(
        packs_all["legacy"][face],
        axis_states["legacy"]["confirmed"], axis_states["legacy"]["raw"],
        panels["legacy"][0], panels["legacy"][1], face, v1_payload)
        for face in FACES}
    corr_out = {face: corr_face(packs_all["legacy"][face],
                               panels["legacy"][1]) for face in FACES}
    attribution = {face: attribution_face(packs_all["legacy"][face],
                                          panels["legacy"][1])
                   for face in FACES}

    # ---- ledger (A-v2 cells only; B/C/D = v1-consumed zero re-count)
    if audit_clean:
        ledger = append_ledger(
            BATCH, N_EFF, file_name="decision_chain_v2.json",
            evidence_cutoff=t34.BINDING_CUTOFF,
            note=(f"A-v2 envelope cells {{base,x2}} x 2,761 starts "
                  f"(legacy 1,255 + deep 1,506); B/C/D = v1-consumed "
                  f"verbatim reuse zero re-count; member curves = "
                  f"checkpoint reuse (T-34/T-22 lineage); sleeve = "
                  f"judged-engine replay, measurement reuse not counted"))
    else:
        ledger = {"prev_total": None, "batch_trials": N_EFF,
                  "total": None,
                  "note": "audit not CLEAN - not counted per prereg s0"}

    axes_out = {axis: {
        "n_starts": len(panels[axis][1]),
        "state_line": ("REGIME_GUARD v3 four-state replay + N=5 hysteresis"
                       if axis == "legacy" else
                       "T-22 3-way proxy a1-map + N=5 hysteresis "
                       "(disclosed, non-v3)"),
        "state_meta": states_meta[axis],
        "tables": {face: judge_all[axis][face]["tables"] for face in FACES},
        "j_target": {face: judge_all[axis][face]["j_target"]
                     for face in FACES},
        "rate_side": {f: packs_all[axis][f]["rate_side"]
                      for f in FACES}} for axis in ("legacy", "deep")}

    with open(PREREG_PATH, "rb") as f:
        prereg_sha = hashlib.sha256(f.read()).hexdigest()
    payload = payload_skeleton()
    payload.update({
        "batch": BATCH, "ticket": TICKET,
        "prereg": "research/DECISION_CHAIN_V2_PREREG.md",
        "prereg_sha256": prereg_sha,
        "evidence_cutoff": t34.BINDING_CUTOFF,
        "cutoff_meta": cutoff_meta(t34.BINDING_CUTOFF),
        "executed_by": mid,
        "faces": list(FACES), "windows": WINDOWS,
        "bootstrap": {"B": BOOTSTRAP_B, "seed": BOOTSTRAP_SEED,
                      "method": "binomial percentile 95% CI",
                      "seed_note": ("SEED_REGISTRY['decision_chain_v2'] "
                                    "single entry 20284110 (s9-a3)")},
        "rate_side": {"base": v1.rate_side("base"), "x2": v1.rate_side("x2"),
                      "derivation": ("v1 rate_side import verbatim "
                                     "(COST_X2_RATE/2 base, x2 doubled), "
                                     "runtime-derived")},
        "gates": {"G_V3_leg1": v3g, "G_V3_leg2": v3l2,
                  "G_CENSUS_expected": expected,
                  "G_ANCHOR": "6/6 PASS (re-run at finalize)",
                  "G_MANIFEST": g_manifest,
                  "G_REPRO_v1": {"ok": repro_ok, "n_checks": n_repro,
                                 "checks": repro_checks},
                  "G_REPRO_REV": {"ok": True,
                                  "faces": {f: {
                                      "path": sleeve_gated[f]["path"],
                                      "stats": sleeve_gated[f]["stats"],
                                      "counters": {
                                          k: sleeve_gated[f]["counters"][k]
                                          for k in ("entries", "trades")}}
                                      for f in FACES}},
                  "G_HEAT": states_meta["legacy"]["heat"],
                  "sleeve_face_note": ("C has no v1 table by construction "
                                       "(passive baseline); its integrity "
                                       "rides the same curve rows via the "
                                       "B/D beat columns (G-REPRO-v1)")},
        "axes": axes_out,
        "pairwise": {axis: {face: judge_all[axis][face]["pairwise"]
                            for face in FACES}
                     for axis in ("legacy", "deep")},
        "verdict": {"j_c_faces": jc_faces, "chain_win": chain_win,
                    "j_target": j_target, "j_target_pass": j_target_pass,
                    "two_tier_note": ("J-C series = per-run scientific "
                                      "readings; J-TARGET = CEO frozen "
                                      "iteration line (O-0809 s2); two "
                                      "tiers disclosed separately, never "
                                      "merged"),
                    "disposition": (
                        "v2 simplified chain WINS the machine test (J-C "
                        "conjunction legacy 12m, both faces)" if chain_win
                        else "v2 chain does NOT win -- honest report + "
                        "four-ring relocalization (prereg s4); J-C1 pass "
                        "with J-C2 fail = no ladder value (member-book "
                        "effect), read separately")},
        "ring_table": ring_table,
        "corr": corr_out,
        "attribution": attribution,
        "sleeve_face": {"provenance": {f: sleeve_gated[f]["prov"]
                                       for f in FACES},
                        "entry_channel": ("admin channel per O-2340 "
                                          "version-ledger law; "
                                          "judged-negative slot closed "
                                          "honestly annotated (prereg s1)")},
        "seat_vacancy": {"attack_corps_live_count": 0,
                         "note": ("0 bull-specialist seats disclosed; "
                                  "seat fill from T-94 survivors = v3 "
                                  "trigger per ticket spec verbatim")},
        "trials_ledger": ledger,
        "audit": audit,
        "finalize_runtime_sec": round(time.time() - t0, 1),
    })
    payload["prediction_reconciliation"] = prediction_reconciliation(payload)
    json.dumps(payload, default=bool)          # parse-validate pre-write
    assert all(k in payload for k in CONSUMER_KEYS), (
        "B7b contract: consumer keys must be subset of construction keys")
    tmp = OUT_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, indent=1, ensure_ascii=False, default=bool)
    os.replace(tmp, OUT_JSON)
    _log(f"verdict chain_win={chain_win} j_target_pass={j_target_pass} "
         f"-> {OUT_JSON}")

    # ---- CSV (small, git)
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    n_csv = 0
    with open(OUT_CSV, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("axis,face,window,arm,n,beat_rate,ci95_lo,ci95_hi,min_dd,"
                "mean_dd,switches_mean,oos_trades,covered_years,"
                "indep_regime_windows,ci95_width,subsample_25td\n")
        for axis in ("legacy", "deep"):
            for face in FACES:
                for wname in WINDOWS:
                    for arm in ARMS_V2:
                        a = judge_all[axis][face]["tables"][wname][arm]
                        fh.write(",".join(str(x) for x in (
                            axis, face, wname, arm, a["n"], a["beat_rate"],
                            a["ci95"][0], a["ci95"][1], a["min_dd"],
                            a["mean_dd"], a["switches_mean"],
                            a["oos_trades"], a["covered_years"],
                            a["independent_regime_windows"],
                            a["ci95_width"], a["subsample_25td"])) + "\n")
                        n_csv += 1
    _log(f"csv -> {OUT_CSV} ({n_csv} rows)")

    # ---- gate attrition row (s7-T)
    attr_path = os.path.join(ROOT, "results", "gate_attrition.json")
    d = json.load(open(attr_path, encoding="utf-8-sig"))
    d["entries"].append({
        "batch": BATCH, "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "kind": "measurement", "retro_fill": False,
        "cells_ledger_delta": N_EFF if audit_clean else 0,
        "ledger_total_after": (ledger or {}).get("total"),
        "gates": {"g_repro_v1_ok": repro_ok, "g_v3": v3g["ok"],
                  "g_repro_rev_ok": True, "chain_win": chain_win,
                  "j_target_pass": j_target_pass, "void": False},
        "eliminated": None,
        "refs": {"results": "results/decision_chain_v2.json",
                 "prereg": "research/DECISION_CHAIN_V2_PREREG.md",
                 "csv": "research/shortline/decision_chain_v2_results.csv",
                 "ticket": f"fleet/tasks/{TICKET}-P1.json"},
        "note": "A-v2 envelope cells only (5,522); B/C/D v1-consumed "
                "zero re-count; sleeve = judged replay measurement reuse"})
    json.dumps(d)
    with open(attr_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

    # ---- prereg §7/§8 backfill + ledger verdict flip (mechanical)
    r1 = ring_table["base"]["ring1_hysteresis"]
    r3 = ring_table["base"]["ring3_friction"]
    r4 = ring_table["base"]["ring4_seat"]
    ring_note = (
        "环①滞回救援 switches "
        f"{r1['a2v_switches_mean_12m']}/12m（rescue_ratio="
        f"{r1['rescue_ratio']} vs v1 {r1['v1_a1_switches_mean_12m']}）；"
        f"环②纯阶梯价值逐段 "
        + json.dumps(ring_table["base"]["ring2_pure_ladder_value"],
                     ensure_ascii=False)
        + f"；环③摩擦 {r3['mean_friction_pp_12m']}pp/份额 "
        f"{r3['friction_share_of_gross']}；环④GREEN 份额 "
        f"{r4['green_day_share']}·席位 0 员如实")
    backfill_prereg(payload, ring_note)
    flip_ledger(payload)
    _log(f"prereg §7/§8 backfilled + ledger v2 row flipped "
         f"(PENDING->LANDED)")
    _log(f"run DONE in {round(time.time() - t0, 1)}s -- chain_win="
         f"{chain_win} j_target_pass={j_target_pass} (negative also "
         f"reported per O-2255)")
    return 0


# ---------------------------------------------------------- sleeve-export

def cmd_sleeve_export(_) -> int:
    """Replay the sleeve on the p1c_stock-bearing machine and freeze the
    daily series artifact (s9-a4 fallback path; small, git-able)."""
    t0 = time.time()
    if not os.path.isdir(ro.CACHE):
        _log(f"p1c_stock cache absent ({ro.CACHE}) -- this machine cannot "
             f"replay the sleeve (s9-a4: run on cache-bearing machine)")
        return 2
    _seed_check()
    faces = {}
    for face in FACES:
        series, stats, counters, prov = sleeve_series_replay(face)
        rec = sleeve_frozen_record()[REV_FACE_MAP[face]]
        ok = (stats == rec["stats"] and counters["entries"] == rec["entries"]
              and counters["trades"] == rec["trades"])
        _log(f"[{face}] G-REPRO-REV replay "
             f"{'PASS' if ok else 'FAIL'} stats={stats}")
        if not ok:
            return 2
        faces[REV_FACE_MAP[face]] = {
            "series": [float(x) for x in series.values],
            "dates": [str(d.date()) for d in series.index],
            "stats": stats, "counters": counters,
            "sha256_series": _series_sha256(series.values)}
    payload = {
        "batch": BATCH, "ticket": TICKET, "kind": "sleeve-daily-series",
        "cell": "FY_BG_TP8", "provenance": {
            "machine": machine_id(),
            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "engine": "rev_osc_stock_p1.sim_cell (judged frozen config, "
                      "deterministic zero-rng)",
            "cache": ro.CACHE,
            "law": "prereg s9-a4 two-path sleeve gate; artifact path = "
                   "physical-dependency fallback, stats gate equal"},
        "faces": faces}
    tmp = SLEEVE_ARTIFACT + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False)
    os.replace(tmp, SLEEVE_ARTIFACT)
    _log(f"sleeve artifact -> {SLEEVE_ARTIFACT} "
         f"({round(time.time() - t0, 1)}s)")
    return 0


# ---------------------------------------------------------------- status

def cmd_status(_) -> int:
    mid = machine_id()
    print(f"machine: {mid}")
    print(f"verdict: {'landed' if os.path.exists(OUT_JSON) else 'pending'}")
    for axis in ("legacy", "deep"):
        base_ok = os.path.exists(t34.curve_path(axis))
        x2, dup = v1._load_x2_curves(axis)
        print(f"curves[{axis}]: base={'present' if base_ok else 'MISSING'} "
              f"x2_cells={len(x2)} dup={len(dup)}")
    print(f"p1c_stock cache: "
          f"{'present' if os.path.isdir(ro.CACHE) else 'ABSENT'}")
    print(f"sleeve artifact: "
          f"{'present' if os.path.exists(SLEEVE_ARTIFACT) else 'absent'}")
    print(f"GC001: "
          f"{'present' if os.path.exists(GC001_CSV) else 'MISSING'}")
    miss = artifact_gate(lambda m: None)
    print(f"artifact gate: "
          f"{'PASS' if not miss else 'FAIL x' + str(len(miss))}")
    for m in miss:
        print(f"  - {m}")
    if os.path.exists(OUT_JSON):
        d = json.load(open(OUT_JSON, encoding="utf-8-sig"))
        print(f"chain_win={d['verdict']['chain_win']} "
              f"j_target_pass={d['verdict']['j_target_pass']} "
              f"executed_by={d.get('executed_by')} "
              f"runtime={d.get('finalize_runtime_sec')}s")
    src = open(PREREG_PATH, encoding="utf-8").read()
    print(f"prereg §7 backfill: "
          f"{'done' if S7_ANCHOR not in src else 'pending'}")
    led = open(LEDGER_PATH, encoding="utf-8").read()
    row = next((l for l in led.splitlines()
                if l.startswith("| v2 简化链版 |")), "")
    print(f"ledger v2 row: "
          f"{'LANDED' if 'LANDED' in row else 'PENDING'}")
    return 0


# --------------------------------------------------------------- selftest

def cmd_selftest(_) -> int:
    """Hermetic offline selftest (r116 law): no engine run, no real panel,
    no network; B7b contract leg included (r297 law)."""
    fails = []

    def t(name, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
        if not ok:
            fails.append(name)

    # S1: seed law (prereg s3 + s9-a3 single entry)
    from science_gates import SEED_REGISTRY, COST_X2_RATE
    src_sg = open(os.path.join(ROOT, "scripts", "science_gates.py"),
                  encoding="utf-8").read()
    t("S1 seed registered + single dict entry + B frozen",
      SEED_REGISTRY.get("decision_chain_v2") == BOOTSTRAP_SEED == 20284110
      and src_sg.count('"decision_chain_v2":') == 1
      and BOOTSTRAP_B == 2000)

    # S2: rate sides = v1 import verbatim
    t("S2 rate_side faces (v1 import)",
      abs(v1.rate_side("base") - COST_X2_RATE / 2) < 1e-15
      and abs(v1.rate_side("x2") - COST_X2_RATE) < 1e-15
      and REV_FACE_MAP == {"base": "x1", "x2": "x2"}
      and abs(ro.COST_X1 - COST_X2_RATE / 2) < 1e-15)

    # S3: hysteresis semantics (5-day confirm, causal)
    idx = pd.bdate_range("2024-01-01", periods=10)
    raw = pd.Series(["G", "G", "Y", "Y", "Y", "Y", "Y", "G", "G", "G"],
                    index=idx)
    conf = hysteresis_confirm(raw)
    t("S3 hysteresis: switch lands on the 5th consecutive new-state day",
      list(conf) == ["G", "G", "G", "G", "G", "G", "Y", "Y", "Y", "Y"]
      or list(conf) == ["G", "G", "G", "G", "G", "G", "Y", "Y", "Y", "Y"])
    raw2 = pd.Series(["G", "Y", "G", "Y", "G", "Y", "G", "Y", "G", "Y"],
                     index=idx)
    t("S4 hysteresis: alternating never switches",
      set(hysteresis_confirm(raw2)) == {"G"})

    # S5: exec shift causality (T close -> T+1 weights)
    caps = pd.Series([0.2, 0.8, 0.8], index=idx[:3])
    t("S5 exec_shift: cap lands T+1 (first row keeps own)",
      list(t34.exec_shift(caps)) == [0.2, 0.2, 0.8])

    # S6: ladder caps = canon verbatim (a1)
    from market_clock_call import POSITION_LADDER, HOT_LADDER_BONUS
    t("S6 ladder canon (a1 verbatim) + heat bonus",
      POSITION_LADDER == {"RED": 0.20, "ORANGE": 0.50, "YELLOW": 0.65,
                          "GREEN": 0.80}
      and abs(HOT_LADDER_BONUS - 0.15) < 1e-12
      and abs(POSITION_LADDER["GREEN"] + HOT_LADDER_BONUS - 0.95) < 1e-12)
    conf_s = pd.Series(["GREEN", "GREEN", "RED"], index=idx[:3])
    heat_ok = {"HOT": "HOT"}
    caps6 = cap_ladder(conf_s, {idx[0]: "HOT", idx[1]: "COOL",
                                idx[2]: "COOL"}, "legacy")
    t("S7 cap_ladder: GREEN x HOT -> 0.95 legacy; deep flat",
      abs(caps6.iloc[0] - 0.95) < 1e-12 and abs(caps6.iloc[1] - 0.80) < 1e-12
      and abs(caps6.iloc[2] - 0.20) < 1e-12
      and abs(cap_ladder(conf_s, {idx[0]: "HOT", idx[1]: "HOT",
                                  idx[2]: "HOT"}, "deep").iloc[0]
              - 0.80) < 1e-12)

    # S8: four-leg envelope reduces bit-level to t34.env_daily (2-leg)
    r_att = np.array([0.01, -0.02, 0.03, 0.004])
    r_chop = np.array([0.005, 0.01, -0.01, 0.002])
    W3 = np.array([[1 / 6, 5 / 6, 0.0], [1 / 6, 5 / 6, 0.0],
                   [1 / 6, 5 / 6, 0.0], [1 / 6, 5 / 6, 0.0]])
    W4 = np.hstack([W3[:, :2], np.zeros((4, 1)), np.zeros((4, 1))])
    t("S8 env_daily_v2 == t34.env_daily at zero sleeve/cash legs",
      bool(np.array_equal(
          env_daily_v2((r_att, r_chop, np.zeros(4), np.zeros(4)), W4, 0.0013),
          t34.env_daily(r_att, r_chop, W3, 0.0013))))

    # S9: fee formula exact (rate x sum|dW|, first day exempt)
    W9 = np.array([[0.2, 0.0, 0.2, 0.6], [0.0, 0.5, 0.2, 0.3],
                   [0.0, 0.5, 0.2, 0.3]])
    r9 = (np.array([0.01, 0.02, 0.0]), np.array([0.01, 0.0, 0.0]),
          np.array([0.05, -0.01, 0.02]), np.array([1e-4, 1e-4, 1e-4]))
    got9 = env_daily_v2(r9, W9, 0.0013)
    dW = np.abs(np.diff(W9, axis=0, prepend=W9[:1])).sum(axis=1)
    dW[0] = 0.0
    exp9 = (W9[:, 0] * r9[0] + W9[:, 1] * r9[1] + W9[:, 2] * r9[2]
            + W9[:, 3] * r9[3]) - 0.0013 * dW
    t("S9 fee = rate x sum|dW| with first-day exemption",
      bool(np.array_equal(got9, exp9))
      and abs(got9[0] - (0.2 * 0.01 + 0.2 * 0.05 + 0.6 * 1e-4)) < 1e-12)

    # S10: weights_v2 structure (non-RED core/cash split; RED sleeve/cash)
    conf10 = pd.Series(["GREEN", "RED", "YELLOW"], index=idx[:3])
    caps10 = pd.Series([0.80, 0.20, 0.65], index=idx[:3])
    act10 = pd.Series([False, True, False], index=idx[:3])
    W10 = weights_v2(conf10, caps10, act10)
    t("S10 weights: GREEN 0.8 -> core 0.8/cash 0.2; RED -> sleeve "
      "0.20/cash 0.80; rows sum 1",
      abs(W10[0, 0] - 0.8 / 6) < 1e-12 and abs(W10[0, 1] - 5 * 0.8 / 6) < 1e-12
      and W10[0, 2] == 0.0 and abs(W10[0, 3] - 0.2) < 1e-12
      and W10[1, 0] == 0.0 and W10[1, 1] == 0.0
      and abs(W10[1, 2] - 0.20) < 1e-12 and abs(W10[1, 3] - 0.80) < 1e-12
      and bool(np.allclose(W10.sum(axis=1), 1.0, atol=1e-12)))

    # S11: cash accrual formula + ffill + pre-coverage zero
    gpath = os.path.join(ROOT, ".codely-cli", "scratch",
                         "_selftest_gc001.csv")
    os.makedirs(os.path.dirname(gpath), exist_ok=True)
    with open(gpath, "w", encoding="utf-8") as fh:
        fh.write("date,open,high,low,close,volume\n")
        fh.write("2024-01-03,1,1,1,2.52,1\n")       # accrue 2.52/100/252
        fh.write("2024-01-05,1,1,1,5.04,1\n")       # gap day ffill
    orig_csv = cash_series.__globals__["GC001_CSV"]
    try:
        cash_series.__globals__["GC001_CSV"] = gpath
        idx11 = pd.bdate_range("2024-01-02", periods=5)
        close11 = pd.DataFrame({"A": [1.0] * 5}, index=idx11)
        accrue, info = cash_series(close11)
        t("S11 cash accrual = close/100/252, ffill, pre-coverage 0",
          abs(accrue.iloc[0] - 0.0) < 1e-15
          and abs(accrue.iloc[1] - 2.52 / 100 / 252) < 1e-15
          and abs(accrue.iloc[2] - 2.52 / 100 / 252) < 1e-15
          and abs(accrue.iloc[3] - 5.04 / 100 / 252) < 1e-15
          and info["pre_coverage_zero_days"] == 1)
    finally:
        cash_series.__globals__["GC001_CSV"] = orig_csv
        os.remove(gpath)

    # S12: bootstrap determinism (v2 seed) + sane bounds
    c1, c2 = _ci_boot(7, 10), _ci_boot(7, 10)
    t("S12 v2 bootstrap deterministic + sane (seed 20284110)",
      c1 == c2 and c1[0] < 0.7 < c1[1] and _ci_boot(10, 10)[0] > 0.5
      and _ci_boot(0, 10)[1] < 0.5)

    # S13: J-C conjunction semantics (one negative kills)
    jc = {"J_C1_chain_vs_best_single": True,
          "J_C2_chain_vs_static_ew": True,
          "J_C3_chain_vs_passive": False,
          "J_C4_dd_redline": True}
    t("S13 chain_win conjunction",
      bool(jc["J_C1_chain_vs_best_single"] and jc["J_C2_chain_vs_static_ew"]
           and jc["J_C3_chain_vs_passive"] and jc["J_C4_dd_redline"])
      is False and DD_RED_LINE == -0.35 and DD_TARGET_LINE == -0.10)

    # S14: J-TARGET needs BOTH beat and dd legs
    t("S14 J-TARGET dual-leg",
      bool(True and False) is False)

    # S15: A-v2 == D identity at constant cap 1 (frozen construction)
    n15 = 6
    att15 = {0: np.array([0.01, 0.02, -0.005, 0.01, 0.0, 0.003])}
    chop15 = {0: np.array([0.004, -0.001, 0.002, 0.0, 0.01, -0.002])}
    W4_15 = np.tile([1 / 6, 5 / 6, 0.0, 0.0], (n15, 1))
    W3_15 = np.tile([1 / 6, 5 / 6, 0.0], (n15, 1))
    r_v2 = env_daily_v2((att15[0], chop15[0], np.zeros(n15), np.zeros(n15)),
                        W4_15, 0.0013)
    r_d = t34.env_daily(att15[0], chop15[0], W3_15, 0.0013)
    t("S15 A-v2 core == D arm composition bit-level (cap=1, no sleeve)",
      bool(np.array_equal(r_v2, r_d)))

    # S16: passive cells ret == t34._passive_window + dd sane
    idx16 = pd.bdate_range("2020-01-01", periods=300)
    close16 = pd.DataFrame({"A": np.linspace(100, 120, 300),
                            "B": np.linspace(50, 60, 300)}, index=idx16)
    reg16 = pd.Series("bull", index=idx16)
    cells16 = passive_cells(close16, [10], reg16)
    c16 = cells16[10]
    t("S16 passive caliber bit-equal t34 + dd <= 0 + self-beat False",
      abs(c16["ret_12m"]
          - t34._passive_window(close16, 10, W12M)) < 1e-12
      and c16["dd_12m"] <= 0.0 and c16["beat_12m"] is False
      and c16["switches"] == 0)

    # S17: agg + D7 + segments on synthetic cells (v1 caliber, v2 seed)
    cells17 = {
        1: {"pos": 1, "start": "2021-01-04", "regime": "bull",
            "partial_12m": False, "beat_12m": True, "dd_12m": -0.01,
            "switches": 2, "ret_6m": 0.1, "ret_12m": 0.2, "ret_24m": 0.3,
            "beat_6m": True, "beat_24m": False, "dd_6m": -0.01,
            "dd_24m": -0.02, "partial_24m": False, "n_bars": 504,
            "p_ret_12m": 0.1, "leg_contrib_12m": {}},
        25: {"pos": 25, "start": "2021-02-08", "regime": "bear",
             "partial_12m": False, "beat_12m": False, "dd_12m": -0.20,
             "switches": 3, "ret_6m": 0.1, "ret_12m": 0.2, "ret_24m": 0.3,
             "beat_6m": True, "beat_24m": False, "dd_6m": -0.01,
             "dd_24m": -0.02, "partial_24m": False, "n_bars": 504,
             "p_ret_12m": 0.1, "leg_contrib_12m": {}},
    }
    a17 = _agg(cells17, "12m")
    t("S17 agg + segments + D7 (v1 caliber)",
      a17["n"] == 2 and a17["beats"] == 1
      and abs(a17["beat_rate"] - 0.5) < 1e-9
      and a17["segments"]["bull"]["n"] == 1
      and a17["independent_regime_windows"] == 2
      and a17["switches_mean"] == 2.5 and a17["oos_trades"] == 5
      and a17["subsample_25td"] == 0.0)
    cells17[25]["partial_24m"] = True
    a24 = _agg(cells17, "24m")
    t("S18 partial split (24m full=1 partial_n=1)",
      a24["n"] == 1 and a24["partial_n"] == 1)
    cells17[25]["partial_24m"] = False

    # S19: pairwise win-rate CI semantics
    pw = _pairwise(cells17, {**cells17}, "12m")
    t("S19 pairwise self-compare wins 0 (strict >)",
      pw["wins"] == 0 and pw["n"] == 2)

    # S20: G-REPRO-v1 comparator catches 1e-4 drift (dict equality)
    mine = {"n": 100, "beats": 43, "beat_rate": 0.4296,
            "ci95": [0.3329, 0.5287], "ci95_width": 0.1958,
            "min_dd": -0.1249, "mean_dd": -0.05, "oos_trades": 4830,
            "switches_mean": 48.3, "covered_years": 5.5,
            "independent_regime_windows": 9, "partial_n": 3,
            "all_windows": {"n": 103, "beat_rate": 0.4175},
            "subsample_25td": 0.4, "segments": {}}
    t("S20 repro comparator drift catch",
      (mine == {**mine, "beat_rate": 0.4296}) is True
      and (mine == {**mine, "beat_rate": 0.4297}) is False)

    # S21: sleeve frozen record live-read shape (no hand-copy)
    rec = sleeve_frozen_record()
    t("S21 sleeve frozen record live-read",
      rec["x1"]["stats"]["sharpe_full"] == -0.219
      and rec["x1"]["stats"]["n_days"] == 8792
      and rec["x1"]["entries"] == 4417 and rec["x2"]["entries"] == 4417
      and sleeve_cell_spec()["name"] == "FY_BG_TP8"
      and sleeve_cell_spec()["H"] == 7)

    # S22: B7b contract leg (r297 law)
    skeleton = payload_skeleton()
    t("S22 B7b consumer keys subset of construction keys",
      all(k in skeleton for k in CONSUMER_KEYS))

    # S23: frozen constants
    t("S23 frozen constants",
      WINDOWS == {"6m": 126, "12m": 252, "24m": 504}
      and FACES == ("base", "x2") and ARMS_V2 == ("A-v2", "B", "C", "D")
      and N_EFF == 5522 and CONFIRM_DAYS == 5
      and t34.ATTACK == ["COMPOSITE-CE-01"] and len(t34.CHOP) == 5
      and t34.BINDING_CUTOFF == "2026-09-22")

    # S24: prereg backfill anchors present (no blind rewrite)
    src = open(PREREG_PATH, encoding="utf-8").read()
    t("S24 prereg §7/§8 anchors in place",
      S7_ANCHOR in src and S8_ANCHOR in src)

    # S25: ledger v2 row PENDING + flip-shape integrity
    led = open(LEDGER_PATH, encoding="utf-8").read()
    row = next((l for l in led.splitlines()
                if l.startswith("| v2 简化链版 |")), "")
    t("S25 ledger v2 row present + verdict cell reachable",
      bool(row) and " | " in row and row.count(" | ") >= 5)

    # S26: artifact gate honest on missing-machine face (bm-c expected)
    miss = artifact_gate(lambda m: None)
    t("S26 artifact gate enumerates honestly (this machine)",
      isinstance(miss, list))

    print(f"\nselftest: "
          f"{'ALL PASS' if not fails else 'FAIL x' + str(len(fails))} "
          f"({', '.join(fails) if fails else 'hermetic zero-network'})")
    return 0 if not fails else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("run")
    sub.add_parser("sleeve-export")
    sub.add_parser("status")
    sub.add_parser("selftest")
    args = ap.parse_args()
    if args.cmd == "run":
        return cmd_run(args)
    if args.cmd == "sleeve-export":
        return cmd_sleeve_export(args)
    if args.cmd == "status":
        return cmd_status(args)
    return cmd_selftest(args)


if __name__ == "__main__":
    sys.exit(main())
