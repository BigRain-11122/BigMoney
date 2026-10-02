import sys, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
t = open(r'scripts\perpetual_faces.py', encoding='utf-8').read()
i = t.find('    104: ')
print('--- pf.py W104/W105 rows + closing ---')
print(repr(t[i:i + 420]))
n = open(r'scripts\perpetual_faces_n1.py', encoding='utf-8').read()
j = n.find('105: {"batch"')
seg = n[j:j + 3000]
print('--- n1 W105 config entry (tail 600) ---')
print(repr(seg[-600:]))
k = n.find('law sec.4 W105 row')
print('--- n1 summary W105 segment tail ---')
print(repr(n[k - 300:k + 130]))
r = json.load(open(r'results\perpetual_faces\n1_w100_results.json'))
print('--- W100 top-level scalar keys ---')
for kk, vv in r.items():
    if not isinstance(vv, (list, dict)):
        print('  %s = %r' % (kk, vv))
print('--- nested dict keys ---', list(r.keys()))
for key in ('skill_line', 'skill_line_v2', 'merged', 'w100', 'batch', 'a_p95',
            'a_sharpe_p95', 'p95', 'a_stats'):
    if key in r:
        print('%s: %s' % (key, json.dumps(r[key], ensure_ascii=False)[:400]))
