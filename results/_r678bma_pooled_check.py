import json, os
import numpy as np
B = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
res = json.load(open(os.path.join(B, "results", "theme_judge_p2", "theme_judge_p2_results.json"), encoding="utf-8"))
o = []
cells = res["cells"]
for f in ("TJ2-FULL-x1", "TJ2-SOLO-x1"):
    c = cells[f]
    r = np.asarray(c["returns"], dtype=float)
    comp = float(np.prod(1 + r) - 1)
    o.append("%s: n_days=%d compounded_net=%.6f sharpe=%.4f keys=%s" % (f, len(r), comp, c["sharpe_full"], ",".join(list(c.keys())[:14])))
loo = res["loo"]
o.append("LOO full_sys_net=%.6f full_bh_net=%.6f" % (loo["full_sys_net"], loo["full_bh_net"]))
# P1 comparison
p1 = json.load(open(os.path.join(B, "results", "theme_judge_p1", "theme_judge_p1_results.json"), encoding="utf-8"))
for f in ("TJ-FULL-x1", "TJ-SOLO-x1"):
    c = p1["cells"][f]
    r = np.asarray(c["returns"], dtype=float)
    comp = float(np.prod(1 + r) - 1)
    o.append("P1 %s: n_days=%d compounded_net=%.6f" % (f, len(r), comp))
o.append("P1 LOO full_sys_net=%.6f" % p1["loo"]["full_sys_net"])
# P1 sens bl0.80/1.25 SOLO reading
p1s = p1.get("sensitivity") or p1["cells"].get("sensitivity")
o.append("P1 sens type=%s" % type(p1s).__name__)
if isinstance(p1s, list):
    for it in p1s:
        o.append("P1 SENS %s" % json.dumps(it, ensure_ascii=False)[:200])
elif isinstance(p1s, dict):
    for k, v in p1s.items():
        o.append("P1 SENS %s: %s" % (k, json.dumps(v, ensure_ascii=False)[:200]))
open(os.path.join(B, "results", "_r678bma_pooled_check.txt"), "w", encoding="utf-8").write("\n".join(o))
print("\n".join(o))
