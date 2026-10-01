import json
d = json.load(open(r'results\perpetual_faces\n1_w21_results.json', encoding='utf-8'))
for k in ('batch', 'K', 'n_values', 'mu', 'sigma', 'se_mu', 'p95', 'p99'):
    if k in d: print(k, '=', d[k])
# nested faces
for key in d:
    if isinstance(d[key], dict):
        print('--', key, ':', {kk: d[key][kk] for kk in list(d[key])[:8]})
        break
a = d.get('family_a') or d.get('A') or {}
print('A keys sample:', {k: a[k] for k in list(a)[:10]} if a else 'n/a')
sl = d.get('skill_line') or d.get('skill_line_v2') or {}
print('skill_line:', sl)
led = d.get('ledger') or {}
print('ledger:', led)
aud = d.get('audit') or {}
print('audit:', {k: aud[k] for k in list(aud)[:8]})
