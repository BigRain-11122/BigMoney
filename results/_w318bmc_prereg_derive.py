# -*- coding: utf-8 -*-
"""W318 prereg derive (bm-c r1216).

Canon-clone of the W317 POST-RUN face
(git 231c6f902f:research/PERPETUAL_N1_W317_PREREG.md, 29,002B / 75 newlines,
sha16 8c22d023eb2f2668) -> research/PERPETUAL_N1_W318_PREREG.md.

Cumulative-history chains (se_mu narrowing, A/B 1-hop wave list, own-turn
rotation list, RAM freeze chain) are parked behind pure-letter sentinels and
EXTENDED by one entry (never rolled) -- r1180/r1182/r1184/r1208 pit family.
The section-7 block is taken VERBATIM from the post-W317-finalize face at HEAD.
Everything else rides ONE single-pass map.

Usage: python results/_w318bmc_prereg_derive.py [--measure|--diag]
"""
import hashlib
import json
import re
import subprocess
import sys

SRC_REV = "231c6f902f"
SRC_PATH = "research/PERPETUAL_N1_W317_PREREG.md"
OUT = "research/PERPETUAL_N1_W318_PREREG.md"
EXPECT_SHA16 = "8c22d023eb2f2668"
EXPECT_BYTES = 29002
SEAT_MSG = "MSG-20261024-2259-bmc-w318-seat"
SEAT_SHA = "a2ba09e18a"
FREE_RAM = "3.8"
MEASURE = "--measure" in sys.argv

raw = subprocess.run(["git", "show", "%s:%s" % (SRC_REV, SRC_PATH)],
                     capture_output=True, check=True).stdout
assert len(raw) == EXPECT_BYTES, "src bytes %d != %d" % (len(raw), EXPECT_BYTES)
assert hashlib.sha256(raw).hexdigest()[:16] == EXPECT_SHA16, "src sha16 mismatch"
src = raw.decode("utf-8")
assert src.count("\n") == 75, "src line count %d" % src.count("\n")

# ---------------------------------------------------------------- facts (machine-read)
res = json.load(open("results/perpetual_faces/n1_w317_results.json", encoding="utf-8"))
led = res["science_gates"]["ledger"]
assert led["total"] == 1121741 and led["prev_total"] == 1119541, "ledger anchor drift"
cum = res["null_pool_cumulative"]
assert cum["merged"]["n_values"] == 695320, "merged K drift"
assert abs(cum["merged"]["mu"] + 0.0928243713685785) < 1e-12
assert abs(cum["merged"]["sigma"] - 0.24516846767474942) < 1e-12
assert cum["se_mu_at_k695320"] == 0.000294
assert abs(cum["w317_only"]["mu"] + 0.0994759090909091) < 1e-12
assert abs(cum["w317_only"]["sigma"] - 0.24644184248926793) < 1e-12
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_695320"] == 1.2012 and kl["line_pre_w317"] == 1.2012
assert kl["line_delta_k_lift"] == 0.0
assert kl["n_eff_held_equal"] == 1119541
assert abs(res["families"]["A_random_engine_exit"]["full_sharpe_p95"] - 0.3158) < 1e-12
assert abs(res["families"]["A_random_engine_exit"]["full_sharpe_p99"] - 0.4508) < 1e-12
seed = json.load(open("results/_w318bmc_20261024_probe_receipt.json", encoding="utf-8"))
assert seed["verdict"] == "ADMIT"
l1 = seed["legs"]["leg1"]
assert l1["A"] == [714901, 716900] and l1["B"] == [716901, 717100]
assert l1["hops_A"] == 1 and l1["hops_B"] == 1
l4 = seed["legs"]["leg4"]
assert l4["W319p_A_naive"] == "716_901..718_900"
assert l4["W319p_B_naive"] == "717_101..717_300"
assert seed["legs"]["leg0"]["owner_rows"] == 307
assert seed["legs"]["leg0"]["bmc_rows"] == 136
assert seed["ordinals"]["a_hop"] == 71 and seed["ordinals"]["above_own_a"] == 72
print("facts OK: ledger 1,121,741 / K 695,320 / W317-only mu -0.09947591 / p95 0.3158")

