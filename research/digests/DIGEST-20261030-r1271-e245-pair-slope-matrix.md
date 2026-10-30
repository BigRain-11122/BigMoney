# DIGEST 2026-10-30 r1271 bm-b -- E245: the "rest channel" is a star (Methodology card E245)

**Question.** E244 attributed the spread across ordered pairs to counterparty identity, but every
number it read came out of a SUM regressor: `rest` is one member against an average of the other
k-2, so twenty pairs report a quantity no single counterparty produces. What does the un-summed
object say?

**Design.** `dy_m = a + b_own * dlog(turnover_m) + sum_{j != m} b_mj * dlog(turnover_j) + e`,
fitted jointly per row with Newey-West HAC (lag from `e225.NW_LAG`), on the common grid per cell.
Published per cell: the k x (k-1) matrix with intervals, a Wald test of row equality (one coherent
rest channel), column concentration (one counterparty), the matrix analogue of E243's difference
(b_mj minus the row mean), and the resolution the matrix carries (median CI half-width).
Six cells: all_five, pre2020_four, three eras, early_three.

**Answer.** In the five-member window (1,328 sessions, median half-width 0.264) the rows reject
equality in 4 of 5 and ONE column carries it:

| counterparty | decisive / members | mean slope |
|---|---|---|
| sh588000 | 4 / 4 | +0.769 |
| sh510300 | 2 / 4 | +0.258 |
| sh510050 | 1 / 4 | -0.078 |
| sh510500 | 1 / 4 | +0.051 |
| sh512100 | 0 / 4 | +0.060 |

The same star repeats in the era cells (0.903 in 2023-24, 0.904 in 2025-now, 0.563 in 2020-22) but
those cells do not resolve (half-widths 0.424 / 0.505 / 0.434 against the frozen 0.30 bound), and
pre-2020 -- before sh588000 prints -- there is no star at all: the four columns read
0.363 / 0.427 / 0.326 / -0.006 with rows rejecting equality, i.e. diffuse.

**Why it matters.** E244 published two carriers, sh588000 (+0.800) and sh512100 (-0.498). The matrix
shows sh512100's column is decisive 0/4 at slope 0.060 in the headline cell: the negative reading is
the mirror of the deviant, cast because the deviant sits INSIDE the sum sh512100 is priced against.
One sleeve, three roles, two signs -- not two channels. Rollup verdict is
`verdict_mixed_across_cells` and is published as such rather than averaged.

**Traps (all caught in-window).**
1. A fixture keyed by ints against panels keyed "S0".."S4" leaves every cross term at 0.0: the
   homogeneous leg passed on an EMPTY panel. Fixed by normalising keys and adding an activity
   assertion (mean cross slope == truth +/- 0.05). r1261/E199 family.
2. "Decisive column" is not "star": with a real effect everywhere every column is decisive, so the
   star needs a ratio to the median column (frozen 2.0). First run of the homogeneous fixture
   returned `counterparty_concentration` for a book with one uniform 0.15 effect.
3. An empty intersection reports zero sessions: the pre-2020 cell was built from all five members
   and published 0 sessions. Cells now name the members they may use.
4. Verdict ordering: a star makes its rows unequal, so checking row equality first buried the star
   under `heterogeneous_rows`; the specific reading now wins.

**Artifacts.** `scripts/e245_pair_slope_matrix.py` (run / selftest 10/10),
`results/state_tilt/SLOPEMATRIX-2026-10-29.json` + `slopematrix_latest.json`,
`Tools/s6_chain_bmb.py` leg `pair_slope_matrix`, `smoke_test.py` leg (re-derives the face's claims
from the face's own frozen spec), `knowledge/METHODOLOGY_ASSETS.md` card E245.

**Next (E246, seeded).** A star can be one sleeve's flow or a common factor read best through that
sleeve. The design that separates them is the lead: lag the star's turnover one and two sessions and
run the reverse direction. If nothing leads anything, the star is a contemporaneous common factor
and must be published as one.