# 车道滞后归因 v1（lane-lag attribution）

r2169 · bm-c · 2026-11-27

## 一句话

`data_lane_freshness` 能说"落后几天、谁拥有"，说不出**"谁本该动它"**。
于是 `stalled / tail 2026-11-20 / owner bm-c` 这种行可以挂一周，每个读者都以为
别的轮在管。本面把"迟到"拆成**有没有驱动**，并点名本机能修的那几条。

正身：`scripts/lane_lag_attribution.py` → `results/lane_lag_attribution.json`
（`--selftest` 9/9，纯只读，只写自己的结果面）。

## 驱动四源（都不是"看起来在跑"）

| 源 | 读什么 | 为什么不算"在跑" |
|---|---|---|
| `chain` | `Tools/s6_chain_bmc.py` 的 `LEGS` 里有没有这个写入器脚本 | 有腿 ≠ 跑过（r1322） |
| `task` | `schtasks /query`（无窗）任务名提到写入器 | 任务名不回答归属（`lane_hosts.json` 就是为"SatEngine-bm-b 注册在 bm-a 上"而存在的） |
| `register` | `Tools/register_*.ps1` 提过这个脚本 | 写过注册脚本 ≠ 任务还活着 |
| `declared_host` | `config/lane_hosts.json` 的指派 | **指派 ≠ 驱动**——本轮最强的一条 |

## 本轮读数（源自 `data_lane_freshness.json` as_of 2026-11-27T09:43:59）

| 车道 | 判词 | 尾 bar | 缺 | 归因 | 本机可修 |
|---|---|---|---|---|---|
| `ah_panel` | absent | — | 0 | `gate_blocked`（gate 面 `complete=false / cutoff=null`） | 是 |
| `cb_panel` | stalled | 2026-11-20 | 4 | `no_driver`（链/任务/注册/指派**四源皆空**） | 是 |
| `heat` | stalled | 2026-11-19 | 5 | `host_dead_takeover_available`（bm-a 静默 205.9h，已接管） | 是 |
| `lhb` | behind_1d | 2026-11-25 | 1 | `host_dead_takeover_available` | 是 |
| `lhb_inst` | stalled | 2026-11-20 | 4 | `declared_host_without_driver`（`lane_hosts.json` 指派 bm-c，**却没有链腿也没有任务**） | 是 |
| `repo` | behind_1d | 2026-11-25 | 1 | `host_dead_takeover_available` | 是 |
| `options` | retired | 2026-09-30 | 36 | `retired_by_design` | 否（设计退役） |
| 其余 9 条 | in_sync | 2026-11-26 | 0–4 | —（滚动窗内，`moneyflow`/`sina_mf` 的 4/2 天缺失属设计内复拉周期，已在面的 note 里） | — |

**最关键的一行是 `lhb_inst`**：它有一条明文指派（bm-c），四个驱动源里却一个都没有。
"写在名册上"和"有人在跑"之间没有别的环节会替它补——这正是 r1322 的上一站。

## 修复清单（下一轮起，按成本从低到高）

1. `lhb_inst`：写入器 `scripts/update_lhb_inst.py` 存在（面板 `data/lhb_inst/lhb_inst.parquet`
   + `_progress.json` 断点），**接一条链腿**（`check` 用面板尾 bar 对 `expected_last_official_day`，
   `run` 才付拉取钱）——接上即自愈，不需要人盯。
2. `cb_panel`：写入器 `scripts/cb_dual_low.py` → `data/cb_panel.csv.gz`。连指派都没有，
   需要先定宿主（本机或他机），再同样接腿。
3. `ah_panel`：gate 面自己写着 `complete=false`（EM 断连），属"源失败"不是"没人跑"；
   重试路径已有（`ah_panel_puller` 在链上），本轮只登记不改。
4. `heat`/`lhb`/`repo`：宿主 bm-a 已静默 205.9h，接管标记已在（`lanes_taken_over`）——
   差的是"接管后谁在定期跑"，与 1/2 同一类问题。

## 不做的事（如实）

- 本轮竞争探针 **rc=3 CONTENTION**（另一宿主 `pid=119956` 在重叠窗内写了
  `results/cpu_fill/STATE.json`），按 r1907 只落**新增文件面**：未改任何共享面、
  未重跑 S6 链、未补任何面板数据。
- 归因只读 `data_lane_freshness.json` 的**那一趟快照**；上游面被重写时读数会跟着变，
  本面不缓存、不做代差判断（r1861 族留给消费者）。
