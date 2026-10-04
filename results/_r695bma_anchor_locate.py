# r695 bm-a: locate failing cell anchor row + shard file git history after original delivery
import json, io, os

CELL = "RC-D-15-raw-base-time-h20"
for k in range(6):
    fp = r"results\refine_bench_stock\rev_census\shard-%dof6.json" % k
    d = json.load(io.open(fp, encoding="utf-8"))
    for r in d.get("rows", []):
        if r["name"] == CELL:
            print("== anchor row found in shard-%dof6:" % k)
            print(json.dumps({kk: r[kk] for kk in ("name", "sharpe_full", "ann_ret",
                                                   "max_dd", "n_days", "entries",
                                                   "unfillable", "skips", "exits")
                              if kk in r}, ensure_ascii=False, indent=1))
    # also print shard meta
    meta = {kk: d[kk] for kk in d if kk != "rows"}
    if k in (0, 1):
        print("== shard-%dof6 meta:" % k, json.dumps(meta, ensure_ascii=False)[:600])

# row counts per shard
for k in range(6):
    fp = r"results\refine_bench_stock\rev_census\shard-%dof6.json" % k
    d = json.load(io.open(fp, encoding="utf-8"))
    print("shard-%dof6 rows=%d names_sample=%s" % (k, len(d.get("rows", [])),
          [r["name"] for r in d.get("rows", [])[:2]]))
print('PROBE_OK')
