# -*- coding: utf-8 -*-
"""W314 prereg derive (bm-c r1207).

Canon-clone of the W313 PRE-FINALIZE face
(git c110bf216e:research/PERPETUAL_N1_W313_PREREG.md, 28,291B / 75 newlines,
sha16 5c33696ff717fee3) -> research/PERPETUAL_N1_W314_PREREG.md.

Cumulative-history chains (se_mu narrowing, A/B 1-hop wave list, own-turn
rotation list, RAM freeze chain) are parked behind pure-letter sentinels and
EXTENDED by one entry (never rolled) -- r1180/r1182/r1184 pit family.
The §7 backfill block is taken VERBATIM from the post-W313-finalize face at
HEAD (it is the prior-wave evidence block, inserted after every map so it
cannot be rolled).  Everything else rides ONE single-pass map.

Usage: python results/_w314bmc_prereg_derive.py [--measure|--diag]
"""
import hashlib
import json
import re
import subprocess
import sys

SRC_REV = "c110bf216e"
SRC_PATH = "research/PERPETUAL_N1_W313_PREREG.md"
OUT = "research/PERPETUAL_N1_W314_PREREG.md"
EXPECT_SHA16 = "5c33696ff717fee3"
EXPECT_BYTES = 28291
SEAT_MSG = "MSG-20261024-1915-bmc-w314-seat"
SEAT_SHA = "d683bad881"
FREE_RAM = "1.7"
MEASURE = "--measure" in sys.argv

raw = subprocess.run(["git", "show", "%s:%s" % (SRC_REV, SRC_PATH)],
                     capture_output=True, check=True).stdout
assert len(raw) == EXPECT_BYTES, "src bytes %d != %d" % (len(raw), EXPECT_BYTES)
assert hashlib.sha256(raw).hexdigest()[:16] == EXPECT_SHA16, "src sha16 mismatch"
src = raw.decode("utf-8")
assert src.count("\n") == 75, "src line count %d" % src.count("\n")

# ---------------------------------------------------------------- facts (machine-read)
res = json.load(open("results/perpetual_faces/n1_w313_results.json", encoding="utf-8"))
led = res["science_gates"]["ledger"]
assert led["total"] == 1112941 and led["prev_total"] == 1110741, "ledger anchor drift"
cum = res["null_pool_cumulative"]
assert cum["merged"]["n_values"] == 686520, "merged K drift"
assert abs(cum["merged"]["mu"] + 0.09282770917089087) < 1e-12
assert abs(cum["merged"]["sigma"] - 0.24516098633452796) < 1e-12
assert cum["se_mu_at_k686520"] == 0.000296
assert abs(cum["w313_only"]["mu"] + 0.09864763636363637) < 1e-12
assert abs(cum["w313_only"]["sigma"] - 0.24314311747244605) < 1e-12
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_686520"] == 1.2008 and kl["line_pre_w313"] == 1.2008
assert kl["line_delta_k_lift"] == 0.0
assert kl["n_eff_held_equal"] == 1110741
assert abs(res["families"]["A_random_engine_exit"]["full_sharpe_p95"] - 0.3071) < 1e-12
assert abs(res["families"]["A_random_engine_exit"]["full_sharpe_p99"] - 0.4734) < 1e-12
seed = json.load(open("results/_w314bmc_20261024_probe_receipt.json", encoding="utf-8"))
assert seed["verdict"] == "ADMIT"
l1 = seed["legs"]["leg1"]
assert l1["A"] == [706101, 708100] and l1["B"] == [708101, 708300]
assert l1["hops_A"] == 1 and l1["hops_B"] == 1
l4 = seed["legs"]["leg4"]
assert l4["W315p_A_naive"] == "708_101..710_100"
assert l4["W315p_B_naive"] == "708_301..708_500"
assert seed["legs"]["leg0"]["owner_rows"] == 303
assert seed["legs"]["leg0"]["bmc_rows"] == 132
assert seed["ordinals"]["a_hop"] == 67 and seed["ordinals"]["above_own_a"] == 68
print("facts OK: ledger 1,112,941 / K 686,520 / W313-only mu -0.09864764 / p95 0.3071")

# ---------------------------------------------------------------- 0. prior-wave §7 block (verbatim from HEAD)
head = subprocess.run(["git", "show", "HEAD:%s" % SRC_PATH],
                      capture_output=True, check=True).stdout.decode("utf-8")
j7 = head.find("## \u00a77")
j8 = head.find("## \u00a78")
assert 0 < j7 < j8, "HEAD sec.7 block not found"
SEC7_NEW = head[j7:j8]
assert "W313-only" in SEC7_NEW and "1,112,941" in SEC7_NEW

