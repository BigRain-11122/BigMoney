# E107 — does a split inside an UNCHANGED holding reach the book's own curve?

Face: `results/e44_midmonth/HELDCURVE-20261026.json` (+ `HELDCURVE-latest.json`), repair_factor `a78d23e15b45`, evidence_cutoff 2026-10-26.
Leg: `scripts/e107_heldcurve.py` (selftest 20/20). Pool row `E107-UNCHANGED-HOLDING-CURVE-EFFECT`.

## The measurement

E104 showed the read on names the book kept through a window (they enter no swap
list, so an entrant/exit decomposition cannot see them). E107 prices those same
windows on the book's own curve. Three curves per era-book cell, all built from
the SAME decision timeline E104 measured:

| curve | holdings | prices |
|---|---|---|
| unscreened | unscreened arm | unscreened |
| repair | repair arm | repair |
| hybrid | repair arm | repair, except persistent names' session **returns** are the unscreened ones inside that window |

* `curve_delta_bp` = repair − unscreened. It pays for **selection + read + cost**.
* `read_effect_bp` = hybrid − repair = the **cost of undoing** the repair on the persistent names.
* `read_attribution_bp` = −`read_effect_bp` = the part of the arm gap the **read** supplies.
* `selection_effect_bp` = curve_delta + read_effect = what the swapped names did.

## Readings

| era | book | arm gap | read supplies | selection supplies | verdict |
|---|---|---|---|---|---|
| 2017_2020 | me / mid | 0.00 | 0.00 | 0.00 | no read, no gap |
| 2021_2023 | me | +0.51 | −0.32 | +0.83 | read opposes |
| 2021_2023 | mid | +1.02 | −1.04 | +2.06 | read opposes |
| 2024_now | me | +2.31 | **+2.31** | **0.00** | read explains the whole gap |
| 2024_now | mid | +2.09 | −2.79 | +4.89 | read opposes |

Largest single windows of read: −71.17bp (2024_now me, 2024-08-30, 705 persistent
names) and +55.37bp (2021_2023 mid, 2021-01-15, 175 names).

The read does reach the curve (5 of 6 cells non-zero), and it reaches drawdown
too: 2024_now me worst drawdown is 19.52% unscreened vs 18.79% repaired.

## Two things a reader must not mis-take

1. **The two "deltas" are not the same quantity.** The arm gap is what the screen
   bought overall; the read attribution is what the *price read alone* supplies.
   In four of six cells the read and the selection work in OPPOSITE directions —
   so quoting the arm gap as "the repair's effect" is wrong in those cells.
2. **The book is a near-universe book.** Persistent names carry 99.4–99.7% of it
   in every era (breadth 108 → 845 names, pick_n 9999), so the swapped names are
   0.3–0.6% of the capital and every bp of "selection" comes out of that sliver.
   The decomposition is still exact (identity control residual 0.0), but selection
   is structurally capped here: this leg scores the *read*, not the screen.

## Instrument notes

* Decisions are filled at the decision session's close and earn idx → idx+1, the
  same holding period E104 measures. `e27.simulate` books the same decision one
  session later, so this curve's LEVEL is not comparable to a published era
  curve; only deltas between the three arms are published here.
* The hybrid rewrites **returns**, never levels: splicing unscreened levels into
  a repair series would inject a jump at every window edge exactly the size of
  the read being measured.
* Identity control: substituting a series for itself must leave the curve
  bit-identical — published per cell, max residual 0.0 on all six.
* Descriptive only: no gate, no verdict on any strategy, zero ledger, no re-burn.