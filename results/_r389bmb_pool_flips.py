# r389 bm-b pool flips (r386 paradigm, dual-face sync per r387 law):
# TRIAL-LABOR-W3-JUDGE shard done-flip ONLY (burn complete 513/513,
# runner claim 15:00:01 pid 4604, checkpoint last-write 15:13:44,
# runner exited clean); entry done-flip DEFERRED to finalize receipt
# (w3_judge.json) per r386 W2 precedent; judge-finalize detached
# in-flight pid 28400 @15:21:53 (logs/w3_judge_finalize_r389.log,
# r386 detach law; serial law r387: no other same-chain finalize active,
# W2 landed r387 + W1 landed r388 verified before detach).
import json, os, datetime

POOL = "results/runnable_pool.json"
LANE = "results/runnable_pool.bm-b.json"
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ---- burn-completion evidence (W3 shard) ----
ckpt = "results/trial_labor_w3/checkpoint/judge_shard_0of1.jsonl"
ids = set()
n_rows = 0
with open(ckpt, encoding="utf-8") as fh:
    for ln in fh:
        if ln.strip():
            n_rows += 1
            ids.add(json.loads(ln)["cell_id"])
scr = json.load(open("results/trial_labor_w3/w3_screen.json", encoding="utf-8"))
sv = scr.get("survivors")
n_sv = len(sv) if isinstance(sv, list) else int(sv or 0)
missing = [c for c in (sv if isinstance(sv, list) else [])
           if f"JUDGE|{c}" not in ids]
assert n_sv == 513 and n_rows >= 513 and not missing, (n_sv, n_rows, missing[:3])
print("W3 shard burn evidence: checkpoint rows =", n_rows,
      "/ survivors =", n_sv, "missing =", len(missing))

RESULT_REF = (ckpt + " (513/513 cells, autofill claim 15:00:01 pid 4604 "
              "runner_sha 8fedac0cdf63bc36, last-write 15:13:44 clean exit)")
NOTE = ("r389 bm-b: burn complete 513/513 @15:13:44 (shard done-flip this "
        "round); judge-finalize detached in-flight pid 28400 @15:21:53 "
        "(log logs/w3_judge_finalize_r389.log, r386 detach law) -- entry "
        "done-flip deferred to finalize receipt (w3_judge.json). Siblings "
        "stay waiting single-burn no-stack + r369 serial (MASS x4/DC-V2/"
        "W4-JUDGE); same-chain finalize serial law r387 honored (W2 landed "
        "r387, W1 landed r388, no other finalize active at detach).")

def flip(path):
    pool = json.load(open(path, encoding="utf-8-sig"))
    for e in pool["entries"]:
        if e["id"] == "TRIAL-LABOR-W3-JUDGE":
            assert e["status"] == "ready", (path, e["status"])
            for sh in e["shards"]:
                assert sh["key"] == "judge-0of1" and sh["status"] == "waiting", \
                    (path, sh["key"], sh["status"])
                sh["status"] = "done"
                sh["done_at"] = now
                sh["result_ref"] = RESULT_REF
            e["note"] = NOTE
    pool["updated_at"] = now
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(pool, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)
    pool2 = json.load(open(path, encoding="utf-8-sig"))
    e2 = [x for x in pool2["entries"] if x["id"] == "TRIAL-LABOR-W3-JUDGE"][0]
    sh = e2["shards"][0]
    print(f"flip OK {path}: entry={e2['status']} shard={sh['status']}")

flip(POOL)
flip(LANE)
