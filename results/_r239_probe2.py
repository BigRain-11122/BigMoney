# -*- coding: utf-8 -*-
"""R239 probe-2: LHB schema via pyarrow (no hardcoded CJK in shell) + daily panel asof census."""
import glob
import json
import os

import pyarrow.parquet as pq

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = {}

# LHB schema (field names via pyarrow, unicode-safe)
p = os.path.join(ROOT, "Money02", "data", "lhb", "lhb_detail.parquet")
sch = pq.read_schema(p)
names = [f.name for f in sch]
types = [str(f.type) for f in sch]
out["lhb_schema"] = {n: t for n, t in zip(names, types)}

# daily panel asof census: which files are fresh (2026-09-24) vs stale
import pandas as pd

census = {}
for f in glob.glob(os.path.join(ROOT, "data", "daily", "*.csv")):
    sym = os.path.splitext(os.path.basename(f))[0]
    try:
        last = pd.read_csv(f, usecols=[0]).iloc[-1, 0]
    except Exception:
        last = "ERR"
    census[sym] = str(last)
from collections import Counter

out["daily_asof_census"] = dict(Counter(census.values()))
out["n_daily_files"] = len(census)
out["stale_examples"] = {k: v for k, v in census.items() if v != "2026-09-24"}

with open(os.path.join(ROOT, "results", "_r239_probe2.json"), "w", encoding="utf-8", newline="\n") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1, default=str)
print("ok")
