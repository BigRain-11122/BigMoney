# -*- coding: utf-8 -*-
"""W311 prereg derive (bm-c r1200).

Canon-clone of the frozen W310 pre-run face
(git 442e881af8:research/PERPETUAL_N1_W310_PREREG.md, 25,913B / 63 newlines,
sha16 98a587b54a1fc058) -> research/PERPETUAL_N1_W311_PREREG.md.

Cumulative-history chains (se_mu narrowing, A/B 1-hop wave list, own-turn
rotation list, RAM freeze chain) are parked behind pure-letter sentinels and
EXTENDED by one entry (never rolled) -- r1180/r1182/r1184 pit family.
Everything else rides ONE single-pass map: wave labels W>=301 +1, band tokens
+2200, ordinals +1, round labels +2, artifact names +1.

Usage: python results/_w311bmc_prereg_derive.py [--measure]
"""
import hashlib
import json
import re
import subprocess
import sys

SRC_REV = "442e881af8"
SRC_PATH = "research/PERPETUAL_N1_W310_PREREG.md"
OUT = "research/PERPETUAL_N1_W311_PREREG.md"
EXPECT_SHA16 = "98a587b54a1fc058"
EXPECT_BYTES = 25913
SEAT_SHA = "5cbfce8417"
SEAT_MSG = "MSG-20261024-1540-bmc-w311-seat"
FREE_RAM = "2.1"
MEASURE = "--measure" in sys.argv

raw = subprocess.run(["git", "show", "%s:%s" % (SRC_REV, SRC_PATH)],
                     capture_output=True, check=True).stdout
assert len(raw) == EXPECT_BYTES, "src bytes %d != %d" % (len(raw), EXPECT_BYTES)
assert hashlib.sha256(raw).hexdigest()[:16] == EXPECT_SHA16, "src sha16 mismatch"
src = raw.decode("utf-8")
assert src.count("\n") == 63, "src line count %d" % src.count("\n")

# ---------------------------------------------------------------- facts (machine-read)
res = json.load(open("results/perpetual_faces/n1_w310_results.json", encoding="utf-8"))
led = res["science_gates"]["ledger"]
assert led["total"] == 1106341 and led["prev_total"] == 1104141, "ledger anchor drift"
cum = res["null_pool_cumulative"]
assert cum["merged"]["n_values"] == 679920, "merged K drift"
assert abs(cum["merged"]["mu"] + 0.09279280400635369) < 1e-12
assert abs(cum["merged"]["sigma"] - 0.24514061686757777) < 1e-12
assert cum["se_mu_at_k679920"] == 0.000297
assert abs(cum["w310_only"]["mu"] + 0.08540904545454546) < 1e-12
assert abs(cum["w310_only"]["sigma"] - 0.24639091362038176) < 1e-12
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_679920"] == 1.2004 and kl["line_pre_w310"] == 1.2004
assert kl["line_delta_k_lift"] == 0.0
assert kl["n_eff_held_equal"] == 1104141
assert (abs(res["families"]["A_random_engine_exit"]["full_sharpe_p95"] - 0.302) < 1e-12
        and abs(res["families"]["A_random_engine_exit"]["full_sharpe_p99"] - 0.4525) < 1e-12)
seed = json.load(open("results/_w311bmc_20261024_probe_receipt.json", encoding="utf-8"))
assert seed["verdict"] == "ADMIT"
l1 = seed["legs"]["leg1"]
assert l1["A"] == [699501, 701500] and l1["B"] == [701501, 701700]
assert l1["hops_A"] == 1 and l1["hops_B"] == 1
assert seed["legs"]["leg0"]["owner_rows"] == 300
assert seed["legs"]["leg0"]["bmc_rows"] == 129
print("facts OK: ledger 1,106,341 / K 679,920 / W310-only mu -0.08540905 / p95 0.302")

# ---------------------------------------------------------------- 1. park cumulative history
out = src
stash = {}


def park(pattern, fn, label, expect=1):
    global out
    ms = list(re.finditer(pattern, out))
    assert len(ms) == expect, "%s: %d hits (expect %d)" % (label, len(ms), expect)
    olds = [m.group(0) for m in ms]
    news = [fn(o) for o in olds]
    for o, n in zip(olds, news):
        assert n != o, "%s: transform was a no-op" % label
    sent = "ZZ" + re.sub(r"[^A-Z]", "", label.upper())
    stash[sent] = news[0]
    for o in olds:
        out = out.replace(o, sent, 1)
    print("PARK %-10s hits=%d ascii_ok=%s" % (label, len(ms), olds[0].isascii()))
    return olds, news


def sub(text, pairs):
    """Single-pass token map (no cascades)."""
    keys = sorted(pairs, key=len, reverse=True)
    pat = re.compile("|".join(re.escape(k) for k in keys))
    return pat.sub(lambda m: pairs[m.group(0)], text)


