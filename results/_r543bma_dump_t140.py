import json, io
for p in ['fleet/tasks/T-2026-10-01-140-P1.json', 'fleet/tasks/T-2026-10-01-142-P0.json']:
    d = json.load(io.open(p, encoding='utf-8'))
    out = ['=== ' + p + ' ===']
    for k, v in d.items():
        s = str(v)
        if len(s) > 600:
            s = s[:600] + '...[trunc]'
        out.append(k + ': ' + s)
    io.open('results/_r543bma_t140.txt', 'a', encoding='utf-8').write('\n'.join(out) + '\n\n')
print('done')
