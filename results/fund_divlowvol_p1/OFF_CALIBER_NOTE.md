# OFF-CALIBER QUARANTINE NOTE (r625 bm-a, 2026-10-03 14:0x)

## Scope
`cells_DIVLOWVOL-YIELDVOL_x1.jsonl`, `cont_DIVLOWVOL-YIELDVOL_x1.json`,
`cells_DIVLOWVOL-YIELDVOL_x2.jsonl`, `cont_DIVLOWVOL-YIELDVOL_x2.json`,
`nulls.jsonl` (partial, 2370B) in this directory, burned on **bm-a**
2026-10-03 10:36-13:56.

## Why quarantined
- bm-a's local `Money02/data/cache/p1c_stock` npy cache is CONFIRMED
  OFF-CALIBER (r615 probe `results/_r615bma_688_probe.json`, 2-source):
  688xxx/689xxx volume/amount stored at 100x raw units.
- `fund_divlowvol_p1.py` eligibility gate `amt20-median >= Y10M`
  (frozen liquidity floor, sec.2) consumes the **amount** column ->
  cold 688/689 stars with true amt20 below the floor pass the gate at
  100x -> phantom universe members -> X1/X2 cell results and the nulls
  partial run on this machine are NOT caliber-trustworthy.
- Cell rows carry no member lists, so the zero-68x probe
  (`results/_r625bma_x12_probe.py`) is structural-blind, not evidence.

## Containment already in place
- SENS burn killed 13:41 (pid 60524 NULLS), 13:56 (pid 23136 SENS);
  orphan ProcessPool workers reaped 14:05 (45).
- crash_fuse keep-block on all four divlowvol sigs (nulls / sens /
  cell-x1 / cell-x2), count=0 honest data-caliber gate (r625) --
  cleared ONLY after T-156 p1c_stock TRANSFER+verify (fleet decision)
  or runner edit (fix-first auto-clear).
- bm-b = correct-caliber rightful burner (its NULLS 2000-draw run
  since 07:26 is unaffected).

## Disposition
- DO NOT consume x1/x2 cell metrics for prereg S7/S8 adjudication
  until re-burned on a verified-caliber cache (post-T-156).
- nulls.jsonl rows from the bm-a window must be discarded on the
  next correct-caliber burn (same r615 "bad rows discarded" handling).

- Addendum r625 close-out: the killed SENS burn (13:38-13:47) had appended 10 off-caliber rows to sens.jsonl (7->17); excised pre-push via HEAD~1 restore (7 rows, zero-origin-harm window, r615 precedent).

## Addendum (r632 bm-a, 2026-10-03 16:5x): X1/X2 caliber verdict -- canonical paths CLEAN, "until re-burned" disposition SUPERSEDED

- The x1/x2 canonical paths now carry **bm-b correct-caliber products** (bm-b burn done 11:36:04; restored at r622 claw fixup a5c2b5108; x2 verdict 401/401 delivered bm-b r617 a4b1d8029). Live files == origin blobs (67fc9ff0 / de6d95b5, verified r632).
- The r625 "DO NOT consume x1/x2 until re-burned" line applied to MY off-caliber leftovers -- those live only in `quarantine_offcaliber_20261003/` (retained as evidence per MSG-1155). **No re-burn needed; pool X1/X2 entries `done` == correct state.** Canonical cells/sens ARE consumable for prereg §7/§8 finalize.
- Nulls face: MY off-caliber partial (2370B) was **never committed/pushed** (file history 15 commits, 0 via bm-a) -- shared nulls.jsonl rows are 100% bm-b correct-caliber. The "bad rows discarded" step has nothing to discard on origin; **no bm-b receipt required before family finalize** (contrast: VALUE nulls r615 case, where bad rows did reach origin).
- Sens face: 500/500 ALL PASS (r630, `sens_acceptance.json`).
- Caliber contrast evidence (quarantine vs canonical, x1): identical 401-key window sets; 335 rows identical; **66 rows diverge in 24m-tail metrics only** (ret_24m/sharpe_24m/dd_24m) -- quarantine copy confirmed genuine off-caliber; universe-membership stats identical (contamination surface = late-window 24m segment, not gate universe in this face).
- Evidence probe: `results/_r632bma_divlowvol_cells_caliber_verdict.json`.
- Family finalize (window >=10-09 pre-open) now waits only on the NULLS 2000-draw completion (bm-b in-flight, ETA 10-06/10-08).
