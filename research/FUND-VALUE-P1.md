# FUND-VALUE-P1 预注册 · 基本面价值族（低 PE / 低 PB）股票横截面月频再平衡**新家族**主考格判决批

> 令链血统：**CEO 直令 O-20261002-2115 §一.1**（新策略/新方向开发提速窗）→ T-2026-10-02-145 leg(c)「FIRST FUNDAMENTAL FAMILY PREREGS（value PE/PB）」——本批=三族基本面线（value/quality/dividend-lowvol）第一件。数据基座=T-131（done·fund_history 5224/5129 完备·2026-10-02 15:40）＋T-145 leg(a) PIT 审计回执＋leg(b) H 行 7/8 解锁（fund_earnings_yield=UNLOCK·academic_hml=UNLOCK）。部门=dept:策略（族规格）+研究（judgment 面）；lane=烧批宿主 bm-a（p1c_stock 面板在位）＋价值面 TRANSFER 前置门（见 §2）。
> 模板=research/PREREG_TEMPLATE.md；判据节调 science_gates 共享库禁手抄判线；跑前 commit 冻结；跑后只回填 §7/§8；CEO 研究导向律（2026-09-28 15:35）合规声明：价值/红利/质量=国内基本面打法主流风格，本批=A 股原生打法形式化，非国外框架筛国内打法。

## §0 批件身份【必填·跑前】

- 批名/批号：**FUND-VALUE-P1**。**N_eff=2,004**＝judged cells 4（2 排序规则 × 2 成本面 x1/x2）＋same-mask 随机 null 2,000；sensitivity Sobol 腿=描述面**不计 N_eff**（§3）。扩容即买单。
- 认领（F-04 先行）：fleet/inbox/ **MSG-2026-10-02-2230-bma-ALL-fund-value-p1.md**（本批开工声明＋价值面 TRANSFER 请求数据车道件）＋本票 T-2026-10-02-145 leg(c) 引用＋TRANSFER 票 **T-2026-10-02-149**（bm-c→bm-a·type=transfer）。
- 算力预算：**长活入池**（>5min 一律 runnable_pool·O-20260924-2100 s2）——池单元=4 cell-face（VALUE-PE-x1/x2·VALUE-PB-x1/x2，每单元=401 起点全窗）＋NULLS（2,000 draws·checkpoint）＋SENS（500 draws）共 **6 池条目**；workers_plan={"workers": 32, "priority": "BelowNormal"}（CEO 10% CPU 余量令=优先级面；worker 数=本机核数 bm-a 32 per O-20261002-2158 宽度律【2026-10-02 r597 bm-a 修正窗：12→32 升格对齐，未点火零格已烧，冻结件对齐核查律 T-90 同法】）；checkpoint 逐单元 JSONL done-key skip；**点火前置门（fail-closed 全链）**：①价值面 TRANSFER 落位（§2）②D6 同族相关性 probe ③数据完备 probe——三门全绿才入池点火；批报告必带 audit 段。
- 账本面：finalize 步 `science_gates.append_ledger(batch_name="FUND-VALUE-P1", batch_trials=2004, file_name="results/fund_value_p1/fund_value_p1_results.json", evidence_cutoff="2026-09-22")`（dict schema 唯一禁手抄 prev·r509 序律：块持久化进产物件后才写 guard）。

## §0.5 禁开方向硬闸【必填·跑前·D-20260930-41 §1.2】

- 跑前过闸：`python Tools/banned_direction_gate.py --prereg research/FUND-VALUE-P1.md` → 退出 0=放行（fail-closed）·冻结 commit 内回执。
- 人工预读结论：**零命中预期**——价值排序=基本面估值面选股，禁向九方向（横截面动量/反转·单名择时·网格·水温前置·个股确认前置·市值/价格因子·缓冲带·风格延续）无一涉及；本批无常开择时前置、无缓冲带、无任何价格动量/反转机制；本节不复述禁向词面（机器闸为准·r483 清洗律）。

## §0.6 出场轴显式声明【O-20261001-1108 立法·TRIAL_LABOR_LAW §4·M02 双件门】

