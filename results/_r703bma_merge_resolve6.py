# r703 bm-a merge resolver leg-6: post_review.jsonl FULL-LINE union repair (leg-4 prefix-key bug
# collapsed 19 real distinct lines -- zero-loss redo per r466 family: full-line keys, ordered union)
import subprocess

def blob(rev, p):
    return subprocess.run(["git", "show", f"{rev}:{p}"], capture_output=True).stdout.decode("utf-8", errors="replace")

p = "results/post_review.jsonl"
ours = blob("HEAD", p).splitlines()
theirs = blob("origin/main", p).splitlines()
seen = set(ours)
merged = list(ours)
theirs_only = [l for l in theirs if l not in seen]
merged.extend(theirs_only)
data = "\n".join(merged) + ("\n" if merged else "")
open(p, "w", encoding="utf-8", newline="").write(data)
subprocess.run(["git", "add", p], capture_output=True)

so, st, sm = set(ours), set(theirs), set(merged)
print(f"post_review.jsonl REPAIR: ours={len(ours)} theirs={len(theirs)} theirs_only_appended={len(theirs_only)} merged={len(merged)}")
print(f"  zero-loss: all-ours-in-merged={so <= sm} all-theirs-in-merged={st <= sm} merged-extra={len(sm - (so | st))}")
# trailing newline + last-line integrity check
raw = open(p, "rb").read()
print(f"  trailing-newline={raw.endswith(chr(10).encode())} last-30-bytes={raw[-30:]!r}")
