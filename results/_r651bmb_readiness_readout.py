# -*- coding: ascii -*-
# r651 bm-b: readiness readout + trio burn process liveness + RAM gate
import json
d = json.load(open(r'results/finalize_trio_readiness.json', encoding='utf-8'))
print('ts:', d['ts'], '| mechanical_ready:', d['mechanical_ready'])
for k, v in d['families'].items():
    print('%s: have=%d rate=%.2f/min eta=%.1fh dup_k=%d' % (
        k, v['have'], v['rate_per_min'], v['eta_hours'], v['dup_k']))
g = d['gates']
print('gates: burn_complete=%s integrity=%s rehearsal_green=%s gov=%s' % (
    g['burn_complete'], g['integrity'], g['rehearsal_green'],
    d['governance']['status']))

import psutil
for p in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent']):
    try:
        cl = p.info['cmdline'] or []
        j = ' '.join(cl)
        if 'fund_' in j and ('nulls' in j or 'burn' in j):
            print('BURNPROC pid=%d %s' % (p.pid, j[:110]))
    except Exception:
        pass
vm = psutil.virtual_memory()
print('RAM avail %.2f GB / total %.2f GB; py CPU %.1f%%' % (
    vm.available / 1e9, vm.total / 1e9,
    psutil.cpu_percent(interval=0.4)))
