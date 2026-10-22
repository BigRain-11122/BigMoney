# E83 / E84 — which published churn cells are one swap wide, and is the second screen arm wasted?

Evidence cutoff **2026-10-21**. Faces:
`results/e44_midmonth/SINGLEPRINT-20261021.json` (E83),
`results/e44_midmonth/MODEEQ-20261021.json` (E84).
Runner: `python scripts/e39_panel_census.py singleprint` (`scripts/e39_panel_census.py`,
selftest 195/195). Descriptive census only: no gate, no verdict, no prereg, no trial booking.

## What was asked

E82 attributed the newest-era churn-gap amplification to **one** transition
(mid15 2024-01-15 sz159925, −6614bp of a −6507bp hit bucket). E83 turns that
anecdote into a screen over **every published churn cell**: each book × screen
mode × era, re-read with its single most influential transition removed. Removing
transition *i* from *n* alphas moves the mean to `(n·m − a_i)/(n−1)`, so the
biggest collapse is always the transition farthest from the mean. A cell that
keeps **less than half** its magnitude without one transition is quoting a swap,
not a period. E84 audits `neutralise_int` vs `neutralise`: the two arms returned
identical churn rows in E80/E82, and a silently duplicated arm is the shape of an
accounting error.

One burn answers both, because both need the same four universes (unscreened +
three screens); the universe half of E84 is hermetic and costs nothing.
24 cells examined (16 book-era + 8 gap-era), 45s.

## E83 — 13 of 24 published churn cells are one swap wide

Per book (month-end `me` vs `mid15`) × universe × era:

| book | universe | era | n | mean bp | without one swap | survives |
|---|---|---|---|---|---|---|
| me | unscreened | 2021_2023 | 27 | +1866.5 | +1609.8 | 86.2% |
| me | unscreened | 2024_now | 27 | +87.3 | +54.3 | 62.2% |
| mid15 | unscreened | 2021_2023 | 29 | +2185.4 | +1926.8 | 88.2% |
| mid15 | unscreened | 2024_now | 27 | **−123.7** | **+1.0** | **0.8% (flag)** |
| me | neutralise | 2024_now | 27 | +92.4 | +59.6 | 64.5% |
| mid15 | neutralise | 2024_now | 27 | **−364.7** | **+5.1** | **1.4% (flag)** |
| me | drop | 2024_now | 27 | **+52.1** | +18.9 | **36.3% (flag)** |
| mid15 | drop | 2024_now | 27 | **+28.0** | +8.1 | **28.9% (flag)** |

The churn-*gap* cells (mid15 − me, one transition removed from one side — the two
books' decision dates are disjoint, so there is no matched transition to drop):

| universe | era | gap bp | without one swap | survives | owning side / window |
|---|---|---|---|---|---|
| unscreened | 2021_2023 | +318.8 | +60.3 | **18.9% (flag)** | mid15 2021-05-17 |
| unscreened | 2024_now | −211.0 | −86.3 | **40.9% (flag)** | mid15 2024-01-15 |
| neutralise | 2021_2023 | +318.8 | +60.3 | **18.9% (flag)** | mid15 2021-05-17 |
| neutralise | 2024_now | **−457.1** | −87.3 | **19.1% (flag)** | mid15 2024-01-15 |
| drop | 2021_2023 | +374.2 | −40.1 | **10.7% (flag)** | me 2022-08-31 |
| drop | 2024_now | −24.1 | −0.2 | **0.8% (flag)** | me 2026-04-30 |

### The one that changes a published conclusion

E80 recorded *"2021_2023 −8bp era gap with churn alpha actually favouring mid
(+318.9bp), so a second mechanism lives there (recorded, not explained)"*. That
+318.8bp gap keeps **18.9%** of itself when one mid15 transition
(2021-05-17 → 2021-06-15) is removed. It is one swap wide: the "second
mechanism in 2021_2023" reading should be **withdrawn as a magnitude claim** and
carried at most as a single-window anecdote. The same transition, the same
collapse, appears in all three neutralise universes — the screen does not touch
it, so this is not a repair artefact either way.

### What is NOT one swap wide

- The month-end book is the robust side in the newest era: +87.3bp keeps 62.2%
  unscreened and +92.4bp keeps 64.5% screened. The asymmetry E80 found
  (mid-month fragile, month-end not) survives the removal test — only the
  magnitudes were levered.
- 2021_2023 both books survive at 86–89% in every cell. The era is broad; it is
  the *gap* between the books in that era that is one swap wide.

### Print tagging

10 of the 13 flagged cells remove a transition whose swapped name carries a
print event (corporate action); 3 do not (me drop 2024_now, mid15 drop 2024_now,
drop-gap 2024_now). So a majority of the fragility is one corporate-action print
landing inside a swap window — but not all of it, and the screen charges the
bar, not the print, so the tag is context, not a cause.

## E84 — the conservative arm is a duplicate *for this consumer*, not the same screen

| reading | value |
|---|---|
| names touched by `neutralise_int` | **65** (65 prints) |
| names touched by `neutralise` | **129** (135 prints) |
| names only the full arm repairs | **64** |
| of those 64, names the book ever swapped | **63** |
| transitions that swapped an extra name | **201** |
| of those, windows where that name's own print lands | **0** |
| churn rows compared / differing | 69 / **0** (`me`), 69 / **0** (`mid15`) |
| era cell differences | **0** |

So the universes are genuinely different objects (64 names / 70 prints apart) and
63 of those names are traded by the book — yet the churn cells are bit-identical.
The reason is structural, not luck: the sleeve prices the forward return of the
names swapped **inside one window**, so a repaired bar can only move a cell when
the swapped name's own print falls in that same window. It never does here.

**Verdict:** `identical_on_this_face`. Reading for the chain:

- for name-level churn sleeves (E44 / E80 / E82 consumers) the second arm is a
  wasted burn at this cutoff — keep one arm;
- this is **not** a statement that the modes are the same screen: any face that
  prices per-name returns over the whole universe (book returns, breadth,
  `screenreg` / `screenwide` / `screenweek`) still needs the full arm, because
  there the repaired bar is the return.

## Pits

- The two books rebalance on **different dates**, so a "matched-transition"
  removal is impossible — the date sets are disjoint by construction. The gap
  screen must remove from one side and leave the other intact; the first draft
  intersected the date sets, produced `gaps = {}` for all four universes, and
  still printed a plausible-looking `cells_examined` because the counter was
  summing universes instead of era cells. An empty limb plus a healthy-looking
  total is exactly the shape this chain keeps getting bitten by — check the limb
  counts, not the total.
- `_print_row` emits `ret_pct`, not `return_pct`; the first publish carried
  `null` moves for every extra name until the key was read off the source.

## Next

E81 (raw hooks on the highest-consumption exposed runners) is still open; E84's
answer frees the second arm for the churn consumers but not for the per-name-return
runners, so E81 should carry both columns where the two arms differ.