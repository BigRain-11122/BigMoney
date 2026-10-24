# -*- coding: utf-8 -*-
"""W325 prereg derive (bm-c r1231).

Canon-clone of the W324 POST-RUN face
(git HEAD:research/PERPETUAL_N1_W324_PREREG.md) ->
research/PERPETUAL_N1_W325_PREREG.md.

Cumulative-history chains (se_mu narrowing, own-turn rotation, RAM freeze
chain) are parked behind pure-letter sentinels and EXTENDED by one entry
(never rolled) -- r1180/r1182/r1184/r1208/r1220/r1222 pit family.
The section-7 block is taken VERBATIM from the post-W324-finalize face at HEAD.
Blocks whose landing law CHANGES this wave (B seed-hop disclosure) are swapped
with freshly written text after the band roll, never rolled through +2,200 --
the rolled form of the W324 B band would be 732_301..732_500, but W325's B
lands at 732_501..732_700 because the registered seed perpetual_n2_w18_gen
(732_500) refuses the cascade window (r1230 pit family, new instance).

Usage: python results/_w325bmc_prereg_derive.py [--measure]
"""
import hashlib
import json
import re
import subprocess
import sys

SRC_REV = "HEAD"
SRC_PATH = "research/PERPETUAL_N1_W324_PREREG.md"
OUT = "research/PERPETUAL_N1_W325_PREREG.md"
SEAT_MSG = "MSG-20261025-0556-bmc-w325-seat"
SEAT_SHA = "4a16e4d4b7"
FREE_RAM = "5.7"
MEASURE = "--measure" in sys.argv
PROJ = "\u6295\u5f71"
ANCHOR = "\u5b9e\u951a"
FREEZE = "\u51bb\u7ed3\u7a97"

raw = subprocess.run(["git", "show", "%s:%s" % (SRC_REV, SRC_PATH)],
                     capture_output=True, check=True).stdout
src = raw.decode("utf-8")
print("SRC %s bytes=%d lines=%d sha16=%s" % (
    SRC_PATH, len(raw), src.count("\n"),
    hashlib.sha256(raw).hexdigest()[:16]))
assert src.count("\n") == 80, "src line count %d" % src.count("\n")

# ---------------------------------------------------------------- facts (machine-read)
res = json.load(open("results/perpetual_faces/n1_w324_results.json", encoding="utf-8"))
led = res["science_gates"]["ledger"]
assert led["total"] == 1137141 and led["prev_total"] == 1134941, "ledger anchor drift"
cum = res["null_pool_cumulative"]
assert cum["merged"]["n_values"] == 710720, "merged K drift"
assert abs(cum["merged"]["mu"] + 0.09286164734353895) < 1e-12
assert abs(cum["merged"]["sigma"] - 0.24520477925859438) < 1e-12
assert cum["se_mu_at_k710720"] == 0.000291
assert abs(cum["w324_only"]["mu"] + 0.08570272727272726) < 1e-9
assert abs(cum["w324_only"]["sigma"] - 0.24908572958678682) < 1e-12
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_710720"] == 1.202 and kl["line_pre_w324"] == 1.2019
assert kl["line_delta_k_lift"] == 0.0001
assert kl["n_eff_held_equal"] == 1134941
assert abs(res["families"]["A_random_engine_exit"]["full_sharpe_p95"] - 0.3218) < 1e-12
assert abs(res["families"]["A_random_engine_exit"]["full_sharpe_p99"] - 0.4639) < 1e-12
DELTA = abs(cum["w324_only"]["mu"] - cum["merged"]["mu"])
assert abs(DELTA - 0.007158920070811689) < 1e-9
seed = json.load(open("results/_w325bmc_20261025_probe_receipt.json", encoding="utf-8"))
assert seed["verdict"] == "ADMIT"
l1 = seed["legs"]["leg1"]
assert l1["A"] == [730301, 732300] and l1["B"] == [732501, 732700]
assert l1["hops_A"] == 1 and l1["hops_B"] == 1
assert l1["B_seed_hop_disclosure"] == [
    {"seed": 732500, "refuser": "REG:perpetual_n2_w18_gen"}]
