"""r1023 rebase conflict resolution: shared generated faces -> origin-newer (stage 2) per r708 merge-mode;
x2_watch_log.jsonl -> content-union dedupe (append-only jsonl law, 5e71102e2 precedent)."""
import subprocess, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def show(stage, path):
    r = subprocess.run(["git", "show", ":%s:%s" % (stage, path)], capture_output=True)
    if r.returncode != 0:
        print("SHOW-FAIL %s %s: %s" % (stage, path, r.stderr.decode()[:200]))
        sys.exit(2)
    return r.stdout.decode("utf-8", "replace")

r = subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"], capture_output=True)
files = [l.strip().lstrip("\ufeff") for l in r.stdout.decode("utf-8", "replace").splitlines() if l.strip()]
print("UU count: %d" % len(files))
x2 = "results/x2_watch_log.jsonl"
for f in files:
    if f == x2:
        continue
    r = subprocess.run(["git", "checkout", "--ours", "--", f])
    if r.returncode != 0:
        print("CHECKOUT-FAIL %s" % f); sys.exit(2)
    subprocess.run(["git", "add", "--", f])
    print("take-origin: %s" % f)

if x2 in files:
    ours = [l for l in show(2, x2).splitlines() if l.strip()]
    theirs = [l for l in show(3, x2).splitlines() if l.strip()]
    seen = set(ours)
    union = ours + [l for l in theirs if l not in seen]
    with open(x2, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(union) + "\n")
    subprocess.run(["git", "add", "--", x2])
    print("x2 union: base-ours=%d theirs=%d union=%d (theirs-new=%d)" % (
        len(ours), len(theirs), len(union), len(union) - len(ours)))
print("RESOLVE-OK")
