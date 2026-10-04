# -*- coding: utf-8 -*-
"""r514 bm-c closeout driver phase-1: round commit + fetch + merge stop.
Zero-window git via python subprocess (CREATE_NO_WINDOW). Message via -F
file (r512 wrapper quote-swallowing law). UU list via git ls-files -u
python stdout only (r511 law 3). Bloodline: Tools/_r513bmc_closegit.py."""
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE = 0x08000000
MSG = os.path.join(ROOT, "results", "_r514bmc_msg.txt")


def git(args, capture=True):
    r = subprocess.run(["git"] + args, cwd=ROOT, capture_output=capture,
                        creationflags=CREATE)
    out = (r.stdout or b"").decode("utf-8", "replace")
    err = (r.stderr or b"").decode("utf-8", "replace")
    return r.returncode, out, err


def main():
    with open(MSG, "w", encoding="utf-8", newline="\n") as f:
        f.write("round 514: watch/maintenance round -- S6 38 legs rc0 CEO faces "
                "regen (REPORT/LIVE-2026-10-05, ZERO-DRIFT streak 14), orders/D-19 "
                "dual-scan zero unacked, smoke 48/48, quartet 4/4, attrition CLEAN, "
                "FF-only S0 integration of bm-b r708 wave, stale-takeover derives "
                "round 2\n")
    rc, out, err = git(["add", "-A"])
    print("ADD rc=%d %s" % (rc, (err or out).strip()[:200]))
    rc, out, err = git(["commit", "-F", MSG])
    print("COMMIT rc=%d %s" % (rc, (err or out).strip()[:300]))
    rc, out, err = git(["rev-parse", "HEAD"])
    print("HEAD %s" % out.strip())
    rc, out, err = git(["fetch", "origin"])
    print("FETCH rc=%d %s" % (rc, (err or out).strip()[:120]))
    rc, behind, _ = git(["rev-list", "--count", "HEAD..origin/main"])
    rc2, ahead, _ = git(["rev-list", "--count", "origin/main..HEAD"])
    print("AHEAD %s BEHIND %s" % (ahead.strip(), behind.strip()))
    if behind.strip() == "0":
        print("NO-MERGE-NEEDED")
        return
    mmsg = os.path.join(ROOT, "results", "_r514bmc_mmsg.txt")
    with open(mmsg, "w", encoding="utf-8", newline="\n") as f:
        f.write("merge r514: origin wave integration (S6 same-family regen faces)\n")
    rc, out, err = git(["merge", "origin/main", "-F", mmsg])
    print("MERGE rc=%d" % rc)
    print((err or out).strip()[:600])
    rc, uu, _ = git(["ls-files", "-u"])
    faces = sorted({l.split("\t", 1)[1].strip() for l in uu.splitlines() if "\t" in l})
    print("UU-FACES %d" % len(faces))
    for p in faces:
        print("UU %s" % p)


if __name__ == "__main__":
    main()
