# -*- coding: utf-8 -*-
"""r747 bm-a W141 registry insertion PART 1: transform the extracted W140 face
-> W141 face (.codely-cli/scratch_w141_face.txt) + N1_BANDS row 141
(perpetual_faces.py). All insertions needle-asserted; idempotent guards.
Bloodline: r745 _r745bma_w140_registry_insert.py verbatim + W141 facts
(A = arithmetic continuation from the registered W140 A tail 325_003+1,
CLEAN hops=0; B = FIRST-CLEAN past the own-wave A window -- the arithmetic
continuation 94_801..95_000 is REFUSED by probe seed 95_000; the honest
forward walk hops=116 lands 325_004..325_203 inside the W141 A band
window; same-freeze mutual exclusion (leg2 law) -> B continues past the
own-wave A window, first-clean 327_004..327_203 hops=117).
r735 codegen pit laws enforced: (1) all new-block assert messages
single-line or parenthesized; (2) rep() expects measured on
post-prior-replacement text (measurement pass results/_r747bma_w141_extract.py
printed every count verbatim before this script was written; w140_b raw=9
with the 9th hit inside the band-gate receipt needle consumed FIRST).
r741 dep-line law: dep lines keep the post-0a W number, advance only the
r number (W140 finalize one-pass = bm-a r746 THAT window).
r740 parity-label law: parity old-needle takes post-0a label forms
([138] shows W139 label, [139] shows W140 label), new block written clean.
r742 backslash law: zero literal backslashes in any needle (parity
continuation built via chr(92); all needles cross no backslash-newline
boundary)."""
import io

BS = chr(92)
NL = chr(10)


def rep(src, pairs, tag):
    for old, new, expect in pairs:
        n = src.count(old)
        assert n == expect, f"{tag}: needle count={n} expect={expect}: {old[:60]!r}"
        src = src.replace(old, new)
    return src

# ============ 0. transform the extracted W140 face -> W141 face ============
face = io.open(r".codely-cli\scratch_w140_face_source.txt", encoding="utf-8").read()

# --- 0a. blanket wave-number shift FIRST (uppercase; then verified needles) ---
n_w140 = face.count("W140"); n_w139 = face.count("W139"); n_w138 = face.count("W138")
face = face.replace("W140", "W141")
face = face.replace("W139", "W140")
face = face.replace("W138", "W139")
assert face.count("W141") == n_w140 and face.count("W140") == n_w139 \
    and face.count("W139") == n_w138 and face.count("W138") == 0, \
    "blanket count check"

# --- 0b. A-block seed-value needles + B-block semantic value swaps ---
face = rep(face, [
    ("== 323_004 == 323_003 + 1", "== 325_004 == 325_003 + 1", 1),
    ("set(range(323_004, 325_004))", "set(range(325_004, 327_004))", 1),
    ("set(range(94_601, 94_801))", "set(range(327_004, 327_204))", 1),
    ("arith_a140", "arith_a141", 2),
    ("arith_b140", "arith_b141", 2),
], "face-0b")

# --- 0c. specific needles (counts measured post-0a/0b by the measurement
#     pass results/_r747bma_w141_extract.py; the receipt/seat needles run
#     FIRST because of the substring-order law -- the band-gate receipt
#     needle carries a w140_b substring, consuming the 9th raw hit) ---
specific = [
    # receipt/seat needles FIRST (substring-order law)
    ("_r745bma_w140_band_gate.py", "_r747bma_w141_band_gate.py", 1),
    ("MSG-2026-10-05-215x-bma-w140-seat", "MSG-2026-10-05-231x-bma-w141-seat", 1),
    ("bm-a r744 freeze 4e3a018c7", "bm-a r745 freeze 5e3984200", 1),
    ("to origin 08710e2d0 BEFORE", "to origin aaa4d9be8 BEFORE", 1),
    ("W140 finalize one-pass bm-a r745", "W140 finalize one-pass bm-a r746", 1),
    ("= W140 bm-a r745 one-pass", "= W140 bm-a r746 one-pass", 1),
    ("net chain head 701,811", "net chain head 704,011", 2),
    ("K=303,720", "K=305,920", 1),
    ("ONE HUNDRED-AND-THIRTIETH", "ONE HUNDRED-AND-THIRTY-FIRST", 1),
    ("fifty-sixth", "fifty-seventh", 1),
    ("(r745 bm-a freeze", "(r747 bm-a freeze", 1),
    ("(law sec.4 W141 row, r745)", "(law sec.4 W141 row, r747)", 1),
    ("wave 140 = first free number", "wave 141 = first free number", 1),
    ("rows 55 + candidate", "rows 56 + candidate", 1),
    ("rows 129 + candidate", "rows 130 + candidate", 1),
    ("below 140 composes", "below 141 composes", 1),
    ("WAVE_CONFIGS[140]", "WAVE_CONFIGS[141]", 5),
    ("pf.N1_BANDS[140]", "pf.N1_BANDS[141]", 3),
    ("_set_wave(140)", "_set_wave(141)", 1),
    ("if w < 140", "if w < 141", 3),
    ("range(17, 140)", "range(17, 141)", 1),
    ("range(16, 140)", "range(16, 141)", 1),
    ("w140_a", "w141_a", 8),
    ("w140_b", "w141_b", 8),  # 9th raw hit = "_r745bma_w140_band_gate.py" substring, consumed by the receipt needle above (substring-order law)
    ("n3r1_used140", "n3r1_used141", 3),
    ("n1w140", "n1w141", 2), ("n1_w140", "n1_w141", 2),
    ("== 94_601 == 94_600 + 1", "== 327_004 == 327_003 + 1", 1),
]
face = rep(face, specific, "face")

