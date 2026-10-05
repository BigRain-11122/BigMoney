# -*- coding: utf-8 -*-
"""r739 bm-a W134 registry insertion: N1_BANDS row 134 (perpetual_faces.py)
+ WAVE_CONFIGS[134] + materializer face + selftest prose face
(perpetual_faces_n1.py). All insertions needle-asserted; idempotent guards.
Bloodline: r738 _r738bma_w133_registry_insert.py verbatim + W134 facts
(double-CLEAN window: A = arithmetic continuation from the registered W133
A tail 311_003+1, CLEAN hops=0; B = arithmetic continuation from
the registered W133 B tail 69_301+1, CLEAN hops=0).
r735 codegen pit laws enforced: (1) all new-block assert messages
single-line or parenthesized; (2) rep() expects measured on
post-prior-replacement text (measurement pass results/_r739bma_w134_extract.py
printed every count verbatim before this script was written; w133_b raw=9
with the 9th hit inside the band-gate receipt needle consumed FIRST)."""
import io

def rep(src, pairs, tag):
    for old, new, expect in pairs:
        n = src.count(old)
        assert n == expect, f"{tag}: needle count={n} expect={expect}: {old[:60]!r}"
        src = src.replace(old, new)
    return src

# ============ 0. transform the extracted W133 face -> W134 face ============
face = io.open(r".codely-cli\scratch_w133_face_source.txt", encoding="utf-8").read()

# --- 0a. blanket wave-number shift FIRST (uppercase; then verified needles) ---
n_w133 = face.count("W133"); n_w132 = face.count("W132"); n_w131 = face.count("W131")
face = face.replace("W133", "W134")
face = face.replace("W132", "W133")
face = face.replace("W131", "W132")
assert face.count("W134") == n_w133 and face.count("W133") == n_w132 \
    and face.count("W132") == n_w131 and face.count("W131") == 0, \
    "blanket count check"

# --- 0b. A/B-block seed-value needles (arithmetic continuation from W133 tails) ---
face = rep(face, [
    ("== 309_004 == 309_003 + 1", "== 311_004 == 311_003 + 1", 1),
    ("set(range(309_004, 311_004))", "set(range(311_004, 313_004))", 1),
    ("== 69_102 == 69_101 + 1", "== 69_302 == 69_301 + 1", 1),
    ("set(range(69_102, 69_302))", "set(range(69_302, 69_502))", 1),
    ("arith_a133", "arith_a134", 2),
    ("arith_b133", "arith_b134", 2),
], "face-0b")

