# the carry sleeve as a morning sheet

evidence cutoff: **2026-11-16** | source judgement: `results/idx_fut_carry_risk.json`

The judgement face says whether the sleeve is worth holding. It does not say
which contract, how many lots, or when it rolls. This sheet answers only that.

## what tomorrow's fill would be

| product | judgement | contract | close | OI share | notional/lot | margin/lot |
|---|---|---|---|---|---|---|
| IC | SLEEVE_CANDIDATE | IC2612 | 6218.4 | 82.41% | 1243680 | 149242 |
| IF | REFUSE | IF2612 | 3939.0 | 81.53% | 1181700 | 141804 |
| IM | SLEEVE_CANDIDATE | IM2612 | 6105.0 | 80.50% | 1221000 | 146520 |
| IH | REFUSE | IH2612 | 2742.4 | 81.69% | 822720 | 98726 |

Margin is the exchange minimum at 12%; a broker adds its own, which this host cannot measure. Notional and margin are per lot = price x multiplier (IF/IH 300, IC/IM 200).

## what a stated capital buys

Capital **1000000 CNY**. Five counts, because "how many lots" has five different answers depending on what the capital is supposed to survive: paid for in full, margin only, the product's own published max drawdown, the index's worst on record paid in cash, and the largest book that is never called at that worst.

| product | cash, no borrowing | margin only | after own max drawdown | after index worst drawdown | survives worst drawdown without a call |
|---|---|---|---|---|---|
| IC | 0 lots | 6 lots | 4 lots | 0 lots | 1 lots |
| IF | 0 lots | 7 lots | 4 lots | 1 lots | 1 lots |
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
| IC | 8.76% | 164015 | 66.45% | 928079 | 11.74% |
| IF | 3.57% | 165734 | 25.43% | 880599 | 4.79% |
| IM | 10.20% | 154374 | 80.66% | 910391 | 13.68% |
| IH | 2.39% | 122018 | 16.13% | 613860 | 3.21% |

The sample column prepares for the hole this window produced (5.64% for IC); the index column prepares for the index's own worst (72.42%).
 A return computed on the smaller capital is not a better trade, it is the same
 trade with less money held against the day the larger number happens.

Read against the adopted book on the same source face (n=1662 bars, 10.33% vol, Sharpe 1.111, max drawdown -10.56%):

- the book compounds **11.56%/yr** and its worst drawdown is **-10.56%**;
- **IC** pays **11.74%/yr** on the capital that funds its index worst (928079), and that capital is the size of a 72.42% fall.
- **IF** pays **4.79%/yr** on the capital that funds its index worst (880599), and that capital is the size of a 72.30% fall.
- **IM** pays **13.68%/yr** on the capital that funds its index worst (910391), and that capital is the size of a 72.35% fall.
- **IH** pays **3.21%/yr** on the capital that funds its index worst (613860), and that capital is the size of a 72.41% fall.

A sleeve that pays the book's rate while requiring its holder to fund a
72.42% fall is not the same instrument at the same price; that comparison is the one this sheet refuses to make for the reader.

So the money question has one answer on this face: the best sleeve is
**IM** at 13.68%/yr against the book's 11.56%/yr (+2.12pp), and the 2.12pp is paid for by holding capital sized for a 72.35% fall rather than the book's 10.56% worst. A reader who wants the book's risk shape should not substitute this; a reader who will fund a 72.42% hole for +2.12pp is being quoted the whole price here, not a partial one.

## how far the index must fall before someone calls

| product | index worst DD on record | fall that calls the own-DD count | with +2pp maintenance | fall that calls the surviving count |
|---|---|---|---|---|
| IC | 72.42% | 4 lots → 13.2% | 11.2% | 1 lots → 78.7% |
| IF | 72.30% | 4 lots → 14.3% | 12.4% | 1 lots → 83.3% |
| IM | 72.35% | 4 lots → 13.6% | 11.6% | 1 lots → 80.3% |
| IH | 72.41% | 6 lots → 13.3% | 11.4% | 1 lots → >100% |

The fall column is not a scenario, it is arithmetic:

```
equity(f)   = capital - V*f          (a future is unfunded, so no interest)
required(f) = m * (1 - f) * V         (maintenance is a share of the marked value)
called when equity(f) < required(f) => f > (capital - m*V) / ((1-m)*V)
```

