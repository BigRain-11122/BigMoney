# -*- coding: utf-8 -*-
# W244 editor gen blocks part 1: A2 band-facts comment+asserts (B refusal->clean)
B_A2_OLD = '''# W243 FACE (probe receipt leg1 relation_asserts):
# A keeps the A-continuation base (prior-wave A tail+1 EXACT -- the naive
# arithmetic continuation is CLEAN at its own start, hops=0, A_hop_chain
# empty, A_clean_at_naive_start=true -- fourth consecutive seed-gap face per
# the W242 seat leg4 anticipation confirmed live); B is a LIVE-SEED-REFUSAL
# face (the naive staircase continuation 541_404..541_603 is REFUSED by the
# live SEED_REGISTRY point 541_500 perpetual_n2_w15_gen, hops=1, hop chain
# recorded -- honest forward walk lands first-clean 541_501..541_700; B base
# != prior-wave B tail+1 in this face; B_no_ownA_jump=true; B lands OUTSIDE
# the own-A window); machine-derived from the LIVE registered row + receipt,
# never transcribed.
assert w242_a_tail + 1 == a_lo, "A continuation base relation broken (A == prior-wave A tail+1 EXACT)"
assert a_lo > w242_b_tail + 1, "seed-decoupled A-continuation face violated: A base must sit ABOVE prior-B tail+1 (seed-gap)"
assert b_hi < a_lo, "seed-decoupled A/B gap face violated: B window must sit entirely below own-A"
assert b_lo > w242_b_tail + 1, "B live-seed-hop face violated: first-clean B base must sit ABOVE the refused naive base (prior-B tail+1)"'''

B_A2_NEW = '''# W243 FACE (probe receipt leg1 relation_asserts):
# A keeps the A-continuation base (prior-wave A tail+1 EXACT -- the naive
# arithmetic continuation is CLEAN at its own start, hops=0, A_hop_chain
# empty, A_clean_at_naive_start=true -- fourth consecutive seed-gap face per
# the W242 seat leg4 anticipation confirmed live); B returns to the CLEAN
# staircase base (prior-wave B tail+1 EXACT, hops=0, B_hop_chain empty,
# B_clean_at_naive_start=true -- the prior-wave live-seed refusal chain is
# behind us; gap face fifth consecutive); A sits far above the B staircase
# (seed-decoupled A/B gap); machine-derived from the LIVE registered row,
# never transcribed.
assert w242_a_tail + 1 == a_lo, "A continuation base relation broken (A == prior-wave A tail+1 EXACT)"
assert w242_b_tail + 1 == b_lo, "B staircase base relation broken (B == prior-wave B tail+1 EXACT)"
assert a_lo > w242_b_tail + 1, "seed-decoupled A-continuation face violated: A base must sit ABOVE prior-B tail+1 (seed-gap)"
assert b_hi < a_lo, "seed-decoupled A/B gap face violated: B window must sit entirely below own-A"'''

B_A3A_OLD = 'assert leg1.get("hops_A") == 0, "hop-count drift vs probe receipt leg1 (A naive hops=0)"'
B_A3A_NEW = 'assert leg1.get("hops_A") == 0 and leg1.get("hops_B") == 0, "hop-count drift vs probe receipt leg1 (both bands naive hops=0)"'

B_A3B_OLD = '''assert leg1.get("hops_B") == 1 and leg1.get("B_naive_hops") == 1, \\
    "B hop-count drift vs probe receipt leg1 (live-seed refusal face, hops=1)"
assert leg1.get("B_hop_chain") and leg1["B_hop_chain"][0].get("refuser_pts") == [541_500] \\
    and leg1["B_hop_chain"][0].get("window") == [541_404, 541_603], \\
    f"B live-seed hop chain drift vs probe receipt leg1: {leg1.get('B_hop_chain')}"'''

B_A3B_NEW = 'assert leg1.get("B_hop_chain") == [] and leg1.get("B_naive_hops") == 0, "B hop-chain face drift (fc_b == fc_b_naive, hops=0, B_clean_at_naive_start=true)"'

B_A3C_OLD = '''assert ra.get("A_clean_at_naive_start") and ra.get("A_base_ge_priorB_tail_plus1") \\
    and ra.get("B_base_above_priorB_tail") and ra.get("AB_mutual_exclusion") \\
    and ra.get("B_live_seed_hop_face") and ra.get("B_no_ownA_jump"), \\
    f"probe receipt leg1 relation_asserts face drift: {ra}"'''

B_A3C_NEW = '''assert ra.get("A_clean_at_naive_start") and ra.get("A_base_ge_priorB_tail_plus1") \\
    and ra.get("B_clean_at_naive_start") and ra.get("B_base_above_priorB_tail") \\
    and ra.get("AB_mutual_exclusion") and ra.get("B_no_ownA_jump"), \\
    f"probe receipt leg1 relation_asserts face drift: {ra}"'''
