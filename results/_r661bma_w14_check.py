import json

d = json.load(open(r'results\runnable_pool.json', encoding='utf-8'))
for it in d['entries']:
    if it.get('id') == 'TRIAL-LABOR-W14-GENERATE':
        print(json.dumps(it, ensure_ascii=False, indent=1).encode('ascii', errors='replace').decode())
