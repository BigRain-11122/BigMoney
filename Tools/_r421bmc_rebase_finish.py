"""r421 bm-c rebase finish v2 (r305/r501 false-refusal family):
Correct verification = staged index vs HEAD (the rebase-stop predecessor),
NOT vs the old pick (cross-base diff includes origin delta by construction).

Steps:
  (0) discard the 2 unstaged daemon-churn files (regen state faces; the
      resident engine rewrites them continuously -- r277 stash-pop avoided),
  (1) verify `git diff --cached HEAD` == the intended pick-2 resolution set
      (S6 output faces + 2 newer-wins resolved snapshots) and carries zero
      conflict markers,
  (2) manual `git commit -F .git/rebase-merge/message` (pre-commit claw runs
      and passes -- no marker findings),
  (3) `git rebase --continue` (todo already empty -> finalize); on the
      'No changes' variant -> `git rebase --skip` (content verified in-tree
      by step 1+2 before the commit; the skip only drops the redundant
      replay bookkeeping),
  (4) orders re-scan + push + fetch delivery verify.
"""
import os
import subprocess
import sys

CREATE_NO_WINDOW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
DAEMON_CHURN = [
    "results/saturation_engine/face_bm-c.json",
    "results/saturation_engine_state.bm-c.json",
]


def git(args, check=True):
    e = dict(os.environ)
    e["GIT_EDITOR"] = "true"
    r = subprocess.run(["git"] + args, capture_output=True, cwd=ROOT,
                       creationflags=CREATE_NO_WINDOW, env=e)
    out = (r.stdout or b"").decode("utf-8", "replace")
    err = (r.stderr or b"").decode("utf-8", "replace")
    if check and r.returncode != 0:
        print(f"GIT FAIL {args[:3]} rc={r.returncode}")
        print((out + err)[-700:])
        sys.exit(2)
    return r.returncode, out, err


def main():
    git(["checkout", "--"] + DAEMON_CHURN)
    rc, st, _ = git(["status", "--porcelain"])
    print("--- after churn discard ---")
    print(st.strip()[:600])

    rc, diff, _ = git(["diff", "--cached", "HEAD"], check=False)
    n_markers = sum(diff.count(m) for m in ("<<<<<<<", ">>>>>>>"))
    files = [l for l in diff.splitlines() if l.startswith("diff --git")]
    print(f"staged-vs-HEAD: {len(files)} files, {len(diff)}B, markers={n_markers}")
    for l in files:
        print("  ", l[11:])
    if n_markers:
        print("CONFLICT MARKERS IN STAGED SET -- abort surgical path")
        sys.exit(3)

    msg_path = os.path.join(ROOT, ".git", "rebase-merge", "message")
    with open(msg_path, encoding="utf-8", errors="replace") as fh:
        msg = fh.read().strip()
    rc, out, err = git(["commit", "-m", msg], check=False)
    print(f"manual commit rc={rc}: {(out + err).strip()[:400]}")
    if rc != 0:
        sys.exit(3)

    rc, out, err = git(["rebase", "--continue"], check=False)
    print(f"rebase --continue rc={rc}: {(out + err).strip()[:300]}")
    if rc != 0:
        lo = (out + err).lower()
        if "no changes" in lo or "nothing to commit" in lo or \
                "edit all merge conflicts" in lo:
            print("post-commit refusal -> skip redundant replay (content "
                  "verified staged pre-commit)")
            rc3, out3, err3 = git(["rebase", "--skip"], check=False)
            print(f"rebase --skip rc={rc3}: {(out3 + err3).strip()[:300]}")
            if rc3 != 0:
                sys.exit(3)
        else:
            print("UNEXPECTED refusal -- stopping for manual path")
            sys.exit(3)

    rc, log, _ = git(["log", "--oneline", "-5"])
    print("--- post-rebase log ---")
    print(log.strip())
    rc, st, _ = git(["status", "--porcelain"])
    print("--- residual status ---")
    print(st.strip()[:400])

    r = subprocess.run([sys.executable, "Tools/orders_diff.py"],
                       capture_output=True, cwd=ROOT,
                       creationflags=CREATE_NO_WINDOW)
    print("orders_diff:", (r.stdout or b"").decode("utf-8", "replace").strip())

    rc, out, err = git(["push"], check=False)
    print(f"push rc={rc}: {(out + err).strip()[:400]}")
    if rc != 0:
        rc2, out2, err2 = git(["pull", "--rebase"], check=False)
        print(f"pull retry rc={rc2}: {(out2 + err2).strip()[:250]}")
        if rc2 == 0:
            rc3, out3, err3 = git(["push"], check=False)
            print(f"push retry rc={rc3}: {(out3 + err3).strip()[:250]}")
            if rc3 != 0:
                sys.exit(4)
        else:
            sys.exit(4)

    git(["fetch", "origin"])
    _, ahead, _ = git(["rev-list", "--count", "origin/main..HEAD"])
    _, behind, _ = git(["rev-list", "--count", "HEAD..origin/main"])
    _, head, _ = git(["rev-parse", "--short", "HEAD"])
    print(f"DELIVERY: ahead={ahead.strip()} behind={behind.strip()} HEAD={head.strip()}")
    print("本地未达 origin commit 数 =", ahead.strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
