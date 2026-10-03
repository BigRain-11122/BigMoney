"""r645 bm-a pick-3 (stale churn-absorb replay) resolver per MSG-0612 newer-wins.

Pick 3 replays an OLDER satengine daemon snapshot; the rebased pick-2 already
absorbed fresher daemon writes (staged during the pick-2 conflict continue).
Recipes: face/state json = snapshot deep-ts take-new (R208/r311 deep-probe);
history jsonl = append-log line-level union zero-loss (r188).
Stage law r351: :2: = base side (rebased HEAD, fresher), :3: = replayed pick-3
(stale churn).
"""
import json
import re
import subprocess

TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")


def stage_bytes(stage, path):
    r = subprocess.run(["git", "show", stage + path], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"stage read fail {stage}{path}: {r.stderr.decode()[:200]}")
    return r.stdout


def deep_ts(obj):
    best = None
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and TS_RE.match(v):
                cand = v.replace(" ", "T")
                if best is None or cand > best:
                    best = cand
            sub = deep_ts(v)
            if sub and (best is None or sub > best):
                best = sub
    elif isinstance(obj, list):
        for v in obj:
            sub = deep_ts(v)
            if sub and (best is None or sub > best):
                best = sub
    return best


def resolve_snapshot(path, label):
    b2 = stage_bytes(":2:", path)
    b3 = stage_bytes(":3:", path)
    j2 = json.loads(b2.decode("utf-8"))
    j3 = json.loads(b3.decode("utf-8"))
    t2 = deep_ts(j2)
    t3 = deep_ts(j3)
    print(f"[{label}] :2:(HEAD fresh) ts={t2} | :3:(pick3 stale) ts={t3}")
    if t3 is not None and (t2 is None or t3 >= t2):
        winner, wb, side = b3, b3, ":3: (pick-3)"
    else:
        winner, wb, side = b2, b2, ":2: (HEAD fresher)"
    with open(path, "wb") as f:
        f.write(wb)
    json.loads(open(path, "rb").read().decode("utf-8"))
    print(f"[{label}] took {side}")


def resolve_jsonl_union(path, label):
    b2 = stage_bytes(":2:", path)
    b3 = stage_bytes(":3:", path)
    l2 = b2.decode("utf-8").splitlines()
    l3 = b3.decode("utf-8").splitlines()
    seen = set()
    out = []
    for ln in l2 + l3:
        if ln not in seen:
            seen.add(ln)
            out.append(ln)
    merged = "\n".join(out) + ("\n" if out else "")
    print(f"[{label}] :2: {len(l2)} lines + :3: {len(l3)} lines -> union {len(out)} lines (superset check: {len(out)==max(len(l2),len(l3))})")
    with open(path, "wb") as f:
        f.write(merged.encode("utf-8"))
    for ln in out:
        json.loads(ln)  # parse-verify every line (r185)


if __name__ == "__main__":
    resolve_snapshot("results/saturation_engine/face_bm-a.json", "satengine.face")
    resolve_snapshot("results/saturation_engine/state_bm-a.json", "satengine.state")
    resolve_jsonl_union("results/saturation_engine/history_bm-a.jsonl", "satengine.history")
    print("PICK-3 RESOLVED -- next: git add + GIT_EDITOR=true git rebase --continue")
