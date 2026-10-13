# _r974bma_resolve.py -- S0 rebase conflict resolver (canon: skill bigmoney-conflict-resolve)
# 3 UU faces: attrition scan (newer-ts take), token_usage (newer generated take),
# compute_audit (union history + newer-latest per r962/r957 canon).
import io, json, re

ROOT = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney'

def read(p):
    return io.open(p, encoding='utf-8', errors='replace').read()

def blocks(c):
    out = []
    for m in re.finditer(r'<<<<<<< HEAD\r?\n(.*?)\r?\n=======\r?\n(.*?)\r?\n>>>>>>> [^\r\n]*', c, re.S):
        out.append((m.start(), m.end(), m.group(1), m.group(2)))
    return out

def take_mine(path):
    c = read(path)
    n = 0
    for s, e, h, t in reversed(blocks(c)):
        c = c[:s] + t + c[e:]
        n += 1
    io.open(path, 'w', encoding='utf-8', newline='').write(c)
    json.loads(read(path))  # parse check
    print(f'{path}: take-MINE x{n} parse-OK')

def resolve_attrition():
    take_mine(ROOT + r'\results\_attrition_guard_scan.json')

def resolve_token():
    take_mine(ROOT + r'\results\token_usage.json')

def resolve_compute_audit():
    p = ROOT + r'\results\compute_audit.json'
    c = read(p)
    bs = blocks(c)
    assert len(bs) == 1, f'expected 1 block got {len(bs)}'
    s, e, h, t = bs[0]
    H = json.loads('{' + h + '}')
    T = json.loads('{' + t + '}')
    # canon: newer latest wins
    newer = T if T['latest']['ts'] >= H['latest']['ts'] else H
    older = H if newer is T else T
    merged = {'latest': newer['latest']}
    # canon: history union by ts, sorted
    hh = {r.get('ts'): r for r in older.get('history', [])}
    for r in newer.get('history', []):
        hh.setdefault(r.get('ts'), r)
    merged['history'] = [hh[k] for k in sorted(hh, key=lambda x: (x is None, x))]
    merged['history_union_note'] = 'r974 S0 rebase union: rows %d+%d -> %d' % (
        len(older.get('history', [])), len(newer.get('history', [])), len(merged['history']))
    io.open(p, 'w', encoding='utf-8', newline='').write(json.dumps(merged, indent=1, ensure_ascii=False) + '\n')
    json.loads(read(p))
    print(f"compute_audit: latest={merged['latest']['ts']} union history {len(merged['history'])} rows parse-OK")

resolve_attrition()
resolve_token()
resolve_compute_audit()
print('ALL RESOLVED')
