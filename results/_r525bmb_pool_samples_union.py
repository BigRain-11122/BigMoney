"""r525 bm-b rebase conflict resolver: pool_core_samples.jsonl append-union (r294 domain law).

Single conflict region, both sides appended distinct burn-sample rows after the
common base (last shared row = bm-b W28 sample). Resolution = union of the two
line sets, dedupe exact duplicate lines within the conflict region ONLY
(r294: dedupe domain pinned to the conflict region, never the whole file --
legal multi-line repeats elsewhere are untouched).
"""
import json
import re
import sys

PATH = r"results/pool_core_samples.jsonl"
raw = open(PATH, "r", encoding="utf-8").read()
assert raw.count("<<<<<<<") == 1, "expected exactly one conflict region"
m = re.search(r"<<<<<<< HEAD\r?\n(.*?)\r?\n=======\r?\n(.*?)\r?\n>>>>>>> [^\r\n]*", raw, re.S)
assert m, "conflict markers not parsed"
head_block = m.group(1)
mine_block = m.group(2)
head_lines = [l for l in head_block.split("\n") if l.strip()]
mine_lines = [l for l in mine_block.split("\n") if l.strip()]

union = []
seen = set()
for l in head_lines + mine_lines:
    if l in seen:
        continue
    seen.add(l)
    union.append(l)

for l in union:
    json.loads(l)  # every output line must be valid json

resolved = raw[: m.start()] + "\n".join(union) + raw[m.end():]
assert "<<<<<<<" not in resolved and "=======" not in resolved and ">>>>>>>" not in resolved
open(PATH, "w", encoding="utf-8", newline="").write(resolved)

# self-verify: both sides fully represented in output
out_lines = [l for l in resolved.split("\n") if l.strip()]
out_set = set(out_lines)
miss_h = [l for l in head_lines if l not in out_set]
miss_m = [l for l in mine_lines if l not in out_set]
dupes = len(out_lines) - len(out_set)
print(f"head_lines={len(head_lines)} mine_lines={len(mine_lines)} union={len(union)} "
      f"exact_dupes_dropped={len(head_lines) + len(mine_lines) - len(union)} "
      f"missing_head={len(miss_h)} missing_mine={len(miss_m)} whole_file_dupe_pairs={dupes}")
assert not miss_h and not miss_m, "union lost lines -- FAIL-CLOSED"
print("POOL_SAMPLES_UNION_OK")
