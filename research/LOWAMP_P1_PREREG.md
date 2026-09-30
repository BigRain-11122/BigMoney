# LOWAMP_P1_PREREG —— 低振幅家族专用判决批（CEO 快速通道·POTENTIAL_WATCHLIST #1·T-132/O-2026-09-30-2230）

> 【状态：FROZEN——跑前 commit 冻结】令源：CEO 直令 O-2026-09-30-2230（「很好，务必关注有做工的」·快速通道律：名单内候选专用批 prereg 优先开热+过线即纸盘提案+判负如实出名）；票=T-2026-09-30-132-P1（immediate·四切片 s1 冻结/s2 runner+池/s3 判决/s4 入册）；勘探证据=research/LOWAMP-FURNACE-20260930-P1.md（1060 格炉·发现+全史验证双窗·top-50 双 nulls·top-20 全 robust·置换 p=0.0018）。跑后只许回填 §7/§8，禁改判据禁重跑（工程修复重跑须双跑留痕）。统摄律：firm/RANDOM_LARGE_SAMPLE_LAW v1.0（§1 起点轴+§2 参数轴+§3 分窗轴）+ firm/TRIAL_LABOR_LAW §3/§4 + research/BACKTEST_SCIENCE.md v2（判据唯一权威）+ BACKTEST_PLAN.md 三铁律 + COMPUTE_AUDIT.md 批件纪律 + O-1820(3) consumer_plan 必填律。

## §0 批件身份【必填·跑前】

- 批名/批号：**LOWAMP_P1**（低振幅家族=日频横截面振幅选股族·新族声明见 §1）。批内格数=**501 judged cells**（1 个熔炉延续锚格 C0096 逐字〔amp89·top2·invvol·always-on·declared anchor 非抽样〕+ **500 Sobol 空间填充参数抽取**〔RANDOM_LARGE_SAMPLE_LAW §2·禁手挑〕）——**非波级语法批**（无 5,000 生成语法面·冻结带宽内参数轴抽样·W 系列零血统新语法）。
- 认领：T-2026-09-30-132-P1 已认领（bm-a r494·commit 97391257f·O-1730 同轮认领即开动）；本件=s1 冻结切片。
- 部门归属：dept:策略+dept:研究 joint（票面 spec 同 W 系例）。
- 算力预算：501 cells × (2 成本面 × 3 窗 {6m,12m,24m} × K=2000 虚拟起点评估 + 双 nulls B=2000/P=2000 重采样)——全向量化腿·est 分钟级-小时级池批 @ workers_plan ≥floor(26/0.8)=32 帽 26 workers（CPU 余量律 O-20260929-10:29·BelowNormal 优先级）——**>5min 一律入 results/runnable_pool.json 提交后返回**（O-2100）；预算上限=**6h 超限合法停**（O-1901 ③·checkpoint 断点续跑 R41）。
- consumer_plan（O-1820(3) 必填）：LOWAMP-P1 verdict 面（results/lowamp_p1/judge.json）→ s4 intake（D6 绑定门→STRATEGY_LIBRARY 注册行+LOWAMP-* 纸盘提案〔快速通道律：prereg-only、GM 署名+激活下一交易日〕+决策链版本台账通道第二活袖候选）→ POTENTIAL_WATCHLIST 状态翻面（过线=纸盘在跑·判负=如实出名）→ 48h CEO 呈报面+scorecard CEO 面；T-86 普查 lowamp 列确认=verbatim 消费本批 judged faces 禁重跑（票面 anti-dup 原文）；screen null p95 无（单级判决批·无初筛面）。
- **48h CEO 呈报钟**：判决面落地起计（judge-finalize 后 48h·票面持有）。

## §0.5 禁开方向硬闸【必填·跑前】

