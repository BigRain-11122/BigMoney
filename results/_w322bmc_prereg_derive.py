# -*- coding: utf-8 -*-
"""W322 prereg derive (bm-c r1225).

Canon-clone of the W321 POST-RUN face
(git d8136c2994:research/PERPETUAL_N1_W321_PREREG.md) -> research/PERPETUAL_N1_W322_PREREG.md.

Cumulative-history chains (se_mu narrowing, A/B 1-hop wave list, own-turn
rotation, RAM freeze chain) are parked behind pure-letter sentinels and
EXTENDED by one entry (never rolled) -- r1180/r1182/r1184/r1208/r1220 pit
family.  The section-7 block is taken VERBATIM from the post-W321-finalize
face at HEAD.  Everything else rides ONE single-pass map.

Usage: python results/_w322bmc_prereg_derive.py [--measure]
"""
import hashlib
import json
import re
import subprocess
import sys

SRC_REV = "d8136c2994"
SRC_PATH = "research/PERPETUAL_N1_W321_PREREG.md"
OUT = "research/PERPETUAL_N1_W322_PREREG.md"
SEAT_MSG = "MSG-20261025-0314-bmc-w322-seat"
SEAT_SHA = "d8136c2994"
FREE_RAM = "4.7"
MEASURE = "--measure" in sys.argv
PROJ = "\u6295\u5f71"          # projection
ANCHOR = "\u5b9e\u951a"        # measured anchor
FREEZE = "\u51bb\u7ed3\u7a97"   # freeze window

raw = subprocess.run(["git", "show", "%s:%s" % (SRC_REV, SRC_PATH)],
                     capture_output=True, check=True).stdout
src = raw.decode("utf-8")
print("SRC %s bytes=%d lines=%d sha16=%s" % (
    SRC_PATH, len(raw), src.count("\n"),
    hashlib.sha256(raw).hexdigest()[:16]))
assert src.count("\n") == 77, "src line count %d" % src.count("\n")

# ---------------------------------------------------------------- facts (machine-read)
res = json.load(open("results/perpetual_faces/n1_w321_results.json", encoding="utf-8"))
led = res["science_gates"]["ledger"]
assert led["total"] == 1130541 and led["prev_total"] == 1128341, "ledger anchor drift"
cum = res["null_pool_cumulative"]
assert cum["merged"]["n_values"] == 704120, "merged K drift"
assert abs(cum["merged"]["mu"] + 0.09287396054649776) < 1e-12
assert abs(cum["merged"]["sigma"] - 0.24518647125511978) < 1e-12
assert cum["se_mu_at_k704120"] == 0.000292
assert abs(cum["w321_only"]["mu"] + 0.106136) < 1e-9
assert abs(cum["w321_only"]["sigma"] - 0.24758882532356405) < 1e-12
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_704120"] == 1.2016 and kl["line_pre_w321"] == 1.2016
assert kl["line_delta_k_lift"] == 0.0
assert kl["n_eff_held_equal"] == 1128341
assert abs(res["families"]["A_random_engine_exit"]["full_sharpe_p95"] - 0.2864) < 1e-12
assert abs(res["families"]["A_random_engine_exit"]["full_sharpe_p99"] - 0.4601) < 1e-12
DELTA = abs(cum["w321_only"]["mu"] - cum["merged"]["mu"])
assert abs(DELTA - 0.013262039453502242) < 1e-12
seed = json.load(open("results/_w322bmc_20261025_probe_receipt.json", encoding="utf-8"))
assert seed["verdict"] == "ADMIT"
l1 = seed["legs"]["leg1"]
assert l1["A"] == [723701, 725700] and l1["B"] == [725701, 725900]
assert l1["hops_A"] == 1 and l1["hops_B"] == 1
l4 = seed["legs"]["leg4"]
assert l4["W323p_A_naive"] == "725_701..727_700"
assert l4["W323p_B_naive"] == "725_901..726_100"
assert seed["legs"]["leg0"]["owner_rows"] == 311
assert seed["legs"]["leg0"]["bmc_rows"] == 140
assert seed["ordinals"]["a_hop"] == 75 and seed["ordinals"]["above_own_a"] == 76
print("facts OK: ledger 1,130,541 / K 704,120 / W321-only mu -0.10613600 / p95 0.2864 / delta %.8f" % DELTA)

