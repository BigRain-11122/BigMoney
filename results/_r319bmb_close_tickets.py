"""R319 bm-b: close tickets T-89 and T-90 (all deliverables landed)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "fleet" / "tasks"
NOW = "2026-09-27 12:05"

UPDATES = {
    "T-2026-09-26-89-P1.json": {
        "status": "done",
        "done_at": NOW,
        "progress_r319_bmb": (
            "R319 bm-b: slice-3 DELIVERED -- attack-corps supply acceleration "
            "memo landed to GM queue as M-20260927-01 in research/GM_REVIEW_MEMOS.md "
            "(status PENDING): bull-specialist supply lanes to queue front (wave-1 "
            "momentum trio #81/#82/#83 prereg first, 35-library trend schools next), "
            "evidence-hardened = PROSPECT 0/22 attack candidates (slice-1 finalize) + "
            "T-90 ring2 routing negative all regimes + ring4 seat vacancy + "
            "SCHOOL_SUPPLY_S1 queue #1-#5 all judged-negative (zero in-flight "
            "candidates = zero exclusion cost); queue re-order execution = GM face "
            "per O-20260927-0752 sec.2, zero law-touch before signature. Slices 1/2/3 "
            "all delivered -> ticket closed; requeue adjudication tracked by "
            "M-20260927-01 PENDING row + self_review aging face."
        ),
        "result_ref": (
            "slice-1 finalize: results/prospect_regime_segments.json + "
            "research/shortline/prospect_regime_segments_results.csv (528 rows) + "
            "MARKET_STAGE_TABLE 22x2 rows (bm-b r318) | slice-2 standing table: "
            "research/MARKET_STAGE_TABLE.md v1.0 (bm-a R303) | slice-3 GM memo: "
            "research/GM_REVIEW_MEMOS.md M-20260927-01 (bm-b r319) | post_review rows "
            "T-89-S1-PROSPECT-SEGMENTS-FINALIZE + T-89-S3-ATTACK-SUPPLY-MEMO registered"
        ),
    },
    "T-2026-09-27-90-P1.json": {
        "status": "done",
        "done_at": NOW,
        "progress_r319_bmb": (
            "R319 bm-b: deliverable-4 LANDED -- monthly four-piece chain-health "
            "section wired into scripts/monthly_briefing.py section six "
            "(1-current-state + 2-switch-events + 3-broken-ring-scan + "
            "4-preference-face-progress; single-source consumption of "
            "results/decision_chain_e2e.json verdict/ring_table/seat_vacancy + "
            "research/DECISION_CHAIN_LEDGER.md version rows + preference prereg glob; "
            "honest missing-file branches on every input); selftest 19/19 incl five "
            "new chain-health legs; live-fire BRIEF-202609.md regenerated with real "
            "v1.1 numbers; DECISION_CHAIN_LEDGER v1.1 verdict record-flipped "
            "PENDING->LANDED (bookkeeping only, criteria untouched). All four ticket "
            "deliverables complete (prereg v1.1 r310/r311; frozen judgments in "
            "finalize; chain verdict + four-ring localization r318; monthly wiring "
            "r319). Iteration series continues per O-20260927-0809 (b)/(e) via the "
            "append-only ledger + trigger evaluation (broken-ring localization fired; "
            "preference v4 landing / corps seat fill / calibration revision = "
            "next-version triggers); next-version prereg = new GM-signed ticket per "
            "P1-signature law -- this ticket closes as the v1 baseline proof."
        ),
        "result_ref": (
            "prereg: research/DECISION_CHAIN_E2E_P1.md v1.1 frozen (r310/r311, "
            "GM RULING MSG-20260927-0814 re-freeze) | runner+batch: "
            "scripts/decision_chain_e2e.py + 9 X2 pool shards (r312-r318) | verdict: "
            "results/decision_chain_e2e.json + research/DECISION_CHAIN_LEDGER.md "
            "v1.1 LANDED (r318 finalize, r319 ledger flip) | deliverable-4: "
            "scripts/monthly_briefing.py chain-health section + "
            "results/briefings/BRIEF-202609.md (r319) | post_review rows "
            "T-90-V1-E2E-FINALIZE + T-90-D4-CHAIN-HEALTH-WIRING registered"
        ),
    },
}


def main():
    for fname, patch in UPDATES.items():
        p = TASKS / fname
        d = json.loads(p.read_text(encoding="utf-8"))
        if d.get("status") == "done":
            print(f"skip (already done): {fname}")
            continue
        for k, v in patch.items():
            d[k] = v
        p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n",
                     encoding="utf-8")
        print(f"closed: {fname} (status={d['status']}, done_at={d['done_at']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
