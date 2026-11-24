# QA — `lane_lag_unit_guard` (r2069, bm-c)

**产物**：`scripts/lane_lag_unit_guard.py` · `results/lane_lag_unit_guard.json` · `research/LANE_LAG_UNIT_GUARD.md` · `results/_r2069bmc_lane_lag_negative.py`

## 被测的是什么

`scripts/block_board.py::probe_dir_bar_fresh` 用**日历日**衡量「落后」，但容差字段叫
`holiday_allow_days`（假日日数）。本面把 `research/QUANT-BLOCKS.json` 里每一条
`dir_bar_fresh` 探针按**官方交易日历**重算一遍，把两个数字并排印出，并把分类冻结成三态。

## 证据（可复跑）

| 项 | 命令 | 结果 |
|---|---|---|
| 自检 | `python scripts/lane_lag_unit_guard.py --selftest` | **28/28 OK**，rc0 |
| 生成 | `python scripts/lane_lag_unit_guard.py run` | rc0，verdict `TOLERANCE_IS_IN_THE_WRONG_UNIT` |
| 复核 | `python scripts/lane_lag_unit_guard.py --check` | **CHECK OK**，rc0 |
| 负控 | `python results/_r2069bmc_lane_lag_negative.py` | **15/15 OK**，rc0 |

## 本轮读数（evidence_cutoff 2026-11-24）

| 块 | 尾部 bar | 应到 bar | 板印日历日 | 日历交易日 | 分类 |
|---|---|---|---|---|---|
| D1_fut_daily | 2026-11-24 | 2026-11-24 | 1 | 0 | AGREE_CURRENT |
| D2_index_daily | 2026-11-23 | 2026-11-24 | 2 | 1 | AGREE_PENDING（生产者已声明 vendor 未发布） |
| D3_etf_daily | 2026-11-23 | 2026-11-24 | 2 | 1 | AGREE_PENDING |
| D4_astock_daily | 2026-11-24 | 2026-11-24 | 1 | 0 | AGREE_CURRENT |
| D6_cash_rate | 2026-11-20 | 2026-11-24 | **5** | **2** | AGREE_LATE |

**5 条的日历差都不是交易日差。** D6 板印 5 天，日历事实 2 个交易日（11-23、11-24）。

## 负控做了什么（为什么绿腿不可能是夹具变了）

1. 改一个数字 → rc3 且句含 `CHECK FAILED`、**不含** `STALE`（链只在 `STALE` 上付钱重建，r1850）；
2. `STALE` 从一个数字里永不出现 —— 这是 `--check` 里两条分支的合同；
3. 改页面 marker 块 → rc3 `CHECK FAILED`；
4. 动 `inputs_digest` → rc3 且句含 `STALE`、且**不含** `CHECK FAILED`（漂移不是缺陷）；
5. 每次复原后 `sha256` 与原始逐字节相同，且 `--check` 回到 rc0；
6. `classify()` 是输入的函数（四个方向各验一次），不是常量；
7. 单位是原因：同一个容差按交易日读时不可能红绿两色，按日历日读时会 —— 两条腿同时钉死。

## 自捕（本窗）

- 首版把「源还没发布」也算成 LATE，D2/D3 被判 `GREEN_IS_PREMATURE`（假红）。r1852 判例：生产者已经在
  `results/index_daily_update_status.json` 里写了 `reason="vendor has not published past 2026-11-23"`，
  读者不该自己再判一遍。改为三态（CURRENT / PENDING_TODAY / LATE）后 D2/D3 转 `AGREE_PENDING`。
- 首版一条自检腿写错（`2026-11-21` 是周六，缺口应从 `11-23` 起算），自检当场红——改的是断言不是代码。

## 未做（如实）

- **未改 `scripts/block_board.py`**（共享面，竞争窗 rc=3，r1907）；补丁形状已写进面，状态 `PROVEN_NOT_APPLIED`。
- 未跑全量冒烟、未跑 S6 链（同属竞争窗禁止项）。
- 未给 `index_daily` 补一条 freshness 车道登记（那是 `data_lane_freshness.py` 的共享面）。
- `data/index_daily` 四只仍停在 2026-11-23：来源端未发布，本面只如实携带生产者原话，不代抓。
