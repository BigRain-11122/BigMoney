import subprocess

GIT = r"C:\Program Files\Git\cmd\git.exe"
PATH = "results/post_review.jsonl"

def stage(n):
    out = subprocess.run([GIT, "show", f":{n}:{PATH}"], capture_output=True)
    if out.returncode != 0:
        raise SystemExit(f"stage {n} fetch failed: {out.stderr[:200]}")
    return out.stdout.decode("utf-8", "replace").splitlines()

ours = stage(2)
theirs = stage(3)
ours_set = set(l.strip() for l in ours if l.strip())
extra = [l for l in theirs if l.strip() and l.strip() not in ours_set]
merged = [l for l in ours if l.strip()] + extra
with open(PATH, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(merged) + "\n")
print(f"ours={len(ours)} theirs={len(theirs)} theirs_unique_appended={len(extra)} merged={len(merged)}")
