# -*- coding: utf-8 -*-
import json, glob, re, io, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
for f in glob.glob(r"C:\Fluxgroup\FluxGroup\quant\bigmoney\results\gate_attrition*.json"):
    try:
        d = json.load(open(f, encoding="utf-8"))
    except Exception as e:
        print(f, "parse-err", e); continue
    s = json.dumps(d, ensure_ascii=False)
    if "W18" in s or "w18" in s:
        print(f, "-> has W18 rows")
        for m in re.findall(r'"[^"]*[Ww]18[^"]*"[^}]{0,140}', s)[:5]:
            print("  ", m[:170])
