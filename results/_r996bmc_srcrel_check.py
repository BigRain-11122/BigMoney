# -*- coding: utf-8 -*-
import io, re, os
t = io.open(r"K:\Fluxgroup\FluxGroup\软著申请材料\generate_copyright.py", encoding="utf-8").read()
ROOTS = [
    r"K:\Fluxgroup\FluxGroup\gaming\MiniGame",
    r"K:\Fluxgroup\FluxGroup\gaming",
    r"K:\Fluxgroup\FluxGroup\projects",
    r"K:\Fluxgroup\projects",
    r"K:\Fluxgroup\MiniGame",
    r"K:\Fluxgroup\FluxGroup",
    r"K:\Fluxgroup",
]
for key in ["G04", "G05", "G07", "G08", "G13", "G14", "G20", "G23", "G26", "G28"]:
    m = re.search(r'"' + key + r'":\s*\{(.+?)\},', t, re.S)
    if not m:
        print(key, "NOT-IN-TABLE")
        continue
    nm = re.search(r'"name_en":\s*"([^"]+)"', m.group(1))
    src = re.search(r'"src_rel":\s*"([^"]+)"', m.group(1))
    rel = src.group(1) if src else "?"
    hit = [r for r in ROOTS if os.path.isdir(os.path.join(r, rel))]
    print(key, (nm.group(1) if nm else "?"), "|", rel, "| found-in:", hit[0] if hit else "NOWHERE")
