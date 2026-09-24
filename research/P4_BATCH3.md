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

**批身份**：finalize 2026-09-25 04:11（autofill C8 发射 04:10:01 pid 14208，88.1s 单进程）·void=false·硬门 3/3（patch/panel/锚定）·evidence_cutoff=2026-09-24·prereg 冻结 7a94dbfa 先于一切跑（audit 载明 prereg_frozen_before_run=true）。

### 7.1 八格全景（x1 面；×2 压测面括注）

| 格 | full Sharpe（×2） | OOS Sharpe | maxDD | 止损咬合率 | n_trades | G1'v2（line 1.1069） | CI95 下界 | D6 注册面 |
|---|---|---|---|---|---|---|---|---|
| ovb\|single\|default | 0.3316（0.1418） | 0.4738 | −0.0455 | 5.88% | 119 | FAIL | −0.4218 | 拒（corr 0.9998 vs PROS-OVB-CE-01） |
| ovb\|single\|ce | 0.3348（0.1512） | 0.4738 | −0.0455 | 4.35% | 115 | FAIL | −0.4249 | 拒（1.0000） |
| ovb\|staged\|default | 0.2682（0.0925） | 0.2882 | −0.0241 | 5.93% | 118 | FAIL | −0.5121 | 拒（0.9835） |
| ovb\|staged\|ce | 0.2742（0.1082） | 0.2882 | −0.0241 | 3.48% | 115 | FAIL | −0.4957 | 拒（0.9831） |
| low252\|single\|default | −0.2802（−0.4382） | −1.0887 | −0.3735 | 12.82% | 733 | FAIL | −1.1223 | 过（0.2738） |
| low252\|single\|ce | −0.0674（−0.2539） | −0.3941 | −0.3279 | 9.60% | 531 | FAIL | −0.8478 | 过（0.3038） |
| low252\|staged\|default | −0.2082（−0.5811） | −0.7050 | −0.1878 | 12.31% | 869 | FAIL | −1.0104 | 过（0.3133） |
| low252\|staged\|ce | −0.0761（−0.2943） | −0.4996 | −0.1998 | 8.92% | 572 | FAIL | −0.8720 | 过（0.3091） |

**G1' v2 过线 0/8**（skill_line_v2=1.1069·n_eff=60,784·μ_null −0.0332·σ_null 0.2429；trade_gate 全格 dual_ok——样本量不缺，判负是水平判负非功效判负）；G2 信息面=空集（无过线者，per §4 设计）。

### 7.2 配对三列（主判读面·同触发同退出）

| 配对 | ΔSharpe | ΔmaxDD | Δ止损咬合 |
|---|---|---|---|
| ovb@default | **−0.0634** | +0.0214 | +0.0005（5.88%→5.93%） |
| ovb@ce | **−0.0606** | +0.0214 | −0.0087（4.35%→3.48%） |
| low252@default | **+0.0720** | **+0.1857** | −0.0051（12.82%→12.31%） |
| low252@ce | **−0.0087** | +0.1281 | −0.0069（9.60%→8.92%） |

机制读数三事实：①**分批不翻转超跌族判负**——low252 staged 改善方向正确（+0.0720）但绝对水平仍深负（−0.2082/OOS −0.7050，CI 下界 −1.01），ovb staged 反而**负向**（两退出制均 −0.06 档）；②**ΔmaxDD 四配对全正**（+0.02~+0.19，low252@default 回撤近乎减半 −0.3735→−0.1878）=分批是稳健的回撤减震器；③**止损咬合率 staged 无一显著升高**（四配对两平两降）。共同根源=加仓档触发稀薄：adds_per_entry ovb 0.078-0.080（全批仅 9 档成交）/low252 0.104-0.216（77-96 档）——−5%/−10% 档在 20d 窗内极少点火，「止损线随 VWAP 下移」的定义性代价停留在理论面。

### 7.3 null/被动/锚定读数

