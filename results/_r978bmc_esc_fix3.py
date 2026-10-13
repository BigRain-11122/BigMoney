# -*- coding: utf-8 -*-
# r978 surgical fix 3: KL needle byte-face alignment.
# Ground truth (hex-verified): R34 stores minus sign as LITERAL escape text "\u2212"
# (7 ASCII chars 5c 75 32 32 31 32), middle dot as real UTF-8 char (c2 b7).
# r35gen L1 placeholder row targets a text that does not exist in R34 (dead row) -> delete.
# r35gen L3 needle parses \u2212 into a real U+2212 char -> mismatch; write \\u2212 so the
# runtime needle carries the literal escape text, byte-aligned with R34.
p = r"results\_r977bmc_r35gen.py"
src = open(p, encoding="utf-8", newline="").read()

# (1) delete dead L1 placeholder row (KEEP37 occurrences asserted ==1 upstream)
L1 = 'rep("\\u952e W233 \\u5b9e\\u6d4b K-lift **\\u2212 0.0002**", "KEEP37KLPLACEHOLDER")\r\n'
assert src.count(L1) == 1, "L1 row count %d" % src.count(L1)
src = src.replace(L1, "")
assert "KEEP37KLPLACEHOLDER" not in src, "placeholder residue"

# (2) L3 needle: literal-escape the minus sign (source \\u2212 -> runtime literal \u2212 text)
L3_OLD = 'K-lift **\\u22120.0002**\\u00b7line_merged@K510,520 **1.1922**\\u00b7line_pre_w234 1.1924\\u00b7n_eff_held_equal 934,189'
L3_NEW = 'K-lift **\\\\u22120.0002**\\u00b7line_merged@K510,520 **1.1922**\\u00b7line_pre_w234 1.1924\\u00b7n_eff_held_equal 934,189'
assert src.count(L3_OLD) == 1, "L3 needle count %d" % src.count(L3_OLD)
src = src.replace(L3_OLD, L3_NEW)

import ast
ast.parse(src)
open(p, "w", encoding="utf-8", newline="").write(src)

# (3) simulate: L2-advanced R34 text must contain the L3 runtime needle exactly once
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
needle = "\u952e W234 \u5b9e\u6d4b K-lift **\\u22120.0002**\u00b7line_merged@K510,520 **1.1922**\u00b7line_pre_w234 1.1924\u00b7n_eff_held_equal 934,189"
print("FIX3 OK; L3 needle after-sim count:", sim.count(needle))
assert sim.count(needle) == 1
