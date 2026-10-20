# FUND-DIVLOWVOL-P2 预注册【DRAFT-NOT-FROZEN·r1038 开批票】· 红利低波族复活批（盈利质量过滤强化+参数邻域扫描+出场轴优化）

> **状态=冻结窗进行中（r1040）**：本件 r1038 开立；r1039 已完成=禁向闸 ADMIT（BAN-04 例外申报逐字过闸）＋§2 四元组锚定稿＋cutoff 裁定（P1 同锚 2026-09-22）＋§3 三腿规格写死＋§5 预测定稿＋种子带 SEED_REGISTRY 登记；r1040 已完成=probe 模块落地（scripts/fund_divlowvol_p2_probe.py·P1 内核单源 import·selftest 17/17·本地腿绿=leg2 分红面/leg5 种子带带册校验/leg6 质量 PIT 结构门·面板腿诚实 AWAITING_PANEL exit4）；**r1066 已完成=本地基座面板腿全绿（GREEN 7/7·回执 results/_fund_divlowvol_p2_freeze_probe_local.json·d6 ADMIT 0.2588·详见 §2.1）**；**余项=runner 落地（scripts/fund_divlowvol_p2_backtest.py）＋烧面二选一（p1c 重投 或 本地基座+送转充足性腿）→ 两件齐后 commit 冻结**；**r1067 已完成=送转充足性腿落地实跑（INADEQUATE_FOR_CASH_ONLY_SIDECAR·裁 A>B·B 条件化走 vwap_raw_proxy·详见 §2.2）——烧面裁决一件已毕，余 runner 一件**；冻结前禁烧；§7/§8 占位纪律（写数字即造假）。
> 模板=`research/PREREG_TEMPLATE.md`（T-02 6/7）；判据权威=`research/BACKTEST_SCIENCE.md` v2＋共享库 `scripts/science_gates.py`（禁手抄判线）。
> **CEO 判负线复活授权（O-20261019-2230-bm-b §二.1·三件律：本授权+新预注册+新证据）**：承 FUND-DIVLOWVOL-P1 判决（0.89 vs 基准 1.0025·DSR 0.675·results/fund_divlowvol_p1/fund_divlowvol_p1_results.json 在册），新证据三腿=①盈利质量过滤强化（eligibility np_ttm/np_annual+quality_faces 盈利质量面——P1 未用）②参数邻域扫描（Sobol/邻域格·判负面主判据邻域稳健性检验）③出场轴优化（出场轴显式门三选一显式声明·P1=②持有到底，P2 出场轴=r1039 冻结窗设计定稿）。防运气门不拆（CEO 令原文：技能线/DSR/PBO/种子登记/预注册冻结全照旧）。
> 血统：FUND-DIVLOWVOL-P1.md（股票横截面月频族·bm-b r610 冻结·N_eff 2,002 池烧）＋ CEO 研究导向律合规（红利低波=A 股原生主流风格打法·形式化非国外框架筛国内打法）。

## §0 批件身份【跑前·冻结窗定稿】
- 批名/批号：**FUND-DIVLOWVOL-P2**（批内格数 **N_eff=2,018 定稿**：judged 策略格 18（主判 2＋邻域 8＋消融 2＋出场 6）×成本 face 计入＋K=2000 null 族——扩容买单律在案）。
- 算力预算：长活入池（runnable_pool·池单元领烧·O-20261019-2230 §二·**workers_plan 定稿：bm-a 宿主满核主力（面板在位·P1 烧批先例）＋bm-b 分片车道候 p1c 缓存重投到位后并入＋bm-c 同**·CEO 10% 余量律）。
- 认领补充（r1039）：**fleet/inbox/ MSG 面板重投请求已发 bm-a**（p1c_stock 缓存＋factor sidecar 面·数据面通道按 TRANSFER.md 矩阵·P1 r610 冻结窗本机曾持同缓存先例）；D6 probe 双通道=bm-a 代跑（宿主面板）或 bm-b 本地跑（重投后）——先到先冻结。
- 部门归属：dept:策略（族规格）＋研究（judgment 面）。
- 认领（F-04 先行·承前）：**本件=r1038 开批票**（O-20261019-2230 §二「bm-b/bm-c＝池单元领烧」）；跑批开批执行票=冻结 commit 后按链式开票律另立（r1039 冻结窗余项收齐即冻结开票）。