- 跑前过闸：`python Tools/banned_direction_gate.py --prereg research/LOWAMP_P1_PREREG.md`——退出 0=放行；退出 1=不受理（fail-closed）。
- 命中已证伪九方向检查：低波/低振幅异象=**未判负方向**（W4 低波异象链已扫=在册支持面；仓内 IC 三窗恒负+lowamp20 G 行登记=方向先验仓内锚）。
- **例外声明（机械闸合同三件套·matched ids 逐条引证）**：正文字面命中 **BAN-03**（§1 证据链引用 intraday_range h5/h10/h20 IC 读数=振幅因子证据非动量择时主张）与 **BAN-04**（§1 新族对照面引用 GRID-SLEEVE=网格触发族=防重复声明的对照项非网格策略）；例外类型=**new_mechanism**；原证伪判面不可能看见：原 BAN-03 判面为单名 5/10/20 日择时动量、原 BAN-04 判面为网格触发退出族，两者构造上皆不可能看见日频横截面振幅排序选股（19 员相对排序+topN 集中度+流动性闸、无择时动量信号、无出场网格）这一新机构造面。

## §1 α 机制段【四选一+论证·D6 门槛】

- **机制主张（A 行为偏差·主+风险源价·辅）**：低振幅横截面溢价——**代价支付者=高振幅奇观 ETF 的追涨彩票偏好者**（注意力/奇观日流量虹吸→宽幅标的拥挤溢价蒸发；窄幅平静标的由耐心持有者收取风险源价）。仓内证据链：①IC 读数 intraday_range h5/h10/h20 三窗恒负（−0.0231/−0.0342/−0.0461·ETF 宇宙在册）②FACTOR_CENSUS_REGISTRY G 行 lowamp20「20 日 mean((high−low)/close)·低=溢价（sign prior −）」③W4 低波异象链已扫在册 ④熔炉 1060 格族级确认（top-20 全 robust·置换 p=0.0018）。**MAX effect 主源未取=未验证假设留档**（W8-AMP 草案 digest 死路实录沿用——宣称不采信留档非先验）。
- **散户凭什么赢（§1.2）**：ETF 域日频横截面=机构主导面，散户优势=不追奇观、拿平静复利——与在册低波员工（VOLATILITY-CE-01）同源不同构（在册员=时序低波门·本族=横截面振幅排序选股·**构造性相异**）。
- **新族声明（D6·禁翻案律对照面）**：本族 vs 已判决闭合族——GRID-SLEEVE=网格触发族（不同构·无出场网格）；CN-DIV-LOWVOL-ROT=**月度**轮动低波族（本族=**日频**再平衡+振幅窗 77-104d 长窗·再平衡频率与选股度量双异）；VOLATILITY-CE-01=在册员工个体（时序 500bar 波动门·非横截面选股）。**族键=lowamp_daily_xs（新族）**——不在 CLOSED_FAMILIES 六行册。
- **同族相关性准入检查【D6】**：批内 501 cells 两两日收益 corr 矩阵全量计算（去重门前置级·|corr|≥0.999 塌缩=T-84 s3 持仓指纹律）；0.7 线在注册级=s4 intake（对在册公判+存活者两两 max|corr|·≥0.7 拒收·sleeve-tag 先例）。
- 排除簿（anti-dredging）：judged declare 窗=generate 时点实读（W1/MASS/W2-W11 已判格+存活清单·cell key 无振幅族构型=结构性零命中预期·命中数如实披露）。

## §2 数据与面板【必填·跑前探针事实】

