# -*- coding: utf-8 -*-
"""r698 bm-a jsonl re-resolve per r694 canon (theirs verbatim + ours-unique
appended; no internal-dup collapse; zero-loss canon-set containment both).
Replaces the earlier keep-first collapse variant for the two jsonl faces."""
import subprocess

FILES = ["results/pool_core_samples.jsonl", "results/pool_red_flags.jsonl"]


def blob(rev, path):
    r = subprocess.run(["git", "show", "%s:%s" % (rev, path)], capture_output=True)
    assert r.returncode == 0, "git show fail %s:%s" % (rev, path)
    return r.stdout


for p in FILES:
    ol = blob("HEAD", p).decode("utf-8").splitlines()
    tl = blob("MERGE_HEAD", p).decode("utf-8").splitlines()
    seen = set(tl)
    extra = [ln for ln in ol if ln not in seen and ln.strip()]
    union_l = tl + extra
    assert set(union_l) >= set(ln for ln in ol if ln.strip()), "ours lost " + p
    assert set(union_l) >= set(ln for ln in tl if ln.strip()), "theirs lost " + p
    with open(p, "wb") as fh:
        fh.write(("\n".join(union_l) + "\n").encode("utf-8"))
    print("[r694-canon union] %s: theirs %d + ours-unique %d = %d rows "
          "(internal dupes preserved)" % (p, len(tl), len(extra), len(union_l)))
