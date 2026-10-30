# DIGEST 2026-10-30 r1288 -- E261: how much of the band interval is the attained bucket

Study: `E261_degenerate_seeds_leave_one_bucket` · face `results/state_tilt/BANDBUCKET-2026-10-29.json`
Source: `BANDWINDIST-2026-10-29.json` (E259) only -- **no new draws, no refit, no re-pricing**

## The question E260 left open

E259 published 52 of 640 per-seed multipliers reading exactly 1.0 (the band's lower endpoint had
already arrived inside the base prefix, so it cannot move again) and those seeds dragged `p05` to
1.000 in 14 of its 16 arms. E259 named the degeneracy and moved on. The open question is what a
reader actually needs: **is the "the band can only widen" floor a property of the stream, or is it
the bucket?**

## What was measured

Every published interval was rebuilt twice from the same per-seed table:

| reading | sample |
|---|---|
| `full` | all 40 seeds (must equal E259 bit-for-bit -- it does, 16/16) |
| `trimmed` | the seeds whose endpoint is still free to move (bucket removed) |

Results on the 4 measured windows x 2 legs x 2 base counts:

- **8 of 16 arms carry a floor at exactly one, and all 8 leave it** once the bucket is removed.
  Median lift **+0.0734** (range +0.0327 .. +0.2005); the width shrinks by a median **10.4%** of
  itself (max 18.2%). So the floor is not the stream's lower bound -- it is the arrived endpoint.
- The floor is **not spread evenly across base counts**: 7 of 8 arms at base 200, 1 of 8 at base 60
  (`era_2023_2024 cross:60`, and that one carries the largest lift on the face, +0.2005 / -18.2%
  width). That is the direction E260's arrival result predicts -- more draws, more arrived endpoints.
- Median shift of the median multiplier when the bucket goes: **+0.0148**. The bucket sits at the
  bottom of the distribution, so removing it moves the interval's ends more than its middle.
- **No published row verdict changes because of the bucket** (0 of the 16 re-judged rows). The
  bucket changes widths, not verdicts.

Largest single lifts: `era_2023_2024 cross:60` +0.2005 (p05 1.0000 -> 1.2005, width -18.2%),
`all_five cross:200` +0.1100 (-16.2%), `era_2025_now self:200` +0.1001 (-16.4%).

## The caveat that is published on the face, not buried here

Removing the attained bucket is a **selection on the sample's own minimum**. The trimmed interval is
narrower by construction and it answers a different sentence than the full one:

- full interval = "where does the multiplier land"
- trimmed interval = "how far can it still move"

So the trimmed interval is **not a better band** and nothing may be billed against it. It is the
decomposition that says *which of the two sentences a published interval is actually making*. And
because it is narrower, "outside" becomes **easier** -- a row that reads outside only under the
trimmed interval is the direction of the edit, not a finding. The face publishes that direction
(`trimming.direction`) and this round's measurement found **0 such rows**.

## Second defect, surfaced by having to do this at all

E259's `rejudge_rows` reads the arm keyed `self:<base>` for **every** row. So the 4 `cross` rows and
the 4 `star_lag1_residual` rows -- whose published coefficient is the cross coefficient -- were
judged against the **self** interval. That is the same "a lookup keyed more coarsely than the arm it
claims to read silently returns another arm" pit E259 recorded against E258, recurring one level
down, in E259's own row table.

This face re-judges each row on the leg its own coefficient identifies (`star_lag1_residual` carries
no leg anywhere upstream, so it is resolved by `b` equality and published as *ambiguous* if both legs
share it -- 0 ambiguous here) and publishes both answers:

- 10 of 16 rows name/identify a leg other than `self` (8 of those carry a band and were judgeable);
- **1 of 16 verdicts moves**: `era_2023_2024 star_lag1_residual` was published as interval-dependent
  (`tight` outside / `wide` inside) and is **outside at every end on its own leg**, because the cross
  band's upper multiplier (2.0161) is narrower than the self band's (2.1748). The change is toward
  "outside", i.e. the easier direction when the band narrows -- it strengthens an existing outside
  verdict rather than overturning one.

## Defects in my own work this round

1. `floor_lifted` counted **16** arms as having moved a floor when only **8** have a floor: the flag
   tested "trimmed p05 > 1" instead of "had a floor and left it". Renamed to `floor_moved_off_one`
   with the conjunction, and a selftest leg now pins that an arm without a floor is never counted.
   (Name-is-semantics, E207/E208 family.)
2. A docstring in `floor_by_base` asserted "every floored arm sits at the larger base count" before
   the numbers existed; the face measured 7 of 8 at base 200 with one at base 60. The docstring now
   states the counts and notes the correction.
3. A first selftest fixture for "an arm without a floor" used two seeds at 1.0 out of ten, which
   *does* put `p05` at one. Rebuilt the fixture with a single attained seed.
4. The cross-tab selftest fixture had only 4 free seeds, so the arm was (correctly) excluded from the
   cross-tab and the leg failed on a missing key -- the exclusion is now its own pinned leg.

## How to apply

> before quoting "this band can only widen", publish the interval with and without the
> endpoint-attained bucket: if the floor moves, the floor was arrival, not the stream's bound.
> a selection on the sample's own minimum answers "how far can it move", never "where does it land";
> publish both and say which sentence which interval makes.
> a lookup keyed by (window, base count) alone silently reads the wrong leg -- key by every axis the
> claim names, and resolve leg-less rows by the coefficient they publish, publishing ambiguity.