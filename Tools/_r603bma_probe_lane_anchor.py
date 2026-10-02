import subprocess

r = subprocess.run(['git', 'show',
                    'origin/main:results/runnable_pool.bm-b.json'],
                   capture_output=True)
txt = r.stdout.decode('utf-8')
for val in ['02:06:04', '02:07:12', '02:08:04', '02:09:11']:
    i = txt.find(f'"owner_since": "2026-10-03 {val}"')
    assert i > 0, val
    print(f'--- {val} ---')
    print(repr(txt[max(0, i - 120):i + 60]))