# --- 0c-2. seat-push race prose needle (triple-quoted, real newlines, no backslash) ---
old_race = '''pre-freeze push plain fast-forward delivery
    #     08710e2d0, zero race this window (behind 0 at fetch),
    #     zero --no-verify)'''
new_race = '''pre-freeze push plain fast-forward delivery
    #     aaa4d9be8, zero race this window (behind 0 at fetch),
    #     zero --no-verify)'''
assert face.count(old_race) == 1, "face: seat-push race needle"
face = face.replace(old_race, new_race)

# --- 0d. B-face semantic needles: band-facts comment + B assert message ---
# post-0a forms (measurement pass verified); no backslash in either needle.
old_bfacts = '''# B = the arithmetic continuation from the registered W140
        # B tail (CLEAN hops=0 at both windows; double-CLEAN
        # continuation window; the W140 zero-hop double-CLEAN
        # continuation landed past the contiguous registered band
        # mass 70_001..94_600, so the continuation is clean by
        # construction; cross-window convergence with the r744
        # W140 gate-tail projection, seat MSG-215x tail, re-derived).'''
new_bfacts = '''# B = FIRST-CLEAN past the own-wave A window (the arithmetic
        # continuation 94_801..95_000 is REFUSED by probe seed 95_000;
        # the honest forward walk from 94_801 lands 325_004..325_203
        # inside the W141 A band window after 116 hops -- same-freeze
        # mutual exclusion (leg2 law) -- the walk continues past the
        # own-wave A window and lands 327_004..327_203, hops=117,
        # non-rotational r587 forward-monotone walk; B base == own-wave
        # A tail+1 (327_003+1) machine-checkable; cross-window
        # convergence with the r745 W140 gate-tail projection -- the
        # re-derive-MANDATORY note honored, the own-A hop is the
        # additional honest face, disclosed; seat MSG-231x tail,
        # re-derived).'''
assert face.count(old_bfacts) == 1, "face: band-facts B comment needle"
face = face.replace(old_bfacts, new_bfacts)

old_bmsg = '''"W141 B must be the arithmetic continuation past the W140 "
            "registered B band tail (CLEAN hops=0 at both the pre-seat "
            "probe and the freeze-window gate; double-CLEAN window)")'''
new_bmsg = '''"W141 B must be the first-clean window past the own-wave A "
            "band tail 327_003+1 (arithmetic continuation 94_801..95_000 "
            "REFUSED by probe seed 95_000; honest forward walk hops=116 "
            "lands 325_004..325_203 inside the W141 A band window; "
            "same-freeze mutual exclusion (leg2 law) -- B continues "
            "past the own-wave A window, first-clean hops=117, "
            "non-rotational r587 forward-monotone walk; B base == "
            "own-wave A tail+1 machine-checkable)")'''
assert face.count(old_bmsg) == 1, "face: B assert message needle"
face = face.replace(old_bmsg, new_bmsg)

