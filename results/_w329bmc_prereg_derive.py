# -*- coding: utf-8 -*-
"""W329 prereg derive (bm-c r1239).

Canon-clone of the W328 POST-RUN face (git HEAD:research/PERPETUAL_N1_W328_PREREG.md)
-> research/PERPETUAL_N1_W329_PREREG.md.

Cumulative-history chains (se_mu narrowing, own-turn rotation, RAM freeze chain) are
PARKED behind pure-letter sentinels and EXTENDED by one entry (never rolled).
Blocks whose landing law differs this wave are swapped with freshly written text
after the band roll:
  * A: 1-HOP WALK, 82nd consecutive A-hop. Arithmetic continuation 742_501..744_500
    (W328 A tail 742_500) is REFUSED at start by the registered W328 B band
    742_501..742_700 AND the registered seed POINT 742_501
    -> first clean window 742_701..744_700 (base == prior-B tail+1 EXACT here).
  * B: FIRST INSIDE face (prior three waves were BELOW). Naive 742_701..742_900 sits
    wholly INSIDE this wave's own-A 742_701..744_700 -> own-A reservation cascade to
    own-A tail+1 = 744_701..744_900, EMPTY seed-hop disclosure, 83rd above-own-A.
Usage: python results/_w329bmc_prereg_derive.py [--measure]
"""
import hashlib
import json
import io
import re
import subprocess
import sys

SRC_REV = "HEAD"
SRC_PATH = "research/PERPETUAL_N1_W328_PREREG.md"
OUT = "research/PERPETUAL_N1_W329_PREREG.md"
SEAT_MSG = "MSG-20261025-1005-bmc-w329-seat"
SEAT_SHA = "94c710026c"
PREV_SPLICE_SHA = "91e318867f"
FREE_RAM = "5.6"
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
res = json.load(io.open("results/perpetual_faces/n1_w328_results.json", encoding="utf-8"))
led = res["science_gates"]["ledger"]
assert led["total"] == 1145941 and led["prev_total"] == 1143741, "ledger anchor drift"
cum = res["null_pool_cumulative"]
assert cum["merged"]["n_values"] == 719520, "merged K drift"
assert abs(cum["merged"]["mu"] + 0.09285873790860574) < 1e-12
assert abs(cum["merged"]["sigma"] - 0.24520372204969282) < 1e-12
assert cum["se_mu_at_k719520"] == 0.000289
assert abs(cum["w328_only"]["mu"] + 0.08770218181818182) < 1e-9
assert abs(cum["w328_only"]["sigma"] - 0.24034611459719468) < 1e-12
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_719520"] == 1.2023 and kl["line_pre_w328"] == 1.2024
assert kl["line_delta_k_lift"] == -0.0001
assert kl["n_eff_held_equal"] == 1143741
assert abs(res["families"]["A_random_engine_exit"]["full_sharpe_p95"] - 0.31) < 1e-12
assert abs(res["families"]["A_random_engine_exit"]["full_sharpe_p99"] - 0.4404) < 1e-12
DELTA = abs(cum["w328_only"]["mu"] - cum["merged"]["mu"])
assert abs(DELTA - 0.00515656) < 1e-6, DELTA
seed = json.load(io.open("results/_w329bmc_20261025_probe_receipt.json", encoding="utf-8"))
assert seed["verdict"] == "ADMIT"
l1 = seed["legs"]["leg1"]
assert l1["A"] == [742701, 744700] and l1["B"] == [744701, 744900]
assert l1["ARITH_A"] == [742501, 744500] and l1["ARITH_B"] == [742701, 742900]
assert l1["hops_A"] == 1 and l1["hops_B"] == 1
assert l1["B_seed_hop_disclosure"] == []
ra = l1["relation_asserts"]
assert ra["B_naive_inside_own_A"] is True and ra["B_naive_below_own_A"] is False
assert ra["A_base_ge_priorB_tail_plus1"] is True
assert ra["B_base_eq_own_A_tail_plus1"] is True
assert ra["B_base_eq_first_clean_above_own_A"] is True
assert ra["AB_mutual_exclusion"] is True
refs = l1["A_hop_chain"][0]["refuser_pts_sample"]
assert refs == [742501], refs
l4 = seed["legs"]["leg4"]
assert l4["W330p_A_naive"] == "744_701..746_700"
assert l4["W330p_B_naive"] == "744_901..745_100"
assert l4["hops_A"] == 0 and l4["hops_B"] == 0
assert l4["W330p_B_lands_inside_W330p_A_naive"] is True
assert seed["legs"]["leg0"]["owner_rows"] == 318
assert seed["legs"]["leg0"]["bmc_rows"] == 147
assert seed["ordinals"]["a_hop"] == 82 and seed["ordinals"]["above_own_a"] == 83
print("facts OK: ledger 1,145,941 / K 719,520 / W328-only mu -0.08770218 / p95 0.3100 / delta %.8f" % DELTA)

