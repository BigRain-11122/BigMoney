# E97 - screened-consumer routing table

Date: 2026-10-27 | round r1176 | dept: research+engineering
Face: `results/e79/ROUTING-20261027.json` | Tool: `scripts/e97_routing.py` (selftest 14/14)

## What this answers

E94 named 25 census modes whose published numbers still come off a repaired print. E109 then fixed the repair factor on the 14 legs that join a screened arm themselves. What nobody had published is the routing question: for each charged mode, **is there a screened twin face on disk at all**, and if not, how much number surface does the untouched face carry?

Coverage is a **code-graph** fact (does a twin leg call this mode's runner, or build that face itself), not a column-name guess. The column test is measured and published, but it is explicitly non-decisive.

## Totals

| charged | covered by twin call | covered by twin body | uncovered | distinct runners | column-only collisions |
|---|---|---|---|---|---|
| 25 | 3 | 1 | 21 | 14 | 7 |

## The table

| mode | runner | screened twin | coverage | numbers carried |
|---|---|---|---|---|
| pair | run_pair | none | uncovered | 93 |
| cashdrag | run_cashdrag | none | uncovered | 70 |
| rebalday | run_rebalday | none | uncovered_column_only | 132 |
| e42 | run_spreadsize | screenspread | covered_twin | 47 |
| spreadsize | run_spreadsize | screenspread | covered_twin | 47 |
| tiltera | run_spreadsize | screenspread | covered_twin | 47 |
| e43 | run_tilt4 | none | uncovered_column_only | 91 |
| tilt4 | run_tilt4 | none | uncovered_column_only | 91 |
| widecomp | run_tilt4 | none | uncovered_column_only | 91 |
| burnin | run_burnin | none | uncovered | 1727 |
| e44 | run_burnin | none | uncovered | 1727 |
| knife | run_burnin | none | uncovered | 1727 |
| skinloo | run_burnin | none | uncovered | 1727 |
| e45 | run_warmspread | none | uncovered | 123 |
| warmspread | run_warmspread | none | uncovered | 123 |
| e46 | run_livespan | none | uncovered | 471 |
| livespan | run_livespan | none | uncovered | 471 |
| cutcurve | run_cutcurve | none | uncovered | 1139 |
| chase | run_chase | none | uncovered | 377 |
| entrydelay | run_entrydelay | none | uncovered_column_only | 223 |
| earlydelay | run_earlydelay | none | uncovered_column_only | 235 |
| neighborhood | run_neighborhood | none | uncovered_column_only | 139 |
| weeklyclash | run_weeklyclash | screenweek | covered_twin_by_name | 332 |
| staletail | run_staletail | none | uncovered | 228 |
| panelsplit | run_panelsplit | none | uncovered | 234 |

## Ranked: uncovered, by runner (one burn per runner)

| # | runner | numbers carried | modes sharing the face |
|---|---|---|---|
| 1 | run_burnin | 1727 | burnin, e44, knife, skinloo |
| 2 | run_cutcurve | 1139 | cutcurve |
| 3 | run_livespan | 471 | e46, livespan |
| 4 | run_chase | 377 | chase |
| 5 | run_earlydelay | 235 | earlydelay |
| 6 | run_panelsplit | 234 | panelsplit |
| 7 | run_staletail | 228 | staletail |
| 8 | run_entrydelay | 223 | entrydelay |
| 9 | run_neighborhood | 139 | neighborhood |
| 10 | run_rebalday | 132 | rebalday |
| 11 | run_warmspread | 123 | e45, warmspread |
| 12 | run_pair | 93 | pair |
| 13 | run_tilt4 | 91 | e43, tilt4, widecomp |
| 14 | run_cashdrag | 70 | cashdrag |

## What the numbers say

1. **The biggest untouched face is not a headline leg.** `run_burnin` carries 1727 numbers across burnin, e44, knife, skinloo - the largest single burn, 33% of the 5282 numbers the 14 uncovered runners carry together (one burn each, shared faces counted once).
2. **Only 3 of 25 charged modes have a twin that calls their runner**, and exactly one more is covered by a twin that builds the face in its own body. So E109's fixed-factor sweep did not reach the base faces: the corrected numbers live on twin faces, while the faces a reader opens are still the unscreened ones.
3. **A column-name test would have routed work to the wrong leg.** 7 rows match some twin at >=80% column overlap without any code link; generic metric names (`ann_return_pct`, `sharpe`, `max_drawdown_pct`) are why.

## Honest

- covered_twin means a screened twin face exists for the mode's runner; it does NOT mean the mode's own published face was re-derived, so the numbers a reader opens are still the unscreened ones until the face itself is re-burned
- covered_twin_by_name is the weaker of the two code channels: the twin builds the face in its own body instead of calling the base runner (run_screenweek borrows run_midsweep for decision sets only), so read it as 'the twin exists' and not as 'the same function burned it'
- the column-overlap channel is published because it was measured, not because it routes work: generic metric names (ann_return_pct/sharpe/max_drawdown_pct) make unrelated twins match a face at ratio 1.00
- published_cells counts numeric leaves in the mode's face; it measures how much number surface a re-burn would touch, not how much of it the repair would move (E94/E109 carry the move counts)
- modes sharing a runner share one burn, so the runner-level ranking is the actionable one; the mode-level ranking double-counts shared faces

## Verify

```
python scripts/e97_routing.py selftest      # 14/14
python scripts/e97_routing.py run --publish
python scripts/e97_routing.py run --md
```
