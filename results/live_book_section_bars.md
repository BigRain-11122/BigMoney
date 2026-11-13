# CEO 页面：这一页是哪一天的（r1533）

*由 `scripts/live_book_section_bars.py` 生成；判据见文件头。*

页面头部写着按 2026-11-13 定价，但 47 个带日期的节里只有 47 节真在这一天；另外 9 节根本没有日期——它们不是同一根 bar 上的数，读的时候不能互相加减。

页面逐节 bar：头部声明 **2026-11-13**，47 个带日期的节里 **47** 节在这一天，其余 0 节在别的 bar 上。

这 9 节没有任何日期字段，本面**不替它们认领**任何一根 bar：backtest_band, agreement, sources, priced_faces, research_arc, permission, sibling_gap, executed, authority。