# ---------------------------------------------------------------- 0. prior-wave S7 block (verbatim from HEAD)
j7 = src.find("## \u00a77")
j8 = src.find("## \u00a78")
assert 0 < j7 < j8, "HEAD sec.7 block not found"
SEC7_NEW = src[j7:j8]
assert "W328-only" in SEC7_NEW and "1,145,941" in SEC7_NEW
assert SEC7_NEW.count("\n") == 10, "sec.7 line count drift: %d" % SEC7_NEW.count("\n")

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
    old_tail = "\u2192W328 " + PROJ + " 0.000289"
    assert old_tail in old, "se chain tail not the expected W328 projection"
    return old.replace(old_tail,
                       "\u2192W328 **0.000289**\u2192W329 " + PROJ + " 0.000289")


def rot(old):
    assert "\u2192W328 bm-c own-turn rotation" in old, "own-turn tail not W328"
    return old.replace("\u2192W328 bm-c own-turn rotation",
                       "\u2192W328 bm-c\u2192W329 bm-c own-turn rotation", 1)


def ram(old):
    m = re.search(r"\u00b7\u672c\u7a97" + FREEZE + r" ~([\d.]+)G bm-c " + ANCHOR + r"\uff09", old)
    assert m, "RAM chain tail not found"
    new = ("\u00b7W328 " + FREEZE + " ~" + m.group(1) + "G bm-c " + ANCHOR +
           "\u00b7\u672c\u7a97" + FREEZE + " ~" + FREE_RAM + "G bm-c " + ANCHOR + "\uff09")
    return old[:m.start()] + new + old[m.end():]


park(r"W277 \*\*0\.000314\*\*[^\n]*?\u6295\u5f71 0\.000289", se, "SECH")
park(r"W288 bm-c(?:\u2192W\d{3} bm-c)* own-turn rotation", rot, "ROTCH")
park(r"W206/W211[^\n]*?" + ANCHOR + "\uff09", ram, "RAMCH")

# ---------------------------------------------------------------- swapped blocks (final coordinates)
AEXT_NEW = (
    "**A-ext seed=742_701..744_700**（**A 面=STAIRCASE-AFFECTS-A·1-HOP WALK 形态"
    "（W239 staircase era 后第八十二次连续 A-hop）**：A 面算术续带 742_501..744_500"
    "（自注册 W328 A 尾 742_500 续）在席位窗宇宙（post-W328-REGISTERED 终态注册）起点即 REFUSED"
    "（拒面机证：注册 W328 B 带 742_501..742_700 落 naive A 窗内 + 注册种子点 742_501 一点）"
    "→walk 越全部拒点→A first-clean **742_701..744_700**·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（742_700+1）恒等关系（本波 == 恒等·A 面连续第四波首净窗落位形态·如实披露）**"
    "（A_hop_chain 1 跳 verbatim leg1 机证〔window 742_501..744_500→jump 742_701·"
    "refuser bands 742_501..742_700/742_501..742_501〕·A_clean_at_naive_start=false）"
    "·非转录 r587 前向单调断言在走册\uff1b")

