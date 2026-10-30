# DIGEST 2026-10-30 r1272 bm-b -- E246: the star leads, but the lags disagree in sign

Card: `knowledge/METHODOLOGY_ASSETS.md` E246. Runner `scripts/e246_star_direction.py`
(selftest 14/14). Face `results/state_tilt/STARDIR-2026-10-29.json` (+ `stardir_latest.json`).
S6 leg `star_direction` (after `pair_slope_matrix`), smoke leg added.

## The question E245 left open

E245 named the "rest channel" a star: sh588000's turnover is decisive for all four other
members in the five-member window (mean slope 0.769), and pre-2020, before that sleeve prints,
no star exists. Two mechanisms produce exactly that simultaneity:

* (a) that sleeve's turnover carries a book-wide factor -- its flow moves the others;
* (b) all five sleeves load on one common driver and the star is simply the column the
  regression reads best.

A contemporaneous matrix cannot separate them. The lead can.

## Design

Every row is refitted with the counterparties' turnover at lag 1 and lag 2 **in the same
regression as their contemporaneous turnover**:

    dy_m[t] = a + b_own dlog(own_m[t]) + sum_j c_mj dlog(T_j[t]) + sum_j L_mj dlog(T_j[t-lag]) + e

Both directions are published (member rows against the star's past, and the star's own row
against everyone else's past). Verdict is a pure function of the published counts
(`derive_verdict`), recomputed by a smoke leg.

**The draft that had to be thrown away**: putting ONLY lagged counterparties in the row (no
contemporaneous block) is not a lead test. On a persistent sleeve the lagged turnover is
0.87-correlated with the present one, and the lone lag coefficient re-reads the present column:
a fixture whose true lead was 0.00 came back at **0.51**. Partialling the past against the
present is what makes the number a lead.

## Answer

Headline cell (five members, 1,328 sessions, resolution 0.264):

| lag | decisive share | mean slope |
|---|---|---|
| 0 (contemporaneous) | 5/5 | **+0.769** |
| 1 | 5/5 | **-0.527** |
| 2 | 5/5 | **+0.397** |
| reverse (star's own row vs everyone's past) | 0/4 | -0.059 |

Verdict `star_flow_leads_with_sign_flip`: the star's past turnover does predict the book, but
the lags disagree in sign, and the pattern is a decaying alternation (+0.77, -0.53, +0.40) --
the signature of an oscillation in a shared driver, **not** a one-way flow that sleeve's
turnover can be billed for.

Ruling on the card's question: **neither (a) nor (b) as stated.** It is not "a common factor
with no dynamics" -- the past matters -- and it is not a monotone flow either. The star is a
common driver read best on one sleeve, with a two-session bounce.

Across cells the face is honestly mixed: `contemporaneous_common_factor` in the pre-2020 four
(lag1 -0.117 at 0/4 decisive, i.e. nothing leads once sh588000 is absent), sign flip in the
five-member window, and four cells unresolved (half-widths 0.42..0.51 against the 0.30 bound).
The rollup refuses to average these.

## Validity checks run before publishing

* **Placebo band**: the star's turnover series permuted in time gives a lag-1 slope of **-0.019
  (se 0.106)** in the star's own row and **-0.060 (se 0.123)** in sh510300's row, while the real
  readings are -0.012..-0.18 and -0.662. The design does not manufacture the alternation.
* **Own-lag persistence disclosed per member**: AR(1) of dlog turnover is **-0.33..-0.44**
  (t -11.9..-16.7) for all five sleeves, which is why the sign alternation inside the row was
  the first suspect -- the face publishes this so the reader sees the collinearity that the
  contemporaneous block has to absorb.
* **Lag 0 is bit-identical to E245's row fit** (selftest leg, max diff 0.00e+00), so the
  contemporaneous number is re-used, not re-estimated.
* Fixtures: lead magnitude recovered (0.608 against a 0.6 truth), lead-only / contemporaneous-
  only / both / none / reverse all classify correctly, too few sessions stays undecided.

## Traps

1. **A lag column without its contemporaneous twin is a proxy.** See 0.51 above. Any "does X
   lead Y" design in this family must carry both blocks in one regression.
2. **A decisive NEGATIVE lead is still a lead.** The first verdict gate required a positive mean
   and would have discarded this face's largest coefficient (-0.527) -- the sign is a finding
   (`star_flow_leads_inverse`), not a disqualifier.
3. **Fixture levels must accumulate.** E245's fixture appends the increment into the `y` slot, so
   its `dy` is the difference of two increments; with a lead term that reads as a sign flip
   (-0.584 for a +0.6 truth). The `y` slot is a LEVEL in the real panel, so the fixture has to
   cumsum or every lag design measures the wrong object.
4. **The one-line answer must handle the mixed rollup.** E245's `_answer` had no branch for
   `verdict_mixed_across_cells` and printed "no direction resolved in any counted cell (6
   counted)" next to a rollup that had just counted six cells; the smoke leg now fails when the
   one-line contradicts the rollup.

## Next

Pool card `E247-OSCILLATION-OR-COEFFICIENT-BAND`: extend the row to lags 1..5, publish a
200-draw permutation band per lag, and separate "period-2 oscillation" from "monotone decay"
before anything is named a channel.