import json, os, time
RB = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results"
FAMILIES = ["fund_value_p1", "fund_quality_p1", "fund_divlowvol_p1"]
out = {"probe": "r452bmc fund NULLS watch (bm-b canonical burn, read-only)",
       "probe_time": time.strftime("%Y-%m-%dT%H:%M:%S+08:00")}
rows = {}
for fam in FAMILIES:
    d = os.path.join(RB, fam)
    rec = {}
    for name in sorted(os.listdir(d)):
        p = os.path.join(d, name)
        if not os.path.isfile(p):
            continue
        if name.endswith(".jsonl"):
            with open(p, encoding="utf-8") as fh:
                n = sum(1 for _ in fh)
            rec[name] = {"rows": n, "mtime": time.strftime("%m-%d %H:%M", time.localtime(os.path.getmtime(p)))}
    # expected cells: 401 x2 per family x3 (judged) + sens 500 x3 per r650/bm-b r654
    cells_total = sum(v["rows"] for k, v in rec.items() if k.startswith("cells_"))
    rec["cells_total"] = cells_total
    rows[fam] = rec
out["families"] = rows
out["expected"] = {"cells_per_family": 802, "sens_per_family": 500, "nulls_cap": 2000}
p = os.path.join(RB, "_r452bmc_fundnulls_watch.json")
with open(p, "w", encoding="utf-8", newline="") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False))
