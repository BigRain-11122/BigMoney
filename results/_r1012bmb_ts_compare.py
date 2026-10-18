import subprocess
import re

FILES = ['docs/daily_report/REPORT-2026-10-18.md', 'docs/daily_report/REPORT-2026-10-18.json',
         'docs/live_usage/LIVE-2026-10-18.md', 'docs/live_usage/LIVE-2026-10-18.json',
         'docs/live_usage/LIVE-latest.md', 'docs/live_usage/LIVE-latest.json',
         'results/_attrition_guard_scan.json', 'results/compute_audit.json',
         'results/fundamental_b_layer_filter.json', 'results/regime_state.json',
         'results/update_status.json']


def blob(rev, p):
    return subprocess.run(['git', 'show', rev + ':' + p], capture_output=True).stdout.decode('utf-8', 'replace')


def ts_of(text):
    m = re.search(r'"ts"\s*:\s*"([^"]+)"', text)
    if m:
        return m.group(1)
    m = re.search(r'2026-10-18[ T]\d{2}:\d{2}:\d{2}', text)
    return m.group(0) if m else '?'


for p in FILES:
    o = ts_of(blob('origin/main', p))
    m = ts_of(blob('HEAD', p))
    win = 'MINE' if m > o else 'ORIGIN'
    print('%-52s origin=%s mine=%s -> %s' % (p, o, m, win))
