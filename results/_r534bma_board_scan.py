import json, glob
for p in sorted(glob.glob(r'fleet\tasks\*.json')):
    try:
        t = json.load(open(p, encoding='utf-8'))
        st = t.get('status', '?')
        own = t.get('claimed_by', '') or t.get('owner', '')
        if st in ('open', 'claimed', 'in_progress'):
            print(f"{t.get('id','?')} | {st} | {own or '-'} | {t.get('title','')[:80]}")
    except Exception as e:
        print(p, 'ERR', e)
