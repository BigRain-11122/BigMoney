# -*- coding: utf-8 -*-
"""r649b bm-b second-merge resolver (bm-c r445 W115 close wave, 3 incoming).

- results/_attrition_guard_scan.json: whole-doc re-derive snapshot, shape/files
  keys identical both sides, rc=0/active_loss=False both -> R216 take-new-by-ts
  -> take-ours (05:28:39 > 05:25:32).
- results/token_usage.json: ours is the successor in the same append series
  (ours.delta_vs_prev.prev_generated == theirs.generated 05:15:10; append
  faces identical sigs 63=63 refusals 1539=1539) -> take-ours zero-loss.
  (theirs here is the stale bm-a-derived copy carried by bm-c's pre-merge base,
  same adjudication as first merge.)
"""
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)


def blob(side, path):
    r = subprocess.run(["git", "show", f":{side}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"FAIL blob {side}:{path}: {r.stderr.decode('utf-8', 'r')[:200]}")
    return r.stdout


def take_ours(path, proofs):
    ours_b = blob(2, path)
    with open(path, "wb") as fh:
        fh.write(ours_b)
    subprocess.run(["git", "add", "--", path], check=True, capture_output=True)
    print(f"  take-ours ok: {path} ({', '.join(proofs)})")


print("== phase 1: _attrition_guard_scan.json take-new-by-ts")
p = "results/_attrition_guard_scan.json"
O, T = json.loads(blob(2, p)), json.loads(blob(3, p))
assert sorted(O) == sorted(T), "shape diverges"
assert sorted(O["files"]) == sorted(T["files"]), "files keys diverge"
assert O["ts"] > T["ts"], f"ours not newer: {O['ts']} vs {T['ts']}"
assert O["rc"] == 0 and O["active_loss"] is False
take_ours(p, [f"ts {O['ts']} > {T['ts']}", "rc0 clean both"])

print("== phase 2: token_usage.json take-ours (successor-in-chain)")
p = "results/token_usage.json"
O, T = json.loads(blob(2, p)), json.loads(blob(3, p))
assert O["delta_vs_prev"]["prev_generated"] == T["generated"], \
    "ours not chained on theirs -- recipe premise broken"
assert O["l2_local_llm"]["crash_fuse"]["sigs"] == T["l2_local_llm"]["crash_fuse"]["sigs"]
assert O["l2_local_llm"]["crash_fuse"]["refusals"] == T["l2_local_llm"]["crash_fuse"]["refusals"]
assert O["generated"] > T["generated"]
take_ours(p, [f"gen {O['generated']} chained on {T['generated']}", "sigs/refusals identical"])

print("== phase 3: zero-marker + zero-UU verification")
r = subprocess.run(["git", "grep", "--cached", "-l", "-E", r"^(<<<<<<<|=======$|>>>>>>>)"],
                   capture_output=True)
assert r.returncode == 1, f"conflict markers in index: {r.stdout.decode()[:300]}"
out = subprocess.run(["git", "status", "--porcelain"],
                     capture_output=True).stdout.decode("utf-8", "r")
uu = [l for l in out.splitlines() if l.startswith(("UU", "AA", "DD"))]
assert not uu, f"remaining conflicts: {uu}"
json.load(open("results/_attrition_guard_scan.json", encoding="utf-8"))
json.load(open("results/token_usage.json", encoding="utf-8"))
print("RESOLVE_OK")
