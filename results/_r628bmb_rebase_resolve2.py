# -*- coding: utf-8 -*-
# r628 bm-b rebase resolver pass 2: runtime-carry replay conflicts (5 UU)
import json, re, subprocess, sys

APPEND_LOGS = [
    "results/fund_divlowvol_p1/nulls.jsonl",
    "results/saturation_engine/history_bm-b.jsonl",
]
SNAPSHOTS = [
    "results/p1d_gates.json",
    "results/saturation_engine/face_bm-b.json",
    "results/saturation_engine/state_bm-b.json",
]
TS_RE = re.compile(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?")


def stage_bytes(path, stage):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    if r.returncode != 0:
        sys.exit("STAGE FAIL %s stage %d" % (path, stage))
    return r.stdout


def newest_ts(blob):
    hits = [m.group(0) for m in TS_RE.finditer(blob.decode("utf-8", "replace"))]
    return max(hits) if hits else ""


for path in APPEND_LOGS:
    o = stage_bytes(path, 2).decode("utf-8", "replace").splitlines()
    t = stage_bytes(path, 3).decode("utf-8", "replace").splitlines()
    seen, out = set(), []
    for ln in o + t:
        s = ln.strip()
        if not s or s in seen:
            continue
        seen.add(s)
        out.append(ln)
    for ln in out:
        json.loads(ln)  # every line must stay valid jsonl
    open(path, "w", encoding="utf-8", newline="").write("\n".join(out) + "\n")
    print("RESOLVED %s append-union ours=%d theirs=%d -> %d" % (path, len(o), len(t), len(out)))

for path in SNAPSHOTS:
    o, t = stage_bytes(path, 2), stage_bytes(path, 3)
    to, tt = newest_ts(o), newest_ts(t)
    winner = t if tt > to else o
    json.loads(winner.decode("utf-8", "replace"))
    open(path, "wb").write(winner)
    print("RESOLVED %s take-new (ours=%s theirs=%s -> %s)" % (path, to, tt, "theirs" if tt > to else "ours"))
