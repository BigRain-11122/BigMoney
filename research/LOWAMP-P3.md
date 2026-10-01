# LOWAMP-P3 预注册 · 低振幅横截面日再平衡族·出场轴 ExitPatch 通道修正面（T-2026-10-01-140 剩余面冻结件）

> 裁决血统：O-20261001-2355 §一（T-142 GM P1 裁决·CEO 直令「排好单子！开工！」随令裁决）**(e) 族供给重开通道=LOWAMP-P3**——「ExitPatch 通道写 loss_time_days/global_hard_limit 两键·live.paper 契约·同冻结族/面板/cutoff 2026-09-22·E1 四腿+烧后出场普查双门」（LOWAMP-P2 §9 全文为准）。前批血统：LOWAMP-P1 verdict VOID（O-20261001-1108 §三）＋ LOWAMP-P2 verdict VOID（O-20261001-2355 §一）——两批均=出场中和死信杂交面（params 通道 6-kwarg 桥外死信），**本批=r522 根因的正面修复面**。
> 出场轴显式门：firm/TRIAL_LABOR_LAW.md §4（O-20261001-1108 立法）——本件 §0.6 为强制节；**本批同时首载律 A 烧后件**（LOWAMP-P2 §9：「烧后退出原因普查 >20% 引擎缺省退出占比=自动封锁消费」）。
> 模板=research/PREREG_TEMPLATE.md；跑前 commit 冻结；跑后只回填 §7/§8，禁改判据禁重跑；LOWAMP-P1/P2 冻结批本身禁重跑不变（本批=新批非重跑·T-136 "Either way" 线·冻结批零重跑铁律）。
> 部门=dept:策略（族规格）+研究（judgment 面）；lane=Money02 deep 面板在位的任何机队机（P1/P2 同门）。

## §0 批件身份【必填·跑前】

- 批名/批号：**LOWAMP-P3**。**N_eff=2,008**＝judged cells 4 × 判面 2（base+x2）+ same-mask null draws 2,000（P1/P2 同式）；sensitivity Sobol 腿=描述面**不计 N_eff**（§3）。扩容即买单。
- 账本面：finalize 步 `science_gates.append_ledger(batch_name="LOWAMP-P3", batch_trials=2008, file_name="results/lowamp_p3/lowamp_p3_results.json", evidence_cutoff="2026-09-22")`（dict schema 唯一禁手抄 prev；LOWAMP-P1 −2,008＋LOWAMP-P2 −2,008 两笔补偿分录已在链=ledger_head void 面自动净额·本批 prev 从净额 head 起）。
- 算力预算：**长活入池**（>5min 一律 runnable_pool·O-20260924-2100 s2）——分片=4 cells × 2 axes × 2 faces=16 cell-shards + nulls 片 + sensitivity 片；workers_plan={"workers": 12, "priority": "BelowNormal"}（O-2130 s1.1·CEO 10% 余量令）；checkpoint+逐片日志；**跑批宿主门=Money02 deep 面板在位**（dir_nonempty=Money02/data/cache/t18_deep_panel/ohlcv·48 文件）；批报告必带 audit 段。

## §0.5 禁开方向硬闸【必填·跑前】

- 跑前过闸：`python Tools/banned_direction_gate.py --prereg research/LOWAMP-P3.md` → 退出 0=放行（fail-closed）。
- 人工预读结论：**零命中**——本批机制与 LOWAMP-P1/P2 冻结面逐字同族（横截面**风险度量（振幅升序）**选低＋**常开**零前置＋core48 ETF 宇宙＋日频再平衡），两批裁决 VOID 后机制面零新增方向；与注册表 v1.0 九类已证伪机制面逐一对照零重叠；禁向词面不在本件复述（机器闸为准·防否证模式词面自撞·r483 清洗律）。

## §0.6 出场轴显式声明【O-20261001-1108 立法·TRIAL_LABOR_LAW §4·本批强制节】

