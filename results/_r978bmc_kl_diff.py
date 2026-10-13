# -*- coding: utf-8 -*-
# r978 KL sim diff probe: reconstruct L2-advanced R34 KL segment and the runtime
# L3 needle, print both in hex to find the last byte mismatch.
import sys
sys.stdout.reconfigure(encoding="utf-8")

t = open(r"results\_w234bmc_r34_data.py", encoding="utf-8").read()
sim = (t.replace("PERPETUAL-N1-W234", "PERPETUAL-N1-W235")
        .replace("PERPETUAL_N1_W234", "PERPETUAL_N1_W235")
        .replace("n1_w234", "n1_w235")
        .replace("_w234bmc", "_w235bmc")
        .replace("W234", "@SELF@")
        .replace("line_pre_w233", "line_pre_w@WPRE@")
        .replace("n1_w233", "n1_w234")
        .replace("W233", "W234")
        .replace("@WPRE@", "w234")
        .replace("@SELF@", "W235"))

i = sim.find("K-lift")
seg = sim[i-14:i+112]
needle = "\u952e W234 \u5b9e\u6d4b K-lift **\\u22120.0002**\u00b7line_merged@K510,520 **1.1922**\u00b7line_pre_w234 1.1924\u00b7n_eff_held_equal 934,189"

print("SIM  :", repr(seg))
print("NEEDL:", repr(needle))
print("in-sim count:", sim.count(needle))
# byte-level walk: find first divergence between seg and needle
a, b = seg, needle
for k in range(min(len(a), len(b))):
    if a[k] != b[k]:
        print("first diff at", k)
        print("  sim  byte:", hex(ord(a[k])) if ord(a[k]) < 128 else a[k].encode("utf-8").hex(), repr(a[k-6:k+8]))
        print("  needl byte:", hex(ord(b[k])) if ord(b[k]) < 128 else b[k].encode("utf-8").hex(), repr(b[k-6:k+8]))
        break
else:
    print("no diff in common prefix; lens", len(a), len(b))
