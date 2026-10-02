import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
import science_gates

hits_50k = [k for k, v in science_gates.SEED_REGISTRY.items() if v == 50_000]
print("registry key at 50_000:", hits_50k)
W66_A = (175_004, 177_003)
W66_B = (49_801, 50_000)
points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
a_hits = sorted(p for p in points if W66_A[0] <= p <= W66_A[1])
b_hits = sorted(p for p in points if W66_B[0] <= p <= W66_B[1])
print("W66 A 175_004..177_003 point-hits:", a_hits if a_hits else "CLEAN")
print("W66 B 49_801..50_000 point-hits:", b_hits if b_hits else "CLEAN")
# next clean B window after the refusal (window-stride chain skip +200)
for lo in range(50_001, 50_401, 200):
    hi = lo + 199
    hits = sorted(p for p in points if lo <= p <= hi)
    print(f"B candidate {lo}..{hi}:", "REFUSED " + str(hits) if hits else "CLEAN")
    if not hits:
        break
