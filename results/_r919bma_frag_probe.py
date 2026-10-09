import io
n1 = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8', newline='').read()
pf = io.open('scripts/perpetual_faces.py', encoding='utf-8', newline='').read()
probes_n1 = ['    # --- W198 materializer face', '    _set_wave(2)',
             '    # --- T-141 s2 lane face',
             '    198: {"batch": "PERPETUAL-N1-W198",',
             '          "+ W198 materializer face',
             '"r916 bm-a] "',
             '    197: {"batch": "PERPETUAL-N1-W197",']
for p in probes_n1:
    print('n1:', repr(p[:45]), n1.count(p))
probes_pf = ['    # W198 (bm-a r916 freeze',
             '    198: {"a": (450_404, 452_403)',
             '    # --- T-141']
for p in probes_pf:
    print('pf:', repr(p[:45]), pf.count(p))
i = n1.find('    # --- W198 materializer face')
j = n1.find('    _set_wave(2)', i)
print('mat198 chunk span:', j - i, 'bytes; tail:', repr(n1[j:j + 22]))
k = n1.find('    # --- T-141 s2 lane face')
print('T141 pos:', k, 'chunk_end:', j + len('    _set_wave(2)'), 'T141 after chunk end:', k > j)
# baseline duplication check: how many literal _set_wave(2) exist and where
import re
for m in re.finditer(r'    _set_wave\(2\)', n1):
    print('  _set_wave(2) at', m.start())
