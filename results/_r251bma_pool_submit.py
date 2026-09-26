# r251 bm-a: pool submit CN-DIV-LOWVOL-ROT-P1 (T-73 s3 slice-2, prereg frozen
# R250 + R251 zero-run amendment commit af368f8e, runner selftest 0 FAIL
# same round; live loader probe all_ok on real corpora). Single-writer =
# this round (control plane).
import json
import time

P = "results/runnable_pool.json"
ENTRY = {
    "id": "CN-DIV-LOWVOL-ROT-P1",
    "ticket_ref": "T-2026-09-26-73 s3 slice-2 (CEO O-20260926-0926 CN-native combo models; bm-a lane)",
    "prereg_ref": ("research/CN_DIV_LOWVOL_ROT_PREREG.md (frozen R250 commit 83ecffbb; R251 zero-run "
                   "amendment af368f8e: T_joint 1861->1862 probe-authoritative, mismatch day = 512890 "
                   "fold-suspension bar, event-guard via DLP._adjust_split per r239 law; zero runs)"),
    "runner": "scripts/cn_div_lowvol_rot_p1.py",
    "runner_args": ["run"],
    "lane_owner": None,
    "priority": 1,
    "status": "ready",
    "entered_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    "data_gates": ("in-runner fail-closed exit 2: intersection T==1862 (2019-01-18..2026-09-22) + "
                   "A-only-within-window==['2021-10-22'] + B-only empty + zero NaN on timeline + "
                   "cutoff==2026-09-22 (D2 lockbox) + SEED_REGISTRY assert (cn_div_lowvol_rot_p1="
                   "20260980, registered AT R250 freeze commit) + zero-rebalance-evaluation sanity "
                   "(R240 law, warmup-aware) + finalize census gate (r188). Panel = in-repo corpus "
                   "twins data/daily/sh{510880,512890}.csv zero network; prices = DLP._adjust_split "
                   "post-event face (512890 factor 0.5); ADV20 = raw volume x close rolling-20. "
                   "Judge face x2 (side_cost_x2 whole-V2 doubled); 1% ADV day-queued fills with "
                   "fill_days counters; affordability loop (no negative cash); completion = sells "
                   "done AND (buys within one lot OR cash cannot buy one lot)."),
    "shards": [{
        "key": "divlowvolrot-0of1",
        "status": "ready",
        "owner": None,
        "owner_since": None,
        "checkpoint": ("results/cn_div_lowvol_rot/ckpt/*.npz per-unit (exact float64 resume, "
                       "date-drift refusal); landed marker = results/cn_div_lowvol_rot/p1_results.json "
                       "with ledger block; idempotent fast path exit 0 after finalize "
                       "(CN_DIV_LOWVOL_ROT_P1_REFINALIZE=1 = only redo); harvest = pool flip done by "
                       "next round per r244 landed-marker law"),
    }],
    "workers_plan": {"workers": 1,
                     "note": ("single finalize dependency chain (4 cells x3 faces -> nulls -> "
                              "baselines -> gates -> D6/regime columns); intersection panel is "
                              "2x1862 trivial; sims are O(T) daily loops; ~1-2 min single worker")},
    "note": None,
}

d = json.load(open(P, encoding="utf-8-sig"))
assert not any(e["id"] == ENTRY["id"] for e in d["entries"]), "already entered"
d["entries"].append(ENTRY)
d["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
tmp = P + ".tmp"
with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(d, fh, ensure_ascii=False, indent=1)
import os
os.replace(tmp, P)
d2 = json.load(open(P, encoding="utf-8-sig"))
mine = [e for e in d2["entries"] if e["id"] == "CN-DIV-LOWVOL-ROT-P1"][0]
print("pool submit OK:", mine["id"], mine["status"], "shard:", mine["shards"][0]["key"],
      "total entries:", len(d2["entries"]))