## §0.5 禁开方向硬闸【冻结窗跑闸】
- 跑前过闸：`python Tools/banned_direction_gate.py --prereg research/FUND-DIVLOWVOL-P2.md`（rc0 放行·fail-closed）。
- **命中编号：BAN-04**（词面命中=§3「参数邻域网格」的方法学表述·非网格交易策略方向：本批零 518880/黄金类标的·零价格网格挂单机制·命中词指回测参数扫描方法·语义不成立仍按闸法逐字申报）。
- **复活例外申报（O-20261019-2230 CEO 授权面）**：例外类型=**new_data**（盈利质量过滤面：data/fund_history_export/quality_faces.parquet **306,414 行 PIT ROE〔avail_date 锚·r1039 探针实测·列 code/period_end/avail_date/roe_q〕**——P1 判负时未入判据面）＋**new_mechanism**（出场轴参数族＋Top-N 邻域稳健性维=原否证未检验的机制面）。CEO 授权=O-20261019-2230-bm-b §二.1 原文在案。
- **原否证不可能看见的东西**：P1 纯持有到底出场下「高股息=价值陷阱」成员缺盈利质量维度无法分层剔除——P2 以 PIT ROE 过滤（new_data）＋出场轴参数族（new_mechanism）检验 P1 看不见的盈利可持续性分层效应。

## §1 α 机制段【D6·承 P1＋质量腿】
- 机制勾选：**风险溢价**（主·承 P1 verbatim 论证）＋**行为偏差**（辅·承 P1 verbatim）；**新增质量腿论证**：盈利质量过滤（TTM 净利为正且盈利质量面过线）剔除「高股息=价值陷阱」伪成员——红利 carry 的现金流确定性主张只在盈利可持续成员上成立，质量过滤=把「股息率排序」从「价值陷阱收集器」矫正为「现金流溢价收集器」——由 P2 burn 读数检验。
- 散户凭什么赢【M0.2】：承 P1 verbatim（制度/容量面：Top-N 等权月频·¥1M 账户容量无限）。
- 同族相关性准入【D6】：probe 冻结窗跑（headline 日收益 vs 在册成员+同批全格 max|corr|≤0.7 fail-closed；**姊妹族披露预置**：FUND-DIVLOWVOL-P1 本族前代=0.8039 价值族 corr 前置披露面照 P1 §1 注记纪律）。
- M1 t 面申报【必填】：`science_gates.t_from_sharpe` 派生＋`m1_t_value_gate`（t≥2.0）冻结窗接线。
- M3 闭合族对号：family_key=**fund_divlowvol_stock_xs**（P1 已入册=**在册闭合族**——本批=P2 复活批按「新证据增量」声明通道（O-20261025-1105）+CEO 复活授权面；delta 声明=①②③三腿，跑前写死）。

## §2 数据与面板【r1038 数据可达性审计实证（本窗已跑）＋冻结窗补齐】
**r1038 审计结论（results/_r1038bmb_stock_domain_audit.json）＋r1039 冻结窗探针补录（本节=冻结窗定稿面）**
| 面 | 路径 | r1038/r1039 实测 | 状态 |
|---|---|---|---|
| 分红事件 | `data/fund_history_export/div_events_faces.parquet` | 54,494 行/5,124 符号/1991-04-03→2026-10-23/列 code,ex_date,cash_div_per_10,record_date（T-154 sha256 在册） | ✅ LOCAL |
| 盈利质量（PIT） | `data/fund_history_export/quality_faces.parquet` | **r1039 探针实测：306,414 行·列 code,period_end,avail_date,roe_q·PIT 锚=avail_date**（2001Q1 起按期滚动） | ✅ LOCAL |
| 资格快照 | `data/fundamental/eligibility.csv` | 11,647 行·**当日快照面（<24h 自刷新）——历史信号日禁用（防前视·裁定 3）**·仅 as-of reporting 交叉核对 | ✅ LOCAL |
| 个股日线（前向采集道） | `data/astock_daily/per/`（T-87 bm-b 车道） | 5,221 件 qfq csv·complete through 2026-10-19（列 date,OHLC,volume,amount,outstanding_share,turnover） | ✅ LOCAL（前向道·非本批烧面） |
| p1c_stock 冻结面板（**烧面**） | bm-a 宿主（T-139 冻结件·P1 同一 meta） | 8,792 bars×5,222 syms·last bar 2026-09-22·qfq＋Money02/data/bars factor sidecar 面宿主在位 | ✅ bm-a 在位（bm-b 重投请求已发 fleet/inbox） |