- **出场轴=②持有到底（ALWAYS-ON hold-through）**：族定义=常开持有——成员**只因月频横截面排序轮换离场**（再平衡日落出 Top-N 入选集=entry≤0 信号出场·t22 惯例），**无价格类出场**（无止盈/无止损/无衰减踢出/无亏损时限/无持有上限）。
- **引擎缺省出场栈显式禁用【双通道逐键申报·r522 根因修正面】**：
  - params 通道（桥内 4 键）：`take_profit_levels=()`·`trailing_stop_activate=1e12`·`initial_stop=-1.0`·`time_decay_period=10**9`；
  - ExitPatch 通道（桥外 2 键·live/paper.py ExitConfig 工厂补丁）：`loss_time_days=10**9`·`global_hard_limit=10**9`；
  - 两通道键集**互斥断言**入 runner selftest（F11 死信回归守卫）；`exit_signal`=entry≤0 全矩阵；**engine/ 零触碰**；T+1 执行与成本模型=引擎正典不变。
- **第二件门=律 A 烧后出场原因普查**（LOWAMP-P2 §9 立法·P3 首载实证范式）：finalize 步对 headline 以同一冻结机件重跑逐符号捕获每笔出场 reason——hold-through 面上**唯一合法 reason=signal_reversal**；**缺省栈出场占比 >20%（CENSUS_BLOCK_SHARE=0.20 跑前写死）→ verdict=consumption-blocked**。普查块入结果 JSON gates.exit_census。

## §1 α 机制段【必填·D6】

- 机制勾选：**风险溢价**（主：价值溢价=持有近期表现差、账面便宜的公司的补偿——周期股/金融股盈利波动风险由持有者承担，投资者要求补偿）＋**行为偏差**（辅：外推偏差——市场把近期盈利差线性外推为永久劣质，系统性超配近期强势股、低配便宜股；代价支付者=追逐近期热点的行为对手盘）——**结构性**面注记：A 股散户主导市场外推偏差更重（风格极端化历史实证），机制主张以 burn 读数检验不以此段宣称为准。
- **散户凭什么赢【§1.2】**：**制度/容量**——¥1,000,000 账户在 5100+ 股票池 Top-20 等权持有=容量无限、零杠杆需求、月频再平衡执行压力近零；不重跑任何机构结论（价值溢价=公开文献常识面引用，Fama-French HML 族）；例外三问=本账户独有约束（场内股票直接持有·真实成本·本市场 1992-2026 全史窗）成立。
- **同族相关性准入检查【必填·D6】**：入批前 probe 步计算 headline（VALUE-PE）日收益序列 vs **在册六员全部成员**日收益序列逐对 max|corr|；**max|corr| ≥ 0.7 → 拒收 fail-closed 禁烧**（数值与逐对清单 probe 件落盘后方可点火；股票池月频族 vs ETF 在册六员预期低相关，以 probe 实测为准）。
- M1 t 面【必填申报】：`science_gates.t_from_sharpe(sharpe_full, n_periods)` 派生面（headline cell）；判据=`science_gates.m1_t_value_gate`（Harvey/Liu/Zhu 门槛 **t≥3.0**）。
- M3 闭合族对号【必填】：family_key=**fund_value_stock_xs**（新键·`science_gates.CLOSED_FAMILIES` 七在册键零命中=open 照跑；基本面族与既有键机制正交：cta_futures=期货·cn_combo_five/wild_route/factor_blend/t28_spm=ETF 组合与合成族·microcap=崩盘个案·lowamp_daily_xs=ETF 日频振幅族——本批=股票月频估值族）；对号同为 T-145 spec NON-GOALS 声明（M04/M05：不沿用闭合线判决，基本面族=独立新问题；股票面动量类负结果不预测基本面族）。

## §2 数据与面板【必填·跑前探针事实，非结果】

