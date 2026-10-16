# -*- coding: utf-8 -*-
"""r1055 absorb heal-4: P5e-rcpt-downstream needle <- actual staged t."""
import io

ST = r"results\_r1055bmc_staged3_t.txt"
ED = r"results\_w254bmc_derive_editor.py"

t = io.open(ST, encoding="utf-8").read()
ed = io.open(ED, encoding="utf-8", newline="").read()

k0 = t.find("W255p face per this window's probe leg4")
k1 = t.find('equalities"', k0)
assert k0 > 0 and k1 > k0
actual = t[k0:k1 + len("equalities")]
print("actual needle len", len(actual))

i = ed.find('rep("W255p face per this window\'s probe leg4')
assert i > 0
k = i + len('rep("')
j = ed.find('equalities"', k)
assert j > k
j_end = j + len("equalities")
dead = ed[k:j_end]
ed2 = ed[:k] + actual + ed[j_end:]
io.open(ED, "w", encoding="utf-8", newline="").write(ed2)
with io.open(r"results\_r1055bmc_heal4_dead_needle.txt", "w", encoding="utf-8") as f:
    f.write(dead)
print("heal-4 done: dead needle %d chars -> actual %d chars" % (len(dead), len(actual)))