assert l1["relation_asserts"]["B_base_eq_own_A_tail_plus1"] is False
assert l1["relation_asserts"]["B_base_eq_first_clean_above_own_A"] is True
l4 = seed["legs"]["leg4"]
assert l4["W326p_A_naive"] == "733_501..735_500"
assert l4["W326p_B_naive"] == "732_701..732_900"
assert seed["legs"]["leg0"]["owner_rows"] == 314
assert seed["legs"]["leg0"]["bmc_rows"] == 143
# ordinal chain (r1170 law): W324 body carried 77th/78th -> W325 is 78th/79th
A_HOP, ABOVE_OWN = 78, 79
print("facts OK: ledger 1,137,141 / K 710,720 / W324-only mu -0.08570273 / p95 0.3218 / delta %.9f" % DELTA)

# ---------------------------------------------------------------- 0. prior-wave S7 block (verbatim from HEAD)
head = src
j7 = head.find("## \u00a77")
j8 = head.find("## \u00a78")
assert 0 < j7 < j8, "HEAD sec.7 block not found"
SEC7_NEW = head[j7:j8]
assert "W324-only" in SEC7_NEW and "1,137,141" in SEC7_NEW

# ---------------------------------------------------------------- 1. park cumulative history + swapped blocks
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


def swap(pattern, fresh, label, expect=1):
    """Replace a block with FRESH text (post-roll, values written as targets)."""
    global out
    ms = list(re.finditer(pattern, out, re.S))
    assert len(ms) == expect, "%s: %d hits (expect %d)" % (label, len(ms), expect)
    sent = "ZZ" + re.sub(r"[^A-Z]", "", label.upper())
    assert sent not in out
    stash[sent] = fresh
    for m in reversed(ms):
        out = out[:m.start()] + sent + out[m.end():]
    print("SWAP %-8s hits=%d len=%d" % (label, len(ms), len(fresh)))


def sub(text, pairs):
    keys = sorted(pairs, key=len, reverse=True)
    pat = re.compile("|".join(re.escape(k) for k in keys))
    return pat.sub(lambda m: pairs[m.group(0)], text)


def wave_bump(text, floor=304):
    return re.sub(r"W(\d{3})", lambda m: "W%03d" % (int(m.group(1)) + 1)
                  if int(m.group(1)) >= floor else m.group(0), text)


def se(old):
    old_tail = "\u2192W324 " + PROJ + " 0.000291"
    assert old_tail in old, "se chain tail not the expected W324 projection"
    return old.replace(old_tail,
                       "\u2192W324 **0.000291**\u2192W325 " + PROJ + " 0.000290")


def rot(old):
    assert "\u2192W324 bm-c own-turn rotation" in old, "own-turn tail not W324"
    return old.replace("\u2192W324 bm-c own-turn rotation",
                       "\u2192W324 bm-c\u2192W325 bm-c own-turn rotation", 1)


def ram(old):
    m = re.search(r"\u00b7\u672c\u7a97" + FREEZE + r" ~([\d.]+)G bm-c " + ANCHOR + r"\uff09", old)
    assert m, "RAM chain tail not found"
    new = ("\u00b7W324 " + FREEZE + " ~" + m.group(1) + "G bm-c " + ANCHOR +
           "\u00b7\u672c\u7a97" + FREEZE + " ~" + FREE_RAM + "G bm-c " + ANCHOR + "\uff09")
    return old[:m.start()] + new + old[m.end():]


park(r"W277 \*\*0\.000314\*\*[^\n]*?\u6295\u5f71 0\.000291", se, "SECH")
park(r"W288 bm-c(?:\u2192W\d{3} bm-c)* own-turn rotation", rot, "ROTCH")
park(r"W206/W211[^\n]*?" + ANCHOR + "\uff09", ram, "RAMCH")

