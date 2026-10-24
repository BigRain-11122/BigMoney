# -*- coding: utf-8 -*-
"""W315 prereg derive (bm-c r1209).

Canon-clone of the W314 PRE-RUN face
(git 5172b1f636:research/PERPETUAL_N1_W314_PREREG.md, 28,621B / 75 newlines,
sha16 fb6ad33bcc858f2e) -> research/PERPETUAL_N1_W315_PREREG.md.

Cumulative-history chains (se_mu narrowing, A/B 1-hop wave list, own-turn
rotation list, RAM freeze chain) are parked behind pure-letter sentinels and
EXTENDED by one entry (never rolled) -- r1180/r1182/r1184 pit family.
The section-7 backfill block is taken VERBATIM from the post-W314-finalize face
at HEAD (it is the prior-wave evidence block, inserted after every map so it
cannot be rolled).  Everything else rides ONE single-pass map.

Usage: python results/_w315bmc_prereg_derive.py [--measure|--diag]
"""
import hashlib
import json
import re
import subprocess
import sys

SRC_REV = "5172b1f636"
SRC_PATH = "research/PERPETUAL_N1_W314_PREREG.md"
OUT = "research/PERPETUAL_N1_W315_PREREG.md"
EXPECT_SHA16 = "fb6ad33bcc858f2e"
EXPECT_BYTES = 28621
SEAT_MSG = "MSG-20261024-2045-bmc-w315-seat"
SEAT_SHA = "7f5421ec6f"
FREE_RAM = "0.8"
MEASURE = "--measure" in sys.argv

raw = subprocess.run(["git", "show", "%s:%s" % (SRC_REV, SRC_PATH)],
                     capture_output=True, check=True).stdout
assert len(raw) == EXPECT_BYTES, "src bytes %d != %d" % (len(raw), EXPECT_BYTES)
assert hashlib.sha256(raw).hexdigest()[:16] == EXPECT_SHA16, "src sha16 mismatch"
src = raw.decode("utf-8")
assert src.count("\n") == 75, "src line count %d" % src.count("\n")

# ---------------------------------------------------------------- facts (machine-read)
res = json.load(open("results/perpetual_faces/n1_w314_results.json", encoding="utf-8"))
led = res["science_gates"]["ledger"]
assert led["total"] == 1115141 and led["prev_total"] == 1112941, "ledger anchor drift"
cum = res["null_pool_cumulative"]
assert cum["merged"]["n_values"] == 688720, "merged K drift"
assert abs(cum["merged"]["mu"] + 0.0928319235683587) < 1e-12
assert abs(cum["merged"]["sigma"] - 0.2451606752073563) < 1e-12
assert cum["se_mu_at_k688720"] == 0.000295
assert abs(cum["w314_only"]["mu"] + 0.09414704545454546) < 1e-12
assert abs(cum["w314_only"]["sigma"] - 0.24511574175891745) < 1e-12
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_688720"] == 1.2008 and kl["line_pre_w314"] == 1.2008
assert kl["line_delta_k_lift"] == 0.0
assert kl["n_eff_held_equal"] == 1112941
assert abs(res["families"]["A_random_engine_exit"]["full_sharpe_p95"] - 0.3246) < 1e-12
assert abs(res["families"]["A_random_engine_exit"]["full_sharpe_p99"] - 0.4575) < 1e-12
seed = json.load(open("results/_w315bmc_20261024_probe_receipt.json", encoding="utf-8"))
assert seed["verdict"] == "ADMIT"
l1 = seed["legs"]["leg1"]
assert l1["A"] == [708301, 710300] and l1["B"] == [710301, 710500]
assert l1["hops_A"] == 1 and l1["hops_B"] == 1
l4 = seed["legs"]["leg4"]
assert l4["W316p_A_naive"] == "710_301..712_300"
assert l4["W316p_B_naive"] == "710_501..710_700"
assert seed["legs"]["leg0"]["owner_rows"] == 304
assert seed["legs"]["leg0"]["bmc_rows"] == 133
assert seed["ordinals"]["a_hop"] == 68 and seed["ordinals"]["above_own_a"] == 69
print("facts OK: ledger 1,115,141 / K 688,720 / W314-only mu -0.09414705 / p95 0.3246")

# ---------------------------------------------------------------- 0. prior-wave S7 block (verbatim from HEAD)
head = subprocess.run(["git", "show", "HEAD:%s" % SRC_PATH],
                      capture_output=True, check=True).stdout.decode("utf-8")
