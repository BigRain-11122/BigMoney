# RW-1 出场未来函数修复 · 6 在册员新旧读数对照表（2026-09-30 r472 bm-a）

- 票：T-2026-09-30-127（RW-1）· 决策 D-20260930-05 · 审计 `docs/audits/bigmoney-credibility-audit-20260930.md` P0-1
- 修复：出场由「当日 close 信号当日 close 成交」（未来函数）改为 **T+1 open 成交**（engine/backtester.py，与入场同因果律）
- 证据：`results/_r472bma_rw1_probe.py`（合成腿证明：出场信号 01-13 → 01-14 open 107.0 成交，非旧 close 106.5）+ `results/_r472bma_rw1_probe.json`
- 锚再冻结：6 员 backtest.in_sample/out_sample 面按同 cutoff 2026-09-22 重冻结（cost_x2 seed=历史证据未动，rolling x2 检查对 vi_bar 不对本表）
- smoke：新断言 `exits fill at T+1 open (RW-1)` PASS（40 出场 0 违例）· 全套 **27/27 PASS**

## OOS Sharpe 旧 → 新（诚实披露高估幅度）

| 交易员 | OOS 旧 | OOS 新 | Δ | OOS 年化 旧→新 | 笔数 旧→新 |
|---|---|---|---|---|---|
| COMPOSITE-CE-01 | 1.7479 | 0.8620 | **−0.886 (−51%)** | 13.7%→7.5% | 181→164 |
| COMPOSITE-CE-02 | 1.6392 | 1.5605 | −0.079 | 11.4%→10.2% | 279→257 |
| DROUGHT-CE-01 | 1.2130 | 1.2407 | +0.028 | 4.1%→4.3% | 44→41 |
| ENGULF-CE-01 | 0.3835 | 0.1686 | −0.215 | 1.2%→0.5% | 46→43 |
| NEEDLE-DE-01 | 0.4089 | 0.1927 | −0.216 | 1.2%→0.5% | 23→19 |
| VOLATILITY-CE-01 | 2.0568 | 1.7166 | −0.340 | 4.2%→3.6% | 147→131 |

- 结论一句话：6 员中 4 员 OOS Sharpe 被旧出场律高估（最大 −51%），2 员小幅变化；**旧读数一律不得再引用**（10-31 前禁向 CEO 报未重算 Sharpe 的执行面）。
- IS 面全表与 max_dd/trades 见 `results/_r472bma_rw1_probe.json`（delta 字段）。
- 后续：RW-2/3/4 完成后 RW-6 出全量「旧 vs 新」终表（含 null 池 + T-28 基线 + 判线 v2）。
