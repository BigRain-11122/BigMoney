# r496 bm-b: rebase UU resolve per bigmoney-conflict-resolve skill
# - crash_fuse.json: canonical merge_crash_fuse (sigs key-union newer-wins + tombstone suppression, r387 law)
# - pool_core_samples.jsonl: append-log -> line-level union zero-loss (r188)
# During rebase: stage2=base(origin/main), stage3=replayed commit (bm-b carry)
import json, subprocess, sys, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "scripts"))
import merge_lane_views as mlv  # noqa: E402

def stage(path, n):
    r = subprocess.run(["git", "-C", REPO, "show", ":%d:%s" % (n, path)], capture_output=True)
    return r.stdout

# --- 1. crash_fuse.json: canonical union ---
p = "results/crash_fuse.json"
base_b, ours_b = stage(p, 2), stage(p, 3)
base = json.loads(base_b.decode("utf-8"))
ours = json.loads(ours_b.decode("utf-8"))
merged, notes = mlv.merge_crash_fuse([("base(origin)", base), ("r496carry(bm-b)", ours)])
crlf = b"\r\n" in base_b
indent = 1
head = base_b.decode("utf-8").splitlines()[1][:6]
if head.startswith("   "):
    indent = 3
elif head.startswith("  "):
    indent = 2
out = json.dumps(merged, ensure_ascii=False, indent=indent)
if crlf:
    out = out.replace("\n", "\r\n")
with open(os.path.join(REPO, p), "w", encoding="utf-8", newline="") as fh:
    fh.write(out)
json.load(open(os.path.join(REPO, p), encoding="utf-8"))
n_b, n_o = len(base.get("sigs", {})), len(ours.get("sigs", {}))
print("crash_fuse merged: sigs %d/%d -> %d, cleared %d/%d -> %d%s" % (
    n_b, n_o, len(merged.get("sigs", {})),
    len(base.get("cleared", {})), len(ours.get("cleared", {})),
    len(merged.get("cleared", {})), " (CRLF)" if crlf else ""))
for n in notes:
    print("  note:", n)

# --- 2. pool_core_samples.jsonl: line-level union (origin lines first, bm-b-only lines appended) ---
p2 = "results/pool_core_samples.jsonl"
base_lines = stage(p2, 2).decode("utf-8").splitlines()
ours_lines = stage(p2, 3).decode("utf-8").splitlines()
base_set, seen = set(base_lines), set()
union, local_only = list(base_lines), 0
for ln in ours_lines:
    if ln in base_set or ln in seen or not ln.strip():
        continue
    seen.add(ln)
    union.append(ln)
    local_only += 1
raw = stage(p2, 2)
nl = "\r\n" if b"\r\n" in raw else "\n"
with open(os.path.join(REPO, p2), "w", encoding="utf-8", newline="") as fh:
    fh.write(nl.join(union) + (nl if union else ""))
# parse-validate every line
for i, ln in enumerate(union):
    if ln.strip():
        json.loads(ln)
print("pool_core_samples: base %d + bm-b new %d = %d lines (jsonl all-parse ok)" % (
    len(base_lines), local_only, len(union)))

print("RESOLVER_DONE")
