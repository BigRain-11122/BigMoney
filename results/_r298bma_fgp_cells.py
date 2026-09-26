import json
d = json.load(open('results/fusion_grid_p1/p1_results.json', encoding='utf-8'))
cells = d['cells']
print('cells type:', type(cells).__name__, 'n=', len(cells))
sample_key = next(iter(cells))
print('sample key:', sample_key)
print('cell fields:', list(cells[sample_key].keys()))
print()
hdr = "%-40s %8s %8s %8s %6s %6s %6s" % ('cell', 'sharpe', 'annret', 'maxdd', 'g1', 'g2', 'dsr')
print(hdr)
for k, c in cells.items():
    print("%-40s %8.4f %8.4f %8.4f %6s %6s %6s" % (
        k, c.get('sharpe_full', float('nan')), c.get('ann_ret', float('nan')),
        c.get('max_dd', float('nan')), str(c.get('g1_pass', c.get('g1_prime_pass', '?'))),
        str(c.get('g2_pass', c.get('g2_registration_pass', '?'))), str(c.get('dsr', '?'))))
