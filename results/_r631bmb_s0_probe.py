import subprocess

incoming = subprocess.run(['git', 'diff', '--name-only', 'HEAD', 'origin/main'],
                          capture_output=True).stdout.decode('utf-8').split()
status = subprocess.run(['git', 'status', '--porcelain'], capture_output=True).stdout.decode('utf-8').splitlines()
mine = set()
for ln in status:
    p = ln[3:].strip().strip('"')
    if p:
        mine.add(p)
inter = sorted(mine & set(incoming))
print('incoming files:', len(incoming))
print('my dirty files:', len(mine))
print('INTERSECTION:')
for f in inter:
    print(' ', f)
