# r660 bm-b: compute_audit.json line-level union fix (r658 law: zero-loss both sides contained)
import json, subprocess

def blob(rev, path):
    return subprocess.run(['git', 'show', f'{rev}:{path}'], capture_output=True).stdout

o = json.loads(blob('HEAD', 'results/compute_audit.json'))
t = json.loads(blob('MERGE_HEAD', 'results/compute_audit.json'))

def canon(row):
    return json.dumps(row, sort_keys=True, ensure_ascii=False)

# union history by (ts, canonical) identity; preserve chronological order by ts
seen = set()
union = []
for row in sorted(o['history'] + t['history'], key=lambda r: str(r.get('ts', ''))):
    k = (str(row.get('ts', '')), canon(row))
    if k in seen:
        continue
    seen.add(k)
    union.append(row)

# containment proof (r656 law): 0 rows lost from either side
o_set = {(str(r.get('ts', '')), canon(r)) for r in o['history']}
t_set = {(str(r.get('ts', '')), canon(r)) for r in t['history']}
u_set = {(str(r.get('ts', '')), canon(r)) for r in union}
lost_o = len(o_set - u_set)
lost_t = len(t_set - u_set)
assert lost_o == 0 and lost_t == 0, f'LOSS o={lost_o} t={lost_t}'

# latest = fresher ts side
lo, lt = str(o['latest'].get('ts', '')), str(t['latest'].get('ts', ''))
latest = o['latest'] if lo >= lt else t['latest']
merged = {'latest': latest, 'history': union}
out = json.dumps(merged, ensure_ascii=False, indent=1).encode('utf-8')
with open('results/compute_audit.json', 'wb') as f:
    f.write(out)
print(f'compute_audit union: ours={len(o["history"])} theirs={len(t["history"])} -> union={len(union)} '
      f'(zero-loss o=0 t=0) latest_ts={latest.get("ts")} ({"ours" if lo >= lt else "theirs"})')
