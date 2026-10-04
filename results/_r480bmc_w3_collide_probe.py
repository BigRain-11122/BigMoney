"""r480 bm-c: diagnose w3-window param collisions for fam0 (selftest FAIL leg)."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import scripts.mass_trial_w1 as m

roster, _ = m.build_roster()
fam = roster[0]
print("fam0 =", fam["family"], "ranges:")
for nm, r in sorted(fam["ranges"].items()):
    print("  ", nm, r)

w1 = list(m.sample_draws(fam, m.N_DRAWS))
w2 = list(m.sample_draws(fam, 64, skip=m.W2_SKIP))
w3 = list(m.sample_draws(fam, 64, skip=m.W3_SKIP))

h1 = {m.param_hash(fam, p, a): (i, p, a) for i, p, a in w1}
h2 = {m.param_hash(fam, p, a): (i, p, a) for i, p, a in w2}
h3 = {m.param_hash(fam, p, a): (i, p, a) for i, p, a in w3}

c13 = set(h1) & set(h3)
c23 = set(h2) & set(h3)
print("w1 n_distinct =", len(h1), "(512 draws)")
print("w3 collides w1:", len(c13), "| w3 collides w2:", len(c23))
for h in list(c13)[:3]:
    i1, p1, a1 = h1[h]
    i3, p3, a3 = h3[h]
    print("  COLLIDE w1 draw", i1, "vs w3 draw", i3)
    print("    p1 =", p1)
    print("    p3 =", p3)
    print("    a1 =", a1, " a3 =", a3)
# also check: distinct param values per dim in w1 frame
import collections
dims = sorted(w1[0][1].keys())
for d in dims:
    vals = collections.Counter(p[1][d] for p in w1)
    print("dim", d, "distinct in w1 frame:", len(vals),
          "top:", vals.most_common(3))
