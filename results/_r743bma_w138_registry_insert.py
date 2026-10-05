# -*- coding: utf-8 -*-
"""r743 bm-a W138 registry insertion PART 1: transform the extracted W137 face
-> W138 face (.codely-cli/scratch_w138_face.txt) + N1_BANDS row 138
(perpetual_faces.py). All insertions needle-asserted; idempotent guards.
Bloodline: r742 _r742bma_w137_registry_insert.py verbatim + W138 facts
(A = arithmetic continuation from the registered W137 A tail 319_003+1,
CLEAN hops=0; B = arithmetic continuation from the registered W137 B
tail 94_200+1, first window CLEAN by construction, double-CLEAN window,
zero hops -- the W137 honest 12-hop forward walk landed past the
contiguous registered band mass 70_001..94_000).
r735 codegen pit laws enforced: (1) all new-block assert messages
single-line or parenthesized; (2) rep() expects measured on
post-prior-replacement text (measurement pass results/_r743bma_w138_extract.py
printed every count verbatim before this script was written; w137_b raw=9
with the 9th hit inside the band-gate receipt needle consumed FIRST).
r741 dep-line law: dep lines keep the post-0a W number, advance only the
r number (W137 finalize one-pass = bm-a r743 THIS window).
r740 parity-label law: parity old-needle takes post-0a label forms
([135] shows W136 label, [136] shows W137 label), new block written clean.
r742 backslash law: zero literal backslashes in any needle (parity
continuation built via chr(92); B-block/race needles triple-quoted with
real newlines, no backslash-newline boundary)."""
import io

BS = chr(92)
NL = chr(10)


def rep(src, pairs, tag):
    for old, new, expect in pairs:
        n = src.count(old)
        assert n == expect, f"{tag}: needle count={n} expect={expect}: {old[:60]!r}"
        src = src.replace(old, new)
    return src

# ============ 0. transform the extracted W137 face -> W138 face ============
face = io.open(r".codely-cli\scratch_w137_face_source.txt", encoding="utf-8").read()

# --- 0a. blanket wave-number shift FIRST (uppercase; then verified needles) ---
n_w137 = face.count("W137"); n_w136 = face.count("W136"); n_w135 = face.count("W135")
face = face.replace("W137", "W138")
face = face.replace("W136", "W137")
face = face.replace("W135", "W136")
assert face.count("W138") == n_w137 and face.count("W137") == n_w136 \
    and face.count("W136") == n_w135 and face.count("W135") == 0, \
    "blanket count check"

# --- 0b. A-block seed-value needles (arithmetic continuation from W137 A tail) ---
face = rep(face, [
    ("== 317_004 == 317_003 + 1", "== 319_004 == 319_003 + 1", 1),
    ("set(range(317_004, 319_004))", "set(range(319_004, 321_004))", 1),
    ("arith_a137", "arith_a138", 2),
    ("arith_b137", "arith_b138", 2),
], "face-0b")

