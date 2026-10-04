import json, subprocess, hashlib, sys, tempfile, shutil, os

REPO_SSH = 'git@github.com:BigRain-11122/FluxGroup.git'
REPO_HTTPS = 'https://github.com/BigRain-11122/FluxGroup.git'

def run(cmd, cwd=None, timeout=300):
    r = subprocess.run(cmd, capture_output=True, cwd=cwd, timeout=timeout)
    return r.returncode, r.stdout, r.stderr

tmp = tempfile.mkdtemp(prefix='fluxgroup_d19_r702_')
ok = False
for url in (REPO_SSH, REPO_HTTPS):
    rc, so, se = run(['git', 'clone', '--depth', '1', '--filter=blob:none', '--sparse', url, tmp])
    if rc == 0:
        ok = True
        break
    sys.stderr.write('clone fail %s: %s\n' % (url.split('@')[-1].split('/')[-1], se.decode('utf-8', 'replace')[:300]))
if not ok:
    sys.stderr.write('ALL CLONE URLS FAILED\n')
    sys.exit(2)

rc, so, se = run(['git', 'sparse-checkout', 'set', '--skip-checks', 'docs/decisions.md', 'docs/orders.md'], cwd=tmp)
if rc != 0:
    sys.stderr.write(se.decode('utf-8', 'replace')[:300]); sys.exit(2)

def git_bytes(path):
    rc, so, se = run(['git', '-C', tmp, 'show', 'origin/main:%s' % path])
    if rc != 0:
        sys.stderr.write('show fail %s: %s' % (path, se.decode('utf-8', 'replace')[:300])); sys.exit(2)
    return so

state = json.load(open('state-bm-a.json', encoding='utf-8'))
hb = json.load(open('fleet/machines/bm-a.json', encoding='utf-8'))
out = {'tmp': tmp}

dec = git_bytes('docs/decisions.md')
out['decisions_sha256'] = hashlib.sha256(dec).hexdigest()
out['decisions_state_key'] = state.get('last_decisions_sha')
out['decisions_changed'] = out['decisions_sha256'] != state.get('last_decisions_sha')

orders = git_bytes('docs/orders.md')
out['orders_sha1'] = hashlib.sha1(orders).hexdigest()
out['orders_state_key'] = state.get('last_orders_sha')
out['orders_changed'] = out['orders_sha1'] != state.get('last_orders_sha')

txt = dec.decode('utf-8', 'replace')
idx = txt.find('派工通告板')
out['board'] = txt[idx:idx + 4000] if idx >= 0 else '(board marker not found) tail:\n' + txt[-4000:]
ord_txt = orders.decode('utf-8', 'replace')
out['orders_tail'] = ord_txt[-4000:]

shutil.rmtree(tmp, ignore_errors=True)
json.dump(out, open('results/_r702bma_d19_check.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in out.items() if k not in ('board', 'orders_tail')}, ensure_ascii=False, indent=1))
