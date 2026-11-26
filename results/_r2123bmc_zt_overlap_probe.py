"""Round 2123 bm-c: why does the zt-pool overlap check refuse 2026-11-23?

The collector re-fetches the latest collected day and refuses to append when the
row set moved; it names no difference (by design: exit 3, local untouched). This
probe prints the difference so the ruling has evidence instead of a symptom.

Read-only: fetches one day and compares against the stored parquet, writes
nothing into data/.
"""
import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import update_zt_pool as uz  # noqa: E402

DAY = sys.argv[1] if len(sys.argv) > 1 else "2026-11-23"
KEY = sys.argv[2] if len(sys.argv) > 2 else "zt"
flat = DAY.replace("-", "")

import akshare as ak  # noqa: E402

fn_name, inv = uz.ENDPOINTS[KEY]
fn = getattr(ak, fn_name)

path = os.path.join(uz.PANEL_DIR, KEY + ".parquet")
old = pd.read_parquet(path)
old["日期"] = old["日期"].astype(str).str.replace("-", "", regex=False)
old_day = old[old["日期"] == flat].copy()
new_day, shape_ok = uz.fetch_day(fn, flat, inv)

print("day=%s key=%s stored=%d refetched=%d shape_ok=%s" % (DAY, KEY, len(old_day), len(new_day), shape_ok))
ocodes = set(old_day["代码"].astype(str))
ncodes = set(new_day["代码"].astype(str))
print("match=%s" % uz.day_rows_match(old_day, new_day))
print("codes only local :", sorted(ocodes - ncodes))
print("codes only source:", sorted(ncodes - ocodes))

shared = ocodes & ncodes
to = old_day.assign(c=old_day["代码"].astype(str)).set_index("c")
tn = new_day.assign(c=new_day["代码"].astype(str)).set_index("c")
diffs = 0
for code in sorted(shared):
    ov = sorted(float(x) for x in to.loc[[code], uz.NUM_COMPARE_COL])
    nv = sorted(float(x) for x in tn.loc[[code], uz.NUM_COMPARE_COL])
    if len(ov) != len(nv) or any(abs(a - b) > max(uz.TOL, abs(a) * 1e-9) for a, b in zip(ov, nv)):
        diffs += 1
        if diffs <= 10:
            print("   %s local=%s source=%s" % (code, ov, nv))
print("value-diff codes among %d shared: %d" % (len(shared), diffs))
print("superset_benign=%s" % (not (ocodes - ncodes) and diffs == 0))
