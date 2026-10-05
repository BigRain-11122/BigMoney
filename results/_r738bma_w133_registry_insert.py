# -*- coding: utf-8 -*-
"""r738 bm-a W133 registry insertion: N1_BANDS row 133 (perpetual_faces.py)
+ WAVE_CONFIGS[133] + materializer face + selftest prose face
(perpetual_faces_n1.py). All insertions needle-asserted; idempotent guards.
Bloodline: r737 _r737bma_w132_registry_insert.py verbatim + W133 facts
(double-CLEAN window: A = arithmetic continuation from the registered W132
A tail 309_003+1, CLEAN hops=0; B = arithmetic continuation from
the registered W132 B tail 69_101+1, CLEAN hops=0).
r735 codegen pit laws enforced: (1) all new-block assert messages
single-line or parenthesized; (2) rep() expects measured on
post-prior-replacement text (measurement passes results/_r738bma_w133_measure.py
+ _r738bma_w133_measure2.py printed every count verbatim before this
script was written)."""
import io

def rep(src, pairs, tag):
    for old, new, expect in pairs:
        n = src.count(old)
        assert n == expect, f"{tag}: needle count={n} expect={expect}: {old[:60]!r}"
        src = src.replace(old, new)
    return src

# ============ 0. transform the extracted W132 face -> W133 face ============
face = io.open(r".codely-cli\scratch_w132_face_source.txt", encoding="utf-8").read()

# --- 0a. blanket wave-number shift FIRST (uppercase; then verified needles) ---
n_w132 = face.count("W132"); n_w131 = face.count("W131"); n_w130 = face.count("W130")
face = face.replace("W132", "W133")
face = face.replace("W131", "W132")
face = face.replace("W130", "W131")
assert face.count("W133") == n_w132 and face.count("W132") == n_w131 \
    and face.count("W131") == n_w130 and face.count("W130") == 0, \
    "blanket count check"

# --- 0b. A/B-block seed-value needles (arithmetic continuation from W132 tails) ---
face = rep(face, [
    ("== 307_004 == 307_003 + 1", "== 309_004 == 309_003 + 1", 1),
    ("set(range(307_004, 309_004))", "set(range(309_004, 311_004))", 1),
    ("== 68_902 == 68_901 + 1", "== 69_102 == 69_101 + 1", 1),
    ("set(range(68_902, 69_102))", "set(range(69_102, 69_302))", 1),
    ("arith_a132", "arith_a133", 2),
    ("arith_b132", "arith_b133", 2),
], "face-0b")

