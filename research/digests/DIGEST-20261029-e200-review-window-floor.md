# DIGEST 2026-10-29 · E200 — what E198's "not found" could actually have found

Round r1333 (bm-c). Face: `results/reviewwindow_floor/REVIEWWINDOWFLOOR-20261028.json`
(mode `reviewwindowfloor` in `scripts/e39_panel_census.py`, selftest 689→695).
Upstream: E198 (`REVIEWWINDOWCROSS-20261028.json`), E196 (`LADDERDROPCARRIER-20261027.json`).

## The question

E198 answered *no*: on a panel the ladder-drop family never touched, the
review window does not move relative performance (pooled p 0.1885, ratio 1.148,
3 of 17 cells at p≤0.10 versus 1.7 expected). A **negative is only informative
if the test could have produced a positive** — so the next question is not
another panel, it is the test's own blind spot: *which effect size would E198
have flagged at 80% power, on exactly these rows?*

## What was measured

The floor, on the same rows the verdict was computed from (one reader:
`_reviewwindowcross_rows` feeds both faces, so the floor can never describe a
different panel than the p it defends).

- 17 cells × 80 monthly returns = **1,350 member-months**, **440 in-window**
  months pooled (26 per cell, 24 for `588000`); 2 files still absent
  (`510880`, `510180`), published, not substituted.
- Statistic = pooled mean standardised |member − bench| inside vs outside the
  window — i.e. **E198's own statistic**, not a normal-theory stand-in.
- The permutation null keeps each cell's |gap| multiset and shuffles only the
  labels, so the pooled inside mean is a sum of independent per-cell
  samples-without-replacement. Its null expectation is exactly 1 (per-cell
  standardisation forces every cell mean to 1) and its variance is the
  hypergeometric sum — computed in closed form, not sampled.
- Effect = window months' |gaps| multiplied by a factor *f* before
  standardisation. Because standardisation is per cell, the published ratio
  obeys `ratio(f) = f · ratio(1)` **exactly**, so the floor converts to ratio
  units with no approximation.
- Alpha 0.01 (reused from E198) and 0.10 for the per-cell reading, power
  target 0.80, bisection to 12× — all declared before any file is read.

## Reading

| quantity | value |
|---|---|
| observed pooled ratio | **1.148** (p 0.1885) |
| **minimum detectable ratio at 80% power** | **1.480** (f = 1.304) |
| per-cell floors (16 of 17 cells) | median **1.678**, min 1.504, max 2.609 |
| cell with no reachable floor | `510310` (observed 0.197, window months *quieter*) |

Power curve on this panel (pooled, one-sided α=0.01):

| effect multiplier | resulting ratio | power |
|---|---|---|
| 1.00 | 1.148 | 0.103 |
| 1.10 | 1.258 | 0.299 |
| 1.25 | 1.422 | 0.690 |
| 1.50 | 1.692 | 0.978 |
| 2.00 | 2.226 | 1.000 |

Verdict (frozen rule, recomputed by the gate):
**`negative_is_below_the_detection_floor`**.

**The sentence that changes:** E198's "not found" is now a *measurement*, not a
shrug. This panel would have needed the window months to carry **48% larger**
|gaps| than the rest of the calendar to fire at 80% power; the observed excess
was **15%**. The test was not silent about a small effect — it was structurally
unable to see one that small. Per cell the bar is higher still (median 1.68),
so "cell-level window effects" are the least testable claim this family could
make on 80 months of data.

## Two checks that make the floor trustworthy

1. **Analytic sd vs. the permutation distribution it claims to describe**:
   0.08951 (closed form) vs 0.09055 (2,000 label shuffles) → **1.16% apart**.
   The power curve leans entirely on that variance, so it is checked rather than
   asserted.
2. **Discrete crossing**: at the published floor the *actual* permutation p is
   **0.00025** (≤0.01), and at **0.85×** the floor it is **0.043** (>0.01). The
   floor is a real edge in the discrete test, not a by-product of the normal
   approximation used to find it.

## What this does not say

1. The floor is a property of the **test**, not of the market: it says which
   effect sizes this panel size could flag, and nothing about whether a larger
   effect exists outside it.
2. Power is priced for a multiplicative window effect that hits **every cell in
   the same direction**. An effect concentrated in a few cells, or pointing both
   ways, needs a bigger per-cell move — which is what the per-cell floors are for.
3. The permuted null keeps this panel's own gap dispersion, so a quieter panel
   would publish a lower floor without the world becoming easier to read.
4. 2020-01→2026-09 is one regime and 17 named funds with local files are not a
   random sample of the ETF universe.

## Cost note

The new leg costs **4.7 s** on the S6 chain: it reads the same 20 daily CSVs and
never loads a panel, so it stays inside the 1 GB-free-RAM window that made the
bigger gates slow this week. Two cells (2.6× and unreachable) are the price of
insisting on 80 months per cell rather than substituting shorter-history names.