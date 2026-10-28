# DIGEST 2026-10-28 r1212 bm-b — E178: a fixed leg's zero is a membership fact

**Face**: `results/e43_tilt_4member/TILT3LEGFAMILY-20261027.json`
**Leg**: `python scripts/e39_panel_census.py tilt3legfamily` (selftest 584/584, +5 legs = 579 -> 584)
**Ticket**: E178-TILT-LADDER-LEG-INVARIANT (pool, claimed + burned in-round)
**Card**: knowledge/METHODOLOGY_ASSETS.md E178

## Question

E176 published the engine column's repair delta split by book and found the ladder leg at
exactly 0.0 in every era, with the cause derived from the screen report: none of the five
ladder members carries a repair event. A reader holding only E176 cannot tell whether
"the fixed leg never moves" is a law of this family or a property of that one 5-name book.

## What was measured

Three pinned skins, each priced member by member on its own month set, both arms:

| skin | large leg | small leg | months | members repaired | max abs member delta |
|---|---|---|---|---|---|
| tilt5 | sh510300, sh510050 | sh510500, sh512100, sh588000 | 2021-2026 | 0 of 5 | 0.0 bp |
| tilt4 | sh510300, sh510050 | sh510500, sh512100 | 2016-2026 | 0 of 4 | 0.0 bp |
| tilt3 | sh510300, sh510050 | sh510500 | 2013-2026 | 0 of 3 | 0.0 bp |

All three skins are flat in all five era windows (`eras_all_pinned_skins_flat` = every
era), and the maximum absolute per-member delta across all pinned members and all eras is
**exactly 0.0 bp** — not a small number, a structural zero.

Beside them, the control that CAN move: the rotating wide book reads
**+30.204 / +49.598 / +17.121 bp** on 2021_2023 / 2024_now / full (identical to E176's
`wide_book_delta_bp`), carrying 7 / 45 / 52 repaired names. The engine delta is
+29.3 / +46.7 / +16.3 bp.

`invariant_scope` = **`pinned_membership_only`**.

## Verdict

"The fixed leg never moves" is **not a family law**. It is a statement about a membership
set: a leg cannot move if none of its names is in the repair set, and every pinned skin
here is built from the same five ladder names (pinned universe = the five ladder members,
disjoint from all 67 repaired names at cutoff 2026-10-27). The three zeros are one fact
reported three times, not three independent confirmations, and the claim transfers to a
fixed composition only for as long as that composition stays out of the repair set.

The mid-month and pair books re-subset the same ladder leg for their fixed side, so they
inherit this scope rather than extend it. The only book in this family whose delta can be
non-zero is the one whose membership turns over — which is exactly what E176 measured
moving.

## Method notes (reusable)

1. **Name the branch, don't print the zero.** `_pinned_leg_verdict` publishes
   `pinned_no_repair_event` vs `carries_repair_event_flat` vs `carries_repair_event_moved`.
   A leg holding a repaired member that still prints zero is a wiring defect and is now a
   published word instead of an indistinguishable 0.0.
2. **A month priced on one arm only must be dropped, never read as a zero return** — doing
   the latter manufactures a large negative delta on a name the repair never touched, i.e.
   it fabricates precisely the quantity being measured (selftest leg 3 pins this).
3. **Annualisation bug caught in-window**: the first cut applied `12/n*1e4` to an already
   averaged mean (double division), printing 600 instead of 1200 bp. The `_era_side_bp`
   convention it copied multiplies a SUM by `12/n*1e4`; a per-member MEAN takes `12*1e4`.
   Three selftest legs went red on the hand-computable fixture — the reason the fixture is
   hand-computable.

## Honest limits

- Per-member deltas are price-return differences on member months, not book contributions;
  the ladder book's `__cash__` sink is not in this face (that is E179's lane).
- `pre2017` has no tilt5 months (sh588000 starts 2020-11), so that cell's null is a window
  fact, not a missing measurement.