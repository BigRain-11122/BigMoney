# E140 — The ETF cross-section has no second book; the futures panel does (weakly)

Round r1297, bm-c, 2026-10-27. Tools: `scripts/etf_book_bakeoff.py` (selftest 10/10),
`scripts/futures_tsmom_probe.py` (selftest 6/6). Faces: `results/etf_book_bakeoff.json`,
`results/futures_tsmom_probe.json`. evidence_cutoff 2026-10-26.

## The question

The capacity study (r1280/r1295) closed "make the shipped book bigger": at 1% of ADV it
holds ~1.5M CNY. The only lever left was a **second, low-correlated, positive-expectancy
book**. r1296 killed the first candidate (short-horizon reversal). This round answers the
question in one pass instead of one mechanism per round, then moves the search to a
different universe.

## Part 1 — five ETF cross-section mechanisms, all rejected

Same panel the production card prices (class-restricted, 168 split prints repaired), same
open-to-open execution, same 10bp/side, same 8% vol target. Control arm **is** the shipped
book: computed 9.49% vs the published card's n12_vt08 9.49% (delta 0.0pp, tolerance 0.5pp
pinned by a selftest leg — the r1296 error was pricing "book A" from a rebuilt panel).

| candidate | CAGR | Sharpe | maxDD | OOS CAGR | corr vs shipped | shared names | 50/50 blend | verdict |
|---|---|---|---|---|---|---|---|---|
| breakout_12 (dist. to 60d high) | +7.47% | 0.81 | −12.6% | +14.0% | 0.752 | 87.9% | +8.63% | same trade |
| lowvol_12 (short-horizon low vol) | +6.11% | 0.61 | −14.7% | +11.3% | 0.622 | 87.9% | +7.91% | blend loses to A |
| mom60_10 (60d momentum, 10d cadence) | +2.77% | 0.35 | −20.6% | +5.6% | 0.542 | 36.1% | +6.28% | blend loses to A |
| rand_12 (seeded random, null control) | −0.27% | 0.02 | −32.1% | +4.4% | 0.563 | 45.8% | +4.67% | loses money |
| rev5_10 (r1296 reference) | −3.67% | −0.37 | −33.6% | −1.7% | 0.461 | 7.2% | +2.84% | loses money |

Two readings that matter beyond the table:

* the reversal arm reproduces r1296 **exactly** (−3.67%, corr 0.461, 7.2% overlap), which
  is the harness checking itself against a published number rather than one book per round.
* the random control is flat (−0.27%) on this panel. A random 12-name book on the ETF
  universe does not earn the equity drift, so book A's +9.5% is selection, not beta.

Conclusion: the mechanisms that make money in this universe are the same trade as book A
(0.62–0.75 correlation, 88% name overlap); the ones that are different trades lose money.
**The ETF cross-section does not contain a second book.** No amount of further ETF-side
screening changes the capacity ceiling.

## Part 2 — a sleeve in a different universe: futures TSMOM

`data/futures_daily/` has 10 main-continuous varieties (AU, IC, IF, IH, IM, RB, SC, T, TF,
TS), 2008-01-09 → 2026-10-26, 4,577 bars. Classic time-series momentum: sign of the
trailing return, risk-parity sizing at 8% vol (|w_i| ≤ 2, gross ≤ 3), 1bp/side, one-bar
execution lag. Contract multipliers are absent by construction (risk sizing), and margin,
financing and roll cost are **not** modelled — stated, not smoothed.

| arm | CAGR | Sharpe | maxDD | OOS CAGR | vs ETF corr | flips |
|---|---|---|---|---|---|---|
| tsmom60 | +1.37% | 0.27 | −11.2% | +2.65% | **0.078** | 1,133 |
| tsmom120 | +1.84% | 0.36 | −13.6% | +3.92% | **0.045** | 774 |
| long_only (no timing) | +2.62% | 0.48 | −22.2% | +8.03% | — | 0 |
| random_sign (null) | −5.63% | −1.28 | −67.1% | −1.98% | — | 0 |

The sign carries content (random signs lose 5.6%/yr), the sleeve is genuinely orthogonal
(0.045–0.078 correlation over the 2020–2026 common window), and it is small: 1.4–1.8%/yr.

**Comparing blends at fixed weights would have answered the wrong question.** A 50/50
blend de-levers the 10.2%-vol ETF book, so its lower CAGR (+6.5%) is a leverage artefact.
At equal risk (all three scaled to the ETF book's own 10.17% realised vol):

| at 10.17% vol | CAGR | Sharpe | maxDD |
|---|---|---|---|
| ETF book alone | 9.60% | 0.990 | −11.8% |
| 50/50 with tsmom60 | **10.36%** | **1.060** | −11.4% |
| 50/50 with tsmom120 | 10.14% | 1.040 | **−10.2%** |

So the sleeve adds ~+0.5–0.8pp of CAGR at the same risk, and its capital lives in a market
with no ETF ADV constraint — the thing the capacity study said was needed.

Two honest caveats, both visible in the table: (a) **long-only beats the timed book out of
sample** (+8.03% vs +2.65%), so the sleeve's value is the long commodity/bond exposure plus
its near-zero correlation, not the timing rule; (b) 10 varieties, spliced continuous
series, no carry/margin/roll modelling — this is a reason to build a real sleeve, not a
number to trade.

## Verdict

* ETF cross-section: **closed** as a second-book source (five mechanisms, all rejected).
* Futures TSMOM: **the first candidate that is additive at equal risk** — modest, but
  orthogonal and capacity-free. Next step is a proper feasibility slice (contract
  multipliers, roll convention, carry, real commissions, margin) before any claim of a
  tradeable second book.

## Reproduction

```
python scripts/etf_book_bakeoff.py --selftest      # 10/10
python scripts/etf_book_bakeoff.py                 # ~3 min, writes results/etf_book_bakeoff.json
python scripts/futures_tsmom_probe.py --selftest   # 6/6
python scripts/futures_tsmom_probe.py              # ~80s, writes results/futures_tsmom_probe.json
```