# -*- coding: utf-8 -*-
"""r698 bm-a wave-2: pool_red_flags.jsonl single-UU resolve (r694 canon:
theirs verbatim + ours-unique appended, zero-loss canon-set containment)."""
import subprocess

p = "results/pool_red_flags.jsonl"


def blob(rev, path):
    r = subprocess.run(["git", "show", "%s:%s" % (rev, path)], capture_output=True)
    assert r.returncode == 0, "git show fail %s:%s" % (rev, path)
    return r.stdout


ol = blob("HEAD", p).decode("utf-8").splitlines()
tl = blob("MERGE_HEAD", p).decode("utf-8").splitlines()
seen = set(tl)
extra = [ln for ln in ol if ln not in seen and ln.strip()]
union_l = tl + extra
assert set(union_l) >= set(ln for ln in ol if ln.strip()), "ours lost"
assert set(union_l) >= set(ln for ln in tl if ln.strip()), "theirs lost"
with open(p, "wb") as fh:
    fh.write(("\n".join(union_l) + "\n").encode("utf-8"))
print("[union] %s: theirs %d + ours-unique %d = %d" % (p, len(tl), len(extra), len(union_l)))
for ln in extra:
    print("  ours-unique: %s" % ln[:150])
