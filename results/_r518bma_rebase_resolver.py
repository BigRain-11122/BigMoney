"""r518 bm-a rebase conflict resolver (r498 canon family, results/_r498_resolve.py lineage).

Situation: r517 round-close commits (d36eaac88/bb734cd68/e8ff52c15) never
reached origin (silent push miss discovered at r518 S0). Rebase replay of
d36eaac88 onto origin/main (which advanced: bm-c r316/r317 + bm-b r505/r506)
produced 23 UU faces.

Classification (r296/r498/r505 canon):
  - same-day idempotent derive faces (REPORT/LIVE/dashboard/scorecard/status/
    token/audit): FULL-REWRITE faces -> take ORIGIN side (:2:) to let the
    newer on-origin derivation land (r296 face-3); r518's own S6 chain
    re-derives every one of them at round close anyway (zero-loss).
  - own-machine faces (state-bm-a / round_reports-bm-a / heartbeat bm-a.json
    / autofill_state.bm-a lane state): take OUR side (:3:) -- own-machine
    authorship law (fleet README: each machine writes only its own files;
    r297 claim-visibility = local truth for own lane).
  - staged D (fleet/inbox MSG deletions): r517 processed those MSGs
    (moved to inbox/processed/) -- keep the deletion, no UU to solve.

During `git pull --rebase`: :2: = ours = HEAD = origin/main side;
:3: = theirs = the replayed local commit side.
Idempotent, prints a per-file ledger; re-runs only touch still-unmerged paths.
"""
import subprocess
import sys

OWN = {
    "fleet/machines/bm-a.json",
    "round_reports-bm-a.md",
    "state-bm-a.json",
    "results/autofill_state.bm-a.json",
}
# everything else unmerged in this commit is a same-day idempotent derive face
DERIVE_TAKE_ORIGIN = [
    "docs/daily_report/REPORT-2026-10-01.json",
    "docs/daily_report/REPORT-2026-10-01.md",
    "docs/live_usage/LIVE-2026-10-01.json",
    "docs/live_usage/LIVE-2026-10-01.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]


def sh(*args):
    return subprocess.run(args, capture_output=True, text=True)


def unmerged():
    out = sh("git", "diff", "--name-only", "--diff-filter=U").stdout
    return [l.strip() for l in out.splitlines() if l.strip()]


def main():
    todo = unmerged()
    if not todo:
        print("resolver: no unmerged paths (already resolved?)")
        return 0
    ledger = []
    for path in todo:
        if path in OWN:
            sh("git", "checkout", "--theirs", path)
            sh("git", "add", path)
            ledger.append(("own-machine", path, ":3: ours"))
        elif path in DERIVE_TAKE_ORIGIN:
            sh("git", "checkout", "--ours", path)
            sh("git", "add", path)
            ledger.append(("derive-fullrewrite", path, ":2: origin"))
        else:
            print(f"resolver: UNCLASSIFIED path {path} -- manual review required")
            return 2
    for kind, path, side in ledger:
        print(f"  {kind:20s} {path:55s} -> {side}")
    print(f"resolver: {len(ledger)} faces resolved "
          f"({sum(1 for x in ledger if x[0]=='own-machine')} own / "
          f"{sum(1 for x in ledger if x[0]=='derive-fullrewrite')} derive-take-origin)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
