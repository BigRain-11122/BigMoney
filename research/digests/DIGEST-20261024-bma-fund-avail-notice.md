# DIGEST-20261024-bma-fund-avail-notice — 财报 PIT 可用日缺陷定谳与首公告派生态修复

- 机器：bm-a（r1098）
- 队列：state/queue/tech.md T27（r1092 登记·本轮闭环）
- 状态：RCA 完结 + 修复工具交付 + 全量缓存分离后台在跑；**派生态三面尚未发布**（缓存未完备=诚实 partial，禁半成品面）

## 一、缺陷到底是什么（不是「历史区间偏移」，是字段语义错位）

旧结论（r1092）：income 面 84% 行 avail_date 晚约一年，疑采集器历史区段 +1 年。
本轮实测推翻该归因：**存进 avail_date 的列是源侧的「最新修订日期」，不是「首次公告日期」**。

证据（results/_r1098bma_t27_notice_rca.json，income 2025-03-31 单期全量 join 6,030 行）：

| 读数 | 值 |
|---|---|
| 存储值 == 源 UPDATE_DATE | **99.83%** |
| 存储值 == 源 NOTICE_DATE | 4.67% |
| 中位存储滞后（自报告期） | **393 天** |
| 中位真公告滞后（NOTICE_DATE） | **29 天** |
| 存储值落在法定截止之后 | **99.25%** |
| 存储值 − NOTICE_DATE 中位 | 365 天 |

一行实例（000001）：period 2025-03-31 存 2026-04-25（= 2026 年一季报的更新戳），真公告 2025-04-19。

## 二、为什么这件事重要（比「慢一年」更严重）

1. 延误本身已知，旧法用 `min(最新修订, 法定截止)` 兜底（fund_avail_pit_t27）。但因为 99.25% 的行都晚于法定截止，兜底实际把**几乎所有行压成同一个日期**——横截面信息（谁先披露）被抹平，任何依赖「披露日序」的 PIT 事件研究都会得到无意义的分组。
2. 年报季的法定截止（次年 04-30）与真实披露（大量 2–3 月）差 1–2 个月，兜底口径系统性低估覆盖。

## 三、修复形态（派生面，源面板零改写）

`scripts/fund_avail_notice.py`（selftest 8/8）：

- `refresh`：逐 (face, period) 翻页取 EM 三报表的 `NOTICE_DATE`，**按 code 取 min**（一家多行=原始/修订稿，最小值=首次可得）→ 缓存 `data/fund_statement_export/_avail_notice/<face>_<period>.parquet`；2.5s 公民节奏、3 连败熔断、per-period checkpoint、`--detach` 分离后台。
- `build`：`avail_first = min(source NOTICE_DATE, stored)`，两者都是真公告的上界，取小者不可能提前；无 notice 行退法定截止（绝不造更早日期）；`late_filer` 旗如实标注逾期披露。**缓存未覆盖该面全部已采期=拒绝写面（exit 3）**。
- 车道：bm-a（T27 登记机），源面板与 bm-b 的采集器均零触碰——修复以派生态并行存在，不回写 staging。

已知边界：EM 侧若只给修订稿日期（cashflow 个别行 NOTICE_DATE 即修订戳），min 仍可能晚于真公告——方向安全（只会晚不会早），但覆盖率提升量需在 build 后按面实测，不得先宣称。

## 四、下一步

1. 缓存 rank 完备 → `build` 三面并记录 `median_lag_stored_days` vs `median_lag_first_days` / `rows_tightened`（results/fund_avail_notice.json）。
2. 派生态接入 Q1：growth/quality 骨架的 `_load_*_faces()` 改读 `pit_avail/<face>_avail_first.parquet`（改读=单独一轮，需 prereg 侧注记可用日口径变更）。