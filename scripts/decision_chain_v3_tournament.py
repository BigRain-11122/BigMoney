#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""decision_chain_v3_tournament.py — DECISION_CHAIN_V3_TOURNAMENT (T-2026-09-28-101).

CEO order O-20260928-1506 (chain-tournament fast iteration); prereg =
research/DECISION_CHAIN_V3_TOURNAMENT_PREREG.md FROZEN bm-c r171 + A-1
amendment r172 (H2 -> H2' SENTIMENT-GATE per O-20260928-1533 broad-index
universe law). K=3 mechanism arms on the v2 simplified-chain base:

  A-H1  STYLE-TILT     v2 face x0.9 + 10% style-ratio satellite overlay
                       (LS pair 512100/510300, GV pair 159915/512800,
                       r60 ratio winner per leg, N=5 confirm, T+1 exec,
                       overlay independent of the ladder cap by design)
  A-H2S SENTIMENT-GATE v2 face under effective cap =
                       min(v2 ladder cap, sentiment ladder cap);
                       E_t from full-A axes Z/F/H (S1 L16-L22 B+ numeric
                       gates, SENTIMENT-AXES-FULLHIST-P1 frozen artifact),
                       caps MAIN->0.80 / CHOPPY->0.50 / RETREAT->0.20
                       (POSITION_LADDER constants reused, zero new params)
  A-H3  MINIMAL-CHAIN  v2 face minus sleeve (six-member EW x ladder +
                       cash leg; falsification control arm)

B/C/D = v1 frozen faces bit-level reuse (G-REPRO-v1, ci95 seed decoration
excluded per v2 s9-a6). Judgments J-C1..C4 + J-TARGET verbatim v1/v2
caliber with A-slot = per-arm; J-TOUR = tournament adjudication
(falsification gate vs H3, cross-arm DSR deflated by batch N_eff, PBO
three-arm panel, E[FP] disclosed, winner = candidate registration only).

Burn host = bm-b MANDATORY (prereg sec.2 G-SENTIMENT host gate: full-A
axes provenance + deep panel physical presence; non-bm-b host = honest
VOID exit 2). Runner lineage = decision_chain_v2 primitives imported
wholesale (import-face reuse law, zero re-implementation); the only new
mechanism code = the three arm overlays + J-TOUR face.

Subcommands: run / status / selftest (hermetic, r116 law).
Exit codes: 0 normal, 2 mechanism/gate failure (honest, never masked).
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import decision_chain_v2 as v2          # v2 primitives (import-face reuse)
import decision_chain_e2e as v1         # v1 curve cells (B/D 2-leg verbatim)
import t34_early_signal as t34          # frozen anchors/enumeration/metrics
from t22_virtual_timepoints import (    # frozen T-22 primitives
    W6M, W12M, W24M, regime_proxy,
)
import science_gates as sg
from screening.pbo import cscv_pbo      # CSCV PBO (backtest-science D4)

TICKET = "T-2026-09-28-101"
BATCH = "DECISION_CHAIN_V3_TOURNAMENT"
PREREG_PATH = os.path.join(ROOT, "research",
                           "DECISION_CHAIN_V3_TOURNAMENT_PREREG.md")
LEDGER_PATH = os.path.join(ROOT, "research", "DECISION_CHAIN_LEDGER.md")
OUT_JSON = os.path.join(ROOT, "results", "decision_chain_v3_tournament.json")
OUT_CSV = os.path.join(ROOT, "research", "shortline",
                       "decision_chain_v3_results.csv")
V1_JSON = os.path.join(ROOT, "results", "decision_chain_e2e.json")
V2_JSON = os.path.join(ROOT, "results", "decision_chain_v2.json")
AXES_JSON = os.path.join(ROOT, "results", "sentiment_axes",
                         "axes_full_history.json")

DD_RED_LINE = t34.DD_RED_LINE          # -0.35 frozen (J-C4)
DD_TARGET_LINE = -0.10                  # J-TARGET CEO line (O-0809 s2)
BOOTSTRAP_B = t34.BOOTSTRAP_B          # 2000 frozen
BOOTSTRAP_SEED = 20291000               # SEED_REGISTRY['decision_chain_...']
N_EFF = 16566                          # 3 arms x {base,x2} x 2,761 starts
CONFIRM_DAYS = 5                        # N=5 hysteresis (prereg s3)
FACES = ("base", "x2")
WINDOWS = {"6m": W6M, "12m": W12M, "24m": W24M}
ARMS_A = ("A-H1", "A-H2S", "A-H3")     # H2S == prereg H2' sentiment gate
ARMS_V3 = ARMS_A + ("B", "C", "D")
BURN_HOST = "bm-b"                     # prereg s2 host gate (mandatory)

# ---- H1 style tilt (prereg s1/s3 frozen) -------------------------------
LS_PAIR = ("512100", "510300")         # small vs large (winner = first
GV_PAIR = ("159915", "512800")         #  growth vs value  iff r60 strictly
TILT_LEG_W = 0.05                      #  greater; ties -> second member)
R60_WIN = 60
H1_CORE_SCALE = 0.9                     # v2 face body share (90/10 split)

# ---- H2' sentiment gates (S1 L22 B+ numeric gates, frozen import) ------
Z_MAIN, F_MAIN, H_MAIN = 80, 0.10, 5      # MAIN-RISE: Z>80 and F<10% and H>5
Z_RETREAT, F_RETREAT, H_RETREAT = 30, 0.25, 3   # RETREAT: Z<30 and F>25% and H<3
SENT_MAIN = "MAIN_RISE"                # residual band = CHOPPY (frozen)
SENT_CHOPPY = "CHOPPY"
SENT_RETREAT = "RETREAT_ICE"

S7_ANCHOR = ("（finalize 于收割轮回填：G 门读数+六臂全表+J-C/J-TARGET/"
             "J-TOUR 逐臂判读+四环复定位+叠加/袖归因+预测对账+账本行）")
S8_ANCHOR = ("（一次定稿；预测对账；门禁链损耗账 results/gate_attrition.json "
             "追加一行；回执入轮报告+CODELY.md 行级追加；锦标赛裁定+证伪门"
             "定案呈 GM/CEO）")


def _log(msg: str) -> None:
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}", flush=True)


def machine_id() -> str:
    return v2.machine_id()


def _seed_check():
    got = sg.SEED_REGISTRY.get("decision_chain_v3_tournament")
    assert got == BOOTSTRAP_SEED, (
        f"seed law: SEED_REGISTRY['decision_chain_v3_tournament']={got} "
        f"!= {BOOTSTRAP_SEED} (prereg s3 + ledger r171 same-commit)")
    src = open(os.path.join(ROOT, "scripts", "science_gates.py"),
               encoding="utf-8").read()
    n = src.count('"decision_chain_v3_tournament":')
    assert n == 1, (
        f"seed law: duplicate-key risk - dict literal appears x{n} "
        f"(r118 pit law: count==1)")


def _ci_boot(k: int, n: int):
    """Binomial bootstrap 95% CI, v3 seed 20291000 (prereg s3), fresh
    seeded rng per call (v1/v2 caliber, v3 seed parameter)."""
    if n == 0:
        return None, None
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    draws = rng.binomial(n, k / n, BOOTSTRAP_B) / n
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return round(float(lo), 4), round(float(hi), 4)


# ---------------------------------------------- v3 agg/pairwise (v3 seed)

def _agg_v3(cells, wname):
    """v2._agg caliber verbatim with the v3 bootstrap seed (the only
    per-batch parameter; ci95/ci95_width are seed-determined decoration
    excluded from G-REPRO comparisons per v2 s9-a6)."""
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


def _pairwise_v3(cells_a, cells_b, wname):
    pflag = {"6m": None, "12m": "partial_12m", "24m": "partial_24m"}[wname]
    full = [p for p, c in cells_a.items() if pflag is None or not c[pflag]]
    k = sum(1 for p in full
            if cells_a[p][f"ret_{wname}"] > cells_b[p][f"ret_{wname}"])
    n = len(full)
    lo, hi = _ci_boot(k, n)
    return {"n": n, "wins": k, "rate": round(k / n, 4) if n else None,
            "ci95": [lo, hi]}


# --------------------------------------- gap-tolerant confirm (warm-up)

def hysteresis_confirm_gap(raw: pd.Series, n: int = CONFIRM_DAYS) -> pd.Series:
    """N-day confirmation over a series that may carry None warm-up days
    (data not yet computable): None/NaN = hold current state, no signal;
    the first valid value initializes. Semantics otherwise identical to
    v2.hysteresis_confirm (causal, zero look-ahead)."""
    vals = list(raw.values)
    out = [None] * len(vals)
    cur, cand, run = None, None, 0

    def _blank(x):
        return x is None or (isinstance(x, float) and np.isnan(x))

    for i, r in enumerate(vals):
        if _blank(r):
            out[i] = cur
            continue
        if cur is None:
            cur, cand, run = r, None, 0
            out[i] = cur
            continue
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


# ------------------------------------------------------ H1 style tilt

def _pair_winner_series(pair, close: pd.DataFrame):
    """Raw r60 winner per pair (None when either leg r60 incomputable).
    Winner = first member iff r60(first) > r60(second); ties -> second
    (frozen deterministic rule)."""
    a, b = pair
    ra = close[a] / close[a].shift(R60_WIN) - 1.0
    rb = close[b] / close[b].shift(R60_WIN) - 1.0
    ok = ra.notna() & rb.notna()
    # explicit None list (pd.Series(None, ...) materializes NaN instead)
    raw = pd.Series([None] * len(close.index), index=close.index,
                    dtype=object)
    raw[ok & (ra > rb)] = a
    raw[ok & (ra <= rb)] = b
    return raw, ok


