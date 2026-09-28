# ETF-OPS-BP1 预注册（宽基回调低吸链全网格回测批）· T-103 s2

> 权威链：research/BACKTEST_SCIENCE.md（v2 判据唯一权威）＋ BACKTEST_PLAN.md 三铁律 ＋ research/COMPUTE_AUDIT.md（批件纪律）＋ PREREG_TEMPLATE.md（本件母板）。
> 法链：O-20260928-1524（ETF 操作链条建制令）→ O-20260928-1533（宽基收窄）→ O-20260928-1555（五员宇宙定谳+两线分治）→ O-20260928-1531（实时行情接入令·T-104 面，本批零实时依赖）。
> 设计源：research/etf_ops/ETF_OPS_S1_CHAIN_DESIGN.md（S1 §2 规则表=本件 §3 逐字源）；宇宙/对照臂=research/etf_ops/ETF_OPS_S0_CENSUS.md（冻结面）。
> 状态：**跑前冻结**（2026-09-28 R396 bm-b · 与 F-04 MSG-20260928-2000＋SEED_REGISTRY 登记同 commit）；跑后只许回填 §7 占位节，禁改判据禁重跑。

## §0 批件身份【跑前冻结】

- 批名 / 批号：**ETF-OPS-BP1**；批内格数=**30 member-cell**（5 员 × 6 cell：D∈{4%,5%} × (P1,P2)∈{(5,10),(6,12),(8,15)}%）——**每 member-cell 计入 N_eff，扩容即买单**；虚拟时点窗 {6m,12m,24m} 与成本面 {base,×2} =同格内披露/压测维度，非扩格。
- 认领：F-04 先行=`fleet/inbox/MSG-20260928-2000-bmb-all-etfops-bp1-prereg-freeze.md`＋任务单=`T-2026-09-28-103-P1`（s2·bm-b standing 认领 r391·progress_r394b 续作点②）。
- 部门归属：ETF 操作链条研究组（直属组·org_chart v2 新行）；轮报告标注 dept:研究/策略。
- 算力预算：runner=T-22 血统向量化 envelope（cn_kline_pattern_p1 范式），**五员可分片**（shard=member，多机多分片合法）；预估 3–8 min/员/worker（≤floor(16×0.8)=12 workers 合规）；>10min 批**一律后台化+跨轮 checkpoint+入池 results/runnable_pool.json**（R41 教训），轮内禁内联代跑；批报告必带 audit 段（无 audit 段的结果件不入账本）。

## §1 α 机制段【D6——无机制段=批不受理】

- [x] **行为偏差**：A 股散户追涨杀跌+处置效应（上涨捂不住、回调恐慌割）：上行趋势内的宽基回调触发集中恐慌抛售，低吸方在局部低点承接恐慌盘获得补偿；分层止盈=把「该止盈就止盈」纪律化，对抗盈利仓处置效应。**谁付钱**：趋势内恐慌止损盘在局部低点付出价差，追涨盘在反弹后为流动性付费。（S1 §1 逐字）
- 国内性主张（O-1522 方向盘）：「趋势不破回调低吸」=A 股原生大众打法（非国外动量/均值回归学术框架原样移植）；T-89 分段先验=宽基 chop 占比高（510300 实勘 71%），低吸型入场天然适配震荡主导形态——趋势上窗吃鱼身、chop 窗吃回归。
- **同族相关性准入检查（D6·冻结程序）**：对照清单=①在册 6 交易员 sleeve（COMPOSITE-CE-01/02、DROUGHT-CE-01、ENGULF-CE-01、NEEDLE-DE-01、VOLATILITY-CE-01·日收益序列口径）；②同批 30 cell=同族网格（族内相关由 **family PBO 门**承担，非 D6 拒收面）；③在队函数：T-104 GRID prereg（frozen 未跑·机制面互斥零重叠声明）、T-106 国家队 s3 事件复盘（判面非策略函数·零重叠）。**数值=跑批时 sleeve 日收益序列实测，§7 回填逐对披露**；任一 cell max|corr|≥0.7（vs ①）→ **该 cell 拒收**如实披露（防 N 膨胀放大 D1 校正负担）；判负族对照臂（CN-TREND-ETF 等）非在册函数不适用 D6，相关性读数随 §7 一并披露。

## §2 数据与面板【跑前探针事实·G-ANCHOR-FACE 四元组逐锚落格】

- 宇宙/池：**五员两档冻结宇宙**（O-1555）：510050（上证50·10cm）/ 510300（沪深300·10cm）/ 510500（中证500·10cm）/ 512100（中证1000·10cm）/ 588000（科创50·**20cm**）。
- **数据锚面定义四元组【每个数字探针锚必填·R99 冻结门】**（r396 探针 2026-09-28 19:56 实测，与 S0 §1 表逐一相等）：

