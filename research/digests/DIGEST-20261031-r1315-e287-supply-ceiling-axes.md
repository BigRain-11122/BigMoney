# E287 - the family's ceiling sits above every supply the family already publishes

**Round** r1315 (bm-b) · **evidence_cutoff** 2026-10-29 · **card** E294 · **pool** E287-ABOVE-CEILING-CROSS-FACE

## The question E285 left open

E285 measured six rows whose flip multiplier sits above the family's published p95 ceiling of
2.2963 and called them extrapolation rather than widening headroom. That label rests on one
assumption: that 2.2963 is the widest multiplier anything in the family publishes. Six dated band
faces publish a number called `multiplier` / `multiplier_max`, and if one of them is both on the
same axis and larger, one of those six rows would already be reachable with no new measurement.

The trap is that "multiplier" is not one quantity, and the family publishes several of them.

## Signing the axis first

The flip multiplier is defined as `b = edge * m`, i.e. **a factor applied to both band edges**. Only
a number of that shape may be compared with it:

| face | published quantity | axis | direction | used as supply? |
| --- | --- | --- | --- | --- |
| BANDWINMULT (E258) | edge(top draws)/edge(published draws), per window x base | band-edge multiplier | widen | **yes** |
| BANDTOPFLIP (E257) | the borrowed ladder range of the same multiplier | band-edge multiplier | widen | **yes** |
| BANDFLOOR | `lo_top / lo_base` of the counterfactual 5 pct band | band-edge multiplier | narrow | **yes** |
| BANDFLIPBUDGET (E272) | published p05/p95 tail ranges | band-edge multiplier | widen | no -- circular |
| BANDDISAGREE / BANDDEFLATE | the same flips, restated | band-edge multiplier | demand | no |

Three numbers look wider and are refused explicitly, each with its reason printed on the face:

| value | what it actually is |
| --- | --- |
| 63.03 pct | a relative tolerance a test could allow before a reading fires -- a looser test is not a wider band |
| 2.0327 | a threshold on the **normalised gap measured in spreads**, not a multiplier of any band |
| 9.90 | the widest arm top of E272 -- the instrument E285's ceiling was read *off*, so using it as supply compares the ceiling with itself |

## What the supplies offer

| reading | widening cap | narrowing cap |
| --- | --- | --- |
| conservative (central value per face) | **1.838251** (E258, early_three base 60, median over seeds) | **0.922022** (E285's counterpart band) |
| optimistic (most extreme single seed) | **2.245734** (same window/base, one seed) | 0.922022 |
| family ceiling | **2.296329** | floor 1.000000 |

So no usable supply exceeds the ceiling, and the optimistic offer falls **2.2 pct** short of it.

## Reach

| class | rows | reached at the median cap | reached at the single best seed |
| --- | --- | --- | --- |
| above the ceiling | 6 | 0 | 0 |
| in the inter-range gap | 2 | 1 | 2 |
| below the floor | 2 | 0 | 0 |

The nearest above-ceiling row is `self|200|0` at flip 2.331055 -- still **3.8 pct** past the best
single seed. The two gap rows, which E285 could only describe as needing an extension of an
interval, are already inside what the family measured: `cross|60|11` (1.802978) at the median,
`star_lag1_residual|60|15` (1.884308) only at the single best seed. On the opposite polarity the
published narrowing instrument misses the nearest below-floor row (`self|60|8`, 0.889387) by
**3.7 pct** -- neither margin is closed by anything already on the shelf.

## Reading

One ceiling, not many: the six numbers that could have been wider are either on another axis or
already below 2.2963, and the six above-ceiling rows stay extrapolation. But the answer is not "no
headroom anywhere" -- the two gap rows are the one place existing supply could pay, which makes the
gap a real target and the extrapolation zone a real wall, and it puts both margins (3.8 pct up,
3.7 pct down) within a single step of what has been measured.

## Pit

The verdict was first written with a `nearest_gap` of `null`, because the helper I used to name the
"closest row still short" filtered on a non-null shortfall and both gap rows are *reached* at the
optimistic cap -- the class being closed produced an empty field where the reader expected a number.
Fixed by publishing `all_rows_reached_at_optimistic` instead of a fabricated nearest. Second: my
first selftest leg asserted every narrowing reading is below 1.0, which is false -- E258's per-seed
minimum of a *widening* multiplier can still be above 1 -- so the leg was pinned to the partition
that actually holds (every widening cap >= 1, at least one narrowing cap < 1).

## Evidence

`scripts/e287_supply_ceiling_axes.py` (selftest 22/22, verify 0 problems) ·
`results/state_tilt/BANDSUPPLY-2026-10-29.json` + `bandsupply_latest.json` · chain leg
`supply_ceiling_axes` (rc=0, 0.30s) · smoke leg extracted verbatim and executed (PASS, and FAILs
when a reach count is mutated while the verdict stands still) · card `knowledge/METHODOLOGY_ASSETS.md` E294.