# B CLEAN label swap + same-freeze mutual-exclusion assert append
# (label is single-line; the appended assert continuation is built via chr(92))
old_blabel = '"W141 B window must be CLEAN (arithmetic ADMIT face, hops=0)"'
new_blabel = ('"W141 B window must be CLEAN (first-clean ADMIT face past '
              'own-wave A)"' + NL
              + '        assert not (arith_b141 & arith_a141), ' + BS + NL
              + '            "W141 A/B same-freeze mutual exclusion '
              '(B hops past own A)"')
assert face.count(old_blabel) == 1, "face: B CLEAN label needle"
face = face.replace(old_blabel, new_blabel)

# --- 0e. registered row parity label fixes + [140] row insertion LAST ---
# r740 parity-label law: 0a has already shifted the [138]/[139] assert
# LABELS (W138->W139, W139->W140); [133]..[137] labels untouched by 0a
# (not in the 0a key set W140/W139/W138).
# No needle crosses a backslash-newline boundary (continuation built via chr(92)).
face = rep(face, [
    ('"registered W139 row parity drift (r307; bm-a r743)"',
     '"registered W138 row parity drift (r307; bm-a r743)"', 1),
], "face-parity-138")
new_140_block = (
    '"registered W139 row parity drift (r307; bm-a r744)"' + NL
    + '        assert pf.N1_BANDS[140] == {"a": (323_004, 325_003),' + NL
    + '                                    "b_exit": (94_601, 94_800),' + NL
    + '                                    "engine_owner": "bm-a"}, ' + BS + NL
    + '            "registered W140 row parity drift (r307; bm-a r745)"'
)
face = rep(face, [
    ('"registered W140 row parity drift (r307; bm-a r744)"',
     new_140_block, 1),
], "face-parity-139")

io.open(r".codely-cli\scratch_w141_face.txt", "w", encoding="utf-8", newline="\n").write(face)
print("face: W141 block transformed", face.count("W141"), "W141 mentions")

# ============ 1. perpetual_faces.py N1_BANDS row 141 ============
pf_path = r"scripts\perpetual_faces.py"
pf_src = io.open(pf_path, encoding="utf-8").read()
if '141: {"a": (325_004' in pf_src:
    print("pf: row 141 already present (idempotent skip)")
else:
    w140_row = '''    140: {"a": (323_004, 325_003), "b_exit": (94_601, 94_800),
         "engine_owner": "bm-a"},
}'''
    assert pf_src.count(w140_row) == 1, "pf: W140 row + closing brace needle"
    w141_block = '''    140: {"a": (323_004, 325_003), "b_exit": (94_601, 94_800),
         "engine_owner": "bm-a"},
    # W141 (bm-a r747 freeze, seat MSG-2026-10-05-231x-bma-w141-seat
    # pushed to origin aaa4d9be8 pre-freeze r565 law (plain
    # fast-forward delivery, zero race this window, zero
    # --no-verify);
    # band gate ADMIT results/_r747bma_w141_band_gate.py: A arithmetic
    # continuation 325_003+1 -> 325_004..327_003 CLEAN hops=0; B =
    # FIRST-CLEAN past the own-wave A window (arithmetic continuation
    # 94_801..95_000 REFUSED by probe seed 95_000; honest forward walk
    # hops=116 lands 325_004..325_203 inside the W141 A band window;
    # same-freeze mutual exclusion (leg2 law) -- B continues past the
    # own-wave A window -> 327_004..327_203 hops=117, non-rotational
    # r587 forward-monotone walk; B base == own-wave A tail+1);
    # dual-window derive parity with pre-seat probe
    # results/_r747bma_w141_probe_receipt.json; scan face =
    # SEED_REGISTRY 187 int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W142+ projection (gate-derived r747): A first-clean
    # 327_004..329_003 CLEAN hops=0 / B first-clean 327_204..327_403
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W141 B band will refuse the naive W142 A window;
    # W142 freezer MUST re-derive on the post-W141 universe AND
    # reserve the own-wave A window when deriving B (W141 precedent,
    # same-freeze mutual exclusion, leg2 law; never transcribe r587).
    # NOT a re-pick (R250: W141 bands were never assigned).
    141: {"a": (325_004, 327_003), "b_exit": (327_004, 327_203),
         "engine_owner": "bm-a"},
}'''
    pf_src = pf_src.replace(w140_row, w141_block)
    io.open(pf_path, "w", encoding="utf-8", newline="\n").write(pf_src)
    print("pf: N1_BANDS row 141 inserted")

print("PART 1 DONE (face + pf row)")
