import json, os, re, sys

src = open('scripts/update_astock_daily.py', encoding='utf-8').read()
paths = set(re.findall(r'[\'"]([^\'"\n]*(?:ckpt|checkpoint|state|progress)[^\'"\n]*\.(?:json|jsonl))[\'"]', src))
print('ckpt faces found in source:', sorted(paths))

for p in sorted(paths):
    if not p.startswith(('data/', 'results/', 'logs/')):
        continue
    if os.path.exists(p):
        try:
            d = json.load(open(p, encoding='utf-8'))
            s = json.dumps(d, ensure_ascii=False)
            print('---', p, len(s), 'bytes')
            print(s[:500])
        except Exception as e:
            print('---', p, 'read err', e)
    else:
        print('---', p, 'missing')

per_dir = 'data/astock_daily/per'
if os.path.exists(per_dir):
    n = len(os.listdir(per_dir))
    print('per files on disk:', n)
else:
    print('per dir missing:', per_dir)
