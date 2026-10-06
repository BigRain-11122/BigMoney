# -*- coding: utf-8 -*-
"""r794 bm-a: extract the W164 prereg's chain/stat prose sites (frozen at
f7d34e5a7) to adjudicate the W165 prereg_build surgical targets, plus live
W164 finalize facts from the results JSON."""
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

raw = subprocess.run(
    ["git", "show", "f7d34e5a7:research/PERPETUAL_N1_W164_PREREG.md"],
    capture_output=True).stdout
txt = raw.decode("utf-8")
print("frozen W164 prereg bytes:", len(raw))

# se_mu chain prose sites
for m in re.finditer(r"[^\n]{0,30}0\.00041[0-9][^\n]{0,60}", txt):
    print("SEC:", m.group(0))
print("---")
# K-lift / skill line sites
for m in re.finditer(r"[^\n]{0,40}1\.18[0-9]{2}[^\n]{0,50}", txt):
    print("KLC:", m.group(0))
print("---")
# sigma sites
for m in re.finditer(r"[^\n]{0,40}0\.245[0-9]{0,12}[^\n]{0,40}", txt):
    print("SIG:", m.group(0))
print("---")
# own-mu / merged-mu sites
for m in re.finditer(r"[^\n]{0,30}0\.0(88982|929|5633|6533)[^\n]{0,50}", txt):
    print("MU:", m.group(0))
print("---")
# A p95 sites
for m in re.finditer(r"[^\n]{0,40}0\.3[0-9]{3}[^\n]{0,40}", txt):
    print("P95:", m.group(0))

print("=== live W164 finalize facts ===")
w = json.load(open("results/perpetual_faces/n1_w164_results.json", encoding="utf-8"))
m2 = w["null_pool_cumulative"]["merged"]
own = w["null_pool_cumulative"]["w164_only"]
led = w["science_gates"]["ledger"]
sk = w["skill_line_v2_k_lift"]
print("merged n_values:", m2["n_values"], "mu:", m2["mu"], "sigma:", m2["sigma"])
print("w164_only mu:", own["mu"], "sigma:", own["sigma"])
print("ledger total:", led["total"], "prev:", led["prev_total"])
print("A_random_engine_exit full_sharpe_p95:",
      w["families"]["A_random_engine_exit"]["full_sharpe_p95"])
print("skill line_merged:", sk.get("line_merged_358720"), "line_pre_w164:",
      sk.get("line_pre_w164"), "delta:", sk.get("line_delta_k_lift"))
print("se_mu_at_k358720:", w["null_pool_cumulative"].get("se_mu_at_k358720"))
print("n_eff_held_equal:", sk.get("n_eff_held_equal"))