j7 = head.find("## \u00a77")
j8 = head.find("## \u00a78")
assert 0 < j7 < j8, "HEAD sec.7 block not found"
SEC7_NEW = head[j7:j8]
assert "W314-only" in SEC7_NEW and "1,115,141" in SEC7_NEW

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


def wave_bump(text, floor=303):
    return re.sub(r"W(\d{3})", lambda m: "W%03d" % (int(m.group(1)) + 1)
                  if int(m.group(1)) >= floor else m.group(0), text)


PROJ = "\u6295\u5f71"          # 投影


def se(old):
    old_tail = "\u2192W314 " + PROJ + " 0.000295"
    assert old_tail in old, "se chain tail not the expected W314 projection"
    assert "0.000296" in old
    return old.replace(old_tail,
                       "\u2192W314 **0.000295**\u2192W315 " + PROJ + " 0.000294")


def ab(old):
    t = old.replace("/W310/W311/W312/W313/W314=A/B", "/W310/W311/W312/W313/W314/W315=A/B", 1)
    assert "/W310/W311/W312/W313/W314/W315=A/B" in t, "A/B chain tail not expected /W310..W314=A/B"
    o_ord = "\u7b2c\u516d\u5341\u4e00\u6ce2"   # 61st wave
    n_ord = "\u7b2c\u516d\u5341\u4e8c\u6ce2"   # 62nd wave
    assert o_ord in t, "A/B chain ordinal not the expected 61st"
    t = t.replace(o_ord, n_ord)
    return t


def rot(old):
    t = old.replace("\u2192W314 bm-c own-turn rotation",
                    "\u2192W314 bm-c\u2192W315 bm-c own-turn rotation", 1)
    assert "W315 bm-c own-turn rotation" in t, "own-turn chain tail not expected W314"
    return t


def ram(old):
    m = re.search(r"\u00b7W312 \u51bb\u7ed3\u7a97 ~([\d.]+)G bm-c \u5b9e\u951a"
                  r"\u00b7W313 \u51bb\u7ed3\u7a97 ~([\d.]+)G bm-c \u5b9e\u951a"
                  r"\u00b7\u672c\u7a97\u51bb\u7ed3\u7a97 ~([\d.]+)G bm-c \u5b9e\u951a\uff09", old)
    assert m, "RAM chain tail not found"
    word = "\u5b9e\u951a"   # 实锚
    new_tail = ("\u00b7W312 \u51bb\u7ed3\u7a97 ~" + m.group(1) + "G bm-c " + word +
                "\u00b7W313 \u51bb\u7ed3\u7a97 ~" + m.group(2) + "G bm-c " + word +
                "\u00b7W314 \u51bb\u7ed3\u7a97 ~" + m.group(3) + "G bm-c " + word +
                "\u00b7\u672c\u7a97\u51bb\u7ed3\u7a97 ~" + FREE_RAM + "G bm-c " + word + "\uff09")
    return old[:m.start()] + new_tail + old[m.end():]


park(r"W277 \*\*0\.000314\*\*[^\n]*?\u6295\u5f71 0\.000295", se, "SECH")
park(r"W252/W253[^\n]*?\u7b2c\u516d\u5341\u4e00\u6ce2", ab, "ABCHAIN")
park(r"W288 bm-c[\s\S]{0,900}?own-turn rotation", rot, "ROTCH")
park(r"W206/W211[^\n]*?\u5b9e\u951a\uff09", ram, "RAMCH")

# S7 block (prior-wave finalize evidence): parked, re-inserted verbatim after all maps
i7 = out.find("## \u00a77")
assert i7 > 0, "sec.7 header not found"
i7_end = out.find("## \u00a78", i7)
assert i7_end > i7, "sec.8 header not found after sec.7"
out = out[:i7] + "ZZSEC7\n" + out[i7_end:]

# S8 block: rebuilt explicitly (finalize-time backfill face; r1184 self-reference family)
i8 = out.find("## \u00a78")
assert i8 > 0, "sec.8 header not found"
i8_end = out.find("- **\u8dd1\u524d\u51bb\u7ed3=\u672c\u4ef6 commit**", i8)
assert i8_end > i8, "sec.8 tail marker not found"
SEC8 = out[i8:i8_end]
assert SEC8.count("706_101..708_100") == 1 and SEC8.count("708_101..708_300") == 1
out = out[:i8] + "ZZSECS" + out[i8_end:]

