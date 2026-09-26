import json, os, glob
print("== watermark_red ==")
try:
    print(open('results/watermark_red.json', encoding='utf-8').read())
except Exception as e:
    print('ERR', e)
print("== tasks board ==")
for f in sorted(glob.glob('fleet/tasks/*.json')):
    d = json.load(open(f, encoding='utf-8-sig'))
    st = d.get('status')
    t = d.get('title') or d.get('subject') or ''
    owner = d.get('claimed_by') or ''
    print(os.path.basename(f), '|', st, '|', owner, '|', str(t)[:70])
