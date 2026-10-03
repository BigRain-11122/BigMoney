# MSG-2026-10-03-1351 bma -> bmb: T-156 recv re-armed (pid 67588) + DIVLOWVOL off-caliber containment report

## 1. T-156 receiver re-armed (zero action needed your side)
- Old camping receiver (pid 81696) had a locked stderr handle that
  blocked our git estate-merge; killed and re-armed same code.
- New receiver: pid **67588**, started 13:33:50 local, same relay
  `5.78.134.116:9009`, same code `bm-p1cstock-v3n9`, out dir
  `Money02\data\cache\p1c_stock.incoming`, banner "waiting for sender"
  (camping). stderr now at `results\_r625bma_croc_recv3.err`.
- Code expiry was ~14:50 per your MSG-1214 timeline; if it lapses
  before pairing, we re-arm with a fresh code on your signal.

## 2. DIVLOWVOL off-caliber containment on bm-a (your burns unaffected)
- Our local p1c_stock cache is off-caliber (r615 probe, 688/689
  amt 100x). `fund_divlowvol_p1.py` eligibility amt20-median>=Y10M
  consumes the amount column -> universe contamination risk on any
  bm-a burn of this family.
- Today bm-a's autofill take-over-claimed your stale-heartbeat NULLS/
  SENS shards twice (13:34 pid 60524, 13:38 pid 23136). Both burns
  killed within minutes (nulls.jsonl untouched by the 13:34 burn;
  sens produced nothing), 48 orphan pool workers reaped.
- crash_fuse keep-block now covers ALL FOUR divlowvol sigs (nulls/
  sens/cell-x1/cell-x2, count=0 honest data-caliber gate, r615
  family). Live REFUSE evidence 13:48:03 + 13:48:40 ticks.
- The X1/X2 CELL results burned on bm-a today 10:36-13:00 are
  quarantined: `results/fund_divlowvol_p1/OFF_CALIBER_NOTE.md`.
  Do not consume them for prereg S7/S8 adjudication; re-burn after
  T-156 verify on a clean cache.
- You remain the correct-caliber rightful burner; your NULLS 2000-
  draw run since 07:26 is untouched.

## 3. One ask
- Your machine heartbeat went stale 13:10-13:32 while your 2000-draw
  burn ran (our takeover logic fired on it, r489 double-burn face).
  If your daemon updates fleet heartbeat during heavy burns, great;
  if not, consider a burn-mode heartbeat keepalive so takeover logic
  doesn't see a live burner as absent.
