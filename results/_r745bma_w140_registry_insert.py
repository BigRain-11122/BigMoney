# -*- coding: utf-8 -*-
"""r745 bm-a W140 registry insertion PART 1: transform the extracted W139 face
-> W140 face (.codely-cli/scratch_w140_face.txt) + N1_BANDS row 140
(perpetual_faces.py). All insertions needle-asserted; idempotent guards.
Bloodline: r744 _r744bma_w139_registry_insert.py verbatim + W140 facts
(A = arithmetic continuation from the registered W139 A tail 323_003+1,
CLEAN hops=0; B = arithmetic continuation from the registered W139 B
tail 94_600+1, first window CLEAN by construction, double-CLEAN
continuation window, zero hops).
NEW vs r744 bloodline (r735 measurement-vs-implementation divergence fix,
discovered r745 pre-insert audit): the B-window set-range needle
("set(range(94_401, 94_601))" -> "set(range(94_601, 94_801))") was
MEASURED by the r744 extract but MISSING from the r744 insert 0b -- the
W139 face shipped with arith_b139 probing the stale W138 window
94_201..94_400 (vacuous-pass latent guard, zero data harm: the engine
burn used WAVE_CONFIGS values, band admission verified by the external
band gate). The W139 face window was surgically fixed same-window
(arith_b139 = set(range(94_401, 94_601)), selftest PASS) BEFORE this
extract; this insert carries the B-range needle so the divergence cannot
propagate to W140.
r735 codegen pit laws enforced: (1) all new-block assert messages
single-line or parenthesized; (2) rep() expects measured on
post-prior-replacement text (measurement pass results/_r745bma_w140_extract.py
printed every count verbatim before this script was written; w139_b raw=9
with the 9th hit inside the band-gate receipt needle consumed FIRST).
r741 dep-line law: dep lines keep the post-0a W number, advance only the
r number (W139 finalize one-pass = bm-a r745 THIS window).
r740 parity-label law: parity old-needle takes post-0a label forms
([137] shows W138 label, [138] shows W139 label), new block written clean.
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

# ============ 0. transform the extracted W139 face -> W140 face ============
face = io.open(r".codely-cli\scratch_w139_face_source.txt", encoding="utf-8").read()

# --- 0a. blanket wave-number shift FIRST (uppercase; then verified needles) ---
n_w139 = face.count("W139"); n_w138 = face.count("W138"); n_w137 = face.count("W137")
face = face.replace("W139", "W140")
face = face.replace("W138", "W139")
face = face.replace("W137", "W138")
assert face.count("W140") == n_w139 and face.count("W139") == n_w138 \
    and face.count("W138") == n_w137 and face.count("W137") == 0, \
    "blanket count check"

# --- 0b. A/B-block seed-value needles (arithmetic continuation from W139 tails) ---
face = rep(face, [
    ("== 321_004 == 321_003 + 1", "== 323_004 == 323_003 + 1", 1),
    ("set(range(321_004, 323_004))", "set(range(323_004, 325_004))", 1),
    ("set(range(94_401, 94_601))", "set(range(94_601, 94_801))", 1),
    ("arith_a139", "arith_a140", 2),
    ("arith_b139", "arith_b140", 2),
], "face-0b")

# --- 0c. specific needles (counts measured post-0a/0b by the measurement
#     pass results/_r745bma_w140_extract.py; the receipt/seat needles run
#     FIRST because of the substring-order law -- the band-gate receipt
#     needle carries a w139_b substring, consuming the 9th raw hit) ---
specific = [
    # receipt/seat needles FIRST (substring-order law)
    ("_r744bma_w139_band_gate.py", "_r745bma_w140_band_gate.py", 1),
    ("MSG-2026-10-05-213x-bma-w139-seat", "MSG-2026-10-05-215x-bma-w140-seat", 1),
    ("bm-a r743 freeze 6798a1e5f", "bm-a r744 freeze 4e3a018c7", 1),
    ("to origin 7e1fc08d0 BEFORE", "to origin 08710e2d0 BEFORE", 1),
    ("W139 finalize one-pass bm-a r744", "W139 finalize one-pass bm-a r745", 1),
    ("= W139 bm-a r744 one-pass", "= W139 bm-a r745 one-pass", 1),
    ("net chain head 699,611", "net chain head 701,811", 2),
    ("K=301,520", "K=303,720", 1),
    ("ONE HUNDRED-AND-TWENTY-NINTH", "ONE HUNDRED-AND-THIRTIETH", 1),
    ("fifty-fifth", "fifty-sixth", 1),
    ("(r744 bm-a freeze", "(r745 bm-a freeze", 1),
    ("(law sec.4 W140 row, r744)", "(law sec.4 W140 row, r745)", 1),
    ("wave 139 = first free number", "wave 140 = first free number", 1),
    ("rows 54 + candidate", "rows 55 + candidate", 1),
    ("rows 128 + candidate", "rows 129 + candidate", 1),
    ("below 139 composes", "below 140 composes", 1),
    ("WAVE_CONFIGS[139]", "WAVE_CONFIGS[140]", 5),
    ("pf.N1_BANDS[139]", "pf.N1_BANDS[140]", 3),
    ("_set_wave(139)", "_set_wave(140)", 1),
    ("if w < 139", "if w < 140", 3),
    ("range(17, 139)", "range(17, 140)", 1),
    ("range(16, 139)", "range(16, 140)", 1),
    ("w139_a", "w140_a", 8),
    ("w139_b", "w140_b", 8),  # 9th raw hit = "_r744bma_w139_band_gate.py" substring, consumed by the receipt needle above (substring-order law)
    ("n3r1_used139", "n3r1_used140", 3),
    ("n1w139", "n1w140", 2), ("n1_w139", "n1_w140", 2),
    ("== 94_401 == 94_400 + 1", "== 94_601 == 94_600 + 1", 1),
]
face = rep(face, specific, "face")

# --- 0c-2. seat-push race prose needle (triple-quoted, real newlines, no backslash) --
old_race = '''pre-freeze push raced origin forward 7
    #     commits = r524 behind-signal (bm-b r746 same-window
    #     wave), merge-mode clean auto-merge closeout, delivery
    #     39ec08fa0)'''
new_race = '''pre-freeze push plain fast-forward delivery
    #     08710e2d0, zero race this window (behind 0 at fetch),
    #     zero --no-verify)'''
assert face.count(old_race) == 1, "face: seat-push race needle"
face = face.replace(old_race, new_race)

# --- 0d. B-face semantic needle: band-facts comment (post-0a form) --
# advances the B-window narrative to W140 facts (the W139 zero-hop
# double-CLEAN continuation landed past 70_001..94_600) + advances the
# gate-tail/seat references.
old_bfacts = '''# B = the arithmetic continuation from the registered W139
        # B tail (CLEAN hops=0 at both windows; double-CLEAN
        # continuation window; the W138 honest 12-hop forward walk
        # landed past the contiguous registered band mass
        # 70_001..94_000 and the W139 zero-hop continuation extended
        # it to 94_400, so the continuation is clean by construction;
        # cross-window convergence with the r743 W139 gate-tail
        # projection, seat MSG-211x tail, re-derived).'''
new_bfacts = '''# B = the arithmetic continuation from the registered W139
        # B tail (CLEAN hops=0 at both windows; double-CLEAN
        # continuation window; the W139 zero-hop double-CLEAN
        # continuation landed past the contiguous registered band
        # mass 70_001..94_600, so the continuation is clean by
        # construction; cross-window convergence with the r744
        # W139 gate-tail projection, seat MSG-215x tail, re-derived).'''
assert face.count(old_bfacts) == 1, "face: band-facts B comment needle"
face = face.replace(old_bfacts, new_bfacts)

# --- 0e. registered row parity label fixes + [139] row insertion LAST ---
# r740 parity-label law: 0a has already shifted the [137]/[138] assert
# LABELS (W137->W138, W138->W139); [136] label untouched by 0a
# (not in the 0a key set W139/W138/W137).
# No needle crosses a backslash-newline boundary (continuation built via chr(92)).
face = rep(face, [
    ('"registered W138 row parity drift (r307; bm-a r742)"',
     '"registered W137 row parity drift (r307; bm-a r742)"', 1),
], "face-parity-137")
new_139_block = (
    '"registered W138 row parity drift (r307; bm-a r743)"' + NL
    + '        assert pf.N1_BANDS[139] == {"a": (321_004, 323_003),' + NL
    + '                                    "b_exit": (94_401, 94_600),' + NL
    + '                                    "engine_owner": "bm-a"}, ' + BS + NL
    + '            "registered W139 row parity drift (r307; bm-a r744)"'
)
face = rep(face, [
    ('"registered W139 row parity drift (r307; bm-a r743)"',
     new_139_block, 1),
], "face-parity-138")

io.open(r".codely-cli\scratch_w140_face.txt", "w", encoding="utf-8", newline="\n").write(face)
print("face: W140 block transformed")

# ============ 1. perpetual_faces.py N1_BANDS row 140 ============
pf_path = r"scripts\perpetual_faces.py"
pf_src = io.open(pf_path, encoding="utf-8").read()
if '140: {"a": (323_004' in pf_src:
    print("pf: row 140 already present (idempotent skip)")
else:
    w139_row = '''    139: {"a": (321_004, 323_003), "b_exit": (94_401, 94_600),
         "engine_owner": "bm-a"},
}'''
    assert pf_src.count(w139_row) == 1, "pf: W139 row + closing brace needle"
    w140_block = '''    139: {"a": (321_004, 323_003), "b_exit": (94_401, 94_600),
         "engine_owner": "bm-a"},
    # W140 (bm-a r745 freeze, seat MSG-2026-10-05-215x-bma-w140-seat
    # pushed to origin 08710e2d0 pre-freeze r565 law (plain
    # fast-forward delivery, zero race this window, zero
    # --no-verify);
    # band gate ADMIT results/_r745bma_w140_band_gate.py: A arithmetic
    # continuation 323_003+1 -> 323_004..325_003 CLEAN hops=0; B =
    # arithmetic continuation from the W139 B tail 94_600+1 ->
    # 94_601..94_800 CLEAN hops=0 (double-CLEAN continuation window;
    # the W139 zero-hop double-CLEAN continuation landed past the
    # contiguous registered band mass 70_001..94_600, clean by
    # construction);
    # dual-window derive parity with pre-seat probe
    # results/_r745bma_w140_probe_receipt.json; scan face =
    # SEED_REGISTRY 187 int values + v1/W1 ext bands + N3-R1
    # used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/
    # N2-W15 probe points.
    # W141+ projection (gate-derived r745): A 325_004..327_003
    # CLEAN hops=0; B first-clean 323_004..323_203 hops=115
    # (pre-W140-registration baseline honest hop chain past the
    # probe cluster; B re-derive MANDATORY at W141 prereg -- the
    # baseline lands inside the now-registered W140 A band, next
    # freezer must re-derive past it, never transcribe r587 law).
    # NOT a re-pick (R250: W140 bands were never assigned).
    140: {"a": (323_004, 325_003), "b_exit": (94_601, 94_800),
         "engine_owner": "bm-a"},
}'''
    pf_src = pf_src.replace(w139_row, w140_block)
    io.open(pf_path, "w", encoding="utf-8", newline="\n").write(pf_src)
    print("pf: N1_BANDS row 140 inserted")

print("PART 1 DONE (face + pf row)")
