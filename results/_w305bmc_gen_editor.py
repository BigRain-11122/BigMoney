# -*- coding: utf-8 -*-
"""Build results/_w305bmc_freeze_edits.py from the proven W304 splice editor (bm-c r1189).

Mechanical canon-clone (r1168/r1170/r1171/r1182 pit family discipline):
  * ordinal words / seat ids / engine-wave words are parked behind pure-letter sentinels,
  * ledger + merged-pool anchors are parked BEFORE the band roll (they are 3-digit pairs too),
  * wave digits 301..304 ride ONE single-pass map (+1), guarded against decimals and bands,
  * band tokens (\\d{3}_\\d{3}) roll +2200 in a separate single pass,
  * every replacement is counted and printed before writing (r1171 law).
"""
import io
import re
import sys

SRC = "results/_w304bmc_freeze_edits.py"
OUT = "results/_w305bmc_freeze_edits.py"
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


# ---- 0. AS-IS count probe
for k in ("FIFTY-EIGHTH", "FIFTY-SEVENTH", "THREE HUNDRED AND SECOND",
          "HUNDRED-AND-TWENTY-FIRST", "162 parity rows", "1_090_941",
          "664_520", "1,090,941", "662,320", "w304bmc_20261024",
          "_w304bmc_freeze_receipt.json", "2026-10-24 07:3x", "07:3x",
          "r1187", "r1186", "MSG-20261024-0735-bmc-w304-seat"):
    print("PRE %-40r %d" % (k, t.count(k)))

# ---- 1. park cumulative / ordinal / seat faces
rep1("MSG-20261024-0735-bmc-w304-seat", "ZZSEATMSG", "seat-msg")
rep1("FIFTY-EIGHTH", "ZZORD59", "ord-59")
rep1("FIFTY-SEVENTH", "ZZORD58", "ord-58")
rep1("THREE HUNDRED AND SECOND", "ZZENGW", "engine-wave-word")
rep1("HUNDRED-AND-TWENTY-FIRST", "ZZOWNCLAIM", "own-claim-word")
rep1("162 parity rows", "ZZPARITY", "parity-count")

# ---- 2. park ledger / merged-pool anchors (they look like band tokens)
rep1("1_090_941", "ZZLEDGERU", "ledger-underline")
rep1("1,090,941", "ZZLEDGER", "ledger-comma")
rep1("664_520", "ZZMERGEDU", "merged-underline")
rep1("662,320", "ZZMERGED", "merged-comma")

# ---- 3. round labels (r1187 -> r1189 splice window; r1186 -> r1187 lineage)
rep1("r1187", "ZZR1189", "r1187")
rep1("r1186", "ZZR1187", "r1186")

# ---- 4. single-pass wave-digit map (301..304 -> +1), decimal/band guarded
def wmap(m):
    n = int(m.group(1))
    counts["wave-digit"] = counts.get("wave-digit", 0) + 1
    return str(n + 1)


t = re.sub(r"(?<![\d.])(30[1-5])(?![\d.])", wmap, t)

# ---- 5. band roll +2200 (single pass)
def bmap(m):
    v = int(m.group(1)) * 1000 + int(m.group(2)) + 2200
    counts["bands"] = counts.get("bands", 0) + 1
    return "%03d_%03d" % (v // 1000, v % 1000)


t = re.sub(r"\b(\d{3})_(\d{3})\b", bmap, t)

# ---- 6. window stamps
rep1("2026-10-24 07:3x", "2026-10-24 08:5x", "date-head")
rep1("07:3x", "08:5x", "hhmm")

# ---- 7. restore placeholders
t = t.replace("ZZSEATMSG", "MSG-20261024-0845-bmc-w305-seat")
t = t.replace("ZZORD58", "FIFTY-EIGHTH").replace("ZZORD59", "FIFTY-NINTH")
t = t.replace("ZZENGW", "THREE HUNDRED AND THIRD")
t = t.replace("ZZOWNCLAIM", "HUNDRED-AND-TWENTY-SECOND")
t = t.replace("ZZPARITY", "164 parity rows")
t = t.replace("ZZLEDGERU", "1_093_141").replace("ZZLEDGER", "1,093,141")
t = t.replace("ZZMERGEDU", "666_720").replace("ZZMERGED", "666,720")
t = t.replace("ZZR1189", "r1189").replace("ZZR1187", "r1187")

# ---- 8. targeted post fixes
POST = [
    ('SEAT_ORIGIN = "098930328c"', 'SEAT_ORIGIN = "871f187361"'),
    ('for _w in range(299, 291, -1):', 'for _w in range(300, 292, -1):'),
    ('expect 1,090,941 / 662,320', 'expect 1,093,141 / 666,720'),
    ('expect 293/130/122', 'expect 294/130/123'),
    ('assert len(owner_rows_live) == 293', 'assert len(owner_rows_live) == 294'),
    ('len(bmc_rows_live) == 122', 'len(bmc_rows_live) == 123'),
    ('ledger 1,093,141 / K=666,720 machine-read',
     'ledger 1,093,141 / K=664,520 machine-read'),
]
for old, new in POST:
    n = t.count(old)
    print("post %-56r %d" % (old[:54], n))
    if n:
        t = t.replace(old, new)

print("COUNT TABLE:", {k: v for k, v in sorted(counts.items())})
if MEASURE:
    sys.exit(0)

assert "ZZ" not in t, "placeholder leaked"
assert "NEW_W = 305" in t and "PREV_W = 304" in t and "PRIOR_W = 303" in t
assert "686_301" in t and "688_300" in t and "688_301" in t and "688_500" in t
assert "684_101" not in t
assert "w303_out_path" in t and "w304_receipt_sha" in t
assert "n1_w305_results.json" in t
assert "w305bmc_20261024" in t and "_w305bmc_freeze_receipt.json" in t
assert "871f187361" in t
io.open(OUT, "w", encoding="utf-8", newline="\n").write(t)
print("WROTE", OUT, "bytes", len(t.encode("utf-8")))