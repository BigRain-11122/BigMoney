# -*- coding: utf-8 -*-
"""r1055 absorb: diff P5e-rcpt-semantics-A needle vs staged2 t, char-exact."""
import io

ST = r"results\_r1055bmc_staged2_t.txt"
ED = r"results\_w254bmc_derive_editor.py"

t = io.open(ST, encoding="utf-8").read()
ed = io.open(ED, encoding="utf-8").read()

i1 = ed.find('"P5e-rcpt-semantics-A")')
i0 = ed.rfind("rep(", 0, i1)
region = ed[i0:i1 + len('"P5e-rcpt-semantics-A")')]
# needle = first arg of the rep call (between the opening quote and "', \n'")
# extract old string literal: region starts with rep(' ... find the string end "', \n
# simpler: find the two top-level string literals via the known markers
old_a = '"A": "1-HOP STAIRCASE-AFFECTS-A walk (hops=1, A_hop_chain verbatim in the probe receipt; the naive continuation 571_701..573_700 refused at start -- the registered W253 B band 571_701..571_900 sits INSIDE the naive A window (staircase re-emergence continues to affect A; the W253 prereg sec.5 item5 A-CLEAN projection superseded live r587, divergence disclosed); the walk hops past the W253 B tail 571_900 -> A first-clean 571_901..573_900 -- SECOND consecutive A-hop of the staircase era, the fourteen-wave seed-gap face ENDED at W253; A_clean_at_naive_start=false; A_staircase_hop_past_W253_B=true; A base == registered prior-wave B tail+1 (571_900+1) EXACT)"'

print("needle count in staged2 t:", t.count(old_a))
j = t.find('"A": "1-HOP STAIRCASE-AFFECTS-A walk (hops=1, A_hop_chain verbatim in the probe receipt; the naive continuation 57')
print("=== staged2 region ===")
print(t[j:j + len(old_a) + 40])
print("=== needle ===")
print(old_a)
# common prefix
lo, hi = 0, min(len(old_a), len(t) - j)
while lo < hi:
    mid = (lo + hi + 1) // 2
    if t[j:j + mid] == old_a[:mid]:
        lo = mid
    else:
        hi = mid - 1
print("=== common prefix:", lo)
print("needle continues:", repr(old_a[lo:lo + 200]))
print("t continues:", repr(t[j + lo:j + lo + 200]))
