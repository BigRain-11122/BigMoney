# -*- coding: utf-8 -*-
"""r741 bm-a W136 registry insertion: N1_BANDS row 136 (perpetual_faces.py)
+ WAVE_CONFIGS[136] + materializer face + selftest prose face
(perpetual_faces_n1.py). All insertions needle-asserted; idempotent guards.
Bloodline: r740 _r740bma_w135_registry_insert.py verbatim + W136 facts
(double-CLEAN window: A = arithmetic continuation from the registered W135
A tail 315_003+1, CLEAN hops=0; B = arithmetic continuation from
the registered W135 B tail 69_701+1, CLEAN hops=0).
r735 codegen pit laws enforced: (1) all new-block assert messages
single-line or parenthesized; (2) rep() expects measured on
post-prior-replacement text (measurement pass results/_r741bma_w136_extract.py
printed every count verbatim before this script was written; w135_b raw=9
with the 9th hit inside the band-gate receipt needle consumed FIRST)."""
import io

def rep(src, pairs, tag):
    for old, new, expect in pairs:
        n = src.count(old)
        assert n == expect, f"{tag}: needle count={n} expect={expect}: {old[:60]!r}"
        src = src.replace(old, new)
    return src

# ============ 0. transform the extracted W135 face -> W136 face ============
face = io.open(r".codely-cli\scratch_w135_face_source.txt", encoding="utf-8").read()

# --- 0a. blanket wave-number shift FIRST (uppercase; then verified needles) ---
n_w135 = face.count("W135"); n_w134 = face.count("W134"); n_w133 = face.count("W133")
face = face.replace("W135", "W136")
face = face.replace("W134", "W135")
face = face.replace("W133", "W134")
assert face.count("W136") == n_w135 and face.count("W135") == n_w134 \
    and face.count("W134") == n_w133 and face.count("W133") == 0, \
    "blanket count check"

# --- 0b. A/B-block seed-value needles (arithmetic continuation from W135 tails) ---
face = rep(face, [
    ("== 313_004 == 313_003 + 1", "== 315_004 == 315_003 + 1", 1),
    ("set(range(313_004, 315_004))", "set(range(315_004, 317_004))", 1),
    ("== 69_502 == 69_501 + 1", "== 69_702 == 69_701 + 1", 1),
    ("set(range(69_502, 69_702))", "set(range(69_702, 69_902))", 1),
    ("arith_a135", "arith_a136", 2),
    ("arith_b135", "arith_b136", 2),
], "face-0b")

# --- 0c. specific needles (counts measured post-0a/0b by the measurement
#     pass results/_r741bma_w136_extract.py; the receipt/seat needles
#     run FIRST because of the substring-order law -- the band-gate receipt
#     needle carries a w135_b substring, consuming the 9th raw hit; the
#     parity block replacement runs LAST because its added rows carry
#     W-numbers) ---
specific = [
    # receipt/seat needles FIRST (substring-order law)
    ("_r740bma_w135_band_gate.py", "_r741bma_w136_band_gate.py", 1),
    ("MSG-2026-10-05-1933-bma-w135-seat", "MSG-2026-10-05-1952-bma-w136-seat", 1),
    ("bm-a r739 freeze d6b64dddd", "bm-a r740 freeze bc921896a", 1),
    ("to origin 98712a0e3 BEFORE", "to origin 20d0036dc BEFORE", 1),
    ("direct clean fast-forward push this\n    #     window (zero race, zero merge window), delivery\n    #     98712a0e3)",
     "pre-freeze push raced origin forward 1\n    #     commit = r524 behind-signal (bm-c r568 same-window\n    #     wave), merge-mode zero-UU closeout, delivery\n    #     2564ba798)", 1),
    ("r739 W135 seat MSG-1857 tail", "r740 W135 seat MSG-1933 tail", 1),
    ("W135 finalize one-pass bm-a r740", "W135 finalize one-pass bm-a r741", 1),
    ("= W135 bm-a r740 one-pass", "= W135 bm-a r741 one-pass", 1),
    ("net chain head 690,811", "net chain head 693,011", 2),
    ("K=292,720", "K=294,920", 1),
    ("ONE HUNDRED-AND-TWENTY-FIFTH", "ONE HUNDRED-AND-TWENTY-SIXTH", 1),
    ("fifty-first", "fifty-second", 1),
    ("wave 135 = first free number", "wave 136 = first free number", 1),
    ("rows 50 + candidate", "rows 51 + candidate", 1),
    ("rows 124 + candidate", "rows 125 + candidate", 1),
    ("below 135 composes", "below 136 composes", 1),
    ("WAVE_CONFIGS[135]", "WAVE_CONFIGS[136]", 5),
    ("pf.N1_BANDS[135]", "pf.N1_BANDS[136]", 3),
    ("_set_wave(135)", "_set_wave(136)", 1),
    ("if w < 135", "if w < 136", 3),
    ("range(17, 135)", "range(17, 136)", 1),
    ("range(16, 135)", "range(16, 136)", 1),
    ("w135_a", "w136_a", 8),
    ("w135_b", "w136_b", 8),  # 9th raw hit = "_r740bma_w135_band_gate.py" substring, consumed by the receipt needle above (substring-order law)
    ("n3r1_used135", "n3r1_used136", 3),
    ("n1w135", "n1w136", 2), ("n1_w135", "n1_w136", 2),
]
face = rep(face, specific, "face")

