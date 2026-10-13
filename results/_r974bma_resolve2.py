# _r974bma_resolve2.py -- blob-face resolver for rebase conflicts (HEAD vs REBASE_HEAD)
# canon: attrition/token = newer full-doc take; compute_audit = newer latest + history union
import subprocess, json, io, sys

def blob(ref, path):
    b = subprocess.run(['git', 'show', ref + ':' + path], capture_output=True).stdout
    return json.loads(b.decode('utf-8'))

def write(path, obj):
    io.open(path, 'w', encoding='utf-8', newline='').write(json.dumps(obj, indent=1, ensure_ascii=False) + '\n')
    json.loads(io.open(path, encoding='utf-8').read())

def resolve_newer(path, ts_key):
    h = blob('HEAD', path)
    t = blob('REBASE_HEAD', path)
    def ts(d):
        return d[ts_key] if ts_key in d else d.get('latest', {}).get('ts', '')
    newer = t if ts(t) >= ts(h) else h
    write(path, newer)
    print(f'{path}: HEAD {ts(h)} vs REBASE {ts(t)} -> take {"REBASE" if newer is t else "HEAD"}')

def resolve_audit(path):
    h = blob('HEAD', path)
    t = blob('REBASE_HEAD', path)
    newer, older = (t, h) if t['latest']['ts'] >= h['latest']['ts'] else (h, t)
    hh = {r.get('ts'): r for r in older.get('history', [])}
    for r in newer.get('history', []):
        hh.setdefault(r.get('ts'), r)
    merged = {'latest': newer['latest'],
              'history': [hh[k] for k in sorted(hh, key=lambda x: (x is None, x))]}
    merged['history_union_note'] = 'r974 S0 rebase-2 union: rows %d+%d -> %d' % (
        len(older.get('history', [])), len(newer.get('history', [])), len(merged['history']))
    write(path, merged)
    print(f"{path}: latest={merged['latest']['ts']} {merged['history_union_note']}")

resolve_newer('results/_attrition_guard_scan.json', 'ts')
resolve_newer('results/token_usage.json', 'generated')
resolve_audit('results/compute_audit.json')
print('RESOLVE2 DONE')
