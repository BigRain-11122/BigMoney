# -*- coding: utf-8 -*-
"""r384 bm-c W115 per-wave prereg generator: copy-adapt from the W114 prereg
(bm-a r594 freeze ddacf2616; anchor rolls to W114 = latest landed finalize at
this freeze window per r576/r590 anchor-roll law; chain state W1..W114 landed,
ZERO in-flight upstream seats -- clean single-state freeze).

W115 = ONE HUNDRED-AND-FIFTH engine wave BY MACHINE-DERIVE (engine_owner
rows 104 + candidate), bm-c's THIRTY-FOURTH owned (engine_owner==bm-c rows
33 + candidate, gate leg0 machine output governs per r359 law).
Bands (machine-derived, seat probe + freeze-window gate double-run):
A 273_004..275_003 arithmetic continuation / B 62_501..62_700 pinned
D-20261002-05 past-hit restart over SEED_REGISTRY grid_sleeve_p1=62_500.
Anchor values are READ from n1_w114_results.json / n1_w113_results.json /
n1_w112_results.json at generation time (derive 禁手抄 law).
"""
import sys, os, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "research", "PERPETUAL_N1_W114_PREREG.md")
DST = os.path.join(REPO, "research", "PERPETUAL_N1_W115_PREREG.md")
t = open(SRC, "rb").read().decode("utf-8")

# ---- machine-derived anchor values (read, never hand-copied) -----------------
d114 = json.load(open(os.path.join(REPO, "results/perpetual_faces/n1_w114_results.json"), encoding="utf-8"))
d113 = json.load(open(os.path.join(REPO, "results/perpetual_faces/n1_w113_results.json"), encoding="utf-8"))
d112 = json.load(open(os.path.join(REPO, "results/perpetual_faces/n1_w112_results.json"), encoding="utf-8"))
npc114, npc113, npc112 = d114["null_pool_cumulative"], d113["null_pool_cumulative"], d112["null_pool_cumulative"]
sk114, sk113, sk112 = d114["skill_line_v2_k_lift"], d113["skill_line_v2_k_lift"], d112["skill_line_v2_k_lift"]
K114, K113 = npc114["merged"]["n_values"], npc113["merged"]["n_values"]
w114_se_mu = npc114[f"se_mu_at_k{K114}"]
w113_se_mu = npc113[f"se_mu_at_k{K113}"]
w114_klift_raw, w113_klift_raw, w112_klift_raw = sk114["line_delta_k_lift"], sk113["line_delta_k_lift"], sk112["line_delta_k_lift"]
w114_ledger_total = d114["science_gates"]["ledger"]["total"]
w114_n_eff_held = sk114["n_eff_held_equal"]
w113_n_eff_held = sk113["n_eff_held_equal"]
assert w113_n_eff_held == 610948, f"W113 n_eff_held drift: {w113_n_eff_held} (expect 610,948)"

def fmt(x):
    return repr(x).replace("-", "\u2212")

def fmt_klift(v):
    if v > 0: return "+" + repr(v)
    if v < 0: return "\u2212" + repr(abs(v))
    return "0.0000"

assert K114 == 248720, f"W114 merged K drift: {K114} (expect 248,720)"
assert w114_ledger_total == 615348, f"W114 ledger total drift: {w114_ledger_total} (expect 615,348)"
assert w114_n_eff_held == 613148, f"W114 n_eff_held drift: {w114_n_eff_held} (expect 613,148)"

w114_merged_mu = fmt(npc114["merged"]["mu"])
w114_merged_sigma = fmt(npc114["merged"]["sigma"])
w114_only_mu = fmt(npc114["w114_only"]["mu"])
w114_p95 = repr(d114["families"]["A_random_engine_exit"]["full_sharpe_p95"])
w114_klift = fmt_klift(w114_klift_raw)
w114_line_merged = repr([v for k, v in sk114.items() if k.startswith("line_merged_")][0])
w114_line_pre = repr(sk114["line_pre_w114"])
# W113-side values (baked into the W114 source text -- rebuilt for old-anchors)
w113_merged_mu = fmt(npc113["merged"]["mu"])
w113_merged_sigma = fmt(npc113["merged"]["sigma"])
w113_only_mu = fmt(npc113["w113_only"]["mu"])
w113_p95 = repr(d113["families"]["A_random_engine_exit"]["full_sharpe_p95"])
w113_klift = fmt_klift(w113_klift_raw)
w112_klift = fmt_klift(w112_klift_raw)
w113_line_merged = repr([v for k, v in sk113.items() if k.startswith("line_merged_")][0])
w113_line_pre = repr(sk113["line_pre_w113"])
w112_se_mu = repr(npc112["se_mu_at_k244320"])

sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, os.path.join(REPO, "research"))
sys.path.insert(0, REPO)
from perpetual_faces import N1_BANDS
bmc_list = "/".join(f"W{w}" for w in sorted(N1_BANDS)
                    if N1_BANDS[w].get("engine_owner") == "bm-c")
assert len([w for w in N1_BANDS if N1_BANDS[w].get("engine_owner") == "bm-c"]) == 33, \
    "bm-c owned rows drift (expect 33)"
print("bm-c owned rows (machine-derived):", bmc_list)

def rep(old, new, count=1):
    global t
    c = t.count(old)
    if c != count:
        key = old[:24]
        j = t.find(key)
        if j >= 0:
            k = 0
            while k < min(len(old), len(t) - j) and old[k] == t[j+k]: k += 1
            print("DIVERGENCE at char %d: file=%r(%s) vs gen=%r(%s)" % (
                k, t[j+k] if j+k < len(t) else '', hex(ord(t[j+k])) if j+k < len(t) else '',
                old[k] if k < len(old) else '', hex(ord(old[k])) if k < len(old) else ''))
        else:
            print("PREFIX ABSENT (24-char):", repr(key))
    assert c == count, f"anchor not unique ({c} != {count}): {old[:70]}..."
    t = t.replace(old, new)
    print("rep ok:", old[:48].replace("\n", " "))

R = rep

# ---- header ------------------------------------------------------------------
R("# PERPETUAL-N1-W114 预注册 · N1 nulls-deepening 泵第 112（never-dry 常供给例常设步·第一百零四枚引擎波·机面 derive：engine_owner 行 103+本候选·bm-a 第三十三枚自有波〔r592〕）",
  "# PERPETUAL-N1-W115 预注册 · N1 nulls-deepening 泵第 113（never-dry 常供给例常设步·第一百零五枚引擎波·机面 derive：engine_owner 行 104+本候选·bm-c 第三十四枚自有波〔r383〕）")

# ---- preamble: engine instance face (bm-a tick -> bm-c resident v0.4) ---------
R("本机 bm-a 实例=**tick 架构**——每 tick 新进程读活工作树·新登记行对下一 tick 天然可见〔r535 律 tick 面免杀重启免做〕·点火验证唯一证据=2 tick 内产物增长面〔r325 律·state queue 面不信〕）→ **never-dry 常供给例常设步**",
  "本机 bm-c 实例=**常驻架构 v0.4 mtime-reload**——冻结编辑落工作树后 LIVE 引擎下一 tick 重读活树自见新行自燃〔D-20261002-03 修法·W59/W60/W61/W66/W69/W71/W78/W80/W88 同窗实证·r325/r330 kill-restart 序免做〕·点火验证唯一证据=2 tick 内产物增长面〔r325 律·state queue 面不信〕）→ **never-dry 常供给例常设步**")

