# -*- coding: utf-8 -*-
t = open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_w223bmc_20261012_probe.py", encoding="utf-8").read()
i = t.find('"bmc_ordinal_note"')
seg = t[i:i+520]
j = t.find('Anchor face:')
seg2 = t[j:j+320]
with open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r935bmc_anchor_dump.txt", "w", encoding="utf-8") as f:
    f.write(repr(seg) + "\n\n@@@\n\n" + repr(seg2))
print("dumped")
