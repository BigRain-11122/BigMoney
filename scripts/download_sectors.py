"""Download sector indices and northbound flow for factor research."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import PATHS
import akshare as ak
import pandas as pd

OUT = os.path.join(PATHS.data_dir, "sector")
os.makedirs(OUT, exist_ok=True)

# 1) SW level-1 industry indices
print("=== SW level-1 industries ===")
try:
    sw = ak.sw_index_first_info()
    print(f"got {len(sw)} industries")
    print(sw.head())
except Exception as e:
    print(f"sw list fail: {e}")
    sw = pd.DataFrame()

# try the daily API
SECTORS = [
    "801010", "801030", "801050", "801080", "801110", "801120",
    "801130", "801140", "801150", "801160", "801170", "801180",
    "801200", "801210", "801230", "801710", "801720", "801730",
    "801740", "801750", "801760", "801770", "801780", "801790",
    "801880", "801890", "801950", "801960", "801970", "801980",
]

ok = 0
for code in SECTORS:
    out = os.path.join(OUT, f"{code}.csv")
    if os.path.exists(out):
        ok += 1
        continue
    try:
        df = ak.sw_index_daily(symbol=code)
        if df is None or df.empty:
            continue
        df.to_csv(out, index=False)
        ok += 1
        print(f"  {code} {len(df)} rows")
        time.sleep(0.2)
    except Exception as e:
        print(f"  {code} fail: {type(e).__name__}")
print(f"sectors: {ok}/{len(SECTORS)}")

# 2) Northbound flow
print("\n=== Northbound flow ===")
try:
    nb = ak.stock_hsgt_north_net_flow_in_em(symbol="北上")
    nb.to_csv(os.path.join(PATHS.basic_dir, "northbound.csv"), index=False)
    print(f"northbound: {len(nb)} rows")
except Exception as e:
    print(f"northbound fail: {e}")
