# ETF book width — what the executable ticket's 5 names cost against the card's 12

Window: r1275 (2026-10-26). Artefact: `scripts/etf_book_width_audit.py` →
`results/etf_book_width_audit.json`. Panel cutoff 2026-10-23, next-open fills,
10bp effective per side on the book leg, |Δk|·8bp on the overlay leg, GC001 close
on the cash remainder, beta target 0.20, inception 2024-01-01.

## Why this exists

The production book has two live faces and they disagree on one number nobody had
priced:

| face | file | name count | leverage rule |
|---|---|---|---|
| executable ticket | `scripts/etf_book_order.py` | **5** (`F.N_HOLD`, the composite factor's default) | beta 0.20 overlay, k = target/beta ≤ 1 |
| production card / forward ledger | `scripts/etf_book_production.py`, `etf_book_forward.py` | **12** | 8% vol target, de-lever only |

Both are published as "the production book". An operator following the ticket buys 5
names; the card that reports 9.47%/0.98/-11.8% describes 12. Until now the only way to
know the difference was to notice the mismatch and run two separate scripts.

## Result — width is a risk dial, not a defect

Holding the ticket's accounting fixed and moving **only** the name count:

| names | CAGR | Sharpe | maxDD | avg cash | excess vs same-beta | turnover/yr |
|---|---|---|---|---|---|---|
| 5 | 11.05% | 1.353 | -6.01% | 55.0% | +8.06pp | 1.53 |
| 8 | 9.73% | 1.437 | -5.04% | 59.8% | +6.74pp | 1.43 |
| 12 | 9.53% | 1.560 | -4.17% | 61.9% | +6.54pp | 1.30 |
| 20 | 8.28% | 1.628 | -2.94% | 66.5% | +5.29pp | 1.14 |

12 names vs the executable 5: **−1.52pp/yr of CAGR for +0.207 Sharpe and 1.84pp less
max drawdown**, with lower turnover. Monotone across the four widths in both directions,
so it is a slope, not a lucky point.

Reading: the concentration premium is real and it is paid in drawdown, exactly the
trade r1262 found when it separated the batched sleeve's width effect from its phase
effect. Neither width is wrong; the ticket is simply the aggressive end of the same
book, which is what a 5-name basket at beta 0.20 is.

## What the audit does not claim

- Not a verdict, not advice, no ledger booking, no change to the production card.
- The panel is the existing one: universe = surviving ETFs (survivorship), names
  without a live bar on the decision day are priced by the engine's ffill.
- The overlay's cash share rises with width (55.0% → 66.5%) because beta 0.20 needs
  more de-levering on a calmer book — the excess column already carries that, the
  CAGR column does not decompose it.
- 2024+ only (the ticket's inception). The 2020-2023 window where the book was mostly
  defensive is not in these numbers.

## Where it lands (r1275)

The measurement is only worth its wall time if the operator meets it where the decision
is made, so the executable ticket now carries it:

- `scripts/etf_book_order.py::width_disclosure` reads this audit's rows and the card's
  own `config.n_hold` out of `results/etf_book_production/latest.json`. Nothing is
  hardcoded and nothing is re-run: if either source is missing it returns `None` and both the
  ticket's `caveats` and the `ORDER-<asof>.md` card say "名数差未定价" instead of
  silently reporting no difference (leg13/leg16 pin that).
- `ORDER-2026-10-23.md` gained a "这张单是 5 名，卡片是 12 名" block with the two rows and
  the deltas, so the aggressive end of the book is labelled at the point of action.
- Both book legs are now wired into `Tools/s6_chain_bmc.py` (they were hand-run only, and
  r1267/r1269/r1273 each named that as owed): `etf_book_forward` appends one mark per new
  bar, `etf_book_order` re-emits the ticket. First chained run: forward = NO-OP (no new
  panel bars, cutoff 2026-10-23), order = ticket rewritten, chain 41/41 rc0.

## Reproduction

```
python scripts/etf_book_width_audit.py --selftest     # 4 legs, offline
python scripts/etf_book_width_audit.py run            # rewrites results/etf_book_width_audit.json
python scripts/etf_book_order.py --selftest           # 16 legs, incl. the disclosure contract
```