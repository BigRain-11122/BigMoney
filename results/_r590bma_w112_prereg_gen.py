# -*- coding: utf-8 -*-
"""r590 bm-a W112 per-wave prereg generator: copy-adapt from the W111 prereg
(bm-b r589 freeze e0a103ec1; anchor stays W107 = latest landed finalize at
this freeze window; chain state W1..W107 landed, four in-flight upstream
seats W108 bm-c + W109 bm-b + W110 bm-a + W111 bm-b registered-unfinalized).

W112 = ONE HUNDRED-AND-SECOND engine wave BY MACHINE-DERIVE (engine_owner
rows 101 + candidate), bm-a's THIRTY-SECOND owned (engine_owner==bm-a rows
31 + candidate, gate leg0 machine output governs per r359 law).
Bands (machine-derived, seat probe + freeze-window gate double-run bitwise
identical): A 267_004..269_003 / B 61_601..61_800, both sides arithmetic
continuation from the registered W111 tails, hops 0/0.
"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "research", "PERPETUAL_N1_W111_PREREG.md")
DST = os.path.join(REPO, "research", "PERPETUAL_N1_W112_PREREG.md")
t = open(SRC, "rb").read().decode("utf-8")

def rep(old, new, count=1):
    global t
    c = t.count(old)
    assert c == count, f"anchor not unique ({c} != {count}): {old[:70]}..."
    t = t.replace(old, new)
    print("rep ok:", old[:48].replace("\n", " "))

R = rep

# ---- header ------------------------------------------------------------------
R("# PERPETUAL-N1-W111 预注册 · N1 nulls-deepening 泵第 109（never-dry 常供给例常设步·第一百零一枚引擎波·机面 derive：engine_owner 行 100+本候选·bm-b 第三十八枚自有波〔r589〕）",
  "# PERPETUAL-N1-W112 预注册 · N1 nulls-deepening 泵第 110（never-dry 常供给例常设步·第一百零二枚引擎波·机面 derive：engine_owner 行 101+本候选·bm-a 第三十二枚自有波〔r590〕）")

# ---- preamble: engine instance face (bm-b -> bm-a, both tick arch) ------------
R("本机 bm-b 实例=**tick 架构**——每 tick 新进程读活工作树·新登记行对下一 tick 天然可见〔r535 律 tick 面免杀重启免做〕·点火验证唯一证据=2 tick 内产物增长面〔r325 律·state queue 面不信〕）→ **never-dry 常供给例常设步**",
  "本机 bm-a 实例=**tick 架构**——每 tick 新进程读活工作树·新登记行对下一 tick 天然可见〔r535 律 tick 面免杀重启免做〕·点火验证唯一证据=2 tick 内产物增长面〔r325 律·state queue 面不信〕）→ **never-dry 常供给例常设步**")

# ---- preamble: wave number + seat + single-state ------------------------------
R("**波号 111=注册表 W110 行后首个自由号**〔r511 表尾锁例冻结前 fetch 实核表尾时 W111 号位净空·pf 行+WAVE_CONFIGS+prereg 路径三查+origin ls-tree vacancy 机验（本冻结窗 gate leg0b/leg2 实跑）＋全 inbox/processed/ W111 席位零外机命中（本机席位公示豁免=MSG-20261002-1911-bmb 已推 origin 8088582ba 先于本冻结 r565 律〕。**单态零席位空档**：W104=bm-a r586 union（48f6f2ff1）+W105=bm-c r376 freeze（f2db133c5）+W106=bm-b r585 freeze（d6b2952e3）+W107=bm-a r587 freeze（a554dedd3）+W108=bm-c r378 freeze（3a3c51b73）+W109=bm-b r587 freeze（f077ae11b）+W110=bm-a r589 freeze（ff0b1869b）**均已注册**（表尾=W110 行）·W111=无 skip-past-published 链面（本波 gate=单态门·pre-seat probe 与冻结窗 gate 双跑 derive 逐位恒等·ADMIT 回执 results/_r589bmb_w111_band_gate.py rc0 实跑）。",
  "**波号 112=注册表 W111 行后首个自由号**〔r511 表尾锁例冻结前 fetch 实核表尾时 W112 号位净空·pf 行+WAVE_CONFIGS+prereg 路径三查+origin ls-tree vacancy 机验（本冻结窗 gate leg0b/leg2 实跑·r374 inbox+processed 双目录腿）＋全 inbox/processed/ W112 席位零外机命中（本机席位公示豁免=MSG-20261002-1922-bma 已推 origin e9f157e25 先于本冻结 r565 律〕。**单态零席位空档**：W105=bm-c r376 freeze（f2db133c5）+W106=bm-b r585 freeze（d6b2952e3）+W107=bm-a r587 freeze（a554dedd3）+W108=bm-c r378 freeze（3a3c51b73）+W109=bm-b r587 freeze（f077ae11b）+W110=bm-a r589 freeze（ff0b1869b）+W111=bm-b r589 freeze（e0a103ec1）**均已注册**（表尾=W111 行）·W112=无 skip-past-published 链面（本波 gate=单态门·pre-seat probe 与冻结窗 gate 双跑 derive 逐位恒等·ADMIT 回执 results/_r590bma_w112_band_gate.py rc0 实跑）。")

R("**席位推送窗三次 origin 前进实录**（首推被拒→r585 纯 FF 窗重落 16feda9→二推被爪拦〔origin 再前进·r374 分叉伪影族〕→三落 8088582ba 一发即达；首稿从未可见=零外见性·rev.A=唯一发布面·重落过程零 rebase 零 force〔r532 活写面律〕·共享 append-only 面 pool_core_samples.jsonl 按 r570 律 origin-verbatim+本地行 union 1051 行全 dict）。",
  "**席位推送窗一次 origin 前进实录**（首推被拒=bm-b r589 收轮 3b7da8dfe 中窗落账→外科 commit-tree 直投 payload=席位 MSG 单件 deletion-set 空断言→e9f157e25 一发即达；rev.A=唯一发布面·零 rebase 零 force〔r532 活写面律〕·本机活写面未触碰）。")

R("本波 ordinal=**第一百零一枚引擎波（机面计数：注册表 engine_owner 行 100+本候选）**·**bm-b 第三十八枚自有波**〔机面 derive：engine_owner==bm-b 行 37+本候选·gate leg0 机证在场·r359 律计数面以 gate 机输出为准〕。",
  "本波 ordinal=**第一百零二枚引擎波（机面计数：注册表 engine_owner 行 101+本候选）**·**bm-a 第三十二枚自有波**〔机面 derive：engine_owner==bm-a 行 31+本候选·gate leg0 机证在场·r359 律计数面以 gate 机输出为准〕。")

R("**带位（r535 机闸 derive 律·ADMIT 回执=results/_r589bmb_w111_band_gate.py 单态门全腿实跑·pre-seat probe+冻结窗 gate 双跑 derive 恒等）**：本波 **A-ext seed=265_004..267_003**（**A 面算术续带**==W110 行 A 尾 265_003+1 起·步长 2_000·CLEAN 零拒绝点·refusal hops=0）；**B-ext exit seed=61_401..61_600**（**B 面算术续带**==W110 行 B 尾 61_400+1 起·步长 200·CLEAN 零拒绝点·refusal hops=0·双侧算术续带=W92 r370/W100 r583/W103 r584/W106 r585/W107 r587/W110 r589 先例族）。",
  "**带位（r535 机闸 derive 律·ADMIT 回执=results/_r590bma_w112_band_gate.py 单态门全腿实跑·pre-seat probe results/_r590bma_w112_probe.py 先跑·双窗 derive 恒等）**：本波 **A-ext seed=267_004..269_003**（**A 面算术续带**==W111 行 A 尾 267_003+1 起·步长 2_000·CLEAN 零拒绝点·refusal hops=0）；**B-ext exit seed=61_601..61_800**（**B 面算术续带**==W111 行 B 尾 61_600+1 起·步长 200·CLEAN 零拒绝点·refusal hops=0·双侧算术续带=W92 r370/W100 r583/W103 r584/W106 r585/W107 r587/W110 r589/W111 r589 先例族）。")

R("R250：W111 带从未指派·测量面零结果可钓。扫描面=pre-W111 全一百零八行注册 N1 带表（表尾=W110 行·leg0 机证 108 行）",
  "R250：W112 带从未指派·测量面零结果可钓。扫描面=pre-W112 全一百零九行注册 N1 带表（表尾=W111 行·leg0 机证 109 行）")

R("`scripts/perpetual_faces_n1.py`（W2..W110 落地 runner 的 wave 参数化复用——同引擎同语义同切分律·仅法典 §4 新带；引擎侧 `scripts/saturation_engine.py`〔本机 bm-b 实例·tick 架构〕只做队列点火台账处理面·runner 零改写）",
  "`scripts/perpetual_faces_n1.py`（W2..W111 落地 runner 的 wave 参数化复用——同引擎同语义同切分律·仅法典 §4 新带；引擎侧 `scripts/saturation_engine.py`〔本机 bm-a 实例·tick 架构〕只做队列点火台账处理面·runner 零改写）")

# ---- §0 batch identity --------------------------------------------------------
R("- 批名=**PERPETUAL-N1-W111**。", "- 批名=**PERPETUAL-N1-W112**。")

R("起草窗实况：**W1..W107 N1 finalize 已全部落账**——净账本链头 **599,948**（bm-a r589 closing W107 落账〔one-pass·起草窗中段落账·锚随锚滚动律自 W106 滚至 W107·如实披露〕·K=233,320 合并池·voids LOWAMP-P1/P2）；**W108 bm-c finalize 未落账+W109 bm-b finalize 未落账+W110 bm-a finalize 未落账（三席 registered=本波 finalize 时 FAIL-CLOSED 前置三空档**（跑时复核；W108/W109/W110 12/12 烧毕产物均已交付 origin）；累计 null 池投影=233,320+2,200×3（W108..W110）+2,200（本波）=**242,120 投影**（机械算：233,320+8,800；",
  "起草窗实况：**W1..W107 N1 finalize 已全部落账**——净账本链头 **599,948**（bm-a r589 closing W107 落账〔one-pass〕·K=233,320 合并池·voids LOWAMP-P1/P2）；**W108 bm-c finalize 未落账+W109 bm-b finalize 未落账+W110 bm-a finalize 未落账+W111 bm-b finalize 未落账（四席 registered=本波 finalize 时 FAIL-CLOSED 前置四空档**（跑时复核；W108/W109/W110 12/12 烧毕产物均已交付 origin·W111 烧录本窗在飞 3/12）；累计 null 池投影=233,320+2,200×4（W108..W111）+2,200（本波）=**244,320 投影**（机械算：233,320+11,000；")

R("本机自有波 W109 12/12 烧毕交付+W106 finalize r588 落账（engine_owner==bm-b 行 37 枚全览·W108/W110=他机 engine_owner 波按 r508 零跨机重复律不可见）·引擎队列清空=供给律触发",
  "本机自有波 W110 12/12 烧毕交付+W107 finalize r589 closing 落账（engine_owner==bm-a 行 31 枚全览·W108/W109/W111=他机 engine_owner 波按 r508 零跨机重复律不可见）·引擎队列清空=供给律触发")

R("T-2026-10-01-141 s1 引擎线第 101 波·bm-b 第三十八枚自有波〔机面 derive：engine_owner==bm-b 行 37+本候选〕。（波号=注册表 W110 行后首个自由号·单态零席位空档〔席位公示=MSG-20261002-1911-bmb 先推 origin 8088582ba r565 律〕；lane-free；部门 dept:研究）。",
  "T-2026-10-01-141 s1 引擎线第 102 波·bm-a 第三十二枚自有波〔机面 derive：engine_owner==bm-a 行 31+本候选〕。（波号=注册表 W111 行后首个自由号·单态零席位空档〔席位公示=MSG-20261002-1922-bma 先推 origin e9f157e25 r565 律〕；lane-free；部门 dept:研究）。")

R("（本机 bm-b 实例=**tick 架构**——每 tick 新进程读活工作树·冻结编辑落工作树后下一 tick 自见 W111 行并点火〔r535 律 tick 面免杀重启免做〕·**点火验证唯一证据=产物增长面**〔r325 律·2 tick 窗〕）",
  "（本机 bm-a 实例=**tick 架构**——每 tick 新进程读活工作树·冻结编辑落工作树后下一 tick 自见 W112 行并点火〔r535 律 tick 面免杀重启免做〕·**点火验证唯一证据=产物增长面**〔r325 律·2 tick 窗〕）")

# ---- §0.5 banned gate ---------------------------------------------------------
R("`python Tools/banned_direction_gate.py --prereg research/PERPETUAL_N1_W111_PREREG.md`",
  "`python Tools/banned_direction_gate.py --prereg research/PERPETUAL_N1_W112_PREREG.md`")

R("（p2_calibration v1/v2 canon；W1 ext；W2..W110 落地）的种子带扩展重测",
  "（p2_calibration v1/v2 canon；W1 ext；W2..W111 落地）的种子带扩展重测")

R("禁向词面不在本件复述（机器闸为准·防证伪模式词面自害，W2..W110 同法先例）",
  "禁向词面不在本件复述（机器闸为准·防证伪模式词面自害，W2..W111 同法先例）")

# ---- §2/§3 method faces -------------------------------------------------------
R("- **A 档**（j=0..1,999）：entry rng seed=**265_004+j**（法典 §4 W111 行 A=265_004..267_003·**算术续带**==W110 行 A 尾 265_003+1 起·CLEAN 零拒绝点·ADMIT 回执在场）；p=`BASELINE_P[(j//50)%2]`（v1 50-seed 块交替惯例逐字）；随机入场短窗=**引擎退出**（v1 设计逐字）。",
  "- **A 档**（j=0..1,999）：entry rng seed=**267_004+j**（法典 §4 W112 行 A=267_004..269_003·**算术续带**==W111 行 A 尾 267_003+1 起·CLEAN 零拒绝点·ADMIT 回执在场）；p=`BASELINE_P[(j//50)%2]`（v1 50-seed 块交替惯例逐字）；随机入场短窗=**引擎退出**（v1 设计逐字）。")

R("- **B 档**（j=0..199）：entry rng=**265_004+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**61_401+j**（法典 §4 W111 行 B=61_401..61_600·**算术续带**==W110 行 B 尾 61_400+1 起·步长 200·CLEAN 零拒绝点·ADMIT 回执在场）；p_exit=`P_EXIT=0.05`。",
  "- **B 档**（j=0..199）：entry rng=**267_004+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**61_601+j**（法典 §4 W112 行 B=61_601..61_800·**算术续带**==W111 行 B 尾 61_600+1 起·步长 200·CLEAN 零拒绝点·ADMIT 回执在场）；p_exit=`P_EXIT=0.05`。")

R("本波设计=W2..W110 逐字复用，runner probe 非本窗真态 no-op；账本 +0）",
  "本波设计=W2..W111 逐字复用，runner probe 非本窗真态 no-op；账本 +0）")

R("W111 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带（10_100..12_099/20_100..20_299）、W2..W110 在用带（**全注册·单态**）",
  "W112 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带（10_100..12_099/20_100..20_299）、W2..W111 在用带（**全注册·单态**）")

R("本波机验 ADMIT 回执在场=r589 bm-b 冻结窗（pre-seat probe 先跑·双窗 derive 恒等）；selftest leg 2 全表 disjoint+leg N3-R1 腿+腿探针簇腿+leg W102..W110 在用带腿+A 算术窗净腿+B 算术窗净腿",
  "本波机验 ADMIT 回执在场=r590 bm-a 冻结窗（pre-seat probe 先跑·双窗 derive 恒等）；selftest leg 2 全表 disjoint+leg N3-R1 腿+腿探针簇腿+leg W102..W111 在用带腿+A 算术窗净腿+B 算术窗净腿")

# ---- §4 ledger face -----------------------------------------------------------
R("合并池 `canon 120 + 已落账波值（起草窗实测 W1..W107 已落账 233,320 实测·derive 禁手抄）+本波 2,200`",
  "合并池 `canon 120 + 已落账波值（起草窗实测 W1..W107 已落账 233,320 实测·derive 禁手抄）+本波 2,200`")

R('append_ledger(batch_name="PERPETUAL-N1-W111", batch_trials=2200, file_name="results/perpetual_faces/n1_w111_results.json"',
  'append_ledger(batch_name="PERPETUAL-N1-W112", batch_trials=2200, file_name="results/perpetual_faces/n1_w112_results.json"')

# ---- §5 pre-run predictions (anchor stays W107) --------------------------------
R("（起草窗实况注记：**W1..W107 N1 finalize 已全部落账**——净账本链头 599,948=bm-a r589 closing W107 落账〔one-pass·起草窗中段落账·锚滚动律自 W106 滚动至 W107·r576 锚滚律如实披露〕·**K=233,320 合并池**；**W108/W109/W110 三空档在飞**（本波 §5 预测键=**W107 finalize 实测值**〔results/perpetual_faces/n1_w107_results.json·N1 面最新已落账键〕）。",
  "（起草窗实况注记：**W1..W107 N1 finalize 已全部落账**——净账本链头 599,948=bm-a r589 closing W107 落账〔one-pass〕·**K=233,320 合并池**；**W108/W109/W110/W111 四空档在飞**（本波 §5 预测键=**W107 finalize 实测值**〔results/perpetual_faces/n1_w107_results.json·N1 面最新已落账键〕）。")

R("1. W111-only mu 与累计池 merged mu（W107 实测键 **−0.0927601842962455**·K=233,320 合并池·W107-only 实测 **−0.09942518181818182**）差异 **|Δ|<0.02**（W2..W107 共三十+面实测 mu 稳定先例·单波跨键律）。",
  "1. W112-only mu 与累计池 merged mu（W107 实测键 **−0.0927601842962455**·K=233,320 合并池·W107-only 实测 **−0.09942518181818182**）差异 **|Δ|<0.02**（W2..W107 共三十+面实测 mu 稳定先例·单波跨键律）。")

R("5. **W112+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 267_004..269_003 **CLEAN**（hops=0）；B 61_601..61_800 **CLEAN**（hops=0）（r589 冻结窗 gate 回执尾行）。",
  "5. **W113+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 269_004..271_003 **CLEAN**（hops=0）；B **62_001..62_200（hops=1·撞值跳位）**——算术窗 61_801..62_000 撞 SEED_REGISTRY `cta_wave1`=62_000 → 法典 §4 W5 撞值跳位先例族（D-20261002-05）·下波冻结方必复核非转抄（r590 冻结窗 gate 回执尾行）。")

# ---- §6 products --------------------------------------------------------------
R("run --shard k --of 12 --wave 111/finalize --wave 111；probe/parity=W2 设计验证面·本波跑完 no-op）；点火面 `scripts/saturation_engine.py`（本机 bm-b 实例·**tick 架构**·本地队列→PreIgnitionChecks→分离子进程点火→完成探测→台账处理〔runner_args --lane engine 车道合同同 r523 律〕）·**点火验证=2 tick 内产物增长面**（n1_w111/ 分片计数增长·唯一点火证据·r325 律）",
  "run --shard k --of 12 --wave 112/finalize --wave 112；probe/parity=W2 设计验证面·本波跑完 no-op）；点火面 `scripts/saturation_engine.py`（本机 bm-a 实例·**tick 架构**·本地队列→PreIgnitionChecks→分离子进程点火→完成探测→台账处理〔runner_args --lane engine 车道合同同 r523 律〕）·**点火验证=2 tick 内产物增长面**（n1_w112/ 分片计数增长·唯一点火证据·r325 律）")

R("- 交付：`results/p2cal_ext/n1_w111/shard-<k>-of-12.json`（append-only·确定性）；`results/perpetual_faces/n1_w111_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 链序前置=**起草窗三空档在飞上游**——跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态律恒在）。",
  "- 交付：`results/p2cal_ext/n1_w112/shard-<k>-of-12.json`（append-only·确定性）；`results/perpetual_faces/n1_w112_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 链序前置=**起草窗四空档在飞上游**——跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态律恒在）。")

R("bm-b tick 架构=engine ledger jsonl+state/face/history 从 git 交付（engine_owner==bm-b 38 枚实况范式=机面 derive：W2..W14 段 bm-b 行+W16..W110 段 bm-b 行〔37 行注册+候选·以 gate leg0 机证为准；r359 律计数面以 gate 机输出为准〕）",
  "bm-a tick 架构=engine ledger jsonl+state/face/history 从 git 交付（engine_owner==bm-a 32 枚实况范式=机面 derive：W12/W18/W21/W24/W27/W30/W33/W35/W44/W45/W48/W54/W57/W62/W64/W68/W73/W75/W77/W81/W84/W86/W87/W90/W94/W96/W98/W101/W104/W107/W110+本波 W112 候选〔31 行注册+候选·以 gate leg0 机证为准〕）")

# ---- final freeze line --------------------------------------------------------
# (the W111 prereg carries no "per-wave prereg=..." self-reference line -- no-op
#  guard per the W110 generator lineage; the canon row lands via freeze edits)

# safety: no W111-specific stragglers
leftovers = [s for s in ("W111", "r589", "bm-b", "61_401", "265_004") if s in t]
print("leftover tokens:", leftovers)

open(DST, "wb").write(t.encode("utf-8"))
print("WROTE", DST, len(t), "chars")
