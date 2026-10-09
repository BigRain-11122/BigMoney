# r940 dead-session rebase estate resolver (r813 salvage + r917 three-state + r794 history-union)
# Stage semantics in rebase window (r782): stage2 = onto/origin side, stage3 = replayed pick side (ours r939).
# Recipes: flat json status faces -> newest-ts side (verified S3 newer 03:55-04:00 vs S2 03:03-03:33);
#          .md faces -> stage3 bytes (r917 theirs-bytes dual-encoding probe);
#          compute_audit -> latest=newest + history content-hash union sorted by ts, keep last 201 (r794).
import subprocess, json, hashlib

GIT = r'C:\Program Files\Git\cmd\git.exe'
RECEIPT = r'results\_r940bma_rebase_resolver.json'

def cat(stage, path):
    r = subprocess.run([GIT, 'cat-file', '-p', ':%d:%s' % (stage, path)], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError('cat-file failed %s stage %d rc %d' % (path, stage, r.returncode))
    return r.stdout

def tsev(j):
    if not isinstance(j, dict):
        return {}
    return {k: j[k] for k in ('ts', 'updated', 'updated_at', 'generated', 'generated_at', 'last_run')
            if k in j and isinstance(j[k], str)}

S3_NEWEST = [
    'docs/daily_report/REPORT-2026-10-10.json',
    'docs/live_usage/LIVE-2026-10-10.json',
    'docs/live_usage/LIVE-latest.json',
    'results/_attrition_guard_scan.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/lhb_update_status.json',
    'results/regime_state.json',
    'results/token_usage.json',
    'results/update_status.json',
]
MD_S3 = [
    'docs/daily_report/REPORT-2026-10-10.md',
    'docs/live_usage/LIVE-2026-10-10.md',
    'docs/live_usage/LIVE-latest.md',
]
COMPUTE_AUDIT = 'results/compute_audit.json'

receipt = {'round': 'r940', 'law': 'r813 dead-session estate + r917 three-state + r794 union',
            'onto': '96caaa9c8', 'pick': '2fae1cd25', 'faces': {}}

for f in S3_NEWEST:
    b3 = cat(3, f)
    b2 = cat(2, f)
    j3 = json.loads(b3)
    j2 = json.loads(b2)
    open(f, 'wb').write(b3)
    receipt['faces'][f] = {'decision': 'take-stage3-newest', 's2_ts': tsev(j2), 's3_ts': tsev(j3)}

for f in MD_S3:
    b3 = cat(3, f)
    open(f, 'wb').write(b3)
    receipt['faces'][f] = {'decision': 'take-stage3-md-bytes (r917)', 'bytes': len(b3)}

b2 = cat(2, COMPUTE_AUDIT)
b3 = cat(3, COMPUTE_AUDIT)
j2 = json.loads(b2)
j3 = json.loads(b3)
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
open(COMPUTE_AUDIT, 'wb').write(txt.encode('utf-8'))
receipt['faces'][COMPUTE_AUDIT] = {
    'decision': 'history-union latest-newest',
    's2_latest_ts': j2['latest'].get('ts'), 's3_latest_ts': j3['latest'].get('ts'),
    's2_hist': len(j2.get('history', [])), 's3_hist': len(j3.get('history', [])),
    'union_unique': len(uniq), 'kept_last': len(merged_hist),
    's2_only_head': str(j2['history'][0].get('ts')) if j2.get('history') else None,
    's3_only_head': str(j3['history'][0].get('ts')) if j3.get('history') else None,
}

with open(RECEIPT, 'w', encoding='utf-8') as f:
    json.dump(receipt, f, indent=1, ensure_ascii=False)
print('RESOLVED', len(receipt['faces']), 'faces; compute_audit union', len(uniq), '->', len(merged_hist))
