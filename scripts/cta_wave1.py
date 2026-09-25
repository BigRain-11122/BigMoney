"""CTA_WAVE1 batch runner — 波-1 期货复活批: 26 candidates + 50 nulls + 2 passives (78 cells).

Prereg: research/CTA_WAVE1_PREREG.md (frozen R186, git-blob sha256
b5bed148df2175c128acb183643d6b817f72dcce632eb5da44457bd921026ce9; integrity
asserted at run, CRLF->LF normalized per R140 law).
Domain: 10-variety main-continuous futures panel (9 in-rail + TS leg), union
window 2008-01-09 -> 2026-09-24 (deep-history dimension; honest 18.7y boundary,
25y unreachable on this data face -- prereg SS2), OHLCV-only signal inputs,
roll-gap V0 direct-use, futures-domain own null pool + deep-panel passive
skill line (pool cta_wave1; no cross-pool borrowing).

Legs (prereg SS3):
  A  8 new trend patterns x {daily, r20}            -> 16 cells
  B  4 vol-target/tsmom bases x margin-cap {50,30}  ->  8 cells (daily only)
  C  2 basis-carry (IF/510300, IC/510500 proxies)   ->  2 cells (daily, 2020+)
  +  K=50 random nulls (seed SEED_REGISTRY cta_wave1 = 62_000 + k)
  +  2 passive long baselines (r20 / monthly)        -> 78 cells

Subcommands:
  gates    G0 smoke / G1 engine selftest (incl. wave1 additive legs) / G2 TS
           exchange-verified constants / G3 data completeness (18-cell frozen
           exemption, exact probe-p2 semantics) / G4 null determinism
  run      full batch (gates re-run inside; aborts exit 2 on any FAIL)
  selftest offline unit tests (synthetic panels; no data files needed)

Ledger: science_gates.append_ledger("cta_wave1", 78, ...,
          evidence_cutoff="2026-09-24").
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "screening"))

import numpy as np
import pandas as pd

from engine import futures_runner as fr
from engine.futures_runner import FUT_META
import science_gates as sg
import cta_p1_screen as p1      # reuse CTA_P1 builders (prereg SS6 zero-rewrite)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREREG_PATH = os.path.join(ROOT, "research", "CTA_WAVE1_PREREG.md")
G2_EVIDENCE_PATH = os.path.join(ROOT, "results", "cta_wave1_g2_ts_check.json")
RESULTS_JSON = os.path.join(ROOT, "results", "shortline_cta_wave1.json")
RESULTS_CSV = os.path.join(ROOT, "research", "cta_wave1_results.csv")
ATTRITION_JSON = os.path.join(ROOT, "results", "gate_attrition.json")

CUTOFF = "2026-09-24"          # evidence_cutoff (09-25 Mid-Autumn holiday, no bar)
WINDOW_START = "2008-01-09"    # panel union start (AU first bar; prereg SS2)
DEEP_END = "2016-12-31"        # deep-window segment end (concentration disclosure)
WIDE_START = "2017-01-01"
IS2_START = "2025-01-01"
FROZEN_PREREG_SHA = "b5bed148df2175c128acb183643d6b817f72dcce632eb5da44457bd921026ce9"
SEED_BASE = 62_000            # SEED_REGISTRY["cta_wave1"] (frozen at prereg R186)
K_NULLS = 50
BATCH_CELLS = 78               # 26 candidates + 50 nulls + 2 passives
START_CASH = 10_000_000.0      # CTA_P1 convention (whole-lot granularity note)
VARIETIES = list(FUT_META)     # 10 with TS (additive R187)
DEEP_WINDOW_NOTE = ("2008-2016 deep segment = 1-2 alive varieties (AU/RB) "
                    "high-concentration ledger; full-period pooled is the "
                    "judgement face, deep/wide split is descriptive (prereg SS2)")

# G2 TS constants frozen from CFFEX official faces 2026-09-25 (R169/R173;
# evidence results/cta_wave1_g2_ts_check.json): /cn/2ts.html contract table
# + /sj/jscs settlement-params CSV (fee 3 yuan/lot). tick frozen at VERIFIED
# 0.002 (prereg provisional 0.005, 150% deviation > 30% -> freeze-verified
# protocol per prereg SS3 G2).
TS_FROZEN_VERIFIED = {"mult": 20000.0, "margin": 0.005, "fee_lot": 3.0,
                      "tick": 0.002, "limit": 0.005}

# G3 frozen source-gap exemption (prereg SS2 condition (2); 18 cells; probe
# p2 semantics: vs-union-calendar in-span holes, full enumeration R186 law)
EXEMPT_CELLS = (
    {(d, v) for d in ("2017-10-09",) for v in ("IF", "IC", "IH", "T", "TF")} |
    {(d, v) for d in ("2019-04-22",) for v in ("AU", "RB", "SC")} |
    {(d, "RB") for d in ("2009-05-01", "2010-05-03", "2010-10-07", "2013-09-19",
                         "2013-10-01", "2013-11-20", "2014-01-16", "2014-03-07",
                         "2014-03-13", "2015-07-02")}
)

SPOT_PROXY = {"basis_if_510300": ("IF", "510300"),
              "basis_ic_510500": ("IC", "510500")}


def _sha256_lf_normalized(path: str) -> str:
    """R140 law: frozen-file integrity must hash the git-blob (LF) form --
    a CRLF working-tree checkout must not read as content drift."""
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read().replace(b"\r\n", b"\n")).hexdigest()


# ---------------------------------------------------------------- signals (Leg A new patterns)

def sig_ma_slope_200(close: pd.DataFrame) -> pd.DataFrame:
    """MA200 20d-slope sign (+1/-1/0) -- trend-regime face (prereg SS3 A7)."""
    ma = close.rolling(200).mean()
    return np.sign(ma - ma.shift(20))


def sig_channel_pos_55(close: pd.DataFrame) -> pd.DataFrame:
    """Prior-55d channel position state: pos>0.8 -> +1, pos<0.2 -> -1,
    middle holds previous state (continuous-position state form, SS3 A8)."""
    lo = close.rolling(55).min().shift(1)
    hi = close.rolling(55).max().shift(1)
    pos = (close - lo) / (hi - lo)
    raw = pd.DataFrame(np.where(pos > 0.8, 1.0, np.where(pos < 0.2, -1.0, np.nan)),
                       index=close.index, columns=close.columns)
    return raw.ffill()


LEG_A = {
    "tsmom_20": lambda c: p1.sig_tsmom(c, 20),
    "tsmom_40": lambda c: p1.sig_tsmom(c, 40),
    "donchian_20_10": lambda c: p1.sig_donchian(c, 20, 10),
    "donchian_120_50": lambda c: p1.sig_donchian(c, 120, 50),
    "dual_ma_20_100": lambda c: p1.sig_dual_ma(c, 20, 100),
    "dual_ma_50_200": lambda c: p1.sig_dual_ma(c, 50, 200),
    "ma_slope_200": sig_ma_slope_200,
    "channel_pos_55": sig_channel_pos_55,
}

LEG_B_BASES = {
    "tsmom_60": lambda c: p1.sig_tsmom(c, 60),
    "tsmom_120": lambda c: p1.sig_tsmom(c, 120),
    "vol_target_tsmom_60": lambda c: p1.sig_vol_target_tsmom(c, 60),
    "vol_target_tsmom_120": lambda c: p1.sig_vol_target_tsmom(c, 120),
}
LEG_B_CAPS = {"cap50": 0.5, "cap30": 0.3}


# ---------------------------------------------------------------- weights

def build_null_weights(panel_close: pd.DataFrame, k: int,
                       rebalance_idx: np.ndarray) -> pd.DataFrame:
    """K-th random null, wave1 registry seed: every 20d each alive variety
    draws equiprobable {-1, 0, +1}; weight = draw / n_alive. Seed = 62_000+k
    (p1 re-derivation -- p1's builder is hardwired to its own 50_000 base)."""
    rng = np.random.default_rng(SEED_BASE + k)
    m = panel_close.shape[1]
    out = pd.DataFrame(np.nan, index=panel_close.index, columns=panel_close.columns)
    alive = panel_close.notna().to_numpy()
    for t in rebalance_idx:
        draws = rng.integers(0, 3, size=m) - 1          # {0,1,2} -> {-1,0,1}
        n_alive = int(alive[t].sum())
        if n_alive == 0:
            continue
        row = np.full(m, np.nan)
        row[alive[t]] = draws[alive[t]] / n_alive
        out.iloc[t] = row
    return out


def leg_c_weights(panel: dict, fut_col: str, spot_code: str) -> pd.DataFrame:
    """Leg C basis-carry weights: signal on ONE variety column (futures close
    vs ETF spot-proxy close, prereg SS2 proxy law); other varieties stay NaN
    (never traded). Sizing = standard per-variety 1/n_alive margin share."""
    fut_close = panel["close"][fut_col]
    spot_path = os.path.join(ROOT, "data", "daily", f"{spot_code}.csv")
    spot = pd.read_csv(spot_path, index_col=0, parse_dates=True).sort_index()["close"]
    sig = fr.basis_carry_signal(fut_close, spot)
    state = pd.DataFrame(np.nan, index=panel["dates"], columns=VARIETIES)
    state[fut_col] = sig.to_numpy()
    return p1.build_weights(state, panel["close"], None)


# ---------------------------------------------------------------- metrics helpers

def seg_range(equity: pd.Series, start: str | None, end: str | None) -> dict:
    seg = equity
    if start:
        seg = seg[seg.index >= pd.Timestamp(start)]
    if end:
        seg = seg[seg.index <= pd.Timestamp(end)]
    if len(seg) < 20:
        return {"status": "insufficient_data", "bars": int(len(seg))}
    rets = seg.pct_change().dropna()
    sd = rets.std(ddof=1)
    sh = float(rets.mean() / sd * math.sqrt(252)) if sd and sd > 0 else 0.0
    return {"sharpe": round(sh, 4), "bars": int(len(seg))}


def run_cell(panel: dict, weights: pd.DataFrame, cost_mult: float = 1.0,
             margin_cap: float = 1.0) -> dict:
    res = fr.run(panel, weights, start_cash=START_CASH, cost_mult=cost_mult,
                 margin_cap=margin_cap)
    yearly = fr.yearly_returns(res.equity)
    worst = min(yearly.values()) if yearly else 0.0
    return {
        "full": {k: res.metrics[k] for k in
                 ("sharpe", "annual_return", "max_drawdown", "n_trades", "n_entries",
                  "n_closes", "win_rate", "turnover", "final_equity", "groups_pnl")},
        "is2": p1.seg_metrics(res.equity, IS2_START),
        "deep": seg_range(res.equity, WINDOW_START, DEEP_END),
        "wide": p1.seg_metrics(res.equity, WIDE_START),
        "yearly": yearly,
        "worst_year": round(worst, 4),
        "margin_usage_max_ratio": round(res.metrics.get("margin_usage_max_ratio", float("nan")), 6),
        "per_variety": res.per_variety,
        "_equity": res.equity,
        "_returns": res.equity.pct_change().dropna(),
    }


# ---------------------------------------------------------------- gates

def gate_g0() -> dict:
    p = subprocess.run([sys.executable, "-m", "smoke_test"], cwd=ROOT,
                       capture_output=True, text=True, timeout=900)
    tail = p.stdout.split("Summary:")[-1] if "Summary:" in p.stdout else ""
    ok = p.returncode == 0 and "0 FAIL" in tail
    return {"gate": "G0 smoke", "ok": bool(ok),
            "exit": p.returncode, "summary": tail.strip()[:60]}


def wave1_engine_selftest() -> dict:
    """G1 additive legs: margin_cap semantics, TS mechanics, Leg C causality."""
    failures = []

    # (a) margin_cap default bit-identity: cap=1.0 == no-param call
    panel = p1._synthetic_panel()
    w = pd.DataFrame(0.10, index=panel["dates"], columns=["AU", "RB"])
    r_def = fr.run(panel, w, start_cash=1_000_000.0)
    r_cap = fr.run(panel, w, start_cash=1_000_000.0, margin_cap=1.0)
    if not (np.array_equal(r_def.equity.to_numpy(), r_cap.equity.to_numpy())
            and r_def.trades == r_cap.trades):
        failures.append("margin_cap: default 1.0 not bit-identical to prior semantics")

    # (b) margin_cap binding: 3 varieties x per-variety cap 0.2 -> full-budget
    # usage ~0.58; caps 0.5/0.3 must bind (usage <= cap, and the full-budget
    # run sits above 0.5 -- guard against vacuous pass)
    dates3 = pd.bdate_range("2020-01-01", periods=6)
    px3 = pd.DataFrame({"AU": [500.0, 502.0, 504.0, 506.0, 508.0, 510.0],
                        "RB": [3500.0, 3510.0, 3490.0, 3500.0, 3520.0, 3530.0],
                        "SC": [600.0, 602.0, 604.0, 606.0, 608.0, 610.0]}, index=dates3)
    panel3 = {"dates": dates3}
    for fld in ("open", "high", "low", "volume"):
        panel3[fld] = px3.copy()
    panel3["close"] = px3.copy()
    panel3["open"] = px3.copy() * 0.999
    w3 = pd.DataFrame(0.90, index=dates3, columns=["AU", "RB", "SC"])
    r_half = fr.run(panel3, w3, start_cash=1_000_000.0, margin_cap=0.5)
    r_third = fr.run(panel3, w3, start_cash=1_000_000.0, margin_cap=0.3)
    r_full = fr.run(panel3, w3, start_cash=1_000_000.0)
    if not r_half.metrics["margin_usage_max_ratio"] <= 0.5 + 1e-9:
        failures.append(f"margin_cap 0.5: usage {r_half.metrics['margin_usage_max_ratio']} > 0.5")
    if not r_third.metrics["margin_usage_max_ratio"] <= 0.3 + 1e-9:
        failures.append(f"margin_cap 0.3: usage {r_third.metrics['margin_usage_max_ratio']} > 0.3")
    if not r_full.metrics["margin_usage_max_ratio"] > 0.5:
        failures.append(f"margin_cap test vacuous: full-budget usage "
                        f"{r_full.metrics['margin_usage_max_ratio']} <= 0.5")
    if np.array_equal(r_half.equity.to_numpy(), r_full.equity.to_numpy()):
        failures.append("margin_cap 0.5 not binding: equity path identical to full budget")

    # (c) TS lots math: FLAT px 102, share 0.10, eq 1M -> lots stay
    #     floor(100000 / (20000*102*0.005)) = floor(9.80) = 9 (no re-size drift
    #     on a flat panel; rising panels grow equity -> re-size by design)
    dates = pd.bdate_range("2020-01-01", periods=6)
    px = pd.DataFrame({"TS": [102.0] * 6}, index=dates)
    tsp = {"dates": dates}
    for fld in ("open", "high", "low", "volume"):
        tsp[fld] = px.copy()
    tsp["close"] = px.copy()
    tsp["open"] = px.copy()
    w_ts = pd.DataFrame(0.10, index=dates, columns=["TS"])
    r_ts = fr.run(tsp, w_ts, start_cash=1_000_000.0)
    ts_open = sum(t["lots"] for t in r_ts.trades
                  if t["variety"] == "TS" and t["reason"] == "fut_open")
    if ts_open != 9:
        failures.append(f"TS lots math: open lots {ts_open} != 9")
    # TS first fill must be T+1 (day 1)
    ts_fills = [t for t in r_ts.trades if t["variety"] == "TS"]
    if ts_fills and ts_fills[0]["date"] != str(dates[1].date()):
        failures.append(f"TS T+1 shift: first fill {ts_fills[0]['date']} != day+1")

    # (d) TS limit guard: open beyond +/-0.5% -> no new open, close allowed
    tsp_lim = {"dates": dates}
    for fld in ("open", "high", "low", "volume"):
        tsp_lim[fld] = px.copy()
    tsp_lim["close"] = px.copy()
    tsp_lim["open"] = px.copy() * 0.999
    tsp_lim["open"].iloc[3, 0] = float(tsp_lim["close"].iloc[2, 0]) * (1 + FUT_META["TS"]["limit"] + 0.002)
    w_lim = pd.DataFrame(0.10, index=dates, columns=["TS"])
    r_l = fr.run(tsp_lim, w_lim, start_cash=1_000_000.0)
    day3 = str(dates[3].date())
    opens_on_limit = [t for t in r_l.trades if t["variety"] == "TS"
                      and t["date"] == day3 and t["reason"] == "fut_open"]
    closes_on_limit = [t for t in r_l.trades if t["variety"] == "TS"
                       and t["date"] == day3 and t["reason"] == "fut_close"]
    if opens_on_limit:
        failures.append("TS limit guard: fut_open on limit-up day")
    if not closes_on_limit:
        failures.append("TS limit guard: closing on limit-up day must be allowed")

    # (e) Leg C basis signal semantics (synthetic 220d)
    idx = pd.bdate_range("2020-01-01", periods=220)
    fut = pd.Series(100.0, index=idx)
    fut.iloc[120:180] = 99.0          # deep discount stretch
    fut.iloc[180:] = 101.0           # premium stretch (vs converged m ~0.99)
    spot_full = pd.Series(100.0, index=idx)
    sig = fr.basis_carry_signal(fut, spot_full, window=60, band=0.002)
    # warmup (m undefined, < 60 obs) = NaN by design (carry, no signal face);
    # rolling(60, min_periods=60) first valid at position 59
    if not sig.iloc[:59].isna().all():
        failures.append("LegC warmup: first 59 days must be NaN (no signal face)")
    # dead zone after warmup (dev == 0) = explicit flat 0
    if not (sig.iloc[60:120] == 0).all():
        failures.append("LegC dead zone: dev==0 days must be 0")
    if sig.iloc[130] != 1.0:
        failures.append(f"LegC deep discount: sig[130]={sig.iloc[130]} != +1")
    if sig.iloc[200] != -1.0:
        failures.append(f"LegC premium: sig[200]={sig.iloc[200]} != -1")
    # causality: truncated-input signal must agree with full-input signal up to T
    for k in (100, 150, 200):
        sig_tr = fr.basis_carry_signal(fut.iloc[:k], spot_full.iloc[:k], window=60, band=0.002)
        if not np.allclose(sig.iloc[:k].to_numpy(), sig_tr.to_numpy(), equal_nan=True):
            failures.append(f"LegC causality: truncate-and-compare mismatch at k={k}")
            break
    # spot ffill: gap day uses prior spot close (no lookahead)
    spot_gap = spot_full.drop(idx[150])
    sig_gap = fr.basis_carry_signal(fut, spot_gap, window=60, band=0.002)
    if not np.allclose(sig.to_numpy(), sig_gap.to_numpy(), equal_nan=True):
        failures.append("LegC spot ffill: gap-day signal drifts vs ffilled-prior close")

    # (f) determinism double-run (synthetic TS panel)
    r1 = fr.run(tsp, w_ts, start_cash=1_000_000.0)
    r2 = fr.run(tsp, w_ts, start_cash=1_000_000.0)
    if not (np.array_equal(r1.equity.to_numpy(), r2.equity.to_numpy())
            and r1.trades == r2.trades):
        failures.append("TS determinism: double run differs")
    return {"gate": "G1 wave1 additive selftest", "ok": len(failures) == 0,
            "failures": failures}


def gate_g2() -> dict:
    """TS exchange-verified constants (frozen evidence file) + 10-variety
    plausibility checks (CTA_P1 G2 precedent)."""
    problems = []
    ts_meta = FUT_META.get("TS")
    if ts_meta is None:
        problems.append("TS missing from FUT_META")
        ts_meta = {}
    for k, v in TS_FROZEN_VERIFIED.items():
        if abs(float(ts_meta.get(k, float("nan"))) - v) > 1e-12:
            problems.append(f"TS {k}: FUT_META {ts_meta.get(k)} != frozen verified {v}")
    if not os.path.exists(G2_EVIDENCE_PATH):
        problems.append(f"G2 evidence file missing: {G2_EVIDENCE_PATH}")
    ref_px = {"IF": 4000.0, "IC": 6000.0, "IM": 6000.0, "IH": 2800.0, "T": 100.0,
              "TF": 102.0, "RB": 3600.0, "AU": 500.0, "SC": 600.0, "TS": 102.5}
    checks = []
    for v, meta in FUT_META.items():
        notional = meta["mult"] * ref_px[v]
        fee_bp = meta["fee_lot"] / notional * 1e4
        c = {"variety": v, "fee_bp_at_ref": round(fee_bp, 4),
             "fee_bp_ok": bool(0.005 <= fee_bp <= 30.0),
             "margin_ok": bool(0.005 <= meta["margin"] <= 0.25),
             "tick_value_ok": bool(3.0 <= meta["tick"] * meta["mult"] <= 500.0),
             "limit_ok": bool(0.005 <= meta["limit"] <= 0.20)}
        if not all(c[k] for k in ("fee_bp_ok", "margin_ok", "tick_value_ok", "limit_ok")):
            problems.append(f"{v}: plausibility fail {c}")
        checks.append(c)
    return {"gate": "G2 TS exchange-verified constants + plausibility",
            "ok": len(problems) == 0, "problems": problems, "checks": checks,
            "ts_frozen_verified": TS_FROZEN_VERIFIED,
            "evidence": "results/cta_wave1_g2_ts_check.json (CFFEX /cn/2ts.html + "
                        "/sj/jscs/202609/21/20260921_1.csv, verified 2026-09-25 R187)",
            "deviation_disclosure": ("prereg provisional tick 0.005 vs exchange-verified "
                                     "0.002 (150% > 30%) -> frozen verified per SS3 G2 "
                                     "protocol; fee/mult/margin/limit provisional = verified")}


def gate_g3() -> dict:
    """Data completeness, probe-p2 semantics verbatim (r179 alignment law):
    vs-union-calendar in-span holes, full enumeration, window-clipped."""
    problems = []
    per_variety = {}
    frames = {}
    for v in VARIETIES:
        path = os.path.join(fr.FUT_DIR, f"{v}.csv")
        if not os.path.exists(path):
            problems.append(f"{v}: csv missing")
            continue
        df = pd.read_csv(path, index_col=0, parse_dates=True).sort_index()
        seg = df.loc[(df.index >= pd.Timestamp(WINDOW_START)) & (df.index <= pd.Timestamp(CUTOFF))]
        frames[v] = seg
        last = str(seg.index[-1].date()) if len(seg) else None
        if last != CUTOFF:
            problems.append(f"{v}: last bar {last} != cutoff {CUTOFF}")
        for fld in ("open", "high", "low", "close", "volume"):
            col = seg[fld].to_numpy(dtype=float)
            col = col[~np.isnan(col)]
            if len(col) and float(col.min()) < 0:
                problems.append(f"{v}.{fld}: negative values")
    if len(frames) == len(VARIETIES):
        all_dates = sorted(set().union(*[set(f.index) for f in frames.values()]))
        idx = pd.DatetimeIndex(all_dates)
        holes_seen = set()
        for v, f in frames.items():
            inspan = [d for d in idx.difference(f.index) if d >= f.index[0]]
            pre_listing = int(len(idx.difference(f.index)) - len(inspan))
            cells = [(str(d.date()), v) for d in inspan]
            holes_seen.update(cells)
            extra = [c for c in cells if c not in EXEMPT_CELLS]
            if extra:
                problems.append(f"{v}: in-span holes outside frozen exemption: {extra}")
            per_variety[v] = {"rows": int(len(f)), "first": str(f.index[0].date()),
                              "last": str(f.index[-1].date()),
                              "in_span_missing": [c[0] for c in cells],
                              "pre_listing_absence_days": pre_listing}
    exempt_unused = sorted(c for c in EXEMPT_CELLS if c not in holes_seen)
    return {"gate": "G3 data completeness (18-cell frozen exemption)", "ok": len(problems) == 0,
            "problems": problems, "per_variety": per_variety,
            "frozen_exempt_cells": len(EXEMPT_CELLS),
            "holes_seen_cells": len(holes_seen),
            "exempt_cells_not_seen": exempt_unused,
            "semantics": "probe p2 verbatim: vs-union-calendar, in-span >= own first bar, full enumeration"}


def gate_g4() -> dict:
    """Null + passive determinism on the full deep panel: same-seed double
    build + double run bit-exact."""
    panel = fr.load_panel(WINDOW_START, CUTOFF)
    ridx = p1.r20_rebalance_index(panel["dates"])
    w1 = build_null_weights(panel["close"], 0, ridx)
    w2 = build_null_weights(panel["close"], 0, ridx)
    if not np.array_equal(w1.to_numpy(), w2.to_numpy(), equal_nan=True):
        return {"gate": "G4 null/passive determinism", "ok": False,
                "stage": "null weights rebuild differ"}
    r1 = fr.run(panel, w1, start_cash=START_CASH)
    r2 = fr.run(panel, w2, start_cash=START_CASH)
    eq_ok = np.array_equal(r1.equity.to_numpy(), r2.equity.to_numpy())
    tr_ok = r1.trades == r2.trades
    p1w = p1.build_passive_weights(panel["close"], ridx)
    pa1 = fr.run(panel, p1w, start_cash=START_CASH)
    pa2 = fr.run(panel, p1w, start_cash=START_CASH)
    pa_ok = np.array_equal(pa1.equity.to_numpy(), pa2.equity.to_numpy()) and pa1.trades == pa2.trades
    return {"gate": "G4 null/passive determinism",
            "ok": bool(eq_ok and tr_ok and pa_ok),
            "equity_bitexact": bool(eq_ok), "trades_bitexact": bool(tr_ok),
            "passive_bitexact": bool(pa_ok)}


def run_gates(include_g0: bool = True) -> dict:
    out = {}
    if include_g0:
        out["G0"] = gate_g0()
    out["G1_p1"] = p1.engine_selftest()
    out["G1_wave1"] = wave1_engine_selftest()
    out["G2"] = gate_g2()
    out["G3"] = gate_g3()
    out["G4"] = gate_g4()
    return out


# ---------------------------------------------------------------- batch run

def do_run() -> int:
    t0 = time.time()
    print("[cta_wave1] prereg integrity + gates ...")
    sha = _sha256_lf_normalized(PREREG_PATH)
    if sha != FROZEN_PREREG_SHA:
        print(f"[cta_wave1] PREREG DRIFT: working sha {sha} != frozen {FROZEN_PREREG_SHA} "
              f"— batch aborted (exit 2)")
        return 2
    gates = run_gates(include_g0=True)
    gates_ok = all(g.get("ok") for g in gates.values())
    for name, g in gates.items():
        print(f"  {name}: {'PASS' if g.get('ok') else 'FAIL'}")
        if not g.get("ok"):
            print(f"    detail: {json.dumps(g, ensure_ascii=False, default=str)[:400]}")
    if not gates_ok:
        print("[cta_wave1] GATES FAILED — batch aborted (exit 2), no numbers produced")
        return 2

    panel = fr.load_panel(WINDOW_START, CUTOFF)
    dates = panel["dates"]
    close = panel["close"]
    r20_idx = p1.r20_rebalance_index(dates)
    mon_idx = p1.month_first_index(dates)

    cells: dict[str, dict] = {}
    # ---- Leg A: 8 patterns x {daily, r20} ----
    for fam_name, builder in LEG_A.items():
        state = builder(close)
        for regime, ridx in (("daily", None), ("r20", r20_idx)):
            name = f"{fam_name}@{regime}"
            w = p1.build_weights(state, close, ridx)
            cell = run_cell(panel, w)
            cell["x2_full_sharpe"] = run_cell(panel, w, cost_mult=2.0)["full"]["sharpe"]
            cell["x3_full_sharpe"] = run_cell(panel, w, cost_mult=3.0)["full"]["sharpe"]
            cells[name] = cell
            print(f"  {name}: full={cell['full']['sharpe']} x2={cell['x2_full_sharpe']} "
                  f"x3={cell['x3_full_sharpe']} entries={cell['full']['n_entries']}")
    # ---- Leg B: 4 bases x {cap50, cap30}, daily only ----
    for bname, builder in LEG_B_BASES.items():
        state = builder(close)
        w = p1.build_weights(state, close, None)
        for cap_name, cap in LEG_B_CAPS.items():
            name = f"legb_{bname}@{cap_name}"
            cell = run_cell(panel, w, margin_cap=cap)
            cell["x2_full_sharpe"] = run_cell(panel, w, cost_mult=2.0, margin_cap=cap)["full"]["sharpe"]
            cell["x3_full_sharpe"] = run_cell(panel, w, cost_mult=3.0, margin_cap=cap)["full"]["sharpe"]
            cells[name] = cell
            print(f"  {name}: full={cell['full']['sharpe']} dd={cell['full']['max_drawdown']} "
                  f"usage={cell['margin_usage_max_ratio']} entries={cell['full']['n_entries']}")
    # ---- Leg C: 2 basis-carry cells, daily ----
    for cname, (fut_col, spot_code) in SPOT_PROXY.items():
        w = leg_c_weights(panel, fut_col, spot_code)
        cell = run_cell(panel, w)
        cell["x2_full_sharpe"] = run_cell(panel, w, cost_mult=2.0)["full"]["sharpe"]
        cell["x3_full_sharpe"] = run_cell(panel, w, cost_mult=3.0)["full"]["sharpe"]
        cells[cname] = cell
        print(f"  {cname}: full={cell['full']['sharpe']} entries={cell['full']['n_entries']}")

    # ---- 50 nulls (r20) ----
    null_sharpes = []
    null_cells = {}
    for k in range(K_NULLS):
        w = build_null_weights(close, k, r20_idx)
        cell = run_cell(panel, w, cost_mult=1.0)
        null_cells[f"null_{k}"] = p1.public_cell(cell)
        null_sharpes.append(cell["full"]["sharpe"])
    null_vals = [float(x) for x in null_sharpes]
    mu = sum(null_vals) / len(null_vals)
    sigma = math.sqrt(sum((x - mu) ** 2 for x in null_vals) / (len(null_vals) - 1))
    null_summary = {"n": len(null_vals), "mu": round(mu, 4), "sigma": round(sigma, 4),
                    "p95": round(float(np.percentile(null_vals, 95)), 4),
                    "max": round(max(null_vals), 4), "min": round(min(null_vals), 4)}
    # ---- 2 passives ----
    passive_cells = {}
    passive_sharpes = {}
    for pname, ridx in (("passive_long_r20", r20_idx), ("passive_long_monthly", mon_idx)):
        w = p1.build_passive_weights(close, ridx)
        cell = run_cell(panel, w, cost_mult=1.0)
        passive_cells[pname] = p1.public_cell(cell)
        passive_sharpes[pname] = cell["full"]["sharpe"]
        print(f"  {pname}: full={cell['full']['sharpe']}")

    meta = {
        "window": {"start": WINDOW_START, "end": CUTOFF, "n_days": int(len(dates)),
                   "deep_segment": {"start": WINDOW_START, "end": DEEP_END},
                   "wide_segment": {"start": WIDE_START, "end": CUTOFF}},
        "varieties": VARIETIES,
        "start_cash": START_CASH,
        "start_cash_note": ("CTA_P1 convention (implementation choice disclosed in "
                            "prereg SS0 scope): 10M CTA allocation keeps whole-lot "
                            "granularity from dominating per-variety margin shares"),
        "rebalance": {"r20_days": int(len(r20_idx)), "monthly_days": int(len(mon_idx))},
        "cost": {v: {"fee_lot": FUT_META[v]["fee_lot"], "tick": FUT_META[v]["tick"],
                     "slippage_per_side_yuan": round(FUT_META[v]["tick"] * FUT_META[v]["mult"], 2)}
                 for v in VARIETIES},
        "prereg_sha_frozen": FROZEN_PREREG_SHA,
        "prereg_sha_at_run": sha,
        "g2_ts_evidence": "results/cta_wave1_g2_ts_check.json",
        "deep_window_disclosure": DEEP_WINDOW_NOTE,
        "legs": {"A": "8 new trend patterns x {daily, r20} (16 cells)",
                 "B": "4 bases x margin-cap {50,30}, daily (8 cells; global usage "
                      "ceiling cap x yesterday equity, shrink-largest-occupant)",
                 "C": "2 basis-carry cells (IF/510300, IC/510500 ETF proxy, ratio "
                      "dev vs 60d mean, dead-zone 20bp, window 2020-01-02+)"},
    }
    phase1 = {
        "batch": "cta_wave1",
        "meta": meta,
        **sg.cutoff_meta(CUTOFF),
        "gates": gates,
        "nulls": {"summary": null_summary,
                  "cells": {k: {"full": v["full"], "deep": v.get("deep"), "wide": v.get("wide")}
                            for k, v in null_cells.items()}},
        "passive": passive_cells,
        "candidates": {k: p1.public_cell(v) for k, v in cells.items()},
    }
    with open(RESULTS_JSON, "w", encoding="utf-8") as fh:
        json.dump(phase1, fh, ensure_ascii=False, indent=1, default=str)
    print("[cta_wave1] phase-1 JSON written (passive pool registered)")

    # ---- verdicts (skill line needs phase-1 passive on file) ----
    null_pool = {"values": null_vals,
                 "coverage": {"n_values": len(null_vals), "mu": mu, "sigma": sigma,
                              "schemas_parsed": ["cta_wave1:nulls.summary (K=50 in-batch)"],
                              "known_unparsed": []}}
    line = sg.skill_line_v2(batch_cells=BATCH_CELLS, pool="cta_wave1",
                            null_pool=null_pool)
    print(f"[cta_wave1] skill_line_v2 = {line['line']} "
          f"(passive_term={line['passive_term']} null_term={line['null_term']})")
    verdicts = {}
    passers = []
    for name, cell in cells.items():
        v = sg.g1_prime_v2(sharpe_full=cell["full"]["sharpe"], returns=cell["_returns"],
                           batch_cells=BATCH_CELLS, pool="cta_wave1",
                           null_pool=null_pool, n_trades=cell["full"]["n_trades"],
                           n_entries=cell["full"]["n_entries"])
        is2 = cell["is2"]
        desc = {
            "annual_positive": bool(cell["full"]["annual_return"] > 0),
            "is2_dual_positive": bool(is2.get("sharpe", 0) > 0 and is2.get("annual_return", 0) > 0),
            "dd_ok": bool(cell["full"]["max_drawdown"] >= -0.35),
            "no_crash_year": bool(cell["worst_year"] >= -0.35),
            "x2_info_sharpe": cell["x2_full_sharpe"],
            "x3_info_sharpe": cell["x3_full_sharpe"],
            "deep_sharpe": cell["deep"].get("sharpe"),
            "wide_sharpe": cell["wide"].get("sharpe"),
            "margin_usage_max_ratio": cell["margin_usage_max_ratio"],
        }
        v["descriptive"] = desc
        verdicts[name] = v
        if v["pass_v2"]:
            passers.append(name)
            print(f"  >> {name} PASSES g1_prime_v2")

    # within-batch pairwise corr (D6 disclosure, all 26 candidates)
    rets_df = pd.DataFrame({k: cells[k]["_returns"] for k in cells})
    corr = rets_df.corr()
    within_max = {}
    for name in cells:
        others = corr[name].drop(name).abs()
        within_max[name] = round(float(others.max()), 4) if len(others) else None

    # family PBO: Leg A = per-pattern 2-cell (daily/r20); Leg B = one 8-cell
    # cap family; Leg C = one 2-cell basis family (prereg SS4)
    from pbo import cscv_pbo, align_returns
    family_pbo = {}
    for fam in LEG_A:
        pair = {f"{fam}@daily": cells[f"{fam}@daily"]["_returns"],
                f"{fam}@r20": cells[f"{fam}@r20"]["_returns"]}
        family_pbo[fam] = cscv_pbo(align_returns(pair))
    family_pbo["legb_cap_family"] = cscv_pbo(align_returns(
        {f"legb_{b}@{c}": cells[f"legb_{b}@{c}"]["_returns"]
         for b in LEG_B_BASES for c in LEG_B_CAPS}))
    family_pbo["basis_family"] = cscv_pbo(align_returns(
        {c: cells[c]["_returns"] for c in SPOT_PROXY}))

    def cell_family(name: str) -> str:
        if name.startswith("legb_"):
            return "legb_cap_family"
        if name.startswith("basis_"):
            return "basis_family"
        return name.split("@")[0]

    verdicts_g2 = {}
    d6_inregister = {}
    if passers:
        try:
            import ew6_portfolio as E
            E._init_worker()
            from firm.hr import TRADERS_DIR, load_trader
            member_rets = {}
            for fn in sorted(os.listdir(TRADERS_DIR)):
                if not fn.endswith(".json"):
                    continue
                tid = fn[:-5]
                t = load_trader(tid)
                if t.get("status") == "FIRE":
                    continue
                mr = E.member_run(tid)
                eq = pd.Series(mr["eq"], index=pd.to_datetime(mr["dates"]))
                member_rets[tid] = eq.pct_change().dropna()
            for name in passers:
                cr = cells[name]["_returns"]
                pairs = {}
                for tid, mret in member_rets.items():
                    j = pd.concat([cr, mret], axis=1, join="inner").dropna()
                    if len(j) > 60 and j.iloc[:, 1].std() > 0:
                        pairs[tid] = round(float(j.corr().iloc[0, 1]), 4)
                d6_inregister[name] = {"max_abs_corr": round(max(abs(v) for v in pairs.values()), 4) if pairs else None,
                                       "pairs": pairs}
        except Exception as exc:  # noqa: BLE001
            d6_inregister = {"error": f"in-register corr skipped: {exc}"}
        for name in passers:
            dsr = sg.deflated_sharpe_ratio(cells[name]["_returns"],
                                           n_trials=line["n_eff"],
                                           var_null_sr=sigma ** 2)
            verdicts_g2[name] = sg.g2_registration_v2(
                g1_pass=True, dsr=dsr, pbo=family_pbo[cell_family(name)]["pbo"])

    # ---- ledger append (single source, live chain head) ----
    ledger = sg.append_ledger(
        "cta_wave1", BATCH_CELLS, "results/shortline_cta_wave1.json",
        evidence_cutoff=CUTOFF,
        note=("26 candidates (LegA 8 new trend patterns x daily/r20 + LegB 4 bases "
              "x margin-cap 50/30 + LegC 2 basis-carry IF/IC vs ETF proxy) + 50 "
              "nulls (seed 62_000+k) + 2 passives; deep panel union 2008-01-09, "
              "10 varieties incl. TS (G2 exchange-verified, tick frozen 0.002 "
              "per >30% deviation protocol); prereg research/CTA_WAVE1_PREREG.md "
              "frozen R186 sha b5bed148; pool cta_wave1 own nulls+deep passives"))
    # ---- audit segment (compute_audit run in-batch, prereg SS0) ----
    audit_seg = {}
    try:
        subprocess.run([sys.executable, os.path.join("scripts", "compute_audit.py")],
                       cwd=ROOT, capture_output=True, text=True, timeout=120)
    except Exception as exc:  # noqa: BLE001
        print(f"[cta_wave1] compute_audit in-batch run failed: {exc}")
    apath = os.path.join(ROOT, "results", "compute_audit.json")
    if os.path.exists(apath):
        with open(apath, encoding="utf-8") as fh:
            aj = json.load(fh)
        latest = aj.get("history", [{}])[-1] if aj.get("history") else aj
        audit_seg = {"source": "results/compute_audit.json (in-batch run, latest)",
                     "verdict": latest.get("verdict"), "ts": latest.get("ts"),
                     "cpu_pct": latest.get("cpu_pct"), "flags": latest.get("flags")}
    final = dict(phase1)
    final.update({
        "null_pool": null_pool,
        "skill_line": line,
        "verdicts_g1": verdicts,
        "g1_passers": passers,
        "verdicts_g2": verdicts_g2,
        "d6": {"within_batch_max_abs_corr": within_max,
               "in_register": d6_inregister,
               "reject_line": 0.7},
        "family_pbo": family_pbo,
        "trials_ledger": ledger,
        "audit": audit_seg,
        "passive_sharpes": passive_sharpes,
    })
    with open(RESULTS_JSON, "w", encoding="utf-8") as fh:
        json.dump(final, fh, ensure_ascii=False, indent=1, default=str)

    # ---- CSV (78 rows) ----
    with open(RESULTS_CSV, "w", newline="", encoding="utf-8") as fh:
        wr = csv.writer(fh)
        wr.writerow(["cell", "leg", "family", "regime", "kind", "sharpe_full",
                     "annual_return", "max_drawdown", "worst_year", "is2_sharpe",
                     "is2_annual", "deep_sharpe", "wide_sharpe", "x2_full_sharpe",
                     "x3_full_sharpe", "n_trades", "n_entries", "turnover",
                     "win_rate", "margin_usage_max_ratio", "line", "line_ok",
                     "ci_ok", "pass_v2"])
        for name, cell in cells.items():
            v = verdicts[name]
            fam = cell_family(name)
            if name.startswith("legb_"):
                leg, reg = "B", name.split("@")[-1]
            elif name.startswith("basis_"):
                leg, reg = "C", "daily"
            else:
                leg, reg = "A", name.split("@")[-1]
            wr.writerow([name, leg, fam, reg, "candidate", cell["full"]["sharpe"],
                         cell["full"]["annual_return"], cell["full"]["max_drawdown"],
                         cell["worst_year"], cell["is2"].get("sharpe"),
                         cell["is2"].get("annual_return"), cell["deep"].get("sharpe"),
                         cell["wide"].get("sharpe"), cell["x2_full_sharpe"],
                         cell["x3_full_sharpe"], cell["full"]["n_trades"],
                         cell["full"]["n_entries"], cell["full"]["turnover"],
                         cell["full"]["win_rate"], cell["margin_usage_max_ratio"],
                         v["skill_line"]["line"], v["line_ok"],
                         v["ci_lower_bound_positive"], v["pass_v2"]])
        for k in range(K_NULLS):
            c = null_cells[f"null_{k}"]
            wr.writerow([f"null_{k}", "", "random", "r20", "null", c["full"]["sharpe"],
                         c["full"]["annual_return"], c["full"]["max_drawdown"],
                         c["worst_year"], c["is2"].get("sharpe"), c["is2"].get("annual_return"),
                         c["deep"].get("sharpe"), c["wide"].get("sharpe"), "", "",
                         c["full"]["n_trades"], c["full"]["n_entries"],
                         c["full"]["turnover"], c["full"]["win_rate"], "",
                         "", "", "", ""])
        for pname, c in passive_cells.items():
            wr.writerow([pname, "", "passive_long", pname, "passive", c["full"]["sharpe"],
                         c["full"]["annual_return"], c["full"]["max_drawdown"],
                         c["worst_year"], c["is2"].get("sharpe"), c["is2"].get("annual_return"),
                         c["deep"].get("sharpe"), c["wide"].get("sharpe"), "", "",
                         c["full"]["n_trades"], c["full"]["n_entries"],
                         c["full"]["turnover"], c["full"]["win_rate"], "",
                         "", "", "", ""])

    # ---- gate_attrition entry (search batch) ----
    try:
        with open(ATTRITION_JSON, encoding="utf-8") as fh:
            attr = json.load(fh)
        attr["entries"].append({
            "batch": "CTA_WAVE1",
            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "kind": "search",
            "cells_ledger_delta": BATCH_CELLS,
            "ledger_total_after": ledger.get("total"),
            "gates": {"skill_line_v2": line["line"],
                      "g1_passers": len(passers),
                      "descriptive_all_pass_candidates": int(sum(
                          1 for n in cells
                          if all(verdicts[n]["descriptive"][k]
                                 for k in ("annual_positive", "is2_dual_positive",
                                           "dd_ok", "no_crash_year"))))},
            "eliminated": 26 - len(passers),
            "refs": {"results": "results/shortline_cta_wave1.json",
                     "prereg": "research/CTA_WAVE1_PREREG.md"},
        })
        with open(ATTRITION_JSON, "w", encoding="utf-8") as fh:
            json.dump(attr, fh, ensure_ascii=False, indent=1)
    except Exception as exc:  # noqa: BLE001
        print(f"[cta_wave1] attrition append failed: {exc}")

    print(f"[cta_wave1] DONE in {time.time() - t0:.1f}s — passers: {passers}")
    print(f"[cta_wave1] null summary: {null_summary}")
    print(f"[cta_wave1] skill line: {line}")
    return 0


# ---------------------------------------------------------------- selftest (offline)

def do_selftest() -> int:
    fails = []
    # p1 engine unit assertions (variety-agnostic G1 body, synthetic = offline)
    g1 = p1.engine_selftest()
    if not g1["ok"]:
        fails.extend(g1["failures"])
    # wave1 additive engine assertions
    g1w = wave1_engine_selftest()
    if not g1w["ok"]:
        fails.extend(g1w["failures"])
    # schedule determinism
    dates = pd.bdate_range("2020-01-01", periods=100)
    if list(p1.r20_rebalance_index(dates)[:3]) != [0, 20, 40]:
        fails.append("r20 schedule drift")
    if len(p1.month_first_index(dates)) < 4:
        fails.append("monthly schedule too short")
    # null weights determinism (synthetic, wave1 seed)
    close = pd.DataFrame({"A": np.arange(100, dtype=float) + 10,
                          "B": np.arange(100, dtype=float) * 0.5 + 5},
                         index=dates)
    r20 = p1.r20_rebalance_index(dates)
    w1 = build_null_weights(close, 0, r20)
    w2 = build_null_weights(close, 0, r20)
    if not np.array_equal(w1.to_numpy(), w2.to_numpy(), equal_nan=True):
        fails.append("null weights rebuild differ (synthetic, seed 62000)")
    if sg.SEED_REGISTRY.get("cta_wave1") != 62_000:
        fails.append("SEED_REGISTRY cta_wave1 != 62000")
    # passive weights: alive-only equal share (p1 builder reuse)
    wp = p1.build_passive_weights(close, r20)
    row0 = wp.iloc[0].dropna()
    if len(row0) != 2 or not np.allclose(row0.to_numpy(), 0.5):
        fails.append(f"passive weights row0 {row0.to_dict()}")
    # exemption set = exactly 18 frozen cells
    if len(EXEMPT_CELLS) != 18:
        fails.append(f"exemption set {len(EXEMPT_CELLS)} != 18 cells")
    # Leg A new-signal shape sanity (synthetic)
    up = pd.DataFrame({"A": np.arange(300, dtype=float) + 10}, index=pd.bdate_range("2020-01-01", periods=300))
    sl = sig_ma_slope_200(up)
    if not (sl["A"].iloc[-1] == 1.0):
        fails.append(f"ma_slope_200 uptrend sign {sl['A'].iloc[-1]} != 1")
    ch = sig_channel_pos_55(up)
    if not (ch["A"].iloc[-1] == 1.0):
        fails.append(f"channel_pos_55 uptrend state {ch['A'].iloc[-1]} != 1")
    print(f"[cta_wave1 selftest] {'ALL PASS' if not fails else 'FAIL: ' + str(fails)}")
    return 0 if not fails else 1


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "selftest"
    if cmd == "gates":
        gs = run_gates()
        for name, g in gs.items():
            print(f"{name}: {'PASS' if g.get('ok') else 'FAIL'}")
            if not g.get("ok"):
                print(json.dumps(g, ensure_ascii=False, default=str)[:600])
        sys.exit(0 if all(g.get("ok") for g in gs.values()) else 2)
    if cmd == "run":
        sys.exit(do_run())
    if cmd == "selftest":
        sys.exit(do_selftest())
    print("usage: cta_wave1.py gates|run|selftest")
    sys.exit(1)
