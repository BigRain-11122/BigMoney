import subprocess, json, io

def blob(stage, path):
    return subprocess.run(['git','show',stage+':'+path],capture_output=True).stdout

# 1) six newer-wins faces: take ours (stage :3:)
for f in ['results/futures_update_status.json','results/lhb_update_status.json',
          'results/regime_state.json','results/scorecard_v1.json',
          'results/strategy_scorecard.json','results/update_status.json']:
    b = blob(':3', f)
    with io.open(f,'wb') as fh:
        fh.write(b)
    print('ours-newer take:', f, len(b), 'bytes')

# 2) compute_audit.json: latest=ours newer; history=union dedupe ts-sorted tail 201
o = json.loads(blob(':2','results/compute_audit.json'))
t = json.loads(blob(':3','results/compute_audit.json'))
assert t['latest']['ts'] > o['latest']['ts'], (t['latest']['ts'], o['latest']['ts'])
merged = {'latest': t['latest'], 'history': None}
oh, th = o['history'], t['history']
seen = set()
rows = []
for r in oh + th:
    key = r.get('ts')
    if key in seen:
        continue
    seen.add(key)
    rows.append(r)
rows.sort(key=lambda r: r.get('ts',''))
merged['history'] = rows[-201:]
with io.open('results/compute_audit.json','w',encoding='utf-8',newline='\n') as fh:
    json.dump(merged, fh, ensure_ascii=False, indent=1)
print('compute_audit.json: latest=ours', t['latest']['ts'], 'history union rows=', len(merged['history']),
      '(origin', len(oh), '+ ours', len(th), '-> dedupe', len(rows), ')')
