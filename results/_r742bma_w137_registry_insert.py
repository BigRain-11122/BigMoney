# -*- coding: utf-8 -*-
"""r742 bm-a W137 registry insertion PART 1: transform the extracted W136 face
-> W137 face (.codely-cli/scratch_w137_face.txt) + N1_BANDS row 137
(perpetual_faces.py). All insertions needle-asserted; idempotent guards.
Bloodline: r741 _r741bma_w136_registry_insert.py verbatim + W137 facts
(A = arithmetic continuation from the registered W136 A tail 317_003+1,
CLEAN hops=0; B = FIRST-CLEAN window after the honest 12-hop forward walk
past the registered W136 B tail 69_901+1 -- first window 69_902..70_101
refused by the N3-R1 used-seed band + contiguous registered 2_000-wide bands
70_001..94_000, lands at 94_001..94_200, non-rotational r587).
r735 codegen pit laws enforced: (1) all new-block assert messages
single-line or parenthesized; (2) rep() expects measured on
post-prior-replacement text (measurement pass results/_r742bma_w137_extract.py
printed every count verbatim before this script was written; w136_b raw=9
with the 9th hit inside the band-gate receipt needle consumed FIRST).
r741 dep-line law: dep lines keep the post-0a W number, advance only the
r number (W136 finalize one-pass = bm-a r742 THIS window).
Face-header stale-r fix (comment-only, r741 precedent): the face header has
carried a stale "(r737 bm-a freeze" since the W133-era insert; the W137 face
header is written truthful "(r742 bm-a freeze". Historical faces W133..W136
are NOT retro-edited (git history preserved)."""
import io

def rep(src, pairs, tag):
    for old, new, expect in pairs:
        n = src.count(old)
        assert n == expect, f"{tag}: needle count={n} expect={expect}: {old[:60]!r}"
        src = src.replace(old, new)
    return src

# ============ 0. transform the extracted W136 face -> W137 face ============
face = io.open(r".codely-cli\scratch_w136_face_source.txt", encoding="utf-8").read()

# --- 0a. blanket wave-number shift FIRST (uppercase; then verified needles) ---
n_w136 = face.count("W136"); n_w135 = face.count("W135"); n_w134 = face.count("W134")
face = face.replace("W136", "W137")
face = face.replace("W135", "W136")
face = face.replace("W134", "W135")
assert face.count("W137") == n_w136 and face.count("W136") == n_w135 \
    and face.count("W135") == n_w134 and face.count("W134") == 0, \
    "blanket count check"

# --- 0b. A-block seed-value needles (arithmetic continuation from W136 A tail) ---
face = rep(face, [
    ("== 315_004 == 315_003 + 1", "== 317_004 == 317_003 + 1", 1),
    ("set(range(315_004, 317_004))", "set(range(317_004, 319_004))", 1),
    ("arith_a136", "arith_a137", 2),
    ("arith_b136", "arith_b137", 2),
], "face-0b")