# --- 0c. specific needles (counts measured post-0a/0b by the measurement
#     pass results/_r743bma_w138_extract.py; the receipt/seat needles run
#     FIRST because of the substring-order law -- the band-gate receipt
#     needle carries a w137_b substring, consuming the 9th raw hit; the
#     parity label replacements run LAST in 0e) ---
specific = [
    # receipt/seat needles FIRST (substring-order law)
    ("_r742bma_w137_band_gate.py", "_r743bma_w138_band_gate.py", 1),
    ("MSG-2026-10-05-202x-bma-w137-seat", "MSG-2026-10-05-211x-bma-w138-seat", 1),
    ("bm-a r741 freeze 7cafbc7ab", "bm-a r742 freeze f9e4ec5d2", 1),
    ("to origin af1c3c267 BEFORE", "to origin 0bf01ef64 BEFORE", 1),
    ("W137 finalize one-pass bm-a r742", "W137 finalize one-pass bm-a r743", 1),
    ("= W137 bm-a r742 one-pass", "= W137 bm-a r743 one-pass", 1),
    ("net chain head 695,211", "net chain head 697,411", 2),
    ("K=297,120", "K=299,320", 1),
    ("ONE HUNDRED-AND-TWENTY-SEVENTH", "ONE HUNDRED-AND-TWENTY-EIGHTH", 1),
    ("fifty-third", "fifty-fourth", 1),
    ("(r742 bm-a freeze", "(r743 bm-a freeze", 1),
    ("(law sec.4 W138 row, r742)", "(law sec.4 W138 row, r743)", 1),
    ("wave 137 = first free number", "wave 138 = first free number", 1),
    ("rows 52 + candidate", "rows 53 + candidate", 1),
    ("rows 126 + candidate", "rows 127 + candidate", 1),
    ("below 137 composes", "below 138 composes", 1),
    ("WAVE_CONFIGS[137]", "WAVE_CONFIGS[138]", 5),
    ("pf.N1_BANDS[137]", "pf.N1_BANDS[138]", 3),
    ("_set_wave(137)", "_set_wave(138)", 1),
    ("if w < 137", "if w < 138", 3),
    ("range(17, 137)", "range(17, 138)", 1),
    ("range(16, 137)", "range(16, 138)", 1),
    ("w137_a", "w138_a", 8),
    ("w137_b", "w138_b", 8),  # 9th raw hit = "_r742bma_w137_band_gate.py" substring, consumed by the receipt needle above (substring-order law)
    ("n3r1_used137", "n3r1_used138", 3),
    ("n1w137", "n1w138", 2), ("n1_w137", "n1_w138", 2),
]
face = rep(face, specific, "face")

# --- 0c-2. seat-push race prose needle (triple-quoted, real newlines, no backslash) --
old_race = '''pre-freeze push raced origin forward 2
    #     commits = r524 behind-signal (bm-c r570 same-window
    #     wave), merge-mode zero-UU closeout, delivery
    #     d28d392ce)'''
new_race = '''pre-freeze push raced origin forward 3
    #     commits = r524 behind-signal (bm-b r745 same-window
    #     wave), merge-mode clean auto-merge closeout, delivery
    #     576b22603)'''
assert face.count(old_race) == 1, "face: seat-push race needle"
face = face.replace(old_race, new_race)

# --- 0d. B-face semantic needles: arithmetic continuation (NOT first-clean) --
# band-facts comment B part (post-0a form)
old_bfacts = '''# B = the FIRST-CLEAN window after the honest 12-hop
        # forward walk past the registered W137 B tail (first window
        # 69_902..70_101 refused by the N3-R1 used-seed band
        # 70_000..70_005 + the contiguous registered 2_000-wide bands
        # 70_001..94_000; non-rotational r587: every hop a strict
        # forward jump; cross-window convergence with the r741 W137
        # gate-tail projection, seat MSG-1952 tail, re-derived).'''
new_bfacts = '''# B = the arithmetic continuation from the registered W137
        # B tail (CLEAN hops=0 at both windows; double-CLEAN window;
        # the W137 honest 12-hop forward walk landed past the
        # contiguous registered band mass 70_001..94_000, so the
        # continuation is clean by construction; cross-window
        # convergence with the r742 W137 gate-tail projection, seat
        # MSG-202x tail, re-derived).'''
assert face.count(old_bfacts) == 1, "face: band-facts B comment needle"
face = face.replace(old_bfacts, new_bfacts)

# B assert block (post-0a/0b form) -- triple-quoted real-newline needles,
# zero literal backslashes (r742 backslash-newline swallow law: no needle
# crosses a backslash-newline boundary)
old_bblock = '''["b_exit_seed_base"] == 94_001, (
            "W138 B must be the FIRST-CLEAN window after the honest "
            "12-hop forward walk past the W137 registered B band tail "
            "(first window 69_902..70_101 refused by the N3-R1 used-"
            "seed band + contiguous registered 2_000-wide bands "
            "70_001..94_000; non-rotational r587: every hop a strict "
            "forward jump past the refusing band)")'''
new_bblock = '''["b_exit_seed_base"] == 94_201 == 94_200 + 1, (
            "W138 B must be the arithmetic continuation past the W137 "
            "registered B band tail (CLEAN hops=0 at both the pre-seat "
            "probe and the freeze-window gate; double-CLEAN window)")'''
