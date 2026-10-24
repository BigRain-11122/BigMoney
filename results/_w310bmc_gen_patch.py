# -*- coding: utf-8 -*-
"""Generate results/_w310bmc_freeze_edits.py from the proven W309 splice editor.

One-wave bump: literal anchors/keys FIRST (matched against the original text), then
lowercase wave identifiers, then uppercase wave labels, then band ranges. Single pass
each with a printed count table (r1171 law) and hard asserts (no silent no-ops).

Usage: python results/_w310bmc_gen_patch.py [--measure]
"""
import io
import re
import sys

SRC = "results/_w309bmc_freeze_edits.py"
OUT = "results/_w310bmc_freeze_edits.py"
MEASURE = "--measure" in sys.argv

s = io.open(SRC, encoding="utf-8").read()

NUM = [
    # ---- ordinals (single pass, longest first)
    ("SIXTY-THIRD", "SIXTY-FOURTH"),
    ("SIXTY-SECOND", "SIXTY-THIRD"),
    ("HUNDRED-AND-TWENTY-SIXTH", "HUNDRED-AND-TWENTY-SEVENTH"),
    ("THREE HUNDRED AND SEVENTH", "THREE HUNDRED AND EIGHTH"),
    # ---- wave constants
    ("NEW_W = 309", "NEW_W = 310"),
    ("PREV_W = 308", "PREV_W = 309"),
    ("PRIOR_W = 307", "PRIOR_W = 308"),
    ("w<308>", "w<309>"), ("w<307>", "w<308>"),
    ("len(owner_rows_live) == 298 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 127",
     "len(owner_rows_live) == 299 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 128"),
    ("(expect 298/130/127)", "(expect 299/130/128)"),
    ('"wave": 308', '"wave": 309'),
    ("wave 309: ", "wave 310: "),
    ('309: {"batch"', '310: {"batch"'),
    ('309: {{"a"', '310: {{"a"'),
    ('309: {{"batch"', '310: {{"batch"'),
    ("range(304, 296, -1)", "range(305, 297, -1)"),
    # ---- ledger / pool anchors
    ("1_101_941", "1_104_141"),
    ("675_520", "677_720"),
    # ---- parity row / leg counts
    ("167 parity rows", "168 parity rows"),
    ("legs (61)", "legs (62)"),
    ("legs (60)", "legs (61)"),
    # ---- round labels, seat sha, window stamp
    ("r1195", "r1196"), ("r1196", "r1198"),
    ("13:4x", "14:1x"),
    ("55eb0897ac", "68a4a18b1f"),
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
    ("694_901", "697_101"), ("695_100", "697_300"),
    ("695_101", "697_301"), ("695_300", "697_500"),
    ("696_900", "699_100"), ("697_100", "699_300"),
    ("697_101", "699_301"), ("697_300", "699_500"),
]
band_pat = re.compile("|".join(re.escape(k) for k, _ in BANDS))
band_tab = dict(BANDS)
s, n_band = band_pat.subn(lambda m: band_tab[m.group(0)], s)
print("band tokens bumped: %d" % n_band)

# ---- seat MSG date suffix (name already advanced by the lowercase bump)
old_msg = "20261024-1406-bmc-w310-seat"
new_msg = "20261024-1500-bmc-w310-seat"
if old_msg in s:
    print("seat MSG date suffix occurrences: %d" % s.count(old_msg))
    s = s.replace(old_msg, new_msg)

assert "NEW_W = 310" in s and "PREV_W = 309" in s and "PRIOR_W = 308" in s, "wave constants not bumped"
assert "results/_w310bmc_20261024_probe_receipt.json" in s
assert "research/PERPETUAL_N1_W310_PREREG.md" in s
assert "MSG-20261024-1500-bmc-w310-seat.md" in s
assert "68a4a18b1f" in s
assert "W309" in s and "W310" in s and s.count("W310") > 10
assert "167 parity rows" not in s and "168 parity rows" in s
assert "694_901" not in s and "697_101" in s

io.open(OUT, "w", encoding="utf-8", newline="\n").write(s)
print("WROTE %s bytes=%d" % (OUT, len(s.encode("utf-8"))))