import subprocess, json, difflib

def blob(spec):
    return subprocess.check_output(['git', 'show', spec], cwd='.')

def j(spec):
    return json.loads(blob(spec).decode('utf-8'))

print('== 1. runner script stage diff (origin :2: vs local-pick :3:) ==')
r2 = blob(':2:scripts/perpetual_faces_n1.py').decode('utf-8')
r3 = blob(':3:scripts/perpetual_faces_n1.py').decode('utf-8')
d = list(difflib.unified_diff(r2.splitlines(), r3.splitlines(), lineterm='', n=0))
print('diff lines total:', len(d))
print('\n'.join(d[:100]))

print()
print('== 2. compute_audit.json format+keys ==')
for spec in (':2:results/compute_audit.json', ':3:results/compute_audit.json'):
    raw = blob(spec)
    head = raw[:120].decode('utf-8', 'replace')
    doc = json.loads(raw.decode('utf-8'))
    print(spec, '| head repr:', repr(head[:80]))
    print(spec, '| keys:', sorted(doc.keys())[:14])
    hist = doc.get('history') or doc.get('snapshots') or []
    print(spec, '| history len:', len(hist) if isinstance(hist, list) else type(hist).__name__)

print()
print('== 3. runnable_pool.json both sides ==')
for spec in (':2:results/runnable_pool.json', ':3:results/runnable_pool.json'):
    raw = blob(spec)
    doc = json.loads(raw.decode('utf-8'))
    ents = doc.get('entries', [])
    print(spec, '| indent head:', repr(raw[:60].decode('utf-8')), '| entries:', len(ents))
    w3 = [e for e in ents if 'N1-W3' in str(e.get('batch_id') or e.get('id') or '')]
    w4 = [e for e in ents if 'N1-W4' in str(e.get('batch_id') or e.get('id') or '')]
    print('   N1-W3 entries:', len(w3), 'N1-W4 entries:', len(w4))

print()
print('== 4. perpetual_faces_state.json both sides ==')
for spec in (':2:results/perpetual_faces_state.json', ':3:results/perpetual_faces_state.json'):
    doc = j(spec)
    print(spec, '| keys:', sorted(doc.keys()))
    l = doc.get('launches', [])
    print('   launches:', len(l) if isinstance(l, list) else 'dict:' + str(len(l)))
    lt = doc.get('last_tick')
    print('   last_tick ts:', lt.get('ts') if isinstance(lt, dict) else lt)

print()
print('== 5. shard product twin check (shard-1) ==')
for spec in (':2:results/p2cal_ext/n1_w3/shard-1-of-12.json', ':3:results/p2cal_ext/n1_w3/shard-1-of-12.json'):
    doc = j(spec)
    print(spec, '| keys:', sorted(doc.keys()))
    for k in ('machine', 'elapsed_sec', 'workers', 'generated', 'generated_at', 'ts'):
        if k in doc:
            print('   ', k, '=', doc[k])

print()
print('== 6. n1_w3_results.json twin check ==')
for spec in (':2:results/perpetual_faces/n1_w3_results.json', ':3:results/perpetual_faces/n1_w3_results.json'):
    doc = j(spec)
    print(spec, '| keys:', sorted(doc.keys()))
    for k in ('mu', 'sigma', 'se_mu', 'K', 'k', 'n_eff'):
        if k in doc:
            print('   ', k, '=', doc[k])

print()
print('== 7. snapshot ts compare ==')
for path in [
    'results/futures_update_status.json',
    'results/lhb_update_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/token_usage.json',
    'results/update_status.json',
    'results/dashboard_status.json',
]:
    try:
        d2 = j(':2:' + path)
        d3 = j(':3:' + path)
    except Exception as e:
        print(path, '| parse fail:', e)
        continue
    def pick_ts(d):
        for k in ('updated', 'updated_at', 'generated', 'generated_at', 'ts', 'asof', 'cutoff'):
            if isinstance(d, dict) and k in d:
                return k + '=' + str(d[k])
        return 'no-ts-key'
    print(path, '| :2:', pick_ts(d2), '| :3:', pick_ts(d3))

print()
print('== 8. regime_state history lens ==')
for spec in (':2:results/regime_state.json', ':3:results/regime_state.json'):
    doc = j(spec)
    print(spec, '| keys:', sorted(doc.keys()))
    for k in ('history', 'transitions'):
        v = doc.get(k)
        print('   ', k, 'len:', len(v) if isinstance(v, (list, dict)) else v)
