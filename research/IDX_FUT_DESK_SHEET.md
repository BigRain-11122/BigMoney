# the carry sleeve as a morning sheet

evidence cutoff: **2026-11-25** | source judgement: `results/idx_fut_carry_risk.json`

The judgement face says whether the sleeve is worth holding. It does not say
which contract, how many lots, or when it rolls. This sheet answers only that.

## what tomorrow's fill would be

| product | judgement | contract | close | OI share | notional/lot | margin/lot |
|---|---|---|---|---|---|---|
| IC | SLEEVE_CANDIDATE | IC2612 | 5769.0 | 100.00% | 1153800 | 138456 |
| IF | REFUSE | IF2612 | 3824.0 | 100.00% | 1147200 | 137664 |
| IM | SLEEVE_CANDIDATE | IM2612 | 5434.4 | 100.00% | 1086880 | 130426 |
| IH | REFUSE | IH2612 | 2708.6 | 100.00% | 812580 | 97510 |

Margin is the exchange minimum at 12%; a broker adds its own, which this host cannot measure. Notional and margin are per lot = price x multiplier (IF/IH 300, IC/IM 200).

## what a stated capital buys

Capital **1000000 CNY**. Five counts, because "how many lots" has five different answers depending on what the capital is supposed to survive: paid for in full, margin only, the product's own published max drawdown, the index's worst on record paid in cash, and the largest book that is never called at that worst.

| product | cash, no borrowing | margin only | after own max drawdown | after index worst drawdown | survives worst drawdown without a call |
|---|---|---|---|---|---|
| IC | 0 lots | 7 lots | 4 lots | 1 lots | 1 lots |
| IF | 0 lots | 7 lots | 4 lots | 1 lots | 1 lots |
| IM | 0 lots | 7 lots | 5 lots | 1 lots | 1 lots |
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
| IC | 8.64% | 152162 | 65.53% | 861008 | 11.58% |
| IF | 3.50% | 160896 | 24.95% | 854890 | 4.70% |
| IM | 9.96% | 137417 | 78.82% | 810389 | 13.36% |
| IH | 2.37% | 120514 | 15.99% | 606295 | 3.18% |

The sample column prepares for the hole this window produced (5.64% for IC); the index column prepares for the index's own worst (72.42%).
 A return computed on the smaller capital is not a better trade, it is the same
 trade with less money held against the day the larger number happens.

Read against the adopted book on the same source face (n=1669 bars, 10.35% vol, Sharpe 1.065, max drawdown -10.56%):

- the book compounds **11.05%/yr** and its worst drawdown is **-10.56%**;
- **IC** pays **11.58%/yr** on the capital that funds its index worst (861008), and that capital is the size of a 72.42% fall.
- **IF** pays **4.70%/yr** on the capital that funds its index worst (854890), and that capital is the size of a 72.30% fall.
- **IM** pays **13.36%/yr** on the capital that funds its index worst (810389), and that capital is the size of a 72.35% fall.
- **IH** pays **3.18%/yr** on the capital that funds its index worst (606295), and that capital is the size of a 72.41% fall.

A sleeve that pays the book's rate while requiring its holder to fund a
72.42% fall is not the same instrument at the same price; that comparison is the one this sheet refuses to make for the reader.

So the money question has one answer on this face: the best sleeve is
**IM** at 13.36%/yr against the book's 11.05%/yr (+2.31pp), and the 2.31pp is paid for by holding capital sized for a 72.35% fall rather than the book's 10.56% worst. A reader who wants the book's risk shape should not substitute this; a reader who will fund a 72.42% hole for +2.31pp is being quoted the whole price here, not a partial one.

## how far the index must fall before someone calls

| product | index worst DD on record | fall that calls the own-DD count | with +2pp maintenance | fall that calls the surviving count |
|---|---|---|---|---|
| IC | 72.42% | 4 lots → 14.9% | 13.0% | 1 lots → 85.5% |
| IF | 72.30% | 4 lots → 15.0% | 13.1% | 1 lots → 86.0% |
| IM | 72.35% | 5 lots → 11.3% | 9.3% | 1 lots → 91.3% |
| IH | 72.41% | 6 lots → 13.6% | 11.7% | 1 lots → >100% |

The fall column is not a scenario, it is arithmetic:

```
equity(f)   = capital - V*f          (a future is unfunded, so no interest)
required(f) = m * (1 - f) * V         (maintenance is a share of the marked value)
called when equity(f) < required(f) => f > (capital - m*V) / ((1-m)*V)
```

