"""Probe EM ban status + baostock data quality (qfq consistency, preclose, isST)."""
import time
import requests

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
try:
    r = requests.get("https://push2his.eastmoney.com/api/qt/stock/kline/get", params={
        "secid": "0.000001", "fields1": "f1,f2,f3",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f59",
        "klt": "101", "fqt": "1", "beg": "20150101", "end": "20261231", "lmt": "1000000"},
        headers=UA, timeout=10)
    d = r.json().get("data")
    print("EM probe:", r.status_code, "rows:", len(d["klines"]) if d else -1)
except Exception as e:
    print("EM probe: FAIL", type(e).__name__)

import baostock as bs
t0 = time.time()
lg = bs.login()
print("baostock login:", lg.error_code, lg.error_msg, f"({time.time()-t0:.1f}s)")

t0 = time.time()
rs = bs.query_history_k_data_plus(
    "sz.000001", "date,code,open,high,low,close,preclose,volume,amount,turn,tradestatus,pctChg,isST",
    start_date="2015-01-10", end_date="2015-01-25", frequency="d", adjustflag="2")  # 2=qfq
rows = []
while (rs.error_code == "0") and rs.next():
    rows.append(rs.get_row_data())
import pandas as pd
df = pd.DataFrame(rows, columns=rs.fields)
print(f"baostock query: {len(df)} rows ({time.time()-t0:.1f}s)")
print(df[["date", "close", "preclose", "pctChg", "tradestatus", "isST"]].to_string(index=False))

t0 = time.time()
rs = bs.query_history_k_data_plus(
    "sz.000001", "date,close,pctChg", start_date="2015-01-05", end_date="2026-09-18",
    frequency="d", adjustflag="2")
rows = []
while (rs.error_code == "0") and rs.next():
    rows.append(rs.get_row_data())
df = pd.DataFrame(rows, columns=rs.fields)
for c in ("close", "pctChg"):
    df[c] = pd.to_numeric(df[c], errors="coerce")
pc = df["pctChg"]
print(f"baostock full: {len(df)} rows ({time.time()-t0:.1f}s) pct min/max {pc.min():.1f}/{pc.max():.1f} "
      f"| |pct|>11 count: {(pc.abs() > 11).sum()}")
bs.logout()
