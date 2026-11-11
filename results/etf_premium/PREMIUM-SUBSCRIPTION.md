# Premium vs the fund's own purchase channel -- 2026-11-11

**Answer (derived):** 1/5 legs show no open primary subscription anywhere in coverage; 4 leg(s) carry no status data; exchange-only on their latest stamp: 513690; the 64 hard-suspended sessions are 42 runs (24 of them a single NAV row); with the 24 one-row valuation gaps removed the block still sits wider on no leg and not on 513690; what those one-row words are is a valuation gap, not an announcement: 24/24 of them suspend 赎回 on the same row, they move the NAV by 0.13 of a normal session (median), and 21/24 sit on a session the HKEX calendar explains against 6.3% of ordinary sessions (13.9x); closed channel is consistent with a standing premium, not a verdict on it

Ruler: panel close / the newest unit NAV stamped strictly before that close - 1. Status joined on: 申购状态 printed on the NAV stamp the premium used.

| leg | class | amount CNY | premium (NAV ruler) | board (price/IOPV) | ruler gap pp | stamp | 申购状态 on stamp | hard-suspended sessions | premium>=10% sessions | share closed at high | window verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 510760 | equity | 86,346 | +0.30% | +0.11% | +0.20 | 2026-11-10 | (none) | 0 | 1 | n/a | NO_STATUS_DATA |
| 512040 | equity | 86,376 | -0.60% | -0.02% | -0.58 | 2026-11-10 | (none) | 0 | 0 | n/a | NO_STATUS_DATA |
| 159655 | crossborder | 86,243 | +9.55% | +9.54% | +0.01 | 2026-11-10 | (none) | 0 | 11 | n/a | NO_STATUS_DATA |
| 513690 | crossborder | 86,394 | -1.06% | +0.17% | -1.24 | 2026-11-10 | 场内买入 | 64 | 0 | n/a | CHANNEL_CLOSED_THROUGHOUT |
| 159519 | crossborder | 86,338 | -0.96% | -0.22% | -0.73 | 2026-11-10 | (none) | 0 | 0 | n/a | NO_STATUS_DATA |

## Within-leg contrast: hard-suspended vs exchange-only

| leg | verdict | median premium, 暂停申购 | median premium, 场内买入 | gap pp | n |
|---|---|---|---|---|---|
| 510760 | NO_CONTRAST | n/a | n/a | n/a | 0 / 0 |
| 512040 | NO_CONTRAST | n/a | n/a | n/a | 0 / 0 |
| 159655 | NO_CONTRAST | n/a | n/a | n/a | 0 / 0 |
| 513690 | BLOCK_DOES_NOT_WIDEN | +0.50% | -0.02% | +0.52 | 64 / 1265 |
| 159519 | NO_CONTRAST | n/a | n/a | n/a | 0 / 0 |

### The same contrast with the valuation gaps removed

The one-row 暂停申购 words are a shut overseas market, not a fund decision (see
"What the one-row words are" below). Those sessions carry no fresh NAV, so their
premium is priced against a stale one. Repricing the block without them asks the
question the table above cannot: is the premium wider on the sessions the fund
itself chose to shut, or was the wider reading the calendar all along?

| leg | verdict | median premium, 暂停申购 | median premium, 场内买入 | gap pp | n kept | rows dropped |
|---|---|---|---|---|---|---|
| 510760 | NO_CONTRAST | n/a | n/a | n/a | 0 | 0 |
| 512040 | NO_CONTRAST | n/a | n/a | n/a | 0 | 0 |
| 159655 | NO_CONTRAST | n/a | n/a | n/a | 0 | 0 |
| 513690 | BLOCK_DOES_NOT_WIDEN | +0.62% | -0.02% | +0.64 | 40 | 24 |
| 159519 | NO_CONTRAST | n/a | n/a | n/a | 0 | 0 |

'rows dropped' is the count of priced 暂停申购 rows whose NAV stamp is one of the
single-row runs named in the cause section. The exchange-only column is untouched:
the same baseline prices both readings, so the only thing that moves is the block.

## Days vs runs: how much evidence the block count actually is

A suspension lasts as long as the fund keeps it, so the days inside one run are
the same fact repeated. The table above counts days; this one counts runs.

| leg | runs (all words) | blocked runs | runs of a single NAV row | median rows per block | longest block | run-level gap vs exchange-only | longest run's own gap | gap with the longest run dropped | verdict |
|---|---|---|---|---|---|---|---|---|---|
| 510760 | 1 | 0 | 0 | n/a | 0 (n/a..n/a) | n/a | n/a | n/a | NO_BLOCKED_EPISODES |
| 512040 | 1 | 0 | 0 | n/a | 0 (n/a..n/a) | n/a | n/a | n/a | NO_BLOCKED_EPISODES |
| 159655 | 1 | 0 | 0 | n/a | 0 (n/a..n/a) | n/a | n/a | n/a | NO_BLOCKED_EPISODES |
| 513690 | 85 | 42 | 24 | 1 | 3 (2021-09-17..2021-09-23) | +0.17 | -0.68 | +0.20 | EPISODE_GAP_DOES_NOT_WIDEN |
| 159519 | 1 | 0 | 0 | n/a | 0 (n/a..n/a) | n/a | n/a | n/a | NO_BLOCKED_EPISODES |

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
| 510760 | (never suspended in coverage) | | | | |
| 512040 | (never suspended in coverage) | | | | |
| 159655 | (never suspended in coverage) | | | | |
| 513690 | 暂停申购 | 2021-09-17 | 2021-09-23 | 3 | -0.70% |
| 513690 | 暂停申购 | 2021-12-30 | 2022-01-04 | 3 | +0.74% |
| 513690 | 暂停申购 | 2024-12-25 | 2024-12-27 | 3 | +2.35% |
| 513690 | 暂停申购 | 2025-12-25 | 2025-12-29 | 3 | -1.25% |
| 513690 | 暂停申购 | 2021-09-30 | 2021-10-08 | 2 | +0.02% |
| 513690 | 暂停申购 | 2021-10-14 | 2021-10-15 | 2 | -0.12% |
| 513690 | 暂停申购 | 2022-01-28 | 2022-02-07 | 2 | +1.92% |
| 513690 | 暂停申购 | 2022-04-01 | 2022-04-06 | 2 | +1.93% |
| 159519 | (never suspended in coverage) | | | | |

