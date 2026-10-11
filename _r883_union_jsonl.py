import subprocess, json, sys
GIT = r"C:\Program Files\Git\cmd\git.exe"
def blob(rev, path):
    return subprocess.run([GIT, "show", f"{rev}:{path}"], capture_output=True).stdout
for f in [r"results/pool_core_samples.jsonl", r"results/pool_red_flags.jsonl"]:
    ours = blob("origin/main", f).decode("utf-8", "replace").splitlines()
    theirs = blob("6ed3092f3", f).decode("utf-8", "replace").splitlines()
    ours_set = set(l.strip() for l in ours if l.strip())
    extra = [l for l in theirs if l.strip() and l.strip() not in ours_set]
    merged = [l for l in ours if l.strip()] + extra
    with open(f, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(merged) + ("\n" if merged else ""))
    print(f"{f}: origin={len(ours)} local={len(theirs)} local-only={len(extra)} merged={len(merged)}")
