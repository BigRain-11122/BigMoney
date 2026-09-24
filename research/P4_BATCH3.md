# P4-B3-DCA 预注册 · 死扛族 #14 补仓摊薄 staged vs single-shot 机制级对照（跑前冻结件）

> **预注册纪律**：本件跑前写死（BACKTEST_PLAN 铁律 ③：禁跑到达标为止、禁跑后调门槛、禁重跑）；freeze commit 先于一切触碰批产物的命令（R99 律）；§7/§8 跑前必须为空。
> 令链：CEO O-20260923-1705（风格动物园）→ zoo #14 死扛族（批三）→ spec `research/shortline/P4_BATCH3_DCA_SPEC.md`（r138 一次定稿）→ T-42 引擎 staged_entry 旗标（r139 done，33/33 门）→ **本件=批测预注册**；认领 F-04 MSG-20260925-0410 + 票 T-2026-09-25-44（同轮认领同轮开工，O-1730 即时律）。
> 跑批脚本：`scripts/p4_batch3_dca.py`（GRID-P1 r136-137 范式：checkpoint 行级断点续跑 t22 律 + finalize 只读文件 T-33 律 + hermetic selftest 子命令）。

## §0 批件身份

- 批名：**P4-B3-DCA**（死扛族 #14 补仓摊薄·机制级对照）；批号格数（N_eff 口径，扩容即买单）=**125**：8 判读格 ×(1×+×2)=16 引擎跑 + 100 随机 null（50/退出制）+ 6 在册锚定复现 + 1 PROS-OVB-CE-01 D6 参照跑 + 2 被动基线。
- 认领：F-04 先行=MSG-20260925-0410（fleet/inbox/）＋票 T-2026-09-25-44-P1（claimed 即锁）。
- 部门归属：dept:研究（风格族机制级对照=本批主产出）＋dept:工程（staged_entry 旗标首次产线使用）。
- 算力预算：预估 ~3-8min 串行单进程（GRID-P1 112 试验同构先例，本批 125）；workers=1 BelowNormal（autofill C8 启动侧设定）；批报告必带 audit 段。>5min 批一律入 `results/runnable_pool.json`（O-2100 s2），**轮内禁内联代跑**。

## §1 α 机制段（四选一勾选 · D6 机制门槛）

