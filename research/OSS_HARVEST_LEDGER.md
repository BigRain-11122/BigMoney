# OSS 引进管线扫描台账 v1（OSS_HARVEST_LEDGER）

- 令源：O-20261007-2245-bm-c（CEO 直令「外源引进优先·自研兜底」·供给排序律修订正典级）。
- 本件=@bm-a 管线主建首件（扫描清单台账·大限 2026-10-10 12:00）；首批策略类 5 件适配回放验证大限 10-16 12:00。
- 方法律：借力律铁面（外源宣称=未验证假设·适配后走本方大样本回放+成本压测+纸盘试用同一门禁链·**拿来≠免检**）+ 反重复纪律（每件引进前必查负结果库：MOM 族 0/4920·时钟 0/228·野路子 0/1569 判负在案族不得借引进复燃）+ 许可律（MIT/Apache 直用·署名型登记·**AGPL 禁入** spark-arc-studio 判例）。
- 五门评估字段：契合 / 反重复 / 许可 / 健康（star·维护活跃度）/ 成本（适配工时预算·单件 ≤8h 首过筛）。
- 引进件过全门上桌者入池编号带 **OSS-** 前缀（收养三律照常）。
- 数据纪律：star 数带取数源与日期（禁编数）；GitHub MCP search 工具本机解析故障（既知坑）→ web 搜索双源交叉。

## 一、策略类首批扫描（O-2245 §二清单）

| # | 件 | 出处 | star（源·日期） | 许可 | 契合初判 | 反重复初查 | 健康度 | 成本预算 | scan 状态 |
|---|---|---|---|---|---|---|---|---|---|
| S1 | **qlib**（因子+AI 模型双面·含 RD-Agent 自动研管） | github.com/microsoft/qlib | ~44.4k-49.2k（finds.dev 2026-04 / star-history 双源） | MIT | 高——AI 因子面与我方门禁链互补；ML 管线可作研究基础设施对标 | 零撞负结果库（AI 因子族未判负·alpha191/WorldQuant 腿已有=扩全候选） | 活跃（2026-04 仍更新·Python） | ≤8h 首筛：因子库面抽取+数据口径适配 | **已扫**（r846 首件） |
| S2 | **vnpy 策略集+vnpy.alpha 4.0**（ML 多因子模块·36.7k★） | github.com/vnpy/vnpy | 36.7k（githublb 2026-02）·v4.3.0 | MIT | 中高——A 股原生 T+1 语境同源；策略模板可移植入我方回测口径 | 零撞（CTA/网格族在役=取模板不取判决） | 活跃（2026-01 push） | ≤8h 首筛：策略模板抽取+T+1/费率口径转换 | **已扫**（r846 首件） |
| S3 | awesome-quant 谱系（清单型入口） | github.com/wilsonfreitas/awesome-quant | 待精核（下窗 GitHub 页直读） | 各件异 | 入口型——从谱系筛 A 股适配件 | 待逐件查 | 待评 | 入口扫描 2h | 待扫（10-09 前） |
| S4 | 聚宽·掘金社区策略移植 | joinquant/.myquant 社区 | 社区型（非 GitHub star 面） | 逐件核（社区策略多为署名转载·许可逐件登记） | 高——A 股原生打法优先（游资情绪/题材面候选池） | 逐件过负结果库（MOM 族判负在案·禁复燃） | 逐件 | 逐件 ≤8h | 待扫（10-09 前） |
| S5 | 游资情绪指标开源实现（A 股原生优先） | 待定位（搜索面：open源 情绪周期/龙虎榜实现） | 待扫 | 待核 | 高——CEO 研究导向哲学（国内打法为纲）+ O-2215 REGIME-5 护盘期判据供给候选 | 待查 | 待评 | ≤8h | 待扫（10-09 前） |

## 二、适配层规格（统一口径转换面·r846 起草）

1. 数据面：外源件默认 OHLCV/因子输入 → 转换入本方 core48/个股面板（qfq·前向窗·evidence_cutoff 冻结律）。
2. T+1：外源默认 T+0 回测假设 → 统一加 T+1 开盘成交保守代理（O-1132 口径）。
3. 费率/滑点：统一 x1 13.041bp/边 + 成本压测三档（x1/x2/x3）。
4. 出场轴显式门（O-20261001-1108）：外源策略出场规则必显式登记三选一，缺=不冻结不烧。
5. 大样本律：适配件回放 ≥K1000 随机时点 + 纸盘试用期（千级矿先廉价普查 gate_census 范式）。

## 三、出账与回访

- 吃单率指标（过初筛门数/扫描数·首批目标 ≥30%）入 10-21 回访（与 O-2215/O-2230 同窗）。
- 下一窗指针：S3/S4/S5 三面补扫（10-09 前）→ 首批 5 件定选 → 适配层首件实跑（qlib 因子面优先）。

（r846 bm-a 首件·后续轮增量 append·禁改既有行）

## 四、工程类首批扫描（@bm-c 车道·O-2245 §三·r706）

