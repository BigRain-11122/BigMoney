import subprocess, hashlib, os, json

def run(cmd, cwd=None):
    r = subprocess.run(cmd, capture_output=True, shell=True, cwd=cwd)
    return r.returncode, r.stdout, r.stderr

k = 'K:/Fluxgroup/FluxGroup'
c = 'C:/Users/sjs20/Desktop/FluxGroup'
tree = None
for p in [k, c]:
    if os.path.exists(os.path.join(p, '.git')):
        tree = p
        break
print('group_tree:', tree)
if tree:
    run('git -C "%s" fetch origin' % tree)
    for f in ['docs/decisions.md', 'docs/orders.md']:
        rc, out, err = run('git -C "%s" show origin/main:%s' % (tree, f))
        if rc == 0:
            h = hashlib.sha256(out).hexdigest()
            print(f, 'sha256:', h)
        else:
            print(f, 'ERR', rc, err.decode('utf-8', 'replace')[:150])

base = 'C:/Users/sjs20/Desktop/FluxGroup/quant/bigmoney'
files = sorted(fn for fn in os.listdir(os.path.join(base, 'fleet', 'orders')) if fn.lower().endswith('.md'))
hb = json.load(open(os.path.join(base, 'fleet', 'machines', 'bm-a.json'), encoding='utf-8'))
acked = set(hb.get('orders_ack', []))
unacked = [f for f in files if f not in acked]
print('orders_total:', len(files), 'acked:', len(acked), 'unacked:', unacked)
