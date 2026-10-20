# FUND-VALUE-P2 预注册【FROZEN 2026-10-20 r1089 bm-a】· 价值族复活批（定义邻域扫描＋参数邻域＋出场轴）

> **r1089 bm-a 冻结注记**：runner 落地并实弹验证 —— `scripts/fund_vq_p2_common.py`（共享核心：格表读自 PLAN.json·成本 face·出场参数族·引擎环·metrics/finalize 封套）＋ `scripts/fund_value_p2_backtest.py`（selftest 18/18），姊妹件 `scripts/fund_quality_p2_backtest.py`（selftest 20/20）。真数据干跑两腿全 rc0：MAIN-x1 383 信号月／t0 1994-05-03、DEF-pe_x_pb_rank-x1 同锚。本件自此 **FROZEN**：§2/§3/§5 全部数字冻结，此后只准 §7/§8 回填。

> **r1088 bm-a 进展注记**：judged-cell 计划已机械化落地 —— `scripts/fund_vq_p2_plan.py`（selftest 14/14）→ `results/fund_value_p2/PLAN.json`（20 格·N_eff 2,020·种子 20515000/20515500 登记校验通过·双通道缺省栈禁用 4+2 键申报）＋闸回执 `results/_value_plan_gate.json` verdict=GREEN。余项=burn runner `scripts/fund_value_p2_backtest.py` 引擎接线（承 P1 runner import 复用）→ 冻结 commit → 入池起烧（bm-a 工作日白天零排单）。

> **状态=冻结窗进行中（r1087 bm-a）**：本件 r1087 开立。已完成=禁向闸 ADMIT（§0.5）＋数据可达性六腿探针全绿（`results/_fund_value_p2_freeze_probe.json`·2026-10-20T08:18:28+08:00·selftest 全 PASS）＋种子带 SEED_REGISTRY 登记（20515000/20515500·probe leg5 实弹扫描零碰撞）＋§2 四元组锚定＋§3 三腿规格写死＋§5 预测定稿。**余项=runner 落地（`scripts/fund_value_p2_backtest.py`·承 P1 runner 骨架 import 复用）→ 跑齐后 commit 冻结；冻结前禁烧。** §7/§8 占位纪律（写数字即造假）。
> 模板=`research/PREREG_TEMPLATE.md`（T-02 6/7）；判据权威=`research/BACKTEST_SCIENCE.md` v2＋共享库 `scripts/science_gates.py`（禁手抄判线）。
> **CEO 判负线复活授权（O-20261019-2230-bm-b §二.2·三件律：本授权+新预注册+新证据）**：承 FUND-VALUE-P1 判决（headline skill 0.44 无条件面·2026-10-14 在册），新证据三腿=①价值定义邻域（PE-only / PB-only / PE×PB 复合排名——P1 只判 PE 单定义）②Top-N 参数邻域（邻域稳健性=P2 判负面主判据）③出场轴优化（P1=②持有到底；P2 显式声明①策略自有出场族）。防运气门不拆（技能线/DSR/PBO/种子登记/预注册冻结全照旧）。
> 血统：FUND-VALUE-P1.md（股票横截面月频族·bm-a r597 冻结·N_eff 2,004）+ CEO 研究导向律合规（价值=国内原生主流风格打法，形式化非国外框架筛国内打法）。

## §0 批件身份【跑前·冻结窗定稿】
- 批名/批号：**FUND-VALUE-P2**（批内格数 **N_eff=2,020 定稿**：judged 策略格 20（主判 2＋N 邻域 8＋定义邻域 4＋出场 6）×成本 face 计入＋K=2000 null 族）。
- 算力预算：长活入池（runnable_pool·池单元领烧·O-20261019-2230 §二）。**workers_plan：bm-a 工作日白天零排单（本机铁律）→ 首批烧在夜窗/周末窗起烧；bm-b/bm-c 池单元领烧合法并行（面板重投到位后）**。
- 部门归属：dept:策略（族规格）＋研究（judgment 面）。
- 认领（F-04 先行）：**本件=r1087 开批票**（bm-a 自领·O-20261019-2230 §二 supply floor 缺口 0/3 为本轮主因）；跑批执行票=冻结 commit 后按链式开票律另立。

## §0.5 禁开方向硬闸【冻结窗跑闸】
- 跑前过闸：`python Tools/banned_direction_gate.py --prereg research/FUND-VALUE-P2.md`（rc0 放行·fail-closed；回执见 §2 表下注）。
- **复活例外申报（O-20261019-2230 CEO 授权面）**：例外类型=**new_mechanism**（出场轴参数族＋价值定义邻域＋Top-N 邻域稳健性维=P1 未检验的机制面）；**new_data 面=N/A 如实声明**（数据面与 P1 同一 `value_faces.parquet` 导出面·零新增数据源——本批增量纯机制面，不冒充新数据）。
- **原否证不可能看见的东西**：P1 单一定义（PE）+ 纯持有到底出场下，「便宜」的两种口径（盈利倍数 vs 账面倍数）与「何时卖」的交互完全不可见——P2 用定义邻域×出场轴族检验 P1 看不见的口径敏感性与出场代价。

