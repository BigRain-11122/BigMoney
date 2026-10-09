# FUND-QUALITY-P1 预注册 · 基本面质量族（高 ROE）股票横截面月频再平衡**新家族**主考格判决批

> **FROZEN v1.0（2026-10-03 bm-b r606 冻结窗·五条件门全绿证链）**：①T-152 TRANSFER 落位——quality_faces.parquet 306,414 行/755,292 B/sha256 `ef35c7335ba967c3bb81a06f1cc75843c34937cfe5a0ad9d72c92219facf9735`（bm-c r399 commit 164737489·06:10 PASS 7/7·manifest T-2026-10-03-152-sender.json）②probe 全绿——leg1-4 true（results/_fund_quality_p1_transfer_probe.json r606 06:25：anchor_median 52.0≥50·anchor_p10 26.0≥20 双门〔r604 修正案〕·dup_period_end 0·法定映射全行恒等·G-CENSUS 401·种子带 disjoint 三门过）③D6 同族 probe——**ADMIT max|corr|=0.2407**（NEEDLE-DE-01·六员全对清单 results/fund_quality_p1/d6.json·价值族 headline 另列披露 corr=−0.044 正交主张实证）④种子带注册——`science_gates.SEED_REGISTRY` 落 fund_quality_p1_nulls=20510000·fund_quality_p1_sens=20510500（R250 一步律·r606）⑤banned_direction_gate 对冻结终稿 ADMIT rc0（回执见冻结 commit）。**t0 pin=2001-09-03**（probe first_signal_date_t0=20010903·runner T0_FROZEN 同窗钉定）；**roe_q 单位口径核验=百分比形态实证**（probe roe_raw_stats median 3.72/p90 15.0 → 资格带 (0,100] 百分比原设成立零换算）。冻结后禁改 §0-§6 判据面；跑后只回填 §7/§8。
> **工程披露（r606）**：probe 修正版（r604 a8e082d16 双门+dup period_end 轴）曾被 bm-a r609 收口 (db66e6c45) reland 环按「他机属主面 origin-verbatim」取陈旧快照重放=**整件反向 revert**（−37/+7 镜像·修正面从 origin HEAD 消失~20min）——r606 从 a8e082d16 blob 字节级恢复（git checkout commit -- file·+37/−7 与 revert 精确镜像）+自检 0 FAIL+probe GREEN 复证；fleet 通报 MSG 已发 bm-a（reland 环 face 级恢复须执行时点 rev-parse 重取·r593 律的 face 级扩展提案）。
>
> 令链血统：**CEO 直令 O-20261002-2115 §一.1③**（新策略/新方向开发提速窗）→ T-2026-10-02-145 leg(c)「首批基本面族 prereg：价值/质量/红利低波」——本批=三族第二件（价值族 FUND-VALUE-P1 已冻结在烧）。数据基座=T-131（done·fund_history 5224/5129 完备·2026-10-02 15:40）＋T-145 leg(a) PIT 审计回执（**roe_q=报告期锚·法定日锚定门 MANDATORY：Q1→04-30/H1→08-31/Q3→10-31/FY→次年04-30·期末锚=前视=预注册拒收**）＋leg(b) H 行解锁（roe=roe_q·UNLOCK direct）。部门=dept:策略（族规格）+研究（judgment 面）；lane=烧批池宿主=全机（pool autofill 域）；质量面 TRANSFER 前置门=**T-2026-10-03-152**（bm-c→fleet·git 方案 A·value-faces 先例 5c3939640）。
> 模板=research/PREREG_TEMPLATE.md＋FUND-VALUE-P1.md（族首件·结构逐节镜像）；判据节调 science_gates 共享库禁手抄判线；跑前 commit 冻结；跑后只回填 §7/§8；CEO 研究导向律（2026-09-28）合规声明：质量=国内基本面打法主流风格（高 ROE 白马/核心资产打法），本批=A 股原生打法形式化，非国外框架筛国内打法。

## §0 批件身份【必填·跑前】

