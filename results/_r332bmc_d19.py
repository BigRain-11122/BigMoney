# r332 bm-c D-19 fresh-read helper: raw-blob SHA-256 of group decisions.md (r292 law:
# python raw-bytes, never PS pipeline transcoding). Prints MATCH/CHANGED + tail lines
# of the dispatch-board block if changed. Also prints CEO physical-items section of orders.md.
import subprocess, hashlib, json

GROUP = r'K:\Fluxgroup\FluxGroup'
STATE = r'K:\Fluxgroup\FluxGroup\quant\bigmoney\state-bm-c.json'

dec = subprocess.check_output(['git', '-C', GROUP, 'show', 'origin/main:docs/decisions.md'])
sha = hashlib.sha256(dec).hexdigest()
text = dec.decode('utf-8', errors='replace')

st = json.load(open(STATE, encoding='utf-8'))
old = str(st.get('last_decisions_sha', '')).lower()

print('NEW_SHA', sha)
print('OLD_SHA', old)
print('VERDICT', 'MATCH-unchanged' if sha.lower() == old else 'CHANGED')
if sha.lower() != old:
    # print last 60 lines (dispatch board + newest decisions live at the tail)
    lines = text.splitlines()
    print('--- decisions.md tail 60 ---')
    for ln in lines[-60:]:
        print(ln)

orders = subprocess.check_output(['git', '-C', GROUP, 'show', 'origin/main:docs/orders.md']).decode('utf-8', errors='replace')
print('--- orders.md CEO physical-items zone (last 40 lines) ---')
for ln in orders.splitlines()[-40:]:
    print(ln)