# --- 0c. specific needles (counts measured post-0a/0b by the measurement
#     passes results/_r738bma_w133_measure{,2}.py; the receipt/seat needles
#     run FIRST because of the substring-order law -- the band-gate receipt
#     needle carries a w132_b substring, consuming the 9th raw hit; the
#     parity block replacement runs LAST because its added rows carry
#     W-numbers) ---
specific = [
    # receipt/seat needles FIRST (substring-order law)
    ("_r737bma_w132_band_gate.py", "_r738bma_w133_band_gate.py", 1),
    ("MSG-2026-10-05-1755-bma-w132-seat", "MSG-2026-10-05-1824-bma-w133-seat", 1),
    ("bm-a r736 freeze 8cd6667e8", "bm-a r737 freeze 37c3925ad", 1),
    ("9c7e85e7f", "2d717cc03", 1),
    ("6e0b0c43f", "1ea4ff938", 1),
    ("first push raced origin forward 3", "first push raced origin forward 8", 1),
    ("(bm-c r560 same-window", "(bm-c r563 same-window", 1),
    ("r736 W132 seat MSG-1726 tail", "r737 W132 seat MSG-1755 tail", 1),
    ("W132 finalize one-pass bm-a r737", "W132 finalize one-pass bm-a r738", 1),
    ("= W132 bm-a r737 one-pass", "= W132 bm-a r738 one-pass", 1),
    ("net chain head 684,211", "net chain head 686,411", 2),
    ("K=286,120", "K=288,320", 1),
    ("ONE HUNDRED-AND-TWENTY-SECOND", "ONE HUNDRED-AND-TWENTY-THIRD", 1),
    ("forty-eighth", "forty-ninth", 1),
    ("wave 132 = first free number", "wave 133 = first free number", 1),
    ("rows 47 + candidate", "rows 48 + candidate", 1),
    ("rows 121 + candidate", "rows 122 + candidate", 1),
    ("below 132 composes", "below 133 composes", 1),
    ("WAVE_CONFIGS[132]", "WAVE_CONFIGS[133]", 5),
    ("pf.N1_BANDS[132]", "pf.N1_BANDS[133]", 3),
    ("_set_wave(132)", "_set_wave(133)", 1),
    ("if w < 132", "if w < 133", 3),
    ("range(17, 132)", "range(17, 133)", 1),
    ("range(16, 132)", "range(16, 133)", 1),
    ("w132_a", "w133_a", 8),
    ("w132_b", "w133_b", 8),  # 9th raw hit = "_r737bma_w132_band_gate.py" substring, consumed by the receipt needle above (substring-order law)
    ("n3r1_used132", "n3r1_used133", 3),
    ("n1w132", "n1w133", 2), ("n1_w132", "n1_w133", 2),
]
face = rep(face, specific, "face")

# --- 0e. registered row parity block shift LAST (W128..W131 -> W129..W132) ---
old_parity = '''assert pf.N1_BANDS[128] == {"a": (299_004, 301_003),
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
            "registered W131 row parity drift (r307; bm-a r735)"
        assert pf.N1_BANDS[131] == {"a": (305_004, 307_003),
                                    "b_exit": (68_702, 68_901),
                                    "engine_owner": "bm-a"}, \\
            "registered W132 row parity drift (r307; bm-a r736)"'''
new_parity = '''assert pf.N1_BANDS[129] == {"a": (301_004, 303_003),
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
            "registered W131 row parity drift (r307; bm-a r736)"
        assert pf.N1_BANDS[132] == {"a": (307_004, 309_003),
                                    "b_exit": (68_902, 69_101),
                                    "engine_owner": "bm-a"}, \\
            "registered W132 row parity drift (r307; bm-a r737)"'''
assert face.count(old_parity) == 1, "face: row-parity block needle"
face = face.replace(old_parity, new_parity)

io.open(r".codely-cli\scratch_w133_face.txt", "w", encoding="utf-8", newline="\n").write(face)
print("face: W133 block transformed")

# ============ 1. perpetual_faces.py N1_BANDS row 133 ============
pf_path = r"scripts\perpetual_faces.py"
pf_src = io.open(pf_path, encoding="utf-8").read()
if '133: {"a": (309_004, 311_003)' in pf_src:
    print("pf: row 133 already present (idempotent skip)")
else:
    w132_row = '''    132: {"a": (307_004, 309_003), "b_exit": (68_902, 69_101),
         "engine_owner": "bm-a"},
}'''
    assert pf_src.count(w132_row) == 1, "pf: W132 row + closing brace needle"
    w133_block = '''    132: {"a": (307_004, 309_003), "b_exit": (68_902, 69_101),
         "engine_owner": "bm-a"},
    # W133 (bm-a r738 freeze, seat MSG-2026-10-05-1824-bma-w133-seat
    # pushed to origin 2d717cc03 pre-freeze r565 law; band gate ADMIT
    # results/_r738bma_w133_band_gate.json: double-CLEAN window --
    # A arithmetic continuation 309_003+1 -> 309_004..311_003
    # CLEAN hops=0; B arithmetic continuation 69_101+1 ->
    # 69_102..69_301 CLEAN hops=0; dual-window derive parity with
    # pre-seat probe; scan face = SEED_REGISTRY 187 int values +
    # v1/W1 ext bands + N3-R1 used-seed band + probe cluster
    # 95_000..95_003 + cross-face probe points 95_004/95_006 +
    # lfc/options actuals + N2/N4/N2-W15 probe points.
    # W134+ projection (gate-derived r738): A 311_004..313_003
    # CLEAN hops=0; B 69_302..69_501 CLEAN hops=0 (next freezer
    # must re-derive, never transcribe r587 law).
    # NOT a re-pick (R250: W133 bands were never assigned).
    133: {"a": (309_004, 311_003), "b_exit": (69_102, 69_301),
         "engine_owner": "bm-a"},
}'''
    pf_src = pf_src.replace(w132_row, w133_block)
    io.open(pf_path, "w", encoding="utf-8", newline="\n").write(pf_src)
    print("pf: N1_BANDS row 133 inserted")