- 批名/批号：**FUND-QUALITY-P1**。**N_eff=2,002**＝judged cells 2（1 排序规则 × 2 成本面 x1/x2）＋same-mask 随机 null 2,000；sensitivity Sobol 腿=描述面**不计 N_eff**（§3）。扩容即买单。
- 认领（F-04 先行）：本票 **T-2026-10-03-153**（bm-b 开票+同轮认领·O-1730 即时律）＋TRANSFER 票 **T-2026-10-03-152**（bm-c 数据车道件）＋T-2026-10-02-145 leg(c) 引用；开工声明=轮报告 r601 回执。
- 算力预算：**长活入池**（>5min 一律 runnable_pool·O-20260924-2100 s2）——池单元=2 cell-face（QUALITY-ROE-x1/x2·每单元=401 起点全窗）＋NULLS（2,000 draws·checkpoint）＋SENS（500 draws）共 **4 池条目**；workers_plan={"workers": 32, "priority": "BelowNormal"}（O-20260930-2355 宽度律同族先例=FUND-VALUE-P1 32 workers 对齐）；checkpoint 逐单元 JSONL done-key skip；**点火前置门（fail-closed 全链）**：①质量面 TRANSFER 落位（§2）②probe 全绿（leg1-4）③D6 同族相关性 probe——三门全绿才入池点火；批报告必带 audit 段。
- 账本面：finalize 步 `science_gates.append_ledger(batch_name="FUND-QUALITY-P1", batch_trials=2002, file_name="results/fund_quality_p1/fund_quality_p1_results.json", evidence_cutoff="2026-09-22")`（dict schema 唯一禁手抄 prev·r509 序律：块持久化进产物件后才写 guard）。

## §0.5 禁开方向硬闸【必填·跑前·D-20260930-41 §1.2】

- 跑前过闸（冻结窗）：`python Tools/banned_direction_gate.py --prereg research/FUND-QUALITY-P1.md` → 退出 0=放行（fail-closed）·冻结 commit 内回执。
- 人工预读结论：**零命中预期**——质量排序=基本面盈利面选股，禁向九方向无一涉及；本批无常开择时前置、无缓冲带、无任何价格动量/反转机制；本节不复述禁向词面（机器闸为准·r483 清洗律）。

## §0.6 出场轴显式声明【O-20261001-1108 立法·TRIAL_LABOR_LAW §4·M02 双件门】

- **出场轴=②持有到底（ALWAYS-ON hold-through）**（族定义与价值族同面逐字）：成员**只因月频横截面排序轮换离场**（再平衡日落出 Top-N 入选集=entry≤0 信号出场·t22 惯例），**无价格类出场**（无止盈/无止损/无衰减踢出/无亏损时限/无持有上限）。
- **引擎缺省出场栈显式禁用【双通道逐键申报·r522 根因修正面·与价值族逐字同面】**：
  - params 通道（桥内 4 键）：`take_profit_levels=()`·`trailing_stop_activate=1e12`·`initial_stop=-1.0`·`time_decay_period=10**9`；
  - ExitPatch 通道（桥外 2 键·live/paper.py ExitConfig 工厂补丁）：`loss_time_days=10**9`·`global_hard_limit=10**9`；
  - 两通道键集**互斥断言**入 runner selftest（F11 死信回归守卫）；`exit_signal`=entry≤0 全矩阵；**engine/ 零触碰**；T+1 执行与成本模型=引擎正典不变。
- **第二件门=律 A 烧后出场原因普查**（LOWAMP-P2 §9 立法）：finalize 步对 headline 以同一冻结机件重跑逐符号捕获每笔出场 reason——hold-through 面上**唯一合法 reason=signal_reversal**；**缺省栈出场占比 >20%（CENSUS_BLOCK_SHARE=0.20 跑前写死）→ verdict=consumption-blocked**。普查块入结果 JSON gates.exit_census。

## §1 α 机制段【必填·D6】

