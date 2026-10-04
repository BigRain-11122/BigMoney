import json

raw = open('results/runnable_pool.json', 'rb').read()
d = json.loads(raw.decode('utf-8', errors='replace'))
for it in d.get('entries', []):
    if it.get('id', '').endswith('-NULLS'):
        print('=====', it.get('id'))
        for s in it.get('shards', []):
            print(json.dumps(s, ensure_ascii=False, indent=1)[:800])
        for k in ('workers_plan', 'lane_owner', 'lane_guard'):
            if k in it:
                print(k, '=', json.dumps(it[k], ensure_ascii=False)[:300])

print('\n--- bm-b heartbeat ---')
try:
    hb = json.loads(open('fleet/machines/bm-b.json', 'rb').read().decode('utf-8', errors='replace'))
    print(json.dumps({k: hb.get(k) for k in ('machine_id', 'last_seen', 'current_task', 'cpu_cores', 'verdict', 'heartbeat_epoch_utc')}, ensure_ascii=False, indent=1))
except Exception as e:
    print('read fail:', e)
