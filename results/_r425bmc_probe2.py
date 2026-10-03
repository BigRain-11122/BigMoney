"""_r425bmc_probe2.py -- bm-c r425 deep probe for SHARD-0 done-flip adoption.
Read-only: (1) full raw entries of the 4 W2-JUDGE shards in shared pool;
(2) lane mirror judge faces; (3) autofill_state face; (4) live python cmdlines;
(5) pool_worker ledger tail; (6) ckpt last-row shape (SHARD-0 outcome evidence).
"""
import json, os, subprocess, sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
os.chdir(REPO)


def load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


print("=== shared runnable_pool.json judge entries (FULL RAW) ===")
pool = load("results/runnable_pool.json")
entries = pool if isinstance(pool, list) else pool.get("entries", [])
for e in entries:
    if "W2-JUDGE-SHARD" in str(e.get("id", "")):
        print(json.dumps(e, ensure_ascii=False, indent=1))

print("=== lane mirror runnable_pool.bm-c.json judge faces ===")
lane = load("results/runnable_pool.bm-c.json")
s = json.dumps(lane, ensure_ascii=False)
# find any dict fragments mentioning W2-JUDGE-SHARD
def walk(o, path=""):
    if isinstance(o, dict):
        if any("W2-JUDGE-SHARD" in str(v) for v in o.values()):
            print(path, json.dumps(o, ensure_ascii=False)[:800])
        for k, v in o.items():
            walk(v, path + "/" + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, path + "[%d]" % i)
walk(lane)

print("=== autofill_state.bm-c.json ===")
print(json.dumps(load("results/autofill_state.bm-c.json"), ensure_ascii=False, indent=1)[:1500])

print("=== pool_worker_ledger tail ===")
lp = "results/pool_worker_ledger.jsonl"
if os.path.exists(lp):
    lines = open(lp, encoding="utf-8").read().strip().splitlines()
    for ln in lines[-4:]:
        print(ln[:400])
else:
    print("missing")

print("=== ckpt SHARD-0 last row + row shape ===")
with open("results/mass_trial/w2_judge_shard_0of4.jsonl", encoding="utf-8") as fh:
    lines = fh.read().strip().splitlines()
print("rows=%d" % len(lines))
print("first:", lines[0][:300])
print("last :", lines[-1][:300])

print("=== live python cmdlines ===")
import psutil
for p in psutil.process_iter(["pid", "name", "cmdline", "create_time"]):
    if (p.info["name"] or "").lower().startswith("python"):
        print("pid=%d ct=%s :: %s" % (p.info["pid"],
              __import__("datetime").datetime.fromtimestamp(p.info["create_time"]).strftime("%H:%M:%S"),
              " ".join(p.info["cmdline"] or [])[:200]))
