import sys
sys.path.insert(0, 'research'); sys.path.insert(0, 'scripts'); sys.path.insert(0, '.')
import science_gates
pts = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
print('SEED_REGISTRY int values in [157_004..159_003]:', sorted(p for p in pts if 157_004 <= p <= 159_003))
print('SEED_REGISTRY int values in [47_401..47_600]:', sorted(p for p in pts if 47_401 <= p <= 47_600))
print('SEED_REGISTRY int values in [155_004..157_003]:', sorted(p for p in pts if 155_004 <= p <= 157_003))
print('SEED_REGISTRY int values in [47_201..47_400]:', sorted(p for p in pts if 47_201 <= p <= 47_400))
print('registry total int values:', len(pts))
# also grep pf.py for the exact 55-row text and n1.py shard_subdir line
pf = open('scripts/perpetual_faces.py', encoding='utf-8').read()
n1 = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
print('---pf 55 row snippet---')
for l in pf.splitlines():
    if '55: {"a"' in l or ('"engine_owner": "bm-b"' in l and 'b_exit' in l):
        print(repr(l))
print('---n1 55 entry tail---')
lines = n1.splitlines()
for i, l in enumerate(lines):
    if '"shard_subdir": "n1_w55"' in l:
        print(repr(l)); print(repr(lines[i+1]))
