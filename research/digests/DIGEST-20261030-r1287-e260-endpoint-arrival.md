# E260 — the published base draw count sits below the endpoint arrival count

*Round r1287 (bm-b), 2026-10-30. Face: `results/state_tilt/BANDARRIVAL-2026-10-29.json`.
Runner: `scripts/e260_band_endpoint_arrival.py` (selftest 21/21, verify OK). Pool card:
`E260-BAND-ENDPOINT-ARRIVAL`.*

## The question

E259 published 52 of 640 per-seed draw multipliers reading **exactly 1.0**. A multiplier of one is
not noise: the prefix-nested band endpoint cannot move again once the draw that set it has already
arrived inside the base prefix. That makes "how many draws" measurable — and it asks a harder
question than E259 did. E259 measured how wide the multiplier's own distribution is; this face
measures **where in the draw count the band stops moving at all**, and whether the count the family
actually publishes sits below it.

## The measurement

For every window and leg, each seed's band endpoint is read back at every count on E259's grid
(60, 120, 200, 480, 960, 1920). Because the streams are prefix-nested, a smaller count is literally
a prefix of the larger one, so the endpoint is non-decreasing and "arrival" is well defined: the
first count at which the seed's endpoint equals its own value at the top of the grid. No new draws,
no new estimation — the edge tables are E259's, unchanged.

## What it says

| quantity | value |
|---|---|
| median arrival across the 4 measured windows | **1440 draws** (min 960, max 1920) |
| published base counts in the family | 60 / 200 |
| seeds that reach their final endpoint only at the top (1920) | **174 of 320** |
| seeds already final at 60 draws | 12 of 320 |
| published rows read off a still-moving stream (`pre_settlement`) | **12 of 16** |
| published rows that had settled at their own base | **0 of 16** |
| rows whose window was never measured | 4 (pre2020_four, era_2020_2022) |
| non-monotone prefix steps | 0 of 320 seeds |

At the base count the family publishes, a median **95%** of seeds still had an endpoint that had
not reached its final value. Not one published row settles at its own base. And the floor is not
the seed stream: 174 of 320 seeds are still moving at the last grid point, so on the windows
measured here **the grid, not the sample, is the binding constraint** — a wider grid would move
these bands again.

## Reading it honestly

- This does **not** say the published bands are wrong. E257's face already established the band's
  endpoint is still rising at 1920 draws, and E259 established the consequences are inside the
  interval. What E260 adds is the count: an arrival distribution, not a yes/no.
- It does say the family's published band draw count is a **snapshot below settlement**. Any future
  claim of the form "this row is outside its band" carries a draw count that had not converged;
  E259's interval re-judging remains the correct way to read such a row.
- The four `window_not_measured` rows are named, not zeroed.

## The cross-check that failed first (and why it is now a leg)

The face's first draft pinned the degeneracy reproduction by summing `n_at_base` over the 16
**published rows**. It read 29 against E259's 52 and looked like a broken upstream. It was a broken
comparison: E259's 52 is the total over its 16 **distribution arms** (4 windows × 2 base counts ×
2 legs), and the published rows are a *different* 16 that carry their own base and leg. Same
family as the r1286 pit — a table read under a key coarser than the arm it claims to describe.

The pin is now per arm (`'cross:200'` → leg and base are both part of the arm), publishes all 16
arm rows with `n_at_base` beside `e259_published`, and reproduces **52/52 with 0 arms mismatched**.
A selftest leg pins that the row sum is *not* the arm total, so the short-cut cannot creep back.

## Wiring

- `Tools/s6_chain_bmb.py` leg `band_endpoint_arrival` → `verify` (<1 s).
- `smoke_test.py` leg *"the published base draw count sits below the endpoint arrival count"*:
  every arrival must be a grid point, the published median must equal the median of its own seeds
  (a grid point is not a median), the hist must sum to the judged seeds, every arm's count must
  re-derive from the arrival table, and the cross-check must match arm by arm.
- Method card: `knowledge/METHODOLOGY_ASSETS.md` E260.

## Next questions this opens (already seeded)

The 174 seeds at the top say the grid binds. That is measurable further: E261 (how much of each
interval width is the endpoint-attained bucket) and E262 (whether the wide end of one window
transfers to another) stay open; the arrival table now gives them a per-seed anchor to read from.