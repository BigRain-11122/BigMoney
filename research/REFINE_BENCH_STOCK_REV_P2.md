# REFINE_BENCH_STOCK_REV_P2 · 股票面 REV 族 stage-B 判决批（普查升格全量判决）

- 票：T-2026-10-01-139-P1 family-1（CEO 直令 O-2026-10-01-1035「股票呢？不要光走ETF」·点火令 O-20261001-1332 §一.1「bm-a 立即预注册+点火 p1c_stock 主炉」）
- 法源链：TRIAL_LABOR_LAW §4（廉价初筛先行→存活者全量判决）+ stage-A prereg §4 升格规则（烧前冻结）+ REFINE_BENCH_LAW v1.0 §2 + RANDOM_LARGE_SAMPLE_LAW v1.0 全律绑定 + O-1901 意义门四闸
- 批性质：**judged 判决批**——升格面=census top10_independent（勘探排序产物），批内零选优；升格判据与名单在 stage-A prereg §4 烧前冻结，本批零改动
- 引擎复用律：面板/宇宙/信号步进/成本/出场机制=rev_osc_stock_p1（RV）逐字 import；轴向参数化（深度阈/流动性地板/出场参数对）=refine_bench_rev_census（CE）逐字 import；判据/DSR/账本=science_gates 共享库；家族 PBO=screening.pbo.cscv_pbo——**零重实现**

## §0 批件身份

- 批名：REFINE_BENCH_STOCK_REV_P2 · 批号格数 N_eff=**2020**（10 胞 × 2 成本面 = 20 + 2000 nulls；每格计入 N_eff）
- 认领：T-2026-10-01-139 已由 bm-a 认领（11:02:30·r511 CEO immediate 律）；本批=该票 family-1 的 stage-B 段
- 部门归属：dept:研究+策略
- 算力预算：est 单分片 2-5min 墙钟（5 胞×2 面×~10-15s/面，ProcessPool workers=min(cap,6)·BelowNormal）；nulls 分片 est 15-35min（2000 事件×10 股×H20 sim，20 块×100 并行）；RAM floor 16GB fail-closed exit 3（~8GB/工人护栏）；**>5min 算力批一律入池（O-20260924-2100 执行面分离）**，轮专注预注册/判定/接线
- 池登记：3 单元=SHARD-0（胞 0-4 双面）+SHARD-1（胞 5-9 双面）+NULLS（20 块×100）；finalize=轮会话工作（LOWAMP-P2 同式，不占池面）；核分布行随轮报告

## §0.5 禁开方向硬闸【D-20260930-41 §1.2】

- 命中编号：**BAN-04**（Grid trading/网格交易族——正文 §5「确定性网格扫描零 RNG」与 §1「普查排序」面的枚举术语字面命中）
- 例外类型：**new_data**
- **原否证不可能看见**：不可能看见——BAN-04 的原证伪面=ETF 网格触发交易族（GRID-SLEEVE：价格触发带×挂单梯机械，engine 层触发结构）；本批=股票超跌反弹事件 cohort 族·纯时间止 H=20·零触发带零挂单梯（出场轴=策略自有时间止·selftest leg2 出场标签只许 {time, tail}），正文的「网格扫描」=stage-A 普查的参数组合枚举术语（240 胞轴带一次性测量）非交易机制——原证伪构造上看不见本批的深跌阈值全格池×H20 慢窗×流动性地板新数据面（判决批 7 胞=Top10-H7/H10-yang/TPSL，从未测过）。
- 跑前过闸记录：`python Tools/banned_direction_gate.py --prereg research/REFINE_BENCH_STOCK_REV_P2.md` → 冻结 commit 内回执（首跑 REJECT=BAN-04 字面命中·按 missing_fields 补齐三件套本节后复跑 ADMIT·r494 律）

## §1 α 机制段【D6】

