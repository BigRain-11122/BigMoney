# -*- coding: utf-8 -*-
# 2026-10-25 05:3x bm-c r1229 splice window: clone the proven W323 five-face freeze
# splice editor into the W324 editor.
# Wave-token face = single-pass simultaneous map (r1168/r1184 law: no sequential
# double-shift of ordinals or wave tokens). Plain-digit face (row numbers, cut
# markers, boundary literals, band tuples) and the numeric/anchors face are
# written as TARGET values explicitly with count asserts (r1171/r1186/r1206/r1208 law).
import io, re, sys

SRC = "results/_w323bmc_freeze_edits.py"
DST = "results/_w324bmc_freeze_edits.py"

t = io.open(SRC, encoding="utf-8", newline="").read()
EOL = "\r\n" if t.count("\r\n") > (t.count("\n") - t.count("\r\n")) else "\n"

# ---------- face 1: wave tokens (single pass, simultaneous) ----------
TOK = {"325": "326", "324": "325", "323": "324", "322": "323", "321": "322"}


def tok(m):
    pre, num = m.group(1), m.group(2)
    return pre + TOK.get(num, num)


t2, n_tok = re.subn(r"([Ww])(3[0-9]{2})", tok, t)
print("wave tokens shifted:", n_tok)

# ---------- face 2: ordinal words (single pass, simultaneous) ----------
ORD = {
    "SEVENTY-SIXTH": "SEVENTY-SEVENTH",
    "SEVENTY-SEVENTH": "SEVENTY-EIGHTH",
    "THREE HUNDRED AND THIRTEENTH": "THREE HUNDRED AND FOURTEENTH",
    "HUNDRED-AND-FORTY-SECOND": "HUNDRED-AND-FORTY-THIRD",
}
pat_ord = re.compile("|".join(sorted((re.escape(k) for k in ORD), key=len, reverse=True)))
t3, n_ord = pat_ord.subn(lambda m: ORD[m.group(0)], t2)
print("ordinal words shifted:", n_ord)

# ---------- face 3: explicit target values (post-shift form) ----------
REPL = [
    # header window label / lineage boundary marker (plain digits, no wave token)
    ("# 2026-10-25 04:4x bm-c r1227 splice window", "# 2026-10-25 05:3x bm-c r1229 splice window"),
    ("block's own w<320> boundary", "block's own w<321> boundary"),
    # finalize anchors of the upstream wave (W323: ledger 1,134,941 / K 708,520)
    ("1_132_741 and w323_merged_n == 706_320", "1_134_941 and w323_merged_n == 708_520"),
    ("(expect 1,132,741 / 706,320)", "(expect 1,134,941 / 708,520)"),
    ("finalize one-pass ledger 1,128,341 / K=701,920 machine-read",
     "finalize one-pass ledger 1,132,741 / K=706,320 machine-read"),
    # frozen-band tuples (range prose lives in the BANDS map below)
    ("(a_lo, a_hi) == (725_901, 727_900) and (b_lo, b_hi) == (727_901, 728_100)",
     "(a_lo, a_hi) == (728_101, 730_100) and (b_lo, b_hi) == (730_101, 730_300)"),
    # registry ordinals (plain digits, outside the token map)
    ("assert len(owner_rows_live) == 312 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 141",
     "assert len(owner_rows_live) == 313 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 142"),
    ("(expect 312/130/141)", "(expect 313/130/142)"),
    # previous boundary row + chain-dep scan window (plain digits)
    ("""'320: {"a"'""", """'321: {"a"'"""),
    ("range(314, 306, -1)", "range(315, 307, -1)"),
    ("PRIOR_W = 321", "PRIOR_W = 322"),
    # wave-config plain digits
    ("NEW_W = 323", "NEW_W = 324"),
    ("PREV_W = 322", "PREV_W = 323"),
    ('"wave": 322', '"wave": 323'),
    # own seat face
    ("MSG-20261025-0420-bmc-w324-seat", "MSG-20261025-0508-bmc-w324-seat"),
    ('SEAT_ORIGIN = "51fa4ede93"', 'SEAT_ORIGIN = "08daa60a30"'),
    # prose round labels (plain digits)
    ("(r1226, queue-head seat-first supply", "(r1228, queue-head seat-first supply"),
    ("bm-c r1227 window derive landed", "bm-c r1229 window derive landed"),
    ("executed at the bm-c r1226 splice window", "executed at the bm-c r1228 splice window"),
    ("derived by the bm-c r1227 window", "derived by the bm-c r1229 window"),
    ('+ " r1226 BEFORE the freeze (r565 law);', '+ " r1228 BEFORE the freeze (r565 law);'),
    # parity prose counts
    ("the W324 block's own W248..W323 legs (75) are",
     "the W324 block's own W248..W323 legs (76) are"),
    ("W248..W323 legs (75) added, machine-derived from the live pf",
     "W248..W323 legs (76) added, machine-derived from the live pf"),
    ("-> 185 parity rows", "-> 186 parity rows"),
]

for old, new in REPL:
    c = t3.count(old)
    assert c >= 1, f"replacement anchor MISSING: {old[:70]!r}"
    t3 = t3.replace(old, new)
    print(f"  rep x{c}: {old[:60]!r} -> {new[:60]!r}")

# ---------- band-token map (single pass; tuples never chained) ----------
BANDS = {
    "725_701..727_700": "727_901..729_900",
    "725_901..727_900": "728_101..730_100",
    "725_701..725_900": "727_901..728_100",
    "725_901..726_100": "728_101..728_300",
    "727_901..728_100": "730_101..730_300",
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
for s in ('NEW_W = 324', 'PREV_W = 323', 'PRIOR_W = 322',
          'n1_w324_results.json', '"shard_subdir": "n1_w324"',
          'MSG-20261025-0508-bmc-w324-seat', 'SEAT_ORIGIN = "08daa60a30"',
          'range(315, 307, -1)', "'321: {\"a\"'",
          'PERPETUAL_N1_W324_PREREG.md', '_w324bmc_20261025_probe_receipt.json',
          '_w324bmc_freeze_receipt.json', '1_134_941', '708_520',
          '(728_101, 730_100)', '186 parity rows'):
    c = t3.count(s)
    print(f"  check {s!r} x{c}")
    assert c >= 1, f"missing {s}"
for stale in ('SEVENTY-SIXTH', 'HUNDRED-AND-FORTY-SECOND', '725_901..727_900',
              'wave": 322', 'NEW_W = 323',
              'MSG-20261025-0420-bmc-w324-seat'):
    print(f"  stale probe {stale!r} x{t3.count(stale)}")
    assert stale not in t3, f"stale literal survived: {stale}"