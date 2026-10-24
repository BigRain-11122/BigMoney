# -*- coding: utf-8 -*-
# 2026-10-25 04:3x bm-c r1227 splice window: clone the proven W322 five-face freeze
# splice editor into the W323 editor.
# Wave-token face = single-pass simultaneous map (r1168/r1184 law: no sequential
# double-shift of ordinals or wave tokens). Plain-digit face (row numbers, cut
# markers, boundary literals, band tuples) and the numeric/anchors face are
# written as TARGET values explicitly with count asserts (r1171/r1186/r1206/r1208 law).
import io, re, sys

SRC = "results/_w322bmc_freeze_edits.py"
DST = "results/_w323bmc_freeze_edits.py"

t = io.open(SRC, encoding="utf-8", newline="").read()
EOL = "\r\n" if t.count("\r\n") > (t.count("\n") - t.count("\r\n")) else "\n"

# ---------- face 1: wave tokens (single pass, simultaneous) ----------
TOK = {"324": "325", "323": "324", "322": "323", "321": "322"}


def tok(m):
    pre, num = m.group(1), m.group(2)
    return pre + TOK.get(num, num)


t2, n_tok = re.subn(r"([Ww])(3[0-9]{2})", tok, t)
print("wave tokens shifted:", n_tok)

# ---------- face 2: ordinal words (single pass, simultaneous) ----------
ORD = {
    "SEVENTY-FIFTH": "SEVENTY-SIXTH",
    "SEVENTY-SIXTH": "SEVENTY-SEVENTH",
    "THREE HUNDRED AND TWELFTH": "THREE HUNDRED AND THIRTEENTH",
    "HUNDRED-AND-FORTY-FIRST": "HUNDRED-AND-FORTY-SECOND",
}
pat_ord = re.compile("|".join(sorted((re.escape(k) for k in ORD), key=len, reverse=True)))
t3, n_ord = pat_ord.subn(lambda m: ORD[m.group(0)], t2)
print("ordinal words shifted:", n_ord)

# ---------- face 3: explicit target values (post-shift form) ----------
REPL = [
    # header window label / lineage boundary marker (plain digits, no wave token)
    ("# 2026-10-25 03:5x bm-c r1226 splice window", "# 2026-10-25 04:4x bm-c r1227 splice window"),
    ("block's own w<319> boundary", "block's own w<320> boundary"),
    # finalize anchors of the upstream wave (W322: ledger 1,132,741 / K 706,320)
    ("1_130_541 and w322_merged_n == 704_120", "1_132_741 and w322_merged_n == 706_320"),
    ("(expect 1,130,541 / 704,120)", "(expect 1,132,741 / 706,320)"),
    # frozen bands (A 725_901..727_900 / B 727_901..728_100) -- band prose + tuples
    ("A 723_701..725_700 (STAIRCASE-AFFECTS-A 1-hop walk",
     "A 725_901..727_900 (STAIRCASE-AFFECTS-A 1-hop walk"),
    ("naive 723_501..725_500 refused at start by the registered",
     "naive 725_701..727_700 refused at start by the registered"),
    ("B band 723_501..723_700; A base == registered prior-wave B tail+1 EXACT)",
     "B band 725_701..725_900; A base == registered prior-wave B tail+1 EXACT)"),
    ("and B 725_701..725_900 (1-hop own-A RESERVATION CASCADE above own-A",
     "and B 727_901..728_100 (1-hop own-A RESERVATION CASCADE above own-A"),
    ("naive 723_701..723_900 lands inside the own-wave A",
     "naive 725_901..726_100 lands inside the own-wave A"),
    ("(a_lo, a_hi) == (723_701, 725_700) and (b_lo, b_hi) == (725_701, 725_900)",
     "(a_lo, a_hi) == (725_901, 727_900) and (b_lo, b_hi) == (727_901, 728_100)"),
    # registry ordinals (plain digits, outside the token map)
    ("assert len(owner_rows_live) == 311 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 140",
     "assert len(owner_rows_live) == 312 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 141"),
    ("(expect 311/130/140)", "(expect 312/130/141)"),
    # previous boundary row + chain-dep scan window (plain digits)
    ("""'319: {"a"'""", """'320: {"a"'"""),
    ("range(313, 305, -1)", "range(314, 306, -1)"),
    ("PRIOR_W = 320", "PRIOR_W = 321"),
    # wave-config plain digits
    ("NEW_W = 322", "NEW_W = 323"),
    ("PREV_W = 321", "PREV_W = 322"),
    ('"wave": 321', '"wave": 322'),
    # own seat face
    ("MSG-20261025-0314-bmc-w323-seat", "MSG-20261025-0420-bmc-w323-seat"),
    ('SEAT_ORIGIN = "d8136c2994"', 'SEAT_ORIGIN = "51fa4ede93"'),
    # prose round labels (plain digits)
    ("(r1225, queue-head seat-first supply", "(r1226, queue-head seat-first supply"),
    ("bm-c r1224 window derive landed", "bm-c r1227 window derive landed"),
    ("executed at the bm-c r1224 splice window", "executed at the bm-c r1226 splice window"),
    ("derived by the bm-c r1224 window", "derived by the bm-c r1227 window"),
    ('+ " r1224 BEFORE the freeze (r565 law);', '+ " r1226 BEFORE the freeze (r565 law);'),
    # parity prose counts
    ("the W323 block's own W248..W322 legs (74) are", "the W323 block's own W248..W322 legs (75) are"),
    ("W248..W322 legs (74) added, machine-derived from the live pf",
     "W248..W322 legs (75) added, machine-derived from the live pf"),
    ("-> 180 parity rows", "-> 185 parity rows"),
]

