# Premium vs the fund's own purchase channel -- 2026-11-12

**Answer (derived):** 5/5 legs show no open primary subscription anywhere in coverage; exchange-only on their latest stamp: 510760, 512040, 159655, 513690, 159519; the 186 hard-suspended sessions are 99 runs (74 of them a single NAV row); with the 74 one-row valuation gaps removed the block still sits wider on 159655, 159519 and not on 513690; 510760 has no real suspension left at all; 159655's gap sits in its single 58-session run (own gap +1.00) while its other 33 runs read +0.39; 159519's gap sits in its single 3-session run (own gap +2.58) while its other 21 runs read -0.02; the single-row runs are not spread over the calendar: Tue carries 43% of them against 20% of priced sessions (chance 6e-06), so a one-row word is a word printed that session, not a fund policy; what those one-row words are is a valuation gap, not an announcement: 74/74 of them suspend 赎回 on the same row, they move the NAV by 0.16 of a normal session (median), and 45/74 sit on a session the HKEX calendar explains against 5.9% of ordinary sessions (10.2x); closed channel is consistent with a standing premium, not a verdict on it

**Session (derived):** premiums priced on 2026-11-12 against a ticket of 2026-11-12 -- every leg prices the ticket's own session; the price/IOPV column comes from the 2026-11-12 board face (ticket_session)

Ruler: panel close / the newest unit NAV stamped strictly before that close - 1. Status joined on: 申购状态 printed on the NAV stamp the premium used.

| leg | class | amount CNY | premium (NAV ruler) | board (price/IOPV) | ruler gap pp | priced session | stamp | 申购状态 on stamp | hard-suspended sessions | premium>=10% sessions | share closed at high | window verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 510760 | equity | 86,377 | -0.77% | -0.21% | -0.56 | 2026-11-12 | 2026-11-11 | 场内买入 | 1 | 1 | 100% | CHANNEL_CLOSED_THROUGHOUT |
| 512040 | equity | 86,414 | -0.94% | -0.01% | -0.93 | 2026-11-12 | 2026-11-11 | 场内买入 | 0 | 0 | n/a | CHANNEL_CLOSED_THROUGHOUT |
| 159655 | crossborder | 86,357 | +8.01% | +7.80% | +0.20 | 2026-11-12 | 2026-11-11 | 场内买入 | 91 | 11 | 100% | CHANNEL_CLOSED_THROUGHOUT |
| 513690 | crossborder | 86,325 | -1.04% | -1.03% | -0.01 | 2026-11-12 | 2026-11-11 | 场内买入 | 64 | 0 | n/a | CHANNEL_CLOSED_THROUGHOUT |
| 159519 | crossborder | 86,403 | -1.57% | -1.16% | -0.41 | 2026-11-12 | 2026-11-11 | 场内买入 | 30 | 0 | n/a | CHANNEL_CLOSED_THROUGHOUT |

## Within-leg contrast: hard-suspended vs exchange-only

| leg | verdict | median premium, 暂停申购 | median premium, 场内买入 | gap pp | n |
|---|---|---|---|---|---|
| 510760 | NO_CONTRAST | +1.19% | +0.05% | n/a | 1 / 1494 |
| 512040 | NO_CONTRAST | n/a | +0.02% | n/a | 0 / 1905 |
| 159655 | BLOCK_DOES_NOT_WIDEN | +1.91% | +0.92% | +0.98 | 91 / 892 |
| 513690 | BLOCK_DOES_NOT_WIDEN | +0.50% | -0.02% | +0.52 | 64 / 1266 |
| 159519 | BLOCK_DOES_NOT_WIDEN | +0.50% | +0.23% | +0.27 | 30 / 743 |

### The same contrast with the valuation gaps removed

The one-row 暂停申购 words are a shut overseas market, not a fund decision (see
"What the one-row words are" below). Those sessions carry no fresh NAV, so their
premium is priced against a stale one. Repricing the block without them asks the
question the table above cannot: is the premium wider on the sessions the fund
itself chose to shut, or was the wider reading the calendar all along?

| leg | verdict | median premium, 暂停申购 | median premium, 场内买入 | gap pp | n kept | rows dropped |
|---|---|---|---|---|---|---|
| 510760 | NO_CONTRAST | n/a | +0.05% | n/a | 0 | 1 |
| 512040 | NO_CONTRAST | n/a | +0.02% | n/a | 0 | 0 |
| 159655 | BLOCK_WIDENS_PREMIUM | +1.93% | +0.92% | +1.00 | 58 | 33 |
| 513690 | BLOCK_DOES_NOT_WIDEN | +0.62% | -0.02% | +0.64 | 40 | 24 |
| 159519 | BLOCK_WIDENS_PREMIUM | +1.40% | +0.23% | +1.17 | 14 | 16 |

