import json

# Fix 1: heartbeat clock_read/last_seen -> colon-form ISO offset
hb_path = 'fleet/machines/bm-a.json'
raw = open(hb_path, 'rb').read()
hb = json.loads(raw.decode('utf-8'))
bad = hb['clock_read']
fixed = bad[:-4] + bad[-4:-2] + ':' + bad[-2:]
assert fixed.endswith('+08:00') and 'T' in fixed, fixed
hb['clock_read'] = fixed
hb['last_seen'] = fixed
open(hb_path, 'wb').write(json.dumps(hb, ensure_ascii=False, indent=1).encode('utf-8'))
import datetime
datetime.datetime.fromisoformat(json.loads(open(hb_path, 'rb').read().decode('utf-8'))['clock_read'])
print('heartbeat clock fixed ->', fixed)

# Fix 2: state last_round_at/updated -> colon form
st_path = 'state-bm-a.json'
raw = open(st_path, 'rb').read()
st = json.loads(raw.decode('utf-8'))
st['last_round_at'] = fixed
st['updated'] = fixed
open(st_path, 'wb').write(json.dumps(st, ensure_ascii=False, indent=1).encode('utf-8'))
print('state clock fixed ->', fixed)

# Fix 3: round report line timestamp -> colon form
rp_path = 'round_reports-bm-a.md'
raw = open(rp_path, 'rb').read()
t = raw.decode('utf-8')
old_ts = '2026-10-03T06:57:29+0800'
n = t.count(old_ts)
assert n == 1, n
t = t.replace(old_ts, '2026-10-03T06:57:29+08:00')
open(rp_path, 'wb').write(t.encode('utf-8'))
print('round report ts fixed (n=%d)' % n)
print('CLOCK-FORMAT-ALL-FIXED')
