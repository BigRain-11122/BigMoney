import json
from collections import Counter

rows = [json.loads(l) for l in open('results/mass_trial/screen_checkpoint.jsonl', encoding='utf-8')]
cand = [r for r in rows if r.get('row_type') == 'candidate']
ctrl = [r for r in rows if r.get('row_type') == 'control']
null = [r for r in rows if r.get('row_type') == 'null']
surv = [r for r in cand if r.get('screen_pass')]
err = [r for r in rows if r.get('status') == 'signal_error']

print('== survivors by module ==')
mods = Counter(r['family'].split('.')[0] for r in surv)
tot = Counter(r['family'].split('.')[0] for r in cand)
for m, n in mods.most_common():
    print(f"  {m:<16} {n:>3}/{tot[m]:<3} = {n/tot[m]*100:.0f}%")

print('== survivors by axis ==')
for ax in ('R', 'X', 'S', 'T'):
    a = Counter(r['axes'][ax] for r in surv)
    t = Counter(r['axes'][ax] for r in cand)
    print(' ', ax, {k: f"{a[k]}/{t[k]}" for k in sorted(t)})

print('== top-12 by beat_rate ==')
for r in sorted(surv, key=lambda x: -x['beat_rate_6m'])[:12]:
    print(f"  {r['id']:<11} {r['family']:<32} {json.dumps(r['axes'])} br={r['beat_rate_6m']} sh={r['sharpe_full']} dd={r['max_dd']} tr={r['n_trades']}")

print('== defaults controls: pass count ==', sum(1 for r in ctrl if r.get('screen_pass')))
ctrl_pass = [r['family'] for r in ctrl if r.get('screen_pass')]
print('  passing defaults:', ctrl_pass[:20])
print('== nulls ==')
print(' ', sorted(round(r.get('beat_rate_6m', 0), 3) for r in null))
print('== errors ==', [(r['id'], r['family']) for r in err])
print('== error rows detail ==')
for r in err:
    print(' ', r['id'], r.get('error'))
