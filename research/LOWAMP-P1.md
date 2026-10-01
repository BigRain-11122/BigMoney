# LOWAMP-P1 预注册 · 低振幅横截面日再平衡族专用判决批（T-2026-09-30-132-P1 s1 冻结件）

> 令源：CEO 直令 O-2026-09-30-2230「很好，务必关注有潜力的」→ POTENTIAL_WATCHLIST #1 快速通道（专用族 prereg 优先开烧·不排大波队）；票=T-2026-09-30-132-P1（P1·immediate·bm-b 认领 2026-09-30 23:26 commit a78b69bc5·CEO 即时律认领即开动）。
> 证据基础：research/LOWAMP-FURNACE-20260930-P1.md（GM 淬炼勘探面·1060 格·top20 全 robust·验证窗 2020-2025 +176% vs EW +59%·置换 p=0.0018）——**勘探面零判决宣称**；本批=真出样判决面。
> 模板=research/PREREG_TEMPLATE.md（§0-§8 全节含 §0.5/§1.2/M1/M3/CN-C7/G-ANCHOR-FACE）；跑前 commit 冻结；跑后只回填 §7/§8，禁改判据禁重跑。
> 认领：F-04 已先行=fleet/inbox/MSG-20260930-2325-bmb-ALL-lowamp-p1-claim.md；部门=dept:策略（族规格）+研究（judgment 面）；执行=bm-b（lane: any fleet machine 合法·O-2320 夜间合法）。

## §0 批件身份【必填·跑前】

- 批名/批号：**LOWAMP-P1**。**N_eff=2,008**＝judged cells 4 × 判面 2（base+x2）+ same-mask null draws 2,000（CN 家族先例：null draws 计入 N_eff·CN_SECTOR_LEADER N_eff=2004 同式）；sensitivity Sobol 腿=描述面**不计 N_eff**（§3）。扩容即买单。
- 认领：T-2026-09-30-132-P1（本件头注）＋MSG-20260930-2325（F-04）；同窗作废让号残留同文票 T-2026-09-30-131-P1（superseded_by 指针·防双认领）。
- 部门归属：dept:策略/研究（双署·票面 Owner dept 逐字）。
- 算力预算：**长活入池**（>5min 批一律 runnable_pool 提交·O-20260924-2100 s2·禁轮内内联代跑）——分片=4 cells × 2 axes × 2 faces=16 cell-shards（每片=单 cell 单轴单面全起点枚举）+ nulls 片（2,000 全面板随机组合 null·双轴）+ sensitivity 片（500 draws legacy 全面板）+ finalize 片；workers_plan={"workers": 12, "priority": "BelowNormal"}（O-2130 s1.1）；checkpoint 断点续跑+逐片日志；**跑批宿主门=Money02 deep 面板在位**（dir_nonempty=Money02/data/cache/t18_deep_panel/ohlcv·48 文件·bm-b 实证在位）；批报告必带 audit 段（COMPUTE_AUDIT v2 §七）。

## §0.5 禁开方向硬闸【必填·跑前】

- 跑前过闸：`python Tools/banned_direction_gate.py --prereg research/LOWAMP-P1.md` → 退出 0=放行（回执入轮报告；fail-closed）。
- 人工预读结论：**零命中**——本批机制=横截面**风险度量（振幅升序）**选低＋**常开**（零前置条件：无政体闸、无市场状态类前置、无个股面确认条件）＋core48 ETF 宇宙（零个股面）＋无换手压缩类机制＋非跨期风格下注；与注册表 v1.0 全部九类已证伪机制面逐一对照零重叠；禁向词面不在本件复述（机器闸为准·防否证模式词面自撞）。

## §1 α 机制段【必填·D6】

