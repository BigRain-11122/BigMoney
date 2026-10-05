# -*- coding: utf-8 -*-
"""r750 bm-a W143 registry insertion PART 1: transform the extracted W142 face
-> W143 face (.codely-cli/scratch_w143_face.txt) + N1_BANDS row 143
(perpetual_faces.py). All insertions needle-asserted; idempotent guards.
Bloodline: r748 _r748bma_w142_registry_insert.py verbatim + W143 facts
(STAIRCASE GEOMETRY second instance, E36 card: A = first-clean past the
registered W142 B band -- the arithmetic continuation 329_204..331_203 is
REFUSED at its own start by the W142 B band, honest forward walk hops=1, A
base == prior-wave B tail+1 machine-checkable, A-hops-prior-B second
instance; B = first-clean past the own-wave A window -- the arithmetic
continuation 329_404..329_603 is CLEAN on the registered universe but lands
INSIDE the W143 own-wave A window, same-freeze mutual exclusion (W141
precedent, leg2 law), reserved walk -> 331_404..331_603, hops=1, B base ==
own-A tail+1 machine-checkable).
r735 codegen pit laws enforced: (1) all new-block assert messages
single-line or parenthesized; (2) rep() expects measured on
post-prior-replacement text (measurement pass results/_r750bma_w143_extract.py
printed every count verbatim before this script was written; w142_b raw=9
with the 9th hit inside the band-gate receipt needle consumed FIRST).
r741 dep-line law: dep lines keep the post-0a W number, advance only the
r number (W142 finalize one-pass = bm-a r749 THAT window).
r740 parity-label law: parity old-needles take post-0a label forms
([140] shows W141 label, [141] shows W142 label), new block written clean.
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

# ============ 0. transform the extracted W142 face -> W143 face ============
face = io.open(r".codely-cli\scratch_w142_face_source.txt", encoding="utf-8").read()

# --- 0a. blanket wave-number shift FIRST (uppercase; then verified needles) ---
n_w142 = face.count("W142"); n_w141 = face.count("W141"); n_w140 = face.count("W140")
face = face.replace("W142", "W143")
face = face.replace("W141", "W142")
face = face.replace("W140", "W141")
assert face.count("W143") == n_w142 and face.count("W142") == n_w141 \
    and face.count("W141") == n_w140 and face.count("W140") == 0, \
    "blanket count check"

# --- 0b. arith-window + arith-name needles (A/B assert blocks rewritten in 0d) ---
face = rep(face, [
    ("set(range(327_204, 329_204))", "set(range(329_404, 331_404))", 1),
    ("set(range(329_204, 329_404))", "set(range(331_404, 331_604))", 1),
    ("arith_a142", "arith_a143", 3),
    ("arith_b142", "arith_b143", 3),
], "face-0b")

# --- 0d. semantic block rewrites FIRST (they carry WAVE_CONFIGS[142] and the
#     A/B base values inside their old forms; the 0c WAVE_CONFIGS needle then
#     sees only the 3 mirror asserts) ---
old_bfacts = '''# band facts (law sec.4 W143 row, r748): A = FIRST-CLEAN past
        # the registered W142 B band (the arithmetic continuation
        # 327_004..329_003 is REFUSED at its own start by the W142
        # B band 327_004..327_203, exactly as the r747 W142 gate-tail
        # projection anticipated; the honest forward walk hops=1
        # lands 327_204..329_203; A base == prior-wave B tail+1
        # (327_203+1) machine-checkable -- A-hops-prior-B staircase
        # first instance, E36 card; non-rotational r587
        # forward-monotone walk);
        # B = FIRST-CLEAN past the own-wave A window (the arithmetic
        # continuation 327_204..327_403 is CLEAN on the registered
        # universe but lands INSIDE the W143 A band window --
        # same-freeze mutual exclusion (W142 precedent, leg2 law) --
        # the walk with the own-wave A window reserved jumps to
        # 329_204 and lands 329_204..329_403, hops=1, non-rotational
        # r587 forward-monotone walk; B base == own-wave A tail+1
        # (329_203+1) machine-checkable; cross-window convergence
        # with the r747 W142 gate-tail projection -- both
        # MANDATORY notes honored (post-W142 universe re-derive +
        # own-wave A reservation when deriving B); seat MSG-233x
        # tail, re-derived).'''
new_bfacts = '''# band facts (law sec.4 W143 row, r750): A = FIRST-CLEAN past
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
assert face.count(old_bfacts) == 1, "face: band-facts comment needle"
face = face.replace(old_bfacts, new_bfacts)

old_aassert = '''assert WAVE_CONFIGS[142]["a_seed_base"] == 327_204 == 327_203 + 1, (
            "W143 A must be the first-clean window past the registered "
            "W142 B band tail 327_203+1 (arithmetic continuation "
            "327_004..329_003 REFUSED at its own start by the W142 B "
            "band 327_004..327_203, exactly as the r747 gate-tail "
            "projection anticipated; honest forward walk hops=1; "
            "A base == prior-wave B tail+1 machine-checkable = "
            "A-hops-prior-B staircase first instance, E36 card)")'''
new_aassert = '''assert WAVE_CONFIGS[143]["a_seed_base"] == 329_404 == 329_403 + 1, (
            "W143 A must be the first-clean window past the registered "
            "W142 B band tail 329_403+1 (arithmetic continuation "
            "329_204..331_203 REFUSED at its own start by the W142 B "
            "band 329_204..329_403, exactly as the r748 gate-tail "
            "projection note anticipated; honest forward walk hops=1; "
            "A base == prior-wave B tail+1 machine-checkable = "
            "A-hops-prior-B staircase second instance, E36 card)")'''
assert face.count(old_aassert) == 1, "face: A assert block needle"
face = face.replace(old_aassert, new_aassert)

old_bassert = '''assert WAVE_CONFIGS[142]["b_exit_seed_base"] == 329_204 == 329_203 + 1, (
            "W143 B must be the first-clean window past the own-wave A "
            "band tail 329_203+1 (arithmetic continuation "
            "327_204..327_403 CLEAN on the registered universe but "
            "lands INSIDE the W143 A band window; same-freeze mutual "
            "exclusion (W142 precedent, leg2 law) -- the walk with the "
            "own-wave A window reserved jumps to 329_204, first-clean "
            "hops=1, non-rotational r587 forward-monotone walk; B "
            "base == own-wave A tail+1 machine-checkable)")'''
new_bassert = '''assert WAVE_CONFIGS[143]["b_exit_seed_base"] == 331_404 == 331_403 + 1, (
            "W143 B must be the first-clean window past the own-wave A "
            "band tail 331_403+1 (arithmetic continuation "
            "329_404..329_603 CLEAN on the registered universe but "
            "lands INSIDE the W143 A band window; same-freeze mutual "
            "exclusion (W141 precedent, leg2 law) -- the walk with the "
            "own-wave A window reserved jumps to 331_404, first-clean "
            "hops=1, non-rotational r587 forward-monotone walk; B "
            "base == own-wave A tail+1 machine-checkable)")'''
assert face.count(old_bassert) == 1, "face: B assert block needle"
face = face.replace(old_bassert, new_bassert)

# --- 0c. specific needles (counts measured post-0a/0b/0d by the measurement
#     pass results/_r750bma_w143_extract.py + 0d-consumption audit; the
#     receipt/seat needles run FIRST because of the substring-order law --
#     the band-gate receipt needle carries a w142_b substring, consuming
#     the 9th raw hit) ---
specific = [
    # receipt/seat needles FIRST (substring-order law)
    ("_r748bma_w142_band_gate.py", "_r750bma_w143_band_gate.py", 1),
    ("MSG-2026-10-05-233x-bma-w142-seat", "MSG-2026-10-06-002x-bma-w143-seat", 1),
    ("bm-a r747 freeze 7ffadab65", "bm-a r748 freeze 16baa2a7b", 1),
    ("to origin 94dee2c36 BEFORE", "to origin 3a7640311 BEFORE", 1),
    ("W142 finalize one-pass bm-a r748", "W142 finalize one-pass bm-a r749", 1),
    ("= W142 bm-a r748 one-pass", "= W142 bm-a r749 one-pass", 1),
    ("net chain head 706,211", "net chain head 708,411", 2),
    ("K=308,120", "K=310,320", 1),
    ("ONE HUNDRED-AND-THIRTY-SECOND", "ONE HUNDRED-AND-THIRTY-THIRD", 1),
    ("fifty-eighth", "fifty-ninth", 1),
    ("(r748 bm-a freeze", "(r750 bm-a freeze", 1),
    ("wave 142 = first free number", "wave 143 = first free number", 1),
    ("rows 57 + candidate", "rows 58 + candidate", 1),
    ("rows 131 + candidate", "rows 132 + candidate", 1),
    ("below 142 composes", "below 143 composes", 1),
    ("WAVE_CONFIGS[142]", "WAVE_CONFIGS[143]", 3),
    ("pf.N1_BANDS[142]", "pf.N1_BANDS[143]", 3),
    ("_set_wave(142)", "_set_wave(143)", 1),
    ("if w < 142", "if w < 143", 3),
    ("range(17, 142)", "range(17, 143)", 1),
    ("range(16, 142)", "range(16, 143)", 1),
    ("w142_a", "w143_a", 8),
    ("w142_b", "w143_b", 8),  # 9th raw hit = "_r748bma_w142_band_gate.py" substring, consumed by the receipt needle above (substring-order law)
    ("n3r1_used142", "n3r1_used143", 3),
    ("n1w142", "n1w143", 2), ("n1_w142", "n1_w143", 2),
]
face = rep(face, specific, "face")

# --- 0c-2. seat-push race prose needle (triple-quoted, real newlines, no backslash) ---
old_race = '''deletion-set EMPTY; pre-freeze push via behind-1 merge absorb
    #     94dee2c36 (bm-b autofill keepalive tick absorbed, zero UU),
    #     zero --no-verify)'''
new_race = '''deletion-set EMPTY; pre-freeze push plain fast-forward delivery
    #     3a7640311, zero race this window (behind 0 at fetch),
    #     zero --no-verify)'''
assert face.count(old_race) == 1, "face: seat-push race needle"
face = face.replace(old_race, new_race)

# --- 0e. registered row parity label fixes + [142] row insertion LAST ---
# r740 parity-label law: 0a has shifted the [140]/[141] assert
# LABELS (W140->W141, W141->W142); [133]..[139] labels untouched by 0a
# (not in the 0a key set W142/W141/W140).
# No needle crosses a backslash-newline boundary (continuation built via chr(92)).
face = rep(face, [
    ('"registered W141 row parity drift (r307; bm-a r745)"',
     '"registered W140 row parity drift (r307; bm-a r745)"', 1),
], "face-parity-140")
new_142_block = (
    '"registered W141 row parity drift (r307; bm-a r747)"' + NL
    + '        assert pf.N1_BANDS[142] == {"a": (327_204, 329_203),' + NL
    + '                                    "b_exit": (329_204, 329_403),' + NL
    + '                                    "engine_owner": "bm-a"}, ' + BS + NL
    + '            "registered W142 row parity drift (r307; bm-a r748)"'
)
face = rep(face, [
    ('"registered W142 row parity drift (r307; bm-a r747)"',
     new_142_block, 1),
], "face-parity-141")

io.open(r".codely-cli\scratch_w143_face.txt", "w", encoding="utf-8", newline="\n").write(face)
print("face: W143 block transformed", face.count("W143"), "W143 mentions")

# ============ 1. perpetual_faces.py N1_BANDS row 143 ============
pf_path = r"scripts\perpetual_faces.py"
pf_src = io.open(pf_path, encoding="utf-8").read()
if '143: {"a": (329_404' in pf_src:
    print("pf: row 143 already present (idempotent skip)")
else:
    w142_row = '''    142: {"a": (327_204, 329_203), "b_exit": (329_204, 329_403),
         "engine_owner": "bm-a"},
}'''
    assert pf_src.count(w142_row) == 1, "pf: W142 row + closing brace needle"
    w143_block = '''    142: {"a": (327_204, 329_203), "b_exit": (329_204, 329_403),
         "engine_owner": "bm-a"},
    # W143 (bm-a r750 freeze, seat MSG-2026-10-06-002x-bma-w143-seat
    # pushed to origin 3a7640311 pre-freeze r565 law (plain
    # fast-forward delivery, zero race this window, zero --no-verify);
    # band gate ADMIT results/_r750bma_w143_band_gate.py: A = FIRST-CLEAN
    # past the registered W142 B band (arithmetic continuation
    # 329_204..331_203 REFUSED at its own start by the W142 B band
    # 329_204..329_403, exactly as the r748 W142 gate-tail projection
    # note anticipated; honest forward walk hops=1 -> 329_404..331_403,
    # non-rotational r587 forward-monotone walk; A base == prior-wave
    # B tail+1 machine-checkable -- A-hops-prior-B staircase second
    # instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 329_404..329_603 CLEAN on the registered universe
    # but lands INSIDE the W143 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 331_404 -> 331_404..331_603,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 machine-checkable);
    # dual-window derive parity with pre-seat probe
    # results/_r750bma_w143_probe_receipt.json; scan face =
    # SEED_REGISTRY 187 int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W144+ projection (gate-derived r750): A first-clean
    # 331_404..333_403 CLEAN hops=0 / B first-clean 331_604..331_803
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W143 B band 331_404..331_603 will refuse the naive
    # W144 A window; W144 freezer MUST re-derive on the post-W143
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W143 bands were never assigned).
    143: {"a": (329_404, 331_403), "b_exit": (331_404, 331_603),
         "engine_owner": "bm-a"},
}'''
    pf_src = pf_src.replace(w142_row, w143_block)
    io.open(pf_path, "w", encoding="utf-8", newline="\n").write(pf_src)
    print("pf: N1_BANDS row 143 inserted")

print("PART 1 DONE (face + pf row)")
