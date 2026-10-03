import json, subprocess, hashlib, time, datetime

# 1. canonical decisions.md sha (raw bytes of git show origin/main:docs/decisions.md via D-19 blobless clone)
import os
p = os.path.join(os.environ['TEMP'], 'd19_r618_https')
r = subprocess.run(['git', '-C', p, 'show', 'origin/main:docs/decisions.md'], capture_output=True)
assert r.returncode == 0, 'decisions.md read fail'
dec_sha = hashlib.sha256(r.stdout).hexdigest()
print('decisions sha256 (raw-bytes):', dec_sha)

# 2. state bump 633->634 + watermark
sp = 'state-bm-a.json'
st = json.load(open(sp, encoding='utf-8'))
old = st.get('round_no')
st['round_no'] = old + 1
st['last_decisions_sha'] = dec_sha
st['last_decisions_ts'] = '2026-10-03T17:58:00+08:00'
json.dump(st, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'state: round_no {old} -> {st["round_no"]}, watermark updated')

# 3. heartbeat (bm-a single-writer)
hp = 'fleet/machines/bm-a.json'
hb = json.load(open(hp, encoding='utf-8'))
now = datetime.datetime.now()
hb['last_seen'] = now.strftime('%Y-%m-%dT%H:%M:%S') + '+08:00'
hb['current_task'] = 'r634: stopped-rebase heal (ring-1 18 UU + ring-2 merge to a9bed981c, pushed 9d282c41a) + S6 39 legs rc0 golden-week + FUND NULLS containment verified (bm-b burn face)'
hb['heartbeat_epoch_utc'] = int(time.time())
hb['clock_read'] = now.strftime('%Y-%m-%dT%H:%M:%S') + '+08:00'
json.dump(hb, open(hp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
# self-verify types (R170/R178/R262 law)
hb2 = json.load(open(hp, encoding='utf-8'))
assert isinstance(hb2['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
assert 'T' in hb2['clock_read'], 'clock_read must be T-separated'
print('heartbeat: epoch int OK, clock_read T-sep OK, last_seen', hb2['last_seen'])
