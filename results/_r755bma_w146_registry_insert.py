# -*- coding: utf-8 -*-
"""r755 bm-a W146 registry insertion PART 1: transform the extracted W145 face
-> W146 face (.codely-cli/scratch_w146_face.txt) + N1_BANDS row 146
(perpetual_faces.py). All insertions needle-asserted (counts measured by
results/_r755bma_w146_extract.py measurement pass); idempotent guards.
Bloodline: r753 _r753bma_w145_registry_insert.py verbatim + W146 facts
(STAIRCASE GEOMETRY fifth instance, E36 card: A = first-clean past the
registered W145 B band, hops=1; B = first-clean past the own-wave A window,
same-freeze mutual exclusion W141 precedent leg2 law, hops=1).
r735 codegen pit laws enforced: assert messages single-line or parenthesized;
rep() expects measured on post-prior-replacement text (receipt needle FIRST
per substring-order law -- the w145_b 9th hit lives inside the receipt path).
r741 dep-line law: dep lines keep the post-0a W number, advance only the
r number (W145 finalize one-pass = bm-a r755 THIS window).
r740 parity-label law: 0e old-needles take post-0a label forms; new block
written clean. r742 backslash law: zero literal backslashes in needles
(parity continuation via chr(92)). W141 = precedent refs, NOT in the 0a key
set (W145 face carries W141=3 all inside 0d-replaced blocks)."""
import io

BS = chr(92)
NL = chr(10)


def rep(src, pairs, tag):
    for old, new, expect in pairs:
        n = src.count(old)
        assert n == expect, f"{tag}: needle count={n} expect={expect}: {old[:60]!r}"
        src = src.replace(old, new)
    return src

# ============ 0. transform the extracted W145 face -> W146 face ============
face = io.open(r".codely-cli\scratch_w145_face_source.txt", encoding="utf-8").read()

# --- 0a. blanket wave-number shift FIRST (uppercase; W141 preserved: precedent) ---
n_w145 = face.count("W145"); n_w144 = face.count("W144"); n_w143 = face.count("W143"); n_w142 = face.count("W142"); n_w141 = face.count("W141")
face = face.replace("W145", "W146")
face = face.replace("W144", "W145")
face = face.replace("W143", "W144")
face = face.replace("W142", "W143")
assert face.count("W146") == n_w145 and face.count("W145") == n_w144 \
    and face.count("W144") == n_w143 and face.count("W143") == n_w142 \
    and face.count("W141") == n_w141, "blanket count check (W141 preserved)"

# --- 0b. arith-window + arith-name needles (A/B staircase asserts rewritten in 0d) ---
face = rep(face, [
    ("set(range(333_804, 335_804))", "set(range(336_004, 338_004))", 1),
    ("set(range(335_804, 336_004))", "set(range(338_004, 338_204))", 1),
    ("arith_a145", "arith_a146", 3),
    ("arith_b145", "arith_b146", 3),
], "face-0b")

# --- 0d. semantic block rewrites FIRST (they carry WAVE_CONFIGS[145] and the
#     A/B base values inside their old forms; the 0c WAVE_CONFIGS needle then
#     sees only the 3 mirror asserts). Old needles = the verbatim pre-0a
#     blocks passed through the same 0a shift (exact-by-construction). ---
old_bfacts_pre = '''# band facts (law sec.4 W145 row, r754): A = FIRST-CLEAN past
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
old_bfacts = old_bfacts_pre.replace("W145", "W146").replace("W144", "W145")
new_bfacts = '''# band facts (law sec.4 W146 row, r755): A = FIRST-CLEAN past
        # the registered W145 B band (the arithmetic continuation
        # 335_804..337_803 is REFUSED at its own start by the W145
        # B band 335_804..336_003, exactly as the r754 W145 gate-tail
        # projection note anticipated; the honest forward walk hops=1
        # lands 336_004..338_003; A base == prior-wave B tail+1
        # (336_003+1) machine-checkable -- A-hops-prior-B staircase
        # fifth instance, E36 card; non-rotational r587
        # forward-monotone walk);
        # B = FIRST-CLEAN past the own-wave A window (the arithmetic
        # continuation 336_004..336_203 is CLEAN on the registered
        # universe but lands INSIDE the W146 A band window --
        # same-freeze mutual exclusion (W141 precedent, leg2 law) --
        # the walk with the own-wave A window reserved jumps to
        # 338_004 and lands 338_004..338_203, hops=1, non-rotational
        # r587 forward-monotone walk; B base == own-wave A tail+1
        # (338_003+1) machine-checkable; cross-window convergence
        # with the r754 W145 gate-tail projection -- both
        # MANDATORY notes honored (post-W145 universe re-derive +
        # own-wave A reservation when deriving B); seat MSG-033x
        # tail, re-derived).'''
assert face.count(old_bfacts) == 1, "face: band-facts comment needle"
face = face.replace(old_bfacts, new_bfacts)

