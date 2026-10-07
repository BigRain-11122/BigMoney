# r674 bm-c pull-rebase resolve batch-2: 19 UU S6 twin faces per r802 per-face canon
#   - compute_audit.json : history union (dedupe (ts,machine), sort ts, latest=max-ts)
#   - token_usage.json   : per-key max (numeric max, string newer-wins)
#   - all other twins   : ts-duel (max embedded ISO-like timestamp wins; tie/no-ts -> stage2 origin per r440 S6-regenerable origin-newer-wins)
# receipt -> results/_r674bmc_pull_rebase_resolve.json
import sys, subprocess, json, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from datetime import datetime, timezone, timedelta

ISO = datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%dT%H:%M:%S+08:00')

FILES = [
    'docs/daily_report/REPORT-2026-10-07.json', 'docs/daily_report/REPORT-2026-10-07.md',
    'docs/live_usage/LIVE-2026-10-07.json', 'docs/live_usage/LIVE-2026-10-07.md',
    'docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md',
    'results/_attrition_guard_scan.json', 'results/compute_audit.json',
    'results/dashboard_status.js', 'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json', 'results/futures_update_status.json',
    'results/lhb_update_status.json', 'results/prospect_promotion/_summary.json',
    'results/regime_state.json', 'results/scorecard_v1.json',
    'results/strategy_scorecard.json', 'results/token_usage.json', 'results/update_status.json',
]
AUDIT = 'results/compute_audit.json'
TOKEN = 'results/token_usage.json'

def st(n, p):
    return subprocess.run(['git', 'show', ':' + str(n) + ':' + p], capture_output=True).stdout

TS_PAT = re.compile(r'20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?')

def max_ts(x):
    best = ''
    stack = [x]
    while stack:
        cur = stack.pop()
        if isinstance(cur, dict):
            stack.extend(cur.values())
        elif isinstance(cur, list):
            stack.extend(cur)
        elif isinstance(cur, str):
            for m in TS_PAT.finditer(cur):
                s = m.group(0).replace('T', ' ')
                if s > best:
                    best = s
    return best

def try_json(raw):
    try:
        return json.loads(raw.decode('utf-8', errors='replace'))
    except Exception:
        return None

receipt = {'round': 674, 'machine': 'bm-c', 'ts': ISO, 'canon': 'r802 per-face canon: ts-duel newer-wins (tie->origin st2) + audit history union + token per-key max', 'faces': {}}

# --- special 1: compute_audit history union ---
raw2, raw3 = st(2, AUDIT), st(3, AUDIT)
crlf = (b'\r\n' in raw2) or (b'\r\n' in raw3)
a2, a3 = try_json(raw2), try_json(raw3)
assert a2 is not None and a3 is not None
h2, h3 = a2.get('history', []), a3.get('history', [])
seen, union = set(), []
for e in h2 + h3:
    k = (str(e.get('ts')), str(e.get('machine')))
    if k not in seen:
        seen.add(k)
        union.append(e)
union.sort(key=lambda e: str(e.get('ts')))
merged = {'latest': (union[-1] if union else (a2.get('latest') or a3.get('latest'))), 'history': union}
s = json.dumps(merged, indent=1, ensure_ascii=False)
if crlf:
    s = s.replace('\n', '\r\n')
open(AUDIT, 'wb').write(s.encode('utf-8'))
json.loads(open(AUDIT, encoding='utf-8').read())
receipt['faces'][AUDIT] = {'mode': 'history-union', 'st2': len(h2), 'st3': len(h3), 'union': len(union)}

# --- special 2: token per-key max ---
t2, t3 = try_json(st(2, TOKEN)), try_json(st(3, TOKEN))
assert t2 is not None and t3 is not None

def per_key_max(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        out = {}
        for k in list(a.keys()) + [x for x in b.keys() if x not in a]:
            if k in a and k in b:
                out[k] = per_key_max(a[k], b[k])
            elif k in a:
                out[k] = a[k]
            else:
                out[k] = b[k]
        return out
    if isinstance(a, bool) or isinstance(b, bool):
        return b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return max(a, b)
    if isinstance(a, str) and isinstance(b, str):
        return a if a >= b else b
    return b if b is not None else a

mt = per_key_max(t2, t3)
s = json.dumps(mt, indent=1, ensure_ascii=False)
if b'\r\n' in st(2, TOKEN):
    s = s.replace('\n', '\r\n')
open(TOKEN, 'wb').write(s.encode('utf-8'))
json.loads(open(TOKEN, encoding='utf-8').read())
receipt['faces'][TOKEN] = {'mode': 'per-key-max', 'generated': mt.get('generated')}

# --- generic ts-duel for the rest ---
for p in FILES:
    if p in (AUDIT, TOKEN):
        continue
    r2, r3 = st(2, p), st(3, p)
    if r2 == r3:
        open(p, 'wb').write(r2)
        receipt['faces'][p] = {'mode': 'identical'}
        continue
    j2, j3 = try_json(r2), try_json(r3)
    ts2 = max_ts(j2 if j2 is not None else r2.decode('utf-8', errors='replace'))
    ts3 = max_ts(j3 if j3 is not None else r3.decode('utf-8', errors='replace'))
    if ts3 > ts2:
        win, mode, wraw = 3, 'ts-duel st3', r3
    else:
        win, mode, wraw = 2, 'ts-duel st2' if ts2 >= ts3 else 'ts-duel st2-fallback', r2
    open(p, 'wb').write(wraw)
    jj = try_json(wraw)
    if jj is not None:
        json.loads(open(p, encoding='utf-8').read())  # parse-back assert for json twins
    receipt['faces'][p] = {'mode': mode, 'ts2': ts2 or None, 'ts3': ts3 or None, 'winner': win}

json.dump(receipt, open('results/_r674bmc_pull_rebase_resolve.json', 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
print('RESOLVE2 OK:', len(receipt['faces']), 'faces / audit union', len(union), '/ token gen', mt.get('generated'))
for k, v in receipt['faces'].items():
    if v.get('mode') != 'identical':
        print(' ', k, v.get('mode'), 'ts2', v.get('ts2'), 'ts3', v.get('ts3'))
