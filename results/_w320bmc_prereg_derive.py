# -*- coding: utf-8 -*-
"""W320 prereg derive (bm-c r1220).

Canon-clone of the W319 POST-RUN face
(git e1aef41119:research/PERPETUAL_N1_W319_PREREG.md) -> research/PERPETUAL_N1_W320_PREREG.md.

Cumulative-history chains (se_mu narrowing, A/B 1-hop wave list, own-turn
rotation list, RAM freeze chain) are parked behind pure-letter sentinels and
EXTENDED by one entry (never rolled) -- r1180/r1182/r1184/r1208 pit family.
The section-7 block is taken VERBATIM from the post-W319-finalize face at HEAD.
Everything else rides ONE single-pass map (r1168/r1170/r1171/r1179/r1199/r1206).

Face classification (r1208/r1214):
  wave tokens (W###)  -> cascade +1 (floor 304)
  band tokens         -> arithmetically +2200 (never a NUM key)
  ordinal words       -> single-pass map (NEVER chained)
  accumulated chains  -> parked, extended by one entry
  self/prior refs     -> explicit hand values in this file

Usage: python results/_w320bmc_prereg_derive.py [--measure|--diag]
"""
import hashlib
import json
import re
import subprocess
import sys

SRC_REV = "e1aef41119"
SRC_PATH = "research/PERPETUAL_N1_W319_PREREG.md"
OUT = "research/PERPETUAL_N1_W320_PREREG.md"
SEAT_MSG = "MSG-20261025-0048-bmc-w320-seat"
SEAT_SHA = "e1aef41119"
FREE_RAM = "4.3"
MEASURE = "--measure" in sys.argv
PROJ = "\u6295\u5f71"          # projection
ANCHOR = "\u5b9e\u951a"        # measured anchor
FREEZE = "\u51bb\u7ed3\u7a97"   # freeze window

raw = subprocess.run(["git", "show", "%s:%s" % (SRC_REV, SRC_PATH)],
                     capture_output=True, check=True).stdout
EXPECT_BYTES = len(raw)
EXPECT_SHA16 = hashlib.sha256(raw).hexdigest()[:16]
src = raw.decode("utf-8")
print("SRC %s bytes=%d lines=%d sha16=%s" % (SRC_PATH, EXPECT_BYTES,
                                             src.count("\n"), EXPECT_SHA16))
assert src.count("\n") == 77, "src line count %d" % src.count("\n")

# ---------------------------------------------------------------- facts (machine-read)
res = json.load(open("results/perpetual_faces/n1_w319_results.json", encoding="utf-8"))
led = res["science_gates"]["ledger"]
assert led["total"] == 1126141 and led["prev_total"] == 1123941, "ledger anchor drift"
cum = res["null_pool_cumulative"]
assert cum["merged"]["n_values"] == 699720, "merged K drift"
assert abs(cum["merged"]["mu"] + 0.09279661407420112) < 1e-12
assert abs(cum["merged"]["sigma"] - 0.24516945432103654) < 1e-12
assert cum["se_mu_at_k699720"] == 0.000293
assert abs(cum["w319_only"]["mu"] + 0.08307518181818181) < 1e-12
assert abs(cum["w319_only"]["sigma"] - 0.2443567200664271) < 1e-12
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_699720"] == 1.2014 and kl["line_pre_w319"] == 1.2014
assert kl["line_delta_k_lift"] == 0.0
assert kl["n_eff_held_equal"] == 1123941
assert abs(res["families"]["A_random_engine_exit"]["full_sharpe_p95"] - 0.3225) < 1e-12
assert abs(res["families"]["A_random_engine_exit"]["full_sharpe_p99"] - 0.4535) < 1e-12
DELTA = abs(cum["w319_only"]["mu"] - cum["merged"]["mu"])
assert abs(DELTA - 0.00972143225598069) < 1e-12
seed = json.load(open("results/_w320bmc_20261025_probe_receipt.json", encoding="utf-8"))
assert seed["verdict"] == "ADMIT"
l1 = seed["legs"]["leg1"]
assert l1["A"] == [719301, 721300] and l1["B"] == [721301, 721500]
assert l1["hops_A"] == 1 and l1["hops_B"] == 1
l4 = seed["legs"]["leg4"]
assert l4["W321p_A_naive"] == "721_301..723_300"
assert l4["W321p_B_naive"] == "721_501..721_700"
assert seed["legs"]["leg0"]["owner_rows"] == 309
assert seed["legs"]["leg0"]["bmc_rows"] == 138
assert seed["ordinals"]["a_hop"] == 73 and seed["ordinals"]["above_own_a"] == 74
print("facts OK: ledger 1,126,141 / K 699,720 / W319-only mu -0.08307518 / p95 0.3225 / delta %.8f" % DELTA)

