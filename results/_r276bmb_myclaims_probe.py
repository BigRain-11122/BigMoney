import json, glob, os
out = []
for p in sorted(glob.glob('fleet/tasks/T-*.json')):
    d = json.load(open(p, encoding='utf-8-sig'))
    cb = d.get('claimed_by', '')
    if 'bm-b' not in cb or d.get('status') != 'claimed':
        continue
    prog_keys = [k for k in d if k.startswith('progress_r')]
    last = prog_keys[-1] if prog_keys else ''
    note = (d.get('note') or '')[:150]
    out.append({'id': d.get('id'), 'last_progress': last,
                'note': note})
json.dump(out, open('results/_r276bmb_myclaims.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('claimed-by-bm-b not done:', len(out))
for r in out:
    print(r['id'], r['last_progress'])