## Why the blips: when the word is printed, not why

A single-row 暂停申购 run is one word printed between two exchange-only rows.
The run table above counts them; this one asks whether those days are ordinary
sessions. If they were, their weekday mix would look like the session mix. It
does not.

| leg | one-row runs | busiest weekday | share of runs on it | its share of sessions | chance of that (1-sided) | bracketed by 场内买入 both sides | runs with a NAV jump >3% | day-of-month peaks | verdict |
|---|---|---|---|---|---|---|---|---|---|
| 510760 | 0 | n/a | n/a | n/a | n/a | 0 | 0 | n/a | TOO_FEW_BLIPS |
| 512040 | 0 | n/a | n/a | n/a | n/a | 0 | 0 | n/a | TOO_FEW_BLIPS |
| 159655 | 0 | n/a | n/a | n/a | n/a | 0 | 0 | n/a | TOO_FEW_BLIPS |
| 513690 | 24 | Tue | 38% | 20% | 0.038 | 24 | 0 | 2(5), 4(2), 10(2) | BLIP_NO_CADENCE |
| 159519 | 0 | n/a | n/a | n/a | n/a | 0 | 0 | n/a | TOO_FEW_BLIPS |

**Pooled:** 24 single-row runs out of 42 blocked runs; **Tue carries 38% of them against 20% of all priced sessions** (one-sided chance 0.039). Peak days of the month: 2(5), 4(2), 10(2). 24 of the runs are bracketed by 场内买入 on both sides, and 0 carry a NAV jump larger than 3% -- a split or a big distribution, not a quota.


Only 0 of 5 legs clear the line on their own (none); the rest lean the same way with too few runs to call it, which is why the pooled reading above -- not a per-leg one -- is the sentence this section quotes.

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
| 510760 | 0 | 0 | 0 | n/a | 0% | 0/0 | 0 | n/a | 4.8% | n/a | NO_ONE_ROW_RUNS |
| 512040 | 0 | 0 | 0 | n/a | 0% | 0/0 | 0 | n/a | 4.7% | n/a | NO_ONE_ROW_RUNS |
| 159655 | 0 | 0 | 0 | n/a | 0% | 0/0 | 0 | n/a | 5.0% | n/a | NO_ONE_ROW_RUNS |
| 513690 | 24 | 24 | 0 | 0.127 | 58% | 1/0 | 23 | 4% | 4.8% | 0.9x | CALENDAR_GAP |
| 159519 | 0 | 0 | 0 | n/a | 0% | 0/0 | 0 | n/a | 4.9% | n/a | NO_ONE_ROW_RUNS |

**Pooled:** 24 one-row runs of 42 blocked runs. **24/24 suspend 赎回 on the very same row** -- an announcement that closes subscription does not close redemption, and this one always does. They move the NAV by **0.13 of the leg's own median move** (median over legs; 58% of the runs sit at a quarter or less) and 0 carry the previous NAV exactly, so a distribution is not what these rows are: the largest move on any of them is 1.6011% at 2022-08-25 and the 90th percentile is 0.8458%. **1/24 land on a session whose gap contains an NYSE closure** (full 1, early 0) against **4.8% of ordinary sessions** -- 0.9x.

**Two calendars in hand, and only one is derived from rules.** The US list is rule-built; the Hong Kong list is *measured* on the HSI series (no bar = Hong Kong did not trade; turnover under a share of its own trailing-20 median = a half day with no closing valuation), because HKEX follows the lunar calendar and also shuts for typhoons, which no rule set predicts. A calendar is named only when it explains at least 60% of these runs at 3.0x the ordinary-session rate and beats the other by 10pp.

| calendar | how it is known | runs it explains | rate | ordinary-session rate | lift | named |
|---|---|---|---|---|---|---|
| NYSE | rule list, window (prev_stamp, stamp] | 1/24 | 4% | 4.8% | 0.9x | no |
| HKEX | measured on HSI (no bar / half day / shut weekday in the gap) | 21/24 | 88% | 6.3% | 13.9x | yes |

HKEX series used here: **3255 sessions, 2013-08-20..2026-11-10** (read: cache-stale). The half-day cutoff is a ruler, so the Hong Kong reading is printed at three of them -- 20/24 runs at 50% of trailing turnover, 21 at 60%, 22 at 70% -- and the page quotes no single one as the answer.

**Named per leg:** HKEX explains 513690. The pool word above is a different question from these: it asks which calendar explains most of the 116 runs, not which one explains a given leg.

### What this changes in the reading

The day counts above are not 141 independent suspensions. 18 of them are multi-row runs -- the fund really did keep the channel shut -- and 24 are the single-row valuation gaps measured here. A session that could not be valued has no fresh NAV to price a premium against, so those rows belong to the calendar and not to the fund's policy.

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
