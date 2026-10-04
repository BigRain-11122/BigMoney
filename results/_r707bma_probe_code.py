import re, io
s = io.open('scripts/perpetual_faces_n2.py', 'rb').read().decode('utf-8', errors='replace')
out = []
for pat in (r'def cmd_judge', r'log', r'[Rr][Aa][Mm]', r'exit\(2\)'):
    out.append('=== ' + pat)
    for m in re.finditer(pat, s):
        a = max(0, m.start()-70)
        out.append(repr(s[a:m.start()+130]))
        out.append('---')
io.open('results/_r707bma_probe_out.txt', 'w', encoding='utf-8').write('\n'.join(out)[:9000])
print('lines', len(out))
