# r1116 S7 tail: fetch + extract rows landed AFTER the advance face (cac54c8f)
import subprocess, hashlib

def git(*args):
    r = subprocess.run(['git', '-C', 'K:/Fluxgroup/FluxGroup'] + list(args), capture_output=True)
    return r.stdout

git('fetch', 'origin')
o_blob = git('show', 'origin/main:docs/orders.md')
print('content-sha1 =', hashlib.sha1(o_blob).hexdigest())
text = o_blob.decode('utf-8')
lines = text.splitlines()
print('total lines =', len(lines))
# rows after the 12:29 batch: find lines with 2026-10-19 timestamps > 12:29
out = []
for i, l in enumerate(lines, 1):
    if l.startswith('| 2026-10-19 1') and ('12:3' in l[:30] or '12:4' in l[:30] or '12:5' in l[:30] or '13:' in l[:30] or '1[34]:' in l[:30]):
        out.append((i, l))
with open(r'C:\Users\Dasheng\AppData\Local\Temp\_r1116_tail2.txt', 'w', encoding='utf-8', newline='\n') as f:
    for i, l in out:
        f.write('=== L%d (len %d) ===\n%s\n' % (i, len(l), l))
print('candidate rows =', len(out))
for i, l in out:
    print('L%d: %s' % (i, l[:160]))
