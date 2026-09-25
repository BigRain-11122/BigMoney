# F-04 claim: T-57 s2 后半 -- WILD_ROUTE_S1 encoding + prereg freeze + pool entry

- Machine: bm-b (OS iteration loop, round 197)
- Scope: scripts/wild_route_lab.py (shared event engine one-pass + 12-pattern 29-arm daily encoders + bucket sim, selftest 22/22 hermetic) + scripts/wild_route_probe.py (pre-freeze data-face facts: cliff thresholds 0.0975/0.1975 capture 99.4%/95.8%, turnover DEAD face, census gate OK) + research/WILD_ROUTE_PREREG_S1.md FREEZE COMMIT (R99: probe facts only pre-freeze, zero strategy runs) + seed base science_gates.SEED_REGISTRY['wild_route_s1']=61000 registered + runnable_pool entry WILD_ROUTE_S1 (8 shards + nulls shard, post-freeze).
- NOT in scope this slice: s4 verdicts, zoo registration, any post-freeze batch execution inside this round (pool fires on autofill/watchdog ticks per O-2100).
- Anti-dup: T-57 ticket bm-b claim r174 in-force, s1 closed r195 (12/12), s2 cards delivered r196 (bm-b own lane); any machine planning wild-route encoding/batch, yield per fleet README sec4 (this claim + freeze commit first).
- Batch discipline: cells 1569 + 50 nulls, N_eff 1619; per-cell checkpoint JSON + per-shard jsonl (rows carry own key); engine build once per process; workers_plan = 1 process per shard, BelowNormal.
