# O-2115 验收实况页（10-08 治理日证据包 · 可复跑自动再生）

- 生成：2026-10-04 06:34:06 · 视角：bm-c (shared-artifact aggregation, machine-agnostic rerun) · 验收日：2026-10-08
- 总判：**ALL_MET**（逐件见下；负结果如实照报）

## 件1 · T-145 PIT审计+解锁评估+首批基本面族prereg冻结 — MET

- face="pit_audit" · present=True · ref=results/fund_pit_audit/audit_results.json (bm-c 2026-10-02 21:21, structure PASS)
- face="unlock_eval" · present=True · n_unlock=7 · n_stay_locked=1 · ref=results/fund_h_unlock_eval.json (T-145 leg b)
- face="dataset_complete" · present=True · done_symbols=5224 · ref=results/fund_history_status.json (T-131)
- 族 FUND-VALUE-P1：prereg FROZEN=True · 池 6 面 done占比 83%
- 族 FUND-QUALITY-P1：prereg FROZEN=True · 池 4 面 done占比 75%
- 族 FUND-DIVLOWVOL-P1：prereg FROZEN=True · 池 4 面 done占比 75%

## 件2 · 深轴低振幅新家族prereg在池 — MET

- face="prereg_frozen" · present=True · ref=research/LOWAMP-DEEP-P1.md
- face="pool_state" · present=True · n_entries=10 · done_share=1.0 · by_status={"done": 10}

## 件3 · 千人wave-2判决面 — MET

> judged LANDED r444 -- honest NEGATIVE: eligible_g2=0 (E[FP]=40.25 @ nominal 5%), funnel does not survive G2 at thousand-scale

- face="w2_judge" · present=True · n_judge_cells=805 · n_eligible_g2=0 · n_stage1_survivors=806 · evidence_cutoff="2026-09-22" · ref=results/mass_trial/w2_judge.json + T-158 r444

## 件4 · 引擎火力分布新面孔占比 — MET

窗口（2026-10-02 21:15 起）三机 autofill 点火计数：**总 81 次**

| 类别 | 次数 |
|---|---|
| o2115_new | 58 |
| other_lines | 16 |
| perpetual_continuation | 7 |

**O-2115 新面孔占比 = 71.6%**（分母=窗口内全部点火）

| 机器 | 窗口内点火 | 分类 |
|---|---|---|
| bm-a | 37 | {"o2115_new": 27, "other_lines": 8, "perpetual_continuation": 2} |
| bm-b | 21 | {"o2115_new": 18, "other_lines": 3} |
| bm-c | 23 | {"o2115_new": 13, "other_lines": 5, "perpetual_continuation": 5} |

## 风险与待决旗

- **fund_trio_nulls_pool_state**：rightful burner = bm-b per MSG-1132/MSG-1155 division (r617-r620); off-caliber-era burns killed+discarded (r622/r629); finalize window 10-05..10-09 状态={"FUND-VALUE-P1-NULLS": "ready", "FUND-QUALITY-P1-NULLS": "ready", "FUND-DIVLOWVOL-P1-NULLS": "ready"}
- **pre_ruling_G_SEG**：G-SEG structural: monthly-freq chop=14<50 -> verdict=insufficient-sample before all gates; GM ruling pending (bm-a zero unilateral action, r633 MSG-2026-10-03-1720)
- **pre_ruling_VALUE_passive**：FUND-VALUE cmd_finalize passive-window crash (t0=1994-05-03 -> base_j=0); owner-fix = bm-b (r633 MSG-2026-10-03-1720)
- **n1_supply**：W116+ N1 supply assessment: O-2115 sec-2 supply priority = new-direction furnaces > perpetual N1 deep-dig (113 waves diminishing); fund-trio in flight -> N1 stays closed this window

---
再跑：`python scripts/o2115_acceptance_pack.py run` · 自检：`selftest` · 证据零网络零新判据，纯聚合面。
