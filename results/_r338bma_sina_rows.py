import json

r = json.load(open('results/shortline/sina_construct_p1.json', encoding='utf-8'))
rows = r.get('rows', [])
print('rows:', len(rows))
if rows:
    print('row keys:', list(rows[0].keys()))
out = []
for row in rows:
    out.append(json.dumps(row, ensure_ascii=False))
# gates + audit + ledger + trials
out.append('audit=' + json.dumps(r.get('audit'), ensure_ascii=False))
out.append('ledger_note=' + json.dumps(r.get('ledger_note'), ensure_ascii=False))
out.append('trials_ledger=' + json.dumps(r.get('trials_ledger'), ensure_ascii=False))
out.append('prereg=' + json.dumps(r.get('prereg'), ensure_ascii=False))
out.append('runtime_s=' + str(r.get('runtime_s')))
open('results/_r338bma_sina_rows.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written, total lines:', len(out))
