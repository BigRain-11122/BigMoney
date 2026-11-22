# Is the bench console honest about its own cells?

Headline: **QUEUE_DRIFT** (11 cell(s), 6 drift(s)). Queue `research/BENCH-QUEUE.json`, updated 2026-11-23T04:30:00+08:00.

| id | status | delivered | script | result | page | verdict in JSON | verdict in status | drift |
|---|---|---|---|---|---|---|---|---|
| fut_trend | done | yes | ok | ok | ok | yes | yes | – |
| bond_curve | done | yes | ok | ok | ok | yes | yes | – |
| astock_lowvol | done | yes | ok | ok | ok | yes | yes | – |
| bond_defensive | done | yes | ok | ok | ok | yes | yes | – |
| revalidate | done | yes | ok | ok | not declared | yes | yes | – |
| idx_fut_basis_reuse | done | no | ok | ok | ok | yes | yes | PATH_MISSING |
| cb_dual_low_reuse | done | yes | ok | ok | ok | no (file exists) | yes | – |
| astock_resid_industry_reuse | done | yes | ok | ok | ok | yes | yes | – |
| basis_capacity | done | yes | ok | ok | ok | yes | no | – |
| basis_timing_size | done | yes | ok | ok | ok | yes | no | – |
| repo_ladder | pending | yes | ok | ok | ok | yes | no | DELIVERED_BUT_PENDING |

Drifts named:
* `PATH_MISSING` · idx_fut_basis_reuse
* `DELIVERED_BUT_PENDING` · repo_ladder
* `STATUS_ROW_MISSING` · basis_capacity
* `STATUS_ROW_MISSING` · basis_timing_size
* `STATUS_ROW_MISSING` · repo_ladder
* `STATUS_COUNT_WRONG` (printed 8, queue 11)

What this face does not claim: This face cannot know whether a published verdict is still true on today's bar; that is the revalidate cell's job. It also cannot know whether a cell was declared with the right question -- only whether the console agrees with the files next to it.

Generated 2026-11-23T06:08:59+08:00 by `scripts/bench_queue_truth.py`.
