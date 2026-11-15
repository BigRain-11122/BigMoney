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

Capital **1000000 CNY**. Two counts: the naive one (margin only) and the one that can also fund the product's own published max drawdown, which is the only count that survives a bad year.

| product | margin only | after own max drawdown | drawdown buffer/lot |
|---|---|---|---|
| IC | 6 lots | 4 lots | 71897 |
| IF | 7 lots | 4 lots | 77735 |
| IM | 6 lots | 4 lots | 63358 |
| IH | 10 lots | 6 lots | 60886 |

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

What the source face says, copied verbatim so it cannot drift here:

- **IC** — carry 12.04% at target risk, corr -0.039, blend Sharpe +0.325
- **IM** — carry 12.02% at target risk, corr -0.064, blend Sharpe +0.387