# ---- preamble: wave number + seat + single-state chain -------------------------
R("**波号 114=注册表 W113 行后首个自由号**〔r511 表尾锁例冻结前 fetch 实核表尾时 W114 号位净空·pf 行+WAVE_CONFIGS+prereg 路径三查+origin ls-tree vacancy 机验（本冻结窗 gate leg0b/leg2 实跑·r374 inbox+processed 双目录腿）＋全 inbox/processed/ W114 席位零外机命中（本机席位公示豁免=MSG-20261002-2014-bma 已推 origin 2cd67216a 先于本冻结 r565 律〕。**单态零席位空档**：W108=bm-c r378 freeze（3a3c51b73）+W109=bm-b r587 freeze（f077ae11b）+W110=bm-a r589 freeze（ff0b1869b）+W111=bm-b r589 freeze（e0a103ec1）+W112=bm-a r590 freeze（0c4d67910）+W113=bm-c r382 freeze（eeb062290）**均已注册**（表尾=W113 行）·W114=无 skip-past-published 链面（本波 gate=单态门·pre-seat probe 与冻结窗 gate 双跑 derive 逐位恒等·ADMIT 回执 results/_r592bma_w114_band_gate.py rc0 实跑）。",
  "**波号 115=注册表 W114 行后首个自由号**〔r511 表尾锁例冻结前 fetch 实核表尾时 W115 号位净空·pf 行+WAVE_CONFIGS+prereg 路径三查+origin ls-tree vacancy 机验（本冻结窗 gate leg0b/leg2 实跑·r374 inbox+processed 双目录腿）＋全 inbox/processed/ W115 席位零外机命中（本机席位公示豁免=MSG-20261002-2130-bmc-w115-seat 已推 origin ac241dd32 先于本冻结 r565 律〕。**单态零席位空档**：W108=bm-c r378 freeze（3a3c51b73）+W109=bm-b r587 freeze（f077ae11b）+W110=bm-a r589 freeze（ff0b1869b）+W111=bm-b r589 freeze（e0a103ec1）+W112=bm-a r590 freeze（0c4d67910）+W113=bm-c r382 freeze（eeb062290）+W114=bm-a r594 freeze（ddacf2616）**均已注册**（表尾=W114 行）·W115=无 skip-past-published 链面（本波 gate=单态门·pre-seat probe 与冻结窗 gate 双跑 derive 逐位恒等·ADMIT 回执 results/_r384bmc_w115_band_gate.py rc0 实跑）。")

R("**席位时态注记（r307 两态族如实披露）**：席位公示窗先于冻结窗——pre-seat 机证=results/_r592bma_w114_probe.py rc0（ADMIT-derive）；冻结窗 gate 重跑 derive 逐位恒等（A 271_004..273_003/B 62_201..62_400·hops 0/0·零分叉面）。",
  "**席位时态注记（r307 两态族如实披露）**：席位公示窗先于冻结窗——pre-seat 机证=results/_r383bmc_w115_probe.py rc0（ADMIT-derive）；冻结窗 gate 重跑 derive 逐位恒等（A 273_004..275_003/B 62_501..62_700·hops 0/1·零分叉面）。")

R("**席位推送窗一次 origin 前进实录**（首推被拒=bm-c 引擎 appender 分片批推（shard-7/9/10 三件）中窗落账→r589 撤-FF-重落环：reset --mixed HEAD~1+merge --ff-only origin/main+重 commit 重推=2cd67216a 一发即达·payload=席位 MSG 单件·deletion-set 空·零 rebase 零 force〔r532 活写面律〕·本机活写面未触碰·rev.A=唯一发布面）。",
  "**席位推送窗实录**（死会话 r383 窗直推 ac241dd32 一发即达·payload=席位 MSG+pre-seat probe 双件·deletion-set 空·零 rebase 零 force〔r532 活写面律〕·rev.A=唯一发布面·本恢复轮 r384 按 r471 收养律核对席位在 origin+探针证据同 commit 闭合）。")

R("本波 ordinal=**第一百零四枚引擎波（机面计数：注册表 engine_owner 行 103+本候选）**·**bm-a 第三十三枚自有波**〔机面 derive：engine_owner==bm-a 行 32+本候选·gate leg0 机证在场·r359 律计数面以 gate 机输出为准〕。",
  "本波 ordinal=**第一百零五枚引擎波（机面计数：注册表 engine_owner 行 104+本候选）**·**bm-c 第三十四枚自有波**〔机面 derive：engine_owner==bm-c 行 33+本候选·gate leg0 机证在场·r359 律计数面以 gate 机输出为准〕。")

