import json
d = json.load(open('results/fusion_grid_p1/p1_results.json', encoding='utf-8'))
cells = d['cells']
hdr = "%-22s %8s %5s %5s %5s %5s %8s %8s %6s" % ('cell', 'sharpe', 'g1', 'line', 'ci+', 'elig', 'dsr', 'n_ent', 'oos2+')
print(hdr)
n_g1 = n_elig = 0
for k, c in cells.items():
    g1 = c.get('g1_pass_v2'); el = c.get('eligible_v2')
    n_g1 += bool(g1); n_elig += bool(el)
    print("%-22s %8.4f %5s %5s %5s %5s %8.4f %8.0f %6s" % (
        k, c['sharpe_full'], str(g1), str(c.get('line_ok')), str(c.get('ci_lower_bound_positive')),
        str(el), c.get('dsr', float('nan')), c.get('n_entries_f6', -1), str(c.get('oos_dual_positive'))))
print()
print('G1 pass:', n_g1, '/ 45;  eligible_v2 (G2):', n_elig, '/ 45')
best = max(cells.values(), key=lambda c: c['sharpe_full'])
bestk = [k for k, c in cells.items() if c is best][0] if False else max(cells, key=lambda k: cells[k]['sharpe_full'])
print('best cell:', bestk, 'sharpe', cells[bestk]['sharpe_full'], 'dsr', cells[bestk]['dsr'])
