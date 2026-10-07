# r801 bm-b: r808 three-step rebase cure (commit -F message with author env, then continue)
import subprocess, shlex, os, sys

def run(cmd, env=None, capture=True):
    r = subprocess.run(cmd, capture_output=capture, env=env)
    out = (r.stdout or b'') + (r.stderr or b'')
    print('rc=%d :: %s' % (r.returncode, ' '.join(cmd[:6])))
    if out:
        print(out.decode('utf-8', 'replace')[:800])
    return r

env = dict(os.environ)
for line in open('.git/rebase-merge/author-script', encoding='utf-8').read().splitlines():
    line = line.strip()
    if '=' in line and line.startswith('GIT_AUTHOR'):
        token = shlex.split(line, posix=True)
        if token and '=' in token[0]:
            k, v = token[0].split('=', 1)
            env[k] = v
            print('env %s=%s' % (k, v))

r = run(['git', 'commit', '-F', '.git/rebase-merge/message'], env=env)
if r.returncode != 0:
    print('MANUAL COMMIT FAILED - see claw/error above')
    sys.exit(1)
r2 = run(['git', '-c', 'core.editor=true', 'rebase', '--continue'])
print('continue rc=%d' % r2.returncode)
run(['git', 'branch', '--show-current'])
run(['git', 'log', '--oneline', '-5'])