for old, new in REPL:
    c = t3.count(old)
    assert c >= 1, f"replacement anchor MISSING: {old[:70]!r}"
    t3 = t3.replace(old, new)
    print(f"  rep x{c}: {old[:60]!r} -> {new[:60]!r}")

# ---------- band-token map (single pass; tuples never chained) ----------
BANDS = {
    "723_501..725_500": "725_701..727_700",
    "723_501..723_700": "725_701..725_900",
    "723_701..725_700": "725_901..727_900",
    "723_701..723_900": "725_901..726_100",
    "725_701..725_900": "727_901..728_100",
}
pat_b = re.compile("|".join(sorted((re.escape(k) for k in BANDS), key=len, reverse=True)))
t3, n_b = pat_b.subn(lambda m: BANDS[m.group(0)], t3)
print("band-range tokens mapped:", n_b)

io.open(DST, "w", encoding="utf-8", newline="").write(t3)
print("wrote", DST, len(t3), "chars")

# ---------- structural self-checks ----------
import py_compile
py_compile.compile(DST, doraise=True)
print("py_compile green")
for s in ('NEW_W = 323', 'PREV_W = 322', 'PRIOR_W = 321',
          'n1_w323_results.json', '"shard_subdir": "n1_w323"',
          'MSG-20261025-0420-bmc-w323-seat', 'SEAT_ORIGIN = "51fa4ede93"',
          'range(314, 306, -1)', "'320: {\"a\"'",
          'PERPETUAL_N1_W323_PREREG.md', '_w323bmc_20261025_probe_receipt.json',
          '_w323bmc_freeze_receipt.json', '1_132_741', '706_320',
          '(725_901, 727_900)', '185 parity rows'):
    c = t3.count(s)
    print(f"  check {s!r} x{c}")
    assert c >= 1, f"missing {s}"
for stale in ('SEVENTY-FIFTH', 'HUNDRED-AND-FORTY-FIRST', '723_501', '723_701',
              'wave": 321', 'NEW_W = 322'):
    print(f"  stale probe {stale!r} x{t3.count(stale)}")
    assert stale not in t3, f"stale literal survived: {stale}"