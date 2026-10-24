# -*- coding: utf-8 -*-
# 2026-10-25 06:2x bm-c r1231 splice window: clone the proven W324 five-face freeze
# splice editor into the W325 editor.
# Face law (r1168/r1184/r1171/r1186/r1206/r1208 family):
#   1) W/w wave tokens        -> ONE simultaneous pass (no chaining)
#   2) ordinal words          -> ONE simultaneous pass
#   3) bands / tuples         -> explicit ordered replacement (B hops past the
#                                registered seed, so +2200 arithmetic is WRONG for B)
#   4) everything else        -> explicit target values with count asserts
# The B landing law CHANGES this wave (registered-seed hop), so the B-law asserts
# and prose are rewritten explicitly, never rolled.
import io, re, sys

SRC = "results/_w324bmc_freeze_edits.py"
DST = "results/_w325bmc_freeze_edits.py"

t = io.open(SRC, encoding="utf-8", newline="").read()
EOL = "\r\n" if t.count("\r\n") > (t.count("\n") - t.count("\r\n")) else "\n"
print("src lines", t.count("\n"), "EOL", repr(EOL))

# ---------- face 1: wave tokens (single pass, simultaneous) ----------
TOK = {"327": "328", "326": "327", "325": "326", "324": "325",
       "323": "324", "322": "323", "321": "322"}


def tok(m):
    pre, num = m.group(1), m.group(2)
    return pre + TOK.get(num, num)


t2, n_tok = re.subn(r"([Ww])(3[0-9]{2})", tok, t)
print("wave tokens shifted:", n_tok)

# ---------- face 2: ordinal words (single pass, simultaneous) ----------
ORD = {
    "SEVENTY-SEVENTH": "SEVENTY-EIGHTH",
    "SEVENTY-EIGHTH": "SEVENTY-NINTH",
    "THREE HUNDRED AND FOURTEENTH": "THREE HUNDRED AND FIFTEENTH",
    "HUNDRED-AND-FORTY-THIRD": "HUNDRED-AND-FORTY-FOURTH",
}
pat_ord = re.compile("|".join(sorted((re.escape(k) for k in ORD), key=len, reverse=True)))
t3, n_ord = pat_ord.subn(lambda m: ORD[m.group(0)], t2)
print("ordinal words shifted:", n_ord)