- 机制勾选：**行为偏差**（主：彩票偏好/注意力稀缺——市场对手盘系统性超配高振幅「彩票型」资产（MAX 效应族），低振幅资产被长期低配，其后续风险调整收益系统性不劣于高振幅者=低波动异象；代价支付者=追高波动的行为对手盘）＋**结构性**（辅：机构委托条款/跟踪误差约束使其无法超配低振幅成员——「基准即枷锁」，散户无此约束）。
- **散户凭什么赢【§1.2·必填】**：**制度/容量**——低振幅倾斜在散户资金规模下容量无限、零杠杆需求（低波动异象的机构套利通道=加杠杆持有低波资产，散户直接持有即得，机构因 mandate/跟踪误差做不到）；RETAIL_QUANT_TRACK §三引用台账：本批不重跑任何机构结论（低波动异象=公开文献常识面引用非本仓实测复跑）；例外三问=本账户独有约束（场内 ETF 零杠杆直接持有·真实成本·本市场 2020-2026 窗）成立。
- **同族相关性准入检查【必填·D6】**：入批前 probe 步计算 headline（LA-REP）日收益序列 vs **在册六员全部成员**日收益序列逐对 max|corr|（日收益口径·sleeve-tag 先例）；**max|corr| ≥ 0.7 → 拒收 fail-closed 禁烧**（数值与逐对清单 probe 件落盘 results/lowamp_p1/probe.json 后方可点火）；确有新机制主张须另开预注册论证相关性来源。预期：低振幅选择偏防御类成员、与股票进攻型在册员 corr 低——以实测为准。
- M1 t 面【必填申报】：策略面无直接因子 IC t → 允许 `science_gates.t_from_sharpe(sharpe_full, n_periods)` 派生面（headline cell）；判据=`science_gates.m1_t_value_gate`（H/L/Z 门槛 **t≥3.0**·新策略主张面）；**缺面=missing_input 拒收**。
- M3 闭合族对号：family_key=**lowamp_daily_xs**——`science_gates.CLOSED_FAMILIES` 六在册键（cta_futures_p1/cn_combo_five_family/wild_route_s1/factor_blend/t28_spm_first/microcap_2024_crash）**无一命中=open 照跑**，无「新证据增量」义务；`closed_family_check` 冻结窗实跑回执入轮报告。**族间对号（票面 anti-dup 逐字）**：GRID-SLEEVE（grid-sleeve 英文键·带状执行族·机制面与本族无关）、CN-DIV-LOWVOL-ROT=monthly-rotation 族、本族=**日频横截面振幅排序族**=new-family（与已判负族零重叠·furnace 诚实注记同读）。

## §2 数据与面板【必填·跑前探针事实，非结果】

- 宇宙/池：**core48**（legacy 轴·48 员·2026-09-30 探针实测 48/48）+ **T-18 增长成员面板**（deep 轴·manifest verdict=PASS·48 员·panel_start=2013-06-17）。
- **价格面=core48 adjusted face（票面逐字）**：两轴均以 T-19 复权视图为 19 受影响员价格源（**振幅信号必须吃复权面**——合并除权日在 raw 面制造人工巨幅 return 会污染 amp 排序，此即 T-19 消费律「adjusted view serves the clean re-run (O-1612 item1)」的判决面适用）；raw 面其余权威性不动（D2 锁盒零改写）；t19 gates（GA-GF）既有 PASS 件 results/t19_adjust_view_gates.json 只读引用。
- **数据锚面定义四元组【G-ANCHOR-FACE·每锚必填】**：
  1. legacy 轴：`data/daily/sh<code>.csv` ＋ `live.paper.load_core`（引擎正典 loader·禁旁路）＋ 起算=load_core 正典面 2020-01-02（510300 锚 1,636 行·末行截 cutoff）＋ 预热=252td（T-22 WARMUP_TD）；19 受影响员以 `data/consolidation/adjusted_view/<code>.parquet`（`pd.read_parquet`·事件窗 ≥2021-04-12 全 21 事件）逐员替换。
  2. deep 轴：`Money02/data/cache/t18_deep_panel/ohlcv/<code>.parquet` ＋ `pd.read_parquet`（t22 `_load_axis_prices` 装载式逐字复用）＋ 起算=manifest panel_start 2013-06-17 ＋ 预热=252td；19 受影响员同上 adjusted_view 替换（**GF 硬门 19/19**）；amount=t18 缓存无额列→`volume×close` disclosed proxy（t22 先例逐字）。
  3. 政体标签：`scripts/t22_virtual_timepoints.regime_proxy(close['510300'])`（冻结 3-way：510300 vs MA200）＋ 起算=各轴面板首 ＋ 预热=200td（MA200）。
