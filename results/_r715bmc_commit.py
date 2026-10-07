# -*- coding: utf-8 -*-
# r715 bm-c round commit + push + delivery self-check (r713/r714 pattern)
import subprocess

NO = getattr(subprocess, 'CREATE_NO_WINDOW', 0)

def g(*args):
    r = subprocess.run(["git"] + list(args), capture_output=True, creationflags=NO)
    out = (r.stdout + r.stderr).decode("utf-8", "replace")
    return r.returncode, out

MSG = ("round 715: 5x HANDOVER (r711-715 window refresh) + QA 5/5 det-36th (equity 1,017,839 "
       "frozen identity) + S6 39/39 rc0 (dualrun streak 35) + W180 harvest chain 801,905 live "
       "read [via bm-c r715]")

def main():
    rc, out = g("status", "--porcelain")
    print("PRE_STATUS lines=%d" % len([l for l in out.splitlines() if l.strip()]))
    rc, out = g("add", "-A")
    print("ADD rc=%d %s" % (rc, out.strip()[:200]))
    rc, out = g("commit", "-m", MSG)
    print("COMMIT rc=%d %s" % (rc, out.strip()[:300]))
    if rc != 0:
        print("COMMIT FAILED -- abort push, report honestly")
        return 1
    rc, out = g("push")
    print("PUSH rc=%d %s" % (rc, out.strip()[:300]))
    if rc != 0:
        rc2, out2 = g("pull", "--rebase")
        print("PULL-REBASE retry rc=%d %s" % (rc2, out2.strip()[:300]))
        if rc2 == 0:
            rc3, out3 = g("push")
            print("PUSH2 rc=%d %s" % (rc3, out3.strip()[:300]))
        else:
            rc4, out4 = g("push", "origin", "HEAD:refs/heads/machine/bm-c-r715")
            print("BRANCH-PUSH rc=%d %s" % (rc4, out4.strip()[:300]))
            print("NOTE: race fallback per law -> machine/bm-c-r715")
    # delivery self-check
    g("fetch", "origin")
    rc, out = g("rev-list", "--count", "HEAD..origin/main")
    behind = out.strip()
    rc, out = g("rev-list", "--count", "origin/main..HEAD")
    ahead = out.strip()
    rc, out = g("log", "--oneline", "-2")
    print("VERIFY behind=%s ahead=%s" % (behind, ahead))
    print("LOCAL TIP:\n" + out)
    print("DELIVERED=%s" % (behind == "0"))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
