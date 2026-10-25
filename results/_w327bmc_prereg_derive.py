# -*- coding: utf-8 -*-
"""W327 prereg derive (bm-c r1235).

Canon-clone of the W326 POST-RUN face (git HEAD:research/PERPETUAL_N1_W326_PREREG.md)
-> research/PERPETUAL_N1_W327_PREREG.md.

Cumulative-history chains (se_mu narrowing, own-turn rotation, RAM freeze chain) are
PARKED behind pure-letter sentinels and EXTENDED by one entry (never rolled).
Blocks whose landing law differs this wave are swapped with freshly written text
after the band roll:
  * A: 1-HOP WALK, 80th consecutive A-hop. Arithmetic continuation 735_501..737_500
    (W326 A tail 735_500) is REFUSED at start by the registered W326 B band
    735_501..735_700 AND three registered seed POINTS 736_000/736_500/737_000
    -> first clean window 737_001..739_000.
  * B: second consecutive BELOW face. Naive 735_701..735_900 sits entirely BELOW
    own-A -> own-A reservation cascade to own-A tail+1 = 739_001..739_200, EMPTY
    seed-hop disclosure, 81st consecutive above-own-A.
Usage: python results/_w327bmc_prereg_derive.py [--measure]
"""
import hashlib
import json
import re
import subprocess
import sys

SRC_REV = "HEAD"
SRC_PATH = "research/PERPETUAL_N1_W326_PREREG.md"
OUT = "research/PERPETUAL_N1_W327_PREREG.md"
SEAT_MSG = "MSG-20261025-0800-bmc-w327-seat"
SEAT_SHA = "9d9319e30a"
PREV_SPLICE_SHA = "3c4ee2bc68"
FREE_RAM = "3.6"
MEASURE = "--measure" in sys.argv
PROJ = "\u6295\u5f71"
ANCHOR = "\u5b9e\u951a"
FREEZE = "\u51bb\u7ed3\u7a97"

raw = subprocess.run(["git", "show", "%s:%s" % (SRC_REV, SRC_PATH)],
                     capture_output=True, check=True).stdout
src = raw.decode("utf-8")
print("SRC %s bytes=%d lines=%d sha16=%s" % (
    SRC_PATH, len(raw), src.count("\n"), hashlib.sha256(raw).hexdigest()[:16]))
assert src.count("\n") == 82, "src line count %d" % src.count("\n")

# ---------------------------------------------------------------- facts (machine-read)
res = json.load(open("results/perpetual_faces/n1_w326_results.json", encoding="utf-8"))
led = res["science_gates"]["ledger"]
assert led["total"] == 1141541 and led["prev_total"] == 1139341, "ledger anchor drift"
cum = res["null_pool_cumulative"]
assert cum["merged"]["n_values"] == 715120, "merged K drift"
assert abs(cum["merged"]["mu"] + 0.092869863659246) < 1e-12
assert abs(cum["merged"]["sigma"] - 0.24522973616642577) < 1e-12
assert cum["se_mu_at_k715120"] == 0.00029
assert abs(cum["w326_only"]["mu"] + 0.09348227272727273) < 1e-9
assert abs(cum["w326_only"]["sigma"] - 0.2473987658876391) < 1e-12
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_715120"] == 1.2023 and kl["line_pre_w326"] == 1.2022
assert kl["line_delta_k_lift"] == 0.0001
assert kl["n_eff_held_equal"] == 1139341
assert abs(res["families"]["A_random_engine_exit"]["full_sharpe_p95"] - 0.3203) < 1e-12
assert abs(res["families"]["A_random_engine_exit"]["full_sharpe_p99"] - 0.4374) < 1e-12
DELTA = abs(cum["w326_only"]["mu"] - cum["merged"]["mu"])
assert abs(DELTA - 0.000612409) < 1e-6, DELTA
seed = json.load(open("results/_w327bmc_20261025_probe_receipt.json", encoding="utf-8"))
assert seed["verdict"] == "ADMIT"
l1 = seed["legs"]["leg1"]
assert l1["A"] == [737001, 739000] and l1["B"] == [739001, 739200]
assert l1["ARITH_A"] == [735501, 737500] and l1["ARITH_B"] == [735701, 735900]
assert l1["hops_A"] == 1 and l1["hops_B"] == 1
assert l1["B_seed_hop_disclosure"] == []
ra = l1["relation_asserts"]
assert ra["B_naive_below_own_A"] is True and ra["B_naive_inside_own_A"] is False
assert ra["A_base_ge_priorB_tail_plus1"] is True
assert ra["B_base_eq_own_A_tail_plus1"] is True
assert ra["B_base_eq_first_clean_above_own_A"] is True
assert ra["AB_mutual_exclusion"] is True
refs = l1["A_hop_chain"][0]["refuser_pts_sample"]
assert refs == [735501, 736000, 736500, 737000], refs
l4 = seed["legs"]["leg4"]
assert l4["W328p_A_naive"] == "740_501..742_500"
assert l4["W328p_B_naive"] == "739_201..739_400"
assert l4["hops_A"] == 1 and l4["hops_B"] == 0
assert l4["W328p_B_lands_inside_W328p_A_naive"] is False
assert seed["legs"]["leg0"]["owner_rows"] == 316
assert seed["legs"]["leg0"]["bmc_rows"] == 145
assert seed["ordinals"]["a_hop"] == 80 and seed["ordinals"]["above_own_a"] == 81
print("facts OK: ledger 1,141,541 / K 715,120 / W326-only mu -0.09348227 / p95 0.3203 / delta %.9f" % DELTA)

