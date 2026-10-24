# -*- coding: utf-8 -*-
"""W310 prereg derive (bm-c r1198).

Canon-clone of the frozen W309 pre-run face
(git b109a52460:research/PERPETUAL_N1_W309_PREREG.md, 25,848B / 63 newlines,
sha16 fbba5b7d8166c35c) -> research/PERPETUAL_N1_W310_PREREG.md.

Cumulative-history chains (se_mu narrowing, A/B 1-hop wave list, own-turn
rotation list, RAM freeze chain) are parked behind pure-letter sentinels and
EXTENDED by one entry (never rolled) -- r1180/r1182/r1184 pit family.
Everything else rides ONE single-pass map: wave labels W>=301 +1, band tokens
+2200, ordinals +1, round labels +2, artifact names +1.

Usage: python results/_w310bmc_prereg_derive.py [--measure]
"""
import hashlib
import json
import re
import subprocess
import sys

SRC_REV = "b109a52460"
SRC_PATH = "research/PERPETUAL_N1_W309_PREREG.md"
OUT = "research/PERPETUAL_N1_W310_PREREG.md"
EXPECT_SHA16 = "fbba5b7d8166c35c"
EXPECT_BYTES = 25848
SEAT_SHA = "68a4a18b1f"
SEAT_MSG = "MSG-20261024-1500-bmc-w310-seat"
FREE_RAM = "6.4"
MEASURE = "--measure" in sys.argv

raw = subprocess.run(["git", "show", "%s:%s" % (SRC_REV, SRC_PATH)],
                     capture_output=True, check=True).stdout
assert len(raw) == EXPECT_BYTES, "src bytes %d != %d" % (len(raw), EXPECT_BYTES)
assert hashlib.sha256(raw).hexdigest()[:16] == EXPECT_SHA16, "src sha16 mismatch"
src = raw.decode("utf-8")
assert src.count("\n") == 63, "src line count %d" % src.count("\n")

# ---------------------------------------------------------------- facts (machine-read)
res = json.load(open("results/perpetual_faces/n1_w309_results.json", encoding="utf-8"))
led = res["science_gates"]["ledger"]
assert led["total"] == 1104141 and led["prev_total"] == 1101941, "ledger anchor drift"
cum = res["null_pool_cumulative"]
assert cum["merged"]["n_values"] == 677720, "merged K drift"
assert abs(cum["merged"]["mu"] + 0.0928167730036003) < 1e-12
assert abs(cum["merged"]["sigma"] - 0.24513636834341376) < 1e-12
assert cum["se_mu_at_k677720"] == 0.000298
assert abs(cum["w309_only"]["mu"] + 0.09261181818181818) < 1e-12
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_677720"] == 1.2003 and kl["line_pre_w309"] == 1.2002
assert kl["line_delta_k_lift"] == 0.0001
assert kl["n_eff_held_equal"] == 1101941
assert (abs(res["families"]["A_random_engine_exit"]["full_sharpe_p95"] - 0.3384) < 1e-12
        and abs(res["families"]["A_random_engine_exit"]["full_sharpe_p99"] - 0.4805) < 1e-12)
seed = json.load(open("results/_w310bmc_20261024_probe_receipt.json", encoding="utf-8"))
assert seed["verdict"] == "ADMIT"
l1 = seed["legs"]["leg1"]
assert l1["A"] == [697301, 699300] and l1["B"] == [699301, 699500]
assert l1["hops_A"] == 1 and l1["hops_B"] == 1
assert seed["legs"]["leg0"]["owner_rows"] == 299
assert seed["legs"]["leg0"]["bmc_rows"] == 128
print("facts OK: ledger 1,104,141 / K 677,720 / W309-only mu -0.09261182 / p95 0.3384")

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
    idx = old.rfind("\u2192W309")   # →W309
    assert idx > 0, "se chain tail not found"
    tail = old[idx:]
    body = old[:idx]
    assert "0.000298" in tail
    return body + "\u2192W309 **0.000298**\u2192W310 " + PROJ + " 0.000298"


