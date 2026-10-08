import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import importlib.util, numpy as np, pandas as pd
spec = importlib.util.spec_from_file_location('probe', os.path.join(ROOT, 'results', '_r890bma_f1_ctap1_corr_probe.py'))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
close = m.etf_close_panel().loc[m.WARMUP_START:]
cut = min(m.futures_cutoff(), close.index[-1]); close = close.loc[:cut]
cta = m.cta_p1_daily_returns(cut)
for L, k in [(60, 2), (120, 2), (250, 2)]:
    r = m.f1_daily_returns(close, L, k)
    j = pd.concat([r.rename('f1'), cta.rename('cta')], axis=1, join='inner').dropna()
    print(f'cell L={L} k={k}: n={len(j)} f1_ann_ret={j.f1.mean()*242*100:.2f}% f1_ann_vol={j.f1.std()*np.sqrt(242)*100:.2f}% cta_ann_ret={j.cta.mean()*242*100:.2f}% cta_ann_vol={j.cta.std()*np.sqrt(242)*100:.2f}% nonzero_f1_days={(j.f1!=0).mean()*100:.1f}%')
print('joined window:', j.index[0].date(), '->', j.index[-1].date())