# ---------- face 3: explicit target values ----------
REPL = [
    # ---- header / lineage ----
    ("# 2026-10-25 05:3x bm-c r1229 splice window", "# 2026-10-25 06:2x bm-c r1231 splice window"),
    ("# Lineage = results/_w324bmc_freeze_edits.py (proven live-fire freeze, bm-c r1205;",
     "# Lineage = results/_w325bmc_freeze_edits.py (proven live-fire freeze, bm-c r1229;"),
    ("block's own w<321> boundary", "block's own w<322> boundary"),
    ("the template's w<318> by exactly one", "the template's w<319> by exactly one"),
    # ---- BANDS comment block (rewritten wholesale: B landing law changed) ----
    ("""# BANDS (frozen research/PERPETUAL_N1_W325_PREREG.md sec.3, re-derived live this
# window): A 728_101..730_100 (STAIRCASE-AFFECTS-A 1-hop walk, SEVENTY-EIGHTH
# consecutive A-hop; naive 727_901..729_900 refused at start by the registered
# W324 B band 730_101..730_300; A base == registered prior-wave B tail+1 EXACT)
# and B 730_101..730_300 (1-hop own-A RESERVATION CASCADE above own-A, SEVENTY-NINTH
# consecutive above-own-A; naive 728_101..728_300 lands inside the own-wave A
# first-clean window; B base == own-A tail+1 EXACT). ADMIT receipt
# results/_w325bmc_20261025_probe_receipt.json.""",
     """# BANDS (frozen research/PERPETUAL_N1_W325_PREREG.md sec.3, re-derived live this
# window): A 730_301..732_300 (STAIRCASE-AFFECTS-A 1-hop walk, SEVENTY-EIGHTH
# consecutive A-hop; naive 730_101..732_100 refused at start by the registered
# W324 B band; A base == registered prior-wave B tail+1 EXACT)
# and B 732_501..732_700 (1-HOP own-A RESERVATION CASCADE + REGISTERED-SEED HOP,
# SEVENTY-NINTH consecutive above-own-A; naive 730_301..730_500 lands inside the
# own-wave A first-clean window; the cascade window 732_301..732_500 is REFUSED by
# the registered seed perpetual_n2_w18_gen=732_500, so B = the FIRST CLEAN WINDOW
# ABOVE OWN-A, i.e. base != own-A tail+1 -- W325 new landing law, disclosed).
# ADMIT receipt results/_w325bmc_20261025_probe_receipt.json."""),
    # ---- upstream finalize anchors (W324: ledger 1,137,141 / K 710,720) ----
    ("assert w324_total == 1_134_941 and w324_merged_n == 708_520",
     "assert w324_total == 1_137_141 and w324_merged_n == 710_720"),
    ("(expect 1,134,941 / 708,520)", "(expect 1,137,141 / 710,720)"),
    ("finalize one-pass ledger 1,132,741 / K=706,320 machine-read",
     "finalize one-pass ledger 1,134,941 / 708,520 machine-read"),
    # ---- band tuples (before the range map) ----
    ("(a_lo, a_hi) == (728_101, 730_100) and (b_lo, b_hi) == (730_101, 730_300)",
     "(a_lo, a_hi) == (730_301, 732_300) and (b_lo, b_hi) == (732_501, 732_700)"),
    # ---- owner-row ordinals ----
    ("assert len(owner_rows_live) == 313 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 142",
     "assert len(owner_rows_live) == 314 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 143"),
    ("(expect 313/130/142)", "(expect 314/130/143)"),
    # ---- plain-digit faces ----
    ("""'321: {"a"'""", """'322: {"a"'"""),
    ("range(315, 307, -1)", "range(316, 308, -1)"),
    ("PRIOR_W = 322", "PRIOR_W = 323"),
    ("NEW_W = 324", "NEW_W = 325"),
    ("PREV_W = 323", "PREV_W = 324"),
    ('"wave": 323', '"wave": 324'),
    # ---- seat face ----
    ("MSG-20261025-0508-bmc-w325-seat.md", "MSG-20261025-0556-bmc-w325-seat.md"),
    ('SEAT_ORIGIN = "08daa60a30"', 'SEAT_ORIGIN = "4a16e4d4b7"'),
    # ---- prose round labels ----
    ("(r1228, queue-head seat-first supply", "(r1230, queue-head seat-first supply"),
    ("bm-c r1229 window derive landed", "bm-c r1231 window derive landed"),
    ("executed at the bm-c r1228 splice window", "executed at the bm-c r1230 splice window"),
    ("derived by the bm-c r1229 window", "derived by the bm-c r1231 window"),
    ('+ " r1228 BEFORE the freeze (r565 law);', '+ " r1230 BEFORE the freeze (r565 law);'),
    # ---- parity prose (prose arithmetic repaired: 69 estate + 37 kept + 77 fresh = 183) ----
    ("the W325 block's own W248..W324 legs (76) are", "the W325 block's own W248..W324 legs (77) are"),
    ("W248..W324 legs (76) added, machine-derived from the live pf",
     "W248..W324 legs (77) added, machine-derived from the live pf"),
    ("-> 186 parity rows", "-> 183 parity rows"),
    # ---- B landing law: code-level asserts ----
    ('assert b_lo == a_hi + 1, "B base == own-A tail+1 EXACT (own-A reservation cascade)"',
     'seed_hop = leg1.get("B_seed_hop_disclosure") or []\n'
     'assert seed_hop, "B registered-seed hop disclosure missing (W325 new landing law)"\n'
     'assert b_lo == a_hi + 201, "B base == FIRST CLEAN WINDOW above own-A tail (cascade window refused by a registered seed)"\n'
     'assert seed_hop[0]["seed"] == b_lo - 1 == a_hi + 200, "seed-hop refuser is not at the cascade-window tail"\n'
     'assert str(seed_hop[0]["refuser"]).startswith("REG:"), "seed-hop refuser must be a registered seed"'),
    ("""assert (ra.get("A_staircase_hop_past_registered_prior_B") or ra.get("A_base_ge_priorB_tail_plus1")) \\
    and ra.get("A_base_ge_priorB_tail_plus1") \\
    and ra.get("B_lands_above_own_A") and ra.get("AB_mutual_exclusion") \\
    and ra.get("B_base_eq_own_A_tail_plus1"), f"probe receipt relation face drift: {ra}\"""",
     """assert (ra.get("A_staircase_hop_past_registered_prior_B") or ra.get("A_base_ge_priorB_tail_plus1")) \\
    and ra.get("A_base_ge_priorB_tail_plus1") \\
    and ra.get("B_lands_above_own_A") and ra.get("AB_mutual_exclusion") \\
    and ra.get("B_base_eq_first_clean_above_own_A") \\
    and ra.get("B_base_eq_own_A_tail_plus1") is False, \\
    f"probe receipt relation face drift: {ra}\""""),
]