- **价格面板（烧批宿主 bm-a 在位）**：p1c_stock 冻结缓存（T-139 炉面板·meta.json 2026-09-23 生成）——**锚面四元组**：`Money02/data/cache/p1c_stock/*.npy`＋`numpy.load` memmap 直读截断＋1990-12-19 全史起算＋252td 预热。探针事实（results/_r596bma_fund_value_probe.json·bm-a 2026-10-02 生成）：8792 bars·5222 列·5129 员≥252 有效 bar·末 bar **2026-09-22**（qfq·factor.json sidecar=f(latest)=1.0 参考 metadata 不施用·event-day gate 实证）。
- **价值面（数据车道件）**：`data/fund_history/<code>/<face>.json`（T-131 采集·baidu 估值面 pe_ttm/pb 半月频锚 2001-2026 ~612 锚/员/面·as-published 快照=PIT 天然安全）——**当前 bm-c 机本地（R31/R65 车道）→ 本批点火前置门=TRANSFER 落位（T-2026-10-02-149·TRANSFER.md §0 任务单制）**：bm-c 导出面板宇宙（5222 码）合并件 `data/fund_history_export/value_faces.parquet`（列：code·anchor_date·pe_ttm·pb），经 fleet/TRANSFER.md 方案 A git 数据车道送达 bm-a；**导出门（bm-c 侧 fail-closed·票 spec 逐字）**：n_symbols ≥ 5100 ∧ 逐员锚数中位 ≥ 550 ∧ 锚日期覆盖 2001-01→2026-09；manifest 双侧 `fleet/transfers/T-2026-10-02-149-{sender,receiver}.json`；**导出门四元组**：`data/fund_history_export/value_faces.parquet`＋`scripts/fund_value_p1.load_value_faces`（pandas read_parquet）＋2001-01 首锚＋零预热（锚=水平面非滚动面）。
- **接合法（冻结·PIT 律）**：信号日 t 取 **anchor_date ≤ t 的最近一锚** forward-fill（半月频→最大 ~15 个交易日 staleness 如实披露；禁用 t 之后任何锚）；本批**不使用任何财报申报面**（pe_ttm/pb=市场比价面 as-published，非 filing 数据）→ **法定日锚定门（T-145 leg(a) 立法：Q1→04-30/H1→08-31/Q3→10-31/FY→次年04-30）本批 N/A 如实声明**；quality/roe 族预注册（后续件）才携带法定锚定映射。
- 窗口与 **evidence_cutoff=2026-09-22**（面板末 bar·P 族系 D2 前向锁盒同界；cutoff 后新 bar 锁定不得回流）；结果 JSON 顶层 `evidence_cutoff` + `science_gates.cutoff_meta("2026-09-22")`（缺字段=C2 VIOLATION）。
- 起点集：**T-22 冻结枚举律·月频适配**——信号日=每月首个交易日；`enumerate_starts` 月频版（pos≥252td ∧ ≥126td 前瞻 ∧ 当日上市成员数≥24）确定性全枚举；**G-CENSUS 门：起点数逐位==401**（首 1992-09-01·末 2026-03-02·probe 件冻结读数）。
- 数据完备门（不过门禁跑·probe fail-closed）：①p1c_stock meta 在位 ∧ 5129 员≥252 bar ∧ 末 bar==2026-09-22；②价值面 TRANSFER 落位 ∧ 导出门绿；③接合后 headline 首信号日起逐月 pe_ttm 覆盖率 ≥80%（覆盖不足月=该月整月跳过如实计数，禁插补）；④零重复日期+单调；⑤G-CENSUS 401。
- **资格掩码（冻结）**：close notna ∧ volume>0 ∧ amount>0 ∧ **amt20_median ≥ ¥10,000,000**（月频信号日回看 20 成交日中位成交额·股票面流动性闸·披露：Top-20 等权 ¥1M 账户单仓 ¥50k=该闸下零冲击）∧ 上市≥252td ∧ **动态资格=As-of-date ST/退市排除（P4_BATCH2 sec.2 verbatim·runner import 既有 helper 禁重写）**；**估值资格**：pe_ttm ∈ (0, 200] ∧ pb ∈ (0, 20]（负 PE=亏损员不入「便宜」序·极值尾剔除=冻结设计常数非调参）。

## §3 方法学【必填·冻结】

