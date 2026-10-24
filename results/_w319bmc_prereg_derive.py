# -*- coding: utf-8 -*-
"""W319 prereg derive (bm-c r1219).

Canon-clone of the W318 POST-RUN face
(git 4421303e49:research/PERPETUAL_N1_W318_PREREG.md, 29,326B / 75 newlines,
sha16 fcdf6098b167be14) -> research/PERPETUAL_N1_W319_PREREG.md.

Cumulative-history chains (se_mu narrowing, A/B 1-hop wave list, own-turn
rotation list, RAM freeze chain) are parked behind pure-letter sentinels and
EXTENDED by one entry (never rolled) -- r1180/r1182/r1184/r1208 pit family.
The section-7 block is taken VERBATIM from the post-W318-finalize face at HEAD.
Everything else rides ONE single-pass map (r1168/r1170/r1171/r1179/r1199/r1206).

Face classification (r1208/r1214):
  wave tokens (W###)  -> cascade +1 (floor 304)
  band tokens         -> arithmetically +2200 (never a NUM key)
  ordinal words       -> single-pass map (NEVER chained)
  accumulated chains  -> parked, extended by one entry
  self/prior refs     -> explicit hand values in this file

Usage: python results/_w319bmc_prereg_derive.py [--measure|--diag]
"""
import hashlib
import json
import re
import subprocess
import sys

SRC_REV = "4421303e49"
SRC_PATH = "research/PERPETUAL_N1_W318_PREREG.md"
OUT = "research/PERPETUAL_N1_W319_PREREG.md"
EXPECT_SHA16 = "fcdf6098b167be14"
EXPECT_BYTES = 29326
SEAT_MSG = "MSG-20261025-0003-bmc-w319-seat"
SEAT_SHA = "4421303e49"
FREE_RAM = "4.3"
MEASURE = "--measure" in sys.argv

raw = subprocess.run(["git", "show", "%s:%s" % (SRC_REV, SRC_PATH)],
                     capture_output=True, check=True).stdout
assert len(raw) == EXPECT_BYTES, "src bytes %d != %d" % (len(raw), EXPECT_BYTES)
assert hashlib.sha256(raw).hexdigest()[:16] == EXPECT_SHA16, "src sha16 mismatch"
src = raw.decode("utf-8")
assert src.count("\n") == 75, "src line count %d" % src.count("\n")

# ---------------------------------------------------------------- facts (machine-read)
res = json.load(open("results/perpetual_faces/n1_w318_results.json", encoding="utf-8"))
led = res["science_gates"]["ledger"]
assert led["total"] == 1123941 and led["prev_total"] == 1121741, "ledger anchor drift"
cum = res["null_pool_cumulative"]
assert cum["merged"]["n_values"] == 697520, "merged K drift"
assert abs(cum["merged"]["mu"] + 0.09282727577703864) < 1e-12
assert abs(cum["merged"]["sigma"] - 0.24517157822132205) < 1e-12
assert cum["se_mu_at_k697520"] == 0.000294
assert abs(cum["w318_only"]["mu"] + 0.09374522727272727) < 1e-12
assert abs(cum["w318_only"]["sigma"] - 0.2462069552546672) < 1e-12
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_697520"] == 1.2013 and kl["line_pre_w318"] == 1.2013
assert kl["line_delta_k_lift"] == 0.0
assert kl["n_eff_held_equal"] == 1121741
assert abs(res["families"]["A_random_engine_exit"]["full_sharpe_p95"] - 0.3212) < 1e-12
assert abs(res["families"]["A_random_engine_exit"]["full_sharpe_p99"] - 0.451) < 1e-12
seed = json.load(open("results/_w319bmc_20261025_probe_receipt.json", encoding="utf-8"))
assert seed["verdict"] == "ADMIT"
l1 = seed["legs"]["leg1"]
assert l1["A"] == [717101, 719100] and l1["B"] == [719101, 719300]
assert l1["hops_A"] == 1 and l1["hops_B"] == 1
l4 = seed["legs"]["leg4"]
assert l4["W320p_A_naive"] == "719_101..721_100"
assert l4["W320p_B_naive"] == "719_301..719_500"
assert seed["legs"]["leg0"]["owner_rows"] == 308
assert seed["legs"]["leg0"]["bmc_rows"] == 137
assert seed["ordinals"]["a_hop"] == 72 and seed["ordinals"]["above_own_a"] == 73
print("facts OK: ledger 1,123,941 / K 697,520 / W318-only mu -0.09374523 / p95 0.3212")

