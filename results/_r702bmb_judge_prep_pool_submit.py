"""r702 bm-b: submit PERPETUAL-N2-W15-JUDGE-PREP to the bm-b pool lane
file (single-writer law: bm-b appends ONLY its own lane). One-shot
in-runner gates (freeze + state-file + RAM) make the entry safe for any
healthy machine; lane_owner=null per multi-machine legality."""
import json
import io
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANE = os.path.join(REPO, "results", "runnable_pool.bm-b.json")

ENTRY = {
    "id": "PERPETUAL-N2-W15-JUDGE-PREP",
    "ticket_ref": ("T-133 s2 standing supply ticket (O-2026-09-30-2340 "
                   "CEO standing-face order, prereg sec.0 authorization "
                   "face, no new signature needed); sec.9.1 freeze "
                   "window 2026-10-05 r702 bm-b (slice-4 judge legs + "
                   "sec.9.1 append + berth registration same freeze "
                   "commit)"),
    "prereg_ref": ("research/PERPETUAL_N2_W15_PREREG.md sec.9.1 (FROZEN "
                   "2026-10-05 r702 bm-b freeze commit; judge berth "
                   "perpetual_n2_w15_judge=545_500 band 545_500..545_999 "
                   "ADMIT receipt _r702bmb_n2_judge_band_gate.json; "
                   "banned gate exit 0 "
                   "_r702bmb_n2_judge_banned_gate.json)"),
    "consumer_plan": ("N2-W15 judge chain step 1: judge-prep (collapse "
                      "0.999 leg-L daily returns -> N_judge + dual-leg "
                      "starts/passive precompute) -> n2_w15_judge_state."
                      "json one-shot -> 12-shard judge burn submissions "
                      "(separate pool entries once N_judge is fixed) -> "
                      "judge-finalize (ledger append PERPETUAL-N2-W15-"
                      "JUDGE) -> prereg sec.7/sec.8 backfill"),
    "runner": "scripts/perpetual_faces_n2.py",
    "runner_args": ["judge-prep"],
    "lane_owner": None,
    "priority": 1,
    "status": "ready",
    "entered_at": "2026-10-05 01:0x",
    "data_gates": ("in-runner: sec.9.1 FREEZE-GATE (judge berth "
                   "registered) + screen product trials_ledger gate + "
                   "survivors-present gate + dual-leg census gates "
                   "(FROZEN_CENSUS L/D) + one-shot state-file gate + "
                   "RAM gate 4GB r354/r691 (honest rc2 refuse while the "
                   "trio NULLS occupy RAM until ~10-06T17; re-claim "
                   "when the window opens)"),
    "shards": [{"key": "n2w15judge-prep-0of1", "status": "ready",
                "owner": None, "owner_since": None,
                "checkpoint": "results/n2_w15/n2_w15_judge_state.json"}],
}


def main() -> int:
    with io.open(LANE, encoding="utf-8") as f:
        pool = json.load(f)
    ents = pool["entries"] if isinstance(pool, dict) else pool
    if any(e.get("id") == ENTRY["id"] for e in ents):
        print("already present -- idempotent no-op")
        return 0
    ents.append(ENTRY)
    with io.open(LANE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(pool, f, ensure_ascii=False, indent=1)
    print(f"submitted: {ENTRY['id']} -> results/runnable_pool.bm-b.json "
          f"({len(ents)} entries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
