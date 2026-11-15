# 车道名单 vs 盘面（roster vs disk）

`scripts/lane_roster_disk_audit.py` → `results/lane_roster_disk_audit.json`
实跑：2026-11-15 15:2x（本地，零网络，6 条车道）

## 为什么有这个面

r1724 手工修好了一条车道：`update_futures` 的截止日用十个 CSV 的 **max**，于是
`TS.csv` 停在 2026-09-24 的 50 个交易日里，门每轮读邻居的新鲜日期回答「covered」。
根因不在日期算法，在**名单**：文件在盘上，车道自己的名单（`VARIETIES`）里没有它，
于是没有任何人或门去刷新它。这类缺陷在仓里从来没有人跨车道查过——本面就是那一步。

## 三种答案，不是一种

| 判词 | 含义 | 动作 |
|---|---|---|
| `on_disk_not_declared` | 文件在盘、名单没写 → 没人刷新（TS 类） | 补进名单（带来源）或退役文件 |
| `declared_not_on_disk` | 名单有人、盘上没有 → 承诺无面板 | 去拉，或从名单删掉 |
| `declared_frozen` | 在盘但不采（v1.0/v1.1 冻结码） | 不是缺陷，但**印出来** |

`ROSTER_UNREADABLE` 是独立判词，**永不算绿**（读不出 ≠ 干净）。共享宇宙目录
（`data/daily` 装全市场 ETF）没有封闭名单可比：该行印
`UNPLANNED_CHECK_NOT_APPLICABLE`，只问「名单→盘面」方向；在那里猜名单会把
1,700 个没人问过的文件印成缺陷。

## 读数（2026-11-15）

| 车道 | 名单 | 盘面 | 判词 |
|---|---|---|---|
| futures | 10（`VARIETIES`） | 10 | `ROSTER_MATCHES_DISK` |
| repo | 11（`TERMS`） | 11 | `ROSTER_MATCHES_DISK` |
| minute_feed | 5（`UNIVERSE`） | 10（5 个冻结） | `ROSTER_MATCHES_DISK` |
| zt_pool | 4（`ENDPOINTS`） | 4 | `ROSTER_MATCHES_DISK` |
| astock_daily | 5,226（`universe_codes()`） | 5,223 | **`ROSTER_OMITS_DISK`** |
| etf_daily | 5（`MEMBERS`·共享目录） | 1,689 | `UNPLANNED_CHECK_NOT_APPLICABLE` |

### 唯一红的一条：`astock_daily`

- **盘面有、名单没有（2 只）**：`002731`、`301139` —— 两只 `sz` 文件坐在
  `data/astock_daily/per/` 里，而车道的资格表（`data/fundamental/eligibility.csv`）
  里没有它们。按名单拉取的车道永远不会再刷新这两只：要么资格表落后于面板，
  要么这两只是退市/改码留下的残件。**动作二选一，不能就这样躺着。**
- **名单有、盘面没有（5 只）**：`001235`、`001381`、`688827`、`688845`、`689009`
  —— 车道说它该拉，盘上没有文件（断点续拉的缺口，或新增资格从未落盘）。

### 顺手抓到自己面上的一个错（E318 族）

第一版把 `eligibility.csv` 原文当名单，于是印出 **6,312 个「名单有、盘面没有」**
——而 `update_astock_daily` 的 `market_of()` 本来就有意跳过 B 股（2/9 前缀）与北交
（4/8/920），按桶计数。用原文当名单＝把「车道按设计不采」印成「车道失职」，
读者无法行动。修法=**复用车道自己的 `universe_codes()`**（零第二实现），跳过桶
作为 `skip_buckets` 一并披露（本次实测：`0`:1495 / `2`:36 / `3`:1411 / `4`:513 /
`6`:2320 / `8`:5360 / `9`:398）。

同族的第二枚：`minute_feed` 盘上有 10 个 CSV，名单只有 5——另外 5 个是 v1.0/v1.1
冻结码（代码里写着 archived-on-disk）。若按「盘面多出来的就是缺陷」判，这一行会
每轮报 5 个假警。`declared_frozen` 因此是一个**必须印出来**的桶。

## 判词怎么用

- 红只红「能点名到文件」的差集。计数不进判词（「N 个品种落后」不能行动）。
- 本面**不判**「落后几天算病」——那是 `data_lane_freshness` 的问题，且它已经用
  自己的 `panel_csv` 逐文件算过 `laggards`；本面只问名单与盘面的**存在性**。
- 面板/目录读不出（目录不存在/名单 import 失败）一律独立判词，不折成 0。

## 未验证（如实）

- `astock_daily` 的 5 只缺口是否真在拉取队列里，本面看不到 checkpoint 状态；
  `002731`/`301139` 是残件还是资格表落后，本面只负责点名，判决归车道主人。
- 其余车道（heat / lhb / marks / options / ah_panel）名单不在代码常量里（或来自
  远端映射），本轮未纳入；它们要么 retire，要么名单在状态件里，需要各自声明来源
  才能进这张表——未纳入不等于它们干净。
- 目录里只看后缀匹配的普通文件；软链/子目录不追。