# ---------------------------------------------------------------- 2. wave labels +1 (W>=303)
out = wave_bump(out)

# ---------------------------------------------------------------- 3. numeric / ordinal / artifact maps
NUM = [
    # --- ledger / pool anchors (single-pass)
    ("1,112,941", "1,115,141"),
    ("686,520", "688,720"),
    ("688,720", "690,920"),
    # --- merged / wave-only statistics
    ("\u22120.09282771", "\u22120.09283192"),
    ("0.24516099", "0.24516068"),
    ("\u22120.09864764", "\u22120.09414705"),
    ("0.0074", "0.0013"),
    # --- A family p95 anchor
    ("0.3071", "0.3246"),
    # --- K-lift n_eff anchor + label
    ("1,108,541", "1,112,941"),
    ("line_pre_w314", "line_pre_w315"),
    # --- wave / row / seed ordinals
    ("\u6c60\u7b2c 312 \u679a", "\u6c60\u7b2c 313 \u679a"),
    ("\u884c 303 \u6ce8\u518c\u5728\u518c", "\u884c 304 \u6ce8\u518c\u5728\u518c"),
    ("bmc rows 132+\u5019\u9009=\u7b2c 133 \u679a", "bmc rows 133+\u5019\u9009=\u7b2c 134 \u679a"),
    ("bmc_rows=132", "bmc_rows=133"),
    ("bmc live rows 132", "bmc live rows 133"),
    ("\u7b2c\u4e00\u767e\u4e09\u5341\u4e8c\u679a", "\u7b2c\u4e00\u767e\u4e09\u5341\u4e09\u679a"),
    ("\u5f15\u64ce\u7ebf\u7b2c 304 \u6ce2", "\u5f15\u64ce\u7ebf\u7b2c 305 \u6ce2"),
    ("\u6ce2\u53f7 312=", "\u6ce2\u53f7 313="),
    ("\u4e09\u767e\u96f6\u516b\u9762", "\u4e09\u767e\u96f6\u4e5d\u9762"),
    ("CLEAN-AT-BIRTH 45th gen", "CLEAN-AT-BIRTH 46th gen"),
    # --- ordinal words (single-pass; NEVER chained)
    ("\u7b2c\u516d\u5341\u4e03\u6b21", "\u7b2c\u516d\u5341\u516b\u6b21"),
    ("\u7b2c\u516d\u5341\u516b\u6b21", "\u7b2c\u516d\u5341\u4e5d\u6b21"),
    # --- runner / artifact names
    ("--wave 314", "--wave 315"),
    ("n1_w313", "n1_w314"),
    ("n1_w314", "n1_w315"),
    ("_w313bmc_", "_w314bmc_"),
    ("_w314bmc_", "_w315bmc_"),
    ("MSG-20261024-1915-bmc-w314-seat", SEAT_MSG),
    # --- commit shas (prereg / splice / seat chain)
    ("c110bf216e", "5172b1f636"),
    ("c44743a1ea", "249e2abf9e"),
    ("d683bad881", SEAT_SHA),
    # --- window clock / round labels (clause-level, single-pass)
    ("bm-c r1205 \u4e94\u9762\u51bb\u7ed3 splice", "bm-c r1208 \u4e94\u9762\u51bb\u7ed3 splice"),
    ("\u843d\u5730 18:1x\u00b7selftest", "\u843d\u5730 19:3x\u00b7selftest"),
    ("r1204/r1205/r1206", "r1207/r1207/r1208"),
    ("bm-c r1206 \u7a97 19:0x", "bm-c r1208 \u7a97 20:2x"),
    ("\u843d\u4e8e r1205 \u7a97", "\u843d\u4e8e r1207 \u7a97"),
    ("\u843d\u4e8e r1205 \u6267\u884c\u7a97 18:1x", "\u843d\u4e8e r1208 \u6267\u884c\u7a97 19:3x"),
    ("2026-10-24 19:1x", "2026-10-24 20:4x"),
    ("r1207", "r1209"),
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
    "- \u00a75.5 W316+ \u6295\u5f71\u627f\u63a5\u673a\u8bc1\uff1a\u672c\u7a97\u5e2d\u4f4d\u56de\u6267 leg4\uff08pre-W315 \u5b87\u5b99\uff09"
    "\u6295\u5f71 W316p A naive **710_301..712_300** clean\uff08hops=0\uff09\u3001B naive **710_501..710_700** clean "
    "\u4f46\u843d\u6295\u5f71 A \u7a97\u5185\uff08own-A reservation \u627f\u88ad\u9884\u671f\uff09\u2014\u2014**W316 \u51bb\u7ed3\u65b9\u5fc5\u987b\u5728 "
    "post-W315 \u5b87\u5b99\u91cd live derive \u4e14 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97\uff08W141 \u5148\u4f8b\uff09\u00b7never transcribe r587**\u3002\n"
    "- \u672c\u7a97\u5e2d\u4f4d\u5b9e\u6d4b\u673a\u8bc1\uff1aA **708_301..710_300**\uff0868th \u8fde\u7eed A-hop\u00b7hops=1\u00b7base==\u6ce8\u518c W314 B \u5c3e 708_300+1\uff09\uff0f"
    "B **710_301..710_500**\uff0869th \u8fde\u7eed above-own-A\u00b7hops=1\u00b7base==\u672c\u6ce2 A \u5c3e 710_300+1\uff09\u2014\u2014"
    "`results/_w315bmc_20261024_probe_receipt.json` verdict ADMIT\u00b7relation_asserts 4/4\u00b7seed_admit_gate FREE x2\u00b7leg3 bands_clear=true\u3002\n"
    "- \u5b9d\u85cf\u4e0e\u65b9\u6cd5\u8bba\u6355\u83b7\u95ee\uff1a\u672c\u6ce2=nulls-deepening \u5e38\u6001\u52a0\u6df1\uff0c**\u65e0\u65b0\u65b9\u6cd5/\u65e0\u65b0\u5b9d\u85cf**\uff0c"
    "knowledge/METHODOLOGY_ASSETS.md \u4e0e TREASURE_REGISTRY.md \u5747\u4e0d\u8ffd\u52a0\u3002\n"
    "- \u8bda\u5b9e\u62ab\u9732\uff1a\u00a75 \u4e94\u9884\u952e\u82e5\u51fa\u73b0 prose \u504f\u5dee\uff08se_mu \u53d6 3 \u4f4d\u5c0f\u6570\uff09\uff0c\u4ee5\u673a\u8bfb\u503c\u4e3a\u51c6\u5e76\u62ab\u9732\u3001"
    "\u4e0d\u62b9\u5e73\uff1bmu/sigma/K-lift \u4e00\u5f8b\u6309\u51bb\u7ed3\u5e26\u6821\u9a8c\u3002\n"
    "- \u5751\u5f8b\u6355\u83b7\uff1apost-W315 finalize \u540c\u7a97\u56de\u586b\uff08\u672c\u6bb5\u5c5e finalize \u56de\u586b\u9762\uff0c\u51bb\u7ed3\u65f6\u4e3a\u524d\u6ce2\u6cbf\u7528\u6587\u672c\uff09\uff1b"
    "\u672c\u7a97\u51bb\u7ed3\u6cbf\u7528 r1208 \u5224\u4f8b\uff1acanon-clone \u751f\u6210\u5668\u7684\u7eaf\u6570\u5b57\u9762\uff08\u6ce8\u518c\u884c\u53f7\u524d\u7f00/\u5207\u53e3/setwave \u952e\u540e\u7f00\uff09"
    "\u76f4\u5199\u76ee\u6807\u6ce2\u53f7\u3001W token \u9762\u4fdd\u7559**\u4e0a\u4e00\u6ce2**\u5f62\u6001\u4ea4\u7ed9\u7ea7\u8054\u63a8\u8fdb\u4e00\u6b21\u3002\n"
    "- \u6536\u53e3\u7eaa\u5f8b\uff1afinalize \u53ea\u6d88\u8d39\u5728\u518c\u5206\u7247\uff08audit.finalize_only=true\uff09\uff0c\u672c\u6ce2\u96f6\u91cd\u70e7\u3001\u96f6\u53cc\u70e7\uff1b"
    "S6 \u94fe\u4e0e\u8f6e\u6536\u53e3\u540c\u7a97\u3002\n\n\n"
)
assert out.count("ZZSECS") == 1
out = out.replace("ZZSECS", SEC8_NEW)

