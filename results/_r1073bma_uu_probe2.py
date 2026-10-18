import subprocess, json

def side(path, n):
    r = subprocess.run(['git', 'show', f':{n}:{path}'], capture_output=True)
    return r.stdout.decode('utf-8', 'replace') if r.returncode == 0 else None

for p in ['results/token_usage.json', 'results/update_status.json', 'results/fundamental_b_layer_filter.json']:
    print('==', p)
    for n, lab in [(2, 'ours(orig)'), (3, 'theirs(mine)')]:
        c = side(p, n)
        if c is None:
            print(' ', lab, 'ABSENT'); continue
        try:
            d = json.loads(c)
            if isinstance(d, dict):
                print(' ', lab, 'keys:', list(d.keys())[:12])
                for k, v in d.items():
                    if isinstance(v, list):
                        print('   ', k, 'list_n=', len(v), 'tail=', json.dumps(v[-1], ensure_ascii=False)[:120] if v else '')
                    elif isinstance(v, (str, int, float)) and any(s in k.lower() for s in ('ts', 'time', 'date', 'updated', 'generated')):
                        print('   ', k, '=', v)
            else:
                print(' ', lab, 'type:', type(d).__name__)
        except Exception as e:
            print(' ', lab, 'parse-fail', str(e)[:60], 'len', len(c))
