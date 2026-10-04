import io

p = r'results\pool_core_samples.jsonl'
with io.open(p, 'r', encoding='utf-8', newline='') as f:
    raw = f.read()
lines = raw.split('\n')
out, state, ours, theirs = [], 0, [], []
kept = 0
for ln in lines:
    if ln.startswith('<<<<<<<'):
        state = 1
        continue
    if ln.startswith('======='):
        state = 2
        continue
    if ln.startswith('>>>>>>>'):
        state = 0
        union = sorted(set(ours + theirs), key=lambda s: s.split('"')[3] if s else '')
        out.extend(union)
        kept += len(union)
        ours, theirs = [], []
        continue
    if state == 1:
        theirs.append(ln)
    elif state == 2:
        ours.append(ln)
    else:
        out.append(ln)
merged = '\n'.join(out)
assert '<<<<<<<' not in merged and '>>>>>>>' not in merged and '=======' not in merged
with io.open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(merged)
print('union kept lines:', kept, '| newlines:', merged.count('\n'))
