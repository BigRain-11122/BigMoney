import json

# r406 bm-b: TRIAL-LABOR-W5-JUDGE shard done-flip (dual-face, r387/r389/r395 precedent).
# Entry done-flip deferred to judge-finalize receipt (w5_judge.json) per r386 W2 precedent.

POOL = "results/runnable_pool.json"
LANE = "results/runnable_pool.bm-b.json"

for path in (POOL, LANE):
    with open(path, encoding="utf-8") as fh:
        pool = json.load(fh)
    jud = next(e for e in pool["entries"] if e["id"] == "TRIAL-LABOR-W5-JUDGE")
    assert jud["status"] == "ready", f"{path}: judge status {jud['status']} != ready"
    assert jud["lane_owner"] == "bm-b", f"{path}: lane_owner {jud.get('lane_owner')} != bm-b"
    sh = jud["shards"][0]
    assert sh["key"] == "judge-0of1", f"{path}: shard key {sh['key']}"
    assert sh["status"] == "ready", f"{path}: shard status {sh['status']} != ready"
    assert sh.get("owner") == "bm-b", f"{path}: shard owner {sh.get('owner')} != bm-b"
    sh["status"] = "done"
    sh["done_at"] = "2026-09-29 03:13:57"
    sh["result_ref"] = (
        "results/trial_labor_w5/checkpoint/judge_shard_0of1.jsonl "
        "(372/372 cells, unique cell_id 372 == w5_screen survivors 372 verified r406; "
        "autofill claim 03:00:01 pid 1276 runner_sha 5a7173738d272eb6, "
        "last-write 03:13:57 clean exit; autofill 03:20 tick relaunch_cooldown = flip-lag window closed by this flip)"
    )
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(pool, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    # round-trip reload assert
    with open(path, encoding="utf-8") as fh:
        p2 = json.load(fh)
    j2 = next(e for e in p2["entries"] if e["id"] == "TRIAL-LABOR-W5-JUDGE")
    assert j2["shards"][0]["status"] == "done", f"{path}: reload shard not done"
    assert j2["shards"][0]["done_at"] == "2026-09-29 03:13:57"
    assert j2["status"] == "ready", f"{path}: entry status changed unexpectedly"
    assert j2["lane_owner"] == "bm-b"
    print(f"{path}: W5-JUDGE judge-0of1 ready->done OK")

print("dual-face shard done-flip complete; entry stays ready pending finalize receipt (w5_judge.json)")
