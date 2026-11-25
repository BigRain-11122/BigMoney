# the carry sleeve: an 8% vol target on a 1,000,000 book is not an integer

evidence cutoff: **2026-11-23** | source: `results/idx_fut_carry_paper/SIZING.json` | generated 2026-11-24T16:13:43

One lot's annualised vol, hedged to the discount, is the whole input here; the face does not re-derive it. 
A fraction of a lot is printed as arithmetic and never as a position: a futures contract is not divisible.

## IC

| capital | target | vol of 1 lot (hedged) | budget at target | lots (fraction) |
|---|---|---|---|---|
| 1,000,000 CNY | 8% | 90,365.27 CNY | 80,000.00 CNY | 0.8853 |

**The same sentence, read three ways at this capital and target: `0` / `1` / `4` lots** (vol <= target / nearest integer / the ticket's own size). Verdict: **THE_RULER_DECIDES_THE_LOTS**.

The ticket's 4 lot(s) carry 361,461.08 CNY of annual vol against a 80,000.00 CNY budget -- **4.5183x the budget**, 36.15% of capital; holding them inside the target would take 4,518,264 CNY of capital.

### capital ladder (k lots at the stated target)

| lots | capital needed (CNY) | vs the book's capital | affordable |
|---|---|---|---|
| 1 | 1,129,566 | +129,566 | no |
| 2 | 2,259,132 | +1,259,132 | no |
| 3 | 3,388,698 | +2,388,698 | no |
| 4 | 4,518,264 | +3,518,264 | no |
| 5 | 5,647,829 | +4,647,829 | no |
| 6 | 6,777,395 | +5,777,395 | no |
| 7 | 7,906,961 | +6,906,961 | no |
| 8 | 9,036,527 | +8,036,527 | no |

### target ladder (k lots at the stated capital)

| lots | target that would be (%) | vs the stated target (pp) | achievable |
|---|---|---|---|
| 1 | 9.0365 | +1.0365 | no |
| 2 | 18.0731 | +10.0731 | no |
| 3 | 27.1096 | +19.1096 | no |
| 4 | 36.1461 | +28.1461 | no |
| 5 | 45.1826 | +37.1826 | no |
| 6 | 54.2192 | +46.2192 | no |
| 7 | 63.2557 | +55.2557 | no |
| 8 | 72.2922 | +64.2922 | no |

### capital x target -> whole lots (vol <= target)

| capital (CNY) | 4% | 6% | 8% | 9% | 10% | 12% | lots at the book's 8% (fraction) |
|---|---|---|---|---|---|---|---|
| 1,000,000 | 0 | 0 | 0 | 0 | 1 | 1 | 0.8853 |
| 1,250,000 | 0 | 0 | 1 | 1 | 1 | 1 | 1.1066 |
| 1,500,000 | 0 | 0 | 1 | 1 | 1 | 1 | 1.3279 |
| 2,000,000 | 0 | 1 | 1 | 1 | 2 | 2 | 1.7706 |
| 3,000,000 | 1 | 1 | 2 | 2 | 3 | 3 | 2.6559 |

### the three roads, each with its price

- **A keep 8%, raise the capital**: 1 lot needs 1,129,566 CNY (+129,566); the ticket's 4 lot(s) need 4,518,264 CNY.
- **B keep 1,000,000 CNY, lower the target**: 1 lot needs 9.0365% (+1.0365pp); the ticket's 4 lot(s) need 36.1461%.
- **C keep both**: 0 lot(s) -- the sleeve is not expressible at this rung and simply does not trade.

The three roads are not a preference ordering: A spends capital, B spends risk, C spends the sleeve. Picking one changes the specification (either the capital rung or the vol target), so this face prints their prices and stops there.

## IM

| capital | target | vol of 1 lot (hedged) | budget at target | lots (fraction) |
|---|---|---|---|---|
| 1,000,000 CNY | 8% | 92,732.72 CNY | 80,000.00 CNY | 0.8627 |

**The same sentence, read three ways at this capital and target: `0` / `1` / `4` lots** (vol <= target / nearest integer / the ticket's own size). Verdict: **THE_RULER_DECIDES_THE_LOTS**.

The ticket's 4 lot(s) carry 370,930.88 CNY of annual vol against a 80,000.00 CNY budget -- **4.6366x the budget**, 37.09% of capital; holding them inside the target would take 4,636,636 CNY of capital.

### capital ladder (k lots at the stated target)

| lots | capital needed (CNY) | vs the book's capital | affordable |
|---|---|---|---|
| 1 | 1,159,159 | +159,159 | no |
| 2 | 2,318,318 | +1,318,318 | no |
| 3 | 3,477,477 | +2,477,477 | no |
| 4 | 4,636,636 | +3,636,636 | no |
| 5 | 5,795,795 | +4,795,795 | no |
| 6 | 6,954,954 | +5,954,954 | no |
| 7 | 8,114,113 | +7,114,113 | no |
| 8 | 9,273,272 | +8,273,272 | no |

### target ladder (k lots at the stated capital)

| lots | target that would be (%) | vs the stated target (pp) | achievable |
|---|---|---|---|
| 1 | 9.2733 | +1.2733 | no |
| 2 | 18.5465 | +10.5465 | no |
| 3 | 27.8198 | +19.8198 | no |
| 4 | 37.0931 | +29.0931 | no |
| 5 | 46.3664 | +38.3664 | no |
| 6 | 55.6396 | +47.6396 | no |
| 7 | 64.9129 | +56.9129 | no |
| 8 | 74.1862 | +66.1862 | no |

### capital x target -> whole lots (vol <= target)

| capital (CNY) | 4% | 6% | 8% | 9% | 10% | 12% | lots at the book's 8% (fraction) |
|---|---|---|---|---|---|---|---|
| 1,000,000 | 0 | 0 | 0 | 0 | 1 | 1 | 0.8627 |
| 1,250,000 | 0 | 0 | 1 | 1 | 1 | 1 | 1.0784 |
| 1,500,000 | 0 | 0 | 1 | 1 | 1 | 1 | 1.2940 |
| 2,000,000 | 0 | 1 | 1 | 1 | 2 | 2 | 1.7254 |
| 3,000,000 | 1 | 1 | 2 | 2 | 3 | 3 | 2.5881 |

### the three roads, each with its price

- **A keep 8%, raise the capital**: 1 lot needs 1,159,159 CNY (+159,159); the ticket's 4 lot(s) need 4,636,636 CNY.
- **B keep 1,000,000 CNY, lower the target**: 1 lot needs 9.2733% (+1.2733pp); the ticket's 4 lot(s) need 37.0931%.
- **C keep both**: 0 lot(s) -- the sleeve is not expressible at this rung and simply does not trade.

The three roads are not a preference ordering: A spends capital, B spends risk, C spends the sleeve. Picking one changes the specification (either the capital rung or the vol target), so this face prints their prices and stops there.