R("**带位（r535 机闸 derive 律·ADMIT 回执=results/_r592bma_w114_band_gate.py 单态门全腿实跑·pre-seat probe results/_r592bma_w114_probe.py 先跑·双窗 derive 恒等）**：本波 **A-ext seed=271_004..273_003**（**A 面算术续带**==W113 行 A 尾 271_003+1 起·步长 2_000·CLEAN 零拒绝点·refusal hops=0）；**B-ext exit seed=62_201..62_400**（**B 面算术续带**==W113 行 B 尾 62_200+1 起·步长 200·CLEAN 零拒绝点·refusal hops=0·双侧算术续带=W92 r370/W100 r583/W103 r584/W106 r585/W107 r587/W110 r589/W111 r589/W112 r590 先例族）。",
  "**带位（r535 机闸 derive 律·ADMIT 回执=results/_r384bmc_w115_band_gate.py 单态门全腿实跑·pre-seat probe results/_r383bmc_w115_probe.py 先跑·双窗 derive 恒等）**：本波 **A-ext seed=273_004..275_003**（**A 面算术续带**==W114 行 A 尾 273_003+1 起·步长 2_000·CLEAN 零拒绝点·refusal hops=0）；**B-ext exit seed=62_501..62_700**（**B 面撞值跳位窗**==W114 行 B 尾 62_400+1 起算术窗 62_401..62_600 撞 SEED_REGISTRY `grid_sleeve_p1`=62_500〔中位命中 100/200 非边缘·两读法可分叉〕→ **法典 §4 D-20261002-05 钉死行越 hit 起窗** 62_501..62_700·refusal hops=1·撞值跳位先例族=W5/W26/W63/W68/W87/W109）。")

R("R250：W114 带从未指派·测量面零结果可钓。扫描面=pre-W114 全一百一十一行注册 N1 带表（表尾=W113 行·leg0 机证 111 行）",
  "R250：W115 带从未指派·测量面零结果可钓。扫描面=pre-W115 全一百一十二行注册 N1 带表（表尾=W114 行·leg0 机证 112 行）")

R("`scripts/perpetual_faces_n1.py`（W2..W113 落地 runner 的 wave 参数化复用——同引擎同语义同切分律·仅法典 §4 新带；引擎侧 `scripts/saturation_engine.py`〔本机 bm-a 实例·tick 架构〕只做队列点火台账处理面·runner 零改写）",
  "`scripts/perpetual_faces_n1.py`（W2..W114 落地 runner 的 wave 参数化复用——同引擎同语义同切分律·仅法典 §4 新带；引擎侧 `Tools/saturation_engine.py`〔本机 bm-c 实例·常驻架构 v0.4 mtime-reload〕只做队列点火台账处理面·runner 零改写）")

# ---- sec.0 batch identity --------------------------------------------------------
R("- 批名=**PERPETUAL-N1-W114**。", "- 批名=**PERPETUAL-N1-W115**。")

R(f"起草窗实况：**W1..W113 N1 finalize 已全部落账**——净账本链头 **{w114_ledger_total - 2200:,}**（bm-c r382 W113 finalize 落账〔one-pass〕·K={K113:,} 合并池·voids LOWAMP-P1/P2）；**零在飞上游席**（W2..W113 全注册全落账·单态全闭=本波 finalize 链序前置零空档·跑时按 registry 键 derive 复核恒在）；累计 null 池投影={K113:,}+2,200（本波）=**248,720 投影**（机械算：246,520+2,200；",
  f"起草窗实况：**W1..W114 N1 finalize 已全部落账**——净账本链头 **{w114_ledger_total:,}**（bm-a r594 W114 finalize 落账〔one-pass〕·K={K114:,} 合并池·voids LOWAMP-P1/P2）；**零在飞上游席**（W2..W114 全注册全落账·单态全闭=本波 finalize 链序前置零空档·跑时按 registry 键 derive 复核恒在）；累计 null 池投影={K114:,}+2,200（本波）=**250,920 投影**（机械算：248,720+2,200；")

