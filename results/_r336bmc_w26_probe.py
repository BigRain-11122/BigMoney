# -*- coding: utf-8 -*-
# r336 bm-c: W26 finalize product field probe (A p95 / se_mu / K / evidence_cutoff / audit)
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

d = json.load(open(r'results\perpetual_faces\n1_w26_results.json', encoding='utf-8'))
print('TOP_KEYS', sorted(d.keys()))

def find(obj, pred, path=''):
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = path + '/' + str(k)
            if pred(k, v):
                out.append((p, v))
            out += find(v, pred, p)
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:2]):
            out += find(v, pred, path + '[%d]' % i)
    return out

KEYS = ('p95', 'p99', 'se_mu', 'evidence_cutoff', 'k_lift', 'klift', 'lift')
NAMES = ('K', 'mu', 'sigma', 'n_eff', 'batch', 'cutoff', 'machine', 'wave', 'nshards',
         'ledger', 'prev_total', 'total', 'skill_line', 'old', 'new', 'delta')
for p, v in find(d, lambda k, v: (any(x in str(k).lower() for x in KEYS) or str(k) in NAMES)
                                  and not isinstance(v, (dict, list))):
    print('FIELD', p, '=', str(v)[:220])
for p, v in find(d, lambda k, v: str(k).lower() in ('audit', 'skill_line_v2', 'k_lift', 'cutoff_meta')
                                  and isinstance(v, dict)):
    print('BLOCK', p, '=', json.dumps(v, ensure_ascii=False)[:500])
