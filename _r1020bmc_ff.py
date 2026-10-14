import subprocess

def run(*args):
    return subprocess.run(list(args), capture_output=True).stdout.decode('utf-8', 'replace')

dirty_lines = [l for l in run('git', 'status', '--porcelain').splitlines() if l.strip()]
incoming = set(run('git', 'diff', '--name-only', 'HEAD', 'origin/main').splitlines())
dfiles = set()
for l in dirty_lines:
    p = l[3:].strip().strip('"')
    if p:
        dfiles.add(p)
overlap = dfiles & incoming
print('dirty:', sorted(dfiles))
print('incoming:', sorted(incoming))
print('OVERLAP:', sorted(overlap) if overlap else 'NONE -> ff-merge safe')
if overlap:
    raise SystemExit('OVERLAP FOUND, abort')
rc = subprocess.run(['git', 'merge', '--ff-only', 'origin/main'], capture_output=True, text=True, encoding='utf-8')
print('ff rc:', rc.returncode, (rc.stdout or '').strip()[:120], (rc.stderr or '').strip()[:120])
print('HEAD now:', run('git', 'rev-parse', 'HEAD').strip())
