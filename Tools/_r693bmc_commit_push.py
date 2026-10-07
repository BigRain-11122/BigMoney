"""r693 bm-c closeout commit + push + fetch delivery self-verify.
Round-start tree was clean (post-absorb) -> git add -A legal. Commit via
-F msg file (zero-window pattern). Push (pre-push claw audits deletion
set); rejected -> pull --rebase once -> push -> else machine/bm-c-r693
branch fallback + note. Then fetch + behind-count = N (delivery gate).
Facts -> stdout."""
import os
import subprocess
import sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
MSG = os.path.join(REPO, "_r693bmc_commitmsg2.txt")


def git(args, check=True):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True)
    out = (p.stdout + p.stderr).decode("utf-8", "replace")
    if check and p.returncode != 0:
        print("GIT FAIL rc=%d: %s" % (p.returncode, out[:500]))
        raise SystemExit(2)
    return p.returncode, out


with open(MSG, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(
        "round 693 bm-c: QA r693 5/5 evidence pack (93 trades determinism=True, "
        "png 66,216B, equity 1,017,839 identical) + S6 39/39 rc0 (dualrun streak 13; "
        "bm-a hb stale -> lane_io stale-takeover reprise) + GM advisory M-20261007-01 "
        "(bm-b stall escalation per r692 next(c): NULLS 1786/2000 done 214 missing, "
        "fuse refusals 1212, bm-c cache-absent; wait-for-revival default + 2 GM options) "
        "+ post_review latest-row-per-item canon pit direct-write pit-tooling.md + "
        "r833 pointer migration (r667 precedent) + in-window truncation heal receipt "
        "(union per treasure_guard rc3, zero origin harm) + tripwire/attrition CLEAN "
        "+ boards 0 open (guard round, reopen 10-08)\n"
    )

rc, out = git(["add", "-A"])
print("add rc=%d" % rc)
rc, out = git(["status", "--porcelain"])
print("staged/untracked summary lines:", len(out.splitlines()))
rc, out = git(["commit", "-F", MSG])
print("commit rc=%d" % rc)
print(out[:300])

rc, out = git(["push"], check=False)
print("push#1 rc=%d" % rc)
print(out[:400])
if rc != 0:
    rc2, out2 = git(["pull", "--rebase"], check=False)
    print("pull --rebase rc=%d" % rc2)
    print(out2[:400])
    rc3, out3 = git(["push"], check=False)
    print("push#2 rc=%d" % rc3)
    print(out3[:300])
    if rc3 != 0:
        rc4, out4 = git(["push", "origin", "HEAD:machine/bm-c-r693"], check=False)
        print("branch fallback rc=%d" % rc4)
        print(out4[:300])

git(["fetch", "origin"])
rc, out = git(["rev-list", "--count", "origin/main..HEAD"])
ahead = out.strip()
rc, out = git(["rev-list", "--count", "HEAD..origin/main"])
behind = out.strip()
print("DELIVERY: ahead=%s behind=%s" % (ahead, behind))
rc, out = git(["log", "--oneline", "-1"])
print("HEAD:", out.strip()[:120])