face = rep(face, [
    (old_bblock, new_bblock, 1),
    ("arith_b138 = set(range(94_001, 94_201))",
     "arith_b138 = set(range(94_201, 94_401))", 1),
    ('"W138 B window must be CLEAN (honest forward-walk ADMIT face)"',
     '"W138 B window must be CLEAN (arithmetic ADMIT face, hops=0)"', 1),
], "face-bblock")

# --- 0e. registered row parity label fixes + [137] row insertion LAST ---
# r740 parity-label law: 0a has already shifted the [135]/[136] assert
# LABELS (W135->W136, W136->W137); [133]/[134] labels untouched by 0a.
# No needle crosses a backslash-newline boundary (continuation built via chr(92)).
face = rep(face, [
    ('"registered W136 row parity drift (r307; bm-a r740)"',
     '"registered W135 row parity drift (r307; bm-a r740)"', 1),
], "face-parity-135")
new_137_block = (
    '"registered W136 row parity drift (r307; bm-a r741)"' + NL
    + '        assert pf.N1_BANDS[137] == {"a": (317_004, 319_003),' + NL
    + '                                    "b_exit": (94_001, 94_200),' + NL
    + '                                    "engine_owner": "bm-a"}, ' + BS + NL
    + '            "registered W137 row parity drift (r307; bm-a r742)"'
)
face = rep(face, [
    ('"registered W137 row parity drift (r307; bm-a r741)"',
     new_137_block, 1),
], "face-parity-136")

io.open(r".codely-cli\scratch_w138_face.txt", "w", encoding="utf-8", newline="\n").write(face)
print("face: W138 block transformed")

# ============ 1. perpetual_faces.py N1_BANDS row 138 ============
pf_path = r"scripts\perpetual_faces.py"
pf_src = io.open(pf_path, encoding="utf-8").read()
if '138: {"a": (319_004' in pf_src:
    print("pf: row 138 already present (idempotent skip)")
else:
    w137_row = '''    137: {"a": (317_004, 319_003), "b_exit": (94_001, 94_200),
         "engine_owner": "bm-a"},
}'''
    assert pf_src.count(w137_row) == 1, "pf: W137 row + closing brace needle"
    w138_block = '''    137: {"a": (317_004, 319_003), "b_exit": (94_001, 94_200),
         "engine_owner": "bm-a"},
    # W138 (bm-a r743 freeze, seat MSG-2026-10-05-211x-bma-w138-seat
    # pushed to origin 0bf01ef64 pre-freeze r565 law (push raced origin
    # forward 3 commits = r524 behind-signal (bm-b r745 same-window
    # wave), merge-mode clean auto-merge closeout, delivery 576b22603);
    # band gate ADMIT results/_r743bma_w138_band_gate.py: A arithmetic
    # continuation 319_003+1 -> 319_004..321_003 CLEAN hops=0; B =
    # arithmetic continuation from the W137 B tail 94_200+1 ->
    # 94_201..94_400 CLEAN hops=0 (double-CLEAN window; the W137
    # honest 12-hop forward walk landed past the contiguous
    # registered band mass 70_001..94_000, clean by construction);
    # dual-window derive parity with pre-seat probe
    # results/_r743bma_w138_probe_receipt.json; scan face =
    # SEED_REGISTRY 187 int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W139+ projection (gate-derived r743): A 321_004..323_003
    # CLEAN hops=0; B first-clean 94_401..94_600 CLEAN hops=0
    # double-CLEAN (next freezer must re-derive, never transcribe
    # r587 law).
    # NOT a re-pick (R250: W138 bands were never assigned).
    138: {"a": (319_004, 321_003), "b_exit": (94_201, 94_400),
         "engine_owner": "bm-a"},
}'''
    pf_src = pf_src.replace(w137_row, w138_block)
    io.open(pf_path, "w", encoding="utf-8", newline="\n").write(pf_src)
    print("pf: N1_BANDS row 138 inserted")

print("PART 1 DONE (face + pf row)")
