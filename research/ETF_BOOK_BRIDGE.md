# ETF book bridge — from the card's published 9.47% to the ticket's 11.05%, knob by knob

Window: r1279 (2026-10-26). Artefacts: `scripts/etf_book_bridge.py` →
`results/etf_book_bridge.json`. Panel cutoff 2026-10-23, 32 arms, 2.1 min
single-machine runtime, `--selftest` 10/10.

## Why this exists

Two live production faces report two different numbers and neither was priced
against the other:

| face | file | names | rule | published |
|---|---|---|---|---|
| production card | `scripts/etf_book_production.py` | 12 | 8% vol target | **9.47% / 0.98 / -11.8%** (full history) |
| executable ticket | `scripts/etf_book_order.py` | 5 | beta 0.20 overlay + GC001 ladder | **11.05%** (since 2024) |

r1275 priced the width difference *inside* the ticket engine and r1278 showed the
sign of that difference flips with the rule. Both stayed inside one engine, so the
gap between the two published numbers — a 1.58pp difference made of universe,
engine, accounting basis, fee model, rule, width, cash and cost — was still
unexplained. This round builds the bridge: one walk from the card's headline to the
ticket's, each step moving exactly one knob and nothing else.

## Method

32 arms = {engine: card | ticket} × {panel: card universe | ticket universe} ×
{names: 5, 12} × {rule: none, vol 8%, vol+repo, beta 0.20, beta+repo}; plus three
`@0bp` twins (same arm, both fee legs zeroed) so the fee contribution is measured
rather than assumed, and one `@8bp` arm so the ticket's own cost step is visible.

The card engine is the production card's own code path (`R.open_to_open_equity`,
vol scale inside the weights); the ticket engine is the executable ticket's
(`run_next_open`, scale applied on top of an unlevered book). Neither is a
re-implementation of the other. `--selftest` pins both engines against hand-built
fixtures, including a leg that *proves* the two conventions disagree on the same
synthetic panel (1.370766 vs 1.398458, rel 1.98%) so the "basis" step cannot
silently vanish.

## Result — the bridge closes exactly

Start `card@card|n12|vol8` 9.47% (full) → window to 2024-01-01 18.08% → … →
end `ticket@ticket|n5|beta+repo@8bp` 11.05%. Steps sum to +1.58pp = the whole gap.

| # | knob | move | Δ (pp, since 2024) |
|---|---|---|---|
| 1 | window | full history → 2024-01-01 | **+8.61** |
| 2 | universe | card USE_CLASSES → ticket KEEP | −2.32 |
| 3 | card fee | 10bp → 0 | +1.51 |
| 4 | accounting basis | open_to_open → run_next_open, both fee-free | **−5.17** |
| 5 | ticket fee | 0 → book 8bp + k-leg 10bp | −1.00 |
| 6 | rule | vol 8% → beta 0.20 | −2.69 |
| 7 | width | 12 names → 5 names | +1.63 |
| 8 | cash | nothing → repo ladder | +1.01 |
| 9 | cost | 10bp → 8bp/side | +0.00 |

Readings that matter:

- **The window is the biggest single "improvement" (+8.61) and it is not skill.**
  2024+ is simply a better stretch; every cell in the factorial shows it. Any
  comparison between the two published numbers that mixes windows is measuring
  the calendar.
- **The accounting basis is the biggest single cost (−5.17).** Moving from
  open-to-open accrual to next-open fills removes 5.17pp of the ticket's
  advantage. That is not a defect of either engine; it is the price of being
  executable. This is the number r1278 left open.
- **Universe (−2.32) and rule (−2.69) are the two real strategy differences**, and
  they point in the same direction as the panel work already published
  (`ETF_WIDE_PANEL_REFRESH.md`, `ETF_PHASE_BETA_TARGET.md`).
- **Width (+1.63 here) is consistent with r1278, not with r1275.** Under the beta
  overlay, narrowing to 5 names *raises* return because the overlay cuts less
  exposure when the basket looks calm — the same interaction r1278 found inside a
  single engine, now reproduced across engines.

## The vol label gap — already disclosed, now attributed

The card face already prints its own delivery gap
(`results/etf_book_production/latest.json → vol_delivery`): *"target 8% → delivered
10.2% over the full window (1.27x)"* (full 1.272 / IS 1.246 / OOS 1.306). The
bridge reproduces that ratio exactly from an independent code path (1.272) and adds
the comparison the card cannot make on its own:

| engine | delivered vol (full) | ratio to an 8% label |
|---|---|---|
| card engine, vol-8% rule | 10.18% | **1.272** |
| ticket engine, vol overlay | 8.52% | **1.065** |

So the 27% overshoot is a property of *that rule as implemented* (a backward-looking
`min(1, target/σ)` scale applied inside the weights), not of the panel or the
period: the same universe under the ticket's overlay lands within 6.5% of its label.
Practical consequence for the reader: the card's 9.47% / −11.8% describes a ~10%-vol
book, so comparing it to an 8%-vol target or to a levered variant without this
adjustment overstates the card by roughly a quarter of its risk budget.

## Caveats

- Path-dependent attribution: the step ORDER is one path through a factorial; an
  interaction-heavy knob (rule × width) moves between positions.
- Both engines charge a per-side rate on turnover but apply the vol scale
  differently (inside the weights vs on top of an unlevered book), so the engine
  step carries a little accounting with it — disclosed, not netted.
- The card engine accrues the new book from the open of its decision bar, i.e. one
  bar of return exists before the decision does; `run_next_open` fills at
  open(d+1). Neither engine can referee the other's level.
- Survivorship (the ETF pool is today's list) applies to every cell equally and is
  NOT what the differences measure.

## Reproduce

```
python scripts/etf_book_bridge.py --selftest    # 10/10
python scripts/etf_book_bridge.py               # ~2.1 min, writes results/etf_book_bridge.json
```

Re-running reproduces every number in the JSON byte-for-byte apart from the `ts`
field (verified r1279: full-file equality after dropping `ts`).