# 车道交接说明 · DASHENG 本机实测（供对端 `ingest_diff` 复核）

> 回应 `O-20261124-2300-bm-c` §1-C。本文件由 `scripts/ingest_lanes_doc.py` 从盘上 derive，禁手改——要改就改生成器再重跑。

## 0. 一句话结论

- 共 **15 条车道 / 12933 个文件 / 1310.9 MB**；其中 **15 条**有重建脚本。
- **全部车道都有重建脚本，不需要分包**——对端按下表逐条跑即可，省掉 95MB 分包的往返。
- 本地交易日历尾 bar = **2026-11-18**（以 `data/daily/510300.csv` 为时钟）；尾 bar 落后它的车道见 §2 的「缺口」列。

## 1. 总表

| 车道 | 文件数 | 体量 | 覆盖首 bar | 覆盖尾 bar | 缺口(交易日) | 重建脚本 |
|---|---|---|---|---|---|---|
| `astock_daily` | 5223 | 1179.1 MB | 1990-12-19 | 2026-11-18 | 0 | `scripts/update_astock_daily.py` |
| `moneyflow` | 5223 | 24.3 MB | 2025-12-26 | 2026-10-19 | 22 | `scripts/update_moneyflow.py` |
| `lhb_inst` | 2 | 3.7 MB | — | — | — | `scripts/update_lhb_inst.py` |
| `options` | 256 | 0.9 MB | 2026-01-29 | 2026-09-30 | 30 | `scripts/update_options.py` |
| `futures_contracts` | 335 | 1.4 MB | 2018-10-22 | 2026-11-17 | 1 | `scripts/update_futures_contracts.py` |
| `futures_daily` | 10 | 1.3 MB | 2008-01-09 | 2026-11-18 | 0 | `scripts/update_futures.py` |
| `index_daily` | 4 | 0.4 MB | 2002-01-04 | 2026-11-18 | 0 | `scripts/update_index_daily.py` |
| `daily` | 1725 | 88.6 MB | 2005-02-23 | 2026-11-18 | 0 | `scripts/update_daily.py` |
| `cb_daily` | 0 | 0.0 MB | — | — | — | `scripts/cb_dual_low.py` |
| `repo_daily` | 11 | 1.5 MB | 2006-11-01 | 2026-11-18 | 0 | `scripts/update_repo.py` |
| `zt_pool` | 5 | 0.5 MB | — | — | — | `scripts/update_zt_pool.py` |
| `fundamental` | 3 | 1.4 MB | — | — | — | `scripts/update_fundamental.py` |
| `heat` | 125 | 4.0 MB | — | — | — | `scripts/update_heat.py` |
| `ext_slots` | 1 | 0.2 MB | 2007-01-18 | 2026-09-24 | 33 | `scripts/backfill_ext_slots.py` |
| `minute_feed` | 10 | 3.6 MB | 2026-09-10 | 2026-11-17 | 1 | `scripts/update_minute_feed.py` |

## 2. 逐车道：重建命令 / 数据源 / 覆盖与缺口

### `astock_daily`

- **重建命令**：`python scripts/update_astock_daily.py`（幂等；面板新鲜=零网络 no-op）
- **数据源与频率**：A-share per-stock daily-bar forward collector (T-2026-09-26-87 supply lane, bm-b).
- **形态**：.csv×5222，.json×1
- **覆盖**：1990-12-19 → 2026-11-18；5222 个文件带日期列
- **缺口**：无（尾 bar 已对齐本地日历）。

### `moneyflow`

- **重建命令**：`python scripts/update_moneyflow.py`（幂等；面板新鲜=零网络 no-op）
- **数据源与频率**：Individual-stock money-flow forward collector (R63 bm-a, claim MSG-20260924-0920).
- **形态**：.csv×5222，.json×1
- **覆盖**：2025-12-26 → 2026-10-19；5222 个文件带日期列
- **缺口**：落后本地日历 **22 个交易日**（2026-10-19 → 2026-11-18）——重建时会自动补。

### `lhb_inst`

- **重建命令**：`python scripts/update_lhb_inst.py`（幂等；面板新鲜=零网络 no-op）
- **数据源与频率**：update_lhb_inst -- the institutional seat aggregate of the LHB face, as a panel.
- **形态**：.json×1，.parquet×1
- **覆盖**：— → —；0 个文件带日期列，1 个文件读不出日期
- **缺口**：无日期列可比，未判定。

### `options`

- **重建命令**：`python scripts/update_options.py`（幂等；面板新鲜=零网络 no-op）
- **数据源与频率**：T-69 wave-2b: OPTIONS forward daily collector (O-20260925-1158 continuation).
- **形态**：.csv×254，.json×2
- **覆盖**：2026-01-29 → 2026-09-30；254 个文件带日期列
- **缺口**：落后本地日历 **30 个交易日**（2026-09-30 → 2026-11-18）——重建时会自动补。

### `futures_contracts`