def wave_bump(text, floor=301):
    return re.sub(r"W(\d{3})", lambda m: "W%03d" % (int(m.group(1)) + 1)
                  if int(m.group(1)) >= floor else m.group(0), text)


PROJ = "\u6295\u5f71"          # 投影


def se(old):
    idx = old.rfind("\u2192W310")   # →W310
    assert idx > 0, "se chain tail not found"
    tail = old[idx:]
    body = old[:idx]
    assert "0.000298" in tail
    return body + "\u2192W310 **0.000298**\u2192W311 " + PROJ + " 0.000297"


def ab(old):
    t = old.replace("/W310=A/B", "/W310/W311=A/B", 1)
    assert "/W310/W311=A/B" in t, "A/B chain tail not the expected /W310=A/B"
    o_ord = "\u7b2c\u4e94\u5341\u4e03\u6ce2"   # 57th wave
    n_ord = "\u7b2c\u4e94\u5341\u516b\u6ce2"   # 58th wave
    assert o_ord in t, "A/B chain ordinal not the expected 57th"
    t = t.replace(o_ord, n_ord)
    return t


def rot(old):
    t = old.replace("\u2192W310 bm-c own-turn rotation",
                    "\u2192W310 bm-c\u2192W311 bm-c own-turn rotation", 1)
    assert "W311 bm-c own-turn rotation" in t, "own-turn chain tail not expected W310"
    return t


def ram(old):
    m = re.search(r"\u00b7W309 \u51bb\u7ed3\u7a97 ~([\d.]+)G bm-c \u5b9e\u951a\u00b7\u672c\u7a97\u51bb\u7ed3\u7a97 ~([\d.]+)G bm-c \u5b9e\u951a\uff09", old)
    assert m, "RAM chain tail not found"
    word = "\u5b9e\u951a"   # 实锚
    new_tail = ("\u00b7W309 \u51bb\u7ed3\u7a97 ~" + m.group(1) + "G bm-c " + word +
                "\u00b7W310 \u51bb\u7ed3\u7a97 ~" + m.group(2) + "G bm-c " + word +
                "\u00b7\u672c\u7a97\u51bb\u7ed3\u7a97 ~" + FREE_RAM + "G bm-c " + word + "\uff09")
    return old[:m.start()] + new_tail + old[m.end():]


park(r"W277 \*\*0\.000314\*\*[^\n]*?\u6295\u5f71 0\.000298", se, "SECH")
park(r"W252/W253[^\n]*?\u7b2c\u4e94\u5341\u4e03\u6ce2", ab, "ABCHAIN")
park(r"W288 bm-c[\s\S]{0,900}?own-turn rotation", rot, "ROTCH")
park(r"W206/W211[^\n]*?\u5b9e\u951a\uff09", ram, "RAMCH")

# ---------------------------------------------------------------- 2. wave labels +1 (W>=301)
out = wave_bump(out)

# ---------------------------------------------------------------- 3. numeric / ordinal / artifact maps
NUM = [
    ("1,104,141", "1,106,341"),
    ("1,101,941", "1,104,141"),
    ("677,720", "679,920"),
    ("679,920", "682,120"),
    ("0.3384", "0.302"),
    ("0.24513637", "0.24514062"),
    ("\u22120.09281677", "\u22120.09279280"),
    ("\u22120.09261182", "\u22120.08540905"),
    ("0.0002", "0.0074"),
    ("+0.0001", "+0.0000"),
    ("1.2003", "1.2004"),
    ("line_pre_w310", "line_pre_w311"),
    ("\u7b2c 308 \u679a", "\u7b2c 309 \u679a"),
    ("\u6ce2\u53f7 308=", "\u6ce2\u53f7 309="),
    ("\u884c 299 \u6ce8\u518c\u5728\u518c", "\u884c 300 \u6ce8\u518c\u5728\u518c"),
    ("bmc rows 126+\u5019\u9009=\u7b2c 129 \u679a", "bmc rows 129+\u5019\u9009=\u7b2c 130 \u679a"),
    ("bmc_rows=128", "bmc_rows=129"),
    ("bmc live rows 128", "bmc live rows 129"),
    ("\u7b2c\u4e00\u767e\u4e8c\u5341\u516b\u679a", "\u7b2c\u4e00\u767e\u4e8c\u5341\u4e5d\u679a"),
    ("\u5f15\u64ce\u7ebf\u7b2c 300 \u6ce2", "\u5f15\u64ce\u7ebf\u7b2c 301 \u6ce2"),
    ("\u4e09\u767e\u96f6\u56db\u9762", "\u4e09\u767e\u96f6\u4e94\u9762"),
    ("CLEAN-AT-BIRTH 41st gen", "CLEAN-AT-BIRTH 42nd gen"),
    ("--wave 310", "--wave 311"),
    ("n1_w309", "n1_w310"), ("n1_w310", "n1_w311"),
    ("_w309bmc_", "_w310bmc_"), ("_w310bmc_", "_w311bmc_"),
    ("MSG-20261024-1500-bmc-w310-seat", SEAT_MSG),
    ("b109a52460", "442e881af8"),
    ("782bcad762", "d490186e9d"),
    ("bf1a8505a9", "5cbfce8417"),
    ("68a4a18b1f", SEAT_SHA),
    ("\u7b2c\u516d\u5341\u4e09\u6b21", "\u7b2c\u516d\u5341\u56db\u6b21"),
    ("\u7b2c\u516d\u5341\u56db\u6b21", "\u7b2c\u516d\u5341\u4e94\u6b21"),
    ("14:1x", "15:1x"),
    ("14:4x", "15:4x"),
    ("15:0x", "15:5x"),
]

