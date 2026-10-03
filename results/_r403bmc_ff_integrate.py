# -*- coding: utf-8 -*-
"""r403 bm-c pre-commit FF integration (r585 pure-FF + r400 shared-face yield).

Steps (single process, minimal race window):
  1. restore-to-HEAD the 19 overlap faces (17 shared daily-regen derive faces
     origin-side yield per r400 law + METHODOLOGY_ASSETS.md whose local edit
     is re-landed as E17 union after FF -- bm-a r612 took the E16 number);
  2. execution-time rev-parse origin/main (r593 fresh-value law) + ff-only;
  3. post-verify: HEAD == origin/main, zero D-faces (E08 law), E16-in-origin.
"""
import subprocess
import sys

REPO = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
CNW = 0x08000000

RESTORE = [
    'docs/daily_report/REPORT-2026-10-03.json',
    'docs/daily_report/REPORT-2026-10-03.md',
    'docs/live_usage/LIVE-2026-10-03.json',
    'docs/live_usage/LIVE-2026-10-03.md',
    'docs/live_usage/LIVE-latest.json',
    'docs/live_usage/LIVE-latest.md',
    'knowledge/METHODOLOGY_ASSETS.md',
    'results/_attrition_guard_scan.json',
    'results/compute_audit.json',
    'results/dashboard_status.js',
    'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/lhb_update_status.json',
    'results/regime_state.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
    'results/token_usage.json',
    'results/update_status.json',
]


def g(args, check=True):
    r = subprocess.run(['git'] + args, capture_output=True, cwd=REPO,
                       text=True, encoding='utf-8', errors='replace',
                       creationflags=CNW)
    if check and r.returncode != 0:
        sys.exit('GIT FAIL %s -> %s' % (args[:3],
                  (r.stderr or r.stdout)[:400]))
    return r.returncode, r.stdout


rc, out = g(['status', '--porcelain'], check=False)
# r380: no whole-output strip; per-line lstrip only for emptiness test
dirty = [l for l in out.splitlines() if l.strip()]
for f in RESTORE:
    if any(l[3:].strip().strip('"') == f for l in dirty):
        g(['checkout', '--', f])
        print('restored', f)
    else:
        print('clean-skip', f)

rc, tip = g(['rev-parse', 'origin/main'])
tip = tip.strip()
print('origin tip (execution-time):', tip)
rc, out = g(['merge', '--ff-only', tip], check=False)
print('ff rc=%d out=%s' % (rc, out.strip()[:200]))
if rc != 0:
    sys.exit('FF REFUSED -- abort, no reset, inspect manually')

rc, head = g(['rev-parse', 'HEAD'])
rc, behind = g(['rev-list', '--count', 'HEAD..origin/main'])
rc, ahead = g(['rev-list', '--count', 'origin/main..HEAD'])
print('HEAD=%s behind=%s ahead=%s' % (head.strip()[:9], behind.strip(),
                                      ahead.strip()))
rc, out = g(['status', '--porcelain'], check=False)
d_faces = [l for l in out.splitlines()
           if l.strip() and l[0] == 'D' and l[1] == ' ']
print('D-faces: %d (must be 0)' % len(d_faces))
for l in d_faces[:5]:
    print('D!', l)
rc, out = g(['show', tip + ':knowledge/METHODOLOGY_ASSETS.md'], check=False)
print('E16-in-origin:', 'E16 reland' in out)
print('FF-OK' if (behind.strip() == '0' and not d_faces) else 'CHECK-NEEDED')
