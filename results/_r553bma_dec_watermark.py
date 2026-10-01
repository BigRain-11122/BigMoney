import subprocess, hashlib, json, io
repo = r'C:\Users\sjs20\Desktop\FluxGroup'
subprocess.run(['git', '-C', repo, 'fetch', 'origin'], capture_output=True)
raw = subprocess.check_output(['git', '-C', repo, 'show', 'origin/main:docs/decisions.md'])
sha = hashlib.sha256(raw).hexdigest().upper()
st = json.load(io.open(r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\state-bm-a.json', encoding='utf-8'))
prev = (st.get('last_decisions_sha') or '').upper()
print('current decisions sha:', sha)
print('state watermark    :', prev)
print('MATCH' if sha == prev else 'CHANGED')
text = raw.decode('utf-8', errors='replace')
tail = text.strip().splitlines()[-25:]
print('--- tail 25 lines ---')
for line in tail:
    print(line[:150])