with m = 8% maintenance (an assumption, printed with the rest) and V = lots x notional. Every extra lot adds V, which costs more equity than it adds maintenance, so the distance shrinks as the book grows -- that is the whole reason a count can look affordable and still be called inside a recorded year.

Counts this table would call **inside the record**, i.e. the own-drawdown
count is not a position a broker lets you keep:

- **IC** — 4 lots are called after a 13.2% fall; the index has fallen 72.4% before.
- **IF** — 4 lots are called after a 14.3% fall; the index has fallen 72.3% before.
- **IM** — 4 lots are called after a 13.6% fall; the index has fallen 72.3% before.
- **IH** — 6 lots are called after a 13.3% fall; the index has fallen 72.4% before.

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
| IC | 300000 | 0 | 0 | 0.0% | 2 | 217967 |
| IC | 1000000 | 0 | 0 | 0.0% | 6 | 653902 |
| IC | 3000000 | 2 | 217967 | 82.9% | 20 | 2179674 |
| IC | 10000000 | 8 | 871869 | 99.5% | 67 | 7301906 |
| IC | 50000000 | 40 | 4359347 | 99.5% | 335 | 36509532 |
| IF | 300000 | 0 | 0 | 0.0% | 2 | 84302 |
| IF | 1000000 | 0 | 0 | 0.0% | 7 | 295059 |
| IF | 3000000 | 2 | 84302 | 78.8% | 21 | 885176 |
| IF | 10000000 | 8 | 337210 | 94.5% | 70 | 2950587 |
| IF | 50000000 | 42 | 1770352 | 99.3% | 352 | 14837236 |
| IM | 300000 | 0 | 0 | 0.0% | 2 | 249035 |
| IM | 1000000 | 0 | 0 | 0.0% | 6 | 747105 |
| IM | 3000000 | 2 | 249035 | 81.4% | 20 | 2490352 |
| IM | 10000000 | 8 | 996141 | 97.7% | 68 | 8467195 |
| IM | 50000000 | 40 | 4980703 | 97.7% | 341 | 42460495 |
| IH | 300000 | 0 | 0 | 0.0% | 3 | 59038 |
| IH | 1000000 | 1 | 19679 | 82.3% | 10 | 196795 |
| IH | 3000000 | 3 | 59038 | 82.3% | 30 | 590384 |
| IH | 10000000 | 12 | 236154 | 98.7% | 101 | 1987626 |
| IH | 50000000 | 60 | 1180768 | 98.7% | 506 | 9957808 |

A zero in the cash column is not a small position: it means one lot costs
more than the whole account, and the margin column is what a leveraged
holder would be looking at -- the row that has a call distance attached.

## when it rolls, and what the published gap is

| product | last roll | td since | median interval | next roll ~td | gap after roll cost (floor / median) |
|---|---|---|---|---|---|
| IC | 2026-09-14 (IC2609→IC2612) | 39 | 20.5 td (n=62) | -18 | +9.16 / +6.86 pp |
| IF | 2026-09-11 (IF2609→IF2612) | 40 | 19.0 td (n=73) | -21 | +2.35 / +0.65 pp |
| IM | 2026-09-14 (IM2609→IM2612) | 39 | 59.0 td (n=22) | +20 | +9.51 / +8.07 pp |
| IH | 2026-09-14 (IH2609→IH2612) | 39 | 17.0 td (n=88) | -22 | ? / ? pp |

The next-roll column is an estimate off this book's own switch history, not a
calendar rule: the calendar rule was measured to catch half of the rolls while
also eating market days near expiry. A negative number means the central
interval has already elapsed -- read it against who is actually holding the book:

- **IC** is 18 td past its median interval, and the incumbent still holds 82.41% of the product's open interest (median over 62 switches, IQR [11.0, 58.0] td): the series is irregular, so this is not a deadline.
- **IF** is 21 td past its median interval, and the incumbent still holds 81.53% of the product's open interest (median over 73 switches, IQR [9.0, 42.0] td): the series is irregular, so this is not a deadline.
- **IH** is 22 td past its median interval, and the incumbent still holds 81.69% of the product's open interest (median over 88 switches, IQR [5.0, 26.0] td): the series is irregular, so this is not a deadline.

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

