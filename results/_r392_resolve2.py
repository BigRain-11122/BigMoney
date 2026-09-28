"""r392 resolve #2: rebase stop #3 (commit 897e7ee2) batch -- 5 files.

Skill: bigmoney-conflict-resolve. Stage semantics (REBASE): stage2=ours=
upstream(origin+replayed), stage3=theirs=commit-being-replayed(bm-b r391).
  CODELY.md            memory-union (R208/r212/D-20260927-09):
                       byte-prefix-identity assertion on both sides, then
                       direct-concat of BOTH suffixes (no line dedupe).
  compute_audit.json   rolling-ledger (r188/R208): history union zero-loss,
                       latest take-new by NESTED latest.ts (r311 deep-scan).
  runnable_pool.json   pool-entry-done-union (r312): per-id union, done
                       absorbs (take the done side's record); same-status ->
                       shard-level union, live claim (fresher owner_since)
                       wins; one-side-only entry kept; flip evidence gate
                       authority note honored (V2-P1 done = mine, W1 x4 done
                       = origin bm-a, W4 live claim = origin 17:10:06).
  token_usage.json     snapshot (R216): take-new by top-level 'generated'.
  processed/MSG-1622   DU (UNKNOWN->manual): origin never had the file (no
                       tree hit, no history); it exists only on my line ->
                       keep mine (processing trail, zero loss).
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

# ---------------- compute_audit.json: rolling-ledger union ------------------
P = "results/compute_audit.json"
A, B = blob_json(2, P), blob_json(3, P)
ha, hb = A.get("history", []), B.get("history", [])
seen, union = set(), []
for row in ha + hb:
    key = json.dumps(row, sort_keys=True, ensure_ascii=False)
    if key not in seen:
        seen.add(key)
        union.append(row)
union.sort(key=lambda r: r.get("ts", ""))
la = (A.get("latest") or {}).get("ts") or ""
lb = (B.get("latest") or {}).get("ts") or ""
newer_side = A if lb <= la else B
merged = {"history": union, "latest": newer_side.get("latest")}
json.loads(json.dumps(merged))
open(P, "w", encoding="utf-8").write(json.dumps(
    merged, ensure_ascii=False, indent=1))
print(f"compute_audit: |A|={len(ha)} |B|={len(hb)} -> union={len(union)} "
      f"rows; latest take-new {'ours' if lb <= la else 'theirs'} "
      f"(A.ts={la} B.ts={lb})")

# ---------------- runnable_pool.json: per-entry done-union ------------------
P = "results/runnable_pool.json"
A, B = blob_json(2, P), blob_json(3, P)
ea = {e["id"]: e for e in A["entries"]}
eb = {e["id"]: e for e in B["entries"]}
merged_entries = []
log = []
for e in A["entries"]:
    k = e["id"]
    if k not in eb:
        merged_entries.append(e)
        continue
    o = eb[k]
    if e["status"] == o["status"]:
        # shard-level union: done absorbs; else live claim (fresher
        # owner_since / non-null) wins; textual extras from the richer dict
        if e["status"] == "done" or o["status"] == "done":
            pick = e if e["status"] == "done" else o
        else:
            se, so = e["shards"][0], o["shards"][0]
            pick = (e if (se.get("owner_since") or "") >=
                    (so.get("owner_since") or "") else o)
            # richer textual fields from the non-picked side must not be
            # lost: fill missing keys only (never overwrite picked values)
        for fkey, fval in ((e if pick is o else o).items()):
            if fkey not in pick:
                pick[fkey] = fval
        merged_entries.append(pick)
        log.append(f"{k}: same-status -> "
                   f"{'ours' if pick is e else 'theirs'} (claim/ts winner)")
    elif "done" in (e["status"], o["status"]):
        pick = e if e["status"] == "done" else o
        other = o if pick is e else e
        for fkey, fval in other.items():
            if fkey not in pick:
                pick[fkey] = fval
        merged_entries.append(pick)
        log.append(f"{k}: DONE-ABSORB -> {'ours' if pick is e else 'theirs'}")
    else:
        merged_entries.append(e if e["status"] == "ready" else o)
        log.append(f"{k}: status race -> keep higher-progress side")
for e in B["entries"]:
    if e["id"] not in ea:
        merged_entries.append(e)
        log.append(f"{e['id']}: theirs-only entry kept verbatim")
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
