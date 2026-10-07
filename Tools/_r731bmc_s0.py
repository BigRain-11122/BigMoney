"""r731 bm-c S0: targeted absorb of own daemon live faces + pull --rebase +
push delivered. r849 family law: commit -F message file via python subprocess
(wrapper -m mangling re-route), push always names origin explicitly, failure
reads full stderr before verdict. Targets = round-start dirty own daemon
live faces (never -A on dirty tree). Daemon live-write race fallback:
treasure_guard restore-class gate + checkout of unstaged live faces then
one rebase retry (r730 same-window canon).
Pattern credit: Tools/_r730bmc_s0.py (canonical clone chain)."""
import os
import subprocess
import sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
MSG = os.path.join(REPO, "_r731bmc_commitmsg.txt")

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
            f.write("round 731: absorb own daemon live faces (pre-open S0 window)\n")
        git(["commit", "-F", MSG])
    pull = git(["pull", "--rebase"], check=False)
    if pull.returncode != 0:
        # daemon live-write race: gate unstaged live faces then checkout, retry once
        df = git(["diff", "--name-only"])
        dirty = [l for l in df.stdout.decode("utf-8", "replace").splitlines() if l.strip()]
        print("unstaged dirty faces:", dirty)
        if dirty:
            tg = subprocess.run([sys.executable, os.path.join(REPO, "Tools",
                                   "treasure_guard.py"), "restore"] + dirty,
                                capture_output=True)
            print("treasure_guard rc=%d" % tg.returncode)
            if tg.returncode != 0:
                print(tg.stdout.decode("utf-8", "replace")[-300:])
                print("TREASURE GUARD REFUSED - honest stop")
                sys.exit(3)
            for t in dirty:
                git(["checkout", "--", t])
            pull2 = git(["pull", "--rebase"], check=False)
            if pull2.returncode != 0:
                print("REBASE STILL FAILING - honest stop, no force, no autostash")
                sys.exit(4)
    git(["push", "origin", "main"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
