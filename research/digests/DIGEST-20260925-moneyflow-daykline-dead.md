# DIGEST-20260925-moneyflow-daykline-dead — 个股资金流 daykline 源面死亡证明 + v2 排行面修复裁定

> 车道：SHORTLINE_PLAYBOOK P-3 域（资金流源修复，**O-1620 GM 已署名**）；MF_COLLECTOR.md V1 spec 的源面续审（R58 审计 DIGEST-20260924-moneyflow-source-audit 的当夜反转实况）。
> 执行：bm-a 循环轮·数据 round 108（2026-09-25 00:47-01:0x，无人值守）；修复票=T-2026-09-25-39。
> 纪律：直连 ProxyHandler({})+代理剥除双路对照（requests.utils.getproxies 重绑，daily_source_probe T4 范式）；单发探针 3s 级节流，无批量拉取。

## 一、结论速览（00:5x 实弹，三探针三面）

| 面 | 接口 | 判定 | 实证 |
|---|---|---|---|
| 个股资金流**历史日线** | `push2his/api/qt/stock/fflow/daykline/get` | **DEAD（接口级硬断 ≥25h）** | RemoteDisconnected 即断；**双域均死**（push2his+push2 同路径）、Referer/Accept/Language 仿冒头无效、代理/直连双路同死=非 Clash 因素非 IP 代理因素 |
| 同域对照组 | `push2his/api/qt/stock/kline/get` | **ALIVE** | HTTP 200 正常回包（rc:102 参数极简属预期）=**域活着、路径死**，R58「按子域×路径分化」判例的路径维再证 |
| 个股资金流**盘中分钟** | `push2his/api/qt/stock/fflow/kline/get`（klt=1） | **ALIVE** | rc:0 真数据（tradePeriods pre 2026-09-24 完整） |
| **主力净流入排行横截面** | `push2/api/qt/clist/get`（fid=f62, fs=沪深A+北交） | **ALIVE** | rc:0，total=**5920**，f62/f184/f66/f69/f72/f75/f78/f81/f84/f87/f2/f3 全回 |

**时间轴定案**：R58（09-24 晨）= daykline 活 × clist 死（板块码表腿）；R108（09-25 夜）= **完全倒转**。EM 阻断面按「子域×接口路径×日」轮换，**同域不同路径可生死并存、且逐日翻转**——拉取管线设计铁律升级：**禁单面依赖，必须双面冗余**。

## 二、对 MF_COLLECTOR V1 的裁定

1. **V1 滚动窗设计前提被证伪**：spec §1「周期性全宇宙重拉维持无缝面板（刷新间隔<120td）」依赖 daykline 120td 回看窗；daykline 死→月度级重拉不可行，且 gate 自愈循环（3 请求/30min 探测死端点）在阻塞持续期=空烧（诚实但无产出）。checkpoint 53/5222 为 brief-window 残留。
2. **v2 修复裁定（T-2026-09-25-39，本 digest 冻结设计要点）**：
   - **主面=clist 排行横截面**：全市场 5920 只 ≈ **60 请求/日**（pz=100 分页，2.5s 节流≈2.5min/全宇宙），替代 daykline 5222 请求/月——效率×100 且 EM 公民义务更优；
   - **12 值列全映射**（schema 零改动）：f2→收盘价、f3→涨跌幅、f62→主力净额、f184→主力占比、f66/f69→超大单净额/占比、f72/f75→大单、f78/f81→中单、f84/f87→小单；`date`=本地 ETF 交易日历「最近完整 bar 日」戳（update_futures 15:30 完整性约定同源），**横截面无日期字段=日期自戳**；
   - **窗口语义变更（spec 修订点）**：rank 面无历史回看→**纯前向采集**（每日一行/股）；daykline 既有代码路径保留为**机会性回填副面**（其 120td 回看窗恰是 gap 修复器，brief-window 自愈机制原样复用零改动）；面板缺口日如实保留禁补假数；
   - **拉取窗守卫**：09:15-15:05 盘中禁拉（横截面=实时变动值）；15:30 后与夜间=终值快照合法；同日幂等（date 已在面板→比对跳过，overlap 主字段 tol 1.0 律不变）；
   - **宇宙过滤**：rank 全市场 5920 ∩ bars 5222（代码 join），非 bars 成员诚实计 `skipped_not_in_universe`。
3. **既有 53 股历史不废**：daykline 拉得的 120td 史为合法回填存量，v2 追加不重写。

## 三、坑律（入册）

- **EM 阻断轮换律**：同一接口路径的阻断**按日翻转**（R58 晨活→R108 夜死，间隔<24h）；「昨天探针可用」不构成「今天管线会通」的依据——源审计结论必须带时间戳消费，跨日引用须重探。R58 spec「阻断按日波动」四字的实锤版。
- **requests 注册表代理陷阱再证**：清 env 变量后 requests 仍走 Windows 注册表 Clash 系统代理（`requests.utils.getproxies()` 重绑剥除=daily_source_probe `_strip_requests_proxy` 范式）；但本例**双路同死**=诊断必须先分层（代理层→域层→路径层）再归因，否则会把接口级阻断误诊为代理病。
- **横截面面无日期字段**：clist 族返回=「当前时点快照」，日期必须消费方自戳且与「终值时刻」对齐（盘中快照≠日频终值）——这是 rank 面替代 daykline 面唯一的语义新增风险点，守卫必须挡盘中拉取。

## 四、指针

- 修复票：`fleet/tasks/T-2026-09-25-39-P1.json`（数据车道·bm-a lane，R31 判例）
- spec 增补：`research/shortline/MF_COLLECTOR.md` §5（2026-09-25 R108）
- 前序审计：`research/digests/DIGEST-20260924-moneyflow-source-audit.md`（R58，当日反转前的正典）
- 采集器：`scripts/update_moneyflow.py`（V1 交付 R63；v2 待 T-39）
