import subprocess

def sh(args):
    r = subprocess.run(args, capture_output=True)
    return r.returncode, (r.stdout + r.stderr).decode('utf-8', errors='replace').strip()

# full intersection of dirty-vs-origin-delta (tracked faces)
rc, dirt = sh(['git', 'status', '--porcelain=v1', '-uno'])
rc, delta = sh(['git', 'diff', '--name-only', 'HEAD', 'origin/main'])
dirty = set(l[3:].strip().strip('"') for l in dirt.splitlines() if l.strip())
origin = set(l.strip() for l in delta.splitlines() if l.strip())
inter = sorted(dirty & origin)
print('INTERSECTION (checkout origin blob):')
for f in inter:
    print('  ', f)
if inter:
    rc, out = sh(['git', 'checkout', 'origin/main', '--'] + inter)
    print('checkout rc=', rc, out[:200])
