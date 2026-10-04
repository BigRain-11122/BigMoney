# BigMoney《SOP 盘点与补建清单》v1.0

- 令源：CEO 全集团 SOP 建制令（registry O-2026-0930-027·09-30 ~23:0x·委员会通道·九司+CPH4 承接；补录找回=集团 orders.md 38c4f2d 2026-10-04 23:19）。
- 出具：BigMoney 总经办（bm-c r502·2026-10-04 23:3x·假期窗内提前交付）；聚合审=10-07 治理日委员会。
- 双闸自检：①轻量闸=本件 57 行 <200 行/25KB 上限；②判据前置闸=每在册项带可执行判据/机器可验面，每缺口项带验收判据（§三）。
- 对标总依据：O-022 标杆定谳律（行业最新最顶尖对标）+O-025 工作流迭代令+本仓 150+ 轮实证判例族；逐项对标锚见行内「对标」列。

## §一 三级盘点·在册清单（业务线 / 司内部门 / 开发模块）

### 1a 业务线级（产品与经营面）

| SOP 件 | 面 | 对标 |
|---|---|---|
| firm/STABLE_PROFIT_MODEL.md | 稳定盈利总模型（产品纲领） | 实战出真知判据=回测+纸盘双基准跑赢（results/beat_market.html 6/6 在册） |
| firm/PRODUCT_MATRIX.md | 产品矩阵（策略/账户/实验三轴） | 矩阵完整性=board/pool/ledger 三台账对账（S6 dualrun 零漂移 streak 机验） |
| firm/OPERATING_PLAN.md + firm/portfolio.md | 经营计划+组合管理 | 里程碑=state.next 窗口可验（≤48h 窗律） |
| research/CEO_HANDBOOK.md（载体=scripts/ceo_live_usage.py） | CEO 实盘使用一页纸 SOP | 大白话律 O-22:44（外行 10 秒看懂）+每日幂等再生（docs/live_usage/ 生成物） |

### 1b 司内部门级（mandate/纪律/治理面）

| SOP 件 | 面 | 对标 |
|---|---|---|
| firm/RULES.md + firm/org_chart.md v2 | 顶层权与法+部门 mandate/KPI | CEO 授权令 O-1620（P1 总经理署名自决面） |
| firm/DECISIONS.md + firm/JUDGMENT_MATRIX.md | 决策记录规约+判决矩阵 | 判决=预注册冻结判据消费（E1 判决链机验） |
| firm/ACCOUNT_LIFECYCLE.md + firm/SPM_REGISTER.md | 账户生命周期（PROSPECT→INTERN→…）+策略注册 | 晋升门=t24_prospect_promotion.py 三腿机验（月≥1+G2 包+beat_rate≥0.70 冻结口径） |
| firm/STYLE_CORPS.md + firm/STRATEGY_EVALUATION.md | 流派军团+策略评估 | 三卡画像=scripts/strategy_scorecard.py 每轮再 derive（17 画像卡机验） |
| firm/TECH.md + firm/DOC_HIERARCHY.md + firm/DEV_AUTOMATION.md | 技术栈+文档层级+开发自动化 | 文档层级=smoke 48 项含心跳/钟面契约（F7 机验） |

### 1c 开发模块级（科学/工程/数据/机队面）

