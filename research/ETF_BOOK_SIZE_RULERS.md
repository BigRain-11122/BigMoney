# One size, three rulers

ticket `TICKET-2026-11-20.json` | evidence cutoff 2026-11-20 | decision date 2026-12-09 | beta target 0.2

**IDENTITY_BROKEN** — a ruler disagrees with a published number (ticket_k_reproduced, graded_k_reproduces_split_receipt); the table is not evidence until that is resolved

| cell | universe | window | beta | k | vs money (pp) |
|---|---|---|---|---|---|
| baseline_published | all classes on the panel | full | 0.436240 | 0.458463 | +2.63 |
| window | all classes on the panel | common (2023-09-01..2026-11-11) | 0.267707 | 0.747086 | +31.49 |
| universe | graded (equity,commodity,convertible) | full | 0.459767 | 0.435003 | +0.28 |
| window_x_universe | graded (equity,commodity,convertible) | common (2023-09-01..2026-11-11) | 0.299551 | 0.667665 | +23.55 |
| denominator | today's 5 names, 100% invested | common | 0.582228 | 0.343508 | -8.87 |

- range: k 0.343508 .. 0.747086 (40.36pp) = CNY 343,508 .. 747,086
- money in force: CNY 432,195 at k=0.432195
- widest mover: window +31.49pp

- denominator: the sized mix is 43.2% invested; dividing by covered weight puts it on the path's denominator (r1448 unit note)

identity legs: 4 pass / 2 fail (ticket_k_reproduced, graded_k_reproduces_split_receipt)

prereg requirements for 2026-12-09:
- 1. fix the ruler before looking: which window (common vs full) and which universe (all vs graded) is the declared measurement universe
- 2. fix the denominator rule (path beta, or static mix divided by covered weight) and forbid mixing the two inside one table
- 3. if the declared size is the floor rather than the ceiling, sign the risk budget it implies (target 0.20 is a budget, not an optimum -- r1447)
- 4. carry the chosen size into the 2026-12-09 ticket and print the three unused readings next to it so the choice stays visible
