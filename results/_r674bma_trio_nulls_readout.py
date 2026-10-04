# r674 bm-a: fund trio NULLS live progress readout (planned r673 next pointer)
import json, os

out = {'ts': None}
fams = {'VALUE': 'results/fund_value_p1/nulls.jsonl',
        'QUALITY': 'results/fund_quality_p1/nulls.jsonl',
        'DIVLOWVOL': 'results/fund_divlowvol_p1/nulls.jsonl'}
import datetime
out['ts'] = datetime.datetime.now().isoformat(timespec='seconds') + '+08:00'
for name, p in fams.items():
    if not os.path.exists(p):
        out[name] = {'exists': False}; continue
    n = 0; last_key = None
    with open(p, 'rb') as f:
        for line in f:
            if line.strip(): n += 1
            last_key = line
    out[name] = {'exists': True, 'lines': n, 'target': 2000,
                 'pct': round(n / 2000 * 100, 1),
                 'last_line_head': last_key[:80].decode('utf-8', 'replace') if last_key else None}
open('results/_r674bma_trio_nulls_readout.json', 'wb').write(json.dumps(out, ensure_ascii=False, indent=1).encode('utf-8'))
print(json.dumps(out, ensure_ascii=False)[:800])
