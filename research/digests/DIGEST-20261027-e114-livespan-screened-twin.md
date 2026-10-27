# E114 — the one-cut era split on the screened arm: the flip flag survives, the halves do not

Face: `results/e44_burnin/LIVESPANSCREEN-20261026.json` (arms beside it as
`LIVESPAN-arm-raw-20261026.json` / `LIVESPAN-arm-neutralise_int-20261026.json`),
evidence_cutoff 2026-10-26. Leg: `scripts/e39_panel_census.py livespanscreen`
(selftest 343 → **348/348**). Pool row `E114-LIVESPAN-SCREENED-TWIN`.

## Why this leg exists

E97 row 3: `run_livespan` carries 471 numbers (it feeds both `e46` and
`livespan`) and had no screened twin. E113 had just shown that one face can hold
several stability classes at once, so this leg was written to test that claim on
a *different* face family rather than to re-answer it: the split publishes an era
level, a dispersion band, the per-part spreads, a widest-part pointer and a
"does this era flip sign inside itself" flag.

Cost: the `raw=` seam and `_burnin_pair_rows(cells_fn, dates_fn)` were already in
place after E113, so the ticket needed one harvest pair and one burn. Both arms
re-derive the split at parts=2, cost ×1, off one load at one cutoff; screen =
`neutralise_int`, 67 prints on 67 of 1,317 names, names in = names out.

## The measurement

44 cells per arm (11 per era × 4 eras) + 8 era-edge strings.

| reading | repair (arm) | refresh (cutoff) |
|---|---|---|
| era edges (`from`/`to`) | 0 of 8 moved | 0 of 8 moved |
| `sign_flips` + `widest_part` | **0 of 8 moved** | 0 of 8 moved |
| era level | 2 of 4 moved (+29 / +58) | 1 of 4 moved (−6) |
| dispersion (band + part spreads) | 6 moved (max −232 pp) | 5 moved (max ±12 pp) |

### 1. The newest-era level carries the same +58.0bp on two independent faces

* cut sweep (E113, `era_spread_bp` at every cut): 83.0 → 141.0 = **+58.0**
* era split (this face, `era_spread_bp`): 83.0 → 141.0 = **+58.0**

Two different aggregations of the same warm pair — one slicing the whole history
into 2..12 parts, the other reading the era whole — land on the identical number,
and 2021_2023 reads +29.0 on both. That is the kind of cross-face agreement worth
quoting: the repair shifts the newest era's ladder-vs-wide level by ~58bp and it
is not an artefact of how the era was cut.

### 2. What the repair actually does to the newest era: it removes the negative half

At parts=2 the newest era splits into two halves that disagree in sign, in both
arms:

| newest era, part | raw | screened | Δ |
|---|---|---|---|
| part 1 spread | +379 bp | +320 bp | −59 |
| part 2 spread | **−227 bp** | **−54 bp** | **+173** |
| band (max − min) | 606 bp | 374 bp | −232 |
| part 2 wide ann % | 9.58 | 11.31 | +1.73 |
| part 1 wide ann % | 12.66 | 12.07 | −0.59 |

So the era's headline +83bp is an average of a strongly positive first half and a
negative second half, and the repair eats most of that negative half. The era
still flips sign inside itself afterwards (−54 vs +320), which is why the flip
flag does not move even though the dispersion collapses by 232bp.

### 3. The flip flag and the widest part are arm-free — and here that is cheap

Zero moves on both axes. But note *why* this is weaker evidence than E113's flip
count: at parts=2 a flip only needs the two halves to disagree in sign, and the
raw halves disagree by 606bp, so almost any repair short of a rescale leaves the
boolean unchanged. The boolean is scale-free by construction; the magnitude it is
built from is exactly the part that moved 232bp. Quote the flag, never the band.

## Three controls, all published

| control | isolates | result |
|---|---|---|
| identity (raw vs raw) | join machinery | 0 of 44 cells, 0 of 8 edges |
| coverage | is the twin a twin? | 44 compared, 0 one-sided, 0 null |
| cutoff (`LIVESPAN-20261020` raw vs today raw, arm fixed) | panel refresh (+4 bars) | 9 of 44 cells, max Δ 12 pp; `bars` 675 → 679; edges 0 |

The refresh control is small here (−6 bp on the same level, ±12 bp on the part
spreads) and concentrated in the newest era, which is what a four-session
extension of an era should look like. Combined with E113's 16/22 window moves,
the pattern is consistent: **levels move a little, pointers move a lot.**

## What survives, and what this does not say

* Survives: era edges, the flip flag, the widest part, and the level shift itself
  (which is corroborated by E113 to the decimal).
* Does not survive: the dispersion picture — the newest era's part-2 spread moves
  +173bp and its band −232bp between arms. Any statement of the form "the newest
  era's second half is a losing half" must carry its arm; the raw arm makes it
  look twice as bad as the screened arm does.
* Not a strategy verdict: descriptive census, no gate, no prereg, no trial count,
  no ledger booking.
* One cut per ticket: the face publishes `parts`/`cost_mult`; a twin is only
  comparable to a published face with the same pair (this one is parts=2, ×1).