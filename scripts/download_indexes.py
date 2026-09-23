"""Download major China indices daily."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import akshare as ak
import pandas as pd
from config import PATHS

INDEXES = {
    "sh000300": "csi300",
    "sh000905": "csi500",
    "sh000852": "csi1000",
    "sh000016": "sse50",
    "sh000688": "star50",
    "sz399006": "chinext",
    "sh000001": "sse",
    "sz399001": "szse",
}

def main():
    os.makedirs(PATHS.basic_dir, exist_ok=True)
    for code, name in INDEXES.items():
        out = os.path.join(PATHS.basic_dir, f"{name}.csv")
        if os.path.exists(out):
            print(f"  skip {name}")
            continue
        try:
            df = ak.stock_zh_index_daily(symbol=code)
            df = df.rename(columns={"date": "date", "close": "close"})
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date").set_index("date")
            df.to_csv(out, encoding="utf-8")
            print(f"  {name}: {len(df)} rows")
        except Exception as e:
            print(f"  {name} fail: {e}")

if __name__ == "__main__":
    main()
