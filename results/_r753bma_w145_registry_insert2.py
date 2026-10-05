# -*- coding: utf-8 -*-
"""r753 bm-a W145 registry insertion PART 2: perpetual_faces_n1.py
WAVE_CONFIGS[145] + materializer face + selftest prose face.
Consumes .codely-cli/scratch_w145_face.txt (transformed by part 1).
Idempotent guards; needle-asserted (r735/r739/r742 lineage).
r740 law: part2 runs strictly AFTER part1 (serial; face file must exist)."""
import io

n1_path = r"scripts\perpetual_faces_n1.py"
n1 = io.open(n1_path, encoding="utf-8").read()

# --- 2a. WAVE_CONFIGS[145] after entry 144 ---
if '"batch": "PERPETUAL-N1-W145"' in n1:
    print("n1: WAVE_CONFIGS[145] already present (idempotent skip)")
else:
    wc_anchor = '''                            "shard_subdir": "n1_w144", "out_name": "n1_w144_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    assert n1.count(wc_anchor) == 1, "n1: WAVE_CONFIGS W144 entry anchor"
    wc_new = '''                            "shard_subdir": "n1_w144", "out_name": "n1_w144_results.json",
                            "engine_owner": "bm-a"},
                       145: {"batch": "PERPETUAL-N1-W145",
                            "prereg": ("research/PERPETUAL_N1_W145_PREREG.md (wave-level frozen "
                                       "pre-run; design = frozen v1 null calibration verbatim, "
                                       "new seed bands only; ONE HUNDRED-AND-THIRTY-FIFTH ENGINE-OWNED WAVE "
                                       "BY MACHINE-DERIVE (engine_owner rows 134 + candidate), "
                                       "own-series continuation per O-20261001-2355 sec.2 (first-free-"
                                       "number law after the REGISTERED W144 row bm-a r752 freeze "
                                       "ff6d2f918, SINGLE STATE zero seat gap W2..W144 all "
                                       "registered; W144 finalize landed same-window r753, ledger "
                                       "head 712,811, merged pool K=314,720; seat published=reserved "
                                       "MSG-2026-10-06-023x-bma-w145-seat PUSHED to origin 55c2a1715 "
                                       "BEFORE this freeze per r565 early-visibility law (payload = "
                                       "seat MSG + pre-seat probe + probe receipt; deletion-set EMPTY; "
                                       "pre-freeze push two-hop merge delivery 55c2a1715 -> d5fdbb317 "
                                       "(first push raced origin forward = r524 behind-signal; "
                                       "merge-mode closeout, zero --no-verify); "
                                       "pre-seat probe and freeze-window band-gate runs derive "
                                       "identical, no fork face), "
                                       "engine_owner=bm-a, wave 145: "
                                       "A = FIRST-CLEAN past the registered W144 B band (the "
                                       "arithmetic continuation 333_604..335_603 is REFUSED at its "
                                       "own start by the W144 B band 333_604..333_803, exactly as "
                                       "the r752 W144 gate-tail projection note anticipated; honest "
                                       "forward walk hops=1 -> 333_804..335_803; A base == "
                                       "prior-wave B tail+1 machine-checkable = A-hops-prior-B "
                                       "staircase fourth instance, E36 card; non-rotational r587 "
                                       "forward-monotone walk) + B = FIRST-CLEAN past the "
                                       "own-wave A window (the arithmetic continuation "
                                       "333_804..334_003 is CLEAN on the registered universe but "
                                       "lands INSIDE the W145 A band window -- same-freeze mutual "
                                       "exclusion, W141 precedent, leg2 law -- the walk with the "
                                       "own-wave A window reserved jumps to 335_804, first-clean "
                                       "335_804..336_003 hops=1, non-rotational r587 forward-"
                                       "monotone walk; B base == own-wave A tail+1 machine-checkable; "
                                       "cross-window convergence with the r752 W144 gate-tail "
                                       "projection note re-derived -- both MANDATORY notes honored "
                                       "(post-W144 universe re-derive + own-wave A reservation); "
                                       "ADMIT receipt results/_r753bma_w145_band_gate.py; W146+ "
                                       "projection per this window gate: A first-clean "
                                       "335_804..337_803 CLEAN / B first-clean 336_004..336_203 "
                                       "CLEAN -- naive B lands INSIDE the naive A window and the "
                                       "registered W145 B band 335_804..336_003 will refuse the "
                                       "naive W146 A window; W146 freezer MUST re-derive on the "
                                       "post-W145 universe AND reserve the own-wave A window when "
                                       "deriving B (W141 precedent, leg2 law, E36 staircase card); "
                                       "W1..W144 finalize ALL LANDED (W144 finalize one-pass bm-a "
                                       "r753 247e53cf8, §7/§8 backfill same commit; net chain head "
                                       "712,811, merged pool K=314,720) -- ZERO in-flight upstream "
                                       "seats, clean finalize chain precondition -- finalize merge "
                                       "loop still derives the wave set from registry keys at run "
                                       "time, FAIL-CLOSED r307 always on)"),
                            "a_seed_base": 333_804,        # law sec.4 W145 A: 333_804..335_803 (FIRST-CLEAN past the registered W144 B band; arithmetic 333_604..335_603 REFUSED at own start by the W144 B band; hops=1; A-hops-prior-B staircase fourth instance, E36 card)
                            "b_exit_seed_base": 335_804,   # law sec.4 W145 B: 335_804..336_003 (FIRST-CLEAN past the own-wave A window; arithmetic 333_804..334_003 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)
                            "shard_subdir": "n1_w145", "out_name": "n1_w145_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    n1 = n1.replace(wc_anchor, wc_new)
    print("n1: WAVE_CONFIGS[145] inserted")

# --- 2b. materializer face insertion after the W144 face end ---
if "_set_wave(145)" in n1:
    print("n1: W145 materializer face already present (idempotent skip)")
else:
    face_anchor = '''        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim'''
    assert n1.count(face_anchor) == 1, "n1: face insertion anchor"
    face = io.open(r".codely-cli\scratch_w145_face.txt", encoding="utf-8").read()
    assert face.lstrip().startswith("# --- W145 materializer face"), "face sanity"
    assert "_set_wave(145)" in face, "face wave sanity"
    n1 = n1.replace(face_anchor,
        '''        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
''' + face + '''    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim''')
    print("n1: W145 materializer face inserted")

# --- 2c. selftest prose face after the W144 prose ---
if 'law sec.4 W145 row, r753 bm-a] ' in n1:
    print("n1: W145 prose face already present (idempotent skip)")
else:
    prose_anchor = 'W144 row, r752 bm-a] "' + chr(10) + '          "+ T-141 s2 "'
    assert n1.count(prose_anchor) == 1, "n1: prose anchor"
    prose_new = '''W144 row, r752 bm-a] "
          "+ W145 materializer face [same guard set, dep=W17..W144 outputs "
          "ALL PRESENT (landed net chain head 712,811 = W144 bm-a r753 "
          "one-pass 247e53cf8, §7/§8 backfill same commit; K=314,720 merged "
          "pool; ZERO in-flight upstream seats, clean precondition freeze "
          "window), ONE HUNDRED-AND-THIRTY-FIFTH ENGINE-OWNED WAVE BY "
          "MACHINE-DERIVE (engine_owner rows 134 + candidate) bm-a's "
          "sixty-first owned claim per machine-derive (engine_owner==bm-a "
          "rows 60 + candidate), engine_owner=bm-a per engine de-throttle "
          "law O-20261001-2355 sec.2 own-continuous-series (wave 145 = "
          "first FREE number after the REGISTERED W144 row bm-a r752 "
          "freeze ff6d2f918, SINGLE STATE zero seat gap W2..W144 all "
          "registered; seat published=reserved "
          "MSG-2026-10-06-023x-bma-w145-seat pushed to origin 55c2a1715 "
          "BEFORE this freeze, r565 law (payload = seat MSG + pre-seat "
          "probe + probe receipt, deletion-set EMPTY; pre-freeze push "
          "two-hop merge delivery 55c2a1715 -> d5fdbb317 (first push raced "
          "origin forward = r524 behind-signal; merge-mode closeout, "
          "zero --no-verify), "
          "A = FIRST-CLEAN past the registered W144 B band (the "
          "arithmetic continuation 333_604..335_603 is REFUSED at its "
          "own start by the W144 B band 333_604..333_803, exactly as "
          "the r752 W144 gate-tail projection note anticipated; honest "
          "forward walk hops=1 -> 333_804..335_803; A base == "
          "prior-wave B tail+1 machine-checkable = A-hops-prior-B "
          "staircase fourth instance, E36 card; non-rotational r587 "
          "forward-monotone walk) + B = FIRST-CLEAN past the "
          "own-wave A window (the arithmetic continuation "
          "333_804..334_003 is CLEAN on the registered universe but "
          "lands INSIDE the W145 A band window -- same-freeze mutual "
          "exclusion, W141 precedent, leg2 law -- the walk with the "
          "own-wave A window reserved jumps to 335_804, first-clean "
          "335_804..336_003 hops=1, non-rotational r587 forward-"
          "monotone walk; B base == own-wave A tail+1 machine-checkable; "
          "cross-window convergence with the r752 W144 gate-tail "
          "projection note re-derived -- both MANDATORY notes honored; "
          "ADMIT receipt results/_r753bma_w145_band_gate.py; W146+ "
          "projection per this window gate: A first-clean "
          "335_804..337_803 CLEAN / B first-clean 336_004..336_203 "
          "CLEAN -- naive B lands INSIDE the naive A window and the "
          "registered W145 B band 335_804..336_003 will refuse the "
          "naive W146 A window; W146 freezer MUST re-derive on the "
          "post-W145 universe AND reserve the own-wave A window when "
          "deriving B (W141 precedent, same-freeze mutual exclusion, "
          "leg2 law, E36 staircase card)) disclosed for the next "
          "freezer; not a free pick -- R250), law sec.4 "
          "W145 row, r753 bm-a] "
          "+ T-141 s2 "'''
    n1 = n1.replace(prose_anchor, prose_new)
    print("n1: W145 prose face inserted")

io.open(n1_path, "w", encoding="utf-8", newline="\n").write(n1)
print("PART 2 DONE (n1 WAVE_CONFIGS[145] + face + prose)")