# ---------------------------------------------------------------- 0. prior-wave S7 block (verbatim from HEAD)
head = subprocess.run(["git", "show", "HEAD:%s" % SRC_PATH],
                      capture_output=True, check=True).stdout.decode("utf-8")
j7 = head.find("## \u00a77")
j8 = head.find("## \u00a78")
assert 0 < j7 < j8, "HEAD sec.7 block not found"
SEC7_NEW = head[j7:j8]
assert "W319-only" in SEC7_NEW and "1,126,141" in SEC7_NEW

# ---------------------------------------------------------------- 1. park cumulative history + S7
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


def wave_bump(text, floor=304):
    return re.sub(r"W(\d{3})", lambda m: "W%03d" % (int(m.group(1)) + 1)
                  if int(m.group(1)) >= floor else m.group(0), text)


def se(old):
    old_tail = "\u2192W319 " + PROJ + " 0.000293"
    assert old_tail in old, "se chain tail not the expected W319 projection"
    return old.replace(old_tail,
                       "\u2192W319 **0.000293**\u2192W320 " + PROJ + " 0.000293")


def ab(old):
    t = old.replace("=A/B", "/W320=A/B", 1)
    assert "/W320=A/B" in t, "A/B chain tail not extended"
    return t


def rot(old):
    t = old.replace("\u2192W319 bm-c own-turn rotation",
                    "\u2192W319 bm-c\u2192W320 bm-c own-turn rotation", 1)
    assert "W320 bm-c own-turn rotation" in t, "own-turn chain tail not expected W319"
    return t


def ram(old):
    m = re.search(r"\u00b7\u672c\u7a97" + FREEZE + r" ~([\d.]+)G bm-c " + ANCHOR + "\uff09", old)
    assert m, "RAM chain tail not found"
    new = ("\u00b7W319 " + FREEZE + " ~" + m.group(1) + "G bm-c " + ANCHOR +
           "\u00b7\u672c\u7a97" + FREEZE + " ~" + FREE_RAM + "G bm-c " + ANCHOR + "\uff09")
    return old[:m.start()] + new + old[m.end():]


park(r"W277 \*\*0\.000314\*\*[^\n]*?\u6295\u5f71 0\.000293", se, "SECH")
park(r"W252/W253[^\n]*?=A/B", ab, "ABCHAIN")
park(r"W288 bm-c(?:\u2192W\d{3} bm-c)* own-turn rotation", rot, "ROTCH")
park(r"W206/W211[^\n]*?" + ANCHOR + "\uff09", ram, "RAMCH")

# S7 block (prior-wave finalize evidence): parked, re-inserted verbatim after all maps
i7 = out.find("## \u00a77")
assert i7 > 0, "sec.7 header not found"
i7_end = out.find("## \u00a78", i7)
assert i7_end > i7, "sec.8 header not found after sec.7"
out = out[:i7] + "ZZSEC7\n" + out[i7_end:]

# S8 block: rebuilt explicitly (finalize-time backfill face; self-reference family)
i8 = out.find("## \u00a78")
assert i8 > 0, "sec.8 header not found"
i8_end = out.find("- **\u8dd1\u524d\u51bb\u7ed3=\u672c\u4ef6 commit**", i8)
assert i8_end > i8, "sec.8 tail marker not found"
SEC8 = out[i8:i8_end]
assert SEC8.count("W320+") == 1 and "lands_inside" in SEC8, "sec.8 template drift"
out = out[:i8] + "ZZSECS" + out[i8_end:]

# ---------------------------------------------------------------- 2. wave labels +1 (W>=304)
out = wave_bump(out)