- [x] **行为偏差**（spec §4 冻结论证逐字继承）：超跌触发日的恐慌卖压（处置效应+损失厌恶踩踏）使 ETF 短端价格偏离均衡；网格分批承接的对手方=被迫止损者与非信息驱动抛售者，承接方赚取行为补偿。
- **本批真问题（机制级对照，主判读面）**：P-4 批一已判深水锚定 full-shot=接飞刀（low252 full −0.267/OOS −1.003）＋oversold_bounce sleeve 差 0.02 未过线（0.332/0.335 vs vi 0.4004）——**入场工程（分批摊薄）是否足以翻转同一超跌信号族的判负**。批的存活判据首先是「判读」（配对三列），注册仅是附带可能。
- **诚实反方（跑前写死）**：下刀尾险——趋势下跌政体中 −8% 止损必咬合；加仓=向下跌方向集中敞口；止损线随 VWAP 摊薄逐档下移（定义性代价，spec §3-c 披露）。
- **同族相关性准入检查（D6）**：参照集=**在册 6 员（NAMED_SIX）+ PROS-OVB-CE-01**（oversold_bounce sleeve2 注册族，spec §5 指名最近亲族）；逐对清单在结果 JSON per-pair 披露；**线=0.70**：registered-face `max|corr|≥0.70 → 拒收注册面**（机制新颖性条款；对照判读面不因此失效——批的知识产出=「分批是否改判」）。same-batch face=T-33 merge 语义（后优先级并入先；优先级序=runner docstring 冻结序，GRID-P1 r137 零格裁定同律，r71 双读法协议）；两触发互为同批面逐对披露。

## §2 数据与面板（跑前探针事实）

- 宇宙/池：core48 裸码 48 只（smoke 实测 48/48 可读）。
- 窗口与 **evidence_cutoff=2026-09-24**（冻结日面板现值；smoke 数据新鲜度实测 latest bar 2026-09-24；前向锁盒 D2：cutoff 后新 bar 永不回流本批）；结果 JSON 顶层必带 `science_gates.cutoff_meta(cutoff)` 字段（缺=C2 VIOLATION）。
- 数据完备门（不过门禁跑批=批 VOID）：①patch selftest（Cost/Exit 补丁咬合+恢复）；②48/48 面板 at cutoff；③**锚定 6/6 逐位复现**（member_run，成员自带 evidence_cutoff 自截断）——任一破=VOID exit 2 无判定。PROS-OVB-CE-01 载入失败=D6 参照面缺格如实披露（判读面不受影响），不作 VOID 条件。

## §3 方法学（冻结参数）

- 触发构造**逐字=批一预注册**（`scripts/p4_batch1_screen.py` build_entries 单一真值源，本 runner import 复用零重写）：
  - `oversold_bounce_20_15`（zoo#9 状态制，params={}）：entry=(close.pct_change(20)<−0.15)&(amount MA5<0.8×MA20)，exit=状态清除（pos>0 二值化）；
  - `low252_prox_top5_r20`（zoo#12 轮动制，params={"max_positions":5,"position_size_pct":0.19}）：score=close/close.rolling(252,min_periods=200).min()，top-5 **升序**（最接近 52 周低点），20d 非重叠冻结成员（_topk_frozen）。
- 入场制（本批对照变量）：**single-shot**=引擎 legacy 缺省（T-42 旗标 None 路径字节恒等）vs **staged**=`staged_entry={"grid_fracs":(0.40,0.30,0.30),"add_triggers":(0.0,−0.05,−0.10)}`（spec §2 冻结值：首档=正常信号；第 k 档 close≤首档成交价×(1+trigger_k) 收盘排队次日 open 执行；max_adds=2 封顶；VWAP 记账；hwm/trailing 不重置）。
- 退出制：default（引擎缺省 8d 强平/分档止盈/−8% 硬止损/25d 上限）| **CE 注册契约**（CE_PARAMS time_decay 25d/5%+trailing 0.10+ExitPatch loss_time_days=16）。
- null 对照：**n=50/退出制**（p∈{0.02,0.05}×25 seeds）；seed 基=**56500**（`science_gates.SEED_REGISTRY['p4_batch3_dca']` **跑前登记**；default 56500+k / ce 56550+k，k<50——grid_p1 55500 之上新空带，与历史族零重叠）+被动基线 EW48 双口径（J8 公式）=一致性信息列。
- 成本口径：**V1 legacy 13bp 恒开**（单边 cost_rate=佣金+经手+监管+滑点）＋**×2 压测面**（CostPatch(2.0)，P-4 族先例线）；成本压测=判读披露面非门。
- 账本：`science_gates.append_ledger("P4-B3-DCA", 125, file_name="results/shortline_p4_batch3.json", evidence_cutoff="2026-09-24")`（dict schema 唯一，禁手抄 prev）。
- 断点续跑：cells+nulls 逐行 checkpoint（`results/p4_batch3_cells.jsonl`，t22 截断尾容忍律）；finalize 只读 checkpoint 文件重建（T-33 律）；finalize 单发守卫（OUT_JSON 已存在拒绝复收，GRID-P1 同律）。

## §4 判据（跑前写死，禁看结果调线）

- **G1' v2 = `science_gates.g1_prime_v2(sharpe_full, returns, batch_cells=125, n_trades, n_entries)`**（共享库，数据驱动 skill_line_v2=ledger 头+共享 null 收集器，**零手抄常数**）；在册记录线 i 0.3521/vi 0.4004 仅作披露对照列（J19 记录常数纪律的信息面，不作本批门）。批报告逐列披露 skill_line/bootstrap_ci/trade_gate 全输入。
- **主判读面（本批第一判据，跑前冻结）**：staged vs single **同触发同退出**配对三列必报——①ΔSharpe（full）；②Δmax_drawdown；③**止损咬合率**（`reason=="stop_loss"` 平仓腿占全部平仓腿比例；配对双列+Δ；退出原因直方图逐格披露）。判读面**无过线判据**（机制级问题，诚实读数不设翻案门）；G1' v2 仍为注册资格唯一门。
- **G2 信息面（G1' 过线者才进，本批不注册）**：DSR=`science_gates.deflated_sharpe_ratio(原始日收益, n_trials=125)`（禁 dsr_from_stats 充数）≥0.95 ＋ 家族 PBO=`screening/pbo.py cscv_pbo(8 块)` ≤0.25（同族网格=**同触发 4 格** {single,staged}×{def,CE}，g25_retro 先例；家族=触发）。注册另开预注册（GRID-P1 先例不变）。
- 描述性条款（批级披露，不替代 v2 门）：年化>0、OOS 双正、回撤≥−35%、×2 成本面。
- 本批无数据腐坏/健康检测类分布界判线（硬界设计三件套 (a)/(b) 不适用）；极端日先验归 §5(c)。

## §5 跑前预测（写死于跑前，§8 对账）

1. **low252_prox 配对读数**：分批改善方向正确但难翻正——点估计 staged full Sharpe ∈ (−0.27, +0.15)（ΔSharpe 正但绝对水平大概率仍低于 skill line）；**止损咬合率 staged 显著高于 single**（下刀政体 −8% 随 VWAP 下移逐档咬合；spec §3-c 定义性代价的实证预测）。
2. **oversold_bounce 配对读数**：触发自带缩量企稳过滤 → 分批在反弹政体摊薄成本，ΔSharpe 预期小幅正（0 ~ +0.15）；止损咬合率与 single 接近或略高（−5%/−10% 加仓档在反弹起点政体少触发）。
3. **G1' v2 候选预期 0-1 格**（8 格中 staged×oversold×default 最有戏）；CE 增益预期小（批一机制读数#2：CE 传输通道=砍笔减成本，状态制 oversold 增益≈0）。
4. **极端日先验（硬界三件套 (c)）**：2016-01 熔断类与 2026-01-19 极端政体窗内，−8% 硬止损必然全批咬合；staged 的 −5%/−10% 档在单日 −7% 级跳空下会同日连续触发（收盘排队、次日 open 执行、跳空成交劣于触发价）→ staged 单笔最大亏损面**更深**（多档同日成交于同一跳空 open）。本批无 max 硬界判线（§4 已声明），如实披露不设豁免。
5. **注册面预测**：staged×oversold 与 PROS-OVB-CE-01（同触发 sleeve2 族）日收益 `max|corr|` 预期 **>0.70 → D6 拒收注册面**（spec §5 预披露；判读面不失效）。

## §6 产物

- `scripts/p4_batch3_dca.py`（runner+selftest）＋`results/shortline_p4_batch3.json`（顶层 cutoff_meta 必带）＋`research/shortline/p4_batch3_results.csv`＋本件 §7/§8 回填＋`results/gate_attrition.json` 追加一行＋append_ledger P4-B3-DCA 125。

## §7 跑后实证（跑前必须为空——占位纪律：写数字即造假）

（待跑后一次定稿回填：8 格全景表+配对三列表+null/被动/锚定读数）

## §8 批后复盘（待批后回填）

（待跑后回填：§5 预测逐条对账＋门禁链损耗账行＋skill_line_v2 当批判读＋zoo #14/§6 P-4 状态翻面）
