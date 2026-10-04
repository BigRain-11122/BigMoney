"""r457 bm-c absorb2: churn-absorb 6 own faces (daemon x4 + post_review products x2)
+ pull --rebase. Staged-set exact-match guard."""
import os
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
FACES = [
    "results/autofill_state.bm-c.json",
    "results/dispatcher_state.bm-c.json",
    "results/post_review.jsonl",
    "results/post_review/REPORT-20261004.md",
    "results/saturation_engine/face_bm-c.json",
    "results/saturation_engine_state.bm-c.json",
]
MSG = "churn absorb (bm-c r457 S0d): satengine/autofill/dispatcher lane faces + post_review rerun ledger/report (r456 post-review discipline leg)"


def git(args):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=ROOT,
                       creationflags=CREATE_NO_WINDOW)
    return r.returncode, (r.stdout or b"").decode("utf-8", "replace"), \
        (r.stderr or b"").decode("utf-8", "replace")


def main():
    rc, out, err = git(["add"] + FACES)
    print("ADD rc=%d %s" % (rc, err.strip()[:120]))
    rc, st, _ = git(["diff", "--cached", "--name-only"])
    staged = [l.strip() for l in st.splitlines() if l.strip()]
    if sorted(staged) != sorted(FACES):
        print("ABORT staged mismatch: %s" % staged)
        git(["reset"])
        return
    print("STAGED OK %d faces" % len(staged))
    rc, out, err = git(["commit", "-m", MSG])
    print("COMMIT rc=%d %s" % (rc, (out + err).strip()[:160]))
    rc, out, err = git(["pull", "--rebase"])
    print("PULL-REBASE rc=%d" % rc)
    tail = (out + err).strip().splitlines()
    print("\n".join(tail[-6:]) if tail else "(clean)")
    rb = os.path.join(ROOT, ".git", "rebase-merge")
    print("REBASE-MERGE-EXIST %s" % os.path.exists(rb))
    rc, a, _ = git(["rev-list", "--count", "origin/main..HEAD"])
    rc2, b, _ = git(["rev-list", "--count", "HEAD..origin/main"])
    print("AHEAD %s BEHIND %s" % (a.strip(), b.strip()))


if __name__ == "__main__":
    main()