# ---------------------------------------------------------------- 3. numeric / ordinal / artifact maps
NUM = [
    # --- ledger / pool anchors (single-pass; longest key wins)
    ("1,123,941", "1,126,141"),
    ("1,121,741", "1,123,941"),
    ("K697,520", "K699,720"),
    ("697,520", "699,720"),
    # --- merged / wave-only statistics
    ("\u22120.09282728", "\u22120.09279661"),
    ("0.24517158", "0.24516945"),
    ("\u22120.09374523", "\u22120.08307518"),
    ("0.005731", "0.00972"),
    # --- A family p95 anchor
    ("0.3212", "0.3225"),
    # --- K-lift pair (long key wins over the bare decimals)
    ("**1.2013**\u00b7line_pre_w319 1.2013", "**1.2014**\u00b7line_pre_w320 1.2014"),
    ("line_pre_w319", "line_pre_w320"),
    # --- wave / row / seed ordinals
    ("\u6c60\u7b2c 317 \u679a", "\u6c60\u7b2c 318 \u679a"),
    ("\u884c 308 \u6ce8\u518c\u5728\u518c", "\u884c 309 \u6ce8\u518c\u5728\u518c"),
    ("bmc rows 137+\u5019\u9009=\u7b2c 138 \u679a", "bmc rows 138+\u5019\u9009=\u7b2c 139 \u679a"),
    ("bmc_rows=137", "bmc_rows=138"),
    ("bmc live rows 137", "bmc live rows 138"),
    ("\u7b2c\u4e00\u767e\u4e09\u5341\u4e03\u679a", "\u7b2c\u4e00\u767e\u4e09\u5341\u516b\u679a"),
    ("\u5f15\u64ce\u7ebf\u7b2c 309 \u6ce2", "\u5f15\u64ce\u7ebf\u7b2c 310 \u6ce2"),
    ("\u6ce2\u53f7 317=", "\u6ce2\u53f7 318="),
    ("\u4e09\u767e\u4e00\u5341\u4e09\u9762", "\u4e09\u767e\u4e00\u5341\u56db\u9762"),
    ("CLEAN-AT-BIRTH 50th gen", "CLEAN-AT-BIRTH 51st gen"),
    # --- ordinal words (single-pass; NEVER chained)
    ("\u7b2c\u4e03\u5341\u4e8c\u6b21", "\u7b2c\u4e03\u5341\u4e09\u6b21"),
    ("\u7b2c\u4e03\u5341\u4e09\u6b21", "\u7b2c\u4e03\u5341\u56db\u6b21"),
    ("\u7b2c\u516d\u5341\u516d\u6ce2", "\u7b2c\u516d\u5341\u4e03\u6ce2"),
    # --- runner / artifact names
    ("--wave 319", "--wave 320"),
    ("n1_w318", "n1_w319"),
    ("n1_w319", "n1_w320"),
    ("_w319bmc_20261025", "_w320bmc_20261025"),
    ("_w319bmc_", "_w320bmc_"),
    ("MSG-20261025-0003-bmc-w319-seat", SEAT_MSG),
    # --- commit shas (prereg / splice / closeout chain)
    ("87669dc1da", "29c7158b0a"),
    ("4a78879173", "3b7d58a25b"),
    ("4421303e49", SEAT_SHA),
    # --- window clock / round labels (long keys first via sort)
    ("bm-c r1217 \u4e94\u9762\u51bb\u7ed3 splice 4a78879173 \u843d\u5730 23:2x",
     "bm-c r1219 \u4e94\u9762\u51bb\u7ed3 splice 3b7d58a25b \u843d\u5730 00:3x"),
    ("bm-c r1218 \u7a97 00:0x", "bm-c r1219 \u7a97 00:4x"),
    ("\u6267\u884c\u7a97 23:2x", "\u6267\u884c\u7a97 00:3x"),
    ("r1217/r1217/r1218 W319", "r1219/r1219/r1219 W319"),
    ("prereg 87669dc1da \u843d\u4e8e r1217 \u7a97", "prereg 29c7158b0a \u843d\u4e8e r1219 \u7a97"),
    ("estate chain r1217/r1217/r1218 W319 \u5168\u5468\u671f 87669dc1da+4a78879173+4421303e49",
     "estate chain r1219/r1219/r1219 W319 \u5168\u5468\u671f 29c7158b0a+3b7d58a25b+e1aef41119"),
    ("\u5e2d\u4f4d r1218 \u7a97+prereg r1219 \u7a97\u843d\u5730", "\u5e2d\u4f4d r1219 \u7a97+prereg r1220 \u7a97\u843d\u5730"),
    ("bm-c r1218 \u5e2d\u4f4d", "bm-c r1219 \u5e2d\u4f4d"),
    ("bm-c \u5faa\u73af\u73ed r1219 " + FREEZE + " 2026-10-25 00:2x",
     "bm-c \u5faa\u73af\u73ed r1220 " + FREEZE + " 2026-10-25 01:0x"),
    ("00:0x", "00:4x"),
    ("r1217", "r1219"),
    ("r1218", "r1219"),
    ("r1219", "r1220"),
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
    "- \u00a75.5 W321+ \u6295\u5f71\u627f\u63a5\u673a\u8bc1\uff1a\u672c\u7a97\u5e2d\u4f4d\u56de\u6267 leg4\uff08pre-W320 \u5b87\u5b99\uff09\u6295\u5f71 W321p A naive **721_301..723_300** clean\uff08hops=0\uff09\u3001"
    "B naive **721_501..721_700** clean\uff08hops=0\uff09\u4f46\u843d\u6295\u5f71 A \u7a97\u5185\uff08own-A reservation \u627f\u88ad\u9884\u671f\uff09\u2014\u2014**W321 \u51bb\u7ed3\u65b9\u5fc5\u987b\u5728 post-W320 \u5b87\u5b99 "
    "\u91cd live derive \u4e14\u5728 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97\uff08W141 \u5148\u4f8b\uff09\u00b7never transcribe r587**\u3002\n"
    "- \u672c\u7a97\u5e2d\u4f4d\u5b9e\u6d4b\u673a\u8bc1\uff1aA **719_301..721_300**\uff0873rd \u8fde\u7eed A-hop\u00b7hops=1\u00b7base==\u6ce8\u518c W319 B \u5c3e 719_300+1\uff09\uff0f"
    "B **721_301..721_500**\uff0874th \u8fde\u7eed above-own-A\u00b7hops=1\u00b7base==\u672c\u6ce2 A \u5c3e 721_300+1\uff09\u2014\u2014"
    "`results/_w320bmc_20261025_probe_receipt.json` verdict ADMIT\u00b7relation_asserts 4/4\u00b7seed_admit_gate FREE x2\u00b7leg3 bands_clear=True\u3002\n"
    "- \u5b9d\u85cf\u4e0e\u65b9\u6cd5\u8bba\u6355\u83b7\u95ee\uff1a\u672c\u6ce2=nulls-deepening \u5e38\u6001\u52a0\u6df1\uff0c**\u65e0\u65b0\u65b9\u6cd5/\u65e0\u65b0\u5b9d\u85cf**\uff0cknowledge/METHODOLOGY_ASSETS.md \u4e0e "
    "TREASURE_REGISTRY.json \u5747\u4e0d\u8ffd\u52a0\u3002\n"
    "- \u8bda\u5b9e\u62ab\u9732\uff08\u672c\u6ce2 1 \u6761\u00b7prose \u9762\uff0c\u5224\u636e\u4e0e\u4ea7\u7269\u96f6\u5f71\u54cd\uff09\uff1a\n"
    "  \u2460 \u00a75 \u4e94\u9884\u952e\u82e5\u51fa\u73b0 prose \u504f\u5dee\uff08se_mu \u53d6 3 \u4f4d\u5c0f\u6570\uff09\uff0c\u4ee5\u673a\u8bfb\u503c\u4e3a\u51c6\u5e76\u62ab\u9732\u3001\u4e0d\u62b9\u5e73\uff1bmu/sigma/p95/K-lift \u4e00\u5f8b\u6309\u51bb\u7ed3\u5e26\u6821\u9a8c\u3002\n"
    "  \u2461 \u00a75 \u7b2c 5 \u6761\u7684 W321 \u6295\u5f71\u5c5e probe \u673a\u8bc1\u9762\uff08pre-W320 \u5b87\u5b99\uff09\uff0c\u975e\u627f\u8bfa\u2014\u2014\u672c\u6ce2\u5b9e\u6d4b\u4ee5 post-W320 live trace \u4e3a\u51c6\u3002\n"
    "- \u5751\u5f8b\u6355\u83b7\uff08\u672c\u7a97\uff09\uff1a\u2460post-W319 finalize \u540c\u7a97\u56de\u586b\uff08\u672c\u6bb5\u5c5e finalize \u56de\u586b\u9762\uff0c\u51bb\u7ed3\u65f6\u4e3a\u524d\u6ce2\u6cbf\u7528\u6587\u672c\uff09\uff1b"
    "\u2461canon-clone \u751f\u6210\u5668\u7684\u7eaf\u6570\u5b57\u9762\uff08\u6ce8\u518c\u884c\u53f7\u524d\u7f00/\u5207\u53e3/setwave \u952e\u540e\u7f00\uff09\u76f4\u5199\u76ee\u6807\u6ce2\u53f7\u3001W token \u9762\u4fdd\u7559**\u4e0a\u4e00\u6ce2**\u5f62\u6001\u4ea4\u7ed9\u7ea7\u8054\u63a8\u8fdb\u4e00\u6b21\uff1b"
    "\u7d2f\u79ef\u94fe\uff08se_mu/A-B/own-turn/RAM\uff09\u4e00\u5f8b park+\u5ef6\u957f\u4e00\u6761\uff0c\u7981\u6eda\u3002\n"
    "- \u6536\u53e3\u7eaa\u5f8b\uff1afinalize \u53ea\u6d88\u8d39\u5728\u518c\u5206\u7247\uff08audit.finalize_only=true\uff09\uff0c\u672c\u6ce2\u96f6\u91cd\u70e7\u3001\u96f6\u53cc\u70e7\uff1bS6 \u94fe\u4e0e\u8f6e\u6536\u53e3\u540c\u7a97\u3002\n\n\n"
)
assert out.count("ZZSECS") == 1
out = out.replace("ZZSECS", SEC8_NEW)