# ---------------------------------------------------------------- 0. prior-wave S7 block (verbatim from HEAD)
head = subprocess.run(["git", "show", "HEAD:%s" % SRC_PATH],
                      capture_output=True, check=True).stdout.decode("utf-8")
j7 = head.find("## \u00a77")
j8 = head.find("## \u00a78")
assert 0 < j7 < j8, "HEAD sec.7 block not found"
SEC7_NEW = head[j7:j8]
assert "W317-only" in SEC7_NEW and "1,121,741" in SEC7_NEW

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


PROJ = "\u6295\u5f71"          # 投影
ANCHOR = "\u5b9e\u951a"        # 实锚
FREEZE = "\u51bb\u7ed3\u7a97"   # 冻结窗


def se(old):
    old_tail = "\u2192W317 " + PROJ + " 0.000293"
    assert old_tail in old, "se chain tail not the expected W317 projection"
    assert "0.000293" in old
    return old.replace(old_tail,
                       "\u2192W317 **0.000294**\u2192W318 " + PROJ + " 0.000293")


def ab(old):
    # only the cumulative wave list is parked; the 62nd-wave ordinal stays in
    # the body and rides the NUM map (otherwise the whole line -- timeline
    # clause included -- would be hidden inside this sentinel, r1211 finding)
    t = old.replace("/W313/W314/W315/W316/W317=A/B", "/W313/W314/W315/W316/W317/W318=A/B", 1)
    assert "W318=A/B" in t, "A/B chain tail not expected /W313..W317=A/B"
    return t


def rot(old):
    t = old.replace("\u2192W317 bm-c own-turn rotation",
                    "\u2192W317 bm-c\u2192W318 bm-c own-turn rotation", 1)
    assert "W318 bm-c own-turn rotation" in t, "own-turn chain tail not expected W317"
    return t


def ram(old):
    m = re.search(r"\u00b7W315 " + FREEZE + r" ~([\d.]+)G bm-c " + ANCHOR +
                  r"\u00b7W316 " + FREEZE + r" ~([\d.]+)G bm-c " + ANCHOR +
                  r"\u00b7\u672c\u7a97" + FREEZE + r" ~([\d.]+)G bm-c " + ANCHOR + "\uff09", old)
    assert m, "RAM chain tail not found"
    new_tail = ("\u00b7W315 " + FREEZE + " ~" + m.group(1) + "G bm-c " + ANCHOR +
                "\u00b7W316 " + FREEZE + " ~" + m.group(2) + "G bm-c " + ANCHOR +
                "\u00b7W317 " + FREEZE + " ~" + m.group(3) + "G bm-c " + ANCHOR +
                "\u00b7\u672c\u7a97" + FREEZE + " ~" + FREE_RAM + "G bm-c " + ANCHOR + "\uff09")
    return old[:m.start()] + new_tail + old[m.end():]


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
assert SEC8.count("W318+") == 1 and "lands_inside=True" in SEC8, "sec.8 template drift"
out = out[:i8] + "ZZSECS" + out[i8_end:]

# ---------------------------------------------------------------- 2. wave labels +1 (W>=304)
out = wave_bump(out)

