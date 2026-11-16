# CEO 页面：这一页是哪一天的（r1533）

*由 `scripts/live_book_section_bars.py` 生成；判据见文件头。*

页面头部写着按 2026-11-16 定价，但 63 个带日期的节里只有 13 节真在这一天；其余 50 节不在这一天（最旧停在 2026-11-13（最差 band_ruler 落后 1 个交易日）），另外 4 节根本没有日期——它们不是同一根 bar 上的数，读的时候不能互相加减。2 节按设计没有 bar（sources=指针块（只列它引用的文件，本身不是一次测量）、authority=人事年龄（机器多久没写心跳，时间量不是价格日））——它们本来就不量某一天，催它们补日期是催不动的事。这 50 节里，34 节的产物有同名链腿在守；4 节（cash_handshake, cash_ladder, cash_money, cash_yield）是这一页每次生成时自己重算的，停的正是它读的那块面板的最后一天：data/repo_daily/GC001.csv（update_repo.py / bm-a · T-88 车道，本机只读，末行 2026-11-13）、data/repo_daily（update_repo.py / bm-a · T-88 车道，本机只读，末行 2026-11-13）——落后的是那块面板，不是没人重跑这节；`data/repo_daily` 末行 2026-11-13；最后写入 62.6 h 前；属主 bm-a（update_repo.py） 自己的心跳停在 65.7 h 前——是那条车道停了，不是页面慢；`data/repo_daily/GC001.csv` 末行 2026-11-13；最后写入 62.6 h 前；属主 bm-a（update_repo.py） 自己的心跳停在 65.7 h 前——是那条车道停了，不是页面慢；12 节（bets, carry_regime, derisk, fill, forward, futures_hedge）没有任何一条链腿重跑过它们——那是这一页真正的缺口；另外 1 节 sample_window（2020-01-01 至 2026-11-13） 讲的是一整段固定窗口，它印的日期就是那段窗口自己的终点，不是某一根 bar 没跟上——要它站到页头那根 bar 上，等于把整段窗口重新定价一遍；其中 2 节自己就带着两根以上的日期（backtest_band：2026-11-13/2026-11-16、fleet：2026-10-30/2026-11-13/2026-11-16）——它们不是「没写日期」，是写了两天的数，本面不替它们挑一天。

页面逐节 bar：头部声明 **2026-11-16**，63 个带日期的节里 **13** 节在这一天，其余 50 节在别的 bar 上。

| 节 | 它停在哪根 bar | 落后（交易日） | 守它的链腿 |
|---|---|---|---|
| band_ruler | 2026-11-13 | 1 | etf_book_band_ruler |
| bets | 2026-11-13 | 1 | **没有** |
| capital | 2026-11-13 | 1 | etf_book_min_capital |
| carry_regime | 2026-11-13 | 1 | **没有** |
| cash_caliber | 2026-11-13 | 1 | etf_book_cash_caliber_band |
| cash_handshake | 2026-11-13 | 1 | 页内重算（data/repo_daily/GC001.csv 末行 2026-11-13） |
| cash_ladder | 2026-11-13 | 1 | 页内重算（data/repo_daily 末行 2026-11-13） |
| cash_money | 2026-11-13 | 1 | 页内重算（data/repo_daily/GC001.csv 末行 2026-11-13） |
| cash_yield | 2026-11-13 | 1 | 页内重算（data/repo_daily/GC001.csv 末行 2026-11-13） |
| causal_rebuild | 2026-11-13 | 1 | etf_book_causal_rebuild |
| concentration | 2026-11-13 | 1 | concentration_levers、etf_book_concentration |
| cost_tape | 2026-11-13 | 1 | etf_book_cost_tape |
| …其余 38 节 | | | |

「守它的链腿」是按名字匹配的链清单（腿名含该节的名字或产物名），只回答「有没有一条腿会重跑它」，不回答那条腿上次过没过——这两件事在页面上一向是两个错。标着「页内重算」的节不是没腿跑：这一页每次生成都把它们算一遍，它们停在那天是因为下面那块面板只到那天，动作在上游数据车道，不在本页。标着「窗口段」的节也不是没更新：它本来就是按一整段固定窗口量的，印的那个日期是窗口的终点，要它跟上页头只能把整段窗口重算一遍（那是引擎的活，不是链腿的活）。印「没有」的那几节，才是这一页真正的缺口。

这 4 节没有任何日期字段，本面**不替它们认领**任何一根 bar：backtest_band, sources, authority, fleet。

其中 2 节按设计就不该有 bar（sources、authority）——它们不是测量：
- sources：指针块（只列它引用的文件，本身不是一次测量）
- authority：人事年龄（机器多久没写心跳，时间量不是价格日）

其中 2 节其实写了两根以上的日期——本面不挑，把两天的出处照抄在这里：backtest_band（5 名·可执行单口径（本单这份账）.priced_bar=2026-11-13、5 名·beta 覆盖.priced_bar=2026-11-16、12 名·8% 波动目标（生产卡片口径）.priced_bar=2026-11-16）；fleet（board_ts=2026-11-16、rows[0].last_seen=2026-11-13、rows[1].last_seen=2026-10-30、rows[2].last_seen=2026-11-16）。
