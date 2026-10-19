import hashlib, io, json, subprocess, datetime

GRP = r'K:\Fluxgroup\FluxGroup'
REPO = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
dec = subprocess.run(['git', '-C', GRP, 'show', 'origin/main:docs/decisions.md'], capture_output=True).stdout
ordr = subprocess.run(['git', '-C', GRP, 'show', 'origin/main:docs/orders.md'], capture_output=True).stdout
dec_sha = hashlib.sha256(dec).hexdigest()
ord_sha = hashlib.sha1(ordr).hexdigest()

st_path = REPO + r'\state-bm-c.json'
st = json.load(io.open(st_path, encoding='utf-8'))
prev_dec, prev_ord = st.get('last_decisions_sha'), st.get('last_orders_sha')
st['last_decisions_sha'] = dec_sha
st['last_orders_sha'] = ord_sha
st['last_orders_sha_note'] = ('r1137: ORD %s->%s (content-sha1 pinned method r977) / DEC %s->%s (raw-blob sha256) -- '
                              'tail read D-20261020-01..03 (HQ/night executors, none binding bm-c) + orders tail '
                              'O-20261019-1935/O-20261019-2230 (full-fleet fill orders already carried by the N1 wave chain)'
                              % (prev_ord[:8], ord_sha[:8], prev_dec[:8], dec_sha[:8]))
json.dump(st, io.open(st_path, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1, sort_keys=True)
print('watermark advanced: ord', ord_sha[:8], 'dec', dec_sha[:8])