# --- 0c. specific needles (counts measured post-0a/0b by the measurement
#     pass results/_r742bma_w137_extract.py; the receipt/seat needles run
#     FIRST because of the substring-order law -- the band-gate receipt
#     needle carries a w136_b substring, consuming the 9th raw hit; the
#     parity block replacement runs LAST because its added rows carry
#     W-numbers) ---
specific = [
    # receipt/seat needles FIRST (substring-order law)
    ("_r741bma_w136_band_gate.py", "_r742bma_w137_band_gate.py", 1),
    ("MSG-2026-10-05-1952-bma-w136-seat", "MSG-2026-10-05-202x-bma-w137-seat", 1),
    ("bm-a r740 freeze bc921896a", "bm-a r741 freeze 7cafbc7ab", 1),
    ("to origin 20d0036dc BEFORE", "to origin af1c3c267 BEFORE", 1),
    ("pre-freeze push raced origin forward 1\n    #     commit = r524 behind-signal (bm-c r568 same-window\n    #     wave), merge-mode zero-UU closeout, delivery\n    #     2564ba798)",
     "pre-freeze push raced origin forward 2\n    #     commits = r524 behind-signal (bm-c r570 same-window\n    #     wave), merge-mode zero-UU closeout, delivery\n    #     d28d392ce)", 1),
    ("W136 finalize one-pass bm-a r741", "W136 finalize one-pass bm-a r742", 1),
    ("= W136 bm-a r741 one-pass", "= W136 bm-a r742 one-pass", 1),
    ("net chain head 693,011", "net chain head 695,211", 2),
    ("K=294,920", "K=297,120", 1),
    ("ONE HUNDRED-AND-TWENTY-SIXTH", "ONE HUNDRED-AND-TWENTY-SEVENTH", 1),
    ("fifty-second", "fifty-third", 1),
    ("(r737 bm-a freeze", "(r742 bm-a freeze", 1),
    ("(law sec.4 W137 row, r737)", "(law sec.4 W137 row, r742)", 1),
    ("wave 136 = first free number", "wave 137 = first free number", 1),
    ("rows 51 + candidate", "rows 52 + candidate", 1),
    ("rows 125 + candidate", "rows 126 + candidate", 1),
    ("below 136 composes", "below 137 composes", 1),
    ("WAVE_CONFIGS[136]", "WAVE_CONFIGS[137]", 5),
    ("pf.N1_BANDS[136]", "pf.N1_BANDS[137]", 3),
    ("_set_wave(136)", "_set_wave(137)", 1),
    ("if w < 136", "if w < 137", 3),
    ("range(17, 136)", "range(17, 137)", 1),
    ("range(16, 136)", "range(16, 137)", 1),
    ("w136_a", "w137_a", 8),
    ("w136_b", "w137_b", 8),  # 9th raw hit = "_r741bma_w136_band_gate.py" substring, consumed by the receipt needle above (substring-order law)
    ("n3r1_used136", "n3r1_used137", 3),
    ("n1w136", "n1w137", 2), ("n1_w136", "n1_w137", 2),
]
face = rep(face, specific, "face")

# --- 0d. B-face semantic needles: honest 12-hop forward walk (NOT arithmetic) --
# band-facts comment B part (post-0a form)
old_bfacts = """# B = the arithmetic continuation from the registered W136
        # B tail (CLEAN hops=0 at both windows; double-CLEAN window;
        # cross-window convergence with the r740 W136 seat MSG-1933 tail
        # W137+ projection)."""
new_bfacts = """# B = the FIRST-CLEAN window after the honest 12-hop
        # forward walk past the registered W136 B tail (first window
        # 69_902..70_101 refused by the N3-R1 used-seed band
        # 70_000..70_005 + the contiguous registered 2_000-wide bands
        # 70_001..94_000; non-rotational r587: every hop a strict
        # forward jump; cross-window convergence with the r741 W136
        # gate-tail projection, seat MSG-1952 tail, re-derived)."""
assert face.count(old_bfacts) == 1, "face: band-facts B comment needle"
face = face.replace(old_bfacts, new_bfacts)

# B assert block (post-0a/0b/WAVE_CONFIGS-rename form) -- three sub-needles,
# none crossing a backslash-newline (a literal \+newline inside a triple-quoted
# needle is a Python line-continuation and gets swallowed = silent no-match;
# caught at first run, sub-needle split per r735 measurement law)
face = rep(face, [
    ('["b_exit_seed_base"] == 69_702 == 69_701 + 1, (\n            "W137 B must be the arithmetic continuation past the W136 "\n            "registered B band tail (CLEAN hops=0 at both the pre-seat "\n            "probe and the freeze-window gate; double-CLEAN window)")',
     '["b_exit_seed_base"] == 94_001, (\n            "W137 B must be the FIRST-CLEAN window after the honest "\n            "12-hop forward walk past the W136 registered B band tail "\n            "(first window 69_902..70_101 refused by the N3-R1 used-"\n            "seed band + contiguous registered 2_000-wide bands "\n            "70_001..94_000; non-rotational r587: every hop a strict "\n            "forward jump past the refusing band)")', 1),
    ("arith_b137 = set(range(69_702, 69_902))",
     "arith_b137 = set(range(94_001, 94_201))", 1),
    ('"W137 B window must be CLEAN (arithmetic ADMIT face, hops=0)"',
     '"W137 B window must be CLEAN (honest forward-walk ADMIT face)"', 1),
], "face-bblock")

