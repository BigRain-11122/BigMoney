import subprocess, re

def ts_of(t):
    for pat in [r'"ts":\s*"([^"]+)"', r'"generated":\s*"([^"]+)"', r'"generated_at":\s*"([^"]+)"', r'"finalized_at":\s*"([^"]+)"']:
        m = re.search(pat, t)
        if m:
            return m.group(1)
    return '?'

files = ['results/compute_audit.json', 'docs/daily_report/REPORT-2026-10-01.json',
         'results/strategy_scorecard.json', 'results/regime_state.json',
         'docs/live_usage/LIVE-2026-10-01.md', 'results/token_usage.json']
for f in files:
    try:
        ours = subprocess.check_output(['git', 'show', ':2:' + f]).decode('utf-8', 'replace')
    except Exception:
        print(f, '| ours: MISSING')
        continue
    theirs = subprocess.check_output(['git', 'show', ':3:' + f]).decode('utf-8', 'replace')
    o, t = ts_of(ours), ts_of(theirs)
    newer = 'OURS(origin)' if o > t else 'THEIRS(mine)'
    print(f"{f.split('/')[-1]:40s} | ours={o[:19]} | theirs={t[:19]} | newer={newer}")
