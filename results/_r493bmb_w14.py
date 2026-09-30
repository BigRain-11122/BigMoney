import json
rp = json.load(open('results/runnable_pool.json'))
for e in rp.get('entries', []):
    if 'W14' in str(e.get('id', '')):
        print(json.dumps(e, ensure_ascii=False, indent=1)[:3500])
