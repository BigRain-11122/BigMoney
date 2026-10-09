# -*- coding: utf-8 -*-
"""r816 bm-c push-recovery leg: drift-normalize + rebase + push + delivery
self-verify (r814/r815 direct-rebase law, applied to the gitclose push
window; M-faces = CRLF-drift/daemon-rewrite regenerable faces)."""
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CREATE = 0x08000000


def git(args, timeout=90):
    r = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True,
                       creationflags=CREATE, timeout=timeout)
    return r.returncode, (r.stdout or b"").decode("utf-8", "replace"), \
        (r.stderr or b"").decode("utf-8", "replace")


def main():
    rc, st, _ = git(["status", "--porcelain"])
    drift = [l[3:].strip().strip('"') for l in st.splitlines()
             if l.strip() and l[:2] in (" M", "MM", "MT")]
    print("DRIFT faces=%d" % len(drift))
    if drift:
        rc3, _, _ = git(["checkout", "--"] + drift)
        print("DRIFT-NORMALIZE rc=%d" % rc3)
    rc, out, err = git(["rebase", "origin/main"])
    print("REBASE rc=%d %s" % (rc, (err or out).strip()[:200]))
    if rc == 0:
        rc, out, err = git(["push", "origin", "main"], timeout=120)
        print("PUSH rc=%d %s" % (rc, (err or out).strip()[:200]))
    git(["fetch", "origin"])
    rc, cnt, _ = git(["rev-list", "--left-right", "--count",
                      "HEAD...origin/main"])
    print("AHEAD-BEHIND %s" % cnt.strip())
    rc, head, _ = git(["rev-parse", "--short", "HEAD"])
    print("HEAD=%s" % head.strip())
    return 0 if cnt.strip().split() == ["0", "0"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
