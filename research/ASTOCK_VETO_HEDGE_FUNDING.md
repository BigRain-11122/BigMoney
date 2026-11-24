# What the hedge costs once you pay for the collateral and the lender

r2033 put both carriers of this hedge on one ruler and the reader has been quoting the result since: 12.39% (ETF) against 12.31% (IM) on the same 52 periods, a 0.354pp gap inside a 1pp tie band. That comparison is gross of two costs the same family prices elsewhere -- the securities the ETF leg rents, and the cash either leg must post and cannot invest. This face charges both and asks whether the carrier ordering and the size decision survive.

Evidence cutoff **2026-11-20**. 52 shared periods (2022-07-26 .. 2026-11-11), 12.6 periods a year. Beta 0.9013 on 1000000 CNY of book, short 901331 CNY of notional. Parents: beta `results/astock_veto_hedgeable_beta.json` (generated 2026-11-24T03:29:09+08:00), carrier `results/astock_veto_hedge_carrier.json` (generated 2026-11-24T07:08:17+08:00), margin `results/astock_veto_hedge_margin.json` (generated 2026-11-24T07:45:02+08:00).

## 1. Three rulers on the same k

| ruler | ETF annual | ETF vol | IM annual | IM vol | IM minus ETF |
|---|---|---|---|---|---|
| gross of lender and collateral | 12.39% | 11.39% | 12.31% | 10.94% | -0.08pp |
| net of the lender at 2.00% | 10.40% | 11.39% | 12.31% | 10.94% | 1.91pp |
| net of the lender at 5.00% | 7.47% | 11.39% | 12.31% | 10.94% | 4.84pp |
| net of the lender at 8.00% | 4.62% | 11.39% | 12.31% | 10.94% | 7.70pp |

The first row reproduces the carrier face's own arms to the last digit -- that is the anchor, not a re-derivation. r2033's quoted number is the leg-to-leg gap (-0.35pp), which the long side dilutes inside a hedged book; both are printed because a reader can quote either. What the rent does to the arm gap is the row that matters: it is an order of magnitude larger than the gap itself.

## 2. Funded: book plus the block, divided by the capital committed

| carrier | block | committed | gross annual | funded annual | give-up | block's give-up, CNY | rent, CNY |
|---|---|---|---|---|---|---|---|
| IM future (r2035 path, 12% rung) | 403938 | 1403938 | 12.31% | 9.39% | 2.92pp | 41650 | 0 |
| 512100 short, haircut 50%, rent 2.00% | 450666 | 1450666 | 10.40% | 7.88% | 2.52pp | 37847 | 18027 |
| 512100 short, haircut 50%, rent 5.00% | 450666 | 1450666 | 7.47% | 5.90% | 1.57pp | 24656 | 45067 |
| 512100 short, haircut 50%, rent 8.00% | 450666 | 1450666 | 4.62% | 3.95% | 0.67pp | 11788 | 72107 |
| 512100 short, haircut 80%, rent 2.00% | 721065 | 1721065 | 10.40% | 6.98% | 3.42pp | 60556 | 18027 |
| 512100 short, haircut 80%, rent 5.00% | 721065 | 1721065 | 7.47% | 5.32% | 2.15pp | 39450 | 45067 |
| 512100 short, haircut 80%, rent 8.00% | 721065 | 1721065 | 4.62% | 3.69% | 0.93pp | 18860 | 72107 |
| 512100 short, haircut 100%, rent 2.00% | 901331 | 1901331 | 10.40% | 6.52% | 3.88pp | 75694 | 18027 |
| 512100 short, haircut 100%, rent 5.00% | 901331 | 1901331 | 7.47% | 5.02% | 2.45pp | 49312 | 45067 |
| 512100 short, haircut 100%, rent 8.00% | 901331 | 1901331 | 4.62% | 3.55% | 1.07pp | 23576 | 72107 |

`gross annual` here is already net of the lender, so the two columns do not count the rent twice: the ETF rows are charged the rent first (section 1) and the block second, which is the order the money actually leaves.

## 3. The size decision

| k | IM funded annual (no sweep) | IM funded vol | ETF funded annual, cheapest corner | ETF funded vol |
|---|---|---|---|---|
| 0.0 | 11.03% | 28.44% | 11.03% | 28.44% |
| 0.5 | 10.97% | 14.00% | 8.86% | 11.96% |
| 1.0 | 9.39% | 7.79% | 6.52% | 5.99% |

The block grows with k, so the funded ruler is not the gross ruler shifted: it is the gross ruler tilted against size. Read the two legs down each column rather than across one row.

## 4. Sweeping the account

