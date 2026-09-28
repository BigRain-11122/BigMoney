"""r392 resolve #1: results/compute_audit.json (rebase stop #2, commit 294f91c4).

Skill: bigmoney-conflict-resolve / class=rolling-ledger (r188/R208).
Recipe: union both blobs on history key (zero row loss), snapshot field
`latest` take-new by NESTED ts (latest.ts deep-scan, r311/r319 laws).
Rebase stage-2/3 semantics: stage2=ours=upstream(origin+replayed), stage3=
theirs=commit-being-replayed(bm-b snapshot).
"""
import json
import subprocess

PATH = "results/compute_audit.json"


def blob(stage):
    b = subprocess.run(["git", "show", f":{stage}:{PATH}"],
                       capture_output=True).stdout
    return json.loads(b)


ours, theirs = blob(2), blob(3)

# -- union history (zero row loss; identity = full row content) -------------
ha, hb = ours.get("history", []), theirs.get("history", [])
seen, union = set(), []
for row in ha + hb:
    key = json.dumps(row, sort_keys=True, ensure_ascii=False)
    if key not in seen:
        seen.add(key)
        union.append(row)
union.sort(key=lambda r: r.get("ts", ""))
assert len(union) == len(seen), "union dedupe invariant"
n_a, n_b = len(ha), len(hb)
lost = len(seen) - max(n_a, n_b)
print(f"history union: |A|={n_a} |B|={n_b} -> |A u B|={len(union)} "
      f"(rows only in B preserved: {len(seen) - n_a}, only in A: {len(seen) - n_b})")

# -- latest take-new by nested ts (deep-scan; existence probe first) --------
la, lb = ours.get("latest") or {}, theirs.get("latest") or {}
ts_a = la.get("ts") if isinstance(la, dict) else None
ts_b = lb.get("ts") if isinstance(lb, dict) else None
newer = ours if (ts_b or "") <= (ts_a or "") else theirs
# ^ strict take-new: compare nested latest.ts; equal/missing -> origin side
print(f"latest.ts ours={ts_a} theirs={ts_b} -> take-new side="
      f"{'ours(origin)' if (ts_b or '') <= (ts_a or '') else 'theirs(bm-b)'}")
latest = (ours if (ts_b or "") <= (ts_a or "") else theirs).get("latest")

merged = {"history": union, "latest": latest}
json.loads(json.dumps(merged))          # parse-verify before write (r185)
with open(PATH, "w", encoding="utf-8") as fh:
    json.dump(merged, fh, ensure_ascii=False, indent=1)
print("written:", PATH)
