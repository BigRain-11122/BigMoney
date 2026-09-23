"""Save all tradable universe lists."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import akshare as ak
from config import PATHS

out_dir = PATHS.basic_dir
os.makedirs(out_dir, exist_ok=True)

# 1. ETF list from sina
print("=== ETF list (sina) ===")
etf = ak.fund_etf_category_sina(symbol="ETF基金")
print(f"rows: {len(etf)}")
print("cols:", list(etf.columns))
etf.to_csv(os.path.join(out_dir, "etf_list.csv"), index=False, encoding="utf-8-sig")

# 2. A-share spot (this includes all stocks; use as list)
print("\n=== A-share list (sina) ===")
spot = ak.stock_zh_a_spot()
print(f"rows: {len(spot)}")
print("cols:", list(spot.columns))
spot.to_csv(os.path.join(out_dir, "ashare_list.csv"), index=False, encoding="utf-8-sig")

# 3. Open fund list
print("\n=== Open fund list (em) ===")
funds = ak.fund_name_em()
print(f"rows: {len(funds)}")
funds.to_csv(os.path.join(out_dir, "fund_list.csv"), index=False, encoding="utf-8-sig")

print("\nDONE. Files saved to", out_dir)
for f in os.listdir(out_dir):
    p = os.path.join(out_dir, f)
    print(f"  {f}  ({os.path.getsize(p)//1024} KB)")