- [x] **行为偏差**：过度反应修正×处置效应——20 日深度跌幅池（−15%/−25% 全格阈值面，非仅 Top10）=散户恐慌性抛售终点，短期反转溢价；H=20 持有窗=捕获慢速均值回归（普查面实证 H20 角落在全带系统性最优——Top10/H7 判决面漏测的持有期维度）；付出代价方=恐慌割肉的处置效应散户与被迫平仓杠杆盘（REV_OSC_STOCK_P1 §1 同源论证，个股事件族先验）。
- **散户凭什么赢【§1.2·D-20260930-41】**：**行为**——散户赢在不跟随恐慌（在 −15%/−25% 深跌位接处置效应盘的对手方）+H20 慢窗持有无速度/数据/容量依赖；制度面 T+1 保守代理如实披露（不依赖盘中速度）。行为五选=行为（反身性对手盘），无机构已验证结论引用面、无 RETAIL_QUANT_TRACK DATA_GAP 消费。
- **同族相关性准入检查【必填·D6】**：①批内 10 形逐对日收益相关=stage-A 旁证 results/refine_bench_stock/rev_census/d6_top10_corr.json（max|corr| 0.8856-1.0——**同族轴向变体高内部相关如实披露**，独立性=结构独立〔同 depth-entry-liq 只取最优 exit×H 形·stage-A §4 规则〕非收益流独立；家族 PBO 面将如实承载该选优不稳定风险）；②vs 在册 6 CE 成员（cn_rev_tilt REG6 canon）逐对 max|corr| in-runner 实测（RV.d6_block 逐字，≥0.7 拒收；族先验 0.11-0.19〔REV_OSC_STOCK_P1 §7 实测〕预期 <0.35）；③vs 判决批 7 胞=不同面（本批 10 形 anchor_judged 全 false·升格名单与 REV_OSC 7 胞零重合·runner 冻结断言）。

## §2 数据与面板【跑前探针事实】

- **面板=P1C-StageA 股票缓存**：T=8792（1990-12-19..2026-09-22）×N=5222，float32，qfq；**cutoff=2026-09-22（D2 前向锁盒）**——`RV.load_panel` 逐字（含全部 fail-closed 门：shape/dates 锁盒/sse 覆盖≥0.97/ok_static=3517/宇宙中位双面哨兵 150∧500）。幸存者偏差=cache 为在建市快照（REV_OSC_STOCK_P1 同批先例披露）。
- **数据锚面定义四元组【G-ANCHOR-FACE】**：
  - 面板：`Money02/data/cache/p1c_stock` + `rev_osc_stock_p1.load_panel` + 1990-12-19 全史起算 + amt20 min_periods=20（20 bar 预热）；
  - 上证政体面：`Money02/data/index/sse.parquet` + `pd.read_parquet→reindex ffill 桥` + 1990-12-19 + MA200 min_periods=200；
  - B 层掩码：`data/fundamental/b_layer_mask.csv` + `pd.read_csv(dtype code str)` + as-of 静态快照 + —（无预热窗）；
  - 结果 JSON 顶层 `science_gates.cutoff_meta('2026-09-22')` 必带（缺=C2 VIOLATION）。
- **探针-锚同面断言**：runner probe 载入路径与上述声明逐位同源（同一 import 面）；探针产物 results/refine_bench_stock/rev_p2/probe.json（面板锁盒+升格名单冻结断言+closed-family 记录+seed 登记）——烧录子命令 fail-closed 要求 probe.json 在场。
- **数据完备门（不过即拒批 exit 2）**：RV.load_panel 全门 + 升格名单冻结断言（P2_CELLS 字面量==census_ranking.json top10_independent 逐位 + anchor_judged 全 false + entries≥500）。

## §3 方法学【冻结】

