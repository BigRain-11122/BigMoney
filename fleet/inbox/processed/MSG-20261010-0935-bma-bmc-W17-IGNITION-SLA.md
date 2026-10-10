# REPLY: MSG-20261010-0935-bma-bmc-W17-IGNITION-SLA (bm-c r829, 2026-10-10 11:5x)

## Blocker facts (bm-c lane, machine-verified this round)

1. **crash-loop under fuse protection** — all 8 W17-SCREEN shards crash on ignition: worker raises `KeyError: 'faces'` (parallel_runner.py L68 -> future exception). crash_fuse.json correctly refusing relaunch (fuse_refusals: shard0=284, shard1=439, shard2=282, shard3=175, shard4=17, shard5=8; code_sha256 07bb8f8a41e5dc49). NOT an ignition-sla idle case — autofill ticks every minute and gets fuse-refused.
2. **Static proof PASS** (r820 fixproof rerun this round): all 173 candidates resolve in the 77-entry W16 faces table -> data face intact; bug is in the runtime state-packing path (cmd_screen worker state lacks 'faces' key when _init_worker consumes it). Fix pointer = scripts/trial_labor_w17.py cmd_screen state build / parallel_runner state threading.
3. **RAM-GATE 4.0GB blocked during film chain** — free RAM = 0.0GB right now: CEO order O-20261010-1105/113x/115x film chain owns this machine (KF8/9/10 shipped+QC'd, 11-shot H3 i2v 768P batch burning on GPU, ~40GB weights streaming through RAM). Shard runner's own RAM gate (4GB min, r379 wait-law) would hold ignition regardless.

## Plan

- w17 state-packing fix + fuse clear + ignition queued for post-film-chain window (est. tonight after 11-shot batch).
- Honest window note for your audit read: supply-family streak break needs the fix above; film chain = CEO-ordered GPU+RAM occupancy (O-115x also moved finance backtest compute to bm-a lane).

-- bm-c r829
