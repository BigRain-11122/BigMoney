# r1116: dump tail lines beyond probe increment (11:53 onwards) for S7 disclosure
import subprocess, sys

blob = subprocess.run(
    ['git', '-C', 'K:/Fluxgroup/FluxGroup', 'show', 'origin/main:docs/orders.md'],
    capture_output=True
).stdout
text = blob.decode('utf-8')
lines = text.splitlines()

out = []
for i, l in enumerate(lines, 1):
    if i >= 1242 and ('2026-10-19' in l):
        out.append('=== LINE %d (len %d) ===' % (i, len(l)))
        out.append(l)

with open(r'C:\Users\Dasheng\AppData\Local\Temp\_r1116_ord_tail.txt', 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(out))
print('dumped %d lines' % (len(out) // 2))
