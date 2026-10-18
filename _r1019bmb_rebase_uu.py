# r1019 rebase UU resolver: 7 shared regen faces, ts newer-wins (r1015/r1017 law).
# Rebase conflict stages: :2 = ours (origin new base), :3 = theirs (my replayed commit).
# ASCII only.
import subprocess, json, re

FILES = ['docs/daily_report/REPORT-2026-10-19.json',
         'docs/daily_report/REPORT-2026-10-19.md',
         'results/_attrition_guard_scan.json',
         'results/compute_audit.json',
         'results/fundamental_b_layer_filter.json',
         'results/regime_state.json',
         'results/update_status.json']

def blob(stage, path):
    r = subprocess.run(['git', 'show', ':%s:%s' % (stage, path)], capture_output=True)
    return r.stdout

def ts_of(raw):
    txt = raw.decode('utf-8', errors='replace')
    for key in ('"ts"', '"generated"', '"updated"', '"asof"'):
        m = re.search(re.escape(key) + r'\s*[:=]\s*"?([^"\n,}]+)', txt)
        if m:
            return m.group(1).strip()
    return 'NO-TS'

for p in FILES:
    o, t = blob(2, p), blob(3, p)
    ov, tv = ts_of(o), ts_of(t)
    win, side = (t, 'MINE(theirs)') if tv > ov else (o, 'ORIGIN(ours)')
    with open(p, 'wb') as f:
        f.write(win)
    subprocess.run(['git', 'add', '--', p], capture_output=True)
    print('%s: origin[%s] mine[%s] -> %s' % (p, ov, tv, side))

r = subprocess.run(['git', 'ls-files', '--unmerged'], capture_output=True)
n = len(r.stdout.decode().strip().splitlines())
print('unmerged-left:', n)
assert n == 0, 'UU not cleared'
