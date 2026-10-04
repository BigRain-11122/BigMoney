# -*- coding: utf-8 -*-
"""r517 bm-c commit+push: targeted add (verified face groups), commit,
push_verify canonical (pushes + verifies). Rejection ladder: pull --rebase
once; conflicts -> machine/bm-c-r517 branch fallback (report, no force)."""
import subprocess
import sys

CREATE = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
MSG = ("round 517: golden-week watch + QA evidence-pack standing re-run "
       "(qa/ 5/5 r517: smoke-r517.md + equity-curve-r517.png; S6 38/38 rc0 "
       "ZERO-DRIFT streak 17; smoke 48/48; quartet 4/4; task-family "
       "naming-face corrected via schtasks CSV cross-check)")


def git(*a):
    p = subprocess.run(["git"] + list(a), capture_output=True,
                       creationflags=CREATE, cwd=ROOT)
    out = (p.stdout or b"").decode("utf-8", "replace")
    err = (p.stderr or b"").decode("utf-8", "replace")
    return p.returncode, out, err


def main():
    rc, out, err = git("fetch", "origin")
    print("FETCH rc=%d %s" % (rc, (err or out).strip()[:100]))
    rc, behind, _ = git("rev-list", "--count", "HEAD..origin/main")
    rc2, ahead, _ = git("rev-list", "--count", "origin/main..HEAD")
    print("BEHIND %s AHEAD %s" % (behind.strip(), ahead.strip()))

    groups = ["CODELY.md", "docs/daily_report", "docs/live_usage",
              "fleet/machines/bm-c.json", "results", "qa",
              "round_reports-bm-c.md", "state-bm-c.json",
              "Tools/_r517bmc_close.py", "Tools/_r517bmc_s3.py",
              "Tools/_r517bmc_s6.py", "Tools/_r517bmc_s7_quartet.py"]
    for g in groups:
        rc, out, err = git("add", "--", g)
        if rc != 0:
            print("ADD-FAIL %s: %s" % (g, err.strip()[:160]))
            return 1
    rc, staged, err = git("diff", "--cached", "--name-only")
    n = len([l for l in staged.splitlines() if l.strip()])
    print("STAGED-COUNT %d" % n)
    for l in sorted(staged.splitlines()):
        if l.strip() and not (l.startswith(("results/", "docs/", "qa/",
                "Tools/_r517bmc_", "fleet/", "round_reports", "state-",
                "CODELY.md"))):
            print("UNEXPECTED-STAGED " + l)
            return 1
    rc, out, err = git("commit", "-m", MSG)
    ok = rc == 0
    print("COMMIT rc=%d %s" % (rc, (out or err).strip()[:200]))
    if not ok:
        return 1
    rc, head, _ = git("rev-parse", "HEAD")
    print("HEAD %s" % head.strip())

    # canonical delivery: push_verify pushes then verifies
    p = subprocess.run([sys.executable, "Tools/push_verify.py"],
                       capture_output=True, creationflags=CREATE, cwd=ROOT)
    print("PUSH_VERIFY rc=%d" % p.returncode)
    print((p.stdout or b"").decode("utf-8", "replace").strip()[-600:])
    verr = (p.stderr or b"").decode("utf-8", "replace").strip()
    if verr:
        print("PV-STDERR " + verr[-300:])
    if p.returncode == 0:
        print("DELIVERED")
        return 0

    # rejection ladder: pull --rebase once, then retry push_verify
    print("REJECTED -> pull --rebase ladder")
    rc, out, err = git("pull", "--rebase", "origin", "main")
    print("PULL-REBASE rc=%d %s" % (rc, (out or err).strip()[:200]))
    if rc != 0:
        rc, uu, _ = git("ls-files", "-u")
        if uu.strip():
            print("UU-FACES %d -> ABORT rebase, machine-branch fallback" %
                  len(uu.splitlines()))
            git("rebase", "--abort")
        else:
            print("rebase rc!=0 with zero UU (unstable churn) -> abort + "
                  "machine-branch fallback")
            git("rebase", "--abort")
    else:
        p = subprocess.run([sys.executable, "Tools/push_verify.py"],
                           capture_output=True, creationflags=CREATE, cwd=ROOT)
        print("PUSH_VERIFY-2 rc=%d" % p.returncode)
        print((p.stdout or b"").decode("utf-8", "replace").strip()[-600:])
        if p.returncode == 0:
            print("DELIVERED (after rebase)")
            return 0
    rc, head, _ = git("rev-parse", "HEAD")
    rc, out, err = git("push", "origin",
                       "%s:refs/heads/machine/bm-c-r517" % head.strip())
    print("MACHINE-BRANCH rc=%d %s" % (rc, (out or err).strip()[:200]))
    print("NOT-DELIVERED-MAIN (machine branch pushed per protocol)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
