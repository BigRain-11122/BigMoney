# CEO 页面：这一页是哪一天的（r1533）

*由 `scripts/live_book_section_bars.py` 生成；判据见文件头。*

页面头部写着按 2026-11-17 定价，但 67 个带日期的节里只有 43 节真在这一天；其余 24 节不在这一天（最旧停在 2026-11-13（最差 cash_caliber 落后 2 个交易日）），另外 3 节根本没有日期——它们不是同一根 bar 上的数，读的时候不能互相加减。2 节按设计没有 bar（sources=指针块（只列它引用的文件，本身不是一次测量）、authority=人事年龄（机器多久没写心跳，时间量不是价格日））——它们本来就不量某一天，催它们补日期是催不动的事。这 24 节里，14 节的产物有同名链腿在守；4 节（cash_handshake, cash_ladder, cash_money, cash_yield）是这一页每次生成时自己重算的，停的正是它读的那块面板的最后一天：data/repo_daily/GC001.csv（update_repo.py / bm-a · T-88 车道，本机只读，末行 2026-11-13）、data/repo_daily（update_repo.py / bm-a · T-88 车道，本机只读，末行 2026-11-13）——落后的是那块面板，不是没人重跑这节；`data/repo_daily` 末行 2026-11-13；最后写入 0.6 h 前；属主 bm-a 的心跳还在（0.4 h 前）——车道活着，只是这块面板还没推进到页头那根 bar；`data/repo_daily/GC001.csv` 末行 2026-11-13；最后写入 0.6 h 前；属主 bm-a 的心跳还在（0.4 h 前）——车道活着，只是这块面板还没推进到页头那根 bar；6 节（derisk, futures_hedge, futures_hedge_tail, futures_ladder, futures_sleeve, k_gap）没有任何一条链腿重跑过它们——那是这一页真正的缺口；其中 1 节自己就带着两根以上的日期（fleet：2026-10-30/2026-11-16/2026-11-17）——它们不是「没写日期」，是写了两天的数，本面不替它们挑一天。

页面逐节 bar：头部声明 **2026-11-17**，67 个带日期的节里 **43** 节在这一天，其余 24 节在别的 bar 上。

| 节 | 它停在哪根 bar | 落后（交易日） | 守它的链腿 |
|---|---|---|---|
| cash_caliber | 2026-11-13 | 2 | etf_book_cash_caliber_band |
| cash_handshake | 2026-11-13 | 2 | 页内重算（data/repo_daily/GC001.csv 末行 2026-11-13） |
| cash_ladder | 2026-11-13 | 2 | 页内重算（data/repo_daily 末行 2026-11-13） |
| cash_money | 2026-11-13 | 2 | 页内重算（data/repo_daily/GC001.csv 末行 2026-11-13） |
| cash_yield | 2026-11-13 | 2 | 页内重算（data/repo_daily/GC001.csv 末行 2026-11-13） |
| lookahead | 2026-11-13 | 2 | etf_book_lookahead、etf_book_lookahead_write |
| cost_tape | 2026-11-16 | 1 | etf_book_cost_tape |
| derisk | 2026-11-16 | 1 | **没有** |
| do_or_wait | 2026-11-16 | 1 | do_or_wait |
| family_coherence | 2026-11-16 | 1 | etf_book_phase_atlas_arms |
| floor_provenance | 2026-11-16 | 1 | floor_provenance、floor_provenance_write |
| futures_hedge | 2026-11-16 | 1 | **没有** |
| …其余 12 节 | | | |

「守它的链腿」是按名字匹配的链清单（腿名含该节的名字或产物名），只回答「有没有一条腿会重跑它」，不回答那条腿上次过没过——这两件事在页面上一向是两个错。标着「页内重算」的节不是没腿跑：这一页每次生成都把它们算一遍，它们停在那天是因为下面那块面板只到那天，动作在上游数据车道，不在本页。标着「窗口段」的节也不是没更新：它本来就是按一整段固定窗口量的，印的那个日期是窗口的终点，要它跟上页头只能把整段窗口重算一遍（那是引擎的活，不是链腿的活）。印「没有」的那几节，才是这一页真正的缺口。

这 3 节没有任何日期字段，本面**不替它们认领**任何一根 bar：sources, authority, fleet。

其中 2 节按设计就不该有 bar（sources、authority）——它们不是测量：
- sources：指针块（只列它引用的文件，本身不是一次测量）
- authority：人事年龄（机器多久没写心跳，时间量不是价格日）

其中 1 节其实写了两根以上的日期——本面不挑，把两天的出处照抄在这里：fleet（board_ts=2026-11-17、rows[0].last_seen=2026-11-16、rows[1].last_seen=2026-10-30、rows[2].last_seen=2026-11-17）。
