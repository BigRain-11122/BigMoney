# -*- coding: utf-8 -*-
"""r747 bm-a W141 registry insertion PART 2: perpetual_faces_n1.py
WAVE_CONFIGS[141] + materializer face + selftest prose face.
Consumes .codely-cli/scratch_w141_face.txt (transformed by part 1).
Idempotent guards; needle-asserted (r735/r739/r742 lineage).
r740 law: part2 runs strictly AFTER part1 (serial; face file must exist)."""
import io

n1_path = r"scripts\perpetual_faces_n1.py"
n1 = io.open(n1_path, encoding="utf-8").read()

# --- 2a. WAVE_CONFIGS[141] after entry 140 ---
if '"batch": "PERPETUAL-N1-W141"' in n1:
    print("n1: WAVE_CONFIGS[141] already present (idempotent skip)")
else:
    wc_anchor = '''                            "shard_subdir": "n1_w140", "out_name": "n1_w140_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    assert n1.count(wc_anchor) == 1, "n1: WAVE_CONFIGS W140 entry anchor"
    wc_new = '''                            "shard_subdir": "n1_w140", "out_name": "n1_w140_results.json",
                            "engine_owner": "bm-a"},
                       141: {"batch": "PERPETUAL-N1-W141",
                            "prereg": ("research/PERPETUAL_N1_W141_PREREG.md (wave-level frozen "
                                       "pre-run; design = frozen v1 null calibration verbatim, "
                                       "new seed bands only; ONE HUNDRED-AND-THIRTY-FIRST ENGINE-OWNED WAVE "
                                       "BY MACHINE-DERIVE (engine_owner rows 130 + candidate), "
                                       "own-series continuation per O-20261001-2355 sec.2 (first-free-"
                                       "number law after the REGISTERED W140 row bm-a r745 freeze "
                                       "5e3984200, SINGLE STATE zero seat gap W2..W140 all "
                                       "registered; W140 finalize landed same-window r746, ledger "
                                       "head 704,011, merged pool K=305,920; seat published=reserved "
                                       "MSG-2026-10-05-231x-bma-w141-seat PUSHED to origin aaa4d9be8 "
                                       "BEFORE this freeze per r565 early-visibility law (payload = "
                                       "seat MSG + pre-seat probe + probe receipt; deletion-set EMPTY; "
                                       "pre-freeze push plain fast-forward delivery aaa4d9be8, zero "
                                       "race this window, zero --no-verify); "
                                       "pre-seat probe and freeze-window band-gate runs derive "
                                       "identical, no fork face), "
                                       "engine_owner=bm-a, wave 141: "
                                       "A = arithmetic continuation from the registered W140 A tail "
                                       "(325_004..327_003 CLEAN hops=0) + B = FIRST-CLEAN past the "
                                       "own-wave A window (the arithmetic continuation 94_801..95_000 "
                                       "is REFUSED by probe seed 95_000; the honest forward walk "
                                       "hops=116 lands 325_004..325_203 inside the W141 A band "
                                       "window -- same-freeze mutual exclusion, leg2 law -- B "
                                       "continues past the own-wave A window, first-clean "
                                       "327_004..327_203 hops=117, non-rotational r587 forward-"
                                       "monotone walk; B base == own-wave A tail+1 machine-checkable; "
                                       "cross-window convergence with the r745 W140 gate-tail "
                                       "projection re-derived -- the re-derive-MANDATORY note "
                                       "honored, the own-A hop is the additional honest face; ADMIT "
                                       "receipt results/_r747bma_w141_band_gate.py; W142+ projection "
                                       "per this window gate: A first-clean 327_004..329_003 CLEAN / "
                                       "B first-clean 327_204..327_403 CLEAN -- naive B lands "
                                       "INSIDE the naive A window and the registered W141 B band "
                                       "will refuse the naive W142 A window; W142 freezer MUST "
                                       "re-derive on the post-W141 universe AND reserve the "
                                       "own-wave A window when deriving B (W141 precedent, leg2 "
                                       "law); W1..W140 finalize ALL LANDED (W140 finalize one-pass "
                                       "bm-a r746, §7 backfill same commit; net chain head 704,011, "
                                       "merged pool K=305,920) -- ZERO in-flight upstream seats, "
                                       "clean finalize chain precondition -- finalize merge loop "
                                       "still derives the wave set from registry keys at run time, "
                                       "FAIL-CLOSED r307 always on)"),
                            "a_seed_base": 325_004,        # law sec.4 W141 A: 325_004..327_003 (arithmetic continuation from the registered W140 A tail)
                            "b_exit_seed_base": 327_004,   # law sec.4 W141 B: 327_004..327_203 (FIRST-CLEAN past the own-wave A window; arithmetic 94_801..95_000 REFUSED by probe seed 95_000; hops=117 non-rotational r587; B base == own-wave A tail+1)
                            "shard_subdir": "n1_w141", "out_name": "n1_w141_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    n1 = n1.replace(wc_anchor, wc_new)
    print("n1: WAVE_CONFIGS[141] inserted")

# --- 2b. materializer face insertion after the W140 face end ---
if "_set_wave(141)" in n1:
    print("n1: W141 materializer face already present (idempotent skip)")
else:
    face_anchor = '''        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim'''
    assert n1.count(face_anchor) == 1, "n1: face insertion anchor"
    face = io.open(r".codely-cli\scratch_w141_face.txt", encoding="utf-8").read()
    assert face.lstrip().startswith("# --- W141 materializer face"), "face sanity"
    assert "_set_wave(141)" in face, "face wave sanity"
    n1 = n1.replace(face_anchor,
        '''        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
''' + face + '''    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim''')
    print("n1: W141 materializer face inserted")

# --- 2c. selftest prose face after the W140 prose ---
if 'law sec.4 W141 row, r747 bm-a] ' in n1:
    print("n1: W141 prose face already present (idempotent skip)")
else:
    prose_anchor = 'W140 row, r745 bm-a] "' + chr(10) + '          "+ T-141 s2 "'
    assert n1.count(prose_anchor) == 1, "n1: prose anchor"
    prose_new = '''W140 row, r745 bm-a] "
          "+ W141 materializer face [same guard set, dep=W17..W140 outputs "
          "ALL PRESENT (landed net chain head 704,011 = W140 bm-a r746 "
          "one-pass, §7 backfill same commit; K=305,920 merged pool; ZERO "
          "in-flight upstream seats, clean precondition freeze window), "
          "ONE HUNDRED-AND-THIRTY-FIRST ENGINE-OWNED WAVE BY MACHINE-DERIVE "
          "(engine_owner rows 130 + candidate) bm-a's fifty-seventh owned "
          "claim per machine-derive (engine_owner==bm-a rows 56 + "
          "candidate), engine_owner=bm-a per engine de-throttle law "
          "O-20261001-2355 sec.2 own-continuous-series (wave 141 = first "
          "FREE number after the REGISTERED W140 row bm-a r745 freeze "
          "5e3984200, SINGLE STATE zero seat gap W2..W140 all registered; "
          "seat published=reserved MSG-2026-10-05-231x-bma-w141-seat "
          "pushed to origin aaa4d9be8 BEFORE this freeze, r565 law "
          "(payload = seat MSG + pre-seat probe + probe receipt, "
          "deletion-set EMPTY; pre-freeze push plain fast-forward "
          "delivery aaa4d9be8, zero race this window, zero --no-verify), "
          "A = ARITHMETIC CONTINUATION from the registered W140 A tail "
          "(325_004..327_003 CLEAN hops=0) + B = FIRST-CLEAN past the "
          "own-wave A window (the arithmetic continuation 94_801..95_000 "
          "is REFUSED by probe seed 95_000; the honest forward walk "
          "hops=116 lands 325_004..325_203 inside the W141 A band "
          "window -- same-freeze mutual exclusion, leg2 law -- B "
          "continues past the own-wave A window, first-clean "
          "327_004..327_203 hops=117, non-rotational r587 forward-"
          "monotone walk; B base == own-wave A tail+1 machine-checkable; "
          "cross-window convergence with the r745 W140 gate-tail "
          "projection re-derived -- the re-derive-MANDATORY note "
          "honored, the own-A hop is the additional honest face; ADMIT "
          "receipt results/_r747bma_w141_band_gate.py; W142+ projection "
          "per this window gate: A first-clean 327_004..329_003 CLEAN / "
          "B first-clean 327_204..327_403 CLEAN -- naive B lands INSIDE "
          "the naive A window and the registered W141 B band will "
          "refuse the naive W142 A window; W142 freezer MUST re-derive "
          "on the post-W141 universe AND reserve the own-wave A window "
          "when deriving B (W141 precedent, same-freeze mutual "
          "exclusion, leg2 law)) disclosed for the next freezer; not a "
          "free pick -- R250), law sec.4 "
          "W141 row, r747 bm-a] "
          "+ T-141 s2 "'''
    n1 = n1.replace(prose_anchor, prose_new)
    print("n1: W141 prose face inserted")

io.open(n1_path, "w", encoding="utf-8", newline="\n").write(n1)
print("PART 2 DONE (n1 WAVE_CONFIGS[141] + face + prose)")
