import io, subprocess, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
GROUP = r'C:\Fluxgroup\FluxGroup'

def blob(path):
    b = subprocess.run(['git','-C',GROUP,'show','origin/main:'+path],
                       capture_output=True).stdout
    return b.decode('utf-8', errors='replace').splitlines()

def read_local(p):
    raw = open(p, 'rb').read()
    if raw[:2] in (b'\xff\xfe', b'\xfe\xff'):
        enc = 'utf-16'
    else:
        enc = 'utf-8'
    return raw.decode(enc, errors='replace').splitlines()

orders_new = blob('docs/orders.md')
orders_old = set(read_local(r'results\_r975bmb_orders_fresh.md'))
dec_new = blob('docs/decisions.md')

# persist fresh views as UTF-8 for this and next round
open(r'results\_r976bmb_orders_fresh.md','w',encoding='utf-8',newline='\n').write('\n'.join(orders_new)+'\n')
open(r'results\_r976bmb_decisions_fresh.md','w',encoding='utf-8',newline='\n').write('\n'.join(dec_new)+'\n')

delta = [l for l in orders_new if l not in orders_old]
open(r'results\_r976bmb_orders_delta.txt','w',encoding='utf-8',newline='\n').write('\n'.join(delta)+'\n')
print('ORDERS_DELTA', len(delta))
KEYS = ('BigMoney','quant','bm-b','金融')
hits = [l for l in delta if any(k in l for k in KEYS)]
print('BM_HITS', len(hits))
for l in hits[:10]:
    print('ROW:', re.sub(r'\s+',' ',l)[:500])

# decisions: find rows newer than our watermark snapshot (578804c1 era).
# r975 kept no decisions fresh view; use last_decisions_sha_probe content anchor:
# find the last row we consumed (D-15-03 / bm-c r1026 note) and take rows after it.
try:
    dec_old = set(read_local(r'results\_r975bmb_decisions_fresh.md'))
except FileNotFoundError:
    dec_old = None
if dec_old is None:
    print('DEC_OLD_VIEW=absent -> full-tail scan needed')
else:
    dd = [l for l in dec_new if l not in dec_old]
    print('DEC_DELTA', len(dd))
    for l in dd[:10]:
        print('DEC:', re.sub(r'\s+',' ',l)[:400])
