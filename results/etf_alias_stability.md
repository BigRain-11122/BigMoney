# 异名同篮：把判词放到前几个年度窗上重问一遍

证据 cutoff `2026-11-17`（盘口 session 2026-11-17）。今日窗 2025-11-06..2026-11-17（250 个交易日）。

## 一句话

今天这张盘口有 867 对异名同篮；把同样两道门放到前 4 个年度窗上重问一遍，每窗只留下（T-1y 57.2%、T-2y 57.0%、T-3y 54.1%、T-4y 50.9%），能数到的 538 对里 137 对每窗都过（25.5%），401 对被某一窗拒过（日级 35 对 / 年级 394 对），329 对历史不够没法问——判词 WINDOW_LUCK。把每个历史窗当独立抽样，每窗 55.5% 的通过率下这些对应该活下来 139.6 对，实测 137 对——所以这不是「某些对不稳」而是这道年级线落在刀口上。过 0.50pp 物质线的 2 组一共 1,311 元的选择成本，其中每一对都过所有窗的只有 694 元。

## 逐窗读数

| 窗 | 区间 | 屏幕内票数 | 可数对数 | 判同篮 | 日级拒 | 年级拒 | 无史 | 通过率 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| T | 2025-11-06..2026-11-17 | 581 | — | — | — | — | — | — |
| T-1y | 2024-10-28..2025-11-05 | 441 | — | — | — | — | — | — |
| T-2y | 2023-10-16..2024-10-25 | 366 | — | — | — | — | — | — |
| T-3y | 2022-09-28..2023-10-13 | 295 | — | — | — | — | — | — |
| T-4y | 2021-09-15..2022-09-27 | 226 | — | — | — | — | — | — |

（今日窗一行只报屏幕规模；重问结果即下表。）

| 历史窗 | 可数 | 判同篮 | 日级拒 | 年级拒 | 无史 | 通过率 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| T-1y | 538 | 308 | 8 | 222 | 329 | 57.2% |
| T-2y | 388 | 221 | 16 | 151 | 479 | 57.0% |
| T-3y | 320 | 173 | 15 | 132 | 547 | 54.1% |
| T-4y | 226 | 115 | 11 | 100 | 641 | 50.9% |

**判词：WINDOW_LUCK**（今日接受 867 对；能数到 538 对，其中每窗都过 137 对＝25.5%，被拒 401 对，历史不够 329 对）。

## 同一个通过率，不同的考试次数

只有一年历史可问的对只需过一次门，有四年历史的对要过四次。把两者算进同一个百分比，读起来就像「四分之三的对不稳」。

| 有几个历史窗可数 | 对数 | 每窗都过 | 通过率 |
| ---: | ---: | ---: | ---: |
| 1 | 139 | 46 | 33.1% |
| 2 | 75 | 17 | 22.7% |
| 3 | 113 | 24 | 21.2% |
| 4 | 211 | 50 | 23.7% |

每个历史窗单独看，通过率 55.5%；把每窗当独立抽样，这些对里应该活下来 139.6 对，实测 137 对。

## 过物质线的族，按「每一对是否每窗都过」分

| 族 | 成员数 | 一手最贵比最便宜 | 对数 | 每窗都过 |
| --- | ---: | ---: | ---: | ---: |
| 半导体ETF/芯片ETF | 2 | 694 | 1 | 1 |
| 中概互联ETF/中概互联网ETF | 2 | 617 | 1 | 0（有翻转） |

物质线以上合计 **1,311 元**；其中每一对都过所有窗的只有 **694 元**。

## 限制（照面内 caveats，一条不改写）

- the earlier windows re-ask the SAME two gates of the SAME two tickers; a pair that holds in all of them is stable in price behaviour, not certified as the same asset
- earlier windows carry membership only: premiums exist for one session on this board, so no earlier money number is published (a prior-year cost would be invented)
- the screen is today's: a ticker that only began trading two years ago drops out of the earlier windows by name and is counted as not measurable, never as a hold
- the drift line is still the census's chosen 1.0 pp; this face measures whether the verdicts move, not whether the line is the right one
- windows are disjoint and exactly 250 sessions; the panel's own holiday calendar decides what a session is
