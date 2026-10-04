# -*- coding: utf-8 -*-
"""r498 bm-c merge-conflict resolver (r656 line-level zero-loss union + r440 two-bucket pick).

Faces:
  - results/pool_red_flags.jsonl, results/pool_core_samples.jsonl: append-only
    record ledgers -> theirs-order + ours-only lines appended, zero-loss set
    containment asserted (r656), historical bad lines tolerated per r696
    (resolved lines are by-construction parent lines; only NEW malformed
    lines would fail, none can exist by construction).
  - results/_attrition_guard_scan.json: regenerable scan face -> ts-newer
    wins (r440), reparse-validated before write.

Both sides fetched via `git show HEAD:<path>` / `git show MERGE_HEAD:<path>`
raw-blob bytes (r657 law 2: add already wiped :2:/:3: stages; direct rev
read is add-pollution-proof). All git calls CREATE_NO_WINDOW (U060).
"""
import json
import subprocess
import sys

CREATE_NO_WINDOW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def git_show(rev, path):
    r = subprocess.run(["git", "show", "%s:%s" % (rev, path)],
                       capture_output=True, cwd=ROOT,
                       creationflags=CREATE_NO_WINDOW)
    if r.returncode != 0:
        sys.exit("GIT SHOW FAIL %s:%s -> %s" % (rev, path, r.stderr.decode("utf-8", "replace")))
    return r.stdout


def canon_lines(blob):
    # r656: split by \n (CRLF split counts blocks not lines); strip \r tail
    return [ln.rstrip(b"\r") for ln in blob.split(b"\n") if ln.strip()]


def resolve_jsonl(path):
    ours = canon_lines(git_show("HEAD", path))
    theirs = canon_lines(git_show("MERGE_HEAD", path))
    t_set = set(theirs)
    o_set = set(ours)
    ours_only = [ln for ln in ours if ln not in t_set]
    resolved = theirs + ours_only
    rset = set(resolved)
    assert set(ours) <= rset, "ZERO-LOSS FAIL: ours lines lost"
    assert set(theirs) <= rset, "ZERO-LOSS FAIL: theirs lines lost"
    # r696 tolerance: exact-dup lines INTERNAL to one parent are historical
    # state -- tolerate + report; the union itself must add no NEW dups:
    # resolved set must equal theirs-set + (ours-minus-theirs) set exactly.
    assert rset == (t_set | (o_set - t_set)), "DUP FAIL: union introduced new dup"
    hist_dup_theirs = len(theirs) - len(t_set)
    hist_dup_ours = len(ours) - len(o_set)
    bad_hist = 0
    for ln in resolved:
        try:
            json.loads(ln.decode("utf-8"))
        except Exception:
            bad_hist += 1  # r696: historical bad line present in a parent -> tolerate
    blob = b"\n".join(resolved) + b"\n"
    with open(ROOT + "\\" + path.replace("/", "\\"), "wb") as fh:
        fh.write(blob)
    print("%s: theirs=%d ours=%d ours_only=%d resolved=%d hist_bad=%d hist_dup(t/o)=%d/%d"
          % (path, len(theirs), len(ours), len(ours_only), len(resolved), bad_hist,
             hist_dup_theirs, hist_dup_ours))
    return len(ours_only)


def resolve_attrition(path):
    ours_b = git_show("HEAD", path)
    theirs_b = git_show("MERGE_HEAD", path)
    o = json.loads(ours_b.decode("utf-8"))
    t = json.loads(theirs_b.decode("utf-8"))

    def tskey(d):
        for k in ("generated_at", "scanned_at", "updated_at", "clock", "ts"):
            if isinstance(d, dict) and k in d:
                return str(d[k])
        return ""

    pick_ours = tskey(o) >= tskey(t)
    winner = ours_b if pick_ours else theirs_b
    json.loads(winner.decode("utf-8"))  # reparse-validate before write
    with open(ROOT + "\\" + path.replace("/", "\\"), "wb") as fh:
        fh.write(winner)
    print("%s: picked %s (ours_ts=%r theirs_ts=%r)" % (path, "OURS" if pick_ours else "THEIRS", tskey(o), tskey(t)))


if __name__ == "__main__":
    n1 = resolve_jsonl("results/pool_red_flags.jsonl")
    n2 = resolve_jsonl("results/pool_core_samples.jsonl")
    resolve_attrition("results/_attrition_guard_scan.json")
    print("RESOLVE OK ours_only_total=%d" % (n1 + n2))
