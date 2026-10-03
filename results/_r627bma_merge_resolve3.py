import json, re, subprocess, sys, os

def show(ref, path):
    r = subprocess.run(['git', 'show', f'{ref}:{path}'], capture_output=True)
    if r.returncode:
        sys.exit(f'no {ref}:{path}')
    return r.stdout

# --- attrition scan: take-new by ts (mine=78f30b234, origin-side=d7ba26867) ---
p = 'results/_attrition_guard_scan.json'
TS = re.compile(r'"(?:ts|scan_ts|updated|generated)"\s*:\s*"([^"]+)"')
b2, b3 = show('78f30b234', p), show('d7ba26867', p)
t2 = TS.search(b2.decode('utf-8', 'replace'))
t3 = TS.search(b3.decode('utf-8', 'replace'))
v2, v3 = (t2.group(1) if t2 else ''), (t3.group(1) if t3 else '')
w = 2 if v2 >= v3 else 3
open(p, 'wb').write(b2 if w == 2 else b3)
json.loads(open(p, 'rb').read().decode('utf-8'))
print(f'attrition: ours={v2} theirs={v3} -> take {"OURS" if w == 2 else "THEIRS"}')

# --- token_usage: canonical resolve from explicit blobs ---
p = 'results/token_usage.json'
s1, s2, s3 = p + '.s1.tmp', p + '.s2.tmp', p + '.s3.tmp'
open(s1, 'wb').write(show('554abaa6f', p))
open(s2, 'wb').write(show('d7ba26867', p))
open(s3, 'wb').write(show('78f30b234', p))
r = subprocess.run([sys.executable, 'scripts/merge_lane_views.py', 'resolve', p,
                    '--stage1', s1, '--stage2', s2, '--stage3', s3, '--out', p],
                   capture_output=True)
print((r.stdout + r.stderr).decode('utf-8', 'replace').strip()[-300:])
if r.returncode:
    sys.exit(f'resolve rc={r.returncode}')
for t in (s1, s2, s3):
    os.remove(t)

# --- verify all three clean at line-start (r412 law) ---
for p in ('research/pit-git.md', 'results/_attrition_guard_scan.json',
          'results/token_usage.json'):
    lines = open(p, 'rb').read().decode('utf-8').split('\n')
    bad = [l[:40] for l in lines
           if l.rstrip('\r').startswith(('<<<<<<<', '=======', '>>>>>>>'))]
    print(p, 'line-start markers:', bad if bad else 'NONE')
print('REBUILD DONE')
