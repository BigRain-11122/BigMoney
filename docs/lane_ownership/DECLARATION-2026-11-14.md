# Lane ownership declaration (2026-11-14T02:10:54)

> derived by `scripts/lane_ownership_declaration.py` from `results/data_lane_freshness.json`,
> `config/lane_hosts.json` and the `owner` defaults inside `data_lane_freshness.LANES`.
> Never hand-edited: the answer is recomputed, and `--check` fails when the file and the
> inputs disagree.

**OWNERSHIP_UNIQUE** -- 15 lanes, 15 owned, 0 conflicts, 4 lanes where the config overrides a stale code default.

| lane | declared host | authority | code default | observed writer | host alive | verdict |
|---|---|---|---|---|---|---|
| options | bm-c | config/lane_hosts.json | bm-a | none (unattributed) | yes | **DECLARED_ONLY** |
| sina_mf | bm-c | config/lane_hosts.json | - | bm-c | yes | **DECLARED_AND_OBSERVED** |
| moneyflow | bm-c | config/lane_hosts.json | bm-a | bm-c | yes | **DECLARED_AND_OBSERVED** |
| lhb_inst | bm-c | config/lane_hosts.json | bm-c | bm-c | yes | **DECLARED_AND_OBSERVED** |
| ah_panel | bm-c | config/lane_hosts.json | - | none (host_copy) | yes | **DECLARED_ONLY** |
| marks | bm-b | data_lane_freshness.LANES | bm-b | bm-c | no | **DECLARED_TAKEOVER** |
| astock_daily | bm-b | data_lane_freshness.LANES | bm-b | bm-c | no | **DECLARED_TAKEOVER** |
| etf_panel | bm-c | config/lane_hosts.json | bm-a | bm-c | yes | **DECLARED_AND_OBSERVED** |
| futures | bm-a | data_lane_freshness.LANES | bm-a | bm-a | no | **DECLARED_AND_OBSERVED** |
| heat | bm-a | config/lane_hosts.json | bm-a | bm-a | no | **DECLARED_AND_OBSERVED** |
| lhb | bm-a | data_lane_freshness.LANES | bm-a | bm-a | no | **DECLARED_AND_OBSERVED** |
| minute_feed | bm-c | config/lane_hosts.json | - | none (host_copy) | yes | **DECLARED_ONLY** |
| repo | bm-a | config/lane_hosts.json | bm-a | bm-a | no | **DECLARED_AND_OBSERVED** |
| ths_panel | bm-c | config/lane_hosts.json | - | bm-c | yes | **DECLARED_AND_OBSERVED** |
| zt_pool | bm-c | config/lane_hosts.json | bm-a | none (host_copy) | yes | **DECLARED_ONLY** |

## Where the two sources disagree

The config wins (it is the 2026-10-21 CEO redline); the code default is what a reader of `data_lane_freshness.LANES` still sees, and it is wrong for: options, moneyflow, etf_panel, zt_pool.

## Owned but never observed

Declared on a host that has not produced an envelope this machine can read: options, ah_panel, minute_feed, zt_pool. That is an absence of evidence, not evidence of a second writer -- it is what the 2026-11-08 enable decision must not read as 'safe'.

## Owned, currently served by a declared stand-in

astock_daily (by bm-c), marks (by bm-c) -- the owner is unchanged and the envelope names both the owner and the stand-in, so this is a standby rule in force, not two writers. The 2026-11-08 enable decision should check whether the owner has come back before re-enabling anything that would run on both.