- 机制勾选：**风险溢价**（主：质量溢价=高盈利企业=更低融资成本/更低财务困境风险的补偿——持有低 ROE「垃圾」股承担盈利恶化与退市尾部风险，投资者要求补偿的反面=质量面折价之谜的补偿面）＋**行为偏差**（辅：彩票偏好/魅力股偏差——投资者系统性超配叙事性强的低盈利成长股、低配「无聊」的高盈利现金牛，代价支付者=追逐魅力股的行为对手盘）——**结构性**面注记：A 股散户主导市场彩票偏好更重（题材股历史实证；本批资格闸 amt20≥¥10M 反向排除微盘=与 BAN-07 方向零接触，机制叙述纯市场结构上下文非因子输入），机制主张以 burn 读数检验不以此段宣称为准。
- **散户凭什么赢【§1.2】**：**制度/容量**——¥1,000,000 账户在 5100+ 股票池 Top-20 等权持有=容量无限、零杠杆需求、月频再平衡执行压力近零；不重跑任何机构结论（质量溢价=公开文献常识面引用，FF5 RMW 族）；例外三问=本账户独有约束（场内股票直接持有·真实成本·本市场 1992-2026 全史窗）成立。
- **同族相关性准入检查【必填·D6】**：入池前 probe 步计算 headline（QUALITY-ROE）日收益序列 vs **在册六员全部成员**日收益序列逐对 max|corr|；**max|corr| ≥ 0.7 → 拒收 fail-closed 禁烧**（数值与逐对清单 probe 件落盘后方可点火；股票月频族 vs ETF 在册六员预期低相关，以 probe 实测为准；**与 FUND-VALUE-P1 headline 的相关性另列披露**——同面板同执行族，两族 headline 相关性由 D6 机制段各自申报、若价值族在册后进六员集则照测）。
- M1 t 面【必填申报】：`science_gates.t_from_sharpe(sharpe_full, n_periods)` 派生面（headline cell）；判据=`science_gates.m1_t_value_gate`（Harvey/Liu/Zhu 门槛 **t≥3.0**）。
- M3 闭合族对号【必填】：family_key=**fund_quality_stock_xs**（新键·`science_gates.CLOSED_FAMILIES` 在册键零命中=open 照跑；与 fund_value_stock_xs 机制面注记=估值面 vs 盈利面正交主张，判据面各自独立全路径回测，互不沿用判决·M04/M05 NON-GOALS verbatim）。

## §2 数据与面板【必填·跑前探针事实，非结果】

- **价格面板**：p1c_stock 冻结缓存（T-139 炉面板·与价值族同面板）——**锚面四元组**：`Money02/data/cache/p1c_stock/*.npy`＋`numpy.load` memmap 直读截断＋1990-12-19 全史起算＋252td 预热。探针事实（probe leg1·bm-b 2026-10-03 已跑绿）：8792 bars·≥5100 列·末 bar **2026-09-22**（qfq）。
- **质量面（数据车道件）**：`data/fund_history/<code>/roe_q.json`（T-131 采集·baidu 基本面面·**报告期键控**·2001Q1..2026Q2·~101 期/员）——当前 bm-c 机本地（R31/R65 车道）→ **本批点火前置门=TRANSFER 落位（T-2026-10-03-152·TRANSFER.md §0 任务单制）**：bm-c 导出面板宇宙合并件 `data/fund_history_export/quality_faces.parquet`（列：code·period_end·**avail_date**·roe_q），**avail_date=法定可获取日烘焙入导出**（Q1→04-30/H1→08-31/Q3→10-31/FY→次年04-30·T-145 leg(a) PIT 审计立法面），经 fleet/TRANSFER.md 方案 A git 数据车道送达全机；**导出门（bm-c 侧 fail-closed·票 spec 逐字）**：n_symbols ≥ 5100 ∧ 逐员 avail 锚数中位 ≥ 60 ∧ avail 覆盖 2001-04-30→2026-08-31 ∧ 零重复期键 ∧ avail 单调升 ∧ **法定映射全行恒等**；13 员 roe_q:nonperiod_keys 非法期键行=诚实排除+计数披露（禁静默丢）；manifest `fleet/transfers/T-2026-10-03-152-sender.json`。
- **接合法（冻结·PIT 律·本批核心增量）**：信号日 t 取 **avail_date ≤ t 的最近一锚** forward-fill（季频→最大 ~124 交易日 staleness 如实披露；**禁用 t 之后任何锚·期末锚=前视=拒收**·probe S2/S6 已知答案腿守护）；**法定日锚定门（T-145 leg(a) 立法）本批 MANDATORY 生效**（与价值族 N/A 声明对照：roe_q=申报面数据非市场比价面）。
- 窗口与 **evidence_cutoff=2026-09-22**（面板末 bar·P 族系 D2 前向锁盒同界；cutoff 后新 bar 锁定不得回流）；结果 JSON 顶层 `evidence_cutoff` + `science_gates.cutoff_meta("2026-09-22")`（缺字段=C2 VIOLATION）。
- 起点集：**T-22 冻结枚举律·月频适配**（与价值族逐字同面）——信号日=每月首个交易日；`enumerate_starts` 月频版（pos≥252td ∧ ≥126td 前瞻 ∧ 当日上市成员数≥24）确定性全枚举；**G-CENSUS 门：起点数逐位==401**（首 1992-09-01·末 2026-03-02·价值族 probe 冻结读数同数）。
- 数据完备门（不过门禁跑·probe fail-closed·leg1-4）：①p1c_stock meta 在位 ∧ ≥5100 员 ∧ 末 bar==2026-09-22；②质量面 TRANSFER 落位 ∧ 导出门绿（含法定映射全行恒等）；③接合后 headline 首信号日起逐月 roe_q **数据覆盖率** ≥80%（**覆盖层=有非空锚即算·资格层分列**·r599 分层律；覆盖不足月=该月整月跳过如实计数，禁插补）；④零重复期键+avail 单调；⑤G-CENSUS 401；⑥种子带 disjoint（leg4·已跑绿）。
- **资格掩码（冻结）**：close notna ∧ volume>0 ∧ amount>0 ∧ **amt20_median ≥ ¥10,000,000**（月频信号日回看 20 成交日中位成交额·与价值族逐字同面）∧ 上市≥252td ∧ 动态资格=As-of-date ST/退市排除（P4_BATCH2 sec.2 verbatim·runner import 既有 helper 禁重写）；**质量资格**：roe_q ∈ **(0, 100]**（正盈利员才入「质量」序·极值尾剔除=冻结设计常数非调参；**单位口径=百分比申报**，冻结窗以 probe roe_raw_stats 实测分布核验单位假设，若实测为小数形态则带内换算为 (0, 1.0] 等价带并如实注记——判据面零漂移）。

