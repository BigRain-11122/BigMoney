# One size, three rulers

ticket `TICKET-2026-11-11.json` | evidence cutoff 2026-11-11 | decision date 2026-11-11 | beta target 0.2

**IDENTITY_BROKEN** — a ruler disagrees with a published number (window_recomputed_matches_receipt); the table is not evidence until that is resolved

| cell | universe | window | beta | k | vs money (pp) |
|---|---|---|---|---|---|
| baseline_published | all classes on the panel | full | 0.434543 | 0.460253 | +6.72 |
| window | all classes on the panel | common (2023-09-01..2026-11-11) | 0.267707 | 0.747086 | +35.40 |
| universe | graded (equity,commodity,convertible) | full | 0.462754 | 0.432195 | +3.91 |
| window_x_universe | graded (equity,commodity,convertible) | common (2023-09-01..2026-11-11) | 0.299551 | 0.667665 | +27.46 |
| denominator | today's 5 names, 100% invested | common | 0.582228 | 0.343508 | -4.96 |

- range: k 0.343508 .. 0.747086 (40.36pp) = CNY 343,508 .. 747,086
- money in force: CNY 393,073 at k=0.393073
- widest mover: window +35.40pp

- denominator: the sized mix is 39.3% invested; dividing by covered weight puts it on the path's denominator (r1448 unit note)

identity legs: 5 pass / 1 fail (window_recomputed_matches_receipt)

prereg requirements for 2026-11-11:
- 1. fix the ruler before looking: which window (common vs full) and which universe (all vs graded) is the declared measurement universe
- 2. fix the denominator rule (path beta, or static mix divided by covered weight) and forbid mixing the two inside one table
- 3. if the declared size is the floor rather than the ceiling, sign the risk budget it implies (target 0.20 is a budget, not an optimum -- r1447)
- 4. carry the chosen size into the 2026-11-11 ticket and print the three unused readings next to it so the choice stays visible