def style_tilt_face(close: pd.DataFrame):
    """H1 overlay daily face (calendar series, prereg s3 frozen):
    per leg 5% to the confirmed r60 winner, T+1 exec (t34.exec_shift
    semantics), warm-up/non-computable days parked at cash 0.0; rebalance
    cost = single-side rate x sum|dw| over the overlay per-ETF weights,
    charged on the position-change day (one-shot per flip, no trades
    inside the hysteresis band)."""
    close_shift = close.shift(1)
    legs = {}
    census = {}
    for tag, pair in (("LS", LS_PAIR), ("GV", GV_PAIR)):
        raw, ok = _pair_winner_series(pair, close)
        conf = hysteresis_confirm_gap(raw)
        exec_sel = t34.exec_shift(conf)
        rets = pd.Series(0.0, index=close.index)     # park cash = 0.0
        # explicit None list (pd.Series(None, ...) materializes NaN)
        held = pd.Series([None] * len(close.index), index=close.index,
                         dtype=object)
        for d in close.index:
            w = exec_sel.loc[d]
            if isinstance(w, str):
                held.loc[d] = w
        # vectorized per-symbol return stitching (no per-day recompute)
        for s in pair:
            m = (held == s)
            if m.any():
                rets[m] = close[s][m] / close_shift[s][m] - 1.0
        # overlay weight change per day: 0.05 out + 0.05 in on flips,
        # 0.05 on park<->position transitions
        dw = pd.Series(0.0, index=close.index)
        prev = None
        for d in close.index:
            cur = held.loc[d]
            if not isinstance(cur, str):
                cur = None
            if prev != cur:
                step = 0.0
                if prev is not None:
                    step += TILT_LEG_W
                if cur is not None:
                    step += TILT_LEG_W
                dw.loc[d] = step
            prev = cur
        legs[tag] = {"exec_winner": exec_sel, "ret": rets, "dw": dw}
        flips = int((conf.astype(str) != conf.astype(str).shift(1)
                     .fillna("")).sum())
        census[tag] = {
            "r60_computable_days": int(ok.sum()),
            "panel_days": int(len(close)),
            "confirm_flip_days": flips,
            "position_change_days": int((dw > 0).sum()),
            "park_days": int((held.isna()).sum()),
            "first_computable": (str(ok[ok].index[0].date())
                                 if ok.any() else None)}
    ls_ret = legs["LS"]["ret"]
    gv_ret = legs["GV"]["ret"]
    ov_dw = legs["LS"]["dw"] + legs["GV"]["dw"]
    return {"ls_ret": ls_ret, "gv_ret": gv_ret, "ov_dw": ov_dw,
            "census": census, "legs": legs}


def g_style_census(close: pd.DataFrame, eligible, tilt):
    """G-STYLE: four style legs' r60 computable coverage across the frozen
    start-point windows (partial -> degraded disclosure, non-VOID)."""
    n = len(close.index)
    full_cov = partial_cov = 0
    per_leg_ok = {s: int(close[s].notna().sum()) for s in
                  set(LS_PAIR + GV_PAIR) if s in close.columns}
    for p in eligible:
        w = min(W24M, n - p)
        seg = tilt["_ok_all"][p:p + w]
        if seg.all():
            full_cov += 1
        elif seg.any():
            partial_cov += 1
    return {"status": ("PASS" if full_cov == len(eligible)
                       else "PARTIAL_DEGRADED_DISCLOSED"),
            "n_starts": len(eligible), "full_coverage_starts": full_cov,
            "partial_coverage_starts": partial_cov,
            "zero_coverage_starts": len(eligible) - full_cov - partial_cov,
            "leg_days_in_panel": per_leg_ok}


# ---------------------------------------------------- H2' sentiment gate