# ---- swapped blocks (landing law changes this wave; written as final targets)
swap(r"\*\*W323 prereg \u00a75 item5 \u6295\u5f71\u627f\u63a5\u9762\u6ce8\u8bb0\u5151\u73b0"
     r"\+落位一致如面\*\*\uff1a.*?\uff08\u89c1 \u00a75 item5\uff09\u3002",
     "**W324 prereg \u00a75 item5 \u6295\u5f71\u627f\u63a5\u9762\u6ce8\u8bb0\u5151\u73b0+落位一致如面**："
     "投影预言 W325 A naive 730_101..732_100 将被注册 W324 B 带 730_101..730_300 拒（staircase affects A 承袭·第七十八次连续 A-hop）"
     "与 B own-A reservation cascade 上移——本窗 live re-derive 与投影在 A 面完全一致（hops=1→**730_301..732_300**·base==注册 W324 B 尾 730_300+1）；"
     "B 面 cascade 方向一致但落位另遇**注册种子让位**（cascade 窗 732_301..732_500 撞注册种子 perpetual_n2_w18_gen=732_500 → 再上一窗落 **732_501..732_700**·"
     "W325 起的新落位形态·如实披露不抹平）。R308：W325 带（A 730_301..732_300/B 732_501..732_700）注册后对 W326+ 的拒面影响=W325 冻结方 leg4 前瞻已机证（见 \u00a75 item5）。",
     "HDRPROJ")

swap(r"\uff08\*\*B \u9762=1-HOP own-A RESERVATION CASCADE[^\n]*?AB \u540c\u7a97\u4e92\u65a5\u9762 leg2 \u5f8b\u5728\u573a\uff09\uff1b",
     "（**B 面=1-HOP own-A RESERVATION CASCADE + 注册种子让位·落位高于本波 A 窗形态（第七十九次连续 above-own-A 落位）**："
     "B naive 续带 730_301..730_500（自注册 W324 B 尾 730_300+1 续）在席位窗宇宙（post-W324-REGISTERED 终态注册）起点即 CLEAN 于注册宇宙"
     "但落本波 A first-clean 窗 730_301..732_300 内=own-A reservation cascade standard leg 强制（probe leg1 B_semantics 机证）"
     "→cascade 落位 732_301..732_500 撞注册种子（perpetual_n2_w18_gen=732_500·seed_admit 拒）→**再上让位一窗**落 **732_501..732_700**"
     "·**hops=1（cascade 跳；种子让位单列 B_seed_hop_disclosure，两面对读）**·**B 落位 base==own-A 尾之上的首个净窗（非 ==own-A 尾+1 恒等·W325 起新读法）机检关系**"
     "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_base_eq_own_A_tail_plus1=false·B_base_eq_first_clean_above_own_A=true·probe 回执 leg1 机证·非转录 r587）；",
     "HDRB")

swap(r"\*\*\uff08\u5e2d\u4f4d\u516c\u793a=MSG-20261025-0508-bmc-w324-seat[^\n]*?never transcribe r587\*\*\uff09\uff09\uff1b",
     "（席位公示=" + SEAT_MSG + " 已推 origin " + SEAT_SHA + " r565 律（bm-c r1230 席·queue-head seat-first lane）·"
     "probe W326+ 投影（pre-W325 宇宙·leg4）A naive **733_501..735_500** CLEAN（hops=1）·B naive **732_701..732_900** CLEAN（hops=0·不落投影 A 窗内）"
     "——**post-W325-REGISTERED 预披露：W325 A 带 730_301..732_300 与 B 带 732_501..732_700 注册后，W326 的算术续带拒面必变；"
     "W326 冻结方必须 post-W325 活 derive 且 derive B 时预留本波 A 窗，并复核注册种子让位规则（W325 新形态）·W141 先例·never transcribe r587**））；",
     "S0SEAT")

