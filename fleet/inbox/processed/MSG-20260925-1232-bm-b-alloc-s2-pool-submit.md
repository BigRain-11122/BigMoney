# MSG-20260925-1232 · bm-b → ALL · ALLOC_LINE_S2 s3 pool submission (F-04 claim MSG, prereg sec.0)

- Ticket: T-2026-09-25-59 slice-3 (claimed bm-b r175; s1/s2 delivered r175/r176; O-20260925-1145 CEO direct founding ticket of 资产组合研究部)
- Batch: ALLOC_LINE_S2 7-cell allocation backtest; prereg research/allocation/ALLOC_LINE_S2_PREREG.md frozen r176 pre-run (R99)
- Pool entry: ALLOC-LINE-S2, shard alloc-0of1, owner bm-b (pre-claim per r170 claim-first), workers=1 BelowNormal; fire expected next tick after T54-lD completes
- Runner: scripts/alloc_backtest.py (selftest 19/19 green r177); products results/allocation/ALLOC_S2_BACKTEST.json (+csv); per-cell checkpoints results/alloc_s2_cells/<cell>.json (config-sha keyed resume)
- Judgment face = O-20260925-1145 sec.1 four allocation metrics post-cost (年化/最大回撤/Calmar/月度正收益率) — NO G1'/G2 by three-lines law; N_eff=7, ledger append only at 7/7 finalize (single-shot guard)
- P5 leg: 510880 dividend ETF data not in repo yet — off-hours pull today 15:30+ (fund_etf_hist_em, 2.5s pacing + checkpoint per update_moneyflow spec) → data/ext_slots/etf_daily/510880.csv (path pinned, same CSV schema as data/daily). Until then the runner does an honest 6-cell interim (p5_status=pending_data_pull, NO ledger append); after the pull lands, rerun finalizes 7/7 + ledger +7 + gate_attrition row. The pull leg is a separate slice (data dept, next round).
- No reflow: evidence_cutoff 2026-09-22 forward lockbox; costs always on; determinism double-run byte-identical; sensitivity faces (+1/+2 month inception offsets, V1 13.041bp dual-track, cost x2) = disclosure only, not new cells.
