# -*- coding: utf-8 -*-
"""r737 bm-a W132 registry insertion: N1_BANDS row 132 (perpetual_faces.py)
+ WAVE_CONFIGS[132] + materializer face + selftest prose face
(perpetual_faces_n1.py). All insertions needle-asserted; idempotent guards.
Bloodline: r736 _r736bma_w131_registry_insert.py verbatim + W132 facts
(double-CLEAN window: A = arithmetic continuation from the registered W131
A tail 307_003+1, CLEAN hops=0; B = arithmetic continuation from the
registered W131 B tail 68_901+1, CLEAN hops=0).
r735 codegen pit laws enforced: (1) all new-block assert messages
single-line or parenthesized; (2) rep() expects measured on
post-prior-replacement text (measurement passes results/_r737bma_w132_measure.py
+ _r737bma_w132_measure2.py printed every count verbatim before this
script was written). Cosmetic drift fix disclosed: the face-header
"wave 129 = first free number" prose line (propagated typo since the
W126/W127-era faces) is corrected to wave 132 in this face -- comment-only
face, zero functional impact."""
import io

def rep(src, pairs, tag):
    for old, new, expect in pairs:
        n = src.count(old)
        assert n == expect, f"{tag}: needle count={n} expect={expect}: {old[:60]!r}"
        src = src.replace(old, new)
    return src

# ============ 0. transform the extracted W131 face -> W132 face ============
face = io.open(r".codely-cli\scratch_w131_face_source.txt", encoding="utf-8").read()

# --- 0a. blanket wave-number shift FIRST (uppercase; then verified needles) ---
n_w131 = face.count("W131"); n_w130 = face.count("W130"); n_w129 = face.count("W129")
face = face.replace("W131", "W132")
face = face.replace("W130", "W131")
face = face.replace("W129", "W130")
assert face.count("W132") == n_w131 and face.count("W131") == n_w130 \
    and face.count("W130") == n_w129 and face.count("W129") == 0, \
    "blanket count check"

# --- 0b. A/B-block seed-value needles (arithmetic continuation from W131 tails) ---
face = rep(face, [
    ("== 305_004 == 305_003 + 1", "== 307_004 == 307_003 + 1", 1),
    ("set(range(305_004, 307_004))", "set(range(307_004, 309_004))", 1),
    ("== 68_702 == 68_701 + 1", "== 68_902 == 68_901 + 1", 1),
    ("set(range(68_702, 68_902))", "set(range(68_902, 69_102))", 1),
    ("arith_a131", "arith_a132", 2),
    ("arith_b131", "arith_b132", 2),
], "face-0b")

# --- 0c. specific needles (counts measured post-0a/0b by the measurement
#     passes results/_r737bma_w132_measure{,2}.py; the band-gate receipt
#     needle runs FIRST because it carries a w131_b substring, consuming
#     the 9th raw hit -- substring-order law; the parity block runs LAST
#     because its added rows carry W-numbers) ---
specific = [
    # receipt/seat needles FIRST (substring-order law)
    ("_r736bma_w131_band_gate.py", "_r737bma_w132_band_gate.py", 1),
    ("MSG-2026-10-05-1726-bma-w131-seat", "MSG-2026-10-05-1755-bma-w132-seat", 1),
    ("bm-a r735 freeze 0b8b308db", "bm-a r736 freeze 8cd6667e8", 1),
    ("fde20e3a1", "9c7e85e7f", 1),
    ("d09d5fe6a", "6e0b0c43f", 1),
    ("(bm-c r559 same-window", "(bm-c r560 same-window", 1),
    ("(r736 bm-a freeze", "(r737 bm-a freeze", 1),
    ("W131 finalize one-pass bm-a r736", "W131 finalize one-pass bm-a r737", 1),
    ("= W131 bm-a r736 one-pass", "= W131 bm-a r737 one-pass", 1),
    ("net chain head 682,011", "net chain head 684,211", 2),
    ("K=283,920", "K=286,120", 1),
    ("r735 W131 gate-tail", "r736 W131 seat MSG-1726 tail", 1),
    ("law sec.4 W132 row, r736", "law sec.4 W132 row, r737", 1),
    ("ONE HUNDRED-AND-TWENTY-FIRST", "ONE HUNDRED-AND-TWENTY-SECOND", 1),
    ("forty-seventh", "forty-eighth", 1),
    ("wave 129 = first free number", "wave 132 = first free number", 1),
    ("rows 46 + candidate", "rows 47 + candidate", 1),
    ("rows 120 + candidate", "rows 121 + candidate", 1),
    ("below 131 composes", "below 132 composes", 1),
    ("WAVE_CONFIGS[131]", "WAVE_CONFIGS[132]", 5),
    ("pf.N1_BANDS[131]", "pf.N1_BANDS[132]", 3),
    ("_set_wave(131)", "_set_wave(132)", 1),
    ("if w < 131", "if w < 132", 3),
    ("range(17, 131)", "range(17, 132)", 1),
    ("range(16, 131)", "range(16, 132)", 1),
    ("w131_a", "w132_a", 8),
    ("w131_b", "w132_b", 8),  # 9th raw hit = "_r736bma_w131_band_gate.py" substring, consumed by the receipt needle above (substring-order law)
    ("n3r1_used131", "n3r1_used132", 3),
    ("n1w131", "n1w132", 2), ("n1_w131", "n1_w132", 2),
]
face = rep(face, specific, "face")

