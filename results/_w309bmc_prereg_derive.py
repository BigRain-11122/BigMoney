# -*- coding: utf-8 -*-
"""W309 prereg derive (bm-c r1196).

Canon-clone of the frozen W308 pre-run face
(git 2da27a4a3a:research/PERPETUAL_N1_W308_PREREG.md, 25,767B / 63 newlines,
sha16 bfbb621954050036) -> research/PERPETUAL_N1_W309_PREREG.md.

Cumulative-history chains (se_mu narrowing, A/B 1-hop wave list, own-turn
rotation list, RAM freeze chain) are parked behind pure-letter sentinels and
EXTENDED by one entry (never rolled) -- r1180/r1182/r1184 pit family.
Everything else rides ONE single-pass map: wave labels W>=301 +1, band tokens
+2200, ordinals +1, round labels +2, artifact names +1.

Usage: python results/_w309bmc_prereg_derive.py [--measure]
"""
import hashlib
import json
import re
import subprocess
import sys

SRC_REV = "2da27a4a3a"
SRC_PATH = "research/PERPETUAL_N1_W308_PREREG.md"
OUT = "research/PERPETUAL_N1_W309_PREREG.md"
EXPECT_SHA16 = "bfbb621954050036"
EXPECT_BYTES = 25767
SEAT_SHA = "55eb0897ac"
SEAT_MSG = "MSG-20261024-1406-bmc-w309-seat"
FREE_RAM = "2"
MEASURE = "--measure" in sys.argv

raw = subprocess.run(["git", "show", "%s:%s" % (SRC_REV, SRC_PATH)],
                     capture_output=True, check=True).stdout
assert len(raw) == EXPECT_BYTES, "src bytes %d != %d" % (len(raw), EXPECT_BYTES)
assert hashlib.sha256(raw).hexdigest()[:16] == EXPECT_SHA16, "src sha16 mismatch"
src = raw.decode("utf-8")
assert src.count("\n") == 63, "src line count %d" % src.count("\n")

# ---------------------------------------------------------------- facts (machine-read)
res = json.load(open("results/perpetual_faces/n1_w308_results.json", encoding="utf-8"))
led = res["science_gates"]["ledger"]
assert led["total"] == 1101941 and led["prev_total"] == 1099741, "ledger anchor drift"
cum = res["null_pool_cumulative"]
assert cum["merged"]["n_values"] == 675520, "merged K drift"
assert abs(cum["merged"]["mu"] + 0.09281744049028896) < 1e-12
assert abs(cum["merged"]["sigma"] - 0.24512184641505352) < 1e-12
assert cum["se_mu_at_k675520"] == 0.000298
assert abs(cum["w308_only"]["mu"] + 0.08883463636363637) < 1e-12
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_675520"] == 1.2001 and kl["line_pre_w308"] == 1.2001
assert kl["n_eff_held_equal"] == 1099741
assert (abs(res["families"]["A_random_engine_exit"]["full_sharpe_p95"] - 0.3234) < 1e-12
        and abs(res["families"]["A_random_engine_exit"]["full_sharpe_p99"] - 0.4468) < 1e-12)
seed = json.load(open("results/_w309bmc_20261024_probe_receipt.json", encoding="utf-8"))
assert seed["verdict"] == "ADMIT"
l1 = seed["legs"]["leg1"]
assert l1["A"] == [695101, 697100] and l1["B"] == [697101, 697300]
assert l1["hops_A"] == 1 and l1["hops_B"] == 1
assert seed["legs"]["leg0"]["owner_rows"] == 298
assert seed["legs"]["leg0"]["bmc_rows"] == 127
print("facts OK: ledger 1,101,941 / K 675,520 / W308-only mu -0.08883464 / p95 0.3234")

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
SHI_AN = "\u5b9e\u951a"        # 实锚


def se(old):
    idx = old.rfind("\u2192W308")   # →W308
    assert idx > 0, "se chain tail not found"
    tail = old[idx:]
    body = old[:idx]
    assert "0.000299" in tail
    return body + "\u2192W308 **0.000298**\u2192W309 " + PROJ + " 0.000298"


