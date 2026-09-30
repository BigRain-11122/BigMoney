"""CENSUS-588000-FULLHIST -- 588000 (STAR50 ETF) full-history stress census.

ORDER = O-20260930-1858 sec.2 item e / O-20260930-2054 sec.1 line 4
("588000 full-history stress batch" -- holiday mobilization scientific-face
investment batch). Lane = bm-b (five-member ETF panel owner, R31 precedent,
O-1555 frozen universe; 588000 is the youngest member, 2020-11 inception,
shortest history in the panel -- evidence-hardening census before any
composition-book sleeve consideration per O-1147).

Class discipline (written before run): descriptive census, ZERO N_eff -- no
gates, no nulls, no strategy returns, no registration, no upgrade claim.
Census precedent: a6_corr_regime_probe / gate_census 09-28 (descriptive
measurement faces are legal pre-prereg evidence; no cost-adjusted claims, no
strategy claims). No trials_ledger append (non-judgment face).

Faces (all mechanical, params frozen before run):
  1. coverage  -- bars, first/last date, per-year counts, max calendar gap;
  2. integrity -- OHLC validity, NaN, strict date monotonicity, duplicates;
  3. distribution -- daily log-return stats (ann mean/vol, skew, kurt,
     best/worst day, median |ret|);
  4. drawdown -- max drawdown + top-5 episodes (depth, peak/trough/recovery);
  5. windows -- rolling 20d/60d close-to-close return p5/p50/p95 + top-5
     worst / top-5 best 20d windows (mechanical stress / melt-up faces,
     no narrative window hardcode);
  6. cost stress -- x1/x2 round-trip bp mirrored from FROZEN calibers
     (knowledge/cost_spec.py Face A + knowledge/rules.py CN-C1), plus
     ADV20-based v2 slippage face for this member; drag table at frozen
     turnover budgets;
  7. corr-stress vs 510300 -- rolling 60d corr, z_t = (rho - trailing-250d
     mean)/std(ddof=1), flag-on = z_t >= 2.0 (a6 law mirror, 2020-11 anchor
     window reported honestly);
  8. MA200 gate -- fraction of days close < MA200, longest consecutive
     below-run; forward-20d rets conditional on the gate (descriptive only);
  9. liquidity -- yearly mean daily amount (CNY) trend.

rc contract: 0 = ok, 2 = mechanism fault. Zero network (local panel only).
selftest subcommand = offline legs (synthetic fixture with hand-computed
drawdown/corr/z expectations, determinism double-run, missing-file guard,
integrity-guard coverage, real-panel anchor read).

Usage: python scripts/census_588000_fullhist.py run | selftest
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

if hasattr(sys.stdout, "encoding") and sys.stdout.encoding \
        and sys.stdout.encoding.lower().replace("-", "") not in ("utf8", "utf8mb4"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from knowledge import cost_spec, rules  # noqa: E402  (frozen caliber mirror)

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

MEMBER = "588000"
CORE = "510300"
PANEL_DIR = os.path.join(_REPO_ROOT, "data", "daily")
OUT_PATH = os.path.join(_REPO_ROOT, "results", "census_588000_fullhist.json")
BP = 1e4

# frozen params (written before run)
CORR_WINDOW = 60
MIN_CORR_OBS = 40
Z_WINDOW = 250
Z_TH = 2.0
MA_WINDOW = 200
FWD = 20
ROLL_WINDOWS = (20, 60)
TOP_N = 5
TURNOVER_RTS_PER_YEAR = [1, 2, 4, 12, 26, 52]
DATE_COL = "date"
PRICE_COLS = ("open", "high", "low", "close")


def _load(code: str) -> pd.DataFrame:
    path = os.path.join(PANEL_DIR, f"sh{code}.csv")
    df = pd.read_csv(path)
    need = {DATE_COL, *PRICE_COLS, "volume", "amount"}
    missing = need - set(df.columns)
    if missing:
        raise RuntimeError(f"panel {code}: missing columns {sorted(missing)}")
    return df


def _integrity(df: pd.DataFrame) -> dict:
    dates = pd.to_datetime(df[DATE_COL])
    strict_incr = bool((dates.diff().dropna() > pd.Timedelta(0)).all())
    dup = int(df[DATE_COL].duplicated().sum())
    nan_ohlc = int(df[list(PRICE_COLS)].isna().sum().sum())
    bad_range = int((
        (df["high"] < df["low"])
        | (df["high"] < df["open"]) | (df["high"] < df["close"])
        | (df["low"] > df["open"]) | (df["low"] > df["close"])
    ).sum())
    bad_vol = int((df["volume"] < 0).sum())
    gaps = dates.diff().dropna().sort_values(ascending=False)
    return {
        "strict_date_increasing": strict_incr,
        "duplicate_dates": dup,
        "nan_ohlc": nan_ohlc,
        "ohlc_range_violations": bad_range,
        "negative_volume": bad_vol,
        "max_calendar_gap_days": int(gaps.max().days) if len(gaps) else 0,
        "integrity_clean": bool(strict_incr and dup == 0 and nan_ohlc == 0
                                and bad_range == 0 and bad_vol == 0),
    }


def _distribution(df: pd.DataFrame) -> dict:
    ret = np.log(df["close"].astype(float)).diff().dropna()
    ann_mu = float(ret.mean() * 252)
    ann_vol = float(ret.std(ddof=1) * np.sqrt(252))
    best_i, worst_i = int(ret.idxmax()), int(ret.idxmin())
    # idxmax/idxmin are positional-adjacent labels after dropna on this panel;
    # map back through the original frame defensively
    pos = ret.index.to_numpy()
    def _pos_to_row(i):
        loc = int(np.where(pos == i)[0][0]) if i in pos else None
        return loc
    b_loc, w_loc = _pos_to_row(best_i), _pos_to_row(worst_i)
    def _row_date(loc):
        return str(df[DATE_COL].iloc[loc]) if loc is not None else None
    return {
        "n_returns": int(len(ret)),
        "ann_mean": round(ann_mu, 6),
        "ann_vol": round(ann_vol, 6),
        "skew": round(float(ret.skew()), 6),
        "kurtosis": round(float(ret.kurtosis()), 6),
        "best_day": {"date": _row_date(b_loc),
                     "ret": round(float(ret.max()), 6)},
        "worst_day": {"date": _row_date(w_loc),
                      "ret": round(float(ret.min()), 6)},
        "median_abs_daily_ret": round(float(ret.abs().median()), 6),
        "sharpe_zero_rate_naive": (round(ann_mu / ann_vol, 4)
                                   if ann_vol > 0 else None),
    }


def _drawdowns(df: pd.DataFrame, top: int = TOP_N) -> dict:
    close = df["close"].astype(float).to_numpy()
    dates = df[DATE_COL].astype(str).tolist()
    peak_v = close[0]
    peak_i = 0
    episodes = []
    cur_trough_i = 0
    cur_depth = 0.0
    for i in range(len(close)):
        if close[i] >= peak_v:
            # episode closed if we were underwater
            if cur_depth > 0:
                episodes.append({
                    "peak_date": dates[peak_i], "trough_date": dates[cur_trough_i],
                    "recovery_date": dates[i],
                    "depth": round(cur_depth, 6),
                    "days_underwater": i - peak_i,
                })
            peak_v = close[i]
            peak_i = i
            cur_depth = 0.0
        else:
            depth = (peak_v - close[i]) / peak_v
            if depth > cur_depth:
                cur_depth = depth
                cur_trough_i = i
    if cur_depth > 0:
        episodes.append({
            "peak_date": dates[peak_i], "trough_date": dates[cur_trough_i],
            "recovery_date": None,
            "depth": round(cur_depth, 6),
            "days_underwater": len(close) - 1 - peak_i,
        })
    episodes.sort(key=lambda e: e["depth"], reverse=True)
    max_dd = episodes[0] if episodes else None
    return {"max_drawdown": max_dd, "top_episodes": episodes[:top],
            "n_episodes_any_depth": len(episodes)}


def _roll_windows(df: pd.DataFrame) -> dict:
    out = {}
    close = df["close"].astype(float)
    for w in ROLL_WINDOWS:
        r = close.shift(1).rolling(w).apply(
            lambda s: s.iloc[-1] / s.iloc[0] - 1.0, raw=False)
        r = r.dropna()
        out[f"roll_{w}d"] = {
            "p5": round(float(r.quantile(0.05)), 6),
            "p50": round(float(r.quantile(0.50)), 6),
            "p95": round(float(r.quantile(0.95)), 6),
        }
        if w == 20:
            ranks = r.sort_values()
            worst = [
                {"end_date": str(df[DATE_COL].iloc[int(i)]),
                 "ret": round(float(v), 6)}
                for i, v in ranks.head(TOP_N).items()]
            best = [
                {"end_date": str(df[DATE_COL].iloc[int(i)]),
                 "ret": round(float(v), 6)}
                for i, v in ranks.tail(TOP_N).iloc[::-1].items()]
            out["worst_20d_windows"] = worst
            out["best_20d_windows"] = best
    return out


def _cost_faces(df: pd.DataFrame) -> dict:
    etf_fee = rules.FeeSchedule()  # default ETF caliber (frozen, account_cost_tax mirror)
    x1_buy_bp = cost_spec.x1_side_rate(etf_fee) * BP
    x1_sell_bp = cost_spec.x1_sell_side_rate(etf_fee) * BP
    # ADV20 face for this member (mirrors account_cost_tax v2 face)
    amt = df["amount"].astype(float).to_numpy()
    adv20 = float(np.mean(amt[-20:])) if len(amt) >= 20 else None
    slip_bp = rules.cost_v2_slippage(adv20) * BP if adv20 else None
    v2_side_bp = x1_buy_bp - etf_fee.slippage_a * BP + slip_bp if slip_bp \
        else None
    rt_x1 = x1_buy_bp + x1_sell_bp
    return {
        "caliber": "knowledge/cost_spec.py Face A + knowledge/rules.py (frozen mirror)",
        "x1_side_buy_bp": round(x1_buy_bp, 4),
        "x1_side_sell_bp": round(x1_sell_bp, 4),
        "x1_round_trip_bp": round(rt_x1, 4),
        "x2_stress_round_trip_bp": round(rt_x1 * 2, 4),
        "adv20_yuan_tail": round(adv20, 2) if adv20 else None,
        "v2_slippage_bp_tail": round(slip_bp, 4) if slip_bp else None,
        "v2_side_buy_bp_tail": round(v2_side_bp, 4) if v2_side_bp else None,
        "t_plus": "T+0" if rules.is_t0(MEMBER) else "T+1",
        "drag_table_bp": [
            {"round_trips_per_year": rts,
             "annual_drag_bp_x1": round(rt_x1 * rts, 2),
             "annual_drag_bp_x2_stress": round(rt_x1 * 2 * rts, 2)}
            for rts in TURNOVER_RTS_PER_YEAR],
    }


def _corr_stress(df_m: pd.DataFrame, df_c: pd.DataFrame) -> dict:
    m = pd.DataFrame({
        "d": df_m[DATE_COL].astype(str),
        "c": df_m["close"].astype(float)}).set_index("d")
    c = pd.DataFrame({
        "d": df_c[DATE_COL].astype(str),
        "c": df_c["close"].astype(float)}).set_index("d")
    j = m.join(c, lsuffix="_m", rsuffix="_c", how="inner").dropna()
    rm = np.log(j["c_m"]).diff()
    rc = np.log(j["c_c"]).diff()
    rho = rm.rolling(CORR_WINDOW).corr(rc)
    rho = rho.dropna()
    # min co-valid obs inside window guard
    nvalid = rm.notna().rolling(CORR_WINDOW).sum()
    rho = rho[nvalid.reindex(rho.index) >= MIN_CORR_OBS]
    z = (rho - rho.rolling(Z_WINDOW, min_periods=Z_WINDOW).mean()) \
        / rho.rolling(Z_WINDOW, min_periods=Z_WINDOW).std(ddof=1)
    z = z.dropna()
    flagged = z[z >= Z_TH]
    anchor = j.loc[(j.index >= "2020-11-16") & (j.index <= "2021-02-28")]
    return {
        "pair": f"{MEMBER}~{CORE}",
        "joint_days": int(len(j)),
        "corr_p5": round(float(rho.quantile(0.05)), 4),
        "corr_p50": round(float(rho.quantile(0.50)), 4),
        "corr_p95": round(float(rho.quantile(0.95)), 4),
        "z_threshold": Z_TH,
        "flag_on_days": int(len(flagged)),
        "flag_on_dates_head": [str(i) for i in flagged.index[:12]],
        "inception_anchor_2020_11_16_to_2021_02_28_days": int(len(anchor)),
        "inception_anchor_flag_on": int(len(
            [i for i in flagged.index
             if "2020-11-16" <= i <= "2021-02-28"])),
    }


def _ma200(df: pd.DataFrame) -> dict:
    close = df["close"].astype(float)
    ma = close.rolling(MA_WINDOW).mean()
    below = (close < ma).dropna()
    frac = float(below.mean())
    # longest consecutive below-run
    runs, cur = [], 0
    for b in below.to_numpy():
        cur = cur + 1 if b else 0
        runs.append(cur)
    longest = int(max(runs)) if runs else 0
    # forward-20d conditional rets (descriptive only)
    fwd = close.shift(-FWD) / close - 1.0
    cond = pd.DataFrame({"below": below, "fwd": fwd}).dropna()
    g_below = cond[cond["below"]]["fwd"]
    g_above = cond[~cond["below"]]["fwd"]
    return {
        "ma_window": MA_WINDOW,
        "frac_days_below_ma200": round(frac, 4),
        "longest_consecutive_below_days": longest,
        "fwd20_mean_on_below_days": round(float(g_below.mean()), 6)
        if len(g_below) else None,
        "fwd20_mean_on_above_days": round(float(g_above.mean()), 6)
        if len(g_above) else None,
        "n_cond_days": int(len(cond)),
    }


def _liquidity(df: pd.DataFrame) -> dict:
    d = df.copy()
    d["year"] = d[DATE_COL].astype(str).str.slice(0, 4)
    g = d.groupby("year")["amount"].mean()
    return {y: round(float(v), 2) for y, v in g.items()}


def run() -> int:
    try:
        df = _load(MEMBER)
        df_core = _load(CORE)
        faces = {
            "coverage": {
                "n_bars": int(len(df)),
                "first_date": str(df[DATE_COL].iloc[0]),
                "last_date": str(df[DATE_COL].iloc[-1]),
                "per_year_bars": {
                    y: int(v) for y, v in
                    df[DATE_COL].astype(str).str.slice(0, 4).value_counts()
                    .sort_index().items()},
            },
            "integrity": _integrity(df),
            "distribution": _distribution(df),
            "drawdown": _drawdowns(df),
            "roll_windows": _roll_windows(df),
            "cost_stress": _cost_faces(df),
            "corr_stress_vs_core": _corr_stress(df, df_core),
            "ma200_gate": _ma200(df),
            "liquidity_yearly_mean_amount_cny": _liquidity(df),
        }
        evidence_cutoff = str(df[DATE_COL].iloc[-1])
        out = {
            "schema": "census_588000_fullhist_v1",
            "order_ref": "O-20260930-1858 sec.2-e / O-20260930-2054 sec.1 "
                         "(588000 full-history stress batch, leg-1 census)",
            "batch_class": "descriptive census (zero N_eff, non-judgment)",
            "member": MEMBER,
            "evidence_cutoff": evidence_cutoff,
            "generated": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
            "faces": faces,
        }
        with open(OUT_PATH, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
        print(f"census ok -> {OUT_PATH} (evidence_cutoff={evidence_cutoff}, "
              f"n_bars={len(df)})")
        return 0
    except Exception as e:
        print(f"census mechanism fault: {type(e).__name__}: {e}")
        return 2


def _selftest() -> int:
    fails = []

    # leg 1: synthetic fixture -- drawdown + corr + z expectations
    # close path: 100,120,90,60,100,110,55,90,130,140
    # one continuous underwater episode from peak 120 (idx1): deepest trough
    # 55 (idx6) -> depth (120-55)/120 = 0.541667, recovered at idx8 (130>=120)
    dates = pd.date_range("2024-01-01", periods=10, freq="D").strftime("%Y-%m-%d")
    close = [100, 120, 90, 60, 100, 110, 55, 90, 130, 140]
    df = pd.DataFrame({"date": dates, "open": close, "high": [c + 1 for c in close],
                       "low": [c - 1 for c in close], "close": close,
                       "volume": [1e6] * 10, "amount": [1e8] * 10})
    dd = _drawdowns(df)
    if abs(dd["max_drawdown"]["depth"] - (120 - 55) / 120) > 1e-6:
        fails.append(f"drawdown depth {dd['max_drawdown']['depth']} != 0.541667")
    if dd["max_drawdown"]["peak_date"] != dates[1] or \
            dd["max_drawdown"]["trough_date"] != dates[6] or \
            dd["max_drawdown"]["recovery_date"] != dates[8]:
        fails.append("drawdown peak/trough/recovery dates wrong")
    if dd["n_episodes_any_depth"] != 1:
        fails.append(f"episodes {dd['n_episodes_any_depth']} != 1 "
                     "(single continuous underwater episode)")

    # leg 2: corr + z on synthetic perfectly-correlated pair
    # close = 1 + linspace: strictly positive, identical for both members ->
    # log-returns identical -> corr == 1.0, zero std -> z NaN -> zero flags
    n = 320
    d2 = pd.date_range("2023-01-01", periods=n, freq="D").strftime("%Y-%m-%d")
    x = np.linspace(0, 1, n)
    dfm = pd.DataFrame({"date": d2, "open": 1 + x, "high": 1 + x, "low": 1 + x,
                        "close": 1 + x, "volume": [1.0] * n, "amount": [1.0] * n})
    dfc = dfm.copy()
    cs = _corr_stress(dfm, dfc)
    if abs(cs["corr_p50"] - 1.0) > 1e-6:
        fails.append(f"corr p50 {cs['corr_p50']} != 1.0 (perfect pair)")
    # perfect corr -> zero std -> z NaN -> flag_on_days must be 0 (honest)
    if cs["flag_on_days"] != 0:
        fails.append(f"flag_on_days {cs['flag_on_days']} != 0 on zero-var corr")

    # leg 3: integrity guard catches violations
    bad = df.copy()
    bad.loc[2, "high"] = bad.loc[2, "low"] - 5  # range violation
    ig = _integrity(bad)
    if ig["ohlc_range_violations"] != 1:
        fails.append(f"integrity guard miss: {ig['ohlc_range_violations']}")

    # leg 4: missing-file guard
    try:
        _load("999999")
        fails.append("missing-file guard did not raise")
    except Exception:
        pass

    # leg 5: determinism double-run on real panel
    if os.path.exists(os.path.join(PANEL_DIR, f"sh{MEMBER}.csv")):
        a = _drawdowns(_load(MEMBER))
        b = _drawdowns(_load(MEMBER))
        if json.dumps(a, sort_keys=True) != json.dumps(b, sort_keys=True):
            fails.append("determinism double-run mismatch (drawdowns)")
        real = _load(MEMBER)
        if str(real[DATE_COL].iloc[0]) != "2020-11-16":
            fails.append(f"real-panel anchor first bar "
                         f"{real[DATE_COL].iloc[0]} != 2020-11-16")
    else:
        fails.append("real panel missing (selftest requires local sh588000.csv)")

    # leg 6: MA200 math on synthetic
    ma = _ma200(dfm)
    if ma["frac_days_below_ma200"] != 0.0:
        fails.append(f"monotonic-up fixture below-MA frac "
                     f"{ma['frac_days_below_ma200']} != 0.0")

    if fails:
        print("SELFTEST FAIL:")
        for f in fails:
            print(" -", f)
        return 2
    print("selftest: 6/6 legs PASS")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "selftest"])
    a = ap.parse_args()
    return _selftest() if a.cmd == "selftest" else run()


if __name__ == "__main__":
    sys.exit(main())