R("本机自有波 W112 12/12 烧毕交付+W112 finalize 同轮落账 r591（engine_owner==bm-a 行 32 枚全览·W108/W109/W111/W113=他机 engine_owner 波按 r508 零跨机重复律不可见）·引擎队列清空=供给律触发",
  "本机自有波 W113 12/12 烧毕交付（r382 窗内 ~8min）+W113 finalize 已落账 r383（engine_owner==bm-c 行 33 枚全览·W108..W112/W114=他机 engine_owner 波按 r508 零跨机重复律不可见）·引擎队列清空=供给律触发")

R("T-2026-10-01-141 s1 引擎线第 104 波·bm-a 第三十三枚自有波〔机面 derive：engine_owner==bm-a 行 32+本候选〕。（波号=注册表 W113 行后首个自由号·单态零席位空档〔席位公示=MSG-20261002-2014-bma 先推 origin 2cd67216a r565 律〕；lane-free；部门 dept:研究）。",
  "T-2026-10-01-141 s1 引擎线第 105 波·bm-c 第三十四枚自有波〔机面 derive：engine_owner==bm-c 行 33+本候选〕。（波号=注册表 W114 行后首个自由号·单态零席位空档〔席位公示=MSG-20261002-2130-bmc-w115-seat 先推 origin ac241dd32 r565 律〕；lane-free；部门 dept:研究）。")

R("（本机 bm-a 实例=**tick 架构**——每 tick 新进程读活工作树·冻结编辑落工作树后下一 tick 自见 W114 行并点火〔r535 律 tick 面免杀重启免做〕·**点火验证唯一证据=产物增长面**〔r325 律·2 tick 窗〕）",
  "（本机 bm-c 实例=**常驻架构 v0.4 mtime-reload**——冻结编辑落工作树后 LIVE 引擎下一 tick 重读活树自见 W115 行并点火〔D-20261002-03 修法·r325/r330 kill-restart 序免做〕·**点火验证唯一证据=产物增长面**〔r325 律·2 tick 窗〕）")

# ---- sec.0.5 banned gate ---------------------------------------------------------
R("`python Tools/banned_direction_gate.py --prereg research/PERPETUAL_N1_W114_PREREG.md`",
  "`python Tools/banned_direction_gate.py --prereg research/PERPETUAL_N1_W115_PREREG.md`")

R("（p2_calibration v1/v2 canon；W1 ext；W2..W113 落地）的种子带扩展重测",
  "（p2_calibration v1/v2 canon；W1 ext；W2..W114 落地）的种子带扩展重测")

R("禁向词面不在本件复述（机器闸为准·防证伪模式词面自害，W2..W113 同法先例）",
  "禁向词面不在本件复述（机器闸为准·防证伪模式词面自害，W2..W114 同法先例）")

# ---- sec.3 method faces -----------------------------------------------------------
R("entry rng seed=**271_004+j**（法典 §4 W114 行 A=271_004..273_003·**算术续带**==W113 行 A 尾 271_003+1 起·步长 2_000·CLEAN 零拒绝点·hops=0·ADMIT 回执在场）",
  "entry rng seed=**273_004+j**（法典 §4 W115 行 A=273_004..275_003·**算术续带**==W114 行 A 尾 273_003+1 起·步长 2_000·CLEAN 零拒绝点·hops=0·ADMIT 回执在场）")

R("exit rng=**62_201+j**（法典 §4 W114 行 B=62_201..62_400·**算术续带**==W113 行 B 尾 62_200+1 起·步长 200·CLEAN 零拒绝点·hops=0·ADMIT 回执在场）；p_exit=`P_EXIT=0.05`。",
  "exit rng=**62_501+j**（法典 §4 W115 行 B=62_501..62_700·**撞值跳位窗**==W114 行 B 尾 62_400+1 起算术窗 62_401..62_600 撞 SEED_REGISTRY `grid_sleeve_p1`=62_500〔中位命中 100/200 非边缘〕→ D-20261002-05 越 hit 起窗·hops=1·ADMIT 回执在场）；p_exit=`P_EXIT=0.05`。")

R("entry rng=**271_004+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）",
  "entry rng=**273_004+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）")

R("本波设计=W2..W113 逐字复用，runner probe 非本窗真态 no-op；账本 +0）",
  "本波设计=W2..W114 逐字复用，runner probe 非本窗真态 no-op；账本 +0）")

