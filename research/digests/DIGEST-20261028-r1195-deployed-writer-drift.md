# DIGEST 2026-10-28 r1195 (bm-b) — the fix was in the repo, the running code was a stale deployed copy

**Round mission:** S1 red at open — `fleet/machine-health.json` was unreadable again
(104 legs, 1 FAIL) one hour after r1193 had rebuilt it clean.

## The finding

The hourly task `FluxGroup-FleetOversight` does **not** run this repo's writer. It runs

```
C:\Fluxgroup\.codely-cli\oversight-bmb\fleet-oversight.ps1
```

A deployed copy from **2026-10-11** (v1.0, 338 lines) against a repo source at
**375 lines**. D-20261028-02's machine-health repair (machine-keyed map,
adopt-only-entries-with-`ts`, never propagate damage) was committed to the repo —
actually it was not even committed, it sat as an uncommitted worktree edit — and the
code that fires every hour still emitted the legacy hourly row array, so:

- 00:22 rebuilt face reads clean (`{"bm-b": {...}}`)
- 01:11 hourly fire re-broke it into `[{value: [...], Count: 2}, {"@{name=qwen...}": {...}}]`
- 01:12 the smoke leg is red again, and the panel shows blank rows, not UNKNOWN

So r1193's fix was correct **and** ineffective for exactly the reason the fleet already
has a pit for: a deployed copy is a second code face, and "worker reads the code that
was on disk when it spawned" is the same shape one step earlier in the pipeline.

## What shipped

| artifact | what it does |
|---|---|
| group `Tools/fleet-oversight.ps1` (pushed `76bf885c`) | the D-20261028-02 fix, now on origin instead of one worktree |
| group `Tools/oversight_deploy.ps1` (new) | source → live copy with UTF-8 BOM + verify-after-write; `-Check` = 0 identical / 1 drift / 2 never deployed; resolves the live dir as `oversight-<id-without-dashes>` (a dashed copy is read by no task) |
| bigmoney smoke leg `fleet: oversight writer's deployed copy tracks its source` | runs `-Check`; drift is RED, not a damaged face discovered by a reader |
| `fleet/machine-health.json` | rebuilt canonical, then re-verified by firing the DEPLOYED writer live (not the repo copy) |
| bigmoney `fleet/inbox/MSG-20261028-0130-ALL.md` | bm-a/bm-c must run `oversight_deploy.ps1 -M <id>` after pulling, or their hourly fire keeps writing the old shape |

## Evidence

```
oversight-deploy: deployed bm-b -> ...\oversight-bmb\fleet-oversight.ps1 (20923 chars, verified)
& ...\oversight-bmb\fleet-oversight.ps1 -M bm-b  ->  OVERSIGHT 2026-10-28T01:21:51 ... flags=1
machine-health: OK machines=1 dropped_junk=0 blank=0 bm-b
smoke: 104/104 PASS  (was 102/103 with the face leg red)
drift probe: clean rc=0 / after adding a line rc=1 / redeploy rc=0
```

## Lesson (card E161)

A fix is only live where the scheduler runs it. Any task whose entry point is copied
outside the repo needs a **drift leg that compares the deployed file to the source**,
or the next repo edit is a paper fix. The tell in this instance was precise: the face
was rebuilt clean at 00:22 and broken at 01:11 — one hourly fire, zero repo edits.

## Not done this round (carried)

E123 pair screened twin (`run_pair` drawdown pair) stays `ready` in the pool — the S1
red consumed the round, and pool ready stood at 2 (floor 3) at close, which the next
round's E123 burn also repairs.