# r358 bm-c W63 S5 four-gate machine-proof vs W63 prereg sec.5 anchors.
# Law: S5 is the session-side verdict face (finalize stdout + product JSON vs
# frozen prereg anchors); four gates per r343/r351 precedent:
#   (1) merged mu drift < 0.02  (2) sigma rel drift < +-10%
#   (3) A p95 delta < 0.05      (4) K-lift <= 0.02
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

res = json.load(open(ROOT + r"\results\perpetual_faces\n1_w63_results.json", "rb"))
print("RESULT-TOP-KEYS:", sorted(res.keys()))
p95 = None
for k in ("a_p95", "p95_a", "a_abs_p95", "abs_p95", "p95"):
    if k in res:
        p95 = res[k]
        print("A_P95 key=%s value=%s" % (k, p95))
        break
if p95 is None:
    # nested search (one level)
    for k, v in res.items():
        if isinstance(v, dict):
            for k2, v2 in v.items():
                if "p95" in str(k2).lower():
                    p95 = v2
                    print("A_P95 nested %s.%s = %s" % (k, k2, v2))
                    break
        if p95 is not None:
            break

pr = open(ROOT + r"\research\PERPETUAL_N1_W63_PREREG.md", "rb").read().decode("utf-8", "replace")
m5 = re.search(r"##\s*§?5[^\n]*\n(.*?)(?=\n##|\Z)", pr, re.S)
print("--- PREREG SEC.5 excerpt ---")
print(m5.group(1)[:1500] if m5 else "SEC5-NOT-FOUND")

# finalize stdout values (this window, single-pass r538 law)
merged_mu, merged_sigma = -0.0926, 0.2448
klift = -0.0005
anchor_mu, anchor_sigma, anchor_p95 = -0.092547, 0.239601, 0.3037
g1 = abs(merged_mu - anchor_mu) < 0.02
g2 = abs(merged_sigma - anchor_sigma) / anchor_sigma < 0.10
g3 = (p95 is not None and abs(float(p95) - anchor_p95) < 0.05)
g4 = klift <= 0.02
print("G1 mu |%s-%s|=%s <0.02 -> %s" % (merged_mu, anchor_mu, round(abs(merged_mu - anchor_mu), 6), g1))
print("G2 sigma |%s-%s|/%s=%s%% <10%% -> %s" % (merged_sigma, anchor_sigma, anchor_sigma, round(100 * abs(merged_sigma - anchor_sigma) / anchor_sigma, 2), g2))
print("G3 p95 %s vs %s -> %s" % (p95, anchor_p95, g3))
print("G4 K-lift %s <=0.02 -> %s" % (klift, g4))
print("S5_VERDICT=%s" % ("PASS" if (g1 and g2 and g3 and g4) else "FAIL"))
