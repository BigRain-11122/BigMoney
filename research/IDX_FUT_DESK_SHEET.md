# the carry sleeve as a morning sheet

evidence cutoff: **2026-11-13** | source judgement: `results/idx_fut_carry_risk.json`

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

Capital **1000000 CNY**. Four counts, because "how many lots" has four different answers depending on what the capital is supposed to survive: margin only, the product's own published max drawdown, the index's worst on record paid in cash, and the largest book that is never called at that worst.

| product | margin only | after own max drawdown | after index worst drawdown | survives worst drawdown without a call |
|---|---|---|---|---|
| IC | 6 lots | 4 lots | 0 lots | 1 lots |
| IF | 7 lots | 4 lots | 0 lots | 1 lots |
| IM | 6 lots | 4 lots | 0 lots | 1 lots |
| IH | 10 lots | 6 lots | 1 lots | 1 lots |

The **own max drawdown** column funds the hole this window
produced (a few percent, on a four-year futures series); the **index worst**
column funds the index's own worst historical drawdown (the per-product number
is printed in the call table below). They are not two estimates of one thing:
the first is a fact about the sample, the second is the size of the hole this
position can be asked to fund. The last column is never larger than the third
because a call arrives at the maintenance level, not at the initial one -- and
that difference is the only room this trade is actually given.

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

