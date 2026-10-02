# -*- coding: utf-8 -*-
# r381 bm-c 4th surgical reland: reset-FF + CODELY line-union + inbox move completion + selective checkout
import subprocess, os
os.chdir(r'K:\Fluxgroup\FluxGroup\quant\bigmoney')
G = r'C:\Program Files\Git\bin\git.exe'

def git(*a):
    r = subprocess.run([G] + list(a), capture_output=True, cwd=os.getcwd())
    return r.returncode, r.stdout.decode('utf-8', 'replace'), r.stderr.decode('utf-8', 'replace')

# 0) capture my pit line from current working CODELY.md BEFORE reset
mine_bytes = open('CODELY.md', 'rb').read()
mine_lines = [l for l in mine_bytes.split(b'\r\n') if l.strip()]
my_pit = mine_lines[-1]
print('my_pit captured: len', len(my_pit), 'head', my_pit[:60].decode('utf-8', 'replace'))

# 1) reset to origin
rc, out, err = git('reset', '--mixed', 'origin/main')
print('reset rc', rc, err[:120])

# 2) CODELY union: origin verbatim + my line (append-face union, zero-loss assert)
r = subprocess.run([G, 'show', 'origin/main:CODELY.md'], capture_output=True)
ob = r.stdout
union = ob
if not union.endswith(b'\r\n'):
    union += b'\r\n'
union += my_pit + b'\r\n'
ob_lines = [l for l in ob.split(b'\r\n') if l.strip()]
un_lines = [l for l in union.split(b'\r\n') if l.strip()]
assert un_lines[:-1] == ob_lines, 'union prefix must equal origin verbatim'
assert len(un_lines) == len(ob_lines) + 1, 'union = origin + 1 mine'
open('CODELY.md', 'wb').write(union)
print('CODELY union written: origin %d lines + 1 mine = %d lines, %d bytes' % (len(ob_lines), len(un_lines), len(union)))

# 3) selective checkout: keep my books + live-writer faces + CODELY union
keep = {'results/autofill_state.bm-c.json', 'results/dispatcher_state.bm-c.json',
        'results/saturation_engine/face_bm-c.json', 'results/saturation_engine_state.bm-c.json',
        'state-bm-c.json', 'round_reports-bm-c.md', 'fleet/machines/bm-c.json', 'CODELY.md'}
rc, out, err = git('status', '--porcelain')
co = []
untracked = []
for line in out.split('\n'):
    if not line.strip():
        continue
    st = line[:2]
    path = line[3:].strip('"')
    if st == '??':
        untracked.append(path)
        continue
    if path in keep:
        continue
    co.append(path)
print('checkout_count', len(co), 'untracked', len(untracked), [os.path.basename(u) for u in untracked])
for i in range(0, len(co), 50):
    rc2, out2, err2 = git('checkout', '--', *co[i:i + 50])
    if rc2 != 0:
        print('CHUNK FAIL', i, rc2, err2[:300])

# 4) inbox archive-move completion (blob already verified identical to processed/ copy this round)
MSG = 'fleet/inbox/MSG-20261002-1922-bma-w112-seat.md'
if os.path.exists(MSG):
    os.remove(MSG)
    print('inbox leftover removed (archive move completion, r586 law)')

rc, out, err = git('status', '--porcelain')
print('--- post ---')
print(out[:900])
