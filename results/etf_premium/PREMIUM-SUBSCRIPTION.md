# Premium vs the fund's own purchase channel -- 2026-11-10

**Answer (derived):** 5/5 legs show no open primary subscription anywhere in coverage; hard-suspended on their latest stamp: 513100; exchange-only on their latest stamp: 159501, 513690, 159577, 159263; the 830 hard-suspended sessions are 141 runs (116 of them a single NAV row); 513100's gap sits in its single 435-session run (own gap +4.28) while its other 47 runs read +0.06; the single-row runs are not spread over the calendar: Tue carries 51% of them against 20% of priced sessions (chance 3e-13), so a one-row word is a word printed that session, not a fund policy; what those one-row words are is a valuation gap, not an announcement: 116/116 of them suspend 赎回 on the same row, they move the NAV by 0.10 of a normal session (median), and 89/116 sit on a session the NYSE calendar explains against 3.0% of ordinary sessions (25.5x); closed channel is consistent with a standing premium, not a verdict on it

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

Read this block as **when**, never as **why**: a source that refreshes its
status word on a weekly rhythm and a fund that announces one-day suspensions
both produce a clump on one weekday, and a count of weekdays cannot separate
them. The next section does, but not from these counts -- from the row itself.

## What the one-row words are: a valuation gap, not an announcement

The weekday block above refuses to name a cause, and on its own counts that
refusal is right. The row itself carries three things a weekday count cannot see:
a distribution or a split moves the unit NAV, an announcement suspends
*subscription*, and a fund-specific decision cannot fall on the same date for two
independently managed legs. All three are measured below, plus a published foreign
closure calendar (NYSE closures, rule-derived: New Year, MLK, Presidents, Good Friday, Memorial, Juneteenth (from 2022), Independence, Labor, Thanksgiving, Christmas -- plus the three scheduled 13:00 early closes).

| leg | one-row runs | 赎回 also suspended | NAV unchanged exactly | median |dNAV| vs a normal session | share <= quarter | closure in the gap (full/early) | unmatched | closure rate | ordinary-session rate | lift | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 159501 | 29 | 29 | 1 | 0.065 | 93% | 28/0 | 1 | 97% | 1.6% | 59.0x | CALENDAR_GAP |
| 513100 | 43 | 43 | 9 | 0.144 | 72% | 41/0 | 2 | 95% | 2.6% | 36.9x | CALENDAR_GAP |
| 513690 | 24 | 24 | 0 | 0.127 | 58% | 1/0 | 23 | 4% | 4.8% | 0.9x | CALENDAR_GAP |
| 159577 | 20 | 20 | 1 | 0.041 | 100% | 19/0 | 1 | 95% | 1.9% | 50.4x | CALENDAR_GAP |
| 159263 | 0 | 0 | 0 | n/a | 0% | 0/0 | 0 | n/a | 4.0% | n/a | NO_ONE_ROW_RUNS |

**Pooled:** 116 one-row runs of 141 blocked runs. **116/116 suspend 赎回 on the very same row** -- an announcement that closes subscription does not close redemption, and this one always does. They move the NAV by **0.10 of the leg's own median move** (median over legs; 79% of the runs sit at a quarter or less) and 11 carry the previous NAV exactly, so a distribution is not what these rows are: the largest move on any of them is 80.4911% at 2022-01-13 and the 90th percentile is 0.8458%. **89/116 land on a session whose gap contains an NYSE closure** (full 89, early 0) against **3.0% of ordinary sessions** -- 25.5x.

**Two calendars in hand, and only one is derived from rules.** The US list is rule-built; the Hong Kong list is *measured* on the HSI series (no bar = Hong Kong did not trade; turnover under a share of its own trailing-20 median = a half day with no closing valuation), because HKEX follows the lunar calendar and also shuts for typhoons, which no rule set predicts. A calendar is named only when it explains at least 60% of these runs at 3.0x the ordinary-session rate and beats the other by 10pp.

| calendar | how it is known | runs it explains | rate | ordinary-session rate | lift | named |
|---|---|---|---|---|---|---|
| NYSE | rule list, window (prev_stamp, stamp] | 89/116 | 77% | 3.0% | 25.5x | yes |
| HKEX | measured on HSI (no bar / half day / shut weekday in the gap) | 45/116 | 39% | 5.7% | 6.9x | no |

HKEX series used here: **3255 sessions, 2013-08-20..2026-11-10** (read: cache). The half-day cutoff is a ruler, so the Hong Kong reading is printed at three of them -- 44/116 runs at 50% of trailing turnover, 45 at 60%, 49 at 70% -- and the page quotes no single one as the answer.

**Named per leg:** HKEX explains 513690; NYSE explains 159501, 513100, 159577. The pool word above is a different question from these: it asks which calendar explains most of the 116 runs, not which one explains a given leg.

The strongest evidence is the overlap: 159501 and 159577 print a one-row word on **20 of the same dates** (29 and 20 runs, 2024-03-29..2026-09-07). A fund can suspend itself; it cannot do it in agreement with a competitor -- a shared foreign holiday can.

### What this changes in the reading

The day counts above are not 141 independent suspensions. 25 of them are multi-row runs -- the fund really did keep the channel shut -- and 116 are the single-row valuation gaps measured here. A session that could not be valued has no fresh NAV to price a premium against, so those rows belong to the calendar and not to the fund's policy.

The verdict word is derived from the counts in this table, not written by hand:
it needs both channels to flip, the NAV to move a fraction of a normal session,
and a majority of the dates to fall inside a published closure. Where the last
condition fails, the leg is labelled GAP_WITH_UNKNOWN_CALENDAR instead of being given a cause it has not earned.

Not claimed: a one-off exchange closure nobody can derive from a rule set (the
2025-01-09 US national day of mourning is the one that appears in this sample)
shows up as unmatched, and the page leaves it unmatched. The calendar explains
the dates; it says nothing about quotas, and nothing about whether a 10%
premium is fair.

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
