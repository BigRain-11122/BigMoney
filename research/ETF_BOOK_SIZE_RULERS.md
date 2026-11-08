# One size, three rulers

ticket `TICKET-2026-11-06.json` | evidence cutoff 2026-11-06 | decision date 2026-11-11 | beta target 0.2

**SIZE_IS_A_RULER_CHOICE** — the same rule priced on the same panel lands between k=0.393073 and k=0.544424 (15.14pp of range, widest mover=denominator +8.42pp); the money sits inside that range at k=0.460253 -- 3 readings below it, 1 above it, floor CNY 393,073 against CNY 460,253 deployed

| cell | universe | window | beta | k | vs money (pp) |
|---|---|---|---|---|---|
| baseline_published | all classes on the panel | full | 0.434543 | 0.460253 | +0.00 |
| window | all classes on the panel | common (2025-07-09..2026-10-14) | 0.484650 | 0.412669 | -4.76 |
| universe | graded (equity,commodity,convertible) | full | 0.462754 | 0.432195 | -2.81 |
| window_x_universe | graded (equity,commodity,convertible) | common (2025-07-09..2026-10-14) | 0.508811 | 0.393073 | -6.72 |
| denominator | today's 5 names, 100% invested | common | 0.367361 | 0.544424 | +8.42 |

- range: k 0.393073 .. 0.544424 (15.14pp) = CNY 393,073 .. 544,424
- money in force: CNY 460,253 at k=0.460253
- widest mover: denominator +8.42pp

- denominator: the sized mix is 46.0% invested; dividing by covered weight puts it on the path's denominator (r1448 unit note)

identity legs: 6 pass / 0 fail

prereg requirements for 2026-11-11:
- 1. fix the ruler before looking: which window (common vs full) and which universe (all vs graded) is the declared measurement universe
- 2. fix the denominator rule (path beta, or static mix divided by covered weight) and forbid mixing the two inside one table
- 3. if the declared size is the floor rather than the ceiling, sign the risk budget it implies (target 0.20 is a budget, not an optimum -- r1447)
- 4. carry the chosen size into the 2026-11-11 ticket and print the three unused readings next to it so the choice stays visible