# ---------------------------------------------------------------- 0. prior-wave S7 block (verbatim from HEAD)
j7 = src.find("## \u00a77")
j8 = src.find("## \u00a78")
assert 0 < j7 < j8, "HEAD sec.7 block not found"
SEC7_NEW = src[j7:j8]
assert "W326-only" in SEC7_NEW and "1,141,541" in SEC7_NEW

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


def swap(start_anchor, end_anchor, fresh, label):
    global out
    i = out.find(start_anchor)
    assert i > 0, "%s: start anchor not found" % label
    j = out.find(end_anchor, i)
    assert j > 0, "%s: end anchor not found" % label
    j += len(end_anchor)
    old = out[i:j]
    assert "\n" not in fresh, "%s: fresh text carries a newline" % label
    sent = "ZZ" + re.sub(r"[^A-Z]", "", label.upper())
    assert sent not in out and sent not in stash
    stash[sent] = fresh
    out = out[:i] + sent + out[j:]
    print("SWAP %-8s old_len=%d new_len=%d" % (label, len(old), len(fresh)))


def sub(text, pairs):
    keys = sorted(pairs, key=len, reverse=True)
    pat = re.compile("|".join(re.escape(k) for k in keys))
    return pat.sub(lambda m: pairs[m.group(0)], text)


def wave_bump(text, floor=304):
    return re.sub(r"W(\d{3})", lambda m: "W%03d" % (int(m.group(1)) + 1)
                  if int(m.group(1)) >= floor else m.group(0), text)


# ---- cumulative chains: EXTEND by one entry, never roll
def se(old):
    old_tail = "\u2192W326 " + PROJ + " 0.000289"
    assert old_tail in old, "se chain tail not the expected W326 projection"
    return old.replace(old_tail,
                       "\u2192W326 **0.000290**\u2192W327 " + PROJ + " 0.000289")


def rot(old):
    assert "\u2192W326 bm-c own-turn rotation" in old, "own-turn tail not W326"
    return old.replace("\u2192W326 bm-c own-turn rotation",
                       "\u2192W326 bm-c\u2192W327 bm-c own-turn rotation", 1)


def ram(old):
    m = re.search(r"\u00b7\u672c\u7a97" + FREEZE + r" ~([\d.]+)G bm-c " + ANCHOR + r"\uff09", old)
    assert m, "RAM chain tail not found"
    new = ("\u00b7W326 " + FREEZE + " ~" + m.group(1) + "G bm-c " + ANCHOR +
           "\u00b7\u672c\u7a97" + FREEZE + " ~" + FREE_RAM + "G bm-c " + ANCHOR + "\uff09")
    return old[:m.start()] + new + old[m.end():]


park(r"W277 \*\*0\.000314\*\*[^\n]*?\u6295\u5f71 0\.000289", se, "SECH")
park(r"W288 bm-c(?:\u2192W\d{3} bm-c)* own-turn rotation", rot, "ROTCH")
park(r"W206/W211[^\n]*?" + ANCHOR + "\uff09", ram, "RAMCH")

