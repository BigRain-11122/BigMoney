# -*- coding: utf-8 -*-
"""r743 bm-a W138 registry insertion PART 2: perpetual_faces_n1.py
WAVE_CONFIGS[138] + materializer face + selftest prose face.
Consumes .codely-cli/scratch_w138_face.txt (transformed by part 1).
Idempotent guards; needle-asserted (r735/r739/r742 lineage).
r740 law: part2 runs strictly AFTER part1 (serial; face file must exist)."""
import io

n1_path = r"scripts\perpetual_faces_n1.py"
n1 = io.open(n1_path, encoding="utf-8").read()

# --- 2a. WAVE_CONFIGS[138] after entry 137 ---
if '"batch": "PERPETUAL-N1-W138"' in n1:
    print("n1: WAVE_CONFIGS[138] already present (idempotent skip)")
else:
    wc_anchor = '''                            "shard_subdir": "n1_w137", "out_name": "n1_w137_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    assert n1.count(wc_anchor) == 1, "n1: WAVE_CONFIGS W137 entry anchor"
    wc_new = '''                            "shard_subdir": "n1_w137", "out_name": "n1_w137_results.json",
                            "engine_owner": "bm-a"},
                       138: {"batch": "PERPETUAL-N1-W138",
                            "prereg": ("research/PERPETUAL_N1_W138_PREREG.md (wave-level frozen "
                                       "pre-run; design = frozen v1 null calibration verbatim, "
                                       "new seed bands only; ONE HUNDRED-AND-TWENTY-EIGHTH ENGINE-OWNED WAVE "
                                       "BY MACHINE-DERIVE (engine_owner rows 127 + candidate), "
                                       "own-series continuation per O-20261001-2355 sec.2 (first-free-"
                                       "number law after the REGISTERED W137 row bm-a r742 freeze "
                                       "f9e4ec5d2, SINGLE STATE zero seat gap W2..W137 all "
                                       "registered; W137 finalize landed same-window r743, ledger "
                                       "head 697,411, merged pool K=299,320; seat published=reserved "
                                       "MSG-2026-10-05-211x-bma-w138-seat PUSHED to origin 0bf01ef64 "
                                       "BEFORE this freeze per r565 early-visibility law (payload = "
                                       "seat MSG + pre-seat probe + probe receipt; deletion-set EMPTY; "
                                       "pre-freeze push raced origin forward 3 commits = r524 "
                                       "behind-signal (bm-b r745 same-window wave), merge-mode "
                                       "clean auto-merge closeout, delivery 576b22603); "
                                       "pre-seat probe and freeze-window band-gate runs derive "
                                       "identical, no fork face), "
                                       "engine_owner=bm-a, wave 138: "
                                       "A = arithmetic continuation from the registered W137 A tail "
                                       "(319_004..321_003 CLEAN hops=0) + B = arithmetic continuation "
                                       "from the registered W137 B tail (94_201..94_400 CLEAN hops=0 "
                                       "double-CLEAN window; the W137 honest 12-hop forward walk "
                                       "landed past the contiguous registered band mass "
                                       "70_001..94_000, clean by construction; cross-window "
                                       "convergence with the r742 W137 gate-tail projection "
                                       "re-derived; ADMIT receipt "
                                       "results/_r743bma_w138_band_gate.py; W139+ projection per this "
                                       "window gate: A 321_004..323_003 CLEAN / B first-clean "
                                       "94_401..94_600 CLEAN hops=0 double-CLEAN; W1..W137 "
                                       "finalize ALL LANDED (W137 finalize one-pass bm-a r743, §7 "
                                       "backfill same commit; net chain head 697,411, merged pool "
                                       "K=299,320) -- ZERO in-flight upstream seats, clean finalize "
                                       "chain precondition -- finalize merge loop still derives the "
                                       "wave set from registry keys at run time, FAIL-CLOSED r307 "
                                       "always on)"),
                            "a_seed_base": 319_004,        # law sec.4 W138 A: 319_004..321_003 (arithmetic continuation from the registered W137 A tail)
                            "b_exit_seed_base": 94_201,   # law sec.4 W138 B: 94_201..94_400 (arithmetic continuation from the registered W137 B tail, double-CLEAN window, clean by construction)
                            "shard_subdir": "n1_w138", "out_name": "n1_w138_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    n1 = n1.replace(wc_anchor, wc_new)
    print("n1: WAVE_CONFIGS[138] inserted")

# --- 2b. materializer face insertion after the W137 face end ---
if "_set_wave(138)" in n1:
    print("n1: W138 materializer face already present (idempotent skip)")
else:
    face_anchor = '''        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim'''
    assert n1.count(face_anchor) == 1, "n1: face insertion anchor"
    face = io.open(r".codely-cli\scratch_w138_face.txt", encoding="utf-8").read()
    assert face.lstrip().startswith("# --- W138 materializer face"), "face sanity"
    assert "_set_wave(138)" in face, "face wave sanity"
    n1 = n1.replace(face_anchor,
        '''        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
''' + face + '''    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim''')
    print("n1: W138 materializer face inserted")

# --- 2c. selftest prose face after the W137 prose ---
if 'law sec.4 W138 row, r743 bm-a] ' in n1:
    print("n1: W138 prose face already present (idempotent skip)")
else:
    prose_anchor = 'W137 row, r742 bm-a] "' + chr(10) + '          "+ T-141 s2 "'
    assert n1.count(prose_anchor) == 1, "n1: prose anchor"
    prose_new = '''W137 row, r742 bm-a] "
          "+ W138 materializer face [same guard set, dep=W17..W137 outputs "
          "ALL PRESENT (landed net chain head 697,411 = W137 bm-a r743 "
          "one-pass, §7 backfill same commit; K=299,320 merged pool; ZERO "
          "in-flight upstream seats, clean precondition freeze window), "
          "ONE HUNDRED-AND-TWENTY-EIGHTH ENGINE-OWNED WAVE BY MACHINE-DERIVE "
          "(engine_owner rows 127 + candidate) bm-a's fifty-fourth owned "
          "claim per machine-derive (engine_owner==bm-a rows 53 + "
          "candidate), engine_owner=bm-a per engine de-throttle law "
          "O-20261001-2355 sec.2 own-continuous-series (wave 138 = first "
          "FREE number after the REGISTERED W137 row bm-a r742 freeze "
          "f9e4ec5d2, SINGLE STATE zero seat gap W2..W137 all registered; "
          "seat published=reserved MSG-2026-10-05-211x-bma-w138-seat "
          "pushed to origin 0bf01ef64 BEFORE this freeze, r565 law "
          "(payload = seat MSG + pre-seat probe + probe receipt, "
          "deletion-set EMPTY; pre-freeze push raced origin forward 3 "
          "commits = r524 behind-signal (bm-b r745 same-window wave), "
          "merge-mode clean auto-merge closeout, delivery 576b22603), "
          "A = ARITHMETIC CONTINUATION from the registered W137 A tail "
          "(319_004..321_003 CLEAN hops=0) + B = ARITHMETIC CONTINUATION "
          "from the registered W137 B tail (94_201..94_400 CLEAN hops=0 "
          "double-CLEAN window; the W137 honest 12-hop forward walk "
          "landed past the contiguous registered band mass 70_001..94_000, "
          "clean by construction; cross-window convergence with the r742 "
          "W137 gate-tail projection re-derived; ADMIT receipt "
          "results/_r743bma_w138_band_gate.py; W139+ projection per "
          "this window gate: A 321_004..323_003 CLEAN / B first-clean "
          "94_401..94_600 CLEAN hops=0 double-CLEAN) disclosed "
          "for the next freezer; not a "
          "free pick -- R250), law sec.4 "
          "W138 row, r743 bm-a] "
          "+ T-141 s2 "'''
    n1 = n1.replace(prose_anchor, prose_new)
    print("n1: W138 prose face inserted")

io.open(n1_path, "w", encoding="utf-8", newline="\n").write(n1)
print("PART 2 DONE (n1 WAVE_CONFIGS[138] + face + prose)")
