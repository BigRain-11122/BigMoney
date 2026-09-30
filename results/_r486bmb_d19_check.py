# r486 bm-b D-19 fresh-read: group decisions watermark via temp partial clone (r481 bm-b recipe, r292 raw-bytes law)
import subprocess, hashlib, json, os, sys

REPO = 'git@github.com:BigRain-11122/FluxGroup.git'
TMP = os.path.join(os.environ['TEMP'], 'fg-dec-bmb')

if not os.path.isdir(os.path.join(TMP, '.git')):
    subprocess.check_call(['git', 'clone', '--depth', '1', '--filter=blob:none', '--no-checkout', REPO, TMP],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.check_call(['git', '-C', TMP, 'fetch', 'origin'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

dec = subprocess.check_output(['git', '-C', TMP, 'show', 'origin/main:docs/decisions.md'])
sha = hashlib.sha256(dec).hexdigest().upper()

st = json.load(open('state.json', encoding='utf-8-sig'))
prev = st.get('last_decisions_sha', '')
print('remote decisions sha:', sha)
print('state watermark      :', prev)
print('MATCH' if sha == prev else 'CHANGED')

if sha != prev:
    # surface the 派工通告板 block + new decision lines for bm-b-relevant rows
    text = dec.decode('utf-8-sig', errors='replace')
    lines = text.splitlines()
    # find the dispatch board section
    for i, l in enumerate(lines):
        if '派工通告板' in l:
            print('--- dispatch board (from line %d) ---' % (i + 1))
            print('\n'.join(lines[i:i + 60]))
            break
    # show tail 40 lines (newest decisions usually at bottom)
    print('--- tail 30 ---')
    print('\n'.join(lines[-30:]))

# also read orders.md CEO physical-items section per D-20260930-13
try:
    orders = subprocess.check_output(['git', '-C', TMP, 'show', 'origin/main:docs/orders.md']).decode('utf-8-sig', errors='replace')
    tail = orders.splitlines()[-25:]
    print('--- group orders.md tail 25 ---')
    print('\n'.join(tail))
except Exception as e:
    print('orders.md read fail:', e)
