import sys, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
r = json.load(open(r'results\perpetual_faces\n1_w100_results.json'))
print('null_pool_cumulative:', json.dumps(r['null_pool_cumulative'], ensure_ascii=False)[:500])
print('skill_line_v2_k_lift:', json.dumps(r['skill_line_v2_k_lift'], ensure_ascii=False)[:500])
print('families keys:', list(r.get('families', {}).keys())[:10])
fam = r.get('families', {})
for k, v in fam.items():
    s = json.dumps(v, ensure_ascii=False)
    print('fam %s: %s' % (k, s[:300]))
t = open(r'scripts\perpetual_faces.py', encoding='utf-8').read()
i = t.find('    105: {"a"')
print('--- pf.py W105 row + closing ---')
print(repr(t[i:i + 260]))
n = open(r'scripts\perpetual_faces_n1.py', encoding='utf-8').read()
k2 = n.find('r376 bm-c] "')
print('--- n1 summary W105 tail anchor ---')
print(repr(n[k2 - 120:k2 + 60]))
# a_p95 search across the results tree
def walk(o, path=''):
    if isinstance(o, dict):
        for kk, vv in o.items():
            if 'p95' in kk.lower():
                print('P95 %s%s = %s' % (path, kk, json.dumps(vv)[:120]))
            walk(vv, path + kk + '.')
walk(r)