# ---------------------------------------------------------------- swapped blocks (final coordinates)
AEXT_NEW = (
    "**A-ext seed=737_001..739_000**（**A 面=STAIRCASE-AFFECTS-A·1-HOP WALK 形态"
    "（W239 staircase era 后第八十次连续 A-hop）**：A 面算术续带 735_501..737_500"
    "（自注册 W326 A 尾 735_500 续）在席位窗宇宙（post-W326-REGISTERED 终态注册）起点即 REFUSED"
    "（拒面机证四点：注册 W326 B 带 735_501..735_700 落 naive A 窗内 + 注册种子点 736_000/736_500/737_000 三点）"
    "→walk 越全部拒点→A first-clean **737_001..739_000**·**hops=1**·"
    "**A 落位 base>=注册前波 B 尾+1（735_700+1）floor 关系（本波非 == 恒等·A 面连续第二波首净窗落位形态·如实披露）**"
    "（A_hop_chain 1 跳 verbatim leg1 机证〔window 735_501..737_500→jump 737_001·"
    "refuser bands 735_501..735_700/736_000..736_000/736_500..736_500/737_000..737_000〕·"
    "A_clean_at_naive_start=false·A base>=registered prior-wave B tail+1 floor relation）"
    "·非转录 r587 前向单调断言在走册\uff1b")

BEXT_NEW = (
    "**B-ext exit seed=739_001..739_200**（**B 面=1-HOP own-A RESERVATION CASCADE·落位紧贴本波 A 尾"
    "（第八十一次连续 above-own-A 落位·连续第二波 BELOW 面）**：B naive 续带 735_701..735_900（自注册 W326 B 尾 735_700+1 续）"
    "在席位窗宇宙（post-W326-REGISTERED 终态注册）起点即 REFUSED——本波 A 面再次整体跳至 naive B 窗之**上**"
    "（A 737_001..739_000 全高于 naive B 窗·B_naive_below_own_A=true 机证），故 B 面按 own-A reservation cascade "
    "强制上移至 own-A 尾+1（probe leg1 B_semantics 机证·B_naive_inside_own_A=false）→**B 落位 739_001..739_200**·"
    "**hops=1（cascade 跳）**·**B_seed_hop_disclosure=[]（本波 cascade 落位零注册种子拒·连续第二波空披露）**·"
    "**B 落位 base==own-A 尾+1（739_000+1）机检关系**（B_hop lands-inside-A=false·B_lands_above_own_A=true·"
    "B_base_eq_own_A_tail_plus1=true·B_base_eq_first_clean_above_own_A=true·probe 回执 leg1 机证·非转录 r587\uff09\uff1b")

HDRPROJ_NEW = (
    "**W326 prereg \u00a75 item5 投影承接面注记兑现+B 落位连续第二波 BELOW 面**：投影预言 W327 A naive 737_001..739_000（hops=1）、"
    "B naive 735_701..735_900（hops=0·不落投影 A 窗内）——本窗 live re-derive 的 A **落位窗与投影同窗**，但实算续带起点为"
    "735_501..737_500（W326 A 尾 735_500+1），被注册 W326 B 带与三点注册种子拒后 walk 至首净窗，故 A 落位 base 为 first-clean 而非 prior-B 尾+1"
    "（投影面与实算面起点不同，如实披露不抹平）；B naive 整段仍落 own-A 之**下**（连续第二波 BELOW 面），B 按 reservation cascade 上移贴 own-A 尾"
    "739_001..739_200（cascade 落位零种子让位·B_seed_hop_disclosure=[]）；**W326 起 B 落位形态三面（above/inside/below）判读律本波第二次适用**，如实披露。"
    "R308：W327 带（A 737_001..739_000/B 739_001..739_200）注册后对 W328+ 的拒面影响=本波冻结方 leg4 前瞻已机证（见 \u00a75 item5）。")

S0SEAT_NEW = (
    "（席位公示=" + SEAT_MSG + " 已推 origin " + SEAT_SHA + " r565 律（bm-c r1234 席位窗发布·r1235 窗落链·queue-head seat-first lane）·"
    "probe W328+ 投影（pre-W327 宇宙·leg4）A naive **740_501..742_500**（hops=1·first_clean 同窗）·"
    "B naive **739_201..739_400**（hops=0·first_clean 同窗·不落投影 A 窗内）"
    "——**post-W327-REGISTERED 预披露：W327 A 带 737_001..739_000 与 B 带 739_001..739_200 注册后，W328 的算术续带拒面必变；"
    "W328 冻结方必须 post-W327 活 derive 且 derive B 时预留本波 A 窗，并复核 B 三面落位（above/inside/below）与注册种子让位规则·"
    "W141 先例·never transcribe r587**）\uff09\uff1b")