# --- 0e. registered row parity block shift LAST (W132..W135 -> W133..W136) ---
# NOTE: the 0a blanket shift has ALREADY shifted the [134]/[135] assert labels
# (W134->W135, W135->W136); the [132]/[133] labels are untouched by 0a.
old_parity = '''assert pf.N1_BANDS[132] == {"a": (307_004, 309_003),
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
            "registered W135 row parity drift (r307; bm-a r739)"
        assert pf.N1_BANDS[135] == {"a": (313_004, 315_003),
                                    "b_exit": (69_502, 69_701),
                                    "engine_owner": "bm-a"}, \\
            "registered W136 row parity drift (r307; bm-a r740)"'''
new_parity = '''assert pf.N1_BANDS[133] == {"a": (309_004, 311_003),
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
            "registered W135 row parity drift (r307; bm-a r740)"
        assert pf.N1_BANDS[136] == {"a": (315_004, 317_003),
                                    "b_exit": (69_702, 69_901),
                                    "engine_owner": "bm-a"}, \\
            "registered W136 row parity drift (r307; bm-a r741)"'''
assert face.count(old_parity) == 1, "face: row-parity block needle"
face = face.replace(old_parity, new_parity)

io.open(r".codely-cli\scratch_w137_face.txt", "w", encoding="utf-8", newline="\n").write(face)
print("face: W137 block transformed")

# ============ 1. perpetual_faces.py N1_BANDS row 137 ============
pf_path = r"scripts\perpetual_faces.py"
pf_src = io.open(pf_path, encoding="utf-8").read()
if '137: {"a": (317_004' in pf_src:
    print("pf: row 137 already present (idempotent skip)")
else:
    w136_row = '''    136: {"a": (315_004, 317_003), "b_exit": (69_702, 69_901),
         "engine_owner": "bm-a"},
}'''
    assert pf_src.count(w136_row) == 1, "pf: W136 row + closing brace needle"
    w137_block = '''    136: {"a": (315_004, 317_003), "b_exit": (69_702, 69_901),
         "engine_owner": "bm-a"},
    # W137 (bm-a r742 freeze, seat MSG-2026-10-05-202x-bma-w137-seat
    # pushed to origin af1c3c267 pre-freeze r565 law (push raced origin
    # forward 2 commits = r524 behind-signal (bm-c r570 same-window
    # wave), merge-mode zero-UU closeout, delivery d28d392ce); band
    # gate ADMIT results/_r742bma_w137_band_gate.py: A arithmetic
    # continuation 317_003+1 -> 317_004..319_003 CLEAN hops=0; B =
    # FIRST-CLEAN window after the honest 12-hop forward walk past
    # the W136 B tail (first window 69_902..70_101 refused by the
    # N3-R1 used-seed band 70_000..70_005 + the contiguous
    # registered 2_000-wide bands 70_001..94_000; non-rotational
    # r587: every hop a strict forward jump; per-hop chain
    # machine-traced in results/_r742bma_w137_probe_receipt.json);
    # dual-window derive parity with pre-seat probe; scan face =
    # SEED_REGISTRY 187 int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W138+ projection (gate-derived r742): A 319_004..321_003
    # CLEAN hops=0; B first-clean 94_201..94_400 CLEAN hops=0
    # double-CLEAN (next freezer must re-derive, never transcribe
    # r587 law).
    # NOT a re-pick (R250: W137 bands were never assigned).
    137: {"a": (317_004, 319_003), "b_exit": (94_001, 94_200),
         "engine_owner": "bm-a"},
}'''
    pf_src = pf_src.replace(w136_row, w137_block)
    io.open(pf_path, "w", encoding="utf-8", newline="\n").write(pf_src)
    print("pf: N1_BANDS row 137 inserted")

print("PART 1 DONE (face + pf row)")