## §3 方法学【必填·冻结】

- **信号定义（冻结）**：信号日=每月首个交易日 t；盈利面=接合法 forward-fill 至 t（法定锚）；资格掩码内**横截面 roe_q 降序排名**：cell A=QUALITY-ROE（**headline·唯一排序规则**·Top-N=20 最高 roe_q）；权重 **eq**（1/N）；**常开**（零前置条件·无择时闸）；**月频再平衡**（信号日 T 收盘算、引擎正典 T+1 开盘执行·O-1132 保守代理）。
- **judged cells 2（跑前写死）**：①QUALITY-ROE（HEADLINE）②=①×x2 成本压测面；N_eff=2+nulls 2,000=2,002。
- **执行语义【§0.6 逐字】**：entry_signal=当日入选 ∧ exit_signal=entry≤0（排序轮换出场·全矩阵注入）→ `engine.run_backtest`（T+1·成本模型·双通道缺省栈显式禁用）→ 持有到底；x2 面=成本乘数 2.0；每起点 fresh-entry 洁净切片（t22 先例）；逐符号子账户分解+eq 权重映射。
- **窗族 {6m=126·12m=252·24m=504}**：最长窗一次跑+同曲线切片（P-5 律）；**主判窗=12m 完整窗**·partial 窗如实标记；被动基线=起点日资格掩码内全体成员等权 B&H 同窗（月频族无再平衡）·beat_k=ret_k>p_ret_k。
- **null 对照（≥2,000 三族全律·RANDOM_LARGE_SAMPLE_LAW §3 逐字）**：①**null_pool（G1' skill line 源）**：K=2,000 **same-mask 随机选择 null**——每月同一资格掩码宇宙（**headline QUALITY-ROE 掩码**·同 N=20·同执行·eq 权·`rng([20510000, k])` 子流律·**新种子带 20510000/20510500 disjoint 机证（probe leg4 2026-10-03 已跑绿：全 registry 166 基点 exact+stock_face_furnace 占用带 [20333000, 20445400) 开区间+邻近 ≥2000 三门全过·与价值族块 20500000 净距 ≥8000）**）内均匀随机选 20 员，全面板模拟取 Sharpe 分布（μ_null/σ_null 入 skill_line_v2）；掩码恒等断言（G-MASK：null 日宇宙==真实 cell 日宇宙逐位）。②**block bootstrap B=2,000**（headline 日收益·块长 21td）＋③**sign-flip permutation P=2,000**（双法并列）。**种子带先登记 `science_gates.SEED_REGISTRY` 再跑**（本批键=fund_quality_p1_nulls=20510000·fund_quality_p1_sens=20510500·冻结窗 R250 一步律落键）。
- **sensitivity 腿（描述面零判定宣称）**：N=500 空间填充均匀抽取 over（N∈{10,15,20}·roe_cap∈{50,100}·rule=roe 固定·再平衡=月频固定·出场轴=§0.6 同面），产物=Sharpe/均值/maxDD 分布描述列，**不计 N_eff、不设门、禁幸存者宣称**；`rng([20510500, k])`。
- **政体分段**：每起点 regime 标签（510300 列 t22 3-way proxy）→ 分段统计；**G-SEG 覆盖门：bear/bull/chop 各 ≥50 起点（12m 完整窗）**——不过=verdict=insufficient-sample。
- **成本口径声明【CN-C7】**：**股票面 V1=13.041bp/边**（`rev_osc_stock_p1.COST_X1` **单源 import 禁手抄**·runner 断言恒等；¥1,000,000 账户口径申报）；往返=26.082bp；x2 面=52.164bp；单笔名义档位披露同价值族（eq Top-20 单仓 ¥50,000 > ¥20,000 最低佣金临界）。
- **反重复披露（票面 anti-dup）**：①FUND-VALUE-P1=同面板姊妹族（估值面），本批=盈利面首烧——两族排序输入正交（pe_ttm/pb vs roe_q）、judgment 全路径各自独立，headline 相关性由 D6 披露不预设；②T-139 炉三族=价格面族零重跑；③p1c 面板在用判决存量+1 族零重跑；④同族参数面（N×roe_cap 维度集）首烧即本批，确定性重现断言=族首烧无前工件（首个 judged 记录即基线）。

