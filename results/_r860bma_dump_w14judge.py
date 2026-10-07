import json
p = json.load(open(r'results\runnable_pool.json', encoding='utf-8'))
for e in p['entries']:
    if e.get('id') == 'TRIAL-LABOR-W14-JUDGE':
        with open(r'results\_r860bma_w14judge_entry.json', 'w', encoding='utf-8') as fh:
            json.dump(e, fh, ensure_ascii=False, indent=1)
        print('written')
        break
