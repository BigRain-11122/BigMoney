# r1116: extract orders.md lines (11:16 + tail beyond probe) from group-tree origin blob, raw bytes -> UTF-8 file
import subprocess, sys

blob = subprocess.run(
    ['git', '-C', 'K:/Fluxgroup/FluxGroup', 'show', 'origin/main:docs/orders.md'],
    capture_output=True
).stdout
if not blob:
    print('FATAL: empty blob'); sys.exit(1)

text = blob.decode('utf-8')
lines = text.splitlines()
print('total_lines=%d bytes=%d' % (len(lines), len(blob)))

sel = []
for i, l in enumerate(lines, 1):
    if '2026-10-19 11:16' in l or '2026-10-19 11:2' in l:
        sel.append((i, l))

out_lines = []
for i, l in sel:
    out_lines.append('=== LINE %d (len %d) ===' % (i, len(l)))
    out_lines.append(l)

with open(r'C:\Users\Dasheng\AppData\Local\Temp\_r1116_ord_sel.txt', 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(out_lines))
print('selected=%d written=%d lines' % (len(sel), len(out_lines)))
