# -*- coding: utf-8 -*-
"""r921 bm-a: resolve UU results/pool_core_samples.jsonl (append-log union, r188/r217 recipe).

Stages during rebase: :2: = origin side, :3: = local replayed side (r351 law).
Recipe: line-level union zero-loss; skeleton = local order; origin-only lines
appended at tail sorted by ts. Parse-verify every line before write-back (r185).
EOL mirrors the origin-side blob (CRLF detected, translated write mode).
"""
import subprocess, json, sys

G = r"C:\Program Files\Git\cmd\git.exe"
PATH = "results/pool_core_samples.jsonl"
OUT = r"results/pool_core_samples.jsonl"

def stage_blob(n):
    r = subprocess.run([G, "show", ":%d:%s" % (n, PATH)], capture_output=True)
    if r.returncode != 0:
        sys.exit("stage %d read fail: %s" % (n, r.stderr.decode("utf-8", "replace")))
    return r.stdout

b2, b3 = stage_blob(2), stage_blob(3)
use_crlf = b"\r\n" in b2

def lines_of(b):
    txt = b.decode("utf-8").replace("\r\n", "\n")
    return [ln for ln in txt.split("\n") if ln.strip()]

L2, L3 = lines_of(b2), lines_of(b3)

# parse-verify every line (r185 law) before any write-back
for ln in L2 + L3:
    json.loads(ln)

S2, S3 = set(L2), set(L3)
origin_only = [ln for ln in L2 if ln not in S3]

def ts_of(ln):
    return json.loads(ln).get("ts", "")

origin_only.sort(key=ts_of)
result = L3 + origin_only

# zero-loss assertions
assert set(result) == (S2 | S3), "union set mismatch"
assert len(set(result)) == len(S2 | S3), "dedupe collapsed distinct lines"
assert all(ln in (S2 | S3) for ln in result), "phantom line"
for ln in origin_only:
    assert ln not in S3, "origin-only line already in local side"

eol = "\r\n" if use_crlf else "\n"
with open(OUT, "w", encoding="utf-8", newline="") as f:
    for ln in result:
        f.write(ln + eol)

# post-write re-verify: file parses line-by-line and matches union set
with open(OUT, "r", encoding="utf-8", newline="") as f:
    back = [ln.strip("\r\n") for ln in f if ln.strip()]
assert set(back) == (S2 | S3), "write-back set mismatch"
for ln in back:
    json.loads(ln)

print(json.dumps({
    "path": PATH,
    "stage2_lines": len(L2),
    "stage3_lines": len(L3),
    "origin_only_added": len(origin_only),
    "union_lines": len(result),
    "crlf": use_crlf,
    "zero_loss": True,
}, ensure_ascii=False))
