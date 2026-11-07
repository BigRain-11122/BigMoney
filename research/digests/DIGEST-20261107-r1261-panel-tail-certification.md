# DIGEST 2026-11-07 r1261 bm-a — 面板尾部：抽样 vs 全量，以及「最新 bar 是谁的」

判例：E399（`knowledge/METHODOLOGY_ASSETS.md`）

## 这件事情是什么

`data_lane_freshness` 的板子里，`futures`/`repo` 这类 10 来个 CSV 的面板是全量读的，`moneyflow`/`astock_daily` 这类 5,222 文件的面板按 40 个均匀抽样点读（r1259 起自披露 `sampled`）。抽样是为「每几分钟刷一次」付的价钱，但它是**声明**。本轮加了 `certify` 子命令：把每块声明过 `panel_csv` 的面板全量读一遍，然后把结论与板子上印的抽样尾巴对账，同时也回答一个抽样永远答不了的问题——**那根最新 bar 被多少个符号持有**。

## 读数（2026-11-07T13:47+08:00，10,465 文件 / 2.8s）

| lane | 全量 tail | 抽样 tail | 一致 | 持有最新 bar 的符号 |
|---|---|---|---|---|
| futures | 2026-11-06 | 2026-11-06 | 是 | 9 / 10（90.0%） |
| repo | 2026-11-06 | 2026-11-06 | 是 | 11 / 11（100%） |
| moneyflow | 2026-10-19 | 2026-10-13 | **否（抽样低估）** | **2 / 5,222（0.04%）** |
| astock_daily | 2026-11-06 | 2026-11-06 | 是 | 4,769 / 5,222（91.3%） |

## 两条律

1. **抽样只可能低估，不可能放过停摆**：抽样是全量的子集，所以全量 max ≥ 抽样 max 恒成立。方向安全，但仍要印，因为它改变读者动作——`moneyflow` 的板面把 10-19 的块印成 10-13，读者会去追一个不存在的停摆。
2. **「面板尾部」这句话常常不成立**：`moneyflow` 的 10-19 只有 2 只标的到达，另外 5,220 只都在它之前。一个符号的最后一根 bar 冒充整块面板的状态，是「最大值 ≠ 状态」的最便宜反例。发布 tail 必须同时发布 `tail_holders` / `tail_holder_share`，低于 10% 打 `thin_tail` 旗。

## 附带读数

- `astock_daily` 两次连扫 453 → 439 只落后：`update_astock_daily refresh`（pid 68824，09:24 起）在飞，这个数会动。同一块面板相隔两分钟数字不同不是漂移，是「有写者在跑」。
- `futures` 有 1 只合约落后（9/10 持有 11-06）。

## 落地

`scripts/data_lane_freshness.py`（`certify` + `panel_tail_csv_full` + selftest 21/21 含新 L23）、`results/data_lane_tail_certification.json`、`docs/data_lanes/TAIL_CERTIFICATION.md`、smoke 腿 `fleet: a panel tail read by sample is certified against a full scan`。