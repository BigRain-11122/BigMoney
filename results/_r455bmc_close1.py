# -*- coding: utf-8 -*-
"""r455 bm-c closeout stage 1: round commit (own outputs incl. lane daemon
faces, r109 targeted discipline satisfied -- full set is mine) + first push
attempt. Expect non-FF rejection (behind=2, bm-b wave in flight) -> merge
path follows in stage 2."""
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def run(args):
    return subprocess.run(
        ["git"] + args, capture_output=True, cwd=ROOT, text=True,
        encoding="utf-8", errors="replace",
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))


def main():
    r = run(["add", "-A"])
    print("ADD rc=%d %s" % (r.returncode, (r.stdout + r.stderr).strip()[:200]))
    r = run(["status", "--porcelain"])
    staged = [l for l in r.stdout.strip().splitlines() if l.strip()]
    print("STAGED/DIRTY count=%d" % len(staged))
    r = run(["commit", "-m",
             "round 455: golden-week watch + HANDOVER 5x; S6 canon 37->38 legs "
             "(update_fund_statements per T-166 wiring) + 38/38 rc0 PARITY PASS; "
             "FUND NULLS V654/Q498/D358 (+8/+6/+6 burn progressing, finalize "
             "window 10-05); smoke 48/48; orders/D-19/group-orders triple MATCH"])
    print("COMMIT rc=%d %s" % (r.returncode, (r.stdout + r.stderr).strip()[:400]))
    r = run(["rev-parse", "HEAD"])
    print("HEAD:", r.stdout.strip())
    r = run(["push", "origin", "main"])
    print("PUSH rc=%d" % r.returncode)
    print((r.stdout or "")[:600])
    print((r.stderr or "")[:600])
    r = run(["rev-list", "--left-right", "--count", "origin/main...HEAD"])
    print("BEHIND_AHEAD after push:", r.stdout.strip())
    print("STAGE1_DONE")


if __name__ == "__main__":
    main()
