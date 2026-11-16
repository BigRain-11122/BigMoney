# the carry sleeve as a morning sheet

evidence cutoff: **2026-11-16** | source judgement: `results/idx_fut_carry_risk.json`

The judgement face says whether the sleeve is worth holding. It does not say
which contract, how many lots, or when it rolls. This sheet answers only that.

## what tomorrow's fill would be

| product | judgement | contract | close | OI share | notional/lot | margin/lot |
|---|---|---|---|---|---|---|
| IC | no_contract_book | - | - | - | - | - |
| IF | no_contract_book | - | - | - | - | - |
| IM | no_contract_book | - | - | - | - | - |
| IH | no_contract_book | - | - | - | - | - |

Margin is the exchange minimum at 12%; a broker adds its own, which this host cannot measure. Notional and margin are per lot = price x multiplier (IF/IH 300, IC/IM 200).

## what a stated capital buys

Capital **1000000 CNY**. Five counts, because "how many lots" has five different answers depending on what the capital is supposed to survive: paid for in full, margin only, the product's own published max drawdown, the index's worst on record paid in cash, and the largest book that is never called at that worst.

| product | cash, no borrowing | margin only | after own max drawdown | after index worst drawdown | survives worst drawdown without a call |
|---|---|---|---|---|---|

The **own max drawdown** column funds the hole this window
produced (a few percent, on a four-year futures series); the **index worst**
column funds the index's own worst historical drawdown (the per-product number
is printed in the call table below). They are not two estimates of one thing:
the first is a fact about the sample, the second is the size of the hole this
position can be asked to fund. The last column is never larger than the third
because a call arrives at the maintenance level, not at the initial one -- and
that difference is the only room this trade is actually given.

## what the sleeve earns on the capital it needs behind it

Carry is measured on notional. Nobody holds a future on notional alone -- the
money that has to sit there is the maintenance level plus the fall it must
fund -- so the same carry buys a different return on the capital actually
committed, and the answer depends on which fall you prepare for.

| product | carry on notional | capital/lot for sample DD | return on it | capital/lot for index worst | return on it |
|---|---|---|---|---|---|

The sample column prepares for the hole this window produced (?% for IC); the index column prepares for the index's own worst (?%).
 A return computed on the smaller capital is not a better trade, it is the same
 trade with less money held against the day the larger number happens.

Read against the adopted book on the same source face (n=1662 bars, 10.33% vol, Sharpe 1.111, max drawdown -10.56%):

- the book compounds **11.56%/yr** and its worst drawdown is **-10.56%**;

A sleeve that pays the book's rate while requiring its holder to fund a
0.00% fall is not the same instrument at the same price; that comparison is the one this sheet refuses to make for the reader.

## how far the index must fall before someone calls

| product | index worst DD on record | fall that calls the own-DD count | with +2pp maintenance | fall that calls the surviving count |
|---|---|---|---|---|

The fall column is not a scenario, it is arithmetic:

```
equity(f)   = capital - V*f          (a future is unfunded, so no interest)
required(f) = m * (1 - f) * V         (maintenance is a share of the marked value)
called when equity(f) < required(f) => f > (capital - m*V) / ((1-m)*V)
```

with m = 8% maintenance (an assumption, printed with the rest) and V = lots x notional. Every extra lot adds V, which costs more equity than it adds maintenance, so the distance shrinks as the book grows -- that is the whole reason a count can look affordable and still be called inside a recorded year.

Two things this table does not model, both of which can only make the distance
shorter: the broker's surcharge (printed as the +2pp column, not as a guess at one number) and the fact that CFFEX may raise the maintenance level mid-crisis, which is exactly when the distance is being used.

## a ladder: what each account size holds, and what it earns

Two counts per account because they answer two different questions: the
cash column is a position that cannot be called, the margin column is the
one the exchange minimum buys and the rest of the capital absorbs the fall.
Returns are carry on notional at the published rate; idle cash earns nothing
here, and the repo rate on that cash is another host's panel.

| product | capital | cash lots | cash earns /yr | cash occupancy | margin lots | margin earns /yr |
|---|---|---|---|---|---|---|
| IC | - | no_contract_book | - | - | - | - |
| IF | - | no_contract_book | - | - | - | - |
| IM | - | no_contract_book | - | - | - | - |
| IH | - | no_contract_book | - | - | - | - |

A zero in the cash column is not a small position: it means one lot costs
more than the whole account, and the margin column is what a leveraged
holder would be looking at -- the row that has a call distance attached.

## when it rolls, and what the published gap is

| product | last roll | td since | median interval | next roll ~td | gap after roll cost (floor / median) |
|---|---|---|---|---|---|

The next-roll column is an estimate off this book's own switch history, not a
calendar rule: the calendar rule was measured to catch half of the rolls while
also eating market days near expiry. A negative number means the central
interval has already elapsed -- read it against who is actually holding the book:


## the sentence this sheet is not allowed to say

Nothing here is adopted. Candidates: **none**. The readings behind them are in-sample, the margin is an assumption, and the roll cost is a band whose two ends are printed side by side because the estimator has no resolution below a few dozen ticks.

The call distance is arithmetic on those assumptions, not a record: this host has no broker statement, no CFFEX margin file and no margin-call history to fit, so it says what the stated rules imply, not what a broker did to anybody.

