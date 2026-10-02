# -*- coding: utf-8 -*-
# r385 bm-c S0 conflation probe: D-19 decisions watermark + task board scan + O-2100 wiring presence
import subprocess, hashlib, json, glob, os, sys
os.chdir(r'K:\Fluxgroup\FluxGroup\quant\bigmoney')
NO_WINDOW = 0x08000000

def gitout(args, cwd=None):
    return subprocess.check_output(['git', '-C'] + ([cwd] if cwd else []) + args, creationflags=NO_WINDOW)

print('--- D-19 decisions watermark ---')
grp = r'K:\Fluxgroup\FluxGroup'
subprocess.run(['git', '-C', grp, 'fetch', 'origin'], capture_output=True, creationflags=NO_WINDOW)
b = gitout(['show', 'origin/main:docs/decisions.md'], cwd=grp)
h = hashlib.sha256(b).hexdigest().upper()
OLD = '937A373DA4339EDC70E95D2EC3E2AC5B1B62E298C834AC84B5FD2955EC5FD4E1'
print('sha256=' + h)
print('verdict=' + ('MATCH' if h == OLD else 'CHANGED'))
if h != OLD:
    txt = b.decode('utf-8', errors='replace')
    lines = txt.splitlines()
    print('total_lines=%d' % len(lines))
    print('== tail 45 ==')
    print('\n'.join(lines[-45:]))
    print('== orders.md CEO todo tail ==')
    try:
        ob = gitout(['show', 'origin/main:docs/orders.md'], cwd=grp)
        ol = ob.decode('utf-8', errors='replace').splitlines()
        print('\n'.join(ol[-30:]))
    except Exception as ex:
        print('orders.md read err:', ex)

print('--- task board (non-done/void) ---')
for f in sorted(glob.glob('fleet/tasks/*.json')):
    try:
        d = json.load(open(f, encoding='utf-8'))
    except Exception as ex:
        print(os.path.basename(f), 'PARSE_ERR', ex); continue
    st = d.get('status')
    if st and st not in ('done', 'void'):
        name = os.path.basename(f)
        t = str(d.get('title') or d.get('subject') or d.get('id') or '')[:90]
        print(name, '|', st, '| claimed_by=' + str(d.get('claimed_by')), '|', t)

print('--- O-2100 wiring presence ---')
ipt = open('Tools/iteration_prompt.txt', 'rb').read().decode('utf-8', errors='replace')
print('iteration_prompt METHODOLOGY_ASSETS mentions=%d' % ipt.count('METHODOLOGY_ASSETS'))
print('assets file exists=%s' % os.path.exists('knowledge/METHODOLOGY_ASSETS.md'))
if os.path.exists('knowledge/METHODOLOGY_ASSETS.md'):
    am = open('knowledge/METHODOLOGY_ASSETS.md', 'rb').read().decode('utf-8', errors='replace')
    import re
    cards = re.findall(r'^## (?:[MNE]\d+)', am, flags=re.M)
    print('asset cards in file=%d' % len(cards))
print('--- done ---')