If the excess margin is swept -- the ordinary treasury habit -- r2035's walk says the futures block is 834029 CNY instead of 403938, and the funded futures leg earns **7.68%** instead of **9.39%**. The leg r2033 priced at 108,160 CNY of blocked capital then holds the largest block in the table, and the funded return of the whole book moves with that habit rather than with any view on the index.

## 5. Verdict

**`THE_TIE_WAS_GROSS_OF_THE_LENDER+THE_RANKING_FLIPS_WHEN_YOU_PAY_FOR_IT`**

Every flag below is computed from its own inputs and several can hold at once; the headline names the ones that change what a reader would do.

- `THE_TIE_WAS_GROSS_OF_THE_LENDER` -- the scarce comparison was priced without the lender; the cheapest rent the family's own table allows already puts the ETF leg a tie band behind
- `EQUAL_CAPITAL_WIDENS_THE_GAP` -- dividing by the capital actually committed multiplies the gross gap, because the leg that blocks more cash also divides by more of it
- `THE_RANKING_FLIPS_WHEN_YOU_PAY_FOR_IT` -- the carrier that led gross of costs trails net of them; the ordering, not just the size of the gap, changes
- `THE_COLLATERAL_COSTS_MORE_THAN_THE_LENDER` -- at the declared reference block (the full haircut) and the cheapest rent, the cash the ETF short must post gives up more return than the lender takes -- at a half haircut it is the smaller of the two, and the page prints both bands rather than picking the friendly one
- `SWEEPING_THE_ACCOUNT_COSTS_TWICE_THE_BLOCK` -- sweeping the margin account's excess is the usual treasury habit and it multiplies the block, so it multiplies the return that block gives up

## 6. Readings

- **R1.** gross of everything, at k=1.0 on 52 periods, the hedged book compounds at 12.39% (ETF) and 12.31% (IM) -- an arm gap of -0.08pp. r2033 published -0.35pp on the two short legs alone; inside the book the same periodicity compounds smaller because the long side dilutes it, which is why both numbers are printed here
- **R2.** charge the lender on the same notional and the tie dissolves: at 2.00% rent the ETF leg lands on 10.40%; at 5.00% rent the ETF leg lands on 7.47%; at 8.00% rent the ETF leg lands on 4.62% -- the arm gap becomes 1.91pp at the cheapest rent, against the 1.00pp band this family calls a tie
- **R3.** on the money you must commit, the futures leg earns 9.39% a year on 1403938 CNY (book 1000000 plus the 403938 r2035 walked out), not the 12.31% it quotes on the book alone -- 2.92pp of annual return given up to hold the block
- **R4.** the ETF leg is funded across a 450666..901331 CNY block and 2.00%..8.00% rent; the band of funded returns runs 3.55% .. 7.88%, and only the cheapest corner of it keeps the leg near the futures buyer
- **R5.** the two costs are not the same size: the ETF block gives up 11788..75694 CNY a year of return and the lender takes 18027..72107 CNY -- the collateral, which r2033 counted as an advantage for the futures leg in principle, is the one that compounds with the haircut
- **R6.** and if the treasury habit of sweeping excess margin is kept, the futures leg needs 834029 CNY and lands on 7.68% funded -- the cheapest carrier in the gross table becomes the one whose block eats the most return
- **R7.** the ordering, at k=1.0, 100% haircut, cheapest rent: funded gap 2.87pp (IM minus ETF), against -0.08pp gross -- the leg that led gross trails net, so the 'tie' compared two prices that neither buyer pays

## 7. What this face does not settle

- the borrow fee is charged on the notional every period and no fee is credited back; a lender that returns part of it, or a locate that fails, is a separate face
- the collateral is modelled as posted and idle at a declared cash yield; in practice a short-sale proceeds balance is frozen and may earn less than a deposit, so this is the optimistic end of the funding question
- the ETF block uses r2033's haircut ladder (50/80/100% of notional); the futures block uses r2035's walked path at the 12% rung -- 403,938 CNY, not the 108,160 a ratio implies
- both legs are marked off their own panels, so an ETF tracking error and its premium/discount remain inside the gap, as on r2033
- the window is the 52 shared periods (the IM panel starts 2022-07); the ETF leg's longer 77-period record is not used anywhere here, exactly as on the carrier face
- the notional is held constant and nothing is rebalanced after a call; a real account de-levers and this face prices the cost of the block instead
- a funded return is not a portfolio recommendation: it says what the money you must commit earns, not what you should commit

Machine `bm-c`, generated 2026-11-24T08:09:49+08:00.

## 8. Reproduction

```
python scripts/astock_veto_hedge_funding.py selftest
python scripts/astock_veto_hedge_funding.py run
python scripts/astock_veto_hedge_funding.py check
```
