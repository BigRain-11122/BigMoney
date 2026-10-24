# -*- coding: utf-8 -*-
"""Build results/_w307bmc_freeze_edits.py from the proven W306 splice editor (bm-c r1192).

Mechanical canon-clone (r1168/r1170/r1171/r1182/r1184 pit family discipline):
  * ordinal words / seat ids / engine-wave words are parked behind pure-letter sentinels,
  * ledger + merged-pool anchors and r-labels are parked BEFORE the band roll,
  * wave digits 303..307 ride ONE single-pass map (+1), guarded against decimals/bands,
  * band tokens (\\d{3}_\\d{3}) roll +2200 in a separate single pass,
  * every replacement is counted and printed before writing (r1171 law).
"""
import io
import re
import sys

SRC = "results/_w306bmc_freeze_edits.py"
OUT = "results/_w307bmc_freeze_edits.py"
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
for k in ("SIXTIETH", "FIFTY-NINTH", "THREE HUNDRED AND FOURTH",
          "HUNDRED-AND-TWENTY-THIRD", "164 parity rows", "1_095_341",
          "668_920", "1,095,341", "668,920", "666,720", "w306bmc_20261024",
          "_w306bmc_freeze_receipt.json", "2026-10-24 10:0x", "r1191",
          "r1190", "r1189", "MSG-20261024-0950-bmc-w306-seat", "W306p"):
    print("PRE %-40r %d" % (k, t.count(k)))

# ---- 1. park cumulative / ordinal / seat faces
rep1("MSG-20261024-0950-bmc-w306-seat", "ZZSEATMSG", "seat-msg")
rep1("SIXTIETH", "ZZORD61", "ord-61")
rep1("FIFTY-NINTH", "ZZORD60", "ord-60")
rep1("THREE HUNDRED AND FOURTH", "ZZENGW", "engine-wave-word")
rep1("HUNDRED-AND-TWENTY-THIRD", "ZZOWNCLAIM", "own-claim-word")
rep1("164 parity rows", "ZZPARITY", "parity-count")
rep1("W1..W306 finalize ALL LANDED", "ZZFIN", "fin-prose")

# ---- 2. park ledger / merged-pool anchors (they look like band tokens)
rep1("1_095_341", "ZZLEDGERU", "ledger-underline")
rep1("1,095,341", "ZZLEDGER", "ledger-comma")
rep1("668_920", "ZZMERGEDU", "merged-underline")
rep1("668,920", "ZZMERGED", "merged-comma")
rep1("666,720", "ZZSTALEK", "stale-k")

# ---- 3. park artifact stems (underscore glues the digits: no \b boundary)
rep1("_w306bmc_freeze_receipt.json", "ZZRECEIPT", "receipt-out")
rep1("_w306bmc_", "ZZSTEMNEW", "stem-306")
rep1("_w305bmc_", "ZZSTEMOLD", "stem-305")
rep1("n1_w306", "ZZN1NEW", "n1-306")
rep1("n1_w305", "ZZN1OLD", "n1-305")
rep1("w306bmc_freeze_edits.py", "ZZEDITS", "edits-lineage")

# ---- 4. round labels (this window's r1191 -> r1192; W306-era r1190/r1189 -> r1191)
rep1("r1191", "ZZRNEW", "r1191")
rep1("r1190", "ZZR1191", "r1190")
rep1("r1189", "ZZR1191B", "r1189")

# ---- 5. single-pass wave-digit map (303..307 -> +1), decimal/band guarded
def wmap(m):
    n = int(m.group(1))
    counts["wave-digit"] = counts.get("wave-digit", 0) + 1
    return str(n + 1)


t = re.sub(r"(?<![\d.])(30[3-7])(?![\d.])", wmap, t)

# ---- 6. band roll +2200 (single pass)
def bmap(m):
    v = int(m.group(1)) * 1000 + int(m.group(2)) + 2200
    counts["bands"] = counts.get("bands", 0) + 1
    return "%03d_%03d" % (v // 1000, v % 1000)


t = re.sub(r"\b(\d{3})_(\d{3})\b", bmap, t)

# ---- 7. window stamps
rep1("2026-10-24 10:0x", "2026-10-24 10:5x", "date-head")
rep1("10:0x", "10:5x", "hhmm")

# ---- 8. restore placeholders
t = t.replace("ZZSEATMSG", "MSG-20261024-1047-bmc-w307-seat")
t = t.replace("ZZORD60", "SIXTIETH").replace("ZZORD61", "SIXTY-FIRST")
t = t.replace("ZZENGW", "THREE HUNDRED AND FIFTH")
t = t.replace("ZZOWNCLAIM", "HUNDRED-AND-TWENTY-FOURTH")
t = t.replace("ZZPARITY", "165 parity rows")
t = t.replace("ZZFIN", "W1..W306 finalize ALL LANDED")
t = t.replace("ZZLEDGERU", "1_097_541").replace("ZZLEDGER", "1,097,541")
t = t.replace("ZZMERGEDU", "671_120").replace("ZZMERGED", "671,120")
t = t.replace("ZZSTALEK", "668,920")
t = t.replace("ZZRECEIPT", "_w307bmc_freeze_receipt.json")
t = t.replace("ZZSTEMNEW", "_w307bmc_").replace("ZZSTEMOLD", "_w306bmc_")
t = t.replace("ZZN1NEW", "n1_w307").replace("ZZN1OLD", "n1_w306")
t = t.replace("ZZEDITS", "w307bmc_freeze_edits.py")
t = t.replace("ZZRNEW", "r1192").replace("ZZR1191B", "r1191").replace("ZZR1191", "r1191")

# ---- 9. targeted post fixes
POST = [
    ('SEAT_ORIGIN = "9da7091894"', 'SEAT_ORIGIN = "d78f799608"'),
    ('for _w in range(301, 293, -1):', 'for _w in range(302, 294, -1):'),
    ('assert len(owner_rows_live) == 295', 'assert len(owner_rows_live) == 296'),
    ('len(bmc_rows_live) == 124', 'len(bmc_rows_live) == 125'),
    ('expect 295/130/124', 'expect 296/130/125'),
    ("the W307 block's own W248..W306 legs (57) are",
     "the W307 block's own W248..W306 legs (58) are"),
    ('W248..W306 legs (58) added', 'W248..W306 legs (59) added'),
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
assert "NEW_W = 307" in t and "PREV_W = 306" in t and "PRIOR_W = 305" in t
assert "690_701" in t and "692_700" in t and "692_701" in t and "692_900" in t
assert "688_501" not in t, "old band block leaked"
assert "n1_w307_results.json" in t
assert "w307bmc_20261024" in t and "_w307bmc_freeze_receipt.json" in t
assert "d78f799608" in t
assert "1_097_541" in t and "671_120" in t
io.open(OUT, "w", encoding="utf-8", newline="\n").write(t)
print("WROTE", OUT, "bytes", len(t.encode("utf-8")))