# the carry sleeve: an 8% vol target on a 1,000,000 book is not an integer

evidence cutoff: **2026-11-19** | source: `results/idx_fut_carry_paper/SIZING.json` | generated 2026-11-20T01:24:19

One lot's annualised vol, hedged to the discount, is the whole input here; the face does not re-derive it. 
A fraction of a lot is printed as arithmetic and never as a position: a futures contract is not divisible.

## IC

| capital | target | vol of 1 lot (hedged) | budget at target | lots (fraction) |
|---|---|---|---|---|
| 1,000,000 CNY | 8% | 89,643.20 CNY | 80,000.00 CNY | 0.8924 |

**The same sentence, read three ways at this capital and target: `0` / `1` / `4` lots** (vol <= target / nearest integer / the ticket's own size). Verdict: **THE_RULER_DECIDES_THE_LOTS**.

The ticket's 4 lot(s) carry 358,572.80 CNY of annual vol against a 80,000.00 CNY budget -- **4.4822x the budget**, 35.86% of capital; holding them inside the target would take 4,482,160 CNY of capital.

### capital ladder (k lots at the stated target)

| lots | capital needed (CNY) | vs the book's capital | affordable |
|---|---|---|---|
| 1 | 1,120,540 | +120,540 | no |
| 2 | 2,241,080 | +1,241,080 | no |
| 3 | 3,361,620 | +2,361,620 | no |
| 4 | 4,482,160 | +3,482,160 | no |
| 5 | 5,602,700 | +4,602,700 | no |
| 6 | 6,723,240 | +5,723,240 | no |
| 7 | 7,843,780 | +6,843,780 | no |
| 8 | 8,964,320 | +7,964,320 | no |

### target ladder (k lots at the stated capital)

| lots | target that would be (%) | vs the stated target (pp) | achievable |
|---|---|---|---|
| 1 | 8.9643 | +0.9643 | no |
| 2 | 17.9286 | +9.9286 | no |
| 3 | 26.8930 | +18.8930 | no |
| 4 | 35.8573 | +27.8573 | no |
| 5 | 44.8216 | +36.8216 | no |
| 6 | 53.7859 | +45.7859 | no |
| 7 | 62.7502 | +54.7502 | no |
| 8 | 71.7146 | +63.7146 | no |

### capital x target -> whole lots (vol <= target)

| capital (CNY) | 4% | 6% | 8% | 9% | 10% | 12% | lots at the book's 8% (fraction) |
|---|---|---|---|---|---|---|---|
| 1,000,000 | 0 | 0 | 0 | 1 | 1 | 1 | 0.8924 |
| 1,250,000 | 0 | 0 | 1 | 1 | 1 | 1 | 1.1155 |
| 1,500,000 | 0 | 1 | 1 | 1 | 1 | 2 | 1.3386 |
| 2,000,000 | 0 | 1 | 1 | 2 | 2 | 2 | 1.7849 |
| 3,000,000 | 1 | 2 | 2 | 3 | 3 | 4 | 2.6773 |

### the three roads, each with its price

- **A keep 8%, raise the capital**: 1 lot needs 1,120,540 CNY (+120,540); the ticket's 4 lot(s) need 4,482,160 CNY.
- **B keep 1,000,000 CNY, lower the target**: 1 lot needs 8.9643% (+0.9643pp); the ticket's 4 lot(s) need 35.8573%.
- **C keep both**: 0 lot(s) -- the sleeve is not expressible at this rung and simply does not trade.

The three roads are not a preference ordering: A spends capital, B spends risk, C spends the sleeve. Picking one changes the specification (either the capital rung or the vol target), so this face prints their prices and stops there.

## IM

| capital | target | vol of 1 lot (hedged) | budget at target | lots (fraction) |
|---|---|---|---|---|
| 1,000,000 CNY | 8% | 91,705.35 CNY | 80,000.00 CNY | 0.8724 |

**The same sentence, read three ways at this capital and target: `0` / `1` / `4` lots** (vol <= target / nearest integer / the ticket's own size). Verdict: **THE_RULER_DECIDES_THE_LOTS**.

The ticket's 4 lot(s) carry 366,821.40 CNY of annual vol against a 80,000.00 CNY budget -- **4.5853x the budget**, 36.68% of capital; holding them inside the target would take 4,585,268 CNY of capital.

### capital ladder (k lots at the stated target)

| lots | capital needed (CNY) | vs the book's capital | affordable |
|---|---|---|---|
| 1 | 1,146,317 | +146,317 | no |
| 2 | 2,292,634 | +1,292,634 | no |
| 3 | 3,438,951 | +2,438,951 | no |
| 4 | 4,585,268 | +3,585,268 | no |
| 5 | 5,731,584 | +4,731,584 | no |
| 6 | 6,877,901 | +5,877,901 | no |
| 7 | 8,024,218 | +7,024,218 | no |
| 8 | 9,170,535 | +8,170,535 | no |

### target ladder (k lots at the stated capital)

| lots | target that would be (%) | vs the stated target (pp) | achievable |
|---|---|---|---|
| 1 | 9.1705 | +1.1705 | no |
| 2 | 18.3411 | +10.3411 | no |
| 3 | 27.5116 | +19.5116 | no |
| 4 | 36.6821 | +28.6821 | no |
| 5 | 45.8527 | +37.8527 | no |
| 6 | 55.0232 | +47.0232 | no |
| 7 | 64.1937 | +56.1937 | no |
| 8 | 73.3643 | +65.3643 | no |

### capital x target -> whole lots (vol <= target)

| capital (CNY) | 4% | 6% | 8% | 9% | 10% | 12% | lots at the book's 8% (fraction) |
|---|---|---|---|---|---|---|---|
| 1,000,000 | 0 | 0 | 0 | 0 | 1 | 1 | 0.8724 |
| 1,250,000 | 0 | 0 | 1 | 1 | 1 | 1 | 1.0904 |
| 1,500,000 | 0 | 0 | 1 | 1 | 1 | 1 | 1.3085 |
| 2,000,000 | 0 | 1 | 1 | 1 | 2 | 2 | 1.7447 |
| 3,000,000 | 1 | 1 | 2 | 2 | 3 | 3 | 2.6171 |

### the three roads, each with its price

- **A keep 8%, raise the capital**: 1 lot needs 1,146,317 CNY (+146,317); the ticket's 4 lot(s) need 4,585,268 CNY.
- **B keep 1,000,000 CNY, lower the target**: 1 lot needs 9.1705% (+1.1705pp); the ticket's 4 lot(s) need 36.6821%.
- **C keep both**: 0 lot(s) -- the sleeve is not expressible at this rung and simply does not trade.

The three roads are not a preference ordering: A spends capital, B spends risk, C spends the sleeve. Picking one changes the specification (either the capital rung or the vol target), so this face prints their prices and stops there.

