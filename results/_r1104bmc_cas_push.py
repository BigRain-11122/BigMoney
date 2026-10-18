# -*- coding: utf-8 -*-
# r1104 bm-c: CAS surgical push of the W274 PREREG FREEZE onto BigMoney origin/main.
# push#1 (local 15680f370) rejected non-FF: origin moved +4 (bm-a r1070 x2 / bm-b r1013 x2).
# Per r1096/r1098/r1005 law: no blind rebase over a dirty shared tree; pure plumbing graft:
# read-tree origin/main -> graft the 5 freeze blobs from local 15680f370 (all NEW paths on
# origin, zero deletion surface, reversal impossible) -> commit-tree -p origin/main ->
# push <sha>:refs/heads/main (pure fast-forward; origin re-move = non-FF reject = die,
# re-run safe via the all-NEW guard). Hard 40-hex validation on every sha field (CAS law).
# Local 15680f370 stays content-redundant; local main convergence happens at closeout.
import os
import re
import subprocess
import sys

GIT = r"C:\Program Files\Git\cmd\git.exe"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCALC = "15680f370"
FILES = [
    "research/PERPETUAL_N1_W274_PREREG.md",
    "results/_r1104bmc_build_w274_derive.py",
    "results/_r1104bmc_scan.py",
    "results/_w274bmc_needle_probe.json",
    "results/_w274bmc_prereg_derive.py",
]
MSG = os.path.join(os.environ.get("TEMP", "."), "w274_freeze_msg.txt")
HEX = re.compile(r"[0-9a-f]{40}")


def git(*a, env=None):
    r = subprocess.run([GIT] + list(a), capture_output=True, env=env, cwd=ROOT)
    return r.stdout.decode("utf-8", "replace").strip(), r.returncode


def die(m):
    print("ABORT: " + m)
    sys.exit(1)


out, rc = git("rev-parse", LOCALC + "^{commit}")
if rc != 0 or not HEX.fullmatch(out):
    die("local commit bad: %r" % out)
localc = out
for p in FILES:
    _, rc = git("rev-parse", "%s:%s" % (localc, p))
    if rc != 0:
        die("local blob missing: " + p)

out, rc = git("fetch", "origin")
if rc != 0:
    die("fetch failed")
out, rc = git("rev-parse", "origin/main")
if rc != 0 or not HEX.fullmatch(out):
    die("origin/main bad: %r" % out)
tip = out

for p in FILES:  # all-NEW guard = duplicate-delivery protection (re-run after success aborts here)
    _, rc = git("rev-parse", "origin/main:" + p)
    if rc == 0:
        die("origin already has %s (already delivered or foreign claim)" % p)

idx = os.path.join(os.environ.get("TEMP", "."), "w274cas-%d.idx" % os.getpid())
if os.path.exists(idx):
    os.remove(idx)
env = dict(os.environ)
env["GIT_INDEX_FILE"] = idx
_, rc = git("read-tree", tip, env=env)
if rc != 0:
    die("read-tree failed")
blobs = {}
for p in FILES:
    out, rc = git("rev-parse", "%s:%s" % (localc, p))
    if rc != 0 or not HEX.fullmatch(out):
        die("blob rev-parse bad for %s: %r" % (p, out))
    blobs[p] = out
    _, rc = git("update-index", "--add", "--cacheinfo", "100644,%s,%s" % (blobs[p], p), env=env)
    if rc != 0:
        die("update-index failed: " + p)
out, rc = git("write-tree", env=env)
if rc != 0 or not HEX.fullmatch(out):
    die("write-tree bad: %r" % out)
tree = out
if os.path.exists(idx):
    os.remove(idx)

out, rc = git("commit-tree", tree, "-p", tip, "-F", MSG)
if rc != 0 or not HEX.fullmatch(out):
    die("commit-tree bad: %r" % out)
newc = out

for p in FILES:  # graft verification: new commit carries my blobs byte-identically
    a, _ = git("rev-parse", "%s:%s" % (newc, p))
    if a != blobs[p]:
        die("graft blob mismatch: " + p)
for probe in ("scripts/saturation_engine.py", "results/watermark_red.json", "state.json",
              "results/token_usage.json", "fleet/machines/bm-a.json"):
    a, rc1 = git("rev-parse", "%s:%s" % (newc, probe))
    b, rc2 = git("rev-parse", "%s:%s" % (tip, probe))
    if rc1 != 0 or rc2 != 0 or a != b:
        die("origin content not preserved on: " + probe)

r = subprocess.run([GIT, "push", "origin", newc + ":refs/heads/main"],
                   capture_output=True, cwd=ROOT)
out = (r.stdout + b"\n" + r.stderr).decode("utf-8", "replace")
print(out.strip())
low = out.lower()
if r.returncode != 0 or any(w in low for w in ("fatal", "rejected", "failed", "error")):
    die("push failed rc=%d" % r.returncode)

git("fetch", "origin")
out, rc = git("rev-parse", "origin/main")
if out != newc:
    die("origin/main != newc after push: %r" % out)
_, rc = git("merge-base", "--is-ancestor", newc, "origin/main")
if rc != 0:
    die("is-ancestor failed")
_, rc = git("merge-base", "--is-ancestor", tip, "origin/main")
if rc != 0:
    die("old tip not ancestor (history rewrite!)")
print("CAS-PUSH-OK %s on origin/main (graft of %d files onto %s)" % (newc[:9], len(FILES), tip[:9]))
