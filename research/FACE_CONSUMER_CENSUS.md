# Face consumer census

evidence set: `results/**/*.json` (depth <= 2), readable against `scripts/`, `Tools/`, `docs/`, `research/`

| tier | faces | what it means |
| --- | --- | --- |
| CODE_MULTI | 820 | >=2 source files name this face |
| CODE_SINGLE | 940 | exactly one source file names it (producer or lone reader) |
| PROSE_ONLY | 74 | only docs/research names it |
| ORPHAN | 370 | nothing names it (undated only) |
| DATED_CODE | 370 | dated snapshot, named somewhere |
| DATED_ORPHAN | 569 | dated snapshot, named nowhere |
| SCRATCH | 4320 | not a face (receipts / backups / hash scratch) |

undated faces: **2204** of 7463 (dated snapshots and scratch excluded from every verdict below)

## undated faces nothing names (370)

276 of them have no literal namesake at all (the name does not appear anywhere in source or prose, even without `.json`); 94 have their stem mentioned somewhere, which is what a runtime-composed path looks like from the outside.

51 of them carry a money-ish name: `results/e24_overlay_breath/latest-ladder20.json`、`results/e33_ladder_baseline/Q1-LADDER-VS-510300-WIN-2016.json`、`results/e33_ladder_baseline/Q1-LADDER-VS-510300-WIN-2018-X3.json`、`results/e33_ladder_baseline/Q1-LADDER-VS-510300-WIN-2018.json`、`results/e33_ladder_baseline/Q1-LADDER-VS-510300-WIN-FULL.json`、`results/e33_ladder_baseline/Q2-LADDER-CADENCE-WIN-2016.json`、`results/e33_ladder_baseline/Q2-LADDER-CADENCE-WIN-2018-X3.json`、`results/e33_ladder_baseline/Q2-LADDER-CADENCE-WIN-2018.json`、`results/e33_ladder_baseline/Q2-LADDER-CADENCE-WIN-FULL-X3.json`、`results/e33_ladder_baseline/Q3-LADDER-MEMBERSHIP-WIN-2016.json`、`results/e33_ladder_baseline/Q3-LADDER-MEMBERSHIP-WIN-2018-X3.json`、`results/e33_ladder_baseline/Q3-LADDER-MEMBERSHIP-WIN-FULL-X3.json`

- `results/e24_overlay_breath/latest-ladder20.json`  · money
- `results/e33_ladder_baseline/Q1-LADDER-VS-510300-WIN-2016.json`  · money
- `results/e33_ladder_baseline/Q1-LADDER-VS-510300-WIN-2018-X3.json`  · money
- `results/e33_ladder_baseline/Q1-LADDER-VS-510300-WIN-2018.json`  · money
- `results/e33_ladder_baseline/Q1-LADDER-VS-510300-WIN-FULL.json`  · money
- `results/e33_ladder_baseline/Q2-LADDER-CADENCE-WIN-2016.json`  · money
- `results/e33_ladder_baseline/Q2-LADDER-CADENCE-WIN-2018-X3.json`  · money
- `results/e33_ladder_baseline/Q2-LADDER-CADENCE-WIN-2018.json`  · money
- `results/e33_ladder_baseline/Q2-LADDER-CADENCE-WIN-FULL-X3.json`  · money
- `results/e33_ladder_baseline/Q3-LADDER-MEMBERSHIP-WIN-2016.json`  · money
- `results/e33_ladder_baseline/Q3-LADDER-MEMBERSHIP-WIN-2018-X3.json`  · money
- `results/e33_ladder_baseline/Q3-LADDER-MEMBERSHIP-WIN-FULL-X3.json`  · money
- `results/fund_trio_p1_ledger_reanchor.json`  · money
- `results/lowamp_deep_p1/cont_LAD-EDGE-EQ_deep_base.json`  · money
- `results/lowamp_deep_p1/cont_LAD-EDGE-EQ_deep_x2.json`  · money
- `results/lowamp_deep_p1/cont_LAD-EDGE_deep_base.json`  · money
- `results/lowamp_deep_p1/cont_LAD-EDGE_deep_x2.json`  · money
- `results/lowamp_p1/cont_LA-EDGE_deep_base.json`  · money
- `results/lowamp_p1/cont_LA-EDGE_deep_x2.json`  · money
- `results/lowamp_p1/cont_LA-EDGE_legacy_base.json`  · money
- `results/lowamp_p1/cont_LA-EDGE_legacy_x2.json`  · money
- `results/lowamp_p2/cont_LA-EDGE_deep_base.json`  · money
- `results/lowamp_p2/cont_LA-EDGE_deep_x2.json`  · money
- `results/lowamp_p2/cont_LA-EDGE_legacy_base.json`  · money
- `results/lowamp_p2/cont_LA-EDGE_legacy_x2.json`  · money

