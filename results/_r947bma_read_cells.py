import json

d = json.load(open('results/lhb_thermo_ic_p1/lhb_thermo_ic_p1_results.json', encoding='utf-8'))
print('gating_summary:', json.dumps(d['gating_summary'], ensure_ascii=False))
print('faces:', json.dumps(d['faces'], ensure_ascii=False)[:200])
print()
hdr = ('axis', 'z', 'IC_full', 'IC_IS', 'IC_OOS', 'IC_IR', 'nM', 'p95', 'V1', 'V2', 'V3', 'M1t', 'M1')
print('%-18s%-5s%9s%9s%9s%8s%4s%8s%5s%5s%5s%7s%5s' % hdr)
for c in d['cells']:
    if not c['gating']:
        continue
    print('%-18s%-5s%9s%9s%9s%8s%4s%8s%5s%5s%5s%7s%5s' % (
        c['axis'], c['zwin'], c['ts_ic_full'], c['ts_ic_is'], c['ts_ic_oos'],
        c['ic_ir_is'], c['n_months_is'], c['null_p95_abs_ic'],
        c['v1'], c['v2'], c['v3'], c['m1_t'], c['m1_pass']))
print()
print('report-only IS ICs (h5/h20):')
for c in d['cells']:
    if c['gating']:
        continue
    print('  %-18s z%-4d h%-3d IS=%s OOS=%s' % (
        c['axis'], c['zwin'], c['h'], c['ts_ic_is'], c['ts_ic_oos']))
print()
print('segment ICs (h10):')
for c in d['cells']:
    if not c['gating']:
        continue
    segs = c['segments']
    print('  %-18s z%-4d S1=%s S2=%s S3=%s' % (
        c['axis'], c['zwin'],
        segs['S1']['ts_ic'], segs['S2']['ts_ic'], segs['S3']['ts_ic']))
