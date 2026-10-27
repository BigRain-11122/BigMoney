# DIGEST 2026-10-28 r1205 bm-b — E169: the tilt's sign is not the book's sign

**Product**: `results/e43_tilt_4member/TILT3SIGN-20261027.json` (162 joined months) + new mode
`python scripts\e39_panel_census.py tilt3sign` (selftest 526 → 535/535 PASS).

## Why this burn

The family publishes the three-member tilt's sign per era and the engine's own wide-vs-ladder
difference per era on *separate rows*. Nothing had ever put the two arrows side by side. E126 measured
the regressor; "small caps led" and "the wide book got paid for it" are two different claims, and only
one of them is about money.

## What the two arrows say

| era | months | tilt bp/yr | engine spread bp/yr | era signs | month agreement |
|---|---|---|---|---|---|
| pre2017 | 44 | +1186.4 | +287.2 | agree | 56.8% (61.5% outside deadband) |
| 2017_2020 | 48 | **−923.9** | **+331.7** | **DIFFER** | 45.8% (44.4%) |
| 2021_2023 | 36 | +609.9 | +251.1 | agree | 44.4% (39.4%) |
| 2024_now | 34 | +252.8 | **−21.6** | **DIFFER** | **23.5%** (18.8%) |
| full | 162 | +237.1 | +227.6 | agree | 43.8% (42.3%) |

- **Two of four eras disagree at the era scale.** 2017_2020 is the loud one: the tilt reads −924 bp/yr
  while the book's own wide-vs-ladder spread earned **+332 bp/yr** in the same months. Quoting the tilt
  as "the wide book lost that era" is a category error — the regressor lost, the book did not.
- **No era clears 57% month-level agreement** (range 23.5–56.8%, and 18.8–61.5% outside the declared
  10 bp deadband). The full window's 43.8% is the load-bearing number: the era-level agreement on
  "full" is a statement about two *levels*, and the monthly series underneath it is a coin flip.
- **2024_now is worse than a coin flip** (23.5%, 8 of 34 months; 18.8% outside the deadband). This is
  the same era where E170 found the *published* arrow flip (−21.6 → +25.1 bp under the repair), i.e.
  the era where the reading is most fragile is also the era where the tilt carries the least
  month-scale information about what the book earned.
- Arithmetic cross-check against the published twin: `engine_mean_ann_bp` reproduces
  `TILT3SCREEN.per_era.*.spread_raw_bp_raw` exactly (287.2 / 331.7 / 251.1 / −21.6 / 227.6), so the
  engine series here is the same quantity the screened twin priced, read on the raw arm.

## Reusable reading

1. **A regressor's sign is not a book's sign.** The tilt is a ratio of member returns; the spread is
   what a portfolio is paid. They can point opposite ways for years, and the family had both numbers in
   the same file without ever joining them.
2. **An era-level sign agreement can be produced entirely by the level.** Publishing the month-level
   rate beside it is what stops "the arrows agree" from reading as "the signal works" — here `full`
   agrees at the era scale at 43.8% monthly agreement, which is the same sentence as "no information".
3. **A near-zero month is not a sign.** The 10 bp deadband was declared before the burn and is printed
   beside the raw rate rather than replacing it; on 2024_now the deadband makes the reading *worse*
   (23.5% → 18.8%), so it is not a knob that flatters the result.

## Wiring

- mode `tilt3sign` added beside `tilt3reach` / `tilt3legs` / `tilt3screened`; reuses `_monthly_core`,
  `_in_era`, `write_json` — no second panel load and no second join.
- selftest +9 legs (535/535) pinning: both scales agree on a same-sign fixture; one disagreeing month
  is counted without moving the era sign; the disagreeing month is *named*; opposite eras disagree on
  both scales; the deadband drops the near-zero month while the raw rate keeps it; a tie is a
  disagreement; a two-month era is refused; the constants are declared before the burn; the `raw=`
  seam exists for a future screened twin.
- card: `knowledge/METHODOLOGY_ASSETS.md` **E170**.

## Open

The face is the **raw arm** (the E126 arm of record). A screened twin of this leg is *not* claimed —
E170 already showed `tilt_bp_delta = 0.0` on every era, so the twin would move only the engine column;
it is seeded as the natural follow-on rather than assumed here.