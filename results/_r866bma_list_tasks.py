import json, glob, os
for f in sorted(glob.glob(r'fleet\tasks\*.json')):
    try:
        d = json.load(open(f, encoding='utf-8'))
        s = d.get('status', '?')
        if s in ('open', 'claimed', 'in_progress'):
            cb = d.get('claimed_by', '-')
            t = d.get('title', d.get('subject', '?'))
            print(f'{os.path.basename(f)}: {s} claimed_by={cb} | {t[:90]}')
    except Exception as e:
        print(os.path.basename(f), 'ERR', e)