R("W114 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带（10_100..12_099/20_100..20_299）、W2..W113 在用带（**全注册·单态**）",
  "W115 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带（10_100..12_099/20_100..20_299）、W2..W114 在用带（**全注册·单态**）")

R("本波机验 ADMIT 回执在场=r592 bm-a 冻结窗（pre-seat probe 先跑·双窗 derive 恒等）；selftest leg 2 全表 disjoint+leg N3-R1 腿+腿探针簇腿+leg W103..W113 在用带腿+A 算术窗净腿+B 算术窗净腿",
  "本波机验 ADMIT 回执在场=r384 bm-c 冻结窗（pre-seat probe 先跑·双窗 derive 恒等）；selftest leg 2 全表 disjoint+leg N3-R1 腿+腿探针簇腿+leg W104..W114 在用带腿+A 算术窗净腿+B 跳位窗净腿+B 跳位先例腿（算术窗含 62_500 拒绝点断言+越 hit 起窗恒等断言）")

# ---- sec.4 ledger face -----------------------------------------------------------
R(f"合并池 `canon 120 + 已落账波值（起草窗实测 W1..W113 已落账 {K113:,} 实测·derive 禁手抄）+本波 2,200`",
  f"合并池 `canon 120 + 已落账波值（起草窗实测 W1..W114 已落账 {K114:,} 实测·derive 禁手抄）+本波 2,200`")

R('append_ledger(batch_name="PERPETUAL-N1-W114", batch_trials=2200, file_name="results/perpetual_faces/n1_w114_results.json"',
  'append_ledger(batch_name="PERPETUAL-N1-W115", batch_trials=2200, file_name="results/perpetual_faces/n1_w115_results.json"')

# ---- sec.5 pre-run predictions (anchor rolls W113 -> W114 landed) -----------------
R(f"（起草窗实况注记：**W1..W113 N1 finalize 已全部落账**——净账本链头 {w114_ledger_total - 2200:,}=bm-c r382 W113 finalize 落账〔one-pass〕·**K={K113:,} 合并池**；**零在飞上游席**（本波 §5 预测键=**W113 finalize 实测值**〔results/perpetual_faces/n1_w113_results.json·N1 面最新已落账键〕）。",
  f"（起草窗实况注记：**W1..W114 N1 finalize 已全部落账**——净账本链头 {w114_ledger_total:,}=bm-a r594 W114 finalize 落账〔one-pass〕·**K={K114:,} 合并池**；**零在飞上游席**（本波 §5 预测键=**W114 finalize 实测值**〔results/perpetual_faces/n1_w114_results.json·N1 面最新已落账键〕）。")

R(f"1. W114-only mu 与累计池 merged mu（W113 实测键 **{w113_merged_mu}**·K={K113:,} 合并池·W113-only 实测 **{w113_only_mu}**）差异 **|Δ|<0.02**（W2..W113 共三十+面实测 mu 稳定先例·单波跨键律）。",
  f"1. W115-only mu 与累计池 merged mu（W114 实测键 **{w114_merged_mu}**·K={K114:,} 合并池·W114-only 实测 **{w114_only_mu}**）差异 **|Δ|<0.02**（W2..W114 共三十+面实测 mu 稳定先例·单波跨键律）。")

R(f"2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **{w113_merged_sigma}**=W113 合并池实测）。",
  f"2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **{w114_merged_sigma}**=W114 合并池实测）。")

R(f"3. A 档 full_sharpe_p95 与 W113 A 档 p95（**{w113_p95}** 实测锚）差 **<0.05**（门标准注记法 W5..W113 先例：结果知情报校准面·仅作机器断言伪测用·测量面非注册利益）。",
  f"3. A 档 full_sharpe_p95 与 W114 A 档 p95（**{w114_p95}** 实测锚）差 **<0.05**（门标准注记法 W5..W114 先例：结果知情报校准面·仅作机器断言伪测用·测量面非注册利益）。")

