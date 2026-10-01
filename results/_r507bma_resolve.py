# -*- coding: utf-8 -*-
"""r507 bm-a rebase wave-2 resolver (8 UU: js-twin + snapshots + append-log).

bigmoney-conflict-resolve skill recipes:
- dashboard twin: .json deep-ts probe picks side; .js byte-copy SAME side
  (R209 js-wrapper-snapshot: take-side whole bytes, never json.dumps rewrite).
- snapshot: hardened deep-ts probe take-new (R350: strip _/- before prefix
  match, value ^20\\d{2}- + time-of-day, staged blobs not working tree);
  same-second tie -> :2: origin side (r140).
- pool_core_samples.jsonl: append-log line-level union zero loss (r188/r217).
Parse-verify before write-back (r185). Zero data judgment.
"""
import json
import re
import subprocess

TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}")
HINTS = ("generated", "updated", "ts", "time", "scannedat", "closedat", "asof")


def stage_blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"stage {stage} read fail {path}: {r.stderr[:200]}")
    return r.stdout


def deep_ts(obj, best=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            kk = re.sub(r"[_\-]", "", str(k).lower())
            if isinstance(v, str) and TS_RE.match(v) and any(
                    h in kk for h in HINTS):
                if v > best:
                    best = v
            else:
                best = deep_ts(v, best)
    elif isinstance(obj, list):
        for x in obj:
            best = deep_ts(x, best)
    return best


def pick_side(path):
    b2 = stage_blob(2, path)          # origin side (r351 stage law)
    b3 = stage_blob(3, path)          # local replay side
    t2 = deep_ts(json.loads(b2.decode("utf-8")))
    t3 = deep_ts(json.loads(b3.decode("utf-8")))
    side = 2 if t3 <= t2 else 3       # tie -> origin (r140)
    return b2, b3, side, t2, t3


def resolve_snapshot(path):
    b2, b3, side, t2, t3 = pick_side(path)
    blob = b2 if side == 2 else b3
    json.loads(blob.decode("utf-8"))  # parse-verify before write
    with open(path, "wb") as f:
        f.write(blob)
    print(f"  {path}: take :{side}: (origin={t2 or 'none'} local={t3 or 'none'})")


def resolve_dash_twin(json_path, js_path):
    b2, b3, side, t2, t3 = pick_side(json_path)
    jblob = b2 if side == 2 else b3
    json.loads(jblob.decode("utf-8"))
    with open(json_path, "wb") as f:
        f.write(jblob)
    with open(js_path, "wb") as f:     # R209: same-side whole bytes
        f.write(stage_blob(side, js_path))
    print(f"  {json_path}: twin take :{side}: (origin={t2 or 'none'} "
          f"local={t3 or 'none'}) + {js_path} same-side byte-copy")


def resolve_jsonl_union(path):
    b2 = stage_blob(2, path).decode("utf-8").splitlines()
    b3 = stage_blob(3, path).decode("utf-8").splitlines()
    seen, out = set(), []
    for ln in b2 + b3:                 # origin order first, local-only appended
        if ln not in seen:
            seen.add(ln)
            out.append(ln)
    data = "\n".join(out) + ("\n" if out else "")
    for ln in out:                     # every line must be valid JSON (r185)
        if ln.strip():
            json.loads(ln)
    with open(path, "wb") as f:
        f.write(data.encode("utf-8"))
    print(f"  {path}: line-union |{len(b2)}|+|{len(b3)}| -> "
          f"{len(out)} ({len(out) - len(set(b2) | set(b3))} dups dropped)")


snapshots = [
    "results/fundamental_b_layer_filter.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/_attrition_guard_scan.json",  # manual: per-run scan snapshot
]
for p in snapshots:
    resolve_snapshot(p)

resolve_dash_twin("results/dashboard_status.json",
                  "results/dashboard_status.js")
resolve_jsonl_union("results/pool_core_samples.jsonl")
print("wave-2 resolver done")