# ---------------------------------------------------------------- 0. prior-wave S7 block (verbatim from HEAD)
head = subprocess.run(["git", "show", "HEAD:%s" % SRC_PATH],
                      capture_output=True, check=True).stdout.decode("utf-8")
j7 = head.find("## \u00a77")
j8 = head.find("## \u00a78")
assert 0 < j7 < j8, "HEAD sec.7 block not found"
SEC7_NEW = head[j7:j8]
assert "W318-only" in SEC7_NEW and "1,123,941" in SEC7_NEW

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
    old_tail = "\u2192W318 " + PROJ + " 0.000293"
    assert old_tail in old, "se chain tail not the expected W318 projection"
    assert "0.000293" in old
    return old.replace(old_tail,
                       "\u2192W318 **0.000294**\u2192W319 " + PROJ + " 0.000293")


def ab(old):
    t = old.replace("/W313/W314/W315/W316/W317/W318=A/B",
                    "/W313/W314/W315/W316/W317/W318/W319=A/B", 1)
    assert "W319=A/B" in t, "A/B chain tail not expected /W313..W318=A/B"
    return t


def rot(old):
    t = old.replace("\u2192W318 bm-c own-turn rotation",
                    "\u2192W318 bm-c\u2192W319 bm-c own-turn rotation", 1)
    assert "W319 bm-c own-turn rotation" in t, "own-turn chain tail not expected W318"
    return t


