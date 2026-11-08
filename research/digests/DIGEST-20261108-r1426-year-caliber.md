# DIGEST-20261108-r1426 — a gate that cannot judge itself was the only reason the book was refused

## What was wrong

r1418 refused the desk's adopted book (nobond_vt08) on exactly one row: Y4 top-2 year
share = 71.08% of the annual net sum, 1.08pp over the 70% line. r1419 moved only the
decision-grid start and the same number swung 71.08 → 79.82%. r1421 showed why: a top-2
share of a NET sum is an annual Sharpe in costume, and its denominator can pass through
zero. r1425 priced the cap that the attribution pointed at and found 3 of its 4 arms
UNADJUDICABLE_PHASE — phase spread wider than the distance to the line — and left the
pointer: replace Y4 with an explicit caliber, and prove on the phase set that the caliber
can adjudicate itself before trusting it.

This round is that proof. Four calibers, one 20-cell grid (the same 4 arms × the frozen
5 weekly starts r1425 published), three tests frozen before the read:

* **V** the denominator cannot vanish (structural)
* **S** it can adjudicate itself — every arm unanimous across phases, and
  `max-min <= |median - line|`
* **D** it resolves this book against an EVEN book (`2/n` for shares, `n` for effective
  years, `ceil(n/2)` for half-years) at a resolution finer than its own phase spread

## Live readings (production arm, 20 cells)

| caliber | per-arm state | median plain / cap≤1 / cap≤2 / both |
|---|---|---|
| `net_top2_share` (control, Y4) | plain FAIL, cap≤1 and cap≤2 **cannot judge**, both FAIL | 79.58 / 84.81 / 76.91 / 84.90 % |
| `gross_top2_share` | plain **cannot judge**, cap≤1 PASS, cap≤2 cannot judge, both PASS | 63.96 / 57.24 / 59.48 / 57.53 % |
| `effective_years` | **PASS on all four arms** | 4.98 / 5.09 / 4.97 / 5.25 of 7 |
| `years_for_half` | **FAIL on all four arms** | 2 / 1 / 1 / 1 |

Trusted set = {`effective_years`, `years_for_half`}; primary = `effective_years`;
composite verdict = **FAIL** (worst word; rulers are never averaged).

So the book is *broad* (five effective years) **and** *front-loaded* (half its return from
one to two years). Both readings are true; only the failing half is actionable, and
averaging them would delete the only action.

## A self-catch worth keeping

D's first form asked whether a caliber separates the **arms**. No caliber passed it. On
review the test was wrong, not the instruments: four genuinely equal books cannot be
separated by any ruler, and that is r1425's cap finding arriving on a third axis (the caps
are concentration-neutral). D was replaced by the even-book resolution test and the arm
reading was demoted to an informational field (`D_arms`,
`arm_separation_is_informational`). The revision happened **after** the first run, so both
versions and the reason are published in the receipt's `rule_revision` block.

## What changed

* `scripts/etf_book_year_caliber.py` (selftest 33/33, `check` PASS): four calibers, the
  three tests, the frozen decision, two identity legs (cap-free arm reproduces nobond_vt08
  bit-for-bit; the 20 cells reproduce r1425's published `top2_share` max|d| = 0.0).
* `results/etf_book_year_caliber.json` — every cell's year-by-year net return, so a reader
  can recompute any caliber without repricing.
* `research/ETF_BOOK_YEAR_CALIBER.md`, card E433.
* S6 leg `year_caliber` (check form, JSON read only); two smoke legs.
* **No production file changed.** A caliber change is an admission-rule change and needs
  its own adoption round; `candidate_year_gate.py` keeps Y1..Y4 exactly as they are.

## Next

The lever is front-loading, not the cap: capping a sleeve was already shown neutral on
concentration (r1425) and this round shows the four cap arms are indistinguishable on every
caliber measured here. Either accept the front-loaded shape and size the capital to it, or
change the instrument/rebalance block — not another sleeve cap.