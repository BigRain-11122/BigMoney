# E118 — the stale tail's own screened twin: the guard, not the panel

- **Face**: `results/e44_midmonth/STALETAILSCREEN-20261027.json`
- **Leg**: `python scripts/e39_panel_census.py staletailscreen`
- **Twin of**: `run_staletail` (E74), face `results/e44_midmonth/STALETAIL-*.json`
- **Evidence cutoff**: 2026-10-27
- **Round**: r1189 bm-b, 2026-10-27 20:2x
- **Trial count**: 0 (descriptive census, no gate, no prereg, no ledger booking)

## Why this twin is not a formality

E74 already excludes, before pricing anything, every stale-tail event whose span
carries a >30% single-session move — the signature of a corporate action printed
on an unadjusted series. So this leg's published numbers are a *guarded* set, and
`panel_screen.screen_universe(mode=neutralise_int)` repairs a *different*
population (integer-ratio prints). The twin therefore asks a question the other
six E112–E117 twins could not: **do the two screens agree on which prints are
impossible?**

## What it found

| reading | value |
| --- | --- |
| cells compared / moved | 77 / 19 |
| guarded columns moved | 3 |
| unguarded columns moved | 8 |
| other (per-era, answers) moved | 8 |
| max abs delta | 0.42 |
| same-arm control | 0 cells moved (correct) |
| artefact events | 19 raw / 19 screened, same count |
| top artefact print | `sh510150@2021-05-31` on **both** arms |
| cutoff control (old face `STALETAIL-20261021` vs today raw) | 44 cells moved, max 6.0 |

The **raw tail is arm-invariant, bit for bit**:

| column | raw arm | screened arm |
| --- | --- | --- |
| `raw_all_events` | 131 events, -514.454 bp | 131 events, -514.454 bp |
| `raw_clean` | 112 events, -6.079 bp | 112 events, -6.079 bp |
| `relative_all_events` | 131 events, -522.209 bp | 131 events, -522.629 bp |
| `relative_clean` | 112 events, -15.862 bp | 112 events, -16.138 bp |

Only the **relative** (excess-over-wide-book) columns move, and they move by
0.08% of their own total. That is the mechanism: the repair edits the *wide
book's* own members' returns, not the exiting name's return, so a "name minus
wide book" arithmetic difference shifts a fraction while the priced tail itself
does not.

## The two lessons

1. **On a face that already carries a guard, a screened twin tests the guard's
   agreement with the repair, not the face's stability.** The right question is
   "which columns *should* move", and here the answer was: none of the priced
   ones. A twin that reports only "19 of 77 moved" would read as instability; the
   split into guarded / unguarded is what makes the reading usable.
2. **Panel refresh moves this family far more than the repair does** (44 cells /
   6.0 bp vs 19 cells / 0.42 bp). Any number quoted from the E7x mid-month family
   must carry its cutoff, or the reader is comparing two panels and calling it a
   repair effect.

## Boundary

- Descriptive census only: no gate, no verdict on the strategy, no prereg, no
  trial count, no ledger booking.
- The screen repairs prints inside the panel it is handed; it does not add or
  remove bars, so an unchanged `universe_members` is a property of the repair,
  not evidence the panel is clean.
- The artefact guard is a daily-limit screen, not an adjustment: an event it
  excludes is excluded identically on both arms, so this leg can only show
  whether the repair reached the prints the guard missed.
- E74's era bp/yr divides a small total by a short span on the early eras; those
  cells move for arithmetic reasons as much as for repair reasons.
- E97 counts the published numbers of this runner; the join covers the
  tail/era/answers cells and the top artefact print, not the full event list or
  the skipped-block counters.