# PC_COLLECTOR — P-C 前向采集管道 spec 小件 V1（O-20260923-1850 工程车道）

> 认领：bm-a 循环轮·工程部（MSG-20260923-2055，F-04 先行）· 2026-09-23。
> 定位：HEAT_ATTENTION_SPEC §4 P-C 行前置件补齐（「data/heat/ 目录+采集器 spec 小件」）。
> 范式：update_daily / update_lhb 同族（守卫+幂等+原子写+诚实 exit 码+selftest 离线）。

## §1 采集物 V1（人气榜日快照）

- **源**：EM `emappdata.eastmoney.com/stockrank/getAllCurrentList`（akshare `stock_hot_rank_em` 的第一腿同端点同 payload；bm-b r39 审计 P-C 行判定 forward_collect）。
- **只取第一腿**：akshare 封装的第二腿=pull2.eastmoney.com 行情富化——(a) bm-b 实证 push2/emappdata 系子域 IP 级阻断风险（r40）、(b) 价格/涨跌幅我们 bars 面板自有，禁重复请求。**单请求/日=EM datacenter 公民义务**。
- **源审计·子域分块验证**（D-20260924-07①）：EM 可用性按子域（push2 族 / datacenter-web / emappdata 等）**分块各自验证、跨子域不可互证**（push2 族死而 datacenter-web 活=不同块不同命，bm-b r40 + heat_source_audit.json 14 探针实证）；本 spec 或 P-C 车道**扩面前置**：先验 datacenter 替代源或降级登记（D-07②）。
- **D-07② 预验已执行**（R97 bm-a·2026-09-24，探针=scripts/d07_datacenter_preval.py 可复跑）：akshare 全源离线扫描=人气榜三函数（stock_hot_rank_em/hk_hot_rank_em/hot_up_em）全挂 emappdata/guba/push2 域，datacenter-web 47 API 族（两融/股东户数/LHB/IPO/业绩等基本面结构化数据）**无人气/热度等价源**；datacenter-web 今日活探针 1 请求 470ms success。**降级登记生效**：P-C 车道=emappdata 单源（push2 同族阻断高危，bm-b r40 实证），持续子域阻断→update_heat.py §2 既有机制=诚实 exit 2+30min 节流+零冷却假设+零假数据，L2 回填 checkpoint 可续，消费条款（§3/§4.1）不变；**车道任何扩面（L3 新闻腿/IC 批/新腿）开工前重跑本探针**（append-only 台账 results/shortline/d07_datacenter_preval.json）。
- **规模**：pageSize=100 定案（>100 实测返回 0 行，2026-09-23 bm-a 直连探针）=公开股吧人气榜 top-100 语义。
- **字段**（冻结 schema）：`code`（裸 6 位）/`market`（SH|SZ）/`rank`（1..N 置换校验）/`rc`/`hisRc`（原样保留，语义以后源侧核名再定名）/`raw_sc`；文件级 meta=`as_of`/`fetched_at`/`source`/`n_rows`。
- **落盘**：`data/heat/popularity/YYYYMMDD.json`（gitignored，原子写 .tmp+os.replace）。

## §2 守卫（S6 链 10 分钟轮询安全）

1. **窗口守卫**：工作日且 ≥15:30 本地钟才采（收盘后快照口径，与日线 bar 对齐；盘中快照=另一数据集不混采）；周末 no-op。
2. **幂等**：当日文件已存在=no-op exit 0（一日一档）。
3. **失败节流**：`last_attempt` **先写 status 镜像后抓取**（中途崩也节流）；30min 最小重试间隔。
4. **直连铁律**：urllib `ProxyHandler({})` 无代理 opener（Clash 劫持 EM 域，J13/bm-b r39 坑 1 同族；requests/环境变量/注册表代理全绕开）。
5. **诚实失败**：抓取失败/校验失败（<50 行、sc 格式、rank 非置换、重复代码）→不写盘 exit 2 原样上报，绝不落假数据。

## §3 因子对齐纪律（HEAT_ATTENTION_SPEC §2C）

- 快照 `as_of=当日`、`fetched_at` 留痕：人气榜为滚动实时榜，**当日 15:30 后快照对齐当日 bar、信号位用 T+1（严格滞后，禁未来数据）**——因子层（`guba_hot_rank_z`/`guba_rank_delta`）未来批实现时按此对齐，本管道不管对齐只管采集。
- **不伪造回测历史**：单股排名历史（detail_em，366 bars）可在后续腿按当日 top-100 成员回填；全市场日截面历史**不存在**，任何 IC 批跑前必须声明前向窗口起点。

## §4 后续腿（另开工，认领制 MSG 先行）

| 腿 | 内容 | 状态 |
|---|---|---|
| L1 人气榜日快照 | 本件（scripts/update_heat.py + data/heat/popularity/） | **V1 交付 2026-09-23** |
| L2 单股排名历史回填 | scripts/backfill_heat_history.py（认领 MSG-20260923-2105）：emappdata `getHisList`+`getHisProfileList` 双腿/股（同域直连），按当日 top-100 成员回填，每股原子写 `data/heat/rank_history/<SEC>.json`（冻结 schema=date/rank/new_uid_rate/old_uid_rate），限速 ≥2.5s/请求+连续 5 失败保险丝+checkpoint 可续跑+selftest 14 用例；探针定案=数据集纪元 **2025-09-23 起、窗封顶 366 bars（≈1 年）**，yearType="5" 亦只返 1 年 | **V1 交付 2026-09-23（R20）** |
| L3 新闻腿 | search-api-web raw jsonp（C 级·3 个月窗）——宇宙 5222 全采不经济，须先定子集策略 | 未启动 |

## §4.1 L2 幸存者条款（消费方必读，写死于交付时）

- 素材=**当日 top-100 成员**的历史回填：只覆盖「现在热门」的股票，强选择偏差（前向性幸存者条款同 P-B spec §2B）；**不存在全市场日截面历史**（r39 审计定案），任何 IC 批跑前必须声明前向窗口起点 2025-09-23 与本条款。
- 快照成员随 L1 前向积累逐日扩张真宇宙；L2 文件=回填时刻冻结，**禁合并不同 fetch 时刻的文件冒充统一截面**。
- **首场实弹（R20）**：97/100 落盘（34865 行），era 全员 2025-09-23 起；3 只诚实拒收=真短史非故障（SZ301686 次新 2 行、SZ301689 次新 14 行、**SZ920025 北交所 1 行=人气榜含北交所股实证**，均低于 30 行 sanity 下限）；短史过门者如实落盘（688825 IPO 2026-07-27 起 59 行、688836 36 行）——次新短史=真实数据形状，重跑不改变，**勿为凑 100/100 降下限**（下限政策若改须另开预注册声明）。

## §5 exit 语义（S6 链接线）

`0`=快照落盘/合法 no-op（周末、已采、节流）；`1`=selftest 失败；`2`=源失败（原样上报勿掩盖）。`selftest` 子命令=离线守卫测试（零网络零真实写）。

—— bm-a 循环轮·工程部 · 2026-09-23
