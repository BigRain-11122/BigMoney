import json, io, os, glob
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
print("--- alloc_paper dir ---")
d = ROOT+r"\results\alloc_paper"
for f in sorted(os.listdir(d))[:12]:
    print(" ", f, os.path.getsize(os.path.join(d,f)))
print("--- cross_start_robustness dir ---")
d2 = ROOT+r"\results\cross_start_robustness"
for f in sorted(os.listdir(d2))[:10]:
    print(" ", f, os.path.getsize(os.path.join(d2,f)))
print("--- thermo_daily head ---")
with io.open(ROOT+r"\results\regime_thermo\thermo_daily.csv", encoding="utf-8-sig") as fh:
    for i, line in enumerate(fh):
        print(line.rstrip()[:200])
        if i >= 3: break
print("--- thermo summary keys ---")
ts = json.load(io.open(ROOT+r"\results\regime_thermo\thermo_summary.json", encoding="utf-8-sig"))
print(list(ts.keys())[:12])
