"""r413 push-collision batch-2 resolver (vs ead43f0d2 = bm-b r408/r408-addendum + bm-c r197/198 window).

11 snapshot faces: hardened deep-ts probe verdict = :2: (origin) newer on ALL 11
(bm-b r408 lawful stale-takeover ran the chain 04:11 vs dead r412's 03:40) ->
take :2: staged blob VERBATIM (byte-identical to parent = clean empty replay diff),
json.loads parse-verify before write (r185 law).

x2_watch_log.jsonl: append-log line-level union zero-loss (r188/r217):
  :2:=1512 lines, :3:=1416 lines, common=1410 -> union 1518
  (neither side superset; batch-82 superset law not applicable), sort by embedded ts.
"""
import collections
import json
import subprocess
import sys

SNAPSHOTS = [
    "results/daily_scorecard.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-28.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/t35_open_fill_verify.json",
]
JSONL = "results/x2_watch_log.jsonl"


def stage_bytes(stage, path):
    b = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True).stdout
    if not b:
        sys.exit(f"FAIL: empty stage {stage} blob for {path}")
    return b


for p in SNAPSHOTS:
    b2 = stage_bytes("2", p)
    json.loads(b2)  # parse-verify the winning blob BEFORE write (r185)
    with open(p, "wb") as f:
        f.write(b2)
    json.loads(open(p, "rb").read())  # parse-verify AFTER write
    print(f"take-:2: verbatim -> {p} (parse-verified)")

l2 = stage_bytes("2", JSONL).decode("utf-8").splitlines()
l3 = stage_bytes("3", JSONL).decode("utf-8").splitlines()
# multiset union (r188 zero-loss): origin side carries 90 legitimate x2 duplicate events
# (two machines' same-second identical rows, multiplicity preserved by bm-b r408-addendum
# union = canonical form); per-line count = max(side counts), NEVER set-dedup.
c2, c3 = collections.Counter(l2), collections.Counter(l3)
union = []
for ln in dict.fromkeys(l2 + l3):  # distinct iteration, stable
    union.extend([ln] * max(c2[ln], c3[ln]))
union.sort(key=lambda ln: (json.loads(ln).get("ts", ""), ln))  # stable chronological
n_expected = sum(max(c2[k], c3[k]) for k in set(c2) | set(c3))
assert len(union) == n_expected, f"multiset union loss: {len(union)} != {n_expected}"
out = ("\n".join(union) + "\n").encode("utf-8")
with open(JSONL, "wb") as f:
    f.write(out)
for ln in union:  # every line parse-verified (r185)
    json.loads(ln)
print(f"x2_watch_log multiset-union: |:2:|={len(l2)} |:3:|={len(l3)} -> {len(union)} lines zero-loss (multiplicity preserved)")
