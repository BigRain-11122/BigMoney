# the carry sleeve: an 8% vol target on a 1,000,000 book is not an integer

evidence cutoff: **2026-11-25** | source: `results/idx_fut_carry_paper/SIZING.json` | generated 2026-11-26T05:32:37

One lot's annualised vol, hedged to the discount, is the whole input here; the face does not re-derive it. 
A fraction of a lot is printed as arithmetic and never as a position: a futures contract is not divisible.

## IC

| capital | target | vol of 1 lot (hedged) | budget at target | lots (fraction) |
|---|---|---|---|---|
| 1,000,000 CNY | 8% | 90,571.63 CNY | 80,000.00 CNY | 0.8833 |

**The same sentence, read three ways at this capital and target: `0` / `1` / `4` lots** (vol <= target / nearest integer / the ticket's own size). Verdict: **THE_RULER_DECIDES_THE_LOTS**.

The ticket's 4 lot(s) carry 362,286.52 CNY of annual vol against a 80,000.00 CNY budget -- **4.5286x the budget**, 36.23% of capital; holding them inside the target would take 4,528,582 CNY of capital.

### capital ladder (k lots at the stated target)

| lots | capital needed (CNY) | vs the book's capital | affordable |
|---|---|---|---|
| 1 | 1,132,145 | +132,145 | no |
| 2 | 2,264,291 | +1,264,291 | no |
| 3 | 3,396,436 | +2,396,436 | no |
| 4 | 4,528,582 | +3,528,582 | no |
| 5 | 5,660,727 | +4,660,727 | no |
| 6 | 6,792,872 | +5,792,872 | no |
| 7 | 7,925,018 | +6,925,018 | no |
| 8 | 9,057,163 | +8,057,163 | no |

### target ladder (k lots at the stated capital)

| lots | target that would be (%) | vs the stated target (pp) | achievable |
|---|---|---|---|
| 1 | 9.0572 | +1.0572 | no |
| 2 | 18.1143 | +10.1143 | no |
| 3 | 27.1715 | +19.1715 | no |
| 4 | 36.2287 | +28.2287 | no |
| 5 | 45.2858 | +37.2858 | no |
| 6 | 54.3430 | +46.3430 | no |
| 7 | 63.4001 | +55.4001 | no |
| 8 | 72.4573 | +64.4573 | no |

### capital x target -> whole lots (vol <= target)

| capital (CNY) | 4% | 6% | 8% | 9% | 10% | 12% | lots at the book's 8% (fraction) |
|---|---|---|---|---|---|---|---|
| 1,000,000 | 0 | 0 | 0 | 0 | 1 | 1 | 0.8833 |
| 1,250,000 | 0 | 0 | 1 | 1 | 1 | 1 | 1.1041 |
| 1,500,000 | 0 | 0 | 1 | 1 | 1 | 1 | 1.3249 |
| 2,000,000 | 0 | 1 | 1 | 1 | 2 | 2 | 1.7666 |
| 3,000,000 | 1 | 1 | 2 | 2 | 3 | 3 | 2.6498 |

### the three roads, each with its price

- **A keep 8%, raise the capital**: 1 lot needs 1,132,145 CNY (+132,145); the ticket's 4 lot(s) need 4,528,582 CNY.
- **B keep 1,000,000 CNY, lower the target**: 1 lot needs 9.0572% (+1.0572pp); the ticket's 4 lot(s) need 36.2287%.
- **C keep both**: 0 lot(s) -- the sleeve is not expressible at this rung and simply does not trade.

The three roads are not a preference ordering: A spends capital, B spends risk, C spends the sleeve. Picking one changes the specification (either the capital rung or the vol target), so this face prints their prices and stops there.

## IM

| capital | target | vol of 1 lot (hedged) | budget at target | lots (fraction) |
|---|---|---|---|---|
| 1,000,000 CNY | 8% | 92,892.90 CNY | 80,000.00 CNY | 0.8612 |

**The same sentence, read three ways at this capital and target: `0` / `1` / `4` lots** (vol <= target / nearest integer / the ticket's own size). Verdict: **THE_RULER_DECIDES_THE_LOTS**.

The ticket's 4 lot(s) carry 371,571.60 CNY of annual vol against a 80,000.00 CNY budget -- **4.6446x the budget**, 37.16% of capital; holding them inside the target would take 4,644,645 CNY of capital.

### capital ladder (k lots at the stated target)

| lots | capital needed (CNY) | vs the book's capital | affordable |
|---|---|---|---|
| 1 | 1,161,161 | +161,161 | no |
| 2 | 2,322,322 | +1,322,322 | no |
| 3 | 3,483,484 | +2,483,484 | no |
| 4 | 4,644,645 | +3,644,645 | no |
| 5 | 5,805,806 | +4,805,806 | no |
| 6 | 6,966,968 | +5,966,968 | no |
| 7 | 8,128,129 | +7,128,129 | no |
| 8 | 9,289,290 | +8,289,290 | no |

### target ladder (k lots at the stated capital)

| lots | target that would be (%) | vs the stated target (pp) | achievable |
|---|---|---|---|
| 1 | 9.2893 | +1.2893 | no |
| 2 | 18.5786 | +10.5786 | no |
| 3 | 27.8679 | +19.8679 | no |
| 4 | 37.1572 | +29.1572 | no |
| 5 | 46.4464 | +38.4464 | no |
| 6 | 55.7357 | +47.7357 | no |
| 7 | 65.0250 | +57.0250 | no |
| 8 | 74.3143 | +66.3143 | no |

### capital x target -> whole lots (vol <= target)

| capital (CNY) | 4% | 6% | 8% | 9% | 10% | 12% | lots at the book's 8% (fraction) |
|---|---|---|---|---|---|---|---|
| 1,000,000 | 0 | 0 | 0 | 0 | 1 | 1 | 0.8612 |
| 1,250,000 | 0 | 0 | 1 | 1 | 1 | 1 | 1.0765 |
| 1,500,000 | 0 | 0 | 1 | 1 | 1 | 1 | 1.2918 |
| 2,000,000 | 0 | 1 | 1 | 1 | 2 | 2 | 1.7224 |
| 3,000,000 | 1 | 1 | 2 | 2 | 3 | 3 | 2.5836 |

### the three roads, each with its price

- **A keep 8%, raise the capital**: 1 lot needs 1,161,161 CNY (+161,161); the ticket's 4 lot(s) need 4,644,645 CNY.
- **B keep 1,000,000 CNY, lower the target**: 1 lot needs 9.2893% (+1.2893pp); the ticket's 4 lot(s) need 37.1572%.
- **C keep both**: 0 lot(s) -- the sleeve is not expressible at this rung and simply does not trade.

The three roads are not a preference ordering: A spends capital, B spends risk, C spends the sleeve. Picking one changes the specification (either the capital rung or the vol target), so this face prints their prices and stops there.

