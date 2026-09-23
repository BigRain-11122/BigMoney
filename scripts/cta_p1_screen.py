"""CTA_P1 batch runner — 16 candidates + 50 nulls + 2 passives (68 cells).

Prereg: research/CTA_P1.md (frozen R49 sha 2aa3d219..., pre-run G3 amendment R50).
Domain: 9-variety main-continuous futures panel (R48 data), window 2017-01-17
-> 2026-09-23, OHLCV-only signal inputs, roll-gap V0 direct-use, futures-domain
own null pool + passive skill line (no cross-pool borrowing).

Subcommands:
  gates    G0 smoke / G1 engine selftest / G2 cost constants / G3 data / G4 null determinism
  run      full batch (gates re-run inside; aborts exit 2 on any gate FAIL)
  selftest offline unit tests (synthetic panel; no data files needed)

Ledger: science_gates.append_ledger("cta_p1", 68, ..., evidence_cutoff=2026-09-23).
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

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREREG_PATH = os.path.join(ROOT, "research", "CTA_P1.md")
RESULTS_JSON = os.path.join(ROOT, "results", "shortline_cta_p1.json")
RESULTS_CSV = os.path.join(ROOT, "research", "cta_p1_results.csv")
ATTRITION_JSON = os.path.join(ROOT, "results", "gate_attrition.json")
CUTOFF = "2026-09-23"
WINDOW_START = "2017-01-17"
IS2_START = "2025-01-01"
FROZEN_PREREG_SHA = "2aa3d219427428a3e7369fa6254ae121fecf81c1d061e23e1ffdb38f8b31c471"
SEED_BASE = 50_000          # SEED_REGISTRY["cta_p1"] (frozen at prereg)
K_NULLS = 50
BATCH_CELLS = 68            # 16 candidates + 50 nulls + 2 passives
START_CASH = 10_000_000.0   # implementation choice (prereg unfrozen): 10M CTA
# allocation keeps whole-lot granularity from dominating small shares;
# disclosed in batch JSON meta.
VARIETIES = list(FUT_META)
# G3 pre-run amendment (R50): the only allowed in-span NaN holes = these two
# source cross-exchange calendar-gap dates (raw-CSV verified).
SOURCE_GAP_DATES = {"2017-10-09", "2019-04-22"}


def _sha256_file(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


# ---------------------------------------------------------------- signals

def sig_tsmom(close: pd.DataFrame, h: int) -> pd.DataFrame:
    return np.sign(close / close.shift(h) - 1.0)


def sig_donchian(close: pd.DataFrame, hi: int = 55, lo: int = 20) -> pd.DataFrame:
    up_break = close > close.rolling(hi).max().shift(1)
    dn_break = close < close.rolling(hi).min().shift(1)
    long_exit = close < close.rolling(lo).min().shift(1)
    short_exit = close > close.rolling(lo).max().shift(1)
    raw = pd.DataFrame(np.where(up_break, 1.0, np.where(dn_break, -1.0, np.nan)),
                       index=close.index, columns=close.columns)
    st = raw.ffill()
    st = st.mask(long_exit & (st == 1), 0.0).mask(short_exit & (st == -1), 0.0)
    return st


def sig_dual_ma(close: pd.DataFrame, fast: int = 10, slow: int = 60) -> pd.DataFrame:
    f = close.rolling(fast).mean()
    s = close.rolling(slow).mean()
    return np.sign(f - s)


def sig_triple_ma(close: pd.DataFrame) -> pd.DataFrame:
    m5 = close.rolling(5).mean()
    m20 = close.rolling(20).mean()
    m60 = close.rolling(60).mean()
    up = (m5 > m20) & (m20 > m60)
    dn = (m5 < m20) & (m20 < m60)
    return pd.DataFrame(np.where(up, 1.0, np.where(dn, -1.0, 0.0)),
                        index=close.index, columns=close.columns)


def sig_breakout(close: pd.DataFrame, w: int = 20) -> pd.DataFrame:
    up = close > close.rolling(w).max().shift(1)
    dn = close < close.rolling(w).min().shift(1)
    return pd.DataFrame(np.where(up, 1.0, np.where(dn, -1.0, 0.0)),
                        index=close.index, columns=close.columns)


def sig_vol_target_tsmom(close: pd.DataFrame, h: int = 60,
                         target_vol: float = 0.01) -> pd.DataFrame:
    direction = np.sign(close / close.shift(h) - 1.0)
    realized = close.pct_change().rolling(h).std()
    mult = (target_vol / realized).clip(upper=1.0)
    return direction * mult


FAMILIES = {
    "tsmom_120": lambda c: sig_tsmom(c, 120),
    "tsmom_60": lambda c: sig_tsmom(c, 60),
    "tsmom_252": lambda c: sig_tsmom(c, 252),
    "donchian_55_20": lambda c: sig_donchian(c, 55, 20),
    "dual_ma_10_60": lambda c: sig_dual_ma(c, 10, 60),
    "triple_ma_5_20_60": lambda c: sig_triple_ma(c),
    "breakout_20": lambda c: sig_breakout(c, 20),
    "vol_target_tsmom_60": lambda c: sig_vol_target_tsmom(c, 60),
}


# ---------------------------------------------------------------- weights

def r20_rebalance_index(dates: pd.DatetimeIndex) -> np.ndarray:
    return np.arange(0, len(dates), 20)


def month_first_index(dates: pd.DatetimeIndex) -> np.ndarray:
    months = pd.Series(dates.month, index=dates)
    years = pd.Series(dates.year, index=dates)
    keys = years.astype(str) + "-" + months.astype(str)
    first_mask = keys.groupby(keys).cumcount() == 0
    return np.where(first_mask.to_numpy())[0]


def build_weights(state: pd.DataFrame, panel_close: pd.DataFrame,
                  rebalance_idx: np.ndarray | None) -> pd.DataFrame:
    """state: signed direction/multiplier dates x variety; None rebalance_idx
    = daily regime. Weight = state / n_alive (margin-share of equity)."""
    n_alive = panel_close.notna().sum(axis=1)
    w = state.div(n_alive, axis=0)
    if rebalance_idx is None:
        return w.fillna(0.0)
    out = pd.DataFrame(np.nan, index=state.index, columns=state.columns)
    if len(rebalance_idx) == 0:
        return out
    sel = w.iloc[rebalance_idx].fillna(0.0)
    out.iloc[rebalance_idx] = sel.to_numpy()
    return out


def build_null_weights(panel_close: pd.DataFrame, k: int,
                       rebalance_idx: np.ndarray) -> pd.DataFrame:
    """K-th random null: every 20d, each alive variety draws equiprobable
    {-1, 0, +1}; weight = draw / n_alive. Frozen seed 50_000+k."""
    rng = np.random.default_rng(SEED_BASE + k)
    m = panel_close.shape[1]
    out = pd.DataFrame(np.nan, index=panel_close.index, columns=panel_close.columns)
    alive = panel_close.notna().to_numpy()
    for t in rebalance_idx:
        draws = rng.integers(0, 3, size=m) - 1        # {0,1,2} -> {-1,0,1}
        n_alive = int(alive[t].sum())
        if n_alive == 0:
            continue
        row = np.full(m, np.nan)
        row[alive[t]] = draws[alive[t]] / n_alive
        out.iloc[t] = row
    return out


def build_passive_weights(panel_close: pd.DataFrame,
                          rebalance_idx: np.ndarray) -> pd.DataFrame:
    n_alive = panel_close.notna().sum(axis=1)
    out = pd.DataFrame(np.nan, index=panel_close.index, columns=panel_close.columns)
    alive = panel_close.notna().to_numpy()
    for t in rebalance_idx:
        na = int(alive[t].sum())
        if na == 0:
            continue
        out.iloc[t] = np.where(alive[t], 1.0 / na, np.nan)
    return out


# ---------------------------------------------------------------- metrics helpers

def seg_metrics(equity: pd.Series, start: str) -> dict:
    seg = equity[equity.index >= pd.Timestamp(start)]
    if len(seg) < 20:
        return {"status": "insufficient_data", "bars": int(len(seg))}
    rets = seg.pct_change().dropna()
    sd = rets.std(ddof=1)
    sh = float(rets.mean() / sd * math.sqrt(252)) if sd and sd > 0 else 0.0
    total = seg.iloc[-1] / seg.iloc[0] - 1.0
    years = len(seg) / 252.0
    ann = float((1.0 + total) ** (1.0 / years) - 1.0) if years > 0 and seg.iloc[0] > 0 else 0.0
    return {"sharpe": round(sh, 4), "annual_return": round(ann, 4), "bars": int(len(seg))}


def run_cell(panel: dict, weights: pd.DataFrame, cost_mult: float = 1.0) -> dict:
    res = fr.run(panel, weights, start_cash=START_CASH, cost_mult=cost_mult)
    yearly = fr.yearly_returns(res.equity)
    worst = min(yearly.values()) if yearly else 0.0
    return {
        "full": {k: res.metrics[k] for k in
                 ("sharpe", "annual_return", "max_drawdown", "n_trades", "n_entries",
                  "n_closes", "win_rate", "turnover", "final_equity", "groups_pnl")},
        "is2": seg_metrics(res.equity, IS2_START),
        "yearly": yearly,
        "worst_year": round(worst, 4),
        "margin_usage_max_ratio": round(res.metrics.get("margin_usage_max_ratio", float("nan")), 6),
        "per_variety": res.per_variety,
        "_equity": res.equity,
        "_returns": res.equity.pct_change().dropna(),
    }


def public_cell(cell: dict) -> dict:
    """Strip private keys (_equity/_returns) for JSON output."""
    return {k: v for k, v in cell.items() if not k.startswith("_")}


# ---------------------------------------------------------------- gates

def gate_g0() -> dict:
    p = subprocess.run([sys.executable, "-m", "smoke_test"], cwd=ROOT,
                       capture_output=True, text=True, timeout=600)
    tail = p.stdout.split("Summary:")[-1] if "Summary:" in p.stdout else ""
    ok = p.returncode == 0 and "0 FAIL" in tail
    return {"gate": "G0 smoke 23/23", "ok": bool(ok),
            "exit": p.returncode, "summary": tail.strip()[:60]}


def gate_g2() -> dict:
    """Cost constants plausibility + frozen-constant disclosure (CTA_P1 SS3)."""
    ref_px = {"IF": 4000.0, "IC": 6000.0, "IM": 6000.0, "IH": 2800.0, "T": 100.0,
              "TF": 102.0, "RB": 3600.0, "AU": 500.0, "SC": 600.0}
    checks = []
    for v, meta in FUT_META.items():
        notional = meta["mult"] * ref_px[v]
        fee_bp = meta["fee_lot"] / notional * 1e4
        checks.append({
            "variety": v,
            "fee_bp_at_ref": round(fee_bp, 4),
            "fee_bp_ok": bool(0.005 <= fee_bp <= 30.0),
            "margin_ok": bool(0.005 <= meta["margin"] <= 0.25),
            "tick_value_ok": bool(3.0 <= meta["tick"] * meta["mult"] <= 500.0),
            "limit_ok": bool(0.005 <= meta["limit"] <= 0.20),
        })
    ok = all(c["fee_bp_ok"] and c["margin_ok"] and c["tick_value_ok"] and c["limit_ok"]
             for c in checks)
    return {"gate": "G2 tick/fee/mult/margin verification", "ok": bool(ok),
            "checks": checks,
            "disclosure": ("M0923 FUT_UNIVERSE 2026-09 exchange-published approximations, "
                           "frozen at Money0923/quant/futures.py; >30% deviation protocol per "
                           "prereg SS3 (freeze verified value, disclose, don't abort)")}


def gate_g3() -> dict:
    """Data completeness (prereg SS2 four conditions + R50 pre-run amendment)."""
    problems = []
    per_variety = {}
    for v in VARIETIES:
        path = os.path.join(fr.FUT_DIR, f"{v}.csv")
        if not os.path.exists(path):
            problems.append(f"{v}: csv missing")
            continue
        df = pd.read_csv(path, index_col=0, parse_dates=True).sort_index()
        seg = df[(df.index >= pd.Timestamp(WINDOW_START)) & (df.index <= pd.Timestamp(CUTOFF))]
        last = str(seg.index[-1].date()) if len(seg) else None
        if last != CUTOFF:
            problems.append(f"{v}: last bar {last} != cutoff {CUTOFF}")
        for fld in ("open", "high", "low", "close", "volume"):
            col = seg[fld].to_numpy(dtype=float)
            col = col[~np.isnan(col)]
            if len(col) and float(col.min()) < 0:
                problems.append(f"{v}.{fld}: negative values")
        s = seg["close"].dropna()
        in_span = seg["close"][seg.index >= s.index[0]]
        holes = [str(d.date()) for d in in_span.index[in_span.isna()]]
        extra = [h for h in holes if h not in SOURCE_GAP_DATES]
        if extra:
            problems.append(f"{v}: in-span NaN holes {extra}")
        per_variety[v] = {"rows": int(len(seg)), "first": str(s.index[0].date()),
                          "last": last, "holes_in_span": holes}
    return {"gate": "G3 data completeness", "ok": len(problems) == 0,
            "problems": problems, "per_variety": per_variety,
            "source_gap_dates_allowed": sorted(SOURCE_GAP_DATES)}


def gate_g4() -> dict:
    """Null determinism: same-seed double build + double run bit-exact."""
    panel = fr.load_panel(WINDOW_START, CUTOFF)
    ridx = r20_rebalance_index(panel["dates"])
    w1 = build_null_weights(panel["close"], 0, ridx)
    w2 = build_null_weights(panel["close"], 0, ridx)
    if not np.array_equal(w1.to_numpy(), w2.to_numpy(), equal_nan=True):
        return {"gate": "G4 null determinism", "ok": False,
                "stage": "weights rebuild differ"}
    r1 = fr.run(panel, w1, start_cash=START_CASH)
    r2 = fr.run(panel, w2, start_cash=START_CASH)
    eq_ok = np.array_equal(r1.equity.to_numpy(), r2.equity.to_numpy())
    tr_ok = r1.trades == r2.trades
    return {"gate": "G4 null determinism", "ok": bool(eq_ok and tr_ok),
            "equity_bitexact": bool(eq_ok), "trades_bitexact": bool(tr_ok)}


def run_gates(include_g0: bool = True) -> dict:
    out = {}
    if include_g0:
        out["G0"] = gate_g0()
    out["G1"] = engine_selftest()
    out["G2"] = gate_g2()
    out["G3"] = gate_g3()
    out["G4"] = gate_g4()
    return out


# ---------------------------------------------------------------- engine selftest (G1)

def _synthetic_panel() -> dict:
    """Deterministic synthetic 6-day x 2-variety panel for unit assertions."""
    dates = pd.bdate_range("2020-01-01", periods=6)
    px = pd.DataFrame({
        "AU": [500.0, 502.0, 504.0, 506.0, 508.0, 510.0],
        "RB": [3500.0, 3510.0, 3490.0, 3500.0, 3520.0, 3530.0],
    }, index=dates)
    panel = {"dates": dates}
    for fld in ("open", "high", "low", "volume"):
        panel[fld] = px.copy()
    panel["close"] = px.copy()
    panel["open"] = px.copy() * 0.999       # open slightly below close
    return panel


def engine_selftest() -> dict:
    """G1: M0923-semantics unit assertions on a synthetic panel."""
    failures = []
    panel = _synthetic_panel()
    dates = panel["dates"]

    # (b) lots math: AU share 0.10, eq 1M -> floor(100k / (1000*~500*0.08)) = 2 lots
    w = pd.DataFrame(0.10, index=dates, columns=["AU", "RB"])
    res = fr.run(panel, w, start_cash=1_000_000.0)
    au_fills = [t for t in res.trades if t["variety"] == "AU"]
    if not au_fills or sum(t["lots"] for t in au_fills if t["reason"] == "fut_open") != 2:
        failures.append("lots math: AU open lots != 2")
    # (h) T+1: first fill date must be day 1 (weights from day 0 shift)
    if au_fills and au_fills[0]["date"] != str(dates[1].date()):
        failures.append(f"T+1 shift: first fill {au_fills[0]['date']} != day+1")

    # (c) per-variety cap 0.20: share 0.9 -> margin capped -> lots = floor(0.2*eq/40k) = 5
    w_cap = pd.DataFrame(0.90, index=dates, columns=["AU", "RB"])
    res_cap = fr.run(panel, w_cap, start_cash=1_000_000.0)
    au_open = sum(t["lots"] for t in res_cap.trades
                  if t["variety"] == "AU" and t["reason"] == "fut_open")
    if au_open != 5:
        failures.append(f"per-variety cap 20%%: AU open lots {au_open} != 5")

    # (d) margin budget invariant: usage ratio <= 1 every day
    if not (res_cap.metrics["margin_usage_max_ratio"] <= 1.0 + 1e-9):
        failures.append("margin budget: usage ratio > 1")

    # (f) two-way: negative weight -> short; flip produces close+open fills
    w_short = pd.DataFrame(0.10, index=dates, columns=["AU", "RB"])
    w_short.iloc[3] = -0.10                     # flip to short mid-panel
    res_s = fr.run(panel, w_short, start_cash=1_000_000.0)
    flip_day = [t for t in res_s.trades if t["date"] == str(dates[4].date())
                and t["variety"] == "AU"]
    kinds = sorted(t["reason"] for t in flip_day)
    if kinds != ["fut_close", "fut_open"]:
        failures.append(f"two-way flip fills {kinds} != [fut_close, fut_open]")

    # (g) carry: NaN weights -> no fills that day despite price move
    w_carry = pd.DataFrame(np.nan, index=dates, columns=["AU", "RB"])
    w_carry.iloc[0] = 0.10                      # open on day1, then carry
    res_c = fr.run(panel, w_carry, start_cash=1_000_000.0)
    later_fills = [t for t in res_c.trades if t["date"] > str(dates[1].date())]
    if later_fills:
        failures.append(f"carry broken: fills on NaN-weight days {later_fills[:2]}")

    # (e) limit guard: synthetic limit day -> target flat (no new open), close allowed
    panel_lim = _synthetic_panel()
    lim_dates = panel_lim["dates"]
    panel_lim["open"].iloc[3, 0] = panel_lim["close"].iloc[2, 0] * (1 + FUT_META["AU"]["limit"] + 0.02)
    w_lim = pd.DataFrame(0.10, index=lim_dates, columns=["AU", "RB"])
    res_l = fr.run(panel_lim, w_lim, start_cash=1_000_000.0)
    day3 = str(lim_dates[3].date())  # limit-day open; day-2 weights execute there
    opens_on_limit = [t for t in res_l.trades if t["variety"] == "AU"
                      and t["date"] == day3 and t["reason"] == "fut_open"]
    closes_on_limit = [t for t in res_l.trades if t["variety"] == "AU"
                       and t["date"] == day3 and t["reason"] == "fut_close"]
    if opens_on_limit:
        failures.append("limit guard: fut_open executed on limit-up day")
    if not closes_on_limit:
        failures.append("limit guard: closing on limit-up day should be allowed (M0923 flat rule)")

    # (a) determinism: double run bit-exact
    r1 = fr.run(panel, w, start_cash=1_000_000.0)
    r2 = fr.run(panel, w, start_cash=1_000_000.0)
    if not (np.array_equal(r1.equity.to_numpy(), r2.equity.to_numpy())
            and r1.trades == r2.trades):
        failures.append("determinism: double run differs")

    # attribution identity: per-variety daily PnL sums == daily equity change
    pnl_sum = res.daily_pnl.sum(axis=1)
    valid = res.daily_pnl.notna().any(axis=1)
    pnl_sum = pnl_sum[valid]
    diffs = (res.equity - res.equity.shift(1))[valid]
    if not np.allclose(pnl_sum.to_numpy(), diffs.to_numpy(), atol=1e-3):
        failures.append("attribution identity: per-variety PnL != equity delta")
    return {"gate": "G1 futures_runner selftest", "ok": len(failures) == 0,
            "failures": failures}


# ---------------------------------------------------------------- batch run

def do_run() -> int:
    t0 = time.time()
    print("[cta_p1] gates ...")
    gates = run_gates(include_g0=True)
    gates_ok = all(g.get("ok") for g in gates.values())
    for name, g in gates.items():
        print(f"  {name}: {'PASS' if g.get('ok') else 'FAIL'}")
        if not g.get("ok"):
            print(f"    detail: {json.dumps(g, ensure_ascii=False, default=str)[:400]}")
    if not gates_ok:
        print("[cta_p1] GATES FAILED — batch aborted (exit 2), no numbers produced")
        return 2

    panel = fr.load_panel(WINDOW_START, CUTOFF)
    dates = panel["dates"]
    close = panel["close"]
    r20_idx = r20_rebalance_index(dates)
    mon_idx = month_first_index(dates)

    cells: dict[str, dict] = {}
    # 16 candidates x1 + x2 info runs
    for fam_name, builder in FAMILIES.items():
        state = builder(close)
        for regime, ridx in (("daily", None), ("r20", r20_idx)):
            name = f"{fam_name}@{regime}"
            w = build_weights(state, close, ridx)
            cell = run_cell(panel, w, cost_mult=1.0)
            cell_x2 = run_cell(panel, w, cost_mult=2.0)
            cell["x2_full_sharpe"] = cell_x2["full"]["sharpe"]
            cells[name] = cell
            print(f"  {name}: full={cell['full']['sharpe']} x2={cell['x2_full_sharpe']} "
                  f"trades={cell['full']['n_trades']} entries={cell['full']['n_entries']}")
    # 50 nulls
    null_sharpes = []
    null_cells = {}
    for k in range(K_NULLS):
        w = build_null_weights(close, k, r20_idx)
        cell = run_cell(panel, w, cost_mult=1.0)
        null_cells[f"null_{k}"] = public_cell(cell)
        null_sharpes.append(cell["full"]["sharpe"])
    null_vals = [float(x) for x in null_sharpes]
    mu = sum(null_vals) / len(null_vals)
    sigma = math.sqrt(sum((x - mu) ** 2 for x in null_vals) / (len(null_vals) - 1))
    null_summary = {"n": len(null_vals), "mu": round(mu, 4), "sigma": round(sigma, 4),
                    "p95": round(float(np.percentile(null_vals, 95)), 4),
                    "max": round(max(null_vals), 4), "min": round(min(null_vals), 4)}
    # 2 passives
    passive_cells = {}
    passive_sharpes = {}
    for pname, ridx in (("passive_long_r20", r20_idx), ("passive_long_monthly", mon_idx)):
        w = build_passive_weights(close, ridx)
        cell = run_cell(panel, w, cost_mult=1.0)
        passive_cells[pname] = public_cell(cell)
        passive_sharpes[pname] = cell["full"]["sharpe"]
        print(f"  {pname}: full={cell['full']['sharpe']}")

    amended_sha = _sha256_file(PREREG_PATH)
    meta = {
        "window": {"start": WINDOW_START, "end": CUTOFF, "n_days": int(len(dates))},
        "varieties": VARIETIES,
        "start_cash": START_CASH,
        "start_cash_note": ("implementation choice (prereg left unfrozen): 10M CTA "
                            "allocation so whole-lot granularity doesn't dominate "
                            "per-variety margin shares; disclosed per prereg SS3"),
        "rebalance": {"r20_days": int(len(r20_idx)), "monthly_days": int(len(mon_idx))},
        "cost": {v: {"fee_lot": FUT_META[v]["fee_lot"], "tick": FUT_META[v]["tick"],
                     "slippage_per_side_yuan": round(FUT_META[v]["tick"] * FUT_META[v]["mult"], 2)}
                 for v in VARIETIES},
        "prereg_sha_frozen": FROZEN_PREREG_SHA,
        "prereg_sha_at_run": amended_sha,
        "prereg_amendments": ["G3 in-span hole criterion: two source cross-exchange "
                              "calendar-gap dates allowed (2017-10-09, 2019-04-22), "
                              "engine carry+ffill semantics, disclosed (R50 pre-run)"],
    }
    phase1 = {
        "batch": "cta_p1",
        "meta": meta,
        **sg.cutoff_meta(CUTOFF),
        "gates": gates,
        "nulls": {"summary": null_summary,
                  "cells": {k: {"full": v["full"]} for k, v in null_cells.items()}},
        "passive": passive_cells,
        "candidates": {k: public_cell(v) for k, v in cells.items()},
    }
    with open(RESULTS_JSON, "w", encoding="utf-8") as fh:
        json.dump(phase1, fh, ensure_ascii=False, indent=1, default=str)
    print("[cta_p1] phase-1 JSON written (passive pool registered)")

    # ---- verdicts (skill line needs phase-1 passive on file) ----
    null_pool = {"values": null_vals,
                 "coverage": {"n_values": len(null_vals), "mu": mu, "sigma": sigma,
                              "schemas_parsed": ["cta_p1:nulls.summary (K=50 in-batch)"],
                              "known_unparsed": []}}
    line = sg.skill_line_v2(batch_cells=BATCH_CELLS, pool="cta_futures",
                            null_pool=null_pool)
    print(f"[cta_p1] skill_line_v2 = {line['line']} "
          f"(passive_term={line['passive_term']} null_term={line['null_term']})")
    verdicts = {}
    passers = []
    for name, cell in cells.items():
        v = sg.g1_prime_v2(sharpe_full=cell["full"]["sharpe"], returns=cell["_returns"],
                           batch_cells=BATCH_CELLS, pool="cta_futures",
                           null_pool=null_pool, n_trades=cell["full"]["n_trades"],
                           n_entries=cell["full"]["n_entries"])
        # descriptive clauses (batch-level disclosure, prereg SS4)
        is2 = cell["is2"]
        desc = {
            "annual_positive": bool(cell["full"]["annual_return"] > 0),
            "is2_dual_positive": bool(is2.get("sharpe", 0) > 0 and is2.get("annual_return", 0) > 0),
            "dd_ok": bool(cell["full"]["max_drawdown"] >= -0.35),
            "no_crash_year": bool(cell["worst_year"] >= -0.35),
            "x2_info_sharpe": cell["x2_full_sharpe"],
        }
        v["descriptive"] = desc
        verdicts[name] = v
        if v["pass_v2"]:
            passers.append(name)
            print(f"  >> {name} PASSES g1_prime_v2")

    # within-batch pairwise corr (D6 disclosure, all 16)
    rets_df = pd.DataFrame({k: cells[k]["_returns"] for k in cells})
    corr = rets_df.corr()
    within_max = {}
    for name in cells:
        others = corr[name].drop(name).abs()
        within_max[name] = round(float(others.max()), 4) if len(others) else None

    # family PBO for all 8 families (2-cell CSCV, informational) + G2 columns for passers
    from pbo import cscv_pbo, align_returns
    family_pbo = {}
    for fam in FAMILIES:
        pair = {f"{fam}@daily": cells[f"{fam}@daily"]["_returns"],
                f"{fam}@r20": cells[f"{fam}@r20"]["_returns"]}
        mat = align_returns(pair)
        family_pbo[fam] = cscv_pbo(mat)

    verdicts_g2 = {}
    d6_inregister = {}
    if passers:
        try:
            import ew6_portfolio as E
            E._init_worker()                      # loads PRICES_FULL for member_run
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
            fam = name.split("@")[0]
            dsr = sg.deflated_sharpe_ratio(cells[name]["_returns"],
                                            n_trials=line["n_eff"],
                                            var_null_sr=sigma ** 2)
            verdicts_g2[name] = sg.g2_registration_v2(
                g1_pass=True, dsr=dsr, pbo=family_pbo[fam]["pbo"])

    # ---- ledger append (single source, live chain head) ----
    ledger = sg.append_ledger("cta_p1", BATCH_CELLS, "results/shortline_cta_p1.json",
                              evidence_cutoff=CUTOFF,
                              note=("16 candidates (8 TS families x daily/r20) + 50 random "
                                    "nulls (seed 50_000+k) + 2 passive long baselines; "
                                    "prereg research/CTA_P1.md (frozen R49 + G3 pre-run "
                                    "amendment R50); futures-domain own null pool + "
                                    "passive skill line (pool cta_futures)"))
    # ---- audit segment (compute_audit run in-batch, per prereg SS0) ----
    audit_seg = {}
    try:
        subprocess.run([sys.executable, os.path.join("scripts", "compute_audit.py")],
                       cwd=ROOT, capture_output=True, text=True, timeout=120)
    except Exception as exc:  # noqa: BLE001
        print(f"[cta_p1] compute_audit in-batch run failed: {exc}")
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

    # ---- CSV (68 rows) ----
    with open(RESULTS_CSV, "w", newline="", encoding="utf-8") as fh:
        wr = csv.writer(fh)
        wr.writerow(["cell", "family", "regime", "kind", "sharpe_full", "annual_return",
                     "max_drawdown", "worst_year", "is2_sharpe", "is2_annual",
                     "x2_full_sharpe", "n_trades", "n_entries", "turnover", "win_rate",
                     "line", "line_ok", "ci_ok", "pass_v2"])
        for name, cell in cells.items():
            v = verdicts[name]
            fam, reg = name.split("@")
            wr.writerow([name, fam, reg, "candidate", cell["full"]["sharpe"],
                         cell["full"]["annual_return"], cell["full"]["max_drawdown"],
                         cell["worst_year"], cell["is2"].get("sharpe"),
                         cell["is2"].get("annual_return"), cell["x2_full_sharpe"],
                         cell["full"]["n_trades"], cell["full"]["n_entries"],
                         cell["full"]["turnover"], cell["full"]["win_rate"],
                         v["skill_line"]["line"], v["line_ok"],
                         v["ci_lower_bound_positive"], v["pass_v2"]])
        for k in range(K_NULLS):
            c = null_cells[f"null_{k}"]
            wr.writerow([f"null_{k}", "random", "r20", "null", c["full"]["sharpe"],
                         c["full"]["annual_return"], c["full"]["max_drawdown"],
                         c["worst_year"], c["is2"].get("sharpe"), c["is2"].get("annual_return"),
                         "", c["full"]["n_trades"], c["full"]["n_entries"],
                         c["full"]["turnover"], c["full"]["win_rate"],
                         "", "", "", ""])
        for pname, c in passive_cells.items():
            wr.writerow([pname, "passive_long", pname, "passive", c["full"]["sharpe"],
                         c["full"]["annual_return"], c["full"]["max_drawdown"],
                         c["worst_year"], c["is2"].get("sharpe"), c["is2"].get("annual_return"),
                         "", c["full"]["n_trades"], c["full"]["n_entries"],
                         c["full"]["turnover"], c["full"]["win_rate"],
                         "", "", "", ""])

    # ---- gate_attrition entry (search batch) ----
    try:
        with open(ATTRITION_JSON, encoding="utf-8") as fh:
            attr = json.load(fh)
        attr["entries"].append({
            "batch": "CTA_P1",
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
            "eliminated": 16 - len(passers),
            "refs": {"results": "results/shortline_cta_p1.json",
                     "prereg": "research/CTA_P1.md"},
        })
        with open(ATTRITION_JSON, "w", encoding="utf-8") as fh:
            json.dump(attr, fh, ensure_ascii=False, indent=1)
    except Exception as exc:  # noqa: BLE001
        print(f"[cta_p1] attrition append failed: {exc}")

    print(f"[cta_p1] DONE in {time.time() - t0:.1f}s — passers: {passers}")
    print(f"[cta_p1] null summary: {null_summary}")
    print(f"[cta_p1] skill line: {line}")
    return 0


# ---------------------------------------------------------------- selftest (offline)

def do_selftest() -> int:
    fails = []
    # engine unit assertions (G1 body, synthetic panel = offline)
    g1 = engine_selftest()
    if not g1["ok"]:
        fails.extend(g1["failures"])
    # schedule determinism
    dates = pd.bdate_range("2020-01-01", periods=100)
    r20 = r20_rebalance_index(dates)
    mon = month_first_index(dates)
    if list(r20[:3]) != [0, 20, 40]:
        fails.append(f"r20 schedule {list(r20[:3])}")
    if len(mon) < 4:
        fails.append(f"monthly schedule too short {len(mon)}")
    # null weights determinism (offline, synthetic close)
    close = pd.DataFrame({"A": np.arange(100, dtype=float) + 10,
                          "B": np.arange(100, dtype=float) * 0.5 + 5},
                         index=dates)
    w1 = build_null_weights(close, 0, r20)
    w2 = build_null_weights(close, 0, r20)
    if not np.array_equal(w1.to_numpy(), w2.to_numpy(), equal_nan=True):
        fails.append("null weights rebuild differ (synthetic)")
    # passive weights: alive-only long, equal share
    wp = build_passive_weights(close, r20)
    row0 = wp.iloc[0].dropna()
    if len(row0) != 2 or not np.allclose(row0.to_numpy(), 0.5):
        fails.append(f"passive weights row0 {row0.to_dict()}")
    print(f"[cta_p1 selftest] {'ALL PASS' if not fails else 'FAIL: ' + str(fails)}")
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
    print("usage: cta_p1_screen.py gates|run|selftest")
    sys.exit(1)