BEXT_NEW = (
    "**B-ext exit seed=744_701..744_900**（**B 面=1-HOP own-A RESERVATION CASCADE·落位紧贴本波 A 尾"
    "（第八十三次连续 above-own-A 落位·**首现 INSIDE 面**）**：B naive 续带 742_701..742_900（自注册 W328 B 尾 742_700+1 续）"
    "在席位窗宇宙（post-W328-REGISTERED 终态注册）起点即 REFUSED——本波 A 窗 742_701..744_700 整段覆盖 naive B 窗"
    "（B_naive_inside_own_A=true 机证·B_naive_below_own_A=false），故 B 面按 own-A reservation cascade "
    "强制上移至 own-A 尾+1→**B 落位 744_701..744_900**·"
    "**hops=1（cascade 跳）**·**B_seed_hop_disclosure=[]（本波 cascade 落位零注册种子拒·连续第四波空披露）**·"
    "**B 落位 base==own-A 尾+1（744_700+1）机检关系**（B_hop lands-inside-A=false·B_lands_above_own_A=true·"
    "B_base_eq_own_A_tail_plus1=true·B_base_eq_first_clean_above_own_A=true·probe 回执 leg1 机证·非转录 r587\uff09\uff1b")

HDRPROJ_NEW = (
    "**W328 prereg \u00a75 item5 投影承接面注记兑现+首现 INSIDE 面**：投影预言 W329 A naive 742_501..744_500（hops=0）、"
    "B naive 742_701..742_900（hops=0·lands_inside_W329p_A_naive=true）——本窗 live re-derive 的 A naive 起点 742_501 "
    "被注册 W328 B 带 742_501..742_700 与注册种子点 742_501 拒（投影 hops=0 **未兑现**，如实披露），故 A 落位为 first-clean "
    "742_701..744_700（hops=1·base==prior-B 尾+1 恒等）；B naive 整段落 own-A 之**内**（投影 INSIDE 面兑现，"
    "连续第三波 BELOW 面就此终止），B 按 reservation cascade 上移贴 own-A 尾 744_701..744_900"
    "（cascade 落位零种子让位·B_seed_hop_disclosure=[]）；**W326 起 B 落位形态三面（above/inside/below）判读律本波第四次适用、"
    "INSIDE 面首次现场适用**，如实披露。"
    "R308：W329 带（A 742_701..744_700/B 744_701..744_900）注册后对 W330+ 的拒面影响=本波冻结方 leg4 前瞻已机证（见 \u00a75 item5）。")

S0SEAT_NEW = (
    "（席位公示=" + SEAT_MSG + " 已推 origin " + SEAT_SHA + " r565 律（bm-c r1238 席位窗发布·queue-head seat-first lane）·"
    "probe W330+ 投影（pre-W329 宇宙·leg4）A naive **744_701..746_700**（hops=0·first_clean 同窗）·"
    "B naive **744_901..745_100**（hops=0·first_clean 同窗·**lands_inside_W330p_A_naive=true**——INSIDE 面连续第二波投影）"
    "——**post-W329-REGISTERED 预披露：W329 A 带 742_701..744_700 与 B 带 744_701..744_900 注册后，W330 的算术续带拒面必变；"
    "W330 冻结方必须 post-W329 活 derive 且 derive B 时预留本波 A 窗，并复核 B 三面落位（above/inside/below）与注册种子让位规则·"
    "W141 先例·never transcribe r587**）\uff09\uff1b")

S3A_NEW = (
    "- **A 档**（j=0..1,999）：entry rng seed=**742_701+j**（法典 \u00a74 W329 行 A=742_701..744_700·"
    "**STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第八十二次连续 A-hop）**：A 算术续带 742_501..744_500"
    "（自注册 W328 A 尾 742_500 续）在席位窗宇宙（post-W328-REGISTERED 终态注册）起点即 REFUSED"
    "（注册 W328 B 带 742_501..742_700 落 naive A 窗内 + 注册种子点 742_501=W328 prereg \u00a75 item5 "
    "post-W328-REGISTERED pre-disclosure 承袭·r587）→walk 越全部拒点→A first-clean 742_701..744_700·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（742_700+1）恒等关系（本波 == 恒等）**"
    "（A_hop_chain 1 跳 verbatim probe leg1 机证·A_clean_at_naive_start=false）·非转录 r587·ADMIT 回执在场）；"
    "p=`BASELINE_P[(j//50)%2]`（v1 50-seed 块交替惯例逐字）；随机入场短窗=**引擎退出口**（v1 设计逐字）。")

