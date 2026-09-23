"""Download real ETF daily data (forward-adjusted) from EastMoney via AKShare."""
import os
import sys
import time
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import PATHS

import akshare as ak

UNIVERSE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "..", "etf_trading_system", "universe", "etf_universe.csv")

START = "20200101"
END = time.strftime("%Y%m%d")
OUT_DIR = PATHS.daily_dir


def fetch_one(code: str, exchange: str) -> pd.DataFrame:
    """Try multiple sources: sina -> tx -> baostock."""
    # Sina: sh510300 / sz159915
    prefix = "sh" if exchange == "SSE" else "sz"
    sym = f"{prefix}{code}"
    try:
        k = ak.fund_etf_hist_sina(symbol=sym)
        if k is not None and not k.empty:
            return k
    except Exception as e:
        print(f"    sina {sym} fail: {type(e).__name__}")
    return pd.DataFrame()


def main():
    df = pd.read_csv(UNIVERSE, dtype={"code": str})
    print(f"universe: {len(df)} ETFs, {START} -> {END}")
    ok, fail = 0, 0
    for _, row in df.iterrows():
        code = row["code"].zfill(6)
        out_path = os.path.join(OUT_DIR, f"{code}.csv")
        if os.path.exists(out_path):
            ok += 1
            continue
        try:
            k = fetch_one(code, row["exchange"])
            if k is None or k.empty:
                print(f"  {code} EMPTY")
                fail += 1
                continue
            k = k.rename(columns={
                "date": "date", "open": "open", "high": "high",
                "low": "low", "close": "close",
                "volume": "volume",
            })
            if "amount" not in k.columns:
                k["amount"] = np.nan
            k = k[["date", "open", "high", "low", "close", "volume", "amount"]]
            k["date"] = pd.to_datetime(k["date"]).dt.strftime("%Y-%m-%d")
            # filter by date range
            k = k[(k["date"] >= START[:4] + "-" + START[4:6] + "-" + START[6:])]
            k.to_csv(out_path, index=False)
            print(f"  {code} {row['name']} {len(k)} rows")
            ok += 1
        except Exception as e:
            print(f"  {code} FAIL {type(e).__name__}: {e}")
            fail += 1
        time.sleep(0.3)
    print(f"done: {ok} ok, {fail} fail")


if __name__ == "__main__":
    main()
