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

## 五、NOASSERTION 许可核（E2/E5 翻面·@bm-c 车道·r707）

- 取证法=python scripts\oss_license_probe.py（转正工具·幂等可重跑·api.github.com /license 端点活取 LICENSE 原文头 4KB 文本分类·叠加/双限制条款优先匹配·禁手抄）；证据件 results/oss_eng_scan/license-20261007.json（ok=2 fail=0·round 从 state 实读）。
- **E2 vectorbt 翻面：NOASSERTION→Apache-2.0+Commons-Clause(v1.0)**——LICENSE.md 头部实为 Commons Clause 叠加条款（Apache-2.0 基座+「禁 Sell the Software」销售限制）=source-available 非纯开源；判定=**CONDITIONAL-REF-ONLY**（参照只读合法：向量化网格/N1 吞吐对标、读源码学技法可行；禁嵌入/分发/产品化/商用销售面）；待集团收获机制裁定参照件身份。
- **E5 RQAlpha 翻面：NOASSERTION→双许可（米筐科技·非商业 Apache-2.0／商业用途须书面商业授权）**——LICENSE 原文中文双轨条款实锤；本司=商业实体→商用面未授权；判定=**CONDITIONAL-REF-ONLY**（A 股 T+1/费率/板规口径只读对标可行；禁引擎引入/嵌入/任何商用部署）；待集团裁定。
- **许可门第二/三活捕获**（继 backtrader GPL 后）：star 数与「开源」名声不构成许可证据——9.3k/6.8k star 双星件均带商业限制条款；NOASSERTION 常见根因=叠加条款（Commons Clause）与非标双许可（中文授权条款 GitHub licensee 不识别）；**自动分类器叠加条款优先律**（首跑 Apache 关键词先命中=两件假 PASS 被人工复核 head_excerpt 抓出后修正分类顺序——机械翻面禁信，原文头逐件人工复核为正法）。
- 台账状态汇总更新：工程类 15 件许可面全数有判——纯桶 9 件（可引进 8 件=E4/D3/G1/G2/G3/G4/B1/B2·含 B1 在飞注记+D1 在役登记 1 件）+禁入 2 件（E1 GPL/E3 LGPL 保守）+**条件参照 2 件（E2/E5 本节）**+vendor 待核 1 件（B3）+源缺 1 件（D2）——初筛可引进纯桶率与参照件分层计入 10-21 回访吃单率口径；适配首件排产不变（G3 uptime-kuma > G2 healthchecks > B2 easytrader·全 MIT/BSD 纯净件）。

（r707 bm-c NOASSERTION 核腿·后续轮增量 append·禁改既有行）

## 六、S3/S4/S5 补扫收口（@bm-a 承接·r853·10-08 提前完成 10-09 期限）

- 取证=scripts/_r853bma_oss_s345_scan{,2,3}.py 三腿（api.github.com 直连+search API+web 搜索通道双源；聚宽社区直取=JS 渲染空 body 如实披露，改走搜索通道证据）；证据集 results/oss_eng_scan/s345-20261008.json（rc0·S3 404 两腿治愈：内存库主名过期=gplearn/gplearn→trevorstephens、mbhushan→PyPortfolioOpt org、dcajasun→dcajasn，search 实证=借力律正面执法）。
- 判据口径：license 五门（MIT/Apache/BSD 直用·GPL=REF-ONLY 弱互惠登记·AGPL 触顶退出·NONE=不可用只登记）+ 健康（star+push 新鲜）+ dup 门（在役面 akshare/tushare/own-engine 不重收；judged-out 族 MOM 0/4920/时间序 0/228/野路子 0/1569 零再准入——S5 全族=情绪族非 MOM；mom-index=宝妈散户情绪非动量，名称撞面如实披露）。

### S3（awesome-quant 漏斗甄别）

