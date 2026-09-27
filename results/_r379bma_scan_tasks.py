import json, glob, io
for p in sorted(glob.glob(r'fleet/tasks/T-*.json')):
    try:
        d = json.load(io.open(p, encoding='utf-8'))
        st = d.get('status', '?')
        if st in ('open', 'claimed', 'in_progress'):
            tid = d.get('id', '?')
            owner = d.get('claimed_by', '-')
            title = str(d.get('title', d.get('subject', '?')))[:90]
            print(f"{tid:6} {st:12} owner={owner:6} | {title}")
    except Exception as e:
        print(p, 'ERR', e)
