# -*- coding: utf-8 -*-
"""r745 bm-a W140 registry insertion PART 2: perpetual_faces_n1.py
WAVE_CONFIGS[140] + materializer face + selftest prose face.
Consumes .codely-cli/scratch_w140_face.txt (transformed by part 1).
Idempotent guards; needle-asserted (r735/r739/r742 lineage).
r740 law: part2 runs strictly AFTER part1 (serial; face file must exist)."""
import io

n1_path = r"scripts\perpetual_faces_n1.py"
n1 = io.open(n1_path, encoding="utf-8").read()

# --- 2a. WAVE_CONFIGS[140] after entry 139 ---
if '"batch": "PERPETUAL-N1-W140"' in n1:
    print("n1: WAVE_CONFIGS[140] already present (idempotent skip)")
else:
    wc_anchor = '''                            "shard_subdir": "n1_w139", "out_name": "n1_w139_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    assert n1.count(wc_anchor) == 1, "n1: WAVE_CONFIGS W139 entry anchor"
    wc_new = '''                            "shard_subdir": "n1_w139", "out_name": "n1_w139_results.json",
                            "engine_owner": "bm-a"},
                       140: {"batch": "PERPETUAL-N1-W140",
                            "prereg": ("research/PERPETUAL_N1_W140_PREREG.md (wave-level frozen "
                                       "pre-run; design = frozen v1 null calibration verbatim, "
                                       "new seed bands only; ONE HUNDRED-AND-THIRTIETH ENGINE-OWNED WAVE "
                                       "BY MACHINE-DERIVE (engine_owner rows 129 + candidate), "
                                       "own-series continuation per O-20261001-2355 sec.2 (first-free-"
                                       "number law after the REGISTERED W139 row bm-a r744 freeze "
                                       "4e3a018c7, SINGLE STATE zero seat gap W2..W139 all "
                                       "registered; W139 finalize landed same-window r745, ledger "
                                       "head 701,811, merged pool K=303,720; seat published=reserved "
                                       "MSG-2026-10-05-215x-bma-w140-seat PUSHED to origin 08710e2d0 "
                                       "BEFORE this freeze per r565 early-visibility law (payload = "
                                       "seat MSG + pre-seat probe + probe receipt; deletion-set EMPTY; "
                                       "pre-freeze push plain fast-forward delivery 08710e2d0, zero "
                                       "race this window, zero --no-verify); "
                                       "pre-seat probe and freeze-window band-gate runs derive "
                                       "identical, no fork face), "
                                       "engine_owner=bm-a, wave 140: "
                                       "A = arithmetic continuation from the registered W139 A tail "
                                       "(323_004..325_003 CLEAN hops=0) + B = arithmetic continuation "
                                       "from the registered W139 B tail (94_601..94_800 CLEAN hops=0 "
                                       "double-CLEAN continuation window; the W139 zero-hop "
                                       "double-CLEAN continuation landed past the contiguous "
                                       "registered band mass 70_001..94_600, clean by construction; "
                                       "cross-window convergence with the r744 W139 gate-tail "
                                       "projection re-derived; ADMIT receipt "
                                       "results/_r745bma_w140_band_gate.py; W141+ projection per this "
                                       "window gate: A 325_004..327_003 CLEAN / B first-clean "
                                       "323_004..323_203 hops=115 pre-W140-registration baseline "
                                       "honest hop chain -- B re-derive MANDATORY at W141 prereg, the "
                                       "baseline lands inside the now-registered W140 A band; W1..W139 "
                                       "finalize ALL LANDED (W139 finalize one-pass bm-a r745, 搂7 "
                                       "backfill same commit; net chain head 701,811, merged pool "
                                       "K=303,720) -- ZERO in-flight upstream seats, clean finalize "
                                       "chain precondition -- finalize merge loop still derives the "
                                       "wave set from registry keys at run time, FAIL-CLOSED r307 "
                                       "always on)"),
                            "a_seed_base": 323_004,        # law sec.4 W140 A: 323_004..325_003 (arithmetic continuation from the registered W139 A tail)
                            "b_exit_seed_base": 94_601,   # law sec.4 W140 B: 94_601..94_800 (arithmetic continuation from the registered W139 B tail, double-CLEAN continuation window, clean by construction)
                            "shard_subdir": "n1_w140", "out_name": "n1_w140_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    n1 = n1.replace(wc_anchor, wc_new)
    print("n1: WAVE_CONFIGS[140] inserted")

# --- 2b. materializer face insertion after the W139 face end ---
if "_set_wave(140)" in n1:
    print("n1: W140 materializer face already present (idempotent skip)")
else:
    face_anchor = '''        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim'''
    assert n1.count(face_anchor) == 1, "n1: face insertion anchor"
    face = io.open(r".codely-cli\scratch_w140_face.txt", encoding="utf-8").read()
    assert face.lstrip().startswith("# --- W140 materializer face"), "face sanity"
    assert "_set_wave(140)" in face, "face wave sanity"
    n1 = n1.replace(face_anchor,
        '''        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
''' + face + '''    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim''')
    print("n1: W140 materializer face inserted")

# --- 2c. selftest prose face after the W139 prose ---
if 'law sec.4 W140 row, r745 bm-a] ' in n1:
    print("n1: W140 prose face already present (idempotent skip)")
else:
    prose_anchor = 'W139 row, r744 bm-a] "' + chr(10) + '          "+ T-141 s2 "'
    assert n1.count(prose_anchor) == 1, "n1: prose anchor"
    prose_new = '''W139 row, r744 bm-a] "
          "+ W140 materializer face [same guard set, dep=W17..W139 outputs "
          "ALL PRESENT (landed net chain head 701,811 = W139 bm-a r745 "
          "one-pass, 搂7 backfill same commit; K=303,720 merged pool; ZERO "
          "in-flight upstream seats, clean precondition freeze window), "
          "ONE HUNDRED-AND-THIRTIETH ENGINE-OWNED WAVE BY MACHINE-DERIVE "
          "(engine_owner rows 129 + candidate) bm-a's fifty-sixth owned "
          "claim per machine-derive (engine_owner==bm-a rows 55 + "
          "candidate), engine_owner=bm-a per engine de-throttle law "
          "O-20261001-2355 sec.2 own-continuous-series (wave 140 = first "
          "FREE number after the REGISTERED W139 row bm-a r744 freeze "
          "4e3a018c7, SINGLE STATE zero seat gap W2..W139 all registered; "
          "seat published=reserved MSG-2026-10-05-215x-bma-w140-seat "
          "pushed to origin 08710e2d0 BEFORE this freeze, r565 law "
          "(payload = seat MSG + pre-seat probe + probe receipt, "
          "deletion-set EMPTY; pre-freeze push plain fast-forward "
          "delivery 08710e2d0, zero race this window, zero --no-verify), "
          "A = ARITHMETIC CONTINUATION from the registered W139 A tail "
          "(323_004..325_003 CLEAN hops=0) + B = ARITHMETIC CONTINUATION "
          "from the registered W139 B tail (94_601..94_800 CLEAN hops=0 "
          "double-CLEAN continuation window; the W139 zero-hop "
          "double-CLEAN continuation landed past the contiguous "
          "registered band mass 70_001..94_600, clean by construction; "
          "cross-window convergence with the r744 W139 gate-tail "
          "projection re-derived; ADMIT receipt "
          "results/_r745bma_w140_band_gate.py; W141+ projection per this "
          "window gate: A 325_004..327_003 CLEAN / B first-clean "
          "323_004..323_203 hops=115 pre-W140-registration baseline "
          "honest hop chain -- B re-derive MANDATORY at W141, the "
          "baseline lands inside the now-registered W140 A band) disclosed "
          "for the next freezer; not a "
          "free pick -- R250), law sec.4 "
          "W140 row, r745 bm-a] "
          "+ T-141 s2 "'''
    n1 = n1.replace(prose_anchor, prose_new)
    print("n1: W140 prose face inserted")

io.open(n1_path, "w", encoding="utf-8", newline="\n").write(n1)
print("PART 2 DONE (n1 WAVE_CONFIGS[140] + face + prose)")
