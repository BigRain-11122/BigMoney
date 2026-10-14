# -*- coding: utf-8 -*-
# W244 editor gen blocks part 2: A5 pf_comment B-block + A6 pf_comment downstream projection

B_A5_OLD = '''"    # B = LIVE-SEED-REFUSAL face: the naive staircase continuation",
"    # " + fmt(w242_b_tail + 1) + ".." + fmt(w242_b_tail + 200) + " is REFUSED by the live SEED_REGISTRY point",
"    # 541_500 perpetual_n2_w15_gen (hops=1, hop chain recorded) -- honest",
"    # forward walk lands first-clean " + fmt(b_lo) + ".." + fmt(b_hi) + "; B base != prior-wave",
"    # B tail+1 in this face (live-seed hop); B lands OUTSIDE the own-A window",
"    # " + fmt(a_lo) + ".." + fmt(a_hi) + ": seed-decoupled A/B gap face fifth",
"    # consecutive; B_no_ownA_jump=true;",'''

B_A5_NEW = '''"    # B = FIRST-CLEAN arithmetic continuation of the prior-wave B tail",
"    # (" + fmt(w242_b_tail + 1) + ".." + fmt(w242_b_tail + 200) + " CLEAN on the",
"    # registered universe, hops=0, B_hop_chain empty + B_no_ownA_jump=true -- B",
"    # lands OUTSIDE the own-A window " + fmt(a_lo) + ".." + fmt(a_hi) + ":",
"    # seed-decoupled A/B gap face fifth",
"    # consecutive; B base == prior-wave B tail+1 (" + fmt(w242_b_tail) + "+1) machine-checkable;",'''

B_A6_OLD = '''"    # W244+ projection (gate-derived pre-seat probe leg4, pre-W243",
"    # universe): A naive first-clean " + rec["legs"]["leg4"]["W244p_A_naive"] + " CLEAN (hops=0, zero live",
"    # seed refusers) / B naive first-clean " + rec["legs"]["leg4"]["W244p_B_naive"] + " CLEAN (hops=" + str(rec["legs"]["leg4"]["hops_B"]) + ", zero live",
"    # seed refusers); W244 freezer MUST re-derive on the post-W243 universe",
"    # AND reserve the own-wave A window when deriving B (do NOT assume the",
"    # staircase A-base==prior-B-tail+1 equality); never transcribe r587.",'''

B_A6_NEW = '''"    # W244+ projection (gate-derived pre-seat probe leg4, pre-W243",
"    # universe): A naive first-clean " + rec["legs"]["leg4"]["W244p_A_naive"] + " CLEAN (hops=0, zero live",
"    # seed refusers) / B naive first-clean " + rec["legs"]["leg4"]["W244p_B_naive"] + " hops=" + str(rec["legs"]["leg4"]["hops_B"]) + " (live refusal",
"    # inside the naive window -- honest forward walk first-clean",
"    # " + rec["legs"]["leg4"]["W244p_B_first_clean"] + " -- B lands OUTSIDE",
"    # the naive A window, seed-gap face inherited); W244 freezer MUST",
"    # re-derive on the post-W243 universe AND reserve the own-wave A window",
"    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1",
"    # equality); never transcribe r587.",'''

B_A7_OLD = '''"non-rotational r587 forward-monotone walk) + B = LIVE-SEED-REFUSAL face (the naive ",
"staircase continuation ",
f"{fmt(w242_b_tail + 1)}..{fmt(w242_b_tail + 200)} is REFUSED at the naive window by a live ",
"SEED_REGISTRY point inside the window (541_500 perpetual_n2_w15_gen -- hops=1, hop chain ",
"recorded) -- honest forward walk lands first-clean ",
f"{fmt(b_lo)}..{fmt(b_hi)}, which is NOT inside the W243 own-wave A window {fmt(a_lo)}..{fmt(a_hi)} ",
"(own-A sits far above the B staircase -- seed-decoupled A/B gap face fifth consecutive); "
"B base != prior-wave B tail+1 EXACT in this face (live-seed hop) -- the honest walk governs, "
"B_no_ownA_jump=true (fc_b == fc_b_naive: no own-A reservation jump needed); ADMIT receipt "'''

B_A7_NEW = '''"non-rotational r587 forward-monotone walk) + B = FIRST-CLEAN arithmetic ",
"continuation of the prior-wave B tail (the continuation ",
f"{fmt(w242_b_tail + 1)}..{fmt(w242_b_tail + 200)} is CLEAN on the registered universe ",
"hops=0, B_hop_chain empty + B_no_ownA_jump=true -- B lands OUTSIDE the ",
f"own-A window {fmt(a_lo)}..{fmt(a_hi)}; seed-decoupled A/B gap ",
"face fifth consecutive; B base == prior-wave B ",
"tail+1 machine-checkable; cross-window convergence with the W242 seat leg4 succession projection ",
"notes -- all MANDATORY notes honored (post-W242 universe ",
"re-derive + live-trace re-read, no staircase-equality assumption); ADMIT receipt "'''
