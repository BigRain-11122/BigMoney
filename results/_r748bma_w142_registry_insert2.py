# -*- coding: utf-8 -*-
"""r748 bm-a W142 registry insertion PART 2: perpetual_faces_n1.py
WAVE_CONFIGS[142] + materializer face + selftest prose face.
Consumes .codely-cli/scratch_w142_face.txt (transformed by part 1).
Idempotent guards; needle-asserted (r735/r739/r742 lineage).
r740 law: part2 runs strictly AFTER part1 (serial; face file must exist)."""
import io

n1_path = r"scripts\perpetual_faces_n1.py"
n1 = io.open(n1_path, encoding="utf-8").read()

# --- 2a. WAVE_CONFIGS[142] after entry 141 ---
if '"batch": "PERPETUAL-N1-W142"' in n1:
    print("n1: WAVE_CONFIGS[142] already present (idempotent skip)")
else:
    wc_anchor = '''                            "shard_subdir": "n1_w141", "out_name": "n1_w141_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    assert n1.count(wc_anchor) == 1, "n1: WAVE_CONFIGS W141 entry anchor"
    wc_new = '''                            "shard_subdir": "n1_w141", "out_name": "n1_w141_results.json",
                            "engine_owner": "bm-a"},
                       142: {"batch": "PERPETUAL-N1-W142",
                            "prereg": ("research/PERPETUAL_N1_W142_PREREG.md (wave-level frozen "
                                       "pre-run; design = frozen v1 null calibration verbatim, "
                                       "new seed bands only; ONE HUNDRED-AND-THIRTY-SECOND ENGINE-OWNED WAVE "
                                       "BY MACHINE-DERIVE (engine_owner rows 131 + candidate), "
                                       "own-series continuation per O-20261001-2355 sec.2 (first-free-"
                                       "number law after the REGISTERED W141 row bm-a r747 freeze "
                                       "7ffadab65, SINGLE STATE zero seat gap W2..W141 all "
                                       "registered; W141 finalize landed same-window r748, ledger "
                                       "head 706,211, merged pool K=308,120; seat published=reserved "
                                       "MSG-2026-10-05-233x-bma-w142-seat PUSHED to origin 94dee2c36 "
                                       "BEFORE this freeze per r565 early-visibility law (payload = "
                                       "seat MSG + pre-seat probe + probe receipt; deletion-set EMPTY; "
                                       "pre-freeze push via behind-1 merge absorb of the bm-b autofill "
                                       "keepalive tick, zero UU, zero --no-verify); "
                                       "pre-seat probe and freeze-window band-gate runs derive "
                                       "identical, no fork face), "
                                       "engine_owner=bm-a, wave 142: "
                                       "A = FIRST-CLEAN past the registered W141 B band (the "
                                       "arithmetic continuation 327_004..329_003 is REFUSED at its "
                                       "own start by the W141 B band 327_004..327_203, exactly as "
                                       "the r747 W141 gate-tail projection anticipated; honest "
                                       "forward walk hops=1 -> 327_204..329_203; A base == "
                                       "prior-wave B tail+1 machine-checkable = A-hops-prior-B "
                                       "staircase first instance, E36 card; non-rotational r587 "
                                       "forward-monotone walk) + B = FIRST-CLEAN past the "
                                       "own-wave A window (the arithmetic continuation "
                                       "327_204..327_403 is CLEAN on the registered universe but "
                                       "lands INSIDE the W142 A band window -- same-freeze mutual "
                                       "exclusion, W141 precedent, leg2 law -- the walk with the "
                                       "own-wave A window reserved jumps to 329_204, first-clean "
                                       "329_204..329_403 hops=1, non-rotational r587 forward-"
                                       "monotone walk; B base == own-wave A tail+1 machine-checkable; "
                                       "cross-window convergence with the r747 W141 gate-tail "
                                       "projection re-derived -- both MANDATORY notes honored "
                                       "(post-W141 universe re-derive + own-wave A reservation); "
                                       "ADMIT receipt results/_r748bma_w142_band_gate.py; W143+ "
                                       "projection per this window gate: A first-clean "
                                       "329_204..331_203 CLEAN / B first-clean 329_404..329_603 "
                                       "CLEAN -- naive B lands INSIDE the naive A window and the "
                                       "registered W142 B band will refuse the naive W143 A "
                                       "window; W143 freezer MUST re-derive on the post-W142 "
                                       "universe AND reserve the own-wave A window when deriving B "
                                       "(W141 precedent, leg2 law, E36 staircase card); W1..W141 "
                                       "finalize ALL LANDED (W141 finalize one-pass bm-a r748, "
                                       "§7 backfill same commit; net chain head 706,211, merged "
                                       "pool K=308,120) -- ZERO in-flight upstream seats, clean "
                                       "finalize chain precondition -- finalize merge loop still "
                                       "derives the wave set from registry keys at run time, "
                                       "FAIL-CLOSED r307 always on)"),
                            "a_seed_base": 327_204,        # law sec.4 W142 A: 327_204..329_203 (FIRST-CLEAN past the registered W141 B band; arithmetic 327_004..329_003 REFUSED at own start by the W141 B band; hops=1; A-hops-prior-B staircase first instance, E36 card)
                            "b_exit_seed_base": 329_204,   # law sec.4 W142 B: 329_204..329_403 (FIRST-CLEAN past the own-wave A window; arithmetic 327_204..327_403 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)
                            "shard_subdir": "n1_w142", "out_name": "n1_w142_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    n1 = n1.replace(wc_anchor, wc_new)
    print("n1: WAVE_CONFIGS[142] inserted")

# --- 2b. materializer face insertion after the W141 face end ---
if "_set_wave(142)" in n1:
    print("n1: W142 materializer face already present (idempotent skip)")
else:
    face_anchor = '''        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim'''
    assert n1.count(face_anchor) == 1, "n1: face insertion anchor"
    face = io.open(r".codely-cli\scratch_w142_face.txt", encoding="utf-8").read()
    assert face.lstrip().startswith("# --- W142 materializer face"), "face sanity"
    assert "_set_wave(142)" in face, "face wave sanity"
    n1 = n1.replace(face_anchor,
        '''        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
''' + face + '''    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim''')
    print("n1: W142 materializer face inserted")

# --- 2c. selftest prose face after the W141 prose ---
if 'law sec.4 W142 row, r748 bm-a] ' in n1:
    print("n1: W142 prose face already present (idempotent skip)")
else:
    prose_anchor = 'W141 row, r747 bm-a] "' + chr(10) + '          "+ T-141 s2 "'
    assert n1.count(prose_anchor) == 1, "n1: prose anchor"
    prose_new = '''W141 row, r747 bm-a] "
          "+ W142 materializer face [same guard set, dep=W17..W141 outputs "
          "ALL PRESENT (landed net chain head 706,211 = W141 bm-a r748 "
          "one-pass, §7 backfill same commit; K=308,120 merged pool; ZERO "
          "in-flight upstream seats, clean precondition freeze window), "
          "ONE HUNDRED-AND-THIRTY-SECOND ENGINE-OWNED WAVE BY MACHINE-DERIVE "
          "(engine_owner rows 131 + candidate) bm-a's fifty-eighth owned "
          "claim per machine-derive (engine_owner==bm-a rows 57 + "
          "candidate), engine_owner=bm-a per engine de-throttle law "
          "O-20261001-2355 sec.2 own-continuous-series (wave 142 = first "
          "FREE number after the REGISTERED W141 row bm-a r747 freeze "
          "7ffadab65, SINGLE STATE zero seat gap W2..W141 all registered; "
          "seat published=reserved MSG-2026-10-05-233x-bma-w142-seat "
          "pushed to origin 94dee2c36 BEFORE this freeze, r565 law "
          "(payload = seat MSG + pre-seat probe + probe receipt, "
          "deletion-set EMPTY; pre-freeze push via behind-1 merge "
          "absorb of the bm-b autofill keepalive tick, zero UU, zero "
          "--no-verify), "
          "A = FIRST-CLEAN past the registered W141 B band (the "
          "arithmetic continuation 327_004..329_003 is REFUSED at its "
          "own start by the W141 B band 327_004..327_203, exactly as "
          "the r747 W141 gate-tail projection anticipated; honest "
          "forward walk hops=1 -> 327_204..329_203; A base == "
          "prior-wave B tail+1 machine-checkable = A-hops-prior-B "
          "staircase first instance, E36 card; non-rotational r587 "
          "forward-monotone walk) + B = FIRST-CLEAN past the "
          "own-wave A window (the arithmetic continuation "
          "327_204..327_403 is CLEAN on the registered universe but "
          "lands INSIDE the W142 A band window -- same-freeze mutual "
          "exclusion, W141 precedent, leg2 law -- the walk with the "
          "own-wave A window reserved jumps to 329_204, first-clean "
          "329_204..329_403 hops=1, non-rotational r587 forward-"
          "monotone walk; B base == own-wave A tail+1 machine-checkable; "
          "cross-window convergence with the r747 W141 gate-tail "
          "projection re-derived -- both MANDATORY notes honored; ADMIT "
          "receipt results/_r748bma_w142_band_gate.py; W143+ projection "
          "per this window gate: A first-clean 329_204..331_203 CLEAN / "
          "B first-clean 329_404..329_603 CLEAN -- naive B lands INSIDE "
          "the naive A window and the registered W142 B band will "
          "refuse the naive W143 A window; W143 freezer MUST re-derive "
          "on the post-W142 universe AND reserve the own-wave A window "
          "when deriving B (W141 precedent, same-freeze mutual "
          "exclusion, leg2 law, E36 staircase card)) disclosed for the "
          "next freezer; not a free pick -- R250), law sec.4 "
          "W142 row, r748 bm-a] "
          "+ T-141 s2 "'''
    n1 = n1.replace(prose_anchor, prose_new)
    print("n1: W142 prose face inserted")

io.open(n1_path, "w", encoding="utf-8", newline="\n").write(n1)
print("PART 2 DONE (n1 WAVE_CONFIGS[142] + face + prose)")