## §4 判据【必填·跑前写死，禁看结果调线】

- **G1' v2 = `science_gates.g1_prime_v2(sharpe_full, returns, batch_cells, n_trades, n_entries)`**：全期 Sharpe > skill_line_v2（数据驱动=max(被动+0.10, μ_null+σ_null·√(2·ln N_eff))）**且** 平稳 bootstrap CI 下界 > 0 **且** entries≥30（F6 双口径）；批报告逐列披露 skill_line/bootstrap_ci/trade_gate 全输入。
- **G2 注册资格 v2 = `science_gates.g2_registration_v2(g1_pass, dsr, pbo)`**：G1' 过线 **且** DSR≥0.95（`deflated_sharpe_ratio` 原始收益跑，禁用 dsr_from_stats 充数）**且** 家族 PBO≤0.25（`screening/pbo.py` CSCV 8 块·同族判面集=本批 2 cell）；缺输入=诚实拒收。
- 保留历史描述性条款（批级披露）：年化>0、OOS 双正、回撤≥−35%、无崩年、成本压测（x2 面逐年稳定）——描述条款不替代 v2 门。
- **硬界设计三件套【D-20260925-01①】**：本批无数据腐坏检测类判线（纯策略批），max 硬界 N/A；极端日先验入 §5(c)。
- **新因子 t 面申报【M1】**：headline cell `t_from_sharpe` 派生面跑前申报槽位；判据=`m1_t_value_gate`（t≥3.0）；缺 t 面=missing_input 拒收非放行。

## §5 跑前预测【必填·写死于跑前，跑后对账】

- (a) **方向**：headline QUALITY-ROE 12m 完整窗全期 Sharpe 预期为正但**低于在册 ETF 六员水平带**（与价值族同面预测：股票单名尾部风险>ETF 组合；预测带 Sharpe 0.3-0.8 区间·超带=数据问题先查接合法与法定锚）；beat 被动基线=**不确定方向**——A 股质量溢价历史含长失效段（2013-2015 题材股牛市=高质量白马持续跑输·2017 白马结构牛=质量大年），多数起点不成立=诚实判负预期**真实存在**。
- (b) **换手**：月频再平衡换手与价值族同阶（远低于日频族）；x2 成本面年化拖累预测 <2pp/年。
- (c) **极端日先验（硬界三件套 (c)）**：面板窗内极端段=2015-06/07 千股跌停救市段、2016-01 熔断段、2024-02 微盘崩段（本族 amt20≥¥10M 闸+盈利序天然偏大盘白马=微盘暴露低）、2018 全年熊（白马消费质量段承压）、2021Q1-2024 白马估值消化段（质量族特色压力段·核心资产抱团瓦解）；以上极端段**不设豁免**（描述性披露非判据）。
- (d) **nulls 面**：same-mask 随机 null μ 预期≈掩码内等权被动——headline 超被动+0.10 才可能过 skill line，预测**过线概率中等偏低**（质量溢价在 A 股月频面强度未知=本批要测的问题本身）。

