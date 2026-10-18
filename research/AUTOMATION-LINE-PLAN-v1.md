# BigMoney 自动化条线建设案 v1（世界一流五要素）

> 令源：集团自动化条线扩面令（CEO 2026-10-18 20:48 原话「其他子公司也去打造世界一流的自动化条线」）+ 九司方案呈报令（CEO 2026-10-18 21:11 原话「每个子公司都给我列出来方案」）。集团基线件=cph4/fleet/GROUP-AUTOMATION-PLAN-v1.md（BigMoney 节）；本件=该节的建设案细化正身。
> 死线：建设案随委员会三合一呈报 ≤2026-10-25；首线实装验收 ≤2026-10-31。
> 现状测量面：`python scripts/automation_line_audit.py`（每轮可跑·只读确定性零网络·产物 `results/automation_line_audit.json`·本件 §一 数字全部由该面机读派生，禁手抄——复测以该面最新 run 为准）。

## §一 现状五要素映射（首测锚=2026-10-18T23:27:54+08:00 bm-a r1069）

| 要素 | 判定 | 实测证据 |
|---|---|---|
| E1 循环驱动（24/7 无人值守自续） | **OK** | 心跳龄 <10min·轮报告龄 <20min（IterationLoop 10min 节律+S4U 全静默链在役）；W 波=自跑范式已验证（W272 全周期 CLOSED 10-18 一窗收官·W273 席已发布 owner=bm-c） |
| E2 自领活自愈（队列空自动领·故障自动重启续跑） | **OK（面在）** | idle_trigger 腽在役（green_idle/claimable 双字段）·backlog 可领行=0·runnable_pool=0·BmaIdleGuard 10min 守卫过渡版在役（r1068 部署·候 canon kit 上链 adopt）；claimable 0/0=供给面缺口归 §二 G 面，非机制缺位 |
| E3 质量闸在环内（判负关线/预算执法/假绿判据） | **PARTIAL（核心缺口区）** | 注册侧闸全在：CLOSED_FAMILIES 登记簿+queue_seed_gate 阻新登记+pre-commit 冲突标记钳；**运行侧三缺**：判负关线烧批续燃面无 CLOSED_FAMILIES 硬拒（G1）·预注册预算无运行时自动停（G2）·saturation_engine 忙闲判定无可点火件交叉面（G3 假绿·SLI-RECONCILE 判例 2026-10-15） |
| E4 日进化（每日好/坏总结+跨线回灌） | **OK（账面在）** | docs/daily_report/REPORT-* 新鲜（<2 日）·每轮自动再生；「好/坏」定性总结节=待 A2 归因日账面一并升级（现=四面上聚合，无盈亏归因轴） |
| E5 定位律（每轮自检「推进哪条业务哪个指标」） | **PARTIAL** | 近 5 轮报告实测等待占比 1.0（r1065-r1068 连续等待态维护轮）——产品优先律计分面已立（2/1/0 分制）但连续产品轮供给不足=排产面缺口（本件 §三 A 面直接对症） |

## §二 缺口清单（G 面·全部为 CEO 令点名件）

- **G1 判负关线运行侧自动执法缺位**：注册侧已闸（closed family 禁新登记），但烧批续燃器（Tools/autofill.py）点火前不查 CLOSED_FAMILIES——判负后关线靠人轮宣停。
- **G2 预注册预算自动执法缺位**：PREREG_TEMPLATE 预算上限字段在（冻结面），无运行时超限自动停——超限靠「亮牌合法停」人宣。
- **G3 假绿判据未修正**：saturation_engine busy/idle 判定无「可点火件」交叉面——结构等待池卡被计成有活（假绿→满载误判）。
- **G4 盈亏归因日账面缺位**：daily_report.py 实测无 PnL/归因面（has_pnl=False）——日账无「钱从哪条腿来/哪条腿亏」。
- **G5 W 波循环正式化缺位**：自跑范式已验证但未正典化为公司标准产线律（现=事实标准，非成文法）。

## §三 建设排期（10-19 起·小步可验证闭环保序）

| 批 | 窗 | 建设件 | 验收物 |
|---|---|---|---|
| A1 | ≤10-21 | G3 假绿修正：saturation_engine 忙闲判定加 claimable 交叉面（结构等待≠可点火活） | 引擎 selftest 含假绿反例断言+一轮实弹 idle 判定带双面读数 |
| A2 | ≤10-23 | G4 盈亏归因日账面：daily_report 增盈亏归因节（纸盘六员+实验账户按 sleeve/腿归因，缺数据如实标注） | REPORT-*.md 归因节连续 ≥3 个交易日+daily_report selftest 腿 |
| A3 | ≤10-24 | G1+G2 运行侧执法：autofill 点火前 CLOSED_FAMILIES 硬拒+在池批带 budget_cap 运行 tick 超限自动 DISABLE 并曝光 | 两件 selftest 断言+一次实弹拦截证据（假种子/超限批被拒入账） |
| A4 | ≤10-25 | G5 W 波循环正式化：firm/ 律位成文（自跑范式=公司标准产线循环）+本审计面入 S6 链提案+本件随委员会三合一呈报 | 律件上链+呈报回执 |
| A5 | ≤10-31 | 首线实装验收（§四判据全过） | 审计面 V5 连绿+验收记录 |

排产纪律：A1→A5 严格保序（每批一闭环·实弹验证后才进下批）；本审计面每轮复测跟踪 G 面收敛（GAP→PARTIAL→OK）。

## §四 验收判据（10-31·全部机读可验）

- V1 假绿修正：saturation_engine idle 判定含 claimable 交叉面，selftest 假绿反例断言在册；
- V2 归因日账面：REPORT-YYYYMMDD.md 盈亏归因节连续 ≥5 个交易日（缺数据如实标注合法）；
- V3 关线自动执法：closed-family 种子被烧批续燃面自动硬拒（selftest 断言+实弹拦截各一）；
- V4 预算自动停：超 budget_cap 在池批自动 DISABLE 并曝光（selftest 断言）；
- V5 五要素审计：`automation_line_audit.py` 五元素无 GAP 级分项（G1-G4 闭）连续 ≥3 天。

## §五 消费面与回执律

- 本件消费面=委员会三合一呈报（≤10-25）+集团 GROUP-AUTOMATION-PLAN-v1.md BigMoney 节细化指针（上链归 @quant 席/GM 面，BM 仓正身即本件）；
- 建设批 A1-A5 每批收口走轮报告回执一行+审计面复测读数（禁宣称完成以 selftest+实弹证据为准）；
- 判据冻结律照旧：本节 V1-V5 禁看结果调线；实现批预注册照 research/PREREG_TEMPLATE.md 起（涉科学判据面时）。
