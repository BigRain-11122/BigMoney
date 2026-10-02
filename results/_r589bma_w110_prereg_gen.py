# -*- coding: utf-8 -*-
"""r589 bm-a W110 per-wave prereg generator: copy-adapt from the W109 prereg
(r587 bm-b freeze f077ae11b; anchors rolled W103 -> W105 finalize per r576
anchor-roll law; chain state W1..W105 landed at this freeze window).

W110 = ONE HUNDREDTH engine wave BY MACHINE-DERIVE (engine_owner rows 99 +
candidate), bm-a's THIRTY-FIRST owned (engine_owner==bm-a rows 30 +
candidate, gate leg0 machine output governs per r359 law).
Bands (machine-derived, re-run this freeze window r589 = bitwise identical
to the r588 seat-window run): A 263_004..265_003 / B 61_201..61_400,
both sides arithmetic continuation from the registered W109 tails, hops 0/0.
"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "research", "PERPETUAL_N1_W109_PREREG.md")
DST = os.path.join(REPO, "research", "PERPETUAL_N1_W110_PREREG.md")
t = open(SRC, "rb").read().decode("utf-8")

def rep(old, new, count=1):
    global t
    c = t.count(old)
    assert c == count, f"anchor not unique ({c} != {count}): {old[:70]}..."
    t = t.replace(old, new)
    print("rep ok:", old[:48].replace("\n", " "))

R = rep

# ---- header ------------------------------------------------------------------
R("# PERPETUAL-N1-W109 预注册 · N1 nulls-deepening 泵第 107（never-dry 常供给例常设步·第九十九枚引擎波·机面 derive：engine_owner 行 98+本候选·bm-b 第三十七枚自有波〔r587〕）",
  "# PERPETUAL-N1-W110 预注册 · N1 nulls-deepening 泵第 108（never-dry 常供给例常设步·第一百枚引擎波·机面 derive：engine_owner 行 99+本候选·bm-a 第三十一枚自有波〔r589〕）")

# ---- preamble: engine instance face (bm-b -> bm-a, both tick arch r535 law) ----
R("本机 bm-b 实例=**tick 架构**——每 tick 新进程读活工作树·新登记行对下一 tick 天然可见〔r535 律 tick 面免杀重启免做〕·点火验证唯一证据=2 tick 内产物增长面〔r325 律·state queue 面不信〕",
  "本机 bm-a 实例=**tick 架构**——每 tick 新进程读活工作树·新登记行对下一 tick 天然可见〔r535 律 tick 面免杀重启免做〕·点火验证唯一证据=2 tick 内产物增长面〔r325 律·state queue 面不信〕")

# ---- preamble: wave number + seat + single-state ------------------------------
R("**波号 109=注册表 W108 行后首个自由号**〔r511 表尾锁例冻结前 fetch 实核表尾时 W109 号位净空·pf 行+WAVE_CONFIGS+prereg 路径三查+origin ls-tree vacancy 机验（r587 gate leg0b/leg2）＋全 inbox/processed/ W109 席位零外机命中（本机席位公示豁免=MSG-20261002-1817-bmb rev.B 已推 origin 99e29877c 先于本冻结 r565 律）〕。**单态零席位空档**：W104=bm-a r586 union（48f6f2ff1）+W105=bm-c r376 freeze（f2db133c5）+W106=bm-b r585 freeze（d6b2952e3）+W107=bm-a r587 freeze（a554dedd3）+W108=bm-c r378 freeze（3a3c51b73）**均已注册**（表尾=W108 行）·W109=无 skip-past-published 链面（本波 gate=单态门·ADMIT 回执 results/_r587bmb_w109_band_gate.py rc0 实跑）。",
  "**波号 110=注册表 W109 行后首个自由号**〔r511 表尾锁例冻结前 fetch 实核表尾时 W110 号位净空·pf 行+WAVE_CONFIGS+prereg 路径三查+origin ls-tree vacancy 机验（r589 冻结窗 gate leg0b/leg2·席位窗 r588 先跑同回执）＋全 inbox/processed/ W110 席位零外机命中（本机席位公示豁免=MSG-20261002-1829-bma 已推 origin f457e1c4f 先于本冻结 r565 律）〕。**单态零席位空档**：W104=bm-a r586 union（48f6f2ff1）+W105=bm-c r376 freeze（f2db133c5）+W106=bm-b r585 freeze（d6b2952e3）+W107=bm-a r587 freeze（a554dedd3）+W108=bm-c r378 freeze（3a3c51b73）+W109=bm-b r587 freeze（f077ae11b）**均已注册**（表尾=W109 行）·W110=无 skip-past-published 链面（本波 gate=单态门·席位窗 r588 与冻结窗 r589 双跑 derive 逐位恒等·ADMIT 回执 results/_r588bma_w110_band_gate.py rc0 实跑）。")

R("**席位 rev.B 披露**：首稿 B 投影 60_801..61_000 在推送前被 pre-push 爪拦（origin 前进分叉伪影 r374）·推送前窗内 bm-c W108 冻结落 origin 且其 gate 尾投影披露 B 60_801..61_000 REFUSED[61_000]·本机独立机验拒绝点=SEED_REGISTRY `wild_route_s1`=61_000 命中算术窗尾·首稿从未推送=零外见性·rev.B=唯一发布面（r565 律序保全：rev.B 先于本冻结 commit 推送）。",
  "**席位时态注记（r307 两态族如实披露）**：席位公示窗（r588 18:29 推送 f457e1c4f）先于冻结窗——冻结窗 r589 重跑 band gate derive 逐位恒等（A 263_004..265_003/B 61_201..61_400·hops 0/0·零分叉面）；席位 prose 序数按 r359 律以 gate 机面 derive（第一百枚）为准。")

R("本波 ordinal=**第九十九枚引擎波（机面计数：注册表 engine_owner 行 98+本候选）**·**bm-b 第三十七枚自有波**〔机面 derive：engine_owner==bm-b 行 36+本候选·gate leg0 机证在场·r359 律计数面以 gate 机输出为准〕。",
  "本波 ordinal=**第一百枚引擎波（机面计数：注册表 engine_owner 行 99+本候选）**·**bm-a 第三十一枚自有波**〔机面 derive：engine_owner==bm-a 行 30+本候选·gate leg0 机证在场·r359 律计数面以 gate 机输出为准〕。")

R("**带位（r535 机闸 derive 律·ADMIT 回执=results/_r587bmb_w109_band_gate.py 单态门全腿实跑）**：本波 **A-ext seed=261_004..263_003**（**A 面算术续带**==W108 行 A 尾 261_003+1 起·步长 2_000·CLEAN 零拒绝点·refusal hops=0）；**B-ext exit seed=61_001..61_200**（**B 面撞值跳位**：算术窗 60_801..61_000 撞 **SEED_REGISTRY `wild_route_s1`=61_000** → **跳位至首个净窗** 61_001..61_200·步长 200·refusal hops=1·拒绝事实机证披露〔bm-c W108 gate 尾投影 REFUSED[61_000] 交叉验证一致·法典 §4 W5 撞值跳位先例族·机闸 disjoint 律优先于步长惯例〕）。",
  "**带位（r535 机闸 derive 律·ADMIT 回执=results/_r588bma_w110_band_gate.py 单态门全腿实跑·席位窗 r588+冻结窗 r589 双跑 derive 恒等）**：本波 **A-ext seed=263_004..265_003**（**A 面算术续带**==W109 行 A 尾 263_003+1 起·步长 2_000·CLEAN 零拒绝点·refusal hops=0）；**B-ext exit seed=61_201..61_400**（**B 面算术续带**==W109 行 B 尾 61_200+1 起·步长 200·CLEAN 零拒绝点·refusal hops=0·双侧算术续带=W92 r370/W100 r583/W103 r584/W106 r585/W107 r587 先例族）。")

R("R250：W109 带从未指派·测量面零结果可钓。扫描面=pre-W109 全一百零六行注册 N1 带表（表尾=W108 行·leg0 机证 106 行）",
  "R250：W110 带从未指派·测量面零结果可钓。扫描面=pre-W110 全一百零七行注册 N1 带表（表尾=W109 行·leg0 机证 107 行）")

R("`scripts/perpetual_faces_n1.py`（W2..W108 落地 runner 的 wave 参数化复用——同引擎同语义同切分律·仅法典 §4 新带；引擎侧 `scripts/saturation_engine.py`〔本机 bm-b 实例·tick 架构〕只做队列点火台账处理面·runner 零改写）",
  "`scripts/perpetual_faces_n1.py`（W2..W109 落地 runner 的 wave 参数化复用——同引擎同语义同切分律·仅法典 §4 新带；引擎侧 `scripts/saturation_engine.py`〔本机 bm-a 实例·tick 架构〕只做队列点火台账处理面·runner 零改写）")

# ---- §0 batch identity --------------------------------------------------------
R("- 批名=**PERPETUAL-N1-W109**。", "- 批名=**PERPETUAL-N1-W110**。")

R("起草窗实况：**W1..W103 N1 finalize 已全部落账**——净账本链头 **591,148**（bm-b r586 W103 落账〔one-pass〕·K=224,520 合并池·voids LOWAMP-P1/P2）；**W104 bm-a finalize 未落账+W105 bm-c finalize 未落账+W106 bm-b finalize 未落账+W107 bm-a finalize 未落账+W108 bm-c finalize 未落账（五席 registered=本波 finalize 时 FAIL-CLOSED 前置五空档**（跑时复核；W104/W105/W106 12/12 烧毕产物在场·W107 burn=bm-a 车道在飞实况·W108 burn=bm-c 车道本窗在飞）；累计 null 池投影=224,520+2,200×5（W104..W108）+2,200（本波）=**237,720 投影**（机械算：224,520+13,200；",
  "起草窗实况：**W1..W105 N1 finalize 已全部落账**——净账本链头 **595,548**（bm-c r379 W105 落账〔one-pass〕·K=228,920 合并池·voids LOWAMP-P1/P2）；**W106 bm-b finalize 未落账+W107 bm-a finalize 未落账+W108 bm-c finalize 未落账+W109 bm-b finalize 未落账（四席 registered=本波 finalize 时 FAIL-CLOSED 前置四空档**（跑时复核；W106/W107/W108 12/12 烧毕产物在场·W109 burn=bm-b 车道在飞实况·冻结窗产物未交付）；累计 null 池投影=228,920+2,200×4（W106..W109）+2,200（本波）=**239,920 投影**（机械算：228,920+11,000；")

R("本机自有波 W106 12/12 烧毕交付+W103 finalize r586 本窗落账（engine_owner==bm-b 行 36 枚全览·W104/W105/W107/W108=他机 engine_owner 波按 r508 零跨机重复律不可见）·引擎队列清空=供给律触发",
  "本机自有波 W107 12/12 烧毕交付+W104 finalize r588 落账（engine_owner==bm-a 行 30 枚全览·W105/W106/W108/W109=他机 engine_owner 波按 r508 零跨机重复律不可见）·引擎队列清空=供给律触发")

R("T-2026-10-01-141 s1 引擎线第 99 波·bm-b 第三十七枚自有波〔机面 derive：engine_owner==bm-b 行 36+本候选〕。（波号=注册表 W108 行后首个自由号·单态零席位空档〔席位公示=MSG-20261002-1817-bmb rev.B 先推 origin 99e29877c r565 律〕；lane-free；部门 dept:研究）。",
  "T-2026-10-01-141 s1 引擎线第 100 波·bm-a 第三十一枚自有波〔机面 derive：engine_owner==bm-a 行 30+本候选〕。（波号=注册表 W109 行后首个自由号·单态零席位空档〔席位公示=MSG-20261002-1829-bma 先推 origin f457e1c4f r565 律〕；lane-free；部门 dept:研究）。")

R("（本机 bm-b 实例=**tick 架构**——每 tick 新进程读活工作树·冻结编辑落工作树后下一 tick 自见 W109 行并点火〔r535 律 tick 面免杀重启免做〕·**点火验证唯一证据=产物增长面**〔r325 律·2 tick 窗〕）",
  "（本机 bm-a 实例=**tick 架构**——每 tick 新进程读活工作树·冻结编辑落工作树后下一 tick 自见 W110 行并点火〔r535 律 tick 面免杀重启免做〕·**点火验证唯一证据=产物增长面**〔r325 律·2 tick 窗〕）")

# ---- §0.5 banned gate ---------------------------------------------------------
R("`python Tools/banned_direction_gate.py --prereg research/PERPETUAL_N1_W109_PREREG.md`",
  "`python Tools/banned_direction_gate.py --prereg research/PERPETUAL_N1_W110_PREREG.md`")

R("（p2_calibration v1/v2 canon；W1 ext；W2..W108 落地）的种子带扩展重测",
  "（p2_calibration v1/v2 canon；W1 ext；W2..W109 落地）的种子带扩展重测")

R("禁向词面不在本件复述（机器闸为准·防证伪模式词面自害，W2..W108 同法先例）",
  "禁向词面不在本件复述（机器闸为准·防证伪模式词面自害，W2..W109 同法先例）")

# ---- §2/§3 method faces -------------------------------------------------------
R("- **A 档**（j=0..1,999）：entry rng seed=**261_004+j**（法典 §4 W109 行 A=261_004..263_003·**算术续带**==W108 行 A 尾 261_003+1 起·CLEAN 零拒绝点·ADMIT 回执在场）",
  "- **A 档**（j=0..1,999）：entry rng seed=**263_004+j**（法典 §4 W110 行 A=263_004..265_003·**算术续带**==W109 行 A 尾 263_003+1 起·CLEAN 零拒绝点·ADMIT 回执在场）")

R("- **B 档**（j=0..199）：entry rng=**261_004+j**（与 A[j] 同源配对语义逐字·runner L3047 实证 entry=A_SEED_BASE+j〔W107 prereg prose 255_004+j=上波复制漂移面·runner 主·本波据实正写〕）；exit rng=**61_001+j**（法典 §4 W109 行 B=61_001..61_200·**撞值跳位带**：算术窗 60_801..61_000 撞 SEED_REGISTRY `wild_route_s1`=61_000 → 跳位至首个净窗·拒绝事实机证披露·ADMIT 回执在场）；p_exit=`P_EXIT=0.05`。",
  "- **B 档**（j=0..199）：entry rng=**263_004+j**（与 A[j] 同源配对语义逐字·runner L3047 实证 entry=A_SEED_BASE+j）；exit rng=**61_201+j**（法典 §4 W110 行 B=61_201..61_400·**算术续带**==W109 行 B 尾 61_200+1 起·步长 200·CLEAN 零拒绝点·ADMIT 回执在场）；p_exit=`P_EXIT=0.05`。")

R("本波设计=W2..W108 逐字复用，runner probe 非本窗真态 no-op；账本 +0）",
  "本波设计=W2..W109 逐字复用，runner probe 非本窗真态 no-op；账本 +0）")

R("W109 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带（10_100..12_099/20_100..20_299）、W2..W108 在用带（**全注册·单态**）",
  "W110 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带（10_100..12_099/20_100..20_299）、W2..W109 在用带（**全注册·单态**）")

R("本波机验 ADMIT 回执在场=r587 bm-b 起草窗；selftest leg 2 全表 disjoint+leg N3-R1 腿+腿探针簇腿+leg W102..W108 在用带腿+A 算术窗净腿+B 跳位因腿",
  "本波机验 ADMIT 回执在场=r589 bm-a 冻结窗（席位窗 r588 先跑·双窗 derive 恒等）；selftest leg 2 全表 disjoint+leg N3-R1 腿+腿探针簇腿+leg W102..W109 在用带腿+A 算术窗净腿+B 算术窗净腿")

# ---- §4 ledger face -----------------------------------------------------------
R("合并池 `canon 120 + 已落账波值（起草窗实测 W1..W103 已落账 224,520 实测·derive 禁手抄）+本波 2,200`",
  "合并池 `canon 120 + 已落账波值（起草窗实测 W1..W105 已落账 228,920 实测·derive 禁手抄）+本波 2,200`")

R('append_ledger(batch_name="PERPETUAL-N1-W109", batch_trials=2200, file_name="results/perpetual_faces/n1_w109_results.json"',
  'append_ledger(batch_name="PERPETUAL-N1-W110", batch_trials=2200, file_name="results/perpetual_faces/n1_w110_results.json"')

# ---- §5 pre-run predictions (anchor roll W103 -> W105) ------------------------
R("（起草窗实况注记：**W1..W103 N1 finalize 已全部落账**——净账本链头 591,148=bm-b r586 W103 落账〔one-pass〕·**K=224,520 合并池**；**W104/W105/W106/W107/W108 五空档在飞**（本波 §5 预测键=**W103 finalize 实测值**〔results/perpetual_faces/n1_w103_results.json·N1 面最新已落账键·锚滚动律自 W101 滚动至 W103·r576 锚滚律跨 W102/W103 双落账窗〕）。",
  "（起草窗实况注记：**W1..W105 N1 finalize 已全部落账**——净账本链头 595,548=bm-c r379 W105 落账〔one-pass〕·**K=228,920 合并池**；**W106/W107/W108/W109 四空档在飞**（本波 §5 预测键=**W105 finalize 实测值**〔results/perpetual_faces/n1_w105_results.json·N1 面最新已落账键·锚滚动律自 W103 滚动至 W105·r576 锚滚律跨 W104/W105 双落账窗〕）。")

R("1. W109-only mu 与累计池 merged mu（W103 实测键 **−0.09289408382326719**·K=224,520 合并池·W103-only 实测 **−0.09905036363636398**）差异 **|Δ|<0.02**（W2..W103 共二十九+面实测 mu 稳定先例·单波跨键律）。",
  "1. W110-only mu 与累计池 merged mu（W105 实测键 **−0.09270678970819501**·K=228,920 合并池·W105-only 实测 **−0.08708795454545455**）差异 **|Δ|<0.02**（W2..W105 共三十+面实测 mu 稳定先例·单波跨键律）。")

R("2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.24490354801693814**=W103 合并池实测）。",
  "2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.2448093671349998**=W105 合并池实测）。")

R("3. A 档 full_sharpe_p95 与 W103 A 档 p95（**0.3342** 实测锚）差 **<0.05**（门标准注记法 W5..W103 先例：结果知情报校准面·仅作机器断言伪测用·测量面非注册利益）。",
  "3. A 档 full_sharpe_p95 与 W105 A 档 p95（**0.3038** 实测锚）差 **<0.05**（门标准注记法 W5..W105 先例：结果知情报校准面·仅作机器断言伪测用·测量面非注册利益）。")

R("4. K-lift 线移动幅度 **≥−0.02**（累计池加深零 se_mu·线自 mu/sigma 微调面非质变——W3..W103 先例·W99 +0.0001/W100 −0.0005/W101 −0.0003/W103 **+0.0005** 正负交替如实报正负）；键 W103 实测 K-lift **+0.0005**（line_merged@K224,520 **1.1695**·line_pre 1.169·n_eff_held 588,948；se_mu 收窄链 W100 0.000524→W101 0.000522→W102 0.000519→W103 **0.000517**）。",
  "4. K-lift 线移动幅度 **≥−0.02**（累计池加深零 se_mu·线自 mu/sigma 微调面非质变——W3..W105 先例·W99 +0.0001/W100 −0.0005/W101 −0.0003/W103 +0.0005/W104 −0.0001/W105 **−0.0002** 正负交替如实报正负）；键 W105 实测 K-lift **−0.0002**（line_merged@K228,920 **1.1696**·line_pre 1.1698·n_eff_held 593,348；se_mu 收窄链 W102 0.000519→W103 0.000517→W104 **0.000514**→W105 **0.000512**）。")

R("5. **W110+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 263_004..265_003 **CLEAN**（hops=0）；B 61_201..61_400 **CLEAN**（hops=0）（r587 gate 回执尾行）。",
  "5. **W111+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 265_004..267_003 **CLEAN**（hops=0）；B 61_401..61_600 **CLEAN**（hops=0）（r589 冻结窗 gate 回执尾行）。")

# ---- §6 products --------------------------------------------------------------
R("run --shard k --of 12 --wave 109/finalize --wave 109；probe/parity=W2 设计验证面·本波跑完 no-op）；点火面 `scripts/saturation_engine.py`（本机 bm-b 实例·**tick 架构**",
  "run --shard k --of 12 --wave 110/finalize --wave 110；probe/parity=W2 设计验证面·本波跑完 no-op）；点火面 `scripts/saturation_engine.py`（本机 bm-a 实例·**tick 架构**")

R("**点火验证=2 tick 内产物增长面**（n1_w109/ 分片计数增长·唯一点火证据·r325 律）",
  "**点火验证=2 tick 内产物增长面**（n1_w110/ 分片计数增长·唯一点火证据·r325 律）")

R("- 交付：`results/p2cal_ext/n1_w109/shard-<k>-of-12.json`（append-only·确定性）；`results/perpetual_faces/n1_w109_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 链序前置=**起草窗五空档在飞上游**——跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态律恒在）。",
  "- 交付：`results/p2cal_ext/n1_w110/shard-<k>-of-12.json`（append-only·确定性）；`results/perpetual_faces/n1_w110_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 链序前置=**起草窗四空档在飞上游**——跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态律恒在）。")

R("engine_owner==bm-b 37 枚实况范式=机面 derive：W12/W18/W21/W24/W27/W30/W33/W35/W44/W45/W48/W54/W57/W62/W64/W68/W73/W75/W77/W81/W84/W86/W87/W90/W94/W96/W98/W101/W103/W106+本波 W109 候选〔36 行注册+候选·以 gate leg0 机证为准〕）",
  "engine_owner==bm-a 31 枚实况范式=机面 derive：W12/W18/W21/W24/W27/W30/W33/W35/W44/W45/W48/W54/W57/W62/W64/W68/W73/W75/W77/W81/W84/W86/W87/W90/W94/W96/W98/W101/W104/W107+本波 W110 候选〔30 行注册+候选·以 gate leg0 机证为准；W109 prereg §6 prose 波清单含上波复制漂移面（W12..W98 段= bm-a 行）——r359 律以 gate 机面 derive 为准·冻结件不回改·本波清单已机 derive 校正〕）")

R("bm-b tick 架构=engine ledger jsonl+state/face/history 从 git 交付",
  "bm-a tick 架构=engine ledger jsonl+state/face/history 从 git 交付")

# ---- final freeze line --------------------------------------------------------
R("per-wave prereg=research/PERPETUAL_N1_W109_PREREG.md", "per-wave prereg=research/PERPETUAL_N1_W110_PREREG.md", 0) if False else None

# safety: no W109-specific stragglers (except §6 freeze-prose refs to the W109 wave row itself)
leftovers = [s for s in ("W109", "r587", "bm-b", "61_001", "261_004") if s in t]
print("leftover tokens:", leftovers)

open(DST, "wb").write(t.encode("utf-8"))
print("WROTE", DST, len(t), "chars")
