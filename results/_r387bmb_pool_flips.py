# r387 bm-b pool flip:
# TRIAL-LABOR-W1-JUDGE shard done-flip only (burn complete 149/149
# 14:25:22, checkpoint+log evidence, autofill claim 14:23:24/34 12-worker
# pool 111s wall); judge-finalize QUEUED behind W2 finalize in-flight
# pid 23800 (started 14:13:55): DSR n_trials snapshots at finalize start
# (w2.py:1566 / w1.py:1450) + per-cell g1 internal ledger_head scans ->
# concurrent finalize = mid-run head drift + cumulative-N cross-miss
# (TRIAL_LABOR_LAW sec.4). W1 finalize detach fires on w2_judge.json
# receipt (this round tail or next round). Entry done-flip deferred to
# w1_judge.json receipt (r386 precedent).
import json, os, datetime

POOL = "results/runnable_pool.json"
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ---- burn-completion evidence (W1 shard) ----
ckpt = "results/trial_labor_w1/checkpoint/judge_shard_0of1.jsonl"
n_rows = 0
ids = set()
with open(ckpt, encoding="utf-8") as fh:
    for ln in fh:
        if ln.strip():
            n_rows += 1
            ids.add(json.loads(ln)["cell_id"])
scr = json.load(open("results/trial_labor_w1/w1_screen.json", encoding="utf-8"))
sv = scr.get("survivors")
n_sv = len(sv) if isinstance(sv, list) else int(sv or 0)
missing = [c for c in (sv if isinstance(sv, list) else [])
           if f"JUDGE|{c}" not in ids]
assert n_sv == 149 and n_rows >= 149 and not missing, (n_sv, n_rows, missing[:3])
print("W1 shard burn evidence: checkpoint rows =", n_rows, "/ survivors =", n_sv)

# W2 finalize still in flight -> queue note lawful (do not detach W1 yet)
log2 = "logs/w2_judge_finalize_r386.log"
head = open(log2, encoding="utf-8").read().strip().splitlines()[-1]
assert "judge-finalize" in head, head
print("W2 finalize log head:", head)

# ---- flip ----
pool = json.load(open(POOL, encoding="utf-8-sig"))
for e in pool["entries"]:
    if e["id"] == "TRIAL-LABOR-W1-JUDGE":
        assert e["status"] == "ready", e["status"]
        for sh in e["shards"]:
            assert sh["key"] == "judge-0of1", sh["key"]
            assert sh["status"] in ("waiting", "running"), sh["status"]
            sh["status"] = "done"
            sh["done_at"] = now
            sh["result_ref"] = (
                ckpt + f" ({n_rows}/{n_sv} cells, autofill log "
                "autofill_TRIAL-LABOR-W1-JUDGE.log shard complete 14:25:22, "
                "claim 14:23:34 pid 18172 12-worker pool)"
            )
        e["note"] = (
            "r387 bm-b: burn complete 149/149 @14:25:22 (shard done-flip this "
            "round); judge-finalize QUEUED behind W2 finalize in-flight "
            "pid 23800 (14:13:55): DSR n_trials start-snapshot + per-cell "
            "g1 internal ledger scans -> sequential finalize required for "
            "cross-wave cumulative-N (TRIAL_LABOR_LAW sec.4). W1 finalize "
            "detach fires on w2_judge.json receipt. Entry done-flip "
            "deferred to w1_judge.json receipt (r386 precedent)."
        )
pool["updated_at"] = now

tmp = POOL + ".tmp"
with open(tmp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(pool, f, ensure_ascii=False, indent=1)
os.replace(tmp, POOL)

pool2 = json.load(open(POOL, encoding="utf-8-sig"))
e2 = [x for x in pool2["entries"] if x["id"] == "TRIAL-LABOR-W1-JUDGE"][0]
sh = e2["shards"][0]
print(f"flip OK: entry={e2['status']} shard={sh['status']}")
