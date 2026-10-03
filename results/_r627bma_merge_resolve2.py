import json, re, subprocess, sys

# --- 1. pit-git.md: union both tail appends (theirs: r624+r420, then mine: r627) ---
p = 'research/pit-git.md'
raw = open(p, 'rb').read()
text = raw.decode('utf-8')
lines = text.split('\n')
out, i = [], 0
ours, theirs = [], []
mode = None
for ln in lines:
    core = ln.rstrip('\r')
    if core.startswith('<<<<<<<'):
        mode = 'ours'; continue
    if core.startswith('======='):
        mode = 'theirs'; continue
    if core.startswith('>>>>>>>'):
        out.extend(theirs); out.extend(ours); mode = None; continue
    if mode == 'ours': ours.append(core)
    elif mode == 'theirs': theirs.append(core)
    else: out.append(core)
# drop a single trailing empty artifact from split
if out and out[-1] == '': out.pop()
payload = ('\r\n'.join(out) + '\r\n').encode('utf-8')
open(p, 'wb').write(payload)
chk = open(p, 'rb').read()
assert chk.count(b'\r\n') == chk.count(b'\n'), 'CRLF purity broken'
chk_lines = [l.rstrip('\r') for l in open(p, 'rb').read().decode('utf-8').split('\n')]
assert not any(l.startswith(('<<<<<<<', '=======', '>>>>>>>')) for l in chk_lines), \
    'line-start markers left (embedded content markers legal, r412 law)'
print('pit-git.md already clean')

# --- 2. _attrition_guard_scan.json: take-new by ts ---
def blob(n, path):
    r = subprocess.run(['git', 'show', f':{n}:{path}'], capture_output=True)
    if r.returncode != 0: sys.exit(f'no :{n}:{path}')
    return r.stdout
p = 'results/_attrition_guard_scan.json'
TS = re.compile(r'"(?:ts|scan_ts|updated|generated)"\s*:\s*"([^"]+)"')
b2, b3 = blob(2, p), blob(3, p)
t2 = TS.search(b2.decode('utf-8', 'replace')); t3 = TS.search(b3.decode('utf-8', 'replace'))
v2, v3 = (t2.group(1) if t2 else ''), (t3.group(1) if t3 else '')
winner = 2 if v2 >= v3 else 3
open(p, 'wb').write(b2 if winner == 2 else b3)
json.loads(open(p, 'rb').read().decode('utf-8'))
print(f'{p}: ours={v2} theirs={v3} -> take {"OURS" if winner == 2 else "THEIRS"}')

# --- 3. token_usage.json: canonical resolve (take-new generated) ---
p = 'results/token_usage.json'
s1, s2, s3 = p + '.s1.tmp', p + '.s2.tmp', p + '.s3.tmp'
open(s1, 'wb').write(blob(1, p))
open(s2, 'wb').write(blob(3, p))  # origin -> base_side
open(s3, 'wb').write(blob(2, p))  # local  -> replay_side
r = subprocess.run([sys.executable, 'scripts/merge_lane_views.py', 'resolve', p,
                    '--stage1', s1, '--stage2', s2, '--stage3', s3, '--out', p],
                   capture_output=True)
print((r.stdout + r.stderr).decode('utf-8', 'replace').strip())
if r.returncode != 0: sys.exit(f'resolve {p} rc={r.returncode}')
import os
for t in (s1, s2, s3): os.remove(t)
print('RESOLVER2 DONE')
