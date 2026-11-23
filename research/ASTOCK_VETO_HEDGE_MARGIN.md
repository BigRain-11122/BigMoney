# Where would the short hedge have been called?

r2033 prints a 12% margin ratio and credits the cash that is left over with interest; r2027 prints a crude bound -- a short loses its whole margin at an adverse move equal to the margin ratio. Both are statements about one number on one day. A margin account is a path: it is marked every session, it is called the first session it is under maintenance, and the capital the hedge consumes is the deepest that path ever went.

Evidence cutoff **2026-11-20**, panel `data/futures_daily/IM.csv` (1050 bars, 2022-07-22 .. 2026-11-20, -20.28% total), parent beta face `results/astock_veto_hedgeable_beta.json` (generated 2026-11-24T03:29:09+08:00), crude-bound face `results/astock_veto_hedge_lots.json` (generated 2026-11-24T05:27:04+08:00). Short 901331 CNY of notional (beta 0.9013 x 1000000 capital x k=1.00).

## 1. Walk the account: where it first goes under maintenance

| initial margin | maintenance | cash posted | first call | sessions under | lowest equity | top-up needed |
|---|---|---|---|---|---|---|
| 8% | 6% | 72107 | 2022-07-28 | 346 | -259725 | 313805 |
| 12% | 8% | 108160 | 2022-08-11 | 322 | -223671 | 295778 |
| 15% | 10% | 135200 | 2022-08-16 | 313 | -196632 | 286765 |

Profits left in the account. The ratio is a per-contract minimum; the call arrives when the marks have eaten it.

## 2. What the position actually consumes

| rung | maintenance | cash, profits kept | % of notional | % of book | cash, profits swept | % of notional |
|---|---|---|---|---|---|---|
| 8% | 6% | 385911 | 42.8% | 38.6% | 816002 | 90.5% |
| 12% | 8% | 403938 | 44.8% | 40.4% | 834029 | 92.5% |
| 15% | 10% | 421964 | 46.8% | 42.2% | 852055 | 94.5% |

Read the middle column against r2033's capital table: that face prices the hedge at 12% of notional and lets the rest earn. The rest is not free -- it is the top-up this account needs to survive its own history.

## 3. The crude bound, measured

| horizon | worst rally | short loss, % of notional | multiple of the 12% rung | ending |
|---|---|---|---|---|
| 1 session | 10.35% | -10.35% | 0.86 x | 2024-02-06 |
| 5 sessions | 33.67% | -33.67% | 2.81 x | 2024-10-08 |
| 10 sessions | 40.82% | -40.82% | 3.40 x | 2024-10-08 |
| 20 sessions | 36.22% | -36.22% | 3.02 x | 2024-10-28 |
| 40 sessions | 43.52% | -43.52% | 3.63 x | 2024-11-13 |
| 60 sessions | 44.80% | -44.80% | 3.73 x | 2024-12-12 |

r2027's bound is the first row. The row that matters is the one whose horizon is the holding period: an excursion is not a session.

## 4. What the call costs

At the 12% rung the short is closed on **2022-08-11** with **-42678 CNY** realised. The remaining 1035 sessions are unhedged, and over them the short would have earned **110374 CNY** -- **11.0% of the book**. That is the price of a margin call: not the loss at the call (which is small and already known), but the insurance that is no longer there.

## 5. Solvent and illiquid at the same time

Marked on the book's own 20-bar schedule, the pair (long book + short future) never went below **5703 CNY** over 52 periods and finished at **450291 CNY**. The futures account alone, marked daily, was under maintenance. Both statements are true: the collateral exists, it is just not in the account that gets marked every session. A hedge that is solvent at month-end and called at mid-month is a hedge with a funding problem, not a risk problem.

## 6. Verdict

**`THE_MARGIN_RATIO_IS_NOT_THE_CAPITAL+CALL_ARRIVES_BEFORE_THE_INSURANCE_PAYS`**

Every flag below is computed from its own inputs and several can hold at once; the headline names the ones that change what a reader would do.

- `THE_MARGIN_RATIO_IS_NOT_THE_CAPITAL` -- the ratio is a per-contract minimum; the cash the position consumes is the deepest drawdown of its own marks, an order of magnitude larger
- `CALL_ARRIVES_BEFORE_THE_INSURANCE_PAYS` -- the first call arrives within weeks of inception, before the drawdown the hedge was bought for
- `SWEEPING_PROFITS_DOUBLES_THE_REQUIREMENT` -- sweeping excess margin is the usual treasury habit and it multiplies the cash that must sit in the account
- `THE_CRUDE_BOUND_UNDERSTATES_THE_PATH` -- a single adverse session is not the excursion; the crude bound is off by a multiple that changes the answer

## 7. Readings

- **R1.** at the 12% rung the account is under maintenance on 2022-08-11 -- the 15th of 1050 sessions, 108160 CNY of margin against a 901331 CNY notional, and stays under it on 322 sessions
- **R2.** the cash the position actually consumes is 403938 CNY (44.8% of notional, 40.4% of the book) if profits stay in the account, against the 108160 CNY the 12% ratio implies -- 3.7 times the ratio
- **R3.** sweeping the excess -- the usual treasury habit -- raises the requirement to 834029 CNY (92.5% of notional), 2.1 times the no-sweep number: the profits are the buffer, and taking them out is what makes the account thin
- **R4.** being called is not free: the short realises -42678 CNY at the call and the remaining 1035 sessions of hedge are gone -- 110374 CNY of short P&L, 11.0% of the book, that the account was closed out of
- **R5.** the crude bound is one session of a four-year path: the worst single session is 10.4% (0.9 times the 12% ratio) but the worst 20-session rally ending 2024-10-28 is 36.2%, 3.0 times the ratio -- a bound quoted in sessions cannot price an excursion quoted in months
- **R6.** solvent and illiquid at the same time: marked on the book's 20-bar schedule the pair never went below 5703 CNY over 52 periods, while the futures account alone went under maintenance -- the collateral exists, it just is not in the account that gets marked daily

## 8. What this face does not settle

- the panel is the IM main-continuous close; a roll is a calendar spread paid once, and that cost is inside the marks rather than separated from them
- the settle column on the panel is empty, so every mark here is a close mark; a broker marks to settlement, and the two differ most on the days that matter
- the margin ratios are broker terms this repository cannot observe; they are printed as axes and no single rung is claimed as the one in force
- no interest is credited or charged on the margin balance, and a margin call in practice allows securities as collateral at a haircut, which is not modelled
- the book is only marked every 20 bars (that is the parent's booking), so the net-account reading is a 20-bar statement sitting next to a daily statement -- the mismatch is real and is the liquidity question, not an approximation to be smoothed
- the notional is held constant; a real account would de-lever after a call, and this face prices the call instead of modelling what an operator does next

Machine `bm-c`, generated 2026-11-24T07:45:02+08:00.

## 9. Reproduction

```
python scripts/astock_veto_hedge_margin.py selftest
python scripts/astock_veto_hedge_margin.py run
python scripts/astock_veto_hedge_margin.py check
```
