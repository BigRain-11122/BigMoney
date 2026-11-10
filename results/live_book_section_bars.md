# CEO 页面：这一页是哪一天的（r1533）

*由 `scripts/live_book_section_bars.py` 生成；判据见文件头。*

页面头部写着按 2026-11-10 定价，但 31 个带日期的节里只有 8 节真在这一天；其余 23 节最旧停在 2026-10-26（最差 sample_window 落后 11 个交易日），另外 19 节根本没有日期——它们不是同一根 bar 上的数，读的时候不能互相加减。

页面逐节 bar：头部声明 **2026-11-10**，31 个带日期的节里 **8** 节在这一天，其余 23 节在别的 bar 上。

| 节 | 它停在哪根 bar | 落后（交易日） |
|---|---|---|
| sample_window | 2026-10-26 | 11 |
| cost_tape | 2026-10-30 | 7 |
| leg_split | 2026-10-30 | 7 |
| lookahead | 2026-10-30 | 7 |
| universe_lock | 2026-10-30 | 7 |
| vol_window | 2026-10-30 | 7 |
| vol_window_edge | 2026-10-30 | 7 |
| band_ruler | 2026-11-03 | 5 |
| window_label | 2026-11-03 | 5 |
| bets | 2026-11-06 | 2 |
| causal_rebuild | 2026-11-06 | 2 |
| concentration | 2026-11-06 | 2 |
| …其余 11 节 | | |

这 19 节没有任何日期字段，本面**不替它们认领**任何一根 bar：cash_yield, cash_money, cash_ladder, forward, backtest_band, money_cny, ticket_book, same_beta_benchmark, agreement, sources, priced_faces, cash_handshake。
