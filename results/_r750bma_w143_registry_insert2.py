# -*- coding: utf-8 -*-
"""r750 bm-a W143 registry insertion PART 2: perpetual_faces_n1.py
WAVE_CONFIGS[143] + materializer face + selftest prose face.
Consumes .codely-cli/scratch_w143_face.txt (transformed by part 1).
Idempotent guards; needle-asserted (r735/r739/r742 lineage).
r740 law: part2 runs strictly AFTER part1 (serial; face file must exist)."""
import io

n1_path = r"scripts\perpetual_faces_n1.py"
n1 = io.open(n1_path, encoding="utf-8").read()

# --- 2a. WAVE_CONFIGS[143] after entry 142 ---
if '"batch": "PERPETUAL-N1-W143"' in n1:
    print("n1: WAVE_CONFIGS[143] already present (idempotent skip)")
else:
    wc_anchor = '''                            "shard_subdir": "n1_w142", "out_name": "n1_w142_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    assert n1.count(wc_anchor) == 1, "n1: WAVE_CONFIGS W142 entry anchor"
    wc_new = '''                            "shard_subdir": "n1_w142", "out_name": "n1_w142_results.json",
                            "engine_owner": "bm-a"},
                       143: {"batch": "PERPETUAL-N1-W143",
                            "prereg": ("research/PERPETUAL_N1_W143_PREREG.md (wave-level frozen "
                                       "pre-run; design = frozen v1 null calibration verbatim, "
                                       "new seed bands only; ONE HUNDRED-AND-THIRTY-THIRD ENGINE-OWNED WAVE "
                                       "BY MACHINE-DERIVE (engine_owner rows 132 + candidate), "
                                       "own-series continuation per O-20261001-2355 sec.2 (first-free-"
                                       "number law after the REGISTERED W142 row bm-a r748 freeze "
                                       "16baa2a7b, SINGLE STATE zero seat gap W2..W142 all "
                                       "registered; W142 finalize landed next-window r749, ledger "
                                       "head 708,411, merged pool K=310,320; seat published=reserved "
                                       "MSG-2026-10-06-002x-bma-w143-seat PUSHED to origin 3a7640311 "
                                       "BEFORE this freeze per r565 early-visibility law (payload = "
                                       "seat MSG + pre-seat probe + probe receipt; deletion-set EMPTY; "
                                       "pre-freeze push plain fast-forward delivery 3a7640311, zero "
                                       "race this window (behind 0 at fetch), zero --no-verify); "
                                       "pre-seat probe and freeze-window band-gate runs derive "
                                       "identical, no fork face), "
                                       "engine_owner=bm-a, wave 143: "
                                       "A = FIRST-CLEAN past the registered W142 B band (the "
                                       "arithmetic continuation 329_204..331_203 is REFUSED at its "
                                       "own start by the W142 B band 329_204..329_403, exactly as "
                                       "the r748 W142 gate-tail projection note anticipated; honest "
                                       "forward walk hops=1 -> 329_404..331_403; A base == "
                                       "prior-wave B tail+1 machine-checkable = A-hops-prior-B "
                                       "staircase second instance, E36 card; non-rotational r587 "
                                       "forward-monotone walk) + B = FIRST-CLEAN past the "
                                       "own-wave A window (the arithmetic continuation "
                                       "329_404..329_603 is CLEAN on the registered universe but "
                                       "lands INSIDE the W143 A band window -- same-freeze mutual "
                                       "exclusion, W141 precedent, leg2 law -- the walk with the "
                                       "own-wave A window reserved jumps to 331_404, first-clean "
                                       "331_404..331_603 hops=1, non-rotational r587 forward-"
                                       "monotone walk; B base == own-wave A tail+1 machine-checkable; "
                                       "cross-window convergence with the r748 W142 gate-tail "
                                       "projection note re-derived -- both MANDATORY notes honored "
                                       "(post-W142 universe re-derive + own-wave A reservation); "
                                       "ADMIT receipt results/_r750bma_w143_band_gate.py; W144+ "
                                       "projection per this window gate: A first-clean "
                                       "331_404..333_403 CLEAN / B first-clean 331_604..331_803 "
                                       "CLEAN -- naive B lands INSIDE the naive A window and the "
                                       "registered W143 B band will refuse the naive W144 A "
                                       "window; W144 freezer MUST re-derive on the post-W143 "
                                       "universe AND reserve the own-wave A window when deriving B "
                                       "(W141 precedent, leg2 law, E36 staircase card); W1..W142 "
                                       "finalize ALL LANDED (W142 finalize one-pass bm-a r749 "
                                       "fec2adb73, §7/§8 backfill same commit; net chain head "
                                       "708,411, merged pool K=310,320) -- ZERO in-flight upstream "
                                       "seats, clean finalize chain precondition -- finalize merge "
                                       "loop still derives the wave set from registry keys at run "
                                       "time, FAIL-CLOSED r307 always on)"),
                            "a_seed_base": 329_404,        # law sec.4 W143 A: 329_404..331_403 (FIRST-CLEAN past the registered W142 B band; arithmetic 329_204..331_203 REFUSED at own start by the W142 B band; hops=1; A-hops-prior-B staircase second instance, E36 card)
                            "b_exit_seed_base": 331_404,   # law sec.4 W143 B: 331_404..331_603 (FIRST-CLEAN past the own-wave A window; arithmetic 329_404..329_603 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)
                            "shard_subdir": "n1_w143", "out_name": "n1_w143_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    n1 = n1.replace(wc_anchor, wc_new)
    print("n1: WAVE_CONFIGS[143] inserted")

# --- 2b. materializer face insertion after the W142 face end ---
if "_set_wave(143)" in n1:
    print("n1: W143 materializer face already present (idempotent skip)")
else:
    face_anchor = '''        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim'''
    assert n1.count(face_anchor) == 1, "n1: face insertion anchor"
    face = io.open(r".codely-cli\scratch_w143_face.txt", encoding="utf-8").read()
    assert face.lstrip().startswith("# --- W143 materializer face"), "face sanity"
    assert "_set_wave(143)" in face, "face wave sanity"
    n1 = n1.replace(face_anchor,
        '''        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
''' + face + '''    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim''')
    print("n1: W143 materializer face inserted")

# --- 2c. selftest prose face after the W142 prose ---
if 'law sec.4 W143 row, r750 bm-a] ' in n1:
    print("n1: W143 prose face already present (idempotent skip)")
else:
    prose_anchor = 'W142 row, r748 bm-a] "' + chr(10) + '          "+ T-141 s2 "'
    assert n1.count(prose_anchor) == 1, "n1: prose anchor"
    prose_new = '''W142 row, r748 bm-a] "
          "+ W143 materializer face [same guard set, dep=W17..W142 outputs "
          "ALL PRESENT (landed net chain head 708,411 = W142 bm-a r749 "
          "one-pass fec2adb73, §7/§8 backfill same commit; K=310,320 merged "
          "pool; ZERO in-flight upstream seats, clean precondition freeze "
          "window), ONE HUNDRED-AND-THIRTY-THIRD ENGINE-OWNED WAVE BY "
          "MACHINE-DERIVE (engine_owner rows 132 + candidate) bm-a's "
          "fifty-ninth owned claim per machine-derive (engine_owner==bm-a "
          "rows 58 + candidate), engine_owner=bm-a per engine de-throttle "
          "law O-20261001-2355 sec.2 own-continuous-series (wave 143 = "
          "first FREE number after the REGISTERED W142 row bm-a r748 "
          "freeze 16baa2a7b, SINGLE STATE zero seat gap W2..W142 all "
          "registered; seat published=reserved "
          "MSG-2026-10-06-002x-bma-w143-seat pushed to origin 3a7640311 "
          "BEFORE this freeze, r565 law (payload = seat MSG + pre-seat "
          "probe + probe receipt, deletion-set EMPTY; pre-freeze push "
          "plain fast-forward delivery 3a7640311, zero race this window "
          "(behind 0 at fetch), zero --no-verify), "
          "A = FIRST-CLEAN past the registered W142 B band (the "
          "arithmetic continuation 329_204..331_203 is REFUSED at its "
          "own start by the W142 B band 329_204..329_403, exactly as "
          "the r748 W142 gate-tail projection note anticipated; honest "
          "forward walk hops=1 -> 329_404..331_403; A base == "
          "prior-wave B tail+1 machine-checkable = A-hops-prior-B "
          "staircase second instance, E36 card; non-rotational r587 "
          "forward-monotone walk) + B = FIRST-CLEAN past the "
          "own-wave A window (the arithmetic continuation "
          "329_404..329_603 is CLEAN on the registered universe but "
          "lands INSIDE the W143 A band window -- same-freeze mutual "
          "exclusion, W141 precedent, leg2 law -- the walk with the "
          "own-wave A window reserved jumps to 331_404, first-clean "
          "331_404..331_603 hops=1, non-rotational r587 forward-"
          "monotone walk; B base == own-wave A tail+1 machine-checkable; "
          "cross-window convergence with the r748 W142 gate-tail "
          "projection note re-derived -- both MANDATORY notes honored; "
          "ADMIT receipt results/_r750bma_w143_band_gate.py; W144+ "
          "projection per this window gate: A first-clean "
          "331_404..333_403 CLEAN / B first-clean 331_604..331_803 "
          "CLEAN -- naive B lands INSIDE the naive A window and the "
          "registered W143 B band will refuse the naive W144 A "
          "window; W144 freezer MUST re-derive on the post-W143 "
          "universe AND reserve the own-wave A window when deriving "
          "B (W141 precedent, same-freeze mutual exclusion, leg2 "
          "law, E36 staircase card)) disclosed for the next freezer; "
          "not a free pick -- R250), law sec.4 "
          "W143 row, r750 bm-a] "
          "+ T-141 s2 "'''
    n1 = n1.replace(prose_anchor, prose_new)
    print("n1: W143 prose face inserted")

io.open(n1_path, "w", encoding="utf-8", newline="\n").write(n1)
print("PART 2 DONE (n1 WAVE_CONFIGS[143] + face + prose)")
