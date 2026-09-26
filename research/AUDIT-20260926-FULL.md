# Bigmoney 全量机制梳理清点表 AUDIT-20260926-FULL（O-20260926-1355 · T-83 s1 · v1.0）

> CEO 原话：「所以你科学理性梳理一下子公司的所有规则和机制，全面优化」→ 本件=**s1 九层全量清点表**。纪律 1（测量先行）：本件只清点+标靶，**零动刀**——不改任何机制/法件/数值；一切优化=后续 s2（检测）与 s3（GM 亲执七件）。
> 机器面：确定性枚举器 `scripts/governance_audit_s1.py`（零网络·零改写·selftest 7/7）→ 快照 `results/governance_audit_20260926.json`（as_of 2026-09-26·同参重跑字节恒等）。本件一切计数可由快照复核；标注「承正典」= 引自既有权威文件原文，标注「实测」= 本轮枚举/读件所得。
> 分工（票 T-83·认领 commit f4dfc5b6 bm-b r267）：s1=本件（bm-b）→ s2=冲突/重复/死面检测（bm-b·下轮）→ s3=优化落地七件（**GM 亲执·本轮零触碰**）→ s4=季度法熵审视常设接线（后续轮·任意健康机）。

## 快照总览（九层计数 · as_of 2026-09-26）

