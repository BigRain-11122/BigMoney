# r684 bm-b: S0.5 orders ack diff probe (r477 same-form both sides: full O-*.md filenames)
import json, subprocess, sys

def git(*a):
    r = subprocess.run(['git', *a], capture_output=True)
    if r.returncode != 0:
        print('GIT_FAIL', a, r.stderr.decode('utf-8', 'replace'))
        sys.exit(2)
    return r.stdout.decode('utf-8', 'replace')

# origin-side: full filenames, filter O-*.md only (r646 same-caliber both sides)
out = git('ls-tree', 'origin/main', '--name-only', 'fleet/orders/')
orders = sorted(l.strip() for l in out.splitlines() if l.strip().startswith('fleet/orders/O-') and l.strip().endswith('.md'))
order_names = set(p.split('/')[-1] for p in orders)

hb = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
ack = set(hb.get('orders_ack', []))
# ack entries are full filenames w/ .md (r477)
unacked = sorted(order_names - ack)
extra = sorted(ack - order_names - {'README.md'})
print('orders_total', len(order_names))
print('ack_total', len(ack))
print('unacked', json.dumps(unacked))
print('ack_extra_n', len(extra))