S3B_NEW = (
    "- **B 档**（j=0..199）：entry rng=**742_701+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；"
    "exit rng=**744_701+j**（法典 \u00a74 W329 行 B=744_701..744_900·**1-HOP own-A RESERVATION CASCADE·落位紧贴本波 A 尾·INSIDE 面形态**："
    "B naive 续带 742_701..742_900（自注册 W328 B 尾 742_700+1 续）在席位窗宇宙（post-W328-REGISTERED 终态注册）起点即 REFUSED"
    "——本波 A 窗 742_701..744_700 整段覆盖 naive B 窗（B_naive_inside_own_A=true·B_naive_below_own_A=false），故 B 按 own-A reservation cascade "
    "上移至 own-A 尾+1（probe leg1 B_semantics 机证）→落 744_701..744_900·**hops=1（cascade 跳）**·"
    "**B_seed_hop_disclosure=[]（cascade 落位零注册种子拒·连续第四波空披露）**·**B 落位 base==own-A 尾+1 机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_base_eq_own_A_tail_plus1=true·第八十三次连续 above-own-A 落位如实注记）"
    "·非转录 r587·ADMIT 回执在场）；p_exit=`P_EXIT=0.05`。")

S5PROJ_NEW = (
    "5. **W330+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive **744_701..746_700**（hops=0·first_clean 同窗·pre-W329 宇宙）；"
    "B naive **744_901..745_100**（hops=0·first_clean 同窗·**lands_inside_W330p_A_naive=true**）"
    "——**post-W329-REGISTERED 预披露：W329 A 带 742_701..744_700 与 B 带 744_701..744_900 注册后 W330 拒面必变"
    "（A 自 W329 A 尾 744_700 续·B 自 W329 B 尾 744_900 续），且 B 落位形态须按 A 是否跳至 naive B 之上/之内/之下三面分别判读"
    "（W326 起 b_placement 三面腿）——W330 冻结方禁假设 A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·"
    "须 post-W329 活 derive 且 derive B 时预留本波 A 窗，hop 链逐跳在 probe 回执（读回执须 B_hop_chain 与 "
    "B_seed_hop_disclosure 两面同读）。")

