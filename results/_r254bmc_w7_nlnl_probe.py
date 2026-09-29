# -*- coding: utf-8 -*-
"""_r254bmc_w7_nlnl_probe.py -- INNOVATION-QUOTA-SLOT-7 berth probe (zoo #87
nh_nl_breadth / NNL-BREADTH-P1 candidate family).

Berth-time probe faces (read-only, zero engine/admission touch):
  F1 G-ANCHOR face   : core48 NH/NL breadth series, W in {20, 60}
                       B_t = (NH_t - NL_t) / valid_t  (valid = members with
                       full W-lookback as-of t; honest denominator).
  F2 D6 signal face : corr(B_t, REGIME_GUARD below-MA20 share series) on the
                       full common window -- nearest in-book narrative neighbor
                       (breadth), construction differs (NH-NL net new
                       extremes vs below-MA20 share). Signal-level read only;
                       cell-level merge clause stays a freeze/judge face.
  F3 descriptive fwd : core48 equal-weight fwd 20d/5d returns conditional on
                       B20 tail deciles -- descriptive census only (overlapping
                       windows, no costs, NOT a strategy claim).

Output: results/_r254bmc_w7_nlnl_probe_facts.json (evidence_cutoff anchored).
Exit 0 normal / 2 mechanism fault (honest, no masking).
"""
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DAILY = os.path.join(ROOT, "data", "daily")
OUT = os.path.join(ROOT, "results", "_r254bmc_w7_nlnl_probe_facts.json")
WINDOWS = (20, 60)


def load_core48() -> tuple[pd.DataFrame, list[str]]:
    """Bare-code core48 close panel (date x code), sorted, de-duplicated."""
    frames = {}
    for fn in os.listdir(DAILY):
        if not fn.endswith(".csv"):
            continue
        code = fn[:-4]
        if not code.isdigit() or len(code) != 6:
            continue  # skip prefixed/special files
        df = pd.read_csv(os.path.join(DAILY, fn), parse_dates=["date"])
        s = df.set_index("date")["close"].astype(float).sort_index()
        s = s[~s.index.duplicated(keep="last")]
        frames[code] = s
    panel = pd.DataFrame(frames).sort_index()
    return panel, list(frames.keys())


def breadth_series(closes: pd.DataFrame, w: int) -> pd.DataFrame:
    """Per-date NH/NL counts + net breadth B_t over members with full lookback."""
    nh = pd.DataFrame(index=closes.index)
    nl = pd.DataFrame(index=closes.index)
    valid = pd.DataFrame(index=closes.index)
    for code, s in closes.items():
        roll_max = s.rolling(w).max()
        roll_min = s.rolling(w).min()
        ok = s.rolling(w).count() >= w  # full W-lookback present
        nh[code] = (s == roll_max) & ok
        nl[code] = (s == roll_min) & ok
        valid[code] = ok
    nh_n = nh.sum(axis=1)
    nl_n = nl.sum(axis=1)
    valid_n = valid.sum(axis=1)
    b = (nh_n - nl_n) / valid_n.replace(0, np.nan)
    return pd.DataFrame({"nh": nh_n, "nl": nl_n, "valid": valid_n, "b": b})


def below_ma20_share(closes: pd.DataFrame) -> pd.Series:
    """REGIME_GUARD breadth leg semantics, full-series reconstruction:
    share of members (with full 20-bar MA history as-of t) whose close is
    below their own MA20. Mirrors scripts/market_regime.py breadth_dims."""
    below = pd.DataFrame(index=closes.index)
    valid = pd.DataFrame(index=closes.index)
    for code, s in closes.items():
        ma = s.rolling(20).mean()
        ok = s.rolling(20).count() >= 20
        below[code] = (s < ma) & ok
        valid[code] = ok
    v = valid.sum(axis=1)
    return (below.sum(axis=1) / v.replace(0, np.nan)).where(v >= 10)


def fwd_ret(ew: pd.Series, h: int) -> pd.Series:
    """Forward h-day cumulative return of the equal-weight face."""
    return (ew.shift(-h) / ew - 1.0)


