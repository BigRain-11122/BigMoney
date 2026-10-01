# -*- coding: utf-8 -*-
# r336 bm-c: post-push integration -- reset --mixed re-anchor + selective checkout
# alignment (r524 law: after surgical push, checkout origin-owned faces before
# dependency checks; r505: same-day idempotent regen faces -> origin side for now,
# S6 chain re-derives fresh on the NEW base = no stale-base derive hazard r512).
import io, sys, os, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

R = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
# full-rewrite shared derive faces / host=bm-a faces / truncation-victim jsonl:
# restore to origin (S6 re-derives the ones bm-c owns a write path to)
RESTORE = [
    'docs/daily_report/REPORT-2026-10-01.json',
    'docs/daily_report/REPORT-2026-10-01.md',
    'docs/live_usage/LIVE-2026-10-01.json',
    'docs/live_usage/LIVE-2026-10-01.md',
    'docs/live_usage/LIVE-latest.json',
    'docs/live_usage/LIVE-latest.md',
    'results/_attrition_guard_scan.json',
    'results/compute_audit.json',
    'results/daily_scorecard.html',
    'results/daily_scorecard.json',
    'results/dashboard_status.js',
    'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/lhb_update_status.json',
    'results/paper_export/export-2026-09-30.json',
    'results/paper_export/latest.json',
    'results/pool_core_samples.jsonl',
    'results/regime_state.json',
    'results/strategy_scorecard.json',
    'results/scorecard_v1.json',
    'results/token_usage.json',
    'results/update_status.json',
]

def git(*a, check=True):
    r = subprocess.run(['git', '-C', R] + list(a), capture_output=True)
    if check and r.returncode != 0:
        print('GIT FAIL', a, r.returncode, r.stderr.decode('utf-8', 'replace')[:300])
        sys.exit(1)
    return r

git('fetch', 'origin')
before = git('rev-parse', 'origin/main').stdout.decode().strip()
git('reset', '--mixed', 'origin/main')
after = git('rev-parse', 'HEAD').stdout.decode().strip()
print('RE-ANCHOR before=%s after=%s' % (before[:12], after[:12]))
behind = git('rev-list', '--count', 'HEAD..origin/main').stdout.decode().strip()
ahead = git('rev-list', '--count', 'origin/main..HEAD').stdout.decode().strip()
print('behind=%s ahead=%s' % (behind, ahead))

# checkout alignment for restore-set (paths valid in new HEAD -> index -> worktree)
bad = []
for f in RESTORE:
    rc = subprocess.run(['git', '-C', R, 'cat-file', '-e', 'HEAD:' + f], capture_output=True).returncode
    if rc == 0:
        git('checkout', '--', f)
    else:
        bad.append(f)
if bad:
    print('NOT-IN-HEAD (left dirty):', bad)
st = git('status', '--porcelain').stdout.decode().strip().splitlines()
print('REMAINING_DIRTY count=%d' % len(st))
for ln in st:
    print('  D|', ln)
