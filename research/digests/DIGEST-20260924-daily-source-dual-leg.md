# DIGEST-20260924-daily-source-dual-leg — 日线源双腿 Phase 0 前置审计（dept:数据·bm-a R34）

类型=专项审计（OPERATING_PLAN Phase 0「日线源双腿」前置证据；零采纳零管线改动，P1 门票决策归 GM）。
工具=`scripts/daily_source_probe.py probe/selftest`（selftest 9/9，直连 opener+限速 2.5s+诚实错误分类），产物=`results/daily_source_probe.json`+本纪要。
试验账本 N=2753 不动（零引擎跑，audit.ledger_trials_added=0）。

## 一、探针矩阵（3 符号 × 4 臂，2026-09-24 ~02:4x bm-a）

| 臂 | 510300/159934/511010 | 判定 |
|---|---|---|
| sina_control（现役源） | 3/3 OK，2012/2013 年起全史，含 09-23 bar，retmax=0.0 leveldiff=0.0 | 方法学锚（源内自证） |
| em_direct（去代理直连） | 3/3 RemoteDisconnected | **push2his 在 bm-a 亦 IP 级阻断** |
| em_envproxy（默认环境） | 3/3 RemoteDisconnected | 代理/直连同死 → bm-b r40/46 阻断扩展为**双机实证** |
| tencent_direct（raw fqkline qfq） | 3/3 OK，含 09-23 bar（02:4x 已在=早于 sina 实证 20:26），retmax 2/3 精确 0.0 | **唯一可用第二源（校验腿）** |

## 二、语义定案（重要发现）：sina 基金日线=**不含分红复权的原始价**，tencent qfq=含分红前复权

- 511010（国债ETF）**2026-09-18 除息日**：local（sina）141.25→140.67=-0.41% phantom 跌；tencent 140.63→140.67=+0.03% 平滑（息前价回溯扣减）。
- 511260（十年国债ETF）同日 **-0.91% phantom**（div=0.00938）；511090 近 60 日无除息=零分歧；512880/159915 零分歧；510500 10 个 >1e-4 分歧全为 3 位小数舍入噪声（≤6e-4），**>4e-3 才是除息事件**。
- 影响面：core48 内债券 ETF（511010/511260）为 VOLATILITY-CE-01 低波袖重仓品种，除息日在本地数据宇宙里表现为 phantom 跌 → 量价信号/纸盘 NAV 在该日轻微失真（方向=低估收益、高估波动）。**这不是数据损坏**：全池自建池起同一 sina 语义、所有在册锚定证据内部自洽；换语义=重锚定全部在册证据=重大决策（GM/CEO 门），**不属本审计处置范围**。
- 校验腿设计推论：**最新共同日 close level 比对在除息日依然成立**（qfq 只回溯调历史价，当日两源同为原始价，probe 实证 leveldiff=0.0）；return 比对在除息日会假红 → 校验腿主判据=level-parity，return 仅作次级诊断（阈值须 ≥4e-3 并注明除息容许）。

## 三、双腿架构裁定（呈 GM 的 P1 门票草案要点）

1. **写源维持 sina 单源**：现网无第二可写源——EM 双机阻断；tencent fqkline **无 amount 列**（6 字段），补不齐本地 7 列契约 → tencent 不能作增量写源，只能作校验源。
2. **tencent=校验腿（推荐，零写风险）**：①freshness watchdog——当日 15:30 后 tencent 有 bar 而 sina 未发布 → 面板报「源滞后」状态（09-23 全日等待的直接解药）；②latest-bar level-parity 门——两源当日 close 逐位比对，分歧>1e-3（非除息日）→ 按 overlap_mismatch 纪律只旗标不动本地。接线量小（update_daily 后置一步，探针速率 1 请求/符号）。
3. **EM 写源路径**：需换出口/代理节点（基础设施决策）后才可再议，本审计仅记录阻断事实。
4. **分红语义修正线（独立于双腿，另案）**：若 GM 决定采纳分红复权语义 → 须重锚定全部在册证据+全史重建+G2.5 复检，工作量=一次性大批，非本门票范围；短期可先在除息日给 paper/因子消费层加「事件日容差」注记（最小干预）。

## 四、局限（诚实）

- publish-latency 无法从快照探针回溯测量（sina 09-23 ≈20:26 来自 update_status 历史）；前向延迟采样器=未来 P-C 式小件，随门票一并裁定。
- tencent 深度探针=640 rows（2024-02 起）；更深的 datalen 上限未探（校验腿只需近窗，非阻塞）。
- 510880 不在 core48 本地池（探针顺手证缺席），扫描未及全部 48 员——全量除息日普查归门票执行件。

## 五、相关性评级：A（Phase 0 直连项「日线源双腿」的决策证据；同时是新数据质量事实=分红语义差异）

下步指针：GM 署名 P1 门票（tencent 校验腿接线）→ 全 48 员除息日普查 → 前向延迟采样器；分红语义另案呈报。
