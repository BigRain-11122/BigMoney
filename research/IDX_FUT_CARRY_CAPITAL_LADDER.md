# the carry sleeve: an 8% vol target on a 1,000,000 book is not an integer

evidence cutoff: **2026-11-20** | source: `results/idx_fut_carry_paper/SIZING.json` | generated 2026-11-21T09:15:00

One lot's annualised vol, hedged to the discount, is the whole input here; the face does not re-derive it. 
A fraction of a lot is printed as arithmetic and never as a position: a futures contract is not divisible.

## IC

| capital | target | vol of 1 lot (hedged) | budget at target | lots (fraction) |
|---|---|---|---|---|
| 1,000,000 CNY | 8% | 89,958.32 CNY | 80,000.00 CNY | 0.8893 |

**The same sentence, read three ways at this capital and target: `0` / `1` / `4` lots** (vol <= target / nearest integer / the ticket's own size). Verdict: **THE_RULER_DECIDES_THE_LOTS**.

The ticket's 4 lot(s) carry 359,833.28 CNY of annual vol against a 80,000.00 CNY budget -- **4.4979x the budget**, 35.98% of capital; holding them inside the target would take 4,497,916 CNY of capital.

### capital ladder (k lots at the stated target)

| lots | capital needed (CNY) | vs the book's capital | affordable |
|---|---|---|---|
| 1 | 1,124,479 | +124,479 | no |
| 2 | 2,248,958 | +1,248,958 | no |
| 3 | 3,373,437 | +2,373,437 | no |
| 4 | 4,497,916 | +3,497,916 | no |
| 5 | 5,622,395 | +4,622,395 | no |
| 6 | 6,746,874 | +5,746,874 | no |
| 7 | 7,871,353 | +6,871,353 | no |
| 8 | 8,995,832 | +7,995,832 | no |

### target ladder (k lots at the stated capital)

| lots | target that would be (%) | vs the stated target (pp) | achievable |
|---|---|---|---|
| 1 | 8.9958 | +0.9958 | no |
| 2 | 17.9917 | +9.9917 | no |
| 3 | 26.9875 | +18.9875 | no |
| 4 | 35.9833 | +27.9833 | no |
| 5 | 44.9792 | +36.9792 | no |
| 6 | 53.9750 | +45.9750 | no |
| 7 | 62.9708 | +54.9708 | no |
| 8 | 71.9667 | +63.9667 | no |

### capital x target -> whole lots (vol <= target)

| capital (CNY) | 4% | 6% | 8% | 9% | 10% | 12% | lots at the book's 8% (fraction) |
|---|---|---|---|---|---|---|---|
| 1,000,000 | 0 | 0 | 0 | 1 | 1 | 1 | 0.8893 |
| 1,250,000 | 0 | 0 | 1 | 1 | 1 | 1 | 1.1116 |
| 1,500,000 | 0 | 1 | 1 | 1 | 1 | 2 | 1.3340 |
| 2,000,000 | 0 | 1 | 1 | 2 | 2 | 2 | 1.7786 |
| 3,000,000 | 1 | 2 | 2 | 3 | 3 | 4 | 2.6679 |

### the three roads, each with its price

- **A keep 8%, raise the capital**: 1 lot needs 1,124,479 CNY (+124,479); the ticket's 4 lot(s) need 4,497,916 CNY.
- **B keep 1,000,000 CNY, lower the target**: 1 lot needs 8.9958% (+0.9958pp); the ticket's 4 lot(s) need 35.9833%.
- **C keep both**: 0 lot(s) -- the sleeve is not expressible at this rung and simply does not trade.

The three roads are not a preference ordering: A spends capital, B spends risk, C spends the sleeve. Picking one changes the specification (either the capital rung or the vol target), so this face prints their prices and stops there.

## IM

| capital | target | vol of 1 lot (hedged) | budget at target | lots (fraction) |
|---|---|---|---|---|
| 1,000,000 CNY | 8% | 92,207.68 CNY | 80,000.00 CNY | 0.8676 |

**The same sentence, read three ways at this capital and target: `0` / `1` / `4` lots** (vol <= target / nearest integer / the ticket's own size). Verdict: **THE_RULER_DECIDES_THE_LOTS**.

The ticket's 4 lot(s) carry 368,830.72 CNY of annual vol against a 80,000.00 CNY budget -- **4.6104x the budget**, 36.88% of capital; holding them inside the target would take 4,610,384 CNY of capital.

### capital ladder (k lots at the stated target)

| lots | capital needed (CNY) | vs the book's capital | affordable |
|---|---|---|---|
| 1 | 1,152,596 | +152,596 | no |
| 2 | 2,305,192 | +1,305,192 | no |
| 3 | 3,457,788 | +2,457,788 | no |
| 4 | 4,610,384 | +3,610,384 | no |
| 5 | 5,762,980 | +4,762,980 | no |
| 6 | 6,915,576 | +5,915,576 | no |
| 7 | 8,068,172 | +7,068,172 | no |
| 8 | 9,220,768 | +8,220,768 | no |

### target ladder (k lots at the stated capital)

| lots | target that would be (%) | vs the stated target (pp) | achievable |
|---|---|---|---|
| 1 | 9.2208 | +1.2208 | no |
| 2 | 18.4415 | +10.4415 | no |
| 3 | 27.6623 | +19.6623 | no |
| 4 | 36.8831 | +28.8831 | no |
| 5 | 46.1038 | +38.1038 | no |
| 6 | 55.3246 | +47.3246 | no |
| 7 | 64.5454 | +56.5454 | no |
| 8 | 73.7661 | +65.7661 | no |

### capital x target -> whole lots (vol <= target)

| capital (CNY) | 4% | 6% | 8% | 9% | 10% | 12% | lots at the book's 8% (fraction) |
|---|---|---|---|---|---|---|---|
| 1,000,000 | 0 | 0 | 0 | 0 | 1 | 1 | 0.8676 |
| 1,250,000 | 0 | 0 | 1 | 1 | 1 | 1 | 1.0845 |
| 1,500,000 | 0 | 0 | 1 | 1 | 1 | 1 | 1.3014 |
| 2,000,000 | 0 | 1 | 1 | 1 | 2 | 2 | 1.7352 |
| 3,000,000 | 1 | 1 | 2 | 2 | 3 | 3 | 2.6028 |

### the three roads, each with its price

- **A keep 8%, raise the capital**: 1 lot needs 1,152,596 CNY (+152,596); the ticket's 4 lot(s) need 4,610,384 CNY.
- **B keep 1,000,000 CNY, lower the target**: 1 lot needs 9.2208% (+1.2208pp); the ticket's 4 lot(s) need 36.8831%.
- **C keep both**: 0 lot(s) -- the sleeve is not expressible at this rung and simply does not trade.

The three roads are not a preference ordering: A spends capital, B spends risk, C spends the sleeve. Picking one changes the specification (either the capital rung or the vol target), so this face prints their prices and stops there.

