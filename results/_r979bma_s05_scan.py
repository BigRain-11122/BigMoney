# r979 S0.5: orders ack diff scan + group watermark probe (DEC sha256 raw-blob / ORD content-sha1)
import json, subprocess, hashlib, os, glob, re

ROOT = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney'
GP = r'C:\Users\sjs20\Desktop\FluxGroup'  # group real-path (C:)

# 1) fleet orders ack diff
hb_path = os.path.join(ROOT, 'fleet', 'machines', 'bm-a.json')
with open(hb_path, encoding='utf-8') as f:
    hb = json.load(f)
acked = set(hb.get('orders_ack', []))
ofiles = glob.glob(os.path.join(ROOT, 'fleet', 'orders', 'O-*.md'))
oids = {os.path.basename(p)[:-3] for p in ofiles}
unacked = sorted(oids - acked)
print(json.dumps({'o_files': len(oids), 'acked': len(acked), 'unacked': unacked}, ensure_ascii=False))

# 2) group decisions.md raw-blob sha256 + orders.md content sha1
def gshow(path):
    r = subprocess.run(['git', '-C', GP, 'show', f'origin/main:{path}'], capture_output=True)
    return r.stdout

dec = gshow('docs/decisions.md')
dec_sha = hashlib.sha256(dec).hexdigest()
# ORD content-sha1: strip whitespace normalization per healed pin method (content face)
ordb = gshow('docs/orders.md')
ord_content = re.sub(r'\s+', ' ', ordb.decode('utf-8', 'replace')).strip()
ord_sha1 = hashlib.sha1(ord_content.encode('utf-8')).hexdigest()
print(json.dumps({'dec_sha256': dec_sha, 'ord_content_sha1': ord_sha1, 'dec_bytes': len(dec), 'ord_bytes': len(ordb)}, ensure_ascii=False))

# compare with state pins
with open(os.path.join(ROOT, 'state-bm-a.json'), encoding='utf-8') as f:
    st = json.load(f)
print(json.dumps({
    'pin_dec': st.get('last_decisions_sha'), 'dec_match': st.get('last_decisions_sha') == dec_sha,
    'pin_ord': st.get('last_orders_sha'), 'ord_match': st.get('last_orders_sha') == ord_sha1,
}, ensure_ascii=False))
