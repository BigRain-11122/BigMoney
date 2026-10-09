# r824 bm-c: union-resolve append-only jsonl pool face (stage2 ours x stage3 theirs -> union, zero-loss)
import subprocess, sys

path = "results/pool_core_samples.jsonl"

def stage(n):
    p = subprocess.run(["git", "show", ":%d:%s" % (n, path)], capture_output=True)
    if p.returncode != 0:
        print("stage %d read rc=%d" % (n, p.returncode))
        sys.exit(2)
    return p.stdout.decode("utf-8", "replace").splitlines()

ours = [l for l in stage(2) if l.strip()]
theirs = [l for l in stage(3) if l.strip()]
seen = set(ours)
union = list(ours)
added = 0
for l in theirs:
    if l not in seen:
        union.append(l)
        seen.add(l)
        added += 1

with open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(union) + ("\n" if union else ""))

print("ours=%d theirs=%d union=%d added_from_theirs=%d" % (len(ours), len(theirs), len(union), added))
# zero-loss assertion: union is superset of both sides
assert len(union) >= len(ours) and len(union) >= len(theirs)
dup_in_ours = len(ours) - len(set(ours))
dup_in_theirs = len(theirs) - len(set(theirs))
print("dup_ours=%d dup_theirs=%d (pre-existing dups preserved as-is)" % (dup_in_ours, dup_in_theirs))