- 取数法=scripts/oss_eng_scan.py 直读 api.github.com /repos（源注日期·禁编数·本表全部 2026-10-07 23:32 复跑实取·首跑 23:31 同数零漂移）；证据件 results/oss_eng_scan/scan-20261007.json（fetch ok=13 fail=1·rc1 partial 诚实披露）。
- **负结果库联动实装**：探针加载 gate_attrition 四件全 token 1434 个逐件交叉——工程类 15 件 dup 全 clean（MOM/时钟/野路子判负族零撞·工程族与策略判负族构造性不相交=联动面成立）；在役线命中 2 件（akshare/tushare=已用通道，登记不引进）；在飞件注记=vnpy 携 CTA 模板面与 CTA_P1 在飞（O-2215②）交叉，只取模板不取判决。
- 许可门活捕获：**backtrader=GPL-3.0 禁入**（最著名 Python 回测库踩雷=许可门实证）+nautilus_trader=LGPL-3.0（非 MIT/Apache 桶·按保守面暂判禁入·待集团收获机制裁定）；vectorbt/rqalpha=NOASSERTION 待逐件核 license 文件。

| # | 件 | 出处 | star（api.github.com·10-07 23:31） | 许可 | 健康门 | 契合初判 | 反重复 | 成本预算 | scan 状态 |
|---|---|---|---|---|---|---|---|---|---|
| E1 | backtrader | mementum/backtrader | 23,413 | **GPL-3.0→禁入** | FAIL（push 停滞） | 事件驱动引擎·出场栈参照 | clean | 8h | **已扫·禁入** |
| E2 | vectorbt | polakowo/vectorbt | 9,290 | NOASSERTION→待核 | PASS | 向量化网格扫描·N1 吞吐参照 | clean | 8h | **已扫·待核许可** |
| E3 | nautilus_trader | nautechsystems/nautilus_trader | 29,681 | **LGPL-3.0→保守禁入** | PASS | 生产级引擎·实盘执行架构参照 | clean | 8h | **已扫·待集团裁定** |
| E4 | zipline-reloaded | stefan-jansen/zipline-reloaded | 1,959 | Apache-2.0 | PASS | 管线式引擎·point-in-time 纪律参照 | clean | 8h | **已扫·全过** |
| E5 | RQAlpha | ricequant/rqalpha | 6,815 | NOASSERTION→待核 | PASS | A 股原生 T+1 引擎·费率/板规口径对标 | clean | 8h | **已扫·待核许可** |
| D1 | akshare | akfamily/akshare | 22,849 | MIT | PASS | 在役（sina 直连通道）·成本/稳健台账面 | clean+在役 | 2h | **已扫·在役登记** |
| D2 | tushare | wadefu/tushare | 仓 404（SDK 现走 pypi/官网） | 待核 | UNVERIFIED | 在役（CEO token 已授权）·备份通道 | clean+在役 | 4h | **已扫·源缺诚实披露** |
| D3 | easyquotation | shidenggui/easyquotation | 5,453 | MIT | PASS | 轻量实时行情库·盘中道候选 | clean | 4h | **已扫·全过** |
| G1 | APScheduler | agronholm/apscheduler | 7,647 | MIT | PASS | 进程内调度器·Windows 机队循环加固候选 | clean | 4h | **已扫·全过** |
| G2 | healthchecks | healthchecks/healthchecks | 10,386 | BSD-3 | PASS | 自托管 dead-man 哨兵·静默律看门狗面 | clean | 4h | **已扫·全过** |
| G3 | uptime-kuma | louislam/uptime-kuma | 92,185 | MIT | PASS | 自托管活性面板·机队/daemon liveness 面 | clean | 4h | **已扫·全过** |
| G4 | prefect | PrefectHQ/prefect | 23,983 | Apache-2.0 | PASS | 重量级 DAG 调度·控制面参照（与 git 控制面契合低） | clean | 6h | **已扫·全过·参照件** |
| B1 | vnpy（工程面=网关腿） | vnpy/vnpy | 45,743 | MIT | PASS | 券商 API 适配+CTA 模板（策略面 S2 已扫） | clean+在飞注记 | 8h | **已扫·全过** |
| B2 | easytrader | shidenggui/easytrader | 10,214 | MIT | PASS | 券商客户端自动化·纸盘→实盘桥候选 | clean | 8h | **已扫·全过** |
| B3 | xtquant/QMT SDK | 官方分发（无 canonical GitHub 仓） | n/a | 待核（vendor docs） | n/a | QMT mini 官方 SDK·实盘对接候选 | clean | 8h | **已扫·vendor 面 PENDING** |

- 引擎族定性（O-2245 §二原文）：回测引擎=「我们自研引擎的补短板参照」——E2-E5 为**参照件**（对标用·代码级借用须过许可门）；引进件候选=网关/调度/数据面。
- bm-c 车道工程类初筛过门率 8/15（≥30% 目标线达）·适配首件建议排产：G3 uptime-kuma（机队活性面板·4h）>G2 healthchecks（dead-man 哨兵·4h）>B2 easytrader（实盘桥预研·8h）；入池编号带 OSS- 前缀（r705 schema 9 字段已备）待适配工单开立后落池。
- 复扫通道：探针幂等可重跑（python scripts\oss_eng_scan.py·star/push 活取）；NOASSERTION 两件下窗核 LICENSE 文件后翻面。

（r706 bm-c 工程类腿·后续轮增量 append·禁改既有行）
