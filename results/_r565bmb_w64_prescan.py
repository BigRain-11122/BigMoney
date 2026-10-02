"""r565 bm-b: W64 candidate band pre-scan + W62 finalize anchors extraction.
W64 candidates (basis: W63 seat-declared bands A 169_004..171_003 / B 49_101..49_300, MSG-0843):
  A = 171_004..173_003 (W63 A tail +1, width 2000)
  B = 49_301..49_500   (W63 B tail +1, width 200)
Also reads W62 finalize product for prereg S5 anchors (K, head, mu/sigma etc.).
"""
import sys, os, json, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
import science_gates
from perpetual_faces import N1_BANDS

CAND_A = (171_004, 173_003)
CAND_B = (49_301, 49_500)
W63_DECLARED_A = (169_004, 171_003)
W63_DECLARED_B = (49_101, 49_300)

print("N1_BANDS registered keys:", sorted(N1_BANDS)[-6:], "count:", len(N1_BANDS))
print("W63 in local registry:", 63 in N1_BANDS)

points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
print("SEED_REGISTRY int values in/near candidate ranges:")
hits_a = sorted(p for p in points if CAND_A[0] - 500 <= p <= CAND_A[1] + 500)
hits_b = sorted(p for p in points if CAND_B[0] - 500 <= p <= CAND_B[1] + 500)
print("  near A:", hits_a, " inside A:", [p for p in points if CAND_A[0] <= p <= CAND_A[1]])
print("  near B:", hits_b, " inside B:", [p for p in points if CAND_B[0] <= p <= CAND_B[1]])
# also show the two p4 keys around 49k for context
print("  p4-family keys:", {k: v for k, v in science_gates.SEED_REGISTRY.items() if isinstance(v, int) and 48_000 <= v <= 50_500})

# band overlap check vs all registered rows + declared W63
def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])
bands = []
for wnum, cfg in N1_BANDS.items():
    bands.append((f"W{wnum}.a", tuple(cfg["a"])))
    bands.append((f"W{wnum}.b", tuple(cfg["b_exit"])))
bands.append(("W63-decl.a", W63_DECLARED_A))
bands.append(("W63-decl.b", W63_DECLARED_B))
for tag, cand in (("A", CAND_A), ("B", CAND_B)):
    conflicts = [f"{nm} {lo}..{hi}" for nm, (lo, hi) in bands if overlaps((lo, hi), cand)]
    print(f"candidate {tag} {cand[0]}..{cand[1]} band-conflicts:", conflicts if conflicts else "NONE")

# W62 finalize anchors (prereg S5 basis)
out = subprocess.check_output(["git", "show", "origin/main:results/perpetual_faces/n1_w62_results.json"])
d = json.loads(out.decode())
npc = d.get("null_pool_cumulative", {})
print("W62 finalize keys of null_pool_cumulative:", sorted(npc.keys()) if isinstance(npc, dict) else type(npc))
print("skill_line_v2_k_lift:", d.get("skill_line_v2_k_lift"))
print("shards_consumed:", d.get("shards_consumed"))
print("audit:", {k: v for k, v in d.get("audit", {}).items() if k in ("machine", "elapsed_sec")})
