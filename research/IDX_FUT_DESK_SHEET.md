# the carry sleeve as a morning sheet

evidence cutoff: **2026-11-16** | source judgement: `results/idx_fut_carry_risk.json`

The judgement face says whether the sleeve is worth holding. It does not say
which contract, how many lots, or when it rolls. This sheet answers only that.

## what tomorrow's fill would be

| product | judgement | contract | close | OI share | notional/lot | margin/lot |
|---|---|---|---|---|---|---|
| IC | SLEEVE_CANDIDATE | IC2612 | 6375.0 | 81.29% | 1275000 | 153000 |
| IF | REFUSE | IF2612 | 3956.6 | 80.71% | 1186980 | 142438 |
| IM | SLEEVE_CANDIDATE | IM2612 | 6276.8 | 78.39% | 1255360 | 150643 |
| IH | REFUSE | IH2612 | 2733.4 | 80.08% | 820020 | 98402 |

Margin is the exchange minimum at 12%; a broker adds its own, which this host cannot measure. Notional and margin are per lot = price x multiplier (IF/IH 300, IC/IM 200).

## what a stated capital buys

Capital **1000000 CNY**. Five counts, because "how many lots" has five different answers depending on what the capital is supposed to survive: paid for in full, margin only, the product's own published max drawdown, the index's worst on record paid in cash, and the largest book that is never called at that worst.

| product | cash, no borrowing | margin only | after own max drawdown | after index worst drawdown | survives worst drawdown without a call |
|---|---|---|---|---|---|
| IC | 0 lots | 6 lots | 4 lots | 0 lots | 1 lots |
| IF | 0 lots | 7 lots | 4 lots | 0 lots | 1 lots |
| IM | 0 lots | 6 lots | 4 lots | 0 lots | 1 lots |
| IH | 1 lots | 10 lots | 6 lots | 1 lots | 1 lots |

The **own max drawdown** column funds the hole this window
produced (a few percent, on a four-year futures series); the **index worst**
column funds the index's own worst historical drawdown (the per-product number
is printed in the call table below). They are not two estimates of one thing:
the first is a fact about the sample, the second is the size of the hole this
position can be asked to fund. The last column is never larger than the third
because a call arrives at the maintenance level, not at the initial one -- and
that difference is the only room this trade is actually given.

