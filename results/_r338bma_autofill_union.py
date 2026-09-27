import subprocess
import json


def show(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    assert r.returncode == 0, f'show :{stage}: rc={r.returncode}'
    return r.stdout


p = 'results/autofill_state.json'
base = show(1, p)
s2 = show(2, p)
eol = '\r\n' if b'\r\n' in s2 else '\n'
indent = 1
for line in s2.decode('utf-8', errors='replace').split(eol):
    if line.startswith(' '):
        indent = len(line) - len(line.lstrip(' '))
        break
a = json.loads(s2.decode('utf-8'))
b = json.loads(show(3, p).decode('utf-8'))


def key(x):
    return (x.get('ts'), x.get('machine'), x.get('pid'), x.get('runner_sha256'), x.get('entry'), x.get('shard'))


seen = {}
merged = []
for e in a.get('launches', []) + b.get('launches', []):
    k = key(e)
    if k in seen:
        if seen[k] != e:
            merged_e = dict(seen[k])
            merged_e.update({kk: e[kk] for kk in set(e) - set(seen[k])})
            seen[k] = merged_e
            merged = [x if key(x) != k else merged_e for x in merged]
        continue
    seen[k] = e
    merged.append(e)
merged.sort(key=lambda x: x.get('ts', ''))
if len(merged) > 50:
    merged = sorted(merged, key=lambda x: x.get('ts', ''))[-50:]
    merged.sort(key=lambda x: x.get('ts', ''))
la, lb = a.get('last_tick') or {}, b.get('last_tick') or {}
ta, tb = la.get('ts'), lb.get('ts')
lt = la if (ta is not None and (tb is None or ta >= tb)) else lb
if ta == tb:
    lt = la
assert isinstance(lt, dict), 'last_tick not dict'
out = dict(a)
out['launches'] = merged
out['last_tick'] = lt
s = (json.dumps(out, ensure_ascii=False, indent=indent) + '\n').replace('\n', eol)
open(p, 'wb').write(s.encode('utf-8'))
json.load(open(p, encoding='utf-8'))
print('autofill union: %s|%s -> %s launches, last_tick ts=%s' % (
    len(a.get('launches', [])), len(b.get('launches', [])), len(merged), lt.get('ts')))
print('OK')
