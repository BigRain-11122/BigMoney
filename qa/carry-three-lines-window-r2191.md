# QA · carry-three-lines-window · r2191 (bm-c)

日期：2026-11-27 23:5x +08:00 · 审判面：`results/carry_three_lines_window.json`

## 判据清单

| # | 判据 | 证据 | 结果 |
|---|---|---|---|
| 1 | 面可生成（rc0） | `python scripts\carry_three_lines_window.py` → verdict `THE_TABLE_MIXES_WINDOWS` | PASS |
| 2 | 自检全绿 | `--selftest` → **18/18 passed** | PASS |
| 3 | 漂移守卫可用 | `--check` → `{"ok": true, "notes": []}` rc0 | PASS |
| 4 | 漂移会说 STALE（行为腿） | selftest 腿 12：改源面 Sharpe → rc3 且含 `STALE` | PASS |
| 5 | 自相矛盾不带 STALE（行为腿） | selftest 腿 13：改面上判词 → rc3 含 `CHECK FAILED`、无 `STALE` | PASS |
| 6 | 排序判词有负控 | selftest 腿：test 段 Sharpe 压到 0.30 → `ORDERING_DEPENDS_ON_THE_CUT` | PASS |
| 7 | 缺窗口不编数 | selftest 腿：缺 `window` → 抛错/判 `WINDOW_UNREADABLE` | PASS |
| 8 | 算术可复核 | 覆盖率 2,951/3,598 = 82.02%；交集 = max(first)/min(last) 逐字 | PASS |
| 9 | 零网络零回测 | 只 `json.load` 两张已发布面（econ / rent） | PASS |
| 10 | 不改任何已发布面 | 新面只写 `results/carry_three_lines_window.json` | PASS |

## 覆盖到的读数

- `basis_nominal` 2.972 / 2017-01-18..2026-11-25 / 2,390 bars
- `excess_hedged` 1.4162 / 2018-10-22..2026-11-20 / 1,961 bars
- `carry_unhedged` 0.5057 / 同窗 / 1,961 bars
- 转化：8% × Sharpe = 23.776% / 11.330% / 4.046%（各自的窗口已附在旁边）

## 已知未覆盖（如实）

1. 没有在共同窗上重算 basis 臂 —— 需要父面日序列或重跑基差腿，本面只定位、不重算。
2. 另两条读数缺 CAGR / 波动 / 回撤（源面未印），本面不补算、不推测。
3. 链腿与冒烟腿未接 —— 本轮 `repo_write_contention` rc=3 CONTENTION，禁改共享面（`Tools/s6_chain_bmc.py` / `smoke_test.py`）。
