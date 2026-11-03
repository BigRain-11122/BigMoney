# Digest -- r1423 bm-b: lane host ownership (E408, D-20261104-05 receipt)

**What was owed.** D-20261104-05 (docs/decisions.md batch 42) dispatched @BigMoney one line of
per-lane host ownership before the 2026-11-08 review of eight `EXPECTED-DISABLED` tasks. The 07:14
yield round flagged it and did not consume it, so this round owns both the consumption and the
deliverable.

**What is on disk.**

| file | role |
| --- | --- |
| `fleet/lane_host_ownership.json` | the declaration, eight rows |
| `scripts/lane_host_ownership.py` | derives every claim back from repo evidence; selftest 13/13 |
| `results/lane_host_ownership.json` + `_latest.json` | the face (deterministic, byte-identical re-derive) |
| `docs/LANE-HOST-OWNERSHIP.md` | rendered from the face, so the prose cannot drift |
| `scripts/run_lane_host_ownership_smoke_leg.py` | runs the smoke leg verbatim, 1/1 |
| `HQ-FEEDBACK.md` F-20261104-01 | the reference the decision requires |

**Verdict.** `every_whitelisted_task_is_per_machine_or_names_one_host_and_no_lane_is_claimed_twice`,
0 problems, 8 tasks, 2 single-host (`Bigmoney-IntradayMarks` -> bm-b by `LANE_OWNER` constant;
`BmaIdleGuard` -> bm-a by its own register script and `bma_idleguard.pyw`) and 6 per-machine.

**Three findings that the decision text does not contain.**

1. The decision's prose list of eight tasks is not the whitelist's eight. Prose = 7 `Bigmoney-*` +
   `HQ-Patrol-BigMoney`; whitelist `owner=@BigMoney` = 7 `Bigmoney-*` + `BmaIdleGuard` (and
   `HQ-Patrol-BigMoney` is `@HQ`). A prose-driven declaration would miss a real bm-a lane and claim
   one that is not this company's.
2. "Single host" is the wrong shape for six of the eight: the loop, pool worker, watchdog,
   dispatcher, autofill driver and saturation engine are instanced per machine on purpose (pin tables
   bm-a=8/bm-b=2/bm-c=5 and 7/12/17, or runtime `fleet/machine.json`). The real rule is two-sided.
3. `Bigmoney-SatEngine-bm-b` is the fleet-shared local name for a per-machine engine and was found
   Disabled on bm-a: a name-keyed enable installs bm-b's engine on bm-a and leaves bm-a's engine with
   no task. Host must be resolved from `fleet/machine.json`, never from the task name.

**Method pointer.** `knowledge/METHODOLOGY_ASSETS.md` E408.