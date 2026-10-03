"""r421 bm-c rebase resolve: both conflicted files are full-regen snapshots
(last-writer-wins semantics; token_usage delta chain + attrition scan ts).
Take MINE (theirs in rebase stage terms = the commit being replayed), add,
continue rebase, then orders re-scan + push + delivery verify.
GIT_EDITOR=true guards the --continue message confirmation (r501 family)."""
import os
import subprocess
import sys

CREATE_NO_WINDOW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
FILES = ["results/token_usage.json", "results/_attrition_guard_scan.json"]


def git(args, check=True, env=None):
    e = dict(os.environ)
    e["GIT_EDITOR"] = "true"
    if env:
        e.update(env)
    r = subprocess.run(["git"] + args, capture_output=True, cwd=ROOT,
                       creationflags=CREATE_NO_WINDOW, env=e)
    out = (r.stdout or b"").decode("utf-8", "replace")
    err = (r.stderr or b"").decode("utf-8", "replace")
    if check and r.returncode != 0:
        print(f"GIT FAIL {args[:3]} rc={r.returncode}")
        print(out[-700:])
        print(err[-700:])
        sys.exit(2)
    return r.returncode, out, err


def main():
    git(["checkout", "--theirs", "--"] + FILES)
    # verify no conflict markers remain, then stage
    for f in FILES:
        with open(os.path.join(ROOT, f), encoding="utf-8-sig") as fh:
            txt = fh.read()
        for marker in ("<<<<<<<", ">>>>>>>", "=======\n"):
            assert marker not in txt or marker == "=======\n" and False, \
                f"conflict marker remains in {f}"
        print(f"resolved (mine/newer): {f} {len(txt)}B")
    git(["add", "--"] + FILES)
    rc, out, err = git(["rebase", "--continue"], check=False)
    print(f"rebase --continue rc={rc}")
    print((out + err).strip()[:600])
    if rc != 0:
        # r501 false-refusal family: if the net path is fully absorbed
        # git refuses with 'No changes' -- verify tree state before --skip
        rc2, st, _ = git(["status", "--porcelain"])
        print("status:", st.strip()[:400])
        sys.exit(3)

    r = subprocess.run([sys.executable, "Tools/orders_diff.py"],
                       capture_output=True, cwd=ROOT,
                       creationflags=CREATE_NO_WINDOW)
    print("orders_diff:", (r.stdout or b"").decode("utf-8", "replace").strip())

    rc, out, err = git(["push"], check=False)
    print(f"push rc={rc}: {(out + err).strip()[:400]}")
    if rc != 0:
        rc2, out2, err2 = git(["pull", "--rebase"], check=False)
        print(f"pull retry rc={rc2}: {(out2 + err2).strip()[:300]}")
        if rc2 == 0:
            rc3, out3, err3 = git(["push"], check=False)
            print(f"push retry rc={rc3}: {(out3 + err3).strip()[:300]}")
            if rc3 != 0:
                sys.exit(4)
        else:
            sys.exit(4)

    git(["fetch", "origin"])
    _, ahead, _ = git(["rev-list", "--count", "origin/main..HEAD"])
    _, behind, _ = git(["rev-list", "--count", "HEAD..origin/main"])
    _, head, _ = git(["rev-parse", "--short", "HEAD"])
    _, log, _ = git(["log", "--oneline", "-4"])
    print("--- final log ---")
    print(log.strip())
    print(f"DELIVERY: ahead={ahead.strip()} behind={behind.strip()} HEAD={head.strip()}")
    print("本地未达 origin commit 数 =", ahead.strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
