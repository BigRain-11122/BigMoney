import json, io, os
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
j = json.load(io.open(ROOT+r"\results\regime5_labels\REGIME5-2026-09-30.json", encoding="utf-8-sig"))
print("REGIME5 keys:", list(j.keys())[:10])
for k,v in j.items():
    if isinstance(v, list):
        print(k, "list len", len(v), "first:", str(v[0])[:120] if v else None, "last:", str(v[-1])[:120] if v else None)
    elif isinstance(v, dict):
        print(k, "dict keys:", list(v.keys())[:8])
    else:
        print(k, "=", str(v)[:100])
print("---thermo dir---")
for f in os.listdir(ROOT+r"\results\regime_thermo"):
    print(" ", f, os.path.getsize(ROOT+r"\results\regime_thermo"+os.sep+f))
