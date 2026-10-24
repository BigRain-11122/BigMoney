# -*- coding: utf-8 -*-
"""Generate results/_w311bmc_freeze_edits.py from the proven W310 splice editor.

One-wave bump: literal anchors/keys FIRST (matched against the original text), then
lowercase wave identifiers, then uppercase wave labels, then band ranges. Single pass
each with a printed count table (r1171 law) and hard asserts (no silent no-ops).

Usage: python results/_w311bmc_gen_patch.py [--measure]
"""
import io
import re
import sys

SRC = "results/_w310bmc_freeze_edits.py"
OUT = "results/_w311bmc_freeze_edits.py"
MEASURE = "--measure" in sys.argv

s = io.open(SRC, encoding="utf-8").read()

NUM = [
    # ---- ordinals (single pass, longest first)
    ("SIXTY-FOURTH", "SIXTY-FIFTH"),
    ("SIXTY-THIRD", "SIXTY-FOURTH"),
    ("HUNDRED-AND-TWENTY-SEVENTH", "HUNDRED-AND-TWENTY-EIGHTH"),
    ("THREE HUNDRED AND EIGHTH", "THREE HUNDRED AND NINTH"),
    # ---- wave constants
    ("NEW_W = 310", "NEW_W = 311"),
    ("PREV_W = 309", "PREV_W = 310"),
    ("PRIOR_W = 308", "PRIOR_W = 309"),
    ("w<309>", "w<310>"), ("w<308>", "w<309>"),
    ("len(owner_rows_live) == 299 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 128",
     "len(owner_rows_live) == 300 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 129"),
    ("(expect 299/130/128)", "(expect 300/130/129)"),
    ("wave 310: ", "wave 311: "),
    ('310: {"batch"', '311: {"batch"'),
    ('310: {{"batch"', '311: {{"batch"'),
    ('310: {{"a"', '311: {{"a"'),
    ("range(305, 297, -1)", "range(306, 298, -1)"),
    # ---- ledger / pool anchors
    ("1_104_141", "1_106_341"),
    ("1,101,941", "1,106,341"),
    ("675,520", "679,920"),
    ("677_720", "679_920"),
    # ---- parity row / leg counts
    ("168 parity rows", "169 parity rows"),
    ("legs (62)", "legs (63)"),
    ("legs (61)", "legs (62)"),
    # ---- seat sha / window stamp
    ("14:1x", "15:1x"),
    ("68a4a18b1f", "5cbfce8417"),
]

counts = {}
for a, _ in NUM:
    counts[a] = s.count(a)
print("COUNT TABLE:")
for a, _ in sorted(NUM, key=lambda kv: -len(kv[0])):
    print("  key=%s -> %d" % (a.encode("ascii", "backslashreplace").decode(), counts[a]))
zero = [a for a in counts if counts[a] == 0]
assert not zero, "zero-hit keys: %r" % zero
if MEASURE:
    print("MEASURE ok")
    sys.exit(0)

tab = dict(NUM)
pat = re.compile("|".join(re.escape(a) for a, _ in sorted(NUM, key=lambda kv: -len(kv[0]))))
s = pat.sub(lambda m: tab[m.group(0)], s)

# ---- round labels (+2 windows) via sentinels (no pairwise cascade)
s = s.replace("r1196", "ZZRR1").replace("r1198", "ZZRR2")
s = s.replace("ZZRR1", "r1198").replace("ZZRR2", "r1200")
print("round labels: r1198=%d r1200=%d" % (s.count("r1198"), s.count("r1200")))

# ---- lowercase wave identifiers (also n1_wNNN and _wNNNbmc_)
s, n_lc = re.subn(r"w(\d{3})", lambda m: "w%03d" % (int(m.group(1)) + 1)
                  if int(m.group(1)) >= 301 else m.group(0), s)
print("lowercase wave tokens bumped: %d" % n_lc)

# ---- uppercase wave labels W>=301
s, n_uc = re.subn(r"W(\d{3})", lambda m: "W%03d" % (int(m.group(1)) + 1)
                  if int(m.group(1)) >= 301 else m.group(0), s)
print("uppercase wave tokens bumped: %d" % n_uc)

# ---- band ranges (explicit table, no ledger anchor touched; all +2200)
BANDS = [
    ("697_101", "699_301"), ("697_300", "699_500"),
    ("697_301", "699_501"), ("697_500", "699_700"),
    ("699_100", "701_300"), ("699_300", "701_500"),
    ("699_301", "701_501"), ("699_500", "701_700"),
]
band_pat = re.compile("|".join(re.escape(k) for k, _ in BANDS))
band_tab = dict(BANDS)
s, n_band = band_pat.subn(lambda m: band_tab[m.group(0)], s)
print("band tokens bumped: %d" % n_band)

# ---- seat MSG date suffix (name already advanced by the lowercase bump)
old_msg = "20261024-1500-bmc-w311-seat"
new_msg = "20261024-1540-bmc-w311-seat"
if old_msg in s:
    print("seat MSG date suffix occurrences: %d" % s.count(old_msg))
    s = s.replace(old_msg, new_msg)

# ---- stale expect-message alignment (assert values already bumped above)
stale = "(expect 1,106,341 / 675,520)"
if stale in s:
    s = s.replace(stale, "(expect 1,106,341 / 679,920)")

assert "NEW_W = 311" in s and "PREV_W = 310" in s and "PRIOR_W = 309" in s, "wave constants not bumped"
assert "results/_w311bmc_20261024_probe_receipt.json" in s
assert "research/PERPETUAL_N1_W311_PREREG.md" in s
assert "MSG-20261024-1540-bmc-w311-seat.md" in s
assert "5cbfce8417" in s
assert "W310" in s and "W311" in s and s.count("W311") > 10
assert "168 parity rows" not in s and "169 parity rows" in s
assert "697_101" not in s and "699_301" in s
assert "1_104_141" not in s and "1_106_341" in s
assert "677_720" not in s and "679_920" in s

io.open(OUT, "w", encoding="utf-8", newline="\n").write(s)
print("WROTE %s bytes=%d" % (OUT, len(s.encode("utf-8"))))