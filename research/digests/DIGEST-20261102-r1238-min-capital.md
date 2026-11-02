# DIGEST 2026-11-02 r1238 · the commission floor under the rate model

**Round:** 1238 (bm-a). **Card:** E355. **Face:** `scripts/etf_book_min_capital.py`.

## The gap this closes

Every cost number the ETF book has published is a **rate per side** — 8bp base plus a
square-root impact term — charged on traded notional. A rate has no floor. A real brokerage
charge does: most retail accounts pay a **5 CNY minimum per trade**. Nobody had checked
whether this book's trades are big enough for the minimum to be irrelevant, and the answer
is no: at `k ≈ 0.20` over twelve names, one rebalance trades 9.2% of NAV per name
(`dw_median = 0.09227` over 864 legs), so the floor crosses the 8bp assumption at
**67,737 CNY**.

The same arithmetic runs the other way, which is why one-sided reporting would have been
wrong: at 2.5bp (万2.5) the floor stops binding at **216,760 CNY**, and above that the
published 8bp is **5.5bp/side too expensive** — worth +0.67pp/yr to a 1M account.

## What was measured

One engine, one weight path (`etf_book_capacity_rule.weight_path`, the production k
schedule), one window (2020-01-01..2026-10-30), **only** the base rate replaced by
`max(prop, 1e4*min_fee/notional)`; the impact term is the published one, and capital is
held constant per rung so each delta is attributable to the fee schedule rather than to
account-size compounding.

| capital | 2.5bp+5 floor | no floor | vs same-NAV 8bp arm | legs at the floor |
|---|---|---|---|---|
| 10,000 | **2.02%** / Sharpe 0.28 | 8.38% / 1.01 | −5.66pp | 100% |
| 50,000 | 7.27% / 0.89 | 8.32% / 1.01 | −0.36pp | 100% |
| 200,000 | 8.09% / 0.98 | 8.23% / 1.00 | +0.56pp | 53% |
| 1,000,000 | 7.97% / 0.97 | 7.99% / 0.97 | +0.67pp | 39% |

The whole small-account damage is the floor, not the rate: a 10,000 CNY account pays
4,320 CNY of commission over 6.8 years (43% of its starting capital) with the floor, and
199 CNY without it. Verdict token (derived, never typed):
`FLOOR_BINDS_BELOW_67737_AND_MODEL_GENEROUS_ABOVE_216760`.

## Three reusable reads

1. **A proportional cost model has no floor; real fees do, and small accounts die on the
   fixed charge, not the rate.** "The rule makes 8.46%/yr" and "the minimum account that can
   reach 8.46%" are one sentence, not two — printed alone the first one gets used to size a
   position that cannot deliver it.
2. **The floor is two-sided.** Below the neutral point the model is optimistic; above it the
   model is pessimistic by exactly the (8bp − prop) × two-way-turnover gap. Reporting only
   the pessimistic side would have called an unsound assumption "conservative".
3. **Derive the neutral point in closed form from the face's own weights**
   (`1e4*min_fee/(bp*dw_median)`), never type it. `--check` recomputes both neutral points
   and the verdict token from the published rows, so a change to `k` or the name count
   cannot leave a stale "about 400k" behind.

## Scope

Fees only — the spread is already inside the 8bp reference arm and is not charged twice;
impact is the published term verbatim; capital is constant per rung (this is a fee-structure
cost, not a small-account net-worth path). ETF stamp duty is zero by construction; a stock
leg would need conveyance duty added and is out of scope.

## Estate disclosure (same round)

This window inherited an uncommitted estate from a dead window: `scripts/etf_book_forced_hold.py`
(card E354, chain leg, digest, CEO page section) plus `scripts/factor_ic_dedupe_audit.py`
(selftest 10/10). It was **machine-checked, not trusted**: forced_hold selftest 22/22 and a
fresh `run` (rc0, verdict `CENSORED_TAIL_IS_IMMATERIAL`, control census reproduces E353's
3,924/109/4.23%). The page's own selftest was **red (125/127)** for a reason worth keeping:
its L122 leg read the *published* forced-hold payload, which predated the `control` block, so
a green script was paired with a stale artifact and the page correctly refused to print
(`status=drifted`). Regenerating the payload healed both legs to 127/127 — the r1257/r1290
orphan-face class again, this time caught by a reader instead of a human.