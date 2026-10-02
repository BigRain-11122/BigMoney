import json, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
d = json.load(open('results/perpetual_faces/n1_w74_results.json', encoding='utf-8'))
npc = d['null_pool_cumulative']
print('canon:', npc['canon'])
print('pre_w74:', npc['pre_w74_cumulative'])
print('w74:', npc.get('w74_cumulative') or npc.get('w74'))
print('merged:', npc['merged'] if 'merged' in npc else {k: v for k, v in npc.items() if 'merg' in k})
sl = d.get('skill_line_v2_k_lift', {})
print('skill_line_v2:', json.dumps(sl, ensure_ascii=False)[:600])
lg = d['science_gates']['ledger']
print('ledger:', json.dumps(lg, ensure_ascii=False))
# A-family p95
fams = d.get('families') or {}
for k, v in fams.items():
    if 'A_random' in k:
        runs = v.get('runs') or []
        import statistics
        sh = sorted(float(r['full']['sharpe']) for r in runs)
        n = len(sh)
        p95 = sh[int(0.95 * (n - 1))]
        print('A_family:', k, 'n=', n, 'p95=', round(p95, 4), 'mu=', round(sum(sh)/n, 6), 'sigma=', round(statistics.pstdev(sh), 6))
    if 'B_random' in k:
        runs = v.get('runs') or []
        sh = sorted(float(r['full']['sharpe']) for r in runs)
        n = len(sh)
        print('B_family:', k, 'n=', n, 'mu=', round(sum(sh)/n, 6), 'sigma=', round(statistics.pstdev(sh), 6))
