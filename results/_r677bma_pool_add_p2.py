# -*- coding: utf-8 -*-
"""r677 bm-a: add THEME-JUDGE-P2 pool entry (T-169 s3) to runnable_pool.json.
Surgical append: read -> append -> write; verify prior entries intact."""
import json, os, time

POOL = os.path.join("results", "runnable_pool.json")
with open(POOL, encoding="utf-8") as fh:
    pool = json.load(fh)
n_before = len(pool["entries"])
ids_before = [e["id"] for e in pool["entries"]]
assert "THEME-JUDGE-P2" not in ids_before, "entry already present"

now = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
entry = {
    "id": "THEME-JUDGE-P2",
    "ticket_ref": ("T-2026-10-04-169-P1 s3 (claimed bm-a r676; s1 prereg "
                   "FROZEN r676 + s2 runner r677 selftest 23/23 incl "
                   "mirror-fidelity vs P1 worker; E24-ii deep-break redirect "
                   "face, order-chain reserved bl=0.75)"),
    "prereg_ref": ("research/THEME_JUDGE_P2.md FROZEN v1.0 r676 "
                   "(banned_direction_gate ADMIT rc0; D6 probe ADMIT "
                   "max|corr|=0.3682; seed band theme_judge_p2_nulls="
                   "20589000 [20589000,20591000) net gap 2000 receipt; "
                   "closed_family_check zero-hit)"),
    "runner": "scripts/theme_judge_p2.py",
    "runner_args": ["run"],
    "lane_owner": None,
    "priority": 1,
    "status": "ready",
    "entered_at": now,
    "worker_class": "self-contained",
    "workers_plan": {"workers": 26, "priority": "BelowNormal"},
    "data_gates": ("in-runner fail-closed sec.2 six gates (census sha16 "
                   "51b1b8226afc74b1 identity + dedup 1822/97 + drop gates 0 "
                   "+ seed band extent-aware disjoint + COST_X1 0.0013041 "
                   "single-source + twin 48/48 price identity) + checkpoint "
                   "digest binding (stale-digest frags ignored; empty-ks "
                   "frags never count as done r670 guard) + exit-reason "
                   "census gate at finalize (P2 gate at 0 illegal per "
                   "sec.0.6); evidence_cutoff 2026-09-22 lockbox; "
                   "POST-FINALIZE POOL FLIP REQUIRED SAME WINDOW (r668 "
                   "autofill re-burn loop law)"),
    "data_deps": ["results/theme_ring/theme_events_v03_algorithmic.json",
                  "data/daily/"],
    "shards": [{
        "key": "theme-judge-p2-burn-0of1",
        "status": "ready",
        "checkpoint": ("results/theme_judge_p2/nulls_frags/ per-chunk "
                       "fragments (digest-bound done-key skip, non-empty-ks "
                       "guard) + burn_state.json completion marker; "
                       "finalize = owner-side separate step after burn done "
                       "(gates + ledger + attrition row + pool flip r668)"),
    }],
}
pool["entries"].append(entry)
pool["updated_at"] = now
with open(POOL, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(pool, fh, ensure_ascii=False, indent=1)

# post-write verification (fresh read)
with open(POOL, encoding="utf-8") as fh:
    pool2 = json.load(fh)
ids_after = [e["id"] for e in pool2["entries"]]
assert ids_after[:n_before] == ids_before, "prior entries mutated"
assert "THEME-JUDGE-P2" in ids_after
e2 = [e for e in pool2["entries"] if e["id"] == "THEME-JUDGE-P2"][0]
assert e2["data_deps"] == entry["data_deps"]
print("POOL-ENTRY-ADDED", e2["id"], "status", e2["status"], "at", now)