# ============ 2. perpetual_faces_n1.py ============
n1_path = r"scripts\perpetual_faces_n1.py"
n1 = io.open(n1_path, encoding="utf-8").read()

# --- 2a. WAVE_CONFIGS[133] after entry 132 ---
if '"batch": "PERPETUAL-N1-W133"' in n1:
    print("n1: WAVE_CONFIGS[133] already present (idempotent skip)")
else:
    wc_anchor = '''                            "shard_subdir": "n1_w132", "out_name": "n1_w132_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    assert n1.count(wc_anchor) == 1, "n1: WAVE_CONFIGS W132 entry anchor"
    wc_new = '''                            "shard_subdir": "n1_w132", "out_name": "n1_w132_results.json",
                            "engine_owner": "bm-a"},
                       133: {"batch": "PERPETUAL-N1-W133",
                            "prereg": ("research/PERPETUAL_N1_W133_PREREG.md (wave-level frozen "
                                       "pre-run; design = frozen v1 null calibration verbatim, "
                                       "new seed bands only; ONE HUNDRED-AND-TWENTY-THIRD ENGINE-OWNED WAVE "
                                       "BY MACHINE-DERIVE (engine_owner rows 122 + candidate), "
                                       "own-series continuation per O-20261001-2355 sec.2 (first-free-"
                                       "number law after the REGISTERED W132 row bm-a r737 freeze "
                                       "37c3925ad, SINGLE STATE zero seat gap W2..W132 all "
                                       "registered; W132 finalize landed same-window r738, ledger "
                                       "head 686,411, merged pool K=288,320; seat published=reserved "
                                       "MSG-2026-10-05-1824-bma-w133-seat PUSHED to origin 2d717cc03 "
                                       "BEFORE this freeze per r565 early-visibility law (payload = "
                                       "seat MSG + pre-seat probe + probe receipt; deletion-set EMPTY; "
                                       "first push raced origin forward 8 commits = r524 behind-signal "
                                       "(bm-c r563 same-window wave), merge-mode zero-UU canonical "
                                       "closeout, delivery 1ea4ff938); "
                                       "pre-seat probe and freeze-window band-gate runs derive "
                                       "identical, no fork face), "
                                       "engine_owner=bm-a, wave 133: "
                                       "A = arithmetic continuation from the registered W132 A tail "
                                       "(309_004..311_003 CLEAN hops=0) + B = arithmetic continuation "
                                       "from the registered W132 B tail (69_102..69_301 CLEAN hops=0 "
                                       "double-CLEAN window; cross-window convergence with the r737 "
                                       "W132 seat MSG-1755 W133+ projection re-derived; ADMIT receipt "
                                       "results/_r738bma_w133_band_gate.py; W134+ projection per this "
                                       "window gate: A 311_004..313_003 CLEAN / B 69_302..69_501 "
                                       "CLEAN both hops=0; W1..W132 finalize ALL LANDED (W132 "
                                       "finalize one-pass bm-a r738, §7 backfill same commit; net "
                                       "chain head 686,411, merged pool K=288,320) -- ZERO in-flight "
                                       "upstream seats, clean finalize chain precondition -- finalize "
                                       "merge loop still derives the wave set from registry keys at "
                                       "run time, FAIL-CLOSED r307 always on)"),
                            "a_seed_base": 309_004,        # law sec.4 W133 A: 309_004..311_003 (arithmetic continuation from the registered W132 A tail)
                            "b_exit_seed_base": 69_102,   # law sec.4 W133 B: 69_102..69_301 (arithmetic continuation from the registered W132 B tail, CLEAN hops=0 double-CLEAN window)
                            "shard_subdir": "n1_w133", "out_name": "n1_w133_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    n1 = n1.replace(wc_anchor, wc_new)
    print("n1: WAVE_CONFIGS[133] inserted")

# --- 2b. materializer face insertion after the W132 face end ---
if "_set_wave(133)" in n1:
    print("n1: W133 materializer face already present (idempotent skip)")
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
    print("n1: W133 materializer face inserted")

# --- 2c. selftest prose face after the W132 prose ---
if 'law sec.4 W133 row, r738 bm-a] ' in n1:
    print("n1: W133 prose face already present (idempotent skip)")
else:
    prose_anchor = 'W132 row, r737 bm-a] "\n          "+ T-141 s2 "'
    assert n1.count(prose_anchor) == 1, "n1: prose anchor"
    prose_new = '''W132 row, r737 bm-a] "
          "+ W133 materializer face [same guard set, dep=W17..W132 outputs "
          "ALL PRESENT (landed net chain head 686,411 = W132 bm-a r738 "
          "one-pass, §7 backfill same commit; K=288,320 merged pool; ZERO "
          "in-flight upstream seats, clean precondition freeze window), "
          "ONE HUNDRED-AND-TWENTY-THIRD ENGINE-OWNED WAVE BY MACHINE-DERIVE "
          "(engine_owner rows 122 + candidate) bm-a's forty-ninth owned "
          "claim per machine-derive (engine_owner==bm-a rows 48 + "
          "candidate), engine_owner=bm-a per engine de-throttle law "
          "O-20261001-2355 sec.2 own-continuous-series (wave 133 = first "
          "FREE number after the REGISTERED W132 row bm-a r737 freeze "
          "37c3925ad, SINGLE STATE zero seat gap W2..W132 all registered; "
          "seat published=reserved MSG-2026-10-05-1824-bma-w133-seat "
          "pushed to origin 2d717cc03 BEFORE this freeze, r565 law "
          "(payload = seat MSG + pre-seat probe + probe receipt, "
          "deletion-set EMPTY; first push raced origin forward 8 commits "
          "= r524 behind-signal (bm-c r563 same-window wave), merge-mode "
          "zero-UU canonical closeout, delivery 1ea4ff938), A = "
          "ARITHMETIC CONTINUATION from the registered W132 A tail "
          "(309_004..311_003 CLEAN hops=0) + B = ARITHMETIC CONTINUATION "
          "from the registered W132 B tail (69_102..69_301 CLEAN hops=0 "
          "double-CLEAN window; cross-window convergence with the r737 "
          "W132 seat MSG-1755 W133+ projection re-derived; ADMIT receipt "
          "results/_r738bma_w133_band_gate.py; W134+ projection per "
          "this window gate: A 311_004..313_003 CLEAN / B 69_302..69_501 "
          "CLEAN both hops=0) disclosed for the next freezer; not a "
          "free pick -- R250), law sec.4 "
          "W133 row, r738 bm-a] "
          "+ T-141 s2 "'''
    n1 = n1.replace(prose_anchor, prose_new)
    print("n1: W133 prose face inserted")

io.open(n1_path, "w", encoding="utf-8", newline="\n").write(n1)
print("ALL INSERTIONS DONE")
