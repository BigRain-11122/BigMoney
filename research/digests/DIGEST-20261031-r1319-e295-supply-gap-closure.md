# E295 supply-gap closure -- "one more rung" is two questions, and only one of them was open (r1319 bm-b)

**Face:** `results/state_tilt/BANDCLOSURE-2026-10-29.json` (+ `bandclosure_latest.json`)
**Producer:** `scripts/e295_supply_gap_closure.py` (run / verify 0 problems / selftest 22/22)
**Wired:** chain leg `supply_gap_closure` (rc=0, 0.15s) + smoke leg (PASS; FAILs when a graded margin
is repointed to another window or the ladder span is mutated)
**Upstream:** E285 (demand rows + cells), E287 (published caps per polarity), E256 (the draw ladder),
E258 (same-window multipliers as a reproduction witness), BANDFLOOR (the narrowing instrument)

## What the margins actually were

E287 closed its round with two numbers that both invite the same sentence -- "one more rung would
close it": the optimistic widening supply stops 3.799 pct above the nearest above-ceiling row
(`self|200|0`, flip 2.331055 vs cap 2.245734), and the narrowing instrument stops 3.669 pct above
the nearest below-floor row (`self|60|8`, flip 0.889387 vs 0.922022).

Reading the demand rows' own `cell` column changes that sentence in a way that matters: `self|200|0`
lives in `all_five` and the cap was written at `early_three|60`, i.e. **neither number came from the
window the ladder was measured in**. The two demands published in the ladder's own window
(`era_2025_now`) are `star_lag1_residual|60|14` (flip 2.380091) and `self|60|8` (flip 0.889387), and
graded there the widening margin is **5.98 pct**, not 3.80. Nine of the twelve demand rows have no
ladder at all and are published as `not_graded` with that reason.

## The measurement

The ladder (E256, 14 rungs x 6 draw counts, base 60, prefix-nested per seed) prices two different
things, and conflating them is the trap:

| question | measurement | result |
| --- | --- | --- |
| granularity -- is the grid too coarse? | adjacent-grid step gain, matched seed for seed | 70 steps, median 1.0699, range 1.0000..1.2589; **37 of 70 buy more than the 5.98 pct margin on their own** |
| headroom -- is any rung on the other side? | edge(1920)/edge(60) per rung | span 1.0000..1.9254 central, 2.4271 at a rung's own widest seed |

Granularity is generous, headroom is not. On the central basis **no rung crosses either margin**:
the nearest rung to `star_lag1_residual|60|14` stops at 1.925449 (residual factor 1.236123), and on
the narrowing side the ladder publishes no sub-1.0 reading at all -- its span only widens, so the
`self|60|8` demand is on a polarity the draw ladder cannot express (residual 1.124370 against the
ladder's own floor of 1.0000). A single rung, `tail|100|1920`, does reach 2.427092 at one of its
three seeds while its central reading is 1.115094 -- a crossing that exists at one seed of three.

Verdict: `one_margin_is_crossed_by_a_single_seed_rung_only`. **2 of 2 interpolation(s) aborted**, with
the residual factor published; nothing between or beyond the rungs is fitted, because the next rung
is a larger draw budget, which is a different, billable decision.

## Reproduction witness (not a new claim)

E258 rebuilt the band per window and published `era_2025_now|60 = 1.644145`; the ladder's own
`head|408` / `tail|408` rung at 1920 draws reproduces that exactly (|diff| 0.0). Two producers, same
window, same base draw count -- so "the ladder describes this family" is measured, and a drift there
will now be caught by the chain leg rather than by a reader.

## Three rules to carry

(a) **Price granularity and headroom separately.** "The margin is smaller than one step" answers a
resolution question and says nothing about whether a rung exists; a ladder can have a 7 pct median
step and still stop 24 pct short of the demand. Publishing only the second number invites the
wrong fix (grind the grid finer).

(b) **Re-derive the margin in the window that owns the ladder.** A margin is a difference between a
demand and a reference; both carry a window, and E258 already measured that a window's multiplier
differs from another's by more than 15 pct. Grading across windows prices a different sleeve's null.
In this case the same-family margin moved 3.80 pct -> 5.98 pct purely by reading it where the ladder
lives.

(c) **A crossing at one seed of three is not a crossing.** Publish per-rung central / matched-seed
min / matched-seed max, the count of crossing rungs, and the residual factor when the count is zero;
a seed-dependent crossing quoted as a result is how a noise draw becomes an adoption.