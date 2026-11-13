# CEO 页面：这一页是哪一天的（r1533）

*由 `scripts/live_book_section_bars.py` 生成；判据见文件头。*

页面头部写着按 2026-11-13 定价，但 47 个带日期的节里只有 41 节真在这一天；其余 6 节不在这一天（最旧停在 2026-11-11（最差 cash_handshake 落后 2 个交易日）），另外 9 节根本没有日期——它们不是同一根 bar 上的数，读的时候不能互相加减。这 6 节里，1 节的产物有同名链腿在守；4 节（cash_handshake, cash_ladder, cash_money, cash_yield）是这一页每次生成时自己重算的，停的正是它读的那块面板的最后一天：data/repo_daily/GC001.csv（update_repo.py / bm-a · T-88 车道，本机只读，末行 2026-11-11）、data/repo_daily（update_repo.py / bm-a · T-88 车道，本机只读，末行 2026-11-11）——落后的是那块面板，不是没人重跑这节；`data/repo_daily` 末行 2026-11-11；最后写入 33.6 h 前；属主 bm-a（update_repo.py） 自己的心跳停在 22.0 h 前——是那条车道停了，不是页面慢；`data/repo_daily/GC001.csv` 末行 2026-11-11；最后写入 33.7 h 前；属主 bm-a（update_repo.py） 自己的心跳停在 22.0 h 前——是那条车道停了，不是页面慢；1 节（k_gap）没有任何一条链腿重跑过它们——那是这一页真正的缺口。

页面逐节 bar：头部声明 **2026-11-13**，47 个带日期的节里 **41** 节在这一天，其余 6 节在别的 bar 上。

| 节 | 它停在哪根 bar | 落后（交易日） | 守它的链腿 |
|---|---|---|---|
| cash_handshake | 2026-11-11 | 2 | 页内重算（data/repo_daily/GC001.csv 末行 2026-11-11） |
| cash_ladder | 2026-11-11 | 2 | 页内重算（data/repo_daily 末行 2026-11-11） |
| cash_money | 2026-11-11 | 2 | 页内重算（data/repo_daily/GC001.csv 末行 2026-11-11） |
| cash_yield | 2026-11-11 | 2 | 页内重算（data/repo_daily/GC001.csv 末行 2026-11-11） |
| k_gap | 2026-11-12 | 1 | **没有** |
| leg_split | 2026-11-12 | 1 | etf_book_leg_attribution |

「守它的链腿」是按名字匹配的链清单（腿名含该节的名字或产物名），只回答「有没有一条腿会重跑它」，不回答那条腿上次过没过——这两件事在页面上一向是两个错。标着「页内重算」的节不是没腿跑：这一页每次生成都把它们算一遍，它们停在那天是因为下面那块面板只到那天，动作在上游数据车道，不在本页。标着「窗口段」的节也不是没更新：它本来就是按一整段固定窗口量的，印的那个日期是窗口的终点，要它跟上页头只能把整段窗口重算一遍（那是引擎的活，不是链腿的活）。印「没有」的那几节，才是这一页真正的缺口。

这 9 节没有任何日期字段，本面**不替它们认领**任何一根 bar：backtest_band, agreement, sources, priced_faces, research_arc, permission, sibling_gap, executed, authority。