- **升格名单（stage-A §4 规则产物·零改动）**：D-15|raw|base|time|h20 · Dtop10|raw|base|time|h20 · D-25|raw|base|time|h20 · D-15|yang|base|time|h20 · D-25|yang|base|time|h20 · Dtop10|yang|base|time|h20 · D-15|raw|liq2|time|h20 · D-25|raw|liq2|time|h20 · Dtop10|raw|liq2|time|h20 · D-15|yang|liq2|time|h20（全部 exit=time、H=20、BG 闸恒开〔族语境·无门 BASE 面已判决不重烧〕、等权）。
- **信号（qfq 面）**：drop20=close[t]/close[t−20]−1（RV 同式）；深度阈=合格池内 drop20≤−15%/−25% 全格面（Dtop10=无阈 Top10 判决面同式）；首阳=close[t]>open[t]（yang 腿）；流动性地板 base amt20≥5e7（宇宙门自带）/liq2 amt20≥2e8（CE._pick_axis 逐字）。
- **入场（T+1 开盘保守代理 O-1132）**：t+1 开盘价入场，近涨停开盘不成交（un-captured premium 计数披露）——CE._sim_axis/RV.sim_stock 机制逐字。
- **出场轴声明【O-20261001-1108 显式门·三选一之①】**：**策略自有出场=纯时间止 H=20**（t+1+H 开盘出；停牌/跌停顺延 wild_route 律；tp=None/sl=None——**引擎缺省出场栈零构造零消费**，judged 面不触碰 engine/exit_rules.py；selftest leg2 出场标签只许 {time, tail}）；全 10 胞同轴无变体。
- **仓位与桶**：等权 1/10；2 资金桶 bucket accounting（cohort 净收益按持有日数均摊·桶空闲日=0）；信号步进=每 5 交易日（grid_from=60 确定性 offset）——RV.signal_grid 逐字。
- **null 对照（RANDOM_LARGE_SAMPLE_LAW §3）**：K=2000 same-mask 随机事件日（随机信号日×随机合格 10 只·BASE 机械无闸无过滤·seed=SEED_REGISTRY['refine_bench_rev_p2']=**20263300**+k k<2000〔band 20263300..20265299，坐落 rev_osc_stock_p1 真实带顶 20263229 之上〕；**H=20 时间出面与批面同构**——REV_OSC 的 H=7 null 族稀疏年序列高散布（σ_null 2.72）线位高族构成面，本批 H=20 null 族 cohort 密度高一个量级=结构差异如实披露，线不可跨批评判）→ 2000 件合成 52-cohort 年化 Sharpe（phase-2 rng(20263300+k) 二次声明用·RV.run_nulls 配方逐字）；双法并列：block bootstrap 2000 draws（块长 10）+ sign-flip permutation 2000 draws（RV.robust_stats 逐字）。被动基线=stock_b_layer 注册池活读（pool='stock_b_layer'）。
- **成本口径声明【CN-C7】**：**V1 legacy 股票日程 13.041bp/边（往返 26.082bp）**=P4_BATCH2 §3.2 冻结锚（RV.COST_X1 单源 import 零手抄）；前缀路由=`knowledge/rules.py fee_schedule_for`（佣金 2.5bp min ¥5/印花税仅卖边 5bp/过户费双边 0.1bp/经手 0.341bp/证管 0.2bp+滑点 10bp=13.041bp/边冻结值）；x1=判决面、x2=压测描述列（26.082bp/边）；¥5 最低佣金临界=名义 ¥20,000（cohort 等权面沿用 V1 冻结口径披露）。
- **账本**：`science_gates.append_ledger('REFINE_BENCH_STOCK_REV_P2', 2020, 'refine_bench_rev_p2', evidence_cutoff='2026-09-22')`（dict schema 唯一禁手抄 prev；r259 prev-echo 守卫同 RV）。
- **闭合族对号声明【M3·D-20260930-37】**：family_key=**rev_osc_stock**——`science_gates.CLOSED_FAMILIES` **不在册=open 照跑**（机械检查 probe.json 记录）；诚实注记：REV_OSC_STOCK_P1 判负（G1'v2 0/7+G2 0/7·slot closed per O-2325 §5 禁翻案）——本批=**新证据新预注册通道**：新证据增量=stage-A 240 胞普查发现的深度阈值池/H20 慢窗/liq2 地板三轴带（判决批 7 胞全部为 Top10-H7/H10-yang/TPSL 面，深度阈值全格池与 H20 持有窗从未测过；普查面 sharpe 0.28-1.155 vs 判决批最优 0.383——升格判据烧前冻结非结果驱动翻案）。
- **虚拟起点面（RANDOM_LARGE_SAMPLE_LAW §2.1）**：RV.virtual_starts 逐字——全部合法起点 [200, T−126] 每 126 交易日窗 vs 合格池 EW 代理；分段 4 类（bull/bear/deep-bear/chop）逐列；<500 起点段=insufficient-sample 如实注记；随机分窗 ≥100（seed 同基）+ walk-forward 5 折双证。
- **M1 t 面申报【D-20260930-37·必填】**：策略面无直接 t→`science_gates.t_from_sharpe(sharpe_annualized, n_periods=8792)` 派生 + `m1_t_value_gate(t, 3.0)`（Harvey/Liu/Zhu 多重检验门槛）逐胞入结果件（t 面=申报披露面，判负判胜主判据仍=§4 v2 门）。

