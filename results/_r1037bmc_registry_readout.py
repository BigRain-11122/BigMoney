# r1037 bm-c: live N1_BANDS registry readout for W249 seat derive
import sys, json
sys.path.insert(0, r"K:\Fluxgroup\FluxGroup\quant\bigmoney\research")
sys.path.insert(0, r"K:\Fluxgroup\FluxGroup\quant\bigmoney\scripts")
sys.path.insert(0, r"K:\Fluxgroup\FluxGroup\quant\bigmoney")
from perpetual_faces import N1_BANDS

rows = {k: {"a": list(v["a"]), "b": list(v["b_exit"]), "owner": v.get("engine_owner")}
        for k, v in N1_BANDS.items() if k >= 243}
print(json.dumps(rows, ensure_ascii=True, indent=1))
owners = {}
for v in N1_BANDS.values():
    o = v.get("engine_owner")
    if o:
        owners[o] = owners.get(o, 0) + 1
print("owner_counts", owners, "total_owner_rows", sum(owners.values()))
print("all_keys_tail", sorted(N1_BANDS)[-6:])