# --- 0e. registered row parity block shift LAST (W127..W130 -> W128..W131) ---
old_parity = '''assert pf.N1_BANDS[127] == {"a": (297_004, 299_003),
                                    "b_exit": (67_601, 67_800),
                                    "engine_owner": "bm-a"}, \\
            "registered W127 row parity drift (r307; bm-a r732)"
        assert pf.N1_BANDS[128] == {"a": (299_004, 301_003),
                                    "b_exit": (68_001, 68_200),
                                    "engine_owner": "bm-a"}, \\
            "registered W128 row parity drift (r307; bm-a r733)"
        assert pf.N1_BANDS[129] == {"a": (301_004, 303_003),
                                    "b_exit": (68_201, 68_400),
                                    "engine_owner": "bm-a"}, \\
            "registered W130 row parity drift (r307; bm-a r734)"
        assert pf.N1_BANDS[130] == {"a": (303_004, 305_003),
                                    "b_exit": (68_502, 68_701),
                                    "engine_owner": "bm-a"}, \\
            "registered W131 row parity drift (r307; bm-a r735)"'''
new_parity = '''assert pf.N1_BANDS[128] == {"a": (299_004, 301_003),
                                    "b_exit": (68_001, 68_200),
                                    "engine_owner": "bm-a"}, \\
            "registered W128 row parity drift (r307; bm-a r733)"
        assert pf.N1_BANDS[129] == {"a": (301_004, 303_003),
                                    "b_exit": (68_201, 68_400),
                                    "engine_owner": "bm-a"}, \\
            "registered W129 row parity drift (r307; bm-a r734)"
        assert pf.N1_BANDS[130] == {"a": (303_004, 305_003),
                                    "b_exit": (68_502, 68_701),
                                    "engine_owner": "bm-a"}, \\
            "registered W130 row parity drift (r307; bm-a r735)"
        assert pf.N1_BANDS[131] == {"a": (305_004, 307_003),
                                    "b_exit": (68_702, 68_901),
                                    "engine_owner": "bm-a"}, \\
            "registered W131 row parity drift (r307; bm-a r736)"'''
assert face.count(old_parity) == 1, "face: row-parity block needle"
face = face.replace(old_parity, new_parity)

io.open(r".codely-cli\scratch_w132_face.txt", "w", encoding="utf-8", newline="\n").write(face)
print("face: W132 block transformed")

# ============ 1. perpetual_faces.py N1_BANDS row 132 ============
pf_path = r"scripts\perpetual_faces.py"
pf_src = io.open(pf_path, encoding="utf-8").read()
if '132: {"a": (307_004, 309_003)' in pf_src:
    print("pf: row 132 already present (idempotent skip)")
