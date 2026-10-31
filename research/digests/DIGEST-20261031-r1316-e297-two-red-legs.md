# DIGEST 2026-10-31 r1316 (bm-b) - E297: two red smoke legs, and both reds were the check

**Task.** E297 as seeded by r1315: two smoke legs were red on published faces and both faces said so
themselves (E243's E240 replay MISMATCH at 5e-5 against a 1e-9 tolerance; E233's empirical-gamma
interval endpoint "absent from its own point set"). The card assumed two science defects. This round
measured both before touching anything, and neither was a science defect.

## Red 1 - a replay control that was not replayed

E243 (additivity out of sample) carries a *headline* cell whose job is to replay E240's published
numbers, and the smoke leg requires `e240_replay.reproduced is True` at tolerance 1e-9. It read
`MISMATCH` with gaps `mean_b_one 5.15453471209848e-05`, `mean_diff 2.645368706081022e-05`.

The cell was built with `_cell(per, allsyms, None, None, ...)` -- i.e. over the *live* panel. The
panel prints a new session every trading day:

| face | sessions | first | last | mean_b_one | mean_diff |
|---|---|---|---|---|---|
| E240 published (aggatt_latest.json) | 1328 | 2020-11-17 | 2026-10-29 | 0.18298467684299835 | 0.00785405388745896 |
| E243 all_five, unpinned (before) | 1329 | 2020-11-17 | 2026-10-30 | 0.18303622219011934 | 0.00782760020039815 |
| E243 all_five, pinned to E240's window (after) | 1328 | 2020-11-17 | 2026-10-29 | 0.18298467684299835 | 0.00785405388745896 |

With the pin, both generated gaps are exactly `0.0`. The 5e-5 "reproduction failure" was one extra
session of data -- the E292/E294 live-vintage family, one layer down: *the control cell is a panel
reader too*.

**Fix.** `_e240_ref` now publishes the reference's own `window {first,last,sessions}` read from the
E240 face's `book`; `run()` pins the headline cell to it and refuses a window that does not apply to
the panel under test (ends after the panel's last session, or keeps fewer than `MIN_SESSIONS`
sessions) with the reason published. `_replay` publishes `window_used`, `window_source`,
`live_panel_last`, `sessions_past_the_pinned_window` (=1 here) and a note saying those sessions are
excluded on purpose. Two selftest legs pin the behaviour: *replay survives a panel that grew* (a
300-session reference replayed against a 312-session panel must still reproduce, and the cell must
NOT grow) and *replay says when it had no window*.

The verdict did not move: the headline is `unresolved_heterogeneous_pairs` on either window, and the
roll-up is `additivity_only_in_the_mean` on 10 counted cells. Only the 5th decimal moved.

## Red 2 - a rounded copy compared at full precision

E233 publishes `summary.gamma_points = [0.829856, 0.927615, 1.025374, 0.253727]` (rounded to 6 dp by
`round(clip_gamma(...), 6)`) beside `gamma_interval = [0.8298563090732277, 1.0253741402202305]` (full
precision). The smoke leg asserted `lo - 1e-9 <= p <= hi + 1e-9` for the first three points. The low
endpoint differs from its own printed copy by 3.09e-7 -- seven orders above the tolerance -- so the
leg reported an absent endpoint when the endpoint was there, printed shorter.

**Fix, in the publisher, not the tolerance.** `GAMMA_POINT_DECIMALS = 6` is now a named constant, the
face publishes `gamma_points_decimals` and `gamma_points_sources`, and the leg (a) requires the
precision field rather than defaulting silently, (b) compares at one rounding unit (`10**-decimals`,
which still separates a genuinely absent endpoint by ~7 orders), and (c) requires the first three
sources to be NAMED `interval_lo` / `point` / `interval_hi` -- numerically inside the interval is a
weaker claim than being the endpoint.

## Verification

- `scripts/e243_additivity_out_of_sample.py selftest` -> **16/16** (14 before + 2 new legs)
- `scripts/e233_empirical_gamma.py selftest` -> **13/13**
- Both smoke legs extracted verbatim from `smoke_test.py` and executed standalone -> **PASS**
  (`.codely-cli/tmp_run_leg.py`, an exec harness, so the copy cannot drift from the registered leg)
- Faces regenerated: `results/state_tilt/addos_latest.json` (`e240_replay.status = reproduced`,
  gaps 0.0), `results/state_tilt/empirical_gamma_latest.json` (gamma 0.928 [0.830, 1.025], 12/12
  ladder cells stable inside the interval, 2 decided by the identification span)

## Reusable

1. A control/replay cell must be pinned to the reference's declared window and disclose the readings
   it excluded. An unpinned re-derivation turns a data vintage into a false reproduction failure, and
   a false failure is expensive in the worst direction: the cheapest "fix" on offer is to relax the
   tolerance.
2. A comparison tolerance is a claim about the printed resolution. Full-precision tolerances on
   rounded publications manufacture reds; the repair belongs in the publisher (declare precision and
   provenance), never in a blanket tolerance bump.
3. Both reds were "the face says so itself" -- E243 literally printed `MISMATCH` with the gaps, E233
   printed both numbers one line apart. Reading the two published numbers side by side was enough to
   classify both before editing anything (the r1281/r1315 shape: measure the claim, don't trust the
   red).

Methodology card: E295. Pool: E297 done, E298/E299 seeded (the census of the other replay controls
and of the other rounded-vs-full-precision legs).