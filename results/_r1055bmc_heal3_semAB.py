# -*- coding: utf-8 -*-
"""r1055 absorb heal-3: P5e-rcpt-semantics-A/B needles <- actual staged t
(the dead window authored them from the W253-editor needle face instead of the
post-blanket source face; dsts are correct and untouched, disclosed)."""
import io

ST = r"results\_r1055bmc_staged2_t.txt"
ED = r"results\_w254bmc_derive_editor.py"

t = io.open(ST, encoding="utf-8").read()
ed = io.open(ED, encoding="utf-8", newline="").read()

# extract actual A/B band_semantics values from staged t
a0 = t.find('"A": "1-HOP')
a1 = t.find('EXACT)"', a0) + len('EXACT)"')
actual_A = t[a0:a1]
b0 = t.find('"B": "1-HOP')
b1 = t.find('EXACT)"', b0) + len('EXACT)"')
actual_B = t[b0:b1]
assert actual_A.count('"') >= 4 and actual_B.count('"') >= 4
print("actual A len", len(actual_A), "| actual B len", len(actual_B))


def patch_rep_needle(ed, head_marker, actual):
    i = ed.find(head_marker)
    assert i > 0, "rep head not found: %s" % head_marker[:60]
    # needle literal starts right after "rep('"
    k = i + len("rep('")
    j = ed.find("'", k)  # needle contains no single quotes
    assert j > k, "closing quote not found"
    dead = ed[k:j]
    ed2 = ed[:k] + actual + ed[j:]
    print("patched needle (%d -> %d chars) at head %s..." % (len(dead), len(actual), head_marker[5:40]))
    return ed2, dead


ed, deadA = patch_rep_needle(ed, "rep('\"A\": \"1-HOP STAIRCASE-AFFECTS-A walk (hops=1,", actual_A)
ed, deadB = patch_rep_needle(ed, "rep('\"B\": \"1-HOP own-A RESERVATION CASCADE above own-A (hops=1,", actual_B)

io.open(ED, "w", encoding="utf-8", newline="").write(ed)
# keep dead needles as evidence
with io.open(r"results\_r1055bmc_heal3_dead_needles.txt", "w", encoding="utf-8") as f:
    f.write("=== dead A needle ===\n" + deadA + "\n=== dead B needle ===\n" + deadB + "\n")
print("heal-3 done")
