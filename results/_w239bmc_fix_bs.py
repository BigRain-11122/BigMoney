# -*- coding: utf-8 -*-
# one-shot: normalize 8-backslash faces to 4 in the W239 derive editor tail span
p = r"results\_w239bmc_derive_editor.py"
s = open(p, "rb").read().decode("utf-8")
bad = ", " + "\\" * 8 + '",'
good = ", " + "\\" * 4 + '",'
n = s.count(bad)
s2 = s.replace(bad, good)
open(p, "wb").write(s2.encode("utf-8"))
print("replaced", n, "occurrences of 8-backslash -> 4")
import py_compile
py_compile.compile(p, doraise=True)
print("derive editor py_compile green")
