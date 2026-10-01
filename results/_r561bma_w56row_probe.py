import io
txt = open('research/PERPETUAL_FACES.md', encoding='utf-8').read()
out = io.open('results/_r561bma_w56row.txt', 'w', encoding='utf-8')
for i, l in enumerate(txt.splitlines()):
    if l.startswith('- N1 波56'):
        out.write(l + '\n\n')
        break
n1 = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
lines = n1.splitlines()
for i, l in enumerate(lines):
    if '"shard_subdir": "n1_w56"' in l:
        out.write('n1.py 56 entry tail:\n')
        out.write('\n'.join(lines[i:i+2]) + '\n')
        break
pf = open('scripts/perpetual_faces.py', encoding='utf-8').read()
for l in pf.splitlines():
    if '56: {"a"' in l:
        out.write('pf.py 56 row: ' + repr(l) + '\n')
out.close()
print('ok')
