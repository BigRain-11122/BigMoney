# E219 — the production signs rank 6th of 64, and a sign chooser with no hindsight earns −1.63%/yr (r1336 bm-c)

**Card:** E219 in `knowledge/METHODOLOGY_ASSETS.md`.
**Artifacts:** `results/etf_sign_enum.json` (re-emitted every chain run by the new
`etf_sign_enum` leg) + smoke leg that re-derives the verdict from the arm table.
**Code:** `scripts/etf_sign_enum.py` — `z_mats / score_from / main_effects / gate`,
selftest 13/13. One panel load, then one engine call per sign set (82s, offline).

## The sentence E218 left open

E218 measured that the six production factor directions in `etf_composite_pf.SIGNS` are
*exactly* the full-sample IC signs, and that reconstructing them from realised windows only
earns −10.81%/yr. It could not say **how much the choice itself is worth**, because it ran
three arms (fixed / trailing-IC / reversed) out of a space of 2^6 = 64.

Sixty-four is small enough to run them all. Same panel, same eligibility, same engine
(`fast_next_open`, next-open fills), same costs (10bp/side), same width (12 names), same
cadence (20 bars), same window (2020-01-01 → 2026-10-28). The only thing that changes across
arms is six signs.

## What the 64 arms say

| | CAGR | note |
|---|---|---|
| production signs | **+6.14%** | rank **6 / 64** (92nd percentile) |
| median arm (no hindsight) | **−1.63%** | what "pick a direction per factor" is worth |
| best of 64 | +8.56% | the ceiling an in-sample chooser can reach |
| worst of 64 | −12.28% | |
| spread | 20.84 pp/yr | one sign block moves the headline more than the whole factor library |
| arms with positive CAGR | 42.2% (27/64) | |

Verdict, recomputed by the gate from the arm table: **`signs_sit_at_the_sample_optimum`**
(production rank ≤ the frozen top-decile line of `ceil(0.10 × 64) = 7`).

**The honest number is the 7.77 pp/yr gap between rank 6 and the median.** A rule that picks
one direction per factor *without* looking at how the factors paid would have landed at
−1.63%/yr on this panel; the published +6.14% is a draw from the top 10% of that space. Both
statements are in-sample for the picker — the point is that the picker's expected draw is the
median, and the median is negative.

## Which sign is actually doing the work (factorial main effects)

The design is a full 2^6, so for any one factor the other five signs are perfectly balanced
between the `+` and `−` halves: the difference of the two half-means is that factor's own
contribution, no engine rerun needed.

| factor | main effect (pp/yr) | production sign | is the production sign the good one? |
|---|---|---|---|
| vol_60 | **−4.87** | − | yes (the `−` half is 4.87pp/yr better) |
| intraday_range | **−3.65** | − | yes |
| adx_14 | +2.01 | + | yes |
| price_position | +1.15 | + | yes |
| drawdown_60 | +1.06 | + | yes |
| mom_12_1 | **−1.37** | + | **no** — the `−` half is 1.37pp/yr better |

Two low-volatility directions carry 8.5 of the 11.4 pp/yr total main effect; momentum's
published direction is a net drag on this panel. That is a fact about the period, not a
recommendation: `mom_12_1 −` on 2020-2026 is exactly the kind of in-sample reversal E218
warned about, and its main effect (−1.37pp) is the smallest of the six.

## Consequence for money

- The card's headline is a **rank-6-of-64** draw, not a rule. That sentence is now derived
  from this artifact and travels with the artifact (chain leg), not typed into prose.
- The "cheap fix" is closed: since flipping momentum only buys the difference between rank 6
  and the best-of-64 (+2.4pp), and E218 already showed trailing-IC reconstruction loses 17pp,
  there is no sign rule on this factor mix that a live operator could have run to reach the
  headline. What is left is E218's conclusion — a sign rule must be frozen *before* the
  sample, on economic grounds, and tested as its own preregistered job.
- The spread is the money number: 20.8 pp/yr across sign sets on a book whose published
  advantage over its own equal-weight control was ~4pp. Sign selection dominates the signal.

## Caveats on this face

- Reference engine only (no impact cost, no gap risk), flat sizing: the vol target / beta
  overlay is deliberately out, so this is not the card's 9.13% headline and should not be
  compared to it. Every arm is sized identically.
- All 64 arms are in-sample by construction. The distribution bounds what a sign chooser can
  reach; it is not a live return estimate.
- Zero-sign arms are excluded: the enumeration is over directions, and "drop a factor" is a
  different question (E218's IC floor already prices it).
- ETF pool is today's listed set (survivorship), unchanged caveat from every face on this line.
- Main effects are average differences over a balanced factorial design, not interactions;
  a sign pair that only works together would show as two small effects and one big joint arm.
  The best-of-64 arm (+8.56%) is the only interaction-free place that shows up, and it is not
  claimed to be reachable without hindsight.