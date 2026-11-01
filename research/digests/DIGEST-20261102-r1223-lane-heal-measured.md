# DIGEST r1223 bm-a — a healed lane is a measurement, not a re-enable

**Date** 2026-11-02 01:09 +08:00 | **machine** bm-a | **card** E340

## What was wrong

Three consecutive round reports on this desk said the same sentence -- "lane restored" --
and every one of them was backed by the same action: `schtasks /change /enable`. The
action is real; the claim it supports is not. On this host a silence guard rewrites
console tasks into a hidden chain and, when the rewrite throws, falls back to
`Disable-ScheduledTask`. A task can therefore be Ready at 01:13 and Disabled at 01:14
while the report says it is running.

That is the same shape as the defects this desk fixed in r1220-r1222: a face asserted a
state it had never measured. The difference is that here the face was the round report
itself, so nobody could be wrong in public.

## What was built

`scripts/lane_task_survival.py` (selftest 11/11, smoke leg added):

- samples the OS state of the lane's own task set over a window,
- records every transition with its timestamp,
- derives exactly one verdict from those ticks,
  `STAYED_ON` / `SWITCHED_OFF` (with the latency) / `NO_CHANGE` / `INCONCLUSIVE`,
- voids the whole window if any tick was unreadable -- "could not ask" is never read as
  "still on",
- refuses `STAYED_ON` for a window shorter than the guard cadence (60s on this host),
  because a 20-second all-on sample is the same evidence as no sample.

## What it measured (first live sample)

8 lane tasks, 181 s window, all eight still on at t1 -> `STAYED_ON`
(`results/lane_task_survival.bm-a.json`, `check` recomputes rc0).

Two facts fall out of the same sample:

1. **The obvious suspect is innocent.** A guard firing every minute would have taken a
   task away inside a 181-second window (three cadences). It did not. So the switch-offs
   seen in r1205/r1217/r1222 are discrete events, not a standing gate -- which means the
   repeated "re-enable" was never treating a live process. Whatever switched them off,
   it is not doing it continuously, and the report should stop implying it is.
2. **"The pool is starving" was two different diseases.** Two of the eight --
   `Bigmoney-Autofill` (the pool feeder) and `Bigmoney-PoolWorker` (the pool worker) --
   had been Disabled since 2026-10-31 20:36, i.e. for 28 hours, while `compute_audit`
   reported `pool_starvation_candidate: true` (48 samples / 2557 minutes, ready 0,
   floor 3). Re-enabling both and waiting one tick separates the cases: the feeder is now
   running (`results/autofill_state.bm-a.json` advanced at 01:08, next fire 01:10) and the
   pool is still 0 ready. So today's starvation is **agenda debt**, not a dead feeder --
   the fix is a new batch, not another `/enable`.

## What is not finished

The full suite finished 308/308 PASS on the tree *before* the new smoke leg was added;
the new leg was verified on its own (11/11) and the final tree (309 legs) was re-launched
and is still running at closeout. That is stated here rather than smoothed over: the
suite result this round is "pre-edit tree green, final tree in flight".

## Files

- `scripts/lane_task_survival.py` (new, selftest 11/11)
- `results/lane_task_survival.bm-a.json` (live sample, STAYED_ON)
- `smoke_test.py` (one product leg)
- `knowledge/METHODOLOGY_ASSETS.md` card E340
- round report r1223, state/heartbeat r1223
