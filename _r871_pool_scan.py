import json
d = json.load(open('results/runnable_pool.json', encoding='utf-8'))
entries = d if isinstance(d, list) else d.get('entries', d.get('tasks', []))
for e in entries:
    name = e.get('name', e.get('id', '?'))
    if 'E16' in str(name):
        print(json.dumps(e, ensure_ascii=False, indent=1))
        break
# also count non-done entries
nd = [e for e in entries if e.get('status') != 'done']
print('non-done count:', len(nd))
for e in nd:
    if 'E16' not in str(e.get('name', '')):
        print('OTHER ready:', e.get('name'), e.get('status'))