'rows dropped' is the count of priced 暂停申购 rows whose NAV stamp is one of the
single-row runs named in the cause section. The exchange-only column is untouched:
the same baseline prices both readings, so the only thing that moves is the block.

On 510760 every hard-suspended session was a single-row valuation gap, so 'n kept' is zero: the day-level contrast on that leg was pricing the calendar, not the fund, and this table is the one that says so.

## Days vs runs: how much evidence the block count actually is

A suspension lasts as long as the fund keeps it, so the days inside one run are
the same fact repeated. The table above counts days; this one counts runs.

| leg | runs (all words) | blocked runs | runs of a single NAV row | median rows per block | longest block | run-level gap vs exchange-only | longest run's own gap | gap with the longest run dropped | verdict |
|---|---|---|---|---|---|---|---|---|---|
| 510760 | 3 | 1 | 1 | 1 | 1 (2024-08-15..2024-08-15) | +1.14 | +1.14 | n/a | TOO_FEW_EPISODES |
| 512040 | 1 | 0 | 0 | n/a | 0 (n/a..n/a) | n/a | n/a | n/a | NO_BLOCKED_EPISODES |
| 159655 | 69 | 34 | 33 | 1 | 58 (2024-03-07..2024-06-03) | +0.70 | +1.00 | +0.39 | EPISODE_GAP_DOES_NOT_WIDEN |
| 513690 | 85 | 42 | 24 | 1 | 3 (2021-09-17..2021-09-23) | +0.17 | -0.68 | +0.20 | EPISODE_GAP_DOES_NOT_WIDEN |
| 159519 | 45 | 22 | 16 | 1 | 3 (2024-12-25..2024-12-27) | +0.25 | +2.58 | -0.02 | EPISODE_GAP_DOES_NOT_WIDEN |

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
| 510760 | 暂停申购 | 2024-08-15 | 2024-08-15 | 1 | +1.19% |
| 512040 | (never suspended in coverage) | | | | |
| 159655 | 暂停申购 | 2024-03-07 | 2024-06-03 | 58 | +1.93% |
| 159655 | 暂停申购 | 2022-11-25 | 2022-11-25 | 1 | +0.22% |
| 159655 | 暂停申购 | 2022-12-27 | 2022-12-27 | 1 | +0.79% |
| 159655 | 暂停申购 | 2023-01-17 | 2023-01-17 | 1 | +0.23% |
| 159655 | 暂停申购 | 2023-02-21 | 2023-02-21 | 1 | -0.52% |
| 159655 | 暂停申购 | 2023-04-10 | 2023-04-10 | 1 | -0.50% |
| 159655 | 暂停申购 | 2023-05-30 | 2023-05-30 | 1 | +0.22% |
| 159655 | 暂停申购 | 2023-06-20 | 2023-06-20 | 1 | +0.26% |
| 513690 | 暂停申购 | 2021-09-17 | 2021-09-23 | 3 | -0.70% |
| 513690 | 暂停申购 | 2021-12-30 | 2022-01-04 | 3 | +0.74% |
| 513690 | 暂停申购 | 2024-12-25 | 2024-12-27 | 3 | +2.35% |
| 513690 | 暂停申购 | 2025-12-25 | 2025-12-29 | 3 | -1.25% |
| 513690 | 暂停申购 | 2021-09-30 | 2021-10-08 | 2 | +0.02% |
| 513690 | 暂停申购 | 2021-10-14 | 2021-10-15 | 2 | -0.12% |
| 513690 | 暂停申购 | 2022-01-28 | 2022-02-07 | 2 | +1.92% |
| 513690 | 暂停申购 | 2022-04-01 | 2022-04-06 | 2 | +1.93% |
| 159519 | 暂停申购 | 2024-12-25 | 2024-12-27 | 3 | +2.81% |
| 159519 | 暂停申购 | 2025-12-25 | 2025-12-29 | 3 | -0.75% |
| 159519 | 暂停申购 | 2023-12-26 | 2023-12-27 | 2 | +1.24% |
| 159519 | 暂停申购 | 2024-04-01 | 2024-04-02 | 2 | +3.03% |
| 159519 | 暂停申购 | 2025-04-21 | 2025-04-22 | 2 | +1.40% |
| 159519 | 暂停申购 | 2026-04-07 | 2026-04-08 | 2 | -0.20% |
| 159519 | 暂停申购 | 2023-09-04 | 2023-09-04 | 1 | +3.32% |
| 159519 | 暂停申购 | 2023-09-11 | 2023-09-11 | 1 | -0.33% |

## Why the blips: when the word is printed, not why

A single-row 暂停申购 run is one word printed between two exchange-only rows.
The run table above counts them; this one asks whether those days are ordinary
sessions. If they were, their weekday mix would look like the session mix. It
does not.

