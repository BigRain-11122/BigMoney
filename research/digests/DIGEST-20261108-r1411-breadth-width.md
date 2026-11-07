# DIGEST-20261108-r1411 — how many names does the breadth premium need?

**Question.** r1408's judge closed zoo #93 and left a side reading worth more than the factor:
equal-weighting every liquid A-share earned 9.24%/yr with a -27% drawdown while 510300 lost
0.2%/yr with -45%. That pool was a *control*. This round asks it as the subject:

> when the book can only hold N names, how much of the premium survives, and is an N-name
> book a lottery or a rule?

**Face.** `scripts/astock_breadth_book.py` (selftest 14/14), receipt
`results/breadth_book/astock_breadth_book.json`. Panel 5,199 names / 1,658 bars, loaded by the
same loader zoo93 uses (imported, never re-implemented). 26 non-overlapping 60-bar cohorts,
2020-04-03 → 2026-06-15 decisions, entry at open[t+1], exit at open[t+1+60], 13.041bp/side,
20-bar median amount ≥ 20M CNY, mean eligible pool 4,211.8 names.

**Readings.**

| arm | net CAGR | cohort maxdd | x3 cost | frozen-book mean (sd) |
|---|---|---|---|---|
| ALL | **+10.11%** | -31.05% | +7.76% | — |
| N20 | +9.97% (sd 5.14, p10 3.92) | -33.71% | +7.31% | +9.77% (3.94) |
| N50 | +9.80% | -31.81% | +5.79% | +9.63% (1.91) |
| N100 | +9.70% | -32.09% | +7.33% | +10.47% (1.48) |
| N200 | +10.12% | -31.18% | +7.78% | +10.46% (0.94) |
| N500 | +10.25% | -30.92% | +7.80% | +10.54% (0.67) |
| 510300 same span | +3.35% | **-45.10%** | — | — |
| 511260 same span | +2.97% | -4.62% | — | — |

Excess over 510300: **+6.76pp/yr**. Cost drag at x1 ≈ 2.4pp/yr (turnover 4.2/yr).

Phase null (12 offsets, 0..55 step 5): 6.08, 6.65, 8.04, 8.09, 8.89, 9.13, 9.32, 9.53, 9.76,
10.11, 10.35, 10.82 %/yr. Worst is **-4.03pp** under offset 0.

**Verdict (rule frozen before the numbers):** REFUSE_AS_CANDIDATE. Condition (a) passes
(+6.76pp ≥ +3.0), (b) passes (N=50 keeps 97% of ALL with a cohort drawdown 0.76pp better),
(c) fails: the worst phase is 4.03pp under the offset-0 reading.

**What this decides.** Width is not the constraint in this domain — 20 names already carry 98.6%
of the all-pool mean, and a frozen 20-name book has a *narrower* spread than a re-drawn one, so
"which names" is not the risk. Cost is not the constraint either (x3 still +7.76%), unlike the
20-bar behavioural factors priced in r1405/r1410 that die on a ~3.3pp/yr cost wall at the same
turnover. The constraint is the calendar: 26 independent cohorts over six years, and moving the
grid by 30 bars moves the headline by 4pp. The premium is real in this panel but this panel
cannot separate it from "the basket that happened to rise over these six years".

**Not measured / honest limits.** qfq prices (adjusted, not as-traded); today's listed names
(survivorship in the 2020 tail); drawdown at 60-bar granularity flatters the book; no cash yield
credited (511260 reported as reference only); eligibility is a 20M-CNY median-amount gate, not a
realistic institution-capacity gate at size.

**Next.** The pool still reads ready 0 < floor 3 (fifteenth round). The remaining registered
berth is zoo #97 `etf_premium_sentiment`, blocked on a core48 IOPV/premium panel.