import io, sys, json, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def stage(stage_id, path):
    b = subprocess.run(['git', 'show', '%s:%s' % (stage_id, path)], capture_output=True).stdout
    return json.loads(b.decode('utf-8-sig'))

for p in ['results/_attrition_guard_scan.json', 'results/compute_audit.json', 'results/token_usage.json']:
    print('=' * 20, p)
    for sid, name in [(':2', 'OURS(bm-a r452)'), (':3', 'THEIRS(r246 bm-c)')]:
        try:
            d = stage(sid, p)
            keys = list(d.keys()) if isinstance(d, dict) else 'LIST len=%d' % len(d)
            print(name, 'keys:', keys)
            for k, v in (d.items() if isinstance(d, dict) else []):
                if isinstance(v, list):
                    print('   %s: list len=%d, tail-item-keys=%s' % (k, len(v), list(v[-1].keys())[:8] if v and isinstance(v[-1], dict) else (v[-1] if v else None)))
                elif isinstance(v, dict):
                    print('   %s: dict keys=%s' % (k, list(v.keys())[:10]))
                else:
                    print('   %s: %r' % (k, v))
        except Exception as ex:
            print(name, 'ERR', ex)
