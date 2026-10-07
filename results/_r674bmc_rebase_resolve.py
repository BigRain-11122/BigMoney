# r674 bm-c rebase resolve: 2 UU S6 twins per r802 bm-b canon
#   results/compute_audit.json -> history union (dedupe by (ts,machine), sort by ts; latest = max-ts entry)
#   results/token_usage.json   -> per-key max (numbers max; strings newer-wins lexicographic)
# receipt -> results/_r674bmc_rebase_resolve.json
import sys, subprocess, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from datetime import datetime, timezone, timedelta

ISO = datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%dT%H:%M:%S+08:00')

def st(n, p):
    return subprocess.run(['git', 'show', ':' + str(n) + ':' + p], capture_output=True).stdout

p_audit = 'results/compute_audit.json'
p_token = 'results/token_usage.json'

raw2, raw3 = st(2, p_audit), st(3, p_audit)
crlf = b'\r\n' in raw2 or b'\r\n' in raw3
a2 = json.loads(raw2.decode('utf-8'))
a3 = json.loads(raw3.decode('utf-8'))

h2, h3 = a2.get('history', []), a3.get('history', [])
seen, union = set(), []
for e in h2 + h3:
    k = (str(e.get('ts')), str(e.get('machine')))
    if k in seen:
        continue
    seen.add(k)
    union.append(e)
union.sort(key=lambda e: str(e.get('ts')))
latest = union[-1] if union else (a3.get('latest') or a2.get('latest'))
merged_audit = {'latest': latest, 'history': union}
s = json.dumps(merged_audit, indent=1, ensure_ascii=False)
if crlf:
    s = s.replace('\n', '\r\n')
open(p_audit, 'wb').write(s.encode('utf-8'))
json.loads(open(p_audit, encoding='utf-8').read())  # parse-back assert

t2 = json.loads(st(2, p_token).decode('utf-8'))
t3 = json.loads(st(3, p_token).decode('utf-8'))

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
        return a if a >= b else b  # newer-wins (ISO ts strings sort lexicographically)
    return b if b is not None else a

merged_token = per_key_max(t2, t3)
s = json.dumps(merged_token, indent=1, ensure_ascii=False)
raw_t2 = st(2, p_token)
if b'\r\n' in raw_t2:
    s = s.replace('\n', '\r\n')
open(p_token, 'wb').write(s.encode('utf-8'))
json.loads(open(p_token, encoding='utf-8').read())  # parse-back assert

receipt = {
    'round': 674, 'machine': 'bm-c', 'ts': ISO,
    'conflicts': [p_audit, p_token],
    'canon': 'r802 bm-b precedent: compute_audit history union (dedupe (ts,machine), sort ts, latest=max-ts) + token_usage per-key max (numeric max, string newer-wins)',
    'audit': {'stage2_hist_len': len(h2), 'stage3_hist_len': len(h3), 'union_len': len(union),
              'union_first_ts': str(union[0].get('ts')) if union else None,
              'union_last_ts': str(union[-1].get('ts')) if union else None,
              'latest_ts': str(latest.get('ts')) if isinstance(latest, dict) else None},
    'token': {'merged_keys': len(merged_token), 'generated': merged_token.get('generated'),
              'totals': {k: merged_token.get(k) for k in ('total_state_tokens_est', 'total_report_tokens_est')}},
    'law_refs': ['r620 churn absorb', 'r789 add+continue atomic', 'r802 S6 twins per-face canon', 'O-2100 s2.4 stale-takeover'],
}
json.dump(receipt, open('results/_r674bmc_rebase_resolve.json', 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
print('RESOLVE OK: audit union', len(h2), '+', len(h3), '->', len(union), '/ token merged', len(merged_token), 'keys / generated', merged_token.get('generated'))
