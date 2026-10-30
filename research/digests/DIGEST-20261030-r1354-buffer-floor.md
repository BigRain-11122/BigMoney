# DIGEST 2026-10-30 r1354 bm-c — the retired buffer family now has a size, and the size is past the end of the knob

## Why this face exists

r1353 closed the buffer family with a direction: every strength between k=0.02 and k=0.40 landed
inside its own per-cell band, so "the effect is small" was published and the family retired. A
direction is not a size. "Inside the band at every strength we tried" leaves the obvious question
open — **how strong would k have to be for this ruler to see it?** — and an open question at 280
engine runs per attempt is what re-litigates a closed family three weeks later.

## What was measured

`scripts/etf_book_phase_atlas_arms.py --floor` fits the five published buffer arms (plus the k=0
baseline as an explicit *identity* anchor, since its delta is zero by definition) and answers in
the knob's own units.

| arm | k | median delta | median band | resolvable share | label |
|---|---|---|---|---|---|
| buffer_k02 | 0.02 | -0.018pp | 7.02pp | 0.000 | NOT-SEPARABLE |
| buffer_k05 | 0.05 | -0.030pp | 6.85pp | 0.000 | REJECT |
| buffer_k10 | 0.10 | +0.072pp | 6.99pp | 0.000 | NOT-SEPARABLE |
| buffer_k20 | 0.20 | +0.138pp | 6.58pp | 0.000 | NOT-SEPARABLE |
| buffer_k40 | 0.40 | +0.318pp | 6.04pp | 0.000 | REJECT |

Fit through the k=0 identity: **+0.862pp of median CAGR per unit k, r² 0.965** across a 20×
sweep — the axis is close to linear, so extrapolating along it is the *least* speculative thing on
offer here. The ruler is the baseline grid's median cell band, **6.68pp**.

**k required to reach the ruler = 7.79.**

## The answer to the answer

k is not a free parameter: it is the share of a target weight change the book executes per
rebalance. k=1.0 already means "trade the entire move the instant the signal moves", and anything
above that is not a larger buffer — it is refusing to trade. So the requirement sits **7.8× past
the end of the knob's domain**, and the verdict is `UNREACHABLE_BY_CONSTRUCTION`.

That is a different fact from "we have not looked", and it is the one that retires the family for
good: the whole measured axis spans 0.318pp, i.e. **0.050 of the ruler** — one twentieth of the
band it is asked to beat.

Two disclosures that travel with the face:

1. **The fit is an extrapolation and is labelled as one.** r² 0.965 over a 20× sweep is good, but
   the published consequence does not depend on it being exact: even if the true slope were 4×
   steeper, k required would still be ~1.9 — past the degenerate end.
2. **The k=0 point is an identity, not a sixth experiment.** Its delta is zero because it *is* the
   baseline; the intercept is published (-0.031pp) precisely so a reader can see the line passes
   near it rather than being forced through it.

## Also this window

The dead r1352/r1353 tail (three buffer faces, digest, card E264) was adopted only after being
re-derived here: arms `--check` green on the 9-arm face, selftest 50/50 before this round's legs
were added, and every median in the digest recomputed from the arm rows (-0.018 / -0.030 / +0.072 /
+0.138 / +0.318pp, not-worse shares 0.917 / 0.667 / 0.833 / 0.917 / 0.750, clearing cells 0/12 for
all five).

## Consequence

Buffer k is closed with a number, not an opinion. A future "what about a smaller buffer" seed now
has to answer the floor face, not re-run the sweep: the axis is monotone, near-linear, spans 1/20 of
the ruler, and would need a k that means "never trade". Card E265.

Faces: `results/etf_book_buffer_resolution_floor.json`,
`research/ETF_BOOK_BUFFER_RESOLUTION_FLOOR.md`, chain leg `etf_book_buffer_floor`,
selftest 50 → **60** legs in `scripts/etf_book_phase_atlas_arms.py`.