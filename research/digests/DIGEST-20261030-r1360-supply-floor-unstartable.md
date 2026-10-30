# r1360 bm-c — the supply floor was green over work that could not start

**Date** 2026-10-30 · **Round** 1360 · **Machine** bm-c · **Dept** 工程/舰队(算力面)

## What the ceiling said this morning

`results/watermark_red.json` (13:57) — `red: true`, lane
`pool-batch-runnable-idle-low-cpu`, `py_series_tail: [5.3, 0.1, 0.2]`,
`pool_ready_ids: [E243-ADDITIVITY-OUT-OF-SAMPLE, E272-ATLAS-COST0, E272-ATLAS-COST20]`.

`scripts/compute_audit.py` read `ready=3 / floor=3 / breach=false` — i.e. the supply
floor considered itself satisfied. `Tools/autofill.py tick --dry` answered the same
pool with `verdict: ghost_ready_no_shards` and the same three ids.

Two published faces, one pool, two worlds.

## What the three rows turned out to be

| row | measured |
| --- | --- |
| `E272-ATLAS-COST0` | deliverable in git since r1163 (`d0cdc4e44b`). Re-ran: every number reproduced bit-for-bit, only `audit.workers` 4→8 differs → determinism proof, not new supply. |
| `E272-ATLAS-COST20` | deliverable in git since r1163, but stocked with `--cost=20`. Cost is a **fraction per side**, so that is 2000%/side: equity crosses zero, `growth ** (1/yr)` is complex, run dies 280 cells deep with `TypeError: float() ... not 'complex'`. |
| `E243-ADDITIVITY-OUT-OF-SAMPLE` | runner imports `e235_charge_granularity` → `e230_hysteresis_toll`, a module in **no commit** (only its digest landed). Cannot start on any clean checkout. |

So the floor counted three rows of which two deliverables already existed and the
third could not even import: **zero new supply**, and nothing in the audit could see it.

## What changed (mechanism, not a sentence)

* `scripts/compute_audit.py` — `ignitable_face` now publishes, beside the untouched
  `ready_ignitable`, the questions the executor asks: `ready_unclaimable`
  (`_unsharded`: no shard = nothing to claim, r301/r1353 law) and `ready_dep_broken`
  (`_unresolved_dep`: `import eNNN_*` naming a sibling script that is not in the tree),
  with `ready_launchable` = owner-legal **and** startable. Flag
  `supply_unstartable` fires when ignitable>0 and launchable==0 under low py. Selftest
  51 → 57, including a **parity leg that imports the launcher's own rule**
  (`Tools/autofill.py unclaimable_ready_ids`) and requires it to name exactly the ids
  the audit calls unclaimable — one rule, two readers (E270).
* `scripts/etf_book_phase_atlas.py` — cost unit guard: anything outside `0..0.05`
  is refused at entry with a message that says `10bp is 0.0010, 20bp is 0.0020`.
  Selftest 12 → 13.
* `results/runnable_pool.json` — the three rows retired with typed evidence
  (two `done` + result notes, one `blocked_by=runner-import-missing:e230_hysteresis_toll`).

Live proof from the chain's own leg (`results/compute_audit.json`, 14:14):

```
verdict FLAG:supply_gap,supply_unstartable
floor   {"ready": 3, "floor": 3, "breach": false, "ready_launchable": 0,
         "breach_launchable": true, "ready_ignitable": 3, "breach_ignitable": false}
unclaimable_ids E243-ADDITIVITY-OUT-OF-SAMPLE, E272-ATLAS-COST0, E272-ATLAS-COST20
```

(`supply_gap` is honest and expected here: the chain itself was burning the CPU while
the audit sampled; the new flag is the one this round is about.)

## The cost question the dead row was supposed to answer

The 20bp face is already published (r1163): band `6.60pp` vs between-cell spread
`3.55pp` → `CONFIG_ORDER_WITHIN_PHASE_NOISE`. Against the 0bp face re-derived today
(band `6.747pp` vs spread `6.92pp` → `CONFIG_ORDER_EXCEEDS_PHASE_NOISE`), the reading
is: **the ruler does not follow the toll (6.75 / 6.68 / 6.60pp at 0/10/20bp), but the
measured ordering does** — at 0bp the 12 cells separate from their own phase noise by
0.17pp, at 20bp they do not separate at all. So "config A beats config B" in this book
is a statement about the cost regime, while every earlier "inside the band" verdict
still stands because the band itself is stable in cost.

## Next

* `e230_hysteresis_toll.py` must land (six scripts import it; none can run on a clean
  checkout) or the importing scripts must stop depending on a file that is not in git.
* `stats2` should name `nonpositive_growth` instead of returning a complex number, so
  the next unit error surfaces as a labelled cell rather than a 280-cell crash.