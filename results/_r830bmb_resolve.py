# -*- coding: utf-8 -*-
"""r830 bm-b push-race resolver (skill bigmoney-conflict-resolve; law r188/R208/r140/r185).

Context: rebase replay of r830 commit onto origin tip 4850cbcda. In a REBASE,
stage2(ours)=origin-side base blob, stage3(theirs)=replayed (mine) blob.
Recipes:
  results/compute_audit.json            rolling-ledger -> union history-type keys zero-loss, snapshot fields take-new(ts)
  results/lhb_update_status.json         snapshot      -> take-new whole doc by ts
  results/queue_head_collision_probe.json UNKNOWN->manually classified SNAPSHOT
        (probe full-output per run, regenerable, no append semantics; zero info loss: loser stays in git history)
        -> take-new by ts; tie -> ours(HEAD)=origin side per r140
"""
import json, subprocess, sys

FILES = [
    "results/compute_audit.json",
    "results/lhb_update_status.json",
    "results/queue_head_collision_probe.json",
]
LEDGER_KEYS = ("history", "launches", "transitions")


def stage_blob(path, n):
    out = subprocess.run(["git", "show", f":{n}:{path}"], capture_output=True, check=True).stdout
    return json.loads(out.decode("utf-8"))


def row_key(r):
    return json.dumps(r, sort_keys=True, ensure_ascii=False)


def ts_of(d):
    t = d.get("ts") or d.get("timestamp") or d.get("updated_at") or ""
    return str(t)


def resolve(path, cls):
    ours = stage_blob(path, 2)     # origin-side (rebase base)
    theirs = stage_blob(path, 3)  # my replayed commit
    if cls == "rolling-ledger":
        merged = dict(theirs if ts_of(theirs) >= ts_of(ours) else ours)  # snapshot fields take-new by ts
        for k in LEDGER_KEYS:
            a, b = ours.get(k) or [], theirs.get(k) or []
            seen, union = set(), []
            for r in a + b:
                kk = row_key(r)
                if kk not in seen:
                    seen.add(kk)
                    union.append(r)
            if union and isinstance(union[0], dict) and "ts" in union[0]:
                union.sort(key=lambda r: str(r.get("ts", "")))
            merged[k] = union
            la, lb, lm = len(a), len(b), len(merged[k])
            assert lm >= max(la, lb), f"union loss on {path}:{k} {la}|{lb}->{lm}"
        return merged
    if cls == "snapshot":
        return theirs if ts_of(theirs) > ts_of(ours) else ours  # tie->ours(HEAD)
    raise SystemExit(f"unhandled class {cls}")


plan = {
    FILES[0]: "rolling-ledger",
    FILES[1]: "snapshot",
    FILES[2]: "snapshot",  # manual classification: per-run probe full output (regenerable), documented in header
}
for p, c in plan.items():
    merged = resolve(p, c)
    text = json.dumps(merged, ensure_ascii=False, indent=1) + "\n"
    json.loads(text)  # r185: parse-validate before write-back
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(f"RESOLVED {p} class={c} ts_final={ts_of(merged)}")
print("resolver done: 3 files, zero-loss union + take-new snapshots, parse-validated")
