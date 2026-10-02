# r602 bm-b fuse-face probe: map the 2 blocked sigs across shared+lanes
import json, subprocess, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TARGETS = ('scripts/fund_value_p1.py|run,--cell,VALUE-PB,--face,x2',
           'scripts/fund_value_p1.py|run,--nulls')

def show(p):
    r = subprocess.run(['git', 'show', 'origin/main:' + p], capture_output=True)
    return json.loads(r.stdout.decode('utf-8', errors='replace'))

for f in ('results/crash_fuse.json', 'results/crash_fuse.bm-a.json',
          'results/crash_fuse.bm-b.json', 'results/crash_fuse.bm-c.json'):
    try:
        d = show(f)
    except Exception as ex:
        print('===', f, 'ERR', str(ex)[:60])
        continue
    print('===', f)
    for k in TARGETS:
        s = (d.get('sigs') or {}).get(k)
        t = (d.get('cleared') or {}).get(k)
        if s:
            print('  sig: refusals=%s last_crash=%s last_refusal=%s' % (
                s.get('refusals'), s.get('last_crash_ts'),
                s.get('last_refusal_ts')))
        else:
            print('  sig: NONE')
        if t:
            print('  tomb: cleared_ts=%s by=%s' % (t.get('cleared_ts'),
                                                  t.get('cleared_by')))
        else:
            print('  tomb: NONE')
