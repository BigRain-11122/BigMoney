# -*- coding: utf-8 -*-
"""r382 bm-c W113 per-wave prereg generator: copy-adapt from the W112 prereg
(bm-a r590 freeze 0c4d67910; anchor rolls to W111 = latest landed finalize at
this freeze window; chain state W1..W111 landed, ONE in-flight upstream seat
W112 bm-a registered-unfinalized).

W113 = ONE HUNDRED-AND-THIRD engine wave BY MACHINE-DERIVE (engine_owner
rows 102 + candidate), bm-c's THIRTY-THIRD owned (engine_owner==bm-c rows
32 + candidate, gate leg0 machine output governs per r359 law).
Bands (machine-derived, seat probe + freeze-window gate double-run bitwise
identical): A 269_004..271_003 arithmetic continuation / B 62_001..62_200
jump-past-hit window over SEED_REGISTRY cta_wave1=62_000 (D-20261002-05).
"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "research", "PERPETUAL_N1_W112_PREREG.md")
DST = os.path.join(REPO, "research", "PERPETUAL_N1_W113_PREREG.md")
t = open(SRC, "rb").read().decode("utf-8")

# machine-derived bm-c owned-wave enumeration (r359 derive law, no hand lists)
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, os.path.join(REPO, "research"))
sys.path.insert(0, REPO)
from perpetual_faces import N1_BANDS
bmc_list = "/".join(f"W{w}" for w in sorted(N1_BANDS)
                    if N1_BANDS[w].get("engine_owner") == "bm-c")
assert len([w for w in N1_BANDS if N1_BANDS[w].get("engine_owner") == "bm-c"]) == 32, \
    "bm-c owned rows drift (expect 32)"
print("bm-c owned rows (machine-derived):", bmc_list)

def rep(old, new, count=1):
    global t
    c = t.count(old)
    assert c == count, f"anchor not unique ({c} != {count}): {old[:70]}..."
    t = t.replace(old, new)
    print("rep ok:", old[:48].replace("\n", " "))

R = rep

# ---- header ------------------------------------------------------------------
R("# PERPETUAL-N1-W112 预注册 · N1 nulls-deepening 泵第 110（never-dry 常供给例常设步·第一百零二枚引擎波·机面 derive：engine_owner 行 101+本候选·bm-a 第三十二枚自有波〔r590〕）",
  "# PERPETUAL-N1-W113 预注册 · N1 nulls-deepening 泵第 111（never-dry 常供给例常设步·第一百零三枚引擎波·机面 derive：engine_owner 行 102+本候选·bm-c 第三十三枚自有波〔r382〕）")

# ---- preamble: engine instance face (bm-a tick -> bm-c resident v0.4) ---------
R("本机 bm-a 实例=**tick 架构**——每 tick 新进程读活工作树·新登记行对下一 tick 天然可见〔r535 律 tick 面免杀重启免做〕·点火验证唯一证据=2 tick 内产物增长面〔r325 律·state queue 面不信〕）→ **never-dry 常供给例常设步**",
  "本机 bm-c 实例=**常驻架构 v0.4 mtime-reload**——冻结编辑落工作树后 LIVE 引擎下一 tick 重读活树自见新行自燃〔D-20261002-03 修法·W59/W60/W61/W66/W69/W71/W78/W80/W88 同窗实证·r325/r330 kill-restart 序免做〕·点火验证唯一证据=2 tick 内产物增长面〔r325 律·state queue 面不信〕）→ **never-dry 常供给例常设步**")

# ---- preamble: wave number + seat + single-state ------------------------------
R("**波号 112=注册表 W111 行后首个自由号**〔r511 表尾锁例冻结前 fetch 实核表尾时 W112 号位净空·pf 行+WAVE_CONFIGS+prereg 路径三查+origin ls-tree vacancy 机验（本冻结窗 gate leg0b/leg2 实跑·r374 inbox+processed 双目录腿）＋全 inbox/processed/ W112 席位零外机命中（本机席位公示豁免=MSG-20261002-1922-bma 已推 origin e9f157e25 先于本冻结 r565 律〕。**单态零席位空档**：W105=bm-c r376 freeze（f2db133c5）+W106=bm-b r585 freeze（d6b2952e3）+W107=bm-a r587 freeze（a554dedd3）+W108=bm-c r378 freeze（3a3c51b73）+W109=bm-b r587 freeze（f077ae11b）+W110=bm-a r589 freeze（ff0b1869b）+W111=bm-b r589 freeze（e0a103ec1）**均已注册**（表尾=W111 行）·W112=无 skip-past-published 链面（本波 gate=单态门·pre-seat probe 与冻结窗 gate 双跑 derive 逐位恒等·ADMIT 回执 results/_r590bma_w112_band_gate.py rc0 实跑）。",
  "**波号 113=注册表 W112 行后首个自由号**〔r511 表尾锁例冻结前 fetch 实核表尾时 W113 号位净空·pf 行+WAVE_CONFIGS+prereg 路径三查+origin ls-tree vacancy 机验（本冻结窗 gate leg0b/leg2 实跑·r374 inbox+processed 双目录腿）＋全 inbox/processed/ W113 席位零外机命中（本机席位公示豁免=MSG-20261002-1949-bmc 已推 origin baa0c3888 先于本冻结 r565 律〕。**单态零席位空档**：W106=bm-b r585 freeze（d6b2952e3）+W107=bm-a r587 freeze（a554dedd3）+W108=bm-c r378 freeze（3a3c51b73）+W109=bm-b r587 freeze（f077ae11b）+W110=bm-a r589 freeze（ff0b1869b）+W111=bm-b r589 freeze（e0a103ec1）+W112=bm-a r590 freeze（0c4d67910）**均已注册**（表尾=W112 行）·W113=无 skip-past-published 链面（本波 gate=单态门·pre-seat probe 与冻结窗 gate 双跑 derive 逐位恒等·ADMIT 回执 results/_r382bmc_w113_band_gate.py rc0 实跑）。")

R("**席位时态注记（r307 两态族如实披露）**：席位公示窗先于冻结窗——pre-seat 机证=results/_r589bmb_w111_probe.py rc0（ADMIT-derive）；冻结窗 gate 重跑 derive 逐位恒等（A 265_004..267_003/B 61_401..61_600·hops 0/0·零分叉面）。",
  "**席位时态注记（r307 两态族如实披露）**：席位公示窗先于冻结窗——pre-seat 机证=results/_r382bmc_w113_probe.py rc0（ADMIT-derive）；冻结窗 gate 重跑 derive 逐位恒等（A 269_004..271_003/B 62_001..62_200·hops 0/1·零分叉面）。")

R("**席位推送窗一次 origin 前进实录**（首推被拒=bm-b r589 收轮 3b7da8dfe 中窗落账→外科 commit-tree 直投 payload=席位 MSG 单件 deletion-set 空断言→e9f157e25 一发即达；rev.A=唯一发布面·零 rebase 零 force〔r532 活写面律〕·本机活写面未触碰）。",
  "**席位推送窗零拒绝实录**（本地 main==origin 净空窗直推 baa0c3888 一发即达·payload=席位 MSG 单件·deletion-set 空·零 rebase 零 force〔r532 活写面律〕·本机活写面未触碰·rev.A=唯一发布面）。")

R("本波 ordinal=**第一百零二枚引擎波（机面计数：注册表 engine_owner 行 101+本候选）**·**bm-a 第三十二枚自有波**〔机面 derive：engine_owner==bm-a 行 31+本候选·gate leg0 机证在场·r359 律计数面以 gate 机输出为准〕。",
  "本波 ordinal=**第一百零三枚引擎波（机面计数：注册表 engine_owner 行 102+本候选）**·**bm-c 第三十三枚自有波**〔机面 derive：engine_owner==bm-c 行 32+本候选·gate leg0 机证在场·r359 律计数面以 gate 机输出为准〕。")

R("**带位（r535 机闸 derive 律·ADMIT 回执=results/_r590bma_w112_band_gate.py 单态门全腿实跑·pre-seat probe results/_r590bma_w112_probe.py 先跑·双窗 derive 恒等）**：本波 **A-ext seed=267_004..269_003**（**A 面算术续带**==W111 行 A 尾 267_003+1 起·步长 2_000·CLEAN 零拒绝点·refusal hops=0）；**B-ext exit seed=61_601..61_800**（**B 面算术续带**==W111 行 B 尾 61_600+1 起·步长 200·CLEAN 零拒绝点·refusal hops=0·双侧算术续带=W92 r370/W100 r583/W103 r584/W106 r585/W107 r587/W110 r589/W111 r589 先例族）。",
  "**带位（r535 机闸 derive 律·ADMIT 回执=results/_r382bmc_w113_band_gate.py 单态门全腿实跑·pre-seat probe results/_r382bmc_w113_probe.py 先跑·双窗 derive 恒等）**：本波 **A-ext seed=269_004..271_003**（**A 面算术续带**==W112 行 A 尾 269_003+1 起·步长 2_000·CLEAN 零拒绝点·refusal hops=0）；**B-ext exit seed=62_001..62_200**（**B 面撞值跳位窗**==W112 行 B 尾 61_800+1 起算术窗 61_801..62_000 撞 SEED_REGISTRY `cta_wave1`=62_000〔窗尾端点命中=W74/W81 判例族·两读法恒同解〕→ **法典 §4 D-20261002-05 钉死行越 hit 起窗** 62_001..62_200·refusal hops=1·撞值跳位先例族=W5/W26/W63/W68/W109）。")

R("R250：W112 带从未指派·测量面零结果可钓。扫描面=pre-W112 全一百零九行注册 N1 带表（表尾=W111 行·leg0 机证 109 行）",
  "R250：W113 带从未指派·测量面零结果可钓。扫描面=pre-W113 全一百一十行注册 N1 带表（表尾=W112 行·leg0 机证 110 行）")

R("`scripts/perpetual_faces_n1.py`（W2..W111 落地 runner 的 wave 参数化复用——同引擎同语义同切分律·仅法典 §4 新带；引擎侧 `scripts/saturation_engine.py`〔本机 bm-a 实例·tick 架构〕只做队列点火台账处理面·runner 零改写）",
  "`scripts/perpetual_faces_n1.py`（W2..W112 落地 runner 的 wave 参数化复用——同引擎同语义同切分律·仅法典 §4 新带；引擎侧 `Tools/saturation_engine.py`〔本机 bm-c 实例·常驻架构 v0.4 mtime-reload〕只做队列点火台账处理面·runner 零改写）")

# ---- sec.0 batch identity --------------------------------------------------------
R("- 批名=**PERPETUAL-N1-W112**。", "- 批名=**PERPETUAL-N1-W113**。")

R("起草窗实况：**W1..W110 N1 finalize 已全部落账**——净账本链头 **606,548**（bm-b r590 三波积压清空 cross-machine finalize〔W108 代 bm-c+W109 bm-b 自有+W110 代 bm-a·audit.machine=bm-b finalize_only=true 诚实归因·起草窗双中窗落账=锚随锚滚动律自 W107 滚至 W108 再滚至 W110·r576 锚滚律如实披露〕·K=239,920 合并池·voids LOWAMP-P1/P2）；**W111 bm-b finalize 未落账（一席 registered=本波 finalize 时 FAIL-CLOSED 前置一空档**（跑时复核；W111 烧录 bm-b 车道在飞）；累计 null 池投影=239,920+2,200（W111）+2,200（本波）=**244,320 投影**（机械算：239,920+4,400；",
  "起草窗实况：**W1..W111 N1 finalize 已全部落账**——净账本链头 **608,748**（bm-b r590 W111 finalize 落账〔one-pass〕·K=242,120 合并池·voids LOWAMP-P1/P2）；**W112 bm-a finalize 未落账（一席 registered=本波 finalize 时 FAIL-CLOSED 前置一空档**（跑时复核；W112 烧录 bm-a 车道在飞）；累计 null 池投影=242,120+2,200（W112）+2,200（本波）=**246,520 投影**（机械算：242,120+4,400；")

R("本机自有波 W110 12/12 烧毕交付+W107 finalize r589 closing 落账（engine_owner==bm-a 行 31 枚全览·W108/W109/W111=他机 engine_owner 波按 r508 零跨机重复律不可见）·引擎队列清空=供给律触发",
  "本机自有波 W108 12/12 烧毕交付+W108 finalize 已落账（bm-b r590 链头 drain 代收·yield 判例 66a8efae6·engine_owner==bm-c 行 32 枚全览·W109..W112=他机 engine_owner 波按 r508 零跨机重复律不可见）·引擎队列清空=供给律触发")

R("T-2026-10-01-141 s1 引擎线第 102 波·bm-a 第三十二枚自有波〔机面 derive：engine_owner==bm-a 行 31+本候选〕。（波号=注册表 W111 行后首个自由号·单态零席位空档〔席位公示=MSG-20261002-1922-bma 先推 origin e9f157e25 r565 律〕；lane-free；部门 dept:研究）。",
  "T-2026-10-01-141 s1 引擎线第 103 波·bm-c 第三十三枚自有波〔机面 derive：engine_owner==bm-c 行 32+本候选〕。（波号=注册表 W112 行后首个自由号·单态零席位空档〔席位公示=MSG-20261002-1949-bmc 先推 origin baa0c3888 r565 律〕；lane-free；部门 dept:研究）。")

R("（本机 bm-a 实例=**tick 架构**——每 tick 新进程读活工作树·冻结编辑落工作树后下一 tick 自见 W112 行并点火〔r535 律 tick 面免杀重启免做〕·**点火验证唯一证据=产物增长面**〔r325 律·2 tick 窗〕）",
  "（本机 bm-c 实例=**常驻架构 v0.4 mtime-reload**——冻结编辑落工作树后 LIVE 引擎下一 tick 重读活树自见 W113 行并点火〔D-20261002-03 修法·r325/r330 kill-restart 序免做〕·**点火验证唯一证据=产物增长面**〔r325 律·2 tick 窗〕）")

# ---- sec.0.5 banned gate ---------------------------------------------------------
R("`python Tools/banned_direction_gate.py --prereg research/PERPETUAL_N1_W112_PREREG.md`",
  "`python Tools/banned_direction_gate.py --prereg research/PERPETUAL_N1_W113_PREREG.md`")

R("（p2_calibration v1/v2 canon；W1 ext；W2..W111 落地）的种子带扩展重测",
  "（p2_calibration v1/v2 canon；W1 ext；W2..W112 落地）的种子带扩展重测")

R("禁向词面不在本件复述（机器闸为准·防证伪模式词面自害，W2..W111 同法先例）",
  "禁向词面不在本件复述（机器闸为准·防证伪模式词面自害，W2..W112 同法先例）")

# ---- sec.2/sec.3 method faces ----------------------------------------------------
R("- **A 档**（j=0..1,999）：entry rng seed=**267_004+j**（法典 §4 W112 行 A=267_004..269_003·**算术续带**==W111 行 A 尾 267_003+1 起·CLEAN 零拒绝点·ADMIT 回执在场）；p=`BASELINE_P[(j//50)%2]`（v1 50-seed 块交替惯例逐字）；随机入场短窗=**引擎退出**（v1 设计逐字）。",
  "- **A 档**（j=0..1,999）：entry rng seed=**269_004+j**（法典 §4 W113 行 A=269_004..271_003·**算术续带**==W112 行 A 尾 269_003+1 起·CLEAN 零拒绝点·ADMIT 回执在场）；p=`BASELINE_P[(j//50)%2]`（v1 50-seed 块交替惯例逐字）；随机入场短窗=**引擎退出**（v1 设计逐字）。")

R("- **B 档**（j=0..199）：entry rng=**267_004+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**61_601+j**（法典 §4 W112 行 B=61_601..61_800·**算术续带**==W111 行 B 尾 61_600+1 起·步长 200·CLEAN 零拒绝点·ADMIT 回执在场）；p_exit=`P_EXIT=0.05`。",
  "- **B 档**（j=0..199）：entry rng=**269_004+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**62_001+j**（法典 §4 W113 行 B=62_001..62_200·**撞值跳位窗**==W112 行 B 尾 61_800+1 起算术窗 61_801..62_000 撞 SEED_REGISTRY `cta_wave1`=62_000〔窗尾端点命中=W74/W81 判例族〕→ D-20261002-05 越 hit 起窗·hops=1·ADMIT 回执在场）；p_exit=`P_EXIT=0.05`。")

R("本波设计=W2..W111 逐字复用，runner probe 非本窗真态 no-op；账本 +0）",
  "本波设计=W2..W112 逐字复用，runner probe 非本窗真态 no-op；账本 +0）")

R("W112 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带（10_100..12_099/20_100..20_299）、W2..W111 在用带（**全注册·单态**）",
  "W113 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带（10_100..12_099/20_100..20_299）、W2..W112 在用带（**全注册·单态**）")

R("本波机验 ADMIT 回执在场=r590 bm-a 冻结窗（pre-seat probe 先跑·双窗 derive 恒等）；selftest leg 2 全表 disjoint+leg N3-R1 腿+腿探针簇腿+leg W102..W111 在用带腿+A 算术窗净腿+B 算术窗净腿",
  "本波机验 ADMIT 回执在场=r382 bm-c 冻结窗（pre-seat probe 先跑·双窗 derive 恒等）；selftest leg 2 全表 disjoint+leg N3-R1 腿+腿探针簇腿+leg W102..W112 在用带腿+A 算术窗净腿+B 跳位窗净腿+B 跳位先例腿（算术窗含 62_000 拒绝点断言+越 hit 起窗恒等断言）")

# ---- sec.4 ledger face -----------------------------------------------------------
R("合并池 `canon 120 + 已落账波值（起草窗实测 W1..W110 已落账 239,920 实测·derive 禁手抄）+本波 2,200`",
  "合并池 `canon 120 + 已落账波值（起草窗实测 W1..W111 已落账 242,120 实测·derive 禁手抄）+本波 2,200`")

R('append_ledger(batch_name="PERPETUAL-N1-W112", batch_trials=2200, file_name="results/perpetual_faces/n1_w112_results.json"',
  'append_ledger(batch_name="PERPETUAL-N1-W113", batch_trials=2200, file_name="results/perpetual_faces/n1_w113_results.json"')

# ---- sec.5 pre-run predictions (anchor rolls W110 -> W111) -----------------------
R("（起草窗实况注记：**W1..W110 N1 finalize 已全部落账**——净账本链头 606,548=bm-b r590 三波积压清空 cross-machine finalize〔W108 代 bm-c+W109 bm-b 自有+W110 代 bm-a·起草窗双中窗落账·锚滚动律自 W107 滚至 W108 再滚至 W110·r576 锚滚律如实披露〕·**K=239,920 合并池**；**W111 一空档在飞**（本波 §5 预测键=**W110 finalize 实测值**〔results/perpetual_faces/n1_w110_results.json·N1 面最新已落账键〕）。",
  "（起草窗实况注记：**W1..W111 N1 finalize 已全部落账**——净账本链头 608,748=bm-b r590 W111 finalize 落账〔one-pass〕·**K=242,120 合并池**；**W112 一空档在飞**（本波 §5 预测键=**W111 finalize 实测值**〔results/perpetual_faces/n1_w111_results.json·N1 面最新已落账键〕）。")

R("1. W112-only mu 与累计池 merged mu（W110 实测键 **−0.09271653342780928**·K=239,920 合并池·W110-only 实测 **−0.10390695454545468**）差异 **|Δ|<0.02**（W2..W110 共三十+面实测 mu 稳定先例·单波跨键律）。",
  "1. W113-only mu 与累计池 merged mu（W111 实测键 **−0.09276358334710065**·K=242,120 合并池·W111-only 实测 **−0.09789459090909067**）差异 **|Δ|<0.02**（W2..W111 共三十+面实测 mu 稳定先例·单波跨键律）。")

R("2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.24487617466590078**=W110 合并池实测）。",
  "2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.24489883563788295**=W111 合并池实测）。")

R("3. A 档 full_sharpe_p95 与 W110 A 档 p95（**0.3159** 实测锚）差 **<0.05**（门标准注记法 W5..W110 先例：结果知情报校准面·仅作机器断言伪测用·测量面非注册利益）。",
  "3. A 档 full_sharpe_p95 与 W111 A 档 p95（**0.3191** 实测锚）差 **<0.05**（门标准注记法 W5..W111 先例：结果知情报校准面·仅作机器断言伪测用·测量面非注册利益）。")

R("4. K-lift 线移动幅度 **≥−0.02**（累计池加深零 se_mu·线自 mu/sigma 微调面非质变——W3..W110 先例·W99 +0.0001/W100 −0.0005/W101 −0.0003/W103 +0.0005/W104 −0.0001/W105 −0.0002/W106 **+0.0002**/W107 **−0.0002**/W108 **+0.0003**/W109 **0.0000**/W110 **0.0000** 正负交替如实报正负）；键 W110 实测 K-lift **0.0000**（line_merged@K239,920 **1.1708**·line_pre 1.1708·n_eff_held 604,348；se_mu 收窄链 W107 0.000507→W108 0.000505→W109 0.000502→W110 **0.0005**）。",
  "4. K-lift 线移动幅度 **≥−0.02**（累计池加深零 se_mu·线自 mu/sigma 微调面非质变——W3..W111 先例·W99 +0.0001/W100 −0.0005/W101 −0.0003/W103 +0.0005/W104 −0.0001/W105 −0.0002/W106 **+0.0002**/W107 **−0.0002**/W108 **+0.0003**/W109 **0.0000**/W110 **0.0000**/W111 **0.0000** 正负交替如实报正负）；键 W111 实测 K-lift **0.0000**（line_merged@K242,120 **1.171**·line_pre 1.171·n_eff_held 606,548；se_mu 收窄链 W108 0.000505→W109 0.000502→W110 0.0005→W111 **0.000498**）。")

R("5. **W113+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 269_004..271_003 **CLEAN**（hops=0）；B **62_001..62_200（hops=1·撞值跳位）**——算术窗 61_801..62_000 撞 SEED_REGISTRY `cta_wave1`=62_000 → 法典 §4 W5 撞值跳位先例族（D-20261002-05）·下波冻结方必复核非转抄（r590 冻结窗 gate 回执尾行）。",
  "5. **W114+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 271_004..273_003 **CLEAN**（hops=0）；B 62_201..62_400 **CLEAN**（hops=0）（r382 冻结窗 gate 回执尾行）。")

# ---- sec.6 products --------------------------------------------------------------
R("run --shard k --of 12 --wave 112/finalize --wave 112；probe/parity=W2 设计验证面·本波跑完 no-op）；点火面 `scripts/saturation_engine.py`（本机 bm-a 实例·**tick 架构**·本地队列→PreIgnitionChecks→分离子进程点火→完成探测→台账处理〔runner_args --lane engine 车道合同同 r523 律〕）·**点火验证=2 tick 内产物增长面**（n1_w112/ 分片计数增长·唯一点火证据·r325 律）",
  "run --shard k --of 12 --wave 113/finalize --wave 113；probe/parity=W2 设计验证面·本波跑完 no-op）；点火面 `Tools/saturation_engine.py`（本机 bm-c 实例·**常驻架构 v0.4 mtime-reload**·本地队列→PreIgnitionChecks→分离子进程点火→完成探测→台账处理〔runner_args --lane engine 车道合同同 r523 律〕）·**点火验证=2 tick 内产物增长面**（n1_w113/ 分片计数增长·唯一点火证据·r325 律）")

R("- 交付：`results/p2cal_ext/n1_w112/shard-<k>-of-12.json`（append-only·确定性）；`results/perpetual_faces/n1_w112_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 链序前置=**起草窗四空档在飞上游**——跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态律恒在）。",
  "- 交付：`results/p2cal_ext/n1_w113/shard-<k>-of-12.json`（append-only·确定性）；`results/perpetual_faces/n1_w113_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 链序前置=**起草窗一空档在飞上游（W112 bm-a）**——跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态律恒在）。")

R("- 引擎台账：bm-a tick 架构=engine ledger jsonl+state/face/history 从 git 交付（engine_owner==bm-a 32 枚实况范式=机面 derive：W12/W18/W21/W24/W27/W30/W33/W35/W44/W45/W48/W54/W57/W62/W64/W68/W73/W75/W77/W81/W84/W86/W87/W90/W94/W96/W98/W101/W104/W107/W110+本波 W112 候选〔31 行注册+候选·以 gate leg0 机证为准〕）；attrition 账本完整性 tripwire 覆盖本波产物件（r448 律）。",
  f"- 引擎台账：bm-c 常驻架构 v0.4=engine ledger jsonl+state/face/history 从 git 交付（engine_owner==bm-c 33 枚实况范式=机面 derive：{bmc_list}+本波 W113 候选〔32 行注册+候选·以 gate leg0 机证为准〕）；attrition 账本完整性 tripwire 覆盖本波产物件（r448 律）。")

# ---- batch-identity leftovers: informational print + hard asserts ---------------
leftovers = [s for s in ("PERPETUAL-N1-W112", "267_004+j", "61_601+j", "n1_w112_results",
                         "r590bma", "e9f157e25", "MSG-20261002-1922-bma") if s in t]
print("leftover tokens:", leftovers)
assert not leftovers, "batch-identity leftovers must be zero (W112 active-face tokens all replaced)"
hist_leftovers = [s for s in ("W112", "r590", "61_601", "267_004") if s in t]
print("history-reference tokens remaining (expected, registered-row context):", hist_leftovers)

open(DST, "wb").write(t.encode("utf-8"))
print("WROTE", DST, len(t), "chars")