# ---------------------------------------------------------------- 0. prior-wave S7 block (verbatim from HEAD)
head = subprocess.run(["git", "show", "HEAD:%s" % SRC_PATH],
                      capture_output=True, check=True).stdout.decode("utf-8")
j7 = head.find("## \u00a77")
j8 = head.find("## \u00a78")
assert 0 < j7 < j8, "HEAD sec.7 block not found"
SEC7_NEW = head[j7:j8]
assert "W321-only" in SEC7_NEW and "1,130,541" in SEC7_NEW

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
    print("PARK %-8s hits=%d" % (label, len(ms)))
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
    old_tail = "\u2192W320 **0.000293**\u2192W321 " + PROJ + " 0.000293"
    assert old_tail in old, "se chain tail not the expected W321 projection"
    return old.replace(old_tail,
                       "\u2192W320 **0.000293**\u2192W321 **0.000292**\u2192W322 " + PROJ + " 0.000292")


def ab(old):
    assert "/W321=A/B" in old, "A/B chain tail not the expected W321"
    t = old.replace("/W321=A/B", "/W321/W322=A/B", 1)
    assert "/W322=A/B" in t, "A/B chain tail not extended"
    return t


def rot(old):
    assert "\u2192W321 bm-c own-turn rotation" in old, "own-turn tail not W321"
    return old.replace("\u2192W321 bm-c own-turn rotation",
                       "\u2192W321 bm-c\u2192W322 bm-c own-turn rotation", 1)


