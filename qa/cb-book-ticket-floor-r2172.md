# qa · cb_book_ticket_floor（r2172 bm-c）

日期：2026-11-27 11:5x +0800 · 面：`scripts/cb_book_ticket_floor.py`

## 1. 这张面回答什么

双低可转债书（`results/cb_dual_low.json`：20 只 / 20 日 / 10bp）在给定本金下能不能真的
把 20 只都拿住，以及整手网格会搁浅多少现金、把权重偏到哪去。

## 2. 跑了什么（都真跑过）

| 动作 | 命令 | 结果 |
|---|---|---|
| 离线自检 | `python scripts/cb_book_ticket_floor.py --selftest` | **17/17** |
| 真定价 | `python scripts/cb_book_ticket_floor.py` | bar 2026-11-26 · 20 只 · rung 25,850 · 干净本金 518,625 |
| 漂移检查 | `python scripts/cb_book_ticket_floor.py --check` | `CHECK OK: priced on panel bar 2026-11-26 (20 names), stamp matches` rc0 |
| 链腿 | `python Tools/s6_chain_bmc.py --only=cb_book_ticket_floor` | `0 cb_book_ticket_floor 0.2s CHECK OK` rc0（1/1） |

## 3. 判据有没有被自己骗过

- **规则不是重写的**：屏幕（价格带 / 剔深度实值 / `close+premium` 排序）通过
  `import cb_dual_low` 用它的 `_eligible` / `_load_panel`，所以这本书改了规则、这张面跟着变；
  自检第 9-10 腿在合成面板上验证排序与深度实值剔除。
- **判词由自己的计数决定**：`verdict_of(n, held, stranded_pct)` 只看「拿住几只」与
  「搁浅比例」，不看名字；自检 7-8 腿把 BUYABLE / BUYABLE_WITH_STRAND / NOT_BUYABLE /
  NO_NAMES 四个分支都点过一遍。
- **门槛是两把尺**：一手门槛（25,850）＝最贵一手 × 只数；干净本金（518,625）＝搁浅 ≤2% 的
  最小本金，用二分在冻结的券表上算，不联网、不看单个命中的运气。
- **盈余不是沉默**：`stranded_pct` / `max_weight_dev_pp` / `top_weight` 逐档印出来——
  小钱版本的书与 1/20 等权版本的差额是可读的数字，不是一句「大致相当」。

## 4. 未做 / 未验证（如实）

- 没做逐笔撮合模拟（次日开盘 + 冲击 + 券商最低佣金）；本面只回答「权重能不能落地」。
- 只读最后一根 bar 的池子；池子在一根 bar 内的进出不在本面射程。
- 全量冒烟未在本轮改动后重跑（本轮改动=新脚本 + 一条链腿）；`--selftest` 与链腿单跑已过。
- 与 `results/cb_dual_low.json` 的年化数字没有交叉重算——本面不重新发明那本书的收益，
  只把它点名的池子按整手网格定价。
