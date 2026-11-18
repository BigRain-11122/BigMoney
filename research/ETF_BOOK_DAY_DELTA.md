# 隔夜差：同一根 bar 上，这页动了哪些数（r1761）

- 比较：`LIVE-BOOK-20261117.json` → `LIVE-BOOK-20261118.json`
- 价格依据：2026-11-17（前一天 2026-11-17）｜数据截止：2026-11-17（前一天 2026-11-17）
- 判决：**UNEXPLAINED_MOVES**

## 一句话
两天**是同一根 bar**（没有新数据进来），这页有 **790** 个数变了；其中 **6** 个是钟面（机器多久没说话之类，本来就该走）、**708** 个能给出解释（旧数还在页上／口径句改了／这一节换了代／这一节换了定价的输入／这个数只是转抄别面）、**76** 个没解释。新增 **395** 个数字叶子、消失 **0** 个。

## 动的数（全部 790 个）

| 数字 | 昨天 | 今天 | 判读 | 依据 |
|---|---|---|---|---|
| `/admission/capacity_cny` | 18582410.0 | 15993296.0 | SECTION_ADVANCED | 这一节自己换了代：`admission` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/admission/concentration_caliber/gap_pp` | 3.13 | 3.14 | SECTION_ADVANCED | 这一节自己换了代：`admission` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/admission/concentration_caliber/lag0_pct` | 71.04 | 71.05 | SECTION_ADVANCED | 这一节自己换了代：`admission` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/admission/concentration_caliber/lag1_cagr_pct` | 10.38 | 10.37 | SECTION_ADVANCED | 这一节自己换了代：`admission` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/admission/concentration_caliber/lag1_pct` | 74.17 | 74.19 | SECTION_ADVANCED | 这一节自己换了代：`admission` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/admission/margin_to_line` | -0.0104 | -0.0105 | SECTION_ADVANCED | 这一节自己换了代：`admission` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/admission/prior/top2_share` | 0.7084 | 0.7104 | SECTION_ADVANCED | 这一节自己换了代：`admission` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/admission/reads/capacity_by_capital/10M/impact_pct_of_adv` | 10.0865 | 10.028 | SECTION_ADVANCED | 这一节自己换了代：`admission` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/admission/reads/capacity_by_capital/1M/impact_pct_of_adv` | 1.0087 | 1.0028 | SECTION_ADVANCED | 这一节自己换了代：`admission` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/admission/reads/oos_sharpe` | 1.8016 | 1.7997 | SECTION_ADVANCED | 这一节自己换了代：`admission` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/admission/top2_share` | 0.7104 | 0.7105 | SECTION_ADVANCED | 这一节自己换了代：`admission` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/admission/worst` | 1.9416 | 1.9241 | SECTION_ADVANCED | 这一节自己换了代：`admission` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/backtest_band/5 名·可执行单口径（本单这份账）/full/cagr_pct` | 7.6 | 7.58 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/band_ruler/cells/book/card/causal/full/bars` | 1665 | 1666 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/card/causal/full/cagr` | 0.1542 | 0.1537 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/card/causal/full/cagr_pp` | 15.42 | 15.37 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/card/causal/full/sharpe` | 0.984 | 0.981 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/card/causal/full/vol` | 0.1659 | 0.1658 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/card/causal/full/years` | 6.87 | 6.88 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/card/causal/oos/bars` | 695 | 696 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/card/causal/oos/cagr` | 0.2473 | 0.246 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/card/causal/oos/cagr_pp` | 24.73 | 24.6 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/card/causal/oos/sharpe` | 1.51 | 1.504 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/card/causal/oos/vol` | 0.1614 | 0.1613 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/card/causal/oos/years` | 2.87 | 2.88 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/card/causal/ticket_window/bars` | 695 | 696 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/card/causal/ticket_window/cagr` | 0.2473 | 0.246 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/card/causal/ticket_window/cagr_pp` | 24.73 | 24.6 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/card/causal/ticket_window/sharpe` | 1.51 | 1.504 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/card/causal/ticket_window/vol` | 0.1614 | 0.1613 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/card/causal/ticket_window/years` | 2.87 | 2.88 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/card/published/full/bars` | 1664 | 1665 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/card/published/full/cagr` | 0.1593 | 0.1592 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/card/published/full/cagr_pp` | 15.93 | 15.92 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/card/published/full/sharpe` | 1.023 | 1.022 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/card/published/oos/bars` | 695 | 696 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/card/published/oos/cagr` | 0.2379 | 0.2375 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/card/published/oos/cagr_pp` | 23.79 | 23.75 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/card/published/oos/sharpe` | 1.498 | 1.496 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/card/published/oos/vol` | 0.157 | 0.1569 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/card/published/oos/years` | 2.87 | 2.88 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/card/published/ticket_window/bars` | 695 | 696 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/card/published/ticket_window/cagr` | 0.2379 | 0.2375 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/card/published/ticket_window/cagr_pp` | 23.79 | 23.75 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/card/published/ticket_window/sharpe` | 1.498 | 1.496 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/card/published/ticket_window/vol` | 0.157 | 0.1569 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/card/published/ticket_window/years` | 2.87 | 2.88 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/ticket/causal/full/bars` | 1665 | 1666 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/ticket/causal/full/cagr` | 0.1657 | 0.1652 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/ticket/causal/full/cagr_pp` | 16.57 | 16.52 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/ticket/causal/full/sharpe` | 1.014 | 1.011 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/ticket/causal/full/years` | 6.87 | 6.88 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/ticket/causal/oos/bars` | 695 | 696 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/ticket/causal/oos/cagr` | 0.263 | 0.2617 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/ticket/causal/oos/cagr_pp` | 26.3 | 26.17 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/ticket/causal/oos/sharpe` | 1.556 | 1.55 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/ticket/causal/oos/vol` | 0.1655 | 0.1654 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/ticket/causal/oos/years` | 2.87 | 2.88 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/ticket/causal/ticket_window/bars` | 695 | 696 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/ticket/causal/ticket_window/cagr` | 0.263 | 0.2617 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/ticket/causal/ticket_window/cagr_pp` | 26.3 | 26.17 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/ticket/causal/ticket_window/sharpe` | 1.556 | 1.55 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/ticket/causal/ticket_window/vol` | 0.1655 | 0.1654 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/ticket/causal/ticket_window/years` | 2.87 | 2.88 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/ticket/published/full/bars` | 1664 | 1665 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/ticket/published/full/cagr` | 0.1747 | 0.1746 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/ticket/published/full/cagr_pp` | 17.47 | 17.46 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/ticket/published/oos/bars` | 695 | 696 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/ticket/published/oos/cagr` | 0.2581 | 0.2578 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/ticket/published/oos/cagr_pp` | 25.81 | 25.78 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/ticket/published/oos/sharpe` | 1.563 | 1.562 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/ticket/published/oos/vol` | 0.1617 | 0.1616 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/ticket/published/oos/years` | 2.87 | 2.88 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/ticket/published/ticket_window/bars` | 695 | 696 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/ticket/published/ticket_window/cagr` | 0.2581 | 0.2578 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/ticket/published/ticket_window/cagr_pp` | 25.81 | 25.78 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/ticket/published/ticket_window/sharpe` | 1.563 | 1.562 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/ticket/published/ticket_window/vol` | 0.1617 | 0.1616 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/book/ticket/published/ticket_window/years` | 2.87 | 2.88 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/card/12/vol08/full/bars` | 1664 | 1665 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/card/12/vol08/full/cagr` | 0.0941 | 0.0943 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/card/12/vol08/full/cagr_pp` | 9.41 | 9.43 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/card/12/vol08/full/sharpe` | 0.971 | 0.973 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/card/12/vol08/oos/bars` | 695 | 696 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/card/12/vol08/oos/cagr` | 0.1772 | 0.1776 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/card/12/vol08/oos/cagr_pp` | 17.72 | 17.76 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/card/12/vol08/oos/sharpe` | 1.681 | 1.685 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/card/12/vol08/oos/vol` | 0.1046 | 0.1045 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/card/12/vol08/oos/years` | 2.87 | 2.88 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/card/12/vol08/ticket_window/bars` | 695 | 696 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/card/12/vol08/ticket_window/cagr` | 0.1772 | 0.1776 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/card/12/vol08/ticket_window/cagr_pp` | 17.72 | 17.76 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/card/12/vol08/ticket_window/sharpe` | 1.681 | 1.685 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/card/12/vol08/ticket_window/vol` | 0.1046 | 0.1045 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/card/12/vol08/ticket_window/years` | 2.87 | 2.88 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/card/cost10/full/bars` | 1537 | 1538 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/card/cost10/full/cagr` | 0.0702 | 0.07 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/card/cost10/full/cagr_pp` | 7.02 | 7.0 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/card/cost10/full/sharpe` | 1.269 | 1.266 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/card/cost10/oos/bars` | 695 | 696 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/card/cost10/oos/cagr` | 0.1178 | 0.1173 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/card/cost10/oos/cagr_pp` | 11.78 | 11.73 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/card/cost10/oos/sharpe` | 1.631 | 1.625 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/card/cost10/oos/years` | 2.87 | 2.88 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/card/cost10/ticket_window/bars` | 695 | 696 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/card/cost10/ticket_window/cagr` | 0.1178 | 0.1173 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/card/cost10/ticket_window/cagr_pp` | 11.78 | 11.73 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/card/cost10/ticket_window/sharpe` | 1.631 | 1.625 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/card/cost10/ticket_window/years` | 2.87 | 2.88 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/card/full/bars` | 1537 | 1538 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/card/full/cagr` | 0.0717 | 0.0715 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/card/full/cagr_pp` | 7.17 | 7.15 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/card/full/sharpe` | 1.295 | 1.291 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/card/full/vol` | 0.0569 | 0.0568 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/card/oos/bars` | 695 | 696 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/card/oos/cagr` | 0.1199 | 0.1193 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/card/oos/cagr_pp` | 11.99 | 11.93 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/card/oos/sharpe` | 1.657 | 1.65 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/card/oos/vol` | 0.073 | 0.0729 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/card/oos/years` | 2.87 | 2.88 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/card/ticket_window/bars` | 695 | 696 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/card/ticket_window/cagr` | 0.1199 | 0.1193 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/card/ticket_window/cagr_pp` | 11.99 | 11.93 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/card/ticket_window/sharpe` | 1.657 | 1.65 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/card/ticket_window/vol` | 0.073 | 0.0729 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/card/ticket_window/years` | 2.87 | 2.88 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/ticket/full/bars` | 1537 | 1538 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/ticket/full/cagr` | 0.076 | 0.0758 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/ticket/full/cagr_pp` | 7.6 | 7.58 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/ticket/full/sharpe` | 1.324 | 1.32 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/ticket/oos/bars` | 695 | 696 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/ticket/oos/cagr` | 0.1245 | 0.1239 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/ticket/oos/cagr_pp` | 12.45 | 12.39 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/ticket/oos/sharpe` | 1.697 | 1.691 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/ticket/oos/vol` | 0.0738 | 0.0737 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/ticket/oos/years` | 2.87 | 2.88 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/ticket/ticket_window/bars` | 695 | 696 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/ticket/ticket_window/cagr` | 0.1245 | 0.1239 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/ticket/ticket_window/cagr_pp` | 12.45 | 12.39 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/ticket/ticket_window/sharpe` | 1.697 | 1.691 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/ticket/ticket_window/vol` | 0.0738 | 0.0737 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/cells/held/causal/ticket/ticket_window/years` | 2.87 | 2.88 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/dial_prices/ordering/price_pp` | -0.51 | -0.55 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/dial_prices/window/price_pp` | 4.82 | 4.78 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/identity/card 18.35% (2024+) reproduced on its own ruler/measured_pp` | 17.97 | 17.72 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/identity/card 18.35% (2024+) reproduced on its own ruler/published_pp` | 17.97 | 17.72 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/identity/card 9.60% reproduced on its own ruler/measured_pp` | 9.51 | 9.41 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/identity/card 9.60% reproduced on its own ruler/published_pp` | 9.51 | 9.41 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/identity/ticket 12.78% reproduced on its own ruler/measured_pp` | 12.54 | 12.45 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/identity/ticket 12.78% reproduced on its own ruler/published_pp` | 12.54 | 12.45 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/published_faces/card_full` | 9.51 | 9.41 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/published_faces/card_oos` | 17.97 | 17.72 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/published_faces/rows/0/full` | 7.64 | 7.6 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/published_faces/rows/0/oos` | 12.54 | 12.45 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/published_faces/rows/1/full` | 15.55 | 15.5 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/published_faces/rows/1/oos` | 23.42 | 23.29 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/published_faces/rows/2/full` | 9.51 | 9.41 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/published_faces/rows/2/oos` | 17.97 | 17.72 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/published_faces/ticket` | 7.64 | 7.6 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/band_ruler/published_faces/ticket_oos` | 12.54 | 12.45 | SECTION_ADVANCED | 这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cash_caliber/control_error_bp` | 0.0043 | 0.0357 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_ladder/rolls/GC028` | 12 | 13 | RECOVERED_OLD_VALUE | 昨天的 12 今天仍在这页上：`/alias_stability/families/n_cross_name`（改名，不是重算） |
| `/cash_ladder/tenors/1/annual_cny_spot` | 7016.0 | 7045.0 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_ladder/tenors/1/mean250_pct` | 1.3611 | 1.3607 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_ladder/tenors/1/spot_pct` | 1.235 | 1.24 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_ladder/tenors/2/annual_cny_spot` | 7414.0 | 7670.0 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_ladder/tenors/2/mean250_pct` | 1.4624 | 1.462 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_ladder/tenors/2/spot_pct` | 1.305 | 1.35 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_ladder/tenors/3/annual_cny_spot` | 7670.0 | 7755.0 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_ladder/tenors/3/mean250_pct` | 1.4673 | 1.4669 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_ladder/tenors/3/spot_pct` | 1.35 | 1.365 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_ladder/tenors/4/annual_cny_realized_1y` | 8372.0 | 8325.0 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_ladder/tenors/4/annual_cny_spot` | 7698.0 | 7812.0 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_ladder/tenors/4/edge_bp/1` | 16.6 | 15.8 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_ladder/tenors/4/edge_bp/5` | 9.0 | 8.0 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_ladder/tenors/4/idle_share_1y` | 0.0059 | 0.0055 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_ladder/tenors/4/mean250_pct` | 1.4628 | 1.4624 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_ladder/tenors/4/realized/1/days` | 338 | 366 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_ladder/tenors/4/realized/1/idle_share` | 0.0059 | 0.0055 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_ladder/tenors/4/realized/1/realized_pct` | 1.4737 | 1.4654 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_ladder/tenors/4/realized/1/rolls` | 12 | 13 | RECOVERED_OLD_VALUE | 昨天的 12 今天仍在这页上：`/alias_stability/families/n_cross_name`（改名，不是重算） |
| `/cash_ladder/tenors/4/realized/5/days` | 1798 | 1826 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_ladder/tenors/4/realized/5/realized_pct` | 1.9789 | 1.9695 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_ladder/tenors/4/realized/5/rolls` | 64 | 65 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_ladder/tenors/4/rolls_1y` | 12 | 13 | RECOVERED_OLD_VALUE | 昨天的 12 今天仍在这页上：`/alias_stability/families/n_cross_name`（改名，不是重算） |
| `/cash_ladder/tenors/4/spot_pct` | 1.355 | 1.375 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_ladder/tenors/5/annual_cny_spot` | 7471.0 | 7499.0 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_ladder/tenors/5/mean250_pct` | 1.4335 | 1.4329 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_ladder/tenors/5/spot_pct` | 1.315 | 1.32 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_money/block/book_rate/annual_cny` | 10067.0 | 10065.0 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_money/block/book_rate/gap_vs_spot_bp` | -59.7 | -59.66 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_money/block/book_rate/gap_vs_spot_cny` | -3392.0 | -3389.0 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_money/block/book_rate/pct` | 1.772 | 1.7716 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_money/forward/book/pct` | 1.772 | 1.7716 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_money/forward/gap_bp` | 85.77 | 85.73 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/cash_money/forward/gap_bp_gross` | 59.7 | 59.66 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/causal_rebuild/elapsed_sec` | 50.0 | 47.7 | CLOCK |  |
| `/cost_tape/arms/assumed_10bp/cagr` | 0.0941 | 0.0943 | SECTION_ADVANCED | 这一节自己换了代：`cost_tape` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cost_tape/arms/assumed_10bp/sharpe` | 0.971 | 0.973 | SECTION_ADVANCED | 这一节自己换了代：`cost_tape` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cost_tape/arms/measured/cagr` | 0.0993 | 0.0995 | SECTION_ADVANCED | 这一节自己换了代：`cost_tape` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cost_tape/arms/measured/sharpe` | 1.019 | 1.021 | SECTION_ADVANCED | 这一节自己换了代：`cost_tape` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cost_tape/arms/upper_p75/cagr` | 0.0954 | 0.0955 | SECTION_ADVANCED | 这一节自己换了代：`cost_tape` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cost_tape/arms/upper_p75/sharpe` | 0.983 | 0.985 | SECTION_ADVANCED | 这一节自己换了代：`cost_tape` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cost_tape/control/engine_cagr` | 0.0941 | 0.0943 | SECTION_ADVANCED | 这一节自己换了代：`cost_tape` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/cost_tape/tape/widest_traded/1/p50_bp` | 30.8 | 30.7 | SECTION_ADVANCED | 这一节自己换了代：`cost_tape` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/exposure_timing/arms/constant/cagr` | 0.0996 | 0.0993 | SECTION_ADVANCED | 这一节自己换了代：`exposure_timing` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/exposure_timing/arms/constant/sharpe` | 0.965 | 0.962 | SECTION_ADVANCED | 这一节自己换了代：`exposure_timing` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/exposure_timing/arms/full/cagr` | 0.1307 | 0.1303 | SECTION_ADVANCED | 这一节自己换了代：`exposure_timing` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/exposure_timing/arms/full/sharpe` | 0.913 | 0.911 | SECTION_ADVANCED | 这一节自己换了代：`exposure_timing` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/exposure_timing/arms/full/vol` | 0.153 | 0.1529 | SECTION_ADVANCED | 这一节自己换了代：`exposure_timing` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/exposure_timing/arms/production/cagr` | 0.0898 | 0.0895 | SECTION_ADVANCED | 这一节自己换了代：`exposure_timing` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/exposure_timing/arms/production/delevered_share` | 0.8799 | 0.88 | SECTION_ADVANCED | 这一节自己换了代：`exposure_timing` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/exposure_timing/arms/production/mean_exposure` | 0.7078 | 0.7079 | SECTION_ADVANCED | 这一节自己换了代：`exposure_timing` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/exposure_timing/arms/production/sharpe` | 0.941 | 0.938 | SECTION_ADVANCED | 这一节自己换了代：`exposure_timing` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/exposure_timing/bars` | 1665 | 1666 | SECTION_ADVANCED | 这一节自己换了代：`exposure_timing` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/exposure_timing/placebo/cagr_mean` | 0.0996 | 0.0994 | SECTION_ADVANCED | 这一节自己换了代：`exposure_timing` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/exposure_timing/verdict/de_risking_pp` | -3.11 | -3.1 | SECTION_ADVANCED | 这一节自己换了代：`exposure_timing` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/exposure_timing/verdict/placebo_p05_pp` | -1.74 | -1.75 | SECTION_ADVANCED | 这一节自己换了代：`exposure_timing` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/feed_lag_days` | 0 | 1 | CLOCK |  |
| `/fleet/rows/0/age_h` | 1.24 | 1.1 | CLOCK |  |
| `/fleet/rows/1/age_h` | 441.79 | 460.16 | CLOCK |  |
| `/fleet/rows/2/age_h` | 4.18 | 2.63 | CLOCK |  |
| `/futures_hedge/beta` | 0.07185718963947142 | 0.07458300567364223 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_hedge/capital_for_one_lot` | 11395936.91471321 | 10985880.665433725 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_hedge/corr` | 0.1373365917783091 | 0.1415643988218339 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_hedge/maxdd_delta_pp` | 1.5453866010586514 | -0.05485315943003499 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_hedge/min_unit_notional` | 818880.0 | 819360.0 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_hedge/sharpe_delta` | 0.005735999804863057 | -0.020536000001067034 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_hedge/splice_days_dropped` | 1 | 85 | RECOVERED_OLD_VALUE | 昨天的 1 今天仍在这页上：`/alias_stability/families/rows/0/pair_stability/n_pairs`（改名，不是重算） |
| `/futures_hedge/unit_over_target` | 11.395936914713209 | 10.985880665433726 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_hedge/variance_removable_pct` | 1.8861339441281915 | 2.004047901378724 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_hedge/vol_delta_pp` | -0.09457028960696418 | -0.10122922788117772 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_hedge_tail/dsharpe` | 0.005735999804863057 | -0.020536000001067034 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_hedge_tail/dsharpe_hi` | 0.09446056903527693 | 0.0719002244924948 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_hedge_tail/dsharpe_lo` | -0.06366444689345857 | -0.0964202006837476 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_hedge_tail/share_above_uncond` | 0.968 | 0.9695 | RECOVERED_OLD_VALUE | 昨天的 0.968 今天仍在这页上：`/width_return/rows/2/sharpe`（改名，不是重算） |
| `/futures_hedge_tail/tail_beta` | 0.6115545672996576 | 0.6126419583867959 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_hedge_tail/tail_ci_hi` | 0.8343491781619469 | 0.8405742148706478 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_hedge_tail/tail_ci_lo` | 0.12672451800387655 | 0.13021062460324065 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_hedge_tail/tail_n` | 57 | 52 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_hedge_tail/uncond_beta` | 0.07185718963947142 | 0.07458300567364223 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/futures_ladder/rows/1/one_lot_notional_cny` | 1175460.0 | 1178520.0 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/2/one_lot_notional_cny` | 818880.0 | 819360.0 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/3/net_pct_of_capital` | 2.63 | 2.62 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/3/net_pct_of_capital_by_mask/calendar` | 3.42 | 3.41 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/3/net_pct_of_capital_by_mask/published` | 2.63 | 2.62 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/3/net_pct_of_capital_by_mask/strictest` | 3.42 | 3.41 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/3/one_lot_notional_cny` | 1204600.0 | 1197480.0 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_ladder/rows/3/vol_contrib_pct` | 6.1 | 6.0 | SECTION_ADVANCED | 这一节自己换了代：`futures_ladder` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_sleeve/rows/0/carry_ann_compound_pct` | 8.778 | 8.753 | SECTION_ADVANCED | 这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_sleeve/rows/0/carry_caliber/calendar_ann_pct` | 9.793 | 9.805 | SECTION_ADVANCED | 这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_sleeve/rows/0/carry_caliber/published_ann_pct` | 2.895 | 2.878 | SECTION_ADVANCED | 这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_sleeve/rows/0/carry_caliber/spread_pp` | 6.898 | 6.927 | SECTION_ADVANCED | 这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_sleeve/rows/0/gap_net_pp` | 6.753 | 6.644 | SECTION_ADVANCED | 这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_sleeve/rows/0/notional_per_lot_cny` | 1243680.0 | 1238960.0 | SECTION_ADVANCED | 这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_sleeve/rows/1/blend_gain_sharpe` | 0.133 | 0.131 | SECTION_ADVANCED | 这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_sleeve/rows/1/carry_ann_compound_pct` | 3.625 | 3.565 | SECTION_ADVANCED | 这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_sleeve/rows/1/carry_caliber/calendar_ann_pct` | 5.795 | 5.843 | SECTION_ADVANCED | 这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_sleeve/rows/1/carry_caliber/published_ann_pct` | 1.923 | 1.876 | SECTION_ADVANCED | 这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_sleeve/rows/1/carry_caliber/spread_pp` | 3.872 | 3.967 | SECTION_ADVANCED | 这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_sleeve/rows/1/gap_net_pp` | 0.558 | 0.651 | SECTION_ADVANCED | 这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_sleeve/rows/1/notional_per_lot_cny` | 1181700.0 | 1175460.0 | SECTION_ADVANCED | 这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_sleeve/rows/2/blend_gain_sharpe` | 0.087 | 0.084 | SECTION_ADVANCED | 这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_sleeve/rows/2/carry_ann_compound_pct` | 2.471 | 2.402 | SECTION_ADVANCED | 这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_sleeve/rows/2/carry_caliber/calendar_ann_pct` | 5.324 | 5.39 | SECTION_ADVANCED | 这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_sleeve/rows/2/carry_caliber/published_ann_pct` | 1.617 | 1.561 | SECTION_ADVANCED | 这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_sleeve/rows/2/carry_caliber/spread_pp` | 3.707 | 3.829 | SECTION_ADVANCED | 这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_sleeve/rows/2/notional_per_lot_cny` | 822720.0 | 818880.0 | SECTION_ADVANCED | 这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_sleeve/rows/3/blend_gain_sharpe` | 0.39 | 0.388 | SECTION_ADVANCED | 这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_sleeve/rows/3/carry_ann_compound_pct` | 10.263 | 10.209 | SECTION_ADVANCED | 这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_sleeve/rows/3/carry_caliber/calendar_ann_pct` | 11.954 | 12.013 | SECTION_ADVANCED | 这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_sleeve/rows/3/carry_caliber/published_ann_pct` | 5.928 | 5.882 | SECTION_ADVANCED | 这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_sleeve/rows/3/carry_caliber/spread_pp` | 6.026 | 6.131 | SECTION_ADVANCED | 这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_sleeve/rows/3/gap_net_pp` | 7.733 | 7.847 | SECTION_ADVANCED | 这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/futures_sleeve/rows/3/notional_per_lot_cny` | 1221000.0 | 1204600.0 | SECTION_ADVANCED | 这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/gap/elapsed_sec` | 48.7 | 48.1 | CLOCK |  |
| `/idle_cash/vehicle_net_pct` | 1.772 | 1.7716 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/leg_split/arms/base_book/bars` | 1665 | 1666 | SECTION_ADVANCED | 这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/leg_split/arms/base_book/buckets_pp_per_year/plain` | 14.022 | 13.986 | SECTION_ADVANCED | 这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/leg_split/arms/base_book/buckets_pp_per_year/toll` | -1.577 | -1.576 | SECTION_ADVANCED | 这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/leg_split/arms/base_book/cagr_pct` | 12.99 | 12.95 | SECTION_ADVANCED | 这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/leg_split/arms/base_book/fill_bar_drag_pp_per_year` | -1.718 | -1.717 | SECTION_ADVANCED | 这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/leg_split/arms/base_book/plain_bars` | 1580 | 1581 | SECTION_ADVANCED | 这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/leg_split/arms/base_book/plain_carry_pp_per_year` | 14.022 | 13.986 | SECTION_ADVANCED | 这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/leg_split/arms/base_book/sharpe` | 0.908 | 0.906 | SECTION_ADVANCED | 这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/leg_split/arms/base_book/total_log_pp` | 12.304 | 12.268 | SECTION_ADVANCED | 这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/leg_split/arms/control_ew/bars` | 1665 | 1666 | SECTION_ADVANCED | 这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/leg_split/arms/control_ew/buckets_pp_per_year/intraday` | -2.151 | -2.15 | SECTION_ADVANCED | 这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/leg_split/arms/control_ew/buckets_pp_per_year/plain` | 6.352 | 6.328 | SECTION_ADVANCED | 这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/leg_split/arms/control_ew/cagr_pct` | 4.01 | 3.99 | SECTION_ADVANCED | 这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/leg_split/arms/control_ew/fill_bar_drag_pp_per_year` | -2.389 | -2.388 | SECTION_ADVANCED | 这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/leg_split/arms/control_ew/plain_bars` | 1580 | 1581 | SECTION_ADVANCED | 这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/leg_split/arms/control_ew/plain_carry_pp_per_year` | 6.351 | 6.328 | SECTION_ADVANCED | 这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/leg_split/arms/control_ew/sharpe` | 0.309 | 0.308 | SECTION_ADVANCED | 这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/leg_split/arms/control_ew/total_log_pp` | 3.963 | 3.94 | SECTION_ADVANCED | 这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/leg_split/arms/production/bars` | 1665 | 1666 | SECTION_ADVANCED | 这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/leg_split/arms/production/buckets_pp_per_year/intraday` | -0.713 | -0.712 | SECTION_ADVANCED | 这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/leg_split/arms/production/buckets_pp_per_year/overnight` | 0.19 | 0.189 | SECTION_ADVANCED | 这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/leg_split/arms/production/buckets_pp_per_year/plain` | 9.759 | 9.728 | SECTION_ADVANCED | 这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/leg_split/arms/production/buckets_pp_per_year/toll` | -1.156 | -1.155 | SECTION_ADVANCED | 这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/leg_split/arms/production/cagr_pct` | 8.35 | 8.32 | SECTION_ADVANCED | 这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/leg_split/arms/production/fill_bar_drag_pp_per_year` | -1.679 | -1.678 | SECTION_ADVANCED | 这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/leg_split/arms/production/plain_bars` | 1580 | 1581 | SECTION_ADVANCED | 这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/leg_split/arms/production/plain_carry_pp_per_year` | 9.76 | 9.727 | SECTION_ADVANCED | 这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/leg_split/arms/production/sharpe` | 0.881 | 0.878 | SECTION_ADVANCED | 这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/leg_split/arms/production/total_log_pp` | 8.081 | 8.05 | SECTION_ADVANCED | 这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/leg_split/selection_wedge_pp/intraday` | 1.504 | 1.503 | SECTION_ADVANCED | 这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/leg_split/selection_wedge_pp/plain` | 7.67 | 7.658 | SECTION_ADVANCED | 这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/leg_split/selection_wedge_pp/toll` | -1.503 | -1.502 | SECTION_ADVANCED | 这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/leg_split/selection_wedge_pp/total` | 8.341 | 8.328 | SECTION_ADVANCED | 这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/lookahead/affected_faces` | 94 | 96 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/lot_floor/capital_needed/AU` | 2782200.0 | 2714400.0 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/lot_floor/capital_needed/IF` | 3918200.0 | 3928400.0 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/lot_floor/capital_needed/IH` | 2729600.0 | 2731200.0 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/lot_floor/capital_needed/IM` | 4015333.3333333335 | 3991600.0 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/lot_floor/capital_needed/SC` | 1938000.0 | 1920333.3333333335 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/lot_floor/capital_needed/T` | 3667000.0 | 3667833.3333333335 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/lot_floor/capital_needed/TS` | 6843066.666666667 | 6843866.666666667 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/lot_floor/etf_shares_at_1m/510300` | 0.000404 | 0.000406 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/lot_floor/etf_shares_at_1m/510500` | 0.000632 | 0.000631 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/lot_floor/etf_shares_at_1m/512100` | 0.000247 | 0.000246 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/lot_floor/etf_shares_at_1m/588000` | 0.000129 | 0.000132 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/lot_floor/shares_at_1m/AU` | 0.83466 | 0.81432 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/lot_floor/shares_at_1m/IF` | 1.17546 | 1.17852 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/lot_floor/shares_at_1m/IH` | 0.81888 | 0.81936 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/lot_floor/shares_at_1m/IM` | 1.2046 | 1.19748 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/lot_floor/shares_at_1m/SC` | 0.5814 | 0.5761 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/lot_floor/shares_at_1m/T` | 1.1001 | 1.10035 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/lot_floor/shares_at_1m/TS` | 2.05292 | 2.05316 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/roster_audit/local_copies/1/laneside/local_disk_n` | 27 | 28 | SECTION_ADVANCED | 这一节自己换了代：`roster_audit` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/roster_audit/local_copies/1/local_disk_n` | 27 | 28 | SECTION_ADVANCED | 这一节自己换了代：`roster_audit` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/sibling_gap/immaterial_gain_cny` | 103.3 | 103.2 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/sibling_gap/pairs/0/amount_cny` | 86400.6 | 86347.8 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/sibling_gap/pairs/0/today_gain_cny` | 103.3 | 103.2 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/sibling_gap/pairs/1/amount_cny` | 86286.0 | 86390.2 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/stress/n_days` | 5282 | 5283 | UNEXPLAINED | 没有旧值留存，也没有口径声明 |
| `/vol_window/paired/rows/0/bars` | 1663 | 1664 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/paired/rows/0/ci_p05_p95_pp/0` | -0.084 | -0.106 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/paired/rows/0/ci_p05_p95_pp/1` | 2.004 | 1.973 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/paired/rows/0/mean_pp` | 0.873 | 0.867 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/paired/rows/0/share_positive` | 0.936 | 0.937 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/paired/rows/1/bars` | 1658 | 1659 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/paired/rows/1/ci_p05_p95_pp/0` | 0.637 | 0.715 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/paired/rows/1/ci_p05_p95_pp/1` | 3.05 | 3.043 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/paired/rows/1/mean_pp` | 1.805 | 1.804 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/paired/rows/1/share_positive` | 0.999 | 0.998 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/paired/rows/2/bars` | 1653 | 1654 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/paired/rows/2/ci_p05_p95_pp/0` | 0.159 | 0.138 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/paired/rows/2/ci_p05_p95_pp/1` | 2.383 | 2.397 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/paired/rows/2/mean_pp` | 1.197 | 1.192 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/paired/rows/2/share_positive` | 0.974 | 0.968 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/paired/rows/3/bars` | 1648 | 1649 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/paired/rows/3/ci_p05_p95_pp/0` | -0.364 | -0.337 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/paired/rows/3/ci_p05_p95_pp/1` | 1.194 | 1.167 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/paired/rows/3/mean_pp` | 0.41 | 0.409 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/paired/rows/3/share_positive` | 0.82 | 0.824 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/paired/verdict/min_ci_low_pp` | -0.364 | -0.337 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/paired/verdict/min_share_positive` | 0.82 | 0.824 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/panel/bars_named` | 5282 | 5283 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/0/cagr` | 0.1032 | 0.1033 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/0/oos_cagr` | 0.19 | 0.1902 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/0/oos_sharpe` | 1.76 | 1.763 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/0/sharpe` | 1.043 | 1.044 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/1/cagr` | 0.1005 | 0.1006 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/1/oos_cagr` | 0.1831 | 0.1835 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/1/oos_sharpe` | 1.731 | 1.734 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/1/sharpe` | 1.035 | 1.036 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/10/cagr` | 0.0995 | 0.0999 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/10/oos_cagr` | 0.1863 | 0.187 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/10/oos_sharpe` | 1.622 | 1.628 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/10/sharpe` | 0.982 | 0.985 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/10/vol` | 0.1065 | 0.1064 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/11/cagr` | 0.0942 | 0.0946 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/11/oos_cagr` | 0.1753 | 0.1761 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/11/oos_sharpe` | 1.558 | 1.565 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/11/sharpe` | 0.936 | 0.94 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/12/cagr` | 0.0871 | 0.0874 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/12/oos_cagr` | 0.1655 | 0.1664 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/12/oos_sharpe` | 1.463 | 1.47 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/12/sharpe` | 0.877 | 0.88 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/13/cagr` | 0.0731 | 0.0734 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/13/oos_cagr` | 0.1491 | 0.1499 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/13/oos_sharpe` | 1.375 | 1.382 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/13/sharpe` | 0.767 | 0.77 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/14/cagr` | 0.0671 | 0.0675 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/14/oos_cagr` | 0.1373 | 0.1381 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/14/oos_sharpe` | 1.331 | 1.338 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/14/sharpe` | 0.741 | 0.744 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/14/vol` | 0.0979 | 0.0978 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/15/cagr` | 0.1154 | 0.1157 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/15/oos_cagr` | 0.1474 | 0.148 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/15/oos_sharpe` | 1.409 | 1.414 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/15/sharpe` | 1.205 | 1.207 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/15/vol` | 0.0982 | 0.0981 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/16/cagr` | 0.1086 | 0.1089 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/16/oos_cagr` | 0.1337 | 0.1343 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/16/oos_sharpe` | 1.253 | 1.258 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/16/sharpe` | 1.117 | 1.12 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/17/cagr` | 0.111 | 0.1112 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/17/oos_cagr` | 0.1451 | 0.1457 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/17/oos_sharpe` | 1.378 | 1.383 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/17/sharpe` | 1.154 | 1.157 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/17/vol` | 0.0989 | 0.0988 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/18/cagr` | 0.0962 | 0.0964 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/18/oos_cagr` | 0.1209 | 0.1214 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/18/oos_sharpe` | 1.228 | 1.232 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/18/sharpe` | 1.046 | 1.048 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/18/vol` | 0.0956 | 0.0955 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/19/cagr` | 0.091 | 0.0912 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/19/oos_cagr` | 0.1162 | 0.1166 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/19/oos_sharpe` | 1.228 | 1.232 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/19/sharpe` | 1.023 | 1.025 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/2/cagr` | 0.0941 | 0.0943 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/2/oos_cagr` | 0.1772 | 0.1776 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/2/oos_sharpe` | 1.681 | 1.685 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/2/sharpe` | 0.971 | 0.973 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/3/cagr` | 0.0754 | 0.0756 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/3/oos_cagr` | 0.1353 | 0.1357 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/3/oos_sharpe` | 1.455 | 1.46 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/3/sharpe` | 0.833 | 0.835 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/4/cagr` | 0.0706 | 0.0708 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/4/oos_cagr` | 0.1277 | 0.1281 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/4/oos_sharpe` | 1.422 | 1.427 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/4/sharpe` | 0.811 | 0.813 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/5/cagr` | 0.1133 | 0.1139 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/5/oos_cagr` | 0.1942 | 0.1956 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/5/oos_sharpe` | 1.583 | 1.593 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/5/sharpe` | 1.072 | 1.077 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/6/cagr` | 0.0993 | 0.0999 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/6/oos_cagr` | 0.1654 | 0.1668 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/6/oos_sharpe` | 1.415 | 1.426 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/6/sharpe` | 0.97 | 0.975 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/7/cagr` | 0.0945 | 0.0951 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/7/oos_cagr` | 0.1651 | 0.1665 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/7/oos_sharpe` | 1.412 | 1.423 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/7/sharpe` | 0.929 | 0.935 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/8/cagr` | 0.085 | 0.0856 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/8/oos_cagr` | 0.1544 | 0.1558 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/8/oos_sharpe` | 1.411 | 1.423 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/8/sharpe` | 0.876 | 0.882 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/9/cagr` | 0.0804 | 0.081 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/9/oos_cagr` | 0.1375 | 0.1389 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/9/oos_sharpe` | 1.317 | 1.329 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/phase_rows/9/sharpe` | 0.863 | 0.869 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/recomputed/largest_sharpe_gap_vs_shipped` | 0.259 | 0.258 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/recomputed/windows/0/oos_sharpe_delta_by_phase/0` | 0.079 | 0.078 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/recomputed/windows/0/oos_sharpe_delta_by_phase/1` | 0.171 | 0.17 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/recomputed/windows/0/oos_sharpe_delta_by_phase/2` | 0.159 | 0.158 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/recomputed/windows/0/sharpe_delta_by_phase/0` | 0.072 | 0.071 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/recomputed/windows/0/sharpe_delta_by_phase/1` | 0.143 | 0.142 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/recomputed/windows/0/sharpe_delta_by_phase/3` | 0.051 | 0.05 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/recomputed/windows/0/sharpe_delta_max` | 0.143 | 0.142 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/recomputed/windows/0/sharpe_delta_min` | 0.051 | 0.05 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/recomputed/windows/1/oos_sharpe_delta_by_phase/0` | 0.05 | 0.049 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/recomputed/windows/1/sharpe_delta_by_phase/0` | 0.064 | 0.063 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/recomputed/windows/1/sharpe_delta_by_phase/1` | 0.041 | 0.04 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/recomputed/windows/1/sharpe_delta_by_phase/2` | 0.059 | 0.06 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/recomputed/windows/1/sharpe_delta_max` | 0.064 | 0.063 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/recomputed/windows/2/oos_sharpe_delta_by_phase/0` | -0.226 | -0.225 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/recomputed/windows/2/oos_sharpe_delta_by_phase/1` | -0.001 | 0.0 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/recomputed/windows/2/oos_sharpe_delta_by_phase/3` | -0.15 | -0.151 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/recomputed/windows/2/sharpe_delta_by_phase/3` | -0.108 | -0.109 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/recomputed/windows/3/oos_sharpe_delta_by_phase/0` | -0.259 | -0.258 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/recomputed/windows/3/oos_sharpe_delta_by_phase/1` | -0.095 | -0.094 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/recomputed/windows/3/oos_sharpe_delta_by_phase/3` | -0.15 | -0.151 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/recomputed/windows/3/sharpe_delta_by_phase/3` | -0.131 | -0.132 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/verdict/largest_sharpe_gap_vs_shipped` | 0.259 | 0.258 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/verdict/windows/0/oos_sharpe_delta_by_phase/0` | 0.079 | 0.078 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/verdict/windows/0/oos_sharpe_delta_by_phase/1` | 0.171 | 0.17 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/verdict/windows/0/oos_sharpe_delta_by_phase/2` | 0.159 | 0.158 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/verdict/windows/0/sharpe_delta_by_phase/0` | 0.072 | 0.071 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/verdict/windows/0/sharpe_delta_by_phase/1` | 0.143 | 0.142 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/verdict/windows/0/sharpe_delta_by_phase/3` | 0.051 | 0.05 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/verdict/windows/0/sharpe_delta_max` | 0.143 | 0.142 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/verdict/windows/0/sharpe_delta_min` | 0.051 | 0.05 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/verdict/windows/1/oos_sharpe_delta_by_phase/0` | 0.05 | 0.049 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/verdict/windows/1/sharpe_delta_by_phase/0` | 0.064 | 0.063 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/verdict/windows/1/sharpe_delta_by_phase/1` | 0.041 | 0.04 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/verdict/windows/1/sharpe_delta_by_phase/2` | 0.059 | 0.06 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/verdict/windows/1/sharpe_delta_max` | 0.064 | 0.063 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/verdict/windows/2/oos_sharpe_delta_by_phase/0` | -0.226 | -0.225 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/verdict/windows/2/oos_sharpe_delta_by_phase/1` | -0.001 | 0.0 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/verdict/windows/2/oos_sharpe_delta_by_phase/3` | -0.15 | -0.151 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/verdict/windows/2/sharpe_delta_by_phase/3` | -0.108 | -0.109 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/verdict/windows/3/oos_sharpe_delta_by_phase/0` | -0.259 | -0.258 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/verdict/windows/3/oos_sharpe_delta_by_phase/1` | -0.095 | -0.094 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/verdict/windows/3/oos_sharpe_delta_by_phase/3` | -0.15 | -0.151 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window/verdict/windows/3/sharpe_delta_by_phase/3` | -0.131 | -0.132 | SECTION_ADVANCED | 这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/edge/best_mean_sharpe` | 1.105 | 1.1078 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/edge/curve/0/max_sharpe` | 1.173 | 1.175 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/edge/curve/0/mean_sharpe` | 1.105 | 1.1078 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/edge/curve/0/min_sharpe` | 1.029 | 1.032 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/edge/curve/1/max_sharpe` | 1.184 | 1.186 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/edge/curve/1/mean_sharpe` | 1.1025 | 1.1053 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/edge/curve/1/min_sharpe` | 1.021 | 1.024 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/edge/curve/2/max_sharpe` | 1.205 | 1.207 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/edge/curve/2/mean_sharpe` | 1.0755 | 1.0782 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/edge/curve/2/min_sharpe` | 0.982 | 0.985 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/edge/curve/3/max_sharpe` | 1.154 | 1.157 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/edge/curve/3/mean_sharpe` | 0.9828 | 0.9862 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/edge/curve/3/min_sharpe` | 0.877 | 0.88 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/edge/gain_of_best_over_shipped` | 0.1222 | 0.1216 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/edge/shipped/max_sharpe` | 1.154 | 1.157 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/edge/shipped/mean_sharpe` | 0.9828 | 0.9862 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/edge/shipped/min_sharpe` | 0.877 | 0.88 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/paired/rows/0/bars` | 1663 | 1664 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/paired/rows/0/ci_p05_p95_pp/0` | 0.371 | 0.347 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/paired/rows/0/ci_p05_p95_pp/1` | 3.111 | 3.008 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/paired/rows/0/mean_pp` | 1.61 | 1.602 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/paired/rows/0/share_positive` | 0.981 | 0.983 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/paired/rows/1/bars` | 1658 | 1659 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/paired/rows/1/ci_p05_p95_pp/0` | 1.092 | 1.085 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/paired/rows/1/ci_p05_p95_pp/1` | 4.197 | 4.182 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/paired/rows/1/mean_pp` | 2.593 | 2.592 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/paired/rows/2/bars` | 1653 | 1654 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/paired/rows/2/ci_p05_p95_pp/0` | 0.01 | -0.007 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/paired/rows/2/ci_p05_p95_pp/1` | 2.732 | 2.76 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/paired/rows/2/mean_pp` | 1.348 | 1.34 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/paired/rows/2/share_positive` | 0.95 | 0.948 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/paired/rows/3/bars` | 1648 | 1649 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/paired/rows/3/ci_p05_p95_pp/0` | -0.67 | -0.708 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/paired/rows/3/ci_p05_p95_pp/1` | 1.75 | 1.742 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/paired/rows/3/mean_pp` | 0.501 | 0.497 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/paired/rows/3/share_positive` | 0.764 | 0.749 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/paired/verdict/min_ci_low_pp` | -0.67 | -0.708 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/paired/verdict/min_share_positive` | 0.764 | 0.749 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/panel/bars_named` | 5282 | 5283 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/0/cagr` | 0.1401 | 0.1403 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/0/oos_cagr` | 0.2348 | 0.2352 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/0/oos_sharpe` | 1.56 | 1.563 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/0/sharpe` | 0.969 | 0.97 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/0/vol` | 0.1531 | 0.153 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/1/cagr` | 0.1401 | 0.1403 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/1/oos_cagr` | 0.2348 | 0.2352 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/1/oos_sharpe` | 1.56 | 1.563 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/1/sharpe` | 0.969 | 0.97 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/1/vol` | 0.1531 | 0.153 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/10/cagr` | 0.1218 | 0.1224 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/10/oos_cagr` | 0.2041 | 0.2055 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/10/oos_sharpe` | 1.653 | 1.663 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/10/sharpe` | 1.146 | 1.151 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/11/cagr` | 0.1186 | 0.1192 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/11/oos_cagr` | 0.2017 | 0.2031 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/11/oos_sharpe` | 1.636 | 1.646 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/11/sharpe` | 1.113 | 1.118 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/12/cagr` | 0.1133 | 0.1139 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/12/oos_cagr` | 0.1942 | 0.1956 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/12/oos_sharpe` | 1.583 | 1.593 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/12/sharpe` | 1.072 | 1.077 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/13/cagr` | 0.0945 | 0.0951 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/13/oos_cagr` | 0.1651 | 0.1665 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/13/oos_sharpe` | 1.412 | 1.423 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/13/sharpe` | 0.929 | 0.935 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/14/cagr` | 0.1354 | 0.1358 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/14/oos_cagr` | 0.2185 | 0.2193 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/14/oos_sharpe` | 1.196 | 1.2 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/14/sharpe` | 0.871 | 0.873 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/15/cagr` | 0.1354 | 0.1358 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/15/oos_cagr` | 0.2185 | 0.2193 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/15/oos_sharpe` | 1.196 | 1.2 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/15/sharpe` | 0.871 | 0.873 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/16/cagr` | 0.1354 | 0.1358 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/16/oos_cagr` | 0.2185 | 0.2193 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/16/oos_sharpe` | 1.196 | 1.2 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/16/sharpe` | 0.871 | 0.873 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/17/cagr` | 0.1015 | 0.1018 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/17/oos_cagr` | 0.1915 | 0.1922 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/17/oos_sharpe` | 1.73 | 1.736 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/17/sharpe` | 1.029 | 1.032 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/17/vol` | 0.1031 | 0.103 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/18/cagr` | 0.1033 | 0.1036 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/18/oos_cagr` | 0.1919 | 0.1925 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/18/oos_sharpe` | 1.668 | 1.674 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/18/sharpe` | 1.021 | 1.024 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/19/cagr` | 0.0995 | 0.0999 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/19/oos_cagr` | 0.1863 | 0.187 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/19/oos_sharpe` | 1.622 | 1.628 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/19/sharpe` | 0.982 | 0.985 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/19/vol` | 0.1065 | 0.1064 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/2/cagr` | 0.1401 | 0.1403 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/2/oos_cagr` | 0.2348 | 0.2352 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/2/oos_sharpe` | 1.56 | 1.563 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/2/sharpe` | 0.969 | 0.97 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/2/vol` | 0.1531 | 0.153 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/20/cagr` | 0.0871 | 0.0874 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/20/oos_cagr` | 0.1655 | 0.1664 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/20/oos_sharpe` | 1.463 | 1.47 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/20/sharpe` | 0.877 | 0.88 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/21/cagr` | 0.1593 | 0.1596 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/21/oos_cagr` | 0.1919 | 0.1926 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/21/oos_sharpe` | 1.29 | 1.294 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/21/sharpe` | 1.13 | 1.132 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/21/vol` | 0.1452 | 0.1451 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/22/cagr` | 0.1593 | 0.1596 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/22/oos_cagr` | 0.1919 | 0.1926 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/22/oos_sharpe` | 1.29 | 1.294 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/22/sharpe` | 1.13 | 1.132 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/22/vol` | 0.1452 | 0.1451 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/23/cagr` | 0.1593 | 0.1596 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/23/oos_cagr` | 0.1919 | 0.1926 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/23/oos_sharpe` | 1.29 | 1.294 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/23/sharpe` | 1.13 | 1.132 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/23/vol` | 0.1452 | 0.1451 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/24/cagr` | 0.1161 | 0.1163 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/24/oos_cagr` | 0.1519 | 0.1523 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/24/oos_sharpe` | 1.368 | 1.372 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/24/sharpe` | 1.173 | 1.175 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/25/cagr` | 0.1139 | 0.1141 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/25/oos_cagr` | 0.1458 | 0.1463 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/25/oos_sharpe` | 1.374 | 1.379 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/25/sharpe` | 1.184 | 1.186 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/26/cagr` | 0.1154 | 0.1157 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/26/oos_cagr` | 0.1474 | 0.148 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/26/oos_sharpe` | 1.409 | 1.414 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/26/sharpe` | 1.205 | 1.207 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/26/vol` | 0.0982 | 0.0981 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/27/cagr` | 0.111 | 0.1112 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/27/oos_cagr` | 0.1451 | 0.1457 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/27/oos_sharpe` | 1.378 | 1.383 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/27/sharpe` | 1.154 | 1.157 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/27/vol` | 0.0989 | 0.0988 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/3/cagr` | 0.1106 | 0.1107 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/3/oos_cagr` | 0.1971 | 0.1974 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/3/oos_sharpe` | 1.762 | 1.764 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/3/sharpe` | 1.072 | 1.073 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/3/vol` | 0.1073 | 0.1072 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/4/cagr` | 0.1116 | 0.1117 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/4/oos_cagr` | 0.2045 | 0.2048 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/4/oos_sharpe` | 1.824 | 1.826 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/4/sharpe` | 1.092 | 1.093 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/5/cagr` | 0.1032 | 0.1033 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/5/oos_cagr` | 0.19 | 0.1902 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/5/oos_sharpe` | 1.76 | 1.763 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/5/sharpe` | 1.043 | 1.044 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/6/cagr` | 0.0941 | 0.0943 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/6/oos_cagr` | 0.1772 | 0.1776 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/6/oos_sharpe` | 1.681 | 1.685 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/6/sharpe` | 0.971 | 0.973 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/7/cagr` | 0.1391 | 0.1396 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/7/oos_cagr` | 0.2038 | 0.2052 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/7/oos_sharpe` | 1.181 | 1.188 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/7/sharpe` | 0.905 | 0.908 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/8/cagr` | 0.1391 | 0.1396 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/8/oos_cagr` | 0.2038 | 0.2052 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/8/oos_sharpe` | 1.181 | 1.188 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/8/sharpe` | 0.905 | 0.908 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/9/cagr` | 0.1391 | 0.1396 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/9/oos_cagr` | 0.2038 | 0.2052 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/9/oos_sharpe` | 1.181 | 1.188 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/phase_rows/9/sharpe` | 0.905 | 0.908 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_edge/best_mean_sharpe` | 1.105 | 1.1078 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_edge/curve/0/max_sharpe` | 1.173 | 1.175 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_edge/curve/0/mean_sharpe` | 1.105 | 1.1078 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_edge/curve/0/min_sharpe` | 1.029 | 1.032 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_edge/curve/1/max_sharpe` | 1.184 | 1.186 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_edge/curve/1/mean_sharpe` | 1.1025 | 1.1053 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_edge/curve/1/min_sharpe` | 1.021 | 1.024 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_edge/curve/2/max_sharpe` | 1.205 | 1.207 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_edge/curve/2/mean_sharpe` | 1.0755 | 1.0782 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_edge/curve/2/min_sharpe` | 0.982 | 0.985 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_edge/curve/3/max_sharpe` | 1.154 | 1.157 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_edge/curve/3/mean_sharpe` | 0.9828 | 0.9862 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_edge/curve/3/min_sharpe` | 0.877 | 0.88 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_edge/gain_of_best_over_shipped` | 0.1222 | 0.1216 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_edge/shipped/max_sharpe` | 1.154 | 1.157 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_edge/shipped/mean_sharpe` | 0.9828 | 0.9862 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_edge/shipped/min_sharpe` | 0.877 | 0.88 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/largest_sharpe_gap_vs_shipped` | 0.267 | 0.27 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/0/oos_sharpe_delta_by_phase/0` | -0.121 | -0.122 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/0/oos_sharpe_delta_by_phase/1` | -0.231 | -0.235 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/0/oos_sharpe_delta_by_phase/2` | -0.267 | -0.27 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/0/oos_sharpe_delta_by_phase/3` | -0.088 | -0.089 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/0/sharpe_delta_by_phase/0` | -0.002 | -0.003 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/0/sharpe_delta_by_phase/1` | -0.024 | -0.027 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/0/sharpe_delta_by_phase/2` | -0.006 | -0.007 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/0/sharpe_delta_by_phase/3` | -0.024 | -0.025 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/0/sharpe_delta_max` | -0.002 | -0.003 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/0/sharpe_delta_min` | -0.024 | -0.027 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/1/oos_sharpe_delta_by_phase/0` | -0.121 | -0.122 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/1/oos_sharpe_delta_by_phase/1` | -0.231 | -0.235 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/1/oos_sharpe_delta_by_phase/2` | -0.267 | -0.27 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/1/oos_sharpe_delta_by_phase/3` | -0.088 | -0.089 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/1/sharpe_delta_by_phase/0` | -0.002 | -0.003 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/1/sharpe_delta_by_phase/1` | -0.024 | -0.027 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/1/sharpe_delta_by_phase/2` | -0.006 | -0.007 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/1/sharpe_delta_by_phase/3` | -0.024 | -0.025 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/1/sharpe_delta_max` | -0.002 | -0.003 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/1/sharpe_delta_min` | -0.024 | -0.027 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/2/oos_sharpe_delta_by_phase/0` | -0.121 | -0.122 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/2/oos_sharpe_delta_by_phase/1` | -0.231 | -0.235 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/2/oos_sharpe_delta_by_phase/2` | -0.267 | -0.27 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/2/oos_sharpe_delta_by_phase/3` | -0.088 | -0.089 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/2/sharpe_delta_by_phase/0` | -0.002 | -0.003 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/2/sharpe_delta_by_phase/1` | -0.024 | -0.027 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/2/sharpe_delta_by_phase/2` | -0.006 | -0.007 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/2/sharpe_delta_by_phase/3` | -0.024 | -0.025 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/2/sharpe_delta_max` | -0.002 | -0.003 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/2/sharpe_delta_min` | -0.024 | -0.027 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/3/oos_sharpe_delta_by_phase/0` | 0.081 | 0.079 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/3/oos_sharpe_delta_by_phase/1` | 0.241 | 0.24 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/3/oos_sharpe_delta_by_phase/2` | 0.267 | 0.266 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/3/oos_sharpe_delta_by_phase/3` | -0.01 | -0.011 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/3/sharpe_delta_by_phase/0` | 0.101 | 0.1 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/3/sharpe_delta_by_phase/1` | 0.217 | 0.216 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/3/sharpe_delta_by_phase/3` | 0.019 | 0.018 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/3/sharpe_delta_max` | 0.217 | 0.216 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/3/sharpe_delta_min` | 0.019 | 0.018 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/4/oos_sharpe_delta_by_phase/0` | 0.143 | 0.141 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/4/oos_sharpe_delta_by_phase/1` | 0.224 | 0.223 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/4/oos_sharpe_delta_by_phase/2` | 0.205 | 0.204 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/4/sharpe_delta_by_phase/0` | 0.121 | 0.12 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/4/sharpe_delta_by_phase/1` | 0.184 | 0.183 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/4/sharpe_delta_by_phase/3` | 0.03 | 0.029 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/4/sharpe_delta_max` | 0.184 | 0.183 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/4/sharpe_delta_min` | 0.03 | 0.029 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/5/oos_sharpe_delta_by_phase/0` | 0.079 | 0.078 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/5/oos_sharpe_delta_by_phase/1` | 0.171 | 0.17 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/5/oos_sharpe_delta_by_phase/2` | 0.159 | 0.158 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/5/sharpe_delta_by_phase/0` | 0.072 | 0.071 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/5/sharpe_delta_by_phase/1` | 0.143 | 0.142 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/5/sharpe_delta_by_phase/3` | 0.051 | 0.05 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/5/sharpe_delta_max` | 0.143 | 0.142 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/recomputed_verdict/windows/5/sharpe_delta_min` | 0.051 | 0.05 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/largest_sharpe_gap_vs_shipped` | 0.267 | 0.27 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/0/oos_sharpe_delta_by_phase/0` | -0.121 | -0.122 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/0/oos_sharpe_delta_by_phase/1` | -0.231 | -0.235 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/0/oos_sharpe_delta_by_phase/2` | -0.267 | -0.27 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/0/oos_sharpe_delta_by_phase/3` | -0.088 | -0.089 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/0/sharpe_delta_by_phase/0` | -0.002 | -0.003 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/0/sharpe_delta_by_phase/1` | -0.024 | -0.027 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/0/sharpe_delta_by_phase/2` | -0.006 | -0.007 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/0/sharpe_delta_by_phase/3` | -0.024 | -0.025 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/0/sharpe_delta_max` | -0.002 | -0.003 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/0/sharpe_delta_min` | -0.024 | -0.027 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/1/oos_sharpe_delta_by_phase/0` | -0.121 | -0.122 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/1/oos_sharpe_delta_by_phase/1` | -0.231 | -0.235 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/1/oos_sharpe_delta_by_phase/2` | -0.267 | -0.27 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/1/oos_sharpe_delta_by_phase/3` | -0.088 | -0.089 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/1/sharpe_delta_by_phase/0` | -0.002 | -0.003 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/1/sharpe_delta_by_phase/1` | -0.024 | -0.027 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/1/sharpe_delta_by_phase/2` | -0.006 | -0.007 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/1/sharpe_delta_by_phase/3` | -0.024 | -0.025 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/1/sharpe_delta_max` | -0.002 | -0.003 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/1/sharpe_delta_min` | -0.024 | -0.027 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/2/oos_sharpe_delta_by_phase/0` | -0.121 | -0.122 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/2/oos_sharpe_delta_by_phase/1` | -0.231 | -0.235 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/2/oos_sharpe_delta_by_phase/2` | -0.267 | -0.27 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/2/oos_sharpe_delta_by_phase/3` | -0.088 | -0.089 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/2/sharpe_delta_by_phase/0` | -0.002 | -0.003 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/2/sharpe_delta_by_phase/1` | -0.024 | -0.027 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/2/sharpe_delta_by_phase/2` | -0.006 | -0.007 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/2/sharpe_delta_by_phase/3` | -0.024 | -0.025 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/2/sharpe_delta_max` | -0.002 | -0.003 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/2/sharpe_delta_min` | -0.024 | -0.027 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/3/oos_sharpe_delta_by_phase/0` | 0.081 | 0.079 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/3/oos_sharpe_delta_by_phase/1` | 0.241 | 0.24 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/3/oos_sharpe_delta_by_phase/2` | 0.267 | 0.266 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/3/oos_sharpe_delta_by_phase/3` | -0.01 | -0.011 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/3/sharpe_delta_by_phase/0` | 0.101 | 0.1 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/3/sharpe_delta_by_phase/1` | 0.217 | 0.216 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/3/sharpe_delta_by_phase/3` | 0.019 | 0.018 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/3/sharpe_delta_max` | 0.217 | 0.216 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/3/sharpe_delta_min` | 0.019 | 0.018 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/4/oos_sharpe_delta_by_phase/0` | 0.143 | 0.141 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/4/oos_sharpe_delta_by_phase/1` | 0.224 | 0.223 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/4/oos_sharpe_delta_by_phase/2` | 0.205 | 0.204 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/4/sharpe_delta_by_phase/0` | 0.121 | 0.12 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/4/sharpe_delta_by_phase/1` | 0.184 | 0.183 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/4/sharpe_delta_by_phase/3` | 0.03 | 0.029 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/4/sharpe_delta_max` | 0.184 | 0.183 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/4/sharpe_delta_min` | 0.03 | 0.029 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/5/oos_sharpe_delta_by_phase/0` | 0.079 | 0.078 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/5/oos_sharpe_delta_by_phase/1` | 0.171 | 0.17 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/5/oos_sharpe_delta_by_phase/2` | 0.159 | 0.158 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/5/sharpe_delta_by_phase/0` | 0.072 | 0.071 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/5/sharpe_delta_by_phase/1` | 0.143 | 0.142 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/5/sharpe_delta_by_phase/3` | 0.051 | 0.05 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/5/sharpe_delta_max` | 0.143 | 0.142 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/vol_window_edge/verdict/windows/5/sharpe_delta_min` | 0.051 | 0.05 | SECTION_ADVANCED | 这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/window_label/identity/the full-window cell's own window reproduces the ticket/delta_pp` | 0.0 | 0.06 | SECTION_ADVANCED | 这一节自己换了代：`window_label` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/window_label/identity/the full-window cell's own window reproduces the ticket/measured_pp` | 12.45 | 12.39 | SECTION_ADVANCED | 这一节自己换了代：`window_label` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/window_label/rows/printed_under_full_header/sharpe` | 1.687 | 1.688 | SECTION_ADVANCED | 这一节自己换了代：`window_label` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/window_label/rows/same_book_full_window/bars` | 1537 | 1538 | SECTION_ADVANCED | 这一节自己换了代：`window_label` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/window_label/rows/same_book_full_window/cagr_pp` | 7.6 | 7.58 | SECTION_ADVANCED | 这一节自己换了代：`window_label` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/window_label/rows/same_book_full_window/sharpe` | 1.324 | 1.32 | SECTION_ADVANCED | 这一节自己换了代：`window_label` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/window_label/table_row/full/cagr_pct` | 7.6 | 7.58 | SECTION_ADVANCED | 这一节自己换了代：`window_label` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/window_label/table_row/full/sharpe` | 1.324 | 1.32 | SECTION_ADVANCED | 这一节自己换了代：`window_label` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/window_label/table_row/full_window_bars` | 1537 | 1538 | SECTION_ADVANCED | 这一节自己换了代：`window_label` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/window_label/table_row/oos/sharpe` | 1.687 | 1.688 | SECTION_ADVANCED | 这一节自己换了代：`window_label` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |
| `/window_label/verdict/gap_pp` | 4.85 | 4.87 | SECTION_ADVANCED | 这一节自己换了代：`window_label` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json |

## 今天新出现的数（395 个）落在这几块上

- `/alias_stability/crosscheck`
- `/alias_stability/families`
- `/alias_stability/stability`
- `/capacity_edge/criteria`
- `/capacity_edge/summary`
- `/capacity_ticket/one_lot_floor_cny`
- `/capacity_ticket/rungs`
- `/capacity_ticket/shortfall_to_typical_cny`
- `/derisk/instrument`
- `/derisk/n_phases`
- `/supply_capacity/ceiling_cny`
- `/supply_capacity/floor_cny`
- `/supply_capacity/gap_cny`
- `/supply_capacity/share_of_floor`
- `/width_fit/gate_reads`
- `/width_fit/gate_vs_ticket`
- `/width_fit/line_pct`
- `/width_fit/min_width`
- `/width_fit/rows`
- `/width_fit/ticket_agreement`

## 钱的两处（同一根 bar 上改了定价口径）

- `/admission/capacity_cny`：**18582410.0 → 15993296.0**（差 -2589114.0）｜SECTION_ADVANCED｜这一节自己换了代：`admission` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/admission/concentration_caliber/gap_pp`：**3.13 → 3.14**（差 0.01）｜SECTION_ADVANCED｜这一节自己换了代：`admission` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/admission/concentration_caliber/lag0_pct`：**71.04 → 71.05**（差 0.01）｜SECTION_ADVANCED｜这一节自己换了代：`admission` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/admission/concentration_caliber/lag1_cagr_pct`：**10.38 → 10.37**（差 -0.01）｜SECTION_ADVANCED｜这一节自己换了代：`admission` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/admission/concentration_caliber/lag1_pct`：**74.17 → 74.19**（差 0.02）｜SECTION_ADVANCED｜这一节自己换了代：`admission` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/admission/margin_to_line`：**-0.0104 → -0.0105**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`admission` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/admission/prior/top2_share`：**0.7084 → 0.7104**（差 0.002）｜SECTION_ADVANCED｜这一节自己换了代：`admission` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/admission/reads/capacity_by_capital/10M/impact_pct_of_adv`：**10.0865 → 10.028**（差 -0.0585）｜SECTION_ADVANCED｜这一节自己换了代：`admission` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/admission/reads/capacity_by_capital/1M/impact_pct_of_adv`：**1.0087 → 1.0028**（差 -0.0059）｜SECTION_ADVANCED｜这一节自己换了代：`admission` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/admission/reads/oos_sharpe`：**1.8016 → 1.7997**（差 -0.0019）｜SECTION_ADVANCED｜这一节自己换了代：`admission` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/admission/top2_share`：**0.7104 → 0.7105**（差 0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`admission` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/admission/worst`：**1.9416 → 1.9241**（差 -0.0175）｜SECTION_ADVANCED｜这一节自己换了代：`admission` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/backtest_band/5 名·可执行单口径（本单这份账）/full/cagr_pct`：**7.6 → 7.58**（差 -0.02）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/band_ruler/cells/book/card/causal/full/bars`：**1665 → 1666**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/card/causal/full/cagr`：**0.1542 → 0.1537**（差 -0.0005）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/card/causal/full/cagr_pp`：**15.42 → 15.37**（差 -0.05）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/card/causal/full/sharpe`：**0.984 → 0.981**（差 -0.003）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/card/causal/full/vol`：**0.1659 → 0.1658**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/card/causal/full/years`：**6.87 → 6.88**（差 0.01）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/card/causal/oos/bars`：**695 → 696**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/card/causal/oos/cagr`：**0.2473 → 0.246**（差 -0.0013）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/card/causal/oos/cagr_pp`：**24.73 → 24.6**（差 -0.13）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/card/causal/oos/sharpe`：**1.51 → 1.504**（差 -0.006）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/card/causal/oos/vol`：**0.1614 → 0.1613**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/card/causal/oos/years`：**2.87 → 2.88**（差 0.01）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/card/causal/ticket_window/bars`：**695 → 696**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/card/causal/ticket_window/cagr`：**0.2473 → 0.246**（差 -0.0013）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/card/causal/ticket_window/cagr_pp`：**24.73 → 24.6**（差 -0.13）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/card/causal/ticket_window/sharpe`：**1.51 → 1.504**（差 -0.006）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/card/causal/ticket_window/vol`：**0.1614 → 0.1613**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/card/causal/ticket_window/years`：**2.87 → 2.88**（差 0.01）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/card/published/full/bars`：**1664 → 1665**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/card/published/full/cagr`：**0.1593 → 0.1592**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/card/published/full/cagr_pp`：**15.93 → 15.92**（差 -0.01）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/card/published/full/sharpe`：**1.023 → 1.022**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/card/published/oos/bars`：**695 → 696**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/card/published/oos/cagr`：**0.2379 → 0.2375**（差 -0.0004）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/card/published/oos/cagr_pp`：**23.79 → 23.75**（差 -0.04）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/card/published/oos/sharpe`：**1.498 → 1.496**（差 -0.002）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/card/published/oos/vol`：**0.157 → 0.1569**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/card/published/oos/years`：**2.87 → 2.88**（差 0.01）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/card/published/ticket_window/bars`：**695 → 696**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/card/published/ticket_window/cagr`：**0.2379 → 0.2375**（差 -0.0004）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/card/published/ticket_window/cagr_pp`：**23.79 → 23.75**（差 -0.04）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/card/published/ticket_window/sharpe`：**1.498 → 1.496**（差 -0.002）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/card/published/ticket_window/vol`：**0.157 → 0.1569**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/card/published/ticket_window/years`：**2.87 → 2.88**（差 0.01）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/ticket/causal/full/bars`：**1665 → 1666**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/ticket/causal/full/cagr`：**0.1657 → 0.1652**（差 -0.0005）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/ticket/causal/full/cagr_pp`：**16.57 → 16.52**（差 -0.05）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/ticket/causal/full/sharpe`：**1.014 → 1.011**（差 -0.003）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/ticket/causal/full/years`：**6.87 → 6.88**（差 0.01）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/ticket/causal/oos/bars`：**695 → 696**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/ticket/causal/oos/cagr`：**0.263 → 0.2617**（差 -0.0013）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/ticket/causal/oos/cagr_pp`：**26.3 → 26.17**（差 -0.13）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/ticket/causal/oos/sharpe`：**1.556 → 1.55**（差 -0.006）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/ticket/causal/oos/vol`：**0.1655 → 0.1654**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/ticket/causal/oos/years`：**2.87 → 2.88**（差 0.01）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/ticket/causal/ticket_window/bars`：**695 → 696**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/ticket/causal/ticket_window/cagr`：**0.263 → 0.2617**（差 -0.0013）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/ticket/causal/ticket_window/cagr_pp`：**26.3 → 26.17**（差 -0.13）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/ticket/causal/ticket_window/sharpe`：**1.556 → 1.55**（差 -0.006）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/ticket/causal/ticket_window/vol`：**0.1655 → 0.1654**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/ticket/causal/ticket_window/years`：**2.87 → 2.88**（差 0.01）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/ticket/published/full/bars`：**1664 → 1665**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/ticket/published/full/cagr`：**0.1747 → 0.1746**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/ticket/published/full/cagr_pp`：**17.47 → 17.46**（差 -0.01）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/ticket/published/oos/bars`：**695 → 696**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/ticket/published/oos/cagr`：**0.2581 → 0.2578**（差 -0.0003）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/ticket/published/oos/cagr_pp`：**25.81 → 25.78**（差 -0.03）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/ticket/published/oos/sharpe`：**1.563 → 1.562**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/ticket/published/oos/vol`：**0.1617 → 0.1616**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/ticket/published/oos/years`：**2.87 → 2.88**（差 0.01）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/ticket/published/ticket_window/bars`：**695 → 696**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/ticket/published/ticket_window/cagr`：**0.2581 → 0.2578**（差 -0.0003）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/ticket/published/ticket_window/cagr_pp`：**25.81 → 25.78**（差 -0.03）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/ticket/published/ticket_window/sharpe`：**1.563 → 1.562**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/ticket/published/ticket_window/vol`：**0.1617 → 0.1616**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/book/ticket/published/ticket_window/years`：**2.87 → 2.88**（差 0.01）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/card/12/vol08/full/bars`：**1664 → 1665**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/card/12/vol08/full/cagr`：**0.0941 → 0.0943**（差 0.0002）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/card/12/vol08/full/cagr_pp`：**9.41 → 9.43**（差 0.02）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/card/12/vol08/full/sharpe`：**0.971 → 0.973**（差 0.002）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/card/12/vol08/oos/bars`：**695 → 696**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/card/12/vol08/oos/cagr`：**0.1772 → 0.1776**（差 0.0004）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/card/12/vol08/oos/cagr_pp`：**17.72 → 17.76**（差 0.04）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/card/12/vol08/oos/sharpe`：**1.681 → 1.685**（差 0.004）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/card/12/vol08/oos/vol`：**0.1046 → 0.1045**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/card/12/vol08/oos/years`：**2.87 → 2.88**（差 0.01）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/card/12/vol08/ticket_window/bars`：**695 → 696**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/card/12/vol08/ticket_window/cagr`：**0.1772 → 0.1776**（差 0.0004）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/card/12/vol08/ticket_window/cagr_pp`：**17.72 → 17.76**（差 0.04）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/card/12/vol08/ticket_window/sharpe`：**1.681 → 1.685**（差 0.004）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/card/12/vol08/ticket_window/vol`：**0.1046 → 0.1045**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/card/12/vol08/ticket_window/years`：**2.87 → 2.88**（差 0.01）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/card/cost10/full/bars`：**1537 → 1538**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/card/cost10/full/cagr`：**0.0702 → 0.07**（差 -0.0002）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/card/cost10/full/cagr_pp`：**7.02 → 7.0**（差 -0.02）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/card/cost10/full/sharpe`：**1.269 → 1.266**（差 -0.003）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/card/cost10/oos/bars`：**695 → 696**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/card/cost10/oos/cagr`：**0.1178 → 0.1173**（差 -0.0005）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/card/cost10/oos/cagr_pp`：**11.78 → 11.73**（差 -0.05）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/card/cost10/oos/sharpe`：**1.631 → 1.625**（差 -0.006）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/card/cost10/oos/years`：**2.87 → 2.88**（差 0.01）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/card/cost10/ticket_window/bars`：**695 → 696**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/card/cost10/ticket_window/cagr`：**0.1178 → 0.1173**（差 -0.0005）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/card/cost10/ticket_window/cagr_pp`：**11.78 → 11.73**（差 -0.05）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/card/cost10/ticket_window/sharpe`：**1.631 → 1.625**（差 -0.006）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/card/cost10/ticket_window/years`：**2.87 → 2.88**（差 0.01）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/card/full/bars`：**1537 → 1538**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/card/full/cagr`：**0.0717 → 0.0715**（差 -0.0002）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/card/full/cagr_pp`：**7.17 → 7.15**（差 -0.02）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/card/full/sharpe`：**1.295 → 1.291**（差 -0.004）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/card/full/vol`：**0.0569 → 0.0568**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/card/oos/bars`：**695 → 696**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/card/oos/cagr`：**0.1199 → 0.1193**（差 -0.0006）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/card/oos/cagr_pp`：**11.99 → 11.93**（差 -0.06）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/card/oos/sharpe`：**1.657 → 1.65**（差 -0.007）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/card/oos/vol`：**0.073 → 0.0729**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/card/oos/years`：**2.87 → 2.88**（差 0.01）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/card/ticket_window/bars`：**695 → 696**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/card/ticket_window/cagr`：**0.1199 → 0.1193**（差 -0.0006）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/card/ticket_window/cagr_pp`：**11.99 → 11.93**（差 -0.06）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/card/ticket_window/sharpe`：**1.657 → 1.65**（差 -0.007）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/card/ticket_window/vol`：**0.073 → 0.0729**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/card/ticket_window/years`：**2.87 → 2.88**（差 0.01）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/ticket/full/bars`：**1537 → 1538**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/ticket/full/cagr`：**0.076 → 0.0758**（差 -0.0002）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/ticket/full/cagr_pp`：**7.6 → 7.58**（差 -0.02）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/ticket/full/sharpe`：**1.324 → 1.32**（差 -0.004）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/ticket/oos/bars`：**695 → 696**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/ticket/oos/cagr`：**0.1245 → 0.1239**（差 -0.0006）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/ticket/oos/cagr_pp`：**12.45 → 12.39**（差 -0.06）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/ticket/oos/sharpe`：**1.697 → 1.691**（差 -0.006）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/ticket/oos/vol`：**0.0738 → 0.0737**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/ticket/oos/years`：**2.87 → 2.88**（差 0.01）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/ticket/ticket_window/bars`：**695 → 696**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/ticket/ticket_window/cagr`：**0.1245 → 0.1239**（差 -0.0006）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/ticket/ticket_window/cagr_pp`：**12.45 → 12.39**（差 -0.06）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/ticket/ticket_window/sharpe`：**1.697 → 1.691**（差 -0.006）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/ticket/ticket_window/vol`：**0.0738 → 0.0737**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/cells/held/causal/ticket/ticket_window/years`：**2.87 → 2.88**（差 0.01）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/dial_prices/ordering/price_pp`：**-0.51 → -0.55**（差 -0.04）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/dial_prices/window/price_pp`：**4.82 → 4.78**（差 -0.04）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/identity/card 18.35% (2024+) reproduced on its own ruler/measured_pp`：**17.97 → 17.72**（差 -0.25）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/identity/card 18.35% (2024+) reproduced on its own ruler/published_pp`：**17.97 → 17.72**（差 -0.25）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/identity/card 9.60% reproduced on its own ruler/measured_pp`：**9.51 → 9.41**（差 -0.1）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/identity/card 9.60% reproduced on its own ruler/published_pp`：**9.51 → 9.41**（差 -0.1）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/identity/ticket 12.78% reproduced on its own ruler/measured_pp`：**12.54 → 12.45**（差 -0.09）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/identity/ticket 12.78% reproduced on its own ruler/published_pp`：**12.54 → 12.45**（差 -0.09）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/published_faces/card_full`：**9.51 → 9.41**（差 -0.1）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/published_faces/card_oos`：**17.97 → 17.72**（差 -0.25）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/published_faces/rows/0/full`：**7.64 → 7.6**（差 -0.04）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/published_faces/rows/0/oos`：**12.54 → 12.45**（差 -0.09）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/published_faces/rows/1/full`：**15.55 → 15.5**（差 -0.05）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/published_faces/rows/1/oos`：**23.42 → 23.29**（差 -0.13）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/published_faces/rows/2/full`：**9.51 → 9.41**（差 -0.1）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/published_faces/rows/2/oos`：**17.97 → 17.72**（差 -0.25）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/published_faces/ticket`：**7.64 → 7.6**（差 -0.04）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/band_ruler/published_faces/ticket_oos`：**12.54 → 12.45**（差 -0.09）｜SECTION_ADVANCED｜这一节自己换了代：`band_ruler` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cash_caliber/control_error_bp`：**0.0043 → 0.0357**（差 0.0314）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_ladder/rolls/GC028`：**12 → 13**（差 1）｜RECOVERED_OLD_VALUE｜昨天的 12 今天仍在这页上：`/alias_stability/families/n_cross_name`（改名，不是重算）
- `/cash_ladder/tenors/1/annual_cny_spot`：**7016.0 → 7045.0**（差 29.0）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_ladder/tenors/1/mean250_pct`：**1.3611 → 1.3607**（差 -0.0004）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_ladder/tenors/1/spot_pct`：**1.235 → 1.24**（差 0.005）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_ladder/tenors/2/annual_cny_spot`：**7414.0 → 7670.0**（差 256.0）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_ladder/tenors/2/mean250_pct`：**1.4624 → 1.462**（差 -0.0004）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_ladder/tenors/2/spot_pct`：**1.305 → 1.35**（差 0.045）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_ladder/tenors/3/annual_cny_spot`：**7670.0 → 7755.0**（差 85.0）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_ladder/tenors/3/mean250_pct`：**1.4673 → 1.4669**（差 -0.0004）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_ladder/tenors/3/spot_pct`：**1.35 → 1.365**（差 0.015）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_ladder/tenors/4/annual_cny_realized_1y`：**8372.0 → 8325.0**（差 -47.0）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_ladder/tenors/4/annual_cny_spot`：**7698.0 → 7812.0**（差 114.0）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_ladder/tenors/4/edge_bp/1`：**16.6 → 15.8**（差 -0.8）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_ladder/tenors/4/edge_bp/5`：**9.0 → 8.0**（差 -1.0）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_ladder/tenors/4/idle_share_1y`：**0.0059 → 0.0055**（差 -0.0004）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_ladder/tenors/4/mean250_pct`：**1.4628 → 1.4624**（差 -0.0004）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_ladder/tenors/4/realized/1/days`：**338 → 366**（差 28）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_ladder/tenors/4/realized/1/idle_share`：**0.0059 → 0.0055**（差 -0.0004）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_ladder/tenors/4/realized/1/realized_pct`：**1.4737 → 1.4654**（差 -0.0083）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_ladder/tenors/4/realized/1/rolls`：**12 → 13**（差 1）｜RECOVERED_OLD_VALUE｜昨天的 12 今天仍在这页上：`/alias_stability/families/n_cross_name`（改名，不是重算）
- `/cash_ladder/tenors/4/realized/5/days`：**1798 → 1826**（差 28）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_ladder/tenors/4/realized/5/realized_pct`：**1.9789 → 1.9695**（差 -0.0094）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_ladder/tenors/4/realized/5/rolls`：**64 → 65**（差 1）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_ladder/tenors/4/rolls_1y`：**12 → 13**（差 1）｜RECOVERED_OLD_VALUE｜昨天的 12 今天仍在这页上：`/alias_stability/families/n_cross_name`（改名，不是重算）
- `/cash_ladder/tenors/4/spot_pct`：**1.355 → 1.375**（差 0.02）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_ladder/tenors/5/annual_cny_spot`：**7471.0 → 7499.0**（差 28.0）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_ladder/tenors/5/mean250_pct`：**1.4335 → 1.4329**（差 -0.0006）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_ladder/tenors/5/spot_pct`：**1.315 → 1.32**（差 0.005）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_money/block/book_rate/annual_cny`：**10067.0 → 10065.0**（差 -2.0）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_money/block/book_rate/gap_vs_spot_bp`：**-59.7 → -59.66**（差 0.04）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_money/block/book_rate/gap_vs_spot_cny`：**-3392.0 → -3389.0**（差 3.0）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_money/block/book_rate/pct`：**1.772 → 1.7716**（差 -0.0004）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_money/forward/book/pct`：**1.772 → 1.7716**（差 -0.0004）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_money/forward/gap_bp`：**85.77 → 85.73**（差 -0.04）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cash_money/forward/gap_bp_gross`：**59.7 → 59.66**（差 -0.04）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/cost_tape/arms/assumed_10bp/cagr`：**0.0941 → 0.0943**（差 0.0002）｜SECTION_ADVANCED｜这一节自己换了代：`cost_tape` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cost_tape/arms/assumed_10bp/sharpe`：**0.971 → 0.973**（差 0.002）｜SECTION_ADVANCED｜这一节自己换了代：`cost_tape` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cost_tape/arms/measured/cagr`：**0.0993 → 0.0995**（差 0.0002）｜SECTION_ADVANCED｜这一节自己换了代：`cost_tape` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cost_tape/arms/measured/sharpe`：**1.019 → 1.021**（差 0.002）｜SECTION_ADVANCED｜这一节自己换了代：`cost_tape` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cost_tape/arms/upper_p75/cagr`：**0.0954 → 0.0955**（差 0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`cost_tape` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cost_tape/arms/upper_p75/sharpe`：**0.983 → 0.985**（差 0.002）｜SECTION_ADVANCED｜这一节自己换了代：`cost_tape` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cost_tape/control/engine_cagr`：**0.0941 → 0.0943**（差 0.0002）｜SECTION_ADVANCED｜这一节自己换了代：`cost_tape` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/cost_tape/tape/widest_traded/1/p50_bp`：**30.8 → 30.7**（差 -0.1）｜SECTION_ADVANCED｜这一节自己换了代：`cost_tape` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/exposure_timing/arms/constant/cagr`：**0.0996 → 0.0993**（差 -0.0003）｜SECTION_ADVANCED｜这一节自己换了代：`exposure_timing` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/exposure_timing/arms/constant/sharpe`：**0.965 → 0.962**（差 -0.003）｜SECTION_ADVANCED｜这一节自己换了代：`exposure_timing` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/exposure_timing/arms/full/cagr`：**0.1307 → 0.1303**（差 -0.0004）｜SECTION_ADVANCED｜这一节自己换了代：`exposure_timing` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/exposure_timing/arms/full/sharpe`：**0.913 → 0.911**（差 -0.002）｜SECTION_ADVANCED｜这一节自己换了代：`exposure_timing` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/exposure_timing/arms/full/vol`：**0.153 → 0.1529**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`exposure_timing` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/exposure_timing/arms/production/cagr`：**0.0898 → 0.0895**（差 -0.0003）｜SECTION_ADVANCED｜这一节自己换了代：`exposure_timing` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/exposure_timing/arms/production/delevered_share`：**0.8799 → 0.88**（差 0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`exposure_timing` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/exposure_timing/arms/production/mean_exposure`：**0.7078 → 0.7079**（差 0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`exposure_timing` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/exposure_timing/arms/production/sharpe`：**0.941 → 0.938**（差 -0.003）｜SECTION_ADVANCED｜这一节自己换了代：`exposure_timing` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/exposure_timing/bars`：**1665 → 1666**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`exposure_timing` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/exposure_timing/placebo/cagr_mean`：**0.0996 → 0.0994**（差 -0.0002）｜SECTION_ADVANCED｜这一节自己换了代：`exposure_timing` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/exposure_timing/verdict/de_risking_pp`：**-3.11 → -3.1**（差 0.01）｜SECTION_ADVANCED｜这一节自己换了代：`exposure_timing` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/exposure_timing/verdict/placebo_p05_pp`：**-1.74 → -1.75**（差 -0.01）｜SECTION_ADVANCED｜这一节自己换了代：`exposure_timing` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_hedge/beta`：**0.07185718963947142 → 0.07458300567364223**（差 0.002726）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_hedge/capital_for_one_lot`：**11395936.91471321 → 10985880.665433725**（差 -410056.249279）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_hedge/corr`：**0.1373365917783091 → 0.1415643988218339**（差 0.004228）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_hedge/maxdd_delta_pp`：**1.5453866010586514 → -0.05485315943003499**（差 -1.60024）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_hedge/min_unit_notional`：**818880.0 → 819360.0**（差 480.0）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_hedge/sharpe_delta`：**0.005735999804863057 → -0.020536000001067034**（差 -0.026272）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_hedge/splice_days_dropped`：**1 → 85**（差 84）｜RECOVERED_OLD_VALUE｜昨天的 1 今天仍在这页上：`/alias_stability/families/rows/0/pair_stability/n_pairs`（改名，不是重算）
- `/futures_hedge/unit_over_target`：**11.395936914713209 → 10.985880665433726**（差 -0.410056）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_hedge/variance_removable_pct`：**1.8861339441281915 → 2.004047901378724**（差 0.117914）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_hedge/vol_delta_pp`：**-0.09457028960696418 → -0.10122922788117772**（差 -0.006659）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_hedge_tail/dsharpe`：**0.005735999804863057 → -0.020536000001067034**（差 -0.026272）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_hedge_tail/dsharpe_hi`：**0.09446056903527693 → 0.0719002244924948**（差 -0.02256）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_hedge_tail/dsharpe_lo`：**-0.06366444689345857 → -0.0964202006837476**（差 -0.032756）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_hedge_tail/share_above_uncond`：**0.968 → 0.9695**（差 0.0015）｜RECOVERED_OLD_VALUE｜昨天的 0.968 今天仍在这页上：`/width_return/rows/2/sharpe`（改名，不是重算）
- `/futures_hedge_tail/tail_beta`：**0.6115545672996576 → 0.6126419583867959**（差 0.001087）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_hedge_tail/tail_ci_hi`：**0.8343491781619469 → 0.8405742148706478**（差 0.006225）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_hedge_tail/tail_ci_lo`：**0.12672451800387655 → 0.13021062460324065**（差 0.003486）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_hedge_tail/tail_n`：**57 → 52**（差 -5）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_hedge_tail/uncond_beta`：**0.07185718963947142 → 0.07458300567364223**（差 0.002726）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/futures_ladder/rows/1/one_lot_notional_cny`：**1175460.0 → 1178520.0**（差 3060.0）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/2/one_lot_notional_cny`：**818880.0 → 819360.0**（差 480.0）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/3/net_pct_of_capital`：**2.63 → 2.62**（差 -0.01）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/3/net_pct_of_capital_by_mask/calendar`：**3.42 → 3.41**（差 -0.01）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/3/net_pct_of_capital_by_mask/published`：**2.63 → 2.62**（差 -0.01）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/3/net_pct_of_capital_by_mask/strictest`：**3.42 → 3.41**（差 -0.01）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/3/one_lot_notional_cny`：**1204600.0 → 1197480.0**（差 -7120.0）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_ladder/rows/3/vol_contrib_pct`：**6.1 → 6.0**（差 -0.1）｜SECTION_ADVANCED｜这一节自己换了代：`futures_ladder` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_sleeve/rows/0/carry_ann_compound_pct`：**8.778 → 8.753**（差 -0.025）｜SECTION_ADVANCED｜这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_sleeve/rows/0/carry_caliber/calendar_ann_pct`：**9.793 → 9.805**（差 0.012）｜SECTION_ADVANCED｜这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_sleeve/rows/0/carry_caliber/published_ann_pct`：**2.895 → 2.878**（差 -0.017）｜SECTION_ADVANCED｜这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_sleeve/rows/0/carry_caliber/spread_pp`：**6.898 → 6.927**（差 0.029）｜SECTION_ADVANCED｜这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_sleeve/rows/0/gap_net_pp`：**6.753 → 6.644**（差 -0.109）｜SECTION_ADVANCED｜这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_sleeve/rows/0/notional_per_lot_cny`：**1243680.0 → 1238960.0**（差 -4720.0）｜SECTION_ADVANCED｜这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_sleeve/rows/1/blend_gain_sharpe`：**0.133 → 0.131**（差 -0.002）｜SECTION_ADVANCED｜这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_sleeve/rows/1/carry_ann_compound_pct`：**3.625 → 3.565**（差 -0.06）｜SECTION_ADVANCED｜这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_sleeve/rows/1/carry_caliber/calendar_ann_pct`：**5.795 → 5.843**（差 0.048）｜SECTION_ADVANCED｜这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_sleeve/rows/1/carry_caliber/published_ann_pct`：**1.923 → 1.876**（差 -0.047）｜SECTION_ADVANCED｜这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_sleeve/rows/1/carry_caliber/spread_pp`：**3.872 → 3.967**（差 0.095）｜SECTION_ADVANCED｜这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_sleeve/rows/1/gap_net_pp`：**0.558 → 0.651**（差 0.093）｜SECTION_ADVANCED｜这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_sleeve/rows/1/notional_per_lot_cny`：**1181700.0 → 1175460.0**（差 -6240.0）｜SECTION_ADVANCED｜这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_sleeve/rows/2/blend_gain_sharpe`：**0.087 → 0.084**（差 -0.003）｜SECTION_ADVANCED｜这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_sleeve/rows/2/carry_ann_compound_pct`：**2.471 → 2.402**（差 -0.069）｜SECTION_ADVANCED｜这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_sleeve/rows/2/carry_caliber/calendar_ann_pct`：**5.324 → 5.39**（差 0.066）｜SECTION_ADVANCED｜这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_sleeve/rows/2/carry_caliber/published_ann_pct`：**1.617 → 1.561**（差 -0.056）｜SECTION_ADVANCED｜这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_sleeve/rows/2/carry_caliber/spread_pp`：**3.707 → 3.829**（差 0.122）｜SECTION_ADVANCED｜这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_sleeve/rows/2/notional_per_lot_cny`：**822720.0 → 818880.0**（差 -3840.0）｜SECTION_ADVANCED｜这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_sleeve/rows/3/blend_gain_sharpe`：**0.39 → 0.388**（差 -0.002）｜SECTION_ADVANCED｜这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_sleeve/rows/3/carry_ann_compound_pct`：**10.263 → 10.209**（差 -0.054）｜SECTION_ADVANCED｜这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_sleeve/rows/3/carry_caliber/calendar_ann_pct`：**11.954 → 12.013**（差 0.059）｜SECTION_ADVANCED｜这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_sleeve/rows/3/carry_caliber/published_ann_pct`：**5.928 → 5.882**（差 -0.046）｜SECTION_ADVANCED｜这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_sleeve/rows/3/carry_caliber/spread_pp`：**6.026 → 6.131**（差 0.105）｜SECTION_ADVANCED｜这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_sleeve/rows/3/gap_net_pp`：**7.733 → 7.847**（差 0.114）｜SECTION_ADVANCED｜这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/futures_sleeve/rows/3/notional_per_lot_cny`：**1221000.0 → 1204600.0**（差 -16400.0）｜SECTION_ADVANCED｜这一节自己换了代：`futures_sleeve` 2026-11-16 → 2026-11-17（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/idle_cash/vehicle_net_pct`：**1.772 → 1.7716**（差 -0.0004）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/leg_split/arms/base_book/bars`：**1665 → 1666**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/leg_split/arms/base_book/buckets_pp_per_year/plain`：**14.022 → 13.986**（差 -0.036）｜SECTION_ADVANCED｜这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/leg_split/arms/base_book/buckets_pp_per_year/toll`：**-1.577 → -1.576**（差 0.001）｜SECTION_ADVANCED｜这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/leg_split/arms/base_book/cagr_pct`：**12.99 → 12.95**（差 -0.04）｜SECTION_ADVANCED｜这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/leg_split/arms/base_book/fill_bar_drag_pp_per_year`：**-1.718 → -1.717**（差 0.001）｜SECTION_ADVANCED｜这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/leg_split/arms/base_book/plain_bars`：**1580 → 1581**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/leg_split/arms/base_book/plain_carry_pp_per_year`：**14.022 → 13.986**（差 -0.036）｜SECTION_ADVANCED｜这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/leg_split/arms/base_book/sharpe`：**0.908 → 0.906**（差 -0.002）｜SECTION_ADVANCED｜这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/leg_split/arms/base_book/total_log_pp`：**12.304 → 12.268**（差 -0.036）｜SECTION_ADVANCED｜这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/leg_split/arms/control_ew/bars`：**1665 → 1666**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/leg_split/arms/control_ew/buckets_pp_per_year/intraday`：**-2.151 → -2.15**（差 0.001）｜SECTION_ADVANCED｜这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/leg_split/arms/control_ew/buckets_pp_per_year/plain`：**6.352 → 6.328**（差 -0.024）｜SECTION_ADVANCED｜这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/leg_split/arms/control_ew/cagr_pct`：**4.01 → 3.99**（差 -0.02）｜SECTION_ADVANCED｜这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/leg_split/arms/control_ew/fill_bar_drag_pp_per_year`：**-2.389 → -2.388**（差 0.001）｜SECTION_ADVANCED｜这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/leg_split/arms/control_ew/plain_bars`：**1580 → 1581**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/leg_split/arms/control_ew/plain_carry_pp_per_year`：**6.351 → 6.328**（差 -0.023）｜SECTION_ADVANCED｜这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/leg_split/arms/control_ew/sharpe`：**0.309 → 0.308**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/leg_split/arms/control_ew/total_log_pp`：**3.963 → 3.94**（差 -0.023）｜SECTION_ADVANCED｜这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/leg_split/arms/production/bars`：**1665 → 1666**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/leg_split/arms/production/buckets_pp_per_year/intraday`：**-0.713 → -0.712**（差 0.001）｜SECTION_ADVANCED｜这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/leg_split/arms/production/buckets_pp_per_year/overnight`：**0.19 → 0.189**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/leg_split/arms/production/buckets_pp_per_year/plain`：**9.759 → 9.728**（差 -0.031）｜SECTION_ADVANCED｜这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/leg_split/arms/production/buckets_pp_per_year/toll`：**-1.156 → -1.155**（差 0.001）｜SECTION_ADVANCED｜这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/leg_split/arms/production/cagr_pct`：**8.35 → 8.32**（差 -0.03）｜SECTION_ADVANCED｜这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/leg_split/arms/production/fill_bar_drag_pp_per_year`：**-1.679 → -1.678**（差 0.001）｜SECTION_ADVANCED｜这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/leg_split/arms/production/plain_bars`：**1580 → 1581**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/leg_split/arms/production/plain_carry_pp_per_year`：**9.76 → 9.727**（差 -0.033）｜SECTION_ADVANCED｜这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/leg_split/arms/production/sharpe`：**0.881 → 0.878**（差 -0.003）｜SECTION_ADVANCED｜这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/leg_split/arms/production/total_log_pp`：**8.081 → 8.05**（差 -0.031）｜SECTION_ADVANCED｜这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/leg_split/selection_wedge_pp/intraday`：**1.504 → 1.503**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/leg_split/selection_wedge_pp/plain`：**7.67 → 7.658**（差 -0.012）｜SECTION_ADVANCED｜这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/leg_split/selection_wedge_pp/toll`：**-1.503 → -1.502**（差 0.001）｜SECTION_ADVANCED｜这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/leg_split/selection_wedge_pp/total`：**8.341 → 8.328**（差 -0.013）｜SECTION_ADVANCED｜这一节自己换了代：`leg_split` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/lookahead/affected_faces`：**94 → 96**（差 2）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/lot_floor/capital_needed/AU`：**2782200.0 → 2714400.0**（差 -67800.0）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/lot_floor/capital_needed/IF`：**3918200.0 → 3928400.0**（差 10200.0）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/lot_floor/capital_needed/IH`：**2729600.0 → 2731200.0**（差 1600.0）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/lot_floor/capital_needed/IM`：**4015333.3333333335 → 3991600.0**（差 -23733.333333）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/lot_floor/capital_needed/SC`：**1938000.0 → 1920333.3333333335**（差 -17666.666667）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/lot_floor/capital_needed/T`：**3667000.0 → 3667833.3333333335**（差 833.333333）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/lot_floor/capital_needed/TS`：**6843066.666666667 → 6843866.666666667**（差 800.0）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/lot_floor/etf_shares_at_1m/510300`：**0.000404 → 0.000406**（差 2e-06）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/lot_floor/etf_shares_at_1m/510500`：**0.000632 → 0.000631**（差 -1e-06）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/lot_floor/etf_shares_at_1m/512100`：**0.000247 → 0.000246**（差 -1e-06）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/lot_floor/etf_shares_at_1m/588000`：**0.000129 → 0.000132**（差 3e-06）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/lot_floor/shares_at_1m/AU`：**0.83466 → 0.81432**（差 -0.02034）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/lot_floor/shares_at_1m/IF`：**1.17546 → 1.17852**（差 0.00306）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/lot_floor/shares_at_1m/IH`：**0.81888 → 0.81936**（差 0.00048）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/lot_floor/shares_at_1m/IM`：**1.2046 → 1.19748**（差 -0.00712）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/lot_floor/shares_at_1m/SC`：**0.5814 → 0.5761**（差 -0.0053）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/lot_floor/shares_at_1m/T`：**1.1001 → 1.10035**（差 0.00025）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/lot_floor/shares_at_1m/TS`：**2.05292 → 2.05316**（差 0.00024）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/roster_audit/local_copies/1/laneside/local_disk_n`：**27 → 28**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`roster_audit` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/roster_audit/local_copies/1/local_disk_n`：**27 → 28**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`roster_audit` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/sibling_gap/immaterial_gain_cny`：**103.3 → 103.2**（差 -0.1）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/sibling_gap/pairs/0/amount_cny`：**86400.6 → 86347.8**（差 -52.8）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/sibling_gap/pairs/0/today_gain_cny`：**103.3 → 103.2**（差 -0.1）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/sibling_gap/pairs/1/amount_cny`：**86286.0 → 86390.2**（差 104.2）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/stress/n_days`：**5282 → 5283**（差 1）｜UNEXPLAINED｜没有旧值留存，也没有口径声明
- `/vol_window/paired/rows/0/bars`：**1663 → 1664**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/paired/rows/0/ci_p05_p95_pp/0`：**-0.084 → -0.106**（差 -0.022）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/paired/rows/0/ci_p05_p95_pp/1`：**2.004 → 1.973**（差 -0.031）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/paired/rows/0/mean_pp`：**0.873 → 0.867**（差 -0.006）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/paired/rows/0/share_positive`：**0.936 → 0.937**（差 0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/paired/rows/1/bars`：**1658 → 1659**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/paired/rows/1/ci_p05_p95_pp/0`：**0.637 → 0.715**（差 0.078）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/paired/rows/1/ci_p05_p95_pp/1`：**3.05 → 3.043**（差 -0.007）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/paired/rows/1/mean_pp`：**1.805 → 1.804**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/paired/rows/1/share_positive`：**0.999 → 0.998**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/paired/rows/2/bars`：**1653 → 1654**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/paired/rows/2/ci_p05_p95_pp/0`：**0.159 → 0.138**（差 -0.021）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/paired/rows/2/ci_p05_p95_pp/1`：**2.383 → 2.397**（差 0.014）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/paired/rows/2/mean_pp`：**1.197 → 1.192**（差 -0.005）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/paired/rows/2/share_positive`：**0.974 → 0.968**（差 -0.006）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/paired/rows/3/bars`：**1648 → 1649**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/paired/rows/3/ci_p05_p95_pp/0`：**-0.364 → -0.337**（差 0.027）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/paired/rows/3/ci_p05_p95_pp/1`：**1.194 → 1.167**（差 -0.027）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/paired/rows/3/mean_pp`：**0.41 → 0.409**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/paired/rows/3/share_positive`：**0.82 → 0.824**（差 0.004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/paired/verdict/min_ci_low_pp`：**-0.364 → -0.337**（差 0.027）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/paired/verdict/min_share_positive`：**0.82 → 0.824**（差 0.004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/panel/bars_named`：**5282 → 5283**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/0/cagr`：**0.1032 → 0.1033**（差 0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/0/oos_cagr`：**0.19 → 0.1902**（差 0.0002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/0/oos_sharpe`：**1.76 → 1.763**（差 0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/0/sharpe`：**1.043 → 1.044**（差 0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/1/cagr`：**0.1005 → 0.1006**（差 0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/1/oos_cagr`：**0.1831 → 0.1835**（差 0.0004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/1/oos_sharpe`：**1.731 → 1.734**（差 0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/1/sharpe`：**1.035 → 1.036**（差 0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/10/cagr`：**0.0995 → 0.0999**（差 0.0004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/10/oos_cagr`：**0.1863 → 0.187**（差 0.0007）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/10/oos_sharpe`：**1.622 → 1.628**（差 0.006）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/10/sharpe`：**0.982 → 0.985**（差 0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/10/vol`：**0.1065 → 0.1064**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/11/cagr`：**0.0942 → 0.0946**（差 0.0004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/11/oos_cagr`：**0.1753 → 0.1761**（差 0.0008）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/11/oos_sharpe`：**1.558 → 1.565**（差 0.007）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/11/sharpe`：**0.936 → 0.94**（差 0.004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/12/cagr`：**0.0871 → 0.0874**（差 0.0003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/12/oos_cagr`：**0.1655 → 0.1664**（差 0.0009）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/12/oos_sharpe`：**1.463 → 1.47**（差 0.007）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/12/sharpe`：**0.877 → 0.88**（差 0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/13/cagr`：**0.0731 → 0.0734**（差 0.0003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/13/oos_cagr`：**0.1491 → 0.1499**（差 0.0008）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/13/oos_sharpe`：**1.375 → 1.382**（差 0.007）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/13/sharpe`：**0.767 → 0.77**（差 0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/14/cagr`：**0.0671 → 0.0675**（差 0.0004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/14/oos_cagr`：**0.1373 → 0.1381**（差 0.0008）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/14/oos_sharpe`：**1.331 → 1.338**（差 0.007）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/14/sharpe`：**0.741 → 0.744**（差 0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/14/vol`：**0.0979 → 0.0978**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/15/cagr`：**0.1154 → 0.1157**（差 0.0003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/15/oos_cagr`：**0.1474 → 0.148**（差 0.0006）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/15/oos_sharpe`：**1.409 → 1.414**（差 0.005）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/15/sharpe`：**1.205 → 1.207**（差 0.002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/15/vol`：**0.0982 → 0.0981**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/16/cagr`：**0.1086 → 0.1089**（差 0.0003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/16/oos_cagr`：**0.1337 → 0.1343**（差 0.0006）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/16/oos_sharpe`：**1.253 → 1.258**（差 0.005）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/16/sharpe`：**1.117 → 1.12**（差 0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/17/cagr`：**0.111 → 0.1112**（差 0.0002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/17/oos_cagr`：**0.1451 → 0.1457**（差 0.0006）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/17/oos_sharpe`：**1.378 → 1.383**（差 0.005）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/17/sharpe`：**1.154 → 1.157**（差 0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/17/vol`：**0.0989 → 0.0988**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/18/cagr`：**0.0962 → 0.0964**（差 0.0002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/18/oos_cagr`：**0.1209 → 0.1214**（差 0.0005）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/18/oos_sharpe`：**1.228 → 1.232**（差 0.004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/18/sharpe`：**1.046 → 1.048**（差 0.002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/18/vol`：**0.0956 → 0.0955**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/19/cagr`：**0.091 → 0.0912**（差 0.0002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/19/oos_cagr`：**0.1162 → 0.1166**（差 0.0004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/19/oos_sharpe`：**1.228 → 1.232**（差 0.004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/19/sharpe`：**1.023 → 1.025**（差 0.002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/2/cagr`：**0.0941 → 0.0943**（差 0.0002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/2/oos_cagr`：**0.1772 → 0.1776**（差 0.0004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/2/oos_sharpe`：**1.681 → 1.685**（差 0.004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/2/sharpe`：**0.971 → 0.973**（差 0.002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/3/cagr`：**0.0754 → 0.0756**（差 0.0002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/3/oos_cagr`：**0.1353 → 0.1357**（差 0.0004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/3/oos_sharpe`：**1.455 → 1.46**（差 0.005）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/3/sharpe`：**0.833 → 0.835**（差 0.002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/4/cagr`：**0.0706 → 0.0708**（差 0.0002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/4/oos_cagr`：**0.1277 → 0.1281**（差 0.0004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/4/oos_sharpe`：**1.422 → 1.427**（差 0.005）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/4/sharpe`：**0.811 → 0.813**（差 0.002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/5/cagr`：**0.1133 → 0.1139**（差 0.0006）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/5/oos_cagr`：**0.1942 → 0.1956**（差 0.0014）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/5/oos_sharpe`：**1.583 → 1.593**（差 0.01）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/5/sharpe`：**1.072 → 1.077**（差 0.005）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/6/cagr`：**0.0993 → 0.0999**（差 0.0006）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/6/oos_cagr`：**0.1654 → 0.1668**（差 0.0014）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/6/oos_sharpe`：**1.415 → 1.426**（差 0.011）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/6/sharpe`：**0.97 → 0.975**（差 0.005）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/7/cagr`：**0.0945 → 0.0951**（差 0.0006）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/7/oos_cagr`：**0.1651 → 0.1665**（差 0.0014）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/7/oos_sharpe`：**1.412 → 1.423**（差 0.011）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/7/sharpe`：**0.929 → 0.935**（差 0.006）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/8/cagr`：**0.085 → 0.0856**（差 0.0006）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/8/oos_cagr`：**0.1544 → 0.1558**（差 0.0014）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/8/oos_sharpe`：**1.411 → 1.423**（差 0.012）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/8/sharpe`：**0.876 → 0.882**（差 0.006）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/9/cagr`：**0.0804 → 0.081**（差 0.0006）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/9/oos_cagr`：**0.1375 → 0.1389**（差 0.0014）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/9/oos_sharpe`：**1.317 → 1.329**（差 0.012）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/phase_rows/9/sharpe`：**0.863 → 0.869**（差 0.006）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/recomputed/largest_sharpe_gap_vs_shipped`：**0.259 → 0.258**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/recomputed/windows/0/oos_sharpe_delta_by_phase/0`：**0.079 → 0.078**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/recomputed/windows/0/oos_sharpe_delta_by_phase/1`：**0.171 → 0.17**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/recomputed/windows/0/oos_sharpe_delta_by_phase/2`：**0.159 → 0.158**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/recomputed/windows/0/sharpe_delta_by_phase/0`：**0.072 → 0.071**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/recomputed/windows/0/sharpe_delta_by_phase/1`：**0.143 → 0.142**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/recomputed/windows/0/sharpe_delta_by_phase/3`：**0.051 → 0.05**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/recomputed/windows/0/sharpe_delta_max`：**0.143 → 0.142**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/recomputed/windows/0/sharpe_delta_min`：**0.051 → 0.05**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/recomputed/windows/1/oos_sharpe_delta_by_phase/0`：**0.05 → 0.049**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/recomputed/windows/1/sharpe_delta_by_phase/0`：**0.064 → 0.063**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/recomputed/windows/1/sharpe_delta_by_phase/1`：**0.041 → 0.04**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/recomputed/windows/1/sharpe_delta_by_phase/2`：**0.059 → 0.06**（差 0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/recomputed/windows/1/sharpe_delta_max`：**0.064 → 0.063**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/recomputed/windows/2/oos_sharpe_delta_by_phase/0`：**-0.226 → -0.225**（差 0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/recomputed/windows/2/oos_sharpe_delta_by_phase/1`：**-0.001 → 0.0**（差 0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/recomputed/windows/2/oos_sharpe_delta_by_phase/3`：**-0.15 → -0.151**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/recomputed/windows/2/sharpe_delta_by_phase/3`：**-0.108 → -0.109**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/recomputed/windows/3/oos_sharpe_delta_by_phase/0`：**-0.259 → -0.258**（差 0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/recomputed/windows/3/oos_sharpe_delta_by_phase/1`：**-0.095 → -0.094**（差 0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/recomputed/windows/3/oos_sharpe_delta_by_phase/3`：**-0.15 → -0.151**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/recomputed/windows/3/sharpe_delta_by_phase/3`：**-0.131 → -0.132**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/verdict/largest_sharpe_gap_vs_shipped`：**0.259 → 0.258**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/verdict/windows/0/oos_sharpe_delta_by_phase/0`：**0.079 → 0.078**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/verdict/windows/0/oos_sharpe_delta_by_phase/1`：**0.171 → 0.17**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/verdict/windows/0/oos_sharpe_delta_by_phase/2`：**0.159 → 0.158**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/verdict/windows/0/sharpe_delta_by_phase/0`：**0.072 → 0.071**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/verdict/windows/0/sharpe_delta_by_phase/1`：**0.143 → 0.142**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/verdict/windows/0/sharpe_delta_by_phase/3`：**0.051 → 0.05**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/verdict/windows/0/sharpe_delta_max`：**0.143 → 0.142**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/verdict/windows/0/sharpe_delta_min`：**0.051 → 0.05**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/verdict/windows/1/oos_sharpe_delta_by_phase/0`：**0.05 → 0.049**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/verdict/windows/1/sharpe_delta_by_phase/0`：**0.064 → 0.063**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/verdict/windows/1/sharpe_delta_by_phase/1`：**0.041 → 0.04**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/verdict/windows/1/sharpe_delta_by_phase/2`：**0.059 → 0.06**（差 0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/verdict/windows/1/sharpe_delta_max`：**0.064 → 0.063**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/verdict/windows/2/oos_sharpe_delta_by_phase/0`：**-0.226 → -0.225**（差 0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/verdict/windows/2/oos_sharpe_delta_by_phase/1`：**-0.001 → 0.0**（差 0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/verdict/windows/2/oos_sharpe_delta_by_phase/3`：**-0.15 → -0.151**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/verdict/windows/2/sharpe_delta_by_phase/3`：**-0.108 → -0.109**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/verdict/windows/3/oos_sharpe_delta_by_phase/0`：**-0.259 → -0.258**（差 0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/verdict/windows/3/oos_sharpe_delta_by_phase/1`：**-0.095 → -0.094**（差 0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/verdict/windows/3/oos_sharpe_delta_by_phase/3`：**-0.15 → -0.151**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window/verdict/windows/3/sharpe_delta_by_phase/3`：**-0.131 → -0.132**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/edge/best_mean_sharpe`：**1.105 → 1.1078**（差 0.0028）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/edge/curve/0/max_sharpe`：**1.173 → 1.175**（差 0.002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/edge/curve/0/mean_sharpe`：**1.105 → 1.1078**（差 0.0028）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/edge/curve/0/min_sharpe`：**1.029 → 1.032**（差 0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/edge/curve/1/max_sharpe`：**1.184 → 1.186**（差 0.002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/edge/curve/1/mean_sharpe`：**1.1025 → 1.1053**（差 0.0028）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/edge/curve/1/min_sharpe`：**1.021 → 1.024**（差 0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/edge/curve/2/max_sharpe`：**1.205 → 1.207**（差 0.002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/edge/curve/2/mean_sharpe`：**1.0755 → 1.0782**（差 0.0027）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/edge/curve/2/min_sharpe`：**0.982 → 0.985**（差 0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/edge/curve/3/max_sharpe`：**1.154 → 1.157**（差 0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/edge/curve/3/mean_sharpe`：**0.9828 → 0.9862**（差 0.0034）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/edge/curve/3/min_sharpe`：**0.877 → 0.88**（差 0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/edge/gain_of_best_over_shipped`：**0.1222 → 0.1216**（差 -0.0006）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/edge/shipped/max_sharpe`：**1.154 → 1.157**（差 0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/edge/shipped/mean_sharpe`：**0.9828 → 0.9862**（差 0.0034）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/edge/shipped/min_sharpe`：**0.877 → 0.88**（差 0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/paired/rows/0/bars`：**1663 → 1664**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/paired/rows/0/ci_p05_p95_pp/0`：**0.371 → 0.347**（差 -0.024）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/paired/rows/0/ci_p05_p95_pp/1`：**3.111 → 3.008**（差 -0.103）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/paired/rows/0/mean_pp`：**1.61 → 1.602**（差 -0.008）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/paired/rows/0/share_positive`：**0.981 → 0.983**（差 0.002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/paired/rows/1/bars`：**1658 → 1659**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/paired/rows/1/ci_p05_p95_pp/0`：**1.092 → 1.085**（差 -0.007）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/paired/rows/1/ci_p05_p95_pp/1`：**4.197 → 4.182**（差 -0.015）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/paired/rows/1/mean_pp`：**2.593 → 2.592**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/paired/rows/2/bars`：**1653 → 1654**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/paired/rows/2/ci_p05_p95_pp/0`：**0.01 → -0.007**（差 -0.017）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/paired/rows/2/ci_p05_p95_pp/1`：**2.732 → 2.76**（差 0.028）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/paired/rows/2/mean_pp`：**1.348 → 1.34**（差 -0.008）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/paired/rows/2/share_positive`：**0.95 → 0.948**（差 -0.002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/paired/rows/3/bars`：**1648 → 1649**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/paired/rows/3/ci_p05_p95_pp/0`：**-0.67 → -0.708**（差 -0.038）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/paired/rows/3/ci_p05_p95_pp/1`：**1.75 → 1.742**（差 -0.008）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/paired/rows/3/mean_pp`：**0.501 → 0.497**（差 -0.004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/paired/rows/3/share_positive`：**0.764 → 0.749**（差 -0.015）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/paired/verdict/min_ci_low_pp`：**-0.67 → -0.708**（差 -0.038）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/paired/verdict/min_share_positive`：**0.764 → 0.749**（差 -0.015）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/panel/bars_named`：**5282 → 5283**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/0/cagr`：**0.1401 → 0.1403**（差 0.0002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/0/oos_cagr`：**0.2348 → 0.2352**（差 0.0004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/0/oos_sharpe`：**1.56 → 1.563**（差 0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/0/sharpe`：**0.969 → 0.97**（差 0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/0/vol`：**0.1531 → 0.153**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/1/cagr`：**0.1401 → 0.1403**（差 0.0002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/1/oos_cagr`：**0.2348 → 0.2352**（差 0.0004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/1/oos_sharpe`：**1.56 → 1.563**（差 0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/1/sharpe`：**0.969 → 0.97**（差 0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/1/vol`：**0.1531 → 0.153**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/10/cagr`：**0.1218 → 0.1224**（差 0.0006）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/10/oos_cagr`：**0.2041 → 0.2055**（差 0.0014）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/10/oos_sharpe`：**1.653 → 1.663**（差 0.01）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/10/sharpe`：**1.146 → 1.151**（差 0.005）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/11/cagr`：**0.1186 → 0.1192**（差 0.0006）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/11/oos_cagr`：**0.2017 → 0.2031**（差 0.0014）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/11/oos_sharpe`：**1.636 → 1.646**（差 0.01）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/11/sharpe`：**1.113 → 1.118**（差 0.005）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/12/cagr`：**0.1133 → 0.1139**（差 0.0006）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/12/oos_cagr`：**0.1942 → 0.1956**（差 0.0014）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/12/oos_sharpe`：**1.583 → 1.593**（差 0.01）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/12/sharpe`：**1.072 → 1.077**（差 0.005）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/13/cagr`：**0.0945 → 0.0951**（差 0.0006）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/13/oos_cagr`：**0.1651 → 0.1665**（差 0.0014）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/13/oos_sharpe`：**1.412 → 1.423**（差 0.011）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/13/sharpe`：**0.929 → 0.935**（差 0.006）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/14/cagr`：**0.1354 → 0.1358**（差 0.0004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/14/oos_cagr`：**0.2185 → 0.2193**（差 0.0008）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/14/oos_sharpe`：**1.196 → 1.2**（差 0.004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/14/sharpe`：**0.871 → 0.873**（差 0.002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/15/cagr`：**0.1354 → 0.1358**（差 0.0004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/15/oos_cagr`：**0.2185 → 0.2193**（差 0.0008）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/15/oos_sharpe`：**1.196 → 1.2**（差 0.004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/15/sharpe`：**0.871 → 0.873**（差 0.002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/16/cagr`：**0.1354 → 0.1358**（差 0.0004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/16/oos_cagr`：**0.2185 → 0.2193**（差 0.0008）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/16/oos_sharpe`：**1.196 → 1.2**（差 0.004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/16/sharpe`：**0.871 → 0.873**（差 0.002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/17/cagr`：**0.1015 → 0.1018**（差 0.0003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/17/oos_cagr`：**0.1915 → 0.1922**（差 0.0007）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/17/oos_sharpe`：**1.73 → 1.736**（差 0.006）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/17/sharpe`：**1.029 → 1.032**（差 0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/17/vol`：**0.1031 → 0.103**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/18/cagr`：**0.1033 → 0.1036**（差 0.0003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/18/oos_cagr`：**0.1919 → 0.1925**（差 0.0006）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/18/oos_sharpe`：**1.668 → 1.674**（差 0.006）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/18/sharpe`：**1.021 → 1.024**（差 0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/19/cagr`：**0.0995 → 0.0999**（差 0.0004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/19/oos_cagr`：**0.1863 → 0.187**（差 0.0007）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/19/oos_sharpe`：**1.622 → 1.628**（差 0.006）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/19/sharpe`：**0.982 → 0.985**（差 0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/19/vol`：**0.1065 → 0.1064**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/2/cagr`：**0.1401 → 0.1403**（差 0.0002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/2/oos_cagr`：**0.2348 → 0.2352**（差 0.0004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/2/oos_sharpe`：**1.56 → 1.563**（差 0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/2/sharpe`：**0.969 → 0.97**（差 0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/2/vol`：**0.1531 → 0.153**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/20/cagr`：**0.0871 → 0.0874**（差 0.0003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/20/oos_cagr`：**0.1655 → 0.1664**（差 0.0009）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/20/oos_sharpe`：**1.463 → 1.47**（差 0.007）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/20/sharpe`：**0.877 → 0.88**（差 0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/21/cagr`：**0.1593 → 0.1596**（差 0.0003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/21/oos_cagr`：**0.1919 → 0.1926**（差 0.0007）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/21/oos_sharpe`：**1.29 → 1.294**（差 0.004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/21/sharpe`：**1.13 → 1.132**（差 0.002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/21/vol`：**0.1452 → 0.1451**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/22/cagr`：**0.1593 → 0.1596**（差 0.0003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/22/oos_cagr`：**0.1919 → 0.1926**（差 0.0007）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/22/oos_sharpe`：**1.29 → 1.294**（差 0.004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/22/sharpe`：**1.13 → 1.132**（差 0.002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/22/vol`：**0.1452 → 0.1451**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/23/cagr`：**0.1593 → 0.1596**（差 0.0003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/23/oos_cagr`：**0.1919 → 0.1926**（差 0.0007）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/23/oos_sharpe`：**1.29 → 1.294**（差 0.004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/23/sharpe`：**1.13 → 1.132**（差 0.002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/23/vol`：**0.1452 → 0.1451**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/24/cagr`：**0.1161 → 0.1163**（差 0.0002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/24/oos_cagr`：**0.1519 → 0.1523**（差 0.0004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/24/oos_sharpe`：**1.368 → 1.372**（差 0.004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/24/sharpe`：**1.173 → 1.175**（差 0.002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/25/cagr`：**0.1139 → 0.1141**（差 0.0002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/25/oos_cagr`：**0.1458 → 0.1463**（差 0.0005）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/25/oos_sharpe`：**1.374 → 1.379**（差 0.005）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/25/sharpe`：**1.184 → 1.186**（差 0.002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/26/cagr`：**0.1154 → 0.1157**（差 0.0003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/26/oos_cagr`：**0.1474 → 0.148**（差 0.0006）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/26/oos_sharpe`：**1.409 → 1.414**（差 0.005）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/26/sharpe`：**1.205 → 1.207**（差 0.002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/26/vol`：**0.0982 → 0.0981**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/27/cagr`：**0.111 → 0.1112**（差 0.0002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/27/oos_cagr`：**0.1451 → 0.1457**（差 0.0006）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/27/oos_sharpe`：**1.378 → 1.383**（差 0.005）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/27/sharpe`：**1.154 → 1.157**（差 0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/27/vol`：**0.0989 → 0.0988**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/3/cagr`：**0.1106 → 0.1107**（差 0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/3/oos_cagr`：**0.1971 → 0.1974**（差 0.0003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/3/oos_sharpe`：**1.762 → 1.764**（差 0.002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/3/sharpe`：**1.072 → 1.073**（差 0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/3/vol`：**0.1073 → 0.1072**（差 -0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/4/cagr`：**0.1116 → 0.1117**（差 0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/4/oos_cagr`：**0.2045 → 0.2048**（差 0.0003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/4/oos_sharpe`：**1.824 → 1.826**（差 0.002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/4/sharpe`：**1.092 → 1.093**（差 0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/5/cagr`：**0.1032 → 0.1033**（差 0.0001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/5/oos_cagr`：**0.19 → 0.1902**（差 0.0002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/5/oos_sharpe`：**1.76 → 1.763**（差 0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/5/sharpe`：**1.043 → 1.044**（差 0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/6/cagr`：**0.0941 → 0.0943**（差 0.0002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/6/oos_cagr`：**0.1772 → 0.1776**（差 0.0004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/6/oos_sharpe`：**1.681 → 1.685**（差 0.004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/6/sharpe`：**0.971 → 0.973**（差 0.002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/7/cagr`：**0.1391 → 0.1396**（差 0.0005）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/7/oos_cagr`：**0.2038 → 0.2052**（差 0.0014）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/7/oos_sharpe`：**1.181 → 1.188**（差 0.007）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/7/sharpe`：**0.905 → 0.908**（差 0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/8/cagr`：**0.1391 → 0.1396**（差 0.0005）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/8/oos_cagr`：**0.2038 → 0.2052**（差 0.0014）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/8/oos_sharpe`：**1.181 → 1.188**（差 0.007）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/8/sharpe`：**0.905 → 0.908**（差 0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/9/cagr`：**0.1391 → 0.1396**（差 0.0005）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/9/oos_cagr`：**0.2038 → 0.2052**（差 0.0014）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/9/oos_sharpe`：**1.181 → 1.188**（差 0.007）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/phase_rows/9/sharpe`：**0.905 → 0.908**（差 0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_edge/best_mean_sharpe`：**1.105 → 1.1078**（差 0.0028）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_edge/curve/0/max_sharpe`：**1.173 → 1.175**（差 0.002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_edge/curve/0/mean_sharpe`：**1.105 → 1.1078**（差 0.0028）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_edge/curve/0/min_sharpe`：**1.029 → 1.032**（差 0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_edge/curve/1/max_sharpe`：**1.184 → 1.186**（差 0.002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_edge/curve/1/mean_sharpe`：**1.1025 → 1.1053**（差 0.0028）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_edge/curve/1/min_sharpe`：**1.021 → 1.024**（差 0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_edge/curve/2/max_sharpe`：**1.205 → 1.207**（差 0.002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_edge/curve/2/mean_sharpe`：**1.0755 → 1.0782**（差 0.0027）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_edge/curve/2/min_sharpe`：**0.982 → 0.985**（差 0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_edge/curve/3/max_sharpe`：**1.154 → 1.157**（差 0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_edge/curve/3/mean_sharpe`：**0.9828 → 0.9862**（差 0.0034）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_edge/curve/3/min_sharpe`：**0.877 → 0.88**（差 0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_edge/gain_of_best_over_shipped`：**0.1222 → 0.1216**（差 -0.0006）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_edge/shipped/max_sharpe`：**1.154 → 1.157**（差 0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_edge/shipped/mean_sharpe`：**0.9828 → 0.9862**（差 0.0034）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_edge/shipped/min_sharpe`：**0.877 → 0.88**（差 0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/largest_sharpe_gap_vs_shipped`：**0.267 → 0.27**（差 0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/0/oos_sharpe_delta_by_phase/0`：**-0.121 → -0.122**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/0/oos_sharpe_delta_by_phase/1`：**-0.231 → -0.235**（差 -0.004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/0/oos_sharpe_delta_by_phase/2`：**-0.267 → -0.27**（差 -0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/0/oos_sharpe_delta_by_phase/3`：**-0.088 → -0.089**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/0/sharpe_delta_by_phase/0`：**-0.002 → -0.003**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/0/sharpe_delta_by_phase/1`：**-0.024 → -0.027**（差 -0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/0/sharpe_delta_by_phase/2`：**-0.006 → -0.007**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/0/sharpe_delta_by_phase/3`：**-0.024 → -0.025**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/0/sharpe_delta_max`：**-0.002 → -0.003**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/0/sharpe_delta_min`：**-0.024 → -0.027**（差 -0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/1/oos_sharpe_delta_by_phase/0`：**-0.121 → -0.122**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/1/oos_sharpe_delta_by_phase/1`：**-0.231 → -0.235**（差 -0.004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/1/oos_sharpe_delta_by_phase/2`：**-0.267 → -0.27**（差 -0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/1/oos_sharpe_delta_by_phase/3`：**-0.088 → -0.089**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/1/sharpe_delta_by_phase/0`：**-0.002 → -0.003**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/1/sharpe_delta_by_phase/1`：**-0.024 → -0.027**（差 -0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/1/sharpe_delta_by_phase/2`：**-0.006 → -0.007**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/1/sharpe_delta_by_phase/3`：**-0.024 → -0.025**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/1/sharpe_delta_max`：**-0.002 → -0.003**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/1/sharpe_delta_min`：**-0.024 → -0.027**（差 -0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/2/oos_sharpe_delta_by_phase/0`：**-0.121 → -0.122**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/2/oos_sharpe_delta_by_phase/1`：**-0.231 → -0.235**（差 -0.004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/2/oos_sharpe_delta_by_phase/2`：**-0.267 → -0.27**（差 -0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/2/oos_sharpe_delta_by_phase/3`：**-0.088 → -0.089**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/2/sharpe_delta_by_phase/0`：**-0.002 → -0.003**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/2/sharpe_delta_by_phase/1`：**-0.024 → -0.027**（差 -0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/2/sharpe_delta_by_phase/2`：**-0.006 → -0.007**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/2/sharpe_delta_by_phase/3`：**-0.024 → -0.025**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/2/sharpe_delta_max`：**-0.002 → -0.003**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/2/sharpe_delta_min`：**-0.024 → -0.027**（差 -0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/3/oos_sharpe_delta_by_phase/0`：**0.081 → 0.079**（差 -0.002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/3/oos_sharpe_delta_by_phase/1`：**0.241 → 0.24**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/3/oos_sharpe_delta_by_phase/2`：**0.267 → 0.266**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/3/oos_sharpe_delta_by_phase/3`：**-0.01 → -0.011**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/3/sharpe_delta_by_phase/0`：**0.101 → 0.1**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/3/sharpe_delta_by_phase/1`：**0.217 → 0.216**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/3/sharpe_delta_by_phase/3`：**0.019 → 0.018**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/3/sharpe_delta_max`：**0.217 → 0.216**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/3/sharpe_delta_min`：**0.019 → 0.018**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/4/oos_sharpe_delta_by_phase/0`：**0.143 → 0.141**（差 -0.002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/4/oos_sharpe_delta_by_phase/1`：**0.224 → 0.223**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/4/oos_sharpe_delta_by_phase/2`：**0.205 → 0.204**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/4/sharpe_delta_by_phase/0`：**0.121 → 0.12**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/4/sharpe_delta_by_phase/1`：**0.184 → 0.183**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/4/sharpe_delta_by_phase/3`：**0.03 → 0.029**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/4/sharpe_delta_max`：**0.184 → 0.183**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/4/sharpe_delta_min`：**0.03 → 0.029**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/5/oos_sharpe_delta_by_phase/0`：**0.079 → 0.078**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/5/oos_sharpe_delta_by_phase/1`：**0.171 → 0.17**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/5/oos_sharpe_delta_by_phase/2`：**0.159 → 0.158**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/5/sharpe_delta_by_phase/0`：**0.072 → 0.071**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/5/sharpe_delta_by_phase/1`：**0.143 → 0.142**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/5/sharpe_delta_by_phase/3`：**0.051 → 0.05**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/5/sharpe_delta_max`：**0.143 → 0.142**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/recomputed_verdict/windows/5/sharpe_delta_min`：**0.051 → 0.05**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/largest_sharpe_gap_vs_shipped`：**0.267 → 0.27**（差 0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/0/oos_sharpe_delta_by_phase/0`：**-0.121 → -0.122**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/0/oos_sharpe_delta_by_phase/1`：**-0.231 → -0.235**（差 -0.004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/0/oos_sharpe_delta_by_phase/2`：**-0.267 → -0.27**（差 -0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/0/oos_sharpe_delta_by_phase/3`：**-0.088 → -0.089**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/0/sharpe_delta_by_phase/0`：**-0.002 → -0.003**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/0/sharpe_delta_by_phase/1`：**-0.024 → -0.027**（差 -0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/0/sharpe_delta_by_phase/2`：**-0.006 → -0.007**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/0/sharpe_delta_by_phase/3`：**-0.024 → -0.025**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/0/sharpe_delta_max`：**-0.002 → -0.003**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/0/sharpe_delta_min`：**-0.024 → -0.027**（差 -0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/1/oos_sharpe_delta_by_phase/0`：**-0.121 → -0.122**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/1/oos_sharpe_delta_by_phase/1`：**-0.231 → -0.235**（差 -0.004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/1/oos_sharpe_delta_by_phase/2`：**-0.267 → -0.27**（差 -0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/1/oos_sharpe_delta_by_phase/3`：**-0.088 → -0.089**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/1/sharpe_delta_by_phase/0`：**-0.002 → -0.003**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/1/sharpe_delta_by_phase/1`：**-0.024 → -0.027**（差 -0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/1/sharpe_delta_by_phase/2`：**-0.006 → -0.007**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/1/sharpe_delta_by_phase/3`：**-0.024 → -0.025**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/1/sharpe_delta_max`：**-0.002 → -0.003**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/1/sharpe_delta_min`：**-0.024 → -0.027**（差 -0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/2/oos_sharpe_delta_by_phase/0`：**-0.121 → -0.122**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/2/oos_sharpe_delta_by_phase/1`：**-0.231 → -0.235**（差 -0.004）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/2/oos_sharpe_delta_by_phase/2`：**-0.267 → -0.27**（差 -0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/2/oos_sharpe_delta_by_phase/3`：**-0.088 → -0.089**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/2/sharpe_delta_by_phase/0`：**-0.002 → -0.003**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/2/sharpe_delta_by_phase/1`：**-0.024 → -0.027**（差 -0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/2/sharpe_delta_by_phase/2`：**-0.006 → -0.007**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/2/sharpe_delta_by_phase/3`：**-0.024 → -0.025**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/2/sharpe_delta_max`：**-0.002 → -0.003**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/2/sharpe_delta_min`：**-0.024 → -0.027**（差 -0.003）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/3/oos_sharpe_delta_by_phase/0`：**0.081 → 0.079**（差 -0.002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/3/oos_sharpe_delta_by_phase/1`：**0.241 → 0.24**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/3/oos_sharpe_delta_by_phase/2`：**0.267 → 0.266**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/3/oos_sharpe_delta_by_phase/3`：**-0.01 → -0.011**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/3/sharpe_delta_by_phase/0`：**0.101 → 0.1**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/3/sharpe_delta_by_phase/1`：**0.217 → 0.216**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/3/sharpe_delta_by_phase/3`：**0.019 → 0.018**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/3/sharpe_delta_max`：**0.217 → 0.216**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/3/sharpe_delta_min`：**0.019 → 0.018**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/4/oos_sharpe_delta_by_phase/0`：**0.143 → 0.141**（差 -0.002）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/4/oos_sharpe_delta_by_phase/1`：**0.224 → 0.223**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/4/oos_sharpe_delta_by_phase/2`：**0.205 → 0.204**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/4/sharpe_delta_by_phase/0`：**0.121 → 0.12**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/4/sharpe_delta_by_phase/1`：**0.184 → 0.183**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/4/sharpe_delta_by_phase/3`：**0.03 → 0.029**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/4/sharpe_delta_max`：**0.184 → 0.183**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/4/sharpe_delta_min`：**0.03 → 0.029**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/5/oos_sharpe_delta_by_phase/0`：**0.079 → 0.078**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/5/oos_sharpe_delta_by_phase/1`：**0.171 → 0.17**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/5/oos_sharpe_delta_by_phase/2`：**0.159 → 0.158**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/5/sharpe_delta_by_phase/0`：**0.072 → 0.071**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/5/sharpe_delta_by_phase/1`：**0.143 → 0.142**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/5/sharpe_delta_by_phase/3`：**0.051 → 0.05**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/5/sharpe_delta_max`：**0.143 → 0.142**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/vol_window_edge/verdict/windows/5/sharpe_delta_min`：**0.051 → 0.05**（差 -0.001）｜SECTION_ADVANCED｜这一节自己换了代：`vol_window_edge` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/window_label/identity/the full-window cell's own window reproduces the ticket/delta_pp`：**0.0 → 0.06**（差 0.06）｜SECTION_ADVANCED｜这一节自己换了代：`window_label` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/window_label/identity/the full-window cell's own window reproduces the ticket/measured_pp`：**12.45 → 12.39**（差 -0.06）｜SECTION_ADVANCED｜这一节自己换了代：`window_label` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/window_label/rows/printed_under_full_header/sharpe`：**1.687 → 1.688**（差 0.001）｜SECTION_ADVANCED｜这一节自己换了代：`window_label` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/window_label/rows/same_book_full_window/bars`：**1537 → 1538**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`window_label` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/window_label/rows/same_book_full_window/cagr_pp`：**7.6 → 7.58**（差 -0.02）｜SECTION_ADVANCED｜这一节自己换了代：`window_label` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/window_label/rows/same_book_full_window/sharpe`：**1.324 → 1.32**（差 -0.004）｜SECTION_ADVANCED｜这一节自己换了代：`window_label` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/window_label/table_row/full/cagr_pct`：**7.6 → 7.58**（差 -0.02）｜SECTION_ADVANCED｜这一节自己换了代：`window_label` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/window_label/table_row/full/sharpe`：**1.324 → 1.32**（差 -0.004）｜SECTION_ADVANCED｜这一节自己换了代：`window_label` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/window_label/table_row/full_window_bars`：**1537 → 1538**（差 1）｜SECTION_ADVANCED｜这一节自己换了代：`window_label` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/window_label/table_row/oos/sharpe`：**1.687 → 1.688**（差 0.001）｜SECTION_ADVANCED｜这一节自己换了代：`window_label` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json
- `/window_label/verdict/gap_pp`：**4.85 → 4.87**（差 0.02）｜SECTION_ADVANCED｜这一节自己换了代：`window_label` 2026-11-17 → 2026-11-18（标题那根 bar 两天相同，这一节不同）；分节 bar 面：results/live_book_section_bars.json

