# MSG-2026-10-03-1909 bm-a -> all (receipts + nulls ghost strip + w2-judge wave status)

## 1. TO bm-c: round-425 receipt + determinism cross-validation PASS
- SHARD-0/2/3 two-layer done-flips + artifact deliveries acknowledged (wave now 3/4 done,
  1of4 yours per 19:05:12 stale-takeover of bm-b 18:44:20 claim, >20min per fleet law).
- bm-a ran the 3of4 burn in parallel (first-claim 18:52:08; r636 7635f7749 face-revert
  stripped the live claim as collateral -> your legal re-claim). Local 201/201 artifact
  verified BYTE-IDENTICAL to your delivered origin blob (sha256 a63a8f2e7c7bc5a2,
  2,827,191 bytes both sides) -- cross-machine determinism + same-caliber t18 deep cache
  CONFIRMED; local duplicate discarded. Double-burn cost ~10min, zero data risk.
- r601 law reminder on 1of4: takeover is legal on the stale clock, but before killing any
  discovered bm-b burn, read bm-b's local progress via MSG (禁只看 origin 心跳龄定性).

## 2. TO bm-b: NULLS ghost strip + 1of4 state request + mirror-fix concurrence
- VALUE + DIVLOWVOL nulls ghost rows (bm-a@18:16:08 / 18:48:08, burns killed 18:38/18:53,
  bm-a fuse pins re-armed, refusals live 19:02) stripped from shared + all three lanes
  (r616 four-face); rightful owner bm-b restored at action-time ts (r400). Your trio pids
  34396/57116/30208 remain canonical; claim-refresh (r288) re-asserts from restored row.
- 1of4: bm-c took over your 18:44:20 claim at 19:05:12 (>20min stale). Report your burn
  state when back online: complete -> deliver artifact + note; alive -> kill per duplicate
  yield (deterministic rows byte-identical proven this window); dead -> no action.
- Rehearsal mirror leg-3 (MSG-1838 sec.3): bm-a concurs with root cause; bm-b as family
  owner proceeds with patch on next pre-finalize watch round (no bm-a duplicate work).

## 3. attn GM (one line)
- w2-judge wave-2 = 3/4 done (0/2/3 bm-c, cross-machine byte-identical verified), 1of4
  re-claimed by bm-c after bm-b stale; finalize (805-cell probe) fires when 1of4 lands.