# ---------------------------------------------------------------- 5b. post-fixes
POST = [
    ("finalize \u5df2\u843d\u5730 17:4x\uff09", "finalize \u5df2\u843d\u5730 20:2x\uff09"),
    ("\u952e\u00b717:4x finalize one-pass", "\u952e\u00b720:2x finalize one-pass"),
    ("\u672c\u7a97 free RAM 1.7GB", "\u672c\u7a97 free RAM " + FREE_RAM + "GB"),
    ("GPU=gen-only \u8f66\u9053 busy\uff08\u5916\u90e8 MV i2v \u8f66\u9053\u5728\u70e7\u00b7util 100% \u5b9e\u8bfb\u00b7\u975e\u672c\u6ce2\u5360\u7528\uff1b"
     "nvidia-smi \u5b9e\u8bfb 15.6G VRAM \u5360\u7528\u00b7GPU \u5728\u70e7\u4ef6\u5c5e\u5916\u90e8 MV \u8f66\u9053\u3014util 100% \u5b9e\u8bfb\u00b7\u975e\u672c\u6ce2\u5360\u7528\u00b7CPU "
     "\u8f66\u9053\u72ec\u7acb\u3015\uff09",
     "GPU=gen-only \u8f66\u9053 idle\uff08nvidia-smi \u5b9e\u8bfb util 3%\u00b7VRAM \u5360\u7528 2.2G/16G\u00b7\u975e\u672c\u6ce2\u5360\u7528\u00b7CPU \u8f66\u9053\u72ec\u7acb\uff09"),
]
for old, new in POST:
    n = out.count(old)
    assert n >= 1, "post-fix %r hits=%d" % (old[:40], n)
    out = out.replace(old, new)
    print("post-fix applied hits=%d" % n)

