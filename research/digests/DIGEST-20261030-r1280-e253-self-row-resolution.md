# E253 digest -- the star's self row is unmeasured after 2025: waiting state or weaker channel?

Round r1280 (bm-b), card E253-STAR-SELF-RESOLUTION. Runner `scripts/e253_self_row_resolution.py`
(selftest 16/16), face `results/state_tilt/SELFRES-2026-10-29.json` (latest twin
`selfres_latest.json`), evidence_cutoff 2026-10-29, source face
`results/state_tilt/STARSELF-2026-10-29.json` (E252).

## The question

E252 published one headline pair and one awkward cell. Headline (all five members, 1,328
sessions): b_self -0.7339 vs b_cross -0.7250, both outside their own shuffled bands. Then
era_2025_now (408 sessions): the star's self coefficient -0.463 sits INSIDE its own band
[-0.521, +0.451] while its cross column stays at -0.911, far outside [-0.415, +0.465].

Two sentences survive that face and E252 could not choose between them:

* the window is too short, and the row will speak once it has more sessions (a waiting state);
* the star's self channel genuinely weakened after 2025 (E246's prior is a sign flip by era).

## What this face does

No panel is read, nothing is refitted. The published face is turned into session counts, because
a shuffled band is the only thing in that design that defines what "measured" means: a coefficient
is measured iff |b| clears the edge its own shuffled column produces at that n. Band width shrinks
with the session count, so

    edge(n') = edge(n) * (n/n')**gamma        gamma = 0.5 frozen
    n'(b)    = n * (edge(n)/|b|)**(1/gamma)   sessions that coefficient needs

Three arithmetic readings and one distributional reading, each published separately:

| reading | what it answers |
|---|---|
| NEEDED | how many sessions the observed coefficient needs to clear its own band |
| FLOOR  | the smallest \|b\| that clears at the current n (the edge itself) |
| PRIOR  | how many sessions a channel of the previously published size would have needed |
| Z      | (b_prior - b_observed) / sd_null, sd_null read off the published full-draw-range band |

## The numbers (era_2025_now, n = 408, star sh588000)

* self b = **-0.4635**, its own band edge **-0.5211** -> margin **0.889**, i.e. **11.1% under
  the detectability floor** of its own cell.
* sessions that coefficient needs: **515.8** -> **107.8 more sessions**, calendar ETA
  **2027-04-23** at the cell's own density (0.6126 sessions/day over 666 days).
* cross column in the same cell: b = **-0.9113**, edge **-0.4149**, margin **2.20**, needed
  **84.6** sessions. The cross row had 4.8x the sessions it needed; the self row is the one
  waiting.
* prior channel: **era_2023_2024** self coefficient **-0.8027** (the last published cell that
  ended before era_2025_now began, so no overlap and no leakage). A channel of that size needed
  **172.0** sessions, and the window has 408 -- **the window was already long enough for the
  earlier size to have spoken**.
* Z against that prior: **1.70** using the band's own 60-draw sd (0.1999) and **1.98** reading
  the band as if it had 200 draws. Both sit under the frozen 2.0 line, so the shortfall is
  **not distinguishable** from noise -- but it is the closest call in the whole face.

Verdict: **self_row_resolves_with_more_sessions**. The honest sentence is "this row is not yet
measurable; re-read it at n >= 516", not "the channel weakened" -- and equally not "the channel is
still -0.80": both of those are claims the 408 sessions cannot carry.

## Other cells

* `all_five` (n=1,328): measured outside (needs 244 sessions).
* `era_2023_2024` (n=446): measured outside (needs 63).
* `early_three` (n=831, closed window): self b = -0.2035, edge -0.3227 -> needs **2,091**
  sessions. The window stopped accruing at 2016-11-03, so the silence **carries no information**:
  `silent_unreachable`, and no calendar is invented for it.
* `pre2020_four` and `era_2020_2022`: no member was named star in the window (`not_a_star_cell`).

## Four traps this face caught in itself (all fixed before publication)

1. **The prior must not overlap the cell it judges.** The first version took "the last clearing
   cell by end date" and picked `all_five` (-0.7339) -- a cell that *contains* era_2025_now. That
   is leakage: the prior would have carried the very sessions being measured. Requiring
   `prior.last < cell.first` gives era_2023_2024 (-0.8027).
2. **A calendar ETA is only meaningful for a window that still accrues.** `early_three` was
   handed an ETA of 2022-05-09 -- a date in the past -- before the fix; a closed window has no
   schedule, only a verdict.
3. **The band exponent must be checked, not assumed.** Fitting log|edge| on log(n) across the four
   published star cells gives gamma = **0.244** (r2 0.28, era heterogeneity), not 0.5. Under the
   fitted exponent the same coefficient needs **659.8** sessions (ETA ~2027-12). The sweep
   0.35/0.5/0.65 gives 570/516/489, so the deliverable is a **range**, not a date; the fit is
   published and never decides.
4. **sd from a full-draw range depends on the draw count.** E252 publishes min/max of the draws,
   not percentiles, and its era cells carry 60 draws while the headline carries 200. Reading the
   same band with the wrong draw count moves z from 1.70 to 1.98 -- across the 2.0 line's
   neighbourhood. The frozen rule therefore requires **both** z readings to clear the line before
   "weakened" may be called, so a coarse band cannot manufacture it.

## Frozen continuation rule (what the next round does)

Re-read the same cell when it reaches **n >= 516** sessions (guard: also >= 660 if the fitted
gamma is adopted):

* if |b_self| >= edge at that n -> the row is measured; compare it to the cross column;
* if |b_self| < edge at n >= 516 with z against -0.8027 still under 2 -> say so and extend;
* if |b_self| < edge at n >= 516 **and** z >= 2 -> `self_row_weakened_beyond_small_sample`, and
  that is a channel change, not a sample problem.

No bill, no adoption, no re-pricing: this face schedules a measurement, it does not make one.

## Wiring

* `Tools/s6_chain_bmb.py` leg `self_row_resolution` (verify mode, <1s) right after
  `star_self_price`.
* `smoke_test.py` leg "product: the star's unread self row is scheduled, not excused" -- pins the
  session count to the published band, the outside-band label, no ETA for a closed window, both z
  readings ordered, the verdict re-derived, and the no-refit declaration.
* method card E253 in `knowledge/METHODOLOGY_ASSETS.md`.