- **信号定义（冻结）**：信号日=每月首个交易日 t；估值面=接合法 forward-fill 至 t；资格掩码内**横截面估值升序排名**：cell A=VALUE-PE（**headline**·Top-N=20 最低 pe_ttm）·cell B=VALUE-PB（Top-N=20 最低 pb）；权重 **eq**（1/N）；**常开**（零前置条件·无择时闸）；**月频再平衡**（信号日 T 收盘算、引擎正典 T+1 开盘执行·O-1132 保守代理）。
- **judged cells 4（跑前写死）**：①VALUE-PE（HEADLINE）②VALUE-PB ③④=①②×x2 成本压测面；N_eff=4+nulls 2,000=2,004。
- **执行语义【§0.6 逐字】**：entry_signal=当日入选 ∧ exit_signal=entry≤0（排序轮换出场·全矩阵注入）→ `engine.run_backtest`（T+1·成本模型·双通道缺省栈显式禁用）→ 持有到底；x2 面=成本乘数 2.0；每起点 fresh-entry 洁净切片（t22 先例）；逐符号子账户分解+eq 权重映射。
- **窗族 {6m=126·12m=252·24m=504}**：最长窗一次跑+同曲线切片（P-5 律）；**主判窗=12m 完整窗**·partial 窗如实标记；被动基线=起点日资格掩码内全体成员等权 B&H 同窗（月频族无再平衡）·beat_k=ret_k>p_ret_k。
- **null 对照（≥2,000 三族全律·RANDOM_LARGE_SAMPLE_LAW §3 逐字）**：①**null_pool（G1' skill line 源）**：K=2,000 **same-mask 随机选择 null**——每月同一资格掩码宇宙（**headline VALUE-PE 掩码**·同 N=20·同执行·eq 权·`rng([20500000, k])` 子流律·**新种子带 20500000/20500500 disjoint 机证（2026-10-02 全 registry 基点+带域实测：避开 stock_face_furnace 零带域 [20333000, 20445400)——基点级检查不足，带域级排查首例）**）内均匀随机选 20 员，全面板模拟取 Sharpe 分布（μ_null/σ_null 入 skill_line_v2）；掩码恒等断言（G-MASK：null 日宇宙==真实 cell 日宇宙逐位）。②**block bootstrap B=2,000**（headline 日收益·块长 21td）＋③**sign-flip permutation P=2,000**（双法并列）。**种子带先登记 `science_gates.SEED_REGISTRY` 再跑**（本批键=fund_value_p1_nulls=20500000·fund_value_p1_sens=20500500）。
- **sensitivity 腿（描述面零判定宣称）**：N=500 空间填充均匀抽取 over（N∈{10,15,20}·pe_cap∈{100,200}·rule∈{pe,pb}·再平衡=月频固定·出场轴=§0.6 同面），产物=Sharpe/均值/maxDD 分布描述列，**不计 N_eff、不设门、禁幸存者宣称**；`rng([20500500, k])`。
- **政体分段**：每起点 regime 标签（510300 列 t22 3-way proxy·p1c 面板侧 510300 在位性由 probe 门⑤前腿验）→ 分段统计；**G-SEG 覆盖门：bear/bull/chop 各 ≥50 起点（12m 完整窗）**——不过=verdict=insufficient-sample。
- **成本口径声明【CN-C7】**：**股票面 V1=13.041bp/边**（`rev_osc_stock_p1.COST_X1` **单源 import 禁手抄**·runner 断言恒等；¥1,000,000 账户口径申报）；往返=26.082bp；x2 面=52.164bp；单笔名义档位披露：eq Top-20 单仓 ¥50,000 > ¥20,000 最低佣金临界=小额档翻倍率不触发；**ETF 与股票结果仅在此口径下可比**。
- **反重复披露（票面 anti-dup）**：①GTJA191/WQ101 因子普查（p1c_stock_ic_batch）=**IC 型因子面**（单因子 IC 序列门），本批=**Top-N 组合 sleeve 面**（全路径回测+注册门），问题正交（IC 高≠sleeve 注册）；②T-139 炉 rev/lowamp/mom 三族=价格面族，本批=基本面估值族首烧；③p1c 面板唯一在用判决存量=上述两族，零重跑；④同族参数面（W×N×cap 维度集）首烧即本批，确定性重现断言=本批为族首烧无前工件可对（首个 judged 记录即基线）。

## §4 判据【必填·跑前写死，禁看结果调线】

