# E288 (r1317) -- the mirror of the ceiling question: a below-floor flip needs the band NARROWED

**Face** `results/state_tilt/BANDFLOORMIRROR-2026-10-29.json` (+ `bandfloormirror_latest.json`)
**Runner** `scripts/e288_below_floor_narrowing.py` (run / verify / selftest 19/19)
**Chain** `Tools/s6_chain_bmb.py` leg `below_floor_narrowing` (verify, rc=0, 0.14s)
**Smoke** one new leg, extracted verbatim and executed standalone -> PASS
**Card** `knowledge/METHODOLOGY_ASSETS.md` E296
**Verdict** `no_published_narrowing_instrument_reaches_a_below_floor_row`

## What was asked

E285 partitioned the family's twelve flips into reachable / in-gap / above-ceiling / below-floor.
E287 then closed the widening half (no published band-edge supply reaches a row above the ceiling)
and explicitly left the below-floor class to the card it belonged on, because a multiplier below
1.0 is not a wider band -- it is a tighter one. This face answers that half.

## What it measured (published records only, no draw, no rebuild)

| row | flip | under the floor | short of 0.9220216 | E285 reference implied |
|---|---|---|---|---|
| `self|60|8` | 0.889387 | 11.06 pct | **3.67 pct** | 1.0283 (above the floor) |
| `self|60|10` | 0.630394 | 36.96 pct | 46.26 pct | 1.5815 (above the floor) |

- The only sub-1.0 band-edge multiplier the family publishes is BANDFLOOR's counterfactual 5 pct
  band (0.9220216). E287's other ten "narrow" readings are per-seed minima of a WIDENING ratio and
  every one of them sits above 1.0, so they cannot be used as a narrowing supply.
- **It reaches neither row**, so "unreachable" now has two directions in the family's vocabulary
  and neither is closed by anything published.
- **Cost.** The same instrument, scored against all twelve rows on each row's own polarity, reaches
  0 of 12 (a row needs a multiplier at or above its flip on the widening side and at or below it on
  the narrowing side). Tightening is therefore not a free fix for the floor class: it gives up
  every widening row.
- **Defect class, disclosed not repaired.** E285's `distance_below_tight_lo_pct` is a narrowing
  demand gauged with a widening reference (implied 1.0283 / 1.5815, both above 1.0). The source
  face is not rewritten here; this face publishes the implied reference beside every row so the
  column cannot be quoted as a distance to the floor.

## Limits

Published faces only: the question answered is "does anything already measured close these
margins", never "would a tighter percentile band work" (that is a new draw and a separate bill).
`partition_identity` re-derives the polarity class from flip vs the two published bounds for 12 of
12 rows; the source face's finer split of the middle band (in_gap / reachable_tight /
reachable_wide) depends on the published intervals and is deliberately not re-derived here.

## Pits (in-window)

1. My first cost rule read "a widening row is reached" unconditionally -- the polarity test has to
   be direction-aware or the cost block certifies everything. Caught by selftest L8, not on the face.
2. The E285 reference figure in selftest L6 was hand-computed and wrong by 1.6e-5; the leg now
   derives it from the same expression the runner uses.
3. The polarity re-derivation first collapsed the source's four classes onto three and compared
   them literally (8 of 12 "mismatches"): the middle band's split is not a restatement of flip, so
   the identity is published over the three polarity classes with the published class list shown.
