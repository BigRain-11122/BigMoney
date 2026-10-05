# -*- coding: utf-8 -*-
"""r732 bm-a W127 registry insertion: N1_BANDS row 127 (perpetual_faces.py)
+ WAVE_CONFIGS[127] + materializer face + selftest prose face
(perpetual_faces_n1.py). All insertions needle-asserted; idempotent guards."""
import io

def rep(src, pairs, tag):
    for old, new, expect in pairs:
        n = src.count(old)
        assert n == expect, f"{tag}: needle count={n} expect={expect}: {old[:60]!r}"
        src = src.replace(old, new)
    return src

# ============ 1. perpetual_faces.py N1_BANDS row 127 ============
pf_path = r"scripts\perpetual_faces.py"
pf_src = io.open(pf_path, encoding="utf-8").read()
if '127: {"a": (297_004, 299_003)' in pf_src:
    print("pf: row 127 already present (idempotent skip)")
else:
    w126_row = '''    126: {"a": (295_004, 297_003), "b_exit": (67_401, 67_600),
         "engine_owner": "bm-a"},
}'''
    assert pf_src.count(w126_row) == 1, "pf: W126 row + closing brace needle"
    w127_block = '''    126: {"a": (295_004, 297_003), "b_exit": (67_401, 67_600),
         "engine_owner": "bm-a"},
    # W127 (bm-a r732 freeze, seat MSG-2026-10-05-1548-bma-w127-seat
    # pre-pushed bef555332 r565 law; band gate ADMIT
    # results/_r732bma_w127_band_gate.json: A arithmetic continuation
    # 297_003+1 -> 297_004..299_003 CLEAN hops=0; B arithmetic continuation
    # 67_600+1 -> 67_601..67_800 CLEAN hops=0; dual-window derive parity
    # with pre-seat probe; scan face = SEED_REGISTRY 187 int values +
    # v1/W1 ext bands + N3-R1 used-seed band + probe cluster 95_000..95_003
    # + cross-face probe points 95_004/95_006 + lfc/options actuals +
    # N2/N4/N2-W15 probe points.
    # W128+ projection (gate-derived r732): A 299_004..301_003
    # CLEAN hops=0; B first-clean 68_001..68_200 hops=1 (refusal fact
    # cny_window_p1=68_000 upper-edge endpoint -> past-hit restart,
    # D-20261002-05 pin; next freezer must re-derive, never transcribe
    # r587 law).
    # NOT a re-pick (R250: W127 bands were never assigned).
    127: {"a": (297_004, 299_003), "b_exit": (67_601, 67_800),
         "engine_owner": "bm-a"},
}'''
    pf_src = pf_src.replace(w126_row, w127_block)
    io.open(pf_path, "w", encoding="utf-8", newline="\n").write(pf_src)
    print("pf: N1_BANDS row 127 inserted")

# ============ 2. perpetual_faces_n1.py ============
n1_path = r"scripts\perpetual_faces_n1.py"
n1 = io.open(n1_path, encoding="utf-8").read()

# --- 2a. WAVE_CONFIGS[127] after entry 126 ---
if '"batch": "PERPETUAL-N1-W127"' in n1:
    print("n1: WAVE_CONFIGS[127] already present (idempotent skip)")
