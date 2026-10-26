# DIGEST 2026-10-27 — E99: the start-2018 churn LEVELs, each cell named with its arm

Source face: `results/e44_midmonth/MID-20261026-s20180101-armed.json`
Runner: `scripts/e39_panel_census.py midlevels --start 2018-01-01` (selftest 271/271)
Evidence cutoff: **2026-10-26** · burn 33s CPU, one panel read per arm
Predecessor: E96 `LEVEL-LABELS-20261027.json` (0 of 2 published LEVEL faces declared an arm)

## What was open

E96 could not label `MID-20261020-s20180101.json` at all: its `2017_2020` era has no
arm twin on the 2020-start sibling, so every candidate arm stopped at 0.854 coverage and
the honest state was `unlabelled`. A label cannot be inferred into existence, so this
round burned the levels again with the arm written into the spec **from the producing
loop** (`spec.arms = list(universes)`), never typed afterwards.

## Arms (5), one universe each, same calendars / rank cache / fee ladder

`unscreened` (untouched `e27` loader) · `neutralise_int` (integer-ratio adjacent prints) ·
`neutralise_gap1` / `gap2` / `gap5` (adjacent + gapped integer prints within k missing sessions)

Coverage: 8 rows (4 eras × 2 books) × 5 arms = **40 cells, 0 missing arm keys**.
Populated eras: `2017_2020`, `2021_2023`, `2024_now`; `pre2017` is null by construction
(start 2018), and reads as null rather than as a borrowed number.

## Churn LEVEL, bp per swap (`churn_alpha_bp_mean`), delta vs unscreened

| era | book | unscreened | neutralise_int | gap1 | gap2 | gap5 |
|---|---|---|---|---|---|---|
| 2017_2020 | me | 1830.0 | 1882.5 (+52.5) | **1084.1 (−745.9)** | 1084.1 | 1084.1 |
| 2017_2020 | mid | 1405.0 | 1405.0 (0.0) | 1405.0 (0.0) | 1405.0 | 1405.0 |
| 2021_2023 | me | 1866.5 | 1866.5 (0.0) | **768.2 (−1098.3)** | 768.2 | 768.2 |
| 2021_2023 | mid | 2185.4 | 2185.4 (0.0) | **1068.2 (−1117.2)** | 1068.2 | 1068.2 |
| 2024_now | me | 100.7 | 105.6 (+4.9) | 105.6 (+4.9) | 105.6 | 105.6 |
| 2024_now | mid | **−123.7** | **−364.7 (−241.0)** | −364.7 (−241.0) | −364.7 | −364.7 |

## Era GAP (mid − me, x1) is arm-invariant

| era | unscreened | neutralise_int | gap1 / gap2 / gap5 |
|---|---|---|---|
| 2017_2020 | +50.0 | +50.0 | +50.0 |
| 2021_2023 | −8.0 | +8.0 | +8.0 |
| 2024_now | −85.0 | −83.0 | −83.0 |

## Three readings worth keeping

1. **The LEVEL moves up to 60% while the GAP moves at most 2bp.** 2021_2023 `me`
   1866.5 → 768.2 is a 59% cut, and 2017_2020 −745.9bp, yet the mid-minus-me gap stays
   +50.0 / +8.0 / −83.0 in every arm. The arm decides which level you publish; it barely
   touches the calendar gap. Same conclusion E92 reached at the 2020 start, now proven at
   the 2018 start where the `2017_2020` era actually exists.
2. **The unlabelled level was the most favourable one.** The newest-era mid-month churn
   reads −123.7bp untreated and −364.7bp under *every* repair arm: the untouched panel
   was flattering the mid-month book by 241bp per swap. A level quoted without its arm is
   not neutral — it is a specific arm, here the kindest one.
3. **The gap sweep saturates at one missing session.** `gap1 == gap2 == gap5` exactly
   (0.0bp marginal) in all 8 rows, so allowing two or five skipped sessions repairs
   nothing beyond the first. Consistent with E93's marginal at the 2020 start.

Zero level cells change sign across arms (`level_sign_flips_across_arms = []`).

## Published twin control

Joined against `MID-20261020-s20180101.json` on (era, book): 6 cells compared,
`max_abs_diff_bp = 5.1`, `identical = false`. That twin was burned on cutoff 2026-10-20
and this one on 2026-10-26, so the drift is a re-derivation through six more sessions of
data, not a producing-code difference. The superseded face is left frozen; nothing is
rewritten.

## Next (seeded as E100)

Name the transitions that carry the −745.9bp (`2017_2020`) and −1098.3bp (`2021_2023`)
gap-arm moves the way E91 named the 2021_2023 `me` gap, so the repair's effect is
auditable by name and date instead of quoted as a level delta.