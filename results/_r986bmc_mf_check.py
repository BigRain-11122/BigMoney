import json, os, glob, time
from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))
now = datetime.now(CST)
print('now:', now.isoformat())

# 1. MF panel status (moneyflow collector face - data/moneyflow/)
print('--- MF panel faces ---')
for p in ['data/moneyflow/status.json', 'data/moneyflow/mf_status.json', 'data/moneyflow/panel_status.json']:
    if os.path.exists(p):
        d = json.load(open(p, encoding='utf-8'))
        print(p, '=>', json.dumps({k: d.get(k) for k in ('complete', 'cutoff', 'status', 'done', 'total', 'last_pull', 'updated') if k in d}, ensure_ascii=False)[:300])

# look for moneyflow dir shape
if os.path.isdir('data/moneyflow'):
    files = glob.glob('data/moneyflow/*.json') + glob.glob('data/moneyflow/*.parquet')
    print('moneyflow dir entries:', len(files), sorted(os.listdir('data/moneyflow'))[:8])

# 2. MF collector state in results (bm-a mirror faces)
for p in glob.glob('results/*moneyflow*') + glob.glob('results/*mf*'):
    print('results face:', p)

# 3. bm-a heartbeat freshness
try:
    hb = json.load(open('fleet/machines/bm-a.json', encoding='utf-8'))
    ts = hb.get('ts') or hb.get('last_seen')
    print('--- bm-a heartbeat ---')
    print('ts:', ts, '| now_active:', str(hb.get('activity_now') or hb.get('now_active'))[:120])
    if ts:
        t = datetime.fromisoformat(ts)
        age = (now - t).total_seconds() / 60
        print('age_min:', round(age, 1))
except Exception as e:
    print('bm-a hb read fail:', e)

# 4. fleet inbox for bm-c unread
print('--- inbox unread for bm-c/ALL ---')
for f in sorted(glob.glob('fleet/inbox/*.md') + glob.glob('fleet/inbox/*.json')):
    print('inbox file:', f, '| mtime:', datetime.fromtimestamp(os.path.getmtime(f), CST).isoformat())