R(f"4. K-lift 线移动幅度 **≥−0.02**（累计池加深零 se_mu·线自 mu/sigma 微调面非质变——W3..W113 先例·W99 +0.0001/W100 −0.0005/W101 −0.0003/W103 +0.0005/W104 −0.0001/W105 −0.0002/W106 **+0.0002**/W107 **−0.0002**/W108 **+0.0003**/W109 **0.0000**/W110 **0.0000**/W111 **0.0000**/W112 **{w112_klift}**/W113 **{w113_klift}** 正负交替如实报正负）；键 W113 实测 K-lift **{w113_klift}**（line_merged@K{K113:,} **{w113_line_merged}**·line_pre {w113_line_pre}·n_eff_held {w113_n_eff_held:,}；se_mu 收窄链 W110 0.0005→W111 **0.000498**→W112 **{w112_se_mu}**→W113 **{w113_se_mu}**）。",
  f"4. K-lift 线移动幅度 **≥−0.02**（累计池加深零 se_mu·线自 mu/sigma 微调面非质变——W3..W114 先例·W99 +0.0001/W100 −0.0005/W101 −0.0003/W103 +0.0005/W104 −0.0001/W105 −0.0002/W106 **+0.0002**/W107 **−0.0002**/W108 **+0.0003**/W109 **0.0000**/W110 **0.0000**/W111 **0.0000**/W112 **{w112_klift}**/W113 **{w113_klift}**/W114 **{w114_klift}** 正负交替如实报正负）；键 W114 实测 K-lift **{w114_klift}**（line_merged@K{K114:,} **{w114_line_merged}**·line_pre {w114_line_pre}·n_eff_held {w114_n_eff_held:,}；se_mu 收窄链 W110 0.0005→W111 **0.000498**→W112 **{w112_se_mu}**→W113 **{w113_se_mu}**→W114 **{w114_se_mu}**）。")

R("5. **W115+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 273_004..275_003 **CLEAN**（hops=0）；B **62_501..62_700（hops=1·撞值跳位）**——算术窗 62_401..62_600 撞 SEED_REGISTRY `grid_sleeve_p1`=62_500（中位命中族·两读法可分叉）→ **法典 §4 D-20261002-05 钉死行越 hit 起窗** 62_501..62_700 CLEAN（r592 冻结窗 gate 回执尾行）。〔两态如实披露：席位 MSG-20261002-2014-bma 尾投影行「62_601..62_800」=pre-seat 探针 first_clean 窗步链读法面（该探针步长推进实现承自 W112 探针）；中位命中族窗步链读法被 D-20261002-05 钉死行取代=advisory 行如实勘注不回改·本波 A/B 主带两读法恒同解（双侧 hops=0）零影响·冻结窗 gate 回执为准〕",
  "5. **W116+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 275_004..277_003 **CLEAN**（hops=0）；B 62_701..62_900 **CLEAN**（hops=0）（r384 冻结窗 gate 回执尾行·与本席位 MSG W116+ 投影披露交叉验证一致=自机 derive 非转抄 r587 律）。")

# ---- sec.6 products --------------------------------------------------------------
R("run --shard k --of 12 --wave 114/finalize --wave 114；probe/parity=W2 设计验证面·本波跑完 no-op）；点火面 `scripts/saturation_engine.py`（本机 bm-a 实例·**tick 架构**·本地队列→PreIgnitionChecks→分离子进程点火→完成探测→台账处理〔runner_args --lane engine 车道合同同 r523 律〕）·**点火验证=2 tick 内产物增长面**（n1_w114/ 分片计数增长·唯一点火证据·r325 律）",
  "run --shard k --of 12 --wave 115/finalize --wave 115；probe/parity=W2 设计验证面·本波跑完 no-op）；点火面 `Tools/saturation_engine.py`（本机 bm-c 实例·**常驻架构 v0.4 mtime-reload**·本地队列→PreIgnitionChecks→分离子进程点火→完成探测→台账处理〔runner_args --lane engine 车道合同同 r523 律〕）·**点火验证=2 tick 内产物增长面**（n1_w115/ 分片计数增长·唯一点火证据·r325 律）")

