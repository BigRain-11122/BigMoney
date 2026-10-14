# -*- coding: utf-8 -*-
# W244 editor gen blocks part 3: A8 cfg downstream + A9 materializer comment/asserts

B_A8_OLD = ''' "ADMIT convention); W244+ projection per this window gate: ",
 f"A naive first-clean {rec['legs']['leg4']['W244p_A_naive']} CLEAN (hops=0, zero live seed refusers) / B naive first-clean ",
 f"{rec['legs']['leg4']['W244p_B_naive']} CLEAN (hops=0, zero live seed refusers); W244 freezer MUST re-derive on the post-W243 universe AND ",
 "reserve the own-wave A window when deriving B (do NOT assume the ",
 "staircase A-base==prior-B-tail+1 equality) -- the finalize "'''

B_A8_NEW = ''' "ADMIT convention); W244+ projection per this window gate: ",
 f"A naive first-clean {rec['legs']['leg4']['W244p_A_naive']} CLEAN (hops=0, zero live seed refusers) / B naive first-clean ",
 f"{rec['legs']['leg4']['W244p_B_naive']} hops=1 (live refusal inside the naive window -- honest forward walk first-clean {rec['legs']['leg4']['W244p_B_first_clean']} -- lands OUTSIDE the naive A window -- seed-gap face ",
 "inherited); W244 freezer MUST re-derive on the post-W243 universe AND ",
 "reserve the own-wave A window when deriving B (do NOT assume the ",
 "staircase A-base==prior-B-tail+1 equality) -- the finalize "'''

B_A9A_OLD = '''  "        # B = LIVE-SEED-REFUSAL face: the naive staircase continuation",
  f"        # {fmt(w242_b_tail + 1)}..{fmt(w242_b_tail + 200)} is REFUSED by the live SEED_REGISTRY point",
  "        # 541_500 perpetual_n2_w15_gen (hops=1, hop chain recorded:",
  "        # [([541_404, 541_603], 541_501, [541_500])]) -- honest forward walk lands",
  f"        # first-clean {fmt(b_lo)}..{fmt(b_hi)}, which is NOT inside the W243 own-wave A",
  "        # window",
  f"        # {fmt(a_lo)}..{fmt(a_hi)} (own-A sits far above the B staircase -- seed-decoupled A/B",
  "        # gap face fifth consecutive); B base != prior-wave B tail+1 EXACT in",
  "        # this face (live-seed hop) -- the honest walk governs;",'''

B_A9A_NEW = '''  "        # B = FIRST-CLEAN arithmetic continuation of the prior-wave B",
  f"        # tail ({fmt(w242_b_tail + 1)}..{fmt(w242_b_tail + 200)} CLEAN on the registered",
  "        # universe, hops=0, B_hop_chain empty + B_no_ownA_jump=true -- B",
  "        # lands OUTSIDE the own-A window",
  f"        # {fmt(a_lo)}..{fmt(a_hi)}; seed-decoupled A/B gap face fifth consecutive;",
  "        # B base == prior-wave B tail+1",
  f"        # ({fmt(w242_b_tail)}+1) machine-checkable;",'''

B_A9B_OLD = '''f\'        assert WAVE_CONFIGS[243]["b_exit_seed_base"] == {b_lo}, (\',
\'            "W243 B live-seed-hop face: the naive staircase continuation "\',
f\'            "{fmt(w242_b_tail + 1)}..{fmt(w242_b_tail + 200)} is REFUSED by the live "\',
\'            "SEED_REGISTRY point 541_500 perpetual_n2_w15_gen (hops=1, hop chain "\',
\'            "recorded) -- honest forward walk lands first-clean "\',
f\'            "{fmt(b_lo)}..{fmt(b_hi)}; B base != prior-B-tail+1 EXACT in this face "\',
\'            "(B_base_above_priorB_tail + B_live_seed_hop_face relation asserts, "\',
\'            "probe receipt leg1 mirrored exactly); B_no_ownA_jump=true")\',
f"        assert {b_lo} > {w242_b_tail} + 1, \\\\",
\'            "W243 B first-clean base must sit above the refused naive base (live-seed hop face)"\',
"        assert 541_500 in reg_ints and 541_500 not in set(range(",
f"{b_lo}, {b_hi + 1})), \\\\",
\'            "W243 B refuser-adjacency face: the live refuser 541_500 must sit inside SEED_REGISTRY and immediately below the B window"\''''

B_A9B_NEW = '''f\'        assert WAVE_CONFIGS[243]["b_exit_seed_base"] == {b_lo} == {w242_b_tail} + 1, (\',
\'            "W243 B keeps the staircase base (FIRST-CLEAN arithmetic "\',
\'            "continuation of the prior-wave B tail, hops=0, B_hop_chain "\',
\'            "empty + B_no_ownA_jump=true -- B lands outside the own-A "\',
\'            "window; seed-decoupled A/B gap face fifth consecutive; "\',
\'            "B base == prior-wave B tail+1 machine-checkable)")\''''
