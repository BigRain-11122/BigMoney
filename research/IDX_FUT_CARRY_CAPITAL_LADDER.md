# the carry sleeve: an 8% vol target on a 1,000,000 book is not an integer

evidence cutoff: **2026-11-17** | source: `results/idx_fut_carry_paper/SIZING.json` | generated 2026-11-18T16:56:33

One lot's annualised vol, hedged to the discount, is the whole input here; the face does not re-derive it. 
A fraction of a lot is printed as arithmetic and never as a position: a futures contract is not divisible.

## IC

| capital | target | vol of 1 lot (hedged) | budget at target | lots (fraction) |
|---|---|---|---|---|
| 1,000,000 CNY | 8% | 89,673.25 CNY | 80,000.00 CNY | 0.8921 |

**The same sentence, read three ways at this capital and target: `0` / `1` / `4` lots** (vol <= target / nearest integer / the ticket's own size). Verdict: **THE_RULER_DECIDES_THE_LOTS**.

The ticket's 4 lot(s) carry 358,693.00 CNY of annual vol against a 80,000.00 CNY budget -- **4.4837x the budget**, 35.87% of capital; holding them inside the target would take 4,483,662 CNY of capital.

### capital ladder (k lots at the stated target)

| lots | capital needed (CNY) | vs the book's capital | affordable |
|---|---|---|---|
| 1 | 1,120,916 | +120,916 | no |
| 2 | 2,241,831 | +1,241,831 | no |
| 3 | 3,362,747 | +2,362,747 | no |
| 4 | 4,483,662 | +3,483,662 | no |
| 5 | 5,604,578 | +4,604,578 | no |
| 6 | 6,725,494 | +5,725,494 | no |
| 7 | 7,846,409 | +6,846,409 | no |
| 8 | 8,967,325 | +7,967,325 | no |

### target ladder (k lots at the stated capital)

| lots | target that would be (%) | vs the stated target (pp) | achievable |
|---|---|---|---|
| 1 | 8.9673 | +0.9673 | no |
| 2 | 17.9346 | +9.9346 | no |
| 3 | 26.9020 | +18.9020 | no |
| 4 | 35.8693 | +27.8693 | no |
| 5 | 44.8366 | +36.8366 | no |
| 6 | 53.8040 | +45.8040 | no |
| 7 | 62.7713 | +54.7713 | no |
| 8 | 71.7386 | +63.7386 | no |

### capital x target -> whole lots (vol <= target)

| capital (CNY) | 4% | 6% | 8% | 9% | 10% | 12% | lots at the book's 8% (fraction) |
|---|---|---|---|---|---|---|---|
| 1,000,000 | 0 | 0 | 0 | 1 | 1 | 1 | 0.8921 |
| 1,250,000 | 0 | 0 | 1 | 1 | 1 | 1 | 1.1152 |
| 1,500,000 | 0 | 1 | 1 | 1 | 1 | 2 | 1.3382 |
| 2,000,000 | 0 | 1 | 1 | 2 | 2 | 2 | 1.7843 |
| 3,000,000 | 1 | 2 | 2 | 3 | 3 | 4 | 2.6764 |

### the three roads, each with its price

- **A keep 8%, raise the capital**: 1 lot needs 1,120,916 CNY (+120,916); the ticket's 4 lot(s) need 4,483,662 CNY.
- **B keep 1,000,000 CNY, lower the target**: 1 lot needs 8.9673% (+0.9673pp); the ticket's 4 lot(s) need 35.8693%.
- **C keep both**: 0 lot(s) -- the sleeve is not expressible at this rung and simply does not trade.

The three roads are not a preference ordering: A spends capital, B spends risk, C spends the sleeve. Picking one changes the specification (either the capital rung or the vol target), so this face prints their prices and stops there.

## IM

| capital | target | vol of 1 lot (hedged) | budget at target | lots (fraction) |
|---|---|---|---|---|
| 1,000,000 CNY | 8% | 91,874.86 CNY | 80,000.00 CNY | 0.8707 |

**The same sentence, read three ways at this capital and target: `0` / `1` / `4` lots** (vol <= target / nearest integer / the ticket's own size). Verdict: **THE_RULER_DECIDES_THE_LOTS**.

The ticket's 4 lot(s) carry 367,499.44 CNY of annual vol against a 80,000.00 CNY budget -- **4.5937x the budget**, 36.75% of capital; holding them inside the target would take 4,593,743 CNY of capital.

### capital ladder (k lots at the stated target)

| lots | capital needed (CNY) | vs the book's capital | affordable |
|---|---|---|---|
| 1 | 1,148,436 | +148,436 | no |
| 2 | 2,296,872 | +1,296,872 | no |
| 3 | 3,445,307 | +2,445,307 | no |
| 4 | 4,593,743 | +3,593,743 | no |
| 5 | 5,742,179 | +4,742,179 | no |
| 6 | 6,890,614 | +5,890,614 | no |
| 7 | 8,039,050 | +7,039,050 | no |
| 8 | 9,187,486 | +8,187,486 | no |

### target ladder (k lots at the stated capital)

| lots | target that would be (%) | vs the stated target (pp) | achievable |
|---|---|---|---|
| 1 | 9.1875 | +1.1875 | no |
| 2 | 18.3750 | +10.3750 | no |
| 3 | 27.5625 | +19.5625 | no |
| 4 | 36.7499 | +28.7499 | no |
| 5 | 45.9374 | +37.9374 | no |
| 6 | 55.1249 | +47.1249 | no |
| 7 | 64.3124 | +56.3124 | no |
| 8 | 73.4999 | +65.4999 | no |

### capital x target -> whole lots (vol <= target)

| capital (CNY) | 4% | 6% | 8% | 9% | 10% | 12% | lots at the book's 8% (fraction) |
|---|---|---|---|---|---|---|---|
| 1,000,000 | 0 | 0 | 0 | 0 | 1 | 1 | 0.8707 |
| 1,250,000 | 0 | 0 | 1 | 1 | 1 | 1 | 1.0884 |
| 1,500,000 | 0 | 0 | 1 | 1 | 1 | 1 | 1.3061 |
| 2,000,000 | 0 | 1 | 1 | 1 | 2 | 2 | 1.7415 |
| 3,000,000 | 1 | 1 | 2 | 2 | 3 | 3 | 2.6122 |

### the three roads, each with its price

- **A keep 8%, raise the capital**: 1 lot needs 1,148,436 CNY (+148,436); the ticket's 4 lot(s) need 4,593,743 CNY.
- **B keep 1,000,000 CNY, lower the target**: 1 lot needs 9.1875% (+1.1875pp); the ticket's 4 lot(s) need 36.7499%.
- **C keep both**: 0 lot(s) -- the sleeve is not expressible at this rung and simply does not trade.

The three roads are not a preference ordering: A spends capital, B spends risk, C spends the sleeve. Picking one changes the specification (either the capital rung or the vol target), so this face prints their prices and stops there.

