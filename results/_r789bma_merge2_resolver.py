# -*- coding: utf-8 -*-
"""r789 bm-a merge loop-2 resolver: compute_audit.json + regime_state.json
shared-state faces -- per-face ts evidence, take-newer (r756 ts-normalize
law + r609/r782 per-face empirical law; never blanket theirs/ours)."""
import io
import json
import re
import subprocess

CREAT = 0x08000000


def read_stage(path, stage):
    r = subprocess.run(["git", "show", f":{stage}:" + path],
                       capture_output=True, creationflags=CREAT)
    return r.stdout


def ts_of(blob):
    try:
        d = json.loads(blob.decode("utf-8"))
    except Exception:
        return ""
    for k in ("ts", "generated", "generated_at", "asof", "updated"):
        v = d.get(k)
        if isinstance(v, str):
            return v
    return ""


def resolve(path):
    ours = read_stage(path, 2)   # ours = HEAD (bm-a local)
    theirs = read_stage(path, 3)  # theirs = MERGE_HEAD
    to, tt = ts_of(ours), ts_of(theirs)
    # normalize: space -> T separator, then compare as strings of equal shape
    def norm(s):
        return s.replace(" ", "T") if s else ""
    no, nt = norm(to), norm(tt)
    pick = "ours" if no >= nt else "theirs"
    blob = ours if pick == "ours" else theirs
    # sanity: picked side parses as JSON
    json.loads(blob.decode("utf-8"))
    io.open(path, "wb").write(blob)
    print(f"{path}: ours_ts={to} theirs_ts={tt} -> take-{pick}")
    # verify no markers
    txt = io.open(path, encoding="utf-8", newline="").read()
    for m in ("<<<<<<< ", ">>>>>>> ", "======="):
        assert m not in txt, f"marker residue {m} in {path}"


for p in ("results/compute_audit.json", "results/regime_state.json"):
    resolve(p)
print("resolver done: 2 faces take-newer, marker scan CLEAN")
