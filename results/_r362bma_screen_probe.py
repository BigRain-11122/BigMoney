import sys, time, json
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')
from scripts.mass_trial_w1 import Ctx, _screen_one

ctx = Ctx()
rows = json.load(open('results/mass_trial/w1_candidates.json', encoding='utf-8'))['candidates']
for r in rows[:2] + [r for r in rows if r['axes']['S'] == 'delever'][:1]:
    r = dict(r); r['row_type'] = 'candidate'
    t0 = time.time()
    try:
        out = _screen_one(ctx, r)
        print(json.dumps({k: out.get(k) for k in
                          ('id', 'family', 'axes', 'beat_rate_6m', 'n_windows',
                           'n_trades', 'sharpe_full', 'max_dd', 'screen_pass',
                           'elapsed_s')}, ensure_ascii=False))
    except Exception as ex:
        print(r['id'], 'ERR', type(ex).__name__, str(ex)[:200])
