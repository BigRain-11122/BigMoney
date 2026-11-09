# Lane ownership declaration (2026-11-09T19:35:21)

> derived by `scripts/lane_ownership_declaration.py` from `results/data_lane_freshness.json`,
> `config/lane_hosts.json` and the `owner` defaults inside `data_lane_freshness.LANES`.
> Never hand-edited: the answer is recomputed, and `--check` fails when the file and the
> inputs disagree.

**OWNERSHIP_UNIQUE** -- 15 lanes, 15 owned, 0 conflicts, 4 lanes where the config overrides a stale code default.

| lane | declared host | authority | code default | observed writer | host alive | verdict |
|---|---|---|---|---|---|---|
| options | bm-c | config/lane_hosts.json | bm-a | none (unattributed) | no | **DECLARED_ONLY** |
| ths_panel | bm-c | config/lane_hosts.json | - | none (unattributed) | no | **DECLARED_ONLY** |
| ah_panel | bm-c | config/lane_hosts.json | - | none (non_host_copy) | no | **DECLARED_ONLY** |
| sina_mf | bm-c | config/lane_hosts.json | - | none (unattributed) | no | **DECLARED_ONLY** |
| marks | bm-b | data_lane_freshness.LANES | bm-b | none (unattributed) | no | **DECLARED_ONLY** |
| zt_pool | bm-c | config/lane_hosts.json | bm-a | none (non_host_copy) | no | **DECLARED_ONLY** |
| astock_daily | bm-b | data_lane_freshness.LANES | bm-b | bm-a | no | **DECLARED_TAKEOVER** |
| etf_panel | bm-c | config/lane_hosts.json | bm-a | bm-a | no | **STALE_ENVELOPE** |
| lhb | bm-a | data_lane_freshness.LANES | bm-a | bm-a | no | **DECLARED_AND_OBSERVED** |
| minute_feed | bm-c | config/lane_hosts.json | - | none (non_host_copy) | no | **DECLARED_ONLY** |
| moneyflow | bm-c | config/lane_hosts.json | bm-a | bm-c | no | **DECLARED_AND_OBSERVED** |
| repo | bm-a | config/lane_hosts.json | bm-a | bm-a | no | **DECLARED_AND_OBSERVED** |
| futures | bm-a | data_lane_freshness.LANES | bm-a | bm-a | no | **DECLARED_AND_OBSERVED** |
| heat | bm-a | config/lane_hosts.json | bm-a | bm-a | no | **DECLARED_AND_OBSERVED** |
| lhb_inst | bm-c | config/lane_hosts.json | bm-c | none (unattributed) | no | **DECLARED_ONLY** |

## Where the two sources disagree

The config wins (it is the 2026-10-21 CEO redline); the code default is what a reader of `data_lane_freshness.LANES` still sees, and it is wrong for: options, zt_pool, etf_panel, moneyflow.

## Owned but never observed

Declared on a host that has not produced an envelope this machine can read: options, ths_panel, ah_panel, sina_mf, marks, zt_pool, minute_feed, lhb_inst. That is an absence of evidence, not evidence of a second writer -- it is what the 2026-11-08 enable decision must not read as 'safe'.

## Owned, currently served by a declared stand-in

astock_daily (by bm-a) -- the owner is unchanged and the envelope names both the owner and the stand-in, so this is a standby rule in force, not two writers. The 2026-11-08 enable decision should check whether the owner has come back before re-enabling anything that would run on both.

