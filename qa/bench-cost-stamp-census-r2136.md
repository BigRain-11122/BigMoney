# QA · 成本戳普查 + 纸盘台账重复行根治（r2136 · bm-c）

日期：2026-11-26T15:0x+0800｜机器：bm-c｜轮：r2136

## 交付物

| 件 | 路径 | 状态 |
|---|---|---|
| 普查器 | `scripts/bench_cost_stamp_census.py` | 新增，selftest 6/6 PASS |
| 普查面 | `results/bench_cost_stamp_census.json` | 生成，verdict=CLEAN，26/26 |
| 读者页 | `research/BENCH_COST_STAMP_CENSUS.md` | 生成 |
| 单元格修复 | `scripts/paper_basis_timing.py`（state 增 `cost` + `evidence_cutoff`；读键 `date` → `product:date`） | 已改 |
| 台账去重 | `results/paper_basis_timing/LEDGER.json` 5832 → 3442 行（2390 重复行删除） | 已改，带备份 |
| 备份与 manifest | `results/_quarantine/paper_basis_timing-LEDGER-20261126T150609.json` + `manifest-*.json` | 已落 |
| 重生成面 | `results/paper_basis_timing/STATE.json`、`research/PAPER-BASIS-TIMING.md`、`results/paper_basis_timing_cost_split.json` | 重跑 rc0 |

## 证据链

1. 谓词同源：普查器 import `block_board.cost_stamp_problem`，不重写判据；selftest 含「结构化戳 / legacy 平铺戳 / 无戳」三行为腿 + 常量提取器两腿 + 板交叉腿（6 腿）。
2. 板交叉断言：修复前 `probe_cells_cost` 返回 false（`no cost rate printed: paper_basis_timing`）、普查 missing=1，同向；修复后 true、普查 missing=0，同向。
3. 缺口唯一性：26 个可判格里只有 `paper_basis_timing` 缺戳，其余 25 格自带 `criteria.cost_bp_side` 或结构化 `cost` 块。
4. 成本常量来源：AST 从该格脚本取 `COST_BP_SIDE = 1.5`，与脚本实际计成本算式 `abs(w-prev_w)*COST_BP_SIDE/10000` 同一常量，非手抄。
5. `evidence_cutoff` 同时补为最新 bar 日（2026-11-25），满足 science_gates C2 顶层合法键要求。

## 台账重复行（r2134 诊断 → 本轮执行修复）

r2134 已诊断根因：读键用 `m["date"]`、写键用 `f"{code}:{d}"`，两把钥匙不同 → 每次运行把每一天重写一遍。
本轮执行 r2134 写明但当时未动的修法（竞争窗已确认该格两文件不在对端写入名单）：

| 项 | 修前 | 修后 |
|---|---|---|
| LEDGER 行数 | 5832（IC 3728 / IM 2103） | **3442**（IC 2390 / IM 1052） |
| IC 累计 carry | 370.06%（重复计） | **155.924%** |
| IC 年化 | 10.66% | **10.07%** |
| IM 累计 carry | 116.862% | **47.000%** |
| IM 年化 | 9.40% | **9.35%** |
| 冪等性 | 每次重跑 +N 行 | **重跑 new_marks=0** |

- 去重前置：`python Tools\treasure_guard.py prescan results/paper_basis_timing/LEDGER.json` → **零命中 rc0**。
- 去重规则：同 `(product, date)` 保留首见；被删行必须与保留行 **JSON 逐字相同**，否则整批拒绝（本次 2390 行全部恒等，无一例外）。
- 备份与回滚：原件整档复制到 `results/_quarantine/`，manifest 记 rows_before/rows_after/dropped/证明行。
- 验收门（r2134 预置）：`paper_basis_timing_cost_split.py --ledger-gate` 修前 rc4（DUPLICATE_DATES）→ **修后 rc0**（`one row per day in the paper ledger`）；`--check` **rc0**（`face matches the panel and the ledger`，`ledger_health=CLEAN`）。

## 判据（预先声明的通过线）

- 普查 `verdict == "CLEAN"` 且 `population.missing == 0` → **PASS**
- 板交叉 `census_agrees == true` → **PASS**
- `STATE.json` 顶层 `cost.basis == "per_side_bp"` 且 `side_bp == 1.5` → **PASS**
- 台账 `(product,date)` 唯一且重跑 `new_marks == 0` → **PASS**
- `--ledger-gate` rc0 → **PASS**

## 未做 / 未验证（如实）

- 未跑全量冒烟（竞争窗 rc=3；本轮 smoke 5 分钟无输出被外部取消，未取得新读数）。
- 未重跑 S6 链（竞争窗律）。
- 未重跑 `block_board.py` 本体刷新 `research/QUANT-BLOCK-BOARD.md`（该面本轮被另一宿主写过；C2 判据已用只读调用复核为绿，页面刷新留待无竞争轮）。
- 成本率 1.5bp/边是脚本既有常量，本次只补「说出成本」，未重新标定成本本身。
- 台账数值本身未被改动：r2134 的独立镜像重放已证逐日 carry 零差，本轮只删重复行。