else:
    wc_anchor = '''                            "shard_subdir": "n1_w126", "out_name": "n1_w126_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    assert n1.count(wc_anchor) == 1, "n1: WAVE_CONFIGS W126 entry anchor"
    wc_new = '''                            "shard_subdir": "n1_w126", "out_name": "n1_w126_results.json",
                            "engine_owner": "bm-a"},
                       127: {"batch": "PERPETUAL-N1-W127",
                            "prereg": ("research/PERPETUAL_N1_W127_PREREG.md (wave-level frozen "
                                       "pre-run; design = frozen v1 null calibration verbatim, "
                                       "new seed bands only; ONE HUNDRED-AND-SEVENTEENTH ENGINE-OWNED WAVE "
                                       "BY MACHINE-DERIVE (engine_owner rows 116 + candidate), "
                                       "own-series continuation per O-20261001-2355 sec.2 (first-free-"
                                       "number law after the REGISTERED W126 row bm-a r731 freeze "
                                       "db9da0e92, SINGLE STATE zero seat gap W2..W126 all "
                                       "registered; W126 finalize landed same-window r732, ledger "
                                       "head 673,211, merged pool K=275,120; seat published=reserved "
                                       "MSG-2026-10-05-1548-bma-w127-seat PUSHED to origin bef555332 "
                                       "BEFORE this freeze per r565 early-visibility law; first "
                                       "push raced origin forward 3 commits = r524 behind-signal, "
                                       "merge-mode zero-UU closeout, delivery b78dc4cc4; pre-seat "
                                       "probe and freeze-window band-gate runs derive identical, "
                                       "no fork face; payload = seat MSG + probe + probe receipt, "
                                       "deletion-set EMPTY, rev.A = only published faces), "
                                       "engine_owner=bm-a, wave 127: "
                                       "A = arithmetic continuation from the registered W126 A tail "
                                       "(297_004..299_003 CLEAN hops=0) + B = arithmetic "
                                       "continuation from the registered W126 B tail "
                                       "(67_601..67_800 CLEAN hops=0; cross-window convergence "
                                       "with the r731 W126 gate-tail W127+ projection re-derived; "
                                       "ADMIT receipt results/_r732bma_w127_band_gate.py; W128+ "
                                       "projection per this window gate: A 299_004..301_003 CLEAN / "
                                       "B first-clean 68_001..68_200 hops=1 (refusal fact "
                                       "cny_window_p1=68_000 upper-edge endpoint, past-hit restart "
                                       "per D-20261002-05 pin); W1..W126 "
                                       "finalize ALL LANDED (W126 finalize one-pass bm-a r732, §7 "
                                       "backfill same commit; net chain head 673,211, merged pool "
                                       "K=275,120) -- ZERO in-flight upstream seats, clean finalize "
                                       "chain precondition -- finalize merge loop still derives the "
                                       "wave set from registry keys at run time, FAIL-CLOSED "
                                       "r307 always on)"),
                            "a_seed_base": 297_004,        # law sec.4 W127 A: 297_004..299_003 (arithmetic continuation from the registered W126 A tail)
                            "b_exit_seed_base": 67_601,   # law sec.4 W127 B: 67_601..67_800 (arithmetic continuation from the registered W126 B tail, CLEAN hops=0)
                            "shard_subdir": "n1_w127", "out_name": "n1_w127_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    n1 = n1.replace(wc_anchor, wc_new)
    print("n1: WAVE_CONFIGS[127] inserted")

# --- 2b. materializer face: transform the extracted W126 block ---
if "_set_wave(127)" in n1:
    print("n1: W127 materializer face already present (idempotent skip)")
    face = None
else:
    face = io.open(r".codely-cli\scratch_w126_face.txt", encoding="utf-8").read()
    n_w126 = face.count("W126"); n_w125 = face.count("W125")
    face = face.replace("W126", "W127")
    face = face.replace("W125", "W126")
    assert face.count("W127") == n_w126 and face.count("W126") == n_w125, "blanket count check"
    specific = [
        # long receipt/seat needles FIRST (substring-order law: _r731bma_w126_band_gate.py contains "w126_b")
        ("_r731bma_w126_band_gate.py", "_r732bma_w127_band_gate.py", 1),
        ("MSG-2026-10-05-1528-bma-w126-seat", "MSG-2026-10-05-1548-bma-w127-seat", 1),
        ("7d70b01fd", "bef555332", 1),
        ("77cd1f6ee", "db9da0e92", 1),
        ("4a77367d3", "b78dc4cc4", 1),
        ("w126_a", "w127_a", 8), ("w126_b", "w127_b", 8),
        ("arith_a126", "arith_a127", 2), ("arith_b126", "arith_b127", 2),
        ("n3r1_used126", "n3r1_used127", 3),
        ("n1w126", "n1w127", 2), ("n1_w126", "n1_w127", 2),
        ("W126 finalize one-pass bm-a r731", "W126 finalize one-pass bm-a r732", 1),
        ("= W126 bm-a r731 one-pass", "= W126 bm-a r732 one-pass", 1),
        ("(r731 bm-a freeze", "(r732 bm-a freeze", 1),
        ("law sec.4 W127 row, r731", "law sec.4 W127 row, r732", 1),
        ("ONE HUNDRED-AND-SIXTEENTH", "ONE HUNDRED-AND-SEVENTEENTH", 1),
        ("forty-second", "forty-third", 1),
        ("rows 41 + candidate", "rows 42 + candidate", 1),
        ("rows 115 + candidate", "rows 116 + candidate", 1),
        ("net chain head 671,011", "net chain head 673,211", 2),
        ("K=272,920", "K=275,120", 1),
        ("the r730 W126 gate-tail", "the r731 W126 gate-tail", 1),
        ("== 295_004 == 295_003 + 1", "== 297_004 == 297_003 + 1", 1),
        ("set(range(295_004, 297_004))", "set(range(297_004, 299_004))", 1),
        ("== 67_401 == 67_400 + 1", "== 67_601 == 67_600 + 1", 1),
        ("set(range(67_401, 67_601))", "set(range(67_601, 67_801))", 1),
        ("WAVE_CONFIGS[126]", "WAVE_CONFIGS[127]", 5),
        ("pf.N1_BANDS[126]", "pf.N1_BANDS[127]", 3),
        ("_set_wave(126)", "_set_wave(127)", 1),
        ("if w < 126", "if w < 127", 3),
        ("range(17, 126)", "range(17, 127)", 1),
        ("range(16, 126)", "range(16, 127)", 1),
    ]
    face = rep(face, specific, "face")
    old_parity = '''        # registered row parity (r307 pinned constants, recent estate)
        assert pf.N1_BANDS[122] == {"a": (287_004, 289_003),
                                    "b_exit": (66_201, 66_400),
                                    "engine_owner": "bm-a"}, \\
            "registered W122 row parity drift (r307; bm-a r727)"
        assert pf.N1_BANDS[123] == {"a": (289_004, 291_003),
                                    "b_exit": (66_401, 66_600),
                                    "engine_owner": "bm-a"}, \\
            "registered W123 row parity drift (r307; bm-a r728)"
        assert pf.N1_BANDS[124] == {"a": (291_004, 293_003),
                                    "b_exit": (66_601, 66_800),
                                    "engine_owner": "bm-a"}, \\
            "registered W124 row parity drift (r307; bm-a r729)"
        assert pf.N1_BANDS[125] == {"a": (293_004, 295_003),
                                    "b_exit": (67_201, 67_400),
                                    "engine_owner": "bm-a"}, \\
            "registered W126 row parity drift (r307; bm-a r730)"'''
    new_parity = '''        # registered row parity (r307 pinned constants, recent estate)
        assert pf.N1_BANDS[123] == {"a": (289_004, 291_003),
                                    "b_exit": (66_401, 66_600),
                                    "engine_owner": "bm-a"}, \\
            "registered W123 row parity drift (r307; bm-a r728)"
        assert pf.N1_BANDS[124] == {"a": (291_004, 293_003),
                                    "b_exit": (66_601, 66_800),
                                    "engine_owner": "bm-a"}, \\
            "registered W124 row parity drift (r307; bm-a r729)"
        assert pf.N1_BANDS[125] == {"a": (293_004, 295_003),
                                    "b_exit": (67_201, 67_400),
                                    "engine_owner": "bm-a"}, \\
            "registered W125 row parity drift (r307; bm-a r730)"
        assert pf.N1_BANDS[126] == {"a": (295_004, 297_003),
                                    "b_exit": (67_401, 67_600),
                                    "engine_owner": "bm-a"}, \\
            "registered W126 row parity drift (r307; bm-a r731)"'''
    assert face.count(old_parity) == 1, "face: row-parity post-blanket needle"
    face = face.replace(old_parity, new_parity)
    io.open(r".codely-cli\scratch_w127_face.txt", "w", encoding="utf-8", newline="\n").write(face)
    print("n1: W127 face block transformed")

    # --- 2c. insert face after W126 block end, before T-141 s2 lane face ---
    face_anchor = '''        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim'''
    assert n1.count(face_anchor) == 1, "n1: face insertion anchor"
    n1 = n1.replace(face_anchor,
        '''        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
''' + face + '''    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim''')
    print("n1: W127 materializer face inserted")

# --- 2d. selftest prose face after the W126 prose ---
if 'law sec.4 W127 row, r732 bm-a] ' in n1:
    print("n1: W127 prose face already present (idempotent skip)")
else:
    prose_anchor = '''          "r731 bm-a] "
          "+ T-141 s2 "'''
    assert n1.count(prose_anchor) == 1, "n1: prose anchor"
    prose_new = '''          "r731 bm-a] "
          "+ W127 materializer face [same guard set, dep=W17..W126 outputs "
          "ALL PRESENT (landed net chain head 673,211 = W126 bm-a r732 "
          "one-pass, §7 backfill same commit; K=275,120 merged pool; ZERO "
          "in-flight upstream seats, clean precondition freeze window), "
          "ONE HUNDRED-AND-SEVENTEENTH ENGINE-OWNED WAVE BY MACHINE-DERIVE "
          "(engine_owner rows 116 + candidate) bm-a's forty-third owned "
          "claim per machine-derive (engine_owner==bm-a rows 42 + "
          "candidate), engine_owner=bm-a per engine de-throttle law "
          "O-20261001-2355 sec.2 own-continuous-series (wave 127 = first "
          "FREE number after the REGISTERED W126 row bm-a r731 freeze "
          "db9da0e92, SINGLE STATE zero seat gap W2..W126 all registered; "
          "seat published=reserved MSG-2026-10-05-1548-bma-w127-seat "
          "pushed to origin bef555332 BEFORE this freeze, r565 law; "
          "first push raced origin forward 3 commits = r524 "
          "behind-signal, merge-mode zero-UU closeout, delivery "
          "b78dc4cc4; payload = seat MSG + probe + probe receipt "
          "deletion-set EMPTY, rev.A = only published faces), BOTH SIDES "
          "ARITHMETIC CONTINUATION from the registered W126 tails (A "
          "297_004..299_003 CLEAN hops=0 + B 67_601..67_800 CLEAN hops=0, "
          "zero-jump two-reading-identical face, cross-window convergence "
          "with the r731 W126 gate-tail W127+ projection re-derived; "
          "ADMIT receipt results/_r732bma_w127_band_gate.py; W128+ "
          "projection per this window gate: A 299_004..301_003 CLEAN / "
          "B first-clean 68_001..68_200 hops=1 (refusal fact "
          "cny_window_p1=68_000 upper-edge endpoint, past-hit restart "
          "per D-20261002-05 pin) disclosed for the next freezer; not a "
          "free pick -- R250), law sec.4 W127 row, r732 bm-a] "
          "+ T-141 s2 "'''
    n1 = n1.replace(prose_anchor, prose_new)
    print("n1: W127 prose face inserted")

io.open(n1_path, "w", encoding="utf-8", newline="\n").write(n1)
print("ALL INSERTIONS DONE")
