# -*- coding: utf-8 -*-
"""r753 bm-a W145 registry insertion PART 1: transform the extracted W144 face
-> W145 face (.codely-cli/scratch_w145_face.txt) + N1_BANDS row 145
(perpetual_faces.py). All insertions needle-asserted; idempotent guards.
Bloodline: r752 _r752bma_w144_registry_insert.py verbatim + W145 facts
(STAIRCASE GEOMETRY fourth instance, E36 card: A = first-clean past the
registered W144 B band -- the arithmetic continuation 333_604..335_603 is
REFUSED at its own start by the W144 B band 333_604..333_803, honest forward
walk hops=1, A base == prior-wave B tail+1 (333_803+1) machine-checkable,
A-hops-prior-B fourth instance; B = first-clean past the own-wave A window --
the arithmetic continuation 333_804..334_003 is CLEAN on the registered
universe but lands INSIDE the W145 own-wave A window, same-freeze mutual
exclusion (W141 precedent, leg2 law), reserved walk -> 335_804..336_003,
hops=1, B base == own-wave A tail+1 (335_803+1) machine-checkable).
r735 codegen pit laws enforced: (1) all new-block assert messages
single-line or parenthesized; (2) rep() expects measured on
post-prior-replacement text (measurement pass results/_r753bma_w145_extract.py
printed every count verbatim before this script was written; w144_b raw=9
with the 9th hit inside the band-gate receipt needle consumed FIRST).
r745 extract-vs-insert needle-set law: every needle measured by the extract
pass as transform-needed is carried below (band-gate receipt, seat MSG,
freeze sha, seat push sha x2 + two-hop delivery form, finalize dep lines,
ledger head x2, K, ordinals, wave-free line, rows x2, below-composes,
WAVE_CONFIGS x5 [2 consumed by the 0d staircase rewrites, 3 at 0c],
N1_BANDS mirror x3, set_wave, w<, range x2, w144_a/w144_b, n3r1_used,
n1w/n1_w, parity [141]/[142] label fixes + [143] label fix + [144] insert).
r741 dep-line law: dep lines keep the post-0a W number, advance only the
r number (W144 finalize one-pass = bm-a r753 THAT window, commit 247e53cf8).
r740 parity-label law: parity old-needles take post-0a label forms
([141] shows W142 label post-0a, [142] shows W143 label post-0a, [143]
shows W144 label post-0a), new block written clean.
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

# ============ 0. transform the extracted W144 face -> W145 face ============
face = io.open(r".codely-cli\scratch_w144_face_source.txt", encoding="utf-8").read()

# --- 0a. blanket wave-number shift FIRST (uppercase; then verified needles) ---
n_w144 = face.count("W144"); n_w143 = face.count("W143"); n_w142 = face.count("W142"); n_w141 = face.count("W141")
face = face.replace("W144", "W145")
face = face.replace("W143", "W144")
face = face.replace("W142", "W143")
face = face.replace("W141", "W142")
assert face.count("W145") == n_w144 and face.count("W144") == n_w143 \
    and face.count("W143") == n_w142 and face.count("W142") == n_w141 \
    and face.count("W141") == 0, \
    "blanket count check"

# --- 0b. arith-window + arith-name needles (A/B staircase asserts rewritten in 0d) ---
face = rep(face, [
    ("set(range(331_604, 333_604))", "set(range(333_804, 335_804))", 1),
    ("set(range(333_604, 333_804))", "set(range(335_804, 336_004))", 1),
    ("arith_a144", "arith_a145", 3),
    ("arith_b144", "arith_b145", 3),
], "face-0b")

# --- 0d. semantic block rewrites FIRST (they carry WAVE_CONFIGS[144] and the
#     A/B base values inside their old forms; the 0c WAVE_CONFIGS needle then
#     sees only the 3 mirror asserts) ---
# band-facts comment needle = the verbatim pre-0a block passed through the same
# 0a shift (exact-by-construction, zero hand-drift).
old_bfacts_pre = '''# band facts (law sec.4 W144 row, r752): A = FIRST-CLEAN past
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
old_bfacts = old_bfacts_pre.replace("W144", "W145").replace("W143", "W144").replace("W142", "W143").replace("W141", "W142")
new_bfacts = '''# band facts (law sec.4 W145 row, r753): A = FIRST-CLEAN past
        # the registered W144 B band (the arithmetic continuation
        # 333_604..335_603 is REFUSED at its own start by the W144
        # B band 333_604..333_803, exactly as the r752 W144 gate-tail
        # projection note anticipated; the honest forward walk hops=1
        # lands 333_804..335_803; A base == prior-wave B tail+1
        # (333_803+1) machine-checkable -- A-hops-prior-B staircase
        # fourth instance, E36 card; non-rotational r587
        # forward-monotone walk);
        # B = FIRST-CLEAN past the own-wave A window (the arithmetic
        # continuation 333_804..334_003 is CLEAN on the registered
        # universe but lands INSIDE the W145 A band window --
        # same-freeze mutual exclusion (W141 precedent, leg2 law) --
        # the walk with the own-wave A window reserved jumps to
        # 335_804 and lands 335_804..336_003, hops=1, non-rotational
        # r587 forward-monotone walk; B base == own-wave A tail+1
        # (335_803+1) machine-checkable; cross-window convergence
        # with the r752 W144 gate-tail projection -- both
        # MANDATORY notes honored (post-W144 universe re-derive +
        # own-wave A reservation when deriving B); seat MSG-023x
        # tail, re-derived).'''
assert face.count(old_bfacts) == 1, "face: band-facts comment needle"
face = face.replace(old_bfacts, new_bfacts)

old_aassert_pre = '''assert WAVE_CONFIGS[144]["a_seed_base"] == 331_604 == 331_603 + 1, (
            "W144 A must be the first-clean window past the registered "
            "W143 B band tail 331_603+1 (arithmetic continuation "
            "331_404..333_403 REFUSED at its own start by the W143 B "
            "band 331_404..331_603, exactly as the r750 gate-tail "
            "projection note anticipated; honest forward walk hops=1; "
            "A base == prior-wave B tail+1 machine-checkable = "
            "A-hops-prior-B staircase third instance, E36 card)")'''
old_aassert = old_aassert_pre.replace("W144", "W145").replace("W143", "W144")
new_aassert = '''assert WAVE_CONFIGS[145]["a_seed_base"] == 333_804 == 333_803 + 1, (
            "W145 A must be the first-clean window past the registered "
            "W144 B band tail 333_803+1 (arithmetic continuation "
            "333_604..335_603 REFUSED at its own start by the W144 B "
            "band 333_604..333_803, exactly as the r752 gate-tail "
            "projection note anticipated; honest forward walk hops=1; "
            "A base == prior-wave B tail+1 machine-checkable = "
            "A-hops-prior-B staircase fourth instance, E36 card)")'''
assert face.count(old_aassert) == 1, "face: A assert block needle"
face = face.replace(old_aassert, new_aassert)

old_bassert_pre = '''assert WAVE_CONFIGS[144]["b_exit_seed_base"] == 333_604 == 333_603 + 1, (
            "W144 B must be the first-clean window past the own-wave A "
            "band tail 333_603+1 (arithmetic continuation "
            "331_604..331_803 CLEAN on the registered universe but "
            "lands INSIDE the W144 A band window; same-freeze mutual "
            "exclusion (W141 precedent, leg2 law) -- the walk with the "
            "own-wave A window reserved jumps to 333_604, first-clean "
            "hops=1, non-rotational r587 forward-monotone walk; B "
            "base == own-wave A tail+1 machine-checkable)")'''
old_bassert = old_bassert_pre.replace("W144", "W145").replace("W143", "W144").replace("W141", "W142")
new_bassert = '''assert WAVE_CONFIGS[145]["b_exit_seed_base"] == 335_804 == 335_803 + 1, (
            "W145 B must be the first-clean window past the own-wave A "
            "band tail 335_803+1 (arithmetic continuation "
            "333_804..334_003 CLEAN on the registered universe but "
            "lands INSIDE the W145 A band window; same-freeze mutual "
            "exclusion (W141 precedent, leg2 law) -- the walk with the "
            "own-wave A window reserved jumps to 335_804, first-clean "
            "hops=1, non-rotational r587 forward-monotone walk; B "
            "base == own-wave A tail+1 machine-checkable)")'''
assert face.count(old_bassert) == 1, "face: B assert block needle"
face = face.replace(old_bassert, new_bassert)

# --- 0c. specific needles (counts measured post-0a/0b/0d by the measurement
#     pass results/_r753bma_w145_extract.py + 0d-consumption audit; the
#     receipt/seat needles run FIRST because of the substring-order law --
#     the band-gate receipt needle carries a w144_b substring, consuming
#     the 9th raw hit) ---
specific = [
    # receipt/seat needles FIRST (substring-order law)
    ("_r752bma_w144_band_gate.py", "_r753bma_w145_band_gate.py", 1),
    ("MSG-2026-10-06-011x-bma-w144-seat", "MSG-2026-10-06-023x-bma-w145-seat", 1),
    ("bm-a r750 freeze 86d3b070c", "bm-a r752 freeze ff6d2f918", 1),
    ("to origin 2ba4a613f BEFORE", "to origin 55c2a1715 BEFORE", 1),
    ("pre-freeze push plain fast-forward delivery" + NL + "    #     2ba4a613f, zero race this window (behind 0 at fetch)," + NL + "    #     zero --no-verify).",
     "pre-freeze push two-hop merge delivery" + NL + "    #     55c2a1715 -> d5fdbb317 (first push raced origin forward =" + NL + "    #     r524 behind-signal; merge-mode closeout, zero --no-verify).", 1),
    ("W144 finalize one-pass bm-a r751", "W144 finalize one-pass bm-a r753", 1),
    ("= W144 bm-a r751 one-pass", "= W144 bm-a r753 one-pass", 1),
    ("net chain head 710,611", "net chain head 712,811", 2),
    ("K=312,520", "K=314,720", 1),
    ("ONE HUNDRED-AND-THIRTY-FOURTH", "ONE HUNDRED-AND-THIRTY-FIFTH", 1),
    ("sixtieth", "sixty-first", 1),
    ("(r752 bm-a freeze", "(r753 bm-a freeze", 1),
    ("wave 144 = first free number", "wave 145 = first free number", 1),
    ("rows 59 + candidate", "rows 60 + candidate", 1),
    ("rows 133 + candidate", "rows 134 + candidate", 1),
    ("below 144 composes", "below 145 composes", 1),
    ("WAVE_CONFIGS[144]", "WAVE_CONFIGS[145]", 3),
    ("pf.N1_BANDS[144]", "pf.N1_BANDS[145]", 3),
    ("_set_wave(144)", "_set_wave(145)", 1),
    ("if w < 144", "if w < 145", 3),
    ("range(17, 144)", "range(17, 145)", 1),
    ("range(16, 144)", "range(16, 145)", 1),
    ("w144_a", "w145_a", 8),
    ("w144_b", "w145_b", 8),  # 9th raw hit = "_r752bma_w144_band_gate.py" substring, consumed by the receipt needle above (substring-order law)
    ("n3r1_used144", "n3r1_used145", 3),
    ("n1w144", "n1w145", 2), ("n1_w144", "n1_w145", 2),
]
face = rep(face, specific, "face")
assert face.count("2ba4a613f") == 0 and face.count("86d3b070c") == 0 \
    and face.count("r751") == 0, "face: stale sha/round residue"

# --- 0e. registered row parity label fixes + [144] row insertion LAST ---
# r740 parity-label law: 0a has shifted the [141]/[142]/[143] assert
# LABELS (W141->W142, W142->W143, W143->W144); [133]..[140] labels
# untouched by 0a (not in the 0a key set W144/W143/W142/W141).
# No needle crosses a backslash-newline boundary (continuation built via chr(92)).
face = rep(face, [
    ('"registered W142 row parity drift (r307; bm-a r747)"',
     '"registered W141 row parity drift (r307; bm-a r747)"', 1),
], "face-parity-141")
face = rep(face, [
    ('"registered W143 row parity drift (r307; bm-a r748)"',
     '"registered W142 row parity drift (r307; bm-a r748)"', 1),
], "face-parity-142")
new_144_block = (
    '"registered W143 row parity drift (r307; bm-a r750)"' + NL
    + '        assert pf.N1_BANDS[144] == {"a": (331_604, 333_603),' + NL
    + '                                    "b_exit": (333_604, 333_803),' + NL
    + '                                    "engine_owner": "bm-a"}, ' + BS + NL
    + '            "registered W144 row parity drift (r307; bm-a r752)"'
)
face = rep(face, [
    ('"registered W144 row parity drift (r307; bm-a r750)"',
     new_144_block, 1),
], "face-parity-143")

io.open(r".codely-cli\scratch_w145_face.txt", "w", encoding="utf-8", newline="\n").write(face)
print("face: W145 block transformed", face.count("W145"), "W145 mentions")

# ============ 1. perpetual_faces.py N1_BANDS row 145 ============
pf_path = r"scripts\perpetual_faces.py"
pf_src = io.open(pf_path, encoding="utf-8").read()
if '145: {"a": (333_804' in pf_src:
    print("pf: row 145 already present (idempotent skip)")
else:
    w144_row = '''    144: {"a": (331_604, 333_603), "b_exit": (333_604, 333_803),
         "engine_owner": "bm-a"},
}'''
    assert pf_src.count(w144_row) == 1, "pf: W144 row + closing brace needle"
    w145_block = '''    144: {"a": (331_604, 333_603), "b_exit": (333_604, 333_803),
         "engine_owner": "bm-a"},
    # W145 (bm-a r753 freeze, seat MSG-2026-10-06-023x-bma-w145-seat
    # pushed to origin 55c2a1715 pre-freeze r565 law (two-hop merge
    # delivery 55c2a1715 -> d5fdbb317: first push raced origin forward
    # = r524 behind-signal; merge-mode closeout, zero --no-verify);
    # band gate ADMIT results/_r753bma_w145_band_gate.py: A = FIRST-CLEAN
    # past the registered W144 B band (arithmetic continuation
    # 333_604..335_603 REFUSED at its own start by the W144 B band
    # 333_604..333_803, exactly as the r752 W144 gate-tail projection
    # note anticipated; honest forward walk hops=1 -> 333_804..335_803,
    # non-rotational r587 forward-monotone walk; A base == prior-wave
    # B tail+1 (333_803+1) machine-checkable -- A-hops-prior-B
    # staircase fourth instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 333_804..334_003 CLEAN on the registered universe
    # but lands INSIDE the W145 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 335_804 -> 335_804..336_003,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (335_803+1) machine-checkable);
    # dual-window derive parity with pre-seat probe
    # results/_r753bma_w145_probe_receipt.json; scan face =
    # SEED_REGISTRY 187 int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W146+ projection (gate-derived r753): A first-clean
    # 335_804..337_803 CLEAN hops=0 / B first-clean 336_004..336_203
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W145 B band 335_804..336_003 will refuse the naive
    # W146 A window; W146 freezer MUST re-derive on the post-W145
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W145 bands were never assigned).
    145: {"a": (333_804, 335_803), "b_exit": (335_804, 336_003),
         "engine_owner": "bm-a"},
}'''
    pf_src = pf_src.replace(w144_row, w145_block)
    io.open(pf_path, "w", encoding="utf-8", newline="\n").write(pf_src)
    print("pf: N1_BANDS row 145 inserted")

print("PART 1 DONE (face + pf row)")