S3A_NEW = (
    "- **A 档**（j=0..1,999）：entry rng seed=**737_001+j**（法典 \u00a74 W327 行 A=737_001..739_000·"
    "**STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第八十次连续 A-hop）**：A 算术续带 735_501..737_500"
    "（自注册 W326 A 尾 735_500 续）在席位窗宇宙（post-W326-REGISTERED 终态注册）起点即 REFUSED"
    "（注册 W326 B 带 735_501..735_700 落 naive A 窗内 + 注册种子点 736_000/736_500/737_000 三点=W326 prereg \u00a75 item5 "
    "post-W326-REGISTERED pre-disclosure 承袭·r587）→walk 越全部拒点→A first-clean 737_001..739_000·**hops=1**·"
    "**A 落位 base>=注册前波 B 尾+1（735_700+1）floor 关系（本波非 == 恒等）**"
    "（A_hop_chain 1 跳 verbatim probe leg1 机证·A_clean_at_naive_start=false）·非转录 r587·ADMIT 回执在场）；"
    "p=`BASELINE_P[(j//50)%2]`（v1 50-seed 块交替惯例逐字）；随机入场短窗=**引擎退出口**（v1 设计逐字）。")

S3B_NEW = (
    "- **B 档**（j=0..199）：entry rng=**737_001+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；"
    "exit rng=**739_001+j**（法典 \u00a74 W327 行 B=739_001..739_200·**1-HOP own-A RESERVATION CASCADE·落位紧贴本波 A 尾形态**："
    "B naive 续带 735_701..735_900（自注册 W326 B 尾 735_700+1 续）在席位窗宇宙（post-W326-REGISTERED 终态注册）起点即 REFUSED"
    "——本波 A 已整体跳至 naive B 窗之上（737_001..739_000·B_naive_below_own_A=true），故 B 按 own-A reservation cascade "
    "上移至 own-A 尾+1（probe leg1 B_semantics 机证·B_naive_inside_own_A=false）→落 739_001..739_200·**hops=1（cascade 跳）**·"
    "**B_seed_hop_disclosure=[]（cascade 落位零注册种子拒·连续第二波空披露）**·**B 落位 base==own-A 尾+1 机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_base_eq_own_A_tail_plus1=true·第八十一次连续 above-own-A 落位如实注记）"
    "·非转录 r587·ADMIT 回执在场）；p_exit=`P_EXIT=0.05`。")

S5PROJ_NEW = (
    "5. **W328+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive **740_501..742_500**（hops=1·first_clean 同窗·pre-W327 宇宙）；"
    "B naive **739_201..739_400**（hops=0·first_clean 同窗·lands_inside_W328p_A_naive=false）"
    "——**post-W327-REGISTERED 预披露：W327 A 带 737_001..739_000 与 B 带 739_001..739_200 注册后 W328 拒面必变"
    "（A 自 W327 A 尾 739_000 续·B 自 W327 B 尾 739_200 续），且 B 落位形态须按 A 是否跳至 naive B 之上/之内/之下三面分别判读"
    "（W326 起 b_placement 三面腿）——W328 冻结方禁假设 A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·"
    "须 post-W327 活 derive 且 derive B 时预留本波 A 窗，hop 链逐跳在 probe 回执（读回执须 B_hop_chain 与 "
    "B_seed_hop_disclosure 两面同读）。")

swap("**A-ext seed=", "\u975e\u8f6c\u5f55 r587 \u524d\u5411\u5355\u8c03\u65ad\u8a00\u5728\u8d70\u518c\uff1b", AEXT_NEW, "AEXT")
swap("**B-ext exit seed=", "\u975e\u8f6c\u5f55 r587\uff09\uff1b", BEXT_NEW, "BEXT")
swap("**W325 prereg \u00a75 item5", "\uff08\u89c1 \u00a75 item5\uff09\u3002", HDRPROJ_NEW, "HDRPROJ")
swap("\uff08\u5e2d\u4f4d\u516c\u793a=" + "MSG-20261025-0655-bmc-w326-seat", "never transcribe r587**\uff09\uff09\uff1b",
     S0SEAT_NEW, "S0SEAT")


