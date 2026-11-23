# The hedge ticket is priced after the book it hedges

**Verdict: `DATING_MOVES_THE_ORDER`**

6 of 8 capital rung(s) place a different number of lots when the price is dated with the book instead of after it: 1000000 (etf 3919 -> 3323), 3000000 (etf 11756 -> 9970), 10000000 (etf 39188 -> 33235), 10000000 (im 8 -> 7), 20000000 (etf 78377 -> 66470), 20000000 (im 16 -> 14)

Evidence cutoff **2026-11-20** · generated 2026-11-24T05:39:38+08:00 · machine bm-c

## 1. The two dates

| | date | what it is |
|---|---|---|
| book | 2026-11-11 | the bar the book's positions were last marked on |
| price | 2026-11-20 | the last bar of the two hedge price panels |

The panels are **7 trading bars** past the book.  Nobody has marked the book since 2026-11-11;
the ticket priced its hedge on 2026-11-20 anyway.

| arm | close on 2026-11-11 | close on 2026-11-20 | move over the unmarked days |
|---|---|---|---|
| etf | 2.7120 | 2.3000 | -15.19% |
| im | 6623.0000 | 5545.6000 | -16.27% |

## 2. The two tickets

Target beta = k x beta = **0.9013**.  Lots = capital x target beta / (price x multiplier);
`round` is the closest whole lot, `floor` is the one that does not overshoot the hedge.

| capital | arm | needed @2026-11-11 | round | needed @2026-11-20 | round | Δ round | verdict |
|---|---|---|---|---|---|---|---|
| 1,000,000 | etf | 3323.493 | 3323 | 3918.832 | 3919 | +596 | MOVED |
| 1,000,000 | im | 0.680 | 1 | 0.813 | 1 | +0 | same |
| 3,000,000 | etf | 9970.479 | 9970 | 11756.495 | 11756 | +1786 | MOVED |
| 3,000,000 | im | 2.041 | 2 | 2.438 | 2 | +0 | same |
| 10,000,000 | etf | 33234.929 | 33235 | 39188.317 | 39188 | +5953 | MOVED |
| 10,000,000 | im | 6.805 | 7 | 8.127 | 8 | +1 | MOVED |
| 20,000,000 | etf | 66469.858 | 66470 | 78376.633 | 78377 | +11907 | MOVED |
| 20,000,000 | im | 13.609 | 14 | 16.253 | 16 | +2 | MOVED |

## 3. How far the price has to move before the order changes

Solved exactly from the book-date lot count: the nearest-integer boundary is at
`lots/(1+f) = n ± 0.5`.  This is the ruler that decides whether the dating defect
can ever reach an order, or only the caption.

| capital | arm | lots @book date | order flips to | when price moves |
|---|---|---|---|---|
| 1,000,000 | etf | 3323.493 | 3324 | -0.00% (price falls) |
| 1,000,000 | im | 0.680 | 0 | 36.09% (price rises) |
| 3,000,000 | etf | 9970.479 | 9971 | -0.00% (price falls) |
| 3,000,000 | im | 2.041 | 3 | -18.35% (price falls) |
| 10,000,000 | etf | 33234.929 | 33234 | 0.00% (price rises) |
| 10,000,000 | im | 6.805 | 6 | 4.69% (price rises) |
| 20,000,000 | etf | 66469.858 | 66469 | 0.00% (price rises) |
| 20,000,000 | im | 13.609 | 13 | 0.81% (price rises) |

Read the two arms differently.  The ETF arm sits at thousands of lots, so the
nearest lot changes on a fraction of a basis point — its flip distance prints as
~0% and means *the ETF can always be sized to the beta you asked for*; dating never
decides that arm.  The futures arm sits at a fractional contract, so a 36% move in
the contract is what changes whether one lot is the closest whole hedge — and that
is a distance the market can cover in the seven bars the book went unmarked.

## 4. What this changes, and what it does not

- The 1,000,000 rung's ETF ticket is **3323.49 lots** on the book date and **3918.83 lots** on the price date — a difference of **+596 lots**.
- The futures arm needs a **36.09%** move in the contract before one lot stops being the closest whole contract at this capital.
- What the face does **not** say: what the book itself did on the unmarked days.
  There is no mark, so no number is printed; the seven bars of 2026-11-11 and 2026-11-20 are printed instead, and they are not the book.

## 5. What was not measured

- Margin ratios, 券源 and recall stay broker terms (r2027's axes are quoted, not re-derived).
- The book is not revalued here: that needs its per-name marks, which is a different
  face's job.  This face only says how much the missing revaluation can matter.
- No cost, basis or roll model is introduced.

## Reproduction

```
python scripts/astock_veto_hedge_dating.py selftest
python scripts/astock_veto_hedge_dating.py run
python scripts/astock_veto_hedge_dating.py check
```
