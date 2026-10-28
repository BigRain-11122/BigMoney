# One book, four published numbers — which one does the executable ticket earn?

`scripts/etf_book_cagr_reconcile.py` → `results/etf_book_cagr_reconcile.json` (grid) ·
`results/etf_book_cagr_reconcile.json:bridge` · evidence cutoff **2026-10-27** · window
2020-01-01..cutoff, R=20 bars, no impact term (impact is a size question and lives in
`etf_book_capacity_rule`).

## The problem this replaces

Four annualised numbers were published over the same window and treated as four views of
one book:

| where | config it actually prices | cagr |
|---|---|---|
| `results/etf_book_spanning.json:book` | 12 names, 8% vol target, 10bp, production panel | **9.62%** |
| `results/etf_book_capacity_rule.json:rule_at_8bp_no_size` | 5 names, beta 0.20 cover, 8bp, raw panel | **7.80%** |
| same face, ladder NAV = 1e6 | 5 names, beta 0.20, 8bp **+ impact** | **7.38%** |
| same face, 1%-of-ADV ceiling (NAV 1.53M) | worst rung of that ladder | **7.28%** |

`capital_placement.py` (r1319) put the 9.62% end and the 7.28% end in one column and
called the difference an **unattributed "run diff" of 2.34pp** — while the order sheet a
human actually trades (`ORDER-<asof>.md`) is neither of those configs: it is 5 names with
a 0.20 beta cover at 8bp.

## What the grid says

Every cell below is a full 2020-01..2026-10-27 run on ONE panel with ONE fill engine; the
only differences between cells are the three knobs (width, risk rule, per-side cost).

Production stack (the panel/engine the card, the order sheet and the forward ledger use):

| n | rule | 8bp | 10bp |
|---|---|---|---|
| 12 | flat (no risk rule) | 14.60% | 14.25% |
| 12 | vol target 8% | 9.87% | **9.62%** (card) |
| 12 | beta 0.20 | 12.66% | 12.31% |
| 5 | flat | 16.23% | 15.80% |
| 5 | vol target 8% | 11.95% | 11.66% |
| 5 | beta 0.20 | **13.35%** (ticket) | 12.95% |

Capacity-face stack (raw un-repaired panel, no class filter — where 7.80% was printed):

| n | rule | 8bp | 10bp |
|---|---|---|---|
| 12 | flat | 6.41% | 6.11% |
| 12 | beta 0.20 | 6.47% | 6.27% |
| 5 | flat | 7.62% | 7.29% |
| 5 | beta 0.20 | **7.80%** (published) | 7.55% |

Controls: the card cell reproduces `etf_book_spanning.json` to **0.00pp** and the no-size
cell reproduces `etf_book_capacity_rule.json` to **0.00pp**. The grid is the same
experiment as both published faces, not a re-implementation.

## The two findings

**1. Most of the published spread is not a rule difference — it is the universe.**
Hold the knobs fixed (5 names, flat rule, 10bp): production panel **15.80%**, raw panel
**7.29%** — 8.5pp apart. Swapping only the engine at fixed panel moves 0.2-1.5pp, so the
engine is not the story. `USE_CLASSES = (equity, commodity, convertible)`: the production
universe excludes bond and money-market ETFs (1,499 symbols vs 1,608 raw). The same
ranking rule is then forced to stay in risk assets — delivered vol **16.4% vs 10.3%**,
Sharpe 1.02 vs 0.76. So the filter is a **risk choice**, not free alpha: roughly 1.6x the
volatility for the higher return.

**2. Within the stack that is actually traded, the ticket beats the card — with more risk.**
Card 9.62% (vol 10.17%, DD −11.8%) → ticket 13.35% (vol 13.46%, DD −16.0%), **+3.73pp**,
decomposed by stepping one knob at a time:

