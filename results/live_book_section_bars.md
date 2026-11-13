# CEO 页面：这一页是哪一天的（r1533）

*由 `scripts/live_book_section_bars.py` 生成；判据见文件头。*

页面头部写着按 2026-11-12 定价，但 48 个带日期的节里只有 34 节真在这一天；其余 14 节最旧停在 2026-10-26（最差 sample_window 落后 13 个交易日），另外 8 节根本没有日期——它们不是同一根 bar 上的数，读的时候不能互相加减。这 14 节里，8 节的产物有同名链腿在守，6 节没有任何一条链腿重跑过它们（lookahead, universe_lock, cash_handshake, cash_ladder, cash_money, cash_yield）——没有腿的那些停在天，是因为没人重跑，不是因为设计。

页面逐节 bar：头部声明 **2026-11-12**，48 个带日期的节里 **34** 节在这一天，其余 14 节在别的 bar 上。

| 节 | 它停在哪根 bar | 落后（交易日） | 守它的链腿 |
|---|---|---|---|
| sample_window | 2026-10-26 | 13 | etf_book_spanning |
| cost_tape | 2026-10-30 | 9 | etf_book_cost_tape |
| lookahead | 2026-10-30 | 9 | **没有** |
| universe_lock | 2026-10-30 | 9 | **没有** |
| vol_window | 2026-10-30 | 9 | etf_book_vol_window_edge、etf_book_vol_window_phase |
| vol_window_edge | 2026-10-30 | 9 | etf_book_vol_window_edge |
| family_coherence | 2026-11-06 | 4 | etf_book_phase_atlas_arms |
| vol_target_gate | 2026-11-08 | 4 | vol_target_gate |
| band_ruler | 2026-11-11 | 1 | etf_book_band_ruler |
| cash_handshake | 2026-11-11 | 1 | **没有** |
| cash_ladder | 2026-11-11 | 1 | **没有** |
| cash_money | 2026-11-11 | 1 | **没有** |
| …其余 2 节 | | | |

「守它的链腿」是按名字匹配的链清单（腿名含该节的名字或产物名），只回答「有没有一条腿会重跑它」，不回答那条腿上次过没过——这两件事在页面上一向是两个错。印「没有」的那几节，才是这一页真正的缺口。

这 8 节没有任何日期字段，本面**不替它们认领**任何一根 bar：backtest_band, agreement, sources, priced_faces, research_arc, permission, sibling_gap, authority。
