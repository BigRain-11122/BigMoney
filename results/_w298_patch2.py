# -*- coding: utf-8 -*-
# bm-c r1181 window, patch 2: repair the inherited +1 drift on PRIOR/NEXT wave prose labels
# inside results/_w298bmc_freeze_edits.py (r1170/r1180 family: annotation faces silently
# inherit the template's stale wave number). Facts:
#   - the band that REFUSES the naive A window belongs to the PRIOR wave (W297) -> W297
#   - 'upstream <W> ALL LANDED / complete incl finalize' names the last finalize -> W297
#   - 'downstream <W> seat' / '<W> freezer MUST re-derive' name the NEXT freezer -> W299
import io

P = 'results/_w298bmc_freeze_edits.py'
t = io.open(P, encoding='utf-8', newline='').read()
RULES = [
    ("registered W298 B band", "registered W297 B band", 4),
    ("W298 B tail", "W297 B tail", 2),
    ("upstream W298 ALL LANDED", "upstream W297 ALL LANDED", 1),
    ("upstream W298 complete incl finalize", "upstream W297 complete incl finalize", 1),
    ("downstream W298 seat NOT YET PUBLISHED", "downstream W299 seat NOT YET PUBLISHED", 1),
    ("W298 freezer MUST", "W299 freezer MUST", 3),
]
for old, new, n in RULES:
    c = t.count(old)
    assert c == n, "drift-repair count %d != %d: %r" % (c, n, old)
    t = t.replace(old, new)
assert t.count("registered W298 B band") == 0
assert t.count("upstream W298") == 1, "only the own-row assert message may keep W298: %d" % t.count("upstream W298")
assert t.count("downstream W299") == 1
assert t.count("W299 freezer MUST") == 3
io.open(P, 'w', encoding='utf-8', newline='').write(t)
print("drift repairs applied:", len(RULES))