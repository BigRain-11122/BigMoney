# -*- coding: utf-8 -*-
# 2026-10-25 03:xx bm-c r1226 splice window: clone the proven W321 five-face freeze
# splice editor into the W322 editor.
# Wave-token face = single-pass simultaneous map (r1168/r1184 law: no sequential
# double-shift of ordinals or wave tokens). Plain-digit face (row numbers, cut
# markers, boundary literals) and the numeric/anchors face are written as TARGET
# values explicitly with count asserts (r1171/r1186/r1206/r1208 law).
import io, re, sys

SRC = "results/_w321bmc_freeze_edits.py"
DST = "results/_w322bmc_freeze_edits.py"

t = io.open(SRC, encoding="utf-8", newline="").read()
EOL = "\r\n" if t.count("\r\n") > (t.count("\n") - t.count("\r\n")) else "\n"

# ---------- face 1: wave tokens (single pass, simultaneous) ----------
TOK = {"322": "323", "321": "322", "320": "321"}


def tok(m):
    pre, num = m.group(1), m.group(2)
    return pre + TOK.get(num, num)


t2, n_tok = re.subn(r"([Ww])(3[0-9]{2})", tok, t)
print("wave tokens shifted:", n_tok)

# ---------- face 2: ordinal words (single pass, simultaneous) ----------
ORD = {
    "SEVENTY-FOURTH": "SEVENTY-FIFTH",
    "SEVENTY-FIFTH": "SEVENTY-SIXTH",
    "THREE HUNDRED AND ELEVENTH": "THREE HUNDRED AND TWELFTH",
    "HUNDRED-AND-FORTIETH": "HUNDRED-AND-FORTY-FIRST",
}
pat_ord = re.compile("|".join(sorted((re.escape(k) for k in ORD), key=len, reverse=True)))
t3, n_ord = pat_ord.subn(lambda m: ORD[m.group(0)], t2)
print("ordinal words shifted:", n_ord)

# ---------- face 3: explicit target values (post-shift form) ----------
REPL = [
    # finalize anchors of the upstream wave (W321: ledger 1,130,541 / K 704,120)
    ("1_128_341 and w321_merged_n == 701_920", "1_130_541 and w321_merged_n == 704_120"),
    ("(expect 1,128,341 / 701,920)", "(expect 1,130,541 / 704,120)"),
    # frozen bands (A 723_701..725_700 / B 725_701..725_900)
    ("(a_lo, a_hi) == (721_501, 723_500) and (b_lo, b_hi) == (723_501, 723_700)",
     "(a_lo, a_hi) == (723_701, 725_700) and (b_lo, b_hi) == (725_701, 725_900)"),
    # band prose (naive continuations + refuser bands)
    ("naive 721_301..723_300 refused at start by the registered W321 B band 721_301..721_500",
     "naive 723_501..725_500 refused at start by the registered W321 B band 723_501..723_700"),
    ("naive 721_501..721_700 clean vs registered", "naive 723_701..723_900 clean vs registered"),
    # shard subdir target (r1221 family: written as the TARGET wave, never inherited)
    ('"shard_subdir": "n1_w321"', '"shard_subdir": "n1_w322"'),
    # own seat face
    ("MSG-20261025-0205-bmc-w322-seat", "MSG-20261025-0314-bmc-w322-seat"),
    ('SEAT_ORIGIN = "3455fa2aa4"', 'SEAT_ORIGIN = "d8136c2994"'),
    ('"wave": 320', '"wave": 321'),
    # registry ordinals (plain digits, outside the token map)
    ("assert len(owner_rows_live) == 310 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 139",
     "assert len(owner_rows_live) == 311 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 140"),
    ("(expect 310/130/139)", "(expect 311/130/140)"),
    # previous boundary row + chain-dep scan window (plain digits)
    ("""'318: {"a"'""", """'319: {"a"'"""),
    ("range(312, 304, -1)", "range(313, 305, -1)"),
    ("PRIOR_W = 319", "PRIOR_W = 320"),
    # wave-config plain digits
    ("NEW_W = 321", "NEW_W = 322"),
    ("PREV_W = 320", "PREV_W = 321"),
    # parity prose counts
    ("the W322 block's own W248..W321 legs (69)", "the W322 block's own W248..W321 legs (74)"),
    ("W248..W321 legs (69) added, machine-derived from the live pf",
     "W248..W321 legs (74) added, machine-derived from the live pf"),
    ("-> 175 parity rows", "-> 180 parity rows"),
]

for old, new in REPL:
    c = t3.count(old)
    assert c >= 1, f"replacement anchor MISSING: {old[:70]!r}"
    t3 = t3.replace(old, new)
    print(f"  rep x{c}: {old[:60]!r} -> {new[:60]!r}")

# residual plain-digit traps: any bare 3xx that must move
for bad, want in (("'0', 304", "'0', 304"),):
    pass

io.open(DST, "w", encoding="utf-8", newline="").write(t3)
print("wrote", DST, len(t3), "chars")

# ---------- structural self-checks ----------
import py_compile
py_compile.compile(DST, doraise=True)
print("py_compile green")
for s in ('NEW_W = 322', 'PREV_W = 321', 'PRIOR_W = 320',
          'n1_w322_results.json', '"shard_subdir": "n1_w322"',
          'MSG-20261025-0314-bmc-w322-seat', 'SEAT_ORIGIN = "d8136c2994"',
          'range(313, 305, -1)', "'319: {\"a\"'",
          'PERPETUAL_N1_W322_PREREG.md', '_w322bmc_20261025_probe_receipt.json',
          '_w322bmc_freeze_receipt.json'):
    c = t3.count(s)
    print(f"  check {s!r} x{c}")
    assert c >= 1, f"missing {s}"
for stale in ('W321 five-face splice', 'n1_w320', 'SEVENTY-FOURTH', 'HUNDRED-AND-FORTIETH'):
    print(f"  stale probe {stale!r} x{t3.count(stale)}")