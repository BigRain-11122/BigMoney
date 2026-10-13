# r959 (bm-c): W228 splice estate verification part 2
# - WAVE_CONFIGS row census (227/228 shape)
# - locate n1 ledger face
# - inspect W227 finalize product shape (template for W228 finalize verification)
import re
import json
import os
import sys

BASE = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
src = open(BASE + r"\scripts\perpetual_faces.py", encoding="utf-8").read()
pat_227 = len(re.findall(r"227: \{\"a\"", src))
pat_228 = len(re.findall(r"228: \{\"a\"", src))
print("WAVE row 227:", pat_227, "| WAVE row 228:", pat_228)
fails = []
if pat_227 != 1 or pat_228 != 1:
    fails.append("WAVE_CONFIGS row census fail (227=%d 228=%d)" % (pat_227, pat_228))

src_n1 = open(BASE + r"\scripts\perpetual_faces_n1.py", encoding="utf-8").read()
print("n1 WAVE row 227:", len(re.findall(r"227: \{\"a\"", src_n1)))
print("n1 WAVE row 228:", len(re.findall(r"228: \{\"a\"", src_n1)))

d = BASE + r"\results\perpetual_faces"
files = sorted(os.listdir(d))
print("perpetual_faces dir tail:", files[-10:])

r = json.load(open(d + r"\n1_w227_results.json", encoding="utf-8"))
print("n1_w227_results keys:", sorted(r.keys()))
for k in ["ledger_total", "ledger_identity", "merged_n", "merged_k", "wave", "mu", "sigma", "skill_line_v2", "se_mu"]:
    if k in r:
        print("W227", k, "=", str(r[k])[:220])

if fails:
    print("VERIFY2-FAIL")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("VERIFY2-PASS")
