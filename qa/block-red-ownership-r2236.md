# 红块可修性归属面 · r2236（bm-c）

## 为什么开这张面

块看板是「下一轮该修什么」的唯一指令面。它能说「这一行是红的」，但说不出两件
决定动作的事：

1. **谁有权写这个产物。** `config/lane_io.C_SINGLE_WRITER_HOSTS` 给 11 个面指了
   指定执笔机（两份 scorecard、dashboard、整个 paper 族）。在他机上，写者会
   `exit 0` 什么都不写——一行红块可以被重 derive 一万次也不会动。r1789 早就判过：
   本机写不了的对比面要记注记、不记红；看板从没接过这条法。
2. **这一行红的是钱，还是一份旧印刷。** C5 读 `paper_equity_recheck.json`，它拿
   四个读者面去比账本；读者面在账本重述之前印出来，行就红——书没毛病，是副本旧。

本面把这两件事逐行答出来：用写者**自己的准入规则**（r1789：判据由写者的守卫回答），
用 lane_io 自己看的两个心跳信号（本地 + origin），用已经量过这件事的重述面算术
（复用，不重算）。

## verdict

`PARTLY_CLEARABLE_HERE` —— **4 个红块里 1 个是本机今天就能清的**。

| 红块 | 类 | 判据 |
|---|---|---|
| `C5_paper_recon` | **STALE_UPSTREAM_COPY** | 对账面本身可写（无守卫）；红是因为上游读者 `strategy_scorecard` 拿的是重述前印刷：印于 22:18:07，账本 updated 22:20:14，早 127 秒；6 员中 5 员缺口合计 **34,238.82 CNY**，**5/5 逐分等于重述幅度**（证据复用 `results/paper_ledger_restatement.json`）。刷新读者后该行应读 **PASS** |
| `W1_supply` | HUMAN_GAP | 银行 20 张卡全部已带判词、0 张未消费；补的是新预注册问题，不是重 derive |
| `G6_ingest` | PRODUCER_DEFECT | 该面拿自己的输出和自己比（两侧 machine 都是 `FLUXGROUP`，15/15 车道相同）→ `COMPLETE` 是恒真命题；改契约才可能清，不是重跑 |
| `P1_cpu_fill` | HUMAN_GAP | duty 0% 是「没有可排的 CPU 活」，重 derive 不可能抬高占空 |

`C5` 的清除序列（非 CONTENTION 窗内一条命令）：`python scripts/strategy_scorecard.py`
→ `python scripts/paper_equity_recheck.py`。

## 顺带量到的一件事：指定执笔机已经 10.3 天没心跳

| 事实 | 读数 |
|---|---|
| bm-a 心跳（本地 / origin） | 14,800 / 14,800 分钟 ≈ **10.3 天**（最后 2026-11-18 19:53） |
| 注册在这些名下的面 | 11 个精确件 + 4 个族（`results/paper/*`、`paper_export/*`、`prospect_paper/*`、`prospect_promotion/*`） |
| 逐个调 `shared_derive_write_allowed` | **全部 True**（陈旧接管窗已开，本机可写） |
| 盘上这 11 个精确件最后刷新 | 全在 22:15 前后，**约 4.2 小时前**，且都已过 1 小时线 |

所以这些面并不是「另一台机器攥着不放」，而是**守卫已经放行、却没有轮次去刷**。
这不是本面要修的东西（写共享面需非 CONTENTION 窗），但它是 C5 以及下一次任何
「读者面比账本旧」类红块的共同结构原因。

## 验收（QA charter 本司清单）

- 自检 **24/24 PASS**（离线，不读树不联网）：守卫注册表精确命中/族令牌只匹配族内、
  未注册面保持遗留写、本机自有面即使心跳陈旧也可写、外来面心跳新鲜＝禁写、两路信号
  皆陈旧＝可取、只有一路陈旧且 origin 不可读＝**UNKNOWN 不盲取**、心跳不可读＝UNKNOWN、
  机 identity 不可读＝UNKNOWN（r98）、重述闭合求和、单缺口未闭合则 `would_read` 必须
  仍是 `BREACH_STANDS`（负控）、supply/duty/ingest 探针不得被判可修、外来新鲜面不得
  被判可修、缺件＝UNMEASURED、verdict 区分「本机可清」与「不归本机」、epoch 字符串
  不算心跳（smoke F7）、**0 缺口读者不算陈旧副本**、逐读者求和互不污染
- `run` rc0；`--check` **rc0**（幂等：比较稳定投影——心跳龄与墙钟句面被排除，判类字段
  全部在内；文档块对**存盘面**逐字比对）
- **负控实跑**：手改文档里 `34,238.82 → 34,000.00` → rc3；手改面里 C5 的 class →
  rc3“field differs: reds”；复原 → rc0
- **自捕一缺陷（已修，留痕）**：首版把「0 个交易员落后」的读者（`paper_export`）也当成
  陈旧副本，且逐行金额用了跨读者累计和 → 打印出 `2 reader face(s)` 与
  `BREACH_STANDS`（把可清的行判成清不掉）。修法：无 `behind` 的读者归 `consistent_readers`，
  逐读者独立求和；补两条自检腿钉死
- 只读面：未改 `Tools/s6_chain_bmc.py`、`smoke_test.py`、任何 `results/` 既有面、
  `docs/live_usage/*`、`fleet/machines/*`