| leg | one-row runs | busiest weekday | share of runs on it | its share of sessions | chance of that (1-sided) | bracketed by 场内买入 both sides | runs with a NAV jump >3% | day-of-month peaks | verdict |
|---|---|---|---|---|---|---|---|---|---|
| 510760 | 1 | Thu | 100% | 20% | 0.2 | 1 | 1 | 15(1) | TOO_FEW_BLIPS |
| 512040 | 0 | n/a | n/a | n/a | n/a | 0 | 0 | n/a | TOO_FEW_BLIPS |
| 159655 | 33 | Tue | 55% | 20% | 1.5e-05 | 33 | 0 | 20(5), 26(4), 5(3) | BLIP_WEEKDAY_CADENCE |
| 513690 | 24 | Tue | 38% | 20% | 0.038 | 24 | 0 | 2(5), 4(2), 10(2) | BLIP_NO_CADENCE |
| 159519 | 16 | Mon | 31% | 20% | 0.19 | 16 | 0 | 2(4), 4(1), 5(1) | BLIP_NO_CADENCE |

**Pooled:** 74 single-row runs out of 99 blocked runs; **Tue carries 43% of them against 20% of all priced sessions** (one-sided chance 6e-06). Peak days of the month: 2(9), 20(5), 5(4). 74 of the runs are bracketed by 场内买入 on both sides, and 1 carry a NAV jump larger than 3% -- a split or a big distribution, not a quota.


Only 1 of 5 legs clear the line on their own (159655); the rest lean the same way with too few runs to call it, which is why the pooled reading above -- not a per-leg one -- is the sentence this section quotes.

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
| 510760 | 1 | 1 | 0 | 9.848 | 0% | 0/0 | 1 | 0% | 4.8% | 0.0x | CAUSE_UNRESOLVED |
| 512040 | 0 | 0 | 0 | n/a | 0% | 0/0 | 0 | n/a | 4.7% | n/a | NO_ONE_ROW_RUNS |
| 159655 | 33 | 33 | 2 | 0.193 | 64% | 32/0 | 1 | 97% | 1.8% | 54.2x | CALENDAR_GAP |
| 513690 | 24 | 24 | 0 | 0.127 | 58% | 1/0 | 23 | 4% | 4.8% | 0.9x | CALENDAR_GAP |
| 159519 | 16 | 16 | 0 | 0.130 | 69% | 1/0 | 15 | 6% | 4.9% | 1.3x | CALENDAR_GAP |

**Pooled:** 74 one-row runs of 99 blocked runs. **74/74 suspend 赎回 on the very same row** -- an announcement that closes subscription does not close redemption, and this one always does. They move the NAV by **0.16 of the leg's own median move** (median over legs; 62% of the runs sit at a quarter or less) and 2 carry the previous NAV exactly, so a distribution is not what these rows are: the largest move on any of them is 5.0722% at 2024-08-14 and the 90th percentile is 5.0722%. **34/74 land on a session whose gap contains an NYSE closure** (full 34, early 0) against **4.3% of ordinary sessions** -- 10.7x.

**Two calendars in hand, and only one is derived from rules.** The US list is rule-built; the Hong Kong list is *measured* on the HSI series (no bar = Hong Kong did not trade; turnover under a share of its own trailing-20 median = a half day with no closing valuation), because HKEX follows the lunar calendar and also shuts for typhoons, which no rule set predicts. A calendar is named only when it explains at least 60% of these runs at 3.0x the ordinary-session rate and beats the other by 10pp.

| calendar | how it is known | runs it explains | rate | ordinary-session rate | lift | named |
|---|---|---|---|---|---|---|
| NYSE | rule list, window (prev_stamp, stamp] | 34/74 | 46% | 4.3% | 10.7x | no |
| HKEX | measured on HSI (no bar / half day / shut weekday in the gap) | 45/74 | 61% | 5.9% | 10.2x | yes |

HKEX series used here: **3257 sessions, 2013-08-20..2026-11-12** (read: fetched). The half-day cutoff is a ruler, so the Hong Kong reading is printed at three of them -- 43/74 runs at 50% of trailing turnover, 45 at 60%, 49 at 70% -- and the page quotes no single one as the answer.

**Named per leg:** HKEX explains 513690, 159519; NYSE explains 159655; left unnamed: 510760. The pool word above is a different question from these: it asks which calendar explains most of the 116 runs, not which one explains a given leg.

The strongest evidence is the overlap: 159519 and 513690 print a one-row word on **16 of the same dates** (16 and 24 runs, 2023-09-01..2026-10-19). A fund can suspend itself; it cannot do it in agreement with a competitor -- a shared foreign holiday can.

### What this changes in the reading

The day counts above are not 141 independent suspensions. 25 of them are multi-row runs -- the fund really did keep the channel shut -- and 74 are the single-row valuation gaps measured here. A session that could not be valued has no fresh NAV to price a premium against, so those rows belong to the calendar and not to the fund's policy.

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