# --- 0c. specific needles (counts measured post-0a/0b by the measurement
#     pass results/_r739bma_w134_extract.py; the receipt/seat needles
#     run FIRST because of the substring-order law -- the band-gate receipt
#     needle carries a w133_b substring, consuming the 9th raw hit; the
#     parity block replacement runs LAST because its added rows carry
#     W-numbers) ---
specific = [
    # receipt/seat needles FIRST (substring-order law)
    ("_r738bma_w133_band_gate.py", "_r739bma_w134_band_gate.py", 1),
    ("MSG-2026-10-05-1824-bma-w133-seat", "MSG-2026-10-05-1857-bma-w134-seat", 1),
    ("bm-a r737 freeze 37c3925ad", "bm-a r738 freeze a869ad2ee", 1),
    ("2d717cc03", "5f3d9fcfc", 1),
    ("1ea4ff938", "ad07612e7", 1),
    ("first push raced origin forward 8", "first push raced origin forward 4", 1),
    ("(bm-c r563 same-window", "(bm-c r565 same-window", 1),
    ("r737 W133 seat MSG-1755 tail", "r738 W133 seat MSG-1824 tail", 1),
    ("W133 finalize one-pass bm-a r738", "W133 finalize one-pass bm-a r739", 1),
    ("= W133 bm-a r738 one-pass", "= W133 bm-a r739 one-pass", 1),
    ("net chain head 686,411", "net chain head 688,611", 2),
    ("K=288,320", "K=290,520", 1),
    ("ONE HUNDRED-AND-TWENTY-THIRD", "ONE HUNDRED-AND-TWENTY-FOURTH", 1),
    ("forty-ninth", "fiftieth", 1),
    ("wave 133 = first free number", "wave 134 = first free number", 1),
    ("rows 48 + candidate", "rows 49 + candidate", 1),
    ("rows 122 + candidate", "rows 123 + candidate", 1),
    ("below 133 composes", "below 134 composes", 1),
    ("WAVE_CONFIGS[133]", "WAVE_CONFIGS[134]", 5),
    ("pf.N1_BANDS[133]", "pf.N1_BANDS[134]", 3),
    ("_set_wave(133)", "_set_wave(134)", 1),
    ("if w < 133", "if w < 134", 3),
    ("range(17, 133)", "range(17, 134)", 1),
    ("range(16, 133)", "range(16, 134)", 1),
    ("w133_a", "w134_a", 8),
    ("w133_b", "w134_b", 8),  # 9th raw hit = "_r738bma_w133_band_gate.py" substring, consumed by the receipt needle above (substring-order law)
    ("n3r1_used133", "n3r1_used134", 3),
    ("n1w133", "n1w134", 2), ("n1_w133", "n1_w134", 2),
]
face = rep(face, specific, "face")

# --- 0e. registered row parity block shift LAST (W129..W132 -> W130..W133) ---
old_parity = '''assert pf.N1_BANDS[129] == {"a": (301_004, 303_003),
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
            "registered W132 row parity drift (r307; bm-a r736)"
        assert pf.N1_BANDS[132] == {"a": (307_004, 309_003),
                                    "b_exit": (68_902, 69_101),
                                    "engine_owner": "bm-a"}, \\
            "registered W133 row parity drift (r307; bm-a r737)"'''
new_parity = '''assert pf.N1_BANDS[130] == {"a": (303_004, 305_003),
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
            "registered W132 row parity drift (r307; bm-a r737)"
        assert pf.N1_BANDS[133] == {"a": (309_004, 311_003),
                                    "b_exit": (69_102, 69_301),
                                    "engine_owner": "bm-a"}, \\
            "registered W133 row parity drift (r307; bm-a r738)"'''
assert face.count(old_parity) == 1, "face: row-parity block needle"
face = face.replace(old_parity, new_parity)

io.open(r".codely-cli\scratch_w134_face.txt", "w", encoding="utf-8", newline="\n").write(face)
print("face: W134 block transformed")

# ============ 1. perpetual_faces.py N1_BANDS row 134 ============
pf_path = r"scripts\perpetual_faces.py"
pf_src = io.open(pf_path, encoding="utf-8").read()
if '134: {"a": (311_004, 313_003)' in pf_src:
    print("pf: row 134 already present (idempotent skip)")
else:
    w133_row = '''    133: {"a": (309_004, 311_003), "b_exit": (69_102, 69_301),
         "engine_owner": "bm-a"},
}'''
    assert pf_src.count(w133_row) == 1, "pf: W133 row + closing brace needle"
    w134_block = '''    133: {"a": (309_004, 311_003), "b_exit": (69_102, 69_301),
         "engine_owner": "bm-a"},
    # W134 (bm-a r739 freeze, seat MSG-2026-10-05-1857-bma-w134-seat
    # pushed to origin 5f3d9fcfc pre-freeze r565 law; band gate ADMIT
    # results/_r739bma_w134_band_gate.json: double-CLEAN window --
    # A arithmetic continuation 311_003+1 -> 311_004..313_003
    # CLEAN hops=0; B arithmetic continuation 69_301+1 ->
    # 69_302..69_501 CLEAN hops=0; dual-window derive parity with
    # pre-seat probe; scan face = SEED_REGISTRY 187 int values +
    # v1/W1 ext bands + N3-R1 used-seed band + probe cluster
    # 95_000..95_003 + cross-face probe points 95_004/95_006 +
    # lfc/options actuals + N2/N4/N2-W15 probe points.
    # W135+ projection (gate-derived r739): A 313_004..315_003
    # CLEAN hops=0; B 69_502..69_701 CLEAN hops=0 (next freezer
    # must re-derive, never transcribe r587 law).
    # NOT a re-pick (R250: W134 bands were never assigned).
    134: {"a": (311_004, 313_003), "b_exit": (69_302, 69_501),
         "engine_owner": "bm-a"},
}'''
    pf_src = pf_src.replace(w133_row, w134_block)
    io.open(pf_path, "w", encoding="utf-8", newline="\n").write(pf_src)
    print("pf: N1_BANDS row 134 inserted")