| 员 | ①数据面路径 | ②加载函数 | ③起算窗 | ④预热窗 | 实测行数 | 末行日期 |
|---|---|---|---|---|---|---|
| 510050 | `data/daily/sh510050.csv` | `pd.read_csv` raw 直读截断（非引擎池面） | 2005-02-23 全史起算 | MA200 min_periods=200（max20d min_periods=20）→首有效 MA200 第 200 bar | 5248 | 2026-09-22 |
| 510300 | `data/daily/sh510300.csv` | 同上 | 2012-05-28 | 同上 | 3483 | 2026-09-22 |
| 510500 | `data/daily/sh510500.csv` | 同上 | 2013-03-15 | 同上 | 3286 | 2026-09-22 |
| 512100 | `data/daily/sh512100.csv` | 同上 | 2016-11-04 | 同上 | 2402 | 2026-09-22 |
| 588000 | `data/daily/sh588000.csv` | 同上 | 2020-11-16 | 同上 | 1422 | 2026-09-22 |

- **探针-锚同面断言【G-ANCHOR-FACE·必填】**：runner 探针实载路径与上表锚声明路径**逐位比对**——一面不相等=**面错配 VOID**（fail-closed 拒烧，报「面错配」非「数据腐坏」·INCIDENT-20260928 立法）。
- 窗口与 **evidence_cutoff（D2 前向锁盒）=2026-09-22**（qfq 五员面实测最新 complete bar）：cutoff 后新 bar（含 core48 面已有 09-24 bar 与 09-28 当日 bar）**锁定不得回流本批**；结果 JSON 顶层必带 `science_gates.cutoff_meta(evidence_cutoff="2026-09-22")`（缺字段=science_audit C2 VIOLATION）。
- **数据维护面如实披露（S0 §3.2 勘误入册）**：qfq 五员面当前**无刷新腿覆盖**——`data/fundamental/eligibility.csv` 11,628 行零 5 前缀码实证（update_astock_daily 宇宙=0/3/6 前缀股），S0 §3.2「qfq 全史面由 update_astock_daily 车道维护」宣称对五员不成立；本批 cutoff=09-22 锁盒合法且与判负族/trial-labor W4 同 cutoff 面一致；**五员 ETF 刷新腿缺口=票面改进指针**（候选工单，非本批阻塞）。
- 数据完备门（不过门禁烧）：每员①实测行数==四元组锚行数（5248/3483/3286/2402/1422 逐一相等）②末行日期==2026-09-22 ③OHLC 无 NaN ④date 单调递增无重复——任一不过=该员 fail-closed 禁烧，如实上报。

## §3 方法学【冻结】

- 信号定义（S1 §2 规则表逐字·全数值零酌情断点·每员独立实例）：
  - 趋势门：`close > MA200`（前 200 收盘均值，含当日）；
  - 触发门：`close ≤ max(close,20d) × (1−D)`，D∈{4%,5%}（网格）；
  - 入场：双门同日满足 ⇒ **T+1 次日开盘**买入一单位（每员单仓位·禁加码金字塔）；
  - 持有：`close > MA200` 且未触止盈/止损 ⇒ 继续持有；
  - TP1：`close ≥ entry_cost×(1+P1)` ⇒ T+1 开盘卖 50%；TP2：`close ≥ entry_cost×(1+P2)` ⇒ T+1 开盘清仓；(P1,P2)∈{(5%,10%),(6%,12%),(8%,15%)}（网格）；
  - 硬止损：`close ≤ entry_cost×0.92`（−8% 公司正典同门）⇒ T+1 开盘清仓；趋势止损：`close < MA200` ⇒ T+1 开盘清仓；
  - 回合=入场到清仓一单位；TP1 后余仓同 entry_cost 计价（成本基准=入场成交价加权）；胜负=回合净盈亏（含双边成本）>0；再入场=回合关闭后重回等双门状态（**同日不重入**）。
  - 涨跌停诚实记账：入场日开盘一字涨停（10cm/20cm 档口径）=不可成交记 `blocked_entry` 不入胜率分母；出场日一字跌停记 `blocked_exit` 次日续执行；
  - 基金事件守卫（r239 冻结律逐字）：单日 `|r1|>10.5%`（588000 用 20.5%）且当日宇宙中位 `|r1|<3%` ⇒ 该员该日隔离不触发；
  - 588000=20cm 档（涨跌停阈 20% 口径，分层披露标签非参数分裂）。
