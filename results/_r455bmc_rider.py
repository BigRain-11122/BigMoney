# -*- coding: utf-8 -*-
"""r455 bm-c receipts rider: commit the two trailing receipts (close4/final).
Single push attempt; if a new wave blocks (behind-type claw), leave documented
for next-round absorb (zero loss, files remain in worktree)."""
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def run(args):
    return subprocess.run(
        ["git"] + args, capture_output=True, cwd=ROOT, text=True,
        encoding="utf-8", errors="replace",
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))


def main():
    r = run(["add", "results/_r455bmc_close4.py", "results/_r455bmc_final.py"])
    print("ADD rc=%d" % r.returncode)
    r = run(["commit", "-m",
             "round 455 receipts rider: close4 (merge commit+push verify) and "
             "final (supplement micro-commit) drivers, in-repo per r430 law"])
    print("COMMIT rc=%d %s" % (r.returncode, (r.stdout + r.stderr).strip()[:200]))
    r = run(["push", "origin", "main"])
    out = (r.stdout or "") + (r.stderr or "")
    print("PUSH rc=%d %s" % (r.returncode, out[:400]))
    r = run(["fetch", "origin"])
    r = run(["rev-list", "--left-right", "--count", "origin/main...HEAD"])
    behind, ahead = r.stdout.strip().split("\t")
    print("RIDER behind=%s ahead=%s" % (behind, ahead))
    print("RIDER_DELIVERY:", "DELIVERED" if ahead == "0" and r.returncode == 0
          else "LEFT-FOR-NEXT-ROUND(behind-type, documented)")
    r = run(["status", "--porcelain"])
    print("--- RESIDUE ---")
    print(r.stdout.strip()[:400] or "(clean)")


if __name__ == "__main__":
    main()
