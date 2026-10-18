"""r1015 push-race conflict resolution: 7 shared regen faces, newer-wins by
embedded ts (r1008/r1014 precedent). Rebase stages: 2=ours(origin/bm-c),
3=theirs(mine/bm-b replayed)."""
import io
import json
import os
import re
import subprocess

os.chdir(r'C:\Fluxgroup\FluxGroup\quant\bigmoney')
UU = ['docs/daily_report/REPORT-2026-10-19.json', 'docs/daily_report/REPORT-2026-10-19.md',
      'results/_attrition_guard_scan.json', 'results/compute_audit.json',
      'results/fundamental_b_layer_filter.json', 'results/regime_state.json',
      'results/update_status.json']


def blob(stage, path):
    r = subprocess.run(['git', 'show', ':%d:%s' % (stage, path)], capture_output=True)
    return r.stdout.decode('utf-8', 'replace')


def ts_of(text):
    m = re.search(r'"(?:ts|generated_at|generated|updated_at|scan_ts|asof)"\s*:\s*"([^"]+)"', text)
    if m:
        return m.group(1)
    m = re.search(r'(2026-10-19[T ][0-9:+\-]+)', text)
    return m.group(1) if m else 'NONE'


report = []
for p in UU:
    o = blob(2, p)
    t = blob(3, p)
    to, tt = ts_of(o), ts_of(t)
    keep = 'theirs' if tt >= to else 'ours'
    report.append('%s origin=%s mine=%s -> keep=%s' % (p, to, tt, keep))
    body = t if keep == 'theirs' else o
    with io.open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(body)
    r = subprocess.run(['git', 'add', '--', p], capture_output=True)
    if r.returncode:
        report.append('  ADD FAIL ' + r.stderr.decode('utf-8', 'replace')[:100])
io.open('results/_r1015bmb_uu_pick.py', 'a', encoding='utf-8').write('\n'.join(report) + '\n')
print('\n'.join(report))
