# -*- coding: utf-8 -*-
"""r793 bm-a rebase UU resolver (2-face): post_review.jsonl = append-log line-level
union zero-loss (r188/r217); REPORT-20261006.md = same-day regen report, generated
ts probe origin 20:02:14 > local 20:01:09 -> take stage2 (origin) verbatim (r327/r329
twin-side coupling, md face byte-copy from the same side)."""
import collections

import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def blob(ref: str) -> bytes:
    return subprocess.run(["git", "show", ref], capture_output=True).stdout


J = "results/post_review.jsonl"
R = "results/post_review/REPORT-20261006.md"

# ---- face 1: jsonl union (rebase window: stage2=onto/origin, stage3=local replay) ----
ours_lines = blob(f":2:{J}").decode("utf-8").splitlines()
theirs_lines = blob(f":3:{J}").decode("utf-8").splitlines()
ours_set = set(ours_lines)
union = list(ours_lines) + [l for l in theirs_lines if l not in ours_set]
# verify every line parses as json
for l in union:
    json.loads(l)
# zero-loss assertion = multiset union (Counter max per row: shared history rows keep
# their count, each side's snapshot-burst rows all survive). The ledger's 500 internal
# dup groups are per-round snapshot bursts by design -- "no duplicate lines" would be
# a false red (r482 family: assert form must match the materialized form).
cu = collections.Counter(union)
expected = collections.Counter(ours_lines) | collections.Counter(theirs_lines)
assert cu == expected, "multiset union mismatch"
assert len(union) == sum(expected.values())
with open(J, "w", encoding="utf-8", newline="") as f:
    f.write("\n".join(union) + "\n")
print(f"jsonl union: origin={len(ours_lines)} local={len(theirs_lines)} merged={len(union)} (zero-loss assert PASS)")

# ---- face 2: REPORT md take-side by generated ts ----
ours_r = blob(f":2:{R}").decode("utf-8")
theirs_r = blob(f":3:{R}").decode("utf-8")


def gen_ts(s: str) -> str:
    for l in s.splitlines():
        if l.startswith("生成 "):
            return l.split("·")[0].strip()
    raise AssertionError("generated ts line not found")


assert gen_ts(ours_r) == "生成 2026-10-06 20:02:14" and gen_ts(theirs_r) == "生成 2026-10-06 20:01:09"
with open(R, "w", encoding="utf-8", newline="") as f:
    f.write(ours_r)
print(f"REPORT md: take stage2 origin (20:02:14 > 20:01:09), {len(ours_r)} bytes verbatim")
print("r793 resolver rc0")
