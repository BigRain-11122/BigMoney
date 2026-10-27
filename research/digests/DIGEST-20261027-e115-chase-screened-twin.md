# E115 — the chase leg on the screened arm: membership is arm-free, forward returns are not

Face: `results/e44_midmonth/CHASESCREEN-20261026.json` (arms beside it as
`CHASE-arm-raw-20261026.json` / `CHASE-arm-neutralise_int-20261026.json`),
evidence_cutoff 2026-10-26. Leg: `scripts/e39_panel_census.py chasescreen`
(selftest 348 → **353/353**). Pool row `E115-CHASE-SCREENED-TWIN`.

## Why this leg exists

E97 ranks the four uncovered runners by published numbers; E112/E113/E114 closed
rows 1–3 (burn-in, cut sweep, era split). Row 4 is `run_chase` (377 numbers, one
runner), which asks a different question than the burn-in: not "how much does the
book earn" but **which names each calendar is chasing**. Its load-bearing reading
is a digital count — of the mid-month book's entrants, how many sit in the
month-end book's next drop set — so it is the one leg where a repaired print
could plausibly move a *count* and not just a level.

Cost: `raw=` seam on `run_chase` (the E113 pattern), one harvest, one burn. Both
arms re-derive at start 2020-01-01, mid_day=15, cost-free descriptive returns;
screen = `neutralise_int`, 67 prints on 67 of 1,317 names, names in = names out
(no `gapped_eligible`, so no name is dropped by the arm).

## The measurement

95 joined cells (per-era bucket shares/returns/counts for both calendars, the
calendar's own entrant counts, the universe size) + the same-arm control.

| reading | repair (arm) | refresh (cutoff) |
|---|---|---|
| bucket `share_pct` (membership) | **0 of 10 moved** | 2 of 10 moved (±0.45 pp) |
| bucket `entrants` / `priced` | 0 of 8 moved | 3 of 8 moved (+6 each) |
| bucket `fwd_pct_mean` / `negative_share_pct` | **5 of 20 moved** (max 0.166 pp) | 4 of 20 moved (max −0.60 pp) |
| entrant counts / universe size | **0 of 4 moved** | 4 of 4 moved (+6) |
| cells total | 5 of 95 | 16 of 95 |

### 1. The repair does not reorder the chase — it re-prices it

Every entrant count, every bucket share and the universe size are byte-identical
between arms. That is stronger than "small delta": the decision sets do not move
at all, so the mid-month book trades the same names off a repaired panel. What
moves is what those names then earned:

| newest era | raw | screened | Δ |
|---|---|---|---|
| `me` → `other_still_holds` fwd | 0.880 % | 1.046 % | **+0.166** |
| `mid15` → `disjoint` fwd | 0.672 % | 0.814 % | **+0.142** |
| `me` → `other_still_holds` negative share | 45.2 % | 44.9 % | −0.3 |

So the answer to E97's routing question is narrow and usable: **quote the bucket
shares without an arm; quote the bucket returns with one.** On the raw panel the
newest era's `other_still_holds` bucket reads 16.6bp per transition and the
`disjoint` bucket 14.2bp higher than they do on the screened arm — the same
direction E114 found, where the raw arm made the losing half look worse.

### 2. The refresh axis moves exactly the numbers the repair leaves alone

The cutoff control (`CHASE-20261020` raw vs today's raw, arm held fixed) moves 16
of 95 cells, and its worst cell is `entrant_slots` +6 with `universe_members`
1265 → 1271. The screen adds no bars; four sessions of new bars add six names to
the universe, which lifts every count and nudges every share.

| axis | moves counts | moves returns |
|---|---|---|
| repair (`neutralise_int`) | **no** | yes, ≤0.17 pp |
| refresh (+4 sessions) | **yes** (+6) | yes, ≤0.60 pp |

That is the opposite decomposition from the burn-in (E112: the gate columns were
stable, the return columns moved) and it is why the twin is worth running per
leg rather than assuming one face's stability classes transfer to another's.

## Three controls, all published

| control | isolates | result |
|---|---|---|
| identity (raw vs raw) | join machinery | 0 of 95 cells, max Δ 0.0 |
| coverage | is the twin a twin? | 95 compared, 0 one-sided, 0 null |
| cutoff (`CHASE-20261020` raw vs today raw) | panel refresh | 16 of 95, max Δ 6 (a count) |

## The blind spot this ticket also closed

E97's coverage test reads a **hand-maintained registry** (`TWIN_FUNCS`), not the
code graph it advertises. The E112–E115 twins were written without being
registered, so the routing table called `run_burnin`, `run_cutcurve`,
`run_livespan` and `run_chase` uncovered while a screened twin for each sat on
disk. Registering the four twins moves the table to:

| | before | after |
|---|---|---|
| covered_by_twin | 3 | **11** |
| uncovered modes | 21 | **13** |
| uncovered distinct runners | 14 | **10** |
| cells unchanged by any twin | 5282 | **1568** |

Lesson recorded on the row: *a twin that is not declared is not a twin as far as
the routing table is concerned* — the same "the law lives only in the receipt"
failure E97 was written to prevent, one level up.

## What this does not say

* Not a strategy verdict: descriptive census, no gate, no prereg, no trial count,
  no ledger booking.
* `fwd_pct` is the raw decision-to-decision return of the name, before weighting,
  cost or cash leg; a +0.166 pp move on an entrant bucket is not a book return.
* Bucket membership is decided on the *other* calendar's book, so an unchanged
  share means "the repair did not reorder the books", not "the panel is clean".
* One mid-month date against one month-end date; the calendars are fixed, not
  swept, exactly as in the raw leg.
* E97 counts 377 published numbers for this runner; 95 are joined here. The
  per-transition rows and the top10/bottom10 symbol lists are pointers, and
  joining a list would report one swap as a dozen moved numbers.