# r1054 S0.5 probe: group orders delta + origin heartbeat faces + W266/W267 gate + inbox msgs
import subprocess, json, hashlib, io, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
REPO = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney'
GRP  = r'C:\Users\sjs20\Desktop\FluxGroup'

def gshow(path):
    p = subprocess.run(['git','-C',GRP,'show','origin/main:'+path],capture_output=True)
    return p.stdout if p.returncode==0 else b''

def gshow_repo(path):
    p = subprocess.run(['git','-C',REPO,'show','origin/main:'+path],capture_output=True)
    return p.stdout if p.returncode==0 else b''

out = {}

# 1) group orders delta: rows mentioning 2026-10-18 after ~10:0x
ordtxt = gshow('docs/orders.md').decode('utf-8','replace')
lines = ordtxt.splitlines()
recent = [l for l in lines if '2026-10-18' in l and ('11:' in l or '10:' in l or '09:5' in l or '12:' in l)]
out['group_orders_recent'] = recent[-25:]

# 2) heartbeat faces from origin
for m in ('bm-b','bm-c'):
    try:
        j = json.loads(gshow_repo('fleet/machines/%s.json'%m))
        hb = {k: j.get(k) for k in ('machine_id','last_seen','ts','round_no','round','verdict','idle_rounds')}
        acks = j.get('orders_ack') or []
        hb['orders_ack_count'] = len(acks)
        hb['orders_ack_tail'] = acks[-4:]
        hb['ack_0948'] = any('O-20261018-0948' in str(a) for a in acks)
        did = str(j.get('did') or j.get('current') or '')[:280]
        hb['did_tail'] = did
        out[m] = hb
    except Exception as e:
        out[m] = {'err': repr(e)[:200]}

# 3) W266/W267 gate on origin: ls-tree full, filter w266/w267
p = subprocess.run(['git','-C',REPO,'ls-tree','-r','--name-only','origin/main'],capture_output=True)
tree = p.stdout.decode('utf-8','replace').splitlines()
w266 = [t for t in tree if 'w266' in t.lower()]
w267 = [t for t in tree if 'w267' in t.lower()]
out['w266_faces'] = w266
out['w267_faces'] = w267
out['w266_finalize_landed'] = any('n1_w266_results' in t for t in w266)
out['w267_prereg_landed'] = len(w267) > 0

# 4) inbox new msgs (headers only, first 12 lines each)
for f in ('MSG-20261018-0845-bmb-audition-redrop-mixsample.md',
          'MSG-20261018-1035-bmb-rootfix.md',
          'MSG-20261018-1137-bmb-canon-installed.md'):
    b = gshow_repo('fleet/inbox/'+f)
    out[f] = b.decode('utf-8','replace')[:600] if b else 'ABSENT'

print(json.dumps(out, ensure_ascii=False, indent=1)[:6500])
