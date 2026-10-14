# r1011 rebase conflict resolution: union append-only jsonl ledgers (line-level,
# ours-then-theirs order, exact-dup drop); full-regen faces resolved by checkout --theirs
import subprocess, sys, json as _j

GIT = r"C:\Program Files\Git\cmd\git.exe"

def stage(sid, path):
    return subprocess.run([GIT, "show", f":{sid}:{path}"], capture_output=True).stdout.decode("utf-8", "replace")

for path in sys.argv[1:]:
    ours = stage(2, path).splitlines()
    theirs = stage(3, path).splitlines()
    seen = set(ours)
    union = list(ours) + [ln for ln in theirs if ln not in seen and ln.strip()]
    bad = 0
    for ln in union:
        if ln.strip():
            try:
                _j.loads(ln)
            except Exception:
                bad += 1
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(union))
        if union:
            f.write("\n")
    print(f"UNION {path}: ours={len(ours)} theirs={len(theirs)} union={len(union)} bad_json={bad}")