- **出场轴=②持有到底（ALWAYS-ON hold-through）**：族定义=常开持有——成员**只因横截面选择轮换离场**（当日跌出 Top-N 最低振幅入选集=entry≤0 信号出场·t22 `_run_cell` exit_sig=entry<=0 惯例逐字），**无价格类出场**（无止盈/无止损/无衰减踢出/无亏损时限/无持有上限）。
- **引擎缺省出场栈显式禁用【双通道逐键申报·r522 根因修正面】**：引擎 ExitConfig 桥（engine/backtester.py）**只读 6 个 params kwargs**（take_profit_levels/trailing_stop_activate/trailing_lock/initial_stop/time_decay_period/time_decay_threshold）——**loss_time_days 与 global_hard_limit 两键为桥外字段，params 通道=死信（r522 E1 实证·P2 VOID 根因）**。本批逐键申报：
  - **params 通道（桥内 4 键）**：`take_profit_levels=()`（空梯·P3 永不触发）·`trailing_stop_activate=1e12`（trailing 永不激活）·`initial_stop=-1.0`（止损价=0·正价格永不触发）·`time_decay_period=10**9`（P4 永不）；
  - **ExitPatch 通道（桥外 2 键·live/paper.py `ExitPatch` ExitConfig 工厂补丁·live.paper 契约）**：`loss_time_days=10**9`（P5 永不）·`global_hard_limit=10**9`（P6 永不）——与 T-136 fixture Leg B、r522 E1 corrected-face 腿（+15.88%/夏普 +1.158·仅 7 笔信号出场）同一通道；
  - 两通道键集**互斥断言**入 runner selftest（F11 死信回归守卫）；`exit_signal` 注入=entry≤0 全矩阵（P1 signal_reversal 通道=族自有选择出场·保留）；**engine/exit_rules.py 与 engine/backtester.py 零触碰**（ExitPatch=引擎自有运行时接口·live.paper 生产通道同款）；T+1 执行与成本模型=引擎正典不变。
- 判读律：出场轴声明三选一——本批=①+②合体（选择轮换=族自有机制·②持有到底=价格类出场零）；缺本节=门拒。

## §1 α 机制段【必填·D6】

- 机制勾选：**行为偏差**（主：彩票偏好/注意力稀缺——市场对手盘系统性超配高振幅「彩票型」资产〔MAX 效应族〕，低振幅资产长期低配=低波动异象；代价支付者=追高波动的行为对手盘）＋**结构性**（辅：机构委托条款/跟踪误差约束令其无法超配低振幅成员——「基准即枷锁」）。
- **散户凭什么赢【§1.2】**：**制度/容量**——低振幅倾斜散户规模容量无限、零杠杆需求；RETAIL_QUANT_TRACK §三引用台账：不重跑任何机构结论（低波动异象=公开文献常识面引用）；例外三问=本账户独有约束（场内 ETF 零杠杆直接持有·真实成本·本市场 2020-2026 窗）成立。
- **同族相关性准入检查【必填·D6】**：入批前 probe 步计算 headline（LA-REP·hold-through 面）日收益序列 vs **在册六员全部成员**日收益序列逐对 max|corr|（日收益口径·sleeve-tag 先例）；**max|corr| ≥ 0.7 → 拒收 fail-closed 禁烧**（数值与逐对清单 probe 件落盘 results/lowamp_p3/probe.json 后方可点火）；P1 先证=0.1688·P2 先证=0.1738（本批 ExitPatch 修正面以本批 fresh probe 实测为准）。
- M1 t 面【必填申报】：`science_gates.t_from_sharpe(sharpe_full, n_periods)` 派生面（headline cell）；判据=`science_gates.m1_t_value_gate`（H/L/Z 门槛 **t≥3.0**）；缺面=missing_input 拒收。
- M3 闭合族对号：family_key=**lowamp_daily_xs**——CLOSED_FAMILIES 六在册键无一命中=open 照跑；**P1/P2 判负已 VOID 不闭合本族**（O-20261001-1108 §三/O-20261001-2355 §一裁决指针）；族间对号同 P1/P2（GRID-SLEEVE 带状执行族无关·CN-DIV-LOWVOL-ROT=monthly-rotation 族·本族=日频横截面振幅排序族）。