| SOP 件 | 面 | 对标 |
|---|---|---|
| research/BACKTEST_PLAN.md（三铁律）+BACKTEST_SCIENCE.md+BACKTEST_READINESS.md | 回测纪律 | 业界回测过拟合纪律（Bailey/López de Prado CSCV·PBO——science_gates 在册实现）+样本外恒盲/成本恒开/N 登记三铁律 |
| research/PREREG_TEMPLATE.md | 预注册范本（α 机制四选一+D6 同族门+出场轴显式门） | OSF 预注册规范（判据先冻结后跑·禁看结果改阈值） |
| research/SCIENCE_AUDIT_PREREG.md + firm/SELF_REVIEW.md + firm/POST_REVIEW.md | 月度科学审计+自审+复审 | SRE 定期审计/验收惯例（findings 只报不阻断+✗ 行=下轮 P0 机验） |
| firm/TRIAL_LABOR_LAW.md + SATURATION_ENGINE_LAW.md + COMPUTE_AUDIT.md | 试用劳动力常设线+饱和引擎+算力审计 | SRE SLO/算力利用率行业惯例（py≥70% 验收线+五旗机验） |
| firm/RANDOM_LARGE_SAMPLE_LAW.md + REFINE_BENCH_LAW.md | 随机三律+见即淬炼 | 大样本统计律（K≥1000/N≥500/分窗）统计学正典 |
| firm/TREASURE_PROTECTION_LAW.md + knowledge/METHODOLOGY_ASSETS.md + TREASURE_REGISTRY.md | 宝藏保护+方法论资产卡 | 数据保全/登记簿审计行业惯例（treasure_guard prescan rc3 硬拒+quarantine 7 天窗机验） |
| firm/LOCAL_FIRST.md + scripts/llm_assist.py | 本地化路由（L1/L2/云端回退） | 双轨制令 O-2026-0930-028（质量硬红线+效率可让·10-04 补录） |
| research/RESEARCH_MECHANISM*（外源常态线 v1.1） | 外源借力研究供给 | CEO 借力律 O-1721（外源=未验证假设·独立验证归本方门禁链） |
| research/pit-*.md 13 域分件（git/engine/pool/protocol/data/ps/encoding/spawn/tooling 族） | 操作坑律正典（域分件） | 团队 Wiki/事故库行业惯例（件内字节对账+md5 零丢失断言机验） |
| 数据采集 spec 族（shortline/{PC_COLLECTOR,MF_COLLECTOR,SINA_MF_PREREG,THS_PANEL,AH_PANEL,FUND_STATEMENT_PANEL,REPO_PANEL}.md+etf_ops/MINUTE_FEED.md） | 采集器契约（no-op 门/分离后台/overlap 校验/exit-code 契约/车道护栏/selftest） | 数据管道 CI 契约惯例（每件 selftest 子命令离线机验） |
| fleet/README.md + fleet/FLEET-OPS.md | 机队多机规则+轮协议 | 分布式协作协议（claim-by-file/D-19 水位内容寻址机验） |

## §二 缺口清单（补建候选·每窗 ≥1 件·夜窗/自驱轨承接·不占业务车道）

| # | 缺口 | 现状证据 | 验收判据（判据前置） | 排期 |
|---|---|---|---|---|
| G1 | 事故复盘 SOP（postmortem 模板：穷查面/根因不可全证处理/重跑幂等链） | 散件在案（r497 W3 judge 死亡穷查/MSG-2130 无单件模板） | 单件 ≤200 行；模板含四节（实证面/根因三态/恢复链/防复发）；下次长批死亡事件按模板落件=验收 | 10 月窗 1（夜窗） |
| G2 | 实盘开闸前检查单 SOP（paper→live gate checklist） | 散在 RULES+CEO 令（开闸=CEO 唯一门在册，无单件检查单） | 检查单含 beat_market 六基准绿+月界考+风控闸+CEO 签面四节；scripts 侧可跑一页自检脚本 | 10 月窗 2（10-31 月界首考后夜窗） |
| G3 | 数据源健康分级与降级登记 SOP（子域分块判据族单件化） | 判据散在 PC_COLLECTOR L11+pit-data.md（F-20260923-06 在册） | 单件含分级（活/限流/阻断）+降级登记动作+恢复自愈判据；与既有 conn-fuse/隔离机制对表 | 10 月窗 3（随开市 10-09 数据链 re-arm 夜窗） |

## §三 双闸自检与呈报

1. 轻量闸：本件 57 行（<200 行上限）——SOP 服务业务非业务服务 SOP；本件=盘点载体不新立法（新立法须 CEO 令/立法窗授权，本件全部内容=在册件指针+缺口候选排期）。
2. 判据前置闸：§一每行带机验面指针（脚本/断言/台账），§二每缺口带验收判据；无对标项=G1-G3 均已给对标锚（SRE postmortem 惯例/上线 gate 惯例/数据管道分级惯例）。
3. 呈报面：本件随轮 commit push（registry 回执=委员会 10-07 聚合审收取面）；O-2026-0930-028（双轨制）本司面=P-32 心跳字段已在册（cores/RAM/VRAM/gpu_model 四字段 fleet/machines/*.json 机验）；O-029（卡点堵点）本司输入=轮台账常态供给（值班轮聚合面）；O-030（思考预算律）=executed 态照录，本司无人值守轮 executive protocol 已在极简协议审计面（state/runbook 面随 SELF_REVIEW F 项机验）。
