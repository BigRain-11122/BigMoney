# E113 — the cut sweep on the screened arm: which reading of a cut curve is reusable?

Face: `results/e44_burnin/CUTCURVESCREEN-20261026.json` (arms beside it as
`CUTCURVE-arm-raw-20261026.json` and `CUTCURVE-arm-neutralise_int-20261026.json`),
evidence_cutoff 2026-10-26. Leg: `scripts/e39_panel_census.py cutcurvescreen`
(selftest 338 → **343/343**). Pool row `E113-CUTCURVE-SCREENED-TWIN`.

## Why this leg exists

E97's routing table ranked the uncovered charged modes by how many published
numbers each carries; E112 priced row 1 (`run_burnin`, 1,727 numbers) and this is
row 2: `run_cutcurve` carries **1,139 numbers** and had no screened twin. The
sweep is the one face that answers "how does the ladder-vs-wide spread move when
you change the cut?" — so the question is not whether its numbers move under a
party repair (they do) but **which of its three answers is still worth quoting
afterwards**: the flip count, the era level, or the widest-part window.

## The measurement

Both arms burn off **one load** of the panel at **one cutoff** through the same
sweep (`run_cutcurve(raw=...)` → `_livespan_setup(raw=...)`; the default path is
untouched for every existing face). The screen is `neutralise_int`: 67 prints on
67 of 1,317 names, every one integer-like, 0 non-integer adjacent prints skipped,
**names in = names out = 1,317** — a neutralising repair cancels a print, it never
drops a name, so eligibility cannot move by construction.

The join is the **same** `_burnin_pair_rows` E112 built, generalised to take a
cell harvest and a date harvest; the cutcurve harvest is 3 summary cells + 3 era
cells per (cost, cut) = **330 cells per arm**, and the date join is the
`widest_window` string per (cost, cut, era) = 22 pointers.

| reading | cells | repair (arm) | refresh (cutoff) | verdict |
|---|---|---|---|---|
| `flip_count` | 22 | **0 moved** | **0 moved** | quotable bare |
| era level (`era_spread_bp`) | 88 | 44 moved (2 of 4 eras) | 22 moved (1 of 4 eras) | quote with arm + cutoff |
| band / `widest_part` | 176 | 80 moved | 44 moved | dispersion only |
| `widest_window` | 22 | **2 moved** | **16 moved** | a pointer at (arm, cutoff) |

### 1. The flip count is arm-free *and* refresh-free

Flip counts are identical between arms and against the 2026-10-20 published face,
at both cost levels, for every cut: `{2:1, 3:3, 4:3, 5:3, 6:4, 7:4, 8:4, 9:4, 10:4,
11:4, 12:4}`. This is the only reading on the face that survives both axes, which
makes "at 6 parts and above every era's spread flips inside the era" safe to cite
without qualification.

### 2. The era level is cut-invariant, but not arm- or cutoff-invariant

`era_level_drift_bp` in the published E58 face already reads **0.0 for every era
at both cost levels**, and this face reproduces it: the newest era sits at
**83.0 bp at all eleven cuts** (raw arm), 141.0 on the screened arm. The cut axis
therefore carries *dispersion only* — slicing one warm curve into more parts
cannot move a level, so any claim about a level is answered by the cut it is
reported at and says nothing about the cut.

What does move a level is the panel:

* repair: `2017_2020` and `pre2017` **0.0**, `2021_2023` **+29.0**, `2024_now`
  **+58.0 bp** (57.0 at x3) — and the delta is **identical at every one of the
  eleven cuts**, so the arm shifts the level uniformly and never reshapes the cut
  axis;
* refresh (2026-10-20 raw vs today raw, arm held fixed): `2024_now` **89 → 83 bp**
  (−6.0), again uniform across all eleven cuts; the other three eras 0.0.

Two arms and one refresh move the same era by +58 and −6 bp. A level quoted
without its arm and its cutoff is therefore off by up to 58bp on a number whose
whole range across cuts is 0.0.

### 3. The widest window is the least reusable number on the face

The sweep's headline ("the widest part of the newest era is this window") moves
under **both** axes:

* repair, cut 5, both costs: raw picks `2024-07-25..2025-02-18`, screened picks
  `2024-01-02..2024-07-24` — the two adjacent halves of the era swap places;
* refresh: **16 of 22** windows move. Eleven of them are edge shifts of 1–3
  sessions because the panel gained four bars (`..2026-10-20` → `..2026-10-26`,
  `2024-01-02..2025-05-28` → `..2025-05-30`); two are wholesale changes
  (`x1/c12`: `2026-07-22..2026-10-20` → `2025-05-28..2025-08-14`).

So the answer to the ticket's question is **no**: the widest-window reading is
not arm-free. Quoting a window names the swap that carried it at one arm and one
cutoff; the string is not reproducible from the spec alone.

## Three controls, all published

| control | isolates | result |
|---|---|---|
| identity (raw vs raw) | did the join machinery move anything? | 0 of 330 cells, 0 of 22 windows, max Δ 0.0 |
| coverage | is the twin a twin? | 330 compared, 0 one-sided, 0 null-on-either-side |
| cutoff (`CUTCURVE-20261020` raw vs today raw, arm fixed) | the panel refresh | 68 of 330 cells, 16 of 22 windows, max Δ 1,175 bp |

The cutoff control is again load-bearing, and on this face it is the *window*
column that it destroys (16/22) rather than the levels (22/88). A reader comparing
two cut sweeps a week apart would otherwise price a four-session panel extension
as a repair effect on the "widest part".

## What survives, and what this does not say

* Survives: the flip-count reading (both axes, all cuts, both costs) and the
  cut-invariance of era levels. Those are properties of the slice geometry.
* Does not survive: the widest-window pointer, and the band magnitude
  (`band_mean_bp` moves up to 121 bp at x1/c12 between arms, in both directions
  across cuts — c2 −72.5, c3 +10.2, c12 +121.0 — so it is not a bias either).
* Not a strategy verdict: descriptive census, no gate, no prereg, no trial count,
  no ledger booking.
* One sweep per runner: `run_livespan` (E97 row 3, 471 numbers) shares
  `_livespan_setup` and therefore the same `raw=` seam, but keeps its own ticket —
  and it is now nearly free, since the seam and the join are in place.