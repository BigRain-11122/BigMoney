"""r1012 rebase-continue ghost-refusal bypass (r1032/r1008 family law):
tree surgery straight-through on the fully-resolved index."""
import io
import os
import subprocess

ROOT = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
os.chdir(ROOT)


def g(*args, **kw):
    return subprocess.run(['git'] + list(args), capture_output=True, **kw)


# reflog guard: local main must equal origin tip (zero foreign commits to orphan)
r = g('rev-parse', 'main')
main_sha = r.stdout.decode().strip()
r = g('rev-parse', 'origin/main')
origin_sha = r.stdout.decode().strip()
assert main_sha == origin_sha, 'main != origin/main, abort surgery: %s vs %s' % (main_sha, origin_sha)

# msg from original commit (bytes-faithful)
msg_bytes = g('log', '-1', '--format=%B', 'd89b02dd4c').stdout
msg_path = os.path.join('results', '_r1012bmb_commit_msg.txt')
with io.open(msg_path, 'wb') as f:
    f.write(msg_bytes)

r = g('write-tree')
tree = r.stdout.decode().strip()
assert len(tree) == 40 and all(c in '0123456789abcdef' for c in tree), 'write-tree bad: %r' % r.stdout + r.stderr
r = g('commit-tree', tree, '-p', origin_sha, '-F', msg_path)
newc = r.stdout.decode().strip()
assert len(newc) == 40 and all(c in '0123456789abcdef' for c in newc), 'commit-tree bad: %r' % r.stdout + r.stderr
g('rebase', '--quit')
r = g('update-ref', 'refs/heads/main', newc)
assert r.returncode == 0, 'update-ref failed: %r' % r.stderr
g('reset', '--mixed')
log = g('log', '--oneline', '-3').stdout.decode('utf-8', 'replace')
print('NEW_COMMIT=' + newc)
print(log)
