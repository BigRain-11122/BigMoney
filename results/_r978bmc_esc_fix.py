# -*- coding: utf-8 -*-
# r978 surgical fix: _r977bmc_r35gen.py line 105 truncated escape \uu679a -> \u679a (r958 transcription family, 5th instance)
p = r"results\_r977bmc_r35gen.py"
src = open(p, encoding="utf-8").read()
BAD = "\\uu679a"  # literal backslash + "uu679a"
GOOD = "\\u679a"
n = src.count(BAD)
assert n == 1, "bad count %d" % n
src = src.replace(BAD, GOOD)
open(p, "w", encoding="utf-8", newline="").write(src)
# verify: compiles now
import ast
ast.parse(src)
print("FIXED + ast.parse OK, bad residue:", src.count(BAD))
