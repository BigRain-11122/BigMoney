# r580 bm-b W94 heal verification (byte-identity + registry counts)
import subprocess, sys

ROOT = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
HOLD = '9a9d05857'

def hold(path):
    r = subprocess.run(['git', '-C', ROOT, 'show', '%s:%s' % (HOLD, path)],
                       capture_output=True)
    assert r.returncode == 0
    return r.stdout

def cur(path):
    return open(ROOT + '\\' + path.replace('/', '\\'), 'rb').read()

hb = hold('scripts/perpetual_faces.py')
pb = cur('scripts/perpetual_faces.py')
# W94 pf entry block from holding: comment start to engine_owner close
def lines(data):
    out, i = [], 0
    while i < len(data):
        j = data.find(b'\n', i)
        if j < 0:
            out.append(data[i:])
            break
        out.append(data[i:j + 1])
        i = j + 1
    return out

hls, pls = lines(hb), lines(pb)
def block(ls, start, end):
    si = next(i for i, l in enumerate(ls) if l.strip().startswith(start))
    ei = si
    while ls[ei].strip() != end:
        ei += 1
    return b''.join(ls[si:ei + 1])

w94_pf_hold = block(hls, b'# EIGHTY-FOURTH ENGINE-OWNED WAVE', b'"engine_owner": "bm-a"},')
n_hold = pb.count(w94_pf_hold)
print('pf W94 block byte-identical copies in current:', n_hold)
assert n_hold == 1, 'pf W94 block not byte-identical/unique'

hn1 = hold('scripts/perpetual_faces_n1.py')
nn1 = cur('scripts/perpetual_faces_n1.py')
h1, c1 = lines(hn1), lines(nn1)
w94_cfg = block(h1, b'94: {"batch"', b'"engine_owner": "bm-a"},')
print('n1 W94 cfg block copies:', nn1.count(w94_cfg))
assert nn1.count(w94_cfg) == 1
# leg block
si = next(i for i, l in enumerate(h1) if l.lstrip().startswith(b'# --- W94 materializer face'))
ei = si
while c1 and h1[ei].strip() != b'_set_wave(2)':
    ei += 1
w94_leg = b''.join(h1[si:ei + 1])
print('n1 W94 leg block copies:', nn1.count(w94_leg))
assert nn1.count(w94_leg) == 1

# registry counts via import
sys.path.insert(0, ROOT + r'\scripts')
import perpetual_faces as pf
keys = sorted(pf.N1_BANDS.keys())
print('N1_BANDS keys:', len(keys), 'min/max:', keys[0], keys[-1], 'has94:', 94 in keys)
assert keys[-1] == 94 and len(keys) == len(set(keys))
expected = set(range(2, 15)) | set(range(16, 95))
assert set(keys) == expected, 'registry key set drift: %s' % (set(keys) ^ expected)
print('W94 bands:', pf.N1_BANDS[94])
assert pf.N1_BANDS[94] == {'a': (231_004, 233_003), 'b_exit': (57_301, 57_500),
                           'engine_owner': 'bm-a'}
owners = {}
for k, v in pf.N1_BANDS.items():
    owners[v.get('engine_owner')] = owners.get(v.get('engine_owner'), 0) + 1
print('owner counts:', owners)
# canon check
cb = cur('research/PERPETUAL_FACES.md')
hc = hold('research/PERPETUAL_FACES.md')
w94_canon = next(l for l in lines(hc) if l.startswith(b'- N1 ') and '\u6ce294'.encode() in l[:12])
print('canon W94 row copies:', cb.count(w94_canon))
assert cb.count(w94_canon) == 1
import py_compile
py_compile.compile(ROOT + r'\scripts\perpetual_faces.py', doraise=True)
py_compile.compile(ROOT + r'\scripts\perpetual_faces_n1.py', doraise=True)
print('py_compile both OK')
print('VERIFY_OK')