# ---------------------------------------------------------------- 1. park cumulative history + §7
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


def wave_bump(text, floor=303):
    return re.sub(r"W(\d{3})", lambda m: "W%03d" % (int(m.group(1)) + 1)
                  if int(m.group(1)) >= floor else m.group(0), text)


PROJ = "\u6295\u5f71"          # 投影


def se(old):
    old_tail = "\u2192W313 " + PROJ + " 0.000295"
    assert old_tail in old, "se chain tail not the expected W313 projection"
    assert "0.000296" in old
    return (old.replace(old_tail, "\u2192W313 **0.000296**\u2192W314 " + PROJ + " 0.000295"))


def ab(old):
    t = old.replace("/W310/W311/W312/W313=A/B", "/W310/W311/W312/W313/W314=A/B", 1)
    assert "/W310/W311/W312/W313/W314=A/B" in t, "A/B chain tail not expected /W310..W313=A/B"
    o_ord = "\u7b2c\u516d\u5341\u6ce2"   # 60th wave
    n_ord = "\u7b2c\u516d\u5341\u4e00\u6ce2"  # 61st wave
    assert o_ord in t, "A/B chain ordinal not the expected 60th"
    t = t.replace(o_ord, n_ord)
    return t


def rot(old):
    t = old.replace("\u2192W313 bm-c own-turn rotation",
                    "\u2192W313 bm-c\u2192W314 bm-c own-turn rotation", 1)
    assert "W314 bm-c own-turn rotation" in t, "own-turn chain tail not expected W313"
    return t


def ram(old):
    m = re.search(r"\u00b7W312 \u51bb\u7ed3\u7a97 ~([\d.]+)G bm-c \u5b9e\u951a\u00b7\u672c\u7a97\u51bb\u7ed3\u7a97 ~([\d.]+)G bm-c \u5b9e\u951a\uff09", old)
    assert m, "RAM chain tail not found"
    word = "\u5b9e\u951a"   # 实锚
    new_tail = ("\u00b7W312 \u51bb\u7ed3\u7a97 ~" + m.group(1) + "G bm-c " + word +
                "\u00b7W313 \u51bb\u7ed3\u7a97 ~" + m.group(2) + "G bm-c " + word +
                "\u00b7\u672c\u7a97\u51bb\u7ed3\u7a97 ~" + FREE_RAM + "G bm-c " + word + "\uff09")
    return old[:m.start()] + new_tail + old[m.end():]


park(r"W277 \*\*0\.000314\*\*[^\n]*?\u6295\u5f71 0\.000295", se, "SECH")
park(r"W252/W253[^\n]*?\u7b2c\u516d\u5341\u6ce2", ab, "ABCHAIN")
park(r"W288 bm-c[\s\S]{0,900}?own-turn rotation", rot, "ROTCH")
park(r"W206/W211[^\n]*?\u5b9e\u951a\uff09", ram, "RAMCH")

# §7 block (prior-wave finalize evidence): parked, re-inserted verbatim after all maps
i7 = out.find("## \u00a77")
assert i7 > 0, "sec.7 header not found"
i7_end = out.find("## \u00a78", i7)
assert i7_end > i7, "sec.8 header not found after sec.7"
out = out[:i7] + "ZZSEC7\n" + out[i7_end:]

# §8 block: rebuilt explicitly (finalize-time backfill face; r1184 self-reference family)
i8 = out.find("## \u00a78")
assert i8 > 0, "sec.8 header not found"
i8_end = out.find("- **\u8dd1\u524d\u51bb\u7ed3=\u672c\u4ef6 commit**", i8)
assert i8_end > i8, "sec.8 tail marker not found"
SEC8 = out[i8:i8_end]
assert SEC8.count("703_901..705_900") == 1 and SEC8.count("705_901..706_100") == 1
out = out[:i8] + "ZZSECS" + out[i8_end:]

# ---------------------------------------------------------------- 2. wave labels +1 (W>=303)
out = wave_bump(out)

