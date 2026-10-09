# r940 rebase round-2 resolver (second rebase onto 520e190b1)
# Dynamic face list from ls-files -u; recipes: json -> newest-ts side (fallback stage3),
# md -> stage3 bytes (r917), compute_audit -> latest-newest + history hash-union keep last 201 (r794).
import subprocess, json, hashlib

GIT = r'C:\Program Files\Git\cmd\git.exe'
RECEIPT = r'results\_r940bma_rebase_resolver2.json'

def git_out(args):
    r = subprocess.run([GIT] + args, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError('git %s rc=%d %s' % (' '.join(args), r.returncode, r.stderr[:200]))
    return r.stdout

def cat(stage, path):
    return git_out(['cat-file', '-p', ':%d:%s' % (stage, path)])

def tsev(j):
    if not isinstance(j, dict):
        return {}
    return {k: j[k] for k in ('ts', 'updated', 'updated_at', 'generated', 'generated_at', 'last_run')
            if k in j and isinstance(j[k], str)}

uu_raw = git_out(['ls-files', '-u']).decode('utf-8', 'replace')
faces = []
for line in uu_raw.strip().split('\n'):
    if line.strip():
        p = line.split('\t')[1]
        if p not in faces:
            faces.append(p)

receipt = {'round': 'r940', 'stage': 'rebase-2 onto 520e190b1', 'pick': '7188a3321', 'faces': {}}

for f in faces:
    b2 = cat(2, f)
    b3 = cat(3, f)
    if f.endswith('.md'):
        open(f, 'wb').write(b3)
        receipt['faces'][f] = {'decision': 'take-stage3-md-bytes (r917)', 'bytes': len(b3)}
        continue
    j2 = json.loads(b2)
    j3 = json.loads(b3)
    if f == 'results/compute_audit.json':
        seen = {}
        order = []
        for e in list(j2.get('history', [])) + list(j3.get('history', [])):
            h = hashlib.sha256(json.dumps(e, sort_keys=True, ensure_ascii=False).encode('utf-8')).hexdigest()
            if h not in seen:
                seen[h] = e
                order.append(h)
        uniq = [seen[h] for h in order]
        uniq.sort(key=lambda e: str(e.get('ts', '')))
        merged_hist = uniq[-201:]
        latest = j3['latest'] if str(j3['latest'].get('ts', '')) >= str(j2['latest'].get('ts', '')) else j2['latest']
        payload = dict(j3)
        payload['latest'] = latest
        payload['history'] = merged_hist
        txt = json.dumps(payload, indent=2, ensure_ascii=False)
        if b'\r\n' in b3:
            txt = txt.replace('\n', '\r\n')
        open(f, 'wb').write(txt.encode('utf-8'))
        receipt['faces'][f] = {
            'decision': 'history-union latest-newest',
            's2_latest_ts': j2['latest'].get('ts'), 's3_latest_ts': j3['latest'].get('ts'),
            's2_hist': len(j2.get('history', [])), 's3_hist': len(j3.get('history', [])),
            'union_unique': len(uniq), 'kept_last': len(merged_hist),
        }
        continue
    e2 = tsev(j2)
    e3 = tsev(j3)
    v2 = list(e2.values())[0] if e2 else ''
    v3 = list(e3.values())[0] if e3 else ''
    if v3 and (not v2 or v3 >= v2):
        winner = 'stage3'
    elif v2 and (not v3 or v2 > v3):
        winner = 'stage2'
    else:
        winner = 'stage3'
    open(f, 'wb').write(b3 if winner == 'stage3' else b2)
    receipt['faces'][f] = {'decision': 'take-%s-newest-ts' % winner, 's2_ts': e2, 's3_ts': e3}

with open(RECEIPT, 'w', encoding='utf-8') as f:
    json.dump(receipt, f, indent=1, ensure_ascii=False)
for f, d in receipt['faces'].items():
    print(f, '->', d.get('decision'))
print('RESOLVED round-2:', len(receipt['faces']), 'faces')
