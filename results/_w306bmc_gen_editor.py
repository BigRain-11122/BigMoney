# -*- coding: utf-8 -*-
"""Build results/_w306bmc_freeze_edits.py from the proven W305 splice editor (bm-c r1191).

Mechanical canon-clone (r1168/r1170/r1171/r1182/r1184 pit family discipline):
  * ordinal words / seat ids / engine-wave words are parked behind pure-letter sentinels,
  * ledger + merged-pool anchors and r-labels are parked BEFORE the band roll,
  * wave digits 302..306 ride ONE single-pass map (+1), guarded against decimals/bands,
  * band tokens (\\d{3}_\\d{3}) roll +2200 in a separate single pass,
  * every replacement is counted and printed before writing (r1171 law).
"""
import io
import re
import sys

SRC = "results/_w305bmc_freeze_edits.py"
OUT = "results/_w306bmc_freeze_edits.py"
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
for k in ("FIFTY-EIGHTH", "FIFTY-NINTH", "THREE HUNDRED AND THIRD",
          "HUNDRED-AND-TWENTY-SECOND", "164 parity rows", "1_093_141",
          "666_720", "1,093,141", "666,720", "664,520", "w305bmc_20261024",
          "_w305bmc_freeze_receipt.json", "2026-10-24 08:5x", "r1189",
          "r1188", "r1187", "MSG-20261024-0845-bmc-w305-seat", "W306p"):
    print("PRE %-40r %d" % (k, t.count(k)))

# ---- 1. park cumulative / ordinal / seat faces
rep1("MSG-20261024-0845-bmc-w305-seat", "ZZSEATMSG", "seat-msg")
rep1("FIFTY-NINTH", "ZZORD60", "ord-60")
rep1("FIFTY-EIGHTH", "ZZORD59", "ord-59")
rep1("THREE HUNDRED AND THIRD", "ZZENGW", "engine-wave-word")
rep1("HUNDRED-AND-TWENTY-SECOND", "ZZOWNCLAIM", "own-claim-word")
rep1("164 parity rows", "ZZPARITY", "parity-count")

# ---- 2. park ledger / merged-pool anchors (they look like band tokens)
rep1("1_093_141", "ZZLEDGERU", "ledger-underline")
rep1("1,093,141", "ZZLEDGER", "ledger-comma")
rep1("666_720", "ZZMERGEDU", "merged-underline")
rep1("666,720", "ZZMERGED", "merged-comma")
rep1("664,520", "ZZSTALEK", "stale-k")

# ---- 3. park artifact stems (underscore glues the digits: no \\b boundary)
rep1("_w305bmc_freeze_receipt.json", "ZZRECEIPT", "receipt-out")
rep1("_w305bmc_", "ZZSTEMNEW", "stem-305")
rep1("_w304bmc_", "ZZSTEMOLD", "stem-304")
rep1("n1_w305", "ZZN1NEW", "n1-305")
rep1("n1_w304", "ZZN1OLD", "n1-304")
rep1("w305bmc_freeze_edits.py", "ZZEDITS", "edits-lineage")

# ---- 4. round labels (r1187 -> r1189 splice window pair; r1188 -> r1190; r1189 -> r1191)
rep1("r1189", "ZZR1191", "r1189")
rep1("r1188", "ZZR1190", "r1188")
rep1("r1187", "ZZR1189", "r1187")

# ---- 5. single-pass wave-digit map (302..306 -> +1), decimal/band guarded
def wmap(m):
    n = int(m.group(1))
    counts["wave-digit"] = counts.get("wave-digit", 0) + 1
    return str(n + 1)


t = re.sub(r"(?<![\d.])(30[2-6])(?![\d.])", wmap, t)

# ---- 6. band roll +2200 (single pass)
def bmap(m):
    v = int(m.group(1)) * 1000 + int(m.group(2)) + 2200
    counts["bands"] = counts.get("bands", 0) + 1
    return "%03d_%03d" % (v // 1000, v % 1000)


t = re.sub(r"\b(\d{3})_(\d{3})\b", bmap, t)

# ---- 7. window stamps
rep1("2026-10-24 08:5x", "2026-10-24 10:0x", "date-head")
rep1("08:5x", "10:0x", "hhmm")

# ---- 8. restore placeholders
t = t.replace("ZZSEATMSG", "MSG-20261024-0950-bmc-w306-seat")
t = t.replace("ZZORD59", "FIFTY-NINTH").replace("ZZORD60", "SIXTIETH")
t = t.replace("ZZENGW", "THREE HUNDRED AND FOURTH")
t = t.replace("ZZOWNCLAIM", "HUNDRED-AND-TWENTY-THIRD")
t = t.replace("ZZPARITY", "164 parity rows")
t = t.replace("ZZLEDGERU", "1_095_341").replace("ZZLEDGER", "1,095,341")
t = t.replace("ZZMERGEDU", "668_920").replace("ZZMERGED", "668,920")
t = t.replace("ZZSTALEK", "668,920")
t = t.replace("ZZRECEIPT", "_w306bmc_freeze_receipt.json")
t = t.replace("ZZSTEMNEW", "_w306bmc_").replace("ZZSTEMOLD", "_w305bmc_")
t = t.replace("ZZN1NEW", "n1_w306").replace("ZZN1OLD", "n1_w305")
t = t.replace("ZZEDITS", "w306bmc_freeze_edits.py")
t = t.replace("ZZR1191", "r1191").replace("ZZR1190", "r1190").replace("ZZR1189", "r1189")

# ---- 9. targeted post fixes
POST = [
    ('SEAT_ORIGIN = "871f187361"', 'SEAT_ORIGIN = "9da7091894"'),
    ('for _w in range(300, 292, -1):', 'for _w in range(301, 293, -1):'),
    ('expect 294/130/123', 'expect 295/130/124'),
    ('W248..W305 legs (55) added', 'W248..W305 legs (58) added'),
    ("the W305 block's own W248..W304 legs (54) are",
     "the W306 block's own W248..W305 legs (57) are"),
    ('f"W1..W305 finalize ALL LANDED', 'f"W1..W306 finalize ALL LANDED'),
    ('assert len(owner_rows_live) == 294', 'assert len(owner_rows_live) == 295'),
    ('len(bmc_rows_live) == 123', 'len(bmc_rows_live) == 124'),
]
for old, new in POST:
    n = t.count(old)
    print("post %-56r %d" % (old[:54], n))
    if n:
        t = t.replace(old, new)

print("COUNT TABLE:", {k: v for k, v in sorted(counts.items())})
if MEASURE:
    sys.exit(0)

print("LEAKS:", sorted(set(re.findall(r"ZZ[A-Z0-9_]+", t))))
assert "ZZ" not in t, "placeholder leaked"
assert "NEW_W = 306" in t and "PREV_W = 305" in t and "PRIOR_W = 304" in t
assert "688_501" in t and "690_500" in t and "690_501" in t and "690_700" in t
assert "686_301" not in t
assert "n1_w306_results.json" in t
assert "w306bmc_20261024" in t and "_w306bmc_freeze_receipt.json" in t
assert "9da7091894" in t
io.open(OUT, "w", encoding="utf-8", newline="\n").write(t)
print("WROTE", OUT, "bytes", len(t.encode("utf-8")))