def ram(old):
    m = re.search(r"\u00b7\u672c\u7a97" + FREEZE + r" ~([\d.]+)G bm-c " + ANCHOR + "\uff09", old)
    assert m, "RAM chain tail not found"
    new = ("\u00b7W321 " + FREEZE + " ~" + m.group(1) + "G bm-c " + ANCHOR +
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
assert SEC8.count("W322+") == 1 and "lands_inside" in SEC8, "sec.8 template drift"
out = out[:i8] + "ZZSECS" + out[i8_end:]

# ---------------------------------------------------------------- 2. wave labels +1 (W>=304)
out = wave_bump(out)

# ---------------------------------------------------------------- 3. numeric / ordinal / artifact maps
NUM = [
    # --- ledger / pool anchors (single-pass; longest key wins)
    ("1,128,341", "1,130,541"),
    ("1,126,141", "1,128,341"),
    ("K701,920", "K704,120"),
    ("701,920", "704,120"),
    ("704,120", "706,320"),
    # --- merged / wave-only statistics
    ("0.09283239", "0.09287396"),
    ("0.24517796", "0.24518647"),
    ("0.10421232", "0.10613600"),
    ("0.01138", "0.01326"),
    # --- A family p95 anchor
    ("0.3096", "0.2864"),
    # --- K-lift pair (long key wins over the bare decimals)
    ("**1.2015**", "**1.2016**"),
    ("line_pre_w321", "line_pre_w322"),
    ("1.2015", "1.2016"),
    # --- wave / row / seed ordinals
    ("\u6c60\u7b2c 319 \u679a", "\u6c60\u7b2c 320 \u679a"),
    ("\u884c 310 \u6ce8\u518c\u5728\u518c", "\u884c 311 \u6ce8\u518c\u5728\u518c"),
    ("bmc rows 139+\u5019\u9009=\u7b2c 140 \u679a", "bmc rows 140+\u5019\u9009=\u7b2c 141 \u679a"),
    ("bmc_rows=139", "bmc_rows=140"),
    ("bmc live rows 139", "bmc live rows 140"),
    ("\u7b2c\u4e00\u767e\u4e09\u5341\u4e5d\u679a", "\u7b2c\u4e00\u767e\u56db\u5341\u679a"),
    ("\u5f15\u64ce\u7ebf\u7b2c 311 \u6ce2", "\u5f15\u64ce\u7ebf\u7b2c 312 \u6ce2"),
    ("\u6ce2\u53f7 319=", "\u6ce2\u53f7 320="),
    ("\u4e09\u767e\u4e00\u5341\u4e94\u9762", "\u4e09\u767e\u4e00\u5341\u516d\u9762"),
    ("CLEAN-AT-BIRTH 52nd gen", "CLEAN-AT-BIRTH 53rd gen"),
    # --- ordinal words (single-pass; NEVER chained)
    ("\u7b2c\u4e03\u5341\u56db\u6b21", "\u7b2c\u4e03\u5341\u4e94\u6b21"),
    ("\u7b2c\u4e03\u5341\u4e94\u6b21", "\u7b2c\u4e03\u5341\u516d\u6b21"),
    ("\u7b2c\u516d\u5341\u516b\u6ce2", "\u7b2c\u516d\u5341\u4e5d\u6ce2"),
    # --- runner / artifact names
    ("--wave 321", "--wave 322"),
    ("n1_w320", "n1_w321"),
    ("n1_w321", "n1_w322"),
    ("_w321bmc_20261025", "_w322bmc_20261025"),
    ("_w321bmc_", "_w322bmc_"),
    ("MSG-20261025-0205-bmc-w321-seat", SEAT_MSG),
    # --- commit shas (prereg / splice / finalize chain)
    ("be2e81ca4b", "88cc3f5684"),
    ("4f54c55538", "ac509891c2"),
    ("3455fa2aa4", SEAT_SHA),
    # --- explicit timeline phrases (longest first via sort)
    # NOTE (r1211 family, third instance): the wave token in these phrases is
    # already bumped by wave_bump, so the KEY must be written POST-bump (W321).
    ("r1220/r1221/r1222 W321 \u5168\u5468\u671f be2e81ca4b+4f54c55538+3455fa2aa4",
     "r1223/r1224/r1224 W321 \u5168\u5468\u671f 88cc3f5684+ac509891c2+d8136c2994"),
    ("r1222/r1222/r1222 W321 \u5168\u5468\u671f",
     "r1223/r1224/r1224 W321 \u5168\u5468\u671f"),
    ("bm-c r1221 \u4e94\u9762\u51bb\u7ed3 splice 4f54c55538 \u843d\u5730 01:2x",
     "bm-c r1224 \u4e94\u9762\u51bb\u7ed3 splice ac509891c2 \u843d\u5730 02:52"),
    ("prereg be2e81ca4b \u843d\u4e8e r1220 \u7a97",
     "prereg 88cc3f5684 \u843d\u4e8e r1223 \u7a97"),
    ("splice 4f54c55538 \u843d\u4e8e r1221 \u6267\u884c\u7a97 01:2x",
     "splice ac509891c2 \u843d\u4e8e r1224 \u6267\u884c\u7a97 02:52"),
    ("bm-c r1222 \u5e2d", "bm-c r1224 \u5e2d"),
    ("bm-c \u5faa\u73af\u73ed r1223 " + FREEZE + " 2026-10-25 02:2x",
     "bm-c \u5faa\u73af\u73ed r1225 " + FREEZE + " 2026-10-25 03:4x"),
    ("01:4x", "03:2x"),
    # --- window clock / round labels
    ("r1220", "r1222"),
    ("r1221", "r1223"),
    ("r1222", "r1224"),
    ("r1223", "r1225"),
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
    "- \u00a75.5 W323+ \u6295\u5f71\u627f\u63a5\u673a\u8bc1\uff1a\u672c\u7a97\u5e2d\u4f4d\u56de\u6267 leg4\uff08pre-W322 \u5b87\u5b99\uff09\u6295\u5f71 W323p A naive **725_701..727_700** clean\uff08hops=0\uff09\u3001"
    "B naive **725_901..726_100** clean\uff08hops=0\uff09\u4f46\u843d\u6295\u5f71 A \u7a97\u5185\uff08own-A reservation \u627f\u88ad\u9884\u671f\uff09\u2014\u2014**W323 \u51bb\u7ed3\u65b9\u5fc5\u987b\u5728 post-W322 \u5b87\u5b99 "
    "\u91cd live derive \u4e14\u5728 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97\uff08W141 \u5148\u4f8b\uff09\u00b7never transcribe r587**\u3002\n"
    "- \u672c\u7a97\u5e2d\u4f4d\u5b9e\u6d4b\u673a\u8bc1\uff1aA **723_701..725_700**\uff0875th \u8fde\u7eed A-hop\u00b7hops=1\u00b7naive \u8d77\u70b9 723_501 \u88ab\u6ce8\u518c W321 B \u5e26 723_501..723_700 \u62d2\u00b7base==\u6ce8\u518c W321 B \u5c3e 723_700+1\uff09\uff0f"
    "B **725_701..725_900**\uff0876th \u8fde\u7eed above-own-A\u00b7hops=1\u00b7own-A reservation cascade \u00b7base==\u672c\u6ce2 A \u5c3e 725_700+1\uff09\u2014\u2014"
    "`results/_w322bmc_20261025_probe_receipt.json` verdict ADMIT\u00b7relation_asserts 4/4\u00b7seed_admit_gate FREE x2\u00b7leg3 bands_clear=True\u3002\n"
    "- \u5b9d\u85cf\u4e0e\u65b9\u6cd5\u8bba\u6355\u83b7\u95ee\uff1a\u672c\u6ce2=nulls-deepening \u5e38\u6001\u52a0\u6df1\uff0c**\u65e0\u65b0\u65b9\u6cd5/\u65e0\u65b0\u5b9d\u85cf**\uff1bknowledge/METHODOLOGY_ASSETS.md \u4e0e "
    "TREASURE_REGISTRY.json \u5747\u4e0d\u8ffd\u52a0\u3002\n"
    "- \u8bda\u5b9e\u62ab\u9732\uff08\u672c\u6ce2 1 \u6761\u00b7\u5747\u4e3a prose \u9762\uff0c\u5224\u636e\u4e0e\u4ea7\u7269\u96f6\u5f71\u54cd\uff09\uff1a\n"
    "  \u2460 \u00a75 \u4e94\u9884\u952e\u82e5\u51fa\u73b0 prose \u504f\u5dee\uff08se_mu \u53d6 3 \u4f4d\u5c0f\u6570\uff09\uff0c\u4ee5\u673a\u8bfb\u503c\u4e3a\u51c6\u5e76\u62ab\u9732\u3001\u4e0d\u62b9\u5e73\u3002\n"
    "  \u2461 \u6cbf\u88ad\u7684\u4e24\u5904 prose \u6ede\u540e\u9762\u672c\u7a97\u4fee\u6b63\u4e0d\u6539\u9762\uff1a\u8868\u5c3e\u884c\u6807\u7b7e=W321\uff08splice ac509891c2 \u6ce8\u518c\u7684\u5c31\u662f\u884c 321\uff09\uff1b\u00a76 engine_owner \u884c\u6570=probe leg0 \u673a\u8bfb 140\u3002\n"
    "- \u5751\u5f8b\u6355\u83b7\uff08\u672c\u7a97\uff09\uff1a\u2460canon-clone \u751f\u6210\u5668\u7684\u7eaf\u6570\u5b57\u9762\uff08\u6ce8\u518c\u884c\u53f7\u524d\u7f00/\u5207\u53e3/setwave \u952e\u540e\u7f00\uff09\u76f4\u5199\u76ee\u6807\u6ce2\u53f7\u3001W token \u9762\u4fdd\u7559**\u4e0a\u4e00\u6ce2**\u5f62\u6001\u4ea4\u7ed9\u7ea7\u8054\u63a8\u8fdb\u4e00\u6b21\uff1b"
    "\u7d2f\u79ef\u94fe\uff08se_mu/A-B/own-turn/RAM\uff09\u4e00\u5f8b park+\u5ef6\u957f\u4e00\u6761\uff0c\u7981\u6eda\uff1b"
    "\u2461\u53ea\u5b58\u5728\u4e8e \u00a77/\u00a78 \u88ab park \u533a\u5757\u5185\u7684\u5b57\u9762\u91cf\uff08\u516d\u95e8\u5e8f\u6570/\u5e10\u672c\u4e09\u5143\u7c7b\uff09\u5728\u6620\u5c04\u8868\u91cc\u5c31\u662f\u96f6\u547d\u4e2d\u9677\u9631\uff0c\u7981\u5165\u6620\u5c04\uff1b"
    "\u2462\u5e26\u7740\u6ce2\u53f7\u7684\u65e5\u5386\u5f15\u7528\uff082026-10-08/10-10 CEO \u4ee4\u65f6\u523b 23:5x/23:1x\uff09\u4e0d\u5c5e\u74e6\u53d8\u9762\uff0c\u7981\u8fdb\u6620\u5c04\u3002\n"
    "- \u6536\u53e3\u7eaa\u5f8b\uff1afinalize \u53ea\u6d88\u8d39\u5728\u518c\u5206\u7247\uff08audit.finalize_only=true\uff09\uff0c\u672c\u6ce2\u96f6\u91cd\u70e7\u3001\u96f6\u53cc\u70e7\uff1bS6 \u94fe\u4e0e\u8f6e\u6536\u53e3\u540c\u7a97\u3002\n\n\n"
)
assert out.count("ZZSECS") == 1
out = out.replace("ZZSECS", SEC8_NEW)

# ---------------------------------------------------------------- 5b. post-fixes (live readings this window)
POST = [
    # live readings this window
    ("\u672c\u7a97 free RAM 3.4GB", "\u672c\u7a97 free RAM 4.7GB"),
    ("nvidia-smi \u5b9e\u8bfb util 2%\u00b7VRAM \u5360\u7528 2.6G/16G\uff08\u5e38\u9a7b\u9762\u5360\u7528\u00b7\u975e\u672c\u6ce2\uff09",
     "nvidia-smi \u5b9e\u8bfb util 1%\u00b7VRAM \u5360\u7528 2.0G/16G\uff08\u5e38\u9a7b\u9762\u5360\u7528\u00b7\u975e\u672c\u6ce2\uff09"),
]
for old, new in POST:
    n = out.count(old)
    assert n >= 1, "post-fix %r hits=%d" % (old[:40], n)
    out = out.replace(old, new)
    print("post-fix applied hits=%d" % n)

# ---------------------------------------------------------------- 6. asserts
assert out.count("\n") == 77, "line count changed: %d" % out.count("\n")
assert out.count("723_701..725_700") >= 2, "new A band missing"
assert out.count("725_701..725_900") >= 2, "new B band missing"
assert out.count("725_701..727_700") >= 1 and out.count("725_901..726_100") >= 1
assert out.count("W322") > 30 and out.count("W323") > 5
assert out.count("W302") == src.count("W302"), "W302 (cumulative) must not roll"
assert out.count("W303") == src.count("W303"), "W303 (cumulative) must not roll"
assert out.count("1,130,541") >= 3, "new ledger anchor missing"
assert out.count("ZQ") == 0
assert out.count("n1_w321") >= 4 and out.count("n1_w322") >= 1
assert out.count("n1_w320") == 0, "n1 double roll"
assert out.count(SEAT_SHA) >= 3
assert out.count(SEAT_MSG) >= 3
assert out.count("CLEAN-AT-BIRTH 53rd gen") == 1
assert out.count("r1225") >= 5, "round labels"
assert out.count("_w322bmc_20261025_probe_receipt.json") >= 1
assert out.count("\u7b2c 84 \u6b21") == 1, "sixgate ordinal is a sec.7 (prior-wave) face"
assert out.count("W321-only") >= 1  # sec.7 prior-wave block intact
assert out.count("ZZ") == 0, "sentinel leaked"

receipt = {"keys": counts, "band_tokens": nband,
           "bytes_src": len(raw), "bytes_out": len(out.encode("utf-8"))}
open("results/_w322bmc_derive_counts.json", "w", encoding="utf-8").write(
    json.dumps(receipt, ensure_ascii=False, indent=1))
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(out)
b = out.encode("utf-8")
print("WROTE %s bytes=%d lines=%d sha16=%s bands=%d keys=%d" % (
    OUT, len(b), out.count("\n"), hashlib.sha256(b).hexdigest()[:16], nband, len(NUM)))