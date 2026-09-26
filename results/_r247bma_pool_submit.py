# r247 bm-a: pool submit CN-REV-TILT-P1 (T-73 s3 slice-1, prereg frozen R245/R246,
# runner selftest 30/30 green same round). Single-writer = this round (control plane).
import json
import time

P = "results/runnable_pool.json"
ENTRY = {
    "id": "CN-REV-TILT-P1",
    "ticket_ref": "T-2026-09-26-73 s3 slice-1 (CEO O-20260926-0926 CN-native combo models; bm-a lane)",
    "prereg_ref": "research/CN_REV_TILT_PREREG.md (frozen R245, ZERO runs; R246 pre-run amendments: seed cn_rev_tilt_p1=20260930 registered + s2 evidence_cutoff=2026-09-22 backfilled)",
    "runner": "scripts/cn_rev_tilt_p1.py",
    "runner_args": ["run"],
    "lane_owner": None,
    "priority": 1,
    "status": "ready",
    "entered_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    "data_gates": ("in-runner fail-closed exit 2: P1C cache cutoff==2026-09-22 + T>=8000 + "
                   "N>=5000 (D2 forward lockbox; 09-23/24 bars excluded) + SEED_REGISTRY assert "
                   "(cn_rev_tilt_p1=20260930) + never-invested all-cash sanity (R240 law) + "
                   "finalize census gate (r188). Panel = Money02/data/cache/p1c_stock close.npy "
                   "(machine-local, zero network, t73_s2 load_close single source). Close-only "
                   "face -> V1 13.041bp/side flat cost (no ADV, prereg s3.2 honest)."),
    "shards": [{
        "key": "cnrev-0of1",
        "status": "ready",
        "owner": None,
        "owner_since": None,
        "checkpoint": ("results/cn_rev_tilt/ckpt/*.npz per-unit (exact float64 resume, date-drift "
                       "refusal); landed marker = results/cn_rev_tilt/p1_results.json with ledger "
                       "block; idempotent fast path exit 0 after finalize "
                       "(CN_REV_TILT_P1_REFINALIZE=1 = only redo); harvest = pool flip done by "
                       "next round per r244 landed-marker law"),
    }],
    "workers_plan": {"workers": 1,
                     "note": ("single finalize dependency chain (bare cells -> 252d trail -> tilt "
                              "cells -> gates); ~2GB panel+signal peak; sims are incremental-held "
                              "O(20)/day; workers>1 would duplicate the 368MB panel load")},
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
mine = [e for e in d2["entries"] if e["id"] == "CN-REV-TILT-P1"][0]
print("pool submit OK:", mine["id"], mine["status"], "shard:", mine["shards"][0]["key"],
      "total entries:", len(d2["entries"]))
