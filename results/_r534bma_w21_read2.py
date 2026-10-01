import json
d = json.load(open(r'results\perpetual_faces\n1_w21_results.json', encoding='utf-8'))
print('TOP KEYS:', list(d.keys()))
def walk(o, pre=''):
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, (dict, list)):
                walk(v, pre + k + '.')
            else:
                if any(t in k.lower() for t in ('mu', 'sigma', 'p95', 'p99', 'se_', 'k', 'n_values', 'count', 'lift', 'prev', 'line')):
                    print(pre + k, '=', v)
    elif isinstance(o, list):
        pass
walk(d)