with m = 8% maintenance (an assumption, printed with the rest) and V = lots x notional. Every extra lot adds V, which costs more equity than it adds maintenance, so the distance shrinks as the book grows -- that is the whole reason a count can look affordable and still be called inside a recorded year.

Counts this table would call **inside the record**, i.e. the own-drawdown
count is not a position a broker lets you keep:

- **IC** — 4 lots are called after a 14.9% fall; the index has fallen 72.4% before.
- **IF** — 4 lots are called after a 15.0% fall; the index has fallen 72.3% before.
- **IM** — 5 lots are called after a 11.3% fall; the index has fallen 72.3% before.
- **IH** — 6 lots are called after a 13.6% fall; the index has fallen 72.4% before.

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
| IC | 300000 | 0 | 0 | 0.0% | 2 | 199423 |
| IC | 1000000 | 0 | 0 | 0.0% | 7 | 697980 |
| IC | 3000000 | 2 | 199423 | 76.9% | 21 | 2093939 |
| IC | 10000000 | 8 | 797691 | 92.3% | 72 | 7179221 |
| IC | 50000000 | 43 | 4287590 | 99.2% | 361 | 35995814 |
| IF | 300000 | 0 | 0 | 0.0% | 2 | 80281 |
| IF | 1000000 | 0 | 0 | 0.0% | 7 | 280984 |
| IF | 3000000 | 2 | 80281 | 76.5% | 21 | 842951 |
| IF | 10000000 | 8 | 321124 | 91.8% | 72 | 2890118 |
| IF | 50000000 | 43 | 1726043 | 98.7% | 363 | 14571012 |
| IM | 300000 | 0 | 0 | 0.0% | 2 | 216615 |
| IM | 1000000 | 0 | 0 | 0.0% | 7 | 758153 |
| IM | 3000000 | 2 | 216615 | 72.5% | 23 | 2491075 |
| IM | 10000000 | 9 | 974768 | 97.8% | 76 | 8231377 |
| IM | 50000000 | 46 | 4982149 | 100.0% | 383 | 41481808 |
| IH | 300000 | 0 | 0 | 0.0% | 3 | 57799 |
| IH | 1000000 | 1 | 19266 | 81.3% | 10 | 192663 |
| IH | 3000000 | 3 | 57799 | 81.3% | 30 | 577988 |
| IH | 10000000 | 12 | 231195 | 97.5% | 102 | 1965160 |
| IH | 50000000 | 61 | 1175243 | 99.1% | 512 | 9864331 |

A zero in the cash column is not a small position: it means one lot costs
more than the whole account, and the margin column is what a leveraged
holder would be looking at -- the row that has a call distance attached.

## when it rolls, and what the published gap is

| product | last roll | td since | median interval | next roll ~td | gap after roll cost (floor / median) |
|---|---|---|---|---|---|
| IC | 2026-09-14 (IC2609→IC2612) | 46 | 20.5 td (n=62) | -26 | +8.97 / +6.67 pp |
| IF | 2026-09-11 (IF2609→IF2612) | 47 | 19.0 td (n=73) | -28 | +2.32 / +0.63 pp |
| IM | 2026-09-14 (IM2609→IM2612) | 46 | 59.0 td (n=22) | +13 | +8.95 / +7.53 pp |
| IH | 2026-09-14 (IH2609→IH2612) | 46 | 17.0 td (n=88) | -29 | ? / ? pp |

The next-roll column is an estimate off this book's own switch history, not a
calendar rule: the calendar rule was measured to catch half of the rolls while
also eating market days near expiry. A negative number means the central
interval has already elapsed -- read it against who is actually holding the book:

- **IC** is 26 td past its median interval, and the incumbent still holds 100.00% of the product's open interest (median over 62 switches, IQR [11.0, 58.0] td): the series is irregular, so this is not a deadline.
- **IF** is 28 td past its median interval, and the incumbent still holds 100.00% of the product's open interest (median over 73 switches, IQR [9.0, 42.0] td): the series is irregular, so this is not a deadline.
- **IH** is 29 td past its median interval, and the incumbent still holds 100.00% of the product's open interest (median over 88 switches, IQR [5.0, 26.0] td): the series is irregular, so this is not a deadline.

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

- **IC** — carry 11.87% at target risk, corr -0.038, blend Sharpe +0.320
- **IM** — carry 11.73% at target risk, corr -0.063, blend Sharpe +0.379

