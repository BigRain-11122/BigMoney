# -*- coding: utf-8 -*-
"""Build results/_w304bmc_freeze_edits.py from the proven W303 splice editor.

Mechanical canon-clone (r1168/r1170/r1171/r1182 pit family discipline):
  * cumulative / historical literals are not present in this script (it derives live),
  * wave digits 301..304 ride ONE single-pass map (+1), guarded against decimals and
    band tokens,
  * band tokens (\\d{3}_\\d{3}) are rolled +2200 in the same single pass family (separate regex),
  * English ordinals and seat identifiers are parked behind placeholders first.
Prints a count table before writing (r1171 law).
"""
import io
import re
import sys

SRC = "results/_w303bmc_freeze_edits.py"
OUT = "results/_w304bmc_freeze_edits.py"
MEASURE = "--measure" in sys.argv

t = io.open(SRC, encoding="utf-8").read()
print("src bytes", len(t.encode("utf-8")), "lines", t.count("\n"))

counts = {}


def rep1(old, new, label):
    global t
    n = t.count(old)
    counts[label] = n
    t = t.replace(old, new)
    return n


# ---- 1. park seat identifiers / ordinals that own digits
SEATP = "ZZSEATMSG"
rep1("MSG-20261024-0640-bmc-w303-seat", SEATP, "seat-msg")
rep1("MSG-20261024-0455-bmc-w301-seat", SEATP, "seat-msg-stale")
rep1("FIFTY-SIXTH", "ZZORD57", "ord-a")
rep1("FIFTY-SEVENTH", "ZZORD58", "ord-b")
rep1("THREE HUNDRED AND FIRST", "ZZENGW", "engine-wave-word")
rep1("HUNDRED-AND-TWENTIETH", "ZZOWNCLAIM", "own-claim-word")
rep1("161 parity rows", "ZZPARITY", "parity-count")

# ---- 2. round labels (r1185/r1186 -> +1)
rep1("r1186", "ZZR1187", "r1186")
rep1("r1185", "ZZR1186", "r1185")

# ---- 3. single-pass wave-digit map (301..304 -> +1), decimal/band guarded
def wmap(m):
    n = int(m.group(1))
    counts.setdefault("wave-digit", 0)
    counts["wave-digit"] += 1
    return str(n + 1)


t = re.sub(r"(?<![\d.])(30[1-4])(?![\d.])", wmap, t)

# ---- 4. band roll +2200 (single pass)
def bmap(m):
    v = int(m.group(1)) * 1000 + int(m.group(2)) + 2200
    counts.setdefault("bands", 0)
    counts["bands"] += 1
    return "%03d_%03d" % (v // 1000, v % 1000)


t = re.sub(r"\b(\d{3})_(\d{3})\b", bmap, t)

# ---- 5. compact underline numbers (1_088_741 / 662_320 forms)
for old, new in (("1_088_741", "1_090_941"), ("1_086_541", "1_088_741"),
                 ("662_320", "664_520"), ("660_120", "662_320"),
                 ("1,088,741", "1,090,941"), ("660,120", "662,320")):
    rep1(old, new, "num:" + old)

# ---- 6. window time stamps
rep1("2026-10-24 06:4x", "2026-10-24 07:3x", "date-head")
rep1("06:4x", "07:3x", "hhmm-1")
rep1("06:1x", "07:1x", "hhmm-2")

# ---- 7. restore placeholders
t = t.replace(SEATP, "MSG-20261024-0735-bmc-w304-seat")
t = t.replace("ZZORD57", "FIFTY-SEVENTH").replace("ZZORD58", "FIFTY-EIGHTH")
t = t.replace("ZZENGW", "THREE HUNDRED AND SECOND")
t = t.replace("ZZOWNCLAIM", "HUNDRED-AND-TWENTY-FIRST")
t = t.replace("ZZPARITY", "162 parity rows")
t = t.replace("ZZR1187", "r1187").replace("ZZR1186", "r1186")

# ---- 8. targeted post fixes
POST = [
    ('SEAT_MSG = "MSG-20261024-0735-bmc-w304-seat.md"',
     'SEAT_MSG = "MSG-20261024-0735-bmc-w304-seat.md"'),
    ('SEAT_ORIGIN = "f09ad33571"', 'SEAT_ORIGIN = "098930328c"'),
    ('for _w in range(298, 290, -1):', 'for _w in range(299, 291, -1):'),
    ('(expect 1,088,741 / 660,120)', '(expect 1,090,941 / 662,320)'),
    ('expect 292/130/121', 'expect 293/130/122'),
    ('assert len(owner_rows_live) == 292', 'assert len(owner_rows_live) == 293'),
    ('len(bmc_rows_live) == 121', 'len(bmc_rows_live) == 122'),
]
for old, new in POST:
    n = t.count(old)
    print("post %-52r %d" % (old[:50], n))
    if n:
        t = t.replace(old, new)

print("COUNT TABLE:", {k: v for k, v in sorted(counts.items())})
if MEASURE:
    sys.exit(0)

assert "ZZ" not in t, "placeholder leaked"
assert "681_" not in t and "683_901/j" not in t
assert "684_101" in t and "686_100" in t and "686_101" in t and "686_300" in t
assert "NEW_W = 304" in t and "PREV_W = 303" in t and "PRIOR_W = 302" in t
assert t.count("SEAT_ORIGIN") >= 2
assert "w302_out_path" in t and "w302_total" in t and "w303_receipt_sha" in t
assert "n1_w304_results.json" in t
assert "w304bmc_20261024" in t and "_w304bmc_freeze_receipt.json" in t
io.open(OUT, "w", encoding="utf-8", newline="\n").write(t)
print("WROTE", OUT, "bytes", len(t.encode("utf-8")))