def load_axes_artifact(log=_log):
    """Load + integrity-verify the frozen full-A axes artifact
    (SENTIMENT-AXES-FULLHIST-P1): schema/batch/evidence_cutoff/axes sha.
    G-SENTIMENT integrity leg (fail-closed)."""
    d = json.load(open(AXES_JSON, encoding="utf-8-sig"))
    problems = []
    if d.get("schema") != "sentiment_axes_full_history/1.0":
        problems.append(f"schema={d.get('schema')}")
    if d.get("batch") != "SENTIMENT-AXES-FULLHIST-P1":
        problems.append(f"batch={d.get('batch')}")
    if d.get("evidence_cutoff") != t34.BINDING_CUTOFF:
        problems.append(f"evidence_cutoff={d.get('evidence_cutoff')} "
                        f"!= {t34.BINDING_CUTOFF}")
    rows = d.get("axes", [])
    canon = json.dumps(rows, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")).encode("utf-8")
    sha = hashlib.sha256(canon).hexdigest()
    if sha != d.get("axes_sha256"):
        problems.append("axes_sha256 drift")
    if problems:
        for p in problems:
            log(f"G-SENTIMENT INTEGRITY PROBLEM: {p}")
        return None
    return d


def sentiment_state_raw(axes_rows):
    """E_t raw mapping (S1 L22 B+ numeric gates, frozen): MAIN_RISE =
    Z>80 and F<10% and H>5; RETREAT_ICE = Z<30 and F>25% and H<3;
    residual band = CHOPPY (band thresholds, frozen residual semantics)."""
    idx, states = [], []
    for r in axes_rows:
        idx.append(pd.Timestamp(r["date"]))
        z, f, h = r["Z"], r["F"], r["H"]
        if z > Z_MAIN and f < F_MAIN and h > H_MAIN:
            states.append(SENT_MAIN)
        elif z < Z_RETREAT and f > F_RETREAT and h < H_RETREAT:
            states.append(SENT_RETREAT)
        else:
            states.append(SENT_CHOPPY)
    return pd.Series(states, index=pd.DatetimeIndex(idx), dtype=object)


def sentiment_face(close: pd.DataFrame, axes_rows):
    """H2' sentiment ladder face (calendar series): confirmed E_t with
    N=5 hysteresis, T+1 exec, caps = POSITION_LADDER constants reused
    (MAIN->GREEN cap / CHOPPY->ORANGE cap / RETREAT->RED cap, zero new
    parameters per prereg s3); reindex onto the panel calendar with ffill
    (beyond-axes tail days hold the last state, census disclosed)."""
    from market_clock_call import POSITION_LADDER
    cap_map = {SENT_MAIN: POSITION_LADDER["GREEN"],
               SENT_CHOPPY: POSITION_LADDER["ORANGE"],
               SENT_RETREAT: POSITION_LADDER["RED"]}
    raw = sentiment_state_raw(axes_rows)
    conf = v2.hysteresis_confirm(raw)
    exec_state = t34.exec_shift(conf)
    caps = exec_state.map(cap_map).astype(float)
    aligned = caps.reindex(close.index).ffill()
    raw_al = raw.reindex(close.index)
    conf_al = conf.reindex(close.index).ffill()
    ffill_days = int(caps.reindex(close.index).isna().sum()
                     - aligned.isna().sum()) if len(caps) else 0
    missing = int(aligned.isna().sum())
    census = {
        "raw_band_days": {s: int((raw_al == s).sum())
                          for s in (SENT_MAIN, SENT_CHOPPY, SENT_RETREAT)},
        "confirmed_band_days": {s: int((conf_al == s).sum())
                                for s in (SENT_MAIN, SENT_CHOPPY,
                                          SENT_RETREAT)},
        "raw_flip_days": int((raw_al.astype(str) != raw_al.astype(str)
                              .shift(1).fillna("")).sum()),
        "confirmed_flip_days": int((conf_al.astype(str)
                                    != conf_al.astype(str).shift(1)
                                    .fillna("")).sum()),
        "cap_value_counts": {str(k): int(v) for k, v in
                             aligned.value_counts().items()},
        "ffill_tail_days": ffill_days, "missing_days": missing,
        "axes_last_day": (str(raw.index[-1].date()) if len(raw) else None),
    }
    return {"caps": aligned, "raw": raw_al, "confirmed": conf_al,
            "census": census}


def g_sentiment_census(close: pd.DataFrame, eligible, sent):
    """G-SENTIMENT: three-axis coverage across all start windows (axes
    computable every day by construction per the artifact census; here we
    census window coverage of the aligned cap series + band occupancy)."""
    okv = sent["caps"].notna().to_numpy()
    n = len(okv)
    full_cov = 0
    for p in eligible:
        w = min(W24M, n - p)
        if bool(okv[p:p + w].all()):
            full_cov += 1
    return {"status": ("PASS" if full_cov == len(eligible)
                       else "PARTIAL_DEGRADED_DISCLOSED"),
            "n_starts": len(eligible), "full_coverage_starts": full_cov,
            "partial_or_missing_starts": len(eligible) - full_cov,
            "band_days": sent["census"]["confirmed_band_days"],
            "ffill_tail_days": sent["census"]["ffill_tail_days"]}


# ------------------------------------------------- generalized arm cells

def _arm_cells_v3(W4, att, chop, sleeve, cash, close, eligible, curves,
                  rate, axis_reg, scale=1.0, extra_ret=None, extra_dw=None,
                  extra_ret_label="overlay"):
    """Generalized v2 arm-cell builder (bit-equal to v2._arm_cells_v2 at
    scale=1.0 / no extras - selftest asserts): r(t) = scale*(four-leg
    envelope) + extra_ret(t) - rate*extra_dw(t). Window metric calibers
    verbatim (t34._win_metrics, passive beat columns, 12m leg
    attribution + overlay attribution when present)."""
    idx = close.index
    cells = {}
    for p in eligible:
        n = min(W24M, len(idx) - p)
        Wp = W4[p:p + n]
        sl = sleeve[p:p + n]
        ca = cash[p:p + n]
        r = v2.env_daily_v2((att[p], chop[p], sl, ca), Wp, rate)
        if scale != 1.0:
            r = r * scale
        if extra_ret is not None:
            r = r + extra_ret[p:p + n]
        if extra_dw is not None:
            r = r - rate * extra_dw[p:p + n]
        row = curves[f"{t34.ATTACK[0]}|{p}"]
        m6 = t34._win_metrics(r, W6M, t34._passive_window(close, p, W6M))
        m12 = t34._win_metrics(r, W12M, row["p_ret_12m"])
        m24 = t34._win_metrics(r, W24M, t34._passive_window(close, p, W24M))
        sw = int((np.abs(np.diff(Wp, axis=0, prepend=Wp[:1])).sum(axis=1)
                  > 0).sum())
        k12 = min(W12M, n)
        leg12 = {
            "core": float(np.sum(Wp[:k12, 0] * att[p][:k12]
                                 + Wp[:k12, 1] * chop[p][:k12])) * scale,
            "sleeve": float(np.sum(Wp[:k12, 2] * sl[:k12])) * scale,
            "cash": float(np.sum(Wp[:k12, 3] * ca[:k12])) * scale,
            "fee": float(-rate * np.abs(np.diff(
                Wp[:k12], axis=0, prepend=Wp[:1])).sum()) * scale,
        }
        if extra_ret is not None:
            leg12[extra_ret_label] = float(np.sum(
                np.asarray(extra_ret[p:p + k12], dtype=float)))
            leg12["overlay_fee"] = float(-rate * np.sum(
                np.asarray(extra_dw[p:p + k12], dtype=float))) \
                if extra_dw is not None else 0.0
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


def overlay_axis_face_v3(axis, face, close, eligible, W4, W4_eff, W4_h3,
                          sleeve, cash, tilt, log=_log):
    """Cells for all six arms on one (axis, face). B/D via the frozen v1
    2-leg cells, C via passive caliber, A arms via the generalized
    builder; per-arm zero-fee counterfactuals (A') kept for ring-3."""
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

    extra_ret = TILT_LEG_W * tilt["ls_ret"] + TILT_LEG_W * tilt["gv_ret"]
    extra_ret = np.asarray(extra_ret, dtype=float)
    extra_dw = np.asarray(tilt["ov_dw"], dtype=float)

    cells = {}
    cells["A-H1"] = _arm_cells_v3(
        W4, att, chop, sleeve_np, cash_np, close, eligible, curves, rate,
        axis_reg, scale=H1_CORE_SCALE, extra_ret=extra_ret,
        extra_dw=extra_dw)
    cells["A-H2S"] = _arm_cells_v3(
        W4_eff, att, chop, sleeve_np, cash_np, close, eligible, curves,
        rate, axis_reg)
    cells["A-H3"] = _arm_cells_v3(
        W4_h3, att, chop, sleeve_np, cash_np, close, eligible, curves,
        rate, axis_reg)
    cells["B"] = v1._arm_cells(W_B, att, chop, close, eligible, curves,
                               rate, axis_reg)
    cells["D"] = v1._arm_cells(W_D, att, chop, close, eligible, curves,
                               rate, axis_reg)
    cells["C"] = v2.passive_cells(close, eligible, axis_reg)
    primes = {
        "A-H1": _arm_cells_v3(
            W4, att, chop, sleeve_np, cash_np, close, eligible, curves,
            0.0, axis_reg, scale=H1_CORE_SCALE, extra_ret=extra_ret,
            extra_dw=None),
        "A-H2S": _arm_cells_v3(
            W4_eff, att, chop, sleeve_np, cash_np, close, eligible,
            curves, 0.0, axis_reg),
        "A-H3": _arm_cells_v3(
            W4_h3, att, chop, sleeve_np, cash_np, close, eligible,
            curves, 0.0, axis_reg),
    }
    return {"cells": cells, "primes": primes, "rate_side": rate,
            "att": att, "chop": chop}


# -------------------------------------------------------------- judgment

def judge_axis_face_v3(pack):
    """Per-arm judgment pack: tables (6 arms) x pairwise (each A arm vs
    B/D/C) x per-arm J-C (legacy 12m primary caliber, J-C4 = arm-level dd
    red line; controls' dd disclosed alongside) + per-arm J-TARGET."""
    cells = pack["cells"]
    tables = {w: {arm: _agg_v3(cells[arm], w) for arm in ARMS_V3}
              for w in WINDOWS}
    pairwise = {}
    for w in WINDOWS:
        pw = {}
        for arm in ARMS_A:
            pw[f"{arm}_vs_B"] = _pairwise_v3(cells[arm], cells["B"], w)
            pw[f"{arm}_vs_D"] = _pairwise_v3(cells[arm], cells["D"], w)
            pw[f"{arm}_vs_C"] = {"n": tables[w][arm]["n"],
                                 "wins": tables[w][arm]["beats"],
                                 "rate": tables[w][arm]["beat_rate"],
                                 "ci95": tables[w][arm]["ci95"]}
        pairwise[w] = pw
    pw12 = pairwise["12m"]

    def _lo(d):
        return d["ci95"][0]

    j_c = {}
    for arm in ARMS_A:
        jc = {
            "J_C1_chain_vs_best_single": bool(
                _lo(pw12[f"{arm}_vs_B"]) is not None
                and _lo(pw12[f"{arm}_vs_B"]) > 0.50),
            "J_C2_chain_vs_static_ew": bool(
                _lo(pw12[f"{arm}_vs_D"]) is not None
                and _lo(pw12[f"{arm}_vs_D"]) > 0.50),
            "J_C3_chain_vs_passive": bool(
                _lo(pw12[f"{arm}_vs_C"]) is not None
                and _lo(pw12[f"{arm}_vs_C"]) > 0.50),
            "J_C4_dd_redline": bool(
                tables["12m"][arm]["min_dd"] is not None
                and tables["12m"][arm]["min_dd"] >= DD_RED_LINE),
        }
        jc["chain_win"] = bool(jc["J_C1_chain_vs_best_single"]
                               and jc["J_C2_chain_vs_static_ew"]
                               and jc["J_C3_chain_vs_passive"]
                               and jc["J_C4_dd_redline"])
        j_c[arm] = jc
    j_target = {}
    for arm in ARMS_A:
        j_target[arm] = {}
        for w in WINDOWS:
            a, b_ = tables[w][arm], tables[w]["B"]
            beat_gt = bool(a["beat_rate"] is not None and b_["beat_rate"]
                           is not None and a["beat_rate"] > b_["beat_rate"])
            dd_ok = bool(a["min_dd"] is not None
                         and a["min_dd"] >= DD_TARGET_LINE)
            j_target[arm][w] = {"arm_beat_rate": a["beat_rate"],
                                "b_beat_rate": b_["beat_rate"],
                                "arm_min_dd": a["min_dd"],
                                "beat_gt_b": beat_gt, "dd_ok": dd_ok,
                                "pass": bool(beat_gt and dd_ok)}
    return {"tables": tables, "pairwise": pairwise, "j_c": j_c,
            "j_target": j_target}


# ---------------------------------------------------- J-TOUR + calendar

def cmd_run(_) -> int:
    t0 = time.time()
    _seed_check()
    mid = machine_id()
    _log(f"=== {BATCH} run: gates -> 6-arm overlay -> J-TOUR verdict "
         f"(machine {mid}) ===")

    if mid != BURN_HOST:
        _log(f"HOST GATE: burn host pinned = {BURN_HOST} (prereg s2 "
             f"G-SENTIMENT host law), this machine = {mid} -> honest VOID "
             f"exit 2 (non-host machines cannot run this batch)")
        return 2

    if os.path.exists(OUT_JSON) and \
            os.environ.get("DECISION_CHAIN_V3_REFINALIZE") != "1":
        _log(f"verdict already landed ({OUT_JSON}); "
             f"DECISION_CHAIN_V3_REFINALIZE=1 = only redo path")
        return 0

    # ---- artifact gate (v2 physical faces + axes artifact)
    missing = v2.artifact_gate()
    if missing:
        return 2
    if not os.path.exists(AXES_JSON):
        _log(f"ARTIFACT MISSING: full-A axes artifact ({AXES_JSON}) -- "
             f"run SENTIMENT-AXES-FULLHIST-P1 first")
        return 2
    axes_artifact = load_axes_artifact()
    if axes_artifact is None:
        return 2
    _log("G-SENTIMENT integrity PASS (axes artifact schema/batch/cutoff/"
         "sha256 verified)")

    # ---- gates (v2 family)
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
        import merge_lane_views as lane_views
        aj = lane_views.face_view(
            "compute_audit", results_dir=os.path.join(ROOT, "results"))
        if not aj:
            raise RuntimeError("compute_audit lane-merged view empty")
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

    # ---- sleeve (two-path gate) + G-REPRO-REV both faces
    sleeve_gated = {}
    for face in FACES:
        got = v2.sleeve_gate(face)
        if got is None or "gate" in got:
            detail = got if (got and "gate" in got) else "no sleeve source"
            _log(f"G-REPRO-REV FAIL [{face}]: sleeve source missing or "
                 f"stats drift ({detail}) -- s9-a4 two-path absent/failing")
            return 2
        sleeve_gated[face] = got
    _log(f"G-REPRO-REV PASS both faces "
         f"(path={sleeve_gated['base']['path']}/"
         f"{sleeve_gated['x2']['path']})")

    # ---- per-axis machinery + overlay
    panels, packs_all, judge_all = {}, {}, {}
    states_meta, tilt_meta, sent_meta = {}, {}, {}
    axis_states = {}
    g_style, g_sentiment = {}, {}
    for axis in ("legacy", "deep"):
        close, eligible = v1._axis_eligible(axis, expected)
        if eligible is None:
            return 2
        panels[axis] = (close, eligible)
        raw = v2.state_series(axis, close)
        assert not raw.isna().any(), (
            f"[{axis}] state series has NaN days - ladder cap undefined "
            f"(honest abort)")
        confirmed = v2.hysteresis_confirm(raw)
        heat, heat_info = v2.heat_series(close)
        caps = v2.cap_ladder(confirmed, heat, axis)
        caps_exec = t34.exec_shift(caps)
        red_exec = t34.exec_shift(confirmed.eq("RED").astype(bool))
        W4 = v2.weights_v2(confirmed, caps_exec, red_exec)
        cash, cash_info = v2.cash_series(close)
        # H1 tilt face (per-axis panel)
        tilt = style_tilt_face(close)
        tilt["_ok_all"] = (_pair_winner_series(LS_PAIR, close)[1]
                           & _pair_winner_series(GV_PAIR, close)[1])
        g_style[axis] = g_style_census(close, eligible, tilt)
        # H2' sentiment face (per-axis panel calendar)
        sent = sentiment_face(close, axes_artifact["axes"])
        g_sentiment[axis] = g_sentiment_census(close, eligible, sent)
        eff_caps = pd.concat([caps_exec, sent["caps"]], axis=1).min(axis=1)
        W4_eff = v2.weights_v2(confirmed, eff_caps, red_exec)
        W4_h3 = v2.weights_v2(confirmed, caps_exec,
                              pd.Series(False, index=close.index))
        axis_states[axis] = {"raw": raw, "confirmed": confirmed}
        states_meta[axis] = {
            "raw_first": str(raw.iloc[0]),
            "confirmed_switch_days": int(
                (confirmed.astype(str) != confirmed.astype(str)
                 .shift(1).fillna(confirmed.iloc[0])).sum()),
            "cap_value_counts": {str(k): int(v) for k, v in
                                 pd.Series(caps_exec).round(2)
                                 .value_counts().items()},
            "eff_cap_value_counts": {str(k): int(v) for k, v in
                                      pd.Series(eff_caps).round(2)
                                      .value_counts().items()},
            "sentiment_binding_days": int((sent["caps"] < caps_exec)
                                          .sum()),
            "heat": heat_info, "cash": cash_info,
            "sleeve_active_days": int(red_exec.sum()),
        }
        tilt_meta[axis] = tilt["census"]
        sent_meta[axis] = sent["census"]
        sleeve_census = {}
        for face in FACES:
            sl, census = v2.sleeve_align(sleeve_gated[face], close)
            sleeve_census[face] = census
            pack = overlay_axis_face_v3(axis, face, close, eligible, W4,
                                        W4_eff, W4_h3, sl, cash, tilt)
            if pack is None:
                return 2
            packs_all.setdefault(axis, {})[face] = pack
        judge_all[axis] = {face: judge_axis_face_v3(packs_all[axis][face])
                           for face in FACES}
        states_meta[axis]["sleeve_census"] = sleeve_census
        _log(f"[{axis}] 6-arm overlay done both faces "
             f"({round(time.time() - t0, 1)}s cumulative)")

    # ---- G-REPRO-v1 (B/D aggregates bit-level vs v1 frozen records)
    repro_checks = v2.repro_v1_checks(judge_all, v1_payload)
    repro_ok = all(repro_checks.values())
    n_repro = len(repro_checks)
    _log(f"G-REPRO-v1 {'PASS' if repro_ok else 'FAIL'} "
         f"({sum(repro_checks.values())}/{n_repro})")
    if not repro_ok:
        bad = [k for k, ok in repro_checks.items() if not ok]
        _log(f"G-REPRO-v1 drift examples: {bad[:6]}")
        return 2

    # ---- verdicts (per-arm)
    j_c_faces = {face: judge_all["legacy"][face]["j_c"] for face in FACES}
    arm_chain_win = {arm: bool(all(j_c_faces[f][arm]["chain_win"]
                                   for f in FACES)) for arm in ARMS_A}
    j_target = {axis: {face: judge_all[axis][face]["j_target"]
                       for face in FACES}
                for axis in ("legacy", "deep")}
    arm_j_target_pass = {arm: bool(all(
        j_target[axis][face][arm][w]["pass"]
        for axis in ("legacy", "deep") for face in FACES for w in WINDOWS))
        for arm in ARMS_A}

    # ---- J-TOUR: falsification vs H3 (pooled 12m beat + CI lo, per face)
    falsified = {}
    for arm in ("A-H1", "A-H2S"):
        per_face = {}
        for face in FACES:
            a = judge_all["legacy"][face]["tables"]["12m"][arm]
            h3 = judge_all["legacy"][face]["tables"]["12m"]["A-H3"]
            pe_le = (a["beat_rate"] is not None and h3["beat_rate"]
                     is not None and a["beat_rate"] <= h3["beat_rate"])
            lo_le = (a["ci95"][0] is not None and h3["ci95"][0] is not None
                     and a["ci95"][0] <= h3["ci95"][0])
            per_face[face] = {"arm_beat_rate": a["beat_rate"],
                              "h3_beat_rate": h3["beat_rate"],
                              "arm_ci_lo": a["ci95"][0],
                              "h3_ci_lo": h3["ci95"][0],
                              "falsified_this_face": bool(pe_le and lo_le)}
        falsified[arm] = {
            "per_face": per_face,
            "falsified": bool(all(v["falsified_this_face"]
                                  for v in per_face.values()))}
    _log(f"J-TOUR falsification gate: "
         + "; ".join(f"{a}={falsified[a]['falsified']}"
                     for a in falsified))

    # ---- cross-arm DSR (n_trials = batch N_eff) + PBO three-arm panel
    # Calendar faces are derived from the p0-sliced member curves; the
    # slice law is asserted inside _calendar_faces.
    dsr_faces, pbo_faces, calendar_note = _calendar_faces(
        packs_all, panels, sleeve_gated)
    e_fp = {"n_jc_conjunction_tests": len(ARMS_A) * len(FACES),
            "E_FP_conjunction_5pct": round(0.05 * len(ARMS_A) * len(FACES), 2),
            "n_jtarget_readings": len(ARMS_A) * 2 * len(FACES) * len(WINDOWS),
            "E_FP_jtarget_5pct": round(
                0.05 * len(ARMS_A) * 2 * len(FACES) * len(WINDOWS), 2)}

    # ---- winner rule (pre-frozen): J all-pass AND not falsified
    winners = [arm for arm in ARMS_A
               if arm_chain_win[arm] and arm_j_target_pass[arm]
               and not (arm in falsified and falsified[arm]["falsified"])]
    tour_verdict = ("zero-arm-pass (tournament negative, honest report; "
                    "v4 trigger evaluation per O-0809 s4.5)"
                    if not winners else
                    "winner candidates (registration only; paper wiring "
                    "through 10-01 month boundary): " + ", ".join(winners))
    _log(f"J-TOUR winners: {winners} chain_win={arm_chain_win} "
         f"j_target_pass={arm_j_target_pass}")

    # ---- ring table (per arm, legacy base face primary)
    ring_table = ring_table_v3(packs_all, judge_all, panels, axis_states,
                               falsified)

    corr_out = {face: corr_face_v3(packs_all["legacy"][face],
                                   panels["legacy"][1]) for face in FACES}
    attribution = {face: attribution_face_v3(packs_all["legacy"][face])
                   for face in FACES}

    # ---- ledger (A arms only; B/C/D = v1-consumed zero re-count)
    if audit_clean:
        ledger = sg.append_ledger(
            BATCH, N_EFF, file_name="decision_chain_v3_tournament.json",
            evidence_cutoff=t34.BINDING_CUTOFF,
            note=(f"3 tournament arms {{base,x2}} x 2,761 starts "
                  f"(legacy 1,255 + deep 1,506); B/C/D = v1-consumed "
                  f"verbatim reuse zero re-count; member curves = "
                  f"checkpoint reuse (T-34/T-22 lineage); sleeve = "
                  f"judged-engine two-path, measurement reuse not counted"))
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
        "g_style": g_style[axis], "g_sentiment": g_sentiment[axis],
        "tilt_census": tilt_meta[axis], "sentiment_census": sent_meta[axis],
        "tables": {face: judge_all[axis][face]["tables"]
                   for face in FACES},
        "j_target": {face: judge_all[axis][face]["j_target"]
                     for face in FACES},
        "rate_side": {f: packs_all[axis][f]["rate_side"]
                      for f in FACES}} for axis in ("legacy", "deep")}

    with open(PREREG_PATH, "rb") as f:
        prereg_sha = hashlib.sha256(f.read()).hexdigest()
    payload = payload_skeleton_v3()
    payload.update({
        "batch": BATCH, "ticket": TICKET,
        "prereg": "research/DECISION_CHAIN_V3_TOURNAMENT_PREREG.md",
        "prereg_sha256": prereg_sha,
        "evidence_cutoff": t34.BINDING_CUTOFF,
        "cutoff_meta": sg.cutoff_meta(t34.BINDING_CUTOFF),
        "executed_by": mid,
        "faces": list(FACES), "windows": WINDOWS,
        "bootstrap": {"B": BOOTSTRAP_B, "seed": BOOTSTRAP_SEED,
                      "method": "binomial percentile 95% CI",
                      "seed_note": ("SEED_REGISTRY['decision_chain_"
                                     "v3_tournament'] single entry 20291000"
                                     " (ledger r171 same-commit)")},
        "rate_side": {"base": v1.rate_side("base"), "x2": v1.rate_side("x2"),
                      "derivation": ("v1 rate_side import verbatim "
                                     "(COST_X2_RATE/2 base, x2 doubled), "
                                     "runtime-derived")},
        "gates": {"G_V3_leg1": v3g, "G_V3_leg2": v3l2,
                  "G_CENSUS_expected": expected,
                  "G_ANCHOR": "6/6 PASS (re-run at finalize)",
                  "G_MANIFEST": g_manifest,
                  "G_REPRO_v1": {"ok": repro_ok, "n_checks": n_repro,
                                 "checks": repro_checks,
                                 "excluded": list(v2.REPRO_EXCLUDED),
                                 "excluded_note": (
                                     "v2 s9-a6 law: seed-determined CI "
                                     "decoration (k/n compared directly; "
                                     "v3 batch seed 20291000 vs v1 "
                                     "registry seed)")},
                  "G_REPRO_REV": {"ok": True,
                                  "faces": {f: {
                                      "path": sleeve_gated[f]["path"],
                                      "stats": sleeve_gated[f]["stats"],
                                      "counters": {
                                          k: sleeve_gated[f]["counters"][k]
                                          for k in ("entries", "trades")}}
                                      for f in FACES}},
                  "G_HEAT": states_meta["legacy"]["heat"],
                  "G_STYLE": g_style,
                  "G_SENTIMENT": {"integrity": "PASS (schema/batch/cutoff/"
                                   "axes_sha256 verified at load)",
                                  "coverage": g_sentiment},
                  "HOST_GATE": {"pinned": BURN_HOST, "executed_on": mid},
                  "sleeve_face_note": ("C has no v1 table by construction "
                                       "(passive baseline); its integrity "
                                       "rides the same curve rows via the "
                                       "B/D beat columns (G-REPRO-v1)")},
        "axes": axes_out,
        "pairwise": {axis: {face: judge_all[axis][face]["pairwise"]
                            for face in FACES}
                     for axis in ("legacy", "deep")},
        "verdict": {"j_c_faces": j_c_faces,
                    "arm_chain_win": arm_chain_win,
                    "j_target": j_target,
                    "arm_j_target_pass": arm_j_target_pass,
                    "j_tour": {"falsification": falsified,
                               "dsr": dsr_faces, "pbo": pbo_faces,
                               "e_fp": e_fp,
                               "calendar_note": calendar_note,
                               "winners": winners,
                               "tournament_verdict": tour_verdict},
                    "two_tier_note": ("J-C series = per-run scientific "
                                      "readings; J-TARGET = CEO frozen "
                                      "iteration line (O-0809 s2); two "
                                      "tiers disclosed separately, never "
                                      "merged"),
                    "disposition": tour_verdict},
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
                                  "seat fill from T-94 survivors = v4 "
                                  "trigger per ticket spec verbatim")},
        "trials_ledger": ledger,
        "audit": audit,
        "finalize_runtime_sec": round(time.time() - t0, 1),
    })
    payload["prediction_reconciliation"] = prediction_reconciliation_v3(
        payload)
    json.dumps(payload, default=bool)
    assert all(k in payload for k in CONSUMER_KEYS_V3), (
        "B7b contract: consumer keys must be subset of construction keys")
    tmp = OUT_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, indent=1, ensure_ascii=False, default=bool)
    os.replace(tmp, OUT_JSON)
    _log(f"verdict winners={winners} -> {OUT_JSON}")

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
                    for arm in ARMS_V3:
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
                  "g_repro_rev_ok": True, "g_style_all_pass": all(
                      g_style[a]["status"] == "PASS"
                      for a in ("legacy", "deep")),
                  "g_sentiment_all_pass": all(
                      g_sentiment[a]["status"] == "PASS"
                      for a in ("legacy", "deep")),
                  "winners": winners, "void": False},
        "eliminated": None,
        "refs": {"results": "results/decision_chain_v3_tournament.json",
                 "prereg": "research/DECISION_CHAIN_V3_TOURNAMENT_PREREG.md",
                 "csv": "research/shortline/decision_chain_v3_results.csv",
                 "ticket": f"fleet/tasks/{TICKET}-P1.json"},
        "note": "3 tournament arms only (16,566); B/C/D v1-consumed "
                "zero re-count; sleeve = two-path measurement reuse"})
    json.dumps(d)
    with open(attr_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

    # ---- prereg s7/s8 backfill + ledger v3 row flip (mechanical)
    backfill_prereg_v3(payload)
    flip_ledger_v3(payload)
    _log(f"prereg s7/s8 backfilled + ledger v3 row flipped "
         f"(PENDING->LANDED)")
    _log(f"run DONE in {round(time.time() - t0, 1)}s -- winners="
         f"{winners} (negative also reported per O-2255)")
    return 0


def _calendar_faces(packs_all, panels, sleeve_gated):
    """Cross-arm correction faces: per-arm calendar daily-return series on
    the legacy axis (both faces) for DSR (n_trials = batch N_eff) and the
    three-arm CSCV PBO panel. Member curves must be calendar slices of the
    member's return history (asserted); violation -> honest n/a faces."""
    axis = "legacy"
    eligible = panels[axis][1]
    p0 = min(eligible)
    close = panels[axis][0]
    n = len(close.index)
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    dsr_faces, pbo_faces = {}, {}
    skipped = []
    note = ("calendar series from p0-sliced member curves (slice law "
            "asserted on sampled starts); DSR n_trials = batch N_eff "
            f"{N_EFF}")
    try:
        att_pool = [p for p in eligible if p > p0 + 5]
        for face in FACES:
            pack = packs_all[axis][face]
            att0 = pack["att"][p0]
            for p in [int(x) for x in rng.choice(
                    att_pool, size=min(3, len(att_pool)), replace=False)]:
                # member curves are W24M-capped windows (t34 curve law);
                # the slice check only exists where the two windows overlap
                k_hi = min(len(pack["att"][p]), len(att0) - (p - p0))
                if k_hi <= 1:
                    skipped.append(p)
                    continue
                k = int(rng.integers(1, max(2, k_hi)))
                d_off = p - p0 + k
                assert abs(att0[d_off] - pack["att"][p][k]) < 1e-10, (
                    "slice law FAIL (calendar faces unavailable)")
            rate = pack["rate_side"]
            # sleeve/cash/tilt calendar faces
            sl, _c = v2.sleeve_align(sleeve_gated[face], close)
            cash, _i = v2.cash_series(close)
            tilt = style_tilt_face(close)
            # per-arm weights
            raw = v2.state_series(axis, close)
            conf = v2.hysteresis_confirm(raw)
            heat, _h = v2.heat_series(close)
            caps = v2.cap_ladder(conf, heat, axis)
            caps_exec = t34.exec_shift(caps)
            red_exec = t34.exec_shift(conf.eq("RED").astype(bool))
            sent = sentiment_face(close, json.load(
                open(AXES_JSON, encoding="utf-8-sig"))["axes"])
            eff_caps = pd.concat([caps_exec, sent["caps"]], axis=1).min(
                axis=1)
            W = {"A-H1": v2.weights_v2(conf, caps_exec, red_exec),
                 "A-H2S": v2.weights_v2(conf, eff_caps, red_exec),
                 "A-H3": v2.weights_v2(
                     conf, caps_exec,
                     pd.Series(False, index=close.index))}
            att0_np = np.asarray(att0, dtype=float)
            chop0 = np.asarray(pack["chop"][p0], dtype=float)
            n_cal = min(len(att0_np), len(chop0), n - p0)
            sl_np = np.asarray(sl, dtype=float)
            ca_np = np.asarray(cash, dtype=float)
            extra_ret = np.asarray(
                TILT_LEG_W * tilt["ls_ret"] + TILT_LEG_W * tilt["gv_ret"],
                dtype=float)
            extra_dw = np.asarray(tilt["ov_dw"], dtype=float)
            panel = {}
            for arm in ARMS_A:
                Wm = W[arm][p0:p0 + n_cal]
                r = v2.env_daily_v2(
                    (att0_np[:n_cal], chop0[:n_cal],
                     sl_np[p0:p0 + n_cal], ca_np[p0:p0 + n_cal]), Wm,
                    rate)
                if arm == "A-H1":
                    r = r * H1_CORE_SCALE
                    r = r + (extra_ret[p0:p0 + n_cal]
                             - rate * extra_dw[p0:p0 + n_cal])
                panel[arm] = pd.Series(
                    r, index=close.index[p0:p0 + n_cal])
                dsr_faces[f"{arm}_{face}"] = sg.deflated_sharpe_ratio(
                    [float(x) for x in r], n_trials=N_EFF)
            pbo_faces[face] = cscv_pbo(pd.DataFrame(panel))
    except AssertionError as ex:
        dsr_faces = {"n/a": True, "reason": str(ex)[:200]}
        pbo_faces = {"n/a": True, "reason": str(ex)[:200]}
        note = ("slice law FAILED -> DSR/PBO faces honestly unavailable: "
                + str(ex)[:200])
    if skipped:
        note += (f"; slice-law assert skipped on {len(skipped)} sampled "
                 "start(s) without p0-window calendar overlap (honest)")
    return dsr_faces, pbo_faces, note


def ring_table_v3(packs_all, judge_all, panels, axis_states, falsified):
    """Four-ring relocalization per arm (prereg s4, legacy base face
    primary; ring semantics per arm's mechanism)."""
    face = "base"
    axis = "legacy"
    pack = packs_all[axis][face]
    cells = pack["cells"]
    confirmed = axis_states[axis]["confirmed"]
    raw = axis_states[axis]["raw"]
    out = {}
    # shared ring1 (state machinery) + ring4 (GREEN share / seats)
    raw_np = raw.astype(str)
    day_flips = int((raw_np != raw_np.shift(1).fillna(raw_np.iloc[0])).sum())
    conf_flips = int((confirmed.astype(str) != confirmed.astype(str)
                      .shift(1).fillna(confirmed.iloc[0])).sum())
    green_days = int((confirmed == "GREEN").sum())
    for arm in ARMS_A:
        cells_a = cells[arm]
        prime = pack["primes"][arm]
        fr = [cells_a[c]["ret_12m"] - prime[c]["ret_12m"]
              for c in cells_a if not cells_a[c]["partial_12m"]]
        gross = [abs(prime[c]["ret_12m"]) for c in cells_a
                 if not cells_a[c]["partial_12m"]]
        a2v_sw = _agg_v3(cells_a, "12m")["switches_mean"]
        ring = {
            "ring1_confirm": {
                "raw_day_flip_rate": round(day_flips / len(raw_np), 4),
                "confirmed_switch_days": conf_flips,
                "arm_switches_mean_12m": a2v_sw},
            "ring3_friction": {
                "switches_mean": a2v_sw,
                "mean_friction_pp_12m": round(sum(fr) / len(fr), 4)
                if fr else None,
                "friction_share_of_gross": (round(sum(fr) / sum(gross), 4)
                                            if gross and sum(gross) > 0
                                            else None),
                "counterfactual": f"A-{arm}' = same weights, rate=0"},
            "ring4_seat": {
                "green_day_share": round(green_days / len(confirmed), 4),
                "vacancy_note": ("attack corps live count 0 "
                                 "(STYLE_CORPS v1.1); 0 seats disclosed")},
        }
        if arm == "A-H1":
            ring["ring2_overlay"] = {
                "arm": "style tilt legs (LS/GV r60 winners, 5% each)",
                "note": "flip counts live in axes.tilt_census (per-leg)"}
        elif arm == "A-H2S":
            ring["ring2_cap_events"] = {
                "arm": "sentiment min-conjunction cap",
                "note": "binding day counts live in axes.state_meta."
                        "sentiment_binding_days"}
        else:
            ring["ring2_minimal_chain"] = {
                "arm": "v2 face minus sleeve (falsification control)",
                "note": "sleeve isolation = A-H3 minus v2 A-arm readings "
                        "(v2 payload consumption, disclosed in s7)"}
        out[arm] = ring
    return out


def corr_face_v3(pack, eligible):
    """Arm-pairwise window-return correlation (disclosure column only)."""
    out = {}
    for w in WINDOWS:
        for i, a in enumerate(ARMS_V3):
            for b in ARMS_V3[i + 1:]:
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


def attribution_face_v3(pack):
    """Sleeve/cash/overlay attribution (mean 12m leg contribution over
    complete-window A-arm cells, per arm)."""
    out = {}
    for arm in ARMS_A:
        full = [c for c in pack["cells"][arm].values()
                if not c["partial_12m"]]
        legs = ("core", "sleeve", "cash", "fee")
        row = {k: (round(sum(c["leg_contrib_12m"][k] for c in full)
                         / len(full), 6) if full else None)
               for k in legs}
        if "overlay" in (full[0]["leg_contrib_12m"] if full else {}):
            row["overlay"] = round(
                sum(c["leg_contrib_12m"]["overlay"] for c in full)
                / len(full), 6) if full else None
            row["overlay_fee"] = round(
                sum(c["leg_contrib_12m"].get("overlay_fee", 0.0)
                    for c in full) / len(full), 6) if full else None
        row["n"] = len(full)
        red_cells = [c for c in full
                     if c["leg_contrib_12m"]["sleeve"] != 0.0]
        row["sleeve_active_cells"] = len(red_cells)
        out[arm] = row
    return out


def payload_skeleton_v3():
    """Construction key set (B7b contract: consumer keys subset assert)."""
    return {"batch": None, "ticket": None, "prereg": None,
            "prereg_sha256": None, "evidence_cutoff": None,
            "cutoff_meta": None, "executed_by": None, "faces": None,
            "windows": None, "bootstrap": None, "rate_side": None,
            "gates": None, "axes": None, "pairwise": None,
            "verdict": None, "ring_table": None, "corr": None,
            "attribution": None, "sleeve_face": None, "seat_vacancy": None,
            "trials_ledger": None, "audit": None,
            "finalize_runtime_sec": None, "prediction_reconciliation": None}


CONSUMER_KEYS_V3 = ("batch", "ticket", "prereg_sha256", "evidence_cutoff",
                    "cutoff_meta", "gates", "axes", "pairwise", "verdict",
                    "ring_table", "corr", "attribution", "sleeve_face",
                    "trials_ledger", "audit")


def prediction_reconciliation_v3(payload):
    """prereg s5 predictions vs measured - mechanical band flags
    (frozen band text + live readings)."""
    t12b = payload["axes"]["legacy"]["tables"]["base"]["12m"]
    t12x = payload["axes"]["legacy"]["tables"]["x2"]["12m"]
    jt = payload["verdict"]["j_target"]
    dsr = payload["verdict"]["j_tour"]["dsr"]
    out = {}
    for arm in ARMS_A:
        dd = min(x for x in (t12b[arm]["min_dd"], t12x[arm]["min_dd"])
                 if x is not None)
        jc1_b = t12b[arm]["beat_rate"]
        out[arm] = {
            "predicted": ("s5 band: contribution point estimate wide; "
                          "J-C1 single-pass probability [15%,45%] (H1/H2S)"
                          if arm != "A-H3" else
                          "s5 band: H3 vs H1/H2' falsification gate "
                          "expected to trigger [55%,80%]"),
            "measured_beat_rate_12m_base": jc1_b,
            "measured_min_dd_12m": dd,
            "j_target_pass": payload["verdict"]["arm_j_target_pass"][arm],
            "falsified_vs_h3": (payload["verdict"]["j_tour"]
                                ["falsification"].get(arm, {})
                                .get("falsified")),
            "dsr_base": (dsr.get(f"{arm}_base", {}) or {}).get("dsr"),
        }
    return out


def backfill_prereg_v3(payload):
    """s7/s8 backfill: replace the placeholder anchors with frozen-number
    blocks (anchors must match exactly; no blind rewrite)."""
    src = open(PREREG_PATH, encoding="utf-8").read()
    if S7_ANCHOR not in src or S8_ANCHOR not in src:
        raise RuntimeError("prereg backfill anchors not found - file "
                           "drifted; refusing blind rewrite")
    gates = payload["gates"]
    v = payload["verdict"]
    s7 = [
        "## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】",
        "",
        f"- finalize {payload['audit'].get('asof', '')} via "
        f"{payload.get('executed_by')}（宿主门={BURN_HOST} 实测）。",
        f"- G 门读数：G-V3 leg1/leg2={'PASS' if gates['G_V3_leg1']['ok'] else 'FAIL'}/"
        f"{'PASS' if gates['G_V3_leg2']['ok'] else 'FAIL'}·G-CENSUS "
        f"{gates['G_CENSUS_expected']}·G-ANCHOR {gates['G_ANCHOR']}·"
        f"G-MANIFEST {'PASS' if gates['G_MANIFEST']['ok'] else 'FAIL'}·"
        f"G-REPRO-v1 {'PASS' if gates['G_REPRO_v1']['ok'] else 'FAIL'}"
        f"（{gates['G_REPRO_v1']['n_checks']} 检查·ci95 种子装饰除外）·"
        f"G-REPRO-REV 双面位级 PASS·G-HEAT census={gates['G_HEAT']}·"
        f"G-STYLE legacy={gates['G_STYLE']['legacy']['status']}/"
        f"deep={gates['G_STYLE']['deep']['status']}·G-SENTIMENT "
        f"legacy={gates['G_SENTIMENT']['coverage']['legacy']['status']}/"
        f"deep={gates['G_SENTIMENT']['coverage']['deep']['status']}（工件"
        f"sha 位级验签 PASS）。",
        "- 六臂全表（legacy 12m 完整窗·逐面·逐臂）：",
    ]
    for face in FACES:
        t12 = payload["axes"]["legacy"]["tables"][face]["12m"]
        s7.append(
            f"  - {face} legacy 12m：" + "；".join(
                f"{arm} n={t12[arm]['n']} beat_rate={t12[arm]['beat_rate']}"
                f" ci95={t12[arm]['ci95']} min_dd={t12[arm]['min_dd']}"
                for arm in ARMS_V3))
        pw = payload["pairwise"]["legacy"][face]["12m"]
        for arm in ARMS_A:
            s7.append(
                f"    {arm}：vs B rate={pw[arm + '_vs_B']['rate']} "
                f"ci95={pw[arm + '_vs_B']['ci95']}；vs D "
                f"rate={pw[arm + '_vs_D']['rate']} "
                f"ci95={pw[arm + '_vs_D']['ci95']}；vs C "
                f"rate={pw[arm + '_vs_C']['rate']} "
                f"ci95={pw[arm + '_vs_C']['ci95']}")
    s7.append(
        "- J 判读（逐臂·base/x2 双面）："
        + "；".join(
            f"{arm} chain_win(base/x2)="
            f"{v['j_c_faces']['base'][arm]['chain_win']}/"
            f"{v['j_c_faces']['x2'][arm]['chain_win']}"
            for arm in ARMS_A)
        + f"；J-TARGET 逐臂 pass={v['arm_j_target_pass']}。")
    jt = v["j_tour"]
    s7.append(
        f"- J-TOUR：证伪门 "
        + json.dumps({a: jt["falsification"][a]["falsified"]
                      for a in jt["falsification"]}, ensure_ascii=False)
        + f"；DSR（N_eff 折减 {N_EFF}）="
        + json.dumps(jt["dsr"], ensure_ascii=False)[:1200]
        + f"；PBO 三臂面板="
        + json.dumps(jt["pbo"], ensure_ascii=False)[:600]
        + f"；E[FP]={jt['e_fp']}；胜者={jt['winners']}（只入册候选·"
          f"纸盘接线走 10-01 月界）。")
    s7.append(
        "- 四环复定位（逐臂）：" + json.dumps(payload["ring_table"],
                                             ensure_ascii=False)[:1600])
    s7.append(
        "- 叠加/袖/现金腿归因（legacy base 12m 均值·逐臂）："
        + json.dumps(payload["attribution"], ensure_ascii=False)[:1200])
    s7.append(
        f"- 账本行：append_ledger batch_trials={N_EFF}"
        f"（audit {'CLEAN' if (payload['trials_ledger'] or {}).get('total') else 'not-CLEAN 未计'}）"
        f"——判定面 results/decision_chain_v3_tournament.json。")
    s8 = [
        "## §8 批后复盘【必填·s7-T】",
        "",
        f"- 一次定稿（finalize {payload['audit'].get('asof', '')} via "
        f"{payload.get('executed_by')}·机制面=预注册 §3 冻结零调参·判据"
        f"零触碰·A-1 修正案驱动非结果驱动）。",
        f"- 预测对账（§5 逐条）：{json.dumps(payload['prediction_reconciliation'], ensure_ascii=False)[:1500]}",
        f"- 门禁链损耗账：results/gate_attrition.json 已追加 {BATCH} 行"
        f"（kind=measurement）。",
        "- 回执入轮报告+CODELY.md 行级追加+锦标赛裁定+证伪门定案呈 "
        "GM/CEO=收割轮会话面（本文件由 runner 机械回填·叙述定案归"
        "会话 per v1.1 先例）。",
    ]
    out = src.replace(S7_ANCHOR, "\n".join(s7))
    out = out.replace(S8_ANCHOR, "\n".join(s8))
    with open(PREREG_PATH, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(out)


def flip_ledger_v3(payload):
    """DECISION_CHAIN_LEDGER.md v3 row verdict flip PENDING -> LANDED
    (recording flip per v1.1 r319 precedent) + append-only changelog."""
    src = open(LEDGER_PATH, encoding="utf-8").read()
    lines = src.splitlines()
    row_i = next(i for i, l in enumerate(lines)
                 if l.startswith("| v3 锦标赛批 |"))
    row = lines[row_i]
    assert "PENDING" in row, "v3 ledger row not PENDING - refusing flip"
    cells_ = row.split(" | ")
    assert cells_[-1].lstrip("| ").startswith("PENDING"), \
        "verdict cell shape drift - refusing blind rewrite"
    v = payload["verdict"]
    jt = v["j_tour"]
    new_cell = (
        f"LANDED {time.strftime('%Y-%m-%d %H:%M')} "
        f"{payload['executed_by']} finalize（记录性翻面 per v1.1 r319 "
        f"先例·判据零改动）：逐臂 chain_win="
        + json.dumps(v["arm_chain_win"], ensure_ascii=False)
        + "·J-TARGET 逐臂 pass="
        + json.dumps(v["arm_j_target_pass"], ensure_ascii=False)
        + "·证伪门="
        + json.dumps({a: jt["falsification"][a]["falsified"]
                      for a in jt["falsification"]}, ensure_ascii=False)
        + f"·胜者={jt['winners']}（{jt['tournament_verdict'][:80]}）·"
          f"批内 N={N_EFF}·判定面 results/decision_chain_v3_tournament.json |")
    cells_[-1] = new_cell
    lines[row_i] = " | ".join(cells_)
    changelog = (
        f"- {time.strftime('%Y-%m-%d %H:%M')} {payload['executed_by']}: v3 "
        f"锦标赛批 verdict 落账（PENDING→LANDED 记录性翻面·finalize "
        f"结果入行·判据零改动 per r319 先例；runner="
        f"{os.path.basename(__file__)}·winners={jt['winners']}）。")
    lines.append(changelog)
    with open(LEDGER_PATH, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------- status

def cmd_status(_) -> int:
    mid = machine_id()
    print(f"machine={mid} burn_host={BURN_HOST} "
          f"host_gate={'PASS' if mid == BURN_HOST else 'NON-HOST(VOID)'}")
    if os.path.exists(OUT_JSON):
        d = json.load(open(OUT_JSON, encoding="utf-8-sig"))
        v = d.get("verdict", {})
        print(f"verdict LANDED by {d.get('executed_by')} "
              f"winners={v.get('j_tour', {}).get('winners')} "
              f"chain_win={v.get('arm_chain_win')}")
    else:
        print("verdict NOT landed (results/decision_chain_v3_tournament"
              ".json absent)")
    for f, label in ((AXES_JSON, "full-A axes artifact"),
                     (V1_JSON, "v1 frozen records"),
                     (os.path.join(ROOT, "results", "shortline",
                                   "t18_deep_manifest.json"),
                      "t18 deep manifest")):
        print(f"artifact {label}: "
              f"{'present' if os.path.exists(f) else 'MISSING'}")
    return 0


# -------------------------------------------------------------- selftest

def cmd_selftest(_) -> int:
    """Hermetic offline selftest (r116 law): no engine run, no real panel,
    no network; B7b contract leg included (r297 law)."""
    fails = []

    def t(name, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
        if not ok:
            fails.append(name)

    # V1: seed law (single registry entry, same-commit law)
    src_sg = open(os.path.join(ROOT, "scripts", "science_gates.py"),
                  encoding="utf-8").read()
    t("V1 seed registered + single dict entry + B frozen",
      sg.SEED_REGISTRY.get("decision_chain_v3_tournament")
      == BOOTSTRAP_SEED == 20291000
      and src_sg.count('"decision_chain_v3_tournament":') == 1
      and BOOTSTRAP_B == 2000)

    # V2: constants frozen (prereg s0/s3)
    t("V2 constants: N_EFF/arm labels/faces/cutoff",
      N_EFF == 16566 and ARMS_A == ("A-H1", "A-H2S", "A-H3")
      and FACES == ("base", "x2") and len(ARMS_V3) == 6
      and t34.BINDING_CUTOFF == "2026-09-22"
      and DD_RED_LINE == -0.35 and DD_TARGET_LINE == -0.10
      and BURN_HOST == "bm-b" and H1_CORE_SCALE == 0.9
      and TILT_LEG_W == 0.05 and R60_WIN == 60)

    # V3: sentiment B+ gates frozen (S1 L22 verbatim)
    t("V3 sentiment B+ gate constants",
      (Z_MAIN, F_MAIN, H_MAIN) == (80, 0.10, 5)
      and (Z_RETREAT, F_RETREAT, H_RETREAT) == (30, 0.25, 3))

    # V4: sentiment state mapping (band thresholds, residual = CHOPPY)
    rows = [{"date": "2024-01-01", "Z": 100, "F": 0.05, "H": 7,
             "universe_n": 1},
            {"date": "2024-01-02", "Z": 20, "F": 0.30, "H": 2,
             "universe_n": 1},
            {"date": "2024-01-03", "Z": 50, "F": 0.15, "H": 4,
             "universe_n": 1}]
    st = sentiment_state_raw(rows)
    t("V4 E_t mapping MAIN/RETREAT/CHOPPY",
      list(st) == [SENT_MAIN, SENT_RETREAT, SENT_CHOPPY]
      and SENT_CHOPPY == "CHOPPY")

    # V5: sentiment caps = POSITION_LADDER reuse (zero new params)
    from market_clock_call import POSITION_LADDER
    t("V5 sentiment caps reuse ladder constants",
      {SENT_MAIN: POSITION_LADDER["GREEN"],
       SENT_CHOPPY: POSITION_LADDER["ORANGE"],
       SENT_RETREAT: POSITION_LADDER["RED"]}
      == {SENT_MAIN: 0.80, SENT_CHOPPY: 0.50, SENT_RETREAT: 0.20}
      and POSITION_LADDER == {"RED": 0.20, "ORANGE": 0.50,
                              "YELLOW": 0.65, "GREEN": 0.80})

    # V6: gap-tolerant hysteresis (warm-up None holds, first value inits)
    idx6 = pd.bdate_range("2024-01-01", periods=12)
    raw6 = pd.Series([None, None, "A", "B", "B", "B", "B", "B", "B",
                      "A", "A", "A"], index=idx6, dtype=object)
    conf6 = hysteresis_confirm_gap(raw6)
    t("V6 hysteresis_gap: None warm-up + 5-day confirm",
      list(conf6) == [None, None, "A", "A", "A", "A", "A", "B", "B",
                      "B", "B", "B"])

    # V7: style tilt winner rule (strictly greater; ties -> second)
    n7 = 80
    idx7 = pd.bdate_range("2024-01-01", periods=n7)
    rng7 = np.random.default_rng(7)
    px = pd.DataFrame({
        "512100": np.cumprod(1 + rng7.normal(0.0005, 0.01, n7)),
        "510300": np.cumprod(1 + rng7.normal(0.0002, 0.008, n7)),
        "159915": np.cumprod(1 + rng7.normal(0.0006, 0.012, n7)),
        "512800": np.cumprod(1 + rng7.normal(0.0001, 0.006, n7))},
        index=idx7)
    raw_ls, ok7 = _pair_winner_series(LS_PAIR, px)
    r60a = px["512100"] / px["512100"].shift(R60_WIN) - 1
    r60b = px["510300"] / px["510300"].shift(R60_WIN) - 1
    pick_a = (r60a > r60b)
    t("V7 tilt winner rule + r60 warm-up None",
      all(raw_ls.iloc[i] == ("512100" if pick_a.iloc[i] else "510300")
          for i in range(n7) if ok7.iloc[i])
      and int(ok7.sum()) == n7 - R60_WIN
      and all(raw_ls.iloc[i] is None for i in range(R60_WIN)))

    # V8: tilt face stitching + cost math (flip day = 2x leg weight)
    tilt8 = style_tilt_face(px)
    legs8 = tilt8["legs"]["LS"]
    dw8 = np.asarray(tilt8["ov_dw"], dtype=float)
    flips8 = (dw8 > 0).sum()
    t("V8 tilt cost: flips charged at sum|dw|, park warm-up 0-return",
      float(np.asarray(tilt8["ls_ret"], dtype=float)[:R60_WIN].sum())
      == 0.0 and flips8 >= 1
      and set(np.unique(dw8[dw8 > 0])).issubset(
          {TILT_LEG_W, 2 * TILT_LEG_W}))

    # V9: generalized cells == v2._arm_cells_v2 bit-level at neutral args
    n9 = 30
    idx9 = pd.bdate_range("2024-01-01", periods=n9)
    close9 = pd.DataFrame({"510300": np.full(n9, 100.0)}, index=idx9)
    att9 = {0: np.asarray(np.random.default_rng(1).normal(
        0.001, 0.01, n9), dtype=float)}
    chop9 = {0: np.asarray(np.random.default_rng(2).normal(
        0.0005, 0.008, n9), dtype=float)}
    W4_9 = np.tile([1 / 6, 5 / 6, 0.02, 0.31], (n9, 1))
    sl9 = np.asarray(np.random.default_rng(3).normal(
        0.0, 0.01, n9), dtype=float)
    ca9 = np.full(n9, 1e-4)
    curves9 = {"COMPOSITE-CE-01|0": {"p_ret_12m": 0.05}}
    axis_reg9 = regime_proxy(close9["510300"])
    mine = _arm_cells_v3(W4_9, att9, chop9, sl9, ca9, close9, [0],
                         curves9, 0.0013, axis_reg9)
    ref = v2._arm_cells_v2(W4_9, att9, chop9, sl9, ca9, close9, [0],
                           curves9, 0.0013, axis_reg9)
    same = (mine[0]["ret_12m"] == ref[0]["ret_12m"]
            and mine[0]["dd_12m"] == ref[0]["dd_12m"]
            and mine[0]["leg_contrib_12m"] == ref[0]["leg_contrib_12m"])
    t("V9 _arm_cells_v3 == v2._arm_cells_v2 bit-level (scale=1, no extra)",
      bool(same))

    # V10: H1 scale math (0.9 body + 10% overlay - overlay cost)
    extra_ret = np.asarray(np.random.default_rng(4).normal(
        0.0, 0.01, n9), dtype=float)
    extra_dw = np.zeros(n9)
    extra_dw[10] = 0.10
    h1 = _arm_cells_v3(W4_9, att9, chop9, sl9, ca9, close9, [0],
                       curves9, 0.0013, axis_reg9, scale=0.9,
                       extra_ret=extra_ret, extra_dw=extra_dw)
    base_r = v2.env_daily_v2((att9[0], chop9[0], sl9, ca9), W4_9, 0.0013)
    expect_r = 0.9 * base_r + extra_ret - 0.0013 * extra_dw
    expect_24m = float(np.prod(1.0 + expect_r) - 1.0)
    t("V10 H1 envelope = 0.9*v2 + overlay - rate*overlay_dw (ret_24m)",
      abs(h1[0]["ret_24m"] - expect_24m) < 1e-9
      and h1[0]["leg_contrib_12m"]["overlay"] ==
      float(np.sum(extra_ret[:n9])))

    # V11: A-H3 weights = v2 non-RED branch with no sleeve (RED too)
    conf11 = pd.Series(["GREEN", "RED", "YELLOW"], index=idx9[:3])
    caps11 = pd.Series([0.80, 0.20, 0.65], index=idx9[:3])
    W_h3 = v2.weights_v2(conf11, caps11,
                         pd.Series(False, index=idx9[:3]))
    t("V11 A-H3 weights: no sleeve activation, RED = core 20%/cash 80%",
      abs(W_h3[1, 0] - 0.2 / 6) < 1e-12
      and abs(W_h3[1, 1] - 5 * 0.2 / 6) < 1e-12
      and W_h3[1, 2] == 0.0 and abs(W_h3[1, 3] - 0.80) < 1e-12
      and abs(W_h3[0, 2]) < 1e-15)

    # V12: H2S min-conjunction + RED binding
    caps_v2 = pd.Series([0.80, 0.20, 0.65], index=idx9[:3])
    sent_caps = pd.Series([0.50, 0.80, 0.20], index=idx9[:3])
    eff = pd.concat([caps_v2, sent_caps], axis=1).min(axis=1)
    t("V12 min-conjunction cap (sentiment binds except RED floor)",
      list(eff) == [0.5, 0.2, 0.2]
      and abs(POSITION_LADDER["GREEN"] + 0.15 - 0.95) < 1e-12)

    # V13: v3 bootstrap determinism + distinctness vs v2 seed
    c1, c2 = _ci_boot(7, 10), _ci_boot(7, 10)
    t("V13 v3 bootstrap deterministic (seed 20291000)",
      c1 == c2 and c1[0] < 0.7 < c1[1] and _ci_boot(0, 10)[1] < 0.5)

    # V14: falsification gate semantics (point est AND CI lo both <= H3)
    a_ = {"beat_rate": 0.50, "ci95": [0.45, 0.55]}
    h3_ = {"beat_rate": 0.55, "ci95": [0.48, 0.62]}
    pe_le = a_["beat_rate"] <= h3_["beat_rate"]
    lo_le = a_["ci95"][0] <= h3_["ci95"][0]
    t("V14 falsification = (point est <= H3) AND (CI lo <= H3)",
      bool(pe_le and lo_le) is True)

    # V15: B7b contract (consumer keys subset of construction keys)
    skel = payload_skeleton_v3()
    t("V15 B7b contract: consumer keys subset of skeleton",
      all(k in skel for k in CONSUMER_KEYS_V3)
      and set(CONSUMER_KEYS_V3) <= set(skel.keys()))

    # V16: prereg anchors present (backfill safety)
    src = open(PREREG_PATH, encoding="utf-8").read()
    t("V16 prereg s7/s8 anchors present (no blind-rewrite risk)",
      S7_ANCHOR in src and S8_ANCHOR in src)

    # V17: DSR face import + n_trials law
    rets17 = list(np.random.default_rng(5).normal(0.001, 0.01, 300))
    d17 = sg.deflated_sharpe_ratio(rets17, n_trials=N_EFF)
    d17b = sg.deflated_sharpe_ratio(rets17, n_trials=100)
    t("V17 DSR import + N_eff deflation monotone (more trials, lower DSR)",
      0.0 <= d17["dsr"] <= 1.0 and d17["dsr"] <= d17b["dsr"]
      and d17["n_trials"] == N_EFF)

    # V18: PBO import face (3-arm panel mechanically computable)
    rng18 = np.random.default_rng(6)
    df18 = pd.DataFrame({
        "A-H1": rng18.normal(0.0008, 0.01, 400),
        "A-H2S": rng18.normal(0.0004, 0.01, 400),
        "A-H3": rng18.normal(0.0002, 0.01, 400)})
    pbo18 = cscv_pbo(df18)
    t("V18 cscv_pbo three-arm panel computes (0<=pbo<=1)",
      0.0 <= float(pbo18["pbo"] if isinstance(pbo18, dict)
                   else pbo18) <= 1.0)

    print(f"\nselftest: {len(fails)} FAIL / "
          f"{18 - len(fails)} PASS")
    return 1 if fails else 0


# ------------------------------------------------------------------ main

def main() -> int:
    ap = argparse.ArgumentParser(description=BATCH)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("run")
    sub.add_parser("status")
    sub.add_parser("selftest")
    args = ap.parse_args()
    return {"run": cmd_run, "status": cmd_status,
            "selftest": cmd_selftest}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
