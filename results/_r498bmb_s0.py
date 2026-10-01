# -*- coding: utf-8 -*-
"""r498 bm-b S0.5 orders diff + D-19 decisions fresh-read (raw-bytes hash, case-normalized per r503)."""
import subprocess, json, os, hashlib, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORD = os.path.join(REPO, 'fleet', 'orders')

def out(*args, cwd=None):
    r = subprocess.run(list(args), capture_output=True, cwd=cwd)
    return r.returncode, r.stdout, r.stderr

# --- S0.5 orders diff ---
files = sorted(f for f in os.listdir(ORD) if f.startswith('O-') and f.endswith('.md'))
hb = json.load(open(os.path.join(REPO, 'fleet', 'machines', 'bm-b.json'), encoding='utf-8'))
ack = set(hb.get('orders_ack', []))
unacked = [f for f in files if f not in ack]
ghost_acks = sorted(ack - set(files))

# --- D-19 fresh read via temp partial clone (bm-b no group-tree canon, r481) ---
tmp = os.path.join(os.environ.get('TEMP', ''), 'fg-dec-bmb')
sha = None
d_err = None
try:
    if not os.path.isdir(os.path.join(tmp, '.git')):
        rc, so, se = out('git', 'clone', '--depth', '1', '--filter=blob:none', '--no-checkout',
                         'git@github.com:BigRain-11122/FluxGroup.git', tmp)
        if rc != 0:
            d_err = 'clone rc=%s %s' % (rc, se[:200])
    if os.path.isdir(os.path.join(tmp, '.git')):
        rc, so, se = out('git', '-C', tmp, 'fetch', 'origin')
        if rc != 0:
            d_err = ('fetch rc=%s %s' % (rc, se[:200])) if d_err is None else d_err + ' | fetch rc=%s' % rc
        rc, so, se = out('git', '-C', tmp, 'show', 'origin/main:docs/decisions.md')
        if rc == 0:
            sha = hashlib.sha256(so).hexdigest().upper()  # raw bytes, zero transcoding (r292)
        else:
            d_err = ('show rc=%s %s' % (rc, se[:200])) if d_err is None else d_err + ' | show rc=%s' % rc
except Exception as e:
    d_err = repr(e)

state = json.load(open(os.path.join(REPO, 'state.json'), encoding='utf-8'))
prev = (state.get('last_decisions_sha') or '').upper()
cur = (sha or '').upper()
verdict = 'UNAVAILABLE' if sha is None else ('UNCHANGED' if cur == prev else 'CHANGED')

# orders.md CEO physical-items section (same fresh-read law)
orders_md_new = None
try:
    rc, so, se = out('git', '-C', tmp, 'show', 'origin/main:docs/orders.md')
    if rc == 0:
        text = so.decode('utf-8', 'replace')
        orders_md_new = len(text.splitlines())
except Exception:
    pass

print(json.dumps({
    'orders_dir_count': len(files), 'acked': len(ack), 'unacked': unacked,
    'ghost_acks': ghost_acks[:5], 'd19_verdict': verdict,
    'prev_sha': prev, 'cur_sha': cur, 'd19_err': d_err,
    'orders_md_lines': orders_md_new,
}, ensure_ascii=False, indent=1))
sys.exit(0)