| knob | step | forward path | reverse path | marginal off card | marginal off ticket |
|---|---|---|---|---|---|
| width | 12 → 5 names | +2.04pp | +0.69pp | +2.04pp | −0.69pp |
| rule | vol 8% → beta 0.20 | +1.29pp | +2.79pp | +2.69pp | −1.40pp |
| cost | 10bp → 8bp | +0.40pp | +0.25pp | +0.25pp | −0.40pp |
| **interaction** | (width x rule) | **−1.25pp** | **−1.24pp** | | |

Both orders sum to exactly +3.73pp, and both endpoints agree the interaction is
**−1.25pp** — the width and rule effects are not separable here (r1291's width x leverage
finding, reproduced on a second pair of knobs). Quoting "narrowing is worth +2pp" without
the interaction is how a knob that is really worth nothing gets credited.

## The bridge that closes r1319's unattributed term

`capital_placement` compared card 9.62% with ceiling 7.28% and called it 2.34pp of
"run diff". It is 2.34pp, but it is three measured things and one measured thing that
compensates:

| term | pp/yr | what it is |
|---|---|---|
| knobs (card → ticket, production stack) | **+3.73** | width + rule + cost + interaction |
| stack (production → capacity-face panel, ticket knobs) | **−5.55** | 13.35% (prod) vs 7.80% (raw) |
| impact (no size → 1%-ADV ceiling NAV) | **−0.52** | 7.80% → 7.28% on the capacity ladder |
| **total (card − ceiling)** | **−2.34** | matches the published gap exactly |

Nothing left unattributed. And the sign matters: on the traded stack the ticket is
*better* than the card by 3.73pp; the published comparison showed the book *worse* than
its card because the ceiling number was priced on a different universe.

## What this changes downstream

* `capital_placement.py` now reads the level from the ticket (13.35%, size-free) and the
  size effect from the capacity ladder's **impact delta** priced at the **deployed**
  amount, never from the ladder's absolute levels. Regenerated face
  (`research/CAPITAL_PLACEMENT.md`): the book is the best vehicle at **CNY 300k / 1M /
  1.5M** (+9,780 / +32,600 / +40,635 per year) and the four-ETF basket takes over from
  **3M**. r1319's face had the basket winning all six tiers because it priced the book at
  the ceiling's 7.28%.
* Both published comparisons are now four-term exact bridges
  (`basket_vs_card` + `card_vs_ticket` + `ticket_vs_size` + `size_vs_effective` ==
  total gap), with a selftest leg pinning the sum, so no future term can be added without
  one of them shrinking.
* Any CEO-facing statement of "the book's return" must now name (a) the panel and (b) the
  rule: the same rule earns 7-8pp more on the class-filtered universe at ~1.6x the
  volatility, and the card's printed 9.62% is not the rule the order sheet trades.

## Risk disclosure that must travel with the ticket number

| book | cagr | vol | maxdd | sharpe |
|---|---|---|---|---|
| card (12 names, vol 8%, 10bp) | 9.62% | 10.17% | −11.77% | 0.992 |
| ticket (5 names, beta 0.20, 8bp) | 13.35% | 13.46% | −15.98% | 1.036 |

The ticket earns 3.73pp more *and* takes 3.3pp more volatility with 4.2pp more drawdown.
Sharpe improves by only 0.044, so the honest sentence is "more risk, marginally better
efficiency", not "the narrower book is better".

## Limits (unchanged, and now more visible)

* Survivor pool: the panel only contains ETFs that exist today (`etf_pool_survival.py`
  buckets that; 1,645/1,656 eligible symbols still print to the panel edge).
* The pre-2020 spanning test (`etf_book_spanning_pre2020.json`) says the rotation premium
  in that window is a fraction of the boom-window figure — this face does not re-test it.
* No impact term here by construction: every cell is size-free. Impact is measured in
  `etf_book_capacity_rule` and transferred as a delta, not re-derived.
* The interaction is measured, not explained: this face can say the width and rule effects
  overlap by 1.25pp, not why.