"""r393 resolve #5: second-rebase stop #3 (commit 047c6dd7, my round-391) -- 3 files.

Skill: bigmoney-conflict-resolve (same recipes as _r392_resolve2, trimmed
to THIS stop's conflict set; compute_audit.json auto-merged this round so
its section is intentionally absent -- stage blobs only exist for
conflicted paths).
  CODELY.md        memory-union (R208/r212/D-20260927-09): byte-prefix
                   assertion both sides, then direct-concat of BOTH
                   suffixes (no line dedupe).
  runnable_pool    pool-entry-done-union (r312): per-id union, done absorbs,
                   same-status -> shard owner_since fresher claim wins,
                   fill-missing-keys from losing side, one-side entries kept.
  token_usage      snapshot (R216): take-new by top-level 'generated'.
"""
import json
import subprocess


def blob_bytes(stage, path):
    return subprocess.run(["git", "show", f":{stage}:{path}"],
                          capture_output=True).stdout


def blob_json(stage, path):
    return json.loads(blob_bytes(stage, path))


# ---------------- CODELY.md: memory-union ---------------------------------
P = "CODELY.md"
base = blob_bytes(1, P)
a = blob_bytes(2, P)
b = blob_bytes(3, P)
assert a.startswith(base), "CODELY.md ours is NOT base+append (in-place edit?)"
assert b.startswith(base), "CODELY.md theirs is NOT base+append (in-place edit?)"
merged = base + a[len(base):] + b[len(base):]
open(P, "wb").write(merged)
print(f"CODELY.md: base={len(base)}B + ours-suffix={len(a)-len(base)}B "
      f"+ theirs-suffix={len(b)-len(base)}B -> {len(merged)}B (zero loss)")

# ---------------- runnable_pool.json: per-entry done-union -----------------
P = "results/runnable_pool.json"
A, B = blob_json(2, P), blob_json(3, P)
ea = {e["id"]: e for e in A["entries"]}
eb = {e["id"]: e for e in B["entries"]}
merged_entries, log = [], []
for e in A["entries"]:
    k = e["id"]
    if k not in eb:
        merged_entries.append(e)
        continue
    o = eb[k]
    if e["status"] == o["status"]:
        if e["status"] == "done" or o["status"] == "done":
            pick = e if e["status"] == "done" else o
        else:
            se, so = e["shards"][0], o["shards"][0]
            pick = (e if (se.get("owner_since") or "") >=
                    (so.get("owner_since") or "") else o)
        for fkey, fval in ((e if pick is o else o).items()):
            if fkey not in pick:
                pick[fkey] = fval
        merged_entries.append(pick)
        log.append(f"{k}:same->{'A' if pick is e else 'B'}")
    elif "done" in (e["status"], o["status"]):
        pick = e if e["status"] == "done" else o
        other = o if pick is e else e
        for fkey, fval in other.items():
            if fkey not in pick:
                pick[fkey] = fval
        merged_entries.append(pick)
        log.append(f"{k}:DONE->{'A' if pick is e else 'B'}")
    else:
        merged_entries.append(e if e["status"] == "ready" else o)
        log.append(f"{k}:race")
for e in B["entries"]:
    if e["id"] not in ea:
        merged_entries.append(e)
        log.append(f"{e['id']}:B-only")
top = {k: v for k, v in A.items() if k != "entries"}
top["updated_at"] = max(A.get("updated_at", ""), B.get("updated_at", ""))
top["entries"] = merged_entries
json.loads(json.dumps(top))
open(P, "w", encoding="utf-8").write(json.dumps(
    top, ensure_ascii=False, indent=1))
print("runnable_pool:", "; ".join(log))

# ---------------- token_usage.json: snapshot take-new -----------------------
P = "results/token_usage.json"
A, B = blob_json(2, P), blob_json(3, P)
ga, gb = A.get("generated", ""), B.get("generated", "")
newer = A if gb <= ga else B
open(P, "w", encoding="utf-8").write(json.dumps(
    newer, ensure_ascii=False, indent=1))
print(f"token_usage: take-new {'ours' if newer is A else 'theirs'} "
      f"(A.generated={ga} B.generated={gb})")
print("resolve5 done")
