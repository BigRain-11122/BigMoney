# -*- coding: utf-8 -*-
"""Heal the W325 editor's B landing law inside the n1 materializer block.

The gate-level assert and the receipt relation asserts were already rewritten by
the clone script, but the materializer's own band-fact assert still encoded the
W324 law ("B base == own-A tail+1").  W325's B hops past the REGISTERED SEED
perpetual_n2_w18_gen=732_500, so the landing is the FIRST CLEAN WINDOW above the
own-A tail (base == own-A tail + 201).  Comments are corrected in the same pass so
the emitted block stays honest.
"""
import io

p = "results/_w325bmc_freeze_edits.py"
t = io.open(p, encoding="utf-8", newline="").read()

OLD_COMMENTS = (
    '    "        # B = 1-HOP own-A RESERVATION CASCADE above own-A (naive continuation",\n'
    '    f"        # {fmt(w324_b_tail + 1)}..{fmt(w324_b_tail + 200)} CLEAN vs registered but lands INSIDE the own-wave A first-clean window);",\n'
    '    f"        # B base == own-A tail+1 ({fmt(a_hi)}+1) EXACT; SEVENTY-NINTH consecutive above-own-A landing.",\n')
NEW_COMMENTS = (
    '    "        # B = own-A RESERVATION CASCADE + REGISTERED-SEED HOP above own-A",\n'
    '    f"        # (naive {fmt(w324_b_tail + 1)}..{fmt(w324_b_tail + 200)} CLEAN vs registered but lands INSIDE the own-wave A first-clean window);",\n'
    '    f"        # the cascade window is REFUSED by the registered seed at its tail, so B base == FIRST CLEAN WINDOW above own-A ({fmt(a_hi)}+201); SEVENTY-NINTH consecutive above-own-A landing.",\n')

OLD_ASSERT = (
    '    f\'        assert WAVE_CONFIGS[{NEW_W}]["b_exit_seed_base"] == {b_lo} == {a_hi} + 1, (\',\n'
    '    f\'            "W{NEW_W} B 1-HOP own-A RESERVATION CASCADE face: naive continuation lands "\',\n'
    "    '            \"INSIDE the own-wave A first-clean window -- B hops past the own-wave A tail; \"',\n"
    "    '            \"B base == own-A tail+1 EXACT; B_hop_lands_inside_A=false\")\',\n")
NEW_ASSERT = (
    '    f\'        assert WAVE_CONFIGS[{NEW_W}]["b_exit_seed_base"] == {b_lo} == {a_hi} + 201, (\',\n'
    '    f\'            "W{NEW_W} B own-A RESERVATION CASCADE + REGISTERED-SEED HOP face: naive "\',\n'
    "    '            \"continuation lands INSIDE the own-wave A first-clean window, and the \"',\n"
    "    '            \"cascade window is REFUSED by the registered seed at its tail -- so B lands \"',\n"
    "    '            \"at the FIRST CLEAN WINDOW above own-A; B_hop_lands_inside_A=false\")\',\n")

for old, new in ((OLD_COMMENTS, NEW_COMMENTS), (OLD_ASSERT, NEW_ASSERT)):
    c = t.count(old)
    assert c == 1, (c, old[:70])
    t = t.replace(old, new)

io.open(p, "w", encoding="utf-8", newline="").write(t)
import py_compile
py_compile.compile(p, doraise=True)
print("B-landing law healed + py_compile green")
assert "{a_hi} + 1," not in t