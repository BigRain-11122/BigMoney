# -*- coding: utf-8 -*-
"""r740 bm-a W135 registry insertion: N1_BANDS row 135 (perpetual_faces.py)
+ WAVE_CONFIGS[135] + materializer face + selftest prose face
(perpetual_faces_n1.py). All insertions needle-asserted; idempotent guards.
Bloodline: r739 _r739bma_w134_registry_insert.py verbatim + W135 facts
(double-CLEAN window: A = arithmetic continuation from the registered W134
A tail 313_003+1, CLEAN hops=0; B = arithmetic continuation from
the registered W134 B tail 69_501+1, CLEAN hops=0).
r735 codegen pit laws enforced: (1) all new-block assert messages
single-line or parenthesized; (2) rep() expects measured on
post-prior-replacement text (measurement pass results/_r740bma_w135_extract.py
printed every count verbatim before this script was written; w134_b raw=9
with the 9th hit inside the band-gate receipt needle consumed FIRST)."""
import io

def rep(src, pairs, tag):
    for old, new, expect in pairs:
        n = src.count(old)
        assert n == expect, f"{tag}: needle count={n} expect={expect}: {old[:60]!r}"
        src = src.replace(old, new)
    return src

# ============ 0. transform the extracted W134 face -> W135 face ============
face = io.open(r".codely-cli\scratch_w134_face_source.txt", encoding="utf-8").read()

# --- 0a. blanket wave-number shift FIRST (uppercase; then verified needles) ---
n_w134 = face.count("W134"); n_w133 = face.count("W133"); n_w132 = face.count("W132")
face = face.replace("W134", "W135")
face = face.replace("W133", "W134")
face = face.replace("W132", "W133")
assert face.count("W135") == n_w134 and face.count("W134") == n_w133 \
    and face.count("W133") == n_w132 and face.count("W132") == 0, \
    "blanket count check"

# --- 0b. A/B-block seed-value needles (arithmetic continuation from W134 tails) ---
face = rep(face, [
    ("== 311_004 == 311_003 + 1", "== 313_004 == 313_003 + 1", 1),
    ("set(range(311_004, 313_004))", "set(range(313_004, 315_004))", 1),
    ("== 69_302 == 69_301 + 1", "== 69_502 == 69_501 + 1", 1),
    ("set(range(69_302, 69_502))", "set(range(69_502, 69_702))", 1),
    ("arith_a134", "arith_a135", 2),
    ("arith_b134", "arith_b135", 2),
], "face-0b")

# --- 0c. specific needles (counts measured post-0a/0b by the measurement
#     pass results/_r740bma_w135_extract.py; the receipt/seat needles
#     run FIRST because of the substring-order law -- the band-gate receipt
#     needle carries a w134_b substring, consuming the 9th raw hit; the
#     parity block replacement runs LAST because its added rows carry
#     W-numbers) ---
specific = [
    # receipt/seat needles FIRST (substring-order law)
    ("_r739bma_w134_band_gate.py", "_r740bma_w135_band_gate.py", 1),
    ("MSG-2026-10-05-1857-bma-w134-seat", "MSG-2026-10-05-1933-bma-w135-seat", 1),
    ("bm-a r738 freeze a869ad2ee", "bm-a r739 freeze d6b64dddd", 1),
    ("5f3d9fcfc", "98712a0e3", 1),
    ("first push raced origin forward 4\n    #     commits = r524 behind-signal (bm-c r565 same-window\n    #     wave), merge-mode zero-UU canonical closeout,\n    #     delivery ad07612e7)",
     "direct clean fast-forward push this\n    #     window (zero race, zero merge window), delivery\n    #     98712a0e3)", 1),
    ("r738 W134 seat MSG-1824 tail", "r739 W134 seat MSG-1857 tail", 1),
    ("W134 finalize one-pass bm-a r739", "W134 finalize one-pass bm-a r740", 1),
    ("= W134 bm-a r739 one-pass", "= W134 bm-a r740 one-pass", 1),
    ("net chain head 688,611", "net chain head 690,811", 2),
    ("K=290,520", "K=292,720", 1),
    ("ONE HUNDRED-AND-TWENTY-FOURTH", "ONE HUNDRED-AND-TWENTY-FIFTH", 1),
    ("fiftieth", "fifty-first", 1),
    ("wave 134 = first free number", "wave 135 = first free number", 1),
    ("rows 49 + candidate", "rows 50 + candidate", 1),
    ("rows 123 + candidate", "rows 124 + candidate", 1),
    ("below 134 composes", "below 135 composes", 1),
    ("WAVE_CONFIGS[134]", "WAVE_CONFIGS[135]", 5),
    ("pf.N1_BANDS[134]", "pf.N1_BANDS[135]", 3),
    ("_set_wave(134)", "_set_wave(135)", 1),
    ("if w < 134", "if w < 135", 3),
    ("range(17, 134)", "range(17, 135)", 1),
    ("range(16, 134)", "range(16, 135)", 1),
    ("w134_a", "w135_a", 8),
    ("w134_b", "w135_b", 8),  # 9th raw hit = "_r739bma_w134_band_gate.py" substring, consumed by the receipt needle above (substring-order law)
    ("n3r1_used134", "n3r1_used135", 3),
    ("n1w134", "n1w135", 2), ("n1_w134", "n1_w135", 2),
]
face = rep(face, specific, "face")

