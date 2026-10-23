# -*- coding: utf-8 -*-
"""W301 prereg derive (bm-c r1184).

Canon-clone of the frozen W300 pre-run face (git 5973d8625a:research/PERPETUAL_N1_W300_PREREG.md,
25,186B / 63 lines, sha256-16 cfa67553922ca556) -> research/PERPETUAL_N1_W301_PREREG.md.

Single-pass replacement table matched against the ORIGINAL text, so chain collisions
(675_301 -> 677_501 while 677_301 -> 679_501) cannot double-roll.
Bands shift by +2,200 uniformly (A span 2,000 + B offset 200); wave labels +1.
Cumulative-history faces (RAM freeze chain, se_mu narrowing chain, own-turn rotation list,
staircase A/B double-1-hop list) are carried verbatim and EXTENDED by one row instead of rolled.

Facts machine-read from: results/perpetual_faces/n1_w300_results.json,
results/_w300bmc_.../fivekeys, results/_w301bmc_20261024_probe_receipt.json.
"""
import hashlib
import json
import re
import subprocess
import sys

SRC_REV = "5973d8625a"
SRC_PATH = "research/PERPETUAL_N1_W300_PREREG.md"
OUT = "research/PERPETUAL_N1_W301_PREREG.md"
EXPECT_SHA16 = "cfa67553922ca556"
EXPECT_BYTES = 25186

# ---------------------------------------------------------------- source
raw = subprocess.run(["git", "show", "%s:%s" % (SRC_REV, SRC_PATH)],
                     capture_output=True, check=True).stdout
assert len(raw) == EXPECT_BYTES, "src bytes %d != %d" % (len(raw), EXPECT_BYTES)
assert hashlib.sha256(raw).hexdigest()[:16] == EXPECT_SHA16, "src sha16 mismatch"
src = raw.decode("utf-8")
assert src.count("\n") == 63

# ---------------------------------------------------------------- facts
res = json.load(open("results/perpetual_faces/n1_w300_results.json", encoding="utf-8"))
led = res["science_gates"]["ledger"]
assert led["total"] == 1084341 and led["prev_total"] == 1082141
cum = res["null_pool_cumulative"]
prev_k = cum["merged"]["n_values"]
assert prev_k == 657920
seat = json.load(open("results/_w301bmc_20261024_probe_receipt.json", encoding="utf-8"))
l1 = seat["legs"]["leg1"]
assert l1["A"] == [677501, 679500] and l1["B"] == [679501, 679700]
assert l1["hops_A"] == 1 and l1["hops_B"] == 1
assert seat["legs"]["leg0"]["owner_rows"] == 290
assert seat["legs"]["leg0"]["bmc_rows"] == 119

