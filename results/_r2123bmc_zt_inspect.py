"""Inspect a zt-pool parquet: row count, columns as stored, day tail, dtype mix."""
import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(ROOT, "data", "zt_pool", sys.argv[1] if len(sys.argv) > 1 else "zt.parquet")
df = pd.read_parquet(path)
print("rows:", len(df))
print("cols:", [c.encode("unicode_escape").decode("ascii") for c in df.columns])
day_col = df.columns[0]
print("day_col_escape:", day_col.encode("unicode_escape").decode("ascii"))
vals = df[day_col]
print("day_dtype:", vals.dtype, "sample:", [str(v) for v in vals.head(2)])
days = vals.astype(str)
uniq = sorted(days.unique())
print("unique_days:", len(uniq), "first:", uniq[0], "last:", uniq[-1])
print("tail:", uniq[-6:])
target = sys.argv[2] if len(sys.argv) > 2 else "20261123"
print("rows_on_%s:" % target, int((days.str.replace("-", "", regex=False) == target).sum()))
