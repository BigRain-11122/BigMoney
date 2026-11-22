# Face consumer census

evidence set: `results/**/*.json` (depth <= 2), readable against `scripts/`, `Tools/`, `docs/`, `research/`

| tier | faces | what it means |
| --- | --- | --- |
| CODE_MULTI | 688 | >=2 source files name this face |
| CODE_SINGLE | 808 | exactly one source file names it (producer or lone reader) |
| PROSE_ONLY | 60 | only docs/research names it |
| ORPHAN | 334 | nothing names it (undated only) |
| DATED_CODE | 354 | dated snapshot, named somewhere |
| DATED_ORPHAN | 493 | dated snapshot, named nowhere |
| SCRATCH | 4097 | not a face (receipts / backups / hash scratch) |

undated faces: **1890** of 6834 (dated snapshots and scratch excluded from every verdict below)

## undated faces nothing names (334)

241 of them have no literal namesake at all (the name does not appear anywhere in source or prose, even without `.json`); 93 have their stem mentioned somewhere, which is what a runtime-composed path looks like from the outside.

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

## written up but never wired (60)

- `results/e33_ladder_baseline/Q1-LADDER-VS-510300-WIN-FULL-X3.json` ← `research/digests/DIGEST-20261021-e34-ladder-followups.md`
- `results/etf_book_capacity_carry_n12.json` ← `research/ETF_CAPACITY_WITH_CARRY.md`
- `results/orders_ack_scan.bm-c.json` ← `research/R1927-BMC-SECOND-HOST-STANDDOWN.md`
- `results/qdii_premium_watch.json` ← `research/HANDOVER.md`、`research/memory-archive/202611.md`
- `results/trial_labor_w18/w18_judge_ledger_reanchor_r902.json` ← `research/HANDOVER.md`、`research/TRIAL_LABOR_W18_PREREG.md`
- `results/ce_admission/CE-ADMISSION-B1.json` ← `research/AUDIT-20260926-S2-ADJUDICATION.md`、`research/CE_ADMISSION_INTAKE_B1_PREREG.md`
- `results/cloudf_face_row.json` ← `research/HANDOVER.md`
- `results/csdn_probe_t57_s1_slice2.json` ← `research/digests/DIGEST-20260925-t57-s1-slice2.md`
- `results/csdn_probe_t57_s1_slice3.json` ← `research/digests/DIGEST-20260925-t57-s1-slice3.md`
- `results/csdn_probe_t57_s1_slice4.json` ← `research/digests/DIGEST-20260925-t57-s1-slice4.md`
- `results/csdn_probe_t57_s1_slice4b.json` ← `research/digests/DIGEST-20260925-t57-s1-slice4.md`
- `results/csdn_probe_t57_s1_slice5.json` ← `research/digests/DIGEST-20260925-t57-s1-slice5.md`
- `results/d19_watermark.bm-c.json` ← `research/D19_WATERMARK_V2.md`
- `results/div_lowvol_rot_probe.json` ← `research/CN_DIV_LOWVOL_ROT_PREREG.md`
- `results/e34_cadence_rolling/CADENCE-ROLLING-3Y-X3.json` ← `research/digests/DIGEST-20261021-e35-broad-book-screens.md`

## named by exactly one source file (808, 40 money-ish)

One file naming a face is not a consumer: it is usually the producer. These are the first place to look when asking "is this number read?"

- `results/capital_placement.json` ← `scripts/capital_placement.py`
- `results/capital_union_decision.json` ← `scripts/capital_union_decision.py`
- `results/core_ddctl_probe.json` ← `scripts/cn_core_ddctl_p1.py`
- `results/cycle_position_census.json` ← `scripts/cycle_position_census.py`
- `results/e33_ladder_baseline/Q2-LADDER-CADENCE-WIN-FULL.json` ← `scripts/e33_ladder_census.py`
- `results/e33_ladder_baseline/Q3-LADDER-MEMBERSHIP-WIN-2018.json` ← `scripts/e33_ladder_census.py`
- `results/e33_ladder_baseline/Q3-LADDER-MEMBERSHIP-WIN-FULL.json` ← `scripts/e33_ladder_census.py`
- `results/e33_ladder_census.json` ← `scripts/e33_ladder_census.py`
- `results/etf_book_buffer_price_of_size.json` ← `scripts/etf_book_buffer_price_of_size.py`
- `results/etf_book_capacity_carry.json` ← `scripts/etf_book_capacity_carry.py`
- `results/etf_book_drawdown_guard.json` ← `scripts/etf_book_drawdown_guard.py`
- `results/etf_book_exposure_ladder.json` ← `scripts/etf_book_exposure_ladder.py`
- `results/etf_book_forward/CARRY_fee_free.json` ← `scripts/etf_book_forward.py`
- `results/etf_book_lot_ladder.json` ← `scripts/etf_book_lot_ladder.py`
- `results/etf_book_premium_phases.json` ← `scripts/etf_book_premium_phases.py`

`generated` 2026-11-22T15:15:12+08:00 · every count above is a face count, not a read count.