# ---------------------------------------------------------------- 6. asserts
if "--diag" in sys.argv:
    for tok in ("708_300", "708_301", "710_300", "710_301", "710_500", "710_501",
                "710_100", "710_101", "712_300", "710_700"):
        print("DIAG", tok, out.count(tok))
    sys.exit(0)

assert out.count("\n") == 75, "line count changed: %d" % out.count("\n")
assert out.count("708_301..710_300") >= 2, "new A band missing"
assert out.count("710_301..710_500") >= 2, "new B band missing"
assert out.count("708_101..710_100") >= 1, "naive A continuation band missing"
assert out.count("710_501..710_700") >= 1, "W316p B naive band missing"
assert out.count("710_301..712_300") >= 1, "W316p A naive band missing"
assert out.count("W315") > 30 and out.count("W316") > 5
assert out.count("W301") == src.count("W301"), "W301 (cumulative) must not roll"
assert out.count("W302") == src.count("W302"), "W302 (cumulative) must not roll"
assert out.count("W303") == src.count("W303"), "W303 (cumulative) must not roll"
assert out.count("1,115,141") >= 3, "new ledger anchor missing"
assert out.count("688,720") >= src.count("686,520") - 1, "prior-K roll mismatch"
assert out.count("line_pre_w315") >= 1 and out.count("line_pre_w314") == 1  # sec.7 prior block
assert out.count("ZZ") == 0, "sentinel leaked"
assert out.count("n1_w314") >= 4 and out.count("n1_w315") >= 1
assert out.count("n1_w313") == 0, "n1 double roll"
assert out.count(SEAT_SHA) >= 3
assert out.count(SEAT_MSG) >= 3
assert out.count("CLEAN-AT-BIRTH 46th gen") == 1
assert out.count("r1209") >= 8, "round labels"
assert "706,101..708,100" not in out, "stale comma-form band leaked"
assert out.count("_w315bmc_20261024_probe_receipt.json") >= 2
assert "\u7b2c 77 \u6b21" in out, "sixgate ordinal missing"
assert out.count("W314-only") >= 1  # sec.7 prior-wave block intact

receipt = {"keys": counts, "band_tokens": nband,
           "bytes_src": len(raw), "bytes_out": len(out.encode("utf-8"))}
open("results/_w315bmc_derive_counts.json", "w", encoding="utf-8").write(
    json.dumps(receipt, ensure_ascii=False, indent=1))
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(out)
b = out.encode("utf-8")
print("WROTE %s bytes=%d lines=%d sha16=%s bands=%d keys=%d" % (
    OUT, len(b), out.count("\n"), hashlib.sha256(b).hexdigest()[:16], nband, len(NUM)))