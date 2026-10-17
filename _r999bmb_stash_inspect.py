import subprocess, os, sys

REPO = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
os.chdir(REPO)

def git(*args, inp=None):
    r = subprocess.run(['git'] + list(args), capture_output=True, input=inp)
    return r.returncode, r.stdout.decode('utf-8', 'replace'), r.stderr.decode('utf-8', 'replace')

# inspect all three stashes
for ref in ('stash@{0}', 'stash@{1}', 'stash@{2}'):
    rc, out, err = git('stash', 'show', '--stat', ref)
    print('==', ref, 'rc', rc)
    print(out.strip()[-900:])

# extract stash@{1} diffs for human-content files
for path in ('CODELY.md', 'fleet/orders/O-20261018-0137-bm-a.md'):
    rc, out, err = git('diff', 'stash@{1}^', 'stash@{1}', '--', path)
    print('== PATCH', path, 'rc', rc, 'len', len(out))
    print(out.strip()[:1500])
