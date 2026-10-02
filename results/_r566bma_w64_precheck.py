import io, sys, os
sys.path.insert(0, 'scripts')
sys.path.insert(0, 'research')
from perpetual_faces import N1_BANDS
import science_gates

# live derive W64 from W63 tail (bm-c's row)
w63 = N1_BANDS[63]
A0 = w63['a'][1] + 1
B0 = w63['b_exit'][1] + 1
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= {40_000, 40_001} | {31_000, 31_500, 32_000} | set(range(70_000, 70_006)) | {95_000, 95_001, 95_002, 95_003}
bands = []
for wnum, cfg in N1_BANDS.items():
    for key in ('a', 'b_exit'):
        bands.append(tuple(cfg[key]))
bands += [(10_000, 10_099), (20_000, 20_019), (10_100, 12_099), (20_100, 20_299)] + [(30_000, 30_099), (63_000, 63_049)]
def ov(a, b):
    return not (a[1] < b[0] or b[1] < a[0])
def clean(lo, width):
    hi = lo + width - 1
    for p in points:
        if lo <= p <= hi:
            return None, ('point', p)
    for b in bands:
        if ov((lo, hi), b):
            return None, ('band', b)
    return (lo, hi), None
print('W63 tail: A end', w63['a'][1], 'B end', w63['b_exit'][1])
print('W64 A arith:', clean(A0, 2000))
print('W64 B arith:', clean(B0, 200))
print('keys:', len(N1_BANDS), sorted(N1_BANDS)[-3:])

# anchors in bm-c's landed files
t = io.open('scripts/perpetual_faces.py', encoding='utf-8').read()
i = t.find('63: {"a"')
print('--- pf W63 row context:')
print(t[i-30:i+220])
a1 = '    63: {"a": (169_004, 171_003), "b_exit": (49_201, 49_400),\n         "engine_owner": "bm-c"},\n}\n'
print('edit1 anchor count:', t.count(a1))
t2 = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
j = t2.find('"shard_subdir": "n1_w63"')
print('--- n1 W63 config tail context:')
print(t2[j-80:j+260])
a3 = '\n    # --- T-141 s2 lane face'
print('edit3 anchor count:', t2.count(a3))
a5 = 'law sec.4 W63 row, r357 bm-c] "' + '\n          "+ T-141 s2 '
print('edit5 anchor count:', t2.count(a5))
t4 = io.open('research/PERPETUAL_FACES.md', encoding='utf-8').read()
print('canon W63 row count:', t4.count('- N1 \u6ce263\uff08'))
print('canon W64 existing:', t4.count('- N1 \u6ce264\uff08'))
print('canon sec5 anchor:', t4.count('\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'))