swap(r"\- \*\*B \u6863\*\*\uff08j=0\.\.199\uff09[^\n]*?p_exit=`P_EXIT=0\.05`\u3002",
     "- **B 档**（j=0..199）：entry rng=**730_301+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；"
     "exit rng=**732_501+j**（法典 \u00a74 W325 行 B=732_501..732_700·**1-HOP own-A RESERVATION CASCADE + 注册种子让位·落位高于本波 A 窗形态**："
     "B naive 续带 730_301..730_500（自注册 W324 B 尾 730_300+1 续）在席位窗宇宙（post-W324-REGISTERED 终态注册）起点即 CLEAN 于注册宇宙"
     "但落本波 A first-clean 窗 730_301..732_300 内=own-A reservation cascade standard leg·probe leg1 B_semantics 机证"
     "→cascade 落位 732_301..732_500 撞注册种子 perpetual_n2_w18_gen=732_500（seed_admit 拒·leg1 B_seed_hop_disclosure 机证）→再上让位一窗落 732_501..732_700"
     "·**B 落位 base==own-A 尾之上的首个净窗（非 own-A 尾+1 恒等）机检关系**（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_base_eq_first_clean_above_own_A=true"
     "·第七十九次连续 above-own-A 落位如实注记）·非转录 r587·ADMIT 回执在场）；p_exit=`P_EXIT=0.05`。",
     "S3B")

swap(r"5\. \*\*W325\+ \u6295\u5f71\uff08probe \u673a\u8bc1 leg4[^\n]*?hop \u94fe\u9010\u8df3\u5728 probe \u56de\u6267\u3002",
     "5. **W326+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive **733_501..735_500** CLEAN（hops=1·pre-W325 宇宙）；"
     "B naive **732_701..732_900** CLEAN（hops=0·lands_inside_W326p_A=false）"
     "——**post-W325-REGISTERED 预披露：W325 A 带 730_301..732_300 与 B 带 732_501..732_700 注册后 W326 拒面必变（A 自 W325 A 尾 732_300 续·B 自 W325 B 尾 732_700 续），"
     "且 B 可能再遇注册种子让位（本波新形态）——W326 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须 post-W325 活 derive 且 derive B 时预留本波 A 窗，"
     "hop 链逐跳在 probe 回执（读回执须 B_hop_chain 与 B_seed_hop_disclosure 两面同读）。",
     "S5PROJ")

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
assert SEC8.count("W325") >= 1 and "lands_inside" in SEC8, "sec.8 template drift"
out = out[:i8] + "ZZSECS" + out[i8_end:]

# ---------------------------------------------------------------- 2. wave labels +1 (W>=304)
out = wave_bump(out)

