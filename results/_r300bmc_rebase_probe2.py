import json, subprocess, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def j(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    return json.loads(r.stdout.decode('utf-8'))

# 1) REPORT rd/token_line/utilization
r2, r3 = j(2, 'docs/daily_report/REPORT-2026-10-01.json'), j(3, 'docs/daily_report/REPORT-2026-10-01.json')
print('REPORT rd:', r2.get('rd'), 'vs', r3.get('rd'))
print('REPORT token_line:', json.dumps(r2.get('token_line'), ensure_ascii=False)[:160], '||', json.dumps(r3.get('token_line'), ensure_ascii=False)[:160])
u2, u3 = r2.get('utilization', {}), r3.get('utilization', {})
print('REPORT utilization keys:', list(u2.keys()), 'vs', list(u3.keys()))
print('  u2:', json.dumps(u2, ensure_ascii=False)[:200])
print('  u3:', json.dumps(u3, ensure_ascii=False)[:200])

# 2) compute_audit latest/history
c2, c3 = j(2, 'results/compute_audit.json'), j(3, 'results/compute_audit.json')
print('compute_audit latest ts:', c2['latest'].get('ts'), '(origin) vs', c3['latest'].get('ts'), '(mine)')
h2, h3 = c2.get('history', []), c3.get('history', [])
print('history lens:', len(h2), len(h3), '| tail ids equal:', [h.get('ts') for h in h2[-2:]], [h.get('ts') for h in h3[-2:]])

# 3) dashboard_status events/fleet
d2, d3 = j(2, 'results/dashboard_status.json'), j(3, 'results/dashboard_status.json')
e2, e3 = d2.get('events', []), d3.get('events', [])
print('dashboard events lens:', len(e2), len(e3), '| fleet keys:', list(d2.get('fleet', {}).keys())[:5], 'vs', list(d3.get('fleet', {}).keys())[:5])

# 4) token_usage machines
t2, t3 = j(2, 'results/token_usage.json'), j(3, 'results/token_usage.json')
print('token machines:', list(t2.get('machines', {}).keys()), 'vs', list(t3.get('machines', {}).keys()))
print('token generated:', t2.get('generated'), 'vs', t3.get('generated'))
pr2, pr3 = t2.get('per_round_context', {}), t3.get('per_round_context', {})
print('per_round_context keys:', list(pr2.keys())[-3:], 'vs', list(pr3.keys())[-3:])
