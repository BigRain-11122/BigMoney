# the carry sleeve: an 8% vol target on a 1,000,000 book is not an integer

evidence cutoff: **2026-11-16** | source: `results/idx_fut_carry_paper/SIZING.json` | generated 2026-11-16T23:02:48

One lot's annualised vol, hedged to the discount, is the whole input here; the face does not re-derive it. 
A fraction of a lot is printed as arithmetic and never as a position: a futures contract is not divisible.

## IC

| capital | target | vol of 1 lot (hedged) | budget at target | lots (fraction) |
|---|---|---|---|---|
| 1,000,000 CNY | 8% | 90,000.98 CNY | 80,000.00 CNY | 0.8889 |

**The same sentence, read three ways at this capital and target: `0` / `1` / `4` lots** (vol <= target / nearest integer / the ticket's own size). Verdict: **THE_RULER_DECIDES_THE_LOTS**.

The ticket's 4 lot(s) carry 360,003.92 CNY of annual vol against a 80,000.00 CNY budget -- **4.5x the budget**, 36.00% of capital; holding them inside the target would take 4,500,049 CNY of capital.

### capital ladder (k lots at the stated target)

| lots | capital needed (CNY) | vs the book's capital | affordable |
|---|---|---|---|
| 1 | 1,125,012 | +125,012 | no |
| 2 | 2,250,024 | +1,250,024 | no |
| 3 | 3,375,037 | +2,375,037 | no |
| 4 | 4,500,049 | +3,500,049 | no |
| 5 | 5,625,061 | +4,625,061 | no |
| 6 | 6,750,074 | +5,750,074 | no |
| 7 | 7,875,086 | +6,875,086 | no |
| 8 | 9,000,098 | +8,000,098 | no |

### target ladder (k lots at the stated capital)

| lots | target that would be (%) | vs the stated target (pp) | achievable |
|---|---|---|---|
| 1 | 9.0001 | +1.0001 | no |
| 2 | 18.0002 | +10.0002 | no |
| 3 | 27.0003 | +19.0003 | no |
| 4 | 36.0004 | +28.0004 | no |
| 5 | 45.0005 | +37.0005 | no |
| 6 | 54.0006 | +46.0006 | no |
| 7 | 63.0007 | +55.0007 | no |
| 8 | 72.0008 | +64.0008 | no |

### capital x target -> whole lots (vol <= target)

| capital (CNY) | 4% | 6% | 8% | 9% | 10% | 12% | lots at the book's 8% (fraction) |
|---|---|---|---|---|---|---|---|
| 1,000,000 | 0 | 0 | 0 | 0 | 1 | 1 | 0.8889 |
| 1,250,000 | 0 | 0 | 1 | 1 | 1 | 1 | 1.1111 |
| 1,500,000 | 0 | 0 | 1 | 1 | 1 | 1 | 1.3333 |
| 2,000,000 | 0 | 1 | 1 | 1 | 2 | 2 | 1.7778 |
| 3,000,000 | 1 | 1 | 2 | 2 | 3 | 3 | 2.6666 |

### the three roads, each with its price

- **A keep 8%, raise the capital**: 1 lot needs 1,125,012 CNY (+125,012); the ticket's 4 lot(s) need 4,500,049 CNY.
- **B keep 1,000,000 CNY, lower the target**: 1 lot needs 9.0001% (+1.0001pp); the ticket's 4 lot(s) need 36.0004%.
- **C keep both**: 0 lot(s) -- the sleeve is not expressible at this rung and simply does not trade.

The three roads are not a preference ordering: A spends capital, B spends risk, C spends the sleeve. Picking one changes the specification (either the capital rung or the vol target), so this face prints their prices and stops there.

## IM

| capital | target | vol of 1 lot (hedged) | budget at target | lots (fraction) |
|---|---|---|---|---|
| 1,000,000 CNY | 8% | 92,163.18 CNY | 80,000.00 CNY | 0.8680 |

**The same sentence, read three ways at this capital and target: `0` / `1` / `4` lots** (vol <= target / nearest integer / the ticket's own size). Verdict: **THE_RULER_DECIDES_THE_LOTS**.

The ticket's 4 lot(s) carry 368,652.72 CNY of annual vol against a 80,000.00 CNY budget -- **4.6082x the budget**, 36.87% of capital; holding them inside the target would take 4,608,159 CNY of capital.

### capital ladder (k lots at the stated target)

| lots | capital needed (CNY) | vs the book's capital | affordable |
|---|---|---|---|
| 1 | 1,152,040 | +152,040 | no |
| 2 | 2,304,080 | +1,304,080 | no |
| 3 | 3,456,119 | +2,456,119 | no |
| 4 | 4,608,159 | +3,608,159 | no |
| 5 | 5,760,199 | +4,760,199 | no |
| 6 | 6,912,238 | +5,912,238 | no |
| 7 | 8,064,278 | +7,064,278 | no |
| 8 | 9,216,318 | +8,216,318 | no |

### target ladder (k lots at the stated capital)

| lots | target that would be (%) | vs the stated target (pp) | achievable |
|---|---|---|---|
| 1 | 9.2163 | +1.2163 | no |
| 2 | 18.4326 | +10.4326 | no |
| 3 | 27.6490 | +19.6490 | no |
| 4 | 36.8653 | +28.8653 | no |
| 5 | 46.0816 | +38.0816 | no |
| 6 | 55.2979 | +47.2979 | no |
| 7 | 64.5142 | +56.5142 | no |
| 8 | 73.7305 | +65.7305 | no |

### capital x target -> whole lots (vol <= target)

| capital (CNY) | 4% | 6% | 8% | 9% | 10% | 12% | lots at the book's 8% (fraction) |
|---|---|---|---|---|---|---|---|
| 1,000,000 | 0 | 0 | 0 | 0 | 1 | 1 | 0.8680 |
| 1,250,000 | 0 | 0 | 1 | 1 | 1 | 1 | 1.0850 |
| 1,500,000 | 0 | 0 | 1 | 1 | 1 | 1 | 1.3020 |
| 2,000,000 | 0 | 1 | 1 | 1 | 2 | 2 | 1.7361 |
| 3,000,000 | 1 | 1 | 2 | 2 | 3 | 3 | 2.6041 |

### the three roads, each with its price

- **A keep 8%, raise the capital**: 1 lot needs 1,152,040 CNY (+152,040); the ticket's 4 lot(s) need 4,608,159 CNY.
- **B keep 1,000,000 CNY, lower the target**: 1 lot needs 9.2163% (+1.2163pp); the ticket's 4 lot(s) need 36.8653%.
- **C keep both**: 0 lot(s) -- the sleeve is not expressible at this rung and simply does not trade.

The three roads are not a preference ordering: A spends capital, B spends risk, C spends the sleeve. Picking one changes the specification (either the capital rung or the vol target), so this face prints their prices and stops there.

