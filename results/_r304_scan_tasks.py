import json, glob, os
for f in sorted(glob.glob('fleet/tasks/*.json')):
    try:
        t = json.load(open(f, encoding='utf-8'))
        s = t.get('status', '?')
        tid = t.get('id', os.path.basename(f))
        claimed = t.get('claimed_by', '')
        if s in ('open', 'claimed'):
            print(tid, '|', s, '| pri=', t.get('priority', '?'), '| claimed_by=', claimed, '|', t.get('title', '')[:80])
    except Exception as e:
        print(f, 'ERR', e)
