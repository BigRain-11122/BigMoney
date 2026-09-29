import json
pf = json.load(open('results/_r237bmc_stdq90_w11_probe_facts.json', encoding='utf-8'))
out = {}
for k in ('extreme_day_states', 'adjacency', 'determinism_cross_checks',
          'core48_std20_open_rate', 'forward_20d', 'forward_5d',
          'drift_face_forward_20d', 'distinct_space_increment',
          'reverse_rates_inside_std20_pct', 'std20_open_rate_inside_pct',
          'warmup_disclosure'):
    out[k] = pf[k]
json.dump(out, open('results/_r442bmb_w11_anchor_parts.json', 'w', encoding='utf-8'),
          indent=1, ensure_ascii=False)
print('written; extreme days sample:')
print(json.dumps(pf['extreme_day_states']['2024-09-24'], indent=1))
print('adjacency:', json.dumps(pf['adjacency'], indent=0)[:600])
