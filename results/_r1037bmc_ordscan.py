import subprocess, hashlib, io, json, re

def blob(repo, path):
    return subprocess.run(['git','-C',repo,'show','origin/main:'+path],
                          capture_output=True).stdout

ord_bytes = blob(r'K:\Fluxgroup\FluxGroup', 'docs/orders.md')
dec_bytes = blob(r'K:\Fluxgroup\FluxGroup', 'docs/decisions.md')

out = {}
out['ord_content_sha1'] = hashlib.sha1(ord_bytes).hexdigest()
out['dec_raw_blob_sha256'] = hashlib.sha256(dec_bytes).hexdigest()

txt = ord_bytes.decode('utf-8', errors='replace')
lines = txt.splitlines()
tail = []
for l in lines:
    if not l.strip().startswith('|'):
        continue
    tail.append(l)
out['ord_tail_rows'] = [r[:600] for r in tail[-30:]]
out['ord_total_table_rows'] = len(tail)

dtxt = dec_bytes.decode('utf-8', errors='replace')
dlines = [l for l in dtxt.splitlines() if l.strip().startswith('|')]
out['dec_tail_rows'] = [r[:400] for r in dlines[-8:]]

io.open(r'results\_r1037bmc_ordscan.json','w',encoding='utf-8').write(json.dumps(out,ensure_ascii=False,indent=1))
print('ORD sha1:', out['ord_content_sha1'])
print('DEC sha256:', out['dec_raw_blob_sha256'])
print('written')