def main() -> int:
    try:
        closes, codes = load_core48()
        cutoff = str(closes.index[-1].date())
        ew_ret = closes.pct_change().mean(axis=1)
        ew = (1.0 + ew_ret.fillna(0.0)).cumprod()

        facts = {
            "probe": "INNOVATION-QUOTA-SLOT-7 berth probe (zoo #87 nh_nl_breadth)",
            "machine": "bm-c",
            "round": "r254",
            "evidence_cutoff": cutoff,
            "panel": {
                "n_symbols": len(codes),
                "first_date": str(closes.index[0].date()),
                "last_date": cutoff,
                "n_dates_total": int(len(closes)),
            },
            "windows": {},
            "d6_signal_face": {},
            "descriptive_fwd_face": {"note": ("descriptive census only; overlapping "
                                              "windows inflate t; no costs; NOT a "
                                              "strategy claim")},
        }

        b_series = {}
        for w in WINDOWS:
            bd = breadth_series(closes, w)
            m = bd["valid"] >= 30
            bdv = bd[m]
            b = bdv["b"].dropna()
            b_series[w] = b
            q10, q50, q90 = (float(b.quantile(q)) for q in (0.10, 0.50, 0.90))
            facts["windows"][f"W{w}"] = {
                "n_valid_days": int(len(b)),
                "valid_min": int(bdv["valid"].min()),
                "valid_max": int(bdv["valid"].max()),
                "first_valid_date": str(b.index[0].date()),
                "b_mean": round(float(b.mean()), 4),
                "b_std": round(float(b.std()), 4),
                "b_min": round(float(b.min()), 4),
                "b_p5": round(float(b.quantile(0.05)), 4),
                "b_p50": round(q50, 4),
                "b_p95": round(float(b.quantile(0.95)), 4),
                "b_max": round(float(b.max()), 4),
                "b_q10": round(q10, 4),
                "b_q90": round(q90, 4),
                "days_nh_ge_10": int((bdv["nh"] >= 10).sum()),
                "days_nl_ge_10": int((bdv["nl"] >= 10).sum()),
                "days_all_member_nh": int((bdv["nh"] == bdv["valid"]).sum()),
                "days_all_member_nl": int((bdv["nl"] == bdv["valid"]).sum()),
            }

        # F2 D6 signal face: vs REGIME_GUARD below-MA20 share
        below = below_ma20_share(closes)
        for w in WINDOWS:
            common = b_series[w].index.intersection(below.dropna().index)
            x, y = b_series[w].loc[common], below.loc[common]
            corr = float(np.corrcoef(x, y)[0, 1]) if len(common) > 100 else None
            facts["d6_signal_face"][f"B_W{w}_vs_below_ma20_share"] = {
                "n_common_days": int(len(common)),
                "pearson": None if corr is None else round(corr, 4),
                "verdict_note": ("signal-level only; cell-level merge clause "
                                 "remains freeze/judge face per prereg sec.1"),
            }

        # F3 descriptive forward face on B20 tails
        b20 = b_series[20]
        q10, q90 = float(b20.quantile(0.10)), float(b20.quantile(0.90))
        for h in (5, 20):
            fwd = fwd_ret(ew, h)
            common = b20.index.intersection(fwd.dropna().index)
            lo = fwd.loc[common][b20.loc[common] <= q10]
            hi = fwd.loc[common][b20.loc[common] >= q90]
            mid = fwd.loc[common][(b20.loc[common] > q10) & (b20.loc[common] < q90)]
            def _st(x: pd.Series) -> dict:
                return {"n": int(len(x)), "mean": round(float(x.mean()), 5),
                        "std": round(float(x.std()), 5)}
            facts["descriptive_fwd_face"][f"fwd_{h}d"] = {
                "b20_le_q10_capitulation": _st(lo),
                "b20_ge_q90_euphoria": _st(hi),
                "mid_band": _st(mid),
                "spread_hi_minus_lo_mean": round(float(hi.mean() - lo.mean()), 5),
            }

        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(facts, f, ensure_ascii=False, indent=1)
        print(json.dumps(facts, ensure_ascii=False, indent=1))
        return 0
    except Exception as exc:  # honest fault, no masking
        import traceback
        traceback.print_exc()
        print(f"PROBE FAULT: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