同一个隔夜、同一根 bar、同一笔钱，这页昨天给一个答案、今天给另一个。两个答案不可能都对：走 `RECOVERED_OLD_VALUE`／`DECLARED_RULER` 的那一条说明**是新答案改了算法**（旧数还在页上或口径句改了），读的人要按新口径重读昨天的判断；没有这两条说明的，就是这页偷偷换了数。

## 还有哪些节在同 bar 上改了数（76 个）

- `cash_ladder`：25 个
- `lot_floor`：18 个
- `futures_hedge`：9 个
- `futures_hedge_tail`：8 个
- `cash_money`：7 个
- `sibling_gap`：4 个
- `backtest_band`：1 个
- `cash_caliber`：1 个
- `idle_cash`：1 个
- `lookahead`：1 个
- `stress`：1 个

这几节的位移**没有任何解释**（不是转抄、不是换输入、不是换代）。页要在同一根 bar 上改这些数，就得自己写出理由；写不出来，读的人就分不清「今天变了」和「口径变了」。

## 这张面自己什么时候算陈旧（r1834）

- 本面在产物里记下它读的那两张日页的字节指纹（`inputs.today` / `inputs.prev`：`day`／`file`／`bytes`／`sha256`）。`--check` **先比字节，再比数字**：日页在写完面之后被重写过（CEO 页有同链生成腿，这是常态）→ 报 `STALE` 并点名是哪张页、指纹从哪个前缀换到哪个前缀；最新两张日页已经换了一对 → 同样 `STALE`；**面里没有指纹**（早于本版写的面）→ 也报 `STALE`，不当作通过。
- 只有字节仍然对得上、数字却对不上，才是 `FACE_DOES_NOT_REPRODUCE`——那才是本面算错了。
- 为什么要分开：两种失败以前都印成一串 `counts.*`，读的人分不清「页动过」和「面坏了」，而链上的修复规则只对写着 stale 的那种付重算（别的重算=把闸变成抹红机器）。

