# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
t = open(r"research\PERPETUAL_N1_W212_PREREG.md", encoding="utf-8").read()
i = t.find("W136..W211")
phys = t[i-40:i+300]
mine = ("\u2014\u2014W136..W211 \u5148\u4f8b\u94fe\u62ab\u9732\u3010\u5404\u6ce2 K-lift \u5168\u5728 \u00b10.0003 \u5185\u00b7\u673a\u8bfb\u53ef\u590d\u6838\u00b7\u952e W211 \u5b9e\u6d4b K-lift **0.0002**\u00b7line_merged@K462,120 **1.1901**\u00b7line_pre_w211 1.1899\u00b7n_eff_held_equal 885,789\uff1bse_mu \u6536\u7a84\u94fe \u2026\u2192W209 0.000362\u2192W211 **0.000361**\u3011\u3002")
n = min(len(phys), len(mine))
for k in range(n):
    if phys[k] != mine[k]:
        print(f"first divergence at {k}: phys={phys[max(0,k-14):k+14]!r} vs mine={mine[max(0,k-14):k+14]!r}")
        break
else:
    print("common prefix OK", n)
