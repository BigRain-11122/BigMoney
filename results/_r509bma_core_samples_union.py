"""r509 bm-a rebase resolver: pool_core_samples.jsonl union (r294 conflict-region law).

Append-only jsonl, both sides appended new sampler rows -> union of the
conflict region only (no global dedup -- id repetition is legal elsewhere),
ts-sorted within the region, byte-level CRLF preserved.
"""
import json
import re
import sys

PATH = "results/pool_core_samples.jsonl"
raw = open(PATH, encoding="utf-8", newline="").read()

pat = re.compile(
    r"<<<<<<< HEAD\r?\n(.*?)\r?\n=======\r?\n(.*?)\r?\n>>>>>>>[^\r\n]*\r?\n",
    re.S,
)
blocks = pat.findall(raw)
if not blocks:
    print("no conflict markers found -- nothing to do")
    sys.exit(0)

nl = "\r\n" if "\r\n" in raw else "\n"
parts = pat.split(raw)  # [pre, ours, theirs, post1, ours2, theirs2, post2, ...]
out = parts[0]
n_ours = n_theirs = n_union = 0
for i in range(1, len(parts), 3):
    ours, theirs, post = parts[i], parts[i + 1], parts[i + 2]
    o_lines = [l for l in ours.splitlines() if l.strip()]
    t_lines = [l for l in theirs.splitlines() if l.strip()]
    n_ours += len(o_lines)
    n_theirs += len(t_lines)
    # union by exact line content (deterministic sampler rows are
    # machine-stamped; exact dup = one copy), then ts-sorted
    seen = set()
    union = []
    for l in o_lines + t_lines:
        if l not in seen:
            seen.add(l)
            union.append(l)
    n_union += len(union)
    d = {}
    for l in union:
        row = json.loads(l)
        d[l] = row.get("ts") or row.get("sampled_at") or ""
    union.sort(key=lambda l: d[l])
    out += nl.join(union) + nl + post

# reassemble: split gives pre + [ours, theirs, post]* groups interleaved --
# rebuild linearly instead to avoid ordering mistakes
pre = parts[0]
chunks = [pre]
merged = pre
idx = 1
final = pre
for i in range(1, len(parts), 3):
    ours, theirs, post = parts[i], parts[i + 1], parts[i + 2]
    o_lines = [l for l in ours.splitlines() if l.strip()]
    t_lines = [l for l in theirs.splitlines() if l.strip()]
    seen = set()
    union = []
    for l in o_lines + t_lines:
        if l not in seen:
            seen.add(l)
            union.append(l)
    key = {}
    for l in union:
        row = json.loads(l)
        key[l] = row.get("ts") or row.get("sampled_at") or ""
    union.sort(key=lambda l: key[l])
    final += nl.join(union) + nl + post

open(PATH, "w", encoding="utf-8", newline="").write(final)
print(f"resolved: ours={n_ours} theirs={n_theirs} union={n_union} "
      f"(exact-dup collapse {n_ours + n_theirs - n_union})")
