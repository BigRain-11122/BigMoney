# FUND-QUALITY-P2 预注册【DRAFT-NOT-FROZEN·r1087 开批票】· 质量族复活批（质量定义邻域＋参数邻域＋出场轴）

> **状态=冻结窗进行中（r1087 bm-a）**：本件 r1087 开立。已完成=禁向闸 ADMIT（§0.5）＋数据可达性六腿探针全绿（`results/_fund_quality_p2_freeze_probe.json`·2026-10-20T08:18:47+08:00·selftest 全 PASS）＋种子带 SEED_REGISTRY 登记（20517500/20518000·probe leg5 实弹扫描零碰撞）＋§2 四元组锚定＋§3 三腿规格写死＋§5 预测定稿。**余项=runner 落地（`scripts/fund_quality_p2_backtest.py`·承 P1 runner 骨架 import 复用）→ 跑齐后 commit 冻结；冻结前禁烧。** §7/§8 占位纪律（写数字即造假）。
> 模板=`research/PREREG_TEMPLATE.md`（T-02 6/7）；判据权威=`research/BACKTEST_SCIENCE.md` v2＋共享库 `scripts/science_gates.py`（禁手抄判线）。
> **CEO 判负线复活授权（O-20261019-2230-bm-b §二.2·三件律：本授权+新预注册+新证据）**：承 FUND-QUALITY-P1 判决（headline skill 0.33 无条件面·2026-10-14 在册·sharpe_full **−0.318** 强负），新证据三腿=①质量定义邻域（ROE 水平-only vs ROE 水平×稳定性复合——P1 只判 ROE 水平单定义）②Top-N 参数邻域（邻域稳健性=P2 判负面主判据）③出场轴优化（P1=②持有到底；P2 显式声明①策略自有出场族）。防运气门不拆（技能线/DSR/PBO/种子登记/预注册冻结全照旧）。
> 血统：FUND-QUALITY-P1.md（股票横截面月频族·bm-b r599 冻结·N_eff 2,002）＋ CEO 研究导向律合规（质量=国内原生主流风格打法之一，形式化非国外框架筛国内打法）。
> **与 FUND-DIVLOWVOL-P2 的关系（防重复开发律）**：DIVLOWVOL-P2 以 PIT ROE 作**过滤器**（红利 carry 的现金流确定性）——本批以 ROE 作**排序信号本体**；两者机制面不同（过滤 vs 排序），数据面共用 `quality_faces.parquet`（同一导出面·零重复采集）。R3 裁决见 §1 同族相关性准入。

## §0 批件身份【跑前·冻结窗定稿】
- 批名/批号：**FUND-QUALITY-P2**（批内格数 **N_eff=2,020 定稿**：judged 策略格 20（主判 2＋N 邻域 8＋定义邻域 4＋出场 6）×成本 face 计入＋K=2000 null 族）。
- 算力预算：长活入池（runnable_pool·池单元领烧）。**workers_plan：bm-a 工作日白天零排单（本机铁律）→ 夜窗/周末窗起烧；bm-b/bm-c 池单元领烧合法并行。**
- 部门归属：dept:策略（族规格）＋研究（judgment 面）。
- 认领（F-04 先行）：**本件=r1087 开批票**（bm-a 自领·O-20261019-2230 §二 supply floor 缺口 0/3 为本轮主因）；跑批执行票=冻结 commit 后按链式开票律另立。

## §0.5 禁开方向硬闸【冻结窗跑闸】
- 跑前过闸：`python Tools/banned_direction_gate.py --prereg research/FUND-QUALITY-P2.md`（rc0 放行·fail-closed）。
- **复活例外申报（O-20261019-2230 CEO 授权面）**：例外类型=**new_mechanism**（质量定义邻域＋出场轴参数族＋Top-N 邻域稳健性维）；**new_data 面=N/A 如实声明**（数据面与 P1 同一 `quality_faces.parquet` 导出面·零新增数据源）。
- **原否证不可能看见的东西**：P1 单定义（ROE 水平）+ 纯持有到底下，「高质量」的两种口径（水平高 vs 水平又稳）与「何时卖」的交互不可见——P2 用稳定性复合定义＋出场轴族检验 P1 看不见的口径敏感性与出场代价。