## written up but never wired (74)

- `results/e33_ladder_baseline/Q1-LADDER-VS-510300-WIN-FULL-X3.json` ← `research/digests/DIGEST-20261021-e34-ladder-followups.md`
- `results/etf_book_capacity_carry_n12.json` ← `research/ETF_CAPACITY_WITH_CARRY.md`
- `results/orders_ack_scan.bm-c.json` ← `research/R1927-BMC-SECOND-HOST-STANDDOWN.md`
- `results/qdii_premium_watch.json` ← `research/HANDOVER.md`、`research/memory-archive/202611.md`
- `results/trial_labor_w18/w18_judge_ledger_reanchor_r902.json` ← `research/HANDOVER.md`、`research/TRIAL_LABOR_W18_PREREG.md`
- `results/bench_census_commodity.json` ← `research/BENCH-VERDICT-BOOK.md`、`research/BENCH_COST_STAMP_CENSUS.md`
- `results/bench_census_index_futures.json` ← `research/BENCH-VERDICT-BOOK.md`、`research/BENCH_COST_STAMP_CENSUS.md`
- `results/bench_pair_bond_curve_60d.json` ← `research/BENCH-VERDICT-BOOK.md`、`research/BENCH_COST_STAMP_CENSUS.md`
- `results/bench_pair_commodity_60d.json` ← `research/BENCH-VERDICT-BOOK.md`、`research/BENCH_COST_STAMP_CENSUS.md`
- `results/bench_reversal_commodity_5d.json` ← `research/BENCH-VERDICT-BOOK.md`、`research/BENCH_COST_STAMP_CENSUS.md`
- `results/bench_reversal_index_5d.json` ← `research/BENCH-VERDICT-BOOK.md`、`research/BENCH_COST_STAMP_CENSUS.md`
- `results/bench_robust_donchian_index.json` ← `research/BENCH-VERDICT-BOOK.md`、`research/BENCH_COST_STAMP_CENSUS.md`
- `results/bench_robust_ma_index.json` ← `research/BENCH-VERDICT-BOOK.md`、`research/BENCH_COST_STAMP_CENSUS.md`
- `results/bench_robust_tsmom_commodity.json` ← `research/BENCH-VERDICT-BOOK.md`、`research/BENCH_COST_STAMP_CENSUS.md`
- `results/bench_trend_single_AU_long.json` ← `research/BENCH-VERDICT-BOOK.md`、`research/BENCH_COST_STAMP_CENSUS.md`

## named by exactly one source file (940, 66 money-ish)

One file naming a face is not a consumer: it is usually the producer. These are the first place to look when asking "is this number read?"

- `results/astock_veto_hedge_instrument.json` ← `scripts/astock_veto_hedge_instrument.py`
- `results/astock_veto_hedge_resize.json` ← `scripts/astock_veto_hedge_resize.py`
- `results/astock_veto_hedge_stability.json` ← `scripts/astock_veto_hedge_stability.py`
- `results/astock_veto_hedge_wait_ladder.json` ← `scripts/astock_veto_hedge_wait_ladder.py`
- `results/bench_ah_premium.json` ← `scripts/bench_ah_premium.py`
- `results/bench_excess_paired_test.json` ← `scripts/bench_excess_paired_test.py`
- `results/bench_ledger_donchian_exposure.json` ← `scripts/bench_ledger_donchian_exposure.py`
- `results/capital_marginal_road.json` ← `scripts/capital_marginal_road.py`
- `results/capital_placement_rent_audit.json` ← `scripts/capital_placement_rent_audit.py`
- `results/carry_entry_window_yield.json` ← `scripts/carry_entry_window_yield.py`
- `results/carry_im_same_rule.json` ← `scripts/carry_im_same_rule.py`
- `results/carry_three_lines_common_window.json` ← `scripts/carry_three_lines_common_window.py`
- `results/cash_shelf_total_return_audit.json` ← `scripts/cash_shelf_total_return_audit.py`
- `results/core_ddctl_probe.json` ← `scripts/cn_core_ddctl_p1.py`
- `results/cycle_position_census.json` ← `scripts/cycle_position_census.py`

`generated` 2026-11-28T11:59:43+08:00 · every count above is a face count, not a read count.
