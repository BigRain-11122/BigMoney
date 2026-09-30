# r495 bm-b: rebase UU resolve per bigmoney-conflict-resolve skill
# - crash_fuse.json: canonical merge_crash_fuse (sigs key-union newer-wins + tombstone suppression, r387 law)
# - dashboard_status.{js,json} + scorecard_v1.json + strategy_scorecard.json: single-writer host=bm-a faces
#   (r378 D-03 C-family) -- bm-a alive again (r504 active), take origin side whole bytes
import json, subprocess, sys, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "scripts"))
import merge_lane_views as mlv  # noqa: E402

def stage(path, n):
    r = subprocess.run(["git", "-C", REPO, "show", ":%d:%s" % (n, path)],
                       capture_output=True)
    return r.stdout

# --- 1. crash_fuse.json: canonical union ---
p = "results/crash_fuse.json"
ours_b, theirs_b = stage(p, 2), stage(p, 3)
ours = json.loads(ours_b.decode("utf-8"))
theirs = json.loads(theirs_b.decode("utf-8"))
merged, notes = mlv.merge_crash_fuse([("base(origin)", ours), ("r495(bm-b)", theirs)])
# format mirror: probe base blob for CRLF + indent width
crlf = b"\r\n" in ours_b
indent = 1
head = ours_b.decode("utf-8").splitlines()[1][:6]
if head.startswith("   "):
    indent = 3
elif head.startswith("  "):
    indent = 2
out = json.dumps(merged, ensure_ascii=False, indent=indent)
if crlf:
    out = out.replace("\n", "\r\n")
with open(os.path.join(REPO, p), "w", encoding="utf-8", newline="") as fh:
    fh.write(out)
json.load(open(os.path.join(REPO, p), encoding="utf-8"))  # parse-validate before add
n_ours, n_theirs = len(ours.get("sigs", {})), len(theirs.get("sigs", {}))
print("crash_fuse merged: sigs %d/%d -> %d, cleared %d/%d -> %d%s" % (
    n_ours, n_theirs, len(merged.get("sigs", {})),
    len(ours.get("cleared", {})), len(theirs.get("cleared", {})),
    len(merged.get("cleared", {})), " (CRLF)" if crlf else ""))
for n in notes:
    print("  note:", n)

# --- 2. single-writer host=bm-a faces: take origin side whole bytes ---
for p in ["results/dashboard_status.js", "results/dashboard_status.json",
          "results/scorecard_v1.json", "results/strategy_scorecard.json"]:
    r = subprocess.run(["git", "-C", REPO, "checkout", "--ours", "--", p])
    if r.returncode != 0:
        print("CHECKOUT_FAIL", p, r.stderr)
        sys.exit(2)
    print("take-origin-side:", p)
print("RESOLVER_DONE")
