import sys, subprocess, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def st(n, p):
    return subprocess.run(['git', 'show', ':' + str(n) + ':' + p], capture_output=True).stdout.decode('utf-8', errors='replace')

for p in ['results/compute_audit.json', 'results/token_usage.json']:
    for n in (2, 3):
        try:
            d = json.loads(st(n, p))
            if isinstance(d, dict):
                print(p, 'stage', n, 'dict keys', list(d.keys())[:16])
                if 'history' in d and isinstance(d['history'], list):
                    print('  hist len', len(d['history']), 'first ts', str(d['history'][0].get('ts'))[:22],
                          'last ts', str(d['history'][-1].get('ts'))[:22])
                else:
                    print('  sample', json.dumps(d, ensure_ascii=False)[:280])
            elif isinstance(d, list):
                print(p, 'stage', n, 'list len', len(d), 'first ts', str(d[0].get('ts'))[:22], 'last ts', str(d[-1].get('ts'))[:22])
        except Exception as e:
            print(p, n, 'ERR', repr(e)[:120])

# also count conflict-marker lines in working copies (sanity)
for p in ['results/compute_audit.json', 'results/token_usage.json']:
    raw = open(p, 'rb').read()
    print(p, 'workcopy markers', raw.count(b'<<<<<<<'), raw.count(b'>>>>>>>'), 'bytes', len(raw))
