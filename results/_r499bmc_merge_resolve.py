# -*- coding: utf-8 -*-
"""r499 bm-c merge resolver: pool_red_flags.jsonl only (expected single UU).

Reuses r498 lineage resolve_jsonl (r656 line-level zero-loss union:
theirs-order + ours-only appended, set-containment + no-new-dup asserted,
r696 historical-bad-line tolerance). Sides via git show HEAD:/MERGE_HEAD:
raw-blob bytes (r657 law 2). Guarded: face must actually be UU before write.
"""
import json
import subprocess
import sys

CREATE_NO_WINDOW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
PATH = "results/pool_red_flags.jsonl"


def git(args):
    return subprocess.run(["git"] + args, capture_output=True, cwd=ROOT,
                           creationflags=CREATE_NO_WINDOW)


def git_show(rev, path):
    r = git(["show", "%s:%s" % (rev, path)])
    if r.returncode != 0:
        sys.exit("GIT SHOW FAIL %s:%s -> %s" % (rev, path, r.stderr.decode("utf-8", "replace")))
    return r.stdout


def main():
    st = git(["status", "--porcelain"]).stdout.decode("utf-8", "replace")
    uu = [ln for ln in st.splitlines() if ln.startswith("UU")]
    assert uu == ["UU " + PATH], "UNEXPECTED UU SET: %r" % (uu,)
    ours = [ln.rstrip(b"\r") for ln in git_show("HEAD", PATH).split(b"\n") if ln.strip()]
    theirs = [ln.rstrip(b"\r") for ln in git_show("MERGE_HEAD", PATH).split(b"\n") if ln.strip()]
    t_set, o_set = set(theirs), set(ours)
    ours_only = [ln for ln in ours if ln not in t_set]
    resolved = theirs + ours_only
    rset = set(resolved)
    assert o_set <= rset, "ZERO-LOSS FAIL: ours lines lost"
    assert t_set <= rset, "ZERO-LOSS FAIL: theirs lines lost"
    assert rset == (t_set | (o_set - t_set)), "DUP FAIL: union introduced new dup"
    bad_hist = 0
    for ln in resolved:
        try:
            json.loads(ln.decode("utf-8"))
        except Exception:
            bad_hist += 1
    with open(ROOT + "\\" + PATH.replace("/", "\\"), "wb") as fh:
        fh.write(b"\n".join(resolved) + b"\n")
    print("%s: theirs=%d ours=%d ours_only=%d resolved=%d hist_bad=%d"
          % (PATH, len(theirs), len(ours), len(ours_only), len(resolved), bad_hist))
    if ours_only:
        print("ours_only first: %s" % ours_only[0].decode("utf-8", "replace")[:200])


if __name__ == "__main__":
    main()
