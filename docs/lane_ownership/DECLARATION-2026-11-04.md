# Lane ownership declaration (2026-11-04T23:10:50)

> derived by `scripts/lane_ownership_declaration.py` from `results/data_lane_freshness.json`,
> `config/lane_hosts.json` and the `owner` defaults inside `data_lane_freshness.LANES`.
> Never hand-edited: the answer is recomputed, and `--check` fails when the file and the
> inputs disagree.

**OWNERSHIP_UNIQUE** -- 10 lanes, 10 owned, 0 conflicts, 5 lanes where the config overrides a stale code default.

| lane | declared host | authority | code default | observed writer | host alive | verdict |
|---|---|---|---|---|---|---|
| options | bm-b | config/lane_hosts.json | bm-a | none (unattributed) | no | **DECLARED_ONLY** |
| moneyflow | bm-b | config/lane_hosts.json | bm-a | none (unattributed) | no | **DECLARED_ONLY** |
| heat | bm-b | config/lane_hosts.json | bm-a | none (unattributed) | no | **DECLARED_ONLY** |
| repo | bm-b | config/lane_hosts.json | bm-a | none (unattributed) | no | **DECLARED_ONLY** |
| marks | bm-b | data_lane_freshness.LANES | bm-b | none (unattributed) | no | **DECLARED_ONLY** |
| zt_pool | bm-b | config/lane_hosts.json | bm-a | none (non_host_copy) | no | **DECLARED_ONLY** |
| astock_daily | bm-b | data_lane_freshness.LANES | bm-b | none (unattributed) | no | **DECLARED_ONLY** |
| etf_panel | bm-a | data_lane_freshness.LANES | bm-a | none (unattributed) | no | **DECLARED_ONLY** |
| futures | bm-a | data_lane_freshness.LANES | bm-a | bm-a | no | **DECLARED_AND_OBSERVED** |
| lhb | bm-a | data_lane_freshness.LANES | bm-a | bm-a | no | **DECLARED_AND_OBSERVED** |

## Where the two sources disagree

The config wins (it is the 2026-10-21 CEO redline); the code default is what a reader of `data_lane_freshness.LANES` still sees, and it is wrong for: options, moneyflow, heat, repo, zt_pool.

## Owned but never observed

Declared on a host that has not produced an envelope this machine can read: options, moneyflow, heat, repo, marks, zt_pool, astock_daily, etf_panel. That is an absence of evidence, not evidence of a second writer -- it is what the 2026-11-08 enable decision must not read as 'safe'.

