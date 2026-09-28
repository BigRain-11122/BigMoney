# r369 bm-b wave-2 resolver: CODELY.md memory-union (single UU face, c1db0b5c replay)
# Recipe: line-level union, keep BOTH machines' new pitlaw entries, dedupe identical.
# In rebase: :2:=HEAD=origin/newer (r149 bm-c entry), :3:=replayed c1db0b5c (r368 bm-b entry).
import io, re, sys

p = 'CODELY.md'
raw = io.open(p, 'rb').read()
text = raw.decode('utf-8')
nl = '\r\n' if '\r\n' in text else '\n'

# extract conflict block via markers
m = re.search(r'<<<<<<< HEAD\r?\n(.*?)\r?\n=======\r?\n(.*?)\r?\n>>>>>>> [^\r\n]*', text, re.S)
assert m, 'conflict block not found'
ours, theirs = m.group(1), m.group(2)

def split_lines(block):
    return [l for l in re.split(r'\r?\n', block)]

ours_lines = split_lines(ours)      # origin side (r149 bm-c entry)
theirs_lines = split_lines(theirs)  # my replay side (r368 bm-b entry)

seen, union = set(), []
for l in ours_lines + theirs_lines:
    if l.strip() and l not in seen:
        seen.add(l)
        union.append(l)

# sanity: both pitlaw entries survive
assert any('r149 bm-c' in l for l in union), 'r149 bm-c entry lost'
assert any('r368 bm-b' in l for l in union), 'r368 bm-b entry lost'

repl = nl.join(union)
text2 = text[:m.start()] + repl + text[m.end():]
assert '<<<<<<<' not in text2 and '>>>>>>>' not in text2
io.open(p, 'wb').write(text2.encode('utf-8'))
print('CODELY.md union:', len(ours_lines), 'origin lines +', len(theirs_lines), 'replay lines ->', len(union))
for l in union:
    print('  kept:', l[:100])
