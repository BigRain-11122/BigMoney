"""r457 bm-c final closeout commit: add all 40 own faces, commit, push, verify;
on push race: fetch + merge origin/main (r437 netpath) then re-push."""
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
MSG = ("round 457: golden-week watch + FUND-QUALITY-P1-NULLS ownerless-window heal "
       "(pool surgery a093a7720 lineage: r637 3rd-shard miss + r288 self-lock found/fixed, "
       "5-gate verified, MSG-0915 to bm-b); S6 38/38 rc0 parity PASS (dualrun streak 51); "
       "smoke 48/48; orders 153/153 double-scan zero-diff; D-19+group-orders double MATCH; "
       "attrition CLEAN; claws TRUE; state+heartbeat r457")


def git(args):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=ROOT,
                       creationflags=CREATE_NO_WINDOW)
    return r.returncode, (r.stdout or b"").decode("utf-8", "replace"), \
        (r.stderr or b"").decode("utf-8", "replace")


def main():
    rc, st, _ = git(["status", "--porcelain"])
    paths = [l[3:].strip() for l in st.splitlines() if l.strip()]
    print("ADD %d paths" % len(paths))
    rc, out, err = git(["add"] + paths)
    print("ADD rc=%d %s" % (rc, err.strip()[:100]))
    rc, st2, _ = git(["diff", "--cached", "--name-only"])
    staged = [l.strip() for l in st2.splitlines() if l.strip()]
    if sorted(staged) != sorted(paths):
        print("ABORT staged mismatch %d vs %d" % (len(staged), len(paths)))
        git(["reset"])
        return
    rc, out, err = git(["commit", "-m", MSG])
    print("COMMIT rc=%d %s" % (rc, (out + err).strip()[:150]))
    rc, out, err = git(["push"])
    print("PUSH-1 rc=%d" % rc)
    if rc != 0:
        print((out + err).strip()[-300:])
        rc, out, err = git(["fetch", "origin"])
        rc, out, err = git(["merge", "origin/main", "--no-edit"])
        print("MERGE rc=%d" % rc)
        tail = (out + err).strip().splitlines()
        print("\n".join(tail[-5:]) if tail else "(clean)")
        rc, st3, _ = git(["status", "--porcelain"])
        uu = [l for l in st3.splitlines() if l.startswith("UU")]
        if uu:
            print("UU FACES: %s" % [l.strip() for l in uu])
            print("ABORT: UU needs manual resolve (r657 survey law) -- stopping for inspection")
            return
        rc, out, err = git(["push"])
        print("PUSH-2 rc=%d" % rc)
        print((out + err).strip()[-200:])
    r = subprocess.run(["python", "Tools\\push_verify.py"], capture_output=True,
                       cwd=ROOT, creationflags=CREATE_NO_WINDOW)
    print("PUSH_VERIFY rc=%d %s" % (r.returncode,
          ((r.stdout or b"") + (r.stderr or b"")).decode("utf-8", "replace").strip()[-300:]))


if __name__ == "__main__":
    main()
