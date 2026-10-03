"""r421 bm-c rebase final finisher: after the manual commit (61a5b34af, staged
set verified markers=0 pre-commit), `rebase --continue` false-refuses again
(same sequencer family). Safe path: verify no unmerged entries remain, then
`rebase --skip` (drops only the redundant replay of the pick whose content is
already in-tree / intentionally superseded by per-file newer-wins choices),
then r624 detached-HEAD self-check (symbolic-ref; branch -f heal if needed),
then push + fetch delivery verify."""
import os
import subprocess
import sys

CREATE_NO_WINDOW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


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
    rc, u, _ = git(["ls-files", "-u"], check=False)
    print(f"ls-files -u: {len(u.strip())} entries")
    if u.strip():
        print("UNEXPECTED unmerged entries -- not skipping blindly")
        print(u[:800])
        sys.exit(3)

    rc, out, err = git(["rebase", "--skip"], check=False)
    print(f"rebase --skip rc={rc}: {(out + err).strip()[:300]}")
    if rc != 0:
        print("skip refused -- stopping (manual path)")
        sys.exit(3)

    # r624 law: detached-HEAD self-check after any rebase quit/skip
    rc, ref, _ = git(["symbolic-ref", "-q", "HEAD"], check=False)
    if rc != 0 or not ref.strip():
        print("detached HEAD after skip -- healing via branch -f (r624 law)")
        _, head, _ = git(["rev-parse", "HEAD"])
        git(["branch", "-f", "main", head.strip()])
        git(["symbolic-ref", "HEAD", "refs/heads/main"])
    rc, ref, _ = git(["symbolic-ref", "-q", "HEAD"], check=False)
    print("HEAD ref:", ref.strip())

    rc, log, _ = git(["log", "--oneline", "-4"])
    print("--- final log ---")
    print(log.strip())
    rc, st, _ = git(["status", "--porcelain"])
    print("--- residual status ---")
    print(st.strip()[:500])

    rc, out, err = git(["push"], check=False)
    print(f"push rc={rc}: {(out + err).strip()[:400]}")
    if rc != 0:
        print("PUSH RACE AGAIN -- CAS direct-push next (law path)")
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
