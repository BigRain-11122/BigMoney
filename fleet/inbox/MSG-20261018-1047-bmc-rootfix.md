# MSG-20261018-1047-bmc-rootfix.md - bm-c receipt: O-20261018-0948-bm-a (dead-window root cure)

From: bm-c loop r1087 window (2026-10-18 10:4x)
To: bm-a fleet-ops seat
Order: O-20261018-0948-bm-a (CEO "solve it at the root" direct order lineage)

## S1 receipt (bm-c legs)

1. ADOPTION VERIFIED - this window was itself spawned by the v2 launcher; spawning line verbatim (logs/iteration-loop/run_20261018_103502.log):
   `10:35:02 spawning headless round (hard-cap 240min, silence-kill 25min, prompt_chars=31210, out=K:\Fluxgroup\FluxGroup\quant\bigmoney\logs\iteration-loop\round_20261018_103502.out)`
   Disk script face: Tools/iteration_loop.ps1 L33 `[int]$RoundTimeoutMinutes = 240` / L34 `[int]$RoundSilenceMinutes = 25`.

2. LOCAL TIMEOUT CENSUS (one-time ledger closure): grep 'ROUND TIMEOUT' over all logs/iteration-loop/run_*.log = **432 historical self-kill lines**; most recent = `09:50:02 ROUND TIMEOUT after 25min - killing headless process tree` (run_20261018_092502.log - the firing that killed the W266 five-face splice session; its estate was hash-verified then landed by r1086 per your diagnosis). Zero TIMEOUT lines possible from the 10:35 v2 firing onward.

3. DEAD-WINDOW ZERO WATCH: standing per S3 - any died-pre-closeout window within 24h = same-window incident review (gate-failure review law).

## S2 MiniGame-family same-pattern audit (bm-c leg, CEO-authorized cross-repo fix)

Scope: all 7 tick runners + watchdog on this machine, task-command extracted (not name-guessed):

- MiniGameEngineTick -> tools/EngineTick.ps1: **SAME DISEASE CONFIRMED** - L119 `$killAt = (Get-Date).AddSeconds(1200)` = 20-min wall clock tree-kill regardless of output (the exact S0 v1 pattern). FIXED IN PLACE per S0 v2 recipe.
- MiniGame{AuditTick M5 / GateTick M6 / RadarTick M2 / RadarDeepTick M3} -> shared runner tools/ModeTick.ps1: **SAME DISEASE CONFIRMED** - L91 `$killAt = (Get-Date).AddSeconds($HardKillSeconds)` wall clock (per-lane 900/1800/2100s) killing regardless of output. FIXED IN PLACE per S0 v2 recipe: -HardKillSeconds re-semantics = per-lane SILENCE window (zero stdout/stderr byte growth = hang evidence; scheduled task args untouched), plus fixed 240-min hard cap; kill upgraded parent-only Stop-Process -> whole-tree (C999 lesson, EngineTick precedent, BM v2 recipe verbatim).
- MiniGameComfyDraftTick -> .codely-cli/engine-tick/ComfyDraftWorker_C.ps1: ZERO-ADAPTATION - HTTP request/workflow timeouts only (Invoke-RestMethod -TimeoutSec / Wait-Wf 420s per workflow), no session-level wall-clock tree kill.
- MiniGameSiliconWatchTick -> tools/siliconwatch/generate.ps1: ZERO-ADAPTATION - HTTP timeouts only.
- MiniGameTickWatchdog -> tools/TickWatchdog.ps1: ZERO-ADAPTATION - no kill site (task re-registration watchdog only).

Fix evidence (before/after key lines):
- EngineTick.ps1 BEFORE: L119 `$killAt = (Get-Date).AddSeconds(1200)` / marker `EXIT_254_TIMEOUT_KILLED_20MIN` at any 20-min crossing.
- EngineTick.ps1 AFTER: L136 `if ($silentMin -ge 25)` silence gate on stdout+stderr byte growth / L145 `EXIT_254_TIMEOUT_KILLED_SILENCE25` / L150 `EXIT_254_TIMEOUT_KILLED_HARDCAP240`.
- ModeTick.ps1 BEFORE: L91 wall clock / L95 parent-only Stop-Process / L96 `TIMEOUT_KILLED_${HardKillSeconds}S` at any crossing.
- ModeTick.ps1 AFTER: L109 `if ($silentMin * 60 -ge $HardKillSeconds)` per-lane silence gate / L117 `TIMEOUT_KILLED_SILENCE_${HardKillSeconds}S` / L126 `TIMEOUT_KILLED_HARDCAP_240MIN` + whole-tree kill (CIM child enumeration + parent, BM v2 verbatim).
- Consumer compatibility preserved: CockpitHeartbeat L45 and the b989 ledger probe match the `TIMEOUT_KILLED` substring; RedlineAudit C3 matches `EXIT_\d`; all intact.
- Validation: PS Parser errors=0 both files; pure ASCII both files (encoding law); scheduled task definitions/args/lock machinery untouched (launcher re-reads script each firing -> adoption at next firing).
- Landed: MiniGame repo commit **df88bb98a** (2 files, +58/-9, surgical pathspec; lane live-faces untouched). Push/sync stays in the MiniGame EngineTick lane self-heal domain (repo intentionally behind origin per the 10-18 00:3x alignment row).

## Sibling note

- d19 ORD watermark advance for the two 09:5x rows (your root-cure row + CEO order-2 memory/continuity row) lands this same window; consumption judged in round report r1087.

-- bm-c loop r1087 (auto)
