"""r1012 surgery v2: full-refname version (refname 'main' is AMBIGUOUS in this
repo -- a stale non-heads ref resolves 'main' to 466312108f; refs/heads/main is
correctly at d89b02dd4c). Tree surgery on the fully-resolved index, then quit
rebase, move refs/heads/main, reset, per r1032/r1008 family. Concurrent executor
(OS loop r1013, PID 9016) is live: finish fast, full ref names everywhere."""
import io
import os
import subprocess

ROOT = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
os.chdir(ROOT)


def g(*args, **kw):
    return subprocess.run(['git'] + list(args), capture_output=True, **kw)


heads_main = g('rev-parse', 'refs/heads/main').stdout.decode().strip()
assert heads_main == 'd89b02dd4c'[:len(heads_main)] or heads_main.startswith('d89b02dd4c'), \
    'refs/heads/main unexpectedly at ' + heads_main
origin_sha = g('rev-parse', 'refs/remotes/origin/main').stdout.decode().strip()
assert origin_sha == 'da13bcf13cf0d314bdd53d634cea789f5431bd2a', 'origin moved again: ' + origin_sha

msg_bytes = g('log', '-1', '--format=%B', 'd89b02dd4c').stdout
msg_path = os.path.join('results', '_r1012bmb_commit_msg.txt')
with io.open(msg_path, 'wb') as f:
    f.write(msg_bytes)

r = g('write-tree')
tree = r.stdout.decode().strip()
assert len(tree) == 40, 'write-tree bad: %r %r' % (r.stdout, r.stderr)
r = g('commit-tree', tree, '-p', origin_sha, '-F', msg_path)
newc = r.stdout.decode().strip()
assert len(newc) == 40, 'commit-tree bad: %r %r' % (r.stdout, r.stderr)
g('rebase', '--quit')
r = g('update-ref', 'refs/heads/main', newc)
assert r.returncode == 0, 'update-ref failed: %r' % r.stderr
g('reset', '--mixed')
log = g('log', '--oneline', '-3').stdout.decode('utf-8', 'replace')
print('NEW_COMMIT=' + newc)
print(log)