## §6 产物

- runner=`scripts/fund_quality_p1.py`（待建·引擎 import 禁重写·selftest 子命令含 F11 双通道互斥断言+G-MASK+G-CENSUS 腿·FUND-VALUE-P1 runner 结构镜像）；
- probe=`scripts/fund_quality_p1_probe.py`（已建·selftest 25/0·live RED=TRANSFER 必要性诚实回执）；
- results：`results/fund_quality_p1/fund_quality_p1_results.json`（顶层 evidence_cutoff + gates 块含 exit_census）＋nulls/bootstrap/signflip/SENS 分件＋CSV；
- 本文件 §7/§8 回填；轮报告回执。

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

（一次定稿；工程修复重跑须双跑留痕如实记账）

**r806 finalize 实证（2026-10-08 23:33-23:35 落判·bm-b·driver 日志 rc0·单读 r638 律）**：

- **判决=insufficient-sample**（G-SEG 分段覆盖 bear 70 / bull 65 / **chop 14<50** / na 246——与 DIVLOWVOL/VALUE 两族同结构性面；判据面顺序先决拒收，禁重跑）。
- headline x1（t0 2001-09-03·T 6,077）：Sharpe **−0.3177**·ret_full 2.4844·maxDD **−1.1454（NAV 负穿面=病理披露）**·1,393 trades；日收益面 skew −54.70·kurtosis 3,044.8（极端日病理面）。
- **病理披露（重要）**：headline x1 净值路径负穿（max_dd < −100%）→ 滚动窗「收益」出现 −12,598.74（3y）/−24,391.97（5y）/−28,030.64（10y）荒谬量级伪影——**该三数禁按面采信**；疑似引擎 per-symbol 子账或 qfq readjust 除权面病理，判决不受影响（G-SEG 先决+判据面全红），但**族重访前必须先修此病理**。
- x2 生存面 Sharpe 0.3911>0 PASS（x1 病理面下两面读数不可比，如实注记）。
- G1' v2 读数：line_ok=false；bootstrap CI95 [−0.5046, −0.1060] 下界<0 ✗；M1 t=−1.5600 fail；DSR 0.0 fail；PBO 1.0（fail band）；exit_census PASS（block_share 0.2）。
- nulls（same-mask k=2,000）：μ 0.0171·σ 0.2046·p05/p50/p95=−0.2943/0.0254/0.3287；bootstrap p_ge_obs=0.522；signflip p_two_sided=0.0405。
- 全起点 12m 分布（n=395）：best +1.9731 / p75 +0.2170 / median 0.0 / p25 −0.1322 / worst −1.0347 / positive_share 40.0%；滚动最差三数如病理披露节=伪影面禁采信。
- 敏感性（k=500）：Sharpe p05/p50/p95=−0.3177/0.0527/0.3035·maxdd_worst −1.1454。
- 台账：本批 +2,002（prev 792,907=陈旧树基座链·r807 追加式分叉补账 FUND-TRIO-REANCHOR-R807 重锚至活链头 831,336·零双计零丢失）。

## §8 批后复盘【必填·s7-T】

- 预测对账（对/部分/错）＋门禁链损耗账（`results/gate_attrition.json` 追加一行）＋判线 v2 当批读数（skill_line_v2 数字）；
- 回执入轮报告＋CODELY.md 行级追加；若注册新员：注册件带 evidence_cutoff＋live/paper SIGNAL_BUILDERS 接线＋smoke 锚定门复跑。
- **全起点分布【§1.3·D-20260930-41】**：最好/最坏/p25/中位/p75＋滚动 3/5/10 年窗口最差——只报单一起点=结论无效；撤回判定=多数起点不成立即撤回。
- **试验量归因【§1.4】**：本批新增试验数 2,002（RETAIL_QUANT_TRACK §四闸 30 天 ≤500 预算**超限申报**：基本面三族假期开发窗=O-20261002-2115 CEO 直令提速授权——与 FUND-VALUE-P1 同窗同归因链；judged 仅 2 格，nulls 2,000=判据校准面非探索面·RANDOM_LARGE_SAMPLE_LAW 立法内必需；一句话归因=CEO 直令新家族第二件，判据面 N_eff 由立法最小值撑起非探索面膨胀）。

