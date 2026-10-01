import json, subprocess, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

mine = json.load(open('results/perpetual_faces/n1_w53_results.json', encoding='utf-8'))
origin = json.loads(subprocess.check_output(['git','show','origin/main:results/perpetual_faces/n1_w53_results.json']).decode('utf-8'))

ENVELOPE = {'audit.machine', 'audit.elapsed_sec', 'audit.workers', 'generated'}

def flat(d, pre=''):
    out = {}
    if isinstance(d, dict):
        for k, v in d.items():
            out.update(flat(v, f'{pre}.{k}' if pre else k))
    elif isinstance(d, list):
        # runs arrays are huge; compare only length + sampled scalars for lists of dicts is too heavy:
        # record length; if list of numbers, compare min/max/first/last
        if all(isinstance(x, (int, float)) for x in d) and d:
            out[pre + '[]len'] = len(d)
            out[pre + '[]first'] = d[0]; out[pre + '[]last'] = d[-1]
        else:
            out[pre + '[]len'] = len(d)
    else:
        out[pre] = d
    return out

fm, fo = flat(mine), flat(origin)
km, ko = set(fm), set(fo)
print('key set equal:', km == ko)
print('only-mine keys:', sorted(km - ko)[:10])
print('only-origin keys:', sorted(ko - km)[:10])

env_diff, float_diff, hard_diff = [], [], []
for k in sorted(km & ko):
    if k in ENVELOPE:
        if fm[k] != fo[k]: env_diff.append((k, fm[k], fo[k]))
        continue
    a, b = fm[k], fo[k]
    if isinstance(a, float) or isinstance(b, float):
        if abs(a - b) > 1e-9 * max(abs(a), abs(b), 1e-12):
            float_diff.append((k, a, b))
    elif a != b:
        hard_diff.append((k, a, b))

print('envelope diffs (expected):', env_diff[:5])
print('float diffs >1e-9 rel:', float_diff[:10])
print('hard diffs:', hard_diff[:10])
print('VERDICT:', 'AA-CONVERGENT (r498/r499)' if not float_diff and not hard_diff and km == ko else 'DIVERGENT')
