# -*- coding: utf-8 -*-
"""r818 bm-c close commit + push + verify (in-repo helper, 1-gen pattern of
the r817 close face). Targeted add = every path from git status (all current
faces are own/daemon products this window; foreign half-done faces would be
skipped explicitly). Push SSH primary, HTTPS explicit-URL fallback without
touching remote config; post-push tracking-ref verify per O-20261001-1108."""
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CNW = 0x08000000
MSG = os.path.join(ROOT, "_r_bmc_s0msg.txt")
HTTPS_URL = "https://github.com/BigRain-11122/BigMoney.git"


def g(args, timeout=90):
    r = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True,
                       creationflags=CNW, timeout=timeout)
    return r.returncode, (r.stdout or b"").decode("utf-8", "replace"), \
        (r.stderr or b"").decode("utf-8", "replace")


def main():
    rc, o, _ = g(["status", "--porcelain"])
    paths = [l[3:].strip().strip('"') for l in o.splitlines() if l.strip()]
    if paths:
        rc, o, e = g(["add", "--"] + paths)
        print("ADD rc=%d %s" % (rc, (e or o).strip()[:200]))
    with open(MSG, "w", encoding="utf-8", newline="\n") as f:
        f.write("round 818: H3 weights 5/5 byte-exact (40.28GB) + 768P T2V "
                "test in-flight (prompt d21c754a, video-only per CEO audio "
                "ban) + pit-data receipt-step-death law + S6 40/40 rc0 + "
                "ORD watermark consumed + self-heal green [via bm-c r818]")
    rc, o, e = g(["commit", "-F", MSG])
    print("COMMIT rc=%d %s" % (rc, (e or o).strip()[:250]))
    rc, o, _ = g(["rev-parse", "--short", "HEAD"])
    head = o.strip()
    print("HEAD=%s" % head)
    rc, o, e = g(["push", "origin", "main"], timeout=120)
    print("PUSH-SSH rc=%d %s" % (rc, (e or o).strip()[:250]))
    if rc != 0:
        rc, o, e = g(["push", HTTPS_URL, "HEAD:main"], timeout=120)
        print("PUSH-HTTPS rc=%d %s" % (rc, (e or o).strip()[:250]))
    rc, o, e = g(["fetch", "origin"], timeout=90)
    print("FETCH rc=%d" % rc)
    rc, o, _ = g(["rev-list", "--left-right", "--count", "HEAD...origin/main"])
    print("AHEAD-BEHIND %s" % o.strip())
    rc, o, _ = g(["ls-remote", "origin", "main"], timeout=60)
    print("REMOTE-MAIN %s" % o.strip()[:60])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