**r1039 冻结窗裁定（三件·定稿）**：
1. **烧批价格面=p1c_stock 冻结面板**（P1 verbatim 同一面：与 P1 判决 0.89/DSR 0.675 同窗同面直接可比=复活批证伪连续性正身）。本地 astock_daily/per 面不胜任烧面：raw-close 回收需 Money02 factor sidecar（本地 0/5,124 在位），仅凭现金分红事件重建 f(t) 遇送转事件必然错位——诚实判负不采用（词面「本地重建主路」就此更正）。**evidence_cutoff=2026-09-22（P1 同锚·D2 lockbox）**：复活批=同窗证伪连续性检验——对 P1 否证的增量证据必须在同一评价窗上成立（新批新锚 2026-10-19 默认位的显式例外·理由在案）；astock_daily/per（cutoff 10-19）=前向采集道记录，非本批烧面。
2. **bm-b/bm-c 分片车道**：p1c 缓存重投请求已发 bm-a（数据面通道按 TRANSFER.md 矩阵·回执窗 ≤2 轮）；重投到位前烧批主力=bm-a 宿主（O-20261019-2230 §二「bm-a=重烧主力」verbatim·P1 N_eff 2,002 池烧先例）。
3. **质量腿历史面=quality_faces PIT only**：eligibility.csv 为当日快照——历史信号日禁用（防前视·r1039 冻结窗焊死；原草案 §3 混用快照面已更正）。

### §2.1 冻结窗修订（r1066 bm-b·本地基座探针全绿·**冻结窗内变更，跑前，非看结果调线**）
r1039 裁定 1 判「本地 astock_daily/per 面不胜任」的理由是**当时本地 0/5,124 因子 sidecar 在位**。该缺口已在 r1056 被补齐（`data/cache/p1c_local`＝由 astock_daily/per 重建的 p1c 兼容 qfq 面板 8,745 bars×5,225 syms·cutoff 2026-10-19；`data/cache/p1c_sidecars`＝5,124 件 qfq-inversion-v1 现金分红因子）。r1066 据此把 probe 的**面板腿**跑到本地基座上（`python scripts/fund_divlowvol_p2_probe.py run --panel local`），结果：

- **探针裁定=GREEN（7/7 腿）**，回执 `results/_fund_divlowvol_p2_freeze_probe_local.json`（内容 sha16 `81409bcd06f02c27`·幂等·selftest 25 腿 PASS）。实测：leg1 8,745 bars/5,225 员/切点 2026-10-19（≥锚 2026-09-22 覆盖，frozen cutoff 前 8,732 bars）；leg2 分红面 54,494 行；**leg3 sidecar 回收 36,697 纯现金事件·中位相对偏差 2.6e-9·frac_exact 1.0**（711 事件混合/缺席如实排除）；leg4 月度普查 402 starts·本地 t0=2003-11-03（早于锚·披露不夹持）·锚后零月破 60 线·锚后 rank 域最小 131；leg6 质量覆盖 min 0.9972/中位 1.0；leg5 种子带全册扫描无碰撞。
- **两处基座相对判据（显式替换·同旨更强，写死不再改）**：①leg1 由「bars==8,792 且末 bar==cutoff」改为「穿 frozen cutoff ≥8,000 bars ∧ 末 bar ≥ cutoff ∧ 员数 ≥5,100」（本地面板日历起点更早、终点更晚，等值式是 Money02 面板的形状而非判据本意）；②leg4 由「t0==2006-02-06 且 starts==401」改为「本地 t0 ≤ 锚 ∧ 锚后零月破线 ∧ **判读窗逐月恒等 P1 网格（2006-02..2026-03=242 月·实测 true）**」。多出的 1 个 start 落在锚前（1992-2006 共 160 个月），永不进入判读窗，如实披露。
- **d6 同族准入=ADMIT**：max|corr|=0.2588（<0.7 线），家族前代披露 0.8039 照记，回执 `results/fund_divlowvol_p2/d6.json`。
- **残留风险（不掩盖·烧面裁决仍待）**：qfq-inversion 因子只建模**现金分红**，本地**无送转事件面**——r1039 的原警告（送转下 raw-close 重建必错位）在本地基座上**仍未排除**，leg3 已知答案只覆盖纯现金事件（故其「精确」部分是构造自洽而非独立证伪）。烧面两条路：**(A) p1c 重投到位**（P1 同面·零残留风险·首选）或 **(B) 本地基座 + 送转充足性腿**（需先取得送转事件面）。**本探针 GREEN 只是冻结门的地板，不等于冻结成立**：冻结仍须 runner 落地（`scripts/fund_divlowvol_p2_backtest.py`）+ 烧面二选一裁决。

