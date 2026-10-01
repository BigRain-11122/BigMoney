import json, os, glob

REPO = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
os.chdir(REPO)

print('=== open/claimed tickets ===')
for p in sorted(glob.glob('fleet/tasks/*.json')):
    try:
        t = json.load(open(p, encoding='utf-8'))
    except Exception as e:
        print('BADJSON:', p, e)
        continue
    st = t.get('status', '')
    if st in ('open', 'claimed', 'in_progress'):
        print(p, '| status:', st, '| claimed_by:', t.get('claimed_by', ''),
              '| title:', str(t.get('title', ''))[:100])

print()
print('=== watermark red flag ===')
try:
    w = json.load(open('results/watermark_red.json', encoding='utf-8'))
    print(json.dumps(w, ensure_ascii=False)[:500])
except Exception as e:
    print('watermark_red.json:', e)

print()
print('=== inbox unread ===')
inbox = 'fleet/inbox'
proc = 'fleet/inbox/processed'
done = set(os.listdir(proc)) if os.path.isdir(proc) else set()
if os.path.isdir(inbox):
    for f in sorted(os.listdir(inbox)):
        if f.endswith('.md') or f.endswith('.json'):
            if f not in done:
                path = os.path.join(inbox, f)
                if os.path.isfile(path):
                    print('UNREAD:', f)
                    c = open(path, encoding='utf-8', errors='replace').read()
                    print(c[:600])
                    print('---')
