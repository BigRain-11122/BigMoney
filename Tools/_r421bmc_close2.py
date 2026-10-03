"""r421 bm-c close leg-2: S6-chain output faces + guard evidence as a second
targeted commit, then rebase over origin-6, orders re-scan, push, verify."""
import json
import subprocess
import sys

CREATE_NO_WINDOW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

FILES = [
    "docs/daily_report/REPORT-2026-10-03.json",
    "docs/daily_report/REPORT-2026-10-03.md",
    "docs/live_usage/LIVE-2026-10-03.json",
    "docs/live_usage/LIVE-2026-10-03.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/_r416bmc_s6_log.txt",
    "results/compute_audit.bm-c.json",
    "results/compute_audit.json",
    "results/fund_premium_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.bm-c.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.bm-c.json",
    "results/lhb_update_status.json",
    "results/pool_dualrun.bm-c.jsonl",
    "results/regime_state.bm-c.json",
    "results/regime_state.json",
    "results/runnable_pool.bm-c.json",
    "results/token_usage.bm-c.json",
    "results/token_usage.json",
    "results/update_status.bm-c.json",
    "results/update_status.json",
]

MSG = ("round 421 bm-c: S6 37-leg output faces + guard/audit evidence "
       "(daily report, CEO live page ORANGE/50%, regime shadow, dualrun "
       "streak 18, watermark/audit/token mirrors) [via bm-c]")


def git(args, check=True):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=ROOT,
                       creationflags=CREATE_NO_WINDOW)
    out = (r.stdout or b"").decode("utf-8", "replace")
    err = (r.stderr or b"").decode("utf-8", "replace")
    if check and r.returncode != 0:
        print(f"GIT FAIL {args[:3]} rc={r.returncode}")
        print(out[-900:])
        print(err[-900:])
        sys.exit(2)
    return r.returncode, out, err


def main():
    git(["add", "--"] + FILES)
    rc, staged, _ = git(["diff", "--cached", "--name-status"])
    staged_files = {ln.split("\t", 1)[1] for ln in staged.strip().splitlines()
                    if ln.strip()}
    extra = staged_files - set(FILES)
    if extra:
        print(f"ABORT: unexpected staged files: {extra}")
        sys.exit(2)
    print("staged:", len(staged_files), "files")

    rc, out, err = git(["commit", "-m", MSG], check=False)
    print(f"commit rc={rc}: {(out + err).strip()[:300]}")
    if rc != 0:
        sys.exit(2)

    rc, out, err = git(["pull", "--rebase"], check=False)
    print(f"pull --rebase rc={rc}")
    print((out + err).strip()[:900])
    if rc != 0:
        print("REBASE CONFLICT -- manual path per law (report, no force)")
        sys.exit(3)

    r = subprocess.run([sys.executable, "Tools/orders_diff.py"],
                       capture_output=True, cwd=ROOT,
                       creationflags=CREATE_NO_WINDOW)
    print("orders_diff:", (r.stdout or b"").decode("utf-8", "replace").strip())

    rc, out, err = git(["push"], check=False)
    print(f"push rc={rc}: {(out + err).strip()[:400]}")
    if rc != 0:
        rc2, out2, err2 = git(["pull", "--rebase"], check=False)
        print(f"pull retry rc={rc2}: {(out2 + err2).strip()[:300]}")
        if rc2 == 0:
            rc3, out3, err3 = git(["push"], check=False)
            print(f"push retry rc={rc3}: {(out3 + err3).strip()[:300]}")
            if rc3 != 0:
                sys.exit(4)
        else:
            sys.exit(4)

    git(["fetch", "origin"])
    _, ahead, _ = git(["rev-list", "--count", "origin/main..HEAD"])
    _, behind, _ = git(["rev-list", "--count", "HEAD..origin/main"])
    _, head, _ = git(["rev-parse", "--short", "HEAD"])
    print(f"DELIVERY: ahead={ahead.strip()} behind={behind.strip()} HEAD={head.strip()}")
    print("本地未达 origin commit 数 =", ahead.strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
