# r948 bm-b git-loss forensics addendum (root-cause continuation, complements results/_r947bmb_gitloss_forensics.json)

## 1. Lock-orphan mechanism (why the r947 restore worker all-faces rc=128)
- Worker `Stop-Process` killed pid 7320 = **git cmd-shim** (`C:\Program Files\Git\cmd\git.exe`), which spawns the REAL git (`mingw64\bin\git.exe`) as a child. Real git pid **9236 (born 20:12:28)** survived as orphan, held `.git\index.lock` 20 min, no `git-remote-https` child = stalled on dead-socket read (network died mid lazy-fetch, GFW night window).
- Worker then ran `Remove-Item index.lock` under `$ErrorActionPreference='Continue'` -> **removal silently failed (file open)**, but log printed "lock cleared" = false. Every subsequent face checkout = instant rc 128 (`Unable to create index.lock: File exists`).
- **Law (new pit, P0-class):** (a) killing git processes must kill the process TREE (`taskkill /PID <p> /T /F`) or match the real body by birth-time+cmdline — shim PID kill orphans the holder; (b) lock removal must be `Remove-Item -ErrorAction Stop` + re-Test-Path assert — EAP=Continue turns lock-clears into silent lies; (c) `Start-Process -FilePath git` returns the shim PID, not the git PID.
- Fixed in `results/_r947bmb_restore_worker.ps1` (r948 patch): taskkill tree + honest lock ops + per-face rc logging unchanged.

## 2. Killed-round command audit = CLEAN (attacker theory "the session deleted it" disproven)
Full 25 executed shell commands of the killed r947-attempt-1 session (transcript `05e45db3.../chats/74ce09a7-*.jsonl`) extracted and audited:
- cmd1-3 (bigmoney): `git status/pull --rebase`, `stash-bridge pull`, `smoke_test 49/49 PASS` (faces intact ~19:35), saturation status. No deletes.
- cmd4-20 (group tree only): status/pull/sparse-checkout list/add (Tools + cph4/fleet/dispatcher)/ls-tree/show/checkout -- Tools/fleet-nodes.json/add+commit sli-reconcile fixes (group 58b0097). **No command touches bigmoney faces.**
- cmd21-25 = post-alarm investigation + treasure_guard restore gate (read-only).
- Group repo CANNOT mechanically delete bigmoney faces: `git ls-files -- quant/bigmoney` = 0 (never tracked), `ls-tree origin/main quant/bigmoney` empty. Mirror theory stays disproven.

## 3. sli-reconcile.ps1 + sli-reconcile-wrapper.ps1 audit = CLEAN
Both scripts (bm-a origin materialized by killed round, first-run at cmd16) read only `cph4/fleet/dispatcher/*` + `media/logs/*heartbeats`, write `SLI-RECONCILE.md`, `git -C C:\Fluxgroup\FluxGroup add/commit/push`. No Remove-Item, no clean, no checkout of bigmoney. Not the killer.

## 4. Deletion signature puzzle (open)
- Destroyed = {.git, .gitignore, CODELY.md, HQ-FEEDBACK.md, docs, engine, firm, fleet, knowledge, legacy, live} = r834 set MINUS data.
- r834 = NTFS-order sweep interrupted before `logs` (data < docs, so data died). **r948 correction: DATA FACE ACTUALLY GUTTED THIS TIME TOO** (data/daily/sh510300.csv + data/fundamental/eligibility.csv + data/zt_pool/collected_days.json ALL absent; only 1 subdir left on disk). r947 "surviving_faces: data" = existence-only check = WRONG. -> **alphabetical/NTFS-order sweep interrupted at the `logs` boundary theory RESTORED** (r834-identical signature incl. data, both times killed/aborted right before `logs` ~ consistent with a single recursive Remove-Item sweep colliding with the 25-min runner kill).
- Data restorability: data/ = machine-local runtime assets; S6 chain legs re-pull panels from sources on missing-file (daily/etf_daily/astock/lhb/moneyflow full history from sina/EM). FORWARD-ONLY faces lose their archive irrecoverably (zt_pool since FIRST_DATE 2026-10-08 ~6 trading days; minute_feed since 2026-09-28) - freeze-law preregs affected accordingly; deep re-pull = r949 S6 chain after faces restore.
- Remaining evidence to pull: USN journal window 19:36-19:55 (deletion timestamps), `bigmoney` dir LastWriteTime (checked by killed round cmd24 — value not captured in transcript excerpt, re-pull from disk), other-lane transcripts active in window (61d7181 / 85e0b26 / 2c48952 / cf4d8126 chat dirs), S4U tasks registered/modified in window.

## 5. Standing laws until root cause (carry from r947)
- No rm/Remove-Item on any repo face by any lane; group-tree zero-touch (git show only).
- Long jobs detached + tree-kill discipline; runner 25-min kill is the backstop.
- Bundle fallback armed: MSG-20261014-2015-bmb.md now PUSHED to origin (was stranded local by r947 commit-worker lock failure) — bm-a/bm-c can act.