def swap_line(prefix, fresh, label):
    global out
    i = out.find(prefix)
    assert i > 0, "%s: line prefix not found" % label
    j = out.find("\n", i)
    assert j > i, "%s: line end not found" % label
    sent = "ZZ" + re.sub(r"[^A-Z]", "", label.upper())
    assert sent not in out and sent not in stash
    stash[sent] = fresh
    out = out[:i] + sent + out[j:]
    print("SWAPL %-8s old_len=%d new_len=%d" % (label, j - i, len(fresh)))


swap_line("- **A \u6863**", S3A_NEW, "S3A")
swap_line("- **B \u6863**", S3B_NEW, "S3B")
swap_line("5. **W327+ \u6295\u5f71", S5PROJ_NEW, "S5PROJ")

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
assert SEC8.count("W326") >= 1 and "lands_inside" in SEC8, "sec.8 template drift"
out = out[:i8] + "ZZSECS" + out[i8_end:]

# ---------------------------------------------------------------- 2. wave labels +1 (W>=304)
out = wave_bump(out)

# ---------------------------------------------------------------- 3. numeric / ordinal / artifact maps
NUM = [
    # --- ledger / pool anchors
    ("1,139,341", "1,141,541"),
    ("1,137,141", "1,139,341"),
    ("K=712,920", "K=715,120"),
    ("K712,920", "K715,120"),
    ("712,920+2,200", "715,120+2,200"),
    ("712,920", "715,120"),
    # --- merged / wave-only statistics
    ("0.09286797", "0.09286986"),
    ("0.24522319", "0.24522974"),
    ("0.09491177", "0.09348227"),
    ("0.00204380", "0.00061241"),
    ("0.3303", "0.3203"),
    ("line_pre_w325 1.2021", "line_pre_w326 1.2022"),
    ("1.2021", "1.2023"),
    # --- wave / row / seed ordinals
    ("\u6c60\u7b2c 324 \u679a", "\u6c60\u7b2c 325 \u679a"),
    ("\u884c 315 \u6ce8\u518c\u5728\u518c", "\u884c 316 \u6ce8\u518c\u5728\u518c"),
    ("bmc rows 144+\u5019\u9009=\u7b2c 145 \u679a", "bmc rows 145+\u5019\u9009=\u7b2c 146 \u679a"),
    ("bmc_rows=144", "bmc_rows=145"),
    ("bmc live rows 144", "bmc live rows 145"),
    ("\u7b2c\u4e00\u767e\u56db\u5341\u56db\u679a", "\u7b2c\u4e00\u767e\u56db\u5341\u4e94\u679a"),
    ("engine_owner==bm-c 139 \u884c\u6ce8\u518c", "engine_owner==bm-c 145 \u884c\u6ce8\u518c"),
    ("\u5f15\u64ce\u7ebf\u7b2c 316 \u6ce2", "\u5f15\u64ce\u7ebf\u7b2c 317 \u6ce2"),
    ("\u6ce2\u53f7 324=", "\u6ce2\u53f7 325="),
    ("\u4e09\u767e\u4e8c\u5341\u9762", "\u4e09\u767e\u4e8c\u5341\u4e00\u9762"),
    ("CLEAN-AT-BIRTH 57th gen", "CLEAN-AT-BIRTH 58th gen"),
    ("\u6ce8\u518c\u8868 W325 \u884c", "\u6ce8\u518c\u8868 W326 \u884c"),
    # --- runner / artifact names
    ("--wave 326", "--wave 327"),
    ("n1_w325", "n1_w326"),
    ("n1_w326", "n1_w327"),
    ("_w325bmc_", "_w326bmc_"),
    ("_w326bmc_", "_w327bmc_"),
    ("_w325bmc_freeze_edits.py \u6a21\u677f\u6d3e\u751f", "_w326bmc_freeze_edits.py \u6a21\u677f\u6d3e\u751f"),
    ("MSG-20261025-0655-bmc-w326-seat", SEAT_MSG),
    # --- commit shas (prior splice / seat chain)
    ("658979c049", PREV_SPLICE_SHA),
    ("e0e7e5786b", SEAT_SHA),
    # --- window clock / round labels
    ("06:5x", "07:5x"),
    ("07:1x", "08:3x"),
    ("r1231", "r1233"),
    ("r1232", "r1234"),
    ("r1233", "r1235"),
]
NUM = [(a, b) for a, b in NUM if a != b]

counts = {}
for a, b in NUM:
    counts[a] = out.count(a)
print("COUNT TABLE (key -> occurrences):")
for a, _ in sorted(NUM, key=lambda kv: -len(kv[0])):
    print("  key=%s -> %d" % (a.encode("ascii", "backslashreplace").decode(), counts[a]))