old_aassert_pre = '''assert WAVE_CONFIGS[145]["a_seed_base"] == 333_804 == 333_803 + 1, (
            "W145 A must be the first-clean window past the registered "
            "W144 B band tail 333_803+1 (arithmetic continuation "
            "333_604..335_603 REFUSED at its own start by the W144 B "
            "band 333_604..333_803, exactly as the r752 gate-tail "
            "projection note anticipated; honest forward walk hops=1; "
            "A base == prior-wave B tail+1 machine-checkable = "
            "A-hops-prior-B staircase fourth instance, E36 card)")'''
old_aassert = old_aassert_pre.replace("W145", "W146").replace("W144", "W145")
new_aassert = '''assert WAVE_CONFIGS[146]["a_seed_base"] == 336_004 == 336_003 + 1, (
            "W146 A must be the first-clean window past the registered "
            "W145 B band tail 336_003+1 (arithmetic continuation "
            "335_804..337_803 REFUSED at its own start by the W145 B "
            "band 335_804..336_003, exactly as the r754 gate-tail "
            "projection note anticipated; honest forward walk hops=1; "
            "A base == prior-wave B tail+1 machine-checkable = "
            "A-hops-prior-B staircase fifth instance, E36 card)")'''
assert face.count(old_aassert) == 1, "face: A assert block needle"
face = face.replace(old_aassert, new_aassert)

old_bassert_pre = '''assert WAVE_CONFIGS[145]["b_exit_seed_base"] == 335_804 == 335_803 + 1, (
            "W145 B must be the first-clean window past the own-wave A "
            "band tail 335_803+1 (arithmetic continuation "
            "333_804..334_003 CLEAN on the registered universe but "
            "lands INSIDE the W145 A band window; same-freeze mutual "
            "exclusion (W141 precedent, leg2 law) -- the walk with the "
            "own-wave A window reserved jumps to 335_804, first-clean "
            "hops=1, non-rotational r587 forward-monotone walk; B "
            "base == own-wave A tail+1 machine-checkable)")'''
old_bassert = old_bassert_pre.replace("W145", "W146")
new_bassert = '''assert WAVE_CONFIGS[146]["b_exit_seed_base"] == 338_004 == 338_003 + 1, (
            "W146 B must be the first-clean window past the own-wave A "
            "band tail 338_003+1 (arithmetic continuation "
            "336_004..336_203 CLEAN on the registered universe but "
            "lands INSIDE the W146 A band window; same-freeze mutual "
            "exclusion (W141 precedent, leg2 law) -- the walk with the "
            "own-wave A window reserved jumps to 338_004, first-clean "
            "hops=1, non-rotational r587 forward-monotone walk; B "
            "base == own-wave A tail+1 machine-checkable)")'''
assert face.count(old_bassert) == 1, "face: B assert block needle"
face = face.replace(old_bassert, new_bassert)

# --- 0c. specific needles (counts measured by the extract pass; the
#     receipt/seat needles run FIRST -- substring-order law: the receipt
#     path carries a w145_b substring, consuming the 9th raw hit) ---
specific = [
    # receipt/seat needles FIRST (substring-order law)
    ("_r753bma_w145_band_gate.py", "_r755bma_w146_band_gate.py", 1),
    ("MSG-2026-10-06-023x-bma-w145-seat", "MSG-2026-10-06-033x-bma-w146-seat", 1),
    ("bm-a r752 freeze ff6d2f918", "bm-a r754 freeze 98c661f8f", 1),
    ("55c2a1715", "c8183f342", 2),
    ("d5fdbb317", "8d4248daf", 1),
    ("= seat MSG + pre-seat probe + probe receipt;", "= seat MSG + pre-seat probe + probe receipt + W145 finalize products;", 1),
    ("W145 finalize one-pass bm-a r753", "W145 finalize one-pass bm-a r755", 1),
    ("= W145 bm-a r753 one-pass", "= W145 bm-a r755 one-pass", 1),
    ("net chain head 712,811", "net chain head 715,011", 2),
    ("K=314,720", "K=316,920", 1),
    ("ONE HUNDRED-AND-THIRTY-FIFTH", "ONE HUNDRED-AND-THIRTY-SIXTH", 1),
    ("sixty-first", "sixty-second", 1),
    ("(r754 bm-a freeze", "(r755 bm-a freeze", 1),
    ("wave 145 = first free number", "wave 146 = first free number", 1),
    ("rows 60 + candidate", "rows 61 + candidate", 1),
    ("rows 134 + candidate", "rows 135 + candidate", 1),
    ("below 145 composes", "below 146 composes", 1),
    ("WAVE_CONFIGS[145]", "WAVE_CONFIGS[146]", 3),
    ("pf.N1_BANDS[145]", "pf.N1_BANDS[146]", 3),
    ("_set_wave(145)", "_set_wave(146)", 1),
    ("if w < 145", "if w < 146", 3),
    ("range(17, 145)", "range(17, 146)", 1),
    ("range(16, 145)", "range(16, 146)", 1),
    ("w145_a", "w146_a", 8),
    ("w145_b", "w146_b", 8),  # 9th raw hit = receipt path substring, consumed above (substring-order law)
    ("n3r1_used145", "n3r1_used146", 3),
    ("n1w145", "n1w146", 2),
    ("n1_w145", "n1_w146", 2),
]
face = rep(face, specific, "face")
for _res in ("55c2a1715", "d5fdbb317", "ff6d2f918", "r753"):
    if face.count(_res):
        _i = face.find(_res)
        print(f"RESIDUE {_res} x{face.count(_res)}: ...{face[max(0,_i-100):_i+60]!r}...")
