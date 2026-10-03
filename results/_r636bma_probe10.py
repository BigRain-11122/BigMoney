import os
import time

for d in (r'results\trial_labor_w2', r'results\mass_trial'):
    print('====', d)
    for fn in sorted(os.listdir(d)):
        fp = os.path.join(d, fn)
        if os.path.isfile(fp):
            mt = time.strftime('%H:%M:%S', time.localtime(os.path.getmtime(fp)))
            sz = os.path.getsize(fp)
            print(f'  {fn} | {sz}B | {mt}')
        else:
            print(f'  [dir] {fn}')