## §1 α 机制段【D6·承 P1＋定义邻域腿】
- 机制勾选：**风险溢价**（主·承 P1 verbatim 论证）＋**行为偏差**（辅·承 P1 verbatim）；**新增定义邻域论证**：PE 与 PB 计量的不是同一风险源（盈利周期 vs 资产重置），二者同族但不同口径——若「便宜」是真溢价，两种口径都应跑赢被动面；若只有单口径跑赢，则是口径特异伪影而非风格溢价。此判读由 P2 burn 读数检验，不预设方向。
- 散户凭什么赢【M0.2】：承 P1 verbatim（Top-N 等权月频·¥1M 账户容量无限）。
- 同族相关性准入【D6】：probe 冻结窗跑（headline 日收益 vs 在册成员 max|corr|≤0.7 fail-closed；**姊妹族披露预置**：FUND-VALUE-P1 本族前代 corr 前置披露面照 P1 §1 注记纪律）。
- M1 t 面申报【必填】：`science_gates.t_from_sharpe` 派生＋`m1_t_value_gate`（t≥2.0）冻结窗接线。
- M3 闭合族对号：family_key=**fund_value_stock_xs**（P1 已入册=**在册闭合族**——本批=P2 复活批按「新证据增量」声明通道（O-20260925-1105）+CEO 复活授权面；delta 声明=①②③三腿，跑前写死）。

## §2 数据与面板【r1087 六腿探针实弹·全绿】
**探针件=`results/_fund_value_p2_freeze_probe.json`（bm-a 2026-10-20T08:18:28+08:00·verdict=GREEN·6/6 腿 PASS·selftest ALL PASS）**

| 腿 | 门 | 实测 | 判定 |
|---|---|---|---|
| leg1 价格面板 | p1c_stock 缓存：bar 数==8792 ∧ 末 bar==evidence_cutoff ∧ 员数≥5100 | 8792 bars·5222 员·1990-12-19→**2026-09-22** | ✅ |
| leg2 价值面结构 | 列齐 ∧ 行数≥2M ∧ 员数≥5100 ∧ 零重复键 ∧ 零逆序锚 ∧ 逐员锚中位≥550 | 4,133,848 行·5,224 员·锚 1991-03-18→2026-10-01·中位 **693**（p10–p90 605–1,142）·重复 0·逆序 0·97.6% 员过 550 线 | ✅ |
| leg3 PIT 卫生 | 价值面=as-published 市场比价面 → 法定申报日门 **N/A 如实声明**；零空锚 | 空锚 0 | ✅ |
| leg4 月度覆盖 | 判读窗=1994-05（P1 headline t0）起 383 个月，逐月 PIT 可得成员占比≥0.80 | 中位 **0.9995**·p05 0.9796·**最小 0.933**·零月破线（全历 401 月中 7 个月破线全在 1992–1993 上市前史，已披露） | ✅ |
| leg5 种子带 | 登记精确命中 ∧ 零碰撞他基 ∧ 出熔炉带 ∧ 他基邻近≥2000 | 20515000/20515500·碰撞 0·熔炉带外·他基最近距 4,500 | ✅ |
| leg6 起点普查 | 月频首交易日枚举==401 ∧ t0==1992-09-01 | 401·1992-09-01 | ✅ |

- **锚面四元组【G-ANCHOR-FACE·冻结窗定稿】**：
  - 价值面：`data/fund_history_export/value_faces.parquet`｜加载=pandas.read_parquet｜起算窗=1991-03-18→2026-10-01 全史｜预热=零（锚=水平面非滚动面）。
  - 接合法（PIT 律·承 P1 verbatim）：信号日 t 取 **anchor_date ≤ t 的最近一锚** forward-fill（半月频→最长 ~15 交易日 staleness 如实披露；禁 t 之后任何锚）。
  - 价格/收益：p1c_stock npy 缓存（`p1c_stock_ic_batch.load_universe` 单源）｜末 bar==evidence_cutoff 断言 fail-closed。
  - **evidence_cutoff（D2 前向锁定·定稿）=2026-09-22（P1 同锚）**——同窗证伪连续性；结果 JSON 顶层必带 `science_gates.cutoff_meta("2026-09-22")`（缺= C2 VIOLATION）。
- **资格掩码（承 P1 verbatim·零改动）**：close notna ∧ volume>0 ∧ amount>0 ∧ amt20_median ≥ ¥10,000,000 ∧ 上市≥252td ∧ 动态资 as-of-date ST/退市排除（P4_BATCH2 sec.2 verbatim·runner import 既有 helper 禁重写）∧ 估值资格 pe_ttm ∈ (0,200] ∨ pb ∈ (0,20]（按各格定义面判定）。
- **数据完备门=上表六腿**（probe fail-closed；任一红=不冻结不烧）。

