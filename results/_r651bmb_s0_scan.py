# -*- coding: ascii -*-
# r651 bm-b: same-scope orders set diff (ls-tree O-*.md vs heartbeat ack) + D-19 decisions hash via sparse clone origin blob
import json, subprocess, sys, hashlib, os, tempfile

def git(args, cwd=None):
    r = subprocess.run(['git'] + args, capture_output=True, cwd=cwd)
    return r.stdout.decode('utf-8', 'replace')

# 1) same-scope orders diff (basename compare: ack stores bare filenames)
ls = git(['ls-tree', 'origin/main', '--name-only', 'fleet/orders/'])
orders = sorted([os.path.basename(l) for l in ls.splitlines() if l.strip().endswith('.md') and '/O-' in l])
ack = set(json.load(open('fleet/machines/bm-b.json')).get('orders_ack') or [])
missing = [o for o in orders if o not in ack]
print('ORDERS_TOTAL', len(orders), 'ACK', len(ack), 'MISSING', len(missing))
for m in missing:
    print('MISSING_ORDER', m)

# 2) D-19 decisions via sparse clone (K: and C: real path both lack .git)
tmp = os.path.join(tempfile.gettempdir(), 'fg-d19-r651-bmb')
dec_hash = None
try:
    if not os.path.exists(tmp):
        r = subprocess.run(['git', 'clone', '--depth', '1', '--filter=blob:none', '--sparse',
                            'https://github.com/BigRain-11122/FluxGroup.git', tmp],
                           capture_output=True)
        if r.returncode != 0:
            print('CLONE_FAIL', r.stderr.decode('utf-8', 'replace')[:300]); sys.exit(0)
    r = subprocess.run(['git', '-C', tmp, 'sparse-checkout', 'set', '--skip-checks', 'docs/decisions.md'],
                       capture_output=True)
    r = subprocess.run(['git', '-C', tmp, 'fetch', 'origin', 'main'], capture_output=True)
    blob = subprocess.run(['git', '-C', tmp, 'show', 'origin/main:docs/decisions.md'], capture_output=True)
    if blob.returncode == 0:
        dec_hash = hashlib.sha256(blob.stdout).hexdigest()
        print('DECISIONS_SHA256', dec_hash)
        # last 30 lines for eyeball
        tail = blob.stdout.decode('utf-8', 'replace').splitlines()[-14:]
        for l in tail:
            print('DEC_TAIL|', l[:150])
    else:
        print('DEC_SHOW_FAIL', blob.stderr.decode('utf-8', 'replace')[:200])
except Exception as e:
    print('D19_EXCEPTION', repr(e)[:200])
finally:
    pass  # keep tmp for reuse this round

# 3) orders.md CEO pending physical-item zone (same tree)
try:
    ob = subprocess.run(['git', '-C', tmp, 'show', 'origin/main:docs/orders.md'], capture_output=True)
    if ob.returncode == 0:
        print('GROUP_ORDERS_SHA256', hashlib.sha256(ob.stdout).hexdigest())
        for l in ob.stdout.decode('utf-8', 'replace').splitlines():
            if 'bm-b' in l.lower() or 'BigMoney' in l or 'quant' in l.lower():
                print('GRP_ORD_LINE|', l[:160])
    else:
        print('GROUP_ORDERS_SHOW_FAIL')
except Exception as e:
    print('GRP_ORD_EXCEPTION', repr(e)[:150])

# 4) state watermark key compare (utf-8 tolerant read per pit-encoding)
raw = open('state.json', 'rb').read().decode('utf-8', 'replace')
st = json.loads(raw)
print('STATE_D19_KEY', st.get('last_decisions_sha'), 'round_no', st.get('round_no'))
