import json, os

tmp = os.environ.get('TEMP', r'C:\Users\Dasheng\AppData\Local\Temp')
a = json.load(open(os.path.join(tmp, 'ca_ours.json'), encoding='utf-8'))
b = json.load(open(os.path.join(tmp, 'ca_theirs.json'), encoding='utf-8'))
A, B = a['history'], b['history']
ma = {r['ts']: r for r in A}
mb = {r['ts']: r for r in B}
overlap = set(ma) & set(mb)
diverge = [ts for ts in overlap if ma[ts] != mb[ts]]
assert not diverge, 'same-ts-diverge nonzero: %r' % diverge
union_ts = sorted(set(ma) | set(mb))
rows = [ma[ts] if ts in ma else mb[ts] for ts in union_ts]
latest = b['latest'] if b['latest']['ts'] > a['latest']['ts'] else a['latest']
merged = {'history': rows, 'latest': latest}
assert len(rows) == len(union_ts)
out = json.dumps(merged, ensure_ascii=False, indent=1)
with open('results/compute_audit.json', 'w', encoding='utf-8', newline='\n') as f:
    f.write(out + '\n')
print('union rows: %d|%d -> %d overlap=%d diverge=0 latest.ts=%s (fresher side taken)' % (
    len(ma), len(mb), len(rows), len(overlap), latest['ts']))
d = json.load(open('results/compute_audit.json', encoding='utf-8'))
assert len(d['history']) == len(rows) and d['latest'] == latest
print('re-parse-ok rows=%d latest=%s' % (len(d['history']), d['latest']['ts']))
