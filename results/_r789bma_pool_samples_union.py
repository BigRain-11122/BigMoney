# -*- coding: utf-8 -*-
"""r789 bm-a merge conflict resolver: results/pool_core_samples.jsonl
union recipe (r758 law -- append-only jsonl, each line an independent
observation event; union dedup + stable sort by ts)."""
import io
import json

PATH = r"results/pool_core_samples.jsonl"
src = io.open(PATH, encoding="utf-8", newline="").read()

# stage-2 (ours, HEAD) and stage-3 (theirs, MERGE_HEAD) full blobs
import subprocess
ours = subprocess.run(["git", "show", ":2:" + PATH], capture_output=True).stdout
theirs = subprocess.run(["git", "show", ":3:" + PATH], capture_output=True).stdout

ours_lines = [l for l in ours.decode("utf-8").splitlines() if l.strip()]
theirs_lines = [l for l in theirs.decode("utf-8").splitlines() if l.strip()]

# union by full line content (each observation line is its own identity)
seen = set()
union = []
for l in ours_lines + theirs_lines:
    if l not in seen:
        seen.add(l)
        union.append(l)

# stable sort by ts (each line carries "ts": "..."; equal-ts lines keep
# insertion order -- stable sort preserves ours-before-theirs)
def ts_key(l):
    try:
        return json.loads(l).get("ts", "")
    except Exception:
        return ""
union_sorted = sorted(union, key=ts_key)

# integrity: no line lost vs either side
assert set(ours_lines) <= set(union_sorted), "ours line lost in union"
assert set(theirs_lines) <= set(union_sorted), "theirs line lost in union"
assert len(union_sorted) == len(union) == len(seen)

out = "\r\n".join(union_sorted) + "\r\n"
io.open(PATH, "w", encoding="utf-8", newline="").write(out)
print(f"union resolver: ours={len(ours_lines)} theirs={len(theirs_lines)} "
      f"union={len(union_sorted)} (dedup={len(ours_lines)+len(theirs_lines)-len(union_sorted)})")
# verify no conflict markers remain
txt = io.open(PATH, encoding="utf-8", newline="").read()
for marker in ("<<<<<<< ", "=======", ">>>>>>> "):
    assert marker not in txt, f"conflict marker residue: {marker}"
# ts monotonicity check (last 12 lines)
tail_ts = [ts_key(l) for l in union_sorted[-12:]]
assert tail_ts == sorted(tail_ts), f"ts order broken in tail: {tail_ts}"
print("marker scan CLEAN, tail ts monotone")
