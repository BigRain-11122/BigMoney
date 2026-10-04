# -*- coding: utf-8 -*-
"""r455 bm-c S0 survey (read-only): fetch, behind/ahead, dirty faces, origin
faces, reflog 3-evidence concurrent-session check (r643 law). Zero-action
probe; merge/absorb decisions follow in a separate step per survey output."""
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def run(args, cwd=ROOT):
    return subprocess.run(
        args, capture_output=True, cwd=cwd, text=True, encoding="utf-8",
        errors="replace", creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))


def main():
    r = run(["git", "fetch", "origin"])
    print("FETCH rc=%d %s" % (r.returncode, (r.stderr or "").strip()[:200]))
    r = run(["git", "rev-list", "--left-right", "--count", "origin/main...HEAD"])
    print("BEHIND_AHEAD (origin-behind  local-ahead):", r.stdout.strip())
    r = run(["git", "status", "--porcelain"])
    print("--- STATUS PORCELAIN ---")
    print(r.stdout.strip() or "(clean)")
    r = run(["git", "diff", "--name-only", "HEAD", "origin/main"])
    origin_faces = sorted(set(r.stdout.strip().splitlines()) - {""}) if r.stdout.strip() else []
    print("--- ORIGIN-DIFF FACES (%d) ---" % len(origin_faces))
    for f in origin_faces:
        print(" ", f)
    r = run(["git", "log", "--format=%h|%ci|%s", "-8", "HEAD..origin/main"])
    print("--- INCOMING COMMITS ---")
    print(r.stdout.strip() or "(none)")
    r = run(["git", "log", "--format=%h|%ci|%s", "-4", "origin/main..HEAD"])
    print("--- LOCAL AHEAD COMMITS ---")
    print(r.stdout.strip() or "(none)")
    r = run(["git", "reflog", "--format=%h|%gd|%gs", "-12"])
    print("--- REFLOG TAIL 12 ---")
    print(r.stdout.strip())
    r = run(["git", "branch", "--show-current"])
    print("BRANCH:", r.stdout.strip() or "(detached?)")
    r = run(["git", "stash", "list"])
    print("STASH:", r.stdout.strip() or "(empty)")
    # rebase-merge residue check (r630 dead-rebase law)
    import os
    rm = os.path.join(ROOT, ".git", "rebase-merge")
    print("REBASE_MERGE_DIR:", "EXISTS" if os.path.isdir(rm) else "absent")
    print("SURVEY_DONE")


if __name__ == "__main__":
    main()
