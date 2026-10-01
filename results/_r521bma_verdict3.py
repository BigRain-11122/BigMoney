import csv
import json

r = json.load(open("results/refine_bench_stock/rev_p2/p2_results.json",
                   encoding="utf-8"))
sl = r["gates"]["D-15|raw|base|time|h20"]["g1_prime_v2"]["skill_line"]
print("mu_null=", sl.get("mu_null"), "sigma_null=", sl.get("sigma_null"),
      "null_term=", sl.get("null_term"), "passive_term=", sl.get("passive_term"))
print("passive_source=", sl.get("passive_source"), "| null_pool_source=",
      sl.get("null_pool_source"))
vs = r["virtual_starts"]
print("vstarts keys:", sorted(vs.keys()))
for k in sorted(vs.keys()):
    v = vs[k]
    if isinstance(v, dict) and "beat_rate" in json.dumps(v)[:2000]:
        print(k, ":", json.dumps(v, ensure_ascii=False)[:300])
# beat rates hunt per cell
for k in sorted(vs.keys()):
    v = vs[k]
    if isinstance(v, (int, float)):
        print("vstarts", k, "=", v)
print("--- cells summary csv ---")
with open("results/refine_bench_stock/rev_p2/cells_summary.csv",
          encoding="utf-8") as fh:
    for row in csv.reader(fh):
        print(" | ".join(x[:10] for x in row))
