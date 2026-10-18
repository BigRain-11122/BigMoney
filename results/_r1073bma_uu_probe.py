import subprocess, json

def side(path, n):
    r = subprocess.run(['git', 'show', f':{n}:{path}'], capture_output=True)
    return r.stdout.decode('utf-8', 'replace') if r.returncode == 0 else None

paths = ['docs/daily_report/REPORT-2026-10-19.json','docs/daily_report/REPORT-2026-10-19.md',
         'results/compute_audit.json','results/fundamental_b_layer_filter.json','results/regime_state.json',
         'results/token_usage.json','results/update_status.json','results/watermark_red.json']

for p in paths:
    o, t = side(p, 2), side(p, 3)
    def probe(c, label):
        if c is None:
            return label + ':ABSENT'
        out = label + ':'
        try:
            d = json.loads(c)
            if isinstance(d, dict):
                for k in ('ts','generated_at','asof','machine','last_ts'):
                    if k in d:
                        out += str(k) + '=' + str(d[k]) + ','
                for hk in ('history','entries','records'):
                    if isinstance(d.get(hk), list):
                        out += hk + '_n=' + str(len(d[hk])) + ','
        except Exception:
            if p.endswith('.md'):
                out += 'attribution=' + ('YES' if ('归因' in c) else 'no') + ','
                i = c.find('2026-10-19T')
                out += 'tsl=' + (c[i:i+19] if i >= 0 else 'none')
        return out[:160]
    print(p[:55])
    print('  ours(orig):', probe(o, 'O'))
    print('  theirs(mine):', probe(t, 'T'))
