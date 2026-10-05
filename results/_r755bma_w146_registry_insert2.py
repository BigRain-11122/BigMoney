# -*- coding: utf-8 -*-
"""r755 bm-a W146 registry insertion PART 2: perpetual_faces_n1.py
WAVE_CONFIGS[146] + materializer face + selftest prose face.
Consumes .codely-cli/scratch_w146_face.txt (transformed by part 1).
Idempotent guards; needle-asserted (r735/r739/r742 lineage).
r740 law: part2 runs strictly AFTER part1 (serial; face file must exist)."""
import io

n1_path = r"scripts\perpetual_faces_n1.py"
n1 = io.open(n1_path, encoding="utf-8").read()

# --- 2a. WAVE_CONFIGS[146] after entry 145 ---
if '"batch": "PERPETUAL-N1-W146"' in n1:
    print("n1: WAVE_CONFIGS[146] already present (idempotent skip)")
else:
    wc_anchor = '''                            "shard_subdir": "n1_w145", "out_name": "n1_w145_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    assert n1.count(wc_anchor) == 1, "n1: WAVE_CONFIGS W145 entry anchor"
    wc_new = '''                            "shard_subdir": "n1_w145", "out_name": "n1_w145_results.json",
                            "engine_owner": "bm-a"},
                       146: {"batch": "PERPETUAL-N1-W146",
                            "prereg": ("research/PERPETUAL_N1_W146_PREREG.md (wave-level frozen "
                                       "pre-run; design = frozen v1 null calibration verbatim, "
                                       "new seed bands only; ONE HUNDRED-AND-THIRTY-SIXTH ENGINE-OWNED WAVE "
                                       "BY MACHINE-DERIVE (engine_owner rows 135 + candidate), "
                                       "own-series continuation per O-20261001-2355 sec.2 (first-free-"
                                       "number law after the REGISTERED W145 row bm-a r754 freeze "
                                       "98c661f8f, SINGLE STATE zero seat gap W2..W145 all "
                                       "registered; W145 finalize landed same-window r755, ledger "
                                       "head 715,011, merged pool K=316,920; seat published=reserved "
                                       "MSG-2026-10-06-033x-bma-w146-seat PUSHED to origin c8183f342 "
                                       "BEFORE this freeze per r565 early-visibility law (payload = "
                                       "seat MSG + pre-seat probe + probe receipt + W145 finalize "
                                       "products; deletion-set EMPTY; pre-freeze push two-hop merge "
                                       "delivery c8183f342 -> 8d4248daf (first push raced origin "
                                       "forward = r524 behind-signal; merge-mode closeout, zero "
                                       "--no-verify); pre-seat probe and freeze-window band-gate "
                                       "runs derive identical, no fork face), "
                                       "engine_owner=bm-a, wave 146: "
                                       "A = FIRST-CLEAN past the registered W145 B band (the "
                                       "arithmetic continuation 335_804..337_803 is REFUSED at its "
                                       "own start by the W145 B band 335_804..336_003, exactly as "
                                       "the r754 W145 gate-tail projection note anticipated; honest "
                                       "forward walk hops=1 -> 336_004..338_003; A base == "
                                       "prior-wave B tail+1 machine-checkable = A-hops-prior-B "
                                       "staircase fifth instance, E36 card; non-rotational r587 "
                                       "forward-monotone walk) + B = FIRST-CLEAN past the "
                                       "own-wave A window (the arithmetic continuation "
                                       "336_004..336_203 is CLEAN on the registered universe but "
                                       "lands INSIDE the W146 A band window -- same-freeze mutual "
                                       "exclusion, W141 precedent, leg2 law -- the walk with the "
                                       "own-wave A window reserved jumps to 338_004, first-clean "
                                       "338_004..338_203 hops=1, non-rotational r587 forward-"
                                       "monotone walk; B base == own-wave A tail+1 machine-checkable; "
                                       "cross-window convergence with the r754 W145 gate-tail "
                                       "projection note re-derived -- both MANDATORY notes honored "
                                       "(post-W145 universe re-derive + own-wave A reservation); "
                                       "ADMIT receipt results/_r755bma_w146_band_gate.py; W147+ "
                                       "projection per this window gate: A first-clean "
                                       "338_004..340_003 CLEAN / B first-clean 338_204..338_403 "
                                       "CLEAN -- naive B lands INSIDE the naive A window and the "
                                       "registered W146 B band 338_004..338_203 will refuse the "
                                       "naive W147 A window; W147 freezer MUST re-derive on the "
                                       "post-W146 universe AND reserve the own-wave A window when "
                                       "deriving B (W141 precedent, leg2 law, E36 staircase card); "
                                       "W1..W145 finalize ALL LANDED (W145 finalize one-pass bm-a "
                                       "r755, §7/§8 backfill same commit; net chain head 715,011, "
                                       "merged pool K=316,920) -- ZERO in-flight upstream "
                                       "seats, clean finalize chain precondition -- finalize merge "
                                       "loop still derives the wave set from registry keys at run "
                                       "time, FAIL-CLOSED r307 always on)"),
                            "a_seed_base": 336_004,        # law sec.4 W146 A: 336_004..338_003 (FIRST-CLEAN past the registered W145 B band; arithmetic 335_804..337_803 REFUSED at own start by the W145 B band; hops=1; A-hops-prior-B staircase fifth instance, E36 card)
                            "b_exit_seed_base": 338_004,   # law sec.4 W146 B: 338_004..338_203 (FIRST-CLEAN past the own-wave A window; arithmetic 336_004..336_203 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)
                            "shard_subdir": "n1_w146", "out_name": "n1_w146_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    n1 = n1.replace(wc_anchor, wc_new)
    print("n1: WAVE_CONFIGS[146] inserted")

# --- 2b. materializer face insertion after the W145 face end ---
if "_set_wave(146)" in n1:
    print("n1: W146 materializer face already present (idempotent skip)")
else:
    face_anchor = '''        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim'''
    assert n1.count(face_anchor) == 1, "n1: face insertion anchor"
    face = io.open(r".codely-cli\scratch_w146_face.txt", encoding="utf-8").read()
    assert face.lstrip().startswith("# --- W146 materializer face"), "face sanity"
    assert "_set_wave(146)" in face, "face wave sanity"
    n1 = n1.replace(face_anchor,
        '''        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
''' + face + '''    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim''')
    print("n1: W146 materializer face inserted")

# --- 2c. selftest prose face after the W145 prose ---
if 'law sec.4 W146 row, r755 bm-a] ' in n1:
    print("n1: W146 prose face already present (idempotent skip)")
else:
    prose_anchor = 'W145 row, r754 bm-a] "' + chr(10) + '          "+ T-141 s2 "'
    assert n1.count(prose_anchor) == 1, "n1: prose anchor"
    prose_new = '''W145 row, r754 bm-a] "
          "+ W146 materializer face [same guard set, dep=W17..W145 outputs "
          "ALL PRESENT (landed net chain head 715,011 = W145 bm-a r755 "
          "one-pass, §7/§8 backfill same commit; K=316,920 merged "
          "pool; ZERO in-flight upstream seats, clean precondition freeze "
          "window), ONE HUNDRED-AND-THIRTY-SIXTH ENGINE-OWNED WAVE BY "
          "MACHINE-DERIVE (engine_owner rows 135 + candidate) bm-a's "
          "sixty-second owned claim per machine-derive (engine_owner==bm-a "
          "rows 61 + candidate), engine_owner=bm-a per engine de-throttle "
          "law O-20261001-2355 sec.2 own-continuous-series (wave 146 = "
          "first FREE number after the REGISTERED W145 row bm-a r754 "
          "freeze 98c661f8f, SINGLE STATE zero seat gap W2..W145 all "
          "registered; seat published=reserved "
          "MSG-2026-10-06-033x-bma-w146-seat pushed to origin c8183f342 "
          "BEFORE this freeze, r565 law (payload = seat MSG + pre-seat "
          "probe + probe receipt + W145 finalize products, deletion-set "
          "EMPTY; pre-freeze push two-hop merge delivery c8183f342 -> "
          "8d4248daf (first push raced origin forward = r524 "
          "behind-signal; merge-mode closeout, zero --no-verify), "
          "A = FIRST-CLEAN past the registered W145 B band (the "
          "arithmetic continuation 335_804..337_803 is REFUSED at its "
          "own start by the W145 B band 335_804..336_003, exactly as "
          "the r754 W145 gate-tail projection note anticipated; honest "
          "forward walk hops=1 -> 336_004..338_003; A base == "
          "prior-wave B tail+1 machine-checkable = A-hops-prior-B "
          "staircase fifth instance, E36 card; non-rotational r587 "
          "forward-monotone walk) + B = FIRST-CLEAN past the "
          "own-wave A window (the arithmetic continuation "
          "336_004..336_203 is CLEAN on the registered universe but "
          "lands INSIDE the W146 A band window -- same-freeze mutual "
          "exclusion, W141 precedent, leg2 law -- the walk with the "
          "own-wave A window reserved jumps to 338_004, first-clean "
          "338_004..338_203 hops=1, non-rotational r587 forward-"
          "monotone walk; B base == own-wave A tail+1 machine-checkable; "
          "cross-window convergence with the r754 W145 gate-tail "
          "projection note re-derived -- both MANDATORY notes honored; "
          "ADMIT receipt results/_r755bma_w146_band_gate.py; W147+ "
          "projection per this window gate: A first-clean "
          "338_004..340_003 CLEAN / B first-clean 338_204..338_403 "
          "CLEAN -- naive B lands INSIDE the naive A window and the "
          "registered W146 B band 338_004..338_203 will refuse the "
          "naive W147 A window; W147 freezer MUST re-derive on the "
          "post-W146 universe AND reserve the own-wave A window when "
          "deriving B (W141 precedent, same-freeze mutual exclusion, "
          "leg2 law, E36 staircase card)) disclosed for the next "
          "freezer; not a free pick -- R250), law sec.4 "
          "W146 row, r755 bm-a] "
          "+ T-141 s2 "'''
    n1 = n1.replace(prose_anchor, prose_new)
    print("n1: W146 prose face inserted")

io.open(n1_path, "w", encoding="utf-8", newline="\n").write(n1)
print("PART 2 DONE (n1 WAVE_CONFIGS[146] + face + prose)")
