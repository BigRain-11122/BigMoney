# r1356 — the two live widths, on one ruler (the gap is inside the engines' own disagreement)

2026-10-30, bm-c. Face: `results/etf_book_live_width_ruler.json`.
Script: `scripts/etf_book_phase_atlas_arms.py --live-widths` (selftest 74 → 88).
Cards E268/E269.

## What was asked

r1355 turned the width ladder into a resolution floor and answered with a direction, not a size.
That answers the ladder. It does not answer the two faces a reader actually holds: the production
card runs **12 names** under an 8% vol target, the executable ticket runs **5 names** under
β = 0.20 with a cash leg, and the ticket's own `card_agreement` block says the five are a
**prefix** of the twelve. So "two live widths" is one book truncated, not two books — and r1355
had already published that the two engines disagree about the *direction* of the 5→12 rung.

The only question left for somebody holding the ticket: is the gap between the two live faces
inside that disagreement, i.e. may any part of it be read as a width effect at all?

## Answer — a coin flip worth 0.09pp, inside a 2.05pp disagreement

**Paired, not difference-of-medians.** The atlas carries one row per decision origin of a
complete R20 cycle (20 origins per cell), so the two live cells are compared origin by origin
rather than by subtracting two medians:

| quantity | value |
|---|---|
| median of the 20 paired differences (12 − 5) | **+0.090pp** |
| mean / range / sd | +0.129pp / −2.050 .. +2.890pp / 1.255 |
| direction | **10 up, 10 down** (sign agreement 0.500) |
| difference of the two medians (the ladder's rung) | **+0.515pp** |

The rung the ladder published is 83% aggregation: the same step taken across paired phases is
+0.090pp. That is not a smaller effect, it is a different quantity, and the difference between
them is the pairing rather than the book.

**The comparator is a difference minus a difference.** The capacity face prices the same step on
its own universe: +0.515pp on the atlas engine, **−1.530pp** on the capacity engine. Disagreement
2.045pp, **with the sign flipping**. The gap between the two live widths is 4.4% of that, and 1.3%
of the atlas ruler (6.68pp).

Verdict: **COIN_FLIP_INSIDE_ENGINE_DISAGREEMENT** — the two live widths are not separated by
their own phases, and the engines disagree about the same step by more than the whole gap.

## The as-issued faces move two knobs, not one

The ticket's own `width_disclosure.square` is a 2×2 (rule × width), re-derived here from its four
cells rather than read off its summaries:

| rule \ names | 5 | 12 |
|---|---|---|
| beta | +11.33pp | +9.80pp |
| vol | +12.19pp | +12.51pp |

The as-issued diagonal is +1.18pp (card − ticket), but the **width** effect is −1.53pp under the
beta rule and +0.32pp under the vol rule, while the **rule** effect is +0.86pp at 5 names and
+2.71pp at 12. The interaction (+1.85pp) is larger than either width effect — so most of the
difference a reader sees between "the card" and "the ticket" is the risk knob, not the width. Both
decomposition paths reproduce the diagonal (+1.180 / +1.180), which is the arithmetic check that
the four cells are internally consistent.

## A coincidence recorded as a coincidence

The beta-rule width effect (−1.530pp) equals the capacity engine's 5→12 rung (−1.530pp) **to the
basis point**. They are different quantities on different windows — one is a live 2×2 cell
difference over 2024+, the other a second engine's rung on its own universe — so the face publishes
the collision with that sentence attached instead of letting anybody read agreement into it. Two
published numbers that happen to land on the same basis point is exactly the r1292 shape.

## What this changes for the operator

Nothing about which face to hold: the ticket is a *risk-scaled truncation* of the same book, and
that is what its own caveat already said. What changes is that the difference between the two
numbers on the two documents is now attributable: **≤1.53pp is width and is not resolvable by
either engine; the rest is the β-vs-vol rule.** The width question is therefore closed for the
live pair, and the only open width question left is the one r1355 already priced (a hill, not a
slope).

## Wiring

S6 leg `etf_book_live_widths` (gate + refresh) and one smoke leg that re-derives the verdict from
the face's own published per-phase deltas — so the label cannot drift away from the numbers that
are supposed to produce it, and the gate carries the same three states (pass / inconsistent /
stale) as the other two floors.