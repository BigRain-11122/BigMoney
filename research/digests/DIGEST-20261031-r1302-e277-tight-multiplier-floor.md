# DIGEST 2026-10-31 r1302 (bm-b) -- E277: the tight multiplier floor is the band build

**Face:** `results/state_tilt/BANDFLOOR-2026-10-29.json` (+ `bandfloor_latest.json`)
**Runner:** `scripts/e277_tight_multiplier_floor.py` -- selftest 23/23, verify 0 problems
**Card:** pool `E277-TIGHT-MULTIPLIER-FLOOR` (done, result_ref attached); banked as methodology E278

## Question

E272 measured both tails of the flip budget on one ruler: the wide tail reaches 2 of 12 rows (exactly
E262's moved rows) and the tight tail reaches none, because every published p05 in the family is
>= 1.0000 while 10 of 12 flips need a multiplier LARGER than that.  Is "the tight end never narrows"
a fact about these windows, or about how a band is built?

## Answer

The build.  `BAND_PCT = (0.0, 100.0)` with `lo = vals[floor(pct/100*(n-1))]` makes lo the MINIMUM of
the per-draw coefficient over a nested prefix; the minimum of a growing sample can only move outward,
so m = |lo|(top)/|lo|(base) >= 1 for base < top while the extreme is negative.  The published draw
exponent says the same thing numerically: gamma 0.348 (head) / 0.647 (tail), endpoint rose on 6 of 7
rungs, minimum rise 0.0% -- it never narrowed once.

## Census (published faces only, no draws)

| face | p05 | range lows | min | below 1.0 | exactly 1.0 |
|---|---|---|---|---|---|
| BANDBUCKET | 32 | 0 | 1.000000 | 0 | 8 |
| BANDNEAR1 | 4 | 0 | 1.000000 | 0 | 4 |
| BANDSTRADDLESWEEP | 0 | 72 | 1.0 | 0 | 0 |
| BANDTRANSFER | 16 | 0 | 1.000000 | 0 | 8 |
| BANDWINDIST | 16 | 0 | 1.000000 | 0 | 8 |

Totals: **140 lower ends, 0 below 1.0, 39 exactly 1.0.**  The exact ones are the degenerate branch --
the extremum arrived inside the base prefix -- and BANDNEAR1 already publishes the proof: drop one
seed and those rows lift to 1.11..1.20.

## Counterfactual

Same synthetic stream (seed frozen 20261031), two rules:

- extremum band (the family's rule): m = 1.0000
- 5% band: m = **0.9220**

So the floor is a property of the rule, not of the sample.  A percentile band would revive every
tight-end question the family has been answering with zeros.

## Verdict

`tight_end_dead_by_construction_family_should_stop_publishing_tight_pass_checks`

Consequence: a tight-pass check on this family can only ever return zero; stop publishing them, or
change the band rule and say so in the same breath.

**Scope published on the face:** the monotonicity holds only while the endpoint's extreme is on the
negative side.  An all-positive draw stream shrinks |min| and m < 1 becomes reachable -- that branch
is carried as a named alternative with its own selftest leg.

## Pits

1. The first census walked `*_latest` mirrors beside their dated twins (136 p05 for 68 real) -- a
   family census must exclude mirrors explicitly and list what it excluded.
2. The face's own counterfactual first read m = 1.0000 on the *extremum* leg because the synthetic
   gaussian put its minimum inside the base prefix -- the very degeneracy the face is about.
   Strictness now uses a stream whose extreme arrives after the base; degeneracy has its own leg.

## Wiring

- S6 leg `tight_multiplier_floor` -- rc=0, 0.11s (`Tools/s6_chain_bmb.py`)
- smoke leg `the tight multiplier floor is the band build` -- 1/1 PASS standalone through the
  verbatim-source harness (full suite ~35 min, not run this round)