## §3 方法学【冻结窗定稿·三腿规格写死】
- **信号骨架**（承 P1 verbatim）：月频横截面 Top-N 等权再平衡·信号日=每月首个交易日（T-22 普查 401 starts）·UNIVERSE_FLOOR=60·t0=1994-05-03（P1 冻结锚复验）。
- **腿①价值定义邻域（new_mechanism）**：3 定义 × 2 face＝6 格？**定稿=2 消融格 ×2 face**：PE-only 排序（=主判格）/ PB-only 排序 / PE×PB 复合秩。**gspec：主判=PE-only**（P1 同定义·直接可比）；PB-only 与复合秩=消融格（判读面=三定义 skill 全部>0.90 且极差≤0.15 → 判定「口径不敏感」；否则如实判「单口径特异」）。
- **腿②Top-N 参数邻域（judged cells·扩容买单）**：Top-N ∈ {10,15,20,25,30}（20=主判格）× 成本 face {x1,x2}＝10 格（PE-only 恒定义·质量/流动性掩码不变）。**邻域稳健性判读=四邻格 skill 全部>0.85 且 max−min≤0.10（§5 预测④）**。
- **腿③出场轴（显式门三选一·定稿）**：主判格=**①策略自有出场**（月频轮转 signal_reversal＋止损参数族三变格：hard_stop −15%、hard_stop −20%、trailing 12% 启动/8% 回撤·×2 face＝6 格）。对照格=**②持有到底＋缺省栈双通道显式禁用**（P1 verbatim face·P1 在册读数复用不重烧）；③template_default=零格不采用。缺省栈双通道逐键申报＋出场原因普查第二件门（CENSUS_BLOCK_SHARE=0.20 承 P1 §0.6）。
- **judged cells 总账（N_eff 定稿）**：策略格 20（主判 2＋N 邻域 8＋定义邻域 2＋出场 6＋PB/复合 2）=**20**；＋nulls K=2000＝**N_eff 2,020**。
- null 对照：K=2000 same-mask 随机段族·rng([20515000, k]) k=0..1999（pair-seed sub-stream law）；sens/自助描述轴 rng([20515500, k]) k=0..499——**SEED_REGISTRY 已登记（r1087）**＋probe leg5 全册碰撞/邻近距离门扫描 fail-closed。
- 成本口径：V2（ADV20 三层滑点+1%ADV 帽）×2 face 恒开；CN-C7 往返成本 bp=承 P1 单源断言（`rev_osc_stock_p1.COST_X1 == cost_spec.x1_side_rate()`·13.041bp/边·rt 52.164bp）。
- 账本：finalize `science_gates.append_ledger`（dict schema 唯一）。

## §4 判据【冻结窗写死·共享库禁手抄】
- G1' v2=`science_gates.g1_prime_v2`（skill_line_v2 数据驱动·bootstrap CI 下界>0·F6 双口径）；G2=`science_gates.g2_registration_v2`（DSR≥0.95·家族 PBO≤0.25）；M1 t≥2.0。
- 防运气门全保留（CEO 令原文「防运气门不拆」）。

## §5 跑前预测【冻结窗写死·≥3 条+极端日先验】
1. **主判格方向**：PE-only N=20 signal_reversal face 的 skill_line_v2 落在 [0.40, 0.60]（P1 在册 0.44 的历史区），出场轴族对其有 ≤+0.10 的结构性改善——不预期复活批把 0.44 拉到 1.0025 判线上（复活成败由三腿合并证据面判定，非单格孤证）。
2. **定义邻域方向**：PB-only 与 PE×PB 复合秩的 skill 与 PE-only 极差 ≤0.15（若 >0.30=口径特异伪影强信号，如实判负）。
3. **null 族相对位**：主判格 skill 高于同 mask nulls 族 95 分位（signal_reversal face·x2 成本）。
4. **N 邻域稳健性**：Top-N∈{10,15,25,30} 四邻格 skill 全部>0.85（相对主判格比值）且极差≤0.10。
5. **极端日先验**：2015-06/07 崩盘、2018 熊市、2024-01 微盘崩三段中≥2 段：P2 最优出场格最大回撤 ≤ P1 同段（止损族在崩盘段收缩回撤）。
6. **出场轴代价-收益**：hard_stop 变格最大回撤较持有到底收缩 ≥20%，代价=年化收益让渡 ≤1.5pp。

## §6 产物
- runner：`scripts/fund_value_p2_backtest.py`（新·承 P1 runner 骨架 import 复用律）；结果件：`results/fund_value_p2/`（顶层 `science_gates.cutoff_meta` 必带）；本件 §7/§8 回填。
- 探针件（已落）：`results/_fund_value_p2_freeze_probe.json`＋`scripts/fund_vq_p2_probe.py`（selftest 全 PASS）。

## §7 跑后实证【跑前占位】

## §8 批后复盘【跑前占位】