- 滞后规则：全部信号用**收盘价可算量**，披露时点=当日收盘后，执行=T+1 开盘（O-1132 保守代理）——禁未来数据；因果律探针=truncate-and-compare（smoke 先例）跑批自证。
- null 对照：**K=200 同掩码随机入场 null/员-cell**（同出场纪律、同持有规则、随机等量触发日）；**seed 基=`etf_ops_bp1`=`20294000`**（30 流 `default_rng([20294000, cell_idx])`·cell_idx<30·K=200 sequential draws/stream；SEED_REGISTRY 本冻结同 commit 登记·R250 律；band 20294000..20294029·rg 全仓扫描零命中）；被动基线=逐员 buy-hold 同窗。
- 成本口径：**V1 legacy 13bp×2 双轨**（base x1 ＋ ×2 压测面照跑——S1 §2 冻结；×2=CostPatch multiplier 律·禁直引常量另算）。
- 账本：`science_gates.append_ledger("ETF_OPS_BP1", batch_trials=30, file_name, evidence_cutoff="2026-09-22")`（dict schema 唯一·禁手抄 prev）。

## §4 判据【跑前写死·禁看结果调线】

- **链条主判（业务 KPI·O-1524 §一.4）=交易级胜率** `wins/n_rounds`（盈利回合占比·含双边成本·逐员-cell 披露）；**胜率科学闸=实测胜率 > 同员-cell K=200 null p95（单侧）**——不过=「低吸有技巧」不成立；回合期望 E[round_pnl] 同 null 同门并行披露。
- **G1' v2（注册资格·公司正典）**=`science_gates.g1_prime_v2(sharpe_full, returns, batch_cells=30, n_trades, n_entries)`：全期 Sharpe>skill_line_v2（数据驱动=max(被动+0.10, μ_null+σ_null·√(2·ln N_eff))）且平稳 bootstrap CI 下界>0 且 entries≥30（F6 双口径，(entries_ok) 为准）；批报告逐列披露 skill_line/bootstrap_ci/trade_gate 全输入。
- **G2 注册资格 v2**=`science_gates.g2_registration_v2(g1_pass, dsr, pbo)`：G1' 过线且 DSR≥0.95（`deflated_sharpe_ratio` 原始收益跑）且**家族 PBO≤0.25**（`screening/pbo.py` CSCV 8 块·30 cell 同族）；缺输入=诚实拒收。
- 三披露并行（禁单指标叙事）：盈亏比 `avg_win/avg_loss`／回合期望／**beat-passive**（同窗同员 buy-hold 总收益 vs 链条费用后总收益——CN-CORE-SATELLITE 教训：增量真实≠量级够）。
- 政体条件化有效窗披露（O-1518 T1）：按 T-74 L2 路由态（GREEN/CHOP/ORANGE/RED·YELLOW→CHOP）与 T-89 分段（trend/chop）分层披露胜率——**禁全天候宣称**。
- 描述条款（批级·不替代门）：年化>0、OOS 双正、回撤≥−35%、无崩年、成本×2 逐年稳定。
- 硬界设计三件套适用面声明：本批=回合制批**无 max 硬界检测判线**；三件套落位=①极端日先验入 §5（一字板记账=事件豁免路径，blocked_entry/blocked_exit 逐日单列披露）②基金事件守卫隔离日单列③危机日（|r1| 双面）命中记日志豁免单列。

## §5 跑前预测【写死于跑前·跑后对账】

1. **胜率方向**：(P1,P2)=(5,10)% 组胜率最高（小目标易达·预测 55%–70%），(8,15)% 组最低（预测 40%–55%）；全批 30 cell 胜率整体区间预测 **40%–70%**（宽基 chop 占比 71% 形态=小赢面为主）。
2. **D 参数**：D=5% 比 D=4% 触发更少更深（恐慌盘补偿更足），回合数预测 −20%~−35%、单回合期望更高，两者胜率差 <5pp。
3. **null 对照**：同掩码随机入场 null 胜率中位预测 ~45%–50%（宽基日频正漂移+同一出场纪律抬 null 底）——链条主张成立面=实测胜率显著过 null p95，非绝对值高。
4. **极端日先验（硬界三件套(c)）**：①2015-06/07 股灾窗（510050/510300 主战场）连续一字跌停=`blocked_exit` 高发（−8% 硬止损跌停队列不可成交→次日续执行，实际损耗深于 −8%）；②2016-01 熔断 4 日同形态；③2024-09-24~10-08 政策脉冲窗单日 +8%~+10% 涨停=TP 触发日开盘一字涨出场不可成交=`blocked_exit` 次日续卖（止盈被「免费升级」）；④2026-01-19 极端溢价日（D-C 批实证形态）588000 20cm 带高发；⑤基金事件守卫隔离窗（510500 2022-08-29 −12.7% 实勘在案）逐日单列。
5. **beat-passive**：链条优势主要来自 MA200 下空仓避险段（2022–2024 熊段）；chop 段预期小输被动（whipsaw）——**全年候跑赢被动不保证**，政体分层是关键披露面。

## §6 产物

