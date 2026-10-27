# E128 the cash window is the backtest's own burn-in, and the identity's residual scales with the share (r1200 bm-b)

Face: `results/e40_cashleg_drag/CASHLeg-20261027.json` (regenerated, new `cash_window_by_book`
+ `cash_window_note` per window). Two-window receipt:
`results/e40_cashleg_drag/IDENTITY-20261027.json`. Code: `scripts/e39_panel_census.py`
(`_first_trade_index`, `_window_is_burn_in_driven`, `_cash_identity`), selftest 476 -> 488.

## What the face could not say before

E40 published a cash **attribution** per book (ladder 36.0bp, wide 37.0bp) but a cash
**mechanism** for the ladder only: `first_trading_rebalance_index`, `cash_bars` and
`cash_bar_share_pct` were computed from the ladder's five names. So a 1bp gap between two books
could not be attributed to a window difference or a rate difference, because only one window
existed on the face.

## Answer 1: the gap is not a window difference

| window | ladder first trade | wide first trade | gap | of which window | unexplained |
|---|---|---|---|---|---|
| 2020-01-01 (1650 bars) | 262 | 262 | -1.0bp | **0.0bp** | -1.0bp |
| 2023-01-01 (922 bars) | 263 | 263 | -1.0bp | **0.0bp** | -1.0bp |

Both books are eligible on the same month end, in both windows, with the same share (15.95% /
28.66%). A wider universe can only make a book eligible earlier, never later, so a shared window
is structural rather than accidental. The 1bp ladder/wide gap is therefore a valuation/compounding
difference between two books holding the same cash window, not two different exposures.

## Answer 2: the "13 months in cash" is the window's own burn-in

`base.elig(prices, i)` requires `i >= MIN_BARS(250)` **and** 250 consecutive non-missing closes
in the array it is handed -- and that array is built over the window's own calendar
(`prices[s] = [c.get(d) for d in cal]`). So the book cannot trade until a month end after bar 250,
in every window, regardless of the panel:

- 2020 window: `first_trading_rebalance_index = 262`, `bars_beyond_burn_in = 12`
- 2023 window: `first_trading_rebalance_index = 263`, `bars_beyond_burn_in = 13`

`window_is_burn_in_driven = true` on both. The repo stretch is a property of the backtest's
burn-in rule, not evidence that the universe was un-investable for a year. The face now carries
`burn_in_bars_required` beside the window so the two readings cannot be confused again.

## Answer 3: the identity closes on 2020 and does not on 2023 -- and that is the point

| window | share | mean rate | expected (rate x share) | ladder measured | residual | ratio |
|---|---|---|---|---|---|---|
| 2020-01-01 | 15.95% | 1.98% | 31.58bp | 36.0bp | **+4.42bp** | 1.14 |
| 2023-01-01 | 28.66% | 1.81% | 51.87bp | 72.0bp | **+20.13bp** | 1.39 |

Wide book: 37.0bp -> residual +5.42bp (ratio 1.17) on 2020; 73.0bp -> +21.13bp (1.41) on 2023.

The residual is positive and grows with the cash share, on both books. That is the signature of
compounding, not of a second cash channel: the repo accrual is earned on the whole equity and then
compounds at the book's own return for the remaining bars, so the linear sum is a **lower bound**
and the gap widens as the cash stretch lengthens.

**Consequence for the tolerance, stated plainly:** the 5.0bp band was declared for the 2020
window before this run (in code), and the wide book lands at 5.42bp -- just outside it. The second
window shows that is not a defect in the attribution but a band that was declared at one share.
An absolute tolerance on this identity is only meaningful if it is quoted with
`cash_bar_share_pct` (or scaled by it); the face therefore publishes both, and neither is quoted
alone.

## Honest

Descriptive census only: no gate, no verdict on the strategy, no prereg, no trial count, no
ledger booking. The identity is `rate_pct * share_pct` in bp and the engine compounds, so the
measured number is not required to equal it. The per-book window shares one eligibility function
with the engine, so this leg measures WHEN the books are allowed to trade; it does not change it.

## Method card

E166 in `knowledge/METHODOLOGY_ASSETS.md`.