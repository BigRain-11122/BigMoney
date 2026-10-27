# E105 — every MID-family LEVEL now names the one name that carries it

Face: `results/e44_midmonth/MIDLEVEL-DRIVERS-20261026-s20180101.json`
Leg: `python scripts/e39_panel_census.py midleveldrivers --start 2018-01-01`
Selftest: `python scripts/e39_panel_census.py selftest` → 331/331 PASS (6 new E105 legs)
Pool entry: E105-LEVEL-SINGLE-NAME-COLUMN (bm-b, cpu-only) → done

## What was open

E100 found each published MID-family LEVEL is a mean over 10-29 transitions and that one name carried
100% of the 2017_2020 `me` cell. A reader of `MID-20261026-s20180101-armed.json` could not see that, and
could not check it without re-running gaptop3. The face published a level and nothing about who produced it.

## The decomposition (exact, not a ranking of correlates)

`churn_alpha = mean(entrant fwd) - mean(exit fwd) = sum(r_e/n_e) - sum(r_x/n_x)`, so each subscribed name
carries an additive share of one transition; the era LEVEL is `sum(churn_alpha)/T`, so a name's share of the
LEVEL is its transition share divided by `T`. Published residual `additivity_max_abs_residual_bp = 0.0`
across all 30 measured cells — the shares sum back to the level, cell by cell.

Control: the same decision sets re-read here reproduce the published MID face exactly —
`cells_joined=30, max_abs_diff_bp=0.0, identical=true`. So nothing below is a data drift.

## Reading (30 measured cells)

`single_name_artefact` 9 · `concentrated` 13 · `broadly_supported` 4 · `immaterial_level` 4

### The biggest cells in the family are one-name artefacts

| arm | era | book | level_bp | carried by | side | contribution | share | date |
|---|---|---|---|---|---|---|---|---|
| unscreened | 2024_now | mid | −123.7 | sz159925 | exit | −130.11bp | **105.2%** | 2024-01-15 |
| gap1/gap2/gap5 | 2017_2020 | me | 1084.1 | sh510230 | exit | 793.21bp | **73.2%** | 2020-07-31 |
| all five arms | 2017_2020 | mid | 1405.0 | sh510230 | exit | 794.19bp | **56.5%** | 2020-07-15 |

Three consequences:

1. **The 1405.0bp 2017_2020 `mid` cell — the largest level in the family — is 56.5% one exit.** It reads
   identically in all five arms because the carrier is in every arm's universe and the transition is the
   same; the arm cannot move what one name carried.
2. **The −123.7bp `2024_now` `mid` unscreened cell is 105.2% one name.** That is the cell E104 quoted as
   "unscreened leaves the mid book at −123.7 while every arm is −364.7". The unscreened half of that contrast
   is a single 2024-01-15 exit (sz159925), so the read is a name artefact, not a screening effect.
3. **The 2017_2020 `me` gap-arm cells (1084.1bp) are 73.2% the same name**, which is why gap1 == gap2 == gap5
   to the last digit: they are not three measurements of a level, they are three prints of one exit.

### The cells that do hold

| arm | era | book | level_bp | biggest name | share | names | transitions |
|---|---|---|---|---|---|---|---|
| unscreened / neutralise_int | 2021_2023 | me | 1866.5 | sh510580 | 17.8% | 419 | 27 |
| unscreened / neutralise_int | 2021_2023 | mid | 2185.4 | sh510150 | 14.5% | 459 | 29 |

These are the only broadly-supported cells in the set: ~420-460 subscribed names, 27-29 transitions, no single
name above 18%. If a level in this family is to be quoted as a property of the calendar, it is one of these two.

## Traps this closes

- **A level that is identical across arms is not thereby robust.** The 2017_2020 `mid` cell prints 1405.0 in
  all five arms *because* one name carried it; arm-invariance and artefact-hood are the same signature here.
  Before this face, the arm grid looked like replication.
- **"The unscreened arm is milder than the screened arms" was measured on an artefact.** One name produced the
  difference; the honest statement is that neither reading is a level.
- Naming a carrier names the swap that produced the read; it does not claim the repair caused the forward
  return inside it. The carrier is usually a corporate-action read (share split) or a single-day gap — which
  is exactly why the name and date are published.

## Honest limits

- Descriptive census: no gate, no verdict on the strategy, no prereg, no trial count, no ledger booking.
- The share is a share of an equal-weight mean of name reads, not of money.
- `pre2017` is empty for a 2018 start and reads `no_transitions`, not a clean zero.
- The material floor is 50bp and the artefact floor is 50% of the cell; both are in `spec` so a reader can
  re-cut the table without guessing the thresholds.