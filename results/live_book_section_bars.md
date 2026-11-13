# CEO 页面：这一页是哪一天的（r1533）

*由 `scripts/live_book_section_bars.py` 生成；判据见文件头。*

页面声明的 2026-11-13 就是它全部 49 个带日期的节的 bar；另有 7 节（backtest_band、agreement、sources、priced_faces、research_arc、sibling_gap、authority）不带任何日期字段——无法核验它们算到哪天，也不把它们猜成同一天。

页面逐节 bar：头部声明 **2026-11-13**，49 个带日期的节里 **49** 节在这一天，其余 0 节在别的 bar 上。

这 7 节没有任何日期字段，本面**不替它们认领**任何一根 bar：backtest_band, agreement, sources, priced_faces, research_arc, sibling_gap, authority。
