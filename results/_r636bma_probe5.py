import json

for fp in (r'results\crash_fuse.json', r'results\crash_fuse.bm-a.json'):
    cf = json.load(open(fp, encoding='utf-8'))
    print('=====', fp)
    sig = cf['sigs'].get('scripts/fund_value_p1.py|run,--nulls')
    print('value-nulls sig:', json.dumps(sig, ensure_ascii=False)[:500] if sig else None)
    sig2 = cf['sigs'].get('scripts/fund_divlowvol_p1.py|run,--nulls')
    print('divlowvol-nulls sig:', json.dumps(sig2, ensure_ascii=False)[:500] if sig2 else None)
    sig3 = cf['sigs'].get('scripts/fund_quality_p1.py|run,--nulls')
    print('quality-nulls sig sha+refusals:', (sig3 or {}).get('code_sha256'), (sig3 or {}).get('refusals'))