## 怎么读

- `CLOCK`＝钟面（`age_h`/`silent_h`/`lag_days` 这类）：没有新 bar 也该走，不构成问题；但它的存在说明「哪些数允许自己走」是**名单制**的，名单写在本脚本顶部，不由数据推出来。
- `DATA_ADVANCED`＝数据推进了，所有定价读数都允许动。
- `RECOVERED_OLD_VALUE`＝昨天那个数今天还在页上，只是换了名字——那是**改名**不是重算；读的人必须知道这一点，否则会把「口径换了」读成「今天变了」。
- `DECLARED_RULER`＝同一块里的口径句（`ruler`/`basis`/`convention`）改了，位移由它自己声明；句子改了而读者没看见，等于数被悄悄换了定义。
- `SECTION_ADVANCED`＝这一**节**自己换了代（标题那根 bar 两天相同，这一节不同，按 `results/live_book_section_bars.json` 判）：不是同 bar 重算漂移，而是页面里混着两代数据（页面本身另有 `PAGE_MIXES_BARS` 面在报）。
- `INPUT_IDENTITY_CHANGED`＝这一节**拿什么算**变了：它在自己身上写下的面板指纹（16 位十六进制）两天不同。族面是按「几个臂已重算」分批定价的，换一批臂，同一根 bar 上这一节的数就会动——这是它自己的输入变了，不是它在同一天改了口径。本档与 `DECLARED_RULER` 同一弱点：它信的是这一节自己的宣告，不独立复算。
- `QUOTED_FROM_SOURCE`＝这个数不是这页算的：它的块里写着 `source`（如`results/x.json:fresh_pairs`），而那个文件**现在**读到的值正好等于今天印的值。页只是转抄，动的是被引用的那张面（另一条车道）；写这张面的人不是改数的人。
- `UNEXPLAINED`＝既没有旧值留存、也没有口径声明——**这一档非零就是本面要报的事**。

## 未验证（如实）

- 只比**相邻两天**：更早的口径变更若在两页之前发生，本面看不见（可手工指定更多日页，未做）。
- 「旧值仍在」靠数值相等判定（相对 1e-9）：两个无关的数恰好相等的概率不低，所以 `RECOVERED_OLD_VALUE` 是**线索**不是证明，行里同时印出它在哪个键上，供人核。
- 钟面名单是写死的：新出现的钟面字段会被算成 `MOVED`，本面会如实报（宁可多报）。
- 本面不判「这个改动是否合理」，也不碰任何生产件；它只读已发布日页。