- script：`scripts/etf_ops_bp1.py`（T-22 血统向量化·五员可分片·G-ANCHOR-FACE 同面断言内建·checkpoint 断点续跑·虚拟时点窗 {6m,12m,24m}×成本面 {base,×2}）。
- results：`results/etf_ops/bp1_grid.json`（顶层 `evidence_cutoff="2026-09-22"`＋`science_gates.cutoff_meta` 必带）＋`results/etf_ops/bp1_rounds_<member>.csv` 逐员回合流＋null 分布件。
- 本件 §7 回填。

## §7 跑后实证【2026-09-28 R397 bm-b 回填·judged face=x2·产物=results/etf_ops/bp1_grid.json+bp1_nulls.json+bp1_rounds_<code>.csv·ledger 317,859→317,889】

- 逐员-cell 胜率/回合数/盈亏比/期望/beat-passive：**胜率区间 22.2%–60.0%**（510050 46.8–60.0 / 510300 25.0–43.3 / 510500 46.4–52.3 / 512100 42.3–57.9 / 588000 22.2–31.6）；回合数 16–58/cell（全批 900 回合）；beat-passive 全窗 **0/30**（链条累计最高 +2.2% vs 同窗被动最高 +89%，CN-CORE-SATELLITE 教训面再现：高胜率≠赢被动）；盈亏比/回合期望逐 cell 载 bp1_grid.json descriptive 节。
- null p95 读数与胜率过闸面：同掩码随机入场 null p95（x2）=50.0%–85.7%；**实测胜率 > null p95 = 0/30——主判全批不过**，「低吸有技巧」在「贪心首触发日入场」口径下不成立：随机取同掩码触发日的入场胜率系统性更高（早接飞刀劣于随机深处承接，588000 20cm 面最显著 22–32% vs null p95 56–67%）。
- G1'/G2 判定与 skill_line_v2/bootstrap_ci/trade_gate 全输入：**G2 eligible 2/30**（510300-D5-P612、512100 高 Sharpe cell：G1'v2 线+CI 双过、DSR≥0.95、PBO≤0.25）但两者均败主判 → **综合注册 0**；全输入（skill_line/bootstrap_ci/trade_gate/dsr/pbo）逐 cell 载 bp1_grid.json gates 节（判线=共享库实算零手抄）。
- D6 同族相关性逐对读数：30 cell vs 在册 6 sleeve max|corr| 全部 <0.7（**0/30 拒收**；回合制链与恒在场 sleeve 结构性解耦，逐对读数载 bp1_grid.json d6 节）。
- 政体/分段分层胜率面：逐 cell by_route_state（regime_deep_replay v3·L2 映射）+ by_t89_segment（bear/chop/bull）载 bp1_grid.json regime_face 节——分层读数如实、无全天候宣称。
- blocked_entry/blocked_exit/基金事件隔离日逐日单列：blocked_entries/open_at_end/blocked_exit_rolls 逐员载 bp1_grid.json blocked_accounting 节+bp1_rounds_<code>.csv 逐回合列；隔离日=mask 构造面排除（5 员面隔离日计数入 shard face）。
- 预测对账（对/部分/错）：§5.1 胜率方向**部分对**（P510 组 3/5 员最高、P815 组 3/5 员最低；区间 40–70% 预测对 4/5 员，588000 22–32% 出带=预测错）；§5.2 D5 回合数更少**对**（mask −23~−24%、回合 −9~−40%），胜率差<5pp 510050 对/510500 错=**部分对**；§5.3 null 中位 ~45–50% 方向对（p50 面载 bp1_nulls.json）；§5.4 极端日先验 blocked 路径实证在册（2015 股灾/2024-09 脉冲窗 blocked_exit 次日续卖逐回合 rolls 列）；§5.5 beat-passive 不保证**对**（0/30，MA200 空仓避险未跑赢 whipsaw+成本）。
- **批判定：judged negative 族**——宽基回调低吸链（贪心首触发日+分层止盈+双止损）在五员两档全网格 30 cell 上主判全败，无注册无锦标赛臂；族教训=触发条件本身（回调幅度 D）不含独立技巧增量，出场纪律（MA200/−8%/分层 TP）是该链唯一可能有价值的部件面（2 个高 Sharpe cell 佐证），后续候选方向=出场纪律移植试验（新预注册），非本批复跑。

## §8 批后复盘【s7-T】

- 预测对账＋门禁链损耗账（`results/gate_attrition.json` 追加一行）＋判线 v2 当批读数（skill_line_v2 数字）；
- 回执入轮报告＋CODELY.md 行级追加；若注册新员：注册件带 evidence_cutoff＋live/paper SIGNAL_BUILDERS 接线＋smoke 锚定门复跑；
- 三出口（O-1524 §3）：锦标赛臂候选（DECISION_CHAIN v1.2）／军团席位供给／现金腿升级提案——judged negatives 记族教训。
