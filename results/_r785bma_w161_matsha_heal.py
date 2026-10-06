# -*- coding: utf-8 -*-
"""r785 bm-a W161 mat-header sha heal (surgical fragment-level replace, r783
_r783bma_w160_fzt_heal.py precedent): the @MATROW@ BACK entry carried a
typo'd sha 'ee44482a2' into the landed W161 mat header citation; the
machine-verified fact is W160 freeze = bm-a r783 freeze ee04482a2 (git log
verified). One needle, count==1, AST gate after."""
import ast
import io
import subprocess

N1 = r"scripts/perpetual_faces_n1.py"
# machine-verify the sha before healing (never transcribe)
out = subprocess.check_output(["git", "log", "--oneline", "-1", "ee04482a2"],
                             encoding="utf-8")
assert out.startswith("ee04482a2 round 783 bm-a W160 freeze"), out[:60]

src = io.open(N1, encoding="utf-8", newline="").read()
old = "bm-a r783 freeze ee44482a2"
new = "bm-a r783 freeze ee04482a2"
n = src.count(old)
assert n == 1, f"heal needle count={n} expect=1"
assert src.count(new) == 0, "correct sha already present (unexpected)"
src = src.replace(old, new)
io.open(N1, "w", encoding="utf-8", newline="").write(src)
ast.parse(io.open(N1, encoding="utf-8", newline="").read())
print("W161 mat-header sha heal landed (ee44482a2 -> ee04482a2), AST gate PASS")
