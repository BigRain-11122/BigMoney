# -*- coding: utf-8 -*-
"""r752 bm-a W144 registry insertion PART 1: transform the extracted W143 face
-> W144 face (.codely-cli/scratch_w144_face.txt) + N1_BANDS row 144
(perpetual_faces.py). All insertions needle-asserted; idempotent guards.
Bloodline: r750 _r750bma_w143_registry_insert.py verbatim + W144 facts
(STAIRCASE GEOMETRY third instance, E36 card: A = first-clean past the
registered W143 B band -- the arithmetic continuation 331_404..333_403 is
REFUSED at its own start by the W143 B band 331_404..331_603, honest forward
walk hops=1, A base == prior-wave B tail+1 (331_603+1) machine-checkable,
A-hops-prior-B third instance; B = first-clean past the own-wave A window --
the arithmetic continuation 331_604..331_803 is CLEAN on the registered
universe but lands INSIDE the W144 own-wave A window, same-freeze mutual
exclusion (W141 precedent, leg2 law), reserved walk -> 333_604..333_803,
hops=1, B base == own-A tail+1 (333_603+1) machine-checkable).
r735 codegen pit laws enforced: (1) all new-block assert messages
single-line or parenthesized; (2) rep() expects measured on
post-prior-replacement text (measurement pass results/_r752bma_w144_extract.py
printed every count verbatim before this script was written; w143_b raw=9
with the 9th hit inside the band-gate receipt needle consumed FIRST).
r745 extract-vs-insert needle-set law: every needle measured by the extract
pass as transform-needed is carried below (band-gate receipt, seat MSG,
freeze sha, seat push sha x2, finalize dep lines, ledger head x2, K, ordinals,
wave-free line, rows x2, below-composes, WAVE_CONFIGS x5 [2 consumed by the
0d staircase rewrites, 3 at 0c], N1_BANDS mirror x3, set_wave, w<, range x2,
w143_a/w143_b, n3r1_used, n1w/n1_w, parity [141] label fix + [143] insert).
r741 dep-line law: dep lines keep the post-0a W number, advance only the
r number (W143 finalize one-pass = bm-a r751 THAT window, commit 6d93bd7ba).
r740 parity-label law: parity old-needles take post-0a label forms
([141] shows W142 label post-0a, [142] shows W143 label post-0a), new block
written clean.
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

# ============ 0. transform the extracted W143 face -> W144 face ============
face = io.open(r".codely-cli\scratch_w143_face_source.txt", encoding="utf-8").read()

# --- 0a. blanket wave-number shift FIRST (uppercase; then verified needles) ---
n_w143 = face.count("W143"); n_w142 = face.count("W142"); n_w141 = face.count("W141")
face = face.replace("W143", "W144")
face = face.replace("W142", "W143")
face = face.replace("W141", "W142")
assert face.count("W144") == n_w143 and face.count("W143") == n_w142 \
    and face.count("W142") == n_w141 and face.count("W141") == 0, \
    "blanket count check"

# --- 0b. arith-window + arith-name needles (A/B staircase asserts rewritten in 0d) ---
face = rep(face, [
    ("set(range(329_404, 331_404))", "set(range(331_604, 333_604))", 1),
    ("set(range(331_404, 331_604))", "set(range(333_604, 333_804))", 1),
    ("arith_a143", "arith_a144", 3),
    ("arith_b143", "arith_b144", 3),
], "face-0b")

# --- 0d. semantic block rewrites FIRST (they carry WAVE_CONFIGS[143] and the
#     A/B base values inside their old forms; the 0c WAVE_CONFIGS needle then
#     sees only the 3 mirror asserts) ---
# band-facts comment needle = the verbatim pre-0a block passed through the same
# 0a shift (exact-by-construction, zero hand-drift).
old_bfacts_pre = '''# band facts (law sec.4 W143 row, r750): A = FIRST-CLEAN past
        # the registered W142 B band (the arithmetic continuation
        # 329_204..331_203 is REFUSED at its own start by the W142
        # B band 329_204..329_403, exactly as the r748 W142 gate-tail
        # projection note anticipated; the honest forward walk hops=1
        # lands 329_404..331_403; A base == prior-wave B tail+1
        # (329_403+1) machine-checkable -- A-hops-prior-B staircase
        # second instance, E36 card; non-rotational r587
        # forward-monotone walk);
        # B = FIRST-CLEAN past the own-wave A window (the arithmetic
        # continuation 329_404..329_603 is CLEAN on the registered
        # universe but lands INSIDE the W143 A band window --
        # same-freeze mutual exclusion (W141 precedent, leg2 law) --
        # the walk with the own-wave A window reserved jumps to
        # 331_404 and lands 331_404..331_603, hops=1, non-rotational
        # r587 forward-monotone walk; B base == own-wave A tail+1
        # (331_403+1) machine-checkable; cross-window convergence
        # with the r748 W142 gate-tail projection -- both
        # MANDATORY notes honored (post-W142 universe re-derive +
        # own-wave A reservation when deriving B); seat MSG-002x
        # tail, re-derived).'''
old_bfacts = old_bfacts_pre.replace("W143", "W144").replace("W142", "W143").replace("W141", "W142")
new_bfacts = '''# band facts (law sec.4 W144 row, r752): A = FIRST-CLEAN past
        # the registered W143 B band (the arithmetic continuation
        # 331_404..333_403 is REFUSED at its own start by the W143
        # B band 331_404..331_603, exactly as the r750 W143 gate-tail
        # projection note anticipated; the honest forward walk hops=1
        # lands 331_604..333_603; A base == prior-wave B tail+1
        # (331_603+1) machine-checkable -- A-hops-prior-B staircase
        # third instance, E36 card; non-rotational r587
        # forward-monotone walk);
        # B = FIRST-CLEAN past the own-wave A window (the arithmetic
        # continuation 331_604..331_803 is CLEAN on the registered
        # universe but lands INSIDE the W144 A band window --
        # same-freeze mutual exclusion (W141 precedent, leg2 law) --
        # the walk with the own-wave A window reserved jumps to
        # 333_604 and lands 333_604..333_803, hops=1, non-rotational
        # r587 forward-monotone walk; B base == own-wave A tail+1
        # (333_603+1) machine-checkable; cross-window convergence
        # with the r750 W143 gate-tail projection -- both
        # MANDATORY notes honored (post-W143 universe re-derive +
        # own-wave A reservation when deriving B); seat MSG-011x
        # tail, re-derived).'''
assert face.count(old_bfacts) == 1, "face: band-facts comment needle"
face = face.replace(old_bfacts, new_bfacts)

old_aassert = '''assert WAVE_CONFIGS[143]["a_seed_base"] == 329_404 == 329_403 + 1, (
            "W144 A must be the first-clean window past the registered "
            "W143 B band tail 329_403+1 (arithmetic continuation "
            "329_204..331_203 REFUSED at its own start by the W143 B "
            "band 329_204..329_403, exactly as the r748 gate-tail "
            "projection note anticipated; honest forward walk hops=1; "
            "A base == prior-wave B tail+1 machine-checkable = "
            "A-hops-prior-B staircase second instance, E36 card)")'''
new_aassert = '''assert WAVE_CONFIGS[144]["a_seed_base"] == 331_604 == 331_603 + 1, (
            "W144 A must be the first-clean window past the registered "
            "W143 B band tail 331_603+1 (arithmetic continuation "
            "331_404..333_403 REFUSED at its own start by the W143 B "
            "band 331_404..331_603, exactly as the r750 gate-tail "
            "projection note anticipated; honest forward walk hops=1; "
            "A base == prior-wave B tail+1 machine-checkable = "
            "A-hops-prior-B staircase third instance, E36 card)")'''
assert face.count(old_aassert) == 1, "face: A assert block needle"
face = face.replace(old_aassert, new_aassert)

old_bassert = '''assert WAVE_CONFIGS[143]["b_exit_seed_base"] == 331_404 == 331_403 + 1, (
            "W144 B must be the first-clean window past the own-wave A "
            "band tail 331_403+1 (arithmetic continuation "
            "329_404..329_603 CLEAN on the registered universe but "
            "lands INSIDE the W144 A band window; same-freeze mutual "
            "exclusion (W142 precedent, leg2 law) -- the walk with the "
            "own-wave A window reserved jumps to 331_404, first-clean "
            "hops=1, non-rotational r587 forward-monotone walk; B "
            "base == own-wave A tail+1 machine-checkable)")'''
new_bassert = '''assert WAVE_CONFIGS[144]["b_exit_seed_base"] == 333_604 == 333_603 + 1, (
            "W144 B must be the first-clean window past the own-wave A "
            "band tail 333_603+1 (arithmetic continuation "
            "331_604..331_803 CLEAN on the registered universe but "
            "lands INSIDE the W144 A band window; same-freeze mutual "
            "exclusion (W141 precedent, leg2 law) -- the walk with the "
            "own-wave A window reserved jumps to 333_604, first-clean "
            "hops=1, non-rotational r587 forward-monotone walk; B "
            "base == own-wave A tail+1 machine-checkable)")'''
assert face.count(old_bassert) == 1, "face: B assert block needle"
face = face.replace(old_bassert, new_bassert)

# --- 0c. specific needles (counts measured post-0a/0b/0d by the measurement
#     pass results/_r752bma_w144_extract.py + 0d-consumption audit; the
#     receipt/seat needles run FIRST because of the substring-order law --
#     the band-gate receipt needle carries a w143_b substring, consuming
#     the 9th raw hit) ---
specific = [
    # receipt/seat needles FIRST (substring-order law)
    ("_r750bma_w143_band_gate.py", "_r752bma_w144_band_gate.py", 1),
    ("MSG-2026-10-06-002x-bma-w143-seat", "MSG-2026-10-06-011x-bma-w144-seat", 1),
    ("bm-a r748 freeze 16baa2a7b", "bm-a r750 freeze 86d3b070c", 1),
    ("to origin 3a7640311 BEFORE", "to origin 2ba4a613f BEFORE", 1),
    ("delivery" + NL + "    #     3a7640311", "delivery" + NL + "    #     2ba4a613f", 1),
    ("W143 finalize one-pass bm-a r749", "W143 finalize one-pass bm-a r751", 1),
    ("= W143 bm-a r749 one-pass", "= W143 bm-a r751 one-pass", 1),
    ("net chain head 708,411", "net chain head 710,611", 2),
    ("K=310,320", "K=312,520", 1),
    ("ONE HUNDRED-AND-THIRTY-THIRD", "ONE HUNDRED-AND-THIRTY-FOURTH", 1),
    ("fifty-ninth", "sixtieth", 1),
    ("(r750 bm-a freeze", "(r752 bm-a freeze", 1),
    ("wave 143 = first free number", "wave 144 = first free number", 1),
    ("rows 58 + candidate", "rows 59 + candidate", 1),
    ("rows 132 + candidate", "rows 133 + candidate", 1),
    ("below 143 composes", "below 144 composes", 1),
    ("WAVE_CONFIGS[143]", "WAVE_CONFIGS[144]", 3),
    ("pf.N1_BANDS[143]", "pf.N1_BANDS[144]", 3),
    ("_set_wave(143)", "_set_wave(144)", 1),
    ("if w < 143", "if w < 144", 3),
    ("range(17, 143)", "range(17, 144)", 1),
    ("range(16, 143)", "range(16, 144)", 1),
    ("w143_a", "w144_a", 8),
    ("w143_b", "w144_b", 8),  # 9th raw hit = "_r750bma_w143_band_gate.py" substring, consumed by the receipt needle above (substring-order law)
    ("n3r1_used143", "n3r1_used144", 3),
    ("n1w143", "n1w144", 2), ("n1_w143", "n1_w144", 2),
]
face = rep(face, specific, "face")
assert face.count("3a7640311") == 0 and face.count("16baa2a7b") == 0 \
    and face.count("r749") == 0, "face: stale sha/round residue"

# --- 0e. registered row parity label fixes + [143] row insertion LAST ---
# r740 parity-label law: 0a has shifted the [141]/[142] assert
# LABELS (W141->W142, W142->W143); [136]..[140] labels untouched by 0a
# (not in the 0a key set W143/W142/W141).
# No needle crosses a backslash-newline boundary (continuation built via chr(92)).
face = rep(face, [
    ('"registered W142 row parity drift (r307; bm-a r747)"',
     '"registered W141 row parity drift (r307; bm-a r747)"', 1),
], "face-parity-141")
new_143_block = (
    '"registered W142 row parity drift (r307; bm-a r748)"' + NL
    + '        assert pf.N1_BANDS[143] == {"a": (329_404, 331_403),' + NL
    + '                                    "b_exit": (331_404, 331_603),' + NL
    + '                                    "engine_owner": "bm-a"}, ' + BS + NL
    + '            "registered W143 row parity drift (r307; bm-a r750)"'
)
face = rep(face, [
    ('"registered W143 row parity drift (r307; bm-a r748)"',
     new_143_block, 1),
], "face-parity-142")

io.open(r".codely-cli\scratch_w144_face.txt", "w", encoding="utf-8", newline="\n").write(face)
print("face: W144 block transformed", face.count("W144"), "W144 mentions")

# ============ 1. perpetual_faces.py N1_BANDS row 144 ============
pf_path = r"scripts\perpetual_faces.py"
pf_src = io.open(pf_path, encoding="utf-8").read()
if '144: {"a": (331_604' in pf_src:
    print("pf: row 144 already present (idempotent skip)")
else:
    w143_row = '''    143: {"a": (329_404, 331_403), "b_exit": (331_404, 331_603),
         "engine_owner": "bm-a"},
}'''
    assert pf_src.count(w143_row) == 1, "pf: W143 row + closing brace needle"
    w144_block = '''    143: {"a": (329_404, 331_403), "b_exit": (331_404, 331_603),
         "engine_owner": "bm-a"},
    # W144 (bm-a r752 freeze, seat MSG-2026-10-06-011x-bma-w144-seat
    # pushed to origin 2ba4a613f pre-freeze r565 law (plain
    # fast-forward delivery, zero race this window, zero --no-verify);
    # band gate ADMIT results/_r752bma_w144_band_gate.py: A = FIRST-CLEAN
    # past the registered W143 B band (arithmetic continuation
    # 331_404..333_403 REFUSED at its own start by the W143 B band
    # 331_404..331_603, exactly as the r750 W143 gate-tail projection
    # note anticipated; honest forward walk hops=1 -> 331_604..333_603,
    # non-rotational r587 forward-monotone walk; A base == prior-wave
    # B tail+1 (331_603+1) machine-checkable -- A-hops-prior-B
    # staircase third instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 331_604..331_803 CLEAN on the registered universe
    # but lands INSIDE the W144 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 333_604 -> 333_604..333_803,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (333_603+1) machine-checkable);
    # dual-window derive parity with pre-seat probe
    # results/_r751bma_w144_probe_receipt.json; scan face =
    # SEED_REGISTRY 187 int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W145+ projection (gate-derived r752): A first-clean
    # 333_604..335_603 CLEAN hops=0 / B first-clean 333_804..334_003
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W144 B band 333_604..333_803 will refuse the naive
    # W145 A window; W145 freezer MUST re-derive on the post-W144
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W144 bands were never assigned).
    144: {"a": (331_604, 333_603), "b_exit": (333_604, 333_803),
         "engine_owner": "bm-a"},
}'''
    pf_src = pf_src.replace(w143_row, w144_block)
    io.open(pf_path, "w", encoding="utf-8", newline="\n").write(pf_src)
    print("pf: N1_BANDS row 144 inserted")

print("PART 1 DONE (face + pf row)")
