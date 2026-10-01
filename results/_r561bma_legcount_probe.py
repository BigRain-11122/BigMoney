import io
n1 = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
lines = n1.splitlines()
out = io.open('results/_r561bma_legcount.txt', 'w', encoding='utf-8')
for i, l in enumerate(lines):
    if 'materializer face' in l:
        out.write(f'{i}: {l[:160]}\n')
# show the second occurrence context for W56
hits = [i for i, l in enumerate(lines) if 'W56 materializer face' in l]
for h in hits:
    out.write(f'\n=== context of line {h} ===\n')
    out.write('\n'.join(lines[max(0, h - 3):h + 6]) + '\n')
out.close()
print('hits:', hits)
