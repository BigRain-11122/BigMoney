import json, os, csv
B = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
res = json.load(open(os.path.join(B, "results", "theme_judge_p2", "theme_judge_p2_results.json"), encoding="utf-8"))
o = []
loo = res["loo"]
rows = loo.get("rows", [])
n_folds = loo.get("n_folds")
sign_false = sum(1 for r in rows if not r.get("sign_match"))
o.append("LOO folds=%s rows=%d sign_match_false=%d stable=%d" % (n_folds, len(rows), sign_false, len(rows) - sign_false))
eps = list(csv.DictReader(open(os.path.join(B, "results", "theme_judge_p2", "episodes.csv"), encoding="utf-8")))
for st in ("TJ2-FULL", "TJ2-SOLO"):
    rs = [r for r in eps if r["stratum"] == st]
    sx1 = sum(float(r["sys_net_x1"]) for r in rs) / len(rs)
    sx2 = sum(float(r["sys_net_x2"]) for r in rs) / len(rs)
    bx1 = sum(float(r["bh_net_x1"]) for r in rs) / len(rs)
    o.append("POOLED %s: sys_x1=%.6f sys_x2=%.6f bh_x1=%.6f x2_drag_pp=%.2f" % (st, sx1, sx2, bx1, (sx1 - sx2) * 100))
# trades per ride means
tr = res["census"].get("trades_per_ride") or []
if tr:
    o.append("census trades_per_ide sample n=%d mean=%.2f" % (len(tr), sum(tr) / len(tr)))
# file tail bytes for needle
raw = open(os.path.join(B, "research", "THEME_JUDGE_P2.md"), "rb").read()
o.append("prereg_tail_bytes=%r" % raw[-260:])
open(os.path.join(B, "results", "_r678bma_p2_tail.txt"), "w", encoding="utf-8").write("\n".join(o))
print("\n".join(o))
