# r627 bm-a: D-19 decisions/orders watermark check (temp partial clone recipe r481 bm-b law, K: absent on bm-a)
import subprocess, hashlib, json, os, sys

CLONE = os.path.join(os.environ.get('TEMP', '.'), 'fg-dec-bma')
REMOTE = 'git@github.com:BigRain-11122/FluxGroup.git'

def sh(args, cwd=None):
    r = subprocess.run(args, cwd=cwd, capture_output=True)
    return r.returncode, r.stdout, r.stderr

# clone if absent, else fetch
if not os.path.isdir(os.path.join(CLONE, '.git')):
    rc, out, err = sh(['git', 'clone', '--depth', '1', '--filter=blob:none', '--no-checkout', REMOTE, CLONE])
    if rc != 0:
        print('CLONE FAIL', err.decode('utf-8', 'replace')[:300]); sys.exit(1)
else:
    rc, out, err = sh(['git', '-C', CLONE, 'fetch', 'origin'])
    if rc != 0:
        print('FETCH FAIL', err.decode('utf-8', 'replace')[:300]); sys.exit(1)

hb = json.load(open(r'fleet\machines\bm-a.json', encoding='utf-8'))
res = {}
for name in ('docs/decisions.md', 'docs/orders.md'):
    rc, out, err = sh(['git', '-C', CLONE, 'show', 'origin/main:' + name])
    if rc != 0:
        print('SHOW FAIL', name, err.decode('utf-8', 'replace')[:200]); sys.exit(1)
    res[name] = hashlib.sha256(out).hexdigest().upper()

stored = (hb.get('last_decisions_sha') or '').upper()
print('decisions sha:', res['docs/decisions.md'][:16], '| stored:', stored[:16],
      '| MATCH' if res['docs/decisions.md'] == stored else '| CHANGED')
print('orders sha:', res['docs/orders.md'][:16])
json.dump(res, open('results/_r627bma_d19.json', 'w'), indent=1)