for old, new in REPL:
    c = t3.count(old)
    assert c >= 1, f"replacement anchor MISSING: {old[:70]!r}"
    t3 = t3.replace(old, new)
    print(f"  rep x{c}: {old[:56]!r}")

# ---------- face 4: band ranges (ordered; B is NOT +2200) ----------
RANGES = [
    ("728_101..730_100", "730_301..732_300"),   # A band
    ("730_101..730_300", "732_501..732_700"),   # B band (seed hop: 732_301..732_500 refused)
    ("727_901..729_900", "730_101..732_100"),   # A naive continuation
    ("728_101..728_300", "730_301..730_500"),   # B naive continuation
    ("727_901..728_100", "730_101..730_300"),   # prior-wave B band (refuser)
]
for old, new in RANGES:
    c = t3.count(old)
    if c == 0:
        print(f"  band skip (already rewritten by a block swap): {old}")
        continue
    t3 = t3.replace(old, new)
    print(f"  band x{c}: {old} -> {new}")

io.open(DST, "w", encoding="utf-8", newline="").write(t3)
print("wrote", DST, len(t3), "chars")

# ---------- structural self-checks ----------
import py_compile
py_compile.compile(DST, doraise=True)
print("py_compile green")
for s in ('NEW_W = 325', 'PREV_W = 324', 'PRIOR_W = 323', 'PRIOR_W = 323',
          'n1_w325_results.json', '"shard_subdir": "n1_w325"',
          'MSG-20261025-0556-bmc-w325-seat.md', 'SEAT_ORIGIN = "4a16e4d4b7"',
          'range(316, 308, -1)', "'322: {\"a\"'",
          'PERPETUAL_N1_W325_PREREG.md', '_w325bmc_20261025_probe_receipt.json',
          '_w325bmc_freeze_receipt.json', '1_137_141', '710_720',
          '(730_301, 732_300)', '183 parity rows', 'SEVENTY-NINTH',
          'THREE HUNDRED AND FIFTEENTH', 'HUNDRED-AND-FORTY-FOURTH'):
    c = t3.count(s)
    print(f"  check {s!r} x{c}")
    assert c >= 1, f"missing {s}"
for stale in ('SEVENTY-SEVENTH', 'THREE HUNDRED AND FOURTEENTH',
              'HUNDRED-AND-FORTY-THIRD', '728_101..730_100',
              '"wave": 323', 'NEW_W = 324', 'MSG-20261025-0508-bmc-w324-seat',
              '1_134_941 and w324_merged_n == 708_520'):
    print(f"  stale probe {stale!r} x{t3.count(stale)}")
    assert stale not in t3, f"stale literal survived: {stale}"