- null（n=100，p∈{0.02,0.05}×25 seeds×2 退出制）：μ=0.0212·σ=0.2342；批内单发 p95 披露=default 0.3533 / ce 0.4644（披露面；skill line 走共享收集器非批内值）。
- 被动双口径（J8）：EW48 buyhold full 0.2825 / OOS 0.6417；月度再平衡 full 0.3606 / OOS 0.7296——八格 x1 全部跑输两被动基线。
- 锚定：NAMED_SIX 6/6 逐位复现 PASS（COMPOSITE-CE-01 0.8114 / CE-02 0.6099 / DROUGHT 0.7240 / ENGULF 0.5392 / NEEDLE 0.6624 / VOLATILITY 1.2578）＋PROS-OVB-CE-01 kin 参照载入成功（0.3350，D6 参照面无缺格）。
- audit：88.1s·workers=1·n_backtests=124（跑批器口径=cells+nulls+锚定复现+kin 腿；两被动基线为解析计算不入引擎计数）；账本口径 125 试验（§0）。

## §8 批后复盘（r141 一次定稿回填）

### 8.1 §5 预测逐条对账（3 中·2 诚实未中·1 未测）

| §5 预测 | 实况 | 判定 |
|---|---|---|
| 1a. low252 staged ∈ (−0.27,+0.15) 方向正难翻正 | −0.2082 带内，ΔSharpe +0.0720 正，仍深负未翻 | **中** |
| 1b. low252 止损咬合 staged 显著高 | 12.31% vs 12.82% = Δ−0.0051 反略低 | **未中①** |
| 2a. ovb ΔSharpe 0~+0.15 | −0.0634/−0.0606 反向 | **未中②** |
| 2b. ovb 咬合接近或略高 | def +0.0005 平 / ce −0.0087 略低 | **中** |
| 3. G1' 候选 0-1 格 | 0 格 | **中** |
| 4. 极端日 staged 单笔更深 | 批读出面未提取单笔 max loss 列 | **未测**（如实：先验无对账读数面；未来 DCA 类 spec 应把 per-trade max loss 列入配对列） |
| 5. D6 ovb staged corr>0.70 拒 | 4/4 格 0.983-1.000 拒收 | **中** |

**两未中共根因**：先验隐含「加仓档会被点着」假设，实测加仓档点火率稀薄（adds_per_entry 0.08-0.22）——摊薄机制在 20d 窗内基本没吃到 −5%/−10% 档，于是咬合不升（档位空置=定义性代价理论化）、ovb 的摊薄收益不存在只剩首档 40% 延迟建仓+摩擦（反弹起点政体首档即对、加仓档闲置）。教训：**DCA/网格类机制先验必须先算加仓档点火率分布再写方向预测**（未来 spec 检查项）。

### 8.2 门禁链损耗账（C4）

125 试验入账 → 账本 60,659→60,784（append_ledger 链头 shortline_p4_batch3.json 实读）；G1' v2 8 进 0 出（eliminated=8，gate_attrition P4-B3-DCA 行已落 2026-09-25 04:11:32）→ G2 空集 → 注册 0（本批设计即不注册，GRID-P1 先例）；D6 registered face ovb 4/4 拒收（机制新颖性条款命中）/low252 4/4 过但无幸存者可送；无同批 merge 事件。

### 8.3 skill_line_v2 当批判读

line=1.1069（ledger head grid_p1 60,659 + 本批 100 null 收集器）；μ_null −0.0332·σ_null 0.2429·n_eff 60,784。披露对照：八格 x1 最优 0.3348 连在册记录线 i 0.3521 都不及、离 vi 0.4004 更远——本批判负与 v2 门判读完全一致无张力。机制级批不设翻案门（§4 冻结），判读面答案定谳：**分批摊薄不足以翻转超跌族判负**。

### 8.4 zoo #14 / playbook §6 P-4 状态翻面

- zoo #14（ASTYLE_ZOO.md）：spec 已落 → **批测判负收线**（§4 机制问题答案=negative；唯一稳健副产出=staged 全配对压回撤不升咬合=回撤减震器，α 面零候选）。
- SHORTLINE_PLAYBOOK §6 P-4 三批：①done（批一）②done（批二 M0923）③**done（本批判负收线）**——P-4 风格动物园分批实现全弧闭环。
