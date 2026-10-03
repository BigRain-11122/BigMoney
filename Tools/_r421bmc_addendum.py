"""r421 bm-c final addendum commit: 5 surgical tools + pit-tooling +1 entry +
round-report addendum line. Byte accounting printed (r420 direct-write
style). Push + fetch delivery verify (race handled by pull --rebase once,
per law)."""
import os
import subprocess
import sys

CREATE_NO_WINDOW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

FILES = [
    "Tools/_r421bmc_addendum.py",
    "Tools/_r421bmc_close2.py",
    "Tools/_r421bmc_rebase_finish.py",
    "Tools/_r421bmc_rebase_resolve.py",
    "Tools/_r421bmc_rebase_resolve2.py",
    "Tools/_r421bmc_rebase_skip.py",
    "research/pit-tooling.md",
    "round_reports-bm-c.md",
]

MSG = ("round 421 bm-c addendum: push-race rebase surgery trail (14 regen "
       "faces ts-newer-wins, r613-family continue false-refusal closed via "
       "verified manual-commit + skip) + 5 surgical tools + pit-tooling +1 "
       "(mixed-separator ISO ts max() false-older) [via bm-c]")


def git(args, check=True):
    e = dict(os.environ)
    e["GIT_EDITOR"] = "true"
    r = subprocess.run(["git"] + args, capture_output=True, cwd=ROOT,
                       creationflags=CREATE_NO_WINDOW, env=e)
    out = (r.stdout or b"").decode("utf-8", "replace")
    err = (r.stderr or b"").decode("utf-8", "replace")
    if check and r.returncode != 0:
        print(f"GIT FAIL {args[:3]} rc={r.returncode}")
        print((out + err)[-600:])
        sys.exit(2)
    return r.returncode, out, err


def main():
    # byte accounting for the direct-write pit entry (worktree CRLF face)
    p = os.path.join(ROOT, "research", "pit-tooling.md")
    with open(p, "rb") as fh:
        n = len(fh.read())
    print(f"pit-tooling.md worktree bytes now: {n} (pre-entry 6,690B expected "
          f"family; delta = entry + CRLF overhead)")

    rc, st, _ = git(["status", "--porcelain"])
    print("--- pre-add ---")
    print(st.strip()[:600])

    git(["add", "--"] + FILES)
    rc, staged, _ = git(["diff", "--cached", "--name-status"])
    staged_files = {ln.split("\t", 1)[1] for ln in staged.strip().splitlines()
                    if ln.strip()}
    extra = staged_files - set(FILES)
    if extra:
        print(f"ABORT: unexpected staged: {extra}")
        sys.exit(2)
    print("staged:", sorted(staged_files))

    rc, out, err = git(["commit", "-m", MSG], check=False)
    print(f"commit rc={rc}: {(out + err).strip()[:300]}")
    if rc != 0:
        sys.exit(2)

    rc, out, err = git(["pull", "--rebase"], check=False)
    print(f"pull --rebase rc={rc}: {(out + err).strip()[:300]}")
    if rc != 0:
        print("RACE/CONFLICT on addendum -- manual path (report)")
        sys.exit(3)

    rc, out, err = git(["push"], check=False)
    print(f"push rc={rc}: {(out + err).strip()[:300]}")
    if rc != 0:
        rc2, out2, err2 = git(["pull", "--rebase"], check=False)
        print(f"pull retry rc={rc2}: {(out2 + err2).strip()[:200]}")
        if rc2 == 0:
            rc3, out3, err3 = git(["push"], check=False)
            print(f"push retry rc={rc3}: {(out3 + err3).strip()[:200]}")
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
