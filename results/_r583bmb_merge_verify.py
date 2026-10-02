# construct-merge order + integrity assertions (W99 < W100 < W101 every face)
ok = True

c = open('research/PERPETUAL_FACES.md', 'rb').read()
p99 = c.find('- N1 波99'.encode())
p100 = c.find('- N1 波100'.encode())
p101 = c.find('- N1 波101'.encode())
print('canon order:', p99, p100, p101, 'OK' if 0 < p99 < p100 < p101 else 'FAIL')
ok &= 0 < p99 < p100 < p101
assert c.count('- N1 波100'.encode()) == 1

pf = open('scripts/perpetual_faces.py', 'rb').read()
for key in (b'99: {"a": (241_004', b'100: {"a": (243_004', b'101: {"a": (245_004'):
    i = pf.find(key)
    assert i > 0, key
assert pf.find(b'99: {"a": (241_004') < pf.find(b'100: {"a": (243_004') < pf.find(b'101: {"a": (245_004'), 'pf order FAIL'
assert pf.count(b'100: {"a": (243_004') == 1
print('pf order OK (99 < 100 < 101)')

n1 = open('scripts/perpetual_faces_n1.py', 'rb').read()
l99 = n1.find(b'# --- W99 materializer face')
l100 = n1.find(b'# --- W100 materializer face')
l101 = n1.find(b'# --- W101 materializer face')
assert 0 < l99 < l100 < l101, f'leg order FAIL {l99} {l100} {l101}'
print('leg order OK (99 < 100 < 101)')
f99 = n1.find(b'"W99 row, r374 bm-c] "')
f100 = n1.find(b'W100 row, r583 bm-b]')
f101 = n1.find(b'"W101 row, r583 bm-a] "')
assert 0 < f99 < f100 < f101, f'frag order FAIL {f99} {f100} {f101}'
assert n1.count(b'W100 row, r583 bm-b]') == 1
print('frag order OK (99 < 100 < 101)')
cfg99 = n1.find(b'"shard_subdir": "n1_w99"')
cfg100 = n1.find(b'"shard_subdir": "n1_w100"')
cfg101 = n1.find(b'"shard_subdir": "n1_w101"')
assert 0 < cfg99 < cfg100 < cfg101, f'cfg order FAIL {cfg99} {cfg100} {cfg101}'
print('cfg order OK (99 < 100 < 101)')

# registry sanity via import
import sys
sys.path.insert(0, 'scripts'); sys.path.insert(0, 'research'); sys.path.insert(0, '.')
from perpetual_faces import N1_BANDS
assert sorted(N1_BANDS)[-3:] == [99, 100, 101]
assert N1_BANDS[100] == {'a': (243004, 245003), 'b_exit': (58751, 58950), 'engine_owner': 'bm-b'}
assert N1_BANDS[101]['engine_owner'] == 'bm-a'
print('N1_BANDS live import OK: tail 99/100/101, W100=bm-b, W101=bm-a')
print('CONSTRUCT-MERGE ORDER + INTEGRITY: ALL PASS')
