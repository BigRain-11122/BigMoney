# Premium vs the fund's own purchase channel -- 2026-11-10

**Answer (derived):** 5/5 legs show no open primary subscription anywhere in coverage; hard-suspended on their latest stamp: 513100; exchange-only on their latest stamp: 159501, 513690, 159577, 159263; the 830 hard-suspended sessions are 141 runs (116 of them a single NAV row); 513100's gap sits in its single 435-session run (own gap +4.28) while its other 47 runs read +0.06; the single-row runs are not spread over the calendar: Tue carries 51% of them against 20% of priced sessions (chance 3e-13), so a one-row word is a word printed that session, not a fund policy; closed channel is consistent with a standing premium, not a verdict on it

Ruler: panel close / the newest unit NAV stamped strictly before that close - 1. Status joined on: 申购状态 printed on the NAV stamp the premium used.

| leg | class | amount CNY | premium (NAV ruler) | board (price/IOPV) | ruler gap pp | stamp | 申购状态 on stamp | hard-suspended sessions | premium>=10% sessions | share closed at high | window verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 159501 | crossborder | 78,501 | +24.40% | +20.29% | +4.11 | 2026-11-06 | 场内买入 | 29 | 82 | 100% | CHANNEL_CLOSED_THROUGHOUT |
| 513100 | crossborder | 78,611 | +22.40% | +18.30% | +4.10 | 2026-11-06 | 暂停申购 | 679 | 163 | 100% | CHANNEL_CLOSED_THROUGHOUT |
| 513690 | crossborder | 78,588 | -0.78% | +0.12% | -0.90 | 2026-11-09 | 场内买入 | 64 | 0 | n/a | CHANNEL_CLOSED_THROUGHOUT |
| 159577 | crossborder | 78,504 | +12.07% | +9.48% | +2.59 | 2026-11-06 | 场内买入 | 58 | 2 | 100% | CHANNEL_CLOSED_THROUGHOUT |
| 159263 | equity | 78,522 | -0.54% | -0.14% | -0.39 | 2026-11-09 | 场内买入 | 0 | 0 | n/a | CHANNEL_CLOSED_THROUGHOUT |

## Within-leg contrast: hard-suspended vs exchange-only

| leg | verdict | median premium, 暂停申购 | median premium, 场内买入 | gap pp | n |
|---|---|---|---|---|---|
| 159501 | BLOCK_DOES_NOT_WIDEN | +1.50% | +1.28% | +0.22 | 29 / 796 |
| 513100 | BLOCK_WIDENS_PREMIUM | +5.04% | +0.54% | +4.50 | 679 / 1223 |
| 513690 | BLOCK_DOES_NOT_WIDEN | +0.50% | -0.02% | +0.52 | 64 / 1264 |
| 159577 | BLOCK_DOES_NOT_WIDEN | +1.18% | +1.79% | -0.60 | 58 / 600 |
| 159263 | NO_CONTRAST | n/a | +0.10% | n/a | 0 / 326 |

## Days vs runs: how much evidence the block count actually is

A suspension lasts as long as the fund keeps it, so the days inside one run are
the same fact repeated. The table above counts days; this one counts runs.

| leg | runs (all words) | blocked runs | runs of a single NAV row | median rows per block | longest block | run-level gap vs exchange-only | longest run's own gap | gap with the longest run dropped | verdict |
|---|---|---|---|---|---|---|---|---|---|
| 159501 | 59 | 29 | 29 | 1 | 1 (2023-06-20..2023-06-20) | +0.22 | -1.18 | +0.49 | EPISODE_GAP_DOES_NOT_WIDEN |
| 513100 | 96 | 48 | 43 | 1 | 435 (2024-11-26..2026-09-08) | +0.08 | +4.28 | +0.06 | EPISODE_GAP_DOES_NOT_WIDEN |
| 513690 | 85 | 42 | 24 | 1 | 3 (2021-09-17..2021-09-23) | +0.17 | -0.68 | +0.20 | EPISODE_GAP_DOES_NOT_WIDEN |
| 159577 | 45 | 22 | 20 | 1 | 30 (2025-04-23..2025-06-09) | +0.40 | -1.42 | +0.42 | EPISODE_GAP_DOES_NOT_WIDEN |
| 159263 | 1 | 0 | 0 | n/a | 0 (n/a..n/a) | n/a | n/a | n/a | NO_BLOCKED_EPISODES |