- **探针-锚同面断言**：runner probe 实载路径与上述四元组逐位比对（load_core 面板首行/行数/成员数/adj 19/19/manifest PASS/cutoff 截断六断言 fail-closed）；一面不符=**面错配 VOID**（报「面错配」非「数据腐坏」·INCIDENT-20260928 立法）。
- 窗口与 **evidence_cutoff=2026-09-22**（前向锁盒 D2·T-22 BATCH_CUTOFF 绑定=deep manifest min of axes·两轴一律截 ≤cutoff 再联合；cutoff 后新 bar 锁定不得回流）；结果 JSON 顶层 `evidence_cutoff` + `science_gates.cutoff_meta("2026-09-22")`（缺字段=science_audit C2 VIOLATION）。
- 起点集：**T-22 冻结枚举律逐字**——`enumerate_starts`（pos≥252td 预热 ∧ ≥126td 前瞻 ∧ 当日上市成员数≥24）确定性全枚举；**G-CENSUS 门：起点数逐位=={legacy: 1,255, deep: 1,506}**（T-22 finalize 冻结读数·V2 先例同门）；双轴各 ≥1,000 → RANDOM_LARGE_SAMPLE_LAW §2.1 K≥1000 ✓。
  - **〔零跑修正案·AMENDMENT 2026-10-01·r251/r280 先例·零格已烧·结果盲〕**：上行的 legacy 1,255 为 t22 的 **2026-09-23 末场面**读数（其 LEGACY_CUTOFF）；本批 §2 绑定 evidence_cutoff=2026-09-22 截断纪律下确定性枚举实测 **legacy=1,254**（锚行 1,631；1,631−252−126+1；raw 面与 adj 替换面双面同读·probe 实测 2026-10-01 pre-burn），deep=1,506 与冻结读数逐位一致。D2 截断纪律优先，G-CENSUS 门锚定实测值 **{legacy: 1,254, deep: 1,506}**——runner=scripts/lowamp_p1.py（G_CENSUS 常量+probe 双轴断言）执行；本注记为唯一修正面，判据其余零改。
- 数据完备门（不过门禁跑）：①legacy 48 员/adj 19/19 子集；②deep manifest PASS ∧ 48 员 ∧ ohlcv 48 文件；③cutoff 截断后两轴末行==2026-09-22；④零重复日期+单调；⑤G-CENSUS。
- **流动性/可交易闸（Top-N 集中风险面·票面 mandatory）**：选择资格=有效 amp（满 W 窗史）∧ 当日 close notna ∧ 当日 volume>0 ∧ amount>0 ∧ **amt20_median ≥ ¥50,000,000**（20 日滚动成交额中位·deep 轴 amount=proxy 面如实披露）；冻结理由=Top-2 集中度的执行保护（探针实测 legacy 末日 amt20 最小员=¥20.9M·p10=¥126.8M——¥50M 线排除尾部流动性行而不空转）。
- DATA_GAP 对号：不涉缺项 1-4/6；缺项 5（2016 前 ETF 日线）→ legacy 轴 2020 起为正典设计面（P-5 caliber 非缺口）、deep 轴 2013 起在仓覆盖。

## §3 方法学【必填·冻结】

