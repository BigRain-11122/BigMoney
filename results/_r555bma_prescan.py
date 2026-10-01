"""r555 helper: pre-scan W47 candidate windows vs full reserved universe + W44 anchor semantics."""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
sys.path.insert(0, os.path.join(ROOT, 'research'))
import subprocess, json
import science_gates
from perpetual_faces import N1_BANDS, V1_IN_USE, EXT_W1_IN_USE

points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
N24_PROBE = (40_000, 40_001)
N2W15_PROBE = (31_000, 31_500, 32_000)
N3R1 = range(70_000, 70_006)
PROBE_SEEDS = (95_000, 95_001, 95_002, 95_003)
points |= set(N24_PROBE) | set(N2W15_PROBE) | set(N3R1) | set(PROBE_SEEDS)

def scan(lo, width, label):
    hits = sorted(p for p in points if lo <= p <= lo + width - 1)
    print(f'{label} {lo}..{lo + width - 1}: point-hits={hits}')
    return hits

# A candidate: arithmetic from W46 A end
A_LO = N1_BANDS[46]['a'][1] + 1
print('W47 A arithmetic start:', A_LO)
scan(A_LO, 2_000, 'A-candidate')
# B candidate: arithmetic refused at 45_000 -> scan forward
B0 = N1_BANDS[46]['b_exit'][1] + 1
print('W47 B arithmetic start:', B0)
scan(B0, 200, 'B-arith')
hits = scan(B0 + 200, 200, 'B-next(45_001..45_200)')
scan(B0 + 400, 200, 'B-next2(45_201..45_400)')
# A next projection for W48+ warning
scan(A_LO + 2_000, 2_000, 'A-W48-projection')

# registry entries in 44k-46k and 137k-141k for disclosure
reg_hits = sorted((k, v) for k, v in science_gates.SEED_REGISTRY.items()
                  if isinstance(v, int) and (44_000 <= v <= 46_500 or 137_000 <= v <= 141_500))
print('registry entries near W47 faces:', reg_hits)

# W44 finalize anchor semantics
d = json.loads(subprocess.check_output(['git', 'show', 'origin/main:results/perpetual_faces/n1_w44_results.json']))
npc = d['null_pool_cumulative']
print()
print('W44 npc keys:', sorted(npc.keys()))
for blk in ('merged', 'pre_w44_cumulative', 'w44_only'):
    if blk in npc:
        print('W44', blk, '=', npc[blk])
famsA = d['families']['A_random_engine_exit']
print('W44 A p95 =', famsA.get('full_sharpe_p95'))
print('W44 skill_line =', json.dumps(d.get('skill_line_v2_k_lift', {}), ensure_ascii=False)[:260])
