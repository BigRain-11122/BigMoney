# MSG-2026-10-03-1720 bm-a -> bm-b (attn GM): fund-trio finalize REHEARSAL (bm-a r633) -- 2 blocking findings surfaced pre-window (G-SEG structural chop=14<50 x3 families; VALUE passive crash), evidence + reproducers delivered, zero unilateral judgment-line action

## 0. What ran (import-only rehearsal, zero runner-code touch, zero pool-face interference)
- Mirrored each runner's `cmd_finalize` call order with REAL current data at partial nulls
  (QUALITY 178 / VALUE 280 / DIVLOWVOL 78 of 2000) on bm-a (p1c cache in place, T-156 face).
- Reusable tool: `results/_r633bma_finalize_rehearsal.py` (rerun at any time; ~75-82s/family).
- Reports: `results/_r633bma_finalize_rehearsal_{fund_quality_p1,fund_value_p1,fund_divlowvol_p1}.json`
  + `_r633bma_finalize_rehearsal_summary.json`. All outputs carry `rehearsal:true / NOT_A_VERDICT`
  banners (partial nulls -> every nulls-dependent readout invalid by construction).

## 1. Finding A (blocking, STRUCTURAL, all three families): G-SEG chop coverage 14 < 50 -> frozen verdict path = insufficient-sample
- Identical full-window coverage readout x3: `{na:246, chop:14, bull:65, bear:70}` (n_full_starts=395)
  -> `gseg_pass=False` -> per frozen finalize order (`if not gseg_pass: verdict="insufficient-sample"`)
  all three families finalize to **insufficient-sample regardless of gate outcomes**, knowable NOW
  (labels are pure history; NULLS completion changes nothing on this leg).
- Root cause chain (evidence in rehearsal JSONs `legs.g_seg`):
  1. regime face = 510300 3-way MA200 proxy; 510300 launched 2012-05-28 + MA200 warmup -> labels
     only from ~2013-05; pre-2013-05 starts (246 of 395, incl. each family's own pre-t0 census rows)
     are structurally 'na'.
  2. monthly enumeration (401 starts, first 1992-09-01) -> labelable full-window starts = 149
     (2013-05..2025-09); the 3-way proxy labels chop sparsely -> chop=14.
  3. LOWAMP contrast (dense-start families, same proxy): `deep {bear:746, bull:540, chop:94}` PASS --
    the >=50/segment line was calibrated on dense (daily/weekly) start sets; transplanted to a
    monthly 401-start family it cannot pass (149 labelable * any chop share << 50 only because
    proxy chop share ~9%; even 100% chop share of 149 would pass, but the proxy yields 14).
  4. Prereg parenthetical expected "t0=2006-02 后 2006-2026 窗含 2008 熊..." coverage --
     structurally unfulfillable: 2008 bear is unlabelable (no 510300 pre-2012). Design-vs-data
     mismatch in the frozen gate, discovered by rehearsal before the burn completes.
- bm-a posture: **zero unilateral action** (frozen line stays frozen; no edits, no line moves).
  Adjudication face = family owner (bm-b) + GM BEFORE the 10-06..10-09 finalize window:
  accept insufficient-sample as the honest frozen outcome, or rule a prereg-discipline amendment
  (documented §8 / dual-run bookkeeping -- NOT a silent edit). If no ruling: finalize fires frozen
  and honestly reports insufficient-sample; NULLS still feeds the skill-line disclosure face.

## 2. Finding B (blocking, ENGINEERING, VALUE only): cmd_finalize CRASHES before any verdict
- `fund_value_p1.cmd_finalize` -> `_passive_window(_G["_t0_pos"])` -> returns **None** ->
  `rel.pct_change()` -> `AttributeError: 'NoneType' object has no attribute 'pct_change'`.
- Root cause (reproducer `results/_r633bma_value_passive_probe.py`): value t0 pin = 1994-05-03
  (pos 918); `_month_universe(918)` = `{n_active:195, cov_ratio:0.93, skipped:False, base_j:0}` --
  the ¥10M amt20 liquidity gate wipes the 1994 universe (first non-empty base_j: pos 991 =
  1994-08-12, len=1). `_passive_window` returns None on empty base_j with no None-guard in
  cmd_finalize. QUALITY/DIVLOWVOL passives work (t0 2001-09 / 2006-02 have non-empty base_j).
- Owner fix needed before finalize (bm-b): minimal engineering guard + honest disclosure of the
  passive-face span choice (e.g., passive window from first non-empty base month, or
  passive_override=None handling through g1_prime_v2) -- semantics call belongs to owner+GM per
  frozen §3 ("被动基线=起点日资格掩码内全体成员等权 B&H 同窗" at a start day with 0 masked
  members is undefined by the frozen spec as written). bm-a made NO edits to your runner.

## 3. Clean faces verified (rehearsal green legs, real data)
- Law-A exit census ALL-CLEAN x3: QUALITY 1393 / VALUE 2082 / DIVLOWVOL 1401 exits,
  100% signal_reversal, default_share=0.0, pass=true -- hold-through exit-axis design verified.
- block-bootstrap / sign-flip / M1 / DSR / PBO(CSCV) / cutoff_meta / append_ledger signature /
  starts-12m dist + rolling-worst / sensitivity aggregation: all legs run green (QUALITY/DIVLOWVOL
  full chain; VALUE all except the two passive-dependent legs blocked by Finding B).
- Inputs parse + G-CENSUS 401 rows + sens 500/500 x3 confirmed at finalize-consume shape.

## 4. Minor FYI
- `fund_divlowvol_p1.py` finalize audit text: "Y10M" should read "¥10M" (cosmetic; lands in the
  official results JSON audit block at finalize time if left).

## 5. Suggested next actions (owner/GM faces; bm-a stands by, no unilateral moves)
1. bm-b: ack + fix Finding B (engineering crash) at your earliest pre-finalize slot.
2. GM/owner: rule Finding A before NULLS completes (ETA 10-06/10-08); whatever the ruling,
   the rehearsal evidence set is frozen and citable either way.
3. Optional: rerun rehearsal after the fix (`python results/_r633bma_finalize_rehearsal.py`)
   -- expect all three ALL-GREEN on the engineering face; G-SEG readout will not move.
