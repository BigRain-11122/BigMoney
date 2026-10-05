"""r555 bm-c S0 churn-absorb + merge (r714/r713 law, r554 lineage).
Targeted add of round-start own faces -> commit -F -> merge origin/main
single-stop. UU truth source = git diff --name-only --diff-filter=U (r713).
No push here (close-time push per r524 two-hop law). CREATE_NO_WINDOW."""
import os
import subprocess
import sys

CREATE_NO_WINDOW = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FACES = [
    "Tools/_r554bmc_closerow.py",
    "Tools/_r554bmc_merge_resolve.py",
    "Tools/_r555bmc_s0.py",
    "results/_r554bmc_close_facts.txt",
    "results/autofill_state.bm-c.json",
    "results/saturation_engine/face_bm-c.json",
    "results/saturation_engine_state.bm-c.json",
    "round_reports-bm-c.md",
]

MSG = ("churn-absorb r555 bm-c: round-start own faces (r554 close tails x4: "
       "closerow edit + merge_resolve script + close_facts + RR close row; own "
       "daemon lane live x3: autofill/satengine face+state; r555 s0 probe) "
       "[via bm-c]")


def git(args, cwd=ROOT, check=True):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=cwd,
                       creationflags=CREATE_NO_WINDOW)
    return r.returncode, (r.stdout or b"").decode("utf-8", "replace"), \
        (r.stderr or b"").decode("utf-8", "replace")


def main():
    lock = os.path.join(ROOT, ".git", "index.lock")
    if os.path.exists(lock):
        print("INDEX-LOCK PRESENT -- abort (r523 law: race, do not retry loop)")
        sys.exit(2)
    # deterministic add of known own faces (r549 law: no status-visibility reliance)
    for f in FACES:
        rc, out, err = git(["add", "--", f])
        if rc != 0:
            print("ADD-FAIL rc=%d %s :: %s" % (rc, f, err.strip()[:120]))
            if rc == 128:
                print("rc128 = daemon race (r523): leave in tree, absorb at close")
                sys.exit(3)
    rc, out, _ = git(["diff", "--cached", "--name-only", "--no-renames"])
    staged = [l for l in out.splitlines() if l.strip()]
    print("STAGED-COUNT %d" % len(staged))
    for l in staged:
        print("  + %s" % l)
    if len(staged) != len(FACES):
        print("STAGED MISMATCH vs FACES -- abort")
        sys.exit(1)
    msgpath = os.path.join(ROOT, "results", "_r555bmc_commit_msg.txt")
    with open(msgpath, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(MSG + "\n")
    rc, out, err = git(["commit", "-F", msgpath])
    print("COMMIT rc=%d %s" % (rc, (err or out).strip()[:200]))
    if rc != 0:
        print("COMMIT FAIL -- abort, staged preserved for diagnosis")
        sys.exit(1)
    rc, head, _ = git(["rev-parse", "HEAD"])
    print("HEAD-AFTER-CHURN %s" % head.strip())
    # merge origin/main single-stop (r713 canon: merge-mode, no rebase)
    rc, out, err = git(["merge", "origin/main", "-m",
                        "merge origin/main round-555 S0 window (own churn "
                        "absorbed pre-merge, dirty-intersect=0, r713 law) "
                        "[via bm-c]"])
    print("MERGE rc=%d" % rc)
    print((out or err).strip()[:400])
    rc2, uu, _ = git(["diff", "--name-only", "--diff-filter=U"])
    uul = [l for l in uu.splitlines() if l.strip()]
    print("UU-COUNT %d" % len(uul))
    for l in uul:
        print("  UU %s" % l)
    if len(uul) == 0 and rc == 0:
        rc, head, _ = git(["rev-parse", "HEAD"])
        rc, ahead, _ = git(["rev-list", "--count", "origin/main..HEAD"])
        rc, behind, _ = git(["rev-list", "--count", "HEAD..origin/main"])
        rc, st, _ = git(["status", "--porcelain"])
        dirty = [l for l in st.splitlines() if l.strip()]
        print("POST-MERGE HEAD %s ahead=%s behind=%s dirty=%d" % (
            head.strip(), ahead.strip(), behind.strip(), len(dirty)))
        for l in dirty[:10]:
            print("  D %s" % l)
        print("S0-DONE")
    else:
        print("S0-MERGE-STOP: resolve UU before any commit (r713 law)")


if __name__ == "__main__":
    main()