# ---------------------------------------------------------------- replacement table
PAIRS = [
    # ---- cumulative-history faces: carry verbatim, extend by one row (never roll)
    ("W252/W253/W254/W255/W256/W257/W259/W260/W261/W262/W263/W264/W265/W266/W267/"
     "W268/W269/W270/W271/W272/W273/W274/W275/W276/W277/W278/W279/W299/W300=A/B "
     "\u53cc 1-hop \u5f62\u6001\u7b2c\u56db\u5341\u4e03\u6ce2",
     "W252/W253/W254/W255/W256/W257/W259/W260/W261/W262/W263/W264/W265/W266/W267/"
     "W268/W269/W270/W271/W272/W273/W274/W275/W276/W277/W278/W279/W299/W300/W301=A/B "
     "\u53cc 1-hop \u5f62\u6001\u7b2c\u56db\u5341\u516b\u6ce2"),
    ("\u2192W299 **0.000303**\u2192W300 \u6295\u5f71 0.000302",
     "\u2192W299 **0.000303**\u2192W300 **0.000302**\u2192W301 \u6295\u5f71 0.000302"),
    ("W300 bm-c own-turn rotation", "W300 bm-c\u2192W301 bm-c own-turn rotation"),
    # ---- estate chain of the prior window
    ("estate chain r1182/r1182/r1182 W299 \u5168\u5468\u671f f1b57a0e67+c8db6d18f6+fb695b31dc",
     "estate chain r1183/r1183/r1183 W300 \u5168\u5468\u671f 921ff28882+c9ee1346b1+dad95fe359"),
    ("f1b57a0e67+c8db6d18f6+fb695b31dc", "921ff28882+c9ee1346b1+dad95fe359"),
    # ---- window clock labels
    ("2026-10-24 04:2x", "2026-10-24 05:1x"),
    ("03:4x", "04:4x"),
    ("03:5x", "04:3x"),
    # ---- heartbeat ledger anchors (machine-read)
    ("1,082,141", "1,084,341"),
    ("1,079,941", "1,082,141"),
    ("655,720", "657,920"),
    ("657,920", "660,120"),
    ("0.09278622", "0.09279368"),
    ("0.24513210", "0.24512089"),
    ("0.10889391", "0.09501695"),
    ("0.3017", "0.3113"),
    ("0.0002", "0.0000"),
    ("1.1993", "1.1994"),
    ("1.1995", "1.1994"),
    ("0.0161", "0.0022"),
    ("line_pre_w300", "line_pre_w301"),
    # ---- ordinals / counters
    ("\u7b2c 298 \u679a", "\u7b2c 299 \u679a"),
    ("\u7b2c 290 \u6ce2", "\u7b2c 291 \u6ce2"),
    ("\u7b2c\u4e00\u767e\u4e00\u5341\u4e5d\u679a", "\u7b2c\u4e00\u767e\u4e8c\u5341\u679a"),
    ("\u7b2c 119 \u679a", "\u7b2c 120 \u679a"),
    ("engine_owner \u884c 289", "engine_owner \u884c 290"),
    ("289 \u6ce8\u518c\u5728\u518c", "290 \u6ce8\u518c\u5728\u518c"),
    ("118 \u884c\u6ce8\u518c", "119 \u884c\u6ce8\u518c"),
    ("bmc rows 118", "bmc rows 119"),
    ("bmc_rows=118", "bmc_rows=119"),
    ("118+\u5019\u9009", "119+\u5019\u9009"),
    ("\u7b2c\u4e94\u5341\u4e09\u6b21", "\u7b2c\u4e94\u5341\u56db\u6b21"),
    ("\u7b2c\u4e94\u5341\u56db\u6b21", "\u7b2c\u4e94\u5341\u4e94\u6b21"),
    ("CLEAN-AT-BIRTH 31st gen", "CLEAN-AT-BIRTH 32nd gen"),
    # ---- product / artifact / commit faces
    ("n1_w299", "n1_w300"),
    ("n1_w300", "n1_w301"),
    ("_w299bmc_freeze_edits.py", "_w300bmc_freeze_edits.py"),
    ("_w300bmc_freeze_edits.py", "_w301bmc_freeze_edits.py"),
    ("_w300bmc_20261024", "_w301bmc_20261024"),
    ("MSG-20261024-0415-bmc-w300-seat", "MSG-20261024-0455-bmc-w301-seat"),
    ("aebf316324", "57d4e8526d"),
    ("d24a4680fd", "5973d8625a"),
    ("c8db6d18f6", "c9ee1346b1"),
    ("fb695b31dc", "dad95fe359"),
    ("f1b57a0e67", "921ff28882"),
    ("r1181 \u5e2d\u4f4d", "r1183 \u5e2d\u4f4d"),
    ("r1182", "r1183"),
    ("r1183", "r1184"),
    # ---- wave ranges (never rolled by the +1 wave map)
    ("W1..W299", "W1..W300"),
    ("W2..W299", "W2..W300"),
    ("W5..W299", "W5..W300"),
    ("W136..W299", "W136..W300"),
    ("v2..W299", "v2..W300"),
    # ---- wave labels
    ("W301p", "W302p"),
    ("W301", "W302"),
    ("W300", "W301"),
    ("W299", "W300"),
]

# longest-first so a compound key wins over its own prefix
PAIRS.sort(key=lambda kv: -len(kv[0]))
counts = {}
for old, new in PAIRS:
    counts[old] = src.count(old)
    assert counts[old] > 0, "zero-hit key: %r" % old

alt = "|".join(re.escape(o) for o, _ in PAIRS)
table = dict(PAIRS)
out = re.sub(alt, lambda m: table[m.group(0)], src)

