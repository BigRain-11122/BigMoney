# -*- coding: utf-8 -*-
p = "results/_r794bma_w165_prereg_build.py"
src = open(p, encoding="utf-8", newline="").read()
old = '("engine_owner \u884c 154+\u672c\u5019\u9009=bm-a \u7b2c\u516b\u5341\u679a\u81ea\u6709\u6ce2\u3010r792\u3011", "@ORDT@")'
new = '("engine_owner \u884c 153+\u672c\u5019\u9009=bm-a \u7b2c\u516b\u5341\u679a\u81ea\u6709\u6ce2\u3010r792\u3011", "@ORDT@")'
n = src.count(old)
print("count", n)
assert n == 1, "ORDT TOK old-string not found or not unique"
open(p, "w", encoding="utf-8", newline="").write(src.replace(old, new))
print("fixed: ORDT TOK 154 -> 153 (frozen L1 face; BACK 154 stays)")
