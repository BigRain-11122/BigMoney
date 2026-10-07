# -*- coding: utf-8 -*-
# r715 bm-c S0: own-churn absorb pre-rebase + clean rebase + push + delivery self-check
# (r713/r714 pattern; net-tree zero-autostash law r642; targeted add r109 law)
import subprocess

NO = getattr(subprocess, 'CREATE_NO_WINDOW', 0)

def g(*args):
    r = subprocess.run(["git"] + list(args), capture_output=True, creationflags=NO)
    out = (r.stdout + r.stderr).decode("utf-8", "replace")
    return r.returncode, out

CHURN = [
    "fleet/machines/bm-c.json",
    "results/_orphan_face_probe.json",
    "results/autofill_state.bm-c.json",
    "results/dispatcher_state.bm-c.json",
    "results/idle_trigger.bm-c.json",
    "results/idle_trigger_state.bm-c.json",
    "results/saturation_engine/face_bm-c.json",
    "results/saturation_engine_state.bm-c.json",
]

def main():
    ok = True
    # 1) targeted add of bm-c-owned churn only (r109 law)
    rc, out = g("add", *CHURN)
    print("ADD rc=%d %s" % (rc, out.strip()[:300]))
    ok &= (rc == 0)
    # 2) absorb commit
    rc, out = g("commit", "-m", "r715 bm-c: churn absorb pre-rebase (lane state faces + orphan probe report)")
    print("COMMIT rc=%d %s" % (rc, out.strip()[:300]))
    ok &= (rc == 0)
    # 3) clean-tree rebase onto origin/main (zero autostash law)
    rc, out = g("rebase", "origin/main")
    print("REBASE rc=%d %s" % (rc, out.strip()[:400]))
    if rc != 0:
        print("REBASE CONFLICT -> read-only maintenance mode this round (per S0 law)")
        return 2
    # 4) push
    rc, out = g("push")
    print("PUSH rc=%d %s" % (rc, out.strip()[:300]))
    if rc != 0:
        rc2, out2 = g("pull", "--rebase")
        print("PULL-REBASE retry rc=%d %s" % (rc2, out2.strip()[:300]))
        if rc2 == 0:
            rc3, out3 = g("push")
            print("PUSH2 rc=%d %s" % (rc3, out3.strip()[:300]))
            ok &= (rc3 == 0)
        else:
            rc4, out4 = g("push", "origin", "HEAD:refs/heads/machine/bm-c-r715")
            print("BRANCH-PUSH rc=%d %s" % (rc4, out4.strip()[:300]))
            print("NOTE: pushed to machine/bm-c-r715 (race fallback per law)")
    # 5) delivery self-check: behind count + clean tree
    rc, out = g("rev-list", "--count", "HEAD..origin/main")
    behind = out.strip()
    rc, out = g("status", "--porcelain")
    print("VERIFY behind=%s porcelain_lines=%d" % (behind, len([l for l in out.splitlines() if l.strip()])))
    if out.strip():
        print("PORCELAIN:\n" + out[:800])
    rc, out = g("log", "--oneline", "-2")
    print("LOCAL TIP:\n" + out)
    print("S0_DONE ok=%s" % ok)
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
