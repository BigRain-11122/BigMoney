# DIGEST 2026-10-21 — E71: the weekly book's residual is timing, not different names

**Question (from E70).** E70 switched the engine fee off (x0) and still left the full
ISO-weekly book ~45bp behind month-end at the 2020 start. Two channels fit that
number: *when* the book trades, or *what* it holds. E71 censuses the held names of
`week` / `week_near_me` / `me` at paired decision sessions.

**Answer.** The names are the same. Mean name overlap at paired sessions is
**0.9993** (2020 start, 80 pairs, min 0.9849) and **0.9994** (2013 start, 164 pairs,
min 0.9630). The entrant/exit flow is a rounding error against a ~1,000-name book:
0.49 entrants / 0.21 exits per pair (2020) and 0.30 / 0.12 (2013). So the -45bp
residual is the **timing of the trade** — the same list bought on a different session
— plus a small, quantified second channel: the monthly book lags on dropping names
that have gone ineligible.

**The membership channel, measured.** Both books equal-weight the entire live
universe (`pick_n=9999`), so membership can only move through the eligibility flow
(250 consecutive priced closes). That flow is visible in the *self-churn*:

| book | decisions (2020 start) | names changed per step | mean sessions a dropped name is still held |
|---|---|---|---|
| `week` (ISO weekly) | 348 | 5.13 | **4.85** |
| `week_near_me` (weekly grid read monthly) | 82 | 21.51 | **20.61** |
| `me` (month-end) | 80 | 21.36 | **20.68** |

A weekly book clears a dead name in about one week; any monthly-cadence book can
carry it for about a month. Exit events are rare — 138 (me) / 145 (week) at the 2020
start, 188 / 194 at 2013 — so this is **~1-14 names per year lingering 16 extra
sessions**, not a membership substitution story. At the 2013 start the churn is
smaller (10.29 / 2.46 per step) because the universe is younger.

**Era split (2020 start).** 2017_2020 is a null era: both books hold nothing there
(eligibility burn-in leaves the window in cash), which is the same cash-slice
signature E59/E64 print as an exact 0.0bp gap. 2021_2023 overlap 0.9988, 2024_now
0.9999. The 2013 start adds pre2017 0.9990 and 2017_2020 0.9998, so the reading is
not a window artefact.

**Coverage.** `week_only` union = 27 names, `me_only` = 0, `both` = 1225: every name
the month-end book ever holds, the weekly book holds too; the 27 extra are names that
list late in the window.

**Where the residual lives.** Since the names agree, the -45bp must come from the
price path between the two decision sessions (E67/E68 priced that shoulder at
-19/-24bp early and -43/-52bp late around the boundary), plus a small drag from
carrying ineligible names. E72 is the direct follow-up: price the stale-hold channel
outright — what does the tail of an exiting name return over the sessions a monthly
book still holds it?

**Files.**
- `results/e44_midmonth/WEEKNAMES-20261021.json` (start 2020)
- `results/e44_midmonth/WEEKNAMES-20261021-s20130101.json` (start 2013)
- `scripts/e39_panel_census.py` — new `weeknames` leg + `_overlap_stats`,
  `_pair_to_grid`, `_name_churn_stats`, `_stale_hold_stats`, `_pair_summary`,
  `_tail_guard`, `_membership_reading` (selftest 117/117, +10 hermetic legs)

**Honest limits.**
- Equal-weight whole-universe books: this is the eligibility flow, not a top-N rule.
- The comparison pairs each month-end with the *nearest* weekly session, so 11 (2020)
  / 21 (2013) of the pairs are the same session and overlap is exact by construction;
  those pairs are counted (`same_session_pairs`), not averaged away.
- `stale_hold` is truncated at the window ends.
- Mid-arrival bars are dropped by a *local* guard (`_tail_guard`): a decision whose
  live count collapses against its neighbours is skipped. Without it the unfinished
  cutoff bar (14 live names) read as a +1,208-name entrant wave — the first draft of
  this face carried exactly that artefact.
- `membership_reading` is a 0.95 flat label on the mean overlap: descriptive, no
  prereg, no gate, trial 0.