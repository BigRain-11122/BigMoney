import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')
from scripts.mass_trial_w1 import Ctx, sample_draws

ctx = Ctx()
picks = ctx.roster[:2] \
    + [f for f in ctx.roster if f['kind'] == 'panel'][:2] \
    + [f for f in ctx.roster if f['kind'] == 'mask'][:1] \
    + [f for f in ctx.roster if f['kind'] == 'macro'][:1]
for fam in picks:
    d_idx, params, axes = next(iter(sample_draws(fam, 4)))
    try:
        e, x, s = ctx.build_signals(fam, params, axes)
        es = int(e.values.sum())
        xs = int(x.values.sum())
        print(f"{fam['family']:<38} {fam['kind']:<6} entry={es:>6} exit={xs:>6}")
    except Exception as ex:
        print(fam['family'], fam['kind'], 'ERR', type(ex).__name__, str(ex)[:120])
