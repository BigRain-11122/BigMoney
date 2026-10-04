"""r470 bm-c: locate ledger total in n1_w115_results.json (nested under science_gates)."""
import json

P = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\perpetual_faces\n1_w115_results.json"
with open(P, encoding="utf-8-sig") as fh:
    d = json.load(fh)


def find_total(obj, path="d", depth=0):
    if depth > 5:
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "total" and isinstance(v, (int, float)):
                print("TOTAL_AT", path + "." + k, "=", v)
            elif k in ("trials_ledger", "ledger") :
                print("LEDGER_OBJ_AT", path + "." + k, "keys=", sorted(v.keys()) if isinstance(v, dict) else type(v).__name__)
                find_total(v, path + "." + k, depth + 1)
            else:
                find_total(v, path + "." + k, depth + 1)


find_total(d)
