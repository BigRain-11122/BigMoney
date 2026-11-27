# QA — r2206 bm-c ｜ ETF 票据族从 11-26 推到 11-27

## 本轮唯一使命（S1 修红）

上一轮冒烟（`logs/smoke_legs.json`，ts `2026-11-28T06:56:04`）：`pass=762 fail=46`。
46 条红里最大的同族簇不是算法错，而是**票面代差**——盘上最新票据是
`results/etf_book_order/TICKET-2026-11-27-card.json`（2026-11-27 21:37:19 落盘），
而下游十张决策面仍印 `TICKET-2026-11-26`。

按 r1850/r1934 判例：这类「面落后一档」不是代码缺陷，是**写者没跑**；正法=让写者跑，
不是放宽腿。

## 做了什么

`python Tools\s6_chain_bmc.py 2206 --only=<11 腿>`（顺序即写者依赖序）：

| 腿 | rc | 耗时 | 刷新 | 判词/回执 |
|---|---|---|---|---|
| `year_concentration_money` | 0 | 0.4s | +0.1s | 最薄那本是 nobond_base：top-2 份额 70.83% vs 70.00% 线，只差 0.83pp |
| `entry_price_write` | 0 | 3.4s | +1.1s | `ENTRY_PRICE_IS_THE_COMMISSION_FLOOR` / 8 rungs |
| `etf_book_size_rulers_write` | 0 | 45.8s | — | 重写落盘 |
| `capacity_ticket` | 0 | 3.4s | +1.1s | `TRADABLE_IN_EVERY_READ_SESSION` |
| `ticket_band` | 0 | 5.6s | +1.9s | `BOTH_LINES_HOLD_AT_SIGNED` / moved_inputs=[] |
| `ticket_floor_write` | 0 | 43.5s | +41.2s | `TRADABLE_AT_1000000` / capital 1,000,000 |
| `capital_union_decision` | 0 | 0.3s | +0.1s | face matches a fresh rebuild |
| `rebalance_permission_write` | 0 | 0.1s | — | 重写落盘 |
| `cash_roll_today` | 0 | 3.6s | +1.2s | 重写落盘 |
| `decision_line_write` | 0 | 0.1s | — | → `results/etf_book_decision_line.json` |
| `permission_vs_size_write` | 0 | 1.1s | — | `SIZE_IS_THE_ONLY_KNOB` / permission=ADMIT |

**11/11 rc0**，记录件 `results/_r2206bmc_s6_chain.only-capacity_ticket-capital_union_decision+11-b9b5c3ff.json`（3,240B），
控制台全文 `logs/_r2206_s6_ticket_family.log`。

## 落地复核（票据真的换了）

| 面 | evidence_cutoff | ticket |
|---|---|---|
| `etf_book_ticket_band.json` | 2026-11-27 | `…/TICKET-2026-11-27-card.json` |
| `etf_book_ticket_floor.json` | 2026-11-27 | `…/TICKET-2026-11-27-card.json` |
| `etf_book_capacity_ticket.json` | 2026-11-27 | `…/TICKET-2026-11-27-card.json` |
| `capital_union_decision.json` | 2026-11-27 | — |
| `etf_book_decision_line.json` | generated 2026-11-28T07:06:22+0800 | — |
| `etf_book_cash_roll_today.json` | generated 2026-11-28T07:06:20+0800 | — |

## 红项覆盖（如实口径，不宣称已清）

46 条红中，**13 条点名了本轮刷新的面**：

1. `etf_book_entry_price (every bp re-derived…)`
2. `etf_book_permission_vs_size (permission and lot words…)`
3. `etf_book_size_rulers_decision (desk sentence…)`
4. `etf_book_rebalance_permission (permission re-derived)`
5. `etf_book_decision_line (row re-derived from the receipts)`
6. `etf_book_capacity_ticket (rungs re-derived…)`
7. `etf_book_ticket_band (both lines folded…)`
8. `etf_book_ticket_band (face re-derives from the two source faces)`
9. `etf_book_cash_roll_today (instruction re-derived from disk)`
10. `etf_book_ticket_floor (published legs and floor…)`
11. `capital_union_decision (published union…)`
12. `year_concentration_money (top-2 year shares…)`
13. `year_concentration_money (published money face…)`

**未做、不宣称**：全量冒烟未复跑（上一轮实测 ~960s，本轮预算不够），因此**不声称
fail 由 46 降到 33**——链腿自己的 `check` 已 rc0（这是同一谓词），下一轮冒烟的数字才是判据。

## 仍在红的其它族（本轮未动，留账）

- `etf_book_phase_admission` / `etf_book_start_grid`（exit 3，上游 year-gate 换字节）
- `etf_book_premium_*` 三面（`PREMIUM-2026-11-27.json` 已落，读者仍读 11-26）
- `astock_resid_veto_layer`（面板推到 11-27，面停 11-26）
- `config: no card or digest carries a control character` —— `knowledge/METHODOLOGY_ASSETS.md:18125` 有一个 `0x08`
- `config: 159519 MONEY_ON_FOREIGN_NAV`（legs/4 红）

## S7 守卫

`python scripts\attrition_ledger_guard.py scan` → **CLEAN**（4 账本，3 处历史缩行 healed），
证据 `results/_attrition_guard_scan.json`。
