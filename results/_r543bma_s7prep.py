import subprocess, hashlib, io, json

# 1. pre-commit claw compare (CR-normalized)
try:
    hook = io.open(r'.git\hooks\pre-commit', encoding='utf-8', errors='replace').read()
except FileNotFoundError:
    hook = ''
canon = io.open(r'Tools\git-hooks\pre-commit', encoding='utf-8', errors='replace').read()
norm = lambda s: s.replace('\r\n', '\n')
same = norm(hook) == norm(canon)
print('claw:', 'IDENTICAL' if same else 'DRIFT/missing')

# 2. state round_no++
p = 'state-bm-a.json'
st = json.load(io.open(p, encoding='utf-8'))
old = st.get('round_no')
st['round_no'] = old + 1
# refresh clock fields if present
import datetime
now = datetime.datetime.now(datetime.timezone.utc).astimezone()
st['last_round_ts'] = now.isoformat(timespec='seconds')
io.open(p, 'w', encoding='utf-8', newline='') .write(json.dumps(st, ensure_ascii=False, indent=2))
print('state round_no:', old, '->', old + 1)