- **G1' v2 = `science_gates.g1_prime_v2(sharpe_full, returns, batch_cells, n_trades, n_entries)`**：全期 Sharpe > skill_line_v2（数据驱动=max(被动+0.10, μ_null+σ_null·√(2·ln N_eff))）**且** 平稳 bootstrap CI 下界 > 0 **且** entries≥30（F6 双口径）；批报告逐列披露 skill_line/bootstrap_ci/trade_gate 全输入。
- **G2 注册资格 v2 = `science_gates.g2_registration_v2(g1_pass, dsr, pbo)`**：G1' 过线 **且** DSR≥0.95（`deflated_sharpe_ratio` 原始收益跑，禁用 dsr_from_stats 充数）**且** 家族 PBO≤0.25（`screening/pbo.py` CSCV 8 块·同族判面集=本批 4 cell）；缺输入=诚实拒收。
- 保留历史描述性条款（批级披露）：年化>0、OOS 双正、回撤≥−35%、无崩年、成本压测（x2 面逐年稳定）——描述条款不替代 v2 门。
- **硬界设计三件套【D-20260925-01①】**：本批无数据腐坏检测类判线（纯策略批），max 硬界 N/A；极端日先验入 §5(c)。
- 因子批（IC 型）条款本批不适用（sleeve 面非 IC 面）。
- **新因子 t 面申报【M1】**：headline cell `t_from_sharpe` 派生面跑前申报槽位（SR_ann=§7 回填·T=面板期数·t=§7 回填）；判据=`m1_t_value_gate`（t≥3.0）；缺 t 面=missing_input 拒收非放行。

## §5 跑前预测【必填·写死于跑前，跑后对账】

- (a) **方向**：headline VALUE-PE 12m 完整窗全期 Sharpe 预期为正但**低于在册 ETF 六员水平带**（股票单名尾部风险>ETF 组合；预测带 Sharpe 0.3-0.8 区间·超带=数据问题先查接合法）；beat 被动基线（月频掩码内等权 B&H）为**不确定方向**——价值族 A 股历史含长钝化段（2019-2021 核资产牛=价值跑输），多数起点不成立=诚实判负预期**真实存在**。
- (b) **换手**：月频再平衡换手远低于日频族（LOWAMP 族对照）；x2 成本面对年化拖累预测 <2pp/年（月频敏感性）。
- (c) **极端日先验（硬界三件套 (c)）**：面板窗内极端段=2015-06/07 千股跌停救市段（主板价值股同跌停·流动性枯竭）、2016-01 熔断段、2024-02 微盘崩段（本族 amt20≥¥10M 闸+估值序**天然回避微盘**=该段预测影响显著小于动量/微盘族）、2018 全年熊（价值金融权重段承压）；以上极端段**不设豁免**（描述性披露非判据）。
- (d) **nulls 面**：same-mask 随机 null μ 预期≈掩码内等权被动（无信息选择）——headline 超被动+0.10 才可能过 skill line，预测**过线概率中等偏低**（外推偏差机制在 A 股月频面强度未知=本批要测的问题本身）。

## §6 产物

- runner=`scripts/fund_value_p1.py`（新建·引擎 import 禁重写·selftest 子命令含 F11 双通道互斥断言+G-MASK+G-CENSUS 腿）；
- results：`results/fund_value_p1/fund_value_p1_results.json`（顶层 evidence_cutoff + gates 块含 exit_census）＋nulls/bootstrap/signflip/SENS 分件＋CSV；
- 本文件 §7/§8 回填；轮报告回执。

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

（一次定稿；工程修复重跑须双跑留痕如实记账）

## §8 批后复盘【必填·s7-T】

- 预测对账（对/部分/错）＋门禁链损耗账（`results/gate_attrition.json` 追加一行）＋判线 v2 当批读数（skill_line_v2 数字）；
- 回执入轮报告＋CODELY.md 行级追加；若注册新员：注册件带 evidence_cutoff＋live/paper SIGNAL_BUILDERS 接线＋smoke 锚定门复跑。
- **全起点分布【§1.3·D-20260930-41】**：最好/最坏/p25/中位/p75＋滚动 3/5/10 年窗口最差——只报单一起点=结论无效；撤回判定=多数起点不成立即撤回。
- **试验量归因【§1.4】**：本批新增试验数 2,004（RETAIL_QUANT_TRACK §四闸 30 天 ≤500 预算**超限申报**：基本面三族假期开发窗=O-20261002-2115 CEO 直令提速授权，本批 2,004 含 nulls 2,000（nulls=判据校准面非探索面·RANDOM_LARGE_SAMPLE_LAW 立法内必需），judged 仅 4 格——一句话归因：CEO 直令新家族首考格，判据面 N_eff 由立法最小值撑起非探索面膨胀）。