- **信号定义（冻结·炉子血统参数带逐字）**：amp(t)＝近 W 交易日收盘-收盘日收益的滚动标准差（`min_periods=W`·严格因果·无未来数据）；横截面升序排名取 **Top-N 最低振幅**；权重 **invvol**（w_i ∝ 1/amp_i·归一）或 **eq**（1/N）；**常开**（零前置条件——无政体闸、无确认条件、无市场状态过滤）；**日频再平衡**（信号日 T 收盘算、引擎正典 T+1 执行）。
- **judged cells 4（跑前写死·炉子冻结带内取格·非结果驱动）**：①**LA-REP**：W=89·N=2·invvol（炉子代表格 C0096 逐字）；②**LA-EQ**：W=89·N=2·eq（sizing 孪生）；③**LA-T3**：W=89·N=3·invvol（集中度孪生）；④**LA-EDGE**：W=104·N=2·invvol（带上缘·最长振幅窗）。
- **执行语义（引擎正典·禁触碰）**：entry_signal=当日入选 ∧ exit_signal=entry≤0（**t22 `_run_cell` exit_sig=entry<=0 惯例逐字**）→ `engine.run_backtest`（T+1·成本模型·退出优先级全引擎冻结律·engine/exit_rules.py 零改）；x2 面=`CostPatch(2.0)` 乘数（r82 修正面·V2 先例）；每起点 fresh-entry 洁净切片（入场即目标权·孪生 naive 先例）。
- **窗族 {6m=126·12m=252·24m=504}**：最长窗一次跑+同曲线切片（P-5 律）；**主判窗=12m 完整窗**·partial 窗如实标记；被动基线=起点日已上市成员等权 B&H 同窗（t22 逐字）；beat_k=ret_k>p_ret_k。
- **null 对照（≥2,000 三族全律）**：
  1. **null_pool（G1' skill line 源）**：K=2,000 **same-mask 随机选择 null**——每日在**同一资格掩码宇宙**内均匀随机选 N 员（同 N·同窗·同执行·eq 权·`rng([20330500, k])` 子流律），全面板模拟取 Sharpe 分布（μ_null/σ_null 入 skill_line_v2）；掩码恒等断言（G-MASK：null 日宇宙==真实 cell 日宇宙逐位）。
  2. **block bootstrap B=2,000**（headline 日收益·块长 21td）＋ **3. sign-flip permutation P=2,000**（headline 日收益·双法并列= RANDOM_LARGE_SAMPLE_LAW §3 逐字）。
- **sensitivity 腿（§2.2 履约·描述面零判定宣称）**：N=500 空间填充均匀抽取 over（W∈[77,104] 整数·N∈{2,3}·sizing∈{invvol,eq}·gate=常开固定），legacy 轴全面板单跑，产物=Sharpe/均值/maxDD 分布描述列，**不计 N_eff、不设门、禁幸存者宣称**（CN_SECTOR_LEADER §2.2 同式判读先例）；`rng([20330000, k])`。
- **政体分段**：每起点 regime 标签（t22 3-way proxy）→ 分段统计（bear/bull/chop 逐段 beat 率/收益）；**G-SEG 覆盖门：每轴 bear/bull/chop 各 ≥50 起点 ∧ ≥4 个历法分段披露**——不过=verdict=**insufficient-sample**（禁算 pass·law §3 逐字）。
- 成本口径声明【CN-C7·必填】：**ETF=26.082bp/往返**（面 A=`knowledge/cost_spec.py X1_RATE=0.0013041` 单边 **import 派生禁手抄**·runner 断言恒等）；股票面 N/A（本批零个股）；名义档位：¥1,000,000 账户口径申报（¥20,000 底佣临界 50 倍·小额档费率放大面不适用）；V2 ADV 滑点面对 ETF 日频零售量级=不适用如实注记。
- 账本：finalize 步 `science_gates.append_ledger(batch_name="LOWAMP-P1", batch_trials=2008, file_name="results/lowamp_p1/lowamp_p1_results.json", evidence_cutoff="2026-09-22")`（dict schema 唯一禁手抄 prev）。
- **闭合族对号声明【M3】**：§1——open，无「新证据增量」义务。
- **反重复披露（票面 anti-dup 逐字）**：T-86 普查 lowamp 列**verbatim 消费本批 judged faces 禁重跑**；千人试用期语法 amp77-104 带已被本批消费=后续 trial-wave 生成语法**排除该带**（W14 起生效）；炉子 1060 格勘探面零重烧（证据件在册引用）。

## §4 判据【必填·跑前写死，禁看结果调线】

