"""r486 bm-c S0 merge resolution: results/pool_core_samples.jsonl tail-union.

Merge shape: base=ebe9292a2 (merge-base==pre-absorb HEAD). Ours (absorb
commit) adds bm-c sample lines at tail; theirs (origin/main 5 commits)
adds bm-a/bm-b sample lines. Resolution = theirs full order + ours-extra
lines appended at tail (r688/r689 lineage, dynamic shape -- no hardcoded
line counts). Zero-loss criterion (r656): multiset(result) contains both
parents' canon multisets; every line parses as JSON; no conflict markers.
If git auto-merged the face (no UU), the same containment check runs as
verification and REBUILDS only on failure.
Blobs via git show HEAD:/MERGE_HEAD: raw bytes (r657 law: immune to add
pollution; r660 law: subprocess raw bytes, zero PS pipeline)."""
import json
import subprocess
import sys

CREATE = 0x08000000
PATH = "results/pool_core_samples.jsonl"


def git(*a):
    r = subprocess.run(["git"] + list(a), capture_output=True,
                        creationflags=CREATE)
    if r.returncode != 0:
        sys.exit("GIT FAIL %s -> %s" % (a[:3], r.stderr.decode("utf-8", "replace")[:200]))
    return r.stdout


def canon(blob):
    return [l.rstrip(b"\r") for l in blob.split(b"\n") if l.strip()]


def multiset_diff(whole, part):
    """lines in `whole` not covered by `part` (multiset semantics)."""
    from collections import Counter
    c = Counter(part)
    out = []
    for l in whole:
        if c[l] > 0:
            c[l] -= 1
        else:
            out.append(l)
    return out


status = subprocess.run(["git", "status", "--porcelain"],
                         capture_output=True, creationflags=CREATE).stdout.decode()
uu = [l[3:] for l in status.splitlines() if l.startswith("UU ")]
print("UU faces:", uu if uu else "(none)")
other_uu = [p for p in uu if p != PATH]

base_sha = git("merge-base", "HEAD", "MERGE_HEAD").decode().strip()
ours = canon(git("show", "HEAD:" + PATH))
theirs = canon(git("show", "MERGE_HEAD:" + PATH))
base = canon(git("show", base_sha + ":" + PATH))
ours_extra = multiset_diff(ours, base)
theirs_extra = multiset_diff(theirs, base)
print("base=%d ours=%d(+%d) theirs=%d(+%d)"
      % (len(base), len(ours), len(ours_extra), len(theirs), len(theirs_extra)))

result = list(theirs) + ours_extra
assert multiset_diff(ours, result) == [], "zero-loss FAIL vs HEAD"
assert multiset_diff(theirs, result) == [], "zero-loss FAIL vs MERGE_HEAD"

if PATH in uu:
    blob_theirs = git("show", "MERGE_HEAD:" + PATH)
    eol = b"\r\n" if b"\r\n" in blob_theirs else b"\n"
    body = eol.join(result) + eol
    with open(PATH, "wb") as fh:
        fh.write(body)
    print("RESOLVED (wrote %d lines, eol=%s)" % (len(result), "CRLF" if eol == b"\r\n" else "LF"))
else:
    wt = canon(open(PATH, "rb").read())
    ok = multiset_diff(ours, wt) == [] and multiset_diff(theirs, wt) == []
    print("no-UU verify: working-tree zero-loss = %s (wt=%d)" % (ok, len(wt)))
    if not ok:
        blob_theirs = git("show", "MERGE_HEAD:" + PATH)
        eol = b"\r\n" if b"\r\n" in blob_theirs else b"\n"
        with open(PATH, "wb") as fh:
            fh.write(eol.join(result) + eol)
        print("REBUILT to zero-loss union (%d lines)" % len(result))

n = 0
for l in result:
    json.loads(l.decode("utf-8"))
    n += 1
assert n == len(result)
print("RESULT lines=%d all-parse=%d zero-loss=PASS other_UU=%s"
      % (len(result), n, other_uu if other_uu else "none"))
