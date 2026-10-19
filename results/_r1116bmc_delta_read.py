# r1116: final pre-advance ORD/DELTA read -- fetch group tree, extract ALL rows
# after the stored watermark content (0992a4ea face = lines through 2026-10-19 11:0x)
# plus DEC delta rows; dump to UTF-8 temp file for judgment consumption.
import subprocess, sys

def git(*args):
    r = subprocess.run(['git', '-C', 'K:/Fluxgroup/FluxGroup'] + list(args), capture_output=True)
    return r.stdout, r.stderr

# 1) fetch
out, err = git('fetch', 'origin')
blob, err2 = git('rev-parse', 'origin/main:docs/orders.md')
blob = blob.decode().strip()
print('orders blob (git) =', blob)

# 2) orders content + find all 2026-10-19 rows with ts >= 10:53 (the delta face:
#    stored 0992a4ea covered lines through ~11:0x; delta rows = 10:53 onwards)
o_blob, _ = git('show', 'origin/main:docs/orders.md')
o_text = o_blob.decode('utf-8')
o_lines = o_text.splitlines()
import hashlib
print('orders content-sha1 =', hashlib.sha1(o_blob).hexdigest())
print('orders total lines =', len(o_lines))

# 3) decisions content-sha256
d_blob, _ = git('show', 'origin/main:docs/decisions.md')
print('decisions content-sha256 =', hashlib.sha256(d_blob).hexdigest())

# 4) dump all delta ORD rows (10-19 lines from 10:53 onward) + head of any 10-19 line
sel = []
for i, l in enumerate(o_lines, 1):
    if l.startswith('| 2026-10-19') or l.startswith('| 10-19'):
        sel.append((i, l))

with open(r'C:\Users\Dasheng\AppData\Local\Temp\_r1116_delta_rows.txt', 'w', encoding='utf-8', newline='\n') as f:
    for i, l in sel:
        f.write('=== L%d ===\n%s\n' % (i, l))
print('10-19 rows found =', len(sel))
