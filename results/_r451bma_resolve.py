# r451 bm-a: resolve rebase-legacy single UU results/post_review.jsonl (append-log family)
# Law: r188 line-level union zero-loss + r209 subprocess-bytes blob reads (no PS `>` artifacts)
#      + r185 parse-verify before write-back + r223/r234 mirror base blob newline style
import json
import subprocess
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
PATH = "results/post_review.jsonl"


def blob_bytes(stage):
    # r209: read git object as raw bytes, decode utf-8 explicitly
    return subprocess.check_output(["git", "show", f":{stage}:{PATH}"])


origin_raw = blob_bytes(2)
local_raw = blob_bytes(3)
crlf = b"\r\n" in origin_raw or b"\r\n" in local_raw

o_lines = origin_raw.decode("utf-8").splitlines()
l_lines = local_raw.decode("utf-8").splitlines()

o_cnt, l_cnt = Counter(o_lines), Counter(l_lines)
common = o_cnt & l_cnt
o_only = o_cnt - common
l_only = l_cnt - common

# union skeleton = origin full order (landed remote truth) + local-only appended (chronologically later sweep 00:10:04)
union = list(o_lines)
l_only_seq = [ln for ln in l_lines if l_only[ln] > 0]  # preserves local order, count-exact
union.extend(l_only_seq)

# zero-loss verification (multiset): union == A + B - common
assert Counter(union) == (o_cnt | l_cnt) or Counter(union) == (
    o_cnt + l_cnt - common
), "multiset mismatch"
assert len(union) == len(o_lines) + sum(l_only.values()), "length mismatch"
for i, ln in enumerate(union):
    json.loads(ln)  # r185 parse-verify every line

nl = "\r\n" if crlf else "\n"
with open(PATH, "w", encoding="utf-8", newline="") as f:
    f.write(nl.join(union))
    if origin_raw.endswith(b"\n") or local_raw.endswith(b"\n"):
        f.write(nl)

print(json.dumps({
    "origin_lines": len(o_lines),
    "local_lines": len(l_lines),
    "common_lines": sum(common.values()),
    "origin_only_lines": sum(o_only.values()),
    "local_only_lines": sum(l_only.values()),
    "union_lines": len(union),
    "crlf": crlf,
    "local_only_ids_preview": [json.loads(x).get("id") for x in l_only_seq][:5],
}, ensure_ascii=False))