## §1 α 机制段【D6·承 P1＋定义邻域腿】
- 机制勾选：**风险溢价**（主·承 P1 verbatim：盈利能力溢价的现金流确定性定价）＋**行为偏差**（辅·承 P1 verbatim：投资者对盈利持续性反应不足）；**新增定义邻域论证**：ROE 水平单看无法区分「一次性高盈利」与「持续高盈利」——稳定性复合定义直接瞄准持续性主张；若稳定性维无增量，则 P1 否证源于机制本身而非定义实现。
- 散户凭什么赢【M0.2】：承 P1 verbatim（Top-N 等权月频·¥1M 账户容量无限）。
- 同族相关性准入【D6】：probe 冻结窗跑（headline 日收益 vs 在册成员 max|corr|≤0.7 fail-closed；**姊妹族披露预置**：FUND-QUALITY-P1 本族前代＋FUND-DIVLOWVOL-P1/P2（同数据面不同机制面）相关系数前置披露）。
- M1 t 面申报【必填】：`science_gates.t_from_sharpe` 派生＋`m1_t_value_gate`（t≥2.0）冻结窗接线。
- M3 闭合族对号：family_key=**fund_quality_stock_xs**（P1 已入册=**在册闭合族**——P2 复活批按「新证据增量」声明通道（O-20260925-1105）+CEO 复活授权面；delta 声明=①②③三腿，跑前写死）。

## §2 数据与面板【r1087 六腿探针实弹·全绿】
**探针件=`results/_fund_quality_p2_freeze_probe.json`（bm-a 2026-10-20T08:18:47+08:00·verdict=GREEN·6/6 腿 PASS·selftest ALL PASS）**

| 腿 | 门 | 实测 | 判定 |
|---|---|---|---|
| leg1 价格面板 | bar 数==8792 ∧ 末 bar==evidence_cutoff ∧ 员数≥5100 | 8792 bars·5222 员·→**2026-09-22** | ✅ |
| leg2 质量面结构 | 列齐 ∧ 行数≥300k ∧ 员数≥5100 ∧ 零重复键 ∧ 零逆序锚 ∧ 逐员锚中位≥40（10 年季报） | 306,414 行·5,223 员·锚 2001-04-30→2026-08-31·中位 **52**（p25 35/p75 83/p90 100）·重复 0·逆序 0·67.3% 员过 40 线 | ✅ |
| leg3 PIT 卫生 | avail_date≥period_end 零违例 ∧ **法定申报日映射全行恒等**（T-145 leg(a)） | 违例 0·法定映射 306,414 行全恒等·空 roe 11,176 行如实计入 | ✅ |
| leg4 月度覆盖 | 判读窗=2001-09（P1 headline t0）起 295 个月，逐月 PIT 可得成员占比≥0.80 | 中位 **0.9998**·p05 0.999·**最小 0.9978**·零月破线（全历 401 月中 106 个月破线全在 2001-09 面世前，已披露） | ✅ |
| leg5 种子带 | 登记精确命中 ∧ 零碰撞他基 ∧ 出熔炉带 ∧ 他基邻近≥2000 | 20517500/20518000·碰撞 0·熔炉带外·他基最近距 2,000（floored 恰好过线·如实披露） | ✅ |
| leg6 起点普查 | 月频枚举==401 ∧ t0==1992-09-01 | 401·1992-09-01 | ✅ |

- **腿2 线口径披露（r1087 冻结窗校正·非看结果调线）**：P1 导出门的「逐员 avail 锚数中位 ≥60」针对 101 期全名册导出件设计；本件面为 5,223 员全上市跨度宇宙（中位 52＝约 13 年季报，含 2010 后 IPO 员），两口径不可直接比较。本批改用「≥40 季锚＝中位员 10 年法定申报史」adequacy 线并**逐字披露原 60 线与本次测量分布**（中位 52/p25 35/p75 83/p90 100·44% 员达 60）。
- **腿2 单调律校正**：`avail_date` 非降（允许相等）——年报与次年 Q1 共用同一法定截止日（4-30），相等键合法；严格逆序实测 0。
- **锚面四元组【G-ANCHOR-FACE·冻结窗定稿】**：
  - 质量面：`data/fund_history_export/quality_faces.parquet`（列 code/period_end/**avail_date**/roe_q·avail=法定可获取日烘焙入导出）｜加载=pandas.read_parquet｜起算窗=2001Q1→2026Q2 全史｜PIT 取法=信号日 t 取 **avail_date ≤ t 的最近一期**（季频→最长 ~124 交易日 staleness 如实披露；禁 t 之后任何锚）。
  - **法定日锚定门（T-145 leg(a)）本批 MANDATORY 生效**（roe_q=申报面数据非市场比价面·与价值族 N/A 声明对照）。
  - 价格/收益：p1c_stock npy 缓存（单源）｜末 bar==evidence_cutoff 断言 fail-closed。
  - **evidence_cutoff（D2 前向锁定·定稿）=2026-09-22（P1 同锚）**；结果 JSON 顶层必带 `science_gates.cutoff_meta("2026-09-22")`（缺=C2 VIOLATION）。
- **资格掩码（承 P1 verbatim·零改动）**：close notna ∧ volume>0 ∧ amount>0 ∧ amt20_median ≥ ¥10,000,000 ∧ 上市≥252td ∧ 动态资 as-of-date ST/退市排除（P4_BATCH2 sec.2 verbatim·import 既有 helper）∧ **质量资格 roe_q ∈ (0, 100]**（百分比申报口径·冻结窗 probe 实测分布核验，若为小数形态则带内换算至 (0,1.0] 等价带并如实注记，判据面零漂移）。
- **数据完备门=上表六腿**（probe fail-closed；任一红=不冻结不烧）。

