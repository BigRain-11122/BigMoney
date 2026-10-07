"""r730 bm-c S0: targeted absorb of own daemon live faces + pull --rebase +
push delivered. r849 family law: commit -F message file via python subprocess
(wrapper -m mangling re-route), push always names origin explicitly, failure
reads full stderr before verdict. Targets = round-start dirty 4 (own daemon
live faces, never -A on dirty tree)."""
import os
import subprocess
import sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
MSG = os.path.join(REPO, "_r730bmc_commitmsg.txt")

TARGETS = [
    "results/_orphan_face_probe.json",
    "results/dispatcher_state.bm-c.json",
    "results/saturation_engine/face_bm-c.json",
    "results/saturation_engine_state.bm-c.json",
]


def git(args, check=True):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True)
    out = p.stdout.decode("utf-8", "replace")
    err = p.stderr.decode("utf-8", "replace")
    print("git %s rc=%d" % (args[0], p.returncode))
    if out.strip():
        print(out.strip()[:600])
    if err.strip():
        print("STDERR:", err.strip()[:600])
    if check and p.returncode != 0:
        print("HARD FAIL on:", " ".join(args))
        sys.exit(p.returncode)
    return p


def main():
    git(["status", "--porcelain"])
    for t in TARGETS:
        git(["add", "--", t])
    cached = git(["diff", "--cached", "--name-only"])
    names = [l for l in cached.stdout.decode("utf-8", "replace").splitlines() if l.strip()]
    print("staged %d files: %s" % (len(names), names))
    if not names:
        print("nothing staged; skip commit")
    else:
        with open(MSG, "w", encoding="utf-8", newline="\n") as f:
            f.write("round 730: absorb own daemon live faces (pre-open S0 window)\n")
        git(["commit", "-F", MSG])
    git(["pull", "--rebase"])
    git(["push", "origin", "main"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
