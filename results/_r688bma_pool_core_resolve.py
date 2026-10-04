"""r688 S0 merge resolution rebuild for results/pool_core_samples.jsonl.

Both parents add exactly one line over the merge base:
  - origin/main: theirs (bm-c 17:06:02 judge-0 sample) inserted before the last line
  - HEAD:        ours   (bm-a 17:16:17 judge-2 sample) appended at tail
Result = base with theirs inserted at origin's position + ours appended.
Zero-loss criterion (r656): canon-line set of result contains both parents' canon sets.
"""
import json
import subprocess

PATH = "results/pool_core_samples.jsonl"
BASE = "285eac2049927012a9730d9dff37a59c3296557c"


def get(ref: str) -> bytes:
    return subprocess.run(
        ["git", "show", ref + ":" + PATH], capture_output=True
    ).stdout


def lines_of(blob: bytes) -> list:
    return [l.rstrip(b"\r") for l in blob.split(b"\n") if l.strip()]


base = get(BASE)
head = get("HEAD")
org = get("origin/main")

bl = lines_of(base)
hl = lines_of(head)
ol = lines_of(org)

assert len(bl) == 1223 and len(hl) == 1224 and len(ol) == 1224, (len(bl), len(hl), len(ol))
# HEAD = base + ours at tail
assert hl == bl + [hl[-1]], "head not base+1-tail"
assert b"17:16:17" in hl[-1] and b"bm-a" in hl[-1]
# origin = base[:1222] + theirs + base[1222:]
assert ol == bl[:1222] + [ol[1222]] + bl[1222:], "origin not base+1-mid"
assert b"17:06:02" in ol[1222] and b"bm-c" in ol[1222]

result = bl[:1222] + [ol[1222]] + bl[1222:] + [hl[-1]]
nb = b"\n".join(result) + b"\n"
with open(PATH, "wb") as f:
    f.write(nb)

rl = set(result)
assert set(hl) <= rl, "zero-loss FAIL vs HEAD"
assert set(ol) <= rl, "zero-loss FAIL vs origin"

n = 0
for l in result:
    json.loads(l.decode("utf-8"))
    n += 1
print("rebuilt lines:", len(result), "contain-head: True contain-origin: True all-parse:", n)
