# -*- coding: utf-8 -*-
"""r455 bm-c closeout stage 2: merge origin/main (r648 law -- behind-type claw
block resolves by merge, deletion set becomes empty), UU survey printed for
recipe-based resolve. Merge legal over rebase (r637 daemon treadmill law)."""
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def run(args):
    return subprocess.run(
        ["git"] + args, capture_output=True, cwd=ROOT, text=True,
        encoding="utf-8", errors="replace",
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))


def main():
    r = run(["fetch", "origin"])
    print("FETCH rc=%d %s" % (r.returncode, (r.stderr or "").strip()[:200]))
    r = run(["rev-list", "--left-right", "--count", "origin/main...HEAD"])
    print("BEHIND_AHEAD:", r.stdout.strip())
    r = run(["merge", "origin/main", "--no-edit"])
    print("MERGE rc=%d" % r.returncode)
    print((r.stdout or "")[:1500])
    print((r.stderr or "")[:400])
    r = run(["diff", "--name-only", "--diff-filter=U"])
    uu = sorted(set(r.stdout.strip().splitlines()) - {""}) if r.stdout.strip() else []
    print("--- UU FACES (%d) ---" % len(uu))
    for f in uu:
        print(" ", f)
    r = run(["status", "--porcelain"])
    dirty = [l for l in r.stdout.strip().splitlines()
             if l.strip() and not l.startswith("??")]
    print("--- NON-UU DIRTY (%d) ---" % len(dirty))
    for l in dirty[:15]:
        print(" ", l[:150])
    print("STAGE2_DONE uu_count=%d" % len(uu))


if __name__ == "__main__":
    main()
