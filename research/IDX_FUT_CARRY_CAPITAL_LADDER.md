# the carry sleeve: an 8% vol target on a 1,000,000 book is not an integer

evidence cutoff: **2026-11-27** | source: `results/idx_fut_carry_paper/SIZING.json` | generated 2026-11-28T09:13:00

One lot's annualised vol, hedged to the discount, is the whole input here; the face does not re-derive it. 
A fraction of a lot is printed as arithmetic and never as a position: a futures contract is not divisible.

## IC

| capital | target | vol of 1 lot (hedged) | budget at target | lots (fraction) |
|---|---|---|---|---|
| 1,000,000 CNY | 8% | 92,767.89 CNY | 80,000.00 CNY | 0.8624 |

**The same sentence, read three ways at this capital and target: `0` / `1` / `4` lots** (vol <= target / nearest integer / the ticket's own size). Verdict: **THE_RULER_DECIDES_THE_LOTS**.

The ticket's 4 lot(s) carry 371,071.56 CNY of annual vol against a 80,000.00 CNY budget -- **4.6384x the budget**, 37.11% of capital; holding them inside the target would take 4,638,394 CNY of capital.

### capital ladder (k lots at the stated target)

| lots | capital needed (CNY) | vs the book's capital | affordable |
|---|---|---|---|
| 1 | 1,159,599 | +159,599 | no |
| 2 | 2,319,197 | +1,319,197 | no |
| 3 | 3,478,796 | +2,478,796 | no |
| 4 | 4,638,394 | +3,638,394 | no |
| 5 | 5,797,993 | +4,797,993 | no |
| 6 | 6,957,592 | +5,957,592 | no |
| 7 | 8,117,190 | +7,117,190 | no |
| 8 | 9,276,789 | +8,276,789 | no |

### target ladder (k lots at the stated capital)

| lots | target that would be (%) | vs the stated target (pp) | achievable |
|---|---|---|---|
| 1 | 9.2768 | +1.2768 | no |
| 2 | 18.5536 | +10.5536 | no |
| 3 | 27.8304 | +19.8304 | no |
| 4 | 37.1072 | +29.1072 | no |
| 5 | 46.3839 | +38.3839 | no |
| 6 | 55.6607 | +47.6607 | no |
| 7 | 64.9375 | +56.9375 | no |
| 8 | 74.2143 | +66.2143 | no |

### capital x target -> whole lots (vol <= target)

| capital (CNY) | 4% | 6% | 8% | 9% | 10% | 12% | lots at the book's 8% (fraction) |
|---|---|---|---|---|---|---|---|
| 1,000,000 | 0 | 0 | 0 | 0 | 1 | 1 | 0.8624 |
| 1,250,000 | 0 | 0 | 1 | 1 | 1 | 1 | 1.0780 |
| 1,500,000 | 0 | 0 | 1 | 1 | 1 | 1 | 1.2936 |
| 2,000,000 | 0 | 1 | 1 | 1 | 2 | 2 | 1.7247 |
| 3,000,000 | 1 | 1 | 2 | 2 | 3 | 3 | 2.5871 |

### the three roads, each with its price

- **A keep 8%, raise the capital**: 1 lot needs 1,159,599 CNY (+159,599); the ticket's 4 lot(s) need 4,638,394 CNY.
- **B keep 1,000,000 CNY, lower the target**: 1 lot needs 9.2768% (+1.2768pp); the ticket's 4 lot(s) need 37.1072%.
- **C keep both**: 0 lot(s) -- the sleeve is not expressible at this rung and simply does not trade.

The three roads are not a preference ordering: A spends capital, B spends risk, C spends the sleeve. Picking one changes the specification (either the capital rung or the vol target), so this face prints their prices and stops there.

## IM

| capital | target | vol of 1 lot (hedged) | budget at target | lots (fraction) |
|---|---|---|---|---|
| 1,000,000 CNY | 8% | 93,599.77 CNY | 80,000.00 CNY | 0.8547 |

**The same sentence, read three ways at this capital and target: `0` / `1` / `4` lots** (vol <= target / nearest integer / the ticket's own size). Verdict: **THE_RULER_DECIDES_THE_LOTS**.

The ticket's 4 lot(s) carry 374,399.08 CNY of annual vol against a 80,000.00 CNY budget -- **4.68x the budget**, 37.44% of capital; holding them inside the target would take 4,679,988 CNY of capital.

### capital ladder (k lots at the stated target)

| lots | capital needed (CNY) | vs the book's capital | affordable |
|---|---|---|---|
| 1 | 1,169,997 | +169,997 | no |
| 2 | 2,339,994 | +1,339,994 | no |
| 3 | 3,509,991 | +2,509,991 | no |
| 4 | 4,679,988 | +3,679,988 | no |
| 5 | 5,849,986 | +4,849,986 | no |
| 6 | 7,019,983 | +6,019,983 | no |
| 7 | 8,189,980 | +7,189,980 | no |
| 8 | 9,359,977 | +8,359,977 | no |

### target ladder (k lots at the stated capital)

| lots | target that would be (%) | vs the stated target (pp) | achievable |
|---|---|---|---|
| 1 | 9.3600 | +1.3600 | no |
| 2 | 18.7200 | +10.7200 | no |
| 3 | 28.0799 | +20.0799 | no |
| 4 | 37.4399 | +29.4399 | no |
| 5 | 46.7999 | +38.7999 | no |
| 6 | 56.1599 | +48.1599 | no |
| 7 | 65.5198 | +57.5198 | no |
| 8 | 74.8798 | +66.8798 | no |

### capital x target -> whole lots (vol <= target)

| capital (CNY) | 4% | 6% | 8% | 9% | 10% | 12% | lots at the book's 8% (fraction) |
|---|---|---|---|---|---|---|---|
| 1,000,000 | 0 | 0 | 0 | 0 | 1 | 1 | 0.8547 |
| 1,250,000 | 0 | 0 | 1 | 1 | 1 | 1 | 1.0684 |
| 1,500,000 | 0 | 0 | 1 | 1 | 1 | 1 | 1.2821 |
| 2,000,000 | 0 | 1 | 1 | 1 | 2 | 2 | 1.7094 |
| 3,000,000 | 1 | 1 | 2 | 2 | 3 | 3 | 2.5641 |

### the three roads, each with its price

- **A keep 8%, raise the capital**: 1 lot needs 1,169,997 CNY (+169,997); the ticket's 4 lot(s) need 4,679,988 CNY.
- **B keep 1,000,000 CNY, lower the target**: 1 lot needs 9.3600% (+1.3600pp); the ticket's 4 lot(s) need 37.4399%.
- **C keep both**: 0 lot(s) -- the sleeve is not expressible at this rung and simply does not trade.

The three roads are not a preference ordering: A spends capital, B spends risk, C spends the sleeve. Picking one changes the specification (either the capital rung or the vol target), so this face prints their prices and stops there.