swap("**A-ext seed=", "\u975e\u8f6c\u5f55 r587 \u524d\u5411\u5355\u8c03\u65ad\u8a00\u5728\u8d70\u518c\uff1b", AEXT_NEW, "AEXT")
swap("**B-ext exit seed=", "\u975e\u8f6c\u5f55 r587\uff09\uff1b", BEXT_NEW, "BEXT")
swap("**W327 prereg \u00a75 item5", "\uff08\u89c1 \u00a75 item5\uff09\u3002", HDRPROJ_NEW, "HDRPROJ")
swap("\uff08\u5e2d\u4f4d\u516c\u793a=" + "MSG-20261025-0910-bmc-w328-seat", "never transcribe r587**\uff09\uff09\uff1b",
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
swap_line("5. **W329+ \u6295\u5f71", S5PROJ_NEW, "S5PROJ")

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
assert SEC8.count("W329") >= 1 and "lands_inside" in SEC8, "sec.8 template drift"
SEC8_NLINES = SEC8.count("\n")
out = out[:i8] + "ZZSECS" + out[i8_end:]

# ---------------------------------------------------------------- 2. wave labels +1 (W>=304)
out = wave_bump(out)

# ---------------------------------------------------------------- 3. numeric / ordinal / artifact maps (POST-BUMP form)
NUM = [
    # --- ledger / pool anchors
    ("1,143,741", "1,145,941"),
    ("K=717,320", "K=719,520"),
    ("717,320+2,200", "719,520+2,200"),
    ("717,320", "719,520"),
    # --- merged / wave-only statistics
    ("0.09287455", "0.09285874"),
    ("0.24521847", "0.24520372"),
    ("0.09439882", "0.08770218"),
    ("0.00152427", "0.00515656"),
    ("0.2977", "0.3100"),
    ("line_pre_w327 1.2023", "line_pre_w328 1.2024"),
    ("+0.0000", "-0.0001"),
    # --- wave / row / seed ordinals
    ("\u6c60\u7b2c 326 \u679a", "\u6c60\u7b2c 327 \u679a"),
    ("\u884c 317 \u6ce8\u518c\u5728\u518c", "\u884c 318 \u6ce8\u518c\u5728\u518c"),
    ("bmc rows 146+\u5019\u9009=\u7b2c 147 \u679a", "bmc rows 147+\u5019\u9009=\u7b2c 148 \u679a"),
    ("bmc_rows=146", "bmc_rows=147"),
    ("bmc live rows 146", "bmc live rows 147"),
    ("\u7b2c\u4e00\u767e\u56db\u5341\u516d\u679a", "\u7b2c\u4e00\u767e\u56db\u5341\u4e03\u679a"),
    ("engine_owner==bm-c 146 \u884c\u6ce8\u518c", "engine_owner==bm-c 147 \u884c\u6ce8\u518c"),
    ("\u5f15\u64ce\u7ebf\u7b2c 318 \u6ce2", "\u5f15\u64ce\u7ebf\u7b2c 319 \u6ce2"),
    ("\u6ce2\u53f7 326=", "\u6ce2\u53f7 327="),
    ("\u4e09\u767e\u4e8c\u5341\u4e8c", "\u4e09\u767e\u4e8c\u5341\u4e09"),
    ("CLEAN-AT-BIRTH 59th gen", "CLEAN-AT-BIRTH 60th gen"),
    # --- runner / artifact names
    ("--wave 328", "--wave 329"),
    ("n1_w327", "n1_w328"),
    ("n1_w328", "n1_w329"),
    ("_w327bmc_", "_w328bmc_"),
    ("_w328bmc_", "_w329bmc_"),
    ("MSG-20261025-0910-bmc-w328-seat", SEAT_MSG),
    # --- commit shas (prior splice / seat chain)
    ("322778b1a8", PREV_SPLICE_SHA),
    ("2850deab05", SEAT_SHA),
    # --- window clock / round labels
    ("08:3x", "09:3x"),
    ("09:2x", "10:2x"),
    ("09:0x", "10:1x"),
    ("r1235", "r1237"),
    ("r1236", "r1238"),
    ("r1237", "r1239"),
]
NUM = [(a, b) for a, b in NUM if a != b]

counts = {}
for a, b in NUM:
    counts[a] = out.count(a)
print("COUNT TABLE (key -> occurrences):")
for a, _ in sorted(NUM, key=lambda kv: -len(kv[0])):
    print("  key=%s -> %d" % (a.encode("ascii", "backslashreplace").decode(), counts[a]))
CRITICAL = ["1,143,741", "K=717,320", "717,320", "\u6c60\u7b2c 326 \u679a", "--wave 328",
            "n1_w327", "_w328bmc_", "0.09287455", "0.2977", "r1236"]
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
    print("SEC8_NLINES", SEC8_NLINES)
    sys.exit(0)

out = sub(out, dict(NUM))

# ---------------------------------------------------------------- 4. bands (all written as final values in swapped blocks)
TOK = re.compile(r"\b(\d{3})_(\d{3})\b")
residual = sorted(set(TOK.findall(out)))
# Every band face must live inside a swapped block or the parked prior-wave
# sec.7/sec.8 body (r1184/r1208 family). A residual token means a band face was
# not covered by an explicit swap -> fail closed.
assert not residual, "residual band tokens not covered by swapped blocks: %r" % residual
nband = 0
print("band tokens rolled: 0 (all band faces written as final values in swapped blocks)")

for sent, txt in stash.items():
    assert out.count(sent) == 1, "sentinel %s count %d" % (sent, out.count(sent))
    out = out.replace(sent, txt)

# ---------------------------------------------------------------- 5. sec.7 / sec.8 rebuild
assert out.count("ZZSEC7") == 1
out = out.replace("ZZSEC7\n", SEC7_NEW)

SEC8_NEW = (
    "## \u00a78 \u6279\u540e\u590d\u76d8\u3002\u3010finalize \u540c\u7a97\u56de\u586b\u3011\n"
    "- \u00a75.5 W330+ \u6295\u5f71\u627f\u63a5\u673a\u8bc1\uff08\u672c\u5e2d receipt "
    "`results/_w329bmc_20261025_probe_receipt.json` leg4\uff0cpre-W329 \u5b87\u5b99\uff09\uff1a"
    "A naive **744_701..746_700**\uff08hops=0\u00b7first_clean \u540c\u7a97\uff09\u3001"
    "B naive **744_901..745_100**\uff08hops=0\u00b7first_clean \u540c\u7a97\u00b7"
    "lands_inside_W330p_A_naive=true\u00b7**INSIDE \u9762\u8fde\u7eed\u7b2c\u4e8c\u6ce2\u6295\u5f71**\uff09\u2014\u2014"
    "**W330 \u51bb\u7ed3\u65b9\u5fc5\u987b\u5728 post-W329 \u5b87\u5b99\u91cd live derive\uff0c"
    "\u4e14\u5728 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97\uff08W141 \u5148\u4f8b\uff09\u00b7never transcribe r587**\u3002\n"
    "- \u672c\u7a97\u5e2d\u4f4d\u5b9e\u6d4b\u673a\u8bc1\uff08post-W328-REGISTERED \u5b87\u5b99\uff0cowner_rows=318\uff0c"
    "bm-c rows=147\uff0cordinal 319\uff09\uff1aA **742,701..744,700**\uff08\u7b2c 82 \u6b21\u8fde\u7eed A-hop\u00b7hops=1\u00b7"
    "naive 742,501..744,500 \u88ab\u6ce8\u518c W328 B \u5e26 742,501..742,700 \u4e0e\u6ce8\u518c\u79cd\u5b50\u70b9 "
    "['742501'] \u62d2\u00b7base=FIRST CLEAN WINDOW\uff09\uff0f"
    "B **744,701..744,900**\uff08\u7b2c 83 \u6b21\u8fde\u7eed above-own-A\u00b7hops=1\u00b7\u9996\u73b0 INSIDE \u9762 "
    "\u2192 cascade \u8d34 own-A \u5c3e+1\u00b7B_seed_hop_disclosure=[]\uff09\u2014\u2014"
    "verdict **ADMIT**\u00b7relation_asserts \u5168\u771f\u00b7seed_admit_gate FREE x2\u00b7leg3 bands_clear=True\u3002\n"
    "- \u672c\u5e2d\u4f4d live \u4e8b\u5b9e\uff1aA \u7b97\u672f\u7eed\u5e26 742,501..744,500 \u5728\u5e2d\u4f4d\u7a97\u8d77\u70b9\u5373\u88ab\u62d2"
    "\uff08\u6ce8\u518c W328 B \u5e26 + \u6ce8\u518c\u79cd\u5b50\u70b9 742,501\uff09\u2192 walk \u81f3\u9996\u51c0\u7a97 742,701..744,700\uff1b"
    "B \u7b97\u672f\u7eed\u5e26 742,701..742,900 \u6574\u6bb5\u843d own-A \u4e4b\u5185\uff08INSIDE \u9762\u9996\u73b0\uff09"
    "\u2192 cascade \u81f3 own-A \u5c3e+1 = 744,701..744,900\uff0c\u96f6\u79cd\u5b50\u8ba9\u4f4d\u3002\n"
    "- \u5b9d\u85cf\u4e0e\u65b9\u6cd5\u8bba\u6355\u83b7\u95ee\uff1a\u672c\u6ce2=nulls-deepening \u5e38\u6001\u52a0\u6df1\uff0c"
    "**\u673a\u5236\u9762\u96f6\u65b0\u589e**\uff1bE95/E96 \u5df2\u5728\u518c\u627f\u88ad\uff0c\u672c\u8f6e\u65e0\u65b0\u589e\u65b9\u6cd5\u8d44\u4ea7\uff1b"
    "TREASURE_REGISTRY.json \u4e0d\u8ffd\u52a0\uff08\u65e0\u65b0\u5b9d\u85cf\uff09\u3002\n"
    "- \u8bda\u5b9e\u62ab\u9732\uff08finalize \u540c\u7a97\u56de\u586b\uff09\uff1a\n"
    "  \u2460 \u672c\u51bb\u7ed3\u65f6\u70b9\u65e0\u5f85\u62ab\u9732\u9879\uff1b\u56de\u586b\u65f6\u82e5\u53d1\u73b0 prose \u504f\u5dee\uff0c"
    "\u4e00\u5f8b\u4ee5\u673a\u8bfb\u503c\u4e3a\u51c6\u5e76\u62ab\u9732\u3001\u4e0d\u62b9\u5e73\u3002\n"
    "  \u2461 \u627f\u88ad\u524d\u6ce2\u62ab\u9732\u9762\uff08W328 \u00a78 \u2460\u2461\uff1an_eff prose \u9648\u65e7\u9762\u5df2\u6309 E96 "
    "\u4fee\u6cd5\u5728\u672c\u6ce2 \u00a75 \u76f4\u5199\u673a\u8bfb\u503c 1,145,941\uff1bEOL \u57fa\u5e95\u9762\u7531 E95 \u5de5\u5177\u5316\uff09\u3002\n"
    "- \u5751\u5f8b\u6355\u83b7\uff08finalize \u540c\u7a97\u56de\u586b\uff09\uff1a\n"
    "  \u2460 **B \u843d\u4f4d INSIDE \u9762\u9996\u73b0**\uff1anaive B \u7a97\u6574\u6bb5\u843d own-A \u4e4b\u5185\u65f6 B \u5fc5 cascade \u81f3 own-A \u5c3e+1\uff1b"
    "\u8bfb\u56de\u6267\u987b\u540c\u8bfb B_naive_inside_own_A / B_naive_below_own_A / B_seed_hop_disclosure \u4e09\u9762\u3002\n"
    "  \u2461 \u884c\u6570\u5b88\u5361\uff08\u51bb\u7ed3\u4ef6\u7ed3\u6784\u5b8c\u6574\u6027\uff09\uff1a\u590d\u5efa \u00a77/\u00a78 "
    "\u5757\u540e\u884c\u6570\u5fc5\u987b\u4e0e\u6e90\u9762\u4e00\u81f4\uff08\u00a77=10 \u884c\u00b7\u00a78=15 \u884c\uff09\uff0c"
    "\u4e0d\u4e00\u81f4=\u7ed3\u6784\u6f02\u79fb\u3001\u76f4\u63a5\u62a5\u6b7b\u3002\n"
    "  \u2462 **\u6295\u5f71\u9762\u53ef\u672a\u5151\u73b0**\uff1a\u672c\u6ce2 A \u6295\u5f71 hops=0 \u88ab\u6ce8\u518c B \u5e26\u62d2\u800c\u672a\u5151\u73b0\uff0c"
    "\u7981\u4ee5\u6295\u5f71\u4ee3\u66ff ADMIT \u673a\u8bc1\u3002\n"
    "  \u2463 **\u91cd\u6d3b\u5fc5\u987b\u5206\u4f53\u70b9\u706b**\uff1afinalize \u5728\u524d\u53f0\u8dd1\u6ee1 5 \u5206\u949f\u65e0\u8f93\u51fa\u5373\u88ab\u5de5\u5177\u53d6\u6d88"
    "\uff08\u96f6 stdout \u7a97\uff09\uff0c\u6b63\u6cd5=DETACHED_PROCESS|CREATE_NO_WINDOW + `python -u` \u5206\u79bb\u70b9\u706b + "
    "\u8f6e\u8be2 pid/\u4ea7\u7269\uff1b\u8fdb\u7a0b\u6d3b\u7740\u3001CPU \u7d2f\u52a0\u3001\u65e5\u5fd7\u7a7a=\u6b63\u5e38\u5728\u8dd1\uff0c\u7981\u91cd\u542f\uff08\u91cd\u542f=\u8d26\u672c\u53cc\u70e7\uff09\u3002\n"
    "- \u6536\u53e3\u7eaa\u5f8b\uff1afinalize \u53ea\u6d88\u8d39\u5728\u518c\u5206\u7247\uff08audit.finalize_only \u9762\uff09\uff0c"
    "\u672c\u6ce2\u96f6\u91cd\u70e7\u3001\u96f6\u53cc\u70e7\uff1bS6 \u94fe\u4e0e\u8f6e\u6536\u53e3\u540c\u7a97\u3002\n\n")
print("SEC8_NLINES src=%d new=%d" % (SEC8_NLINES, SEC8_NEW.count("\n")))
assert SEC8_NEW.count("\n") == SEC8_NLINES, \
    "sec.8 line count drift: %d != %d" % (SEC8_NEW.count("\n"), SEC8_NLINES)
assert out.count("ZZSECS") == 1
out = out.replace("ZZSECS", SEC8_NEW)

# ---------------------------------------------------------------- 5b. post-fixes (live readings this window)
POST = [
    ("\u672c\u7a97 free RAM 4.4GB", "\u672c\u7a97 free RAM " + FREE_RAM + "GB"),
    # derived-prose arithmetic defect (r1235 family): the projection cell must be the sum
    ("=**719,520 \u6295\u5f71**", "=**721,720 \u6295\u5f71**"),
]
for old, new in POST:
    n = out.count(old)
    assert n >= 1, "post-fix %r hits=%d" % (old[:40], n)
    out = out.replace(old, new)
    print("post-fix applied hits=%d" % n)

# ---------------------------------------------------------------- 6. asserts
assert out.count("\n") == 82, "line count changed: %d" % out.count("\n")
assert out.count("742_701..744_700") >= 3, "new A band missing"
assert out.count("744_701..744_900") >= 4, "new B band missing"
assert out.count("742_501..744_500") >= 2, "A naive continuation missing"
assert out.count("742_701..742_900") >= 2, "B naive continuation missing"
assert out.count("W329") > 30 and out.count("W330") > 5
assert out.count("W304 bm-c") == src.count("W304 bm-c"), "rotation chain must not roll"
assert out.count("1,145,941") >= 3, "new ledger anchor missing"
assert out.count("ZQ") == 0
assert out.count("n1_w328") >= 4 and out.count("n1_w329") >= 1
assert out.count("n1_w327") == 0, "n1 double roll"
assert out.count(SEAT_SHA) >= 3
assert out.count(SEAT_MSG) >= 3
assert out.count("CLEAN-AT-BIRTH 60th gen") == 1
assert out.count("r1239") >= 5, "round labels"
assert out.count("_w329bmc_20261025_probe_receipt.json") >= 1
assert out.count("W328-only") >= 1  # sec.7 prior-wave block intact
assert out.count("ZZ") == 0, "sentinel leaked"
assert out.count("B_seed_hop_disclosure=[]") >= 2, "empty seed-hop disclosure face missing"
assert out.count("B_naive_inside_own_A=true") >= 2, "inside-own-A disclosure face missing"
assert out.count("744_901") >= 0 and out.count("746_901") == 0, "stale band token leaked"

receipt = {"keys": counts, "dropped": [d.encode("ascii", "backslashreplace").decode() for d in DROPPED],
           "band_tokens": nband,
           "bytes_src": len(raw), "bytes_out": len(out.encode("utf-8"))}
io.open("results/_w329bmc_derive_counts.json", "w", encoding="utf-8").write(
    json.dumps(receipt, ensure_ascii=False, indent=1))
with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(out)
b = out.encode("utf-8")
print("WROTE %s bytes=%d lines=%d sha16=%s bands=%d keys=%d" % (
    OUT, len(b), out.count("\n"), hashlib.sha256(b).hexdigest()[:16], nband, len(NUM)))