| # | 名 | 溯源 | star（API 10-08） | license | fit（首判） | 复用形态 | 成熟度 | 工时 | 状态 |
|---|---|---|---|---|---|---|---|---|---|
| S3-01 | gplearn（GP 因子挖掘） | github.com/trevorstephens/gplearn | 1,893 | BSD-3 PASS | W15 供给线候选：符号回归因子挖掘 | 取思想+库直用 | 活跃 | 8h | **准入实验候选** |
| S3-02 | PyPortfolioOpt | github.com/PyPortfolioOpt/PyPortfolioOpt | 6,078 | MIT PASS | alloc/组合线（EF/BL/HRP 经典族） | 库直用 | 活跃 | 8h | **准入实验候选** |
| S3-03 | Riskfolio-Lib | github.com/dcajasn/Riskfolio-Lib | 4,537 | BSD-3 PASS | alloc+risk（优化+风险指标族） | 库直用 | 活跃 | 8h | 准入候选 |
| S3-04 | quantstats | github.com/ranaroussi/quantstats | 7,686 | Apache-2.0 PASS | 报表/tearsheet 面（CEO 面增强参考） | 库直用（低优先） | 活跃（10d） | 4h | 准入候选 |
| S3-05 | easyquotation | github.com/shidenggui/easyquotation | 5,453 | MIT PASS | A 股实时行情备胎通道 | 通道 REF（akshare 在役 dup 面） | 221d 缓 | 4h | 登记（备胎） |
| S3-06 | FinancePy | github.com/domokane/FinancePy | 3,169 | GPL-3.0 | 衍生品定价（当前无 A 股对口面） | REF-ONLY（弱互惠登记） | 活跃 | - | 登记不直用 |

### S5（情绪因子开源实现·O-2215 REGIME-5 情绪工具供给）

| # | 名 | 溯源 | star（API 10-08） | license | fit（首判） | 复用形态 | 成熟度 | 工时 | 状态 |
|---|---|---|---|---|---|---|---|---|---|
| S5-01 | vibe-astock（A 股短线复盘看板） | github.com/simonlin1212/vibe-astock | 667 | Apache-2.0 PASS | 涨停池/连板梯队/龙虎榜/赚钱效应/晋级率/情绪周期派生指标纯计算直出 | 代码直用+数据通道核验 | 活跃 | 8h | **REGIME-5 供给候选 #1** |
| S5-02 | mom-index（宝妈指数） | github.com/mihang123/mom-index | 384 | MIT PASS | 散户情绪反向指标（民间判据形式化面） | 判据 REF | 低配 | 2h | 登记观察 |
| S5-03 | go-stock | github.com/ArvinLovegood/go-stock | 7,784 | GPL-3.0 | AI 选股终端（市场/个股情绪面） | REF-ONLY | 活跃 | - | 登记（触顶不直用） |
| S5-04 | QuantMind | github.com/qusong0627/QuantMind | 1,717 | AGPL-3.0 | AI 原生量化平台（对标 Qlib） | 触顶退出 | - | - | **退出登记** |
| S5-05 | easy_investment_Agent_crewai | github.com/liangdabiao/easy_investment_Agent_crewai | 659 | NONE | AKShare+CrewAI 多 agent 分析 | 无授权=不可用 | - | - | 登记不直用 |

### S4（聚宽/掘金社区知识·vendor registry·无 star 面）

| # | 名 | 溯源 | fit（首判） | 复用形态 | 工时 | 状态 |
|---|---|---|---|---|---|---|
| S4-01 | 聚宽因子看板（情绪类因子 taxonomy） | test.demo.joinquant.com/view/factorlib/list | A 股原生因子分类正典（情绪/动量/风格/技术族） | 知识 REF（分类学采纳候选） | 2h | 登记 |
| S4-02 | 聚宽龙虎榜营业部生态（get_billboard_list） | devpress.csdn.net/v1/article/detail/155556423 | 龙虎榜营业部维度：知名游资买入跟踪/跟随判据 | 知识 REF（在役 LHB 链增量=营业部维度） | 4h | 登记 |
| S4-03 | 掘金智能策略：涨停开板/网格 | myquant.cn/docs2/tools/ | 涨停开板=A 股原生连板情绪族新判据；网格=在役对照 | 知识 REF（判据形式化候选） | 4h | 登记 |
| S4-04 | 游资龙虎榜驱动短线（风格切换判据） | stockapi.com.cn/blog/22 | 弱势连板概率骤降/游资快速兑现/T+1 滞后三判据 | 知识 REF（情绪周期状态机判据） | 2h | 登记 |

- 首轮准入扫描清单（第一节）S3/S4/S5 全部**已扫**，5 路准入链齐（S1/S2 r846+S3/S4/S5 r853）；下一准入实验推荐排序：S5-01 vibe-astock（REGIME-5 情绪工具供给·Apache 净）> S3-02 PyPortfolioOpt（alloc 线）> S3-01 gplearn（因子供给）；达标 30% 准入门槛复核与预注册实验另开票（出场轴三选一门+同族 corr 门照旧）。
- 借力律注：外部宣称=未验证假设——以上 fit/工时为首判面，正式准入前一律走独立验证门禁链（数据口径→T+1→成本→随机基线三铁律）。

※r853 bm-a S3/S4/S5 补扫执行体（本章 append-only，本章在册）