# ---------------------------------------------------------------- 3. numeric / ordinal / artifact maps
NUM = [
    # --- ledger / pool anchors (single-pass)
    ("1,119,541", "1,121,741"),
    ("1,117,341", "1,119,541"),
    ("K693,120", "K695,320"),
    ("693,120", "695,320"),
    ("695,320", "697,520"),
    # --- merged / wave-only statistics
    ("−0.09280326", "−0.09282437"),
    ("0.24516431", "0.24516847"),
    ("−0.08997064", "−0.09947591"),
    ("0.0028", "0.0067"),
    # --- A family p95 anchor
    ("0.3227", "0.3158"),
    # --- K-lift pair (long key wins over the bare decimals)
    ("**1.2011**·line_pre_w317 1.2011", "**1.2012**·line_pre_w318 1.2012"),
    ("line_pre_w317", "line_pre_w318"),
    # --- wave / row / seed ordinals
    ("池第 315 枚", "池第 316 枚"),
    ("行 306 注册在册", "行 307 注册在册"),
    ("bmc rows 135+候选=第 136 枚", "bmc rows 136+候选=第 137 枚"),
    ("bmc_rows=135", "bmc_rows=136"),
    ("bmc live rows 135", "bmc live rows 136"),
    ("第一百三十五枚", "第一百三十六枚"),
    ("引擎线第 307 波", "引擎线第 308 波"),
    ("波号 315=", "波号 316="),
    ("三百一十一面", "三百一十二面"),
    ("CLEAN-AT-BIRTH 48th gen", "CLEAN-AT-BIRTH 49th gen"),
    # --- ordinal words (single-pass; NEVER chained)
    ("第七十次", "第七十一次"),
    ("第七十一次", "第七十二次"),
    ("第六十四波", "第六十五波"),
    # --- runner / artifact names
    ("--wave 317", "--wave 318"),
    ("n1_w316", "n1_w317"),
    ("n1_w317", "n1_w318"),
    ("_w317bmc_", "_w318bmc_"),
    ("MSG-20261024-2215-bmc-w317-seat", SEAT_MSG),
    # --- commit shas (prereg / splice / seat chain)
    ("24d7917916", "06002d41aa"),
    ("dfeb4f3d21", "5d6d26634f"),
    ("db6d35c413", SEAT_SHA),
    # --- window clock / round labels (long keys first via sort)
    ("bm-c r1212 五面冻结 splice dfeb4f3d21 落地 21:5x",
     "bm-c r1214 五面冻结 splice 5d6d26634f 落地 22:4x"),
    ("bm-c r1213 窗 22:1x", "bm-c r1215 窗 23:0x"),
    ("r1211/r1212/r1213 W317", "r1214/r1214/r1215 W317"),
    ("prereg 24d7917916 落于 r1211 窗·splice dfeb4f3d21 落于 r1212 执行窗 21:5x",
     "prereg 06002d41aa 落于 r1214 窗·splice 5d6d26634f 落于 r1214 执行窗 22:4x"),
    ("estate chain r1211/r1212/r1213", "estate chain r1214/r1214/r1215"),
    ("席位 r1210 窗+prereg r1211 窗落地", "席位 r1215 窗+prereg r1216 窗落地"),
    ("bm-c r1214 席位", "bm-c r1215 席位"),
    ("r1214 席位窗实跑", "r1215 席位窗实跑"),
    ("bm-c 循环班 r1214 " + FREEZE + " 2026-10-24 22:4x",
     "bm-c 循环班 r1216 " + FREEZE + " 2026-10-24 23:1x"),
    ("r1214", "r1216"),
    ("r1213", "r1215"),
    ("r1211", "r1214"),
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
    "## §8 批后复盘。【finalize 同窗回填】\n"
    "- §5.5 W319+ 投影承接机证：本窗席位回执 leg4（pre-W318 宇宙）投影 W319p A naive **716_901..718_900** clean（hops=0）、"
    "B naive **717_101..717_300** clean（hops=0）但落投影 A 窗内（own-A reservation 承袭预期）——**W319 冻结方必须在 "
    "post-W318 宇宙重 live derive 且在 derive B 时预留本波 A 窗（W141 先例）·never transcribe r587**。\n"
    "- 本窗席位实测机证：A **714_901..716_900**（71st 连续 A-hop·hops=1·base==注册 W317 B 尾 716_900+1）／"
    "B **716_901..717_100**（72nd 连续 above-own-A·hops=1·base==本波 A 尾 716_900+1）——"
    "`results/_w318bmc_20261024_probe_receipt.json` verdict ADMIT·relation_asserts 4/4·seed_admit_gate FREE x2·leg3 bands_clear=True。\n"
    "- 宝藏与方法论捕获问：本波=nulls-deepening 常态加深，**无新方法/无新宝藏**，knowledge/METHODOLOGY_ASSETS.md 与 "
    "TREASURE_REGISTRY.md 均不追加。\n"
    "- 诚实披露：§5 五预键若出现 prose 偏差（se_mu 取 3 位小数），以机读值为准并披露、不抹平；mu/sigma/K-lift 一律按冻结带校验。\n"
    "- 坑律捕获：post-W317 finalize 同窗回填（本段属 finalize 回填面，冻结时为前波沿用文本）；本窗冻结沿用 r1208 判例："
    "canon-clone 生成器的纯数字面（注册行号前缀/切口/setwave 键后缀）直写目标波号、W token 面保留**上一波**形态交给级联推进一次。\n"
    "- 收口纪律：finalize 只消费在册分片（audit.finalize_only=true），本波零重烧、零双烧；S6 链与轮收口同窗。\n\n\n"
)
assert out.count("ZZSECS") == 1
out = out.replace("ZZSECS", SEC8_NEW)

