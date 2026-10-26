# E100 — the two published gap-arm moves are one window each, and the window is a split print

- date: 2026-10-27 (bm-b r1169)
- face: `results/e44_midmonth/GAPTOP3-20261026-s2018.json`
- code: `scripts/e39_panel_census.py` mode `gaptop3`, selftest 299 -> 307
- question (pool E100): E99 published the gap arm as a difference of LEVELS
  (-745.9bp on 2017_2020 me, -1098.3bp on 2021_2023 me); E101 and E103 then showed the
  delta survives the end grid and the limit ladder while the levels themselves do not.
  Name the transitions that carry those moves, so the repair's effect is auditable by
  name and date instead of quoted as a level difference.

## The split is exact, and it lands on one window per cell

`level_arm` is an equal-weight mean over **that arm's own** transitions, so each shared
transition contributes `a_gap/n_gap - a_unscreened/n_unscreened`; a date present in only
one arm contributes its own term; the residual is published, not assumed to be zero.
Here there are **zero one-sided dates and residual 0.0 on every cell**, so the pieces add
up to the published delta exactly (control: all six published deltas reproduce at
≤0.05bp).

| era | book | published delta | transitions | window carrying it | share of delta |
|---|---|---|---|---|---|
| 2017_2020 | me | **-745.9** | 10 | **2020-12-31** → 2021-01-29 | **100.0%** (it is the only non-zero window) |
| 2021_2023 | me | **-1098.3** | 27 | 2021-06-30 → 2021-07-30 | top-3 61.6% (one window 30.7%) |
| 2021_2023 | mid | **-1117.2** | 29 | 2021-05-17 → 2021-06-15 | top-3 58.8% (one window 28.3%) |
| 2024_now | mid | **-241.0** | 27 | 2024-01-15 → 2024-02-19 | **101.7%** (one window, offset by others) |
| 2024_now | me | +4.9 | 28 | 2026-07-31 | one window |
| 2017_2020 | mid | 0.0 | 10 | — | every window reads 0.0 |

Five of six measurable cells: `delta_is_one_window`.

## The two arms hold the same names there

At the top windows there is **no composition difference at all**: 18 top windows carry
non-empty price drivers and `held_only_in_gap` / `held_only_in_unscreened` are empty in
every one of them, member counts identical (167/167, 218/218, 206/206, 636/636). The gap
arm does not pick different names inside these eras — it reads the **same** names
differently. So the published delta is a **price-read difference, not a portfolio
difference**.

## And the read it changes is a split artefact, by name

Each window's drivers are the swapped names whose forward read moves most between arms:

| cell | window | driver | unscreened read | repaired read |
|---|---|---|---|---|
| 2017_2020 me | 2020-12-31 | **sz159975** | **-89.54%** | +5.04% |
| | | sh510210 | **-79.98%** | -0.14% |
| 2021_2023 me | 2021-06-30 | **sh510580** | **-89.95%** | +1.02% |
| | 2021-04-30 | **sh510150** | **-91.20%** | +5.32% |
| 2021_2023 mid | 2021-05-17 | **sh510150** | **-91.63%** | +0.23% |
| | 2021-07-15 | **sh510580** | **-89.75%** | +3.05% |
| 2024_now mid | 2024-01-15 | **sz159925** | **+105.39%** | **+303.82%** |
| 2024_now me | 2026-07-31 | sh588920 | -46.58% | +6.93% |

A −90% one-window read on an ETF is an unadjusted split (1:10 scale), not a return. In a
10-transition era a single name reading −89.5% instead of +5% moves the cell's equal-weight
mean by ~750bp, which is *exactly* the published 745.9. The 2024 window is the mirror
case: the repaired read is the *larger* one (+304% vs +105%), so the artefact can push a
level either way.

## What this changes in how the E99 family may be cited

- Do **not** write "the gap arm cuts the 2017_2020 me level by 745.9bp". Write **"the
  unscreened panel prices `sz159975` at −89.5% across 2020-12-31→2021-01-29 (a split
  print); the repair reads +5.0%; that single name is the whole 745.9bp"**.
- The level is a **mean over few transitions** (10 in 2017_2020), so one name can carry
  the whole cell. A level with `transitions < ~30` should always be published with its
  largest single-name read (this leg's `drivers` column) beside it.
- E101/E102/E103 conclusions are unaffected in their own terms — they are statements
  about whether the DELTA moves with the end/limit, and it does not. But they must not be
  read as "the repair changes the book": **the books are identical; the prices are not.**
- The E102 sentence "gap1/gap2/gap5 agree so the repair is limit-insensitive" now has a
  mechanical reason: the arms differ only where a split print is repaired, and no limit
  inside the panel's 3-session gap spectrum repairs a different set of prints.

## Honest limits

- Descriptive only: no gate, no verdict on the strategy, no prereg, no trial count, no
  ledger booking.
- `drivers` are the names on the engine's own entrant/exit lists for that window; a name
  held in both decides nothing, so a split inside an unchanged holding would be invisible
  here even though it still moves the book's curve.
- The split diagnosis is inferred from the shape of the read (−89.5% ≈ 1/10 of a flat
  print) plus the repair's own report; it is not proven against the vendor's corporate
  action file.
- `pre2017` has no decision ends on this panel and stays `null`, not 0.