# ---------------------------------------------------------------- 5b. post-fixes (live readings this window)
POST = [
    ("GPU=gen-only \u8f66\u9053 idle\uff08nvidia-smi \u5b9e\u8bfb util 2%\u00b7VRAM \u5360\u7528 3.0G/16G\u00b7\u975e\u672c\u6ce2\u5360\u7528\u00b7CPU \u8f66\u9053\u72ec\u7acb\uff09",
     "GPU=gen-only \u8f66\u9053 idle\uff08nvidia-smi \u5b9e\u8bfb util 1%\u00b7VRAM \u5360\u7528 14.1G/16G\uff08\u5e38\u9a7b\u9762\u5360\u7528\u00b7\u975e\u672c\u6ce2\uff09\u00b7CPU \u8f66\u9053\u72ec\u7acb\uff09"),
    # inherited prose lag repaired (r1170 family): the projected cumulative pool
    # after this wave is prior K + 2,200, not prior K itself.
    ("699,720+2,200\uff08\u672c\u6ce2\uff09=**699,720 \u6295\u5f71**",
     "699,720+2,200\uff08\u672c\u6ce2\uff09=**701,920 \u6295\u5f71**"),
]
for old, new in POST:
    n = out.count(old)
    assert n >= 1, "post-fix %r hits=%d" % (old[:40], n)
    out = out.replace(old, new)
    print("post-fix applied hits=%d" % n)