Run-level gap = median over blocked runs of (that run's own median premium - the
leg's exchange-only median), so one long block cannot stand in for hundreds of
sessions. A verdict needs at least five blocked runs; below that the page says
TOO_FEW_EPISODES rather than printing a median of one run as a measurement.

The last two columns are the cheapest honest question about any such gap: does it
survive dropping the single longest block? A gap that lives in one run is one
decision by one fund, and the page says so instead of quoting it as a population.

### The transition days, named

Up to 8 longest blocked runs per leg, with the first and last priced session that
carried the word. Every run in coverage is in the JSON twin (`episode_granularity.runs`),
including the exchange-only ones between them.

| leg | 申购状态 | first priced session carrying it | last | rows | its own median premium |
|---|---|---|---|---|---|
| 159501 | 暂停申购 | 2023-06-20 | 2023-06-20 | 1 | +0.10% |
| 159501 | 暂停申购 | 2023-07-05 | 2023-07-05 | 1 | -0.36% |
| 159501 | 暂停申购 | 2023-09-05 | 2023-09-05 | 1 | -0.13% |
| 159501 | 暂停申购 | 2023-11-24 | 2023-11-24 | 1 | -0.27% |
| 159501 | 暂停申购 | 2023-12-26 | 2023-12-26 | 1 | +0.39% |
| 159501 | 暂停申购 | 2024-01-16 | 2024-01-16 | 1 | -0.32% |
| 159501 | 暂停申购 | 2024-02-20 | 2024-02-20 | 1 | +0.03% |
| 159501 | 暂停申购 | 2024-04-01 | 2024-04-01 | 1 | +0.85% |
| 513100 | 暂停申购 | 2024-11-26 | 2026-09-08 | 435 | +4.82% |
| 513100 | 暂停申购 | 2020-03-30 | 2020-10-23 | 138 | +7.18% |
| 513100 | 暂停申购 | 2020-01-20 | 2020-03-12 | 33 | +9.93% |
| 513100 | 暂停申购 | 2026-10-09 | 2026-11-10 | 23 | +17.06% |
| 513100 | 暂停申购 | 2024-09-24 | 2024-10-09 | 7 | -0.28% |
| 513100 | 暂停申购 | 2019-01-22 | 2019-01-22 | 1 | -0.92% |
| 513100 | 暂停申购 | 2019-02-19 | 2019-02-19 | 1 | -0.04% |
| 513100 | 暂停申购 | 2019-05-28 | 2019-05-28 | 1 | +0.11% |
| 513690 | 暂停申购 | 2021-09-17 | 2021-09-23 | 3 | -0.70% |
| 513690 | 暂停申购 | 2021-12-30 | 2022-01-04 | 3 | +0.74% |
| 513690 | 暂停申购 | 2024-12-25 | 2024-12-27 | 3 | +2.35% |
| 513690 | 暂停申购 | 2025-12-25 | 2025-12-29 | 3 | -1.25% |
| 513690 | 暂停申购 | 2021-09-30 | 2021-10-08 | 2 | +0.02% |
| 513690 | 暂停申购 | 2021-10-14 | 2021-10-15 | 2 | -0.12% |
| 513690 | 暂停申购 | 2022-01-28 | 2022-02-07 | 2 | +1.92% |
| 513690 | 暂停申购 | 2022-04-01 | 2022-04-06 | 2 | +1.93% |
| 159577 | 暂停申购 | 2025-04-23 | 2025-06-09 | 30 | +0.37% |
| 159577 | 暂停申购 | 2025-11-20 | 2025-12-01 | 8 | +7.21% |
| 159577 | 暂停申购 | 2024-04-01 | 2024-04-01 | 1 | +1.96% |
| 159577 | 暂停申购 | 2024-05-28 | 2024-05-28 | 1 | +2.45% |
| 159577 | 暂停申购 | 2024-06-20 | 2024-06-20 | 1 | +2.89% |
| 159577 | 暂停申购 | 2024-07-05 | 2024-07-05 | 1 | +3.86% |
| 159577 | 暂停申购 | 2024-09-03 | 2024-09-03 | 1 | -0.03% |
| 159577 | 暂停申购 | 2024-11-29 | 2024-11-29 | 1 | +1.46% |
| 159263 | (never suspended in coverage) | | | | |

## Why the blips: when the word is printed, not why

A single-row 暂停申购 run is one word printed between two exchange-only rows.
The run table above counts them; this one asks whether those days are ordinary
sessions. If they were, their weekday mix would look like the session mix. It
does not.

| leg | one-row runs | busiest weekday | share of runs on it | its share of sessions | chance of that (1-sided) | bracketed by 场内买入 both sides | runs with a NAV jump >3% | day-of-month peaks | verdict |
|---|---|---|---|---|---|---|---|---|---|
| 159501 | 29 | Tue | 52% | 20% | 0.00018 | 29 | 0 | 20(5), 26(4), 5(3) | BLIP_NO_CADENCE |
| 513100 | 43 | Tue | 60% | 20% | 9.8e-09 | 43 | 1 | 5(5), 26(4), 6(3) | BLIP_WEEKDAY_CADENCE |
| 513690 | 24 | Tue | 38% | 20% | 0.038 | 24 | 0 | 2(5), 4(2), 10(2) | BLIP_NO_CADENCE |
| 159577 | 20 | Tue | 45% | 20% | 0.011 | 20 | 0 | 20(3), 26(3), 7(2) | BLIP_NO_CADENCE |
| 159263 | 0 | n/a | n/a | n/a | n/a | 0 | 0 | n/a | TOO_FEW_BLIPS |

**Pooled:** 116 single-row runs out of 141 blocked runs; **Tue carries 51% of them against 20% of all priced sessions** (one-sided chance 2.6e-13). Peak days of the month: 26(11), 5(8), 20(8). 116 of the runs are bracketed by 场内买入 on both sides, and 1 carry a NAV jump larger than 3% -- a split or a big distribution, not a quota.


Only 1 of 5 legs clear the line on their own (513100); the rest lean the same way with too few runs to call it, which is why the pooled reading above -- not a per-leg one -- is the sentence this section quotes.

Read this as **when**, never as **why**: a source that refreshes its status word
on a weekly rhythm and a fund that announces one-day suspensions both produce a
clump on one weekday, and this data cannot separate them. What it does settle is
the reading of a single-row run: it is a word printed on one session, so it must
not be priced as 'the fund was suspended that day'.

## What this face refuses to claim

* A closed channel is **consistent with** a standing premium; it does not make the
  premium fair, and it is not a sell signal. What it does establish is that the
  creation valve an arbitrageur would need was not listed as open on any session
  this face can see -- so 'the premium should already have been arbitraged away'
  is not an argument this data supports.
* The status word is as published on each NAV row; it is not a statement about
  creation limits, quotas, or how much would be accepted if it reopened.
* A same-session open state would falsify the hypothesis. None appears in coverage:
  the only words present are 场内买入 (exchange-only) and 暂停申购 (suspended).
* 'share closed at high' is a census, not a contrast: on a leg with no hard-suspended
  sessions it reads 100% by construction, because every session is exchange-only.
  The only column that carries a difference is the within-leg contrast above, and
  there it is printed as measured -- 159501 and 159577 come out flat or negative.
* The two premium columns are different quantities and are never added: this face
  divides the panel close by the disclosed unit NAV; the board divides price by
  intraday IOPV. The gap column prices how far apart those rulers sit on one session.
* The day counts in the first table are **not** independent observations. A single
  block of 435 sessions is one decision by the fund, and a run of one NAV row is
  one word printed between two exchange-only rows -- neither is 435 answers or a
  policy. The second table is the same contrast re-read per run; where the two
  disagree, the run-level reading is the one with a defensible count behind it.
