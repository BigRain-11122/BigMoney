# One size, three rulers

ticket `TICKET-2026-11-11.json` | evidence cutoff 2026-11-11 | decision date 2026-11-11 | beta target 0.2

**SIZE_IS_A_RULER_CHOICE** — the same rule priced on the same panel lands between k=0.343508 and k=0.747086 (40.36pp of range, widest mover=window +31.49pp); the money sits inside that range at k=0.432195 -- 1 readings below it, 3 above it, floor CNY 343,508 against CNY 432,195 deployed

| cell | universe | window | beta | k | vs money (pp) |
|---|---|---|---|---|---|
| baseline_published | all classes on the panel | full | 0.434543 | 0.460253 | +2.81 |
| window | all classes on the panel | common (2023-09-01..2026-11-11) | 0.267707 | 0.747086 | +31.49 |
| universe | graded (equity,commodity,convertible) | full | 0.462754 | 0.432195 | +0.00 |
| window_x_universe | graded (equity,commodity,convertible) | common (2023-09-01..2026-11-11) | 0.299551 | 0.667665 | +23.55 |
| denominator | today's 5 names, 100% invested | common | 0.582228 | 0.343508 | -8.87 |

- range: k 0.343508 .. 0.747086 (40.36pp) = CNY 343,508 .. 747,086
- money in force: CNY 432,195 at k=0.432195
- widest mover: window +31.49pp

- denominator: the sized mix is 43.2% invested; dividing by covered weight puts it on the path's denominator (r1448 unit note)

identity legs: 6 pass / 0 fail

prereg requirements for 2026-11-11:
- 1. fix the ruler before looking: which window (common vs full) and which universe (all vs graded) is the declared measurement universe
- 2. fix the denominator rule (path beta, or static mix divided by covered weight) and forbid mixing the two inside one table
- 3. if the declared size is the floor rather than the ceiling, sign the risk budget it implies (target 0.20 is a budget, not an optimum -- r1447)
- 4. carry the chosen size into the 2026-11-11 ticket and print the three unused readings next to it so the choice stays visible