R("- 交付：`results/p2cal_ext/n1_w114/shard-<k>-of-12.json`（append-only·确定性）；`results/perpetual_faces/n1_w114_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 链序前置=**起草窗零在飞上游**（W2..W113 全落账）——跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态律恒在）。",
  "- 交付：`results/p2cal_ext/n1_w115/shard-<k>-of-12.json`（append-only·确定性）；`results/perpetual_faces/n1_w115_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 链序前置=**起草窗零在飞上游**（W2..W114 全落账）——跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态律恒在）。")

bma_draft_list = "/".join(f"W{w}" for w in sorted(N1_BANDS)
                           if N1_BANDS[w].get("engine_owner") == "bm-a" and w < 114)
assert len([w for w in N1_BANDS if N1_BANDS[w].get("engine_owner") == "bm-a" and w < 114]) == 32, \
    "bm-a draft-time rows drift (expect 32, pre-W114 drafting snapshot)"
R(f"- 引擎台账：bm-a tick 架构=engine ledger jsonl+state/face/history 从 git 交付（engine_owner==bm-a 33 枚实况范式=机面 derive：{bma_draft_list}+本波 W114 候选〔32 行注册+候选·以 gate leg0 机证为准〕）；attrition 账本完整性 tripwire 覆盖本波产物件（r448 律）。",
  f"- 引擎台账：bm-c 常驻架构 v0.4=engine ledger jsonl+state/face/history 从 git 交付（engine_owner==bm-c 34 枚实况范式=机面 derive：{bmc_list}+本波 W115 候选〔33 行注册+候选·以 gate leg0 机证为准〕）；attrition 账本完整性 tripwire 覆盖本波产物件（r448 律）。")

# ---- sec.7/8 tail reset to the r382-verbatim placeholder (r307/E07 law) -------
i7 = t.find("## §7")
assert i7 > 0 and t.count("## §7") == 1 and t.count("## §8") == 1, \
    "sec7/8 tail anchor drift (single-sec anchor law)"
_eol = "\r\n" if t.count("\r\n") * 2 > t.count("\n") else "\n"
S78_PLACEHOLDER = _eol.join([
    "## §7 跑后实证。【跑前必须为空——占位纪律：写数字即造假】",
    "",
    "- （finalize 落账后机械回填；两态腿断言在场=r307 律）",
    "",
    "## §8 批后复盘。【必填·终 7-T】",
    "",
    "- （finalize 落账后机械回填）",
    "",
    "- **跑前冻结=本件 commit**（freeze hash 归轮报告与法典 §4 行；冻结后禁改判据（回填限 §7/§8）。",
    "",
])
t = t[:i7] + S78_PLACEHOLDER
print("sec7/8 tail reset to r382-verbatim placeholder (source carried r594 bm-a backfill)")

# ---- batch-identity leftovers: hard asserts --------------------------------------
leftovers = [s for s in ("PERPETUAL-N1-W114", "271_004+j", "62_201+j", "n1_w114_results", "r592bma", "2cd67216a", "MSG-20261002-2014-bma", "bm-a 第三十三")
             if s in t]
# sec.5 anchor-key exemption: the ONLY legal 'n1_w114_results' in the W115
# output is the sec.5 prediction-anchor key reference (latest LANDED finalize
# = W114 results file, r576 anchor-roll law) written by this generator's own
# sec.5 rep -- exempt from the active-face leftover blacklist with count+context
# gates (r594 bm-a E07 precedent).
if "n1_w114_results" in leftovers and t.count("n1_w114_results") == 1 and \
        "本波 §5 预测键=**W114 finalize 实测值**〔results/perpetual_faces/n1_w114_results.json·N1 面最新已落账键〕" in t:
    leftovers.remove("n1_w114_results")
    print("sec.5 anchor-key exemption applied (n1_w114_results count=1, anchor context verified)")
print("leftover tokens:", leftovers)
assert not leftovers, "batch-identity leftovers must be zero (W114 active-face tokens all replaced)"
hist_leftovers = [s for s in ("W114", "r592/r594", "62_201", "271_004", "ddacf2616") if s in t]
print("history-reference tokens remaining (expected, registered-row context):", hist_leftovers)

open(DST, "wb").write(t.encode("utf-8"))
print("WROTE", DST, len(t), "chars")
