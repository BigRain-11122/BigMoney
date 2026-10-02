import subprocess, sys, os
ROOT = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
sys.path.insert(0, os.path.join(ROOT, 'research'))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
sys.path.insert(0, ROOT)
from perpetual_faces import N1_BANDS
import science_gates

# --- registered W70 row parity (derivation basis) ---
assert 70 in N1_BANDS and N1_BANDS[70]['a'] == (183_004, 185_003) \
    and N1_BANDS[70]['b_exit'] == (51_001, 51_200) \
    and N1_BANDS[70]['engine_owner'] == 'bm-b', 'W70 registered row parity'
print('W70 registered:', N1_BANDS[70])
print('bm-c owned rows (pre-W71):', sum(1 for c in N1_BANDS.values() if c.get('engine_owner')=='bm-c'))
print('bm-b owned rows:', sum(1 for c in N1_BANDS.values() if c.get('engine_owner')=='bm-b'))
print('bm-a owned rows:', sum(1 for c in N1_BANDS.values() if c.get('engine_owner')=='bm-a'))
print('registry keys:', sorted(N1_BANDS))

points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
print('SEED_REGISTRY int values sorted:')
print(sorted(points))
N3R1 = set(range(70_000, 70_006))
PROBE_SEEDS = {95_000, 95_001, 95_002, 95_003}
N24 = {40_000, 40_001}
N2W15 = {31_000, 31_500, 32_000}
allpts = points | N3R1 | PROBE_SEEDS | N24 | N2W15

A0 = N1_BANDS[70]['a'][1] + 1
B0 = N1_BANDS[70]['b_exit'][1] + 1
WA, WB = 2_000, 200
aw = (A0, A0 + WA - 1)
bw = (B0, B0 + WB - 1)
a_hits = sorted(p for p in allpts if aw[0] <= p <= aw[1])
b_hits = sorted(p for p in allpts if bw[0] <= p <= bw[1])
print('W71-A arithmetic window', aw, 'hits:', a_hits)
print('W71-B arithmetic window', bw, 'hits:', b_hits)
for h in b_hits + a_hits:
    for k, v in science_gates.SEED_REGISTRY.items():
        if v == h:
            print('hit key:', k, '=', v)
# band overlap vs all registered bands
def overlaps(a, b): return not (a[1] < b[0] or b[1] < a[0])
conf = []
for wnum, cfg in N1_BANDS.items():
    for key in ('a', 'b_exit'):
        if overlaps(tuple(cfg[key]), aw): conf.append(f'W{wnum}.{key} x A')
        if overlaps(tuple(cfg[key]), bw): conf.append(f'W{wnum}.{key} x B')
V1 = [(10_000, 10_099), (20_000, 20_019)]
W1E = [(10_100, 12_099), (20_100, 20_299)]
for nm, r in [('v1', V1), ('w1ext', W1E), ('lfc', [(30_000, 30_099)]), ('opts', [(63_000, 63_049)])]:
    for bb in r:
        if overlaps(bb, aw): conf.append(f'{nm} x A')
        if overlaps(bb, bw): conf.append(f'{nm} x B')
print('band conflicts:', conf if conf else 'NONE')
print('VERDICT:', 'BOTH CLEAN zero-skip' if not a_hits and not b_hits and not conf else 'REFUSAL FACE PRESENT')
