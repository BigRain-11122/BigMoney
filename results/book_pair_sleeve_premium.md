# Which ruler says the sleeve is expensive

**Does 'the cb sleeve is expensive' mean the same thing on the market's median premium as on the premium of the 20 bonds the sleeve actually holds?**

generated 2026-11-27T20:51:42+08:00 · cutoff 2026-11-26 · book 30.0% cb share

| verdict | |
|---|---|
| **THE_ANSWER_DEPENDS_ON_WHICH_RULER** | rules labelled same in 23 of 81 months (58 differ) |

## Today, on each ruler

| ruler | label in force | read at | sleeve | today's reading | its own rich line | expensive now? |
|---|---|---|---|---|---|---|
| market median | rich | 2026-10-31 | 收进现金 | 70.34% | 32.64% | 贵 |
| our 20 bonds | rich | 2026-10-31 | 收进现金 | 8.77% | 15.23% | 不贵 |
| our bonds, 3y window | rich | 2026-10-31 | 收进现金 | 8.77% | 12.28% | 不贵 |

> 两把尺的**当日读数**不同向：the label in force was read at the previous month end; the bonds the sleeve holds today read differently, so the call is a month-old reading of a sleeve that has since re-picked

## The rule, priced on each ruler

| ruler | cash months | rule CAGR | rule Sharpe | rule MDD | always-on Sharpe | edge/mo | band | verdict |
|---|---|---|---|---|---|---|---|---|
| market median | 46/81 | 10.0% | +1.38 | -4.4% | +1.21 | +0.14 pp | +0.02 .. +0.28 | THE_RULE_BEATS_ITS_OWN_EXPOSURE |
| our 20 bonds | 3/81 | 9.4% | +1.25 | -8.1% | +1.21 | +0.01 pp | -0.03 .. +0.06 | RULE_EDGE_NOT_SEPARABLE_FROM_NOISE |
| our bonds, 3y window | 28/81 | 9.3% | +1.25 | -6.8% | +1.21 | +0.05 pp | -0.06 .. +0.17 | RULE_EDGE_NOT_SEPARABLE_FROM_NOISE |

## Where the two rulers disagree

- months both labelled: **81**
- same bucket: **23** (28.4%)
- market says rich, our bonds do not: **43**
- our bonds say rich, market does not: **0**

| month ending | market | our bonds |
|---|---|---|
| 2020-04-30 | rich | mid |
| 2020-05-31 | rich | mid |
| 2021-01-31 | mid | cheap |
| 2021-03-31 | mid | cheap |
| 2021-04-30 | mid | cheap |
| 2021-05-31 | mid | cheap |
| 2021-06-30 | mid | cheap |
| 2021-08-31 | mid | cheap |
| 2021-10-31 | mid | cheap |
| 2022-02-28 | rich | mid |
| 2022-03-31 | rich | mid |
| 2022-04-30 | rich | mid |
| 2022-05-31 | rich | mid |
| 2022-06-30 | rich | mid |
| 2022-07-31 | rich | mid |
| 2022-08-31 | rich | mid |
| 2022-09-30 | rich | mid |
| 2022-10-31 | rich | mid |
| 2022-11-30 | rich | mid |
| 2022-12-31 | rich | mid |
| 2023-01-31 | rich | mid |
| 2023-02-28 | rich | mid |
| 2023-03-31 | rich | mid |
| 2023-04-30 | rich | mid |
| … | 34 more | |

## What is not verified

- membership is rebuilt from the parent's pick formula, not read from the parent's holdings -- the parent does not publish them, so a formula change on its side would move this face without either side failing
- the sleeve's own premium jumps at rebalances (a pick turns over half the 20 bonds), so part of its month-end reading is 'which bonds we happen to hold', not only 'how expensive they are' -- the coverage gate cannot see that
- the sleeve ruler still has only one premium cycle in it (81 labelled months); a second cycle is what would tell us whether the two rulers converge in a genuinely cheap market
- an expanding-window tertile cannot call a structurally falling series rich: the sleeve reads rich in 3 of 81 months and the market in 46, so the two arms do not fire equally often -- the recent-window arm is published beside them for that reason, not as a tiebreak
- premium on a held bond can be stale on its last quoted day; the coverage gate drops a month below 80% coverage, it does not correct the rest
- the rule is priced on monthly switches only; intra-month runs are not modelled
- the cb arm and the etf arm are the parents' published arms -- this face does not re-test them
