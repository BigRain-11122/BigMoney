import json
d = json.load(open(r'results\t73_s2\factor_history.json', encoding='utf-8'))
print('elapsed:', d['elapsed_s'], 'ts:', d['ts'], 'cache_last_bar:', d['cache_last_bar'])
for k in ('vol60/h10', 'size/h10'):
    f = d['faces'][k]
    print(k, 'gates:', f['gates'])
    print('  is :', f['blocks']['is'])
    print('  oos:', f['blocks']['oos'])
print('--- era_table_h10 (ic_mean/ic_ir per era) ---')
for sig, eras in d['era_table_h10'].items():
    row = {e: (None if v is None else (v.get('ic_mean'), v.get('ic_ir'), v.get('n_periods')))
           for e, v in eras.items()}
    print(sig, row)
print('--- mktcap_median_era ---')
print(d.get('mktcap_median_era'))
print('--- dividend_style ---')
ds = d['dividend_style']
print('events:', ds['suspected_fund_events_510880'])
print('eras_510880:', json.dumps(ds['eras_510880'], ensure_ascii=False))
print('overlap:', json.dumps(ds['overlap_vs_510300'], ensure_ascii=False))
