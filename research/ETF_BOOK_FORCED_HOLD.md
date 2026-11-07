# ETF book: what the censored half of the exit queue is worth

**Question.** r1237 reported 109 positions (2.78%) as outside_cap with no price attached; what are they worth when sold at the first print available?

**Panel.** 1515 funds x 5275 bars, 2005-02-23..2026-11-06, 169 quote flips repaired.

**Arm.** declared fill (score held one bar back, close t -> open t+1); rows imported from etf_book_exit_liquidity.measure_positions, never re-typed.

## Reading

| phase | start | holds | positions | tail | share | priced | open at end | mean ret | pp/yr | weight ceiling | gate-wait pp/yr | gate-wait median bars |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 2020-01-02 | 82 | 984 | 25 | 2.54% | 25 | 0 | +0.000 | +0.026 | 20.54 | +1.202 | 64 |
| 1 | 2020-01-09 | 82 | 984 | 28 | 2.85% | 28 | 0 | +0.000 | +0.095 | 24.58 | +1.557 | 62 |
| 2 | 2020-01-16 | 82 | 984 | 33 | 3.35% | 33 | 0 | +0.000 | +0.067 | 26.02 | +1.506 | 54 |
| 3 | 2020-01-23 | 82 | 984 | 23 | 2.34% | 23 | 0 | +0.000 | +0.013 | 18.46 | +0.497 | 57 |

**Verdict: `CENSORED_TAIL_IS_IMMATERIAL`** -- the tail is worth +0.05 pp/yr when sold at the first print available (range +0.01..+0.10), inside the 0.57 pp material line.

109 of 3936 positions sit in the tail (109 in the sibling face's `outside_cap` bucket); 0 could not be priced at all and are reported as `open_at_end` rather than as zero.

**The control.** This face speaks for the same census the sibling published, or it does not speak: expected 3924 positions / 109 outside_cap / 4.23% below gate, measured 3936 / 109 / 4.21% -> **same census**.

**The other definition, kept separate.** If instead of taking the first print you wait for the name to clear the 20M gate again, the same bucket reads +1.19 pp/yr -- a median wait of ~60 bars, which is mostly time in the market rather than a liquidity effect. The two arms answer different questions and are never added.

## 它量的是什么，不是什么

- the published number is pp/yr of weight x (sale_px / ref_px - 1) divided by that phase's own span in years: an attribution of stuck capital, not a CAGR
- a name that stops printing is open_at_end: counted and disclosed, never scored 0 and never scored as a loss
- gate_wait_pp_per_year is the OTHER definition (sell at the first bar where the name clears the 20M gate again). It waits a median of ~60 bars, so it also collects the market's drift over those bars -- it is printed beside the first-print arm, never added to it
- this face may only publish a verdict while the imported census reproduces the sibling face's totals; otherwise it reports CONTROL_DOES_NOT_REPRODUCE_THE_SIBLING_CENSUS
- what is NOT measured here: impact, spread, and the terminal value of names that stop printing (counted as open_at_end, disclosed, never guessed);
- the freed capital is not reinvested anywhere in this face, so the number adds to the exit face's reading and never replaces it.

## 复跑

```
python scripts/etf_book_forced_hold.py run
python scripts/etf_book_forced_hold.py --check
python scripts/etf_book_forced_hold.py --selftest
```
