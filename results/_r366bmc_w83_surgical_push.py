import subprocess, os, sys

R = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'

def git(*args, **kw):
    return subprocess.run(['git', '-C', R] + list(args), capture_output=True, **kw)

def gb(*args):
    return subprocess.check_output(['git', '-C', R] + list(args))

head = gb('rev-parse', 'HEAD').decode().strip()
origin = gb('rev-parse', 'origin/main').decode().strip()
mb = gb('merge-base', origin, head).decode().strip()
print('HEAD', head[:9], 'ORIGIN', origin[:9], 'MB', mb[:9])

# payload from fork point (r568 law) -- my committed content only
files = gb('diff', '--name-only', mb, head).decode().splitlines()
print('PAYLOAD', len(files))
for f in files:
    print('  ', f)
dels = gb('diff', '--diff-filter=D', '--name-only', mb, head).decode().splitlines()
assert not dels, 'DELETION SET NON-EMPTY -- ABORT r530 law: %s' % dels

# temp index: read-tree origin/main, then overlay my committed blobs (r561: reset --soft trap avoided)
idx = os.path.join(R, '.codely-cli', 'scratch', '_r366_temp_index')
env = dict(os.environ, GIT_INDEX_FILE=idx)
subprocess.check_output(['git', '-C', R, 'read-tree', origin], env=env)
entries = []
for f in files:
    parts = gb('ls-tree', head, f).decode().split()
    mode, sha = parts[0], parts[2]
    entries.append(('%s %s\t%s' % (mode, sha, f)).encode())
subprocess.run(['git', '-C', R, 'update-index', '--index-info'],
               input=b'\n'.join(entries) + b'\n', env=env, capture_output=True, check=True)
tree = subprocess.check_output(['git', '-C', R, 'write-tree'], env=env).decode().strip()

# post-write ls-tree reconciliation (r331 law): new-tree vs origin diff == payload exactly
delta = subprocess.check_output(['git', '-C', R, 'diff', '--name-only', origin, tree]).decode().splitlines()
assert sorted(delta) == sorted(files), 'TREE DELTA != PAYLOAD: %s' % delta
dels2 = subprocess.check_output(['git', '-C', R, 'diff', '--diff-filter=D', '--name-only', origin, tree]).decode().splitlines()
assert not dels2, 'SILENT DELETION VS ORIGIN -- ABORT r519 law: %s' % dels2

msg = gb('log', '-1', '--format=%B', head).decode().strip()
newsha = subprocess.check_output(['git', '-C', R, 'commit-tree', tree, '-p', origin],
                                 input=msg.encode() + b'\n').decode().strip()
print('NEWSHA', newsha[:9])
r = git('push', 'origin', '%s:main' % newsha)
print('PUSH_RC', r.returncode)
if r.returncode != 0:
    print(r.stdout.decode(errors='replace'), r.stderr.decode(errors='replace'))
    sys.exit(2)
# re-anchor local (reset --mixed does not touch working tree)
git('reset', '--mixed', newsha)
print('DONE head now', gb('rev-parse', 'HEAD').decode().strip()[:9])
