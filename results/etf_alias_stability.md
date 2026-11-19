# 异名同篮：把判词放到前几个年度窗上重问一遍

证据 cutoff `2026-11-19`（盘口 session 2026-11-19）。今日窗 2025-11-10..2026-11-19（250 个交易日）。

## 一句话

这张盘口有 741 对异名同篮；把同样两道门放到前 4 个年度窗上重问一遍，每窗只留下（T-1y 56.8%、T-2y 57.0%、T-3y 54.4%、T-4y 55.3%），能数到的 470 对里 122 对每窗都过（26.0%），348 对被某一窗拒过（日级 24 对 / 年级 339 对），271 对历史不够没法问——判词 WINDOW_LUCK。把每个历史窗当独立抽样，每窗 56.1% 的通过率下这些对应该活下来 126.1 对，实测 122 对——所以这不是「某些对不稳」而是这道年级线落在刀口上。过 0.50pp 物质线的 7 组一共 6,330 元的选择成本，其中每一对都过所有窗的只有 2,569 元。

## 逐窗读数

| 窗 | 区间 | 屏幕内票数 | 可数对数 | 判同篮 | 日级拒 | 年级拒 | 无史 | 通过率 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| T | 2025-11-10..2026-11-19 | 543 | — | — | — | — | — | — |
| T-1y | 2024-10-30..2025-11-07 | 414 | — | — | — | — | — | — |
| T-2y | 2023-10-18..2024-10-29 | 346 | — | — | — | — | — | — |
| T-3y | 2022-09-30..2023-10-17 | 279 | — | — | — | — | — | — |
| T-4y | 2021-09-17..2022-09-29 | 215 | — | — | — | — | — | — |

（今日窗一行只报屏幕规模；重问结果即下表。）

| 历史窗 | 可数 | 判同篮 | 日级拒 | 年级拒 | 无史 | 通过率 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| T-1y | 470 | 267 | 4 | 199 | 271 | 56.8% |
| T-2y | 342 | 195 | 11 | 136 | 399 | 57.0% |
| T-3y | 270 | 147 | 11 | 112 | 471 | 54.4% |
| T-4y | 190 | 105 | 6 | 79 | 551 | 55.3% |

**判词：WINDOW_LUCK**（今日接受 741 对；能数到 470 对，其中每窗都过 122 对＝26.0%，被拒 348 对，历史不够 271 对）。

## 同一个通过率，不同的考试次数

只有一年历史可问的对只需过一次门，有四年历史的对要过四次。把两者算进同一个百分比，读起来就像「四分之三的对不稳」。

| 有几个历史窗可数 | 对数 | 每窗都过 | 通过率 |
| ---: | ---: | ---: | ---: |
| 1 | 120 | 38 | 31.7% |
| 2 | 78 | 19 | 24.4% |
| 3 | 92 | 21 | 22.8% |
| 4 | 180 | 44 | 24.4% |

每个历史窗单独看，通过率 56.1%；把每窗当独立抽样，这些对里应该活下来 126.1 对，实测 122 对。

## 过物质线的族，按「每一对是否每窗都过」分

| 族 | 成员数 | 一手最贵比最便宜 | 对数 | 每窗都过 |
| --- | ---: | ---: | ---: | ---: |
| 2000E/中证2000/中证2000ETF | 3 | 2,497 | 3 | 0（有翻转） |
| HK消费/港股通消费ETF | 2 | 845 | 1 | 1 |
| 港股央企红利ETF景顺/港股通红利ETF | 2 | 663 | 1 | 0（有翻转） |
| 港股科技ETF/港股通恒生科技ETF | 2 | 628 | 1 | 1 |
| 地产ETF/地产龙头 | 2 | 600 | 1 | 0（有翻转） |
| 港科ETF/港科技30 | 2 | 574 | 1 | 1 |
| 港红利TH/港股通红利ETF | 2 | 523 | 1 | 1 |

物质线以上合计 **6,330 元**；其中每一对都过所有窗的只有 **2,569 元**。

## 限制（照面内 caveats，一条不改写）

- the earlier windows re-ask the SAME two gates of the SAME two tickers; a pair that holds in all of them is stable in price behaviour, not certified as the same asset
- earlier windows carry membership only: premiums exist for one session on this board, so no earlier money number is published (a prior-year cost would be invented)
- the screen is today's: a ticker that only began trading two years ago drops out of the earlier windows by name and is counted as not measurable, never as a hold
- the drift line is still the census's chosen 1.0 pp; this face measures whether the verdicts move, not whether the line is the right one
- windows are disjoint and exactly 250 sessions; the panel's own holiday calendar decides what a session is
