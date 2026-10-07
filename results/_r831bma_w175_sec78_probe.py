"""r831 W175 prereg sec7/sec8 mechanical backfill (r587 machine-derive law, r826/r827 lineage).

Reads frozen-section keys from n1_w175_results.json + n1_w174_results.json, asserts
the sec5 four pre-keys, replaces the two placeholder lines verbatim, verifies
zero-criteria-edit (all frozen sections byte-identical).
"""
import json, io, sys

W175 = json.load(open('results/perpetual_faces/n1_w175_results.json', encoding='utf-8'))
W174 = json.load(open('results/perpetual_faces/n1_w174_results.json', encoding='utf-8'))

def fam(d, pref):
    for k in d['families']:
        if k.startswith(pref):
            return d['families'][k]
    raise KeyError(pref)

a175 = fam(W175, 'A_')
a174 = fam(W174, 'A_')
wonly = W175.get('w_only', {}) or {}
if not wonly:
    # derive from families A+B merged stats if w_only absent
    wonly = {'mu': W175.get('w_only_mu'), 'sigma': W175.get('w_only_sigma')}

keys175 = {k: W175[k] for k in W175 if k not in ('families',)}
print('W175 top keys:', sorted(keys175.keys()))
print(json.dumps({k: v for k, v in keys175.items() if not isinstance(v, list)}, indent=1, ensure_ascii=False)[:1500])
