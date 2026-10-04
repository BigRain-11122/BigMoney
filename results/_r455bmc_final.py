# -*- coding: utf-8 -*-
"""r455 bm-c final micro-commit: S7-supplement report line + receipt file.
Targeted add only (r109 law). Push + delivery re-verify."""
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def run(args):
    return subprocess.run(
        ["git"] + args, capture_output=True, cwd=ROOT, text=True,
        encoding="utf-8", errors="replace",
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))


def main():
    r = run(["status", "--porcelain"])
    print("--- PRE-COMMIT STATUS ---")
    print(r.stdout.strip()[:1200] or "(clean)")
    r = run(["add", "round_reports-bm-c.md", "results/_r455bmc_supplement.py"])
    print("ADD rc=%d" % r.returncode)
    r = run(["commit", "-m",
             "round 455 S7-supplement: closeout claw-block(behind-type) + 14-UU "
             "merge resolve receipt (take-ours x12 by ts, lhb take-theirs, "
             "compute_audit union 201+201->212), DELIVERED 2a12c8fad verified"])
    print("COMMIT rc=%d %s" % (r.returncode, (r.stdout + r.stderr).strip()[:250]))
    r = run(["push", "origin", "main"])
    out = (r.stdout or "") + (r.stderr or "")
    print("PUSH rc=%d %s" % (r.returncode, out[:400]))
    r = run(["fetch", "origin"])
    r = run(["rev-list", "--left-right", "--count", "origin/main...HEAD"])
    behind, ahead = r.stdout.strip().split("\t")
    print("FINAL behind=%s ahead=%s" % (behind, ahead))
    print("FINAL_DELIVERY:", "DELIVERED" if ahead == "0" else "NOT-DELIVERED")
    r = run(["status", "--porcelain"])
    print("--- POST-COMMIT RESIDUE ---")
    print(r.stdout.strip()[:600] or "(clean)")


if __name__ == "__main__":
    main()