**r807 批后复盘（absorb 窗回填）**：

- **预测对账=部分对**：①方向带=**错（远低于带）**——headline Sharpe −0.3177 低于 §5(a) 预测带 0.3-0.8 下沿且为负，但读数受 NAV 负穿病理污染（§7 病理披露节），方向带对账**暂缓定性**，待病理修复后族重访再对；②「多数起点不成立预期」=**对**（positive_share 40.0%·median 0.0）；③nulls μ≈等权被动预期=**对**（μ 0.0171·σ 0.2046 宽 null 面≈无信息被动量级）。
- **判线 v2 当批读数**：line_ok=false（obs 负值远离技能线；N_eff 面为陈旧树 792,909 时点读数如实留档）。
- **门禁链损耗账**：`results/gate_attrition.json` 追加一行（FUND-QUALITY-P1·r807）。
- **判决链结论**：G-SEG 先决 insufficient-sample（单读 r638 律）→ 无注册新员；判据面独立读数全红（CI 下界负/M1 fail/DSR 0/PBO fail）留档。**族重访前置=①NAV 负穿病理修复（工程排查项·疑似 qfq readjust 或 per-symbol 子账面）②G-SEG chop 覆盖结构性裁决**，两项齐备才准重烧。
- **全起点分布**：见 §7 六数面（滚动三数因病理禁采信已如实标注）；撤回判定=不适用（判决非 judged-negative）。
- 回执：r807 轮报告+CODELY.md 行级追加。

**r811 NAV 病理分诊定谳（due ≤10-10 12:00·bm-b·探针=scripts/fund_trio_p1_diagnostics.py quality-nav/quality-cliff/quality-era 三腿·selftest 7/7）**：

- **病理定谳=真实年代亏损+分母伪影复合，非数据/引擎缺陷**：①面板无零/负价（close·open 全史 0 符号命中）；②引擎记账与价格面恒等（2005-05-16 过零日对账：observed pnl Δ−¥16,001 vs 简化 mark-to-market −¥16,580，96% 吻合=数据面解释、引擎无罪）；③**NAV 毁灭根因=2001-2005 高 ROE 排名在财报造假年代= fraud 磁铁**——era 归因 45 个 firing 月实证：最差月 2004-04 −19.1%（000633 合金投资 −77.8%=德隆系崩盘真实事件·000717 −33.5%）、2001-09 −9.9%（000682 东方电子 −34%=造假崩盘真实事件）、2005-04/05 −11.5%/−11.4%；简化月度复合 −67%（引擎真实路径更深至过零）；④2005-05-16 NAV 0.0045 过零=资本已灭后的常日（当日成员均动 −10%~+3.8% 平常），过零后一切统计（maxDD −1.1454/2006 年 −338×/rolling −12,598×/ret_full +248%/Sharpe −0.32 符号混乱）=**负 NAV 分母伪影，全部禁采信**（r807 披露确认）。
- **族重访前置①诊断面=已闭合**（病理根因定谳如上）；**修复面候选（须走预注册+GM 署名链，本批零擅改）**：a) 年代处理——2001-2005 造假高 ROE 段须 fraud-era 处理或仿 divlowvol 干净尾 t0 后钉（2006-02 后）；b) 记账止损诚实面——hold-through+eq 设计对已灭账本无停机机制，重访版应过零即终止并诚实报 ruin（禁符号翻转伪影继续复利）。前置②（G-SEG chop 覆盖）维持。
- 证据三件：results/fund_quality_p1/nav_pathology_triage_r811.json（重构校验 Sharpe/NAV/maxDD 三恒等）+ nav_cliff_dissection_r811.json（过零日逐成员解剖+记账对账）+ nav_era_attribution_r811.json（45 月毁伤归因+点名）。回执：r811 轮报告。
