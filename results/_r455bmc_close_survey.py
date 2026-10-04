# -*- coding: utf-8 -*-
"""r455 bm-c closeout survey: pre-commit tree status (who is dirty now)."""
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def run(args):
    return subprocess.run(
        ["git"] + args, capture_output=True, cwd=ROOT, text=True,
        encoding="utf-8", errors="replace",
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))


def main():
    r = run(["status", "--porcelain"])
    print("--- STATUS PORCELAIN ---")
    print(r.stdout.strip() or "(clean)")
    r = run(["rev-list", "--left-right", "--count", "origin/main...HEAD"])
    print("BEHIND_AHEAD:", r.stdout.strip())
    r = run(["diff", "--name-only", "HEAD", "origin/main"])
    print("--- ORIGIN-DIFF FACES ---")
    print(r.stdout.strip() or "(none)")
    print("SURVEY_DONE")


if __name__ == "__main__":
    main()
