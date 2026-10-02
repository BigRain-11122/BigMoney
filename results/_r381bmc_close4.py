import subprocess, os
os.chdir(r'K:\Fluxgroup\FluxGroup\quant\bigmoney')
G = r'C:\Program Files\Git\bin\git.exe'

def git(*a):
    r = subprocess.run([G] + list(a), capture_output=True, cwd=os.getcwd())
    return r.returncode, r.stdout.decode('utf-8', 'replace'), r.stderr.decode('utf-8', 'replace')

r = subprocess.run([G, 'status', '--porcelain'], capture_output=True, cwd=os.getcwd())
files = []
for line in r.stdout.decode('utf-8', 'replace').split('\n'):
    if not line.strip():
        continue
    files.append(line[3:].strip('"'))
rc, out, err = git('add', '-A', '--', *files)
print('add rc', rc, err[:150])
rc, out, err = git('commit', '-F', r'.codely-cli\scratch\commit_msg_r381_close4.txt')
print('commit rc', rc, out[:120], err[:150])
rc, out, err = git('push')
print('push rc', rc, err[:250])
if rc == 0:
    git('fetch', 'origin')
    rc2, out2, err2 = git('rev-list', '--count', 'HEAD..origin/main')
    rc3, out3, err3 = git('log', '-1', '--format=%H', 'origin/main')
    rc4, out4, err4 = git('log', '-1', '--format=%H', 'HEAD')
    print('behind', out2.strip(), '| origin_head', out3.strip()[:10], '| my_head', out4.strip()[:10])
else:
    git('fetch', 'origin')
    rc2, out2, err2 = git('rev-list', '--count', 'HEAD..origin/main')
    print('REJECTED behind', out2.strip())
