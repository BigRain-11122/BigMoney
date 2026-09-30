# r491 bm-a: CODELY.md 3-way union (worktree GM archival edits vs remote additions)
# byte-faithful via subprocess git; writes merged result + zero-loss audit.
import subprocess, io, hashlib, os, sys

def show(ref_path):
    r = subprocess.run(["git", "show", ref_path], capture_output=True)
    assert r.returncode == 0, (ref_path, r.stderr[:200])
    return r.stdout

base = show("d62411e1c0536241718044e483a1818f9b7e7ec4:CODELY.md")
theirs = show("origin/main:CODELY.md")
with io.open("CODELY.md", "rb") as fh:
    ours = fh.read()

tmp = "results/_r491bma_codely"
for nm, data in (("base", base), ("theirs", theirs)):
    with io.open(f"{tmp}_{nm}.tmp", "wb") as fh:
        fh.write(data)
with io.open(f"{tmp}_ours.tmp", "wb") as fh:
    fh.write(ours)

r = subprocess.run(["git", "merge-file", "-p", "-L", "ours", "-L", "base", "-L", "theirs",
                    f"{tmp}_ours.tmp", f"{tmp}_base.tmp", f"{tmp}_theirs.tmp"],
                   capture_output=True)
merged = r.stdout
conflicts = r.returncode  # >0 = number of conflict hunks
print("merge-file rc:", r.returncode, "| merged bytes:", len(merged))
if r.stderr:
    print("stderr:", r.stderr.decode("utf-8", "replace")[:300])
if conflicts:
    # print conflict markers context for manual resolution
    txt = merged.decode("utf-8", "replace")
    lines = txt.splitlines()
    for i, ln in enumerate(lines):
        if ln.startswith(("<<<<<<<", "=======", ">>>>>>>")):
            print(i + 1, ln[:160])
else:
    with io.open(f"{tmp}_merged.tmp", "wb") as fh:
        fh.write(merged)
    # zero-loss audit: line-level union check
    def lines_of(b):
        return [l for l in b.decode("utf-8", "replace").splitlines() if l.strip()]
    B, O, T, M = (set(lines_of(x)) for x in (base, ours, theirs, merged))
    lost_ours = (B | O) - M
    lost_theirs = (B | T) - M
    print("AUDIT: lines only-in-base(replaced by both sides ok):", len(B - M))
    print("AUDIT: ours lines missing from merged:", len(lost_ours))
    print("AUDIT: theirs lines missing from merged:", len(lost_theirs))
    if lost_ours:
        for l in list(lost_ours)[:5]:
            print("  LOST-OURS:", l[:150])
    if lost_theirs:
        for l in list(lost_theirs)[:5]:
            print("  LOST-THEIRS:", l[:150])
    print("VERDICT:", "UNION-COMPLETE" if not lost_ours and not lost_theirs else "LOSS-DETECTED")
