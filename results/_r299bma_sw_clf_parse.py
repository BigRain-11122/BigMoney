"""R299 bm-a SW classification parse + coverage facts (queue #4, R99 probe).

Parses the official SW 2021 stock classification workbook
(data/basic/sw_stock_classify_2021.xls, fetched 2026-09-27 sha256 1111bceb...)
-> stock -> (industry_code, start_date) rows; builds the frozen mapping
asset data/basic/sw_l3_map.csv (latest classification per stock) and reports
coverage vs the 5222-stock P1C bars panel. FACTS ONLY (R99: zero runs).
"""
import json
import time

import pandas as pd

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
XLS = ROOT + r"\data\basic\sw_stock_classify_2021.xls"
OUT_CSV = ROOT + r"\data\basic\sw_l3_map.csv"
PROBE = ROOT + r"\results\cn_sector_leader_probe.json"

t0 = time.time()
df = pd.read_excel(XLS, dtype={"股票代码": "str", "行业代码": "str"})
df.columns = ["symbol", "start_date", "industry_code", "update_time"]
df["symbol"] = df["symbol"].astype(str).str.strip()
df["industry_code"] = df["industry_code"].astype(str).str.strip()
res = {"kind": "SW classification parse facts (R99 probe leg-1)", "ts": time.strftime("%Y-%m-%d %H:%M:%S")}
res["raw_rows"] = int(len(df))
res["n_stocks_raw"] = int(df["symbol"].nunique())
res["n_industry_codes_raw"] = int(df["industry_code"].nunique())
res["code_len_dist"] = df["industry_code"].str.len().value_counts().to_dict()
res["start_date_min"] = str(df["start_date"].min())
res["start_date_max"] = str(df["start_date"].max())
res["multi_class_stocks"] = int((df.groupby("symbol").size() > 1).sum())

# bars universe
import glob, os
syms = [os.path.basename(p)[:-8] for p in sorted(glob.glob(ROOT + r"\Money02\data\bars\*.parquet"))]
bars_set = set(syms)
res["bars_n"] = len(syms)

# latest classification per stock (by start_date; tie -> last row)
df = df.sort_values(["symbol", "start_date"])
latest = df.groupby("symbol", as_index=False).last()
latest_set = set(latest["symbol"])
res["coverage_bars_intersection"] = int(len(bars_set & latest_set))
res["coverage_pct_of_bars"] = round(100 * len(bars_set & latest_set) / len(bars_set), 1)
missing = bars_set - latest_set
res["unmapped_examples"] = sorted(missing)[:10]

# industry code structure: SW 2021 L3 codes are 6-digit (e.g. 110000-style? check)
res["industry_code_examples"] = latest["industry_code"].head(10).tolist()
res["elapsed_sec"] = round(time.time() - t0, 1)
json.dump(res, open(PROBE, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print(json.dumps(res, ensure_ascii=False, indent=1, default=str))