# ============ 2. perpetual_faces_n1.py ============
n1_path = r"scripts\perpetual_faces_n1.py"
n1 = io.open(n1_path, encoding="utf-8").read()

# --- 2a. WAVE_CONFIGS[134] after entry 133 ---
if '"batch": "PERPETUAL-N1-W134"' in n1:
    print("n1: WAVE_CONFIGS[134] already present (idempotent skip)")
else:
    wc_anchor = '''                            "shard_subdir": "n1_w133", "out_name": "n1_w133_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    assert n1.count(wc_anchor) == 1, "n1: WAVE_CONFIGS W133 entry anchor"
    wc_new = '''                            "shard_subdir": "n1_w133", "out_name": "n1_w133_results.json",
                            "engine_owner": "bm-a"},
                       134: {"batch": "PERPETUAL-N1-W134",
                            "prereg": ("research/PERPETUAL_N1_W134_PREREG.md (wave-level frozen "
                                       "pre-run; design = frozen v1 null calibration verbatim, "
                                       "new seed bands only; ONE HUNDRED-AND-TWENTY-FOURTH ENGINE-OWNED WAVE "
                                       "BY MACHINE-DERIVE (engine_owner rows 123 + candidate), "
                                       "own-series continuation per O-20261001-2355 sec.2 (first-free-"
                                       "number law after the REGISTERED W133 row bm-a r738 freeze "
                                       "a869ad2ee, SINGLE STATE zero seat gap W2..W133 all "
                                       "registered; W133 finalize landed same-window r739, ledger "
                                       "head 688,611, merged pool K=290,520; seat published=reserved "
                                       "MSG-2026-10-05-1857-bma-w134-seat PUSHED to origin 5f3d9fcfc "
                                       "BEFORE this freeze per r565 early-visibility law (payload = "
                                       "seat MSG + pre-seat probe + probe receipt; deletion-set EMPTY; "
                                       "first push raced origin forward 4 commits = r524 behind-signal "
                                       "(bm-c r565 same-window wave), merge-mode zero-UU canonical "
                                       "closeout, delivery ad07612e7); "
                                       "pre-seat probe and freeze-window band-gate runs derive "
                                       "identical, no fork face), "
                                       "engine_owner=bm-a, wave 134: "
                                       "A = arithmetic continuation from the registered W133 A tail "
                                       "(311_004..313_003 CLEAN hops=0) + B = arithmetic continuation "
                                       "from the registered W133 B tail (69_302..69_501 CLEAN hops=0 "
                                       "double-CLEAN window; cross-window convergence with the r738 "
                                       "W133 seat MSG-1824 W134+ projection re-derived; ADMIT receipt "
                                       "results/_r739bma_w134_band_gate.py; W135+ projection per this "
                                       "window gate: A 313_004..315_003 CLEAN / B 69_502..69_701 "
                                       "CLEAN both hops=0; W1..W133 finalize ALL LANDED (W133 "
                                       "finalize one-pass bm-a r739, §7 backfill same commit; net "
                                       "chain head 688,611, merged pool K=290,520) -- ZERO in-flight "
                                       "upstream seats, clean finalize chain precondition -- finalize "
                                       "merge loop still derives the wave set from registry keys at "
                                       "run time, FAIL-CLOSED r307 always on)"),
                            "a_seed_base": 311_004,        # law sec.4 W134 A: 311_004..313_003 (arithmetic continuation from the registered W133 A tail)
                            "b_exit_seed_base": 69_302,   # law sec.4 W134 B: 69_302..69_501 (arithmetic continuation from the registered W133 B tail, CLEAN hops=0 double-CLEAN window)
                            "shard_subdir": "n1_w134", "out_name": "n1_w134_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    n1 = n1.replace(wc_anchor, wc_new)
    print("n1: WAVE_CONFIGS[134] inserted")

# --- 2b. materializer face insertion after the W133 face end ---
if "_set_wave(134)" in n1:
    print("n1: W134 materializer face already present (idempotent skip)")
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
    print("n1: W134 materializer face inserted")

# --- 2c. selftest prose face after the W133 prose ---
if 'law sec.4 W134 row, r739 bm-a] ' in n1:
    print("n1: W134 prose face already present (idempotent skip)")
else:
    prose_anchor = 'W133 row, r738 bm-a] "\n          "+ T-141 s2 "'
    assert n1.count(prose_anchor) == 1, "n1: prose anchor"
    prose_new = '''W133 row, r738 bm-a] "
          "+ W134 materializer face [same guard set, dep=W17..W133 outputs "
          "ALL PRESENT (landed net chain head 688,611 = W133 bm-a r739 "
          "one-pass, §7 backfill same commit; K=290,520 merged pool; ZERO "
          "in-flight upstream seats, clean precondition freeze window), "
          "ONE HUNDRED-AND-TWENTY-FOURTH ENGINE-OWNED WAVE BY MACHINE-DERIVE "
          "(engine_owner rows 123 + candidate) bm-a's fiftieth owned "
          "claim per machine-derive (engine_owner==bm-a rows 49 + "
          "candidate), engine_owner=bm-a per engine de-throttle law "
          "O-20261001-2355 sec.2 own-continuous-series (wave 134 = first "
          "FREE number after the REGISTERED W133 row bm-a r738 freeze "
          "a869ad2ee, SINGLE STATE zero seat gap W2..W133 all registered; "
          "seat published=reserved MSG-2026-10-05-1857-bma-w134-seat "
          "pushed to origin 5f3d9fcfc BEFORE this freeze, r565 law "
          "(payload = seat MSG + pre-seat probe + probe receipt, "
          "deletion-set EMPTY; first push raced origin forward 4 commits "
          "= r524 behind-signal (bm-c r565 same-window wave), merge-mode "
          "zero-UU canonical closeout, delivery ad07612e7), A = "
          "ARITHMETIC CONTINUATION from the registered W133 A tail "
          "(311_004..313_003 CLEAN hops=0) + B = ARITHMETIC CONTINUATION "
          "from the registered W133 B tail (69_302..69_501 CLEAN hops=0 "
          "double-CLEAN window; cross-window convergence with the r738 "
          "W133 seat MSG-1824 W134+ projection re-derived; ADMIT receipt "
          "results/_r739bma_w134_band_gate.py; W135+ projection per "
          "this window gate: A 313_004..315_003 CLEAN / B 69_502..69_701 "
          "CLEAN both hops=0) disclosed for the next freezer; not a "
          "free pick -- R250), law sec.4 "
          "W134 row, r739 bm-a] "
          "+ T-141 s2 "'''
    n1 = n1.replace(prose_anchor, prose_new)
    print("n1: W134 prose face inserted")

io.open(n1_path, "w", encoding="utf-8", newline="\n").write(n1)
print("ALL INSERTIONS DONE")
