# Can the debt-floor convertible cell be judged at all?

> Answer: **NO_GO** -- the smallest difference 13.05 years of this noise can tell from zero is **10.11pp/yr**, against a 5.0pp target.

Question: `research/BENCH-NEXT.md` cell 3 wants a convertible-bond line cut down to the debt floor (price near par, above its own pure-bond value), marked to market daily. Its own rule says the first deliverable is the minimum detectable effect, not a return. This page is that number.

## The measurement

| | bucket | universe |
|---|---|---|
| what | close <= 105.0 and pure_bond_premium >= 0.0 at the previous close | every convertible bond with a return that day, equal weight |
| CAGR (context, no costs) | 10.08% | 7.70% |

Difference series (bucket minus universe): 3288 days, 13.05 years, 2008-03-19 to 2026-11-13.

| quantity | value |
|---|---|
| daily sigma | 0.821% |
| annual sigma | 13.03% |
| observed mean difference | +2.380pp/yr (t = 1.30) |
| **minimum detectable effect** | **10.11pp/yr** |
| target from the cell brief | 5.0pp/yr |
| verdict | **NO_GO** |

widen the sample: at this noise a 5.0pp edge needs 53.3 years and the panel has 13.1.

## Why a bigger bucket is not the fix

On the 2665 days with at least 5 names the noise falls to 0.420%/day and the MDE to **5.74pp** -- still above the target. Adding names before measuring is the same move as widening a ruler until the object fits.

## How long would it take

| edge you want to detect | years of this noise needed | years we have |
|---|---|---|
| 5.0pp (the target) | 53.3 | 13.1 |
| 2.38pp (what we actually saw) | 235 | 13.1 |

## Coverage and hygiene

| | |
|---|---|
| bonds in the universe | 1046 |
| calendar days | 4701 |
| panel span | 2007-07-12 to 2026-11-13 |
| days in the bucket | 3288 |
| names per day | median 14, min 1, max 169 |
| days under 5 names | 623 |
| 退债 rows dropped (404xxx) | 1727 |
| impossible returns masked | 1 of 785561 cells |

## What this face does not claim

* it does not say the debt floor has no edge -- it says this sample cannot see one of the size required; the observed 2.38pp is a third of the detection line and carries t=1.30
* it does not price costs, tickets or capacity: no money is attached to either series
* it does not rank the debt floor against other cells -- it only says whether this sample could ever separate it from holding everything
* the returns printed are compounded daily equal-weight series with no cost model; they are context for the MDE, not a backtest

Generated 2026-11-23T05:52:16+0800 by `scripts/cb_debt_floor_mde.py`.
