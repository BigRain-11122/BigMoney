import json, re
d = json.load(open('results/perpetual_faces/n1_w205_results.json', encoding='utf-8'))
s = json.dumps(d)
print('p95 hits:', re.findall(r'"[a-z0-9_]*p95[a-z0-9_]*":\s*[0-9.\-]+', s)[:12])
print('top keys:', sorted(d.keys()))
w = json.load(open('results/perpetual_faces/n1_w204_results.json', encoding='utf-8'))
sw = json.dumps(w)
print('W204 p95 hits:', re.findall(r'"[a-z0-9_]*p95[a-z0-9_]*":\s*[0-9.\-]+', sw)[:12])
