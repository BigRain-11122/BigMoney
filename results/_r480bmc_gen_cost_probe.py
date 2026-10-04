"""r480 bm-c: measure build_signals per-call cost (generate runtime estimate)."""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import scripts.mass_trial_w1 as m

t0 = time.time()
ctx = m.Ctx()
t_ctx = time.time() - t0
print(f"Ctx build: {t_ctx:.1f}s")
fam0 = ctx.roster[0]
draws = list(m.sample_draws(fam0, 12, skip=m.W3_SKIP))
t0 = time.time()
n_ok = 0
for _, p, a in draws:
    try:
        m.ctx_ok = None
        e, x, s = ctx.build_signals(fam0, p, a)
        n_ok += 1
    except Exception as ex:
        print("  err", type(ex).__name__)
per = (time.time() - t0) / max(len(draws), 1)
print(f"build_signals: {per*1000:.0f} ms/call x {n_ok}/{len(draws)} ok")
est_builds = 6500
print(f"generate estimate: {per*est_builds/60:.1f} min for ~{est_builds} builds (single-core)")