# ---------------------------------------------------------------- 6. asserts
if "--diag" in sys.argv:
    for tok in ("719_301", "721_300", "721_301", "721_500", "721_501", "721_700",
                "723_300", "717_101"):
        print("DIAG", tok, out.count(tok))
    sys.exit(0)

assert out.count("\n") == 77, "line count changed: %d" % out.count("\n")
assert out.count("719_301..721_300") >= 2, "new A band missing"
assert out.count("721_301..721_500") >= 2, "new B band missing"
assert out.count("721_301..723_300") >= 1 and out.count("721_501..721_700") >= 1
assert out.count("W320") > 30 and out.count("W321") > 5
assert out.count("W302") == src.count("W302"), "W302 (cumulative) must not roll"
assert out.count("W303") == src.count("W303"), "W303 (cumulative) must not roll"
assert out.count("1,126,141") >= 3, "new ledger anchor missing"
assert out.count("699,720") >= src.count("697,520") - 2, "prior-K roll mismatch"
assert out.count("line_pre_w320") >= 1 and out.count("line_pre_w319") == 1  # sec.7 prior block
assert out.count("ZZ") == 0, "sentinel leaked"
assert out.count("n1_w319") >= 4 and out.count("n1_w320") >= 1
assert out.count("n1_w318") == 0, "n1 double roll"
assert out.count(SEAT_SHA) >= 3
assert out.count(SEAT_MSG) >= 3
assert out.count("CLEAN-AT-BIRTH 51st gen") == 1
assert out.count("r1220") >= 6, "round labels"
assert out.count("_w320bmc_20261025_probe_receipt.json") >= 1
assert out.count("\u7b2c 83 \u6b21") == 0, "sixgate ordinal is a sec.7 (prior-wave) face"
assert out.count("W319-only") >= 1  # sec.7 prior-wave block intact

receipt = {"keys": counts, "band_tokens": nband,
           "bytes_src": len(raw), "bytes_out": len(out.encode("utf-8"))}
open("results/_w320bmc_derive_counts.json", "w", encoding="utf-8").write(
    json.dumps(receipt, ensure_ascii=False, indent=1))
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(out)
b = out.encode("utf-8")
print("WROTE %s bytes=%d lines=%d sha16=%s bands=%d keys=%d" % (
    OUT, len(b), out.count("\n"), hashlib.sha256(b).hexdigest()[:16], nband, len(NUM)))