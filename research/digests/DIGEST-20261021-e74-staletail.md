# DIGEST 2026-10-21 — E74: the stale-hold tail is a corporate-action artefact, not a channel

**Round** r1145 (bm-b) · **Evidence cutoff** 2026-10-21 · **Runner** `scripts/e39_panel_census.py staletail`
(selftest 138/138) · **Faces** `results/e44_midmonth/STALETAIL-20261021.json`,
`STALETAIL-20261021-s20130101.json` · **Chain** E70 fee → E71 names → E72 stale tail → E74 relative + artefact screen

## Question

E72 priced the stale-exit tail (a name the weekly book sold that the month-end book keeps holding) and
found its sign flipping era to era: **+282bp/yr pre2017, −226bp/yr 2021_2023, +1.6bp/yr 2024_now**.
Sign flips with the era are the signature of beta, not of a membership mechanism. E74 recharges the same
events **relative to the wide book over the identical sessions** and reports both columns side by side.

## What was added

* `_stale_hold_inputs` — one shared panel/calendar/book builder so the absolute (E72) and relative (E74)
  reads cannot drift onto two different universes.
* `book_ret_fn` on `_stale_hold_events` — adds `book_return_pct`, `excess_return_pct`,
  `relative_bp_contrib` per event; an unpriceable reference span is reported in `skipped.unpriced_book`.
* `_wide_session_returns` / `_compound_between` — the wide book = equal weight of every universe member
  priced at both `t-1` and `t`, compounded over the event span.
* `_max_session_jump` — the artefact screen (largest move between two **consecutive priced closes**).
* `_relative_reading` — a label (`collapsed` / `partial` / `survives`), not a test.
* new `staletail` leg + 11 hermetic selftest legs (127 → 138).

## Finding 1 — nineteen of 128 events are share splits

`sh510150` prints **10.414 → 0.87** between 2021-05-27 and 2021-05-31 (a 12:1 split on an unadjusted
series, with a suspension bar in between). E72 read that as a −91% name return over five sessions and it
alone was −44bp of the published −512.6bp total.

Guarding at 30% per priced pair (beyond any A-share/ETF daily limit) removes:

| window | events | artefacts | clean events |
|---|---|---|---|
| 2020 start | 128 | **19** | 109 |
| 2013 start | 172 | **23** | 149 |

The guard must skip missing bars, not abort on them: the split hides *behind* a `None` session, and a
None-blind scan reports the span as unjudged and misses the very artefact it exists to catch.

## Finding 2 — the tail is empty once the splits are screened

| reading | 2020 start | 2013 start |
|---|---|---|
| raw, all events | −76.7bp/yr | +1.8bp/yr |
| raw, clean | **−0.63bp/yr** | **−0.61bp/yr** |
| relative, clean | **−2.30bp/yr** | **+0.80bp/yr** |
| label | collapsed | collapsed |

By era (relative, clean): pre2017 **+3.99**, 2017_2020 **+4.24**, 2021_2023 **−2.45**, 2024_now **−3.53**
bp/yr — every era reads `collapsed`, and the newest-era column is bit-identical at both window starts.

So both the −226bp/yr of 2021_2023 and the +282bp/yr of pre2017 were **unadjusted split prints**. The
stale-hold channel is null in both directions: E71's structural asymmetry (20.7 sessions held past the
weekly drop vs 4.9) is real but worth **~2bp/yr**, far below the −45bp residual E70 left on the calendar.

## Chain state

Fee (E70) ✗ · names (E71) ✗ — overlap 0.9993, `me_only` 0 names · stale tail (E72/E74) ✗ — ~2bp/yr.
What remains of the −45bp is **session timing** between the two calendars, already priced as a shoulder
by E67/E68 (−19/−24bp early, −43/−52bp late at 1 session).

## Honest limits

* the guard is a daily-limit screen, not an adjustment: it removes events, it does not repair prices, and
  the all-events columns are kept beside the guarded ones so nothing is silently dropped;
* a split on a name that *rose* would be dropped too — the screen is symmetric, so it cannot bias the
  tail in the direction of the result;
* `relative_bp` is an arithmetic difference of returns, not a hedged P&L (no short leg, no borrow);
* pre2017 at the 2013 start rests on 18 clean events — the bp/yr there divides a small total by a short
  span and is quoted only to show it collapsed;
* reading labels use a 0.25 shrink share with a 5bp floor: a label, not a test; no prereg covers it;
* descriptive census only — no gate, no verdict, no ledger booking, trial_count 0.

## Follow-up seeded

**E75-PANEL-SPLIT-AUDIT** (ready): the same screen applied to the *whole* panel, with the list of affected
names/dates and an assessment of which already-published census legs can be contaminated — an equal-weight
book of ~200 names absorbs a −90% print as −45bp, which is exactly the size of the gap this chain is
chasing.