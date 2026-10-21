# DIGEST 2026-10-22 - E76 panel-screen regrade (measure the correction)

Leg: `screenreg` in `scripts/e39_panel_census.py` (selftest 151/151).
Loader: `scripts/panel_screen.py` (opt-in; selftest 17/17). Every other leg still reads `e27.load_universe()` unmodified.
Face: `results/e44_midmonth/SCREENREG-20261021.json` (evidence_cutoff 2026-10-21).

## What E75 left open

E75 sized the problem: 135 adjacent-session prints past the 30% screen on 1,265 names, ~216bp/yr of
equal-weight book impact, 4.8x the -45bp weekly-vs-monthly residual the chain had spent six rounds on.
It only *sized* it. The ladder and era-spread columns the chain quotes were still charging those prints.

## What this leg measures

The same two headline faces, replayed from a repaired universe, with the unscreened column kept
beside every screened one:

- **ladder5** (E39 columns) at the 2020-01-01 and 2018-01-01 starts, and
- **era spread** (E41: ladder5 vs wide_top9999 on the full calendar), four eras.

Three screen columns bound the correction:

| mode | what it does | names touched | events |
| --- | --- | --- | --- |
| `neutralise_int` | forward-adjust only integer-ratio adjacent prints | 65 | 65 |
| `neutralise` | forward-adjust every adjacent print | 129 | 135 |
| `drop` | remove the name entirely | 129 | 135 |

Gapped prints (33 in total, 5 names carry an adjacent print too) are never repaired: a resumption
after a suspension can be a real market print.

## Headline

The era spread is where the correction lives. Screened, the **newest era stops being the thin one**:

| era | unscreened bp | integer-only bp | all-adjacent bp | drop bp |
| --- | --- | --- | --- | --- |
| pre2017 | 236.0 | 236.0 | 236.0 | 219.0 |
| 2017_2020 | 419.0 | 419.0 | 446.0 | 443.0 |
| 2021_2023 | 243.0 | 289.0 | 379.0 | 314.0 |
| 2024_now | **103.0** | **303.0** | **479.0** | 78.0 |

Read the 2024_now row: unscreened the newest era looks 4.1x thinner than 2017_2020, which is the
reading the chain has been quoting. Repair only the integer-ratio prints and it is 303bp; repair every
adjacent print and it is 479bp -- i.e. **two thirds to all of the "spread collapses in the newest era"
reading is unadjusted corporate-action prints**, mostly -90% tails dragging the wide book's ann% down
(11.95% unscreened vs 15.71% neutralised in that era).

The ladder column moves **0.0 in every one of its seven columns at both starts**. That is not a bug and
not an absence of artefacts: both ladder5 corporate actions sit behind a suspension bar
(sh510500 2015-04-15 +248.55%, sh512100 2022-09-05 +176.27%, both `adjacent: false`), so the
adjacent-only screen deliberately leaves them. `answers.ladder_member_prints` publishes the pair so the
zero is explained rather than mysterious.

16 of 34 delta cells are non-zero. The widest single cell is the 2024_now spread (+376bp under
`neutralise`); the ratio path's max drawdown in that era also moves (-13.04% -> -10.95%), so the
"spread's own drawdown" reading is contaminated too.

## Honest boundaries

- The screen repairs arithmetic impossibility, not confirmed corporate actions. An ETF's daily limit is
  not the 10%/20% stock band, so a flagged ETF print may be genuine. `neutralise` is a sensitivity face,
  not a corrected truth; that is why three columns are published instead of one.
- `drop` changes the universe (n and eligibility), so its delta mixes the correction with a composition
  change. `neutralise` isolates the correction; `drop` bounds it from the other side.
- The repaired series is forward-adjusted at every event it finds; a name that needs a second adjustment
  after the first is handled (selftest leg), but no announcement feed confirms the factor.
- Gapped prints are out of scope by design, which is exactly why the ladder and pre2017 columns do not
  move. Any claim about those columns inherits that scope.
- Descriptive census only: no prereg, no gate, no verdict, no ledger booking, trial_count 0.

## Next

`E77-SCREENED-WIDE-ERA` (seeded into the pool): replay the wide-book era columns and the cost-x3 face
from the screened universe, so the correction is shown to survive costs and both start windows before
anyone quotes it.