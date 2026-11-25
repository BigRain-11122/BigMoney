# CEO 页面：这一页是哪一天的（r1533）

*由 `scripts/live_book_section_bars.py` 生成；判据见文件头。*

页面头部写着按 2026-11-24 定价，但 75 个带日期的节里只有 45 节真在这一天；其余 30 节不在这一天（最旧停在 2026-11-17（最差 alias_census 落后 5 个交易日）），另外 3 节根本没有日期——它们不是同一根 bar 上的数，读的时候不能互相加减。2 节按设计没有 bar（sources=指针块（只列它引用的文件，本身不是一次测量）、authority=人事年龄（机器多久没写心跳，时间量不是价格日））——它们本来就不量某一天，催它们补日期是催不动的事。这 30 节里，23 节的产物有同名链腿在守；4 节（cash_handshake, cash_ladder, cash_money, cash_yield）是这一页每次生成时自己重算的，停的正是它读的那块面板的最后一天：data/repo_daily/GC001.csv（update_repo.py / bm-a · T-88 车道，本机只读，末行 2026-11-20）、data/repo_daily（update_repo.py / bm-a · T-88 车道，本机只读，末行 2026-11-20）——落后的是那块面板，不是没人重跑这节；`data/repo_daily` 末行 2026-11-20；最后写入 56.8 h 前；属主 bm-a（update_repo.py） 自己的心跳停在 143.0 h 前——是那条车道停了，不是页面慢；`data/repo_daily/GC001.csv` 末行 2026-11-20；最后写入 56.8 h 前；属主 bm-a（update_repo.py） 自己的心跳停在 143.0 h 前——是那条车道停了，不是页面慢；3 节（bets, derisk, k_gap）没有任何一条链腿重跑过它们——那是这一页真正的缺口；其中 1 节自己就带着两根以上的日期（fleet：2026-10-30/2026-11-18/2026-11-24）——它们不是「没写日期」，是写了两天的数，本面不替它们挑一天。

页面逐节 bar：头部声明 **2026-11-24**，75 个带日期的节里 **45** 节在这一天，其余 30 节在别的 bar 上。

| 节 | 它停在哪根 bar | 落后（交易日） | 守它的链腿 |
|---|---|---|---|
| alias_census | 2026-11-17 | 5 | alias_census |
| harvest_census | 2026-11-17 | 5 | harvest_census |
| alias_stability | 2026-11-19 | 3 | alias_stability |
| era_capacity | 2026-11-19 | 3 | era_capacity_write |
| width_fit | 2026-11-19 | 3 | etf_book_width_fit |
| bets | 2026-11-20 | 2 | **没有** |
| cash_caliber | 2026-11-20 | 2 | etf_book_cash_caliber_band |
| cash_handshake | 2026-11-20 | 2 | 页内重算（data/repo_daily/GC001.csv 末行 2026-11-20） |
| cash_ladder | 2026-11-20 | 2 | 页内重算（data/repo_daily 末行 2026-11-20） |
| cash_money | 2026-11-20 | 2 | 页内重算（data/repo_daily/GC001.csv 末行 2026-11-20） |
| cash_yield | 2026-11-20 | 2 | 页内重算（data/repo_daily/GC001.csv 末行 2026-11-20） |
| closed_axes | 2026-11-20 | 2 | etf_book_closed_axes |
| …其余 18 节 | | | |

「守它的链腿」是按名字匹配的链清单（腿名含该节的名字或产物名），只回答「有没有一条腿会重跑它」，不回答那条腿上次过没过——这两件事在页面上一向是两个错。标着「页内重算」的节不是没腿跑：这一页每次生成都把它们算一遍，它们停在那天是因为下面那块面板只到那天，动作在上游数据车道，不在本页。标着「窗口段」的节也不是没更新：它本来就是按一整段固定窗口量的，印的那个日期是窗口的终点，要它跟上页头只能把整段窗口重算一遍（那是引擎的活，不是链腿的活）。印「没有」的那几节，才是这一页真正的缺口。

这 3 节没有任何日期字段，本面**不替它们认领**任何一根 bar：sources, authority, fleet。

其中 2 节按设计就不该有 bar（sources、authority）——它们不是测量：
- sources：指针块（只列它引用的文件，本身不是一次测量）
- authority：人事年龄（机器多久没写心跳，时间量不是价格日）

其中 1 节其实写了两根以上的日期——本面不挑，把两天的出处照抄在这里：fleet（board_ts=2026-11-24、rows[0].last_seen=2026-11-18、rows[1].last_seen=2026-10-30、rows[2].last_seen=2026-11-24）。
