# -*- coding: utf-8 -*-
"""r742 bm-a W137 registry insertion PART 2: perpetual_faces_n1.py
WAVE_CONFIGS[137] + materializer face + selftest prose face.
Consumes .codely-cli/scratch_w137_face.txt (transformed by part 1).
Idempotent guards; needle-asserted (r735/r739 lineage)."""
import io

n1_path = r"scripts\perpetual_faces_n1.py"
n1 = io.open(n1_path, encoding="utf-8").read()

# --- 2a. WAVE_CONFIGS[137] after entry 136 ---
if '"batch": "PERPETUAL-N1-W137"' in n1:
    print("n1: WAVE_CONFIGS[137] already present (idempotent skip)")
else:
    wc_anchor = '''                            "shard_subdir": "n1_w136", "out_name": "n1_w136_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    assert n1.count(wc_anchor) == 1, "n1: WAVE_CONFIGS W136 entry anchor"
    wc_new = '''                            "shard_subdir": "n1_w136", "out_name": "n1_w136_results.json",
                            "engine_owner": "bm-a"},
                       137: {"batch": "PERPETUAL-N1-W137",
                            "prereg": ("research/PERPETUAL_N1_W137_PREREG.md (wave-level frozen "
                                       "pre-run; design = frozen v1 null calibration verbatim, "
                                       "new seed bands only; ONE HUNDRED-AND-TWENTY-SEVENTH ENGINE-OWNED WAVE "
                                       "BY MACHINE-DERIVE (engine_owner rows 126 + candidate), "
                                       "own-series continuation per O-20261001-2355 sec.2 (first-free-"
                                       "number law after the REGISTERED W136 row bm-a r741 freeze "
                                       "7cafbc7ab, SINGLE STATE zero seat gap W2..W136 all "
                                       "registered; W136 finalize landed same-window r742, ledger "
                                       "head 695,211, merged pool K=297,120; seat published=reserved "
                                       "MSG-2026-10-05-202x-bma-w137-seat PUSHED to origin af1c3c267 "
                                       "BEFORE this freeze per r565 early-visibility law (payload = "
                                       "seat MSG + pre-seat probe + probe receipt; deletion-set EMPTY; "
                                       "pre-freeze push raced origin forward 2 commits = r524 "
                                       "behind-signal (bm-c r570 same-window wave), merge-mode "
                                       "zero-UU closeout, delivery d28d392ce); "
                                       "pre-seat probe and freeze-window band-gate runs derive "
                                       "identical, no fork face), "
                                       "engine_owner=bm-a, wave 137: "
                                       "A = arithmetic continuation from the registered W136 A tail "
                                       "(317_004..319_003 CLEAN hops=0) + B = FIRST-CLEAN window "
                                       "after the honest 12-hop forward walk past the registered "
                                       "W136 B tail (94_001..94_200 hops=12 non-rotational r587; "
                                       "cross-window convergence with the r741 W136 gate-tail "
                                       "projection re-derived; ADMIT receipt "
                                       "results/_r742bma_w137_band_gate.py; W138+ projection per this "
                                       "window gate: A 319_004..321_003 CLEAN / B first-clean "
                                       "94_201..94_400 CLEAN hops=0 double-CLEAN; W1..W136 "
                                       "finalize ALL LANDED (W136 finalize one-pass bm-a r742, §7 "
                                       "backfill same commit; net chain head 695,211, merged pool "
                                       "K=297,120) -- ZERO in-flight upstream seats, clean finalize "
                                       "chain precondition -- finalize merge loop still derives the "
                                       "wave set from registry keys at run time, FAIL-CLOSED r307 "
                                       "always on)"),
                            "a_seed_base": 317_004,        # law sec.4 W137 A: 317_004..319_003 (arithmetic continuation from the registered W136 A tail)
                            "b_exit_seed_base": 94_001,   # law sec.4 W137 B: 94_001..94_200 (FIRST-CLEAN after honest 12-hop forward walk past the registered W136 B tail, non-rotational r587)
                            "shard_subdir": "n1_w137", "out_name": "n1_w137_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    n1 = n1.replace(wc_anchor, wc_new)
    print("n1: WAVE_CONFIGS[137] inserted")

# --- 2b. materializer face insertion after the W136 face end ---
if "_set_wave(137)" in n1:
    print("n1: W137 materializer face already present (idempotent skip)")
else:
    face_anchor = '''        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim'''
    assert n1.count(face_anchor) == 1, "n1: face insertion anchor"
    face = io.open(r".codely-cli\scratch_w137_face.txt", encoding="utf-8").read()
    assert face.lstrip().startswith("# --- W137 materializer face"), "face sanity"
    assert "_set_wave(137)" in face, "face wave sanity"
    n1 = n1.replace(face_anchor,
        '''        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
''' + face + '''    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim''')
    print("n1: W137 materializer face inserted")

# --- 2c. selftest prose face after the W136 prose ---
if 'law sec.4 W137 row, r742 bm-a] ' in n1:
    print("n1: W137 prose face already present (idempotent skip)")
else:
    prose_anchor = 'W136 row, r741 bm-a] "\n          "+ T-141 s2 "'
    assert n1.count(prose_anchor) == 1, "n1: prose anchor"
    prose_new = '''W136 row, r741 bm-a] "
          "+ W137 materializer face [same guard set, dep=W17..W136 outputs "
          "ALL PRESENT (landed net chain head 695,211 = W136 bm-a r742 "
          "one-pass, §7 backfill same commit; K=297,120 merged pool; ZERO "
          "in-flight upstream seats, clean precondition freeze window), "
          "ONE HUNDRED-AND-TWENTY-SEVENTH ENGINE-OWNED WAVE BY MACHINE-DERIVE "
          "(engine_owner rows 126 + candidate) bm-a's fifty-third owned "
          "claim per machine-derive (engine_owner==bm-a rows 52 + "
          "candidate), engine_owner=bm-a per engine de-throttle law "
          "O-20261001-2355 sec.2 own-continuous-series (wave 137 = first "
          "FREE number after the REGISTERED W136 row bm-a r741 freeze "
          "7cafbc7ab, SINGLE STATE zero seat gap W2..W136 all registered; "
          "seat published=reserved MSG-2026-10-05-202x-bma-w137-seat "
          "pushed to origin af1c3c267 BEFORE this freeze, r565 law "
          "(payload = seat MSG + pre-seat probe + probe receipt, "
          "deletion-set EMPTY; pre-freeze push raced origin forward 2 "
          "commits = r524 behind-signal (bm-c r570 same-window wave), "
          "merge-mode zero-UU closeout, delivery d28d392ce), A = "
          "ARITHMETIC CONTINUATION from the registered W136 A tail "
          "(317_004..319_003 CLEAN hops=0) + B = FIRST-CLEAN window "
          "after the honest 12-hop forward walk past the registered "
          "W136 B tail (94_001..94_200 hops=12 non-rotational r587; "
          "cross-window convergence with the r741 W136 gate-tail "
          "projection re-derived; ADMIT receipt "
          "results/_r742bma_w137_band_gate.py; W138+ projection per "
          "this window gate: A 319_004..321_003 CLEAN / B first-clean "
          "94_201..94_400 CLEAN hops=0 double-CLEAN) disclosed "
          "for the next freezer; not a "
          "free pick -- R250), law sec.4 "
          "W137 row, r742 bm-a] "
          "+ T-141 s2 "'''
    n1 = n1.replace(prose_anchor, prose_new)
    print("n1: W137 prose face inserted")

io.open(n1_path, "w", encoding="utf-8", newline="\n").write(n1)
print("PART 2 DONE (n1 WAVE_CONFIGS[137] + face + prose)")
