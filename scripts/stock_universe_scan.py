"""Stock-pool universe scan for P-4 batch 2 (B-layer) spec evidence.

One pass over Money02/data/bars/*.parquet. Read-only recon: board mix,
listing dates, liquidity, ST-regime proxy (sealed 5% boards), limit-board
day counts. No signals, no engine runs.
Output: results/shortline_stock_universe_scan.json + research/shortline/stock_universe_scan.csv
"""
from __future__ import annotations

import glob
import json
import os
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

BARS_DIR = os.path.join("Money02", "data", "bars")
OUT_JSON = os.path.join("results", "shortline_stock_universe_scan.json")
OUT_CSV = os.path.join("research", "shortline", "stock_universe_scan.csv")


def board_of(code: str) -> str:
    if code.startswith(("300", "301")):
        return "chinext"      # 创业板
    if code.startswith("688"):
        return "star"        # 科创板
    if code.startswith(("8", "4", "92")):
        return "bse"         # 北交所
    if code.startswith(("60", "00")):
        return "main"        # 沪深主板
    return "other"


def scan_one(path: str) -> dict:
    code = os.path.basename(path).split(".")[0]
    try:
        df = pd.read_parquet(path, columns=["date", "close", "high", "pct_chg", "amount"])
    except Exception as e:  # noqa: BLE001
        return {"code": code, "error": str(e)[:80]}
    if df.empty:
        return {"code": code, "error": "empty"}
    d = df["date"].astype(str)
    close = df["close"].to_numpy(float)
    high = df["high"].to_numpy(float)
    pct = df["pct_chg"].to_numpy(float)
    amt = pd.to_numeric(df["amount"], errors="coerce").to_numpy(float)
    n = len(df)
    sealed_close = (np.isfinite(high) & np.isfinite(close) & (high > 0) & (close > 0)
                    & (np.abs(high / close - 1.0) < 1e-6))
    sealed5 = int(np.nansum(sealed_close & (pct >= 4.6) & (pct <= 5.4)))
    sealed10 = int(np.nansum(sealed_close & (pct >= 9.4) & (pct <= 10.6)))
    sealed20 = int(np.nansum(sealed_close & (pct >= 19.4) & (pct <= 20.6)))
    sealed_dn = int(np.nansum(sealed_close & (pct <= -4.6) & (pct >= -10.6)))
    last20_amt = float(np.nanmean(amt[-20:])) if n >= 20 else float("nan")
    min_close60 = float(np.nanmin(close[-60:])) if n >= 1 else float("nan")
    return {
        "code": code, "board": board_of(code), "rows": n, "error": None,
        "first": d.iloc[0], "last": d.iloc[-1],
        "last20_amt_yi": round(last20_amt / 1e8, 4) if np.isfinite(last20_amt) else None,
        "min_close60": round(min_close60, 3) if np.isfinite(min_close60) else None,
        "sealed5": sealed5, "sealed10": sealed10, "sealed20": sealed20,
        "sealed_dn": sealed_dn,
    }


def main() -> None:
    paths = sorted(glob.glob(os.path.join(BARS_DIR, "*.parquet")))
    print(f"scanning {len(paths)} stock bars ...", flush=True)
    with ProcessPoolExecutor(max_workers=12) as ex:  # O-1738 cap: bm-b <= 12
        rows = list(ex.map(scan_one, paths, chunksize=64))
    df = pd.DataFrame(rows)
    ok = df[df["error"].isna()].copy()
    agg = {
        "n_bars_files": len(paths),
        "n_ok": int(len(ok)),
        "n_error": int(len(df) - len(ok)),
        "board_mix": ok["board"].value_counts().to_dict(),
        "last_date_max": str(ok["last"].max()),
        "fresh_f1_ge_0916": int((ok["last"] >= "2026-09-16").sum()),
        "stale_pre_sep": int((ok["last"] < "2026-09-01").sum()),
        "amt_ge_20m_last20": int((ok["last20_amt_yi"] >= 0.2).sum()),
        "amt_ge_50m_last20": int((ok["last20_amt_yi"] >= 0.5).sum()),
        "amt_ge_100m_last20": int((ok["last20_amt_yi"] >= 1.0).sum()),
        "price_lt_1_last60": int((ok["min_close60"] < 1.0).sum()),
        "st_regime_proxy": int(((ok["sealed5"] >= 3) & (ok["sealed10"] == 0)).sum()),
        "has_sealed10_ge1": int((ok["sealed10"] >= 1).sum()),
        "rows_ge_500": int((ok["rows"] >= 500).sum()),
        "first_year_median": str(int(ok["first"].str[:4].astype(int).median())),
    }
    fy = ok["first"].str[:4].astype(int)
    agg["first_year_hist"] = {
        f"{b}s": int(((fy >= b) & (fy < b + 10)).sum()) for b in (1990, 2000, 2010, 2020)
    }
    os.makedirs("results", exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(agg, f, ensure_ascii=False, indent=2)
    keep = ["code", "board", "rows", "first", "last", "last20_amt_yi",
            "min_close60", "sealed5", "sealed10", "sealed20", "sealed_dn"]
    ok[keep].to_csv(OUT_CSV, index=False, encoding="utf-8")
    print(json.dumps(agg, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
