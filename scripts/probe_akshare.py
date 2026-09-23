"""Probe available akshare endpoints from local Windows."""
import akshare as ak
import sys

print("akshare version:", ak.__version__)

# 1. ETF list from sina
print("\n--- ETF list (sina) ---")
try:
    df = ak.fund_etf_category_sina(symbol="ETF基金")
    print(f"  rows: {len(df)}")
    print(df.head(3).to_string())
    print("  columns:", list(df.columns))
except Exception as e:
    print(f"  FAIL: {e}")

# 2. A-share stock list
print("\n--- A-share spot (sina) ---")
try:
    df = ak.stock_zh_a_spot()
    print(f"  rows: {len(df)}")
    print(df.head(2).to_string())
except Exception as e:
    print(f"  FAIL: {e}")

# 3. Fund list
print("\n--- Open fund list ---")
try:
    df = ak.fund_name_em()
    print(f"  rows: {len(df)}")
    print(df.head(2).to_string())
except Exception as e:
    print(f"  FAIL: {e}")
