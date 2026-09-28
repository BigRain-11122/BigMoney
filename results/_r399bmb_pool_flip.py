import json
import sys

POOL = "results/runnable_pool.json"
ENTRY = "T104-GRID-S3-DUALFACE-P1"

with open(POOL, encoding="utf-8") as f:
    pool = json.load(f)

hit = None
for e in pool["entries"]:
    if e.get("id") == ENTRY:
        hit = e
        break
if hit is None:
    print("ENTRY ABSENT")
    sys.exit(1)
if hit.get("status") != "waiting":
    print("status not waiting, refusing:", hit.get("status"))
    sys.exit(1)

hit["status"] = "ready"
hit["ready_at"] = "2026-09-28 21:5x"
hit["prereg_ref"] = (
    "research/etf_ops/GRID_DUALFACE_P1_PREREG.md FROZEN r399 commit "
    "a03887474 (salvage of dead r399 session draft; probe facts "
    "independently re-verified 5/5 members rows/last/mono + minute feed "
    "1970x5 window 09-15..09-28); SEED_REGISTRY grid_dualface_p1=20295500 "
    "registered same commit (R250 one-step; pair-derivation vs innovation "
    "20295000 first-element distinct, census_unc precedent)")
hit["data_gates"] = (
    "ALL GATES GREEN r399 bm-b: (1) prereg FROZEN a03887474 precedes runner "
    "build (R99); (2) runner + selftest hermetic PASS (lifecycle fixture: "
    "sets/anchors/reanchor/multi-level fills/blocked_entry/blocked_exit "
    "roll/guard/nulls/fee/minute equivalence/grammar; double-run "
    "byte-identical) + real-data timing probe 1.5s/member incl 200-null "
    "engine (results/_r399bmb_grid_timing_probe.py); (3) minute-feed "
    "archive v1.3 five-symbol verified 1970 rows each 09-15..09-28 15:00 "
    "(runner minute leg = local archive only, zero network); (4) RAM "
    "11.7GB free > 4GB floor. IN-RUNNER fail-closed: anchor face mismatch "
    "= exit 2; grammar sha mismatch = exit 2. JUDGED FACE x2; K=200 "
    "same-mask random-trigger-day nulls = FIRST gate (T-78 lesson "
    "product). LIVE PAPER GRID ENGINE fires 10-01 = separate face per "
    "ticket. Finalize = owner follow-up round after pool shards complete "
    "(python scripts/grid_dualface_backtest.py finalize; r253 "
    "redo-echo guard in-runner)")
hit["shards"][0]["checkpoint"] = (
    "results/etf_ops/grid_shard_<member>.json x5 + "
    "results/etf_ops/grid_rounds_<member>.csv x5 + "
    "results/etf_ops/grid_series/*.npy (30 cells x 2 faces)")
hit["workers_plan"]["note"] = (
    "single shard 'run' (all five members sequential, per-member "
    "idempotent skip; measured 1.5s/member -> light batch); dual-face: "
    "deep face = daily-granularity grid state machine on T-22 lineage "
    "(HONEST DISCLOSURE: daily granularity undercounts intraday fills = "
    "lower-bound reading disclosed in prereg s1); minute face = LOCAL "
    "forward-accumulated archive data/minute_feed v1.3 (descriptive "
    "equivalence only, never a judgement; zero network)")

with open(POOL, "w", encoding="utf-8") as f:
    json.dump(pool, f, ensure_ascii=False, indent=1)
print("FLIPPED", ENTRY, "-> ready")
