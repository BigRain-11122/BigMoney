# QA — 车道滞后归因 r2169 (bm-c, 2026-11-27)

## 交付物

| 件 | 路径 | 类型 |
|---|---|---|
| 归因脚本 | `scripts/lane_lag_attribution.py` | 新文件（只读探针，只写自己的结果面） |
| 结果面 | `results/lane_lag_attribution.json` | 新文件 |
| 说明 | `research/LANE-LAG-ATTRIBUTION.md` | 新文件 |

## 验证（实测输出）

1. `python scripts/lane_lag_attribution.py --selftest` → **9/9 ok**
   - L1 三源全空 = `no_driver`
   - L2 `in_sync` 不参与归因
   - L3 注册脚本只是声明（`declared_only`）
   - L3b 活任务名把同一行变成 `driven_but_late`
   - L4 宿主死且不可接管 → 不归本机
   - L5 宿主死且可接管 → 归本机
   - L6 退役车道不算迟到
   - L6b 有指派无驱动 = `declared_host_without_driver`（只在指派给 bm-c 时归本机）
   - L7 链解析只读 `LEGS` 块（324 个脚本名，`s6_chain_bmc.py` 自身不在内）
2. `python scripts/lane_lag_attribution.py` → rc0，6 条非同步车道全部归因：
   `gate_blocked` 1（ah_panel）、`no_driver` 1（cb_panel）、
   `declared_host_without_driver` 1（lhb_inst）、`host_dead_takeover_available` 3
   （heat/lhb/repo）、`retired_by_design` 1（options）
3. 驱动源规模实测：链脚本 324 / 计划任务名 368 / 注册脚本 11 —— 说明三源都真的读到了，
   `no_driver` 不是"探针没探到"。
4. 反证：`rg cb_dual_low|update_lhb_inst` 全仓，除 `data_lane_freshness.py`（判词来源）、
   `config/lane_hosts.json`（指派）、`block_board.py`（读面板）与各自的 benchmark 外，
   **没有调用者**——与归因结论一致。

## 未做 / 未验证（如实）

1. 本轮 `repo_write_contention --lookback-min 12` → **rc=3 CONTENTION**
   （另一宿主 pid=119956，重叠窗内 `results/cpu_fill/STATE.json` 不可归因）。
   按 r1907：只落新增文件面，**未改任何共享面、未重跑 S6 链、未补数据**。
2. 未跑全量冒烟（本轮为新增面，不触碰既有腿；上一轮 794/794）。
3. `lhb_inst` / `cb_panel` 的修复（接链腿）**未做**，属改共享面，留给无竞争窗。
4. 归因只对 `data_lane_freshness.json` 的一趟快照负责；上游重生后需重跑本面。

## 判词

`PRODUCT_DELIVERED` — 新面 + 新数字（把 3+2+1 的计数变成 6 条点名、5 条本机可修、1 条设计退役），
自检 9/9；数据面修复尚未执行，已在 `research/LANE-LAG-ATTRIBUTION.md` 列成本序清单。
