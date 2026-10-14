import json, io, re
tree = json.load(open(r'results/_r936bmb_tsp_tree.json', encoding='utf-8'))
paths = [t['path'] for t in tree.get('tree', []) if t['type'] == 'blob']
out = io.open(r'results/_r936bmb_tsp_paths.txt', 'w', encoding='utf-8')
out.write('total blobs: %d\n' % len(paths))
# strategy-related paths
strat = [p for p in paths if re.search(r'(?i)strateg|策略', p)]
out.write('--- strategy-face paths (%d) ---\n' % len(strat))
for p in strat:
    out.write(p + '\n')
out.write('--- top-level dirs ---\n')
tops = sorted(set(p.split('/')[0] for p in paths))
for t in tops:
    out.write(t + '\n')
out.close()
print('blobs:', len(paths), 'strategy-face:', len(strat))