## §2 数据与面板【必填·跑前探针事实，非结果】

- 宇宙/池：**core48**（legacy 轴·48 员）＋ **T-18 增长成员面板**（deep 轴·manifest PASS·48 员·panel_start=2013-06-17）。
- **价格面=core48 adjusted face（P1/P2 §2 逐字继承）**：两轴均以 T-19 复权视图为 19 受影响员价格源（振幅信号必须吃复权面）；raw 面权威性不动（D2 锁盒零改写）；t19 gates 既有 PASS 件只读引用。
- **数据锚面定义四元组【G-ANCHOR-FACE】**：legacy 轴=`data/daily/sh<code>.csv`＋`live.paper.load_core`＋起算 2020-01-02＋预热 252td（19 员 adjusted_view parquet 逐员替换）；deep 轴=`Money02/data/cache/t18_deep_panel/ohlcv/<code>.parquet`＋`pd.read_parquet`＋起算 2013-06-17＋预热 252td（GF 硬门 19/19；amount=volume×close disclosed proxy）；政体标签=`t22_virtual_timepoints.regime_proxy(close['510300'])`＋预热 200td。
- **探针-锚同面断言**：runner probe 实载路径与四元组逐位比对 fail-closed；一面不符=**面错配 VOID**。
- 窗口与 **evidence_cutoff=2026-09-22**（前向锁盒 D2·两轴一律截 ≤cutoff 再联合；cutoff 后新 bar 锁定不得回流）；结果 JSON 顶层 `evidence_cutoff` + `science_gates.cutoff_meta("2026-09-22")`（缺字段=C2 VIOLATION）。
- 起点集：**T-22 冻结枚举律逐字**——`enumerate_starts`（pos≥252td ∧ ≥126td 前瞻 ∧ 当日上市成员数≥24）确定性全枚举；**G-CENSUS 门：起点数逐位=={legacy: 1,254, deep: 1,506}**（P2 零跑修正案锚读数继承·同 cutoff 截断同枚举·raw/adj 双面同读）。
- 数据完备门（不过门禁跑）：①legacy 48 员/adj 19/19；②deep manifest PASS ∧ 48 员 ∧ ohlcv 48 文件；③cutoff 截断后两轴末行==2026-09-22；④零重复日期+单调；⑤G-CENSUS。
- **流动性/可交易闸（票面 mandatory 继承）**：选择资格=有效 amp（满 W 窗史）∧ 当日 close notna ∧ volume>0 ∧ amount>0 ∧ **amt20_median ≥ ¥50,000,000**（deep 轴 amount=proxy 面如实披露）。
- DATA_GAP 对号：同 P1/P2（缺项 5→legacy 2020 起为正典设计面、deep 2013 起在仓覆盖）。

## §3 方法学【必填·冻结】

