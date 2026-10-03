"""r637 bm-b: D-19 decisions watermark probe (fresh-read law).

Byte-exact SHA-256 of origin/main:docs/decisions.md without touching any
working tree (K: group tree direct if visible, else temp sparse clone recipe
from r631). Zero tree writes on the group repo.
"""
import hashlib
import os
import subprocess
import sys

GROUP = r"K:\Fluxgroup\FluxGroup"


def run(cwd, *args, timeout=180):
    return subprocess.run(
        ["git", "-C", cwd, *args], capture_output=True, timeout=timeout
    )


def main():
    repo = GROUP
    if not os.path.isdir(os.path.join(GROUP, ".git")):
        tmp = os.path.join(os.environ["TEMP"], "fg-dec-bmb")
        if not os.path.isdir(os.path.join(tmp, ".git")):
            r = subprocess.run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "--filter=blob:none",
                    "--sparse",
                    "https://github.com/BigRain-11122/FluxGroup.git",
                    tmp,
                ],
                capture_output=True,
                timeout=300,
            )
            if r.returncode != 0:
                print("CLONE_FAIL:" + r.stderr.decode("utf-8", "replace")[:300])
                return 2
            r = run(tmp, "sparse-checkout", "set", "--skip-checks", "docs/decisions.md")
            if r.returncode != 0:
                print("SPARSE_FAIL:" + r.stderr.decode("utf-8", "replace")[:300])
                return 2
        repo = tmp
    run(repo, "fetch", "origin")
    r = run(repo, "show", "origin/main:docs/decisions.md")
    if r.returncode != 0 or not r.stdout:
        print("SHOW_FAIL:" + r.stderr.decode("utf-8", "replace")[:300])
        return 2
    print("DEC_SHA256:" + hashlib.sha256(r.stdout).hexdigest())
    # CEO pending-items face (same-law read, zero action unless lines touch BigMoney)
    o = run(repo, "show", "origin/main:docs/orders.md")
    if o.returncode == 0 and o.stdout:
        lines = o.stdout.decode("utf-8", "replace").splitlines()
        hits = [ln for ln in lines if ("BigMoney" in ln or "quant" in ln)]
        print("ORDERS_FACE_HITS:" + str(len(hits)))
        for ln in hits[-10:]:
            print("HIT:" + ln[:200])
    else:
        print("ORDERS_FACE_UNAVAILABLE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
