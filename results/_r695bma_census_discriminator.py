# r695 bm-a: census-code discriminator -- re-run census _cell_job for D-15|raw|base|time|h20
# Question: does TODAY's census code+panel give 1.1622 (= revcensus glue, panel/env drift)
#           or 1.1551 (= published anchor, glue-only divergence)?
import io, json, os, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import refine_bench_rev_census as RC

# 1) anchor row (published census value)
anchor = None
for k in range(RC.N_SHARDS):
    fp = os.path.join(RC.OUT_DIR, "shard-%dof%d.json" % (k, RC.N_SHARDS))
    d = json.load(io.open(fp, encoding="utf-8"))
    for r in d.get("rows", []):
        if r["name"] == "D-15|raw|base|time|h20":
            anchor = r
            print("== anchor row (shard-%dof6):" % k)
            print(json.dumps({kk: anchor.get(kk) for kk in
                              ("name", "sharpe_full", "ann_ret", "max_dd", "n_days",
                               "entries", "unfillable", "skips", "exits", "hit_rate")},
                             ensure_ascii=False, indent=1))
if anchor is None:
    print("ANCHOR NOT FOUND -- name mismatch, investigate")
    sys.exit(2)

# 2) locate the census cell dict
cell = None
for c in RC.census_cells():
    if c["name"] == "D-15|raw|base|time|h20":
        cell = c
        break
print("== census cell:", json.dumps(cell, ensure_ascii=False))

# 3) load panel in-process (census worker init verbatim) and run _cell_job twice
t0 = time.time()
RC._init_worker()
print("panel loaded %.1fs" % (time.time() - t0))
t0 = time.time()
row1 = RC._cell_job(cell)
print("census _cell_job run1 %.1fs" % (time.time() - t0))
t0 = time.time()
row2 = RC._cell_job(cell)
print("census _cell_job run2 %.1fs" % (time.time() - t0))

for kk in ("sharpe_full", "ann_ret", "max_dd", "n_days", "entries", "unfillable"):
    v1, v2, va = row1.get(kk), row2.get(kk), anchor.get(kk)
    mark = "SAME" if v1 == va else "**DIFF**"
    print("%-12s rerun1=%r rerun2=%r anchor=%r  %s" % (kk, v1, v2, va, mark))
print("skips rerun=%r anchor=%r" % (row1.get("skips"), anchor.get("skips")))
print("exits rerun=%r anchor=%r" % (row1.get("exits"), anchor.get("exits")))
print("determinism rerun1==rerun2:", row1 == row2)
print("PROBE_OK")
