"""Fetch full ETF list from Sina, then batch download daily history.

Output:
  data/basic/etf_list.csv   - all ETFs
  data/daily/<code>.csv      - per-ETF daily bars
"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import akshare as ak
import pandas as pd
from config import PATHS


def fetch_list():
    """Get all ETFs from Sina."""
    print("fetching ETF list from Sina...")
    df = ak.fund_etf_category_sina(symbol="ETF基金")
    print(f"  got {len(df)} ETFs")
    print(df.head())
    print("cols:", list(df.columns))
    out = os.path.join(PATHS.basic_dir, "etf_list.csv")
    df.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"saved: {out}")
    return df


def download_one(code: str, start: str = "2018-01-01"):
    """Download one ETF daily. Code like 'sh510300'."""
    try:
        df = ak.fund_etf_hist_sina(symbol=code)
        if df is None or len(df) == 0:
            return None
        df = df.rename(columns={
            "date": "date", "open": "open", "high": "high",
            "low": "low", "close": "close", "volume": "volume",
        })
        if "amount" not in df.columns:
            df["amount"] = df["close"] * df["volume"]
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").set_index("date")
        df = df[["open", "high", "low", "close", "volume", "amount"]]
        return df
    except Exception as e:
        print(f"  {code} fail: {e}")
        return None


def main():
    list_path = os.path.join(PATHS.basic_dir, "etf_list.csv")
    if not os.path.exists(list_path):
        df = fetch_list()
    else:
        df = pd.read_csv(list_path)

    # Sina uses 'sh510300' / 'sz159915' format, column is '代码'
    codes = df["代码"].tolist()
    print(f"total codes: {len(codes)}, sample: {codes[:3]}")

    # Skip already-downloaded
    done = set(f.replace(".csv", "") for f in os.listdir(PATHS.daily_dir) if f.endswith(".csv"))
    todo = [c for c in codes if c not in done]
    print(f"already: {len(done)}, todo: {len(todo)}")

    os.makedirs(PATHS.daily_dir, exist_ok=True)
    for i, code in enumerate(todo):
        if i % 20 == 0:
            print(f"  [{i}/{len(todo)}] {code}")
        df = download_one(code)
        if df is not None and len(df) > 30:
            df.to_csv(os.path.join(PATHS.daily_dir, f"{code}.csv"),
                      encoding="utf-8")
        time.sleep(0.3)


if __name__ == "__main__":
    main()
