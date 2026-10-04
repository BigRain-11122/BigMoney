"""r457 bm-c S0c: churn absorb (4 lane daemon faces, zero intersection) + pull --rebase heal.
Staged-set exact-match guard before commit (anti-swallow); rebase leftover check after;
all git children CREATE_NO_WINDOW."""
import os
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FACES = [
    "results/autofill_state.bm-c.json",
    "results/dispatcher_state.bm-c.json",
    "results/saturation_engine/face_bm-c.json",
    "results/saturation_engine_state.bm-c.json",
]
MSG = "churn absorb (bm-c r457 S0): satengine/autofill/dispatcher lane faces (treadmill, r648/r437 law)"


def git(args, cwd=ROOT):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=cwd,
                       creationflags=CREATE_NO_WINDOW)
    return r.returncode, (r.stdout or b"").decode("utf-8", "replace"), \
        (r.stderr or b"").decode("utf-8", "replace")


def main():
    rc, out, err = git(["add"] + FACES)
    print("ADD rc=%d %s" % (rc, err.strip()[:120]))
    rc, st, _ = git(["diff", "--cached", "--name-only"])
    staged = [l.strip() for l in st.splitlines() if l.strip()]
    print("STAGED %s" % staged)
    if sorted(staged) != sorted(FACES):
        print("ABORT: staged set mismatch (anti-swallow guard)")
        git(["reset"])
        return
    rc, out, err = git(["commit", "-m", MSG])
    print("COMMIT rc=%d %s" % (rc, (out + err).strip()[:200]))
    rc, out, err = git(["pull", "--rebase"])
    print("PULL-REBASE rc=%d" % rc)
    tail = (out + err).strip().splitlines()
    print("\n".join(tail[-8:]) if tail else "(clean)")
    rb = os.path.join(ROOT, ".git", "rebase-merge")
    print("REBASE-MERGE-EXIST %s" % os.path.exists(rb))
    rc, h, _ = git(["rev-parse", "--short", "HEAD"])
    print("HEAD %s" % h.strip())
    rc, a, _ = git(["rev-list", "--count", "origin/main..HEAD"])
    rc2, b, _ = git(["rev-list", "--count", "HEAD..origin/main"])
    print("AHEAD %s BEHIND %s" % (a.strip(), b.strip()))


if __name__ == "__main__":
    main()
