"""r668 bm-a THEME-JUDGE-P1 pool entry append (single-writer coordinated append;
json.loads self-proof after write per state-write law)."""
import json
import time

POOL = "results/runnable_pool.json"
now = time.strftime("%Y-%m-%d %H:%M:%S")

d = json.load(open(POOL, encoding="utf-8"))
assert not any(e.get("id") == "THEME-JUDGE-P1" for e in d["entries"]), \
    "entry already present"
d["entries"].append({
    "id": "THEME-JUDGE-P1",
    "ticket_ref": ("T-2026-10-04-167-P1 s3 (claimed bm-a r666; s1 probe "
                   "r666 + s2 prereg FROZEN r667; queue-never-empty standing "
                   "line after moneyflow-IC blocked + G2 stage-2 closure)"),
    "prereg_ref": ("research/THEME_JUDGE_P1.md FROZEN v1.0 r667 "
                   "(banned_direction_gate ADMIT rc0; D6 probe ADMIT "
                   "max|corr|=0.3682; seed band theme_judge_p1_nulls=20585000 "
                   "disjoint; panel probe r668 all-green digest 663f1f11)"),
    "runner": "scripts/theme_judge_p1.py",
    "runner_args": ["run"],
    "lane_owner": None,
    "priority": 1,
    "status": "ready",
    "entered_at": now,
    "worker_class": "self-contained",
    "workers_plan": {"workers": 26, "priority": "BelowNormal"},
    "data_gates": ("in-runner fail-closed sec.2 six gates (census sha16 "
                   "51b1b8226afc74b1 identity + dedup 1822/97 + drop gates "
                   "0 + seed band disjoint + COST_X1 0.0013041 single-source "
                   "+ twin 48/48 price identity) + checkpoint digest binding "
                   "(stale-digest rows ignored) + exit-reason census gate at "
                   "finalize; evidence_cutoff 2026-09-22 lockbox (wide-panel "
                   "real tail, two-caliber disclosure)"),
    "shards": [{
        "key": "theme-judge-p1-burn-0of1",
        "status": "ready",
        "owner": None,
        "owner_since": None,
        "checkpoint": ("results/theme_judge_p1/nulls_frags/ per-chunk "
                       "fragments (digest-bound done-key skip) + "
                       "burn_state.json completion marker; finalize = "
                       "owner-side separate step after burn done (gates + "
                       "ledger + attrition row)"),
    }],
})
with open(POOL, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(d, fh, ensure_ascii=False, indent=1)
chk = json.load(open(POOL, encoding="utf-8"))
n = sum(1 for e in chk["entries"] if e.get("id") == "THEME-JUDGE-P1")
print(json.dumps({"appended": "THEME-JUDGE-P1", "n_entries": len(chk["entries"]),
                  "self_proof_count": n, "entered_at": now}))
assert n == 1