- **G1' v2 = `science_gates.g1_prime_v2(sharpe_full, returns, batch_cells=2008, pool='core48', n_trades, n_entries, null_pool=<本批 2,000 same-mask own 池>)`**（headline=LA-REP·**legacy 轴全面板** 2020-01-02→2026-09-22 连续单跑）：全期 Sharpe > skill_line_v2（数据驱动=max(被动+0.10, μ_null+σ_null·√(2·ln 2008))）∧ 平稳 bootstrap CI 下界>0 ∧ entries≥30（F6 双口径）；逐列披露 skill_line/bootstrap_ci/trade_gate 全输入。
- **G2 = `science_gates.g2_registration_v2(g1_pass, dsr, pbo)`**：DSR≥0.95（`deflated_sharpe_ratio` 跑 LA-REP legacy 全面板原始日序列·禁 dsr_from_stats 充数）∧ **家族 PBO≤0.25**（`screening/pbo.py` CSCV 8 块·家族矩阵=4 judged cells base 面日收益列·g25_retro 同族小矩阵先例）。
- **双轴确认（RANDOM_LARGE_SAMPLE_LAW 双轴逐字）**：**deep 轴 LA-REP 12m 完整窗 beat 率 95% bootstrap CI 下界 > 0.50**（B=2000 二项·CI=comprehensive 分位）——legacy 过而 deep 不过=单轴存活如实披露、家族判**负。
- **x2 成本存活线**：LA-REP x2 面 legacy 全面板 Sharpe_full **> 0**（成本加倍后仍为正=存活·描述条款升级为冻结线·票面 x2 逐字）；x2 全列披露。
- **M1 门**：`m1_t_value_gate(t_from_sharpe(sharpe_full_LA-REP_legacy, n_periods))` t≥3.0。
- **族级 PASS（全合取）**：G1' ∧ G2 ∧ 双轴确认 ∧ x2 存活 ∧ M1 ∧ G-SEG 覆盖（不过=insufficient-sample 三态如实）；任一不合=**judged-negative**（诚实出 POTENTIAL_WATCHLIST 名单·O-2230 fast-track law 逐字「判负如实出名单」）。三态=PASS/judged-negative/insufficient-sample 禁混报。
- readout（公布不设线）：全起点 12m 分布（最好/最坏/p25/中位/p75/正份额）、滚动 3/5/10 年最差、分段逐政体 beat 率、4 cells×2 faces 全表、nulls 分布、sensitivity 分布、成本拖累、换手/年。
- 描述条款（批级披露·不替代门）：年化>0、OOS 双正、回撤≥−35%、无崩年、成本压测逐年稳定。

## §5 跑前预测【必填·写死于跑前·≥3 条+极端日先验】

1. **LA-REP legacy 全面板 Sharpe ∈ [0.8, 1.4]**（炉子验证窗 Sharpe 1.11/19 员宇宙 → core48 宇宙+整窗稀释预期微降）。
2. **12m beat 率点估计 ∈ [0.52, 0.72]·CI 下界 ∈ [0.48, 0.65]**（炉子 5.75 年 +117pp 超额映射到逐年起点份额非全胜——2021 入场起点预期负贡献）。
3. **skill_line_v2 过线概率 [40%, 70%]**（N_eff=2008 双 null 校正为高门槛·诚实面：本批判负概率不低）。
4. **deep 轴 CI_lo>0.50 概率 [35%, 65%]**（2013 起含 2015-06 崩盘+2016 熔断极端段·增长成员面更长史更难）。
5. **PBO≤0.25 概率 [60%, 85%]**（4 cells 高相关孪生=选择稳定性预期好；M=4 小矩阵分辨率粗如实注记）。
6. **x2 存活（Sharpe>0）概率 [70%, 90%]**（日频 Top-2 换手成本重·x2 面存活性是真考）。
7. **M1 t ∈ [2.3, 3.6]**（Sharpe~1.1×√T~1630 → t~2.8 量级——**3.0 线贴边，过与不过皆如实**）。
8. **极端日先验（三件套(c)）**：2024-09-24/10-08 政策脉冲（高振幅成员暴涨=低振幅选择**错过**反弹=机会成本面非回撤面）；2015-06~07/2016-01（deep 轴：低振幅防御成员相对跑赢段）；2026-01-19 极端溢价日入整窗。**max 硬界先验**：Top-2 集中面单一日极端 |r1| 可达 −4%~−6%（防御员 2024-10-08 高开缺口日/债灾日），本批**无裸 max 门**（分布界 median/p99.9 主责+整窗路径内化=三件套(a)/(c)合规设计）。