# --- 0e. registered row parity block shift LAST (W130..W133 -> W131..W134) ---
# NOTE: the 0a blanket shift has ALREADY shifted the [132]/[133] assert labels
# (W132->W133, W133->W134); the [130]/[131] labels are untouched by 0a.
old_parity = '''assert pf.N1_BANDS[130] == {"a": (303_004, 305_003),
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
            "registered W133 row parity drift (r307; bm-a r737)"
        assert pf.N1_BANDS[133] == {"a": (309_004, 311_003),
                                    "b_exit": (69_102, 69_301),
                                    "engine_owner": "bm-a"}, \\
            "registered W134 row parity drift (r307; bm-a r738)"'''
new_parity = '''assert pf.N1_BANDS[131] == {"a": (305_004, 307_003),
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
            "registered W133 row parity drift (r307; bm-a r738)"
        assert pf.N1_BANDS[134] == {"a": (311_004, 313_003),
                                    "b_exit": (69_302, 69_501),
                                    "engine_owner": "bm-a"}, \\
            "registered W134 row parity drift (r307; bm-a r739)"'''
assert face.count(old_parity) == 1, "face: row-parity block needle"
face = face.replace(old_parity, new_parity)

io.open(r".codely-cli\scratch_w135_face.txt", "w", encoding="utf-8", newline="\n").write(face)
print("face: W135 block transformed")

# ============ 1. perpetual_faces.py N1_BANDS row 135 ============
pf_path = r"scripts\perpetual_faces.py"
pf_src = io.open(pf_path, encoding="utf-8").read()
if '135: {"a": (313_004' in pf_src:
    print("pf: row 135 already present (idempotent skip)")
else:
    w134_row = '''    134: {"a": (311_004, 313_003), "b_exit": (69_302, 69_501),
         "engine_owner": "bm-a"},
}'''
    assert pf_src.count(w134_row) == 1, "pf: W134 row + closing brace needle"
    w135_block = '''    134: {"a": (311_004, 313_003), "b_exit": (69_302, 69_501),
         "engine_owner": "bm-a"},
    # W135 (bm-a r740 freeze, seat MSG-2026-10-05-1933-bma-w135-seat
    # pushed to origin 98712a0e3 pre-freeze r565 law; band gate ADMIT
    # results/_r740bma_w135_band_gate.json: double-CLEAN window --
    # A arithmetic continuation 313_003+1 -> 313_004..315_003
    # CLEAN hops=0; B arithmetic continuation 69_501+1 ->
    # 69_502..69_701 CLEAN hops=0; dual-window derive parity with
    # pre-seat probe; scan face = SEED_REGISTRY 187 int values +
    # v1/W1 ext bands + N3-R1 used-seed band + probe cluster
    # 95_000..95_003 + cross-face probe points 95_004/95_006 +
    # lfc/options actuals + N2/N4/N2-W15 probe points.
    # W136+ projection (gate-derived r740): A 315_004..317_003
    # CLEAN hops=0; B 69_702..69_901 CLEAN hops=0 (next freezer
    # must re-derive, never transcribe r587 law).
    # NOT a re-pick (R250: W135 bands were never assigned).
    135: {"a": (313_004, 315_003), "b_exit": (69_502, 69_701),
         "engine_owner": "bm-a"},
}'''
    pf_src = pf_src.replace(w134_row, w135_block)
    io.open(pf_path, "w", encoding="utf-8", newline="\n").write(pf_src)
    print("pf: N1_BANDS row 135 inserted")

print("PART 1 DONE (face + pf row)")