# ---------------------------------------------------------------- 3. numeric / ordinal / artifact maps
NUM = [
    # --- ledger / pool anchors (single-pass; longest key wins)
    ("\u952e W324 \u5b9e\u6d4b K-lift **+0.0000**\u00b7line_merged@K708,520 **1.2018**\u00b7line_pre_w324 1.2018\u00b7n_eff_held_equal 1,132,741\uff1b",
     "\u952e W324 \u5b9e\u6d4b K-lift **+0.0001**\u00b7line_merged@K710,720 **1.202**\u00b7line_pre_w325 1.202\u00b7n_eff_held_equal 1,134,941\uff1b"),
    ("1,134,941", "1,137,141"),
    ("1,132,741", "1,134,941"),
    ("K708,520", "K710,720"),
    ("710,720", "712,920"),
    ("708,520", "710,720"),
    # --- merged / wave-only statistics
    ("0.09288388", "0.09286165"),
    ("0.24519249", "0.24520478"),
    ("0.09244968", "0.08570273"),
    ("0.00043", "0.00715892"),
    # --- A family p95 anchor
    ("0.3192", "0.3218"),
    # --- wave / row / seed ordinals
    ("\u6c60\u7b2c 322 \u679a", "\u6c60\u7b2c 323 \u679a"),
    ("\u884c 313 \u6ce8\u518c\u5728\u518c", "\u884c 314 \u6ce8\u518c\u5728\u518c"),
    ("bmc rows 142+\u5019\u9009=\u7b2c 143 \u679a", "bmc rows 143+\u5019\u9009=\u7b2c 144 \u679a"),
    ("bmc_rows=142", "bmc_rows=143"),
    ("bmc live rows 142", "bmc live rows 143"),
    ("\u7b2c\u4e00\u767e\u56db\u5341\u4e8c\u679a", "\u7b2c\u4e00\u767e\u56db\u5341\u4e09\u679a"),
    ("\u5f15\u64ce\u7ebf\u7b2c 314 \u6ce2", "\u5f15\u64ce\u7ebf\u7b2c 315 \u6ce2"),
    ("\u6ce2\u53f7 322=", "\u6ce2\u53f7 323="),
    ("\u4e09\u767e\u4e00\u5341\u516b\u9762", "\u4e09\u767e\u4e00\u5341\u4e5d\u9762"),
    ("CLEAN-AT-BIRTH 55th gen", "CLEAN-AT-BIRTH 56th gen"),
    # --- ordinal words (single-pass; NEVER chained)
    ("\u7b2c\u4e03\u5341\u4e03\u6b21", "\u7b2c\u4e03\u5341\u516b\u6b21"),
    # --- runner / artifact names
    ("--wave 324", "--wave 325"),
    ("n1_w323", "n1_w324"),
    ("n1_w324", "n1_w325"),
    ("_w323bmc_", "_w324bmc_"),
    ("_w324bmc_", "_w325bmc_"),
    ("_w323bmc_freeze_edits.py \u6a21\u677f\u6d3e\u751f", "_w324bmc_freeze_edits.py \u6a21\u677f\u6d3e\u751f"),
    ("MSG-20261025-0508-bmc-w324-seat", SEAT_MSG),
    # --- commit shas (prereg / splice / seat chain)
    ("37e570fa4d+832cffac64+08daa60a30", "9d495afdcd+4a16e4d4b7"),
    ("832cffac64", "9d495afdcd"),
    ("08daa60a30", SEAT_SHA),
    # --- window clock / round labels
    ("04:36", "05:4x"),
    ("05:1x", "06:0x"),
    ("05:2x", "06:1x"),
    ("r1227", "r1229"),
    ("r1228", "r1230"),
    ("r1229", "r1231"),
]
# the seat-msg key is a no-op self-map: drop it (assert-free hygiene)
NUM = [(a, b) for a, b in NUM if a != b]

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
    "- \u00a75.5 W326+ \u6295\u5f71\u627f\u63a5\u673a\u8bc1\uff08\u672c\u5e2d receipt `results/_w325bmc_20261025_probe_receipt.json` leg4\uff0cpre-W325 \u5b87\u5b99\uff09\uff1a"
    "A naive **733_501..735_500** clean\uff08hops=1\uff09\u3001B naive **732_701..732_900** clean\uff08hops=0\uff0clands_inside_W326p_A=false\uff09"
    "\u2014\u2014**W326 \u51bb\u7ed3\u65b9\u5fc5\u987b\u5728 post-W325 \u5b87\u5b99\u91cd live derive \u4e14\u5728 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97"
    "\uff08W141 \u5148\u4f8b\uff09\u00b7never transcribe r587**\u3002\n"
    "- \u672c\u7a97\u5e2d\u4f4d\u5b9e\u6d4b\u673a\u8bc1\uff08post-W324-REGISTERED \u5b87\u5b99\uff09\uff1aA **730_301..732_300**\uff0878th \u8fde\u7eed A-hop\u00b7hops=1\u00b7naive \u8d77\u70b9 730_101 \u88ab\u6ce8\u518c W324 B \u5e26 730_101..730_300 \u62d2\u00b7base==\u6ce8\u518c W324 B \u5c3e 730_300+1\uff09\uff0f"
    "B **732_501..732_700**\uff0879th \u8fde\u7eed above-own-A\u00b7hops=1\uff1aown-A reservation cascade \u843d 732_301..732_500 \u649e\u6ce8\u518c\u79cd\u5b50 perpetual_n2_w18_gen=732_500 \u2192 \u8ba9\u4f4d\u81f3\u4e0a\u4e00\u7a97\uff09\u2014\u2014"
    "`results/_w325bmc_20261025_probe_receipt.json` verdict ADMIT\u00b7relation_asserts 4/5\uff08B_base_eq_own_A_tail_plus1=false \u4e3a\u771f\u5b9e\u8bed\u4e49\uff0cB_base_eq_first_clean_above_own_A=true\uff09\u00b7seed_admit_gate FREE x2\u00b7"
    "leg3 bands_clear=True\u00b7owner_rows=314 / bmc_rows=143 / ordinal=315\u3002\n"
    "- \u672c\u6ce2\u5e2d\u4f4d live \u4e8b\u5b9e\uff1aA \u7b97\u672f\u7eed\u5e26 730,101..732,100 \u5728\u5e2d\u4f4d\u7a97\u8d77\u70b9\u5373\u88ab\u6ce8\u518c W324 B \u5e26 730,101..730,300 \u62d2\u7edd\uff08hops=1 \u2192 730,301..732,300\uff09\uff1bB \u7b97\u672f\u7eed\u5e26 730,301..730,500 \u843d\u672c\u6ce2 A \u7a97\uff08cascade\uff09\u2192 732,301..732,500 \u649e\u6ce8\u518c\u79cd\u5b50 732,500 \u2192 \u8ba9\u4f4d 732,501..732,700\u3002\n"
    "- \u5b9d\u85cf\u4e0e\u65b9\u6cd5\u8bba\u6355\u83b7\u95ee\uff1a\u672c\u6ce2=nulls-deepening \u5e38\u6001\u52a0\u6df1\uff0c**\u65e0\u65b0\u65b9\u6cd5/\u65e0\u65b0\u5b9d\u85cf**\uff1bknowledge/METHODOLOGY_ASSETS.md \u4e0e "
    "TREASURE_REGISTRY.json \u5747\u4e0d\u8ffd\u52a0\u3002\n"
    "- \u8bda\u5b9e\u62ab\u9732\uff08finalize \u540c\u7a97\u56de\u586b\uff09\uff1a\n"
    "  \u2460 \u672c\u51bb\u7ed3\u65f6\u70b9\u65e0\u5f85\u62ab\u9732\u9879\uff1b\u56de\u586b\u65f6\u82e5\u53d1\u73b0 prose \u504f\u5dee\uff0c\u4e00\u5f8b\u4ee5\u673a\u8bfb\u503c\u4e3a\u51c6\u5e76\u62ab\u9732\u3001\u4e0d\u62b9\u5e73\u3002\n"
    "  \u2461 \u5ef6\u7eed\u524d\u6ce2\u62ab\u9732\u9762\uff08W324 \u00a78 \u2460\uff1afreeze receipt post \u9762=landed \u9762\u672c\u4f53\uff0cheal_delta 0\uff09\u2014\u2014\u672c\u6ce2\u82e5\u540c\u9762\u91cd\u73b0\uff0c\u4e00\u5f8b\u7531 adjudication \u9006\u5411\u590d\u73b0\u6d4b\u8bc1\u3002\n"
    "- \u5751\u5f8b\u6355\u83b7\uff08finalize \u540c\u7a97\u56de\u586b\uff09\uff1a\n"
    "  \u2460 **\u5e2d\u4f4d B \u843d\u4f4d\u65b0\u5f62\u6001\uff08\u6ce8\u518c\u79cd\u5b50\u8ba9\u4f4d\uff09**\uff1acascade \u540e\u7684\u9996\u4e2a\u51c0\u7a97\u53ef\u88ab SEED_REGISTRY \u79cd\u5b50\u5360\u7528\uff0c\u6b64\u65f6 B \u843d\u4f4d base \u2260 own-A \u5c3e+1\uff0c"
    "\u800c\u662f\u300cown-A \u5c3e\u4e4b\u4e0a\u7684\u9996\u4e2a\u51c0\u7a97\u300d\uff1b\u8bfb\u56de\u6267\u987b B_hop_chain \u4e0e B_seed_hop_disclosure \u4e24\u9762\u540c\u8bfb\uff08r1230 \u63a2\u9488\u4fee\u6cd5\u5728\u672c\u6ce2\u9996\u6b21\u5b9e\u6218\uff09\u3002\n"
    "  \u2461 \u884c\u6570\u5b88\u5361\uff08\u51bb\u7ed3\u4ef6\u7ed3\u6784\u5b8c\u6574\u6027\uff09\uff1a\u590d\u5efa \u00a77/\u00a78 \u5757\u540e\u884c\u6570\u5fc5\u987b\u4e0e\u6e90\u9762\u4e00\u81f4\uff0c\u4e0d\u4e00\u81f4=\u7ed3\u6784\u6f02\u79fb\u3001\u76f4\u63a5\u62a5\u6b7b\u3002\n"
    "- \u6536\u53e3\u7eaa\u5f8b\uff1afinalize \u53ea\u6d88\u8d39\u5728\u518c\u5206\u7247\uff08audit.finalize_only=true\uff09\uff0c\u672c\u6ce2\u96f6\u91cd\u70e7\u3001\u96f6\u53cc\u70e7\uff1bS6 \u94fe\u4e0e\u8f6e\u6536\u53e3\u540c\u7a97\u3002\n\n"
)
assert out.count("ZZSECS") == 1
out = out.replace("ZZSECS", SEC8_NEW)