## §4 判据【跑前写死，禁看结果调线】

- **G1' v2 = `science_gates.g1_prime_v2(sharpe_full, returns, batch_cells=2020, n_trades, n_entries, pool='stock_b_layer', null_pool=<本批 2000 nulls>, n_eff_override=<账本头+2020>)`**：全期 Sharpe > skill_line_v2（数据驱动=max(被动+0.10, μ_null+σ_null·√(2·ln N_eff))——H=20 null 族结构差异见 §3 披露）且平稳 bootstrap CI 下界>0 且 entries≥30（F6 双口径）；逐列披露 skill_line/bootstrap_ci/trade_gate 全输入。
- **G2 = `science_gates.g2_registration_v2(g1_pass, dsr, pbo)`**：DSR≥0.95（`deflated_sharpe_ratio` 原始日序列·n_trials=账本累计）∧ 家族 PBO≤0.25（`screening/pbo.cscv_pbo` CSCV-8·10 胞家族矩阵——批内高相关（§1 d6_top10_corr 0.886-1.0）×族内选优=PBO 面将如实承载该风险）。
- **硬界三件套【D-20260925-01①】**：(a) 分布界（median/p99.9）主责（RV.cell_stats 逐字）；(b) max 硬界 |r_day|>15%=危机日志豁免单列（RV.crisis_face 逐字·2015-06/07、2016-01、2024-01/02、2024-09/10 预期危机窗）；(c) 极端日先验见 §5.5。
- 描述性条款（批级披露不替代 v2 门）：年化>0、OOS 双正（虚拟起点前后半）、回撤≥−35%、无崩年、x2 成本压测逐年稳定。
- 判负=slot closed+新证据新预注册重开律注记（O-2325 §5）；判负真关线禁保满载续烧（O-1901 ②）。

## §5 跑前预测【写死于跑前】

