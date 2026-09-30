# -*- coding: utf-8 -*-
# r494bma: probe adjusted_view 19-member panel end dates + common history (LOWAMP-P1 data face).
import glob, os, sys

import pandas as pd

out = []
files = sorted(glob.glob("data/consolidation/adjusted_view/*.parquet"))
ends = {}
starts = {}
for f in files:
    df = pd.read_parquet(f)
    sym = os.path.basename(f).replace(".parquet", "")
    dates = pd.to_datetime(df["date"] if "date" in df.columns else df.index)
    starts[sym] = str(dates.min().date())
    ends[sym] = str(dates.max().date())
common_start = max(starts.values())
common_end = min(ends.values())
out.append(f"members: {len(files)}")
out.append(f"per-member start range: {min(starts.values())} .. {max(starts.values())}")
out.append(f"per-member end range: {min(ends.values())} .. {max(ends.values())}")
out.append(f"common window: {common_start} .. {common_end}")
late = [s for s, e in ends.items() if e < max(ends.values())]
out.append(f"members ending before panel max: {late}")
out.append("cols sample: " + str(list(pd.read_parquet(files[0]).columns)))
sys.stdout.buffer.write("\n".join(out).encode("utf-8"))
