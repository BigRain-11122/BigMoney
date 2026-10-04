# r684 bm-b: verify census shard row structure + 10 RC anchor stats presence
import json, io

cells = ["D-15|raw|base|time|h20", "D-15|raw|liq2|time|h20", "D-15|yang|base|time|h20",
         "D-15|yang|liq2|time|h20", "D-25|raw|base|time|h20", "D-25|raw|liq2|time|h20",
         "D-25|yang|base|time|h20", "Dtop10|raw|base|time|h20", "Dtop10|raw|liq2|time|h20",
         "Dtop10|yang|base|time|h20"]
found = {}
for k in range(6):
    d = json.load(io.open(r'results/refine_bench_stock/rev_census/shard-%dof6.json' % k, encoding='utf-8'))
    rows = d.get('rows', [])
    for r in rows:
        if r.get('name') in cells:
            found[r['name']] = r
print('found', len(found), 'of', len(cells))
missing = [c for c in cells if c not in found]
print('missing:', missing)
r = found.get('D-15|raw|base|time|h20', {})
print('sample keys:', sorted(r.keys()))
print('sample stats:', {k: r.get(k) for k in ('sharpe_full', 'ann_ret', 'max_dd', 'n_days', 'entries', 'unfillable')})
print('exits:', found.get('D-15|raw|base|time|h20', {}).get('exits'))