1. **x1 面读数=census 面逐位复现**（同引擎同成本同桶账：确定性网格扫描零 RNG——D-15|raw|base|time|h20 sharpe_full 预期 1.1551、D-15|yang|liq2|time|h20 预期 0.2805、entries 4363-4464 带）；x2 面≈x1 减本批额外 13.041bp/边拖累（H20 年 cohort 数~126→年换手拖累估 Sharpe −0.15~−0.35）。
2. **G1'v2 判负概率 55-80%**：skill_line=数据驱动双面取大——被动项 stock_b_layer 活读（REV_OSC 批 0.4606+0.10=0.5606 先例）vs H=20 null 族 μ+σ√(2ln(账本头+2020))；**H=20 null 族 σ_null 方向低于 REV_OSC H=7 族（2.72）一个量级带**（cohort 密度↑→年序列散布↓→线位↓），本批最优 1.1551>0.5606=股票面首批被动项真竞争批；bootstrap CI：最优两胞下界>0 概率~50-70%（点 1.13-1.16·REV_OSC BASE 先例点 0.38 CI [−0.008,0.745] 外推）；honest 风险置顶：**线位不确定度主要由 null 族 σ 面构成**。
3. **G2 0/10 概率>90%**：DSR 在 n_trials≈账本头（~19 万）下逼近 0（REV_OSC 先例 0-0.0125）；家族 PBO 预期 0.3-0.6（批内相关 0.886-1.0×10 胞选优面——d6_top10_corr 旁证）——族内选优不稳定如实披露。
4. **deep-bear 分段 beat 族条件效应预期持续**（REV_OSC §7 先例 0.5481-0.6220 全分段最高）：H20 慢窗面预期 0.50-0.65 带；全史 beat6m≈0.44-0.48 随机带（若显著>0.5=预测 MISS 方向利好如实报）。
5. **极端日先验（三件套 (c)）**：2015-06/07 千股跌停/停牌簇（出场顺延激增）、2016-01 熔断、2024-02 微盘流动性塌陷、2024-09/10 暴力反弹涨停开盘拒单簇——10 只集中组合单日限位叠加 |r| 可合法击穿 15%，全走豁免单列禁整批判负（REV_OSC 先例零击穿·p999≤3.95%——本批 H20 面预期同量级）。
6. **回撤描述线**：普查面 max_dd −0.74~−0.88 → 描述线 −35% 预期 10/10 全破（描述面如实披露不替代 v2 门）。

## §6 产物

- script: scripts/refine_bench_rev_p2.py（probe | run --shard {0,1} --of 2 | run --nulls | run --finalize | selftest；per-cell-face checkpoint 幂等=在场即 done；fail-closed exit 2；RAM floor exit 3；worker 侧 claim 握手 r497 三调用点=烧录/幂等 no-op 同律，runner+握手同 commit）
- results/refine_bench_stock/rev_p2/：probe.json + cells/（20 件 checkpoint json+npy）+ nulls/chunk-00..19.json + nulls_pool.json + shard-{0,1}of2.audit.json（核分布行）+ p2_results.json（顶层 evidence_cutoff+cutoff_meta+20 面全量+nulls+D6+虚拟起点+robust+crisis+family_pbo+gates+M1 t 面+closed_family+账本）+ cells_summary.csv
- 本文件 §7/§8 跑后回填（finalize 后一次定稿）；ledger 单次 finalize（append_ledger prev_total 守卫）；语法登记=TRIAL_GRAMMAR_LEDGER 两行（stage-A 普查 240 胞补记〔r512 §7 尾巴·勘探面零判负语义〕+本批判决 10 胞×2 面+2000 nulls）
- 消费面：千人题库股票语法首批候选 + REV-OSC 淬炼供给 + 判决台账（stage-A §4 预期消耗面）+ CEO O-1332 算力饱和面（runnable-work-idle-low-cpu 红旗的合法工作面）

## §7 跑后实证【跑前为空——写数字即造假】

（finalize 2026-10-01 15:12 bm-a 一次定稿回填·源=results/refine_bench_stock/rev_p2/p2_results.json·ledger 382239→384259）

