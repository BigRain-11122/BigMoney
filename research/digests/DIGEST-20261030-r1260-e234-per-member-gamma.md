# E234 -- the book holds five instruments, so its exponent is a mixture (r1260 bm-b)

Question (frozen before any number): E233 measured one charge exponent per panel
(sh510300 0.928 [0.830, 1.026]; equal-weight basket 0.917). The basket is five instruments
with different liquidity and history -- sh588000 only starts in 2020 -- so a book-level
exponent may be a summary of a spread charged to four sleeves that do not share it. (a) Is it
per member or a mixture? (b) Was the 2017+ ladder conclusion an artefact of borrowing the
full sample's exponent?

## Per member (estimator B = controlled, Newey-West lag 20, 95% intervals)

| member | gamma | 95% interval | n |
| --- | --- | --- | --- |
| sh510300 | 0.928 | [0.830, 1.026] | 3,455 |
| sh510050 | 0.760 | [0.674, 0.847] | -- |
| sh510500 | 0.416 | [0.306, 0.527] | -- |
| sh512100 | 0.414 | [0.332, 0.496] | -- |
| sh588000 | 1.456 | [1.310, 1.602] | -- |
| pooled (5 intercepts) | 0.622 | [0.567, 0.676] | 15,641 |

Eight of the ten member pairs have DISJOINT intervals; four of five members sit outside the
pooled interval (sh510300, sh510500, sh512100, sh588000). Verdict: **mixture** -- the single
exponent is a summary of a 0.414..1.456 spread, not a property of the book.

## What the mixture costs at the book (5,269 sessions, 2005-02-23..2026-10-29, 2,108 OOS)

cost_book(dw) = sum_i c*(|dw|/N)**gamma_i, which collapses to the linear bill only when every
gamma_i = 1 (selftest leg pins this, and that the per-member rows reproduce the family rows at
gamma = 1 to 1e-12).

| arm | weight changes | linear bill | same-granularity (pooled gamma) | per-member | split term | mixture term |
| --- | --- | --- | --- | --- | --- | --- |
| binary_low | 118 | 1,538.8 bp | 2,828.2 | 2,523.3 | +1,289.3 | -304.9 |
| tilt_step | 241 | 1,610.6 | 3,803.9 | 3,485.0 | +2,193.4 | -318.9 |
| tilt_linear | 997 | 1,706.0 | 5,720.5 | 6,009.8 | +4,014.5 | +289.2 |

The bill multiplies 1.6x..3.5x, but that is the SPLIT of one book move into five concave
charges, not the mixture. Granularity is a first-order design choice; the mixture is a
second-order correction that takes either sign.

## Family verdicts under the per-member charge

The toll clears its bar (3.26 over 15 cells) on 3 of 3 arms with |t| = 6.37 / 9.97 / 10.27
(linear charge: 6.37 / 10.03 / 10.05) and selection stays inside the bar (binary_low +1.32,
both tilt arms -0.34). OOS totals: binary_low pair +149.2 bp/yr of which selection +265.5,
sizing +83.1, toll -199.4; tilt_step -330.3 (selection -83.0, sizing +26.7, toll -274.0);
tilt_linear -501.4 (selection -84.7, sizing +49.0, toll -465.7). Identity residual 0.0 on
every arm. So the family conclusion is curvature- AND granularity-invariant in sign, and the
arm-level losses get deeper, not shallower.

E230's ladder under the two charges: only 2 of 6 cells change verdict -- both the 0.10 band
(binary_low and tilt_linear), i.e. exactly the band that already carried the family's single
passing cell.

## Era (b): was the 2017+ reading a borrowed exponent?

The 2017+ exponent measured on that slice is 0.883 [0.768, 0.998]; the full-sample interval
0.928 [0.830, 1.026] COVERS that point, and pre-2017 reads 1.079 [0.904, 1.255]. Re-deriving
the 2,383-session 2017+ ladder with the era's own exponent instead of the borrowed one changes
**0 of 6** verdicts (all BAND_NOISE both ways; levels move by at most 1.9..6.8 bp/yr). The
era gap is real in the point estimates but does not reach a verdict.

## Pits

1. A pooled fit that drops the lagged magnitude/volume controls is the naive estimator wearing
   the controlled one's name: the first version published 0.051 with "5 of 5 members outside
   the pooled interval", comparing a naive pooled slope against controlled member slopes.
   Caught before the face was written; the pooled specification now carries the same three
   regressors plus four member dummies, and a selftest leg asserts the regressor count.
2. The per-member bill alone reads as "the mixture moved the bill 1.0k..4.3k bp" when almost
   all of it is granularity. The same-granularity control is mandatory: without it the headline
   would be a statement about how many orders the book sends, not about the exponents.
3. A concave charge on a split move is dearer per unit (E232 pit restated): for gamma < 1,
   (|dw|/N)**gamma * N > |dw|, so five sleeve charges beat one book charge; the selftest pins
   both the inequality and the N-times identity so the effect cannot be silently re-signed.

## Pieces

- `scripts/e234_per_member_gamma.py` (run / selftest 14/14)
- `results/state_tilt/PER-MEMBER-GAMMA-2026-10-29.json` + `per_member_gamma_latest.json`
- `Tools/s6_chain_bmb.py` leg `per_member_gamma` after `empirical_gamma`
- smoke leg: per-member intervals contain their points, the pooled fit carries the member
  specification, a mixture verdict names its breakers, and the mixture term closes against the
  granularity control on every arm
- `knowledge/METHODOLOGY_ASSETS.md` card E234