def ab(old):
    t = old.replace("/W308=A/B", "/W308/W309=A/B", 1)
    assert "/W308/W309=A/B" in t, "A/B chain tail not the expected /W308=A/B"
    o_ord = "\u7b2c\u4e94\u5341\u4e94\u6ce2"   # 55th wave
    n_ord = "\u7b2c\u4e94\u5341\u516d\u6ce2"   # 56th wave
    assert o_ord in t, "A/B chain ordinal not the expected 55th"
    t = t.replace(o_ord, n_ord)
    return t


def rot(old):
    t = old.replace("\u2192W308 bm-c own-turn rotation",
                    "\u2192W308 bm-c\u2192W309 bm-c own-turn rotation", 1)
    assert "W309 bm-c own-turn rotation" in t, "own-turn chain tail not the expected W308"
    return t


def ram(old):
    m = re.search(r"\u00b7W307 \u51bb\u7ed3\u7a97 ~1\.3G bm-c (\S+?)\u00b7\u672c\u7a97\u51bb\u7ed3\u7a97 ~0\.3G bm-c ", old)
    assert m, "RAM chain tail not found"
    word = m.group(1)
    new_tail = ("\u00b7W307 \u51bb\u7ed3\u7a97 ~1.3G bm-c " + word +
                "\u00b7W308 \u51bb\u7ed3\u7a97 ~0.3G bm-c " + word +
                "\u00b7\u672c\u7a97\u51bb\u7ed3\u7a97 ~" + FREE_RAM + "G bm-c " + word)
    return old[:m.start()] + new_tail + old[m.end():]


park(r"W277 \*\*0\.000314\*\*[^\n]*?\u6295\u5f71 0\.000299", se, "SECH")
park(r"W252/W253[^\n]*?\u7b2c\u4e94\u5341\u4e94\u6ce2", ab, "ABCHAIN")
park(r"W288 bm-c[\s\S]{0,900}?own-turn rotation", rot, "ROTCH")
park(r"W206/W211[^\n]*\u5b9e\u951a\uff09", ram, "RAMCH")

# ---------------------------------------------------------------- 2. wave labels +1 (W>=301)
out = wave_bump(out)

