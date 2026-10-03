# -*- coding: utf-8 -*-
"""r644 bm-a: old-family eps downgrade calibration check (old_047/old_067)."""
import os
import re

BASE = r"C:\Users\sjs20\Desktop\FluxGroup\quant\toolstack\repos\ml-quant-trading\src\mlquant\features"
t = open(os.path.join(BASE, "_factors_old.py"), encoding="utf-8").read()
for fid in ["old_047", "old_067"]:
    m = re.search(r'@register_legacy_factor\("' + fid + r'"\).*?\n(?=@|\Z)', t, re.S)
    if m:
        body = m.group(0)
        attrs = sorted(set(re.findall(r"panel\.([a-zA-Z_][a-zA-Z_0-9]*)", body)))
        print("=====", fid, "| panel attrs:", attrs)
        print(body[:600])
        print()
    else:
        print(fid, "NOT FOUND in _factors_old.py")
