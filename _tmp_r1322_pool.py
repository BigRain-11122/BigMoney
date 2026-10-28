import json, subprocess

def stage(n):
    p = subprocess.run(['git','show',f':{n}:results/runnable_pool.json'], capture_output=True)
    return json.loads(p.stdout.decode('utf-8'))

base, ours, theirs = stage(1), stage(2), stage(3)

def keyed(d):
    return {e.get('id') or e.get('job_id') or json.dumps(e, sort_keys=True): e for e in d['entries']}

kb, ko, kt = keyed(base), keyed(ours), keyed(theirs)
print('base', len(kb), 'ours', len(ko), 'theirs', len(kt))
print('only in ours:', sorted(set(ko) - set(kt)))
print('only in theirs:', sorted(set(kt) - set(ko)))
diff = [k for k in set(ko) & set(kt) if ko[k] != kt[k]]
print('differing shared entries:', diff)
for k in diff:
    print('  ', k)
    print('    ours  :', json.dumps(ko[k], ensure_ascii=False, sort_keys=True)[:400])
    print('    theirs:', json.dumps(kt[k], ensure_ascii=False, sort_keys=True)[:400])