import re, sys
for p in [r'results\_r871bma_closeout.py']:
    src = open(p, 'rb').read().decode('utf-8', errors='replace')
    print('FILE', p, len(src))
    for m in re.finditer(r'round_reports', src):
        seg = src[max(0, m.start() - 80):m.end() + 60]
        print('  HIT:', repr(seg))
    print('  has-root-face:', 'round_reports-bm-a' in src)
    print('  has-logs-path:', 'logs/iteration-loop' in src or 'logs\\\\iteration-loop' in src)