- **信号定义（冻结·炉子血统参数带逐字·P1/P2 同族）**：amp(t)＝近 W 交易日收盘-收盘日收益滚动标准差（`min_periods=W`·严格因果）；横截面升序排名取 **Top-N 最低振幅**；权重 **invvol**（w_i∝1/amp_i·归一）或 **eq**（1/N）；**常开**（零前置条件）；**日频再平衡**（信号日 T 收盘算、引擎正典 T+1 执行）。
- **judged cells 4（跑前写死·P1/P2 同格·非结果驱动）**：①**LA-REP**：W=89·N=2·invvol（炉子代表格 C0096 逐字）；②**LA-EQ**：W=89·N=2·eq；③**LA-T3**：W=89·N=3·invvol；④**LA-EDGE**：W=104·N=2·invvol（带上缘）。
- **执行语义【§0.6 出场轴=本批唯一变更面（P2 的 ExitPatch 修正）】**：entry_signal=当日入选 ∧ exit_signal=entry≤0（选择轮换出场·全矩阵注入）→ `engine.run_backtest`（T+1·成本模型·§0.6 双通道缺省栈显式禁用：params 桥内 4 键+ExitPatch 桥外 2 键）→ **持有到底**（价格类出场零触发·成员仅因跌出 Top-N 离场）；x2 面=`CostPatch(2.0)` 乘数（r82 修正面）；每起点 fresh-entry 洁净切片（入场即目标权·孪生 naive 先例）。
- **窗族 {6m=126·12m=252·24m=504}**：最长窗一次跑+同曲线切片（P-5 律）；**主判窗=12m 完整窗**·partial 窗如实标记；被动基线=起点日已上市成员等权 B&H 同窗（t22 逐字）；beat_k=ret_k>p_ret_k。
- **null 对照（≥2,000 三族全律·P1/P2 同式·P3 新种子带）**：①**null_pool（G1' skill line 源）**：K=2,000 **same-mask 随机选择 null**——每日同一资格掩码宇宙内均匀随机选 N 员（同 N·同窗·同执行·eq 权·**`rng([20336500, k])` 子流律·本批新种子带**），全面板模拟取 Sharpe 分布（μ_null/σ_null 入 skill_line_v2）；掩码恒等断言（G-MASK：null 日宇宙==真实 cell 日宇宙逐位）。②**block bootstrap B=2,000**（headline 日收益·块长 21td）＋③**sign-flip permutation P=2,000**（双法并列=RANDOM_LARGE_SAMPLE_LAW §3 逐字）。
- **sensitivity 腿（§2.2 履约·描述面零判定宣称）**：N=500 空间填充均匀抽取 over（W∈[77,104] 整数·N∈{2,3}·sizing∈{invvol,eq}·gate=常开固定·**出场轴=§0.6 hold-through 同面（双通道）**），legacy 轴全面板单跑，产物=Sharpe/均值/maxDD 分布描述列，**不计 N_eff、不设门、禁幸存者宣称**；`rng([20335500, k])`；registry 行 `lowamp_p3_starts=20336000` **不消费**（judged 起点=T-22 确定性全枚举·sensitivity=全面板连续跑）——如实披露。
- **政体分段**：每起点 regime 标签（t22 3-way proxy）→ 分段统计；**G-SEG 覆盖门：每轴 bear/bull/chop 各 ≥50 起点**——不过=verdict=**insufficient-sample**。
- **律 A 烧后退出原因普查【本批首载·LOWAMP-P2 §9/O-20261001-2355 §一立法】**：finalize 步对 headline（LA-REP·legacy·base）以同一冻结机件重跑逐符号捕获每笔出场 reason——hold-through 面上**唯一合法 reason=signal_reversal**（选择轮换）；一切非 signal_reversal reason=引擎缺省栈出场；**缺省栈出场占比 >20%（CENSUS_BLOCK_SHARE=0.20·跑前写死）→ verdict=consumption-blocked（判决消费自动封锁·四态如实·禁下游消费）**。普查块（total_exits/per_reason/default_share/pass）入结果 JSON gates.exit_census。
- 成本口径声明【CN-C7】：**ETF=26.082bp/往返**（`knowledge/cost_spec.py X1_RATE=0.0013041` 单边 **import 派生禁手抄**·runner 断言恒等）；股票面 N/A（零个股）；¥1,000,000 账户口径申报；V2 ADV 滑点面对 ETF 日频零售量级=不适用如实注记。
- **闭合族对号声明【M3】**：open，无「新证据增量」义务。
- **反重复披露（票面 anti-dup）**：LOWAMP-P1/P2 已烧批禁重跑（两批 VOID 裁决不改变冻结批零重跑铁律）；本批=W∈[77,104] 带**唯一合法在烧面**（P2 判负 VOID→P3 重开·O-20261001-2355 §一(e) 裁决通道·LOWAMP-P2 §9 在案）；炉子 1060 格勘探面零重烧（证据件在册引用）。

