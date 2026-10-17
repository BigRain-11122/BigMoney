# r1040 generic UU resolver: all unmerged runtime faces, ts-field newer-wins (r1028/r1032 recipes)
# rebase context: stage2=ours=HEAD(origin side), stage3=theirs=replayed local absorb side
import subprocess, re, io, json, sys

GIT = r"C:\Program Files\Git\cmd\git.exe"

def git_bytes(*args):
    return subprocess.run([GIT] + list(args), capture_output=True).stdout

unmerged = git_bytes('diff', '--name-only', '--diff-filter=U').decode('utf-8', 'utf-8').split()
unmerged = [u.strip() for u in unmerged if u.strip()]
print('unmerged_files', len(unmerged))
for u in unmerged:
    print(' -', u)

TS_KEYS = ['ts', 'generated', 'generated_at', 'updated', 'updated_at', 'asof', 'date', 'last_run']

def best_ts(text: str):
    found = []
    for k in TS_KEYS:
        for m in re.finditer(r'"%s"\s*:\s*"([^"]+)"' % k, text):
            found.append(m.group(1))
    return max(found) if found else ''

resolved_all = True
for p in unmerged:
    ours = git_bytes('show', ':%d:%s' % (2, p))
    theirs = git_bytes('show', ':%d:%s' % (3, p))
    to, tt = best_ts(ours.decode('utf-8', 'replace')), best_ts(theirs.decode('utf-8', 'replace'))
    if tt > to:
        win, side = theirs, 'theirs(local-replay)'
    elif to > tt:
        win, side = ours, 'ours(origin-HEAD)'
    else:
        win, side = theirs, 'tie/missing->theirs'
    # json validation for .json winners
    ok = True
    if p.endswith('.json'):
        try:
            json.loads(win.decode('utf-8', 'replace'))
        except Exception as e:
            ok = False
            print('  JSON_FAIL', p, repr(e)[:80])
            resolved_all = False
            continue
    io.open(p, 'wb').write(win)
    r = subprocess.run([GIT, 'add', '--', p], capture_output=True)
    print('RESOLVED', p, 'side=', side, 'ts_ours=', to, 'ts_theirs=', tt, 'add_rc=', r.returncode)
print('DONE resolved_all=', resolved_all)
sys.exit(0 if resolved_all else 1)