CRITICAL = ["1,139,341", "K=712,920", "712,920", "\u6c60\u7b2c 324 \u679a", "--wave 326",
            "n1_w326", "_w326bmc_", "0.09286797", "0.3303", "r1233"]
zero_crit = [k for k in CRITICAL if counts.get(k, 0) == 0]
assert not zero_crit, "critical keys with zero hits: %r" % zero_crit
DROPPED = [a for a in counts if counts[a] == 0]
if DROPPED:
    print("DROPPED (zero-hit, not present in this source face): %r"
          % [d.encode("ascii", "backslashreplace").decode() for d in DROPPED])
NUM = [(a, b) for a, b in NUM if counts[a] > 0]
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
# Every band face must live inside a swapped block or the parked prior-wave
# sec.7/sec.8 body (r1184/r1208 family). A residual token means a band face was
# not covered by an explicit swap -> fail closed.
assert nband == 0, "residual band tokens not covered by swapped blocks: %r" % sorted(set(TOK.findall(out)))
print("band tokens rolled: 0 (all band faces written as final values in swapped blocks)")

for sent, txt in stash.items():
    assert out.count(sent) == 1, "sentinel %s count %d" % (sent, out.count(sent))
    out = out.replace(sent, txt)

# ---------------------------------------------------------------- 5. sec.7 / sec.8 rebuild
assert out.count("ZZSEC7") == 1
out = out.replace("ZZSEC7\n", SEC7_NEW)

