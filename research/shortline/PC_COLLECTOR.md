# PC_COLLECTOR — P-C 前向采集管道 spec 小件 V1（O-20260923-1850 工程车道）

> 认领：bm-a 循环轮·工程部（MSG-20260923-2055，F-04 先行）· 2026-09-23。
> 定位：HEAT_ATTENTION_SPEC §4 P-C 行前置件补齐（「data/heat/ 目录+采集器 spec 小件」）。
> 范式：update_daily / update_lhb 同族（守卫+幂等+原子写+诚实 exit 码+selftest 离线）。

## §1 采集物 V1（人气榜日快照）

- **源**：EM `emappdata.eastmoney.com/stockrank/getAllCurrentList`（akshare `stock_hot_rank_em` 的第一腿同端点同 payload；bm-b r39 审计 P-C 行判定 forward_collect）。
- **只取第一腿**：akshare 封装的第二腿=pull2.eastmoney.com 行情富化——(a) bm-b 实证 push2/emappdata 系子域 IP 级阻断风险（r40）、(b) 价格/涨跌幅我们 bars 面板自有，禁重复请求。**单请求/日=EM datacenter 公民义务**。
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
| L2 单股排名历史回填 | detail_em 按当日 top-100 成员拉 366 bars 历史（100 请求×3-5s 限速≈8min，另开轮次跑） | 未启动 |
| L3 新闻腿 | search-api-web raw jsonp（C 级·3 个月窗）——宇宙 5222 全采不经济，须先定子集策略 | 未启动 |

## §5 exit 语义（S6 链接线）

`0`=快照落盘/合法 no-op（周末、已采、节流）；`1`=selftest 失败；`2`=源失败（原样上报勿掩盖）。`selftest` 子命令=离线守卫测试（零网络零真实写）。

—— bm-a 循环轮·工程部 · 2026-09-23
