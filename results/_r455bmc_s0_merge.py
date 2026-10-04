# -*- coding: utf-8 -*-
"""r455 bm-c S0 step2: absorb own daemon faces + merge origin/main (r437/r637
net-path). Dirty faces (bm-c satengine) have EMPTY intersection with origin
change-set per survey, so merge is legal. UU survey printed for recipe-based
resolve in follow-up step. Push deferred to round closeout (S7)."""
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def run(args):
    return subprocess.run(
        ["git"] + args, capture_output=True, cwd=ROOT, text=True,
        encoding="utf-8", errors="replace",
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))


def main():
    r = run(["add", "results/saturation_engine/face_bm-c.json",
             "results/saturation_engine_state.bm-c.json"])
    print("ADD rc=%d %s" % (r.returncode, (r.stdout + r.stderr).strip()[:150]))
    r = run(["commit", "-m",
             "absorb: bm-c daemon live faces (satengine tick) pre-merge origin r657 wave"])
    print("ABSORB_COMMIT rc=%d %s" % (r.returncode, (r.stdout + r.stderr).strip()[:300]))
    r = run(["rev-parse", "HEAD"])
    print("HEAD after absorb:", r.stdout.strip())
    r = run(["merge", "origin/main", "--no-edit"])
    print("MERGE rc=%d" % r.returncode)
    print((r.stdout or "")[:1200])
    print((r.stderr or "")[:600])
    r = run(["diff", "--name-only", "--diff-filter=U"])
    uu = sorted(set(r.stdout.strip().splitlines()) - {""}) if r.stdout.strip() else []
    print("--- UU FACES (%d) ---" % len(uu))
    for f in uu:
        print(" ", f)
    r = run(["status", "--porcelain"])
    print("--- STATUS ---")
    print(r.stdout.strip()[:2000] or "(clean)")
    print("MERGE_STEP_DONE uu_count=%d" % len(uu))


if __name__ == "__main__":
    main()