- **重建命令**：`python scripts/update_futures_contracts.py`（幂等；面板新鲜=零网络 no-op）
- **数据源与频率**：Give data/futures_contracts a producer inside the repo.
- **形态**：.csv×335
- **覆盖**：2018-10-22 → 2026-11-17；335 个文件带日期列
- **缺口**：落后本地日历 **1 个交易日**（2026-11-17 → 2026-11-18）——重建时会自动补。

### `futures_daily`

- **重建命令**：`python scripts/update_futures.py`（幂等；面板新鲜=零网络 no-op）
- **数据源与频率**：Futures main-continuous daily puller (R48 bm-a, claim MSG-20260924-0645).
- **形态**：.csv×10
- **覆盖**：2008-01-09 → 2026-11-18；10 个文件带日期列
- **缺口**：无（尾 bar 已对齐本地日历）。

### `index_daily`

- **重建命令**：`python scripts/update_index_daily.py`（幂等；面板新鲜=零网络 no-op）
- **数据源与频率**：Index daily forward refresh (bm-c lane, r1791).
- **形态**：.csv×4
- **覆盖**：2002-01-04 → 2026-11-18；4 个文件带日期列
- **缺口**：无（尾 bar 已对齐本地日历）。

### `daily`

- **重建命令**：`python scripts/update_daily.py`（幂等；面板新鲜=零网络 no-op）
- **数据源与频率**：Incremental daily-bar updater for the core-48 pool + paper accrual hook.
- **形态**：.csv×1725
- **覆盖**：2005-02-23 → 2026-11-18；1725 个文件带日期列
- **缺口**：无（尾 bar 已对齐本地日历）。

### `cb_daily`

- **重建命令**：`python scripts/cb_dual_low.py`（幂等；面板新鲜=零网络 no-op）
- **数据源与频率**：脚本未写模块 docstring（未标注）
- **覆盖**：— → —；0 个文件带日期列
- **缺口**：无日期列可比，未判定。

### `repo_daily`

- **重建命令**：`python scripts/update_repo.py`（幂等；面板新鲜=零网络 no-op）
- **数据源与频率**：Repo term-ladder daily rate puller (T-2026-09-26-88 s3, R328 bm-a).
- **形态**：.csv×11
- **覆盖**：2006-11-01 → 2026-11-18；11 个文件带日期列
- **缺口**：无（尾 bar 已对齐本地日历）。

### `zt_pool`

- **重建命令**：`python scripts/update_zt_pool.py`（幂等；面板新鲜=零网络 no-op）
- **数据源与频率**：ZT-pool daily snapshot collector gate (O-20261001-2103 R2 data face, bm-a lane, S5-01 GO landing; OSS harvest ledger section-7 pointer).
- **形态**：.json×1，.parquet×4
- **覆盖**：— → —；0 个文件带日期列，4 个文件读不出日期
- **缺口**：无日期列可比，未判定。

### `fundamental`

- **重建命令**：`python scripts/update_fundamental.py`（幂等；面板新鲜=零网络 no-op）
- **数据源与频率**：Fundamental + ST eligibility snapshot (O-1820 item2 data lane).
- **形态**：.csv×3
- **覆盖**：— → —；0 个文件带日期列，3 个文件读不出日期
- **缺口**：无日期列可比，未判定。

### `heat`

- **重建命令**：`python scripts/update_heat.py`（幂等；面板新鲜=零网络 no-op）
- **数据源与频率**：Daily popularity-ranking (人气榜) forward-collect snapshot - P-C v1.
- **形态**：.json×125
- **覆盖**：— → —；0 个文件带日期列
- **缺口**：无日期列可比，未判定。

### `ext_slots`

- **重建命令**：`python scripts/backfill_ext_slots.py`（幂等；面板新鲜=零网络 no-op）
- **数据源与频率**：backfill_ext_slots.py -- P-1d extension-slot raw pulls (one-shot backfill).
- **形态**：.csv×1
- **覆盖**：2007-01-18 → 2026-09-24；1 个文件带日期列
- **缺口**：落后本地日历 **33 个交易日**（2026-09-24 → 2026-11-18）——重建时会自动补。

### `minute_feed`

- **重建命令**：`python scripts/update_minute_feed.py`（幂等；面板新鲜=零网络 no-op）
- **数据源与频率**：T-104 s1: sina 1-minute-K forward-accumulation archive collector.
- **形态**：.csv×10
- **覆盖**：2026-09-10 → 2026-11-17；10 个文件带日期列
- **缺口**：落后本地日历 **1 个交易日**（2026-11-17 → 2026-11-18）——重建时会自动补。

## 3. 分包规则（当前未启用）

本机全部车道都有重建路径，按上表跑脚本即可，不需要分包。
若对端网络不可用、必须走物理件，则按令 §1-C：单包 ≤95MB，放 `research/INGEST/PACKS/<日期>/`，并在 `research/INGEST/PACKS.json` 写 `{path, bytes, sha256, covers:[起,止]}`；分包清单届时由生成器补 `--packs` 面，禁手写。

## 4. 复现

```
python scripts/ingest_lanes_doc.py           # 重生本文件 + .json 孪生
python scripts/ingest_lanes_doc.py --check # 比对面是否落后于盘（rc0 一致 / rc3 需重建）
```

