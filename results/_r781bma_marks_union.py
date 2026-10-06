# -*- coding: utf-8 -*-
"""r781 marks UU union resolver (r758 law: append-only jsonl both-sides-
appended -- union dedupe + stable ts sort; each line an independent
observation event, time order = true order; zero-loss assert)."""
import io
import json

P = r"results/paper/marks/marks-20261006.jsonl"
raw = io.open(P, encoding="utf-8", newline="").read()

# stage capture BEFORE any git add (r609 ①): ours = HEAD, theirs = MERGE_HEAD
import subprocess
ours = subprocess.run(["git", "show", "HEAD:" + P], capture_output=True).stdout.decode("utf-8")
theirs = subprocess.run(["git", "show", "MERGE_HEAD:" + P], capture_output=True).stdout.decode("utf-8")
assert "<<<<<<<" not in ours and "<<<<<<<" not in theirs, "stage blobs carry markers (impossible)"

o_lines = [l for l in ours.splitlines() if l.strip()]
t_lines = [l for l in theirs.splitlines() if l.strip()]
print("ours lines:", len(o_lines), "theirs lines:", len(t_lines))


def ts_of(l):
    try:
        return json.loads(l).get("ts", "")
    except Exception:
        return ""


# union by full-line identity (dedupe exact duplicates), stable ts sort
union = {}
for l in o_lines + t_lines:
    union[l] = True
merged = sorted(union.keys(), key=lambda l: (ts_of(l), l))
# zero-loss assert: every ours+theirs line present exactly once
for l in o_lines + t_lines:
    assert merged.count(l) == 1, "line lost or duplicated"
io.open(P, "w", encoding="utf-8", newline="").write("\r\n".join(merged) + "\r\n")
print("union landed:", len(merged), "lines (ours", len(o_lines), "+ theirs", len(t_lines),
      "- overlap", len(o_lines) + len(t_lines) - len(merged), ")")
# per-line json validity gate
for l in merged:
    json.loads(l)
print("per-line json validity PASS")
