# -*- coding: utf-8 -*-
"""r748 bm-a W142 registry insertion PART 1: transform the extracted W141 face
-> W142 face (.codely-cli/scratch_w142_face.txt) + N1_BANDS row 142
(perpetual_faces.py). All insertions needle-asserted; idempotent guards.
Bloodline: r747 _r747bma_w141_registry_insert.py verbatim + W142 facts
(STAIRCASE GEOMETRY, E36 card: A = first-clean past the registered W141
B band -- the arithmetic continuation 327_004..329_003 is REFUSED at
its own start by the W141 B band, honest forward walk hops=1, A base ==
prior-wave B tail+1 machine-checkable, A-hops-prior-B first instance;
B = first-clean past the own-wave A window -- the arithmetic
continuation 327_204..327_403 is CLEAN on the registered universe but
lands INSIDE the W142 own-wave A window, same-freeze mutual exclusion
(W141 precedent, leg2 law), reserved walk -> 329_204..329_403, hops=1,
B base == own-A tail+1 machine-checkable).
r735 codegen pit laws enforced: (1) all new-block assert messages
single-line or parenthesized; (2) rep() expects measured on
post-prior-replacement text (measurement pass results/_r748bma_w142_extract.py
printed every count verbatim before this script was written; w141_b raw=9
with the 9th hit inside the band-gate receipt needle consumed FIRST).
r741 dep-line law: dep lines keep the post-0a W number, advance only the
r number (W141 finalize one-pass = bm-a r748 THAT window).
r740 parity-label law: parity old-needles take post-0a label forms
([139] shows W140 label, [140] shows W141 label), new block written clean.
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

# ============ 0. transform the extracted W141 face -> W142 face ============
face = io.open(r".codely-cli\scratch_w141_face_source.txt", encoding="utf-8").read()

# --- 0a. blanket wave-number shift FIRST (uppercase; then verified needles) ---
n_w141 = face.count("W141"); n_w140 = face.count("W140"); n_w139 = face.count("W139")
face = face.replace("W141", "W142")
face = face.replace("W140", "W141")
face = face.replace("W139", "W140")
assert face.count("W142") == n_w141 and face.count("W141") == n_w140 \
    and face.count("W140") == n_w139 and face.count("W139") == 0, \
    "blanket count check"

# --- 0b. arith-window + arith-name needles (A/B assert blocks rewritten in 0d) ---
face = rep(face, [
    ("set(range(325_004, 327_004))", "set(range(327_204, 329_204))", 1),
    ("set(range(327_004, 327_204))", "set(range(329_204, 329_404))", 1),
    ("arith_a141", "arith_a142", 3),
    ("arith_b141", "arith_b142", 3),
], "face-0b")

# --- 0d. semantic block rewrites FIRST (they carry WAVE_CONFIGS[141] and the
#     A/B base values inside their old forms; the 0c WAVE_CONFIGS needle then
#     sees only the 3 mirror asserts) ---
old_bfacts = '''# band facts (law sec.4 W142 row, r747): A = the arithmetic
        # continuation from the registered W141 A tail (CLEAN hops=0
        # at both the pre-seat probe and the freeze-window gate);
        # B = FIRST-CLEAN past the own-wave A window (the arithmetic
        # continuation 94_801..95_000 is REFUSED by probe seed 95_000;
        # the honest forward walk from 94_801 lands 325_004..325_203
        # inside the W142 A band window after 116 hops -- same-freeze
        # mutual exclusion (leg2 law) -- the walk continues past the
        # own-wave A window and lands 327_004..327_203, hops=117,
        # non-rotational r587 forward-monotone walk; B base == own-wave
        # A tail+1 (327_003+1) machine-checkable; cross-window
        # convergence with the r745 W141 gate-tail projection -- the
        # re-derive-MANDATORY note honored, the own-A hop is the
        # additional honest face, disclosed; seat MSG-231x tail,
        # re-derived).'''
new_bfacts = '''# band facts (law sec.4 W142 row, r748): A = FIRST-CLEAN past
        # the registered W141 B band (the arithmetic continuation
        # 327_004..329_003 is REFUSED at its own start by the W141
        # B band 327_004..327_203, exactly as the r747 W141 gate-tail
        # projection anticipated; the honest forward walk hops=1
        # lands 327_204..329_203; A base == prior-wave B tail+1
        # (327_203+1) machine-checkable -- A-hops-prior-B staircase
        # first instance, E36 card; non-rotational r587
        # forward-monotone walk);
        # B = FIRST-CLEAN past the own-wave A window (the arithmetic
        # continuation 327_204..327_403 is CLEAN on the registered
        # universe but lands INSIDE the W142 A band window --
        # same-freeze mutual exclusion (W141 precedent, leg2 law) --
        # the walk with the own-wave A window reserved jumps to
        # 329_204 and lands 329_204..329_403, hops=1, non-rotational
        # r587 forward-monotone walk; B base == own-wave A tail+1
        # (329_203+1) machine-checkable; cross-window convergence
        # with the r747 W141 gate-tail projection -- both
        # MANDATORY notes honored (post-W141 universe re-derive +
        # own-wave A reservation when deriving B); seat MSG-233x
        # tail, re-derived).'''
assert face.count(old_bfacts) == 1, "face: band-facts comment needle"
face = face.replace(old_bfacts, new_bfacts)

old_aassert = '''assert WAVE_CONFIGS[141]["a_seed_base"] == 325_004 == 325_003 + 1, (
            "W142 A must be the arithmetic continuation past the W141 "
            "registered A band tail")'''
new_aassert = '''assert WAVE_CONFIGS[142]["a_seed_base"] == 327_204 == 327_203 + 1, (
            "W142 A must be the first-clean window past the registered "
            "W141 B band tail 327_203+1 (arithmetic continuation "
            "327_004..329_003 REFUSED at its own start by the W141 B "
            "band 327_004..327_203, exactly as the r747 gate-tail "
            "projection anticipated; honest forward walk hops=1; "
            "A base == prior-wave B tail+1 machine-checkable = "
            "A-hops-prior-B staircase first instance, E36 card)")'''
assert face.count(old_aassert) == 1, "face: A assert block needle"
face = face.replace(old_aassert, new_aassert)

old_bassert = '''assert WAVE_CONFIGS[141]["b_exit_seed_base"] == 327_004 == 327_003 + 1, (
            "W142 B must be the first-clean window past the own-wave A "
            "band tail 327_003+1 (arithmetic continuation 94_801..95_000 "
            "REFUSED by probe seed 95_000; honest forward walk hops=116 "
            "lands 325_004..325_203 inside the W142 A band window; "
            "same-freeze mutual exclusion (leg2 law) -- B continues "
            "past the own-wave A window, first-clean hops=117, "
            "non-rotational r587 forward-monotone walk; B base == "
            "own-wave A tail+1 machine-checkable)")'''
new_bassert = '''assert WAVE_CONFIGS[142]["b_exit_seed_base"] == 329_204 == 329_203 + 1, (
            "W142 B must be the first-clean window past the own-wave A "
            "band tail 329_203+1 (arithmetic continuation "
            "327_204..327_403 CLEAN on the registered universe but "
            "lands INSIDE the W142 A band window; same-freeze mutual "
            "exclusion (W141 precedent, leg2 law) -- the walk with the "
            "own-wave A window reserved jumps to 329_204, first-clean "
            "hops=1, non-rotational r587 forward-monotone walk; B "
            "base == own-wave A tail+1 machine-checkable)")'''
assert face.count(old_bassert) == 1, "face: B assert block needle"
face = face.replace(old_bassert, new_bassert)

face = rep(face, [
    ('"W142 A window must be CLEAN (arithmetic ADMIT face)"',
     '"W142 A window must be CLEAN (first-clean ADMIT face past '
     'prior-wave B)"', 1),
], "face-a-label")

# --- 0c. specific needles (counts measured post-0a/0b/0d by the measurement
#     pass results/_r748bma_w142_extract.py + 0d-consumption audit; the
#     receipt/seat needles run FIRST because of the substring-order law --
#     the band-gate receipt needle carries a w141_b substring, consuming
#     the 9th raw hit) ---
specific = [
    # receipt/seat needles FIRST (substring-order law)
    ("_r747bma_w141_band_gate.py", "_r748bma_w142_band_gate.py", 1),
    ("MSG-2026-10-05-231x-bma-w141-seat", "MSG-2026-10-05-233x-bma-w142-seat", 1),
    ("bm-a r745 freeze 5e3984200", "bm-a r747 freeze 7ffadab65", 1),
    ("to origin aaa4d9be8 BEFORE", "to origin 94dee2c36 BEFORE", 1),
    ("W141 finalize one-pass bm-a r746", "W141 finalize one-pass bm-a r748", 1),
    ("= W141 bm-a r746 one-pass", "= W141 bm-a r748 one-pass", 1),
    ("net chain head 704,011", "net chain head 706,211", 2),
    ("K=305,920", "K=308,120", 1),
    ("ONE HUNDRED-AND-THIRTY-FIRST", "ONE HUNDRED-AND-THIRTY-SECOND", 1),
    ("fifty-seventh", "fifty-eighth", 1),
    ("(r747 bm-a freeze", "(r748 bm-a freeze", 1),
    ("wave 141 = first free number", "wave 142 = first free number", 1),
    ("rows 56 + candidate", "rows 57 + candidate", 1),
    ("rows 130 + candidate", "rows 131 + candidate", 1),
    ("below 141 composes", "below 142 composes", 1),
    ("WAVE_CONFIGS[141]", "WAVE_CONFIGS[142]", 3),
    ("pf.N1_BANDS[141]", "pf.N1_BANDS[142]", 3),
    ("_set_wave(141)", "_set_wave(142)", 1),
    ("if w < 141", "if w < 142", 3),
    ("range(17, 141)", "range(17, 142)", 1),
    ("range(16, 141)", "range(16, 142)", 1),
    ("w141_a", "w142_a", 8),
    ("w141_b", "w142_b", 8),  # 9th raw hit = "_r747bma_w141_band_gate.py" substring, consumed by the receipt needle above (substring-order law)
    ("n3r1_used141", "n3r1_used142", 3),
    ("n1w141", "n1w142", 2), ("n1_w141", "n1_w142", 2),
]
face = rep(face, specific, "face")

# --- 0c-2. seat-push race prose needle (triple-quoted, real newlines, no backslash) ---
old_race = '''deletion-set EMPTY; pre-freeze push plain fast-forward delivery
    #     aaa4d9be8, zero race this window (behind 0 at fetch),
    #     zero --no-verify)'''
new_race = '''deletion-set EMPTY; pre-freeze push via behind-1 merge absorb
    #     94dee2c36 (bm-b autofill keepalive tick absorbed, zero UU),
    #     zero --no-verify)'''
assert face.count(old_race) == 1, "face: seat-push race needle"
face = face.replace(old_race, new_race)

# --- 0e. registered row parity label fixes + [141] row insertion LAST ---
# r740 parity-label law: 0a has shifted the [139]/[140] assert
# LABELS (W139->W140, W140->W141); [133]..[138] labels untouched by 0a
# (not in the 0a key set W141/W140/W139).
# No needle crosses a backslash-newline boundary (continuation built via chr(92)).
face = rep(face, [
    ('"registered W140 row parity drift (r307; bm-a r744)"',
     '"registered W139 row parity drift (r307; bm-a r744)"', 1),
], "face-parity-139")
new_141_block = (
    '"registered W140 row parity drift (r307; bm-a r745)"' + NL
    + '        assert pf.N1_BANDS[141] == {"a": (325_004, 327_003),' + NL
    + '                                    "b_exit": (327_004, 327_203),' + NL
    + '                                    "engine_owner": "bm-a"}, ' + BS + NL
    + '            "registered W141 row parity drift (r307; bm-a r747)"'
)
face = rep(face, [
    ('"registered W141 row parity drift (r307; bm-a r745)"',
     new_141_block, 1),
], "face-parity-140")

io.open(r".codely-cli\scratch_w142_face.txt", "w", encoding="utf-8", newline="\n").write(face)
print("face: W142 block transformed", face.count("W142"), "W142 mentions")

# ============ 1. perpetual_faces.py N1_BANDS row 142 ============
pf_path = r"scripts\perpetual_faces.py"
pf_src = io.open(pf_path, encoding="utf-8").read()
if '142: {"a": (327_204' in pf_src:
    print("pf: row 142 already present (idempotent skip)")
else:
    w141_row = '''    141: {"a": (325_004, 327_003), "b_exit": (327_004, 327_203),
         "engine_owner": "bm-a"},
}'''
    assert pf_src.count(w141_row) == 1, "pf: W141 row + closing brace needle"
    w142_block = '''    141: {"a": (325_004, 327_003), "b_exit": (327_004, 327_203),
         "engine_owner": "bm-a"},
    # W142 (bm-a r748 freeze, seat MSG-2026-10-05-233x-bma-w142-seat
    # pushed to origin 94dee2c36 pre-freeze r565 law (via behind-1
    # merge absorb of the bm-b autofill keepalive tick, zero UU,
    # zero --no-verify);
    # band gate ADMIT results/_r748bma_w142_band_gate.py: A = FIRST-CLEAN
    # past the registered W141 B band (arithmetic continuation
    # 327_004..329_003 REFUSED at its own start by the W141 B band
    # 327_004..327_203, exactly as the r747 W141 gate-tail projection
    # anticipated; honest forward walk hops=1 -> 327_204..329_203,
    # non-rotational r587 forward-monotone walk; A base == prior-wave
    # B tail+1 machine-checkable -- A-hops-prior-B staircase first
    # instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 327_204..327_403 CLEAN on the registered universe
    # but lands INSIDE the W142 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 329_204 -> 329_204..329_403,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 machine-checkable);
    # dual-window derive parity with pre-seat probe
    # results/_r748bma_w142_probe_receipt.json; scan face =
    # SEED_REGISTRY 187 int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W143+ projection (gate-derived r748): A first-clean
    # 329_204..331_203 CLEAN hops=0 / B first-clean 329_404..329_603
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W142 B band 329_204..329_403 will refuse the naive
    # W143 A window; W143 freezer MUST re-derive on the post-W142
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W142 bands were never assigned).
    142: {"a": (327_204, 329_203), "b_exit": (329_204, 329_403),
         "engine_owner": "bm-a"},
}'''
    pf_src = pf_src.replace(w141_row, w142_block)
    io.open(pf_path, "w", encoding="utf-8", newline="\n").write(pf_src)
    print("pf: N1_BANDS row 142 inserted")

print("PART 1 DONE (face + pf row)")
