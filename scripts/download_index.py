"""Download CSI300 index (sh000300) for market regime filter."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import PATHS
import akshare as ak
import pandas as pd

out = os.path.join(PATHS.basic_dir, "csi300.csv")
k = ak.stock_zh_index_daily(symbol="sh000300")
k = k.rename(columns={"date": "date", "open": "open", "high": "high",
                       "low": "low", "close": "close", "volume": "volume"})
k["date"] = pd.to_datetime(k["date"]).dt.strftime("%Y-%m-%d")
k = k[k["date"] >= "2020-01-01"]
k.to_csv(out, index=False)
print(f"CSI300: {len(k)} rows -> {out}")
print(k.tail(3))
