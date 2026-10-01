import subprocess, re, sys
for f in ('docs/daily_report/REPORT-2026-10-01.json',
          'results/compute_audit.json',
          'results/fundamental_b_layer_filter.json'):
    for side, stage in (('origin:2', ':2:'), ('mine:3', ':3:')):
        p = subprocess.run(['git', 'show', stage + f], capture_output=True)
        t = p.stdout.decode('utf-8', 'replace')
        m = re.search(r'"(generated_at|ts|generated)"\s*:\s*"([^"]+)"', t)
        print(side, f.split('/')[-1], '->',
              m.group(2) if m else 'no-ts', '| bytes', len(p.stdout))