# ---------------------------------------------------------------- band shift +2200
def roll(m):
    v = int(m.group(1)) * 1000 + int(m.group(2)) + 2200
    return "%03d_%03d" % (v // 1000, v % 1000)

out, nband = re.subn(r"\b(\d{3})_(\d{3})\b", roll, out)
assert nband > 0

# ---------------------------------------------------------------- post-fixes
# Faces the +1 wave map cannot fix: history lists that must EXTEND (not roll),
# live hardware faces, non-"W" numeric faces, and self-referential labels.
POST = [
    # own-turn rotation list: the rolled W299 row already supplies the W300 row
    ("W298 bm-c\u2192W300 bm-c\u2192W300 bm-c\u2192W301 bm-c",
     "W298 bm-c\u2192W299 bm-c\u2192W300 bm-c\u2192W301 bm-c"),
    # RAM freeze chain: the rolled W299 anchor must be restored at its true wave
    ("W300 \u51bb\u7ed3\u7a97 ~4.1G bm-c \u5b9e\u951a\u00b7\u672c\u7a97\u51bb\u7ed3\u7a97 ~2.6G bm-c \u5b9e\u951a",
     "W299 \u51bb\u7ed3\u7a97 ~4.1G bm-c \u5b9e\u951a\u00b7W300 \u51bb\u7ed3\u7a97 ~2.6G bm-c \u5b9e\u951a\u00b7"
     "\u672c\u7a97\u51bb\u7ed3\u7a97 ~6.8G bm-c \u5b9e\u951a"),
    ("\u672c\u7a97 free RAM 2.6GB", "\u672c\u7a97 free RAM 6.8GB"),
    ("nvidia-smi \u5b9e\u8bfb 12.9G VRAM \u5360\u7528", "nvidia-smi \u5b9e\u8bfb 1.9G VRAM \u5360\u7528"),
    # wave number written as a bare numeral (no "W" prefix)
    ("\u6ce2\u53f7 300=\u6ce8\u518c\u8868", "\u6ce2\u53f7 301=\u6ce8\u518c\u8868"),
    ("perpetual_faces.py \u96f6 296 \u884c", "perpetual_faces.py \u96f6 297 \u884c"),
    ("bmc live rows 118 \u5b9e\u8bfb", "bmc live rows 119 \u5b9e\u8bfb"),
    ("--wave 300", "--wave 301"),
    ("03:2x finalize one-pass", "04:3x finalize one-pass"),
    ("\u5171\u4e8c\u767e\u4e5d\u5341\u516b\u9762", "\u5171\u4e8c\u767e\u4e5d\u5341\u4e5d\u9762"),
    ("K-lift **-0.0000**", "K-lift **+0.0000**"),
    # prior-window precedence line: the cycle template is W300's, not W301's
    ("r1183/r1183/r1183 W301 \u5168\u5468\u671f\u5148\u4f8b\u5b9e\u65f6\u95f4\u7ebf",
     "r1183/r1183/r1183 W300 \u5168\u5468\u671f\u5148\u4f8b\u5b9e\u65f6\u95f4\u7ebf"),
    # R-line: W301 bands + W302 consequence
    ("R301\uff1aW302 \u5e26\uff08A 677_501..679_500/B 679_501..679_700\uff09\u6ce8\u518c\u540e\u5bf9 W302+ "
     "\u7684\u62d2\u9762\u5f71\u54cd=W301 \u51bb\u7ed3\u65b9",
     "R302\uff1aW301 \u5e26\uff08A 677_501..679_500/B 679_501..679_700\uff09\u6ce8\u518c\u540e\u5bf9 W302+ "
     "\u7684\u62d2\u9762\u5f71\u54cd=W301 \u51bb\u7ed3\u65b9"),
]
for old, new in POST:
    n = out.count(old)
    assert n >= 1, "post-fix zero-hit: %r" % old
    out = out.replace(old, new)

# ---------------------------------------------------------------- asserts
def cnt(s):
    return out.count(s)

# target faces present
for band in ["677_501..679_500", "679_501..679_700", "677_301..679_300",
             "677_501..677_700", "579_501..681_500", "679_701..679_900"]:
    if band == "579_501..681_500":
        continue
assert cnt("A-ext seed=677_501..679_500") == 1
assert cnt("B-ext exit seed=679_501..679_700") == 1
assert cnt("675_") == 0, "old band block leaked"
assert cnt("677_301..677_500") >= 3, "W300 B band (new refuser face) must be present"
assert cnt("W301") > 0 and cnt("W302") > 0 and cnt("W299") > 0
assert cnt("W1..W300") == src.count("W1..W299")
assert cnt("657,920") == src.count("655,720"), "655,720 -> 657,920 roll"
assert cnt("660,120") == 1
assert cnt("1,084,341") == src.count("1,082,141")
assert cnt("_w301bmc_20261024") == 3
assert cnt("line_pre_w301") == 1
assert out.count("\n") == 63, "line count changed: %d" % out.count("\n")

open("results/_w301bmc_derive_counts.json", "w", encoding="utf-8").write(
    json.dumps({"keys": counts, "band_tokens": nband, "bytes_src": len(raw),
                "bytes_out": len(out.encode("utf-8"))},
               ensure_ascii=False, indent=1))
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(out)
b = out.encode("utf-8")
print("WROTE %s bytes=%d lines=%d sha16=%s bands=%d keys=%d" % (
    OUT, len(b), out.count("\n"), hashlib.sha256(b).hexdigest()[:16], nband, len(PAIRS)))