# ---------------------------------------------------------------- 3. numeric / ordinal / artifact maps
NUM = [
    ("1,097,541", "1,099,741"),
    ("1,099,741", "1,101,941"),
    ("673,320", "675,520"),
    ("675,520", "677,720"),
    ("0.3153", "0.3234"),
    ("0.24512009", "0.24512185"),
    ("\u22120.09284764", "\u22120.09281744"),
    ("\u22120.08758805", "\u22120.08883464"),
    ("0.0052", "0.0040"),
    ("1.2", "1.2001"),
    ("line_pre_w308", "line_pre_w309"),
    ("\u7b2c 306 \u679a", "\u7b2c 307 \u679a"),
    ("\u6ce2\u53f7 306=", "\u6ce2\u53f7 307="),
    ("\u884c 297 \u6ce8\u518c\u5728\u518c", "\u884c 298 \u6ce8\u518c\u5728\u518c"),
    ("bmc_rows=126", "bmc_rows=127"),
    ("bmc live rows 126", "bmc live rows 127"),
    ("\u7b2c 127 \u679a", "\u7b2c 128 \u679a"),
    ("\u7b2c\u4e00\u767e\u4e8c\u5341\u516d\u679a", "\u7b2c\u4e00\u767e\u4e8c\u5341\u4e03\u679a"),
    ("\u5f15\u64ce\u7ebf\u7b2c 298 \u6ce2", "\u5f15\u64ce\u7ebf\u7b2c 299 \u6ce2"),
    ("\u4e09\u767e\u96f6\u4e8c\u9762", "\u4e09\u767e\u96f6\u4e09\u9762"),
    ("CLEAN-AT-BIRTH 39th gen", "CLEAN-AT-BIRTH 40th gen"),
    ("--wave 308", "--wave 309"),
    ("n1_w307", "n1_w308"), ("n1_w308", "n1_w309"),
    ("_w307bmc_", "_w308bmc_"), ("_w308bmc_", "_w309bmc_"),
    ("MSG-20261024-1325-bmc-w308-seat", SEAT_MSG),
    ("3e1ecb3110", SEAT_SHA),
    ("897b31fc83", "054ba69f34"),
    ("2131c78e84", "2da27a4a3a"),
    ("5270a15dd8", "55c0dd2c83"),
    ("\u7b2c\u516d\u5341\u4e00\u6b21", "\u7b2c\u516d\u5341\u4e8c\u6b21"),
    ("\u7b2c\u516d\u5341\u4e8c\u6b21", "\u7b2c\u516d\u5341\u4e09\u6b21"),
    ("11:5x", "13:2x"),
    ("13:0x", "14:0x"),
    ("r1193", "r1195"), ("r1194", "r1196"),
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

# ---------------------------------------------------------------- 5. post-fixes
POST = [
    # header engine-row reference: this window's splice registers the W309 row
    ("\u8868\u5c3e W310 \u884c", "\u8868\u5c3e W309 \u884c"),
    ("W308 finalize \u5df2\u843d\u5730 10:3x", "W308 finalize \u5df2\u843d\u5730 13:4x"),
    ("bm-c r1195 W309 \u00a77 \u8303\u5f0f", "bm-c r1196 W309 \u00a77 \u8303\u5f0f"),
    ("bm-c r1195 W309 \u00a78 \u8303\u5f0f", "bm-c r1196 W309 \u00a78 \u8303\u5f0f"),
]
for old, new in POST:
    n = out.count(old)
    assert n == 1, "post-fix %r hits=%d" % (old, n)
    out = out.replace(old, new)
    print("post-fix applied hits=%d" % n)

# ---------------------------------------------------------------- 6. asserts
assert out.count("\n") == 63, "line count changed: %d" % out.count("\n")
for _old in ("692_901", "694_900", "695_100", "697_100"):
    for _m in re.finditer(re.escape(_old), out):
        print("DBG %s >>> %r" % (_old, out[max(0, _m.start() - 60):_m.end() + 30]))
assert out.count("692_901") == 0, "old A band leaked"
assert out.count("692_701") == 0, "old naive A base leaked"
assert out.count("694_900") >= 2, "new prior-wave A tail missing"
for band in ("695_101..697_100", "697_101..697_300"):
    assert out.count(band) >= 2, "target band missing: %s" % band
assert out.count("W309") > 30 and out.count("W310") > 5
assert out.count("W300") == src.count("W300"), "W300 (cumulative) must not roll"
assert out.count("1,101,941") == src.count("1,099,741")
assert out.count("675,520") == src.count("673,320"), "673,320 roll mismatch"
assert out.count("677,720") == src.count("675,520"), "675,520 roll mismatch"
assert out.count("line_pre_w309") >= 1 and out.count("line_pre_w308") == 0
assert out.count("ZZ") == 0, "sentinel leaked"
assert out.count("n1_w308") >= 4 and out.count("n1_w309") >= 1
assert out.count("n1_w307") == 0, "n1 double roll"
assert out.count(SEAT_SHA) >= 3
assert out.count(SEAT_MSG) >= 3
assert out.count("CLEAN-AT-BIRTH 40th gen") == 1
assert out.count("r1195") >= 3 and out.count("r1196") >= 1

receipt = {"keys": counts, "band_tokens": nband,
           "bytes_src": len(raw), "bytes_out": len(out.encode("utf-8"))}
open("results/_w309bmc_derive_counts.json", "w", encoding="utf-8").write(
    json.dumps(receipt, ensure_ascii=False, indent=1))
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(out)
b = out.encode("utf-8")
print("WROTE %s bytes=%d lines=%d sha16=%s bands=%d keys=%d" % (
    OUT, len(b), out.count("\n"), hashlib.sha256(b).hexdigest()[:16], nband, len(NUM)))