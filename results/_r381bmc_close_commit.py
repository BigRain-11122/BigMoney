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
    path = line[3:].strip('"')
    files.append(path)
print('stage_count', len(files))
rc, out, err = git('add', '-A', '--', *files)
print('add rc', rc, err[:200])
rc, out, err = git('diff', '--cached', '--stat')
print(out.strip().split('\n')[-1] if out.strip() else 'no staged diff')
rc, out, err = git('commit', '-F', r'.codely-cli\scratch\commit_msg_r381_close.txt')
print('commit rc', rc, out[:150], err[:200])
