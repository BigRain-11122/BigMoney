# DIGEST 2026-10-31 r1303 -- E278: is a zero-spread tail a hole in the ruler, or one bad group?

**Round** r1303 · **machine** bm-b · **dept** research + engineering · **cutoff** 2026-10-29
**Face** `results/state_tilt/BANDSPREADFLOOR-2026-10-29.json` · **Runner** `scripts/e278_spread_floor.py`
(selftest 13/13, verify 0 problems) · **Card** `knowledge/METHODOLOGY_ASSETS.md` E279

## The question

E272 put both flip-budget tails on one ruler: `normalised_gap = gap_pct / that tail's spread`, inside
the row's (leg, base-count) group. `cross:200` publishes `p05 = 1.0000` on all four windows, so its
tight spread is exactly 0 and two rows could not be normalised. One group can be bad luck. If zeros
cluster by base count (a thin shuffle across few base counts collapses the percentile), the ruler
needs a published minimum-spread policy instead of per-row notes. No new draws: every number is a
function of the published faces.

## The measurement

16 arm rows in `BANDWINDIST-2026-10-29.json` -> **4 (leg, base) groups x 4 cells**, each group read at
both tails:

| group | tight values (p05) | tight spread | wide spread |
|---|---|---|---|
| cross:60 | 1.1008 / 1.0438 / 1.0000 / 1.0961 | 10.08% | 16.73% |
| **cross:200** | **1.0000 / 1.0000 / 1.0000 / 1.0000** | **0.00%** | 16.79% |
| self:60 | 1.1065 / 1.0667 / 1.0095 / 1.0932 | 9.60% | 9.51% |
| self:200 | 1.0688 / 1.0000 / 1.0000 / 1.0000 | 6.88% | 9.08% |

- **One zero spread in eight group-tails: cross:200 tight, and all four of its cells sit on the 1.0
  floor.**
- **8 of 16 published tight values are exactly 1.0, and 7 of those 8 are at base 200** (base 60
  contributes 1). The floor hits — not the group — are what cluster.
- The wide tail never degenerates: 0 zeros, smallest spread 9.08%, largest 16.79%.
- No group degenerates at both tails.

## Verdict

`the_zero_spread_tail_is_the_band_floor_landing_on_the_thin_shuffle`

The zero is E277's build property (lo is the minimum of a nested draw prefix, so a multiplier can
never fall below 1) showing up where the percentile has least support: at base 200 the four windows
collapse onto the floor together, at base 60 they never do. It is not one unlucky group — but it is
also not "the ruler is broken": three of four groups divide cleanly, and the wide side always does.

**Consequence for the published face:** `minimum_spread_policy` — a group whose tail spread is
exactly 0 is flagged; a row in it stays **unmeasured**, never given a default (other tail, pooled
spread, or 1.0). A group flagged on *both* tails has no usable ruler at all. 2 published E272 rows
(cross / all_five index 1 and 12) are stranded on that tail and stay unmeasured.

## Checks that ran

- `identity_check`: **8 group-tail spreads re-derived from the arms and matched against E272's
  published per-row `spread_pct`, 0 mismatches** — the census is the same quantity, not a lookalike.
- `affected_rows`: both stranded rows carry `normalised_gap = null` on the face itself; the join
  proves the policy flags nothing else.
- Selftest legs L1-L12: floor group / identical-not-at-floor / single-cell / spread arithmetic /
  healthy group / conflicting duplicate values / by-base aggregation / both-tail flag (both
  directions) / real census shape / identity to E272 / policy coverage / stranded rows unmeasurable.

## Pits caught before publish

1. A group with ONE published cell has `min == max` by construction, so a naive `spread == 0` test
   calls it a zero spread and counts "nothing to compare" as evidence of a hole. Leg L3 failed on the
   first cut; the class is now explicit (`single_cell_group`, never `zero_spread`).
2. One cell publishing two different values must poison the group (`conflicting_cell_values`) rather
   than silently taking one of them — otherwise the ruler rests on an arbitrary duplicate.

## Product

- `scripts/e278_spread_floor.py` (run / verify / selftest)
- `results/state_tilt/BANDSPREADFLOOR-2026-10-29.json` + `bandspreadfloor_latest.json`
- `knowledge/METHODOLOGY_ASSETS.md` card E279
- `Tools/s6_chain_bmb.py` leg `spread_floor`
- `smoke_test.py` leg `the one zero-spread tail is the band floor at the thin shuffle`