import subprocess, hashlib, os, json
t = os.path.join(os.environ['TEMP'], 'fg-dec-bmb')
b = subprocess.check_output(['git', '-C', t, 'show', 'origin/main:docs/decisions.md'])
new_sha = hashlib.sha256(b).hexdigest().upper()
st = json.load(open('state.json', encoding='utf-8'))
old = str(st.get('last_decisions_sha', '')).upper()
print('old:', old)
print('new:', new_sha)
print('MATCH' if old == new_sha else 'CHANGED')