- **确定性复现**：D-15|raw|base x1 sharpe 1.1551=census 逐位 ✓；entries 4457（4363-4464 带 ✓）；D-15|yang|liq2 0.2805 逐位 ✓；x2 拖累 top 胞 −0.2141（1.1551→0.9410，带 −0.15~−0.35 ✓）。
- **G1'v2：0/10 全 line_ok=False**。line=max(passive 0.5606, null_term **24.1017**)=24.1017；n_eff=**384259**（集团累计试验深度）；μ_null=−0.2112，**σ_null=4.7942**；最优 1.1551≪线位。
- **M1 t-face 8/10 过**（t 3.41~6.82；D-15|yang|liq2 t=1.66 挂）。**Bootstrap CI 下界>0 9/10**（top 三胞 0.754~0.778；唯 D-15|yang|liq2 [−0.108, 0.637] 挂）。
- **DSR 0.0013~0.9941**（raw|base 三胞 ≥0.990；yang|liq2 尾 0.0013）；**G2 eligible 0/10**（G1 腿串联）。
- **family PBO=0.0**（omega_mean 0.0，register_eligible 面，70 组合×8 块）；**D6 reject 0/10**。
- **beat 面**（D-15|raw|base，8466 虚拟时点）：全史 beat_rate_6m=**0.5191**；分段 bull 0.4923 / bear 0.5511 / **deep_bear 0.6276**（n=717）。
- **max_dd −0.737~−0.889 全 10 胞**（−35% 描述线 10/10 破）；p999 |r| 2.93%~3.56%，极端日危机表全空（零击穿）。

## §8 批后复盘【s7-T】

- **§5.1 HIT**：census 逐位复现+x2 拖累带内。
- **§5.2 方向 HIT/σ 面 MISS**：0/10 判负落在 55-80% 预测带内；但 σ_null 预测（H=20 族低于 H=7 族 2.72 一个量级）**反向 MISS——实测 4.7942 不降反升**（cohort 密度↑→散布↓的直觉对慢窗不成立：低频大 cohort=年序列散布升）；「线位不确定度由 σ 面构成」的 honest 置顶预判兑现=本批判决主轴；CI 下界>0 实测 9/10 vs 预测概率 50-70%（利好向）。
- **§5.3 G2 0/10 HIT**（>90% 预测）；**PBO MISS 利好向**（0.0 vs 0.3-0.6，族内选优稳定）；**DSR 面 MISS**（raw|base 0.990+ vs 预测→0：8792 日长序列 sigma_sr=0.0101 使 DSR 对 384k trial 通缩不敏感——DSR 与 skill-line 两腿在长序列×高 σ_null 族面的分歧如实记录，不改任何判线）。
- **§5.4 分段 HIT/全史 MISS 利好向**：deep_bear 0.6276 落 0.50-0.65 带（REV_OSC §7 先例持续性确认，族条件效应非均匀 bear>bull）；全史 0.5191 出 0.44-0.48 带上照报。
- **§5.5 HIT**：零击穿（p999≤3.56%<15%）。**§5.6 HIT**：10/10 破 −35% 描述线。
- **门禁链损耗账**：ledger 382239→384259（+2020 单次 finalize prev_total 守卫 ✓）；gate_attrition 行已落（g1_pass 0/10 / g2_eligible 0/10 / d6_reject 0/10 / family_pbo 0.0）。
- **skill_line 当批判读**：判决完全由 null 族 σ 面构成——被动项 0.5606 从未进入竞争（null_term 24.10 主导）；√(2ln 384259)≈5.07 × σ_null 4.79 ⇒ 线位 24.1；t=6.8 的点估计强度与线位间鸿沟=集团级多重检验税的诚实代价；重开唯一路径=新证据注记（O-2325 s5）。
- **全起点分布**：8466 虚拟时点（bull 2415/bear 3170/deep_bear 717/chop 2164）。
- **试验量归因**：2020 格=10 胞×2 成本面（20）+2000 同掩码 null；点火源=CEO 直令 O-1035（股票炉）/O-1332（P1c 面板）链。
- **判负处置**：槽位关闭+族保持 open（closed_family status=open·不在 registry）；判负=真关线（O-1901）禁保满载续烧；E1 三腿对账未跑（判负面零消费不阻塞；未来若消费本批任何数字须先过 r492/r301 三腿）。
