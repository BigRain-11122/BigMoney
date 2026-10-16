# -*- coding: utf-8 -*-
# r1050 bm-c: repair P5e-tail-amsg + P5e-tail-aclean calls in the derive editor.
# Defect: dead window authored multi-line needles missing the per-line `'`
# wrappers/commas present in the generated script's list-literal source, plus a
# no-op `.replace("'''","'")` trick. Rebuilt as exact substring needles.
import io

EP = "results/_w252bmc_derive_editor.py"
ed = io.open(EP, encoding="utf-8").read()

# ---- P5e-tail-amsg: 5-line needle (post-blanket) -> 7-line W252 staircase dst
needle_amsg = "\n".join([
    '            "W252 A must be the first-clean arithmetic continuation of the "\',',
    "'            \"prior-wave A tail (hops=0, A_hop_chain empty + A_clean_at_naive_start=true -- \"',",
    "'            \"seed-decoupled A-continuation face, FOURTEENTH consecutive seed-gap face, \"',",
    "'            \"exactly as the W251 probe leg4 + seat leg4 succession projection notes \"',",
    "'            \"anticipated; A base == prior-wave A tail+1 machine-checkable)\"",
])
dst_amsg = "\n".join([
    '            "W252 A staircase-affects-A walk: the naive continuation is REFUSED at "\',',
    "'            \"its own start (the registered W251 B band sits INSIDE the naive A window -- \"',",
    "'            \"staircase re-emergence affects A; hops=1, A_hop_chain verbatim in the probe receipt, \"',",
    "'            \"A_clean_at_naive_start=false, A_staircase_hop_past_W251_B=true; the walk hops past \"',",
    "'            \"the W251 B tail -> A first-clean -- FIRST A-hop since the W239 staircase era, \"',",
    "'            \"the fourteen-wave seed-gap face ENDS at W252; A base == registered prior-wave B \"',",
    "'            \"tail+1 machine-checkable, floor relation honored)\"",
])
s1 = ed.find("rep('''            \"W252 A must be the first-clean")
assert s1 > 0, "amsg call start not found"
e1 = ed.find('"P5e-tail-amsg")', s1)
assert e1 > 0, "amsg call end not found"
new_amsg = "rep(" + repr(needle_amsg) + ",\n    " + repr(dst_amsg) + ', 1, "P5e-tail-amsg")'
ed = ed[:s1] + new_amsg + ed[e1 + len('"P5e-tail-amsg")'):]
print("amsg call rebuilt")

# ---- P5e-tail-aclean: single-line substring needle (drop the broken trick)
needle_ac = '            "W252 A window must be CLEAN (first-clean ADMIT face, A-continuation)"\''
dst_ac = '            "W252 A window must be CLEAN (first-clean ADMIT face, staircase walk landing)"\''
s2 = ed.find("rep('''            \"W252 A window must be CLEAN")
assert s2 > 0, "aclean call start not found"
e2 = ed.find('"P5e-tail-aclean")', s2)
assert e2 > 0, "aclean call end not found"
new_ac = "rep(" + repr(needle_ac) + ", " + repr(dst_ac) + ', 1, "P5e-tail-aclean")'
ed = ed[:s2] + new_ac + ed[e2 + len('"P5e-tail-aclean")'):]
print("aclean call rebuilt")

assert ".replace(\"'''\", \"'\")" not in ed, "leftover replace-trick"
io.open(EP, "w", encoding="utf-8", newline="").write(ed)
print("PATCH2 LANDED")