else:
    w131_row = '''    131: {"a": (305_004, 307_003), "b_exit": (68_702, 68_901),
         "engine_owner": "bm-a"},
}'''
    assert pf_src.count(w131_row) == 1, "pf: W131 row + closing brace needle"
    w132_block = '''    131: {"a": (305_004, 307_003), "b_exit": (68_702, 68_901),
         "engine_owner": "bm-a"},
    # W132 (bm-a r737 freeze, seat MSG-2026-10-05-1755-bma-w132-seat
    # pushed to origin 9c7e85e7f pre-freeze r565 law; band gate ADMIT
    # results/_r737bma_w132_band_gate.json: double-CLEAN window --
    # A arithmetic continuation 307_003+1 -> 307_004..309_003
    # CLEAN hops=0; B arithmetic continuation 68_901+1 ->
    # 68_902..69_101 CLEAN hops=0; dual-window derive parity with
    # pre-seat probe; scan face = SEED_REGISTRY 187 int values +
    # v1/W1 ext bands + N3-R1 used-seed band + probe cluster
    # 95_000..95_003 + cross-face probe points 95_004/95_006 +
    # lfc/options actuals + N2/N4/N2-W15 probe points.
    # W133+ projection (gate-derived r737): A 309_004..311_003
    # CLEAN hops=0; B 69_102..69_301 CLEAN hops=0 (next freezer
    # must re-derive, never transcribe r587 law).
    # NOT a re-pick (R250: W132 bands were never assigned).
    132: {"a": (307_004, 309_003), "b_exit": (68_902, 69_101),
         "engine_owner": "bm-a"},
}'''
    pf_src = pf_src.replace(w131_row, w132_block)
    io.open(pf_path, "w", encoding="utf-8", newline="\n").write(pf_src)
    print("pf: N1_BANDS row 132 inserted")

# ============ 2. perpetual_faces_n1.py ============
n1_path = r"scripts\perpetual_faces_n1.py"
n1 = io.open(n1_path, encoding="utf-8").read()

# --- 2a. WAVE_CONFIGS[132] after entry 131 ---
if '"batch": "PERPETUAL-N1-W132"' in n1:
    print("n1: WAVE_CONFIGS[132] already present (idempotent skip)")
