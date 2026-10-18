# -*- coding: utf-8 -*-
"""r1102 bm-c: post-surgery disk converge (origin-newer-wins materialization).

After surgery push (origin/main=839441a5 = origin tip tree + 8 freeze blobs), the
working tree still carries the local-line (r1101-closeout-era) versions of shared
faces. Live loop closeout would re-commit those stale faces -> regression of
bm-b r1011 / bm-a r1068 content on origin (r1008/r1061 family hazard).

Converge: for every tracked M/D face, materialize HEAD (== origin) version,
EXCEPT the two live loop probe faces (disk newer than any committed version):
  results/_s05_probe.bm-c.json, results/watermark_red.json  (kept disk-live)
Untracked files untouched. Zero data loss: pre-surgery status proved only those
two probe faces had uncommitted (live) content; all other disk content is
already committed in the superseded local line.
"""
import subprocess, sys, os

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
OLD_TIP = "b6bbb69e92"   # superseded local line tip (freeze commit)
NEW_TIP = "839441a547"   # surgery-pushed origin/main
SKIP_LIVE = {
    "results/_s05_probe.bm-c.json",
    "results/watermark_red.json",
}

def git(*args, **kw):
    return subprocess.run(["git", "-C", REPO] + list(args), capture_output=True, **kw)

def out(p):
    if p.returncode != 0:
        sys.stderr.write("GIT-FAIL %s :: %s\n" % (p.args[2:], p.stderr.decode("utf-8", "replace")[:400]))
        sys.exit(1)
    return p.stdout.decode("utf-8", "replace")

# 0. pre-flight: for the 2 live probe faces, disk-live version must be NEWER than
#    origin's committed version (rotating snapshot faces, newest-write-wins).
#    watermark_red.json: origin has bm-a 23:12 snapshot, disk has bm-c live >=23:30.
import json, datetime
def ts_of(d):
    s = str(d.get("ts", ""))
    s = s.replace("T", " ").split("+")[0].strip()
    return datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
for face in sorted(SKIP_LIVE):
    origin_raw = out(git("show", "%s:%s" % (NEW_TIP, face)))
    disk_raw = open(os.path.join(REPO, face.replace("/", os.sep)), "rb").read().decode("utf-8", "replace")
    t_origin = ts_of(json.loads(origin_raw))
    t_disk = ts_of(json.loads(disk_raw))
    verdict = "keep-disk" if t_disk >= t_origin else "MUST-MATERIALIZE-ORIGIN"
    print("STEP0 face=%s origin_ts=%s disk_ts=%s -> %s" % (face, t_origin, t_disk, verdict))
    if verdict != "keep-disk":
        sys.exit(2)
print("STEP0 probe_faces_disk_newer=PASS")

# 1. collect tracked M/D paths from status (worktree-side changes only)
st = out(git("status", "--porcelain")).splitlines()
paths, untracked = [], []
for entry in st:
    if not entry:
        continue
    xy, path = entry[:2], entry[3:]
    if xy == "??":
        untracked.append(path)
    else:
        paths.append(path)
tracked = [p for p in paths if p not in SKIP_LIVE]
skipped = [p for p in paths if p in SKIP_LIVE]
print("STEP1 tracked_to_materialize=%d skipped_live=%d untracked_untouched=%d"
      % (len(tracked), len(skipped), len(untracked)))

# 2. materialize HEAD version for each tracked face (per-path checkout; index==HEAD after reset --mixed)
fail = []
for p in tracked:
    r = git("checkout", "--", p)
    if r.returncode != 0:
        fail.append((p, r.stderr.decode("utf-8", "replace")[:160]))
if fail:
    for p, e in fail:
        sys.stderr.write("CHECKOUT-FAIL %s :: %s\n" % (p, e))
    sys.exit(3)
print("STEP2 checkout_done=%d failures=%d" % (len(tracked), len(fail)))

# 3. verify: remaining changes must be exactly the 2 live probe faces + untracked
st2 = out(git("status", "--porcelain"))
lines = [l for l in st2.splitlines() if l.strip()]
bad = [l for l in lines if not l.startswith("??") and l[3:] not in SKIP_LIVE]
if bad:
    sys.stderr.write("CONVERGE-INCOMPLETE residual tracked diffs:\n" + "\n".join(bad[:20]))
    sys.exit(4)
print("STEP3 residual=live_probes_only+%d_untracked" % len(untracked))
for l in lines:
    print("   " + l)

# 4. frozen prereg byte-proof: blob sha in new tree + disk file raw hash faces
blob = out(git("rev-parse", "HEAD:research/PERPETUAL_N1_W273_PREREG.md")).strip()
import hashlib
disk = open(os.path.join(REPO, "research", "PERPETUAL_N1_W273_PREREG.md"), "rb").read()
print("STEP4 prereg_blob=%s blob16=%s sha256_16=%s size=%d" % (
    blob, blob[:16], hashlib.sha256(disk).hexdigest()[:16], len(disk)))
w272_blob = out(git("rev-parse", "HEAD:research/PERPETUAL_N1_W272_PREREG.md")).strip()
print("    w272_blob16=%s (canon expectation b023511eba80a9bf)" % w272_blob[:16])
print("CONVERGE-OK")