# --- 0e. registered row parity block shift LAST (W131..W134 -> W132..W135) ---
# NOTE: the 0a blanket shift has ALREADY shifted the [133]/[134] assert labels
# (W133->W134, W134->W135); the [131]/[132] labels are untouched by 0a
# (W131/W132 not in the 0a key set this round).
old_parity = '''assert pf.N1_BANDS[131] == {"a": (305_004, 307_003),
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
            "registered W134 row parity drift (r307; bm-a r738)"
        assert pf.N1_BANDS[134] == {"a": (311_004, 313_003),
                                    "b_exit": (69_302, 69_501),
                                    "engine_owner": "bm-a"}, \\
            "registered W135 row parity drift (r307; bm-a r739)"'''
new_parity = '''assert pf.N1_BANDS[132] == {"a": (307_004, 309_003),
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
            "registered W134 row parity drift (r307; bm-a r739)"
        assert pf.N1_BANDS[135] == {"a": (313_004, 315_003),
                                    "b_exit": (69_502, 69_701),
                                    "engine_owner": "bm-a"}, \\
            "registered W135 row parity drift (r307; bm-a r740)"'''
assert face.count(old_parity) == 1, "face: row-parity block needle"
face = face.replace(old_parity, new_parity)

io.open(r".codely-cli\scratch_w136_face.txt", "w", encoding="utf-8", newline="\n").write(face)
print("face: W136 block transformed")

# ============ 1. perpetual_faces.py N1_BANDS row 136 ============
pf_path = r"scripts\perpetual_faces.py"
pf_src = io.open(pf_path, encoding="utf-8").read()
if '136: {"a": (315_004' in pf_src:
    print("pf: row 136 already present (idempotent skip)")
else:
    w135_row = '''    135: {"a": (313_004, 315_003), "b_exit": (69_502, 69_701),
         "engine_owner": "bm-a"},
}'''
    assert pf_src.count(w135_row) == 1, "pf: W135 row + closing brace needle"
    w136_block = '''    135: {"a": (313_004, 315_003), "b_exit": (69_502, 69_701),
         "engine_owner": "bm-a"},
    # W136 (bm-a r741 freeze, seat MSG-2026-10-05-1952-bma-w136-seat
    # pushed to origin 20d0036dc pre-freeze r565 law (push raced origin
    # forward 1 commit = r524 behind-signal (bm-c r568 same-window
    # wave), merge-mode zero-UU closeout, delivery 2564ba798); band
    # gate ADMIT results/_r741bma_w136_band_gate.json: double-CLEAN
    # window -- A arithmetic continuation 315_003+1 ->
    # 315_004..317_003 CLEAN hops=0; B arithmetic continuation
    # 69_701+1 -> 69_702..69_901 CLEAN hops=0; dual-window derive
    # parity with pre-seat probe; scan face = SEED_REGISTRY 187 int
    # values + v1/W1 ext bands + N3-R1 used-seed band + probe
    # cluster 95_000..95_003 + cross-face probe points
    # 95_004/95_006 + lfc/options actuals + N2/N4/N2-W15 probe
    # points.
    # W137+ projection (gate-derived r741): A 317_004..319_003
    # CLEAN hops=0; B first-clean 94_001..94_200 hops=12 (honest
    # forward walk past N3-R1 used band + registry points; next
    # freezer must re-derive, never transcribe r587 law).
    # NOT a re-pick (R250: W136 bands were never assigned).
    136: {"a": (315_004, 317_003), "b_exit": (69_702, 69_901),
         "engine_owner": "bm-a"},
}'''
    pf_src = pf_src.replace(w135_row, w136_block)
    io.open(pf_path, "w", encoding="utf-8", newline="\n").write(pf_src)
    print("pf: N1_BANDS row 136 inserted")

print("PART 1 DONE (face + pf row)")
