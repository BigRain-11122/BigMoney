import sys, os
ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
import science_gates
from perpetual_faces import N1_BANDS

points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
keys = {v: k for k, v in science_gates.SEED_REGISTRY.items() if isinstance(v, int)}
print("registry keys near 50_000..51_000:", sorted((v, keys[v]) for v in points if 49_000 <= v <= 51_000))
# first clean window past 50_500 (width 200)
lo = 50_401
while True:
    hits = sorted(p for p in points if lo <= p <= lo + 199)
    if not hits:
        print(f"first clean window from 50_401 walk = {lo}..{lo+199}")
        break
    print(f"window {lo}..{lo+199} REFUSED at {hits} (keys: {[keys[h] for h in hits]})")
    lo = max(hits) + 1