### §2.2 烧面裁决（r1067 bm-b·**冻结窗内裁决，跑前，非看结果调线**）
送转充足性腿已落地并实跑：`scripts/fund_divlowvol_p2_split_adequacy.py`（selftest 8/8）→ 回执 `results/fund_divlowvol_p2/split_adequacy.json`。方法=以 **VWAP（amount/volume，原始价位）** 作 raw price 代理，检验残差

> ρ_t = close_qfq(t) / (amount/volume)(t) × f_cash(t)

是否恒为 1.0（现金面因子若完整解释了面板 qfq 的全部还原，则 ρ≡1）。

实测（月频采样 430 个月·判读面 5,007 员·cutoff 2026-09-22）：
- **level 面**：ρ 中位 0.9898，但 **1,702 员（33.99%）的个体 ρ 中位偏离 1.0 超过 ±5%**；
- **step 面**：月间 ρ 阶跃越阈 **13,076 次**、波及 **3,649 员（72.88%）**，隐含比例集中于 0.5/0.49（≈ 2 拆 1 档）；
- **裁定=`INADEQUATE_FOR_CASH_ONLY_SIDECAR`**：现金面因子**不足以**还原 raw close——面板 qfq 的还原幅度大于纯现金分红所能解释的部分，差额即送转。

**烧面裁决（写死，不再改）**：
1. **路线 A（首选）= p1c 重投**——其 qfq 携带供应方完整还原因子，零残留风险；重投到位即走 A，本裁决不改。
2. **路线 B（备用·条件化）= 本地基座 + `vwap_raw_proxy`**——若 A 在冻结窗内未到，B **必须**以信号日的 `amount/volume` 作 `P_raw`（原始价位天然含送转，无需送转事件面）；**禁止**以 `qfq × f_cash` 反推 raw close（本 leg 已实证其错位，且 33.99% 成员个体层面超 ±5% 容差）。
3. 送转事件候选面 `results/fund_divlowvol_p2/split_events_candidate.json`（13,326 条·逐条含 sym/日期/隐含比例）仅作**审计留痕与候选修正面**，本批**不并入**判据（并入须另批预注册）。
4. 判据不变：两条路线共用同一 evidence_cutoff=2026-09-22 与同一 judged 格表；路线差异须在 §7 逐格标注（A/B 标签）。

- **数据锚面定义四元组【G-ANCHOR-FACE·冻结窗定稿】**：
  - 分红事件：`data/fund_history_export/div_events_faces.parquet`｜加载=pandas.read_parquet｜起算窗=1991-04-03→2026-10-23 全史｜预热=信号日前推 365d TTM 窗（ttm_cash_sum 内核 import 自 fund_divlowvol_p1_probe 单源）。
  - 盈利质量：`data/fund_history_export/quality_faces.parquet`｜加载=pandas.read_parquet｜起算窗=2001Q1→最新法定完备期全史｜PIT 取法=avail_date≤t 的最新 period_end 之 roe_q（无可得期=不入选·诚实排除）。
  - 价格/收益：p1c_stock npy 缓存（p1c_stock_ic_batch.load_universe 单源）｜8,792 bars×≥5,100 syms·qfq｜last bar=2026-09-22==evidence_cutoff 断言 fail-closed。
  - raw-close 回收：sidecar_f_at 内核（import 自 fund_divlowvol_p1_probe 单源）·Money02/data/bars/<sym>.factor.json 随面板宿主。
- **evidence_cutoff（D2 前向锁定·定稿）=2026-09-22（P1 同锚）**——复活批同窗证伪连续性（裁定 1·cutoff_meta 必带）。
- 数据完备门：probe 腿跑（leg1 价格面板门/leg2 分红面门/leg3 sidecar 回收已知答案/leg4 月度普查＋t0 锚复验/leg5 种子带全册扫描=承 P1 §2 门族 verbatim＋**leg6 新增=quality PIT 覆盖门**：信号日历 2006-02→2026-03 逐月统计 quality_faces 可得成员占 yield>0 候选域比例·覆盖率断言≥80% fail-closed＋NaN/停牌/政体系列漂移对账承 P1 门族）。

