import json, os, csv
B = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
res = json.load(open(os.path.join(B, "results", "theme_judge_p2", "theme_judge_p2_results.json"), encoding="utf-8"))
o = []
sens = res.get("sensitivity")
o.append("sens_type=%s" % type(sens).__name__)
if isinstance(sens, dict):
    for k, v in list(sens.items())[:50]:
        o.append("  SENS %s: %s" % (k, json.dumps(v, ensure_ascii=False)[:260]))
elif isinstance(sens, list):
    for it in sens[:30]:
        o.append("  SENS item: %s" % json.dumps(it, ensure_ascii=False)[:260])
# episodes per-stratum and per-year
rows = list(csv.DictReader(open(os.path.join(B, "results", "theme_judge_p2", "episodes.csv"), encoding="utf-8")))
strata = {}
years = {}
for r in rows:
    st = r["stratum"]
    try:
        e_ = (float(r["sys_net_x1"]) - float(r["bh_net_x1"])) * 100
    except Exception:
        continue
    strata.setdefault(st, []).append(e_)
    years.setdefault((st, r["ignition_date"][:4]), []).append(e_)
for st, v in sorted(strata.items()):
    v2 = sorted(v)
    n = len(v2)
    o.append("STRATUM %s: n=%d best=%.1f%% worst=%.1f%% p25=%.1f%% med=%.1f%% p75=%.1f%% edge_mean=%.2fpp pos=%.1f%%" % (
        st, n, max(v2), min(v2), v2[n//4], v2[n//2], v2[3*n//4], sum(v2)/n, 100*sum(1 for x in v2 if x>0)/n))
for (st, y), v in sorted(years.items()):
    o.append("YR %s %s: n=%d mean=%.2fpp" % (st, y, len(v), sum(v)/len(v)))
# per-stratum neg-year count
for st in sorted(strata):
    neg = [y for (s2, y) in years if s2 == st and sum(years[(s2, y)]) < 0]
    pos = [y for (s2, y) in years if s2 == st and sum(years[(s2, y)]) >= 0]
    o.append("NEG_YEARS %s (%d): %s" % (st, len(neg), ",".join(neg)))
    o.append("POS_YEARS %s (%d): %s" % (st, len(pos), ",".join(pos)))
# prereg section 5 (predictions)
src = open(os.path.join(B, "research", "THEME_JUDGE_P2.md"), encoding="utf-8").read()
ps = [i for i in range(len(src)) if src.startswith("## ", i)]
sec5 = src[ps[-4]:ps[-3]] if len(ps) >= 4 else ""
o.append("=== PREREG SEC5 ===")
o.append(sec5)
open(os.path.join(B, "results", "_r678bma_p2_sec5.txt"), "w", encoding="utf-8").write("\n".join(o))
print("WROTE")
