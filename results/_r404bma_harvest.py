# r404 bm-a pool-side harvest (T-113 s1 second half): consume closed-ok
# worker claim files -> flip pool shards done (workers never write the
# pool; the harvest face does, single-writer window inside a round).
# Formal Tools/pool_harvest.py (selftest family) lands next slice --
# this one-shot script leaves the exact recipe + audit trail.
import json, os, subprocess, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POOL = os.path.join(ROOT, "results", "runnable_pool.json")
CLAIMS = os.path.join(ROOT, "results", "pool_claims")
LEDGER = os.path.join(ROOT, "results", "pool_worker_ledger.jsonl")

def blob(b):
    return hashlib.sha256(b).hexdigest()

with open(POOL, "rb") as fh:
    local = fh.read()
subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True)
r = subprocess.run(["git", "show", "origin/main:results/runnable_pool.json"],
                   cwd=ROOT, capture_output=True)
print("origin==local:", r.returncode == 0 and blob(r.stdout) == blob(local))

pool = json.loads(local.decode("utf-8"))
ledger = [json.loads(x) for x in open(LEDGER, encoding="utf-8")] \
    if os.path.exists(LEDGER) else []
flips = []
for d in os.listdir(CLAIMS) if os.path.isdir(CLAIMS) else []:
    ed = os.path.join(CLAIMS, d)
    if not os.path.isdir(ed):
        continue
    for fn in os.listdir(ed):
        if not fn.endswith(".json"):
            continue
        with open(os.path.join(ed, fn), encoding="utf-8") as fh:
            c = json.load(fh)
        if c.get("state") != "closed" or c.get("outcome") != "ok":
            continue
        # find the pool entry+shard
        for e in pool.get("entries", []):
            if e["id"] != d:
                continue
            for sh in e.get("shards", []):
                if sh.get("key") + "." + c.get("machine_id", "") not in fn:
                    continue
                if sh.get("status") == "done":
                    continue  # already harvested
                sh["status"] = "done"
                sh["owner"] = c.get("machine_id", "worker")
                sh["owner_since"] = c.get("closed_at")
                sh["done_note"] = (f"worker harvest r404: claim "
                                   f"{fn} outcome=ok exit={c.get('exit_code')}")
                lr = [x for x in ledger if x.get("entry") == e["id"]
                      and x.get("shard") == sh["key"]
                      and x.get("machine_id") == c.get("machine_id")]
                if lr:
                    sh["done_evidence"] = (f"ledger row ts={lr[-1]['ts']} "
                                           f"core_hours={lr[-1]['core_hours']}")
                flips.append((e["id"], sh["key"]))
            # entry-level flip when ALL shards done (pool law)
            if e.get("status") == "ready" and e.get("shards") and \
               all(s.get("status") == "done" for s in e["shards"]):
                e["status"] = "done"
                e["done_ts"] = c.get("closed_at")
                e["done_note"] = "all shards done via worker harvest (O-2210)"
                flips.append((e["id"], "<entry>"))
print("flips:", flips)
out = json.dumps(pool, ensure_ascii=False, indent=1) + "\n"
json.loads(out)
with open(POOL, "w", encoding="utf-8", newline="") as fh:
    fh.write(out)
print("harvest write-back OK (parse-verified)")
