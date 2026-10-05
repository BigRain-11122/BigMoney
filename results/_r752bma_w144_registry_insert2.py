# -*- coding: utf-8 -*-
"""r752 bm-a W144 registry insertion PART 2: perpetual_faces_n1.py
WAVE_CONFIGS[144] + materializer face + selftest prose face.
Consumes .codely-cli/scratch_w144_face.txt (transformed by part 1).
Idempotent guards; needle-asserted (r735/r739/r742 lineage).
r740 law: part2 runs strictly AFTER part1 (serial; face file must exist)."""
import io

n1_path = r"scripts\perpetual_faces_n1.py"
n1 = io.open(n1_path, encoding="utf-8").read()

# --- 2a. WAVE_CONFIGS[144] after entry 143 ---
if '"batch": "PERPETUAL-N1-W144"' in n1:
    print("n1: WAVE_CONFIGS[144] already present (idempotent skip)")
else:
    wc_anchor = '''                            "shard_subdir": "n1_w143", "out_name": "n1_w143_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    assert n1.count(wc_anchor) == 1, "n1: WAVE_CONFIGS W143 entry anchor"
    wc_new = '''                            "shard_subdir": "n1_w143", "out_name": "n1_w143_results.json",
                            "engine_owner": "bm-a"},
                       144: {"batch": "PERPETUAL-N1-W144",
                            "prereg": ("research/PERPETUAL_N1_W144_PREREG.md (wave-level frozen "
                                       "pre-run; design = frozen v1 null calibration verbatim, "
                                       "new seed bands only; ONE HUNDRED-AND-THIRTY-FOURTH ENGINE-OWNED WAVE "
                                       "BY MACHINE-DERIVE (engine_owner rows 133 + candidate), "
                                       "own-series continuation per O-20261001-2355 sec.2 (first-free-"
                                       "number law after the REGISTERED W143 row bm-a r750 freeze "
                                       "86d3b070c, SINGLE STATE zero seat gap W2..W143 all "
                                       "registered; W143 finalize landed next-window r751, ledger "
                                       "head 710,611, merged pool K=312,520; seat published=reserved "
                                       "MSG-2026-10-06-011x-bma-w144-seat PUSHED to origin 2ba4a613f "
                                       "BEFORE this freeze per r565 early-visibility law (payload = "
                                       "seat MSG + pre-seat probe + probe receipt; deletion-set EMPTY; "
                                       "pre-freeze push plain fast-forward delivery 2ba4a613f, zero "
                                       "race this window (behind 0 at fetch), zero --no-verify); "
                                       "pre-seat probe and freeze-window band-gate runs derive "
                                       "identical, no fork face), "
                                       "engine_owner=bm-a, wave 144: "
                                       "A = FIRST-CLEAN past the registered W143 B band (the "
                                       "arithmetic continuation 331_404..333_403 is REFUSED at its "
                                       "own start by the W143 B band 331_404..331_603, exactly as "
                                       "the r750 W143 gate-tail projection note anticipated; honest "
                                       "forward walk hops=1 -> 331_604..333_603; A base == "
                                       "prior-wave B tail+1 machine-checkable = A-hops-prior-B "
                                       "staircase third instance, E36 card; non-rotational r587 "
                                       "forward-monotone walk) + B = FIRST-CLEAN past the "
                                       "own-wave A window (the arithmetic continuation "
                                       "331_604..331_803 is CLEAN on the registered universe but "
                                       "lands INSIDE the W144 A band window -- same-freeze mutual "
                                       "exclusion, W141 precedent, leg2 law -- the walk with the "
                                       "own-wave A window reserved jumps to 333_604, first-clean "
                                       "333_604..333_803 hops=1, non-rotational r587 forward-"
                                       "monotone walk; B base == own-wave A tail+1 machine-checkable; "
                                       "cross-window convergence with the r750 W143 gate-tail "
                                       "projection note re-derived -- both MANDATORY notes honored "
                                       "(post-W143 universe re-derive + own-wave A reservation); "
                                       "ADMIT receipt results/_r752bma_w144_band_gate.py; W145+ "
                                       "projection per this window gate: A first-clean "
                                       "333_604..335_603 CLEAN / B first-clean 333_804..334_003 "
                                       "CLEAN -- naive B lands INSIDE the naive A window and the "
                                       "registered W144 B band 333_604..333_803 will refuse the "
                                       "naive W145 A window; W145 freezer MUST re-derive on the "
                                       "post-W144 universe AND reserve the own-wave A window when "
                                       "deriving B (W141 precedent, leg2 law, E36 staircase card); "
                                       "W1..W143 finalize ALL LANDED (W143 finalize one-pass bm-a "
                                       "r751 6d93bd7ba, §7/§8 backfill same commit; net chain head "
                                       "710,611, merged pool K=312,520) -- ZERO in-flight upstream "
                                       "seats, clean finalize chain precondition -- finalize merge "
                                       "loop still derives the wave set from registry keys at run "
                                       "time, FAIL-CLOSED r307 always on)"),
                            "a_seed_base": 331_604,        # law sec.4 W144 A: 331_604..333_603 (FIRST-CLEAN past the registered W143 B band; arithmetic 331_404..333_403 REFUSED at own start by the W143 B band; hops=1; A-hops-prior-B staircase third instance, E36 card)
                            "b_exit_seed_base": 333_604,   # law sec.4 W144 B: 333_604..333_803 (FIRST-CLEAN past the own-wave A window; arithmetic 331_604..331_803 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)
                            "shard_subdir": "n1_w144", "out_name": "n1_w144_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    n1 = n1.replace(wc_anchor, wc_new)
    print("n1: WAVE_CONFIGS[144] inserted")

# --- 2b. materializer face insertion after the W143 face end ---
if "_set_wave(144)" in n1:
    print("n1: W144 materializer face already present (idempotent skip)")
else:
    face_anchor = '''        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim'''
    assert n1.count(face_anchor) == 1, "n1: face insertion anchor"
    face = io.open(r".codely-cli\scratch_w144_face.txt", encoding="utf-8").read()
    assert face.lstrip().startswith("# --- W144 materializer face"), "face sanity"
    assert "_set_wave(144)" in face, "face wave sanity"
    n1 = n1.replace(face_anchor,
        '''        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
''' + face + '''    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim''')
    print("n1: W144 materializer face inserted")

# --- 2c. selftest prose face after the W143 prose ---
if 'law sec.4 W144 row, r752 bm-a] ' in n1:
    print("n1: W144 prose face already present (idempotent skip)")
else:
    prose_anchor = 'W143 row, r750 bm-a] "' + chr(10) + '          "+ T-141 s2 "'
    assert n1.count(prose_anchor) == 1, "n1: prose anchor"
    prose_new = '''W143 row, r750 bm-a] "
          "+ W144 materializer face [same guard set, dep=W17..W143 outputs "
          "ALL PRESENT (landed net chain head 710,611 = W143 bm-a r751 "
          "one-pass 6d93bd7ba, §7/§8 backfill same commit; K=312,520 merged "
          "pool; ZERO in-flight upstream seats, clean precondition freeze "
          "window), ONE HUNDRED-AND-THIRTY-FOURTH ENGINE-OWNED WAVE BY "
          "MACHINE-DERIVE (engine_owner rows 133 + candidate) bm-a's "
          "sixtieth owned claim per machine-derive (engine_owner==bm-a "
          "rows 59 + candidate), engine_owner=bm-a per engine de-throttle "
          "law O-20261001-2355 sec.2 own-continuous-series (wave 144 = "
          "first FREE number after the REGISTERED W143 row bm-a r750 "
          "freeze 86d3b070c, SINGLE STATE zero seat gap W2..W143 all "
          "registered; seat published=reserved "
          "MSG-2026-10-06-011x-bma-w144-seat pushed to origin 2ba4a613f "
          "BEFORE this freeze, r565 law (payload = seat MSG + pre-seat "
          "probe + probe receipt, deletion-set EMPTY; pre-freeze push "
          "plain fast-forward delivery 2ba4a613f, zero race this window "
          "(behind 0 at fetch), zero --no-verify), "
          "A = FIRST-CLEAN past the registered W143 B band (the "
          "arithmetic continuation 331_404..333_403 is REFUSED at its "
          "own start by the W143 B band 331_404..331_603, exactly as "
          "the r750 W143 gate-tail projection note anticipated; honest "
          "forward walk hops=1 -> 331_604..333_603; A base == "
          "prior-wave B tail+1 machine-checkable = A-hops-prior-B "
          "staircase third instance, E36 card; non-rotational r587 "
          "forward-monotone walk) + B = FIRST-CLEAN past the "
          "own-wave A window (the arithmetic continuation "
          "331_604..331_803 is CLEAN on the registered universe but "
          "lands INSIDE the W144 A band window -- same-freeze mutual "
          "exclusion, W141 precedent, leg2 law -- the walk with the "
          "own-wave A window reserved jumps to 333_604, first-clean "
          "333_604..333_803 hops=1, non-rotational r587 forward-"
          "monotone walk; B base == own-wave A tail+1 machine-checkable; "
          "cross-window convergence with the r750 W143 gate-tail "
          "projection note re-derived -- both MANDATORY notes honored; "
          "ADMIT receipt results/_r752bma_w144_band_gate.py; W145+ "
          "projection per this window gate: A first-clean "
          "333_604..335_603 CLEAN / B first-clean 333_804..334_003 "
          "CLEAN -- naive B lands INSIDE the naive A window and the "
          "registered W144 B band 333_604..333_803 will refuse the "
          "naive W145 A window; W145 freezer MUST re-derive on the "
          "post-W144 universe AND reserve the own-wave A window when "
          "deriving B (W141 precedent, same-freeze mutual exclusion, "
          "leg2 law, E36 staircase card)) disclosed for the next "
          "freezer; not a free pick -- R250), law sec.4 "
          "W144 row, r752 bm-a] "
          "+ T-141 s2 "'''
    n1 = n1.replace(prose_anchor, prose_new)
    print("n1: W144 prose face inserted")

io.open(n1_path, "w", encoding="utf-8", newline="\n").write(n1)
print("PART 2 DONE (n1 WAVE_CONFIGS[144] + face + prose)")