## §3 方法学【冻结窗定稿·三腿规格写死】
- **信号骨架**（承 P1 verbatim）：月频横截面 Top-N 等权再平衡·信号日=每月首个交易日（401 starts）·UNIVERSE_FLOOR=60·t0=2001-09-03（P1 冻结锚复验）。
- **腿①质量定义邻域（new_mechanism）**：主判=**ROE 水平**（avail≤t 最近期 roe_q·P1 同定义·直接可比）；消融=**ROE 水平×稳定性复合秩**（水平秩 + 稳定性秩，稳定性=最近 8 期 roe_q 的逆标准差秩；期数不足 8 期=不入选·诚实排除）×2 face。**判读线：主判与复合秩 skill 极差 ≤0.15=定义不敏感；复合秩胜出 ≥+0.10=稳定性维有增量（如实两向判读）**。
- **腿②Top-N 参数邻域（judged cells）**：Top-N ∈ {10,15,20,25,30}（20=主判格）× 成本 face {x1,x2}＝10 格（ROE 水平恒定义）。**邻域稳健性判读=四邻格 skill 全部>0.85 且 max−min≤0.10（§5 预测④）**。
- **腿③出场轴（显式门三选一·定稿）**：主判格=**①策略自有出场**（月频轮转 signal_reversal＋止损参数族三变格：hard_stop −15%、hard_stop −20%、trailing 12% 启动/8% 回撤·×2 face＝6 格）。对照格=**②持有到底＋缺省栈双通道显式禁用**（P1 verbatim face·P1 在册读数复用不重烧）；③template_default=零格不采用。缺省栈双通道逐键申报＋出场原因普查第二件门（CENSUS_BLOCK_SHARE=0.20）。
- **judged cells 总账（N_eff 定稿）**：策略格 20（主判 2＋N 邻域 8＋定义邻域 2＋复合秩/稳定性 2＋出场 6）＋nulls K=2000＝**N_eff 2,020**。
- null 对照：K=2000 same-mask 随机段族·rng([20517500, k]) k=0..1999；sens/自助 rng([20518000, k]) k=0..499——**SEED_REGISTRY 已登记（r1087）**＋probe leg5 全册碰撞/邻近距离门扫描 fail-closed。
- 成本口径：V2（ADV20 三层滑点+1%ADV 帽）×2 face 恒开；CN-C7 往返 bp=承 P1 单源断言（13.041bp/边）。
- 账本：finalize `science_gates.append_ledger`。

## §4 判据【冻结窗写死·共享库禁手抄】
- G1' v2=`science_gates.g1_prime_v2`；G2=`science_gates.g2_registration_v2`（DSR≥0.95·家族 PBO≤0.25）；M1 t≥2.0。
- 防运气门全保留（CEO 令原文「防运气门不拆」）。

## §5 跑前预测【冻结窗写死·≥3 条+极端日先验】
1. **主判格方向**：ROE 水平 N=20 signal_reversal face 的 skill_line_v2 落在 [0.30, 0.55]（P1 在册 0.33·sharpe −0.318 的历史区）；出场轴族对其结构改善 ≤+0.10——不预期单格复活到 1.0025 判线。
2. **定义邻域方向**：复合秩（水平×稳定性）相对水平单定义的 skill 增量 ≤+0.10（若 ≥+0.20=稳定性维真增量强信号，如实判读）。
3. **null 族相对位**：主判格 skill 高于同 mask nulls 族 95 分位（x2 成本）。
4. **N 邻域稳健性**：Top-N∈{10,15,25,30} 四邻格 skill 全部>0.85（相对主判格比值）且极差≤0.10。
5. **极端日先验**：2015-06/07 崩盘、2018 熊市、2024-01 微盘崩三段中≥2 段：P2 最优出场格最大回撤 ≤ P1 同段（P1 全史 max_dd −1.145 属病态量级，止损族必须显著收缩）。
6. **出场轴代价-收益**：hard_stop 变格最大回撤较持有到底收缩 ≥20%，代价=年化收益让渡 ≤1.5pp。

## §6 产物
- runner：`scripts/fund_quality_p2_backtest.py`（新·承 P1 runner 骨架 import 复用律）；结果件：`results/fund_quality_p2/`（顶层 `science_gates.cutoff_meta` 必带）；本件 §7/§8 回填。
- 探针件（已落）：`results/_fund_quality_p2_freeze_probe.json`＋`scripts/fund_vq_p2_probe.py`（selftest 全 PASS）。

## §7 跑后实证【跑前占位】

## §8 批后复盘【跑前占位】