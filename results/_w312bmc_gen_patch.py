# -*- coding: utf-8 -*-
"""Generate results/_w312bmc_freeze_edits.py from the proven W311 splice editor.

One-wave bump: literal anchors/keys FIRST (matched against the original text), then
lowercase wave identifiers, then uppercase wave labels, then band ranges. Single pass
each with a printed count table (r1171 law) and hard asserts (no silent no-ops).

Usage: python results/_w312bmc_gen_patch.py [--measure]
"""
import io
import re
import sys

SRC = "results/_w311bmc_freeze_edits.py"
OUT = "results/_w312bmc_freeze_edits.py"
MEASURE = "--measure" in sys.argv

s = io.open(SRC, encoding="utf-8").read()

NUM = [
    # ---- ordinals (single pass, longest first)
    ("SIXTY-FIFTH", "SIXTY-SIXTH"),
    ("SIXTY-FOURTH", "SIXTY-FIFTH"),
    ("HUNDRED-AND-TWENTY-EIGHTH", "HUNDRED-AND-TWENTY-NINTH"),
    ("THREE HUNDRED AND NINTH", "THREE HUNDRED AND TENTH"),
    # ---- wave constants
    ("NEW_W = 311", "NEW_W = 312"),
    ("PREV_W = 310", "PREV_W = 311"),
    ("PRIOR_W = 309", "PRIOR_W = 310"),
    ("w<310>", "w<311>"), ("w<309>", "w<310>"),
    ("len(owner_rows_live) == 300 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 129",
     "len(owner_rows_live) == 301 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 130"),
    ("(expect 300/130/129)", "(expect 301/130/130)"),
    ("wave 311: ", "wave 312: "),
    ('311: {"batch"', '312: {"batch"'),
    ('311: {{"batch"', '312: {{"batch"'),
    ('311: {{"a"', '312: {{"a"'),
    ("range(306, 298, -1)", "range(307, 299, -1)"),
    # ---- ledger / pool anchors
    ("1_106_341", "1_108_541"),
    ("1,106,341", "1,108,541"),
    ("679,920", "682,120"),
    ("679_920", "682_120"),
    # ---- parity row / leg counts
    ("169 parity rows", "170 parity rows"),
    ("legs (63)", "legs (64)"),
    ("legs (62)", "legs (63)"),
    # ---- seat sha / window stamp
    ("15:1x", "17:0x"),
    ("5cbfce8417", "831cbe0a27"),
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

# ---- underscore ledger anchors would be eaten by the band roll (3-digit_3-digit shape):
# park them first (r1168 double-shift family), restore after the band pass.
UNDERSCORE = {"ZZNUM1": "1_108_541", "ZZNUM2": "682_120"}
for _old, _sent in (("1_108_541", "ZZNUM1"), ("682_120", "ZZNUM2")):
    assert s.count(_old) == 1, "underscore anchor %s count %d" % (_old, s.count(_old))
    s = s.replace(_old, _sent)

# ---- round labels (+2 windows) via sentinels (no pairwise cascade)
s = s.replace("r1198", "ZZRR1").replace("r1200", "ZZRR2")
s = s.replace("ZZRR1", "r1200").replace("ZZRR2", "r1202")
print("round labels: r1200=%d r1202=%d" % (s.count("r1200"), s.count("r1202")))

# ---- lowercase wave identifiers (also n1_wNNN and _wNNNbmc_)
s, n_lc = re.subn(r"w(\d{3})", lambda m: "w%03d" % (int(m.group(1)) + 1)
                  if int(m.group(1)) >= 301 else m.group(0), s)
print("lowercase wave tokens bumped: %d" % n_lc)

# ---- uppercase wave labels W>=301
s, n_uc = re.subn(r"W(\d{3})", lambda m: "W%03d" % (int(m.group(1)) + 1)
                  if int(m.group(1)) >= 301 else m.group(0), s)
print("uppercase wave tokens bumped: %d" % n_uc)

# ---- band ranges (generic +2200; arithmetic identity per W311 -> W312 seat)
s, n_band = re.subn(
    r"\b(\d{3})_(\d{3})\b",
    lambda m: "%03d_%03d" % ((int(m.group(1)) * 1000 + int(m.group(2)) + 2200) // 1000,
                             (int(m.group(1)) * 1000 + int(m.group(2)) + 2200) % 1000),
    s)
print("band tokens bumped: %d" % n_band)

for _sent, _val in UNDERSCORE.items():
    assert s.count(_sent) == 1, "sentinel %s count %d" % (_sent, s.count(_sent))
    s = s.replace(_sent, _val)

# ---- seat MSG date suffix (name already advanced by the lowercase bump)
old_msg = "20261024-1540-bmc-w312-seat"
new_msg = "20261024-1639-bmc-w312-seat"
if old_msg in s:
    print("seat MSG date suffix occurrences: %d" % s.count(old_msg))
    s = s.replace(old_msg, new_msg)

assert "NEW_W = 312" in s and "PREV_W = 311" in s and "PRIOR_W = 310" in s, "wave constants not bumped"
assert "results/_w312bmc_20261024_probe_receipt.json" in s
assert "research/PERPETUAL_N1_W312_PREREG.md" in s
assert "MSG-20261024-1639-bmc-w312-seat.md" in s
assert "831cbe0a27" in s
assert "W311" in s and "W312" in s and s.count("W312") > 10
assert "169 parity rows" not in s and "170 parity rows" in s
assert "699_501" not in s and "701_701" in s
assert "1_106_341" not in s and "1_108_541" in s
assert "679_920" not in s and "682_120" in s

io.open(OUT, "w", encoding="utf-8", newline="\n").write(s)
print("WROTE %s bytes=%d" % (OUT, len(s.encode("utf-8"))))