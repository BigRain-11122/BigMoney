# the carry sleeve: an 8% vol target on a 1,000,000 book is not an integer

evidence cutoff: **2026-11-26** | source: `results/idx_fut_carry_paper/SIZING.json` | generated 2026-11-27T02:33:48

One lot's annualised vol, hedged to the discount, is the whole input here; the face does not re-derive it. 
A fraction of a lot is printed as arithmetic and never as a position: a futures contract is not divisible.

## IC

| capital | target | vol of 1 lot (hedged) | budget at target | lots (fraction) |
|---|---|---|---|---|
| 1,000,000 CNY | 8% | 91,029.00 CNY | 80,000.00 CNY | 0.8788 |

**The same sentence, read three ways at this capital and target: `0` / `1` / `4` lots** (vol <= target / nearest integer / the ticket's own size). Verdict: **THE_RULER_DECIDES_THE_LOTS**.

The ticket's 4 lot(s) carry 364,116.00 CNY of annual vol against a 80,000.00 CNY budget -- **4.5514x the budget**, 36.41% of capital; holding them inside the target would take 4,551,450 CNY of capital.

### capital ladder (k lots at the stated target)

| lots | capital needed (CNY) | vs the book's capital | affordable |
|---|---|---|---|
| 1 | 1,137,862 | +137,862 | no |
| 2 | 2,275,725 | +1,275,725 | no |
| 3 | 3,413,588 | +2,413,588 | no |
| 4 | 4,551,450 | +3,551,450 | no |
| 5 | 5,689,312 | +4,689,312 | no |
| 6 | 6,827,175 | +5,827,175 | no |
| 7 | 7,965,038 | +6,965,038 | no |
| 8 | 9,102,900 | +8,102,900 | no |

### target ladder (k lots at the stated capital)

| lots | target that would be (%) | vs the stated target (pp) | achievable |
|---|---|---|---|
| 1 | 9.1029 | +1.1029 | no |
| 2 | 18.2058 | +10.2058 | no |
| 3 | 27.3087 | +19.3087 | no |
| 4 | 36.4116 | +28.4116 | no |
| 5 | 45.5145 | +37.5145 | no |
| 6 | 54.6174 | +46.6174 | no |
| 7 | 63.7203 | +55.7203 | no |
| 8 | 72.8232 | +64.8232 | no |

### capital x target -> whole lots (vol <= target)

| capital (CNY) | 4% | 6% | 8% | 9% | 10% | 12% | lots at the book's 8% (fraction) |
|---|---|---|---|---|---|---|---|
| 1,000,000 | 0 | 0 | 0 | 0 | 1 | 1 | 0.8788 |
| 1,250,000 | 0 | 0 | 1 | 1 | 1 | 1 | 1.0986 |
| 1,500,000 | 0 | 0 | 1 | 1 | 1 | 1 | 1.3183 |
| 2,000,000 | 0 | 1 | 1 | 1 | 2 | 2 | 1.7577 |
| 3,000,000 | 1 | 1 | 2 | 2 | 3 | 3 | 2.6365 |

### the three roads, each with its price

- **A keep 8%, raise the capital**: 1 lot needs 1,137,862 CNY (+137,862); the ticket's 4 lot(s) need 4,551,450 CNY.
- **B keep 1,000,000 CNY, lower the target**: 1 lot needs 9.1029% (+1.1029pp); the ticket's 4 lot(s) need 36.4116%.
- **C keep both**: 0 lot(s) -- the sleeve is not expressible at this rung and simply does not trade.

The three roads are not a preference ordering: A spends capital, B spends risk, C spends the sleeve. Picking one changes the specification (either the capital rung or the vol target), so this face prints their prices and stops there.

## IM

| capital | target | vol of 1 lot (hedged) | budget at target | lots (fraction) |
|---|---|---|---|---|
| 1,000,000 CNY | 8% | 93,259.93 CNY | 80,000.00 CNY | 0.8578 |

**The same sentence, read three ways at this capital and target: `0` / `1` / `4` lots** (vol <= target / nearest integer / the ticket's own size). Verdict: **THE_RULER_DECIDES_THE_LOTS**.

The ticket's 4 lot(s) carry 373,039.72 CNY of annual vol against a 80,000.00 CNY budget -- **4.663x the budget**, 37.30% of capital; holding them inside the target would take 4,662,996 CNY of capital.

### capital ladder (k lots at the stated target)

| lots | capital needed (CNY) | vs the book's capital | affordable |
|---|---|---|---|
| 1 | 1,165,749 | +165,749 | no |
| 2 | 2,331,498 | +1,331,498 | no |
| 3 | 3,497,247 | +2,497,247 | no |
| 4 | 4,662,996 | +3,662,996 | no |
| 5 | 5,828,746 | +4,828,746 | no |
| 6 | 6,994,495 | +5,994,495 | no |
| 7 | 8,160,244 | +7,160,244 | no |
| 8 | 9,325,993 | +8,325,993 | no |

### target ladder (k lots at the stated capital)

| lots | target that would be (%) | vs the stated target (pp) | achievable |
|---|---|---|---|
| 1 | 9.3260 | +1.3260 | no |
| 2 | 18.6520 | +10.6520 | no |
| 3 | 27.9780 | +19.9780 | no |
| 4 | 37.3040 | +29.3040 | no |
| 5 | 46.6300 | +38.6300 | no |
| 6 | 55.9560 | +47.9560 | no |
| 7 | 65.2820 | +57.2820 | no |
| 8 | 74.6079 | +66.6079 | no |

### capital x target -> whole lots (vol <= target)

| capital (CNY) | 4% | 6% | 8% | 9% | 10% | 12% | lots at the book's 8% (fraction) |
|---|---|---|---|---|---|---|---|
| 1,000,000 | 0 | 0 | 0 | 0 | 1 | 1 | 0.8578 |
| 1,250,000 | 0 | 0 | 1 | 1 | 1 | 1 | 1.0723 |
| 1,500,000 | 0 | 0 | 1 | 1 | 1 | 1 | 1.2867 |
| 2,000,000 | 0 | 1 | 1 | 1 | 2 | 2 | 1.7156 |
| 3,000,000 | 1 | 1 | 2 | 2 | 3 | 3 | 2.5735 |

### the three roads, each with its price

- **A keep 8%, raise the capital**: 1 lot needs 1,165,749 CNY (+165,749); the ticket's 4 lot(s) need 4,662,996 CNY.
- **B keep 1,000,000 CNY, lower the target**: 1 lot needs 9.3260% (+1.3260pp); the ticket's 4 lot(s) need 37.3040%.
- **C keep both**: 0 lot(s) -- the sleeve is not expressible at this rung and simply does not trade.

The three roads are not a preference ordering: A spends capital, B spends risk, C spends the sleeve. Picking one changes the specification (either the capital rung or the vol target), so this face prints their prices and stops there.