SEC8_NEW = (
    "## \u00a78 \u6279\u540e\u590d\u76d8\u3002\u3010finalize \u540c\u7a97\u56de\u586b\u3011\n"
    "- \u00a75.5 W328+ \u6295\u5f71\u627f\u63a5\u673a\u8bc1\uff08\u672c\u5e2d receipt "
    "`results/_w327bmc_20261025_probe_receipt.json` leg4\uff0cpre-W327 \u5b87\u5b99\uff09\uff1a"
    "A naive **740_501..742_500** clean\uff08hops=1\u00b7first_clean \u540c\u7a97\uff09\u3001"
    "B naive **739_201..739_400** clean\uff08hops=0\u00b7first_clean \u540c\u7a97\u00b7"
    "lands_inside_W328p_A_naive=false\uff09\u2014\u2014**W328 \u51bb\u7ed3\u65b9\u5fc5\u987b\u5728 post-W327 "
    "\u5b87\u5b99\u91cd live derive \u4e14\u5728 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97"
    "\uff08W141 \u5148\u4f8b\uff09\u00b7\u4e14\u9700\u6309 above/inside/below \u4e09\u9762\u5224\u8bfb B\uff08W326 \u8d77\u7684\u65b0\u5f62\u6001\uff09"
    "\u00b7never transcribe r587**\u3002\n"
    "- \u672c\u7a97\u5e2d\u4f4d\u5b9e\u6d4b\u673a\u8bc1\uff08post-W326-REGISTERED \u5b87\u5b99\uff0cowner_rows=316\uff09\uff1a"
    "A **737,001..739,000**\uff0880th \u8fde\u7eed A-hop\u00b7hops=1\u00b7naive \u8d77\u70b9 735,501 \u88ab\u6ce8\u518c W326 B \u5e26 "
    "735_501..735_700 \u4e0e\u4e09\u70b9\u6ce8\u518c\u79cd\u5b50 736_000/736_500/737_000 \u62d2\u00b7base = FIRST CLEAN WINDOW\uff09\uff0f"
    "B **739,001..739,200**\uff0881th \u8fde\u7eed above-own-A\u00b7hops=1\u00b7\u8fde\u7eed\u7b2c\u4e8c\u6ce2 BELOW \u9762 "
    "\u2192 cascade \u8d34 own-A \u5c3e+1\u00b7B_seed_hop_disclosure=[]\uff09\u2014\u2014"
    "`results/_w327bmc_20261025_probe_receipt.json` verdict ADMIT\u00b7relation_asserts "
    "A_base_ge_priorB_tail_plus1=true / B_base_eq_own_A_tail_plus1=true / AB_mutual_exclusion=true\u00b7"
    "seed_admit_gate FREE x2\u00b7leg3 bands_clear=True\u00b7leg0 bmc_rows=145 / ordinal=317\u3002\n"
    "- \u672c\u6ce2\u5e2d\u4f4d live \u4e8b\u5b9e\uff1aA \u7b97\u672f\u7eed\u5e26 735,501..737,500 \u5728\u5e2d\u4f4d\u7a97\u8d77\u70b9\u5373\u88ab\u62d2"
    "\uff08\u6ce8\u518c W326 B \u5e26 + \u4e09\u70b9\u6ce8\u518c\u79cd\u5b50\uff09\u2192 walk \u81f3\u9996\u51c0\u7a97 737,001..739,000\uff1b"
    "B \u7b97\u672f\u7eed\u5e26 735,701..735,900 \u6574\u6bb5\u843d own-A \u4e4b\u4e0b\uff08\u672c\u6ce2 A \u5df2\u8df3\u81f3\u5176\u4e0a\uff09"
    "\u2192 cascade \u81f3 own-A \u5c3e+1 = 739,001..739,200\uff0c\u96f6\u79cd\u5b50\u8ba9\u4f4d\u3002\n"
    "- \u5b9d\u85cf\u4e0e\u65b9\u6cd5\u8bba\u6355\u83b7\u95ee\uff1a\u672c\u6ce2=nulls-deepening \u5e38\u6001\u52a0\u6df1\uff0c"
    "**\u65e0\u65b0\u65b9\u6cd5/\u65e0\u65b0\u5b9d\u85cf**\uff1b\u9664\u975e finalize \u540c\u7a97\u53d1\u73b0\u65b0\u9762\uff0c"
    "knowledge/METHODOLOGY_ASSETS.md \u4e0e TREASURE_REGISTRY.json \u5747\u4e0d\u8ffd\u52a0\u3002\n"
    "- \u8bda\u5b9e\u62ab\u9732\uff08finalize \u540c\u7a97\u56de\u586b\uff09\uff1a\n"
    "  \u2460 \u672c\u51bb\u7ed3\u65f6\u70b9\u65e0\u5f85\u62ab\u9732\u9879\uff1b\u56de\u586b\u65f6\u82e5\u53d1\u73b0 prose \u504f\u5dee\uff0c"
    "\u4e00\u5f8b\u4ee5\u673a\u8bfb\u503c\u4e3a\u51c6\u5e76\u62ab\u9732\u3001\u4e0d\u62b9\u5e73\u3002\n"
    "  \u2461 \u5ef6\u7eed\u524d\u6ce2\u62ab\u9732\u9762\uff08W326 \u00a78 \u2460/W326 \u884c\u6ce8\u91ca heal \u9762\uff09\u2014\u2014"
    "\u672c\u6ce2\u884c\u5185\u6ce8\u91ca\u4e0e materializer \u65ad\u8a00\u5747\u6309 W327 \u673a\u5668\u9762\u76f4\u5199\uff0c\u5e76\u7531 six-gate "
    "\u884c\u8303\u56f4 stale-clause \u95e8\u590d\u6838\u3002\n"
    "- \u5751\u5f8b\u6355\u83b7\uff08finalize \u540c\u7a97\u56de\u586b\uff09\uff1a\n"
    "  \u2460 **B \u843d\u4f4d BELOW \u9762\u8fde\u7eed\u4e8c\u6ce2**\uff1a\u5f53 A \u9762\u6574\u4f53\u8df3\u81f3 naive B \u7a97\u4e4b\u4e0a\u65f6\uff0c"
    "B \u843d\u4f4d\u5f62\u6001\u4e0e above/inside \u4e24\u9762\u4e0d\u540c\uff1b\u8bfb\u56de\u6267\u5fc5\u987b\u540c\u65f6\u770b "
    "B_naive_below_own_A / B_naive_inside_own_A / B_seed_hop_disclosure \u4e09\u9762\u3002\n"
    "  \u2461 \u884c\u6570\u5b88\u5361\uff08\u51bb\u7ed3\u4ef6\u7ed3\u6784\u5b8c\u6574\u6027\uff09\uff1a\u590d\u5efa \u00a77/\u00a78 "
    "\u5757\u540e\u884c\u6570\u5fc5\u987b\u4e0e\u6e90\u9762\u4e00\u81f4\uff0c\u4e0d\u4e00\u81f4=\u7ed3\u6784\u6f02\u79fb\u3001\u76f4\u63a5\u62a5\u6b7b\u3002\n"
    "  \u2462 **\u6295\u5f71\u9762\u4e0e\u5b9e\u7b97\u9762\u8d77\u70b9\u53ef\u4e0d\u540c**\uff1a\u672c\u6ce2 A \u843d\u4f4d\u7a97\u4e0e W326 \u6295\u5f71\u540c\u7a97\uff0c"
    "\u4f46\u6295\u5f71\u540d\u4e49 naive \u4e0e\u5b9e\u7b97\u7eed\u5e26\u8d77\u70b9\u4e0d\u4e00\u81f4\uff08\u5b9e\u7b97\u81ea own A \u5c3e\u7eed\uff09\u2014\u2014"
    "\u4e24\u9762\u540c\u8bfb\u3001\u7981\u4ee5\u6295\u5f71\u4ee3\u66ff ADMIT \u673a\u8bc1\u3002\n"
    "  \u2463 **\u884c\u5185 law \u6ce8\u91ca\u9762\u62a4\u680f\u5ef6\u7eed\u5728\u5f79**\uff08E94\uff09\uff1aW327 \u51bb\u7ed3\u884c\u5185 A/B law \u6ce8\u91ca\u4e0e materializer \u65ad\u8a00\u4e00\u5f8b\u6309\u672c\u6ce2\u673a\u5668\u9762\u76f4\u5199\uff0c\u884c\u8303\u56f4 stale-clause \u95e8\u590d\u6838\u4e3a\u96f6\u547d\u4e2d\u3002\n"
    "- \u6536\u53e3\u7eaa\u5f8b\uff1afinalize \u53ea\u6d88\u8d39\u5728\u518c\u5206\u7247\uff08audit.finalize_only=true\uff09\uff0c"
    "\u672c\u6ce2\u96f6\u91cd\u70e7\u3001\u96f6\u53cc\u70e7\uff1bS6 \u94fe\u4e0e\u8f6e\u6536\u53e3\u540c\u7a97\u3002\n\n"
)
assert out.count("ZZSECS") == 1
out = out.replace("ZZSECS", SEC8_NEW)

