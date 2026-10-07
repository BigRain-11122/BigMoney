# -*- coding: utf-8 -*-
"""r863 bm-a: pit-git-staged.md append-ledger union (memory-union law R208/r212).

base 7347B prefix identical on both sides (assert) -> union =
base + r862 suffix (04:4x entry, 959B) + bm-c suffix (05:1x entry, 917B)
= 7347+959+917 = 9223B expected.
"""
import subprocess

PATH = "research/pit-git-staged.md"


def blob(stage):
    r = subprocess.run(["git", "show", f"{stage}:{PATH}"], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"git show {stage} failed")
    return r.stdout


base = blob(":1")
ours = blob(":2")    # onto side (bm-c r731)
theirs = blob(":3")  # replay side (r862 bm-a)

# common prefix
n = 0
m = min(len(ours), len(theirs))
while n < m and ours[n] == theirs[n]:
    n += 1
p = ours.rfind(b"\n", 0, n) + 1
assert p == len(base), f"prefix {p} != base {len(base)}"
assert len(base) + len(theirs) - p + len(ours) - p == 9223, "byte-account mismatch"

# ts order: r862 entry (04:4x) precedes bm-c entry (05:1x)
union = theirs + ours[p:]
assert len(union) == 9223, f"union len {len(union)} != 9223"
with open(PATH, "wb") as f:
    f.write(union)
print(f"union written: base={len(base)} + r862={len(theirs)-p} + bmc={len(ours)-p} = {len(union)}B")