## §4 判据【必填·跑前写死，禁看结果调线】

- **G1' v2 = `science_gates.g1_prime_v2(sharpe_full, returns, batch_cells=2008, pool='core48', n_trades, n_entries, null_pool=<本批 2,000 same-mask own 池>)`**（headline=LA-REP·**legacy 轴全面板** 2020-01-02→2026-09-22 连续单跑·hold-through 面）：全期 Sharpe > skill_line_v2（数据驱动=max(被动+0.10, μ_null+σ_null·√(2·ln N_eff))·**N_eff=净额账本 head+2,008**〔LOWAMP-P1/P2 两笔 −2,008 void 已净〕）∧ 平稳 bootstrap CI 下界>0 ∧ entries≥30（F6 双口径）；逐列披露 skill_line/bootstrap_ci/trade_gate 全输入。
- **G2 = `science_gates.g2_registration_v2(g1_pass, dsr, pbo)`**：DSR≥0.95（`deflated_sharpe_ratio` 跑 LA-REP legacy 全面板原始日序列·禁 dsr_from_stats 充数）∧ **家族 PBO≤0.25**（judged 4 cells 带内格）——P1/P2 同门逐字。
- **双轴确认**：deep 轴 LA-REP 同门重跑（CI 下界>0·方向一致）。
- **x2 成本压测存活**：LA-REP x2 面 Sharpe ≥ 0（成本翻倍不死）。
- **M1 t 值门**：`m1_t_value_gate`（t≥3.0·headline）。
- **G-SEG 覆盖门**：§3 政体分段门（不过=insufficient-sample 如实）。
- **律 A 普查门（本批强制·§3）**：出场原因普查缺省栈占比 >20% → **verdict=consumption-blocked（先于 PASS/judged-negative 定谳·自动封锁下游消费）**。
- **E1 四腿强制门【消费前置·LOWAMP-P2 §9/O-20261001-2355 §一】**：本批任何 verdict 数字被下游消费（watchlist 翻面/STRATEGY_LIBRARY 注册/族间 meta 结论）前必过 E1 四腿对账（r492/r301/r522 律）：**Leg A** as-burned 引擎重放对 artifact 逐 bp＋**Leg A2** 出场原因普查（=§3 律 A 腿）＋**Leg C** 无引擎独立算术腿交叉验证（B/C 腿差 ≤5bp/日）——证据件=results/lowamp_p3/e1_three_leg.json（跑后产出）；缺 E1 件或 FAIL=禁消费。
- **族级 PASS（全合取）**：G1' ∧ G2 ∧ 双轴确认 ∧ x2 存活 ∧ M1 ∧ G-SEG 覆盖 ∧ 律 A 普查门 ≤20%；任一不合=**judged-negative**（诚实出 POTENTIAL_WATCHLIST 名单·O-2230 fast-track law 逐字）；hold-through+ExitPatch 修正面判负=族设计面真判负（出场轴已显式+双通道已修正·无 prereg 自相矛盾面可归咎·第三次同族缺陷已由律 A 双门封死）。
- 下游：PASS → E1 四腿门 → s4 intake（LOWAMP-* 纸盘提案 fast-track + STRATEGY_LIBRARY 注册 + POTENTIAL_WATCHLIST 状态翻面）；judged-negative → E1 四腿门 → 如实出名单。

## §5-§8 预留

- §5 资源申报/§6 里程碑/§7 回填（全起点分布+预测对账+损耗账）/§8 结论：跑后回填，跑前留空。
- **跑前冻结=本件 commit**（freeze hash 入轮报告与 pool 票）；冻结后禁改判据（回填限 §7/§8）。