## §3 方法学【r1039 冻结窗定稿·三腿规格写死】
- **信号骨架**（承 P1 verbatim）：月频横截面 Top-N 等权再平衡·信号日=每月首个交易日（T-22 普查 401 starts）·yield_ttm=ttm_cash/P_raw_close（ttm_cash_sum/sidecar_f_at 内核 import 自 fund_divlowvol_p1_probe 单源·重实现零）·低波筛选 σ252≤候选域中位（bottom half·min 126 bars）·UNIVERSE_FLOOR=60·t0=2006-02-06（P1 冻结锚复验）。
- **腿①盈利质量过滤（new_data）**：质量面=quality_faces PIT——信号日 t 取 avail_date≤t 的最新 period_end 的 roe_q>0（盈利为正·简单一次定稿）；无可得期=诚实排除。消融面=质量过滤 OFF=P1 在册判决（0.89·不重烧）——增量=QF ON 减 OFF。
- **腿②参数邻域扫描（judged cells·扩容买单）**：Top-N ∈ {10,15,20,25,30}（20=主判格）×成本 face {x1,x2}＝10 格（质量过滤恒 ON·vol_frac 恒 0.5）；消融格=vol_frac 1.0（去低波屏·N=20）×2 face＝2 格。**邻域稳健性判读=四邻格 skill 全部>0.85 且 max−min≤0.10（§5 预测④）**。
- **腿③出场轴（r1039 定稿）**：主判格=**①策略自有出场**（月频轮转 signal_reversal＋止损参数族三变格：hard_stop −15%、hard_stop −20%、trailing 12% 启动/8% 回撤·×2 face＝6 格）；对照格=**②持有到底＋缺省栈双通道显式禁用**（P1 verbatim face·P1 在册 0.89 复用不重烧）；template_default（③）=零格不采用。缺省栈双通道逐键申报＋出场原因普查第二件门（CENSUS_BLOCK_SHARE=0.20 承 P1 §0.6）。
- **judged cells 总账（N_eff 定稿）**：策略格 18（主判 2＋邻域 8＋消融 2＋出场 6）＋nulls K=2000＝**N_eff 2,018**。
- null 对照：K=2000 same-mask 随机段族·rng([20523000, k]) k=0..1999（pair-seed sub-stream law）；sens/自助描述轴 rng([20523500, k]) k=0..499——种子带 SEED_REGISTRY r1039 登记＋probe leg5 全册碰撞/邻近距离（≥2,000）门扫描 fail-closed。
- 成本口径：V2（ADV20 三层滑点+1%ADV 帽）×2 face 恒开；CN-C7 往返成本 bp 申报=承 P1 单源断言（rev_osc_stock_p1.COST_X1==cost_spec.x1_side_rate()·13.041bp/边·rt 52.164bp·Y1M 账户 Top-20 等权 Y50k 单位过 ¥20k 最低佣金档）。
- 账本：finalize `science_gates.append_ledger`（dict schema 唯一）。

## §4 判据【冻结窗写死·共享库禁手抄】
- G1' v2=`science_gates.g1_prime_v2`（skill_line_v2 数据驱动·bootstrap CI 下界>0·F6 双口径）；G2=`science_gates.g2_registration_v2`（DSR≥0.95·家族 PBO≤0.25）；M1 t≥2.0；阶段×风格面（O-20261019-2230 §二.4 组合族批归其本批·本批=族级判决面）。
- 防运气门全保留（CEO 令原文「防运气门不拆」：技能线/DSR/PBO/种子登记/预注册冻结照旧）。

## §5 跑前预测【r1039 冻结窗写死·≥3 条+极端日先验】
1. **质量腿增量方向**：QF 主判格 skill_line_v2 高于 P1 在册 0.89（盈利质量过滤剔除价值陷阱→预期落在 [0.93, 1.00] 区间；仍可能低于判线 1.0025——复活成败由三腿合并证据面判定，非单格孤证）。
2. **成分重叠面**：QF 月度选股与 P1 选股平均成员重叠 ≤70%（质量过滤实质性改变成分·非 P1 复刻）。
3. **null 族相对位**：QF 主判格 skill 高于同 mask nulls 族 95 分位（signal_reversal face·x2 成本）。
4. **邻域稳健性**：Top-N∈{10,15,25,30} 四邻格 skill 全部>0.85 且 max−min≤0.10（腿②判读线·写死）。
5. **极端日先验**：2015-06/07 崩盘、2018 熊市、2024-01 微盘崩三段中≥2 段：QF 袖筒最大回撤 ≤ P1 同段（盈利质量名在崩盘段更抗跌）。
6. **出场轴代价-收益**：hard_stop 变格最大回撤较 hold-through 收缩 ≥20%，代价=年化收益让渡 ≤1.5pp（腿③判读线·写死）。

## §6 产物
- runner：`scripts/fund_divlowvol_p2_backtest.py`（新·承 P1 runner 骨架 import 复用律）；结果件：`results/fund_divlowvol_p2/`（顶层 `science_gates.cutoff_meta` 必带）；本件 §7/§8 回填。

## §7 跑后实证【跑前占位】

## §8 批后复盘【跑前占位】
