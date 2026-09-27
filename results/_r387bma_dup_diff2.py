import json
a = json.load(open('results/trial_labor_w2/w2_candidates.json', encoding='utf-8'))
b = json.load(open('results/trial_labor_w2/w2_candidates.json.live-bma-dup', encoding='utf-8'))
ca = a['candidates']; cb = b['candidates']
print('list order identical:', [json.dumps(c, sort_keys=True) for c in ca[:50]] == [json.dumps(c, sort_keys=True) for c in cb[:50]])
# key-by-key top-level compare
for k in sorted(set(a) | set(b)):
    va, vb = a.get(k), b.get(k)
    if k == 'generated':
        print(k, ':', va, 'vs', vb); continue
    same = json.dumps(va, sort_keys=True) == json.dumps(vb, sort_keys=True)
    print(k, 'equal=', same)
    if not same and isinstance(va, dict) and isinstance(vb, dict):
        for k2 in sorted(set(va) | set(vb)):
            s2 = json.dumps(va.get(k2), sort_keys=True) == json.dumps(vb.get(k2), sort_keys=True)
            if not s2:
                print('   sub', k2, 'equal=', False, 'canon=', str(va.get(k2))[:100], 'dup=', str(vb.get(k2))[:100])
# per-candidate field-level: find first candidate differing
for i, (x, y) in enumerate(zip(ca, cb)):
    if json.dumps(x, sort_keys=True) != json.dumps(y, sort_keys=True):
        print('first differing candidate at idx', i)
        for k2 in sorted(set(x) | set(y)):
            if json.dumps(x.get(k2), sort_keys=True) != json.dumps(y.get(k2), sort_keys=True):
                print('   field', k2, 'canon=', str(x.get(k2))[:80], '| dup=', str(y.get(k2))[:80])
        break
else:
    print('all zipped candidates byte-equal (semantically)')
