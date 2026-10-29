# E230 -- can the toll channel be bought back with a hysteresis deadband?

Round r1256 · bm-b · evidence cutoff 2026-10-29 · pool card
`E230-HYSTERESIS-TOLL-BAND`

## What the card asked

E229 split each gated arm's paired series into selection / sizing / toll and found the
toll was the only channel clearing its bar (`tilt_step`, `tilt_linear` on the basket,
t ~ -10). The toll is charged on `|dw|`, one side per unit of weight movement, so the one
instrument that can buy it back is making the rule move less often. The card's question
is exact: **does a hysteresis deadband on the volatility state cut the toll faster than
it costs in selection?**

## The rule

Hold the committed weight until the signal has travelled `band` away from the value it sat
at when that weight was committed:

```
if |v_i - v_at_last_commit| >= band:  commit weight_at(sig, i, arm); last_commit = v_i
else:                                 hold
```

`band = 0` commits every session and *is* the base arm exactly -- that identity is a
selftest leg, not a claim. The band grid is `0, 0.10, 0.25, 0.50, 1.00, 2.00` times the
**in-sample** standard deviation of the signal (`sd_is` = 77.0 bp single / 85.4 bp basket),
so the band itself cannot see the future. Three arms (binary_low, tilt_step, tilt_linear),
two panels, x1 and x2 costs, bar `|t| >= 3.34` over 60 cells.

One design point that is not cosmetic: the three channels are computed against **one
frozen constant per (panel, arm)** -- the base arm's own OOS average weight -- so rungs are
comparable. E229's per-arm match would re-derive the constant at every rung and every rung
would then have a different benchmark.

## Base arms (reproduce E229 exactly)

| panel | arm | pair | selection | sizing | toll | changes |
|---|---|---|---|---|---|---|
| single | binary_low | -519.8 | +261.4 | -579.6 | -201.6 | 154 |
| single | tilt_step | -637.6 | -29.9 | -424.9 | -182.8 | 276 |
| single | tilt_linear | -709.7 | -31.1 | -509.7 | -168.9 | 1140 |
| basket | binary_low | +227.0 | +265.5 | +83.1 | -121.6 | 118 |
| basket | tilt_step | -183.3 | -83.0 | +26.7 | -127.1 | 241 |
| basket | tilt_linear | -170.4 | -84.7 | +49.0 | -134.7 | 997 |

(bp/yr, x1 costs. These are E229's published numbers to the decimal, which is the
crosscheck: the base rung of a ladder has to be the thing the ladder is about.)

## What the ladder found

The band works mechanically: across 30 banded cells it removed between 36 and 1,138 weight
changes (12,585 in total) and the toll channel moved with it, +81 to +399 bp/yr at x2 costs.
The selection channel moved -243 to +290 bp/yr against it. Verdicts:

| verdict | cells |
|---|---|
| BAND_PAYS (a fix) | **1** |
| BAND_COSTS | 5 |
| BAND_NOISE (point estimate only) | 24 |
| BAND_PAYS_TOLL_SHORT | 0 |
| NO_EFFECT | 0 |

The one cell called a fix is `tilt_linear` on the single panel at the narrowest band
`f = 0.10`: pair +285.9 bp/yr, `t = 4.04`, toll saving +113 bp/yr at x2 against a
selection loss of -42 bp/yr, with 295 weight changes left against the base arm's 1,140 --
so it is still a rule, not a degenerate hold. It clears the 3.34 bar, which was set over
60 cells including both cost levels, so it is not a multiple-testing artefact of the ladder.

Everything else does not resolve. That is the honest headline: **the toll is buyable, but
the buy rarely pays for itself within the sample.** Toll savings are real, monotone and
large in every cell; the selection cost that comes with slowing the rule is of the same
order and noisy in sign, so 24 of 30 rungs move the pair in the right direction without
clearing the bar.

## The trap this study had to disclose

At the widest band the toll saving peaks (+398 bp/yr) and the pair improves -- because the
rule collapses. Six of 30 rungs sit at or below **5** weight changes over the whole sample
(3,504 single / 5,269 basket sessions): those cells have not slowed the rule, they have
replaced it with a buy-and-hold at roughly the base exposure, which is the null arm. Any
toll saving there is the null's zero turnover, not a fix. The face carries
`rule_collapsed` per rung, `rule_collapsed` in the ladder summary, a sentence in `answer`,
and a smoke leg that refuses a `BAND_PAYS` cell whose rule collapsed. The single cell
above is not one of them.

Second disclosure, printed in `frozen_spec.known_mechanical`: the toll is exactly linear in
the cost parameter, so `d_toll(x2) == 2 * d_toll(x1)` identically -- the x2 limb of the
frozen condition can never fail once x1 passes. It is reported because the card asks for
x2 costs, and it is labelled because otherwise it reads as a result.

## Files

* `scripts/e230_hysteresis_toll.py` -- run / selftest, 15 hermetic legs
* `results/state_tilt/HYSTERESIS-2026-10-29.json`, `hysteresis_latest.json`,
  `hysteresis_by_rung_2026-10-29.csv`
* S6 leg `hysteresis_toll` (after `timing_selection`)
* smoke leg: re-adds every rung's split, refuses a fix under the bar, refuses a fix on a
  collapsed rule, requires a rung-0 baseline per arm
* methodology card E230