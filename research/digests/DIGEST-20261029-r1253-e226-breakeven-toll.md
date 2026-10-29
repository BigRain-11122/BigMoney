# DIGEST 2026-10-29 r1253 bm-b -- E226: the tilt's break-even toll, and survival that is not a verdict

Face: `results/state_tilt/BREAKEVEN-2026-10-28.json` (+ `breakeven_latest.json`,
`breakeven_by_arm_2026-10-28.csv`). Runner: `scripts/e226_tilt_breakeven.py`
(run / selftest, 18/18 legs). Card: `knowledge/METHODOLOGY_ASSETS.md` E227.
Pool: `E226-TILT-BREAKEVEN-COST` done. Chain: S6 leg `tilt_breakeven` after `state_tilt`.

## What the question was

E225 ended with five arms that all lost after the drift they normalised to was charged
back, gate-specific residuals between -200 and -704 bp/yr. One question remained and it
was arithmetic, not a new study: the toll is a per-unit-turnover charge, the tilt pays it
4-11 times a year, so in the cost `c`

    gate_specific(c) = gate_specific(0) - c * D
    c* = gate_specific(0) / D          (D = arm turnover/yr - avg_w * null turnover/yr)

One root. The question the card asked: at what cost per unit of turnover does the best
gate-specific arm cross zero, and is that below a plausible traded cost?

## The frozen band, declared before the run

- `PLAUSIBLE_LOW_BP = 5.0` -- a wide-base ETF one-way all-in: half-spread 1-2bp plus
  impact 1-3bp. The optimistic end of a real fill.
- `PLAUSIBLE_HIGH_BP = 13.041` -- the frozen model cost (E222's unit cost, already
  punitive for an index ETF).
- Bands: `<0` DEAD_AT_ANY_PRICE / `[0,5)` NEEDS_CHEAPER_FILL / `[5,13.041)` FILL_DEPENDENT
  / `>=13.041` SURVIVES_MODEL_COST, and UNDEFINED where `D <= 0` (nothing to solve),
  UNASSESSABLE below 252 OOS decisions.

## Result: primary panel -- dead at any price

sh510300, 3,503 sessions 2012-05-28..2026-10-28, 1,401 OOS decisions:

| arm | gate-specific @ c=0 | D (units/yr) | break-even c* | verdict |
|---|---|---|---|---|
| binary_low | -324.4 | 15.289 | **-21.216** | DEAD_AT_ANY_PRICE |
| tilt_step | -455.2 | 13.940 | -32.657 | DEAD_AT_ANY_PRICE |
| tilt_linear | -534.7 | 12.947 | -41.297 | DEAD_AT_ANY_PRICE |
| voltarget | -173.9 | 2.014 | -86.355 | DEAD_AT_ANY_PRICE |

All four gated arms need a **negative** cost: the gross rule loses before it is charged
anything. This is the strongest form of the E225 result -- it is not that the tilt is too
expensive to run, it is that cheaper execution cannot help, because the loss is already
there at zero toll.

Note the two rankings name different arms. The largest gross gate-specific residual is
voltarget (-173.9 bp/yr); the highest break-even is binary_low (-21.2 bp/unit), because
voltarget pays only 2.0 units of turnover a year and so needs a very negative price to fall
to zero. An earlier draft of this face printed "the best gate-specific arm (binary_low)". It
now publishes `best_gate_specific_arm` and `best_break_even_arm` as separate fields, with a
selftest leg on a fixture where they disagree.

## Result: basket -- one root above the model cost, and why that is not good news

Equal-weight basket, 5,268 sessions 2005-02-23..2026-10-28:

| arm | gate-specific @ c=0 | D | c* | verdict |
|---|---|---|---|---|
| binary_low | +340.1 | 9.329 | **36.454** | SURVIVES_MODEL_COST |
| tilt_step | -55.2 | 9.748 | -5.667 | DEAD_AT_ANY_PRICE |
| tilt_linear | -37.8 | 10.297 | -3.674 | DEAD_AT_ANY_PRICE |
| voltarget | -346.6 | 3.753 | -92.361 | DEAD_AT_ANY_PRICE |

At the frozen 13.041bp that surviving arm's own excess is **+1.8 bp/yr at t=0.01** -- the
null arm in that panel lost -662 bp/yr, so the +340 gate-specific residual is the drift
attribution, not money the tilt earned. `any_survivor_clears_the_bar: false`.

The two readings disagree deliberately: the same rule dies on one instrument and its root
lands above cost on five. Because the surviving arm's excess is indistinguishable from
zero, the disagreement is not evidence for the rule -- it is evidence that a drift-split
residual can be positive for a rule that earned nothing. Published as
`breakeven_vs_significance`, with every survivor's excess and t at the model cost beside
its root.

## The pit that the selftest caught

My first version asserted *"the excess-basis root is stricter than the gate-specific one"*.
It failed: excess -9.416 vs gate-specific -31.630. The two lines differ by
`avg_w * null_excess`, which is constant in `c`, so which root is larger **flips with the
sign of the null arm's drift** -- on a negative root, "stricter" means more negative, and
my inequality pointed the other way. Replaced with the identity
`excess_root - gate_root == avg_w * null_excess / D` (measured 22.2140 vs expected 22.2140
bp/unit), which holds whichever way the signs fall.

## Fragility, disclosed rather than hidden

`root_fragility = 1/D` (bp per unit of cost per bp/yr of residual). voltarget pays only
2.0 units/yr on the single panel, so 100 bp/yr of measurement error moves its root 50
bp/unit. Its root is exact arithmetic on a nearly flat line -- the face says so.