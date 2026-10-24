# -*- coding: utf-8 -*-
"""Generate results/_w309bmc_freeze_edits.py from the proven W308 splice editor.

One-wave bump: literal anchors/keys FIRST (matched against the original text), then
lowercase wave identifiers, then uppercase wave labels, then band ranges. Single pass
each with a printed count table (r1171 law) and hard asserts (no silent no-ops).

Usage: python results/_w309bmc_gen_freeze.py [--measure]
"""
import io
import re
import sys

SRC = "results/_w308bmc_freeze_edits.py"
OUT = "results/_w309bmc_freeze_edits.py"
MEASURE = "--measure" in sys.argv

s = io.open(SRC, encoding="utf-8").read()

NUM = [
    # ---- ordinals (single pass, longest first)
    ("SIXTY-SECOND", "SIXTY-THIRD"),
    ("SIXTY-FIRST", "SIXTY-SECOND"),
    ("HUNDRED-AND-TWENTY-FIFTH", "HUNDRED-AND-TWENTY-SIXTH"),
    ("THREE HUNDRED AND SIXTH", "THREE HUNDRED AND SEVENTH"),
    # ---- wave constants
    ("NEW_W = 308", "NEW_W = 309"),
    ("PREV_W = 307", "PREV_W = 308"),
    ("PRIOR_W = 306", "PRIOR_W = 307"),
    ("w<307>", "w<308>"), ("w<306>", "w<307>"),
    ("len(owner_rows_live) == 297 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 126",
     "len(owner_rows_live) == 298 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 127"),
    ("(expect 297/130/126)", "(expect 298/130/127)"),
    ('"wave": 307', '"wave": 308'),
    ("wave 308: ", "wave 309: "),
    ('308: {{"a"', '309: {{"a"'),
    ('308: {"batch"', '309: {"batch"'),
    ('{CFG_I}308: {{"batch"', '{CFG_I}309: {{"batch"'),
    ("range(303, 295, -1)", "range(304, 296, -1)"),
    # ---- ledger / pool anchors
    ("1,099,741", "1,101,941"),
    ("1_099_741", "1_101_941"),
    ("673,320", "675,520"),
    ("673_320", "675_520"),
    # ---- parity row / leg counts
    ("166 parity rows", "167 parity rows"),
    ("legs (60)", "legs (61)"),
    ("legs (59)", "legs (60)"),
    # ---- round labels, seat sha, window stamp
    ("r1193", "r1195"), ("r1194", "r1196"),
    ("r309;", "r310;"),
    ("13:1x", "13:4x"),
    ("3e1ecb3110", "55eb0897ac"),
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

# ---- band ranges (explicit table, no ledger anchor touched)
BANDS = [
    ("692_701", "694_901"), ("692_900", "695_100"),
    ("692_901", "695_101"), ("693_100", "695_300"),
    ("694_700", "696_900"), ("694_900", "697_100"),
    ("694_901", "697_101"), ("695_100", "697_300"),
]
band_pat = re.compile("|".join(re.escape(k) for k, _ in BANDS))
band_tab = dict(BANDS)
s, n_band = band_pat.subn(lambda m: band_tab[m.group(0)], s)
print("band tokens bumped: %d" % n_band)

# ---- seat MSG date suffix (name already advanced by the lowercase bump)
old_msg = "20261024-1325-bmc-w309-seat"
new_msg = "20261024-1406-bmc-w309-seat"
if old_msg in s:
    print("seat MSG date suffix occurrences: %d" % s.count(old_msg))
    s = s.replace(old_msg, new_msg)

assert "NEW_W = 309" in s and "PREV_W = 308" in s and "PRIOR_W = 307" in s, "wave constants not bumped"
assert "results/_w309bmc_20261024_probe_receipt.json" in s
assert "research/PERPETUAL_N1_W309_PREREG.md" in s
assert "MSG-20261024-1406-bmc-w309-seat.md" in s
assert "55eb0897ac" in s
assert "W308" in s and "W309" in s and s.count("W309") > 10
assert "166 parity rows" not in s and "167 parity rows" in s
assert "692_901" not in s and "695_101" in s

io.open(OUT, "w", encoding="utf-8", newline="\n").write(s)
print("WROTE %s bytes=%d" % (OUT, len(s.encode("utf-8"))))