def ab(old):
    t = old.replace("/W309=A/B", "/W309/W310=A/B", 1)
    assert "/W309/W310=A/B" in t, "A/B chain tail not the expected /W309=A/B"
    o_ord = "\u7b2c\u4e94\u5341\u516d\u6ce2"   # 56th wave
    n_ord = "\u7b2c\u4e94\u5341\u4e03\u6ce2"   # 57th wave
    assert o_ord in t, "A/B chain ordinal not the expected 56th"
    t = t.replace(o_ord, n_ord)
    return t


def rot(old):
    t = old.replace("\u2192W309 bm-c own-turn rotation",
                    "\u2192W309 bm-c\u2192W310 bm-c own-turn rotation", 1)
    assert "W310 bm-c own-turn rotation" in t, "own-turn chain tail not the expected W309"
    return t


def ram(old):
    m = re.search(r"\u00b7W308 \u51bb\u7ed3\u7a97 ~0\.3G bm-c \u5b9e\u951a\u00b7\u672c\u7a97\u51bb\u7ed3\u7a97 ~([\d.]+)G bm-c \u5b9e\u951a\u5b9e\u951a\uff09", old)
    assert m, "RAM chain tail not found"
    word = "\u5b9e\u951a"   # 实锚
    new_tail = ("\u00b7W308 \u51bb\u7ed3\u7a97 ~0.3G bm-c " + word +
                "\u00b7W309 \u51bb\u7ed3\u7a97 ~" + m.group(1) + "G bm-c " + word +
                "\u00b7\u672c\u7a97\u51bb\u7ed3\u7a97 ~" + FREE_RAM + "G bm-c " + word + "\uff09")
    return old[:m.start()] + new_tail + old[m.end():]


park(r"W277 \*\*0\.000314\*\*[^\n]*?\u6295\u5f71 0\.000298", se, "SECH")
park(r"W252/W253[^\n]*?\u7b2c\u4e94\u5341\u516d\u6ce2", ab, "ABCHAIN")
park(r"W288 bm-c[\s\S]{0,900}?own-turn rotation", rot, "ROTCH")
park(r"W206/W211[^\n]*?\u5b9e\u951a\uff09", ram, "RAMCH")

# ---------------------------------------------------------------- 2. wave labels +1 (W>=301)
out = wave_bump(out)

