import io
import subprocess

FILES = ['docs/daily_report/REPORT-2026-10-18.md', 'docs/daily_report/REPORT-2026-10-18.json',
         'docs/live_usage/LIVE-2026-10-18.md', 'docs/live_usage/LIVE-2026-10-18.json',
         'docs/live_usage/LIVE-latest.md', 'docs/live_usage/LIVE-latest.json',
         'results/_attrition_guard_scan.json', 'results/compute_audit.json',
         'results/fundamental_b_layer_filter.json', 'results/regime_state.json',
         'results/update_status.json']

for p in FILES:
    b = subprocess.run(['git', 'show', 'd89b02dd4c:' + p], capture_output=True).stdout
    assert b, 'empty blob for ' + p
    with io.open(p, 'wb') as f:
        f.write(b)
    subprocess.run(['git', 'add', p], check=True)
print('resolved %d conflict faces (all MINE newer-wins per ts compare)' % len(FILES))