def ram(old):
    m = re.search(r"\u00b7W316 " + FREEZE + r" ~([\d.]+)G bm-c " + ANCHOR +
                  r"\u00b7W317 " + FREEZE + r" ~([\d.]+)G bm-c " + ANCHOR +
                  r"\u00b7\u672c\u7a97" + FREEZE + r" ~([\d.]+)G bm-c " + ANCHOR + "\uff09", old)
    assert m, "RAM chain tail not found"
    new_tail = ("\u00b7W316 " + FREEZE + " ~" + m.group(1) + "G bm-c " + ANCHOR +
                "\u00b7W317 " + FREEZE + " ~" + m.group(2) + "G bm-c " + ANCHOR +
                "\u00b7W318 " + FREEZE + " ~" + m.group(3) + "G bm-c " + ANCHOR +
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
assert SEC8.count("W319+") == 1 and "lands_inside=True" in SEC8, "sec.8 template drift"
out = out[:i8] + "ZZSECS" + out[i8_end:]

# ---------------------------------------------------------------- 2. wave labels +1 (W>=304)
out = wave_bump(out)

# ---------------------------------------------------------------- 3. numeric / ordinal / artifact maps
NUM = [
    # --- ledger / pool anchors (single-pass; longest key wins)
    ("1,121,741", "1,123,941"),
    ("1,119,541", "1,121,741"),
    ("K695,320", "K697,520"),
    ("697,520", "699,720"),
    ("695,320", "697,520"),
    # --- merged / wave-only statistics
    ("−0.09282437", "−0.09282728"),
    ("0.24516847", "0.24517158"),
    ("−0.09947591", "−0.09374523"),
    ("0.0067", "0.005731"),
    # --- A family p95 anchor
    ("0.3158", "0.3212"),
    # --- K-lift pair (long key wins over the bare decimals)
    ("**1.2012**·line_pre_w318 1.2012", "**1.2013**·line_pre_w319 1.2013"),
    ("line_pre_w318", "line_pre_w319"),
    # --- wave / row / seed ordinals
    ("池第 316 枚", "池第 317 枚"),
    ("行 307 注册在册", "行 308 注册在册"),
    ("bmc rows 136+候选=第 137 枚", "bmc rows 137+候选=第 138 枚"),
    ("bmc_rows=136", "bmc_rows=137"),
    ("bmc live rows 136", "bmc live rows 137"),
    ("第一百三十六枚", "第一百三十七枚"),
    ("引擎线第 308 波", "引擎线第 309 波"),
    ("波号 316=", "波号 317="),
    ("三百一十二面", "三百一十三面"),
    ("CLEAN-AT-BIRTH 49th gen", "CLEAN-AT-BIRTH 50th gen"),
    # --- ordinal words (single-pass; NEVER chained)
    ("第七十一次", "第七十二次"),
    ("第七十二次", "第七十三次"),
    ("第六十五波", "第六十六波"),
    # --- runner / artifact names
    ("--wave 318", "--wave 319"),
    ("n1_w317", "n1_w318"),
    ("n1_w318", "n1_w319"),
    ("_w318bmc_20261024", "_w319bmc_20261025"),
    ("_w318bmc_", "_w319bmc_"),
    ("MSG-20261024-2259-bmc-w318-seat", SEAT_MSG),
    # --- commit shas (prereg / splice / seat chain)
    ("06002d41aa", "87669dc1da"),
    ("5d6d26634f", "4a78879173"),
    ("a2ba09e18a", SEAT_SHA),
    # --- window clock / round labels (long keys first via sort)
    ("bm-c r1214 五面冻结 splice 5d6d26634f 落地 22:4x",
     "bm-c r1217 五面冻结 splice 4a78879173 落地 23:2x"),
    ("bm-c r1215 窗 23:0x", "bm-c r1218 窗 00:0x"),
    ("finalize 已落地 23:0x", "finalize 已落地 00:0x"),
    ("键·23:0x finalize one-pass", "键·00:0x finalize one-pass"),
    ("执行窗 22:4x", "执行窗 23:2x"),
    ("r1214/r1214/r1215 W318", "r1217/r1217/r1218 W318"),
    ("prereg 06002d41aa 落于 r1214 窗", "prereg 87669dc1da 落于 r1217 窗"),
    ("estate chain r1214/r1214/r1215 W318 全周期 06002d41aa+5d6d26634f+a2ba09e18a",
     "estate chain r1217/r1217/r1218 W318 全周期 87669dc1da+4a78879173+4421303e49"),
    ("席位 r1215 窗+prereg r1216 窗落地", "席位 r1218 窗+prereg r1219 窗落地"),
    ("bm-c r1215 席位", "bm-c r1218 席位"),
    ("bm-c 循环班 r1216 " + FREEZE + " 2026-10-24 23:1x",
     "bm-c 循环班 r1219 " + FREEZE + " 2026-10-25 00:2x"),
    ("r1214", "r1217"),
    ("r1215", "r1218"),
    ("r1216", "r1219"),
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
    "- §5.5 W320+ 投影承接机证：本窗席位回执 leg4（pre-W319 宇宙）投影 W320p A naive **719_101..721_100** clean（hops=0）、"
    "B naive **719_301..719_500** clean（hops=0）但落投影 A 窗内（own-A reservation 承袭预期）——**W320 冻结方必须在 "
    "post-W319 宇宙重 live derive 且在 derive B 时预留本波 A 窗（W141 先例）·never transcribe r587**。\n"
    "- 本窗席位实测机证：A **717_101..719_100**（72nd 连续 A-hop·hops=1·base==注册 W318 B 尾 717_100+1）／"
    "B **719_101..719_300**（73rd 连续 above-own-A·hops=1·base==本波 A 尾 719_100+1）——"
    "`results/_w319bmc_20261025_probe_receipt.json` verdict ADMIT·relation_asserts 4/4·seed_admit_gate FREE x2·leg3 bands_clear=True。\n"
    "- 宝藏与方法论捕获问：本波=nulls-deepening 常态加深，**无新方法/无新宝藏**，knowledge/METHODOLOGY_ASSETS.md 与 "
    "TREASURE_REGISTRY.md 均不追加。\n"
    "- 诚实披露：§5 五预键若出现 prose 偏差（se_mu 取 3 位小数），以机读值为准并披露、不抹平；mu/sigma/K-lift 一律按冻结带校验。\n"
    "- 坑律捕获：post-W318 finalize 同窗回填（本段属 finalize 回填面，冻结时为前波沿用文本）；本窗冻结沿用 r1208/r1214 判例："
    "canon-clone 生成器的纯数字面（注册行号前缀/切口/setwave 键后缀）直写目标波号、W token 面保留**上一波**形态交给级联推进一次。\n"
    "- 收口纪律：finalize 只消费在册分片（audit.finalize_only=true），本波零重烧、零双烧；S6 链与轮收口同窗。\n\n\n"
)
assert out.count("ZZSECS") == 1
out = out.replace("ZZSECS", SEC8_NEW)

# ---------------------------------------------------------------- 5b. post-fixes
POST = [
    ("GPU=gen-only 车道 idle（nvidia-smi 实读 util 8%·VRAM 占用 3.2G/16G·非本波占用·CPU 车道独立）",
     "GPU=gen-only 车道 idle（nvidia-smi 实读 util 2%·VRAM 占用 3.0G/16G·非本波占用·CPU 车道独立）"),
]
for old, new in POST:
    n = out.count(old)
    assert n >= 1, "post-fix %r hits=%d" % (old[:40], n)
    out = out.replace(old, new)
    print("post-fix applied hits=%d" % n)

# ---------------------------------------------------------------- 6. asserts
if "--diag" in sys.argv:
    for tok in ("717_101", "719_100", "719_101", "719_300", "719_301", "721_100",
                "719_500", "714_501"):
        print("DIAG", tok, out.count(tok))
    sys.exit(0)

assert out.count("\n") == 75, "line count changed: %d" % out.count("\n")
assert out.count("717_101..719_100") >= 2, "new A band missing"
assert out.count("719_101..719_300") >= 2, "new B band missing"
assert out.count("717_101..719_100") >= 1 and out.count("719_101..721_100") >= 1
assert out.count("719_301..719_500") >= 0
assert out.count("W319") > 30 and out.count("W320") > 5
assert out.count("W303") == src.count("W303"), "W303 (cumulative) must not roll"
assert out.count("W304") == src.count("W304"), "W304 (cumulative) must not roll"
assert out.count("1,123,941") >= 3, "new ledger anchor missing"
assert out.count("697,520") >= src.count("695,320") - 1, "prior-K roll mismatch"
assert out.count("line_pre_w319") >= 1 and out.count("line_pre_w318") == 1  # sec.7 prior block
assert out.count("ZZ") == 0, "sentinel leaked"
assert out.count("n1_w318") >= 4 and out.count("n1_w319") >= 1
assert out.count("n1_w317") == 0, "n1 double roll"
assert out.count(SEAT_SHA) >= 3
assert out.count(SEAT_MSG) >= 3
assert out.count("CLEAN-AT-BIRTH 50th gen") == 1
assert out.count("r1219") >= 6, "round labels"
assert "708_301..710_300" not in out, "stale comma-form band leaked"
assert out.count("_w319bmc_20261025_probe_receipt.json") >= 2
assert "\u7b2c 82 \u6b21" in out or "\u7b2c 81 \u6b21" in out, "sixgate ordinal missing"
assert out.count("W318-only") >= 1  # sec.7 prior-wave block intact

receipt = {"keys": counts, "band_tokens": nband,
           "bytes_src": len(raw), "bytes_out": len(out.encode("utf-8"))}
open("results/_w319bmc_derive_counts.json", "w", encoding="utf-8").write(
    json.dumps(receipt, ensure_ascii=False, indent=1))
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(out)
b = out.encode("utf-8")
print("WROTE %s bytes=%d lines=%d sha16=%s bands=%d keys=%d" % (
    OUT, len(b), out.count("\n"), hashlib.sha256(b).hexdigest()[:16], nband, len(NUM)))