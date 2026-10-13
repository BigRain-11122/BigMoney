import json, subprocess

def show(rev, path):
    r = subprocess.run(['git', 'show', f'{rev}:{path}'], capture_output=True)
    return json.loads(r.stdout.decode('utf-8', errors='replace'))

# ---------- compute_audit.json: history union-by-key + latest newer-ts ----------
theirs = show('5036a2f07', 'results/compute_audit.json')
mine = show('dbb9af2ab', 'results/compute_audit.json')

th_hist = theirs.get('history', [])
mi_hist = mine.get('history', [])
print('audit history: theirs', len(th_hist), 'mine', len(mi_hist))
print('audit latest ts theirs:', theirs['latest'].get('ts'), '| mine:', mine['latest'].get('ts'))

# union histories by (ts, machine) identity key
seen = {}
for e in th_hist + mi_hist:
    k = (e.get('ts'), e.get('machine', e.get('machine_id', '?')))
    if k not in seen:
        seen[k] = e
merged_hist = sorted(seen.values(), key=lambda e: e.get('ts', ''))
print('merged history len:', len(merged_hist))

latest = mine['latest'] if (mine['latest'].get('ts', '') >= theirs['latest'].get('ts', '')) else theirs['latest']
merged_audit = {'latest': latest, 'history': merged_hist}
# preserve any other top keys from the newer side
for k in theirs:
    if k not in ('latest', 'history') and k not in merged_audit:
        merged_audit[k] = theirs[k]
for k in mine:
    if k not in ('latest', 'history'):
        merged_audit[k] = mine[k]
json.dump(merged_audit, open('results/compute_audit.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('compute_audit.json merged + written')

# ---------- token_usage.json: machines mirror union + top newer-wins ----------
tt = show('5036a2f07', 'results/token_usage.json')
tm = show('dbb9af2ab', 'results/token_usage.json')
print('token generated theirs:', tt.get('generated'), '| mine:', tm.get('generated'))

# base = the NEWER generated side (mine 06:11 vs theirs 05:49), overlay machines union
base = tm if str(tm.get('generated', '')) >= str(tt.get('generated', '')) else tt
other = tt if base is tm else tm

machines = {}
# per-machine key: newer generated timestamp inside the mirror face wins
for mkey in set(list(base.get('machines', {})) + list(other.get('machines', {}))):
    b = base.get('machines', {}).get(mkey)
    o = other.get('machines', {}).get(mkey)
    if b is None:
        machines[mkey] = o
    elif o is None:
        machines[mkey] = b
    else:
        machines[mkey] = b if str(b.get('generated', b.get('ts', ''))) >= str(o.get('generated', o.get('ts', ''))) else o

merged_token = dict(base)
merged_token['machines'] = machines
# l2_local_llm union if dict-of-machines
if isinstance(base.get('l2_local_llm'), dict) and isinstance(other.get('l2_local_llm'), dict):
    l2 = dict(other.get('l2_local_llm', {}))
    l2.update(base.get('l2_local_llm', {}))
    merged_token['l2_local_llm'] = l2
json.dump(merged_token, open('results/token_usage.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('token_usage.json merged + written; machines keys:', sorted(machines)[:6])
