import subprocess, re

r = subprocess.run(['git', 'show', 'origin/main:results/runnable_pool.json'],
                   capture_output=True)
txt = r.stdout.decode('utf-8')
for val in ['02:06:04', '02:07:12', '02:08:04', '02:09:11']:
    i = txt.find(f'"owner_since": "2026-10-03 {val}"')
    assert i > 0, val
    s = txt.rfind('\n', 0, i - 200)
    seg = txt[max(0, i - 260):i + 120]
    print(f'--- {val} ---')
    print(repr(seg))
# count owner bm-c lines total
print('total "owner": "bm-c" lines:',
      len(re.findall(r'"owner": "bm-c"', txt)))
print('total "owner_since": "2026-10-03 02:0 lines:',
      len(re.findall(r'"owner_since": "2026-10-03 02:0[6-9]', txt)))