## §6 产物

- script：`scripts/lowamp_p1.py`（probe/selftest/run/status/finalize 子命令·hermetic selftest 离线夹具·确定性双跑字节恒等·checkpoint 断点续跑·import-face 复用=t22 装载/枚举/切片/政体代理+live.paper load_core+engine 正典+t19 adjusted view 消费+science_gates 全库——禁重实现）。
- 产物：`results/lowamp_p1/lowamp_p1_results.json`（顶层 evidence_cutoff+cutoff_meta+audit 段+4 cells×2 axes×2 faces 全表+G 门读数+nulls 三族+sensitivity 分布+分段统计+D6 corr 逐对清单）+ `cells.csv`（小件入 git）+ `probe.json`（探针/锚/D6/closed_family 回执）+ 本文件 §7/§8 回填。
- 下游：PASS → s4 intake（**LOWAMP-\* 纸盘提案**（fast-track：prereg only+GM 署名+次交易日激活）+ STRATEGY_LIBRARY 注册 + 决策链版本台账通道第二活袖候选 + POTENTIAL_WATCHLIST 状态翻面）；judged-negative → 如实出名单（append-only 进出记录）；T-86 普查 lowamp 列 verbatim 消费。

## §7 跑后实证【2026-10-01 finalize 落地·bm-a 03:18:35 audit.machine·§7/§8 回填=bm-b r490】

- **verdict = judged-negative**（三态如实：G1' ∧ G2 ∧ 双轴 ∧ x2 ∧ M1 五门中四败·G-SEG 过——族级合取 FAIL）。产物=results/lowamp_p1/lowamp_p1_results.json（evidence_cutoff=2026-09-22·trials ledger 366,789→368,797 +2,008）。
- **G1' v2（headline=LA-REP legacy 全面板 2020-01-02→2026-09-22 连续单跑）**：sharpe_full=**−1.4475** vs skill_line_v2=**1.9459**（μ_null=+0.0564·σ_null=0.3732·n_eff=ledger 368,797·null_term=1.9459＞passive_term=0.4792）→ line_ok=**FAIL**；block bootstrap CI95=[−2.1969, −0.6836] 下界>0=**FAIL**；trade gate（n_trades=254/n_entries=255≥30·双口径）=PASS。ret_full=−17.99%·maxDD=−18.36%·39.24 笔/年。
- **G2**：DSR=**0.0**＜0.95=FAIL（T=1630·skew=−1.2106·kurt=11.378·sr_star=0.0816）；家族 PBO=**0.0**≤0.25=PASS（M=4 小矩阵分辨率粗如实注记）；eligible_v2=false → **FAIL**。
- **双轴确认**：deep 轴 LA-REP 12m beat=527/1380=**0.3819**·CI_lo=**0.3558**＜0.50 → **FAIL**。
- **x2 存活线**：LA-REP legacy x2 sharpe_full=**−3.6391**＜0 → **FAIL**（ret −50.85%·maxDD −51.01%·x2_cost_drag_sharpe=−2.1915）。
- **M1**：t_from_sharpe=**−3.6815**＜3.0 → **FAIL**（H/L/Z 门槛 t≥3.0·新策略主张面）。
- **G-SEG**：覆盖 legacy bear696/bull345/chop87·deep bear746/bull540/chop94（每段≥50 起点）→ PASS（insufficient-sample 未触发）。
- 全起点 12m 分布（n=1128）：best=+2.98% / p75=−0.72% / median=−1.88% / p25=−3.37% / worst=−7.01% / **positive_share=11.79%**；滚动最差 3y=−9.65%·5y=−14.01%·10y=n/a。
- nulls 三族：same-mask K=2000（μ=+0.0564·p05=−0.5062·p50=+0.0746·p95=+0.5951·σ=0.3732）+ block bootstrap B=2000（p_ge_obs=0.4865）+ sign-flip P=2000（p_two_sided=0.0）。
- sensitivity 描述面（K=500·legacy）：sharpe p05=−1.5256 / p50=−1.0305 / p95=−0.0377·maxdd_worst=−19.71%（零判定宣称）。
- 4 cells×2 axes×2 faces 全表=results/lowamp_p1/cells.csv（**16/16 cell 全负 Sharpe**：legacy base −0.93~−1.47·deep base −0.21~−0.42·x2 全列 −1.77~−3.65）；LA-REP 与 LA-EQ 全轴逐位恒等（两入选员 amp 近同→invvol≈eq·sizing 维度无区分度如实）。
- descriptive：IS 年化 −9.05% / OOS 年化 −9.82% / 无 ≤−35% 崩年 / 成本口径=ETF 26.082bp/往返（X1_RATE import 派生断言恒等）。
- 探针回执：D6 max|corr|=0.1688（VOLATILITY-CE-01·逐对 6/6＜0.7 admit）·closed_family=open（六键零命中）·§0.5 banned gate ADMIT（r483 清洗后）·G-CENSUS {legacy 1,254, deep 1,506} 实测逐位（probe.json）。
- audit.liquidity：amt20_min=¥50M·active_members_ever=**4**·elig_days_median=45·selected_days=1542。

