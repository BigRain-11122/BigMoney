# W95 freeze anchor shape verification (read-only)
s = open(r'scripts/perpetual_faces_n1.py', encoding='utf-8').read()
# W94 frag end line
import re
lines = s.splitlines()
for i, l in enumerate(lines):
    if 'law sec.4 W94 row' in l and l.rstrip().endswith('] "'):
        print('W94 frag end line idx', i, '->', repr(l[-60:]))
        print('  next line:', repr(lines[i + 1][:60]) if i + 1 < len(lines) else 'EOF')
# what follows the W94 leg finally
k = s.find('# --- W94 materializer face')
m = s.find('_set_wave(2)', k)
print('after W94 leg finally:', repr(s[m + len('_set_wave(2)'):m + len('_set_wave(2)') + 80]))
# pf 94 entry close
p = open(r'scripts/perpetual_faces.py', encoding='utf-8').read()
q = p.find('94: {"a"')
r = p.find('\n', q)
print('pf 94 entry line:', repr(p[q:q + 70]))
print('pf 94 close line:', repr(p[r + 1:r + 50]))
# canon W94 row + what follows
c = open(r'research/PERPETUAL_FACES.md', encoding='utf-8').read()
w = c.find('- N1 ' + '\u6ce294')
e = c.find('\n', w)
print('canon W94 row head:', repr(c[w:w + 40]))
print('canon after W94 row:', repr(c[e + 1:e + 60]))
# n1 cfg 94 close shape
t = s.find('"shard_subdir": "n1_w94"')
u = s.find('\n', t)
print('n1 w94 subdir line:', repr(s[t:u + 1]))
print('n1 w94 close line:', repr(s[u + 1:u + 45]))
