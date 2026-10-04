import json, os, glob

raw = open('results/crash_fuse.bm-a.json', 'rb').read()
d = json.loads(raw.decode('utf-8', errors='replace'))
sig = d.get('sigs', {})
for k in ['scripts/fund_value_p1.py|run,--nulls',
          'scripts/fund_quality_p1.py|run,--nulls',
          'scripts/fund_divlowvol_p1.py|run,--nulls']:
    print('=====', k)
    print(json.dumps(sig.get(k, {}), ensure_ascii=False, indent=1)[:1500])

print('\n--- nulls checkpoint files ---')
for fam in ['fund_value_p1', 'fund_quality_p1', 'fund_divlowvol_p1']:
    p = os.path.join('results', fam)
    if not os.path.isdir(p):
        print(fam, ': dir missing')
        continue
    for f in sorted(glob.glob(os.path.join(p, '*nulls*'))):
        sz = os.path.getsize(f)
        print(f, sz)
