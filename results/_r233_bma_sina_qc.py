# r233 bm-a probe: T-72 s2 first-pull spot QC (supervision R6) on 6 freshest per-dir files
# R230-R232 QC caliber: 14-col frozen schema identical, exactly 100 rows/stock (num=100 frozen),
# tail = latest bar day (2026-09-24). Plus sina r0..r3 self-consistency law (netamount ~= sum of *_net).
import os, json, sys, time
sys.stdout.reconfigure(encoding='utf-8')

FROZEN_HEADER = "opendate,trade,changeratio,turnover,netamount,ratioamount,r0,r1,r2,r3,r0_net,r1_net,r2_net,r3_net"
LATEST_BAR = "2026-09-24"
per = 'data/sina_mf/per'
files = [(os.path.getmtime(os.path.join(per, f)), f) for f in os.listdir(per) if f.endswith('.csv')]
files.sort()
print('per-dir files:', len(files), 'newest mtime:', time.strftime('%H:%M:%S', time.localtime(files[-1][0])))

prog = json.load(open('data/sina_mf/_progress.json', encoding='utf-8-sig'))
print('checkpoint done:', len(prog['done']), 'attempts:', len(prog.get('attempts', {})))

results = []
for mt, f in files[-6:]:
    p = os.path.join(per, f)
    with open(p, encoding='utf-8-sig') as fh:
        lines = [l.rstrip('\n').rstrip('\r') for l in fh if l.strip()]
    hdr_ok = lines[0] == FROZEN_HEADER
    nrows = len(lines) - 1
    tail = lines[-1].split(',')[0]
    # self-consistency: |netamount - (r0_net+r1_net+r2_net+r3_net)| / max(|netamount|,1) <= 1e-3
    worst = 0.0
    for l in lines[1:]:
        c = l.split(',')
        try:
            na = float(c[4]); s = sum(float(c[i]) for i in (10, 11, 12, 13))
        except ValueError:
            continue
        worst = max(worst, abs(na - s) / max(abs(na), 1.0))
    ok = hdr_ok and nrows == 100 and tail == LATEST_BAR and worst <= 1e-3
    results.append(ok)
    print(f'{f}: header_ok={hdr_ok} rows={nrows} tail={tail} sum_dev_max={worst:.2e} -> {"PASS" if ok else "FAIL"}')

print('SPOT QC:', 'PASS' if all(results) and len(results) == 6 else 'FAIL', f'({sum(results)}/{len(results)})')
