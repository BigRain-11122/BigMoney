# The repo curve as a cash leg -- does duration pay?

Window 2011-05-13 -> 2026-11-20 (5670 calendar days). Baseline: rolling GC001 at 2.495% net.

| tenor | net CAGR | pickup vs GC001 | 1st half | 2nd half | worst year vs base | utilisation | idle d/yr | median volume | verdict |
|---|---|---|---|---|---|---|---|---|---|
| GC001 (1d) | 2.495% | +0.00pp | +0.00 | +0.00 | +0.00 | 100.0% | 0.0 | 806,739,750 | **NO_EDGE** |
| GC003 (3d) | 2.261% | -0.23pp | -0.34 | -0.64 | +0.04 | 100.0% | 0.1 | 7,245,003 | **NO_EDGE** |
| GC004 (4d) | 2.468% | -0.03pp | -0.05 | -0.07 | +0.05 | 100.0% | 0.2 | 6,252,756 | **NO_EDGE** |
| GC007 (7d) | 2.585% | +0.09pp | +0.08 | +0.25 | +0.13 | 100.0% | 0.1 | 88,535,571 | **NO_EDGE** |
| GC014 (14d) | 2.613% | +0.12pp | +0.14 | +0.33 | +0.11 | 100.0% | 0.1 | 15,086,450 | **NO_EDGE** |
| GC028 (28d) | 2.595% | +0.10pp | +0.10 | +0.28 | +0.12 | 100.0% | 0.1 | 4,472,445 | **NO_EDGE** |
| GC091 (91d) | 2.820% | +0.33pp | +0.47 | +0.90 | -0.25 | 97.9% | 7.6 | 116,774 | **NO_EDGE** |
| GC182 (182d) | 2.693% | +0.20pp | +0.24 | +0.55 | -0.19 | 96.4% | 13.3 | 10,400 | **NO_EDGE** |
| R-001 (1d) | 1.740% | -0.75pp | -1.15 | -2.06 | -0.90 | 88.5% | 41.9 | 90,584,774 | **NO_EDGE** |
| R-003 (3d) | 1.627% | -0.87pp | -1.26 | -2.37 | -0.90 | 88.7% | 41.4 | 821,732 | **NO_EDGE** |
| R-007 (7d) | 2.050% | -0.44pp | -0.74 | -1.22 | -0.90 | 89.1% | 39.7 | 6,382,182 | **NO_EDGE** |

**Headline: NO_EDGE.**
Best pickup is GC091 at +0.33pp/yr (verdict NO_EDGE).

Curve on the last bar: GC001 1.395%, GC003 1.355%, GC004 1.380%, GC007 1.385%, GC014 1.385%, GC028 1.365%, GC091 1.340%, GC182 1.340%, R-001 1.380%, R-003 1.320%, R-007 1.375%

Notes: Commission is the exchange schedule charged on principal per lend; interest is paid on actual calendar days held; idle days between maturity and the next trading day earn nothing. Volume is not converted to money -- the two longest tenors are indicative until capacity is measured at our size.
