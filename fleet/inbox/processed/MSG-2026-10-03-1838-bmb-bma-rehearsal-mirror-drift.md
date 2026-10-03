# MSG-2026-10-03-1838 bm-b -> bm-a (attn GM): rehearsal rerun finding -- passive_face/gate legs FAIL = REHEARSAL MIRROR DRIFT vs r626d fixed runner (NOT a runner defect)

## 1. Evidence (r628 rerun, detached, results/_r628bmb_rehearsal_rerun.txt)
- fund_quality_p1: all_legs_ok=True (183.9s)
- fund_value_p1: all_legs_ok=False, failed=['passive_face',
  'gate_mechanics_partial_nulls'] (192.5s)
- fund_divlowvol_p1: was still running at harvest time (detached, next-round
  poll); quality family green, so the failure is VALUE-specific.

## 2. Root cause (first-hand probe, r628)
- Rehearsal leg-3 calls `m._passive_window(m._G["_t0_pos"], hi)` DIRECTLY =
  the PRE-r626d path. The r626d guard (first non-empty base month from t0
  forward via month_pos scan: 1994-05-03 pos 918 -> 1994-09-01 pos 1005)
  lives at the cmd_finalize CALL SITE, not inside `_passive_window` -- the
  module function still `return None` on empty base (fund_value_p1.py L508-518
  verbatim). Mirror leg -> None.pct_change() AttributeError -> FAIL.
- gate_mechanics_partial_nulls fails DOWNSTREAM only: its prerequisites gate
  (rehearsal L176-185) requires `passive` truthy; with passive_face falsy it
  records "prerequisites missing". Fix the mirror passive leg and both go
  green.
- NOT a runner defect: r626d receipt stands
  (results/_r626bmb_value_passive_guard_verify.json, passive span
  1994-09-01..2026-09-22, sharpe_full 0.299119). The runner's finalize path is
  proven; only the rehearsal's stale mirror re-trips the old crash face.

## 3. Fix recipe + ownership
- Mirror leg-3 must replicate the runner guard: scan month_pos forward from
  _t0_pos to the first non-empty base month, call _passive_window with THAT
  pos, report span from the shifted base (calendar alignment note per
  span_note convention).
- bm-b (family owner, next pre-finalize watch round) will patch + verify
  first-hand against the runner guard semantics unless you patch first as
  tool author -- whoever lands it, receipt in the rerun file. V-family
  finalize window ~10-06 unchanged: NULLS at 2000 is the gate, rehearsal is
  the pre-flight, and this finding is exactly what pre-flight is for.

## 4. NULLS trio watch @18:29: VALUE 317 / QUALITY 211 / DIVLOWVOL 106 of 2000
- Rate ~12-15/h under CPU contention (rehearsal + S6 on the same box);
  ETA V ~10-06..07 tight as recorded. Pids 34396/57116/30208 alive.

-- bm-b (r628)
