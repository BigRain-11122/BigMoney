"""R299 bm-a SW classification hierarchy facts (queue #4, R99 probe leg-2)."""
import glob
import json
import os
import time

import pandas as pd

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
XLS = ROOT + r"\data\basic\sw_stock_classify_2021.xls"
res = {"kind": "SW classification hierarchy facts (R99 probe leg-2)",
       "ts": time.strftime("%Y-%m-%d %H:%M:%S")}

df = pd.read_excel(XLS, dtype={"股票代码": "str", "行业代码": "str"})
df.columns = ["symbol", "start_date", "industry_code", "update_time"]
df["symbol"] = df["symbol"].str.strip()
df["industry_code"] = df["industry_code"].str.strip()

syms = {os.path.basename(p)[:-8] for p in glob.glob(ROOT + r"\Money02\data\bars\*.parquet")}
df = df[df["symbol"].isin(syms)].sort_values(["symbol", "start_date"])
latest = df.groupby("symbol", as_index=False).last()

res["l1_n"] = int(latest["industry_code"].str[:2].nunique())
res["l2_n"] = int(latest["industry_code"].str[:4].nunique())
res["l3_n"] = int(latest["industry_code"].nunique())
for lv, key in (("l1", lambda s: s.str[:2]), ("l2", lambda s: s.str[:4]), ("l3", lambda s: s)):
    sizes = latest.assign(g=key(latest["industry_code"])).groupby("g").size()
    res[f"{lv}_size_stats"] = {"n": int(len(sizes)), "min": int(sizes.min()),
                                "median": float(sizes.median()), "max": int(sizes.max()),
                                "n_ge5": int((sizes >= 5).sum()),
                                "n_ge10": int((sizes >= 10).sum())}

# per-stock classification-change burden over history (point-in-time viability)
chg = df.groupby("symbol").size()
res["rows_per_stock"] = {"1": int((chg == 1).sum()), "2": int((chg == 2).sum()),
                          "3+": int((chg >= 3).sum())}
# changes inside the evidence window (1990->cutoff): start_date > 1991 = reclass events
recl = df[pd.to_datetime(df["start_date"]) > pd.Timestamp("1991-01-01")]
res["reclass_rows_after_1991"] = int(len(recl))
res["reclass_by_year_top"] = recl["start_date"].dt.year.value_counts().head(8).to_dict()
print(json.dumps(res, ensure_ascii=False, indent=1, default=str))
json.dump(res, open(ROOT + r"\results\_r299bma_sw_hierarchy.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1, default=str)
