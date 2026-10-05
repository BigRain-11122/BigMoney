# -*- coding: utf-8 -*-
"""r744 bm-a W139 registry insertion PART 2: perpetual_faces_n1.py
WAVE_CONFIGS[139] + materializer face + selftest prose face.
Consumes .codely-cli/scratch_w139_face.txt (transformed by part 1).
Idempotent guards; needle-asserted (r735/r739/r742 lineage).
r740 law: part2 runs strictly AFTER part1 (serial; face file must exist)."""
import io

n1_path = r"scripts\perpetual_faces_n1.py"
n1 = io.open(n1_path, encoding="utf-8").read()

# --- 2a. WAVE_CONFIGS[139] after entry 138 ---
if '"batch": "PERPETUAL-N1-W139"' in n1:
    print("n1: WAVE_CONFIGS[139] already present (idempotent skip)")
else:
    wc_anchor = '''                            "shard_subdir": "n1_w138", "out_name": "n1_w138_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    assert n1.count(wc_anchor) == 1, "n1: WAVE_CONFIGS W138 entry anchor"
    wc_new = '''                            "shard_subdir": "n1_w138", "out_name": "n1_w138_results.json",
                            "engine_owner": "bm-a"},
                       139: {"batch": "PERPETUAL-N1-W139",
                            "prereg": ("research/PERPETUAL_N1_W139_PREREG.md (wave-level frozen "
                                       "pre-run; design = frozen v1 null calibration verbatim, "
                                       "new seed bands only; ONE HUNDRED-AND-TWENTY-NINTH ENGINE-OWNED WAVE "
                                       "BY MACHINE-DERIVE (engine_owner rows 128 + candidate), "
                                       "own-series continuation per O-20261001-2355 sec.2 (first-free-"
                                       "number law after the REGISTERED W138 row bm-a r743 freeze "
                                       "6798a1e5f, SINGLE STATE zero seat gap W2..W138 all "
                                       "registered; W138 finalize landed same-window r744, ledger "
                                       "head 699,611, merged pool K=301,520; seat published=reserved "
                                       "MSG-2026-10-05-213x-bma-w139-seat PUSHED to origin 7e1fc08d0 "
                                       "BEFORE this freeze per r565 early-visibility law (payload = "
                                       "seat MSG + pre-seat probe + probe receipt; deletion-set EMPTY; "
                                       "pre-freeze push raced origin forward 7 commits = r524 "
                                       "behind-signal (bm-b r746 same-window wave), merge-mode "
                                       "clean auto-merge closeout, delivery 39ec08fa0); "
                                       "pre-seat probe and freeze-window band-gate runs derive "
                                       "identical, no fork face), "
                                       "engine_owner=bm-a, wave 139: "
                                       "A = arithmetic continuation from the registered W138 A tail "
                                       "(321_004..323_003 CLEAN hops=0) + B = arithmetic continuation "
                                       "from the registered W138 B tail (94_401..94_600 CLEAN hops=0 "
                                       "double-CLEAN continuation window; the W137 honest 12-hop "
                                       "forward walk landed past the contiguous registered band "
                                       "mass 70_001..94_000 and the W138 zero-hop continuation "
                                       "extended it to 94_400, clean by construction; cross-window "
                                       "convergence with the r743 W138 gate-tail projection "
                                       "re-derived; ADMIT receipt "
                                       "results/_r744bma_w139_band_gate.py; W140+ projection per this "
                                       "window gate: A 323_004..325_003 CLEAN / B first-clean "
                                       "94_601..94_800 CLEAN hops=0 double-CLEAN; W1..W138 "
                                       "finalize ALL LANDED (W138 finalize one-pass bm-a r744, §7 "
                                       "backfill same commit; net chain head 699,611, merged pool "
                                       "K=301,520) -- ZERO in-flight upstream seats, clean finalize "
                                       "chain precondition -- finalize merge loop still derives the "
                                       "wave set from registry keys at run time, FAIL-CLOSED r307 "
                                       "always on)"),
                            "a_seed_base": 321_004,        # law sec.4 W139 A: 321_004..323_003 (arithmetic continuation from the registered W138 A tail)
                            "b_exit_seed_base": 94_401,   # law sec.4 W139 B: 94_401..94_600 (arithmetic continuation from the registered W138 B tail, double-CLEAN continuation window, clean by construction)
                            "shard_subdir": "n1_w139", "out_name": "n1_w139_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    n1 = n1.replace(wc_anchor, wc_new)
    print("n1: WAVE_CONFIGS[139] inserted")

# --- 2b. materializer face insertion after the W138 face end ---
if "_set_wave(139)" in n1:
    print("n1: W139 materializer face already present (idempotent skip)")
else:
    face_anchor = '''        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim'''
    assert n1.count(face_anchor) == 1, "n1: face insertion anchor"
    face = io.open(r".codely-cli\scratch_w139_face.txt", encoding="utf-8").read()
    assert face.lstrip().startswith("# --- W139 materializer face"), "face sanity"
    assert "_set_wave(139)" in face, "face wave sanity"
    n1 = n1.replace(face_anchor,
        '''        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
''' + face + '''    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim''')
    print("n1: W139 materializer face inserted")

# --- 2c. selftest prose face after the W138 prose ---
if 'law sec.4 W139 row, r744 bm-a] ' in n1:
    print("n1: W139 prose face already present (idempotent skip)")
else:
    prose_anchor = 'W138 row, r743 bm-a] "' + chr(10) + '          "+ T-141 s2 "'
    assert n1.count(prose_anchor) == 1, "n1: prose anchor"
    prose_new = '''W138 row, r743 bm-a] "
          "+ W139 materializer face [same guard set, dep=W17..W138 outputs "
          "ALL PRESENT (landed net chain head 699,611 = W138 bm-a r744 "
          "one-pass, §7 backfill same commit; K=301,520 merged pool; ZERO "
          "in-flight upstream seats, clean precondition freeze window), "
          "ONE HUNDRED-AND-TWENTY-NINTH ENGINE-OWNED WAVE BY MACHINE-DERIVE "
          "(engine_owner rows 128 + candidate) bm-a's fifty-fifth owned "
          "claim per machine-derive (engine_owner==bm-a rows 54 + "
          "candidate), engine_owner=bm-a per engine de-throttle law "
          "O-20261001-2355 sec.2 own-continuous-series (wave 139 = first "
          "FREE number after the REGISTERED W138 row bm-a r743 freeze "
          "6798a1e5f, SINGLE STATE zero seat gap W2..W138 all registered; "
          "seat published=reserved MSG-2026-10-05-213x-bma-w139-seat "
          "pushed to origin 7e1fc08d0 BEFORE this freeze, r565 law "
          "(payload = seat MSG + pre-seat probe + probe receipt, "
          "deletion-set EMPTY; pre-freeze push raced origin forward 7 "
          "commits = r524 behind-signal (bm-b r746 same-window wave), "
          "merge-mode clean auto-merge closeout, delivery 39ec08fa0), "
          "A = ARITHMETIC CONTINUATION from the registered W138 A tail "
          "(321_004..323_003 CLEAN hops=0) + B = ARITHMETIC CONTINUATION "
          "from the registered W138 B tail (94_401..94_600 CLEAN hops=0 "
          "double-CLEAN continuation window; the W137 honest 12-hop "
          "forward walk landed past the contiguous registered band mass "
          "70_001..94_000 and the W138 zero-hop continuation extended it "
          "to 94_400, clean by construction; cross-window convergence "
          "with the r743 W138 gate-tail projection re-derived; ADMIT "
          "receipt results/_r744bma_w139_band_gate.py; W140+ projection "
          "per this window gate: A 323_004..325_003 CLEAN / B first-clean "
          "94_601..94_800 CLEAN hops=0 double-CLEAN) disclosed "
          "for the next freezer; not a "
          "free pick -- R250), law sec.4 "
          "W139 row, r744 bm-a] "
          "+ T-141 s2 "'''
    n1 = n1.replace(prose_anchor, prose_new)
    print("n1: W139 prose face inserted")

io.open(n1_path, "w", encoding="utf-8", newline="\n").write(n1)
print("PART 2 DONE (n1 WAVE_CONFIGS[139] + face + prose)")
