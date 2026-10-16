# -*- coding: utf-8 -*-
"""r1055 absorb: stage before P5e-rcpt-downstream, dump the actual projection text."""
import io

ED = r"results\_w254bmc_derive_editor.py"
OUT = r"results\_r1055bmc_editor_staged3.py"

t = io.open(ED, encoding="utf-8").read()
i = t.find('rep("W255p face per this window\'s probe leg4')
assert i > 0
staged = t[:i]
tail = '''

with io.open(r"results/_r1055bmc_staged3_t.txt", "w", encoding="utf-8", newline="") as f:
    f.write(t)
k = t.find("p face per this window's probe leg4")
print("anchor at", k)
print(t[k - 20:k + 1100])
print("STAGE3 OK")
'''
io.open(OUT, "w", encoding="utf-8", newline="").write(staged + tail)
print("staged3 written")
