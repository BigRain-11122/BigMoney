# r404 T-113 s1: one-shot runnable_pool worker_class schema migration
# (O-20260928-2210 data-locality honesty face). Provider-side GM window
# single-writer leg: lane_owner in {None,"","ANY"} -> self-contained
# (in-repo data, clone-and-run, any machine); named host -> bm-hosted
# (data physically on the host, e.g. full-A astock panel on bm-b).
# Idempotent: re-run keeps existing explicit worker_class fields.
import json, os, hashlib, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POOL = os.path.join(ROOT, "results", "runnable_pool.json")

def blob_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

with open(POOL, "rb") as fh:
    local_bytes = fh.read()
local_sha = blob_hash(local_bytes)
# r239 collision law: fetch fresh, compare origin blob before writing.
subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True)
r = subprocess.run(["git", "show", "origin/main:results/runnable_pool.json"],
                   cwd=ROOT, capture_output=True)
origin_same = (r.returncode == 0 and blob_hash(r.stdout) == local_sha)
print("origin pool == local pool:", origin_same)

pool = json.loads(local_bytes.decode("utf-8"))
changed = 0
for e in pool.get("entries", []):
    if e.get("worker_class"):
        continue
    lo = e.get("lane_owner")
    e["worker_class"] = ("self-contained"
                         if lo in (None, "", "ANY") else "bm-hosted")
    changed += 1
sc = pool.setdefault("schema", {})
sc["entries[].worker_class"] = (
    "O-20260928-2210 (T-113 s1): self-contained = in-repo data, "
    "clone-and-run on ANY machine; bm-hosted = data physically on the "
    "lane host (e.g. astock panel bm-b) -- workers honor data locality, "
    "no fake sharing; autofill._pick + Tools/pool_worker.py both read it")
out = json.dumps(pool, ensure_ascii=False, indent=1) + "\n"
json.loads(out)  # parse-verify before write-back (r185 law)
with open(POOL, "w", encoding="utf-8", newline="") as fh:
    fh.write(out)
print("entries migrated:", changed)
dist = {}
for e in pool["entries"]:
    dist[e["worker_class"]] = dist.get(e["worker_class"], 0) + 1
print("worker_class dist:", dist)
print("origin-drift-risk:", "none" if origin_same else "LOCAL AHEAD/DRIFT -> push may rebase")