- **宇宙（19 员·冻结）**：data/consolidation/adjusted_view/ 全 19 parquet（159901/159928/159995/510310/510500/512000/512010/512100/512170/512200/512480/512690/512710/512800/513100/513500/515000/515050/515220·consolidation 后复权 OHLCV+A 面·r494 探针实测：common window **2020-03-02..2026-09-23**·19/19 员末日齐一·cols=open/high/low/close/volume/amount/adj_factor/cons_break）。熔炉同面（furnace「19 只复权 ETF·consolidation adjusted_view」逐字）。
- **信号度量（冻结·零发明律）**：amp_N(d)=rolling N 日 mean( (high(d')−low(d'))/close(d') )（日振幅=在册 intraday_range 公式〔engine/factors.py 冻结公式·FACTOR_CENSUS_REGISTRY A 行+G 行 lowamp20 同构·窗口参数化为 N〕；N∈冻结带 **[77,104] 整数日**）；选股=**amp_N(d) 升序**取最低 topN 员（低振幅·sign prior −）；信息集=信号日 d 收盘（T+1 因果律：入场=d+1 开盘）。
- **仓位（冻结）**：topN∈{2,3}；sizing∈{invvol,eq}——invvol=1/vol20_i 归一（vol20_i=ret 滚动 20d 样本 std·ddof=1·min_periods=20·含 d）；eq=1/topN 等权。**常开**（无政体/波动门——furnace 带逐字）。
- **集中度风险闸（T-132 强制面·冻结）**：①流动性下限=员资格 iff amount(d)>0 **且** med20_amount(i,d)≥**¥50,000,000**（20 日中位成交额·5 千万元 ETF 面保守下限）；②可交易性=信号日在面板内且非末日（防假尾）；③合格池<topN 日=缺位槽**持现金**（现金腿 0 收益如实·缺位计数披露）。
- **成本口径（冻结·repo 正典面）**：x1=13bp/边·T+1 开盘成交·退出优先级冻结禁改（engine/exit_rules.py 零触碰）；x2=CostPatch(2.0)（T22 Erratum-1 multiplier 律·禁直引常数）。**诚实披露**：熔炉面=0.1%/边（10bp）<判决面 13bp=判决面更保守·不可比性如实注记。
- **evidence_cutoff=2026-09-22（P-5C 冻结口径 binding·全窗截断）**：面板截断于 cutoff（末日 2026-09-22 逐员断言）；cutoff 后新 bar 不回流。结果 JSON 顶层必带 `evidence_cutoff`+`science_gates.cutoff_meta("2026-09-22")`（缺字段=C2 VIOLATION）。
- 数据完备门（fail-closed·不过即 VOID 零产出）：①G-PANEL：19/19 员 parquet 在位·截断后末行==2026-09-22 逐员唯一·OHLCV+amount 列齐；②G-COMMON：common window ≥2020-03-02 起（探针锚·r494 实测冻结）；③G-UNIVERSE：19 员清单==§2 逐字（runner 断言）；④G-COST：13bp/26bp 双面常数 import 实读禁手抄；⑤G-EXCLUDE：judged declare 窗装载+命中计数披露；⑥G-SEED：三 seed 键=SEED_REGISTRY 三步律（见 §3·冻结合 commit 登记 R250 一步律·撞带重取）。

## §3 方法学【冻结】

- **参数轴抽样（RANDOM_LARGE_SAMPLE_LAW §2·禁手挑）**：Sobol 空间填充 500 抽（scipy.stats.qmc.Sobol(参数维, scramble=True, seed=SEED_BASE)——**import-face 复用 MASS_TRIAL_W1 sample_draws 范式禁重写**）：连续轴 amp∈[77,104]→取整；离散轴 topN∈{2,3}/sizing∈{invvol,eq}（独立 RNG 流 `default_rng([SEED_BASE, 7919])` 等概率）；+1 declared anchor cell C0096（amp89·top2·invvol·熔炉代表格逐字·延续锚非抽样·provenance 单列）。**去重门（T-84 s3）**：参数四元组恒等塌缩（保留代表=确定性最低 idx·塌缩计数披露）；预期 501→distinct ~500±2。
- **起点轴抽样（RANDOM_LARGE_SAMPLE_LAW §1）**：**K=2000 虚拟起点**/cell（O-2230 N≥2000 逐字·全史均匀抽取·deterministic seed=SEED_STARTS·R3 再生律）；双腿 L/D 语义（P-5C 机械·import scripts/p5c_virtual_timepoint.py 口径禁重实现——19 员面自持 census：valid start=common_start+max lookback(104+20d)≤d≤cutoff−window）；窗 {6m,12m,24m} 全带（TRIAL_LABOR_LAW §3）。
- **政体分段（TRIAL_LABOR_LAW §3 律）**：bear/bull/chop 三段（T-22 §3 冻结 3-way proxy 逐字·import 禁重实现）+na 桶诚实。
- **双 nulls（RANDOM_LARGE_SAMPLE_LAW 判决面）**：block bootstrap **B=2000**（block=20 交易日循环块·拼样截回 n 长）+ sign-flip 置换 **P=2000**（逐日符号独立翻转·双侧）；rng 流仅限重采样面禁挪用（census §9.1 用途钉死先例）；**判线=skill_line_v2 数据自适应刻度**（μ_null+σ_null 由本批 null 族实读——非手挑阈）。
- **账本**：`science_gates.append_ledger("LOWAMP_P1", <distinct cells>, file, evidence_cutoff="2026-09-22")`（prev=活锚头实读禁手抄）；DSR n_trials=**累计账本总试验数**（活锚头实读·跨批不重置·TRIAL_LABOR_LAW §4）。
- **复跑纪律**：checkpoint 逐 cell append（kill-safe·R41）；工程修复重跑=双跑留痕零判据触碰（r493 三跑先例）。

## §4 判据【跑前写死——禁看结果调整；共享库引用零手抄】

- **G1' v2 = `science_gates.g1_prime_v2(sharpe_full, returns, batch_cells, pool="core48", n_trades, n_entries, null_pool=本批 null 族实读面)`**：全期 Sharpe>skill_line_v2（max(被动+0.10, μ_null+σ_null·√(2·ln N_eff))·**判决线由本批双 nulls 族经 null_pool 附加面校准**〔P4_EXT_TILT 附加面先例·数据自适应刻度·禁手抄阈〕·N_eff=活链头本批格数）**∧**平稳 bootstrap CI 下界>0 **∧** entries≥30（G6 双口径）；批报告逐列披露 skill_line/bootstrap_ci/trade_gate 全输入。
- **G2 注册资格 v2 = `science_gates.g2_registration_v2(g1_pass, dsr, pbo)`**：G1' 过线 **∧** DSR≥0.95（deflated_sharpe_ratio 原始收益跑·n_trials=累计账本总试验数活读）**∧** 审慎 PBO≤0.25（screening/pbo.py CSCV 8 块·**族=本批 501 cells**〔单族批·族内竞争网格〕·全史 base 面 Sharpe 向量；不足 8 等分=insufficient 如实→G2 不可过）；缺输入诚实拒收。
- **x2 生存**：x2 成本面判据面逐字稳定（G1' 各输入在 x2 面重算·全期+x2 双正）。
- **样本充足律**：n_eff≥100 起点 × bear/bull/chop 各 ≥100 起点窗（na 桶诚实）——不越→verdict=**insufficient-sample 禁判 pass**。
- **多重检验税披露（O-2245·护栏随 N 加码）**：E[FP]=0.05×501 如实披露（DSR≥0.95 门=多重检验校正门·通过者仍存活非否定面）。
- **s4 intake（上岗线·过线触发）**：G2 eligible 存活者 → **D6 绑定门**（对在册公判+存活者两两 max|corr|·日收益口径·≥0.7 拒收·簇内留 DSR 最高〔平手=最低 cell idx〕）→ STRATEGY_LIBRARY 注册行（evidence_cutoff+SIGNAL_BUILDERS 接线+smoke 锚定门复跑·模板 §8 律）+ **LOWAMP-* 纸盘提案**（快速通道律：prereg-only·GM 署名+激活下一交易日·O-2045 PROSPECT 机械复用观察车道）+ 决策链版本台账通道**第二活袖候选**注记 + **48h 内 CEO 呈报**（判决面落地起计）。**实际存活数按实际划（零存活=合法判决照报不翻案·判负=POTENTIAL_WATCHLIST 如实出名——CEO 令原文「判负如实出名」）**。

## §5 跑前预测【写死于跑前·对账用】

1. **去重率**：raw 501 → distinct ∈ [497, 501]（参数四元组空间窄·重复抽中率低；anchor 与抽样撞四元组概率 ≈28×2×2 分之一/抽·预期 ≤2 塌缩）。
2. **族一致面**：≥80% cells 全期 Sharpe>0（熔炉 top-20 全 +115%~+200%/Sharpe 0.95-1.17 族级证据·13bp 保守面预期缩水但正号保持）；全期 Sharpe 中位 ∈ [0.6, 1.2]。
3. **G1' 过线** ∈ [15, 300]（skill_line 数据自适应·null 族实读后定·族级强信号预期非零过线）；**G2 eligible ∈ [0, 3]——模态结局=近零**（DSR 按 333k+ 累计折减=极重校正·七批同门实证；零存活=合法产出）。
4. **方向先验（可证伪）**：低振幅选股（amp 升序取最低）LONG 面=仓内锚（IC 恒负+lowamp20 sign prior −）——若判决面系统性负号=熔炉面伪信号嫌疑·如实报不翻案。
5. **极端日先验（硬界三件套 c）**：窗内极端微观结构日（2024-02-05 微盘崩/2024-09-24/09-30 政策脉冲/2025-04-07 外生缺口/2026-01-19 极端量日等）在 19 员面在场真值——候选格尾部|日收益|>8% 层级=19 员 ETF 日频面结构性有限（宽基/行业 ETF 单日极限 ~±10%）·整窗判读+dd 线非单点 max 检测线。
6. **流动性闸**：50m 下限日缺位计数预期 0-偶发（19 员皆主流 ETF·历史早期窗（2020-03 起）部分小员可能触线——缺位计数如实披露·非 0 预期 [0, 500] cell·日）。

## §6 产物

- runner：`scripts/lowamp_p1.py`（subcommands: probe / judge / intake / status / selftest；engine/backtester import-face 复用禁重写·engine/exit_rules.py 零触碰；selftest=hermetic 合成面离线腿〔r116 律 B7b 合约腿+r297 律确定性双跑字节恒等腿〕+T+1 因果腿+流动性闸腿+invvol 权重归一腿+塌缩去重腿）。
- 产物：`results/lowamp_p1/`——manifest.json（探针+完备门读数）、cells.json（501 cells provenance+抽样审计+D6 披露列）、judge.json（判决全面 G1'/G2/DSR/PBO/E[FP]/null 族 floor/分段面/x2 面/流动性缺位计数·顶层 evidence_cutoff+cutoff_meta+audit 段）、checkpoint 逐 cell jsonl（kill-safe）、intake.json（s4 裁定·过线触发时产）。
- 池路由：judge 批 >5min 入池（O-2100）·lane_owner=null（in-repo 双机可跑）·workers_plan 26 workers BelowNormal（CPU 余量律）·checkpoint 断点续跑·**池条目必带 consumer_plan**（§0）。
- SEED_REGISTRY 三键（三步律撞带重取实录：初选 20308500/20308600/20308700 **撞带重取**〔20308500=t101_v4_a2 已占·r494 ast 实读 registry 148 键 20302000-20329500 全带连续占〕→重取新带 **20330000/20330500/20331000**〔max 20329500+500 自然推位·全仓 rg 零命中·ast 实读非旧含 CSV 巧合面〕；冻结合 commit 登记 R250 一步律）：`lowamp_p1_params`=**20330000**（Sobol 参数轴）·`lowamp_p1_starts`=**20330500**（K=2000 起点轴·派生 [20330500, cell_idx, leg]）·`lowamp_p1_nulls`=**20331000**（双 nulls·派生 [20331000, cell_idx]）。

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

（空）

## §8 批后复盘【必填·s7-T】

（空）
