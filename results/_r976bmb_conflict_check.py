import subprocess

# find O-1200 filename on origin
c = subprocess.run(['git', 'ls-tree', 'origin/main', 'fleet/orders/'], capture_output=True).stdout.decode()
for l in c.splitlines():
    if '1200' in l:
        print('O1200FILE:', l.split()[-1])

# incoming changed files
inc = subprocess.run(['git', 'diff', '--name-only', 'HEAD', 'origin/main'],
                     capture_output=True).stdout.decode().split()
open('results/_r976bmb_incoming.txt', 'w').write('\n'.join(inc))
print('incoming changed files:', len(inc))

# my dirty faces
myfiles = set()
for l in subprocess.run(['git', 'status', '--porcelain'], capture_output=True).stdout.decode().splitlines():
    p = l[3:].strip().strip('"') if len(l) > 3 else ''
    if p:
        myfiles.add(p)
untr = set(subprocess.run(['git', 'ls-files', '--others', '--exclude-standard'],
                          capture_output=True).stdout.decode().split())
myfiles |= untr
inter = sorted(myfiles & set(inc))
open('results/_r976bmb_conflict_cands.txt', 'w').write('\n'.join(inter))
print('my dirty+untracked files:', len(myfiles))
print('INTERSECTION (conflict candidates):', len(inter))
for f in inter[:20]:
    print(' X', f)