# ---------------------------------------------------------------- 3. numeric / ordinal / artifact maps
NUM = [
    ("1,101,941", "1,104,141"),
    ("1,099,741", "1,101,941"),
    ("675,520", "677,720"),
    ("677,720", "679,920"),
    ("0.3234", "0.3384"),
    ("0.24512185", "0.24513637"),
    ("\u22120.09281744", "\u22120.09281677"),
    ("\u22120.08883464", "\u22120.09261182"),
    ("0.0040", "0.0002"),
    ("+0.0000", "+0.0001"),
    ("1.2001", "1.2003"),
    ("line_pre_w309", "line_pre_w310"),
    ("\u7b2c 307 \u679a", "\u7b2c 308 \u679a"),
    ("\u6ce2\u53f7 307=", "\u6ce2\u53f7 308="),
    ("\u884c 298 \u6ce8\u518c\u5728\u518c", "\u884c 299 \u6ce8\u518c\u5728\u518c"),
    ("bmc_rows=127", "bmc_rows=128"),
    ("bmc live rows 127", "bmc live rows 128"),
    ("\u7b2c 128 \u679a", "\u7b2c 129 \u679a"),
    ("\u7b2c\u4e00\u767e\u4e8c\u5341\u4e03\u679a", "\u7b2c\u4e00\u767e\u4e8c\u5341\u516b\u679a"),
    ("\u5f15\u64ce\u7ebf\u7b2c 299 \u6ce2", "\u5f15\u64ce\u7ebf\u7b2c 300 \u6ce2"),
    ("\u4e09\u767e\u96f6\u4e09\u9762", "\u4e09\u767e\u96f6\u56db\u9762"),
    ("CLEAN-AT-BIRTH 40th gen", "CLEAN-AT-BIRTH 41st gen"),
    ("--wave 309", "--wave 310"),
    ("n1_w308", "n1_w309"), ("n1_w309", "n1_w310"),
    ("_w308bmc_", "_w309bmc_"), ("_w309bmc_", "_w310bmc_"),
    ("MSG-20261024-1406-bmc-w309-seat", SEAT_MSG),
    ("2da27a4a3a", "b109a52460"),
    ("054ba69f34", "782bcad762"),
    ("55c0dd2c83", "bf1a8505a9"),
    ("55eb0897ac", SEAT_SHA),
    ("\u7b2c\u516d\u5341\u4e8c\u6b21", "\u7b2c\u516d\u5341\u4e09\u6b21"),
    ("\u7b2c\u516d\u5341\u4e09\u6b21", "\u7b2c\u516d\u5341\u56db\u6b21"),
    ("13:2x", "14:1x"),
    ("14:0x", "15:0x"),
    ("13:4x", "14:4x"),
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
# Round labels ride sentinels so the two windows can be addressed separately:
# r1195 = prior-wave (W308) splice/freeze window -> W309's own window r1196;
# r1196 = the freeze window of the source wave -> this window r1198.
out = out.replace("r1195", "ZZRRP").replace("r1196", "ZZRRC")
out = out.replace("ZZRRP", "r1196").replace("ZZRRC", "r1198")

POST = [
    # W309 finalize window is r1197 at 14:4x; its whole cycle is r1196/r1196/r1197
    ("finalize one-pass bm-c r1196 \u7a97 14:1x\u00b7estate chain r1196/r1196/r1196",
     "finalize one-pass bm-c r1197 \u7a97 14:4x\u00b7estate chain r1196/r1196/r1197"),
    ("finalize one-pass bm-c r1196 \u7a97 14:1x\u3011\u3011",
     "finalize one-pass bm-c r1197 \u7a97 14:4x\u3011\u3011"),
    ("\uff08r1196/r1196/r1196 W309 \u5168\u5468\u671f",
     "\uff08r1196/r1196/r1197 W309 \u5168\u5468\u671f"),
]
for old, new in POST:
    n = out.count(old)
    assert n >= 1, "post-fix %r hits=%d" % (old, n)
    out = out.replace(old, new)
    print("post-fix applied hits=%d" % n)

# ---------------------------------------------------------------- 6. asserts
assert out.count("\n") == 63, "line count changed: %d" % out.count("\n")
assert out.count("694_901") == 0, "old A band leaked"
assert out.count("694_700") == 0, "old naive A base leaked"
assert out.count("697_100") >= 2, "new prior-wave A tail missing"
for band in ("697_301..699_300", "699_301..699_500"):
    assert out.count(band) >= 2, "target band missing: %s" % band
assert out.count("W310") > 30 and out.count("W311") > 5
assert out.count("W300") == src.count("W300"), "W300 (cumulative) must not roll"
assert out.count("1,104,141") == src.count("1,101,941")
assert out.count("677,720") == src.count("675,520"), "675,520 roll mismatch"
assert out.count("line_pre_w310") >= 1 and out.count("line_pre_w309") == 0
assert out.count("ZZ") == 0, "sentinel leaked"
assert out.count("n1_w309") >= 4 and out.count("n1_w310") >= 1
assert out.count("n1_w308") == 0, "n1 double roll"
assert out.count(SEAT_SHA) >= 3
assert out.count(SEAT_MSG) >= 3
assert out.count("CLEAN-AT-BIRTH 41st gen") == 1
assert out.count("r1197") >= 3 and out.count("r1198") >= 1

receipt = {"keys": counts, "band_tokens": nband,
           "bytes_src": len(raw), "bytes_out": len(out.encode("utf-8"))}
open("results/_w310bmc_derive_counts.json", "w", encoding="utf-8").write(
    json.dumps(receipt, ensure_ascii=False, indent=1))
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(out)
b = out.encode("utf-8")
print("WROTE %s bytes=%d lines=%d sha16=%s bands=%d keys=%d" % (
    OUT, len(b), out.count("\n"), hashlib.sha256(b).hexdigest()[:16], nband, len(NUM)))