**IC, IF, IM** cannot be paid for in full even once at this account size (one lot's notional is larger than the stated capital), so every count in the last three columns is a margin position: the account borrows, and the borrowed part is exactly what a fall calls first.

## what the sleeve earns on the capital it needs behind it

Carry is measured on notional. Nobody holds a future on notional alone -- the
money that has to sit there is the maintenance level plus the fall it must
fund -- so the same carry buys a different return on the capital actually
committed, and the answer depends on which fall you prepare for.

| product | carry on notional | capital/lot for sample DD | return on it | capital/lot for index worst | return on it |
|---|---|---|---|---|---|
| IC | 8.76% | 168145 | 66.45% | 951451 | 11.74% |
| IF | 3.57% | 166475 | 25.43% | 884534 | 4.79% |
| IM | 10.20% | 158718 | 80.66% | 936010 | 13.68% |
| IH | 2.39% | 121617 | 16.13% | 611846 | 3.21% |

The sample column prepares for the hole this window produced (5.64% for IC); the index column prepares for the index's own worst (72.42%).
 A return computed on the smaller capital is not a better trade, it is the same
 trade with less money held against the day the larger number happens.

Read against the adopted book on the same source face (n=1662 bars, 10.33% vol, Sharpe 1.111, max drawdown -10.56%):

- the book compounds **11.56%/yr** and its worst drawdown is **-10.56%**;
- **IC** pays **11.74%/yr** on the capital that funds its index worst (951451), and that capital is the size of a 72.42% fall.
- **IF** pays **4.79%/yr** on the capital that funds its index worst (884534), and that capital is the size of a 72.30% fall.
- **IM** pays **13.68%/yr** on the capital that funds its index worst (936010), and that capital is the size of a 72.35% fall.
- **IH** pays **3.21%/yr** on the capital that funds its index worst (611846), and that capital is the size of a 72.41% fall.

A sleeve that pays the book's rate while requiring its holder to fund a
72.42% fall is not the same instrument at the same price; that comparison is the one this sheet refuses to make for the reader.

So the money question has one answer on this face: the best sleeve is
**IM** at 13.68%/yr against the book's 11.56%/yr (+2.12pp), and the 2.12pp is paid for by holding capital sized for a 72.35% fall rather than the book's 10.56% worst. A reader who wants the book's risk shape should not substitute this; a reader who will fund a 72.42% hole for +2.12pp is being quoted the whole price here, not a partial one.

## how far the index must fall before someone calls

| product | index worst DD on record | fall that calls the own-DD count | with +2pp maintenance | fall that calls the surviving count |
|---|---|---|---|---|
| IC | 72.42% | 4 lots → 12.6% | 10.7% | 1 lots → 76.6% |
| IF | 72.30% | 4 lots → 14.2% | 12.3% | 1 lots → 82.9% |
| IM | 72.35% | 4 lots → 12.9% | 11.0% | 1 lots → 77.9% |
| IH | 72.41% | 6 lots → 13.4% | 11.5% | 1 lots → >100% |

The fall column is not a scenario, it is arithmetic:

```
equity(f)   = capital - V*f          (a future is unfunded, so no interest)
required(f) = m * (1 - f) * V         (maintenance is a share of the marked value)
called when equity(f) < required(f) => f > (capital - m*V) / ((1-m)*V)
```

with m = 8% maintenance (an assumption, printed with the rest) and V = lots x notional. Every extra lot adds V, which costs more equity than it adds maintenance, so the distance shrinks as the book grows -- that is the whole reason a count can look affordable and still be called inside a recorded year.

Counts this table would call **inside the record**, i.e. the own-drawdown
count is not a position a broker lets you keep:

- **IC** — 4 lots are called after a 12.6% fall; the index has fallen 72.4% before.
- **IF** — 4 lots are called after a 14.2% fall; the index has fallen 72.3% before.
- **IM** — 4 lots are called after a 12.9% fall; the index has fallen 72.3% before.
- **IH** — 6 lots are called after a 13.4% fall; the index has fallen 72.4% before.

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
| IC | 300000 | 0 | 0 | 0.0% | 1 | 111728 |
| IC | 1000000 | 0 | 0 | 0.0% | 6 | 670370 |
| IC | 3000000 | 2 | 223456 | 85.0% | 19 | 2122837 |
| IC | 10000000 | 7 | 782098 | 89.2% | 65 | 7262336 |
| IC | 50000000 | 39 | 4357402 | 99.5% | 326 | 36423410 |
| IF | 300000 | 0 | 0 | 0.0% | 2 | 84679 |
| IF | 1000000 | 0 | 0 | 0.0% | 7 | 296377 |
| IF | 3000000 | 2 | 84679 | 79.1% | 21 | 889131 |
| IF | 10000000 | 8 | 338717 | 95.0% | 70 | 2963770 |
| IF | 50000000 | 42 | 1778262 | 99.7% | 351 | 14861191 |
| IM | 300000 | 0 | 0 | 0.0% | 1 | 128022 |
| IM | 1000000 | 0 | 0 | 0.0% | 6 | 768130 |
| IM | 3000000 | 2 | 256043 | 83.7% | 19 | 2432411 |
| IM | 10000000 | 7 | 896151 | 87.9% | 66 | 8449426 |
| IM | 50000000 | 39 | 4992843 | 97.9% | 331 | 42375154 |
| IH | 300000 | 0 | 0 | 0.0% | 3 | 58845 |
| IH | 1000000 | 1 | 19615 | 82.0% | 10 | 196149 |
| IH | 3000000 | 3 | 58845 | 82.0% | 30 | 588446 |
| IH | 10000000 | 12 | 235379 | 98.4% | 101 | 1981103 |
| IH | 50000000 | 60 | 1176893 | 98.4% | 508 | 9964358 |

A zero in the cash column is not a small position: it means one lot costs
more than the whole account, and the margin column is what a leveraged
holder would be looking at -- the row that has a call distance attached.

## when it rolls, and what the published gap is

| product | last roll | td since | median interval | next roll ~td | gap after roll cost (floor / median) |
|---|---|---|---|---|---|
| IC | 2026-09-14 (IC2609→IC2612) | 38 | 20.5 td (n=62) | -18 | +9.16 / +6.86 pp |
| IF | 2026-09-11 (IF2609→IF2612) | 39 | 19.0 td (n=73) | -20 | +2.35 / +0.65 pp |
| IM | 2026-09-14 (IM2609→IM2612) | 38 | 59.0 td (n=22) | +21 | +9.51 / +8.07 pp |
| IH | 2026-09-14 (IH2609→IH2612) | 38 | 17.0 td (n=88) | -21 | ? / ? pp |

The next-roll column is an estimate off this book's own switch history, not a
calendar rule: the calendar rule was measured to catch half of the rolls while
also eating market days near expiry. A negative number means the central
interval has already elapsed -- read it against who is actually holding the book:

- **IC** is 18 td past its median interval, and the incumbent still holds 81.29% of the product's open interest (median over 62 switches, IQR [11.0, 58.0] td): the series is irregular, so this is not a deadline.
- **IF** is 20 td past its median interval, and the incumbent still holds 80.71% of the product's open interest (median over 73 switches, IQR [9.0, 42.0] td): the series is irregular, so this is not a deadline.
- **IH** is 21 td past its median interval, and the incumbent still holds 80.08% of the product's open interest (median over 88 switches, IQR [5.0, 26.0] td): the series is irregular, so this is not a deadline.

A missing gap is refused, not zero:

- **IH** — no ETF is mapped to this index, so there is no other leg to price

Known defects in the ETF leg behind each gap -- the gap still prints, but
this is what the source face had to repair to get there:

- **IC** — 1 share conversion(s) removed at the open (2015-04-15 x3.486); the level change is not a return
- **IM** — 1 share conversion(s) removed at the open (2022-09-05 x2.763); the level change is not a return

## the sentence this sheet is not allowed to say

Nothing here is adopted. Candidates: **IC, IM**. The readings behind them are in-sample, the margin is an assumption, and the roll cost is a band whose two ends are printed side by side because the estimator has no resolution below a few dozen ticks.

The call distance is arithmetic on those assumptions, not a record: this host has no broker statement, no CFFEX margin file and no margin-call history to fit, so it says what the stated rules imply, not what a broker did to anybody.

What the source face says, copied verbatim so it cannot drift here:

- **IC** — carry 12.04% at target risk, corr -0.039, blend Sharpe +0.325
- **IM** — carry 12.02% at target risk, corr -0.064, blend Sharpe +0.387

