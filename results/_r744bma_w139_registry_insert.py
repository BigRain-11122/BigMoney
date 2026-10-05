# -*- coding: utf-8 -*-
"""r744 bm-a W139 registry insertion PART 1: transform the extracted W138 face
-> W139 face (.codely-cli/scratch_w139_face.txt) + N1_BANDS row 139
(perpetual_faces.py). All insertions needle-asserted; idempotent guards.
Bloodline: r743 _r743bma_w138_registry_insert.py verbatim + W139 facts
(A = arithmetic continuation from the registered W138 A tail 321_003+1,
CLEAN hops=0; B = arithmetic continuation from the registered W138 B
tail 94_400+1, first window CLEAN by construction, double-CLEAN
continuation window, zero hops -- the W137 honest 12-hop forward walk
landed past the contiguous registered band mass 70_001..94_000 and the
W138 zero-hop continuation extended it to 94_400).
r735 codegen pit laws enforced: (1) all new-block assert messages
single-line or parenthesized; (2) rep() expects measured on
post-prior-replacement text (measurement pass results/_r744bma_w139_extract.py
printed every count verbatim before this script was written; w138_b raw=9
with the 9th hit inside the band-gate receipt needle consumed FIRST).
r741 dep-line law: dep lines keep the post-0a W number, advance only the
r number (W138 finalize one-pass = bm-a r744 THIS window).
r740 parity-label law: parity old-needle takes post-0a label forms
([136] shows W137 label, [137] shows W138 label), new block written clean.
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

# ============ 0. transform the extracted W138 face -> W139 face ============
face = io.open(r".codely-cli\scratch_w138_face_source.txt", encoding="utf-8").read()

# --- 0a. blanket wave-number shift FIRST (uppercase; then verified needles) ---
n_w138 = face.count("W138"); n_w137 = face.count("W137"); n_w136 = face.count("W136")
face = face.replace("W138", "W139")
face = face.replace("W137", "W138")
face = face.replace("W136", "W137")
assert face.count("W139") == n_w138 and face.count("W138") == n_w137 \
    and face.count("W137") == n_w136 and face.count("W136") == 0, \
    "blanket count check"

# --- 0b. A-block seed-value needles (arithmetic continuation from W138 A tail) ---
face = rep(face, [
    ("== 319_004 == 319_003 + 1", "== 321_004 == 321_003 + 1", 1),
    ("set(range(319_004, 321_004))", "set(range(321_004, 323_004))", 1),
    ("arith_a138", "arith_a139", 2),
    ("arith_b138", "arith_b139", 2),
], "face-0b")

# --- 0c. specific needles (counts measured post-0a/0b by the measurement
#     pass results/_r744bma_w139_extract.py; the receipt/seat needles run
#     FIRST because of the substring-order law -- the band-gate receipt
#     needle carries a w138_b substring, consuming the 9th raw hit) ---
specific = [
    # receipt/seat needles FIRST (substring-order law)
    ("_r743bma_w138_band_gate.py", "_r744bma_w139_band_gate.py", 1),
    ("MSG-2026-10-05-211x-bma-w138-seat", "MSG-2026-10-05-213x-bma-w139-seat", 1),
    ("bm-a r742 freeze f9e4ec5d2", "bm-a r743 freeze 6798a1e5f", 1),
    ("to origin 0bf01ef64 BEFORE", "to origin 7e1fc08d0 BEFORE", 1),
    ("W138 finalize one-pass bm-a r743", "W138 finalize one-pass bm-a r744", 1),
    ("= W138 bm-a r743 one-pass", "= W138 bm-a r744 one-pass", 1),
    ("net chain head 697,411", "net chain head 699,611", 2),
    ("K=299,320", "K=301,520", 1),
    ("ONE HUNDRED-AND-TWENTY-EIGHTH", "ONE HUNDRED-AND-TWENTY-NINTH", 1),
    ("fifty-fourth", "fifty-fifth", 1),
    ("(r743 bm-a freeze", "(r744 bm-a freeze", 1),
    ("(law sec.4 W139 row, r743)", "(law sec.4 W139 row, r744)", 1),
    ("wave 138 = first free number", "wave 139 = first free number", 1),
    ("rows 53 + candidate", "rows 54 + candidate", 1),
    ("rows 127 + candidate", "rows 128 + candidate", 1),
    ("below 138 composes", "below 139 composes", 1),
    ("WAVE_CONFIGS[138]", "WAVE_CONFIGS[139]", 5),
    ("pf.N1_BANDS[138]", "pf.N1_BANDS[139]", 3),
    ("_set_wave(138)", "_set_wave(139)", 1),
    ("if w < 138", "if w < 139", 3),
    ("range(17, 138)", "range(17, 139)", 1),
    ("range(16, 138)", "range(16, 139)", 1),
    ("w138_a", "w139_a", 8),
    ("w138_b", "w139_b", 8),  # 9th raw hit = "_r743bma_w138_band_gate.py" substring, consumed by the receipt needle above (substring-order law)
    ("n3r1_used138", "n3r1_used139", 3),
    ("n1w138", "n1w139", 2), ("n1_w138", "n1_w139", 2),
    ("== 94_201 == 94_200 + 1", "== 94_401 == 94_400 + 1", 1),
]
face = rep(face, specific, "face")

# --- 0c-2. seat-push race prose needle (triple-quoted, real newlines, no backslash) --
old_race = '''pre-freeze push raced origin forward 3
    #     commits = r524 behind-signal (bm-b r745 same-window
    #     wave), merge-mode clean auto-merge closeout, delivery
    #     576b22603)'''
new_race = '''pre-freeze push raced origin forward 7
    #     commits = r524 behind-signal (bm-b r746 same-window
    #     wave), merge-mode clean auto-merge closeout, delivery
    #     39ec08fa0)'''
assert face.count(old_race) == 1, "face: seat-push race needle"
face = face.replace(old_race, new_race)

# --- 0d. B-face semantic needle: band-facts comment (post-0a form) --
# fixes the FALSE "W138 honest 12-hop" history (W138 was zero-hop; the
# 12-hop walk was W137's) + advances the gate-tail/seat references.
old_bfacts = '''# B = the arithmetic continuation from the registered W138
        # B tail (CLEAN hops=0 at both windows; double-CLEAN window;
        # the W138 honest 12-hop forward walk landed past the
        # contiguous registered band mass 70_001..94_000, so the
        # continuation is clean by construction; cross-window
        # convergence with the r742 W138 gate-tail projection, seat
        # MSG-202x tail, re-derived).'''
new_bfacts = '''# B = the arithmetic continuation from the registered W138
        # B tail (CLEAN hops=0 at both windows; double-CLEAN
        # continuation window; the W137 honest 12-hop forward walk
        # landed past the contiguous registered band mass
        # 70_001..94_000 and the W138 zero-hop continuation extended
        # it to 94_400, so the continuation is clean by construction;
        # cross-window convergence with the r743 W138 gate-tail
        # projection, seat MSG-211x tail, re-derived).'''
assert face.count(old_bfacts) == 1, "face: band-facts B comment needle"
face = face.replace(old_bfacts, new_bfacts)

# --- 0e. registered row parity label fixes + [138] row insertion LAST ---
# r740 parity-label law: 0a has already shifted the [136]/[137] assert
# LABELS (W136->W137, W137->W138); [133]/[134]/[135] labels untouched by 0a
# (not in the 0a key set W138/W137/W136).
# No needle crosses a backslash-newline boundary (continuation built via chr(92)).
face = rep(face, [
    ('"registered W137 row parity drift (r307; bm-a r741)"',
     '"registered W136 row parity drift (r307; bm-a r741)"', 1),
], "face-parity-136")
new_138_block = (
    '"registered W137 row parity drift (r307; bm-a r742)"' + NL
    + '        assert pf.N1_BANDS[138] == {"a": (319_004, 321_003),' + NL
    + '                                    "b_exit": (94_201, 94_400),' + NL
    + '                                    "engine_owner": "bm-a"}, ' + BS + NL
    + '            "registered W138 row parity drift (r307; bm-a r743)"'
)
face = rep(face, [
    ('"registered W138 row parity drift (r307; bm-a r742)"',
     new_138_block, 1),
], "face-parity-137")

io.open(r".codely-cli\scratch_w139_face.txt", "w", encoding="utf-8", newline="\n").write(face)
print("face: W139 block transformed")

# ============ 1. perpetual_faces.py N1_BANDS row 139 ============
pf_path = r"scripts\perpetual_faces.py"
pf_src = io.open(pf_path, encoding="utf-8").read()
if '139: {"a": (321_004' in pf_src:
    print("pf: row 139 already present (idempotent skip)")
else:
    w138_row = '''    138: {"a": (319_004, 321_003), "b_exit": (94_201, 94_400),
         "engine_owner": "bm-a"},
}'''
    assert pf_src.count(w138_row) == 1, "pf: W138 row + closing brace needle"
    w139_block = '''    138: {"a": (319_004, 321_003), "b_exit": (94_201, 94_400),
         "engine_owner": "bm-a"},
    # W139 (bm-a r744 freeze, seat MSG-2026-10-05-213x-bma-w139-seat
    # pushed to origin 7e1fc08d0 pre-freeze r565 law (push raced origin
    # forward 7 commits = r524 behind-signal (bm-b r746 same-window
    # wave), merge-mode clean auto-merge closeout, delivery 39ec08fa0);
    # band gate ADMIT results/_r744bma_w139_band_gate.py: A arithmetic
    # continuation 321_003+1 -> 321_004..323_003 CLEAN hops=0; B =
    # arithmetic continuation from the W138 B tail 94_400+1 ->
    # 94_401..94_600 CLEAN hops=0 (double-CLEAN continuation window;
    # the W137 honest 12-hop forward walk landed past the contiguous
    # registered band mass 70_001..94_000 and the W138 zero-hop
    # continuation extended it to 94_400, clean by construction);
    # dual-window derive parity with pre-seat probe
    # results/_r744bma_w139_probe_receipt.json; scan face =
    # SEED_REGISTRY 187 int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W140+ projection (gate-derived r744): A 323_004..325_003
    # CLEAN hops=0; B first-clean 94_601..94_800 CLEAN hops=0
    # double-CLEAN (next freezer must re-derive, never transcribe
    # r587 law).
    # NOT a re-pick (R250: W139 bands were never assigned).
    139: {"a": (321_004, 323_003), "b_exit": (94_401, 94_600),
         "engine_owner": "bm-a"},
}'''
    pf_src = pf_src.replace(w138_row, w139_block)
    io.open(pf_path, "w", encoding="utf-8", newline="\n").write(pf_src)
    print("pf: N1_BANDS row 139 inserted")

print("PART 1 DONE (face + pf row)")
