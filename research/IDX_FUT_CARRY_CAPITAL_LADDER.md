# the carry sleeve: an 8% vol target on a 1,000,000 book is not an integer

evidence cutoff: **2026-11-16** | source: `results/idx_fut_carry_paper/SIZING.json` | generated 2026-11-17T16:10:22

One lot's annualised vol, hedged to the discount, is the whole input here; the face does not re-derive it. 
A fraction of a lot is printed as arithmetic and never as a position: a futures contract is not divisible.

## IC

| capital | target | vol of 1 lot (hedged) | budget at target | lots (fraction) |
|---|---|---|---|---|
| 1,000,000 CNY | 8% | 89,822.60 CNY | 80,000.00 CNY | 0.8906 |

**The same sentence, read three ways at this capital and target: `0` / `1` / `4` lots** (vol <= target / nearest integer / the ticket's own size). Verdict: **THE_RULER_DECIDES_THE_LOTS**.

The ticket's 4 lot(s) carry 359,290.40 CNY of annual vol against a 80,000.00 CNY budget -- **4.4911x the budget**, 35.93% of capital; holding them inside the target would take 4,491,130 CNY of capital.

### capital ladder (k lots at the stated target)

| lots | capital needed (CNY) | vs the book's capital | affordable |
|---|---|---|---|
| 1 | 1,122,782 | +122,782 | no |
| 2 | 2,245,565 | +1,245,565 | no |
| 3 | 3,368,348 | +2,368,348 | no |
| 4 | 4,491,130 | +3,491,130 | no |
| 5 | 5,613,912 | +4,613,912 | no |
| 6 | 6,736,695 | +5,736,695 | no |
| 7 | 7,859,478 | +6,859,478 | no |
| 8 | 8,982,260 | +7,982,260 | no |

### target ladder (k lots at the stated capital)

| lots | target that would be (%) | vs the stated target (pp) | achievable |
|---|---|---|---|
| 1 | 8.9823 | +0.9823 | no |
| 2 | 17.9645 | +9.9645 | no |
| 3 | 26.9468 | +18.9468 | no |
| 4 | 35.9290 | +27.9290 | no |
| 5 | 44.9113 | +36.9113 | no |
| 6 | 53.8936 | +45.8936 | no |
| 7 | 62.8758 | +54.8758 | no |
| 8 | 71.8581 | +63.8581 | no |

### capital x target -> whole lots (vol <= target)

| capital (CNY) | 4% | 6% | 8% | 9% | 10% | 12% | lots at the book's 8% (fraction) |
|---|---|---|---|---|---|---|---|
| 1,000,000 | 0 | 0 | 0 | 1 | 1 | 1 | 0.8906 |
| 1,250,000 | 0 | 0 | 1 | 1 | 1 | 1 | 1.1133 |
| 1,500,000 | 0 | 1 | 1 | 1 | 1 | 2 | 1.3360 |
| 2,000,000 | 0 | 1 | 1 | 2 | 2 | 2 | 1.7813 |
| 3,000,000 | 1 | 2 | 2 | 3 | 3 | 4 | 2.6719 |

### the three roads, each with its price

- **A keep 8%, raise the capital**: 1 lot needs 1,122,782 CNY (+122,782); the ticket's 4 lot(s) need 4,491,130 CNY.
- **B keep 1,000,000 CNY, lower the target**: 1 lot needs 8.9823% (+0.9823pp); the ticket's 4 lot(s) need 35.9290%.
- **C keep both**: 0 lot(s) -- the sleeve is not expressible at this rung and simply does not trade.

The three roads are not a preference ordering: A spends capital, B spends risk, C spends the sleeve. Picking one changes the specification (either the capital rung or the vol target), so this face prints their prices and stops there.

## IM

| capital | target | vol of 1 lot (hedged) | budget at target | lots (fraction) |
|---|---|---|---|---|
| 1,000,000 CNY | 8% | 92,018.43 CNY | 80,000.00 CNY | 0.8694 |

**The same sentence, read three ways at this capital and target: `0` / `1` / `4` lots** (vol <= target / nearest integer / the ticket's own size). Verdict: **THE_RULER_DECIDES_THE_LOTS**.

The ticket's 4 lot(s) carry 368,073.72 CNY of annual vol against a 80,000.00 CNY budget -- **4.6009x the budget**, 36.81% of capital; holding them inside the target would take 4,600,922 CNY of capital.

### capital ladder (k lots at the stated target)

| lots | capital needed (CNY) | vs the book's capital | affordable |
|---|---|---|---|
| 1 | 1,150,230 | +150,230 | no |
| 2 | 2,300,461 | +1,300,461 | no |
| 3 | 3,450,691 | +2,450,691 | no |
| 4 | 4,600,922 | +3,600,922 | no |
| 5 | 5,751,152 | +4,751,152 | no |
| 6 | 6,901,382 | +5,901,382 | no |
| 7 | 8,051,613 | +7,051,613 | no |
| 8 | 9,201,843 | +8,201,843 | no |

### target ladder (k lots at the stated capital)

| lots | target that would be (%) | vs the stated target (pp) | achievable |
|---|---|---|---|
| 1 | 9.2018 | +1.2018 | no |
| 2 | 18.4037 | +10.4037 | no |
| 3 | 27.6055 | +19.6055 | no |
| 4 | 36.8074 | +28.8074 | no |
| 5 | 46.0092 | +38.0092 | no |
| 6 | 55.2111 | +47.2111 | no |
| 7 | 64.4129 | +56.4129 | no |
| 8 | 73.6147 | +65.6147 | no |

### capital x target -> whole lots (vol <= target)

| capital (CNY) | 4% | 6% | 8% | 9% | 10% | 12% | lots at the book's 8% (fraction) |
|---|---|---|---|---|---|---|---|
| 1,000,000 | 0 | 0 | 0 | 0 | 1 | 1 | 0.8694 |
| 1,250,000 | 0 | 0 | 1 | 1 | 1 | 1 | 1.0867 |
| 1,500,000 | 0 | 0 | 1 | 1 | 1 | 1 | 1.3041 |
| 2,000,000 | 0 | 1 | 1 | 1 | 2 | 2 | 1.7388 |
| 3,000,000 | 1 | 1 | 2 | 2 | 3 | 3 | 2.6082 |

### the three roads, each with its price

- **A keep 8%, raise the capital**: 1 lot needs 1,150,230 CNY (+150,230); the ticket's 4 lot(s) need 4,600,922 CNY.
- **B keep 1,000,000 CNY, lower the target**: 1 lot needs 9.2018% (+1.2018pp); the ticket's 4 lot(s) need 36.8074%.
- **C keep both**: 0 lot(s) -- the sleeve is not expressible at this rung and simply does not trade.

The three roads are not a preference ordering: A spends capital, B spends risk, C spends the sleeve. Picking one changes the specification (either the capital rung or the vol target), so this face prints their prices and stops there.

