# -*- coding: utf-8 -*-
"""r740 bm-a W135 registry insertion PART 2: perpetual_faces_n1.py
WAVE_CONFIGS[135] + materializer face + selftest prose face.
Consumes .codely-cli/scratch_w135_face.txt (transformed by part 1).
Idempotent guards; needle-asserted (r735/r739 lineage)."""
import io

n1_path = r"scripts\perpetual_faces_n1.py"
n1 = io.open(n1_path, encoding="utf-8").read()

# --- 2a. WAVE_CONFIGS[135] after entry 134 ---
if '"batch": "PERPETUAL-N1-W135"' in n1:
    print("n1: WAVE_CONFIGS[135] already present (idempotent skip)")
else:
    wc_anchor = '''                            "shard_subdir": "n1_w134", "out_name": "n1_w134_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    assert n1.count(wc_anchor) == 1, "n1: WAVE_CONFIGS W134 entry anchor"
    wc_new = '''                            "shard_subdir": "n1_w134", "out_name": "n1_w134_results.json",
                            "engine_owner": "bm-a"},
                       135: {"batch": "PERPETUAL-N1-W135",
                            "prereg": ("research/PERPETUAL_N1_W135_PREREG.md (wave-level frozen "
                                       "pre-run; design = frozen v1 null calibration verbatim, "
                                       "new seed bands only; ONE HUNDRED-AND-TWENTY-FIFTH ENGINE-OWNED WAVE "
                                       "BY MACHINE-DERIVE (engine_owner rows 124 + candidate), "
                                       "own-series continuation per O-20261001-2355 sec.2 (first-free-"
                                       "number law after the REGISTERED W134 row bm-a r739 freeze "
                                       "d6b64dddd, SINGLE STATE zero seat gap W2..W134 all "
                                       "registered; W134 finalize landed same-window r740, ledger "
                                       "head 690,811, merged pool K=292,720; seat published=reserved "
                                       "MSG-2026-10-05-1933-bma-w135-seat PUSHED to origin 98712a0e3 "
                                       "BEFORE this freeze per r565 early-visibility law (payload = "
                                       "seat MSG + pre-seat probe + probe receipt; deletion-set EMPTY; "
                                       "direct clean fast-forward push this window, zero race, "
                                       "zero merge window, delivery 98712a0e3); "
                                       "pre-seat probe and freeze-window band-gate runs derive "
                                       "identical, no fork face), "
                                       "engine_owner=bm-a, wave 135: "
                                       "A = arithmetic continuation from the registered W134 A tail "
                                       "(313_004..315_003 CLEAN hops=0) + B = arithmetic continuation "
                                       "from the registered W134 B tail (69_502..69_701 CLEAN hops=0 "
                                       "double-CLEAN window; cross-window convergence with the r739 "
                                       "W134 seat MSG-1857 W135+ projection re-derived; ADMIT receipt "
                                       "results/_r740bma_w135_band_gate.py; W136+ projection per this "
                                       "window gate: A 315_004..317_003 CLEAN / B 69_702..69_901 "
                                       "CLEAN both hops=0; W1..W134 finalize ALL LANDED (W134 "
                                       "finalize one-pass bm-a r740, §7 backfill same commit; net "
                                       "chain head 690,811, merged pool K=292,720) -- ZERO in-flight "
                                       "upstream seats, clean finalize chain precondition -- finalize "
                                       "merge loop still derives the wave set from registry keys at "
                                       "run time, FAIL-CLOSED r307 always on)"),
                            "a_seed_base": 313_004,        # law sec.4 W135 A: 313_004..315_003 (arithmetic continuation from the registered W134 A tail)
                            "b_exit_seed_base": 69_502,   # law sec.4 W135 B: 69_502..69_701 (arithmetic continuation from the registered W134 B tail, CLEAN hops=0 double-CLEAN window)
                            "shard_subdir": "n1_w135", "out_name": "n1_w135_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    n1 = n1.replace(wc_anchor, wc_new)
    print("n1: WAVE_CONFIGS[135] inserted")

# --- 2b. materializer face insertion after the W134 face end ---
if "_set_wave(135)" in n1:
    print("n1: W135 materializer face already present (idempotent skip)")
else:
    face_anchor = '''        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim'''
    assert n1.count(face_anchor) == 1, "n1: face insertion anchor"
    face = io.open(r".codely-cli\scratch_w135_face.txt", encoding="utf-8").read()
    assert face.lstrip().startswith("# --- W135 materializer face"), "face sanity"
    assert "_set_wave(135)" in face, "face wave sanity"
    n1 = n1.replace(face_anchor,
        '''        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
''' + face + '''    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim''')
    print("n1: W135 materializer face inserted")

# --- 2c. selftest prose face after the W134 prose ---
if 'law sec.4 W135 row, r740 bm-a] ' in n1:
    print("n1: W135 prose face already present (idempotent skip)")
else:
    prose_anchor = 'W134 row, r739 bm-a] "\n          "+ T-141 s2 "'
    assert n1.count(prose_anchor) == 1, "n1: prose anchor"
    prose_new = '''W134 row, r739 bm-a] "
          "+ W135 materializer face [same guard set, dep=W17..W134 outputs "
          "ALL PRESENT (landed net chain head 690,811 = W134 bm-a r740 "
          "one-pass, §7 backfill same commit; K=292,720 merged pool; ZERO "
          "in-flight upstream seats, clean precondition freeze window), "
          "ONE HUNDRED-AND-TWENTY-FIFTH ENGINE-OWNED WAVE BY MACHINE-DERIVE "
          "(engine_owner rows 124 + candidate) bm-a's fifty-first owned "
          "claim per machine-derive (engine_owner==bm-a rows 50 + "
          "candidate), engine_owner=bm-a per engine de-throttle law "
          "O-20261001-2355 sec.2 own-continuous-series (wave 135 = first "
          "FREE number after the REGISTERED W134 row bm-a r739 freeze "
          "d6b64dddd, SINGLE STATE zero seat gap W2..W134 all registered; "
          "seat published=reserved MSG-2026-10-05-1933-bma-w135-seat "
          "pushed to origin 98712a0e3 BEFORE this freeze, r565 law "
          "(payload = seat MSG + pre-seat probe + probe receipt, "
          "deletion-set EMPTY; direct clean fast-forward push this "
          "window, zero race, zero merge window, delivery 98712a0e3), A = "
          "ARITHMETIC CONTINUATION from the registered W134 A tail "
          "(313_004..315_003 CLEAN hops=0) + B = ARITHMETIC CONTINUATION "
          "from the registered W134 B tail (69_502..69_701 CLEAN hops=0 "
          "double-CLEAN window; cross-window convergence with the r739 "
          "W134 seat MSG-1857 W135+ projection re-derived; ADMIT receipt "
          "results/_r740bma_w135_band_gate.py; W136+ projection per "
          "this window gate: A 315_004..317_003 CLEAN / B 69_702..69_901 "
          "CLEAN both hops=0) disclosed for the next freezer; not a "
          "free pick -- R250), law sec.4 "
          "W135 row, r740 bm-a] "
          "+ T-141 s2 "'''
    n1 = n1.replace(prose_anchor, prose_new)
    print("n1: W135 prose face inserted")

io.open(n1_path, "w", encoding="utf-8", newline="\n").write(n1)
print("PART 2 DONE (n1 WAVE_CONFIGS[135] + face + prose)")
