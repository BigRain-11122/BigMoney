import subprocess, hashlib

def sha(b):
    return hashlib.sha256(b).hexdigest()[:16]

untracked = [
    'docs/daily_report/REPORT-2026-10-14.json',
    'docs/daily_report/REPORT-2026-10-14.md',
    'docs/live_usage/LIVE-2026-10-14.json',
    'docs/live_usage/LIVE-2026-10-14.md',
    'fleet/orders/O-20261013-0951-bm-b.md',
    'fleet/orders/O-20261014-0030-bm-b.md',
    'results/paper_export/export-2026-10-13.json',
]
for p in untracked:
    local = sha(open(p, 'rb').read())
    r = subprocess.run(['git', 'show', 'origin/main:' + p], capture_output=True)
    if r.returncode != 0:
        print('NOT-ON-ORIGIN', p, 'local=' + local)
    else:
        remote = sha(r.stdout)
        verdict = 'IDENTICAL' if local == remote else 'DIFFERS'
        print(verdict, p, 'local=' + local, 'origin=' + remote)
