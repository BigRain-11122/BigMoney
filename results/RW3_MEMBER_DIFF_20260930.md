# RW-3 成本口径归一——六员重算差异表（old vs new）

- **日期**: 2026-09-30 · r475 bm-a · T-202609-30-127 RW-3（D-20260930-05 验收窗 10-03）
- **机器证据**: `results/_r475bma_rw3_probe.json`（探针 `_r475bma_rw3_probe.py`·锚定门同路径确定性重推导·零网络零新批）+ smoke 33/33（新增 2 条 RW-3 断言）+ t03 引擎完整性自检 32/32（修复 RW-1 遗留的 2 条陈旧夹具）
- **一句话结论**: **六员锚面 old vs new 全恒等（0/6 moved·24 个冻结字段逐位一致）**——full-pnl 不触碰权益曲线（只加 *_full 报告键），strict_open_fills 在六员 core48 历史上零停牌日挂单成交（无行为分叉）。翻面零风险实证，无需重冻结。

## 逐员读数（IS/OOS Sharpe·交易数：冻结值 → 新口径重算值）

| 员 | IS Sharpe | OOS Sharpe | OOS trades | 判定 |
|---|---|---|---|---|
| COMPOSITE-CE-01 | 1.1244 → 1.1244 | 0.862 → 0.862 | 164 → 164 | 恒等 |
| COMPOSITE-CE-02 | 0.7841 → 0.7841 | 1.5605 → 1.5605 | 257 → 257 | 恒等 |
| DROUGHT-CE-01 | 0.461 → 0.461 | 1.2407 → 1.2407 | 41 → 41 | 恒等 |
| ENGULF-CE-01 | 0.5337 → 0.5337 | 0.1686 → 0.1686 | 43 → 43 | 恒等 |
| NEEDLE-DE-01 | 0.6862 → 0.6862 | 0.1927 → 0.1927 | 19 → 19 | 恒等 |
| VOLATILITY-CE-01 | 1.103 → 1.103 | 1.7166 → 1.7166 | 131 → 131 | 恒等 |

（max_dd/annual 两列同恒等，探针 JSON 逐字段在证；上表为 CEO 面主判读数。）

## RW-3 四件落地清单

1. **单一来源正典件** = `knowledge/cost_spec.py`：Face A（活跃口径）13.041bp/边由 `FeeSchedule` 四件套现算（佣金2.5+经手0.341+证管0.2+滑点10bp）+ `verify()` 自检锁 G2 记录值；Face B（网格冻结面）13.0bp 留档声明口径，新网格批（RW-5 解冻后）必须改用 Face A。
2. **七面接线**：`engine/backtester.py`（cost_rate 派生）、`live/paper.py`、`scripts/ce_transfer.py`、`scripts/combined_exit_screen.py`（COST_X1_RATE 三处本地字面量→import 派生）、`scripts/science_gates.py`（COST_X2_RATE→2×派生）、`scripts/grid_paper.py`+`grid_sleeve_p1.py`（13.0/26.0/PASSIVE_COST→冻结面常量引用，数值逐位不变=档存重估律）。
3. **默认翻面（审计件②③）**：引擎 `trade_pnl_mode` 默认 legacy→**full**（每笔 pnl 含买方成本，~13bp/笔不再漏记）；`strict_open_fills` 默认 False→**True**（停牌日 ffilled 陈旧 bar 不再成交）。翻面前序=先落参后翻默认（对账件「慎」节照办）：六员 JSON 显式钉新口径、22 个 PROSPECT 员 JSON 显式钉冻结时申报口径（legacy——P-5 冻结证据面继续可复现，t24 selftest ALL PASS）。
4. **三面同 bar 同价同成本自检** = smoke 新断言：同一根 ¥100k bar 上 engine/paper/x2 三面 130.41 恒等 + 网格旧面偏差=申报 0.041bp（¥0.41）逐分核对。

## 陈旧夹具修复（t03 引擎自检 29/31→32/32）

- RW-1（出场 T+1 open）遗留 2 条过时断言：F2 legacy 出场日期期望 day12 同收盘（现=day13 ffilled open）、F1 win_rate 翻面夹具的开盘价不承载涨幅（现按 T+1 open 语义补齐 W/T/L 三腿开盘价）。
- RW-3 键集断言升级：legacy 钉参跑=精确 7 历史键；默认跑=7+3（win_rate_full/profit_factor_full/avg_pnl_full）。

## 引用纪律（D-20260930-22 律延续）

本表只报重算事实；六员 OOS Sharpe 旧数作废面不变（以 RW-1 差异表为准），RW-6 全量重算（null 池+T-28 基线+判线 v2）仍按票面在 RW-1~4 全绿后一次跑清。

*本件为研究产出非投资建议；所有数字为回测/纸盘口径，非实盘业绩。*