## §8 批后复盘【bm-b r490 回填】

- **预测对账（§5 逐条）**：#1 **错**（Sharpe −1.4475 vs [0.8,1.4]·符号反）；#2 **错**（beat 0.3819 vs [0.52,0.72]·CI_lo 0.3558 vs [0.48,0.65]）；#3 结果=未过线（预测过线概率 [40,70%]——未过在其支持集内，但幅度远超区间反面）；#4 **部分**（deep 未过线在 [35,65%] 概率支持集内）；#5 **对**（PBO 0.0≤0.25）；#6 **错**（x2 −3.64 深负·存活预测 [70,90%] 的点面完全落空）；#7 **错**（t=−3.68 vs [2.3,3.6]·符号反）；#8 极端日先验=无裸 max 门·maxDD −18.4% 路径内化（未逐日对账如实）。
- **⚠ 判决完整性审计（回填轮读只探针·证据=归因面审计）**：core48 冻结白名单+冻结资格面归因探针定谳入选员=**511010（5年国债ETF）+511260（10年国债ETF）**（8/8 采样日 Top-2 稳定·第三席近年=511090·与 audit active_members_ever=4 一致）；**输入面净性四证**：两员均不在 19 员 adjusted-view 替换集（实载=raw face）·raw 全窗零 |ret|>2% 日（无事件伪影）·in-window 价格路径 511010 +17.9%（119.377→140.709）/511260 +24.4%（108.351→134.821）·深轴同向（−17.2%）排除单轴面因 → 常开 Top-2 毛收益应为正两位数，判出面 headline **−18.0%** 不可调和（**~39pp 背离**；成本满算仅 ~6.6% 累计=39.24 笔/年×26.082bp×6.5 年）。**二次证据**：x2 面 ΔSharpe=−2.1915，按 vol≈6.2% 反隐 Δcost≈13.6%/年=单笔 ≈347bp=声明 26bp 的 **13 倍**——成本乘二不可能解释。结论=**疑 runner 执行面缺陷（信号→持仓→P&L 映射），判决数值作为该族测量的可信度=低，verdict 完整性=UNDER REVIEW**；炉子勘探面背离候选因（top20 选择偏差/窗延 2026 债熊/宇宙流动性闸差异）在此旗标裁定前**降级为次要**——先修测量仪再谈机制。
- **治理动作**：完整性旗标入轮报告+CODELY.md（E1 级）+修复单入队（T-2026-10-01-135-P0：lowamp_p1.py 执行面已知答案审计——债对 B&H 已知收益 vs 引擎输出对账）；消费警告=skill_line_v2 n_eff 已吞本批 2,008 试验（若后续治理裁定 VOID 则账本回退=治理动作非本批权限）；watchlist 出名单按冻结门照走+完整性注记（下）。
- 门禁链损耗账：results/gate_attrition.json 追加行（kind=judgment·retro_fill=true·finalize 2026-10-01 03:18 bm-a·回填=bm-b r490）。
- skill_line_v2 当批读数：**1.9459**（null_term 1.9459=μ 0.0564+σ 0.3732×√(2·ln 368,797)；passive_term 0.4792）。
- 试验量归因：2,008 = judged cells 4×判面 2（base+x2）+ same-mask null draws 2,000（§0 冻结式·账本 366,789→368,797 已随 finalize 落账）。
- 全起点分布：见 §7（最好/最坏/p25/中位/p75/正份额+滚动 3/5/10 年最差——非单一起点宣称）。
- 新员注册：**无**（判负不出新员；完整性旗标下双禁——既不注册亦不据本 verdict 作族间 meta 结论）。


