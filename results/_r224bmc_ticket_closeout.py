"""r224 bm-c ticket close-out flips: T-19 (G6 verified) + T-118 (W7 wave chain closed by bm-b).

Both flips are evidence-backed:
- T-19: G6 live-run proof verified this round -- 6/6 member paper states carry
  forward_guard.consolidation block (registry 21ev/19sym bit-exact read-only),
  crossing_rows_n=0 across all members, as_of fresh 2026-09-29 (multi new-bar rounds
  since r129 pending face). Ticket remaining faces per progress_r129: none post-G6.
- T-118: W7 wave full chain closed by bm-b (r422 merge-back: GENERATE n=2834 +
  SCREEN done + JUDGE 284 cells TOTAL-ZERO G1 verdict) + CEO-REPORT-WAVE7 landed;
  pool entries TRIAL-LABOR-W7-{GENERATE,SCREEN,JUDGE} all status=done.
"""
import json

FLIPS = [
    {
        "path": "fleet/tasks/T-2026-09-24-19-P1.json",
        "progress_key": "progress_r224_bmc_closeout",
        "progress": (
            "r224 bm-c: G6 live-run proof VERIFIED and ticket closed done. "
            "Evidence: 6/6 results/paper/*_paper.json carry forward_guard.enabled=true + "
            "consolidation block (registry 21ev/19sym bit-exact, read-only source), "
            "crossing_rows_n=0 all members (boundary-inclusive s5 semantics), "
            "as_of 2026-09-29 15:49 (every live.paper round refreshes the guard -- multiple "
            "new-bar rounds since the r129 pending face). Stage-2a paper forward-protection "
            "remains bm-a T-20 G6 relay HOLD per O-1325 (separate lane, not this ticket)."
        ),
        "result_ref": (
            "results/paper/*_paper.json forward_guard.consolidation (6/6, crossing 0) + "
            "research/shortline spec faces per stage-2b closure r81"
        ),
    },
    {
        "path": "fleet/tasks/T-2026-09-29-118-P1.json",
        "progress_key": "progress_r224_bmc_closeout",
        "progress": (
            "r224 bm-c: W7 wave full-chain close-out verified, ticket closed done. "
            "Chain receipts: GENERATE done (n=3704 distinct raw 5000 per r420 / harvest "
            "w7_candidates.json), SCREEN done, JUDGE done 284 cells TOTAL-ZERO G1 verdict "
            "(bm-b r422 merge-back landed main; CEO-REPORT-WAVE7-20260929.md in docs/trial_labor/); "
            "pool TRIAL-LABOR-W7-{GENERATE,SCREEN,JUDGE} all status=done in runnable_pool.json. "
            "Zero G2 survivors = lawful falsification outcome per prereg sec.5."
        ),
        "result_ref": (
            "docs/trial_labor/CEO-REPORT-WAVE7-20260929.md + results/trial_labor_w7/ "
            "(w7 candidates/screen/judge faces) + runnable_pool W7 rows done x3"
        ),
    },
]

for f in FLIPS:
    with open(f["path"], encoding="utf-8") as fh:
        d = json.load(fh)
    assert d.get("status") == "claimed", f'{f["path"]}: unexpected status {d.get("status")}'
    d["status"] = "done"
    d[f["progress_key"]] = f["progress"]
    d["result_ref"] = f["result_ref"]
    with open(f["path"], "w", encoding="utf-8") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("FLIPPED done:", f["path"])
print("OK 2 flips")
