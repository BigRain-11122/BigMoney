# -*- coding: utf-8 -*-
"""r755 bm-c commit+push driver: r751 law (round-start clean tree => closeout
add -A unconditionally), Money02/legacy red-line assert, commit -F msgfile,
push with non-FF rebase retry (UU -> honest stop for resolver), delivery
verify (fetch + ahead/behind + ls-tree product proof)."""
import os
import re
import subprocess

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CF = 0x08000000
MSG = os.path.join(REPO, "_r755bmc_commitmsg.txt")
PRODUCTS = [
    "qa/smoke-r755.md",
    "qa/equity-curve-r755.png",
    "results/_r755bmc_s6_log.txt",
    "results/_r755bmc_clone_receipt.json",
    "results/_r755bmc_fleet_adopt_receipt.json",
    "results/_r755bmc_silence_receipt.json",
    "research/HANDOVER.md",
    "state-bm-c.json",
    "fleet/machines/bm-c.json",
    "logs/iteration-loop/round_reports-bm-c.md",
]


def git(args):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True,
                       creationflags=CF)
    return p.returncode, p.stdout.decode("utf-8", "replace"), \
        p.stderr.decode("utf-8", "replace")


rc, out, _ = git(["status", "--porcelain"])
lines = [ln for ln in out.splitlines() if ln.strip()]
print("pre-add dirty faces: %d" % len(lines))

rc, _, err = git(["add", "-A"])
print("add rc=%d %s" % (rc, err[:150]))
rc, out, _ = git(["diff", "--cached", "--name-only"])
staged = [ln for ln in out.splitlines() if ln.strip()]
print("staged files: %d" % len(staged))
bad = [s for s in staged if s.startswith("Money02") or s.startswith("legacy")]
assert not bad, "RED-LINE staged: %s" % bad
for s in staged[:14]:
    print("  +", s)
if len(staged) > 14:
    print("  ... +%d more" % (len(staged) - 14))

rc, out, err = git(["commit", "-F", MSG])
print("commit rc=%d" % rc)
if rc != 0:
    print("commit err: %s" % err[:500])
    raise SystemExit(2)
rc, out, _ = git(["log", "-1", "--format=%h %s"])
print("head: %s" % out.strip()[:150])

rc, out, err = git(["push"])
print("push rc=%d out=%s err=%s" % (rc, out.strip()[:200], err.strip()[:200]))
if rc != 0:
    print("first push rejected -> fetch + rebase origin/main retry")
    git(["fetch", "origin"])
    rc, out, err = git(["rebase", "origin/main"])
    print("rebase rc=%d %s" % (rc, err[:300]))
    if rc != 0:
        rc2, uo, _ = git(["diff", "--name-only", "--diff-filter=U"])
        print("UU faces:\n%s" % uo)
        print("HONEST STOP: resolver required (r750 canon bloodline)")
        raise SystemExit(3)
    rc, out, err = git(["push"])
    print("push-retry rc=%d err=%s" % (rc, err.strip()[:200]))
    if rc != 0:
        raise SystemExit(4)

git(["fetch", "origin"])
rc, out, _ = git(["rev-list", "--left-right", "--count", "HEAD...origin/main"])
ahead, behind = out.strip().split("\t")
print("delivery: ahead=%s behind=%s (本地未达 origin commit 数=%s)" % (ahead, behind, behind))
for prod in PRODUCTS:
    rc, out, _ = git(["ls-tree", "origin/main", prod])
    present = bool(out.strip())
    print("  ls-tree %-52s %s" % (prod, "ON-ORIGIN" if present else "MISSING"))
rc, out, _ = git(["status", "--porcelain"])
print("post-status clean: %s" % (not [l for l in out.splitlines() if l.strip()]))
