import json, io, glob

bad = []
for pat in ['docs/daily_report/REPORT-2026-10-07.json','docs/daily_report/REPORT-2026-10-07.md',
            'docs/live_usage/LIVE-2026-10-07.json','docs/live_usage/LIVE-2026-10-07.md',
            'docs/live_usage/LIVE-latest.json','docs/live_usage/LIVE-latest.md',
            'results/dashboard_status.js','results/dashboard_status.json',
            'results/fundamental_b_layer_filter.json','results/fund_divlowvol_p1/nulls.jsonl',
            'results/saturation_engine/history_bm-b.jsonl','results/token_usage.json']:
    raw = io.open(pat, encoding='utf-8', errors='replace').read()
    has_marker = ('<<<<<<<' in raw) or ('>>>>>>>' in raw) or ('\n=======' in raw)
    if has_marker:
        bad.append(('MARKER', pat))
    if pat.endswith('.json'):
        try:
            json.loads(raw)
        except Exception as e:
            bad.append(('BADJSON', pat, str(e)[:60]))

# nulls.jsonl duplicate cell-key check
rows = [json.loads(s) for s in io.open('results/fund_divlowvol_p1/nulls.jsonl',encoding='utf-8',errors='replace') if s.strip()]
print('nulls rows:', len(rows))
print('nulls row keys:', list(rows[0])[:10] if rows else 'none')
keys = {}
for r in rows:
    k = json.dumps({kk: r[kk] for kk in r if kk not in ('ann','sharpe','mdd','ret','stats','result','curve','daily','path')}, sort_keys=True)
    keys.setdefault(k, 0)
    keys[k] += 1
dups = {k: v for k, v in keys.items() if v > 1}
print('dup cell keys:', len(dups))
for k in list(dups)[:2]:
    print('  DUP:', k[:200])
print('token_usage keys:', list(json.load(io.open('results/token_usage.json',encoding='utf-8'))))
print('BAD:', bad if bad else 'NONE')