| 层 | 清点面 | 计数（实测） |
|---|---|---|
| L1 | 判据载体 | 正典件 9 + science_gates.py 判据函数 23 |
| L2 | 正典/战略文件指针位 | 21（research 顶层 md 全量=103 件） |
| L3 | 组织 | 9 部门 · 11 团队 · 交易员 5 级阶梯+淘汰 |
| L4 | 产品线矩阵（四轴） | 17 行（✅8 · 🟡5 · ⬜4） |
| L5 | 账户生命周期载体 | 9 件 + live/ 3 面 |
| L6 | 纸盘账户族目录 | 11 族（+grid_paper 已接线未物化） |
| L7 | 研发管线 | 池 49 批（done 48 / ready 1）· PREREG 正典 14 件 |
| L8 | 机队机制载体 | Tools 32 件 · scripts/*.py 216 件 · 心跳 3 机 |
| L9 | CEO 令 | 83 令（09-23=28 · 09-24=33 · 09-25=13 · 09-26=9；取代/让路/作废/收回面 9 令） |

## L1 判据层（逐件）

| 载体 | 角色（承正典） | 状态 |
|---|---|---|
| `research/BACKTEST_SCIENCE.md` | 判据科学层**唯一权威**（O-2215）：D1 试验数校正（技能线 v2+DSR≥0.95）·D2 前向锁盒（cutoff 2026-09-22 后锁定）·D3 CI 必报·D4 PBO≤0.25·D5 成本 v2·D6 机制门槛·D7 样本充分性 | 活·宪法级 |
| `scripts/science_gates.py` | 判据共享库（23 函数：ledger_head/N_eff/技能线/DSR/CI/append_ledger/cutoff_meta/g1_prime_v2/g2_registration_v2 等）——禁各批手抄判线 | 活·消费面=全门禁脚本 |
| `firm/STRATEGY_EVALUATION.md` | 策略评价判据面（§1.3 禁看结果调线与 BACKTEST_SCIENCE 同源） | 活 |
| `firm/hr.py` | paper 判据数值正典（考核条款/晋升淘汰阈值——BACKTEST_SCIENCE §2 明文「本文不复制」） | 活 |
| `firm/SELF_REVIEW.md` | SR1-SR5 自审判据冻结（v1.0·禁看结果调线） | 活·月度 |
| `firm/POST_REVIEW.md` | 复审判据正典（O-2115·判据前置+确定性重derive+三态标注） | 活·每轮 |
| `research/SCIENCE_AUDIT_PREREG.md` | 月度科学审计 C1-C5 判据冻结 | 活·月度 |
| `research/T28_STABLE_PROFIT.md` §4 | SPM 族 J1-J5 冻结判面（SPM_REGISTER 引用） | 活 |
| `research/PREREG_TEMPLATE.md` | 预注册模板（α 机制段四选一必填+同族 max\|corr\|≥0.7 拒收=D6） | 活·每批 |

**L1 观察靶（对应令文「判决体系碎片化」——枚举证实）**：判据面按产品线并存至少六套——①交易员/交易线=G1'/G2/G3 门禁链+hr.py 考核；②组合/SPM=J1-J5（T28 冻结）；③激进线=AGGR 族 prereg KPI（NOCASH cap 0.95/其余 0.80 实验风险预算面）；④配置线=ALLOC mirror s2 cells 判据；⑤CN 线=各 prereg §s4 判据（REV-TILT/DIV-LOWVOL-ROT/REGIME-POLICY/CORE-SATELLITE/DDCTL 五片各异）；⑥纸盘族=anchor gates（COMPOSITE-CE-01/02 等）+t35 成交验证。**缺一张「判决体系总图」钉死每条产品线×每阶段用哪套判据**（令文预判靶 #1，s3 GM 件①）。防跨线挪用现有唯一护栏=各 prereg 显式引用判据面。

## L2 正典文件层（逐件·指针位 21）

| 文件 | 唯一职责（承各件头部定位声明） |
|---|---|
| `README.md` | 仓库入口总览 |
| `PLAN.md` | 路线图 P0-P4+§7 待办（开发范围正典）+§0 六条不可妥协 |
| `CODELY.md`（根） | 长效坑律/执行记录（42,973B·<50KB 水位内） |
| `firm/RULES.md` | **权与法**（T0-T3 分层立法权/红线台账指针/令牌路径/瘦法） |
| `firm/OPERATING_PLAN.md` | 运营总规划（跑什么·三阶段·节律表） |
| `firm/org_chart.md` | 组织 v5（见 L3） |
| `firm/SPM_REGISTER.md` | SPM 版本台账（append-only·v1 在册未过闸·J4 挂点） |
| `firm/STABLE_PROFIT_MODEL.md` | SPM 章程（§一登记簿纪律） |
| `firm/PRODUCT_MATRIX.md` | 产品矩阵（见 L4） |
| `research/PROFIT_MODEL_MAP.md` | 盈利模型作战图 v1.0（一页伞形·七层现状+两约束攻击线·随月度四件套更新） |
| `research/STRATEGY_LIBRARY.md` | 策略工厂实况总目（§一工厂/§二在册名单——org_chart 交易/策略部 mandate 指针所指） |
| `research/HANDOVER.md` | 产物清单与完成状态（**277,620B=全仓最大件**·5 倍数轮核对） |
| `research/BACKTEST_SCIENCE.md` | 判据宪法（见 L1） |
| `research/BACKTEST_PLAN.md` | 回测三铁律（随机基线同跑/N 计数/样本外恒盲） |
| `research/CEO_HANDBOOK.md` | CEO 汇报口径手册 |
| `research/RESEARCH_MECHANISM.md` | 研究机制（五步制） |
| `research/SYSTEM_LOGIC.md` | 系统逻辑总述 |
| `research/COMPUTE_AUDIT.md` | 算力审计章程（O-1810·五旗） |
| `firm/DEV_AUTOMATION.md` | 10min 自迭代循环机制 |
| `firm/TECH.md` | 技术栈约束 |
| `firm/LOCAL_FIRST.md` | 本地化路由三问（O-2325） |

**L2 观察靶**：①「四份战略件 48h 内先后落」实证——OPERATING_PLAN（O-2310 节律）/PRODUCT_MATRIX/PROFIT_MODEL_MAP（O-0857·09-25）/SPM_REGISTER（O-1105·09-25）互指已具雏形但**文档层级表（谁管什么·层级序）未定义**（s3 GM 件③）；②HANDOVER.md 277KB 体量与「根级文档低频编辑」纪律张力——归档分层候选（s2 检测面）；③指针纪律现状良好（RULES 薄法指针式、各件头部定位声明普遍在位）——优化面=把「层级定义」补上而非重写内容。

## L3 组织层（org_chart.md v5 实测）

- **9 部门**（mandate/域指针/KPI/自动化钩子/升级线五列）：研究部·策略部·交易部·风控部(含审计)·数据部·工程部·舰队部·组合与资金部·总经办。
- **11 团队**（全挂 Phase 0/1 交付·AUDIT-20260924-ORG §一零空壳判定）：组合构建·现金腿与资金运营·经营分析与月报·PK 赛制·J13 本地助理·政体研究·执行质量与实盘预备·对外引擎服务·科学审计·双源与核名·盯防与算力运维。
- **交易员阶梯**：INTERN(0 资金)→TRAINEE(模拟盘)→TRADER(5%)→SENIOR(15%)→PRINCIPAL(30%)；淘汰=连续 2 月不达标。
- **L3 观察靶**：KPI 面刷新滞后（令文预判靶：研究部现供交易/配置/激进/CN/野路子 5+ 条线而 KPI 列仍是三词老面；总经办已加战报面 T-75/daily_report——两列均为 s3 GM 件④「KPI 刷新」输入）。车队部 mandate 已含三机车道分工+周期任务轮值（09-24 立法）——无冲突。

## L4 产品线层（PRODUCT_MATRIX 四轴 17 行实测 + 线状态单源候选）

矩阵现状：✅8（短线波段·长线配置·A 股·ETF·债/金/QDII·三线三判·择时α·配置β）·🟡5（中线摆动·REITs·商品期货·事件驱动·套利carry）·⬜4（转债·金融期货·期权·港股通/北交所/现券）。

| 线 | 状态（实测载体） |
|---|---|
| 交易线（ETF 波段） | 在产：core48·6 在册+PROSPECT 22 观察（anchor gates 每轮 smoke PASS） |
| 配置线 ALLOC | 在产：T-59·7 账户 mirror frozen s2 cells（alloc_paper/） |
| 激进线 AGGR | 在产：T-56·5 账户 ¥1M（aggr_paper/·marks 日累） |
| GRID 网格线 | 已接线：engine/grid_sleeve.py+grid_paper 脚本（r245）·**marks 首跑=09-28 窗**（grid_paper/ 目录未物化如实） |
| CN 原生线 | s3 六片批跑收尾：REV-TILT 判负收线（r252）/DIV-LOWVOL-ROT/REGIME-POLICY/CORE-SATELLITE 已落地·DDCTL 在飞（bm-a 车道） |
| 野路子 | WILD-S1 池批 done（wr-1..8of8）·T-57 股票短线开线 |
| 期权/债券/转债 | 数据道在采（T-69 wave-2b 前向采集·T-68 债券面板 done）·转债⬜ 空白（集思录源已验） |
| 期货 | CTA 三连判负归档（O-1158 授权复活批 gated on 新预注册） |

**L4 观察靶**：线状态现散在 PRODUCT_MATRIX（轴面）/PROFIT_MODEL_MAP（七层现状）/STRATEGY_LIBRARY（工厂实况）/HANDOVER（产物清单）四面——**需一表单源**（令文 L4 靶·s3 关联件；zoo 升格 L7 靶同源）。

## L5 账户生命周期（准入链四环·载体枚举）

链（承 RULES §1+O-2045/1326）：**判决（G1'/G2/G3 注册）→ 纸盘（paper/PROSPECT 观察）→ CEO 认可（docs/CEO_APPROVALS.md 台账）→ 模拟盘准入 → 实盘门（CEO 保留·2027-04 判据未触发）**。

| 载体 | 环 |
|---|---|
| `firm/hr.py`（阶梯/晋升/淘汰执行面） | 全链 |
| `research/CE_ADMISSION_V1.md`+`CE_ADMISSION_INTAKE_B1_PREREG.md` | 判决→注册（CE 正典层稳定优先准入） |
| `research/PROFILE_CARDS_P1.md`（17 画像卡）·`L3_ACTIVATION_EVIDENCE.md`·`LANDING_HOOKS_P1.md` | 适用域画像/激活证据/落地钩子（T-81 三片·O-1342） |
| `research/PAPER_GUARD_DUAL_RAIL.md` | 纸盘守卫双轨 |
| `research/RETRO_PAPER_2026_PREREG.md` | 年内回放纸盘（T-79·回放榜） |
| `live/`（__init__/gateway/paper 3 面） | 模拟盘执行面（锚定门禁+REGIME_GUARD） |
| `docs/CEO_APPROVALS.md` | 认可台账（O-1326 认可+模拟盘网关队列） |
| `scripts/t24_prospect_promotion.py`（PROSPECT→INTERN 门） | 观察池晋升评估 |

**L5 观察靶**：四环在机制上全部已建（hr.py/CE_ADMISSION/CEO_APPROVALS/live 锚定链各有实跑），但**无一册「账户生命周期正典」把五段串明**（令文 L5 靶·s3 GM 件②）。现状链序=从各令/票拼合（本表即拼合证据）。

## L6 账户族（11 族目录实测+1 接线未物化）

| 族 | 目录（results/） | 规模 | 归属报告面 |
|---|---|---|---|
| 真账本 paper | `paper/` | 6 员 | t35/daily_scorecard/CEO 面 |
| PROSPECT 观察池 | `prospect_paper/`+`prospect_g2/`+`prospect_promotion/` | 22 员 | 观察面（构造性排除 CEO 面·O-2045） |
| AGGR 激进 | `aggr_paper/`+`aggr_capacity_face/` | 5 账户 ×¥1M | 独立车道（不入 t35/scorecard CEO 面） |
| ALLOC 配置 | `alloc_paper/`+`alloc_s2_cells/`+`allocation/` | 7 账户 mirror | 独立车道（marks 观察账本） |
| GRID 网格 | `grid_paper/`=**未物化**（r245 接线·09-28 首跑窗） | 5 cells 计划 | 独立车道 |
| 回放纸盘 | `retro_paper_2026/` | 17 台账（r252） | 一页榜呈 CEO |
| 城侧导出 | `paper_export/` | 6 员持仓/操作/资本 | 只读消费面 |

**L6 观察靶**：族在增殖（09-24 三族→09-26 六族车道+回放+导出）而**注册表/命名/本金/报告归属规范未单源**（令文 L6 靶·s3 关联件；车道隔离纪律现散在各接线令+票 spec——本表首度聚合）。

## L7 研发管线（五步制+池+队列）

| 机件 | 载体（实测） |
|---|---|
| 五步制/供给节律 | `research/RESEARCH_MECHANISM.md`+`OPERATING_PLAN.md`（外源波 6 链·常态双频立法） |
| 预注册 | `PREREG_TEMPLATE.md`+14 件 PREREG 正典（AGGR 族/BOND/CE×2/CN×5/CTA/OPTIONS/RETRO/SCIENCE_AUDIT/WILD）——跑前冻结纪律全程实证（R245/R250 一段式种子登记律后零撞号） |
| 池 | `results/runnable_pool.json` 49 批（done 48·ready 1=CN-CORE-DDCTL-P1 bm-a 在飞）；landed→收割律 R244（轮首 S3 优先翻池） |
| 自动续批 | `Tools/autofill.py` watchdog（tick 跳过循环 r252 修正版·crash-fuse·lane 归属护栏） |
| 探索-利用 | `research/QUEUE_BANDIT.md`+`results/bandit_queue.json`（advisory-only）+`results/watermark_red.json`（next_pick 面） |
| 损耗账 | `results/gate_attrition.json`（38,216B·G1'→G2→注册死亡率）+trials 分布式账本（各批 JSON 内嵌 trials_ledger 块·链头=max-total·R252 修链后单计） |
| 算力审计 | `research/COMPUTE_AUDIT.md`+`scripts/compute_audit.py`（五旗）+`scripts/py_watermark.py`（水位探针） |

**L7 观察靶**：候选线库存（活/死/判负一表可查）现无单源载体——**zoo 升格**（令文 L7 靶）；判负线档案现散（PROFIT_MODEL_MAP §五诚实链+各 prereg s7/s8+CODELY.md 行）。

## L8 机队机制（Tools 32 件+scripts 216 件实测）

| 机件 | 载体 | 状态 |
|---|---|---|
| 10min 循环 | `Tools/iteration_loop.ps1`+`register_loop_task.ps1`（schtasks 正典）+`iteration_prompt.txt`（规格钉死·R262 T 分隔律） | 活·bm-a/bm-b 双机在跑 |
| 看门狗 | `Tools/watchdog.ps1`+`register_watchdog_task.ps1`+`watchdog_c7_selftest.ps1`（30min·治循环自死） | 活 |
| 自动续批 | `Tools/autofill.py`+`register_autofill_task.ps1`+`loop_lock_selftest.ps1` | 活 |
| 复审 | `Tools/post_review.py`+`results/post_review.jsonl`（1,010 行）+`results/post_review_criteria.json` | 活（1010 行·689 YES/316 WAIT/5 NO 全被后续轮翻正·债=0） |
| 心跳 | `fleet/machines/{bm-a,bm-b,bm-c}.json`（epoch int+clock_read T 分隔·smoke F7 每轮验） | 活·3 机（bm-c 停摆如实） |
| 传输 | `fleet/TRANSFER.md`+`transfer_manifest.ps1`（大件禁入 git·EOL 方向律 r257） | 活 |
| 令差集 | `Tools/orders_diff.py`（Ack format contract 头注·r251 律） | 活 |
| 盘中道 | `register_intraday_marks_task.ps1`+`t36_drill_runner.py`（演练） | 活 |
| 一次性解器 | `_r190_af_union.py` 等 **13 件**（r190-r210 冲突解/收割/翻面残件） | **残件=归档候选** |
| 坑律语料 | 根 `CODELY.md`（40+ 律·42,973B<50KB 水位）+`install_scorecard_shortcut.ps1`+`bootstrap-machine.ps1` | 自优化在飞（令文 L8 判语=保持） |

**L8 观察靶**：①13 件一次性解器滞留 Tools/ 正典位——归档不删（纪律 3）候选；②复审登记面已知缺口已修（r264 正律=检查锚稳定产物件）——令文「保持」判语正确。

## L9 令面（83 令实测·索引缺）

- 全量 83 令机器面=快照 JSON `L9_orders`（逐令 id/字节/标题/取代面标记）；本件指针不复制。
- 分布：09-23=28 · 09-24=33 · 09-25=13 · 09-26=9（令速=26h 内 ~30 道 CEO 直令，与令文预判一致）。
- **取代/让路/作废/收回面 9 令**（取代链正典化输入）：O-0923-1705(让路)·2134(收回)·2205(废止)·2210(作废)·O-0924-1136(取代)·1730(作废·即时律取代面)·2012(作废)·O-0925-2313-bm-c(让路)·O-0926-1355(取代)。
- **L9 观察靶**：无令索引载体（谁 supersede 谁、生效面/作废面分栏）——陈令误引风险敞口=9 令现存文本仍可被引用而不知其被取代（s3 GM 件关联·机械面=s2 可先出取代链清单）。

## s2 输入汇总（十观察·未动刀·检测面待跑）

| # | 层 | 观察 | s2 检测法（机械可跑） |
|---|---|---|---|
| 1 | L1 | 判决体系六套并存无总图 | 逐 prereg/judgment 载体 grep 判据引用→产品线×判据面矩阵 |
| 2 | L2 | 战略件层级未定义 | 头部定位声明交叉比对+互指链接完整性 |
| 3 | L2 | HANDOVER.md 277KB | 体量/编辑频率/引用面 census |
| 4 | L3 | KPI 列滞后（研究部/总经办两列） | mandate 实况（5+ 线）vs KPI 文本 diff |
| 5 | L4/L7 | 产品线状态四面散 | 矩阵行 vs MAP 七层 vs LIBRARY 实况一致性 |
| 6 | L5 | 生命周期无串册 | 环载体在位性五段核 |
| 7 | L6 | 账户族注册表缺 | 12 族×命名/本金/归属枚举 |
| 8 | L8 | 一次性解器 13 件滞留 | mtime+引用扫描→归档清单 |
| 9 | L9 | 令索引/取代链缺 | 83 令全文取代词扫描→取代链图（快照已带首词标记） |
| 10 | L9 | 陈令误引敞口 | 已作废/被取代令号在 git log/轮报告的引用扫描 |

—— s1 完 · bm-b r267 · 2026-09-26 19:0x · 复审锚=本文件+快照 JSON+枚举器 selftest 7/7（post_review 注册行 T-83-S1）
