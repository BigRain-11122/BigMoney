raw = open("results/gate_attrition.json", encoding="utf-8").read()
for i, ln in enumerate(raw.split("\n")):
    if '"history"' in ln or '"entries"' in ln:
        print(i, repr(ln[:70]))
