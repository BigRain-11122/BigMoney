# -*- coding: utf-8 -*-
# r336 bm-c D-19 fresh-read helper: fetch group repo, raw-blob SHA-256 of decisions.md
# (r292 law: python raw-bytes, never PS pipeline transcoding; r333 pattern + fetch leg).
import subprocess, hashlib, json, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

GROUP = r'K:\Fluxgroup\FluxGroup'
STATE = r'K:\Fluxgroup\FluxGroup\quant\bigmoney\state-bm-c.json'

r = subprocess.run(['git', '-C', GROUP, 'fetch', 'origin'], capture_output=True)
print('FETCH_RC', r.returncode)

dec = subprocess.check_output(['git', '-C', GROUP, 'show', 'origin/main:docs/decisions.md'])
sha = hashlib.sha256(dec).hexdigest()
text = dec.decode('utf-8', errors='replace')

st = json.load(open(STATE, encoding='utf-8'))
old = str(st.get('last_decisions_sha', '')).lower()

print('NEW_SHA', sha)
print('OLD_SHA', old)
print('VERDICT', 'MATCH-unchanged' if sha.lower() == old else 'CHANGED')
if sha.lower() != old:
    lines = text.splitlines()
    print('--- decisions.md tail 50 ---')
    for ln in lines[-50:]:
        print(ln)

orders = subprocess.check_output(['git', '-C', GROUP, 'show', 'origin/main:docs/orders.md']).decode('utf-8', errors='replace')
print('--- orders.md CEO physical-items zone (last 30 lines) ---')
for ln in orders.splitlines()[-30:]:
    print(ln)
