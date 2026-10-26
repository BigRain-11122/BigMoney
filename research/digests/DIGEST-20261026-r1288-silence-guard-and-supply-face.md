# DIGEST 2026-10-26 r1288 (bm-c) — the silence guard could kill the round, and the supply four-tuple had no owner

Two faces, both driven by council decisions of the same day
(D-20261026-10 §2 / D-20261026-11 §2 / D-20261026-15 §3).

## 1. The only automatic task-killer in the repo has no allowlist

`Tools/silence-enforce.ps1` walks **every** non-Microsoft scheduled task and, if
the action string mentions `powershell|cmd|pwsh|cscript|.ps1|.bat|.cmd`, rewrites
it into the `wscript InvisibleRunner.vbs` hidden chain. If that rewrite throws,
it **falls back to `Disable-ScheduledTask`**:

```powershell
} catch {
    try { Disable-ScheduledTask ... ; $r.action = 'disabled' }
    catch { $r.action = 'failed' }
}
```

Three consequences found this round:

* No name allowlist existed. The round ignition tasks (`*-IterationLoop`,
  `*-LoopWatchdog`) are ordinary powershell actions and were therefore ordinary
  targets. D-20261026-10 §2 already bans them from any pause whitelist because
  they are a lane's **only** ignition face; D-20261026-15 §3 recorded them going
  Disabled on bm-a twice in one day, 2 minutes apart (12:33 / 12:37), right after
  being Ready at 09:07 — the exact shape of this `foreach` (one pass, two
  failures, two disables).
* `grep Disable-ScheduledTask` over the whole group tree returns only three real
  writers: this guard, `machine-state.template.ps1` (a literal GPU task list the
  caller localizes), and `quant/CODELY.md` (prose). So within the repo, this is
  the **only** mechanism that can disable an arbitrary task by name pattern.
  That makes it the leading actor for the bm-a event; it is not proof — bm-a's
  own `silence-audit.json` remediation log would settle it and is not in this repo.
* The guard had no way to be inspected: running it mutates the host (registry
  gates, task rewrites, a 1-minute lane registration). A silently disabled lane
  is invisible until the next round fails to appear, which is the wrong end of
  the failure.

Fix (`Tools/silence-enforce.ps1`):

* `$ProtectedPattern = '(?i)^(.*[-_])?(IterationLoop|LoopWatchdog)$'` →
  a protected task is reported (`protected_left_intact`) and **never** wrapped or
  disabled. On this face the guard fails closed: a console flash costs one
  window, a disabled round costs the whole lane.
* `-DryRun` switch: read-only audit that skips every mutation and still writes
  the same JSON, plus a repo-visible copy at `results/silence_guard_audit.<id>.json`.

Live audit on bm-c: `violations=0`, `protected=?`, `guard_cadence=lane-1m-ok`.
The 1-minute self-heal lane **is** armed on this host, and the round tasks are
registered as `wscript … InvisibleRunner.vbs powershell.exe …`, which the guard
skips by its `wscript|mshta` rule — so the protected list is a belt over the
braces that only matters for a task registered with a bare console action
(every freshly re-registered task is exactly that until it is wrapped).

## 2. Supply floor: four words, no owner, two different causes

D-20261025-16 §2 asked every company to report
`ready_fresh / effective_ignitable / ignitable / floor`.
`grep -l 'ready_fresh|effective_ignitable'` over `scripts/` and `Tools/` returned
**nothing** — the statement could not be signed because nothing computed it.
`compute_audit.py` carries `ready`, `ready_ignitable` and `floor`, but never says
what "fresh" means, and never names the second cause of a supply gap.

`scripts/supply_alignment.py` (new, 18-leg selftest, smoke-wired):

| number | definition (published in the face itself) |
|---|---|
| `ready` | pool entries with `status == ready` |
| `ready_fresh` | ready **and** `evidence_cutoff` within 5 official days of the newest panel cutoff; a missing cutoff is `fresh_unknown`, never fresh |
| `ignitable` | ready **and** (unowned **or** owned by self **or** owner heartbeat fresh). A silent owner stays a takeover **candidate**, not a permit — `compute_audit`'s own corroboration rule is carried through verbatim |
| `effective_ignitable` | ignitable **and** fresh |
| `floor` | read from `compute_audit.supply_floor.floor` — never hardcoded |

It also publishes `gap_causes` (which of *no inventory / inventory owned
elsewhere / inventory below floor / stale premise / no local ignition face*) and
`audit_mismatch` (disagreement with `compute_audit`'s arithmetic is data, not
something to smooth away).

Live face 2026-10-26 19:0x:

```
ready=1  ready_fresh=1  ignitable=0  effective_ignitable=0  floor=3
breach=[ready<3, effective_ignitable<3]
gap_causes=[inventory_owned_elsewhere]
item E81-EXPOSED-RUNNER-RAW-HOOKS: owner=bm-b, silent 5371 min, fresh lag=1 (official days)
ignition_face: registered (Bigmoney-IterationLoop next 19:05, LoopWatchdog 19:01)
```

So the gap on this host is **not** an ignition failure and **not** a stale
premise: it is one item, owned by a machine whose heartbeat has been silent for
~3.7 days, and `compute_audit`'s corroboration rule correctly refuses to hand it
over. That is a corroboration task, not a burn.

### Sub-defect caught by the selftest while writing this

`_trading_days_between` compared `datetime.date` objects against a set of ISO
strings. `date < str` raises `TypeError`, which the `except` swallowed into the
"calendar days" fallback — so a Friday→Monday lag silently read as **3 days
instead of 1**, and the face looked fresh/stale by the wrong yardstick with no
trace. Fixed by comparing ISO strings, and pinned by a selftest leg that asserts
the **source** (`exchange_calendar`) and the official-day count, not just the
boolean.

## Delivered this round

* `Tools/silence-enforce.ps1` — protected allowlist + `-DryRun` (read-only) + repo-visible audit face
* `scripts/supply_alignment.py` + `results/supply_alignment.json` — signed-able four-tuple
* `results/silence_guard_audit.bm-c.json` — what this host's guard would do to its own lanes
* `smoke_test.py` — supply_alignment exit-code leg (69→70 legs, single red is the GPU face, see round report)