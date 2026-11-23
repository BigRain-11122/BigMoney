# The order ticket: what 90.13% of the book is in lots

Generated 2026-11-24T05:27:04+08:00 · evidence cutoff 2026-11-20 · machine bm-c

## Why this face exists

r2023-r2026 decided how much insurance to buy, in shares of the book; no face said what that is in lots, what the rounding costs in beta, how much capital the hedge ties up, or how far the futures margin is from a call.

Nothing is re-fitted. The size comes from `results/astock_veto_hedge_default.json` (k = 1.00, beta = 0.9013, i.e. 90.13% of the book); the two prices come from the last bar of their own panels. The margin ratios are broker terms this repository cannot observe, so they are printed as axes and every rung is shown.

## The two instruments, as of the last bar

| | 512100 (ETF) | IM (index future) |
|---|---|---|
| bar | 2026-11-20 | 2026-11-20 |
| close | 2.300 | 5545.6 |
| one lot | 100 shares = **230 CNY** | 200 x index = **1,109,120 CNY** |
| last session | -4.80% | -5.64% |
| traded that day | 11,829,132,261 CNY | 288,059 lots |

**One contract is 4822 times one ETF lot.** That ratio is the whole story of this face: the two arms are the same hedge and they are not the same order.

## What rounding costs, in beta

`floor` never overshoots the target; `round` is the nearest whole number. The error is `|lots x one_lot / capital - target beta|`.

| capital | arm | lots needed | floor | beta after floor | round | beta after round | beta error |
|---|---|---|---|---|---|---|---|
| 1,000,000 | 512100 | 3918.832 | 3918 | 0.9011 | 3919 | 0.9014 | 0.00004 |
| 1,000,000 | IM | 0.813 | 0 | 0.0000 | 1 | 1.1091 | 0.20779 |
| 3,000,000 | 512100 | 11756.495 | 11756 | 0.9013 | 11756 | 0.9013 | 0.00004 |
| 3,000,000 | IM | 2.438 | 2 | 0.7394 | 2 | 0.7394 | 0.16192 |
| 10,000,000 | 512100 | 39188.317 | 39188 | 0.9013 | 39188 | 0.9013 | 0.00001 |
| 10,000,000 | IM | 8.127 | 8 | 0.8873 | 8 | 0.8873 | 0.01404 |
| 20,000,000 | 512100 | 78376.633 | 78376 | 0.9013 | 78377 | 0.9013 | 0.00000 |
| 20,000,000 | IM | 16.253 | 16 | 0.8873 | 16 | 0.8873 | 0.01404 |

A half-lot is the most a fill can be off, so the smallest capital at which the rounding moves beta by no more than 0.50% is `0.5 x one_lot / 0.50%`:

* 512100: **23,000 CNY**
* IM: **110,912,000 CNY**

At the smallest published capital (1,000,000 CNY) one contract is **110.9% of the book**, so the closest fill is either no hedge at all or a book hedged at **1.11 units of beta** instead of 0.90 — the same order, two different books.

### The capitals where one and two contracts are exactly beta-neutral

| contracts | capital that makes it exactly neutral |
|---|---|
| 1 | 1,230,535 CNY |
| 2 | 2,461,071 CNY |

## What the hedge ties up

Margin per rung, plus — for the ETF short — the proceeds the sale leaves frozen as collateral. `committed` is what is not available to the rest of the account while the hedge is on.

### 1,000,000 CNY

| arm | ratio | margin | frozen proceeds | committed | share of capital |
|---|---|---|---|---|---|
| 512100 | 50% | 450,685 | 901,370 | 1,352,055 | 135% |
| 512100 | 80% | 721,096 | 901,370 | 1,622,466 | 162% |
| 512100 | 100% | 901,370 | 901,370 | 1,802,740 | 180% |
| IM (1 lot) | 12% | 133,094 | — | 133,094 | 13% |
| IM (1 lot) | 15% | 166,368 | — | 166,368 | 17% |

### 3,000,000 CNY

| arm | ratio | margin | frozen proceeds | committed | share of capital |
|---|---|---|---|---|---|
| 512100 | 50% | 1,351,940 | 2,703,880 | 4,055,820 | 135% |
| 512100 | 80% | 2,163,104 | 2,703,880 | 4,866,984 | 162% |
| 512100 | 100% | 2,703,880 | 2,703,880 | 5,407,760 | 180% |
| IM (2 lot) | 12% | 266,189 | — | 266,189 | 9% |
| IM (2 lot) | 15% | 332,736 | — | 332,736 | 11% |

### What one CNY of target notional ties up

At the smallest capital, cash committed per CNY of the 901,331 CNY the hedge is supposed to be worth:

| arm and rung | CNY committed per CNY of target notional |
|---|---|
| 512100 at 50% margin | 1.50 |
| 512100 at 80% margin | 1.80 |
| 512100 at 100% margin | 2.00 |
| IM at 12% margin | 0.15 |
| IM at 15% margin | 0.18 |

The future is the cheaper way to hold the exposure by an order of magnitude — 0.12–0.15 CNY per CNY against 1.50–2.00 for a 融券 short, whose sale proceeds are frozen on top of the margin. That is exactly why the arm that wins on funding is the arm that cannot be sized: cheap capital does not buy the beta you asked for.

## How far the futures margin is from a call

The crude bound: a short loses its whole margin at an adverse move equal to the margin ratio. On the latest session that instrument moved **-5.64%**, which is 47% of the 12% rung and 38% of the 15% rung — one session, before any call.

| ratio | adverse move to zero equity |
|---|---|
| 12% | 12% |
| 15% | 15% |

## What the hedge costs to keep rolling

Quoted from the parent's spec, not re-estimated: 12.6 rolls a year, 16 bp per roll on the shorted notional, i.e. **2.02% of the shorted notional a year** and **1.82% of the book**.

The futures arm pays its roll inside the price. Its median basis is **-0.629%** — a negative median basis is the future trading below the index; the direction is against a short, but it cannot be annualised from a median taken across mixed expiries -- not modelled here.

## Liquidity is not the constraint on either arm

At the smallest capital the ETF short is 76.2 ppm of that day's traded value and the contract is 3.5 ppm of that day's traded lots. What cannot be read from here is 券源 — whether a broker has the inventory to lend — and that is a desk question, not a panel question.

## The answer

**LOT_IS_FREE_ON_THE_ETF_AND_A_FOUR_THOUSANDTH_OF_THE_BOOK_ON_THE_FUTURE** — the ETF's half-lot error is 0.00004 of beta at the smallest capital, while one contract is 110.9% of that book and cannot be made beta-neutral with any whole number.

Read two numbers together before placing anything. At an 80% 融券 ratio the ETF short at the smallest capital ties up **1,622,466 CNY** — **162% of the book** — because the margin and the frozen sale proceeds are both unavailable while the hedge is on. So "90% of the book" is not 90% of the account: it is a promise of about **1.6 times** the book in cash, and the futures arm that would cost a tenth of that cannot be filled at this size.

