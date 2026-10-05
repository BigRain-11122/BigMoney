# -*- coding: utf-8 -*-
"""r741 bm-a W136 registry insertion PART 2: perpetual_faces_n1.py
WAVE_CONFIGS[136] + materializer face + selftest prose face.
Consumes .codely-cli/scratch_w136_face.txt (transformed by part 1).
Idempotent guards; needle-asserted (r735/r739 lineage)."""
import io

n1_path = r"scripts\perpetual_faces_n1.py"
n1 = io.open(n1_path, encoding="utf-8").read()

# --- 2a. WAVE_CONFIGS[136] after entry 135 ---
if '"batch": "PERPETUAL-N1-W136"' in n1:
    print("n1: WAVE_CONFIGS[136] already present (idempotent skip)")
else:
    wc_anchor = '''                            "shard_subdir": "n1_w135", "out_name": "n1_w135_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    assert n1.count(wc_anchor) == 1, "n1: WAVE_CONFIGS W135 entry anchor"
    wc_new = '''                            "shard_subdir": "n1_w135", "out_name": "n1_w135_results.json",
                            "engine_owner": "bm-a"},
                       136: {"batch": "PERPETUAL-N1-W136",
                            "prereg": ("research/PERPETUAL_N1_W136_PREREG.md (wave-level frozen "
                                       "pre-run; design = frozen v1 null calibration verbatim, "
                                       "new seed bands only; ONE HUNDRED-AND-TWENTY-SIXTH ENGINE-OWNED WAVE "
                                       "BY MACHINE-DERIVE (engine_owner rows 125 + candidate), "
                                       "own-series continuation per O-20261001-2355 sec.2 (first-free-"
                                       "number law after the REGISTERED W135 row bm-a r740 freeze "
                                       "bc921896a, SINGLE STATE zero seat gap W2..W135 all "
                                       "registered; W135 finalize landed same-window r741, ledger "
                                       "head 693,011, merged pool K=294,920; seat published=reserved "
                                       "MSG-2026-10-05-1952-bma-w136-seat PUSHED to origin 20d0036dc "
                                       "BEFORE this freeze per r565 early-visibility law (payload = "
                                       "seat MSG + pre-seat probe + probe receipt; deletion-set EMPTY; "
                                       "pre-freeze push raced origin forward 1 commit = r524 "
                                       "behind-signal (bm-c r568 same-window wave), merge-mode "
                                       "zero-UU closeout, delivery 2564ba798); "
                                       "pre-seat probe and freeze-window band-gate runs derive "
                                       "identical, no fork face), "
                                       "engine_owner=bm-a, wave 136: "
                                       "A = arithmetic continuation from the registered W135 A tail "
                                       "(315_004..317_003 CLEAN hops=0) + B = arithmetic continuation "
                                       "from the registered W135 B tail (69_702..69_901 CLEAN hops=0 "
                                       "double-CLEAN window; cross-window convergence with the r740 "
                                       "W135 seat MSG-1933 W136+ projection re-derived; ADMIT receipt "
                                       "results/_r741bma_w136_band_gate.py; W137+ projection per this "
                                       "window gate: A 317_004..319_003 CLEAN / B first-clean "
                                       "94_001..94_200 hops=12 honest forward walk; W1..W135 "
                                       "finalize ALL LANDED (W135 finalize one-pass bm-a r741, §7 "
                                       "backfill same commit; net chain head 693,011, merged pool "
                                       "K=294,920) -- ZERO in-flight upstream seats, clean finalize "
                                       "chain precondition -- finalize merge loop still derives the "
                                       "wave set from registry keys at run time, FAIL-CLOSED r307 "
                                       "always on)"),
                            "a_seed_base": 315_004,        # law sec.4 W136 A: 315_004..317_003 (arithmetic continuation from the registered W135 A tail)
                            "b_exit_seed_base": 69_702,   # law sec.4 W136 B: 69_702..69_901 (arithmetic continuation from the registered W135 B tail, CLEAN hops=0 double-CLEAN window)
                            "shard_subdir": "n1_w136", "out_name": "n1_w136_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    n1 = n1.replace(wc_anchor, wc_new)
    print("n1: WAVE_CONFIGS[136] inserted")

# --- 2b. materializer face insertion after the W135 face end ---
if "_set_wave(136)" in n1:
    print("n1: W136 materializer face already present (idempotent skip)")
else:
    face_anchor = '''        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim'''
    assert n1.count(face_anchor) == 1, "n1: face insertion anchor"
    face = io.open(r".codely-cli\scratch_w136_face.txt", encoding="utf-8").read()
    assert face.lstrip().startswith("# --- W136 materializer face"), "face sanity"
    assert "_set_wave(136)" in face, "face wave sanity"
    n1 = n1.replace(face_anchor,
        '''        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
''' + face + '''    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim''')
    print("n1: W136 materializer face inserted")

# --- 2c. selftest prose face after the W135 prose ---
if 'law sec.4 W136 row, r741 bm-a] ' in n1:
    print("n1: W136 prose face already present (idempotent skip)")
else:
    prose_anchor = 'W135 row, r740 bm-a] "\n          "+ T-141 s2 "'
    assert n1.count(prose_anchor) == 1, "n1: prose anchor"
    prose_new = '''W135 row, r740 bm-a] "
          "+ W136 materializer face [same guard set, dep=W17..W135 outputs "
          "ALL PRESENT (landed net chain head 693,011 = W135 bm-a r741 "
          "one-pass, §7 backfill same commit; K=294,920 merged pool; ZERO "
          "in-flight upstream seats, clean precondition freeze window), "
          "ONE HUNDRED-AND-TWENTY-SIXTH ENGINE-OWNED WAVE BY MACHINE-DERIVE "
          "(engine_owner rows 125 + candidate) bm-a's fifty-second owned "
          "claim per machine-derive (engine_owner==bm-a rows 51 + "
          "candidate), engine_owner=bm-a per engine de-throttle law "
          "O-20261001-2355 sec.2 own-continuous-series (wave 136 = first "
          "FREE number after the REGISTERED W135 row bm-a r740 freeze "
          "bc921896a, SINGLE STATE zero seat gap W2..W135 all registered; "
          "seat published=reserved MSG-2026-10-05-1952-bma-w136-seat "
          "pushed to origin 20d0036dc BEFORE this freeze, r565 law "
          "(payload = seat MSG + pre-seat probe + probe receipt, "
          "deletion-set EMPTY; pre-freeze push raced origin forward 1 "
          "commit = r524 behind-signal (bm-c r568 same-window wave), "
          "merge-mode zero-UU closeout, delivery 2564ba798), A = "
          "ARITHMETIC CONTINUATION from the registered W135 A tail "
          "(315_004..317_003 CLEAN hops=0) + B = ARITHMETIC CONTINUATION "
          "from the registered W135 B tail (69_702..69_901 CLEAN hops=0 "
          "double-CLEAN window; cross-window convergence with the r740 "
          "W135 seat MSG-1933 W136+ projection re-derived; ADMIT receipt "
          "results/_r741bma_w136_band_gate.py; W137+ projection per "
          "this window gate: A 317_004..319_003 CLEAN / B first-clean "
          "94_001..94_200 CLEAN hops=12 honest forward walk) disclosed "
          "for the next freezer; not a "
          "free pick -- R250), law sec.4 "
          "W136 row, r741 bm-a] "
          "+ T-141 s2 "'''
    n1 = n1.replace(prose_anchor, prose_new)
    print("n1: W136 prose face inserted")

io.open(n1_path, "w", encoding="utf-8", newline="\n").write(n1)
print("PART 2 DONE (n1 WAVE_CONFIGS[136] + face + prose)")
