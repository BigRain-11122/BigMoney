# r387 bm-b W2-JUDGE entry done-flip (finalize receipt) + W1 finalize
# detach. w2_judge.json landed+verified: 404 judged, E[FP]=20.2, G2
# eligible 0, ledger prev 310810 + 404 = 311214 (chain linear). Queue
# condition for W1 finalize (cross-wave cumulative-N) now MET.
import json, os, datetime, subprocess

POOL = "results/runnable_pool.json"
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

d = json.load(open(r"results\trial_labor_w2\w2_judge.json", encoding="utf-8-sig"))
led = d["trials_ledger"]
assert led["batch"] == "TRIAL_LAB_W2_JUDGE" and led["total"] == 311214, led
assert d["n_judged_cells"] == 404, d["n_judged_cells"]
assert d["n_eligible_g2"] == 0, d["n_eligible_g2"]
assert d["evidence_cutoff"] == "2026-09-22"
print("w2_judge.json receipt verified: 404 judged, E[FP] face in log, "
      "G2 eligible 0, ledger total 311214")

# ---- entry done-flip (shared) ----
pool = json.load(open(POOL, encoding="utf-8-sig"))
for e in pool["entries"]:
    if e["id"] == "TRIAL-LABOR-W2-JUDGE":
        assert e["status"] == "ready", e["status"]
        e["status"] = "done"
        e["done_at"] = now
        e["done_note"] = (
            "r387 bm-b finalize receipt: judge-finalize detached pid 23800 "
            "(14:13:55, r386) landed ~14:40 -> w2_judge.json (404 judged "
            "cells, E[FP]=20.2, G2 eligible 0 -> [], family PBO faces, "
            "descriptive summary; ledger TRIAL_LAB_W2_JUDGE prev 310810 "
            "+ 404 = 311214 cross-wave linear) committed 200be873. "
            "Wave-2 funnel honest zero-registration. Intake face (D6 "
            "binding gate) lawful-zero path per prereg sec.4; TRIAL-* "
            "paper accounts face = zero eligible = none spawned."
        )
pool["updated_at"] = now
tmp = POOL + ".tmp"
with open(tmp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(pool, f, ensure_ascii=False, indent=1)
os.replace(tmp, POOL)

# ---- lane re-mirror (dual-face law, r387 pitlaw) ----
lp = "results/runnable_pool.bm-b.json"
payload = dict(pool)
payload["lane_machine"] = "bm-b"
ltmp = lp + ".tmp"
with open(ltmp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(payload, f, ensure_ascii=False, indent=1)
os.replace(ltmp, lp)

# ---- reload assertions (post-write, both faces) ----
pool2 = json.load(open(POOL, encoding="utf-8-sig"))
e2 = [x for x in pool2["entries"] if x["id"] == "TRIAL-LABOR-W2-JUDGE"][0]
assert e2["status"] == "done" and e2["shards"][0]["status"] == "done"
lane2 = json.load(open(lp, encoding="utf-8-sig"))
l2 = [x for x in lane2["entries"] if x["id"] == "TRIAL-LABOR-W2-JUDGE"][0]
assert l2["status"] == "done"
print("W2-JUDGE entry done-flip OK: shared+lane both done")

# ---- W1 finalize detach (r386 pitlaw: never inline; queue condition met) ----
log = "logs/w1_judge_finalize_r387.log"
with open(log, "w", encoding="utf-8", newline="\n") as f:
    f.write("=== TRIAL_LABOR_W1 judge-finalize (r387 detach) ===\n")
proc = subprocess.Popen(
    [r"C:\Program Files\Python311\python.exe", "-u",
     "scripts/trial_labor_w1.py", "judge-finalize"],
    stdout=open(log, "a", encoding="utf-8", newline="\n"),
    stderr=subprocess.STDOUT,
)
print("W1 judge-finalize detached: pid =", proc.pid,
      "| log =", log, "| n_trials snapshot should be 311214")
with open("results/_r387bmb_w1_finalize_pid.txt", "w") as f:
    f.write(str(proc.pid))
