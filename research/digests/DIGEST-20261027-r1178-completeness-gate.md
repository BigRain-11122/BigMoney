# DIGEST r1178 (bm-b): a pipeline gate on a completeness BOOLEAN is a gate that never opens

Face: `scripts/rev_osc_signal_export.py` (REV-OSC SIG/BARS bridge) -> consumer
`scripts/system_v1_paper.py` (SYSTEM-V1 live paper book, bm-a lane).

## What was wrong

The live paper book had been priced at **2026-10-20 for four trading
sessions** while every other face said 2026-10-26. The obvious reading --
"the A-share panel is stale" -- was wrong: `results/astock_daily_update_status.json`
reported `cutoff=2026-10-26`, `coverage_pct=99.8`, `coverage_90=2026-10-26`,
5225 of 5227 per-file panels on disk.

The panel was not stale. The gate was:

    if not panel.get("complete"):  return 0   # "harness waits"

`complete` is a boolean over the WHOLE universe, and a handful of permanently
quarantined / persistently-failing symbols (5 quarantined, 1 write failure in
the last continuation pass) keep it `false` forever. Every round the collector
honestly re-spawned, found `todo=8`, fetched 7, appended 0 -- and every round
the bridge concluded the panel was not ready. Six days, zero output; the
blocked leg is the only feed for the CEO-visible paper book.

## What was changed

`panel_readiness(panel)` -- a pure function, replacing the boolean test:

    ready = panel["complete"]                           # basis=complete
         or (coverage_pct >= coverage_floor_pct         # basis=coverage
             and coverage_90 == cutoff)

Rationale is the E136/E102 口径 already in the repo: **a panel cutoff is a MAX
over a heterogeneous population, never a coverage claim.** So the readiness
question must be answered by coverage at the cutoff, not by "are all names
done". The floor is read from the panel's own `coverage_floor_pct` (90), not
hardcoded. Every SIG file now carries `panel_readiness` (basis, coverage_pct,
coverage_90, floor, and the two booleans behind the decision), so a consumer
can see *why* a date was priced rather than only that it was.

## Evidence

- Bridge output: `SIG-2026-10-26.json` -- picks=10, gate_open=True,
  universe 3508/3513 names with a bar at the cutoff, qualified_n=1384;
  `BARS-2026-10-26.json` -- 72 codes, 15 rows each. (Before: newest files
  2026-10-20, written 2026-10-21 07:53.)
- Selftest 10/10, three legs added: complete->basis=complete; the exact live
  regression (complete=false + coverage>=floor at cutoff -> ready on coverage
  basis); and the two ways it must still wait (coverage below floor; the
  >=floor coverage date trailing the cutoff; missing fields).
- smoke 85/85 PASS after the change.

## Reusable rule

When a lane gates on an upstream artifact, ask what the boolean is a boolean
OVER. `complete`/`all_done`/`finished` describe the worst member of a
population; a lane that needs the population's bulk must gate on the coverage
distribution, state the floor it used, and stamp the basis into its output.
A gate whose only two states are "wait" and "go" will be read by nobody --
publish the numbers behind it.

Sibling faces to check with the same question (not done in this round):
`coverage_90`-style fields exist on `astock_daily_update_status.json` but any
other lane testing `complete` inherits the same permanent-wait failure mode.