# ---------------------------------------------------------------- 3. numeric / ordinal / artifact maps
NUM = [
    # --- ledger / pool anchors (longest keys first, single-pass)
    ("1,110,741", "1,112,941"),
    ("684,320", "686,520"),
    ("686,520", "688,720"),
    # --- merged / wave-only statistics
    ("\u22120.09280900", "\u22120.09282771"),
    ("0.24516740", "0.24516099"),
    ("\u22120.08867268", "\u22120.09864764"),
    # --- A/B family percentile band
    ("0.3338", "0.3071"),
    # --- K-lift line
    ("1.2007", "1.2008"),
    ("line_pre_w313", "line_pre_w314"),
    ("W313 \u5b9e\u6d4b K-lift **+0.0001**", "W313 \u5b9e\u6d4b K-lift **+0.0000**"),
    # --- wave / row / seed ordinals
    ("\u7b2c 311 \u679a", "\u7b2c 312 \u679a"),
    ("\u6ce2\u53f7 311=", "\u6ce2\u53f7 312="),
    ("\u884c 302 \u6ce8\u518c\u5728\u518c", "\u884c 303 \u6ce8\u518c\u5728\u518c"),
    ("bmc rows 131+\u5019\u9009=\u7b2c 132 \u679a", "bmc rows 132+\u5019\u9009=\u7b2c 133 \u679a"),
    ("bmc_rows=131", "bmc_rows=132"),
    ("bmc live rows 131", "bmc live rows 132"),
    ("\u7b2c\u4e00\u767e\u4e09\u5341\u4e00\u679a", "\u7b2c\u4e00\u767e\u4e09\u5341\u4e8c\u679a"),
    ("\u5f15\u64ce\u7ebf\u7b2c 303 \u6ce2", "\u5f15\u64ce\u7ebf\u7b2c 304 \u6ce2"),
    ("\u4e09\u767e\u96f6\u4e03\u9762", "\u4e09\u767e\u96f6\u516b\u9762"),
    ("CLEAN-AT-BIRTH 44th gen", "CLEAN-AT-BIRTH 45th gen"),
    # --- ordinal words (single-pass; NEVER chained)
    ("\u7b2c\u516d\u5341\u516d\u6b21", "\u7b2c\u516d\u5341\u4e03\u6b21"),
    ("\u7b2c\u516d\u5341\u4e03\u6b21", "\u7b2c\u516d\u5341\u516b\u6b21"),
    # --- runner / artifact names
    ("--wave 313", "--wave 314"),
    ("n1_w312", "n1_w313"),
    ("n1_w313", "n1_w314"),
    ("_w312bmc_", "_w313bmc_"),
    ("_w313bmc_", "_w314bmc_"),
    ("MSG-20261024-1749-bmc-w313-seat", SEAT_MSG),
    # --- commit shas (prereg / splice / seat chain)
    ("3c1691cf81", "c110bf216e"),
    ("0a5e9866f3", "c44743a1ea"),
    ("6f4d496935", SEAT_SHA),
    # --- window clock / round labels (clause-level, single-pass)
    ("bm-c r1203 \u7a97 17:4x\u00b7estate chain r1202/r1202/r1203 W313 \u5168\u5468\u671f",
     "bm-c r1206 \u7a97 19:0x\u00b7estate chain r1204/r1205/r1206 W313 \u5168\u5468\u671f"),
    ("bm-c r1202 \u4e94\u9762\u51bb\u7ed3 splice", "bm-c r1205 \u4e94\u9762\u51bb\u7ed3 splice"),
    ("\u843d\u5730 17:1x", "\u843d\u5730 18:1x"),
    ("\u5e2d\u4f4d r1204 \u7a97+prereg r1205 \u7a97\u843d\u5730",
     "\u5e2d\u4f4d r1207 \u7a97+prereg r1207 \u7a97\u843d\u5730"),
    ("\u5faa\u73af\u73ed r1205 \u51bb\u7ed3\u7a97 2026-10-24 18:0x",
     "\u5faa\u73af\u73ed r1207 \u51bb\u7ed3\u7a97 2026-10-24 19:1x"),
    ("r1204 \u5e2d\u4f4d\u7a97\u5b9e\u8dd1", "r1207 \u5e2d\u4f4d\u7a97\u5b9e\u8dd1"),
    ("live-read r1204", "live-read r1207"),
    ("heartbeat \u65b0\u9c9c\u5b9e\u8bfb r1202 \u7a97", "heartbeat \u65b0\u9c9c\u5b9e\u8bfb r1207 \u7a97"),
    ("heartbeat \u65b0\u9c9c r1204 \u7a97\u5b9e\u8bfb", "heartbeat \u65b0\u9c9c r1207 \u7a97\u5b9e\u8bfb"),
    ("\uff08r1204 \u7a97\u7b97\u6cd5", "\uff08r1207 \u7a97\u7b97\u6cd5"),
    ("prereg 3c1691cf81 \u843d\u4e8e r1202 \u7a97\u00b7splice 0a5e9866f3 \u843d\u4e8e r1202 \u6267\u884c\u7a97 17:1x",
     "prereg c110bf216e \u843d\u4e8e r1205 \u7a97\u00b7splice c44743a1ea \u843d\u4e8e r1205 \u6267\u884c\u7a97 18:1x"),
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
TOK = re.compile(r"\b(\d{3})_(\d{3})\b")
print("band tokens distinct:", sorted(set(TOK.findall(out))))


def roll(m):
    v = int(m.group(1)) * 1000 + int(m.group(2)) + 2200
    return "%03d_%03d" % (v // 1000, v % 1000)


out, nband = re.subn(TOK, roll, out)
assert nband > 0
print("band tokens rolled:", nband)

for sent, txt in stash.items():
    assert out.count(sent) == 1, "sentinel %s count %d" % (sent, out.count(sent))
    out = out.replace(sent, txt)

# ---------------------------------------------------------------- 5. sec.7 / sec.8 rebuild (explicit, never rolled)
assert out.count("ZZSEC7") == 1
out = out.replace("ZZSEC7\n", SEC7_NEW)

SEC8_NEW = (
    "## \u00a78 \u6279\u540e\u590d\u76d8\u3002\u3010finalize \u540c\u7a97\u56de\u586b\u3011\n"
    "- \u00a75.5 W315+ \u6295\u5f71\u627f\u63a5\u673a\u8bc1\uff1a\u672c\u7a97\u5e2d\u4f4d\u56de\u6267 leg4\uff08pre-W314 \u5b87\u5b99\uff09"
    "\u6295\u5f71 W315p A naive **708_101..710_100** clean\uff08hops=0\uff09\u3001B naive **708_301..708_500** clean "
    "\u4f46\u843d\u6295\u5f71 A \u7a97\u5185\uff08own-A reservation \u627f\u88ad\u9884\u671f\uff09\u2014\u2014**W315 \u51bb\u7ed3\u65b9\u5fc5\u987b\u5728 "
    "post-W314 \u5b87\u5b99\u91cd live derive \u4e14 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97\uff08W141 \u5148\u4f8b\uff09\u00b7never transcribe r587**\u3002\n"
    "- \u672c\u7a97\u5e2d\u4f4d\u5b9e\u6d4b\u673a\u8bc1\uff1aA **706_101..708_100**\uff0867th \u8fde\u7eed A-hop\u00b7hops=1\u00b7base==\u6ce8\u518c W313 B \u5c3e 706_100+1\uff09\uff0f"
    "B **708_101..708_300**\uff0868th \u8fde\u7eed above-own-A\u00b7hops=1\u00b7base==\u672c\u6ce2 A \u5c3e 708_100+1\uff09\u2014\u2014"
    "`results/_w314bmc_20261024_probe_receipt.json` verdict ADMIT\u00b7relation_asserts 4/4\u00b7seed_admit_gate FREE x2\u00b7leg3 bands_clear=true\u3002\n"
    "- \u5b9d\u85cf\u4e0e\u65b9\u6cd5\u8bba\u6355\u83b7\u95ee\uff1a\u672c\u6ce2=nulls-deepening \u5e38\u6001\u52a0\u6df1\uff0c**\u65e0\u65b0\u65b9\u6cd5/\u65e0\u65b0\u5b9d\u85cf**\uff0c"
    "knowledge/METHODOLOGY_ASSETS.md \u4e0e TREASURE_REGISTRY.md \u5747\u4e0d\u8ffd\u52a0\u3002\n"
    "- \u8bda\u5b9e\u62ab\u9732\uff1a\u00a75 \u4e94\u9884\u952e\u82e5\u51fa\u73b0 prose \u504f\u5dee\uff08se_mu \u53d6 3 \u4f4d\u5c0f\u6570\uff09\uff0c\u4ee5\u673a\u8bfb\u503c\u4e3a\u51c6\u5e76\u62ab\u9732\u3001"
    "\u4e0d\u62b9\u5e73\uff1bmu/sigma/K-lift \u4e00\u5f8b\u6309\u51bb\u7ed3\u5e26\u6821\u9a8c\u3002\n"
    "- \u5751\u5f8b\u6355\u83b7\uff1apost-W314 finalize \u540c\u7a97\u56de\u586b\uff08\u672c\u6bb5\u5c5e finalize \u56de\u586b\u9762\uff0c\u51bb\u7ed3\u65f6\u4e3a\u524d\u6ce2\u6cbf\u7528\u6587\u672c\uff09\uff1b"
    "\u672c\u7a97\u51bb\u7ed3\u6cbf\u7528 r1206 \u5224\u4f8b\uff1acanon-clone \u751f\u6210\u5668\u7684\u4e0a\u4e00\u6ce2\u6ce8\u518c\u9762\u6b63\u5219\u4e0e boundary \u79cd\u5b50\u9762\u4e00\u5f8b\u4fdd\u7559**\u4e0a\u4e00\u6ce2**\u5f62\u6001\u4ea4\u7ed9\u6ce2\u53f7\u7ea7\u8054\u63a8\u8fdb\u4e00\u6b21\uff0c\u7981\u624b\u5199\u6210\u672c\u6ce2\u53f7\u3002\n"
    "- \u6536\u53e3\u7eaa\u5f8b\uff1afinalize \u53ea\u6d88\u8d39\u5728\u518c\u5206\u7247\uff08audit.finalize_only=true\uff09\uff0c\u672c\u6ce2\u96f6\u91cd\u70e7\u3001\u96f6\u53cc\u70e7\uff1b"
    "S6 \u94fe\u4e0e\u8f6e\u6536\u53e3\u540c\u7a97\u3002\n\n\n"
)
assert out.count("ZZSECS") == 1
out = out.replace("ZZSECS", SEC8_NEW)

# ---------------------------------------------------------------- 5b. post-fixes
POST = [
    ("\u672c\u7a97 free RAM 1.2GB", "\u672c\u7a97 free RAM " + FREE_RAM + "GB"),
    ("bm-c r1204 \u5e2d\u4f4d MSG-20261024-1915-bmc-w314-seat",
     "bm-c r1207 \u5e2d\u4f4d MSG-20261024-1915-bmc-w314-seat"),
    ("bm-c r1204 \u5e2d\u00b7queue-head", "bm-c r1207 \u5e2d\u00b7queue-head"),
    ("r1202/r1202/r1203 W313", "r1204/r1205/r1206 W313"),
    ("bm-c r1203 \u7a97 17:4x", "bm-c r1206 \u7a97 19:0x"),
]
for old, new in POST:
    n = out.count(old)
    assert n >= 1, "post-fix %r hits=%d" % (old, n)
    out = out.replace(old, new)
    print("post-fix applied hits=%d" % n)

# ---------------------------------------------------------------- 6. asserts
if "--diag" in sys.argv:
    for tok in ("706_100", "706_101", "708_100", "708_101", "708_300", "708_301"):
        print("DIAG", tok, out.count(tok))
    sys.exit(0)

assert out.count("\n") == 75, "line count changed: %d" % out.count("\n")
assert out.count("706_101..708_100") >= 2, "new A band missing"
assert out.count("708_101..708_300") >= 2, "new B band missing"
assert out.count("705_901..707_900") >= 1, "naive A continuation band missing"
assert out.count("708_301..708_500") >= 1, "W315p B naive band missing"
assert out.count("708_101..710_100") >= 1, "W315p A naive band missing"
assert out.count("W314") > 30 and out.count("W315") > 5
assert out.count("W301") == src.count("W301"), "W301 (cumulative) must not roll"
assert out.count("W302") == src.count("W302"), "W302 (cumulative) must not roll"
assert out.count("W303") == src.count("W303"), "W303 (cumulative) must not roll"
assert out.count("1,112,941") >= 3, "new ledger anchor missing"
assert out.count("686,520") >= src.count("684,320"), "prior-K roll mismatch"
assert out.count("line_pre_w314") >= 1 and out.count("line_pre_w313") == 1  # sec.7 prior block
assert out.count("ZZ") == 0, "sentinel leaked"
assert out.count("n1_w313") >= 4 and out.count("n1_w314") >= 1
assert out.count("n1_w312") == 0, "n1 double roll"
assert out.count(SEAT_SHA) >= 3
assert out.count(SEAT_MSG) >= 3
assert out.count("CLEAN-AT-BIRTH 45th gen") == 1
assert out.count("r1207") >= 3, "round labels"
assert "703,901..705,900" not in out, "stale comma-form band leaked"
assert out.count("_w314bmc_20261024_probe_receipt.json") >= 2
assert "\u7b2c 76 \u6b21" in out, "sixgate ordinal missing"
assert out.count("W313-only") >= 1  # sec.7 prior-wave block intact

receipt = {"keys": counts, "band_tokens": nband,
           "bytes_src": len(raw), "bytes_out": len(out.encode("utf-8"))}
open("results/_w314bmc_derive_counts.json", "w", encoding="utf-8").write(
    json.dumps(receipt, ensure_ascii=False, indent=1))
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(out)
b = out.encode("utf-8")
print("WROTE %s bytes=%d lines=%d sha16=%s bands=%d keys=%d" % (
    OUT, len(b), out.count("\n"), hashlib.sha256(b).hexdigest()[:16], nband, len(NUM)))