assert face.count("55c2a1715") == 0 and face.count("d5fdbb317") == 0 \
    and face.count("ff6d2f918") == 0 and face.count("r753") == 0, "face: stale sha/round residue"

# --- 0e. registered row parity label fixes + [145] row insertion LAST ---
# r740 parity-label law: 0a shifted the [142]/[143]/[144] assert LABELS
# (W142->W143, W143->W144, W144->W145); fix back to row-aligned labels,
# then insert the [145] assert block.
face = rep(face, [
    ('"registered W143 row parity drift (r307; bm-a r748)"',
     '"registered W142 row parity drift (r307; bm-a r748)"', 1),
], "face-parity-142")
face = rep(face, [
    ('"registered W144 row parity drift (r307; bm-a r750)"',
     '"registered W143 row parity drift (r307; bm-a r750)"', 1),
], "face-parity-143")
new_145_block = (
    '"registered W144 row parity drift (r307; bm-a r752)"' + NL
    + '        assert pf.N1_BANDS[145] == {"a": (333_804, 335_803),' + NL
    + '                                    "b_exit": (335_804, 336_003),' + NL
    + '                                    "engine_owner": "bm-a"}, ' + BS + NL
    + '            "registered W145 row parity drift (r307; bm-a r754)"'
)
face = rep(face, [
    ('"registered W145 row parity drift (r307; bm-a r752)"',
     new_145_block, 1),
], "face-parity-144")

io.open(r".codely-cli\scratch_w146_face.txt", "w", encoding="utf-8", newline="\n").write(face)
print("face: W146 block transformed", face.count("W146"), "W146 mentions")

# ============ 1. perpetual_faces.py N1_BANDS row 146 ============
pf_path = r"scripts\perpetual_faces.py"
pf_src = io.open(pf_path, encoding="utf-8").read()
if '146: {"a": (336_004' in pf_src:
    print("pf: row 146 already present (idempotent skip)")
else:
    w145_row = '''    145: {"a": (333_804, 335_803), "b_exit": (335_804, 336_003),
         "engine_owner": "bm-a"},
}'''
    assert pf_src.count(w145_row) == 1, "pf: W145 row + closing brace needle"
    w146_block = '''    145: {"a": (333_804, 335_803), "b_exit": (335_804, 336_003),
         "engine_owner": "bm-a"},
    # W146 (bm-a r755 freeze, seat MSG-2026-10-06-033x-bma-w146-seat
    # pushed to origin c8183f342 pre-freeze r565 law (two-hop merge
    # delivery c8183f342 -> 8d4248daf: first push raced origin forward
    # = r524 behind-signal; merge-mode closeout, zero --no-verify);
    # band gate ADMIT results/_r755bma_w146_band_gate.py: A = FIRST-CLEAN
    # past the registered W145 B band (arithmetic continuation
    # 335_804..337_803 REFUSED at its own start by the W145 B band
    # 335_804..336_003, exactly as the r754 W145 gate-tail projection
    # note anticipated; honest forward walk hops=1 -> 336_004..338_003,
    # non-rotational r587 forward-monotone walk; A base == prior-wave
    # B tail+1 (336_003+1) machine-checkable -- A-hops-prior-B
    # staircase fifth instance, E36 card);
    # B = FIRST-CLEAN past the own-wave A window (arithmetic
    # continuation 336_004..336_203 CLEAN on the registered universe
    # but lands INSIDE the W146 A band window -- same-freeze mutual
    # exclusion (W141 precedent, leg2 law) -- the walk with the
    # own-wave A window reserved jumps to 338_004 -> 338_004..338_203,
    # hops=1, non-rotational r587 forward-monotone walk; B base ==
    # own-wave A tail+1 (338_003+1) machine-checkable);
    # dual-window derive parity with pre-seat probe
    # results/_r755bma_w146_probe_receipt.json; scan face =
    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W147+ projection (gate-derived r755): A first-clean
    # 338_004..340_003 CLEAN hops=0 / B first-clean 338_204..338_403
    # CLEAN hops=0 -- naive B lands INSIDE the naive A window and the
    # registered W146 B band 338_004..338_203 will refuse the naive
    # W147 A window; W147 freezer MUST re-derive on the post-W146
    # universe AND reserve the own-wave A window when deriving B
    # (W141 precedent, same-freeze mutual exclusion, leg2 law,
    # E36 staircase card; never transcribe r587).
    # NOT a re-pick (R250: W146 bands were never assigned).
    146: {"a": (336_004, 338_003), "b_exit": (338_004, 338_203),
         "engine_owner": "bm-a"},
}'''
    pf_src = pf_src.replace(w145_row, w146_block)
    io.open(pf_path, "w", encoding="utf-8", newline="\n").write(pf_src)
    print("pf: N1_BANDS row 146 inserted")

print("PART 1 DONE (face + pf row)")
