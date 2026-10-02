import json, os
d = 'results/p2cal_ext/n4_b1'
for i in range(6):
    p = os.path.join(d, f'shard-{i}-of-6.json')
    r = json.load(open(p, encoding='utf-8'))
    au = r['audit']
    print(f"shard-{i} {r['member']}: k={r['k_burned']}/{r['k_expected']} "
          f"L={r['L']} elapsed={au['elapsed_sec']}s workers={au['workers']} "
          f"lane={au['lane']}")
rows_dir = 'results/perpetual_faces/n4_b1'
total = 0
for m in ('COMPOSITE-CE-01', 'COMPOSITE-CE-02', 'DROUGHT-CE-01',
          'ENGULF-CE-01', 'NEEDLE-DE-01', 'VOLATILITY-CE-01'):
    n = sum(1 for _ in open(os.path.join(rows_dir, f'universes-{m}.jsonl'),
                            encoding='utf-8'))
    total += n
    print(f'  rows {m}: {n}')
print('TOTAL universe rows:', total)