# ---------------------------------------------------------------- 5b. post-fixes (live readings this window)
POST = [
    ("\u672c\u7a97 free RAM 6.3GB", "\u672c\u7a97 free RAM " + FREE_RAM + "GB"),
]
for old, new in POST:
    n = out.count(old)
    assert n >= 1, "post-fix %r hits=%d" % (old[:40], n)
    out = out.replace(old, new)
    print("post-fix applied hits=%d" % n)

# ---------------------------------------------------------------- 6. asserts
assert out.count("\n") == 82, "line count changed: %d" % out.count("\n")
assert out.count("737_001..739_000") >= 3, "new A band missing"
assert out.count("739_001..739_200") >= 4, "new B band missing"
assert out.count("735_501..737_500") >= 2, "A naive continuation missing"
assert out.count("735_701..735_900") >= 2, "B naive continuation missing"
assert out.count("W327") > 30 and out.count("W328") > 5
assert out.count("W304 bm-c") == src.count("W304 bm-c"), "rotation chain must not roll"
assert out.count("1,141,541") >= 3, "new ledger anchor missing"
assert out.count("ZQ") == 0
assert out.count("n1_w326") >= 4 and out.count("n1_w327") >= 1
assert out.count("n1_w325") == 0, "n1 double roll"
assert out.count(SEAT_SHA) >= 3
assert out.count(SEAT_MSG) >= 3
assert out.count("CLEAN-AT-BIRTH 58th gen") == 1
assert out.count("r1235") >= 5, "round labels"
assert out.count("_w327bmc_20261025_probe_receipt.json") >= 1
assert out.count("W326-only") >= 1  # sec.7 prior-wave block intact
assert out.count("ZZ") == 0, "sentinel leaked"
assert out.count("B_seed_hop_disclosure=[]") >= 2, "empty seed-hop disclosure face missing"
assert out.count("B_naive_below_own_A=true") >= 2, "below-own-A disclosure face missing"

receipt = {"keys": counts, "dropped": [d.encode("ascii", "backslashreplace").decode() for d in DROPPED],
           "band_tokens": nband,
           "bytes_src": len(raw), "bytes_out": len(out.encode("utf-8"))}
open("results/_w327bmc_derive_counts.json", "w", encoding="utf-8").write(
    json.dumps(receipt, ensure_ascii=False, indent=1))
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(out)
b = out.encode("utf-8")
print("WROTE %s bytes=%d lines=%d sha16=%s bands=%d keys=%d" % (
    OUT, len(b), out.count("\n"), hashlib.sha256(b).hexdigest()[:16], nband, len(NUM)))