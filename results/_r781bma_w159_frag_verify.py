# -*- coding: utf-8 -*-
"""Post-edit needle-shape verify: where do the 'refuse the naive' faces
live in the (now-edited) n1 file, and what is the exact W160 freezer
fragment shape."""
import io
import re

n2 = io.open(r"scripts/perpetual_faces_n1.py", encoding="utf-8", newline="").read()
for m in re.finditer(r".{0,60}refuse the naive.{0,80}", n2):
    print(repr(m.group(0))[:210])
    print("---")
print("W160 freezer fragments:")
for m in re.finditer(r".{0,50}W160 A window; W160 freezer.{0,60}", n2):
    print(repr(m.group(0))[:190])
    print("---")
