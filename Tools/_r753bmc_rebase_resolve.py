# -*- coding: utf-8 -*-
"""r753 bm-c rebase conflict resolver v2 (col-index fix + union faces).
Canon: same-day idempotent regen faces -> per-face ts-duel (r738 deep-ts law,
datetime.fromisoformat, never string-compare r711/r756) newer-wins; append-only
rolling faces -> union zero-loss (compute_audit history by-ts union r678/r742;
token_usage per-key max-union r658/r678). During rebase: stage2 = origin base
side, stage3 = my replayed commit side.
Receipt -> results/_r753bmc_rebase_resolve.json."""
import datetime
import json
import os
import re
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

p = subprocess.run(["git", "ls-files", "-u"], capture_output=True, text=True, cwd=ROOT)
faces = []
for ln in p.stdout.splitlines():
    parts = ln.split("\t")
    if len(parts) == 2:
        face = parts[1].strip()
        if face not in faces:
            faces.append(face)
print("UU faces: %d" % len(faces))

TS_RE = re.compile(
    r'"(generated|generated_at|ts|asof|asof_ts)"\s*:\s*"([0-9T:+\-\.Z ]{8,32})"')


def blob(sha):
    return subprocess.run(["git", "cat-file", "blob", sha], capture_output=True,
                          text=True, errors="replace", cwd=ROOT).stdout


def getts(txt):
    m = TS_RE.search(txt)
    return m.group(2) if m else None


def norm(x):
    try:
        return datetime.datetime.fromisoformat(str(x).replace("Z", "+00:00"))
    except Exception:
        return None


def stages_of(face):
    info = subprocess.run(["git", "ls-files", "-u", "--", face], capture_output=True,
                          text=True, cwd=ROOT).stdout.splitlines()
    st = {}
    for l in info:
        cols = l.split("\t")[0].split()
        if len(cols) >= 3:
            st[int(cols[2])] = cols[1]
    return st


UNION_HISTORY = {ROOT.replace("\\", "/") + "/results/compute_audit.json":
                 "history_by_ts_union"}
UNION_TOKEN = {ROOT.replace("\\", "/") + "/results/token_usage.json":
               "per_key_max_union"}
UNION_FACES = {"results/compute_audit.json", "results/token_usage.json"}


def union_json(o2, o3, face):
    # per-key recursive max-union for numbers; dicts merge; lists by-ts for history
    if isinstance(o2, dict) and isinstance(o3, dict):
        out = dict(o2)
        for k, v in o3.items():
            if k in out:
                out[k] = union_json(out[k], v, face)
            else:
                out[k] = v
        return out
    if isinstance(o2, (int, float)) and isinstance(o3, (int, float)):
        return max(o2, o3)
    if isinstance(o2, list) and isinstance(o3, list):
        if all(isinstance(x, dict) for x in o2 + o3):
            key = "ts"
            seen = {}
            for x in o2 + o3:
                k = x.get(key)
                if k is None:
                    seen[id(x)] = x
                else:
                    seen[k] = x          # later write wins for same ts
            return list(seen.values())
        return o3 if len(o3) >= len(o2) else o2
    # scalar mismatch: newer-side logic left to caller via ts-duel on top level
    return o3


res = {}
for f in faces:
    rel = f.replace("\\", "/")
    st = stages_of(f)
    t2, t3 = getts(blob(st[2]) if 2 in st else ""), getts(blob(st[3]) if 3 in st else "")
    n2, n3 = norm(t2), norm(t3)
    if rel in UNION_FACES:
        try:
            o2 = json.loads(blob(st[2]))
            o3 = json.loads(blob(st[3]))
            merged = union_json(o2, o3, rel)
            # tie-break top-level freshness fields to the newer side
            if n3 and (not n2 or n3 > n2) and isinstance(merged, dict):
                for k in ("ts", "generated", "generated_at"):
                    if k in o3:
                        merged[k] = o3[k]
            out = os.path.join(ROOT, rel)
            with open(out, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(merged, fh, indent=1, ensure_ascii=False)
            subprocess.run(["git", "add", "--", f], capture_output=True, cwd=ROOT)
            res[f] = ("union", t2, t3)
            print("%-46s UNION (ts2=%s ts3=%s) history/keys merged zero-loss" % (f, t2, t3))
            continue
        except Exception as e:
            print("%-46s union FAILED (%s) -> fall to ts-duel" % (f, e))
    if n3 and (not n2 or n3 > n2):
        side = "theirs"
    else:
        side = "ours"
    subprocess.run(["git", "checkout", "--%s" % side, "--", f], capture_output=True, cwd=ROOT)
    subprocess.run(["git", "add", "--", f], capture_output=True, cwd=ROOT)
    res[f] = (side, t2, t3)
    print("%-46s ts-duel stage2=%s stage3=%s -> %s" % (f, t2, t3, side.upper()))

with open(os.path.join(ROOT, "results", "_r753bmc_rebase_resolve.json"), "w",
          encoding="utf-8") as fh:
    json.dump({"round": 753, "faces": {f: {"resolution": v[0], "stage2_ts": v[1],
                                           "stage3_ts": v[2]} for f, v in res.items()}},
              fh, indent=1, ensure_ascii=False)
left = subprocess.run(["git", "ls-files", "-u"], capture_output=True, text=True,
                      cwd=ROOT).stdout.splitlines()
print("resolved %d faces, uu-left=%d" % (len(res), len([l for l in left if l.strip()])))
