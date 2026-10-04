# r502 bm-c S0.5: orders full-set diff (r477 full-name caliber, r696 tree-ish) + D-19 dual-key raw-byte check (r660 subprocess law, r458/r672 per-key caliber)
import json, subprocess, hashlib, sys
REPO = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
HQ = r'K:\Fluxgroup\FluxGroup'
out_lines = []

def git_show_bytes(repo, spec):
    r = subprocess.run(['git', '-C', repo, 'show', spec], capture_output=True)
    if r.returncode != 0:
        return None, r.stderr.decode('utf-8', 'replace')
    return r.stdout, None

# --- orders diff (repo fleet/orders vs heartbeat ack) ---
out = subprocess.run(['git', '-C', REPO, 'ls-tree', '--name-only', 'HEAD:fleet/orders'], capture_output=True)
files = [l for l in out.stdout.decode('utf-8').splitlines() if l.strip().endswith('.md') and l.strip().startswith('O-')]
hb = json.load(open(REPO + r'\fleet\machines\bm-c.json', encoding='utf-8'))
ack = set(hb.get('orders_ack', []))
fs = set(files)
unacked = sorted(fs - ack)
extra = sorted(ack - fs)
out_lines.append('orders_in_git=%d ack=%d unacked=%d ack_extra=%d' % (len(fs), len(ack), len(unacked), len(extra)))
for u in unacked: out_lines.append('UNACKED: ' + u)
for e in extra: out_lines.append('ACK_EXTRA: ' + e)

# --- D-19 decisions + group orders (raw bytes via subprocess, zero PS pipeline) ---
st = json.load(open(REPO + r'\state-bm-c.json', encoding='utf-8'))
exp_dec = st.get('last_decisions_sha', '')
exp_ord = st.get('last_orders_sha', '')
fetch = subprocess.run(['git', '-C', HQ, 'fetch', 'origin'], capture_output=True)
out_lines.append('hq_fetch_rc=%d' % fetch.returncode)
dec_bytes, err1 = git_show_bytes(HQ, 'origin/main:docs/decisions.md')
ord_bytes, err2 = git_show_bytes(HQ, 'origin/main:docs/orders.md')
if dec_bytes is None:
    out_lines.append('DECISIONS_READ_ERR: ' + str(err1)[:200])
else:
    dec_sha = hashlib.sha256(dec_bytes).hexdigest().upper()
    out_lines.append('decisions_sha256=%s match=%s' % (dec_sha, dec_sha == exp_dec.upper()))
if ord_bytes is None:
    out_lines.append('GROUP_ORDERS_READ_ERR: ' + str(err2)[:200])
else:
    ord_sha = hashlib.sha1(ord_bytes).hexdigest().upper()
    out_lines.append('group_orders_sha1=%s match=%s' % (ord_sha, ord_sha == exp_ord.upper()))

# --- fleet inbox unread for bm-c/ALL ---
import os
inbox = REPO + r'\fleet\inbox'
proc = inbox + r'\processed'
names = []
for f in sorted(os.listdir(inbox)):
    p = os.path.join(inbox, f)
    if os.path.isfile(p) and (f.startswith('MSG-')) and f not in os.listdir(proc):
        names.append(f)
out_lines.append('inbox_unread=%d' % len(names))
for n in names: out_lines.append('UNREAD: ' + n)

txt = '\n'.join(out_lines) + '\n'
open(REPO + r'\results\_r502bmc_s05.txt', 'w', encoding='utf-8').write(txt)
print(txt)