# ---------------------------------------------------------------- 5b. post-fixes (live readings this window)
POST = [
    ("\u672c\u7a97 free RAM 5.8GB", "\u672c\u7a97 free RAM " + FREE_RAM + "GB"),
    ("nvidia-smi \u5b9e\u8bfb util 1%\u00b7VRAM \u5360\u7528 2.4G/16G",
     "nvidia-smi \u5b9e\u8bfb util 1%\u00b7VRAM \u5360\u7528 2.6G/16G"),
]
for old, new in POST:
    n = out.count(old)
    assert n >= 1, "post-fix %r hits=%d" % (old[:40], n)
    out = out.replace(old, new)
    print("post-fix applied hits=%d" % n)

# ---------------------------------------------------------------- 6. asserts
assert out.count("\n") == 80, "line count changed: %d" % out.count("\n")
assert out.count("730_301..732_300") >= 2, "new A band missing"
assert out.count("732_501..732_700") >= 4, "new B band missing"
assert out.count("730_101..732_100") >= 1, "A naive continuation missing"
assert out.count("730_301..730_500") >= 1, "B naive continuation missing"
assert out.count("732_301..732_500") >= 1, "cascade window missing (disclosed)"
assert out.count("W325") > 30 and out.count("W326") > 5
assert out.count("W303 bm-c") == src.count("W303 bm-c"), "rotation chain must not roll"
assert out.count("1,137,141") >= 3, "new ledger anchor missing"
assert out.count("ZQ") == 0
assert out.count("n1_w324") >= 4 and out.count("n1_w325") >= 1
assert out.count("n1_w323") == 0, "n1 double roll"
assert out.count(SEAT_SHA) >= 3
print("SEAT_MSG count", out.count(SEAT_MSG))
assert out.count(SEAT_MSG) >= 3
assert out.count("CLEAN-AT-BIRTH 56th gen") == 1
assert out.count("r1231") >= 5, "round labels"
assert out.count("_w325bmc_20261025_probe_receipt.json") >= 1
assert out.count("W324-only") >= 1  # sec.7 prior-wave block intact
assert out.count("ZZ") == 0, "sentinel leaked"
assert out.count("perpetual_n2_w18_gen=732_500") >= 2, "seed-hop disclosure missing"

receipt = {"keys": counts, "band_tokens": nband,
           "bytes_src": len(raw), "bytes_out": len(out.encode("utf-8"))}
open("results/_w325bmc_derive_counts.json", "w", encoding="utf-8").write(
    json.dumps(receipt, ensure_ascii=False, indent=1))
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(out)
b = out.encode("utf-8")
print("WROTE %s bytes=%d lines=%d sha16=%s bands=%d keys=%d" % (
    OUT, len(b), out.count("\n"), hashlib.sha256(b).hexdigest()[:16], nband, len(NUM)))