counts = {}
for a, b in NUM:
    counts[a] = out.count(a)
print("COUNT TABLE (key -> occurrences):")
for a, _ in sorted(NUM, key=lambda kv: -len(kv[0])):
    print("  key=%s -> %d" % (a.encode("ascii", "backslashreplace").decode(), counts[a]))
zero = [a for a in counts if counts[a] == 0]
assert not zero, "zero-hit keys: %r" % zero
if MEASURE:
    print("MEASURE ok")
    for s, t in stash.items():
        print("STASH", s, "len", len(t))
    sys.exit(0)

out = sub(out, dict(NUM))

# ---------------------------------------------------------------- 4. bands +2200
def roll(m):
    v = int(m.group(1)) * 1000 + int(m.group(2)) + 2200
    return "%03d_%03d" % (v // 1000, v % 1000)


out, nband = re.subn(r"\b(\d{3})_(\d{3})\b", roll, out)
assert nband > 0

for sent, txt in stash.items():
    assert out.count(sent) == 1, "sentinel %s count %d" % (sent, out.count(sent))
    out = out.replace(sent, txt)

# ---------------------------------------------------------------- 5. round labels + post-fixes
# W309 window r1196/r1197 -> W310 window r1198/r1199; this window = r1200.
out = out.replace("r1196", "ZZRR1").replace("r1197", "ZZRR2").replace("r1198", "ZZRR3")
out = out.replace("ZZRR1", "r1198").replace("ZZRR2", "r1199").replace("ZZRR3", "r1200")

POST = [
    ("\u672c\u7a97 free RAM 0.3GB", "\u672c\u7a97 free RAM " + FREE_RAM + "GB"),
]
for old, new in POST:
    n = out.count(old)
    assert n >= 1, "post-fix %r hits=%d" % (old, n)
    out = out.replace(old, new)
    print("post-fix applied hits=%d" % n)

# ---------------------------------------------------------------- 6. asserts
assert out.count("\n") == 63, "line count changed: %d" % out.count("\n")
assert out.count("696_901") == 0, "old A band leaked"
assert out.count("696_700") == 0, "old naive A base leaked"
assert out.count("699_300") >= 2, "new prior-wave A tail missing"
for band in ("699_501..701_500", "701_501..701_700"):
    assert out.count(band) >= 2, "target band missing: %s" % band
assert out.count("W311") > 30 and out.count("W312") > 5
assert out.count("W300") == src.count("W300"), "W300 (cumulative) must not roll"
assert out.count("1,106,341") == src.count("1,104,141")
assert out.count("679,920") == src.count("677,720"), "677,720 roll mismatch"
assert out.count("line_pre_w311") >= 1 and out.count("line_pre_w310") == 0
assert out.count("ZZ") == 0, "sentinel leaked"
assert out.count("n1_w310") >= 4 and out.count("n1_w311") >= 1
assert out.count("n1_w309") == 0, "n1 double roll"
assert out.count(SEAT_SHA) >= 3
assert out.count(SEAT_MSG) >= 3
assert out.count("CLEAN-AT-BIRTH 42nd gen") == 1
assert out.count("r1199") >= 3 and out.count("r1200") >= 1

receipt = {"keys": counts, "band_tokens": nband,
           "bytes_src": len(raw), "bytes_out": len(out.encode("utf-8"))}
open("results/_w311bmc_derive_counts.json", "w", encoding="utf-8").write(
    json.dumps(receipt, ensure_ascii=False, indent=1))
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(out)
b = out.encode("utf-8")
print("WROTE %s bytes=%d lines=%d sha16=%s bands=%d keys=%d" % (
    OUT, len(b), out.count("\n"), hashlib.sha256(b).hexdigest()[:16], nband, len(NUM)))