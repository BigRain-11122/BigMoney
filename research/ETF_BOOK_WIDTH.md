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

## Correction (r1278): the −1.52pp was a width effect *under the ticket's rule only*

The table above varies width while holding the ticket's beta overlay fixed, then compares the
12-name row against the 5-name row. But the two published faces do not differ in width alone —
they also use different leverage rules (ticket: beta target 0.20; card: 8% vol target). So the
−1.52pp was being attributed to width, although it is the width **under one rule**. Both rules
re-run on the same book series (`book_leg` cache) and the same accounting, factor 2×2:

| rule | 5 names | 12 names | width effect |
|---|---|---|---|
| beta target 0.20 | 11.05% / 1.353 / −6.01% | 9.53% / 1.560 / −4.17% | **−1.52pp** |
| vol target 8% | 11.69% / 1.351 / −7.56% | 11.88% / 1.355 / −7.95% | **+0.19pp** |

Rule effect (vol minus beta): **+0.64pp at 5 names, +2.35pp at 12 names**; interaction
+1.71pp. So:

- **The width penalty is not a property of width, it belongs to the beta rule.** Under the
  card's own rule, going from 5 to 12 names is worth +0.19pp of CAGR with unchanged Sharpe
  (+0.004) and 0.4pp *more* drawdown — i.e. flat, not costly.
- **The two rules chase the same thing from opposite sides.** A wider basket is calmer: beta
  falls and realised vol falls. The beta rule therefore cuts exposure *more* when the basket is
  wide (cash 55.0% → 61.9%), while the vol rule cuts it *less* (cash 48.1% → 42.9%). Same calm
  signal, opposite action, which is the whole interaction term.
- Read on the diagonal the two published faces differ by **+0.83pp** (card-side rule at 12 vs
  ticket rule at 5), not −1.52pp. The card's book is the *better* of the two on this accounting,
  not the more conservative one.

Honest limits of this correction, both load-bearing:

1. It is measured **inside the ticket engine** (`F.run_next_open` + `BT.apply_overlay`), because
   that is the only place both rules can be applied to one book series. The card's own headline
   comes from `R.open_to_open_equity` (10bp/side, vol target inside the engine) and prints
   9.47% / 0.98 / −11.8% at 12 names — a different level from the 11.88% / 1.355 / −7.95% here.
   So the two published faces differ in **three** dimensions (width, rule, engine); this square
   prices the first two and leaves the engine delta explicitly unpriced.
2. The vol arm inherits r1272's estimator bias: a one-sided `min(1, target/vol)` sized on a
   biased-low 60-bar estimator delivers ~1.27× its label, which is why the vol arms carry less
   cash and more drawdown than an 8% label suggests. Reported, not corrected.

The ticket's `width_disclosure` still quotes the beta-rule rows, and now says so.

## Reproduction

```
python scripts/etf_book_width_audit.py --selftest     # 8 legs, offline
python scripts/etf_book_width_audit.py run            # rewrites results/etf_book_width_audit.json
python scripts/etf_book_order.py --selftest           # 16 legs, incl. the disclosure contract
```