# ---------------------------------------------------------------- 5b. post-fixes
POST = [
    ("finalize 已落地 22:1x）", "finalize 已落地 23:0x）"),
    ("键·22:1x finalize one-pass", "键·23:0x finalize one-pass"),
    ("本窗 free RAM 3.7GB", "本窗 free RAM " + FREE_RAM + "GB"),
    ("GPU=gen-only 车道 idle（nvidia-smi 实读 util 3%·VRAM 占用 2.3G/16G·非本波占用·CPU 车道独立）",
     "GPU=gen-only 车道 idle（nvidia-smi 实读 util 8%·VRAM 占用 3.2G/16G·非本波占用·CPU 车道独立）"),
]
for old, new in POST:
    n = out.count(old)
    assert n >= 1, "post-fix %r hits=%d" % (old[:40], n)
    out = out.replace(old, new)
    print("post-fix applied hits=%d" % n)

# ---------------------------------------------------------------- 6. asserts
if "--diag" in sys.argv:
    for tok in ("714_500", "714_700", "714_701", "716_700", "716_701", "716_900",
                "716_500", "716_901", "718_700", "717_100"):
        print("DIAG", tok, out.count(tok))
    sys.exit(0)

assert out.count("\n") == 75, "line count changed: %d" % out.count("\n")
assert out.count("714_901..716_900") >= 2, "new A band missing"
assert out.count("716_901..717_100") >= 2, "new B band missing"
assert out.count("714_701..716_700") >= 1, "naive A continuation band missing"
assert out.count("717_101..717_300") >= 1, "W319p B naive band missing"
assert out.count("716_901..718_900") >= 1, "W319p A naive band missing"
assert out.count("W318") > 30 and out.count("W319") > 5
assert out.count("W302") == src.count("W302"), "W302 (cumulative) must not roll"
assert out.count("W303") == src.count("W303"), "W303 (cumulative) must not roll"
assert out.count("W304") == src.count("W304"), "W304 (cumulative) must not roll"
assert out.count("1,121,741") >= 3, "new ledger anchor missing"
assert out.count("695,320") >= src.count("693,120") - 1, "prior-K roll mismatch"
assert out.count("line_pre_w318") >= 1 and out.count("line_pre_w317") == 1  # sec.7 prior block
assert out.count("ZZ") == 0, "sentinel leaked"
assert out.count("n1_w317") >= 4 and out.count("n1_w318") >= 1
assert out.count("n1_w316") == 0, "n1 double roll"
assert out.count(SEAT_SHA) >= 3
assert out.count(SEAT_MSG) >= 3
assert out.count("CLEAN-AT-BIRTH 49th gen") == 1
assert out.count("r1216") >= 6, "round labels"
assert "708_301..710_300" not in out, "stale comma-form band leaked"
assert out.count("_w318bmc_20261024_probe_receipt.json") >= 2
assert "\u7b2c 80 \u6b21" in out or "\u7b2c 81 \u6b21" in out, "sixgate ordinal missing"
assert out.count("W317-only") >= 1  # sec.7 prior-wave block intact

receipt = {"keys": counts, "band_tokens": nband,
           "bytes_src": len(raw), "bytes_out": len(out.encode("utf-8"))}
open("results/_w318bmc_derive_counts.json", "w", encoding="utf-8").write(
    json.dumps(receipt, ensure_ascii=False, indent=1))
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(out)
b = out.encode("utf-8")
print("WROTE %s bytes=%d lines=%d sha16=%s bands=%d keys=%d" % (
    OUT, len(b), out.count("\n"), hashlib.sha256(b).hexdigest()[:16], nband, len(NUM)))