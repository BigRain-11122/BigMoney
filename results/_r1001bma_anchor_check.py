import io
pf = io.open('scripts/perpetual_faces.py', encoding='utf-8').read()
n1 = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
checks = {
    'pf 242 row literal': ('    242: {"a"', 1),
    'pf v1+ext marker': ('# v1 + ext(wave-1) in-use bands', 1),
    'n1 W242 block hdr': ('# --- W242 materializer face', 1),
    'n1 T141 marker': ('    # --- T-141 s2 lane face', 1),
    'n1 242 cfg': ('242: {"batch": "PERPETUAL-N1-W242"', 1),
    'n1 cfg close': ('PREREG = WAVE_CONFIGS[2]["prereg"]', 1),
    'n1 241 cfg': ('241: {"batch": "PERPETUAL-N1-W241"', 1),
    'n1 W241 block hdr': ('# --- W241 materializer face', 1),
}
for name, (needle, want) in checks.items():
    c = pf.count(needle) + n1.count(needle)
    print('%-22s count=%d (want %d in combined pf+n1)' % (name, c, want))
# pf row own-line owner check
i = pf.find('    242: {"a"')
ls = pf.find('\n', i) + 1
le = pf.find('\n', ls)
print('W242 own line:', repr(pf[ls:le][:120]))
# n1 block parity span check for the W242 block
a = n1.find('    # --- W242 materializer face')
t = n1.find('    # --- T-141 s2 lane face')
blk = n1[a:t]
print('W242 block bytes:', t - a)
print('W242 block parity rows:', blk.count('assert pf.N1_BANDS['))
import re
m = re.search(r'assert pf\.N1_BANDS\[232\] ==', blk)
print('W232 leg inside W242 block:', bool(m))
# first row indent faces
print('pf bytes:', len(pf), 'n1 bytes:', len(n1))