---
## §9 治理裁定附录（append-only·2026-10-01 11:4x·bm-a T-140 执行）

- **裁定**：LOWAMP-P1 verdict **VOID-with-face-note**（O-20261001-1108 §三 GM P1 裁决·CEO 反瞎搞令随令裁决·T-2026-10-01-140 执行票）。T-136 审计（research/T136_VERDICT_AUDIT.md）Option VOID 采纳：prereg 自相矛盾（§0 α 机制段 ALWAYS-ON 家族定义 × 裸缺省出场栈=年涨 2-3% 的债对结构性 8-13 天强制换手 254 笔·−33.9pp 磨耗）——判负不归族设计面，**族按设计本意 +15.9%/夏普 +1.16**（审计 Legs B/C 无引擎算术双核）非判负。
- **face-note 保留**：judged-negative 数值面作「引擎缺省出场栈 × 低幅乐器」杂交测量科学保留（verdict 字段已翻 void-with-face-note + verdict_ruling 块），本批产物文件零历史改写（trials_ledger 块逐字保留）。
- **账本补偿回滚**：−2,008 试验（裁决刻快照 368,797→366,789；执行刻 W3..W7 已链入 LOWAMP 含入基·raw head 379,847→**377,839** 净额不变式）＝**results/lowamp_p1/lowamp_p1_void_compensation.json**（ledger_voids 活跃声明+补偿分录·append-only）；science_gates.ledger_head void 面升级（活跃 void 对未 stamp 块恰扣一次·voids_applied 单计律·selftest 69/69 含 6 新腿）；skill_line_v2 n_eff 面：本批判面读数 1.9459@368,799 为历史记录不变，未来读数链自净额 head。
- **E1 完整性旗标解除**：T-136 四腿对账闭环（as-burned 引擎重放逐 bp＋出口中和腿＋无引擎独立算术腿）＝零仪器缺陷；r492 消费警告=正确保护动作（当时如实披露非误报）；修复单 T-2026-10-01-135-P0 面向 P2 出场轴设计收编（AXIS_EXITS 显式轴=设计内测量）。
- **语法带与名单**：W∈[77,104] 带消费声明随判回退（TRIAL_GRAMMAR_LEDGER 行已翻面）——已烧 LOWAMP-P1 批本身禁重跑不变；POTENTIAL_WATCHLIST ① 复列（快通道不变）；**重开通道=LOWAMP-P2 新考卷**（出场轴显式门 TRIAL_LABOR_LAW §4 首个应用：ALWAYS-ON 持有到底显式声明＋runner 显式禁用引擎缺省出场栈·evidence_cutoff 2026-09-22 不变·同族去重门照走）。
- **禁令不变**：冻结批零重跑（P2=新批非重跑）；engine/exit_rules.py 零触碰；样本外恒盲+成本恒开。
