# E93 — does the gap-tolerant screen move the era SPREAD? (bm-a r1114, 2026-10-24)

**Answer: no. At gap_limit 1, 2 and 5 the published era spread is byte-identical
to the unscreened column in every era, and no era changes sign. What moves the
spread is the ADJACENT-ONLY arm, which E92's gap arm never touched.**

Deliverable: `results/e44_midmonth/SCREENGAPERA-20261023.json`
(evidence_cutoff 2026-10-23). Regenerate with
`python scripts/e39_panel_census.py screengapera` (`--gaps 1,2,5` default).

## The face

| era | unscreened | adjacent-only | neutralise_int | gap@1 | gap@2 | gap@5 |
|---|---|---|---|---|---|---|
| pre2017 | 236 | 236 | 236 | 236 | 236 | 236 |
| 2017_2020 | 419 | 446 | 419 | 419 | 419 | 419 |
| 2021_2023 | 243 | 379 | 289 | 289 | 289 | 289 |
| 2024_now | 100 | **475** | **300** | 300 | 300 | 300 |

(spread_ann_bp, ladder5 vs wide_topN, same face E76 published)

## What it means

1. **The gap-tolerant arm is empty on this face.** gap_limit 1, 2 and 5 produce
   the same spread in every era; raising the limit from 1 to 5 repairs exactly
   one extra event (75 -> 76) and moves nothing. The E92 conclusion ("levels
   move, the gap does not") now has its published-spread twin: the gap arm does
   not even move the level here. The 74 names the gap loader touches are not
   ladder or wide-headline members.
2. **The spread itself is screen-sensitive through the adjacent arm only.**
   2024_now sits at 100bp unscreened and 475bp adjacent-only — a 375bp swing on
   the number the chain publishes as an edge. 2021_2023 moves 243 -> 379.
   `neutralise_int` (integer-ratio adjacent prints only) sits between them at
   300 / 289, so roughly half of the adjacent correction is integer-ratio
   corporate actions and the rest is non-integer adjacent prints.
3. **Reading rule for downstream consumers:** quote an era spread with its arm.
   An unqualified "2024_now spread ~100bp" is the most fragile point on the
   face; the same era reads 300-475bp under repair. This is a description of
   sensitivity, not a correction — the honest list in the JSON says the
   corrected value is not a truth claim.

## Honest gaps

- Descriptive census: no gate, no verdict, no ledger booking, trial 0. Nothing
  here is a new claim; it is the already-published face re-read from a
  different input.
- The ladder windows (2018 / 2020 starts) are carried in `ladder_faces` for
  completeness but are not the subject of this leg.
- Prior files (`SCREENREG-*`, `SCREENGAP-*`) are untouched; this leg writes its
  own `SCREENGAPERA-*` file only.

## Provenance

E93 was the bm-b-owned ready pool entry `E93-GAPSPLIT-ERA-SPREAD`
(entered 2026-10-23T00:5x by bm-b r1158, deliverable exactly this file).
bm-b's heartbeat had been silent 31.8h at execution time, which makes the entry
un-ignitable under the r1100/r1101 gate; bm-a executed it under that takeover
condition. The takeover condition itself is now machine-readable: see the
`pool_ignitable` block in `results/compute_audit.json` (ready 3 / ignitable 0 /
takeover_candidate_ids 3 / silent_owners bm-b 1905min).

**Caveat discovered after the burn (disclosed, not hidden):** bm-b's heartbeat
was 31.8h stale, but its zt_pool panels were written 2026-10-24 03:38 and its
minute_feed files 2026-10-23 23:20 — i.e. heartbeat silence is NOT machine
death. The takeover gate as written (heartbeat >= 120min) was satisfied by the
letter and not by the spirit. No harm was done here: the deliverable file did
not exist before this run (untracked, zero prior content), so nothing was
overwritten and no duplicate burn of an existing result occurred — but the
right precondition would have been independent liveness evidence. The audit now
carries `takeover_needs_corroboration: true` and says so in
`corroboration_note`, and the flag is named `supply_owner_silent` rather than
claiming the owner is dead.