else:
    wc_anchor = '''                            "shard_subdir": "n1_w131", "out_name": "n1_w131_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    assert n1.count(wc_anchor) == 1, "n1: WAVE_CONFIGS W131 entry anchor"
    wc_new = '''                            "shard_subdir": "n1_w131", "out_name": "n1_w131_results.json",
                            "engine_owner": "bm-a"},
                       132: {"batch": "PERPETUAL-N1-W132",
                            "prereg": ("research/PERPETUAL_N1_W132_PREREG.md (wave-level frozen "
                                       "pre-run; design = frozen v1 null calibration verbatim, "
                                       "new seed bands only; ONE HUNDRED-AND-TWENTY-SECOND ENGINE-OWNED WAVE "
                                       "BY MACHINE-DERIVE (engine_owner rows 121 + candidate), "
                                       "own-series continuation per O-20261001-2355 sec.2 (first-free-"
                                       "number law after the REGISTERED W131 row bm-a r736 freeze "
                                       "8cd6667e8, SINGLE STATE zero seat gap W2..W131 all "
                                       "registered; W131 finalize landed same-window r737, ledger "
                                       "head 684,211, merged pool K=286,120; seat published=reserved "
                                       "MSG-2026-10-05-1755-bma-w132-seat PUSHED to origin 9c7e85e7f "
                                       "BEFORE this freeze per r565 early-visibility law (payload = "
                                       "seat MSG + pre-seat probe + probe receipt; deletion-set EMPTY; "
                                       "first push raced origin forward 3 commits = r524 behind-signal "
                                       "(bm-c r560 same-window wave), merge-mode zero-UU canonical "
                                       "closeout, delivery 6e0b0c43f); "
                                       "pre-seat probe and freeze-window band-gate runs derive "
                                       "identical, no fork face), "
                                       "engine_owner=bm-a, wave 132: "
                                       "A = arithmetic continuation from the registered W131 A tail "
                                       "(307_004..309_003 CLEAN hops=0) + B = arithmetic continuation "
                                       "from the registered W131 B tail (68_902..69_101 CLEAN hops=0 "
                                       "double-CLEAN window; cross-window convergence with the r736 "
                                       "W131 seat MSG-1726 W132+ projection re-derived; ADMIT receipt "
                                       "results/_r737bma_w132_band_gate.py; W133+ projection per this "
                                       "window gate: A 309_004..311_003 CLEAN / B 69_102..69_301 "
                                       "CLEAN both hops=0; W1..W131 finalize ALL LANDED (W131 "
                                       "finalize one-pass bm-a r737, §7 backfill same commit; net "
                                       "chain head 684,211, merged pool K=286,120) -- ZERO in-flight "
                                       "upstream seats, clean finalize chain precondition -- finalize "
                                       "merge loop still derives the wave set from registry keys at "
                                       "run time, FAIL-CLOSED r307 always on)"),
                            "a_seed_base": 307_004,        # law sec.4 W132 A: 307_004..309_003 (arithmetic continuation from the registered W131 A tail)
                            "b_exit_seed_base": 68_902,   # law sec.4 W132 B: 68_902..69_101 (arithmetic continuation from the registered W131 B tail, CLEAN hops=0 double-CLEAN window)
                            "shard_subdir": "n1_w132", "out_name": "n1_w132_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    n1 = n1.replace(wc_anchor, wc_new)
    print("n1: WAVE_CONFIGS[132] inserted")

# --- 2b. materializer face insertion after the W131 face end ---
if "_set_wave(132)" in n1:
    print("n1: W132 materializer face already present (idempotent skip)")
else:
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
    print("n1: W132 materializer face inserted")

# --- 2c. selftest prose face after the W131 prose ---
if 'law sec.4 W132 row, r737 bm-a] ' in n1:
    print("n1: W132 prose face already present (idempotent skip)")
else:
    prose_anchor = 'W131 row, r736 bm-a] "\n          "+ T-141 s2 "'
    assert n1.count(prose_anchor) == 1, "n1: prose anchor"
    prose_new = '''W131 row, r736 bm-a] "
          "+ W132 materializer face [same guard set, dep=W17..W131 outputs "
          "ALL PRESENT (landed net chain head 684,211 = W131 bm-a r737 "
          "one-pass, §7 backfill same commit; K=286,120 merged pool; ZERO "
          "in-flight upstream seats, clean precondition freeze window), "
          "ONE HUNDRED-AND-TWENTY-SECOND ENGINE-OWNED WAVE BY MACHINE-DERIVE "
          "(engine_owner rows 121 + candidate) bm-a's forty-eighth owned "
          "claim per machine-derive (engine_owner==bm-a rows 47 + "
          "candidate), engine_owner=bm-a per engine de-throttle law "
          "O-20261001-2355 sec.2 own-continuous-series (wave 132 = first "
          "FREE number after the REGISTERED W131 row bm-a r736 freeze "
          "8cd6667e8, SINGLE STATE zero seat gap W2..W131 all registered; "
          "seat published=reserved MSG-2026-10-05-1755-bma-w132-seat "
          "pushed to origin 9c7e85e7f BEFORE this freeze, r565 law "
          "(payload = seat MSG + pre-seat probe + probe receipt, "
          "deletion-set EMPTY; first push raced origin forward 3 commits "
          "= r524 behind-signal (bm-c r560 same-window wave), merge-mode "
          "zero-UU canonical closeout, delivery 6e0b0c43f), A = "
          "ARITHMETIC CONTINUATION from the registered W131 A tail "
          "(307_004..309_003 CLEAN hops=0) + B = ARITHMETIC CONTINUATION "
          "from the registered W131 B tail (68_902..69_101 CLEAN hops=0 "
          "double-CLEAN window; cross-window convergence with the r736 "
          "W131 seat MSG-1726 W132+ projection re-derived; ADMIT receipt "
          "results/_r737bma_w132_band_gate.py; W133+ projection per "
          "this window gate: A 309_004..311_003 CLEAN / B 69_102..69_301 "
          "CLEAN both hops=0) disclosed for the next freezer; not a "
          "free pick -- R250), law sec.4 "
          "W132 row, r737 bm-a] "
          "+ T-141 s2 "'''
    n1 = n1.replace(prose_anchor, prose_new)
    print("n1: W132 prose face inserted")

io.open(n1_path, "w", encoding="utf-8", newline="\n").write(n1